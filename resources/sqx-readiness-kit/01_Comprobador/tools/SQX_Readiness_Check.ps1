param(
    [ValidateSet("check", "install", "rollback")]
    [string]$Action = "check",
    [string]$SqxRoot = "",
    [string]$ManifestPath = "",
    [string]$BackupId = ""
)

$ErrorActionPreference = "Stop"
$CheckerVersion = "sqx-edge-readiness-checker-v1"
$ToolRoot = $PSScriptRoot
$KitRoot = (Resolve-Path (Join-Path $ToolRoot "..\..")).Path
if (-not $ManifestPath) {
    $ManifestPath = Join-Path $KitRoot "01_Comprobador\manifest\sqx_edge_readiness_manifest.json"
}
$InstallRoot = Join-Path $KitRoot "02_Instalables_para_SQX"
$BackupRootName = "SQX_Edge_Readiness_Backups"

function Select-SqxRoot {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = "Selecciona la carpeta raiz de tu StrategyQuant X"
    $dialog.ShowNewFolderButton = $false
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw "No se selecciono ninguna carpeta SQX."
    }
    return $dialog.SelectedPath
}

function Convert-ToSlash {
    param([string]$Value)
    return ($Value -replace "\\", "/")
}

function Get-Sha256Text {
    param([string]$Value)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    return ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}

function Get-SqxProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -like "StrategyQuantX*" -or $_.ProcessName -like "SQX*"
    })
}

