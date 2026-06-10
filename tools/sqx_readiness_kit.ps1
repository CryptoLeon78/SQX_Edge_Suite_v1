param(
    [string]$OutputDir = "",
    [string]$PortableSourceZip = "",
    [switch]$IncludePortable,
    [switch]$PrivateOperatorTransfer,
    [string]$SqxPrivateSourceRoot = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$KitName = if ($PrivateOperatorTransfer) { "SQX_Edge_Preparacion_Kit_PRIVADO_QXPRO_v1" } else { "SQX_Edge_Preparacion_Kit_v1" }
$LocalRoot = Join-Path $RepoRoot ".local\sqx_readiness_kit"
$StageRoot = Join-Path $LocalRoot $KitName
$SourceRoot = Join-Path $RepoRoot "resources\sqx-readiness-kit"
$ManifestSource = Join-Path $RepoRoot "backend\sqx-edge-tool\config\sqx_readiness_manifest.json"
$CorrelationPack = Join-Path $RepoRoot "integrations\sqx142\own_features\correlation_pack"
if (-not $OutputDir) { $OutputDir = Join-Path $RepoRoot "dist" }

$PublicBlockedNamePatterns = @(
    "\.git($|[\\/])",
    "\.local($|[\\/])",
    "user[\\/]data[\\/]data\.db$",
    "user[\\/].*\.db$",
    "user[\\/]projects($|[\\/])",
    "license",
    "licence",
    "activation",
    "crack",
    "jars($|[\\/])",
    "plugins[\\/]internal",
    "token",
    "secret"
)

$PrivateBlockedNamePatterns = @(
    "\.git($|[\\/])",
    "\.local($|[\\/])",
    "\.local_cache_backups($|[\\/])",
    "\.local_code_backups($|[\\/])",
    "artifacts($|[\\/])",
    "temp($|[\\/])",
    "tmp($|[\\/])",
    "cache($|[\\/])",
    "backup",
    "user[\\/]data($|[\\/])",
    "user[\\/].*\.db$",
    "user[\\/]projects($|[\\/])",
    "license\.db$",
    "trust tokens",
    "license",
    "licence",
    "activation",
    "crack",
    "token",
    "secret",
    "\.log$",
    "\.local\.json",
    "\.local\.jsonl"
)

$PrivateAllowedRuntimePatterns = @(
    "^internal[\\/]libs[\\/]activation\.jar$",
    "^internal[\\/]web[\\/]img[\\/]licence-dialog-header\.png$",
    "^internal[\\/]web[\\/]img[\\/]sq-license-progress\.gif$",
    "^internal[\\/]web[\\/]app[\\/]licensedialog\.html$",
    "^internal[\\/]web[\\/]app[\\/]licensedialogbr\.html$",
    "^internal[\\/]web[\\/]app[\\/]licensedialogqdm\.html$",
    "^internal[\\/]web[\\/]app[\\/]licensedialogranger\.html$",
    "^internal[\\/]electron[\\/]license\.electron\.txt$",
    "^internal[\\/]electron[\\/]licenses\.chromium\.html$",
    "^internal[\\/]electron-qdm[\\/]license\.electron\.txt$",
    "^internal[\\/]electron-qdm[\\/]licenses\.chromium\.html$",
    "^j64[\\/]legal[\\/].*[\\/](additional_license_info|license)$",
    "^j64[\\/]legal[\\/]jdk\.crypto\.cryptoki[\\/]pkcs11cryptotoken\.md$",
    "^sq_license_and_service_terms\.pdf$"
)

$PrivateAllowedBootstrapDataPatterns = @(
    "^user[\\/]data[\\/]brokers\.version$",
    "^user[\\/]data[\\/]connections\.txt$",
    "^user[\\/]data[\\/]data_futures\.h2\.db$",
    "^user[\\/]data[\\/]data_futures\.version$",
    "^user[\\/]data[\\/]data_stock\.h2\.db$",
    "^user[\\/]data[\\/]data_stock\.version$",
    "^user[\\/]data[\\/]data\.db$"
)

function Assert-SafeDeleteTarget {
    param([string]$Path)
    $resolved = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetFullPath($LocalRoot).TrimEnd("\")
    if (-not $resolved.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe cleanup target: $resolved"
    }
}

function New-CleanDirectory {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        Assert-SafeDeleteTarget $Path
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Set-TextFile {
    param([string]$Path, [string]$Content)
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Test-BlockedName {
    param(
        [string]$Name,
        [string[]]$Patterns = $PublicBlockedNamePatterns
    )
    $normalized = $Name.Replace("\", "/").ToLowerInvariant()
    foreach ($pattern in $Patterns) {
        if ($normalized -match $pattern) { return $true }
    }
    return $false
}

function Test-PrivateAllowedRuntimeName {
    param([string]$Name)
    $normalized = $Name.Replace("\", "/").ToLowerInvariant()
    foreach ($pattern in $PrivateAllowedRuntimePatterns) {
        if ($normalized -match $pattern) { return $true }
    }
    return $false
}

function Test-PrivateAllowedBootstrapDataName {
    param([string]$Name)
    $normalized = $Name.Replace("\", "/").ToLowerInvariant()
    foreach ($pattern in $PrivateAllowedBootstrapDataPatterns) {
        if ($normalized -match $pattern) { return $true }
    }
    return $false
}

function Test-PrivateBlockedName {
    param([string]$Name)
    if (Test-PrivateAllowedRuntimeName $Name) { return $false }
    if (Test-PrivateAllowedBootstrapDataName $Name) { return $false }
    return (Test-BlockedName -Name $Name -Patterns $PrivateBlockedNamePatterns)
}

function Assert-ZipSourceSafe {
    param([string]$ZipPath)
    if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
        throw "Portable source zip not found: $ZipPath"
    }
    if (Test-BlockedName $ZipPath) {
        throw "Portable source path is not allowed by readiness packaging policy."
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        foreach ($entry in $zip.Entries) {
            if (Test-BlockedName $entry.FullName) {
                throw "Portable source contains blocked entry: $($entry.FullName)"
            }
        }
    } finally {
        $zip.Dispose()
    }
}

function Assert-PrivateSourceRoot {
    param([string]$SourceRootPath)
    if (-not (Test-Path -LiteralPath $SourceRootPath -PathType Container)) {
        throw "Private SQX source root not found: $SourceRootPath"
    }
    if (Test-BlockedName -Name $SourceRootPath -Patterns @("crack")) {
        throw "Private SQX source root cannot contain Crack in its path."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $SourceRootPath "StrategyQuantX.exe") -PathType Leaf)) {
        throw "Private SQX source root is missing StrategyQuantX.exe."
    }
}

function Assert-StageSafe {
    $files = Get-ChildItem -LiteralPath $StageRoot -Recurse -File
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($StageRoot.Length).TrimStart("\")
        $normalized = $relative.Replace("\", "/")
        if ($PrivateOperatorTransfer -and $normalized.StartsWith("05_SQX_142_Codex_QXPRO_Privado/SQX_142_Codex_QXPRO/")) {
            $sqxRelative = $normalized.Substring("05_SQX_142_Codex_QXPRO_Privado/SQX_142_Codex_QXPRO/".Length)
            if (Test-PrivateBlockedName $sqxRelative) {
                throw "Private readiness kit contains blocked SQX file path: $relative"
            }
            continue
        }
        if (-not $PrivateOperatorTransfer -and $relative -like "05_SQX_142_Codex_Portable\SQX_142_Codex_Portable_AUTORIZADO.zip") {
            continue
        }
        if (Test-BlockedName $relative $PublicBlockedNamePatterns) {
            throw "Readiness kit contains blocked file path: $relative"
        }
    }
}

function New-KitZip {
    param(
        [Parameter(Mandatory=$true)][string]$SourceDirectory,
        [Parameter(Mandatory=$true)][string]$DestinationZip
    )

    $parent = Split-Path -Parent $SourceDirectory
    $name = Split-Path -Leaf $SourceDirectory
    $tar = Get-Command tar.exe -ErrorAction SilentlyContinue
    if ($tar) {
        & $tar.Source -a -c -f $DestinationZip -C $parent $name
        if ($LASTEXITCODE -ne 0) {
            throw "tar.exe failed while creating $DestinationZip"
        }
        return
    }

    Compress-Archive -LiteralPath $SourceDirectory -DestinationPath $DestinationZip -Force
}

function Copy-IfExists {
    param([string]$Source, [string]$Destination)
    if (Test-Path -LiteralPath $Source -PathType Leaf) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        return $true
    }
    return $false
}

function Export-ManifestFiles {
    $manifest = Get-Content -LiteralPath $ManifestSource -Raw | ConvertFrom-Json
    New-Item -ItemType Directory -Force -Path (Join-Path $StageRoot "01_Comprobador\manifest") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $StageRoot "03_Data_y_Activos_Requeridos") | Out-Null
    Copy-Item -LiteralPath $ManifestSource -Destination (Join-Path $StageRoot "01_Comprobador\manifest\sqx_edge_readiness_manifest.json") -Force
    Copy-Item -LiteralPath $ManifestSource -Destination (Join-Path $StageRoot "03_Data_y_Activos_Requeridos\Config_referencia_saneada.json") -Force

    $assetLines = @("asset,timeframes,defaultSpread,commissions,swap,tickSize,tickStep,pointValue,dataType")
    foreach ($asset in $manifest.curatedAssets) {
        $ref = $asset.reference
        $assetLines += ('"{0}","{1}",{2},{3},{4},{5},{6},{7},{8}' -f
            $asset.asset,
            (($asset.timeframes) -join "|"),
            $ref.defaultSpread,
            ($ref.commissions -as [string]),
            ($ref.swap -as [string]),
            $ref.tickSize,
            $ref.tickStep,
            $ref.pointValue,
            $ref.dataType
        )
    }
    Set-TextFile (Join-Path $StageRoot "03_Data_y_Activos_Requeridos\Activos_requeridos.csv") ($assetLines -join "`r`n")

    $nameLines = @("asset,data_manager_names")
    foreach ($asset in $manifest.curatedAssets) {
        $nameLines += ('"{0}","{1}"' -f $asset.asset, (($asset.dataManagerNames) -join "|"))
    }
    Set-TextFile (Join-Path $StageRoot "03_Data_y_Activos_Requeridos\Nombres_Data_Manager.csv") ($nameLines -join "`r`n")
}

function Copy-PrivateSqxSource {
    param(
        [string]$SourceRootPath,
        [string]$DestinationRoot
    )
    Assert-PrivateSourceRoot $SourceRootPath
    $resolvedSource = (Resolve-Path -LiteralPath $SourceRootPath).Path.TrimEnd("\")
    New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null
    $copied = 0
    $excluded = @{}

    $items = Get-ChildItem -LiteralPath $resolvedSource -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        $relative = $item.FullName.Substring($resolvedSource.Length).TrimStart("\")
        if (-not $relative) { continue }
        if (Test-PrivateBlockedName $relative) {
            $first = ($relative.Replace("\", "/").Split("/"))[0]
            if (-not $excluded.ContainsKey($first)) { $excluded[$first] = 0 }
            $excluded[$first] += 1
            continue
        }
        $target = Join-Path $DestinationRoot $relative
        if ($item.PSIsContainer) {
            New-Item -ItemType Directory -Force -Path $target | Out-Null
        } else {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
            Copy-Item -LiteralPath $item.FullName -Destination $target -Force
            $copied += 1
        }
    }

    $manifest = [pscustomobject]@{
        schema = "sqx-edge.private-operator-transfer-manifest-v1"
        distributionScope = "private_operator_only"
        label = "SQX 142 Codex QXPRO privado - NO REDISTRIBUIR"
        sourceRootRedacted = "[private-operator-source]/[SQX_142_Codex_QXPRO]"
        sourceRootHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $resolvedSource "StrategyQuantX.exe")).Hash.ToLowerInvariant()
        generatedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        copiedFileCount = $copied
        excludedTopLevelCounts = $excluded
        exclusionsApplied = @(
            ".git", ".local", ".local_cache_backups", ".local_code_backups", "temp", "tmp", "artifacts",
            "user/data except bootstrap allowlist", "user/data/History", "user/*.db except bootstrap allowlist", "user/projects", "license/licence state except runtime allowlist",
            "activation state except runtime library", "token state except legal docs", "secret", "logs", "caches", "backups"
        )
        bootstrapDataAllowlistApplied = @(
            "user/data/brokers.version",
            "user/data/connections.txt",
            "user/data/data_futures.h2.db",
            "user/data/data_futures.version",
            "user/data/data_stock.h2.db",
            "user/data/data_stock.version",
            "user/data/data.db"
        )
        runtimeAllowlistApplied = @(
            "internal/libs/activation.jar",
            "internal/web/app/licenseDialog*.html",
            "internal/web/img/licence-dialog-header.png",
            "internal/web/img/sq-license-progress.gif",
            "internal/electron*/LICENSE*",
            "j64/legal/**/LICENSE",
            "j64/legal/**/ADDITIONAL_LICENSE_INFO",
            "SQ_License_and_Service_Terms.pdf"
        )
        operatorNotice = "NO REDISTRIBUIR. Paquete privado para el operador. Incluye runtime legal/UI/licensing neutro y bootstrap privado de Data Manager para compatibilidad de arranque, pero no incluye license.db, tokens, historico History, proyectos ni caches; la licencia/activacion debe gestionarse manualmente por via autorizada en el otro equipo."
        privacy = [pscustomobject]@{
            dataDbCopied = $true
            privateBootstrapDataIncluded = $true
            historicalDataIncluded = $false
            userProjectsCopied = $false
            licenseOrActivationIncluded = $false
            licenseOrActivationStateIncluded = $false
            runtimeLicenseUiIncluded = $true
            runtimeActivationLibraryIncluded = $true
            tokensIncluded = $false
            sourcePathReturned = $false
        }
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $DestinationRoot "portable_authorization_manifest.json") -Encoding UTF8
    return $manifest
}

New-Item -ItemType Directory -Force -Path $LocalRoot | Out-Null
New-CleanDirectory $StageRoot
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Copy-Item -LiteralPath (Join-Path $SourceRoot "01_Comprobador") -Destination (Join-Path $StageRoot "01_Comprobador") -Recurse -Force
foreach ($requiredBat in @("Comprobar_mi_SQX.bat", "Instalar_snippets_y_View_CORR1.bat", "Deshacer_instalacion_snippets_y_View_CORR1.bat")) {
    if (-not (Test-Path -LiteralPath (Join-Path $StageRoot "01_Comprobador\$requiredBat") -PathType Leaf)) {
        throw "Readiness kit missing required guided BAT: $requiredBat"
    }
}
Copy-Item -LiteralPath (Join-Path $SourceRoot "04_Checklist_Web") -Destination (Join-Path $StageRoot "04_Checklist_Web") -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $StageRoot "02_Instalables_para_SQX\Snippets") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $StageRoot "02_Instalables_para_SQX\Views") | Out-Null
Get-ChildItem -LiteralPath (Join-Path $CorrelationPack "Snippets") | Copy-Item -Destination (Join-Path $StageRoot "02_Instalables_para_SQX\Snippets") -Recurse -Force
Copy-IfExists (Join-Path $CorrelationPack "views\SQX EDGE CORRELATION REVIEW.vw") (Join-Path $StageRoot "02_Instalables_para_SQX\Views\SQX EDGE CORRELATION REVIEW.vw") | Out-Null

Export-ManifestFiles

if ($PrivateOperatorTransfer) {
    Set-TextFile (Join-Path $StageRoot "00_PRIVADO_OPERADOR_NO_REDISTRIBUIR\LEER_ANTES.txt") @"
SQX Edge QXPRO Private Operator Transfer

Este paquete es privado para el operador y NO se debe redistribuir.
Incluye bootstrap privado de Data Manager para compatibilidad de arranque:
- user\data\brokers.version
- user\data\connections.txt
- user\data\data_futures.h2.db
- user\data\data_futures.version
- user\data\data_stock.h2.db
- user\data\data_stock.version
- user\data\data.db

No incluye user\data\History, proyectos, license.db, estado de activacion, tokens, caches, backups ni evidencia local.
Si incluye runtime neutro de licencia/UI/legal necesario para compatibilidad de arranque.
Si SQX requiere licencia o activacion en el otro equipo, debe gestionarse manualmente por via autorizada.
"@
}

Set-TextFile (Join-Path $StageRoot "LEEME_PRIMERO.txt") @"
SQX Edge Preparacion Kit v1

1. Ejecuta 01_Comprobador\Comprobar_mi_SQX.bat.
2. Selecciona la carpeta raiz de tu StrategyQuant X.
3. Importa el JSON generado en el checklist web SQX Edge.
4. Solo instala snippets y la view CORR1 si SQX esta cerrado y entiendes que se crea backup previo.
5. Para instalar sin usar PowerShell, haz doble clic en 01_Comprobador\Instalar_snippets_y_View_CORR1.bat.
6. Para deshacer esa instalacion, haz doble clic en 01_Comprobador\Deshacer_instalacion_snippets_y_View_CORR1.bat.

Este kit privado incluye solo bootstrap de Data Manager para compatibilidad de arranque, incluyendo user\data\data.db.
No incluye user\data\History, proyectos, license.db, estado de activacion, fuentes con Crack, tokens ni archivos comerciales sensibles.
En modo privado puede incluir runtime neutro de licencia/UI/legal necesario para compatibilidad de arranque.
"@

Set-TextFile (Join-Path $StageRoot "02_Instalables_para_SQX\Rollback_instrucciones.txt") @"
Rollback

El comprobador crea backup antes de sobrescribir snippets o la view CORR1 autorizada.
Ejecuta desde PowerShell:

01_Comprobador\tools\SQX_Readiness_Check.ps1 -Action rollback -SqxRoot "C:\RUTA\A\TU\SQX"

Si no indicas BackupId, se usa el ultimo backup disponible.
"@

Set-TextFile (Join-Path $StageRoot "02_Instalables_para_SQX\Views\README_VIEW_CORR1.txt") @"
View activa incluida:
- SQX EDGE CORRELATION REVIEW.vw

EGT Core, Robustez y CVC Decision Cert ya no forman parte del readiness obligatorio.
"@

Set-TextFile (Join-Path $StageRoot "03_Data_y_Activos_Requeridos\Descargas_recomendadas.txt") @"
Descarga los activos/timeframes indicados en Activos_requeridos.csv.
Usa los nombres Data Manager de Nombres_Data_Manager.csv.
Mantener brokers esperados: Darwinex/SQX Edge y Dukascopy OOS.
El kit privado puede incluir bootstrap de Data Manager, pero no incluye historico user\data\History; descarga el historico indicado si falta cobertura.
"@

Set-TextFile (Join-Path $StageRoot "04_Checklist_Web\Como_importar_reporte_checker.txt") @"
Como importar el reporte

1. Ejecuta 01_Comprobador\Comprobar_mi_SQX.bat.
2. Localiza el archivo SQX_Readiness_Report_YYYYMMDD_HHMMSS.json.
3. Entra al dashboard web SQX Edge.
4. En el modal SQX Edge Readiness pulsa Importar reporte del comprobador.
5. Las funciones SQX-dependientes se desbloquean cuando el checklist queda completo.
"@

if ($PrivateOperatorTransfer) {
    if (-not $SqxPrivateSourceRoot) {
        throw "Private operator transfer requires -SqxPrivateSourceRoot pointing to an authorized local SQX 142 source."
    }
    $portableDir = Join-Path $StageRoot "05_SQX_142_Codex_QXPRO_Privado"
    $privateSqxDir = Join-Path $portableDir "SQX_142_Codex_QXPRO"
    $privateManifest = Copy-PrivateSqxSource $SqxPrivateSourceRoot $privateSqxDir
    Set-TextFile (Join-Path $StageRoot "06_PostInstalacion_Otro_PC\PASOS_OTRO_PC.txt") @"
Pasos en el otro equipo privado

1. Descomprime el kit privado.
2. Abre 05_SQX_142_Codex_QXPRO_Privado\SQX_142_Codex_QXPRO y ejecuta SQX segun tu autorizacion/licencia.
3. Revisa Data Manager. El kit privado incluye bootstrap base, pero no historico user\data\History.
4. Ejecuta 01_Comprobador\Comprobar_mi_SQX.bat y selecciona la carpeta 05_SQX_142_Codex_QXPRO_Privado\SQX_142_Codex_QXPRO.
5. Si faltan snippets o la view CORR1, cierra SQX y haz doble clic en 01_Comprobador\Instalar_snippets_y_View_CORR1.bat.
6. Si necesitas deshacer esa instalacion, cierra SQX y haz doble clic en 01_Comprobador\Deshacer_instalacion_snippets_y_View_CORR1.bat.
7. Importa el reporte JSON en el dashboard.
"@
} else {
    $portableDir = Join-Path $StageRoot "05_SQX_142_Codex_Portable"
    New-Item -ItemType Directory -Force -Path $portableDir | Out-Null
    Set-TextFile (Join-Path $portableDir "README_PORTABLE.txt") @"
SQX 142 Codex Portable

El ZIP portable solo se incluye si se proporciona una fuente redistribuible, limpia y autorizada.
No uses instalaciones diagnosticas locales ni archivos con licencia, activacion, Crack o internos sensibles.
"@

    if ($IncludePortable -and $PortableSourceZip) {
        Assert-ZipSourceSafe $PortableSourceZip
        Copy-Item -LiteralPath $PortableSourceZip -Destination (Join-Path $portableDir "SQX_142_Codex_Portable_AUTORIZADO.zip") -Force
    } else {
        Set-TextFile (Join-Path $portableDir "NO_INCLUIDO_REQUIERE_FUENTE_AUTORIZADA.txt") @"
No se incluyo SQX 142 Codex Portable porque no se proporciono una fuente ZIP redistribuible y autorizada.
"@
    }
}

Assert-StageSafe
$zipPath = Join-Path $OutputDir "$KitName.zip"
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
New-KitZip -SourceDirectory $StageRoot -DestinationZip $zipPath

[pscustomobject]@{
    ok = $true
    kit = $KitName
    zip = $zipPath
    privateOperatorTransfer = [bool]$PrivateOperatorTransfer
    portableIncluded = [bool]($PrivateOperatorTransfer -or ($IncludePortable -and $PortableSourceZip))
    privateManifest = if ($PrivateOperatorTransfer) { $privateManifest } else { $null }
    privacy = [pscustomobject]@{
        dataDbCopied = [bool]$PrivateOperatorTransfer
        privateBootstrapDataIncluded = [bool]$PrivateOperatorTransfer
        historicalDataIncluded = $false
        localPathsReturned = $false
        licenseOrActivationIncluded = $false
        licenseOrActivationStateIncluded = $false
        runtimeLicenseUiIncluded = [bool]$PrivateOperatorTransfer
        runtimeActivationLibraryIncluded = [bool]$PrivateOperatorTransfer
        tokensIncluded = $false
    }
} | ConvertTo-Json -Depth 8