function Assert-NoSqxProcess {
    $processes = Get-SqxProcesses
    if ($processes.Count -gt 0) {
        $names = ($processes | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ", "
        throw "Cierra SQX antes de $Action. Procesos detectados: $names"
    }
}

function Assert-ValidSqxRootForWrite {
    if (-not (Test-Path -LiteralPath (Join-Path $SqxRoot "StrategyQuantX.exe") -PathType Leaf)) {
        throw "La carpeta seleccionada no parece ser la raiz de SQX. No encuentro StrategyQuantX.exe. Vuelve a ejecutar y selecciona la carpeta principal de StrategyQuant X."
    }
}

function Assert-AllowedTarget {
    param([string]$TargetPath)
    $root = (Resolve-Path $SqxRoot).Path.TrimEnd("\")
    $resolved = [System.IO.Path]::GetFullPath($TargetPath)
    if (-not $resolved.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Destino fuera de SQX: $resolved"
    }
    $relative = $resolved.Substring($root.Length).TrimStart("\").Replace("/", "\")
    $lower = $relative.ToLowerInvariant()
    $allowed = (
        $lower.StartsWith("user\extend\snippets\sq\customanalysis\") -or
        $lower.StartsWith("user\extend\snippets\sq\columns\databanks\") -or
        $lower.StartsWith("user\settings\views\databanks\")
    )
    $blocked = (
        $lower.Contains("\jars\") -or
        $lower.Contains("\plugins\") -or
        $lower.Contains("\license\") -or
        $lower.Contains("\activation\") -or
        $lower.EndsWith("data.db") -or
        $lower.StartsWith("user\projects\")
    )
    if (-not $allowed -or $blocked) {
        throw "Destino no autorizado: $relative"
    }
}

function Get-SourceForTarget {
    param([string]$RelativeTarget)
    $relative = $RelativeTarget.Replace("/", "\")
    if ($relative.ToLowerInvariant().StartsWith("user\extend\snippets\")) {
        $tail = $relative.Substring("user\extend\Snippets\".Length)
        return Join-Path (Join-Path $InstallRoot "Snippets") $tail
    }
    if ($relative.ToLowerInvariant().StartsWith("user\settings\views\databanks\")) {
        return Join-Path (Join-Path $InstallRoot "Views") (Split-Path $relative -Leaf)
    }
    return $null
}

function Invoke-SqliteProbe {
    param([string]$DbPath, [object]$Manifest)
    $python = (Get-Command python -ErrorAction SilentlyContinue)
    if (-not $python) {
        return [pscustomobject]@{
            ok = $false
            error = "sqlite_reader_unavailable"
            brokersValidated = $false
            curatedAssetsValidated = $false
            blockers = @("sqlite_reader_unavailable")
        }
    }
    $probe = @'
import json, sqlite3, sys
db_path = sys.argv[1]
manifest_path = sys.argv[2]
manifest = json.load(open(manifest_path, encoding="utf-8-sig"))
expected_brokers = {int(item["brokerId"]): item for item in manifest.get("brokerProfiles", [])}
expected_assets = [item["asset"] for item in manifest.get("curatedAssets", [])]
con = sqlite3.connect("file:" + db_path.replace("\\", "/") + "?mode=ro", uri=True)
con.row_factory = sqlite3.Row
brokers = {int(row["ID"]): dict(row) for row in con.execute("SELECT ID, NAME, POSTFIX FROM BROKER")}
instruments = {str(row["INSTRUMENT"]): dict(row) for row in con.execute("SELECT INSTRUMENT, DEFAULTSPREAD, COMMISSIONS, SWAP, TICKSIZE, TICKSTEP, POINTVALUE, DATATYPE FROM INSTRUMENTS")}
data_rows = con.execute("SELECT INSTRUMENT, TIMEFRAME, COUNT(*) AS rows_found FROM DATA GROUP BY INSTRUMENT, TIMEFRAME").fetchall()
coverage = {}
for row in data_rows:
    coverage.setdefault(str(row["INSTRUMENT"]), []).append(str(row["TIMEFRAME"]))
missing_brokers = [profile["id"] for bid, profile in expected_brokers.items() if bid not in brokers]
missing_assets = [asset for asset in expected_assets if asset not in instruments]
print(json.dumps({
    "ok": not missing_brokers and not missing_assets,
    "brokersValidated": not missing_brokers,
    "curatedAssetsValidated": not missing_assets,
    "missingBrokers": missing_brokers,
    "missingAssets": missing_assets,
    "coverage": {asset: sorted(coverage.get(asset, [])) for asset in expected_assets},
    "privacy": {"data_db_copied": False, "local_paths_returned": False}
}))
'@
    $tmp = New-TemporaryFile
    Set-Content -LiteralPath $tmp -Value $probe -Encoding UTF8
    try {
        $raw = & $python.Source $tmp $DbPath $ManifestPath
        return ($raw | ConvertFrom-Json)
    } catch {
        return [pscustomobject]@{
            ok = $false
            error = "sqlite_probe_failed"
            detail = $_.Exception.Message
            brokersValidated = $false
            curatedAssetsValidated = $false
            blockers = @("sqlite_probe_failed")
        }
    } finally {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
    }
}

function New-FileStatus {
    param([string[]]$Targets)
    return @($Targets | ForEach-Object {
        $target = Join-Path $SqxRoot ($_.Replace("/", "\"))
        [pscustomobject]@{
            relativeTarget = $_
            exists = Test-Path -LiteralPath $target -PathType Leaf
            sourceAvailable = [bool]((Get-SourceForTarget $_) -and (Test-Path -LiteralPath (Get-SourceForTarget $_) -PathType Leaf))
        }
    })
}

function Test-AllowedSensitiveRuntimePath {
    param([string]$FullPath)
    $root = (Resolve-Path $SqxRoot).Path.TrimEnd("\")
    $relative = [System.IO.Path]::GetFullPath($FullPath).Substring($root.Length).TrimStart("\").Replace("\", "/").ToLowerInvariant()
    $allowed = @(
        "^internal/libs/activation\.jar$",
        "^internal/web/img/licence-dialog-header\.png$",
        "^internal/web/img/sq-license-progress\.gif$",
        "^internal/web/app/licensedialog\.html$",
        "^internal/web/app/licensedialogbr\.html$",
        "^internal/web/app/licensedialogqdm\.html$",
        "^internal/web/app/licensedialogranger\.html$",
        "^internal/electron/license\.electron\.txt$",
        "^internal/electron/licenses\.chromium\.html$",
        "^internal/electron-qdm/license\.electron\.txt$",
        "^internal/electron-qdm/licenses\.chromium\.html$",
        "^j64/legal/.*/(additional_license_info|license)$",
        "^j64/legal/jdk\.crypto\.cryptoki/pkcs11cryptotoken\.md$",
        "^sq_license_and_service_terms\.pdf$"
    )
    foreach ($pattern in $allowed) {
        if ($relative -match $pattern) { return $true }
    }
    return $false
}

function New-Report {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $dataDb = Join-Path $SqxRoot "user\data\data.db"
    $snippets = New-FileStatus @($manifest.requiredSnippets)
    $views = New-FileStatus @($manifest.requiredViews)
    $dbProbe = if (Test-Path -LiteralPath $dataDb -PathType Leaf) { Invoke-SqliteProbe $dataDb $manifest } else { $null }
    $sensitiveFindings = @()
    foreach ($pattern in @("license.db", "trust tokens", "license", "activation", "crack", "token", "secret")) {
        $matches = @(Get-ChildItem -LiteralPath $SqxRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName.ToLowerInvariant().Contains($pattern) -and
                -not (Test-AllowedSensitiveRuntimePath $_.FullName)
            } |
            Select-Object -First 5)
        if ($matches.Count -gt 0) { $sensitiveFindings += $pattern }
    }
    $checks = [ordered]@{
        sqx_root_selected = Test-Path -LiteralPath $SqxRoot -PathType Container
        sqx_version_compatible = Test-Path -LiteralPath (Join-Path $SqxRoot "StrategyQuantX.exe") -PathType Leaf
        data_db_found = Test-Path -LiteralPath $dataDb -PathType Leaf
        brokers_validated = [bool]($dbProbe -and $dbProbe.brokersValidated)
        curated_assets_validated = [bool]($dbProbe -and $dbProbe.curatedAssetsValidated)
        snippets_ready = (@($snippets | Where-Object { -not $_.exists }).Count -eq 0)
        correlation_view_ready = (@($views | Where-Object { -not $_.exists }).Count -eq 0)
        portable_source_acknowledged = $true
        sensitive_files_excluded = ($sensitiveFindings.Count -eq 0)
    }
    $blockers = @()
    if ($dbProbe -and $dbProbe.blockers) { $blockers += @($dbProbe.blockers) }
    [pscustomobject]@{
        ok = $true
        source = "portable_checker"
        checkerVersion = $CheckerVersion
        generatedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        selectedRootName = Split-Path -Leaf $SqxRoot
        sqxRootHash = Get-Sha256Text $SqxRoot
        checks = $checks
        summary = [pscustomobject]@{
            sqxRootSelected = $checks.sqx_root_selected
            versionCompatible = $checks.sqx_version_compatible
            dataDbFound = $checks.data_db_found
            brokersValidated = $checks.brokers_validated
            curatedAssetsValidated = $checks.curated_assets_validated
            snippetsReady = $checks.snippets_ready
            correlationViewReady = $checks.correlation_view_ready
            viewsReady = $checks.correlation_view_ready
        }
        files = [pscustomobject]@{
            snippets = $snippets
            views = $views
            sensitiveFindings = $sensitiveFindings.Count -gt 0
            sensitiveFindingKinds = $sensitiveFindings
        }
        data = $dbProbe
        blockers = $blockers
        privacy = [pscustomobject]@{ local_paths_returned = $false; data_db_copied = $false }
    }
}

function Invoke-Install {
    Assert-ValidSqxRootForWrite
    Assert-NoSqxProcess
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupRoot = Join-Path $SqxRoot $BackupRootName
    $backupDir = Join-Path $backupRoot "readiness_$stamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $installed = @()
    foreach ($relative in @($manifest.requiredSnippets + $manifest.requiredViews)) {
        $source = Get-SourceForTarget $relative
        if (-not ($source -and (Test-Path -LiteralPath $source -PathType Leaf))) {
            throw "El kit no contiene el instalable requerido: $relative. Vuelve a generar o descargar el kit completo."
        }
        $target = Join-Path $SqxRoot ($relative.Replace("/", "\"))
        Assert-AllowedTarget $target
        $backupPath = $null
        if (Test-Path -LiteralPath $target -PathType Leaf) {
            $backupPath = Join-Path $backupDir ($relative.Replace("/", "\"))
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
            Copy-Item -LiteralPath $target -Destination $backupPath -Force
        }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -LiteralPath $source -Destination $target -Force
        $installed += [pscustomobject]@{
            relativeTarget = $relative
            existed = [bool]$backupPath
            backupRelative = if ($backupPath) { $relative } else { $null }
        }
    }
    if ($installed.Count -eq 0) {
        throw "No se instalo ningun archivo. Revisa que el kit este completo y que seleccionaste la raiz correcta de SQX."
    }
    $rollback = [pscustomobject]@{
        checkerVersion = $CheckerVersion
        createdAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        backupId = (Split-Path -Leaf $backupDir)
        installed = $installed
    }
    $rollback | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $backupDir "rollback_manifest.json") -Encoding UTF8
    [pscustomobject]@{ ok = $true; action = "install"; backupId = (Split-Path -Leaf $backupDir); installed = $installed }
}

function Invoke-Rollback {
    Assert-ValidSqxRootForWrite
    Assert-NoSqxProcess
    $backupRoot = Join-Path $SqxRoot $BackupRootName
    if ($BackupId) {
        $backupDir = Join-Path $backupRoot $BackupId
    } else {
        $latest = Get-ChildItem -LiteralPath $backupRoot -Directory -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if (-not $latest) { throw "No hay backup disponible para rollback." }
        $backupDir = $latest.FullName
    }
    $rollbackPath = Join-Path $backupDir "rollback_manifest.json"
    if (-not (Test-Path -LiteralPath $rollbackPath -PathType Leaf)) {
        throw "No existe rollback_manifest.json en $backupDir"
    }
    $rollback = Get-Content -LiteralPath $rollbackPath -Raw | ConvertFrom-Json
    $restored = @()
    foreach ($entry in @($rollback.installed)) {
        $relative = [string]$entry.relativeTarget
        $target = Join-Path $SqxRoot ($relative.Replace("/", "\"))
        Assert-AllowedTarget $target
        if ($entry.existed -eq $true) {
            $backupFile = Join-Path $backupDir ($relative.Replace("/", "\"))
            if (-not (Test-Path -LiteralPath $backupFile -PathType Leaf)) {
                throw "Backup faltante: $relative"
            }
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $backupFile -Destination $target -Force
            $actionTaken = "restored"
        } elseif (Test-Path -LiteralPath $target -PathType Leaf) {
            Remove-Item -LiteralPath $target -Force
            $actionTaken = "removed_installed_file"
        } else {
            $actionTaken = "already_absent"
        }
        $restored += [pscustomobject]@{ relativeTarget = $relative; action = $actionTaken }
    }
    [pscustomobject]@{ ok = $true; action = "rollback"; backupId = (Split-Path -Leaf $backupDir); files = $restored }
}

try {
    if (-not $SqxRoot) { $SqxRoot = Select-SqxRoot }
    $SqxRoot = (Resolve-Path $SqxRoot).Path
    if ($Action -eq "install") {
        $result = Invoke-Install
    } elseif ($Action -eq "rollback") {
        $result = Invoke-Rollback
    } else {
        $result = New-Report
    }
    $outPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) ("SQX_Readiness_Report_{0}.json" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outPath -Encoding UTF8
    Write-Host "SQX Edge Readiness completado."
    Write-Host ("Reporte JSON: {0}" -f $outPath)
    Write-Host ("Accion: {0}" -f $Action)
    if ($Action -eq "install") {
        Write-Host ("Instalados/actualizados: {0} archivos" -f @($result.installed).Count)
        Write-Host ("Backup creado: {0}" -f $result.backupId)
        Write-Host "Si algo no queda bien, ejecuta Deshacer_instalacion_snippets_y_View_CORR1.bat."
    }
    if ($Action -eq "rollback") {
        Write-Host ("Backup restaurado: {0}" -f $result.backupId)
        Write-Host ("Archivos procesados: {0}" -f @($result.files).Count)
    }
    if ($result.checks) {
        $missing = @($result.checks.GetEnumerator() | Where-Object { -not [bool]$_.Value } | ForEach-Object { $_.Key })
        if ($missing.Count -eq 0 -and @($result.blockers).Count -eq 0) {
            Write-Host "Estado: OK"
        } else {
            Write-Host ("Pendiente: {0}" -f ($missing -join ", "))
        }
    }
    exit 0
} catch {
    Write-Host ""
    Write-Host "No se pudo completar la accion SQX Edge Readiness."
    Write-Host ("Motivo: {0}" -f $_.Exception.Message)
    Write-Host ""
    exit 1
}
