param(
    [ValidateSet("status", "build", "install", "rollback")]
    [string]$Action = "status",
    [string]$InputCsv = "",
    [string]$TagCsvPath = "",
    [string]$OutputDir = "",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$BackupId = "",
    [string]$SettingsJson = ""
)

$ErrorActionPreference = "Stop"

$Version = "sqx142-own-features2-correlation-data-smoke-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonExe = Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"
$BuilderPy = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_correlation_data_smoke.py"
$DefaultInput = Join-Path $RepoRoot "integrations\sqx142\own_features\correlation_pack\samples\correlation_source_rows.csv"
$LocalRoot = Join-Path $RepoRoot ".local\sqx142_own_features\data_smoke"
$BackupRoot = Join-Path $LocalRoot "backups"
$TargetCsv = Join-Path $SqxRoot "user\extend\SQXEdge\Correlation\correlation_decisions.csv"

if (-not $OutputDir.Trim()) {
    $OutputDir = Join-Path $LocalRoot "latest"
}
if (-not $InputCsv.Trim()) {
    $InputCsv = $DefaultInput
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
        throw "SQX must be closed before $Action. Running process(es): $names"
    }
}

function Assert-TargetAllowed {
    param([string]$Path)
    $root = (Resolve-Path $SqxRoot).Path.TrimEnd("\")
    $resolved = [System.IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Target escapes SQX root: $resolved"
    }
    $relative = $resolved.Substring($root.Length).TrimStart("\").Replace("/", "\").ToLowerInvariant()
    if ($relative -ne "user\extend\sqxedge\correlation\correlation_decisions.csv") {
        throw "Data smoke can only target correlation_decisions.csv, got: $relative"
    }
}

function Get-Sha256OrNull {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    }
    return $null
}

function Get-CsvSummary {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{ exists = $false; hash = $null; rows = 0; schemaOk = $false }
    }
    $lines = @(Get-Content -LiteralPath $Path -ErrorAction Stop)
    $header = if ($lines.Count -gt 0) { $lines[0] } else { "" }
    $schema = "strategyRef,candidateId,decision,reason,score,maxObservedCorrelation,correlationStatus,nearestWinnerId,portfolioRank,generatedAt,version"
    return [pscustomobject]@{
        exists = $true
        hash = Get-Sha256OrNull $Path
        rows = [Math]::Max(0, $lines.Count - 1)
        schemaOk = $header -eq $schema
    }
}

function Invoke-Status {
    $processes = Get-SqxProcesses
    $latestBackup = Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "status"
        sqxClosed = $processes.Count -eq 0
        processCount = $processes.Count
        target = Get-CsvSummary $TargetCsv
        latestBuild = Get-CsvSummary (Join-Path $OutputDir "correlation_decisions.csv")
        latestBackup = if ($latestBackup) { $latestBackup.Name } else { $null }
        guards = @{
            sqx_runtime_started = $false
            data_db_write_allowed = $false
            user_projects_write_allowed = $false
            databank_delete_allowed = $false
            tag_csv_only = $true
        }
    } | ConvertTo-Json -Depth 5
}

function Invoke-Build {
    if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
        throw "Backend venv python not found: $PythonExe"
    }
    if (-not (Test-Path -LiteralPath $BuilderPy -PathType Leaf)) {
        throw "Data smoke builder missing: $BuilderPy"
    }
    if (-not (Test-Path -LiteralPath $InputCsv -PathType Leaf)) {
        throw "Input CSV/JSON missing: $InputCsv"
    }
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $args = @($BuilderPy, "--input", $InputCsv, "--output-dir", $OutputDir)
    if ($SettingsJson.Trim()) {
        $args += @("--settings-json", $SettingsJson)
    }
    & $PythonExe @args
    if ($LASTEXITCODE -ne 0) {
        throw "Data smoke builder failed with exit code $LASTEXITCODE"
    }
}

function Resolve-TagCsvForInstall {
    if ($TagCsvPath.Trim()) {
        if (-not (Test-Path -LiteralPath $TagCsvPath -PathType Leaf)) { throw "TagCsvPath missing: $TagCsvPath" }
        return (Resolve-Path $TagCsvPath).Path
    }
    $built = Join-Path $OutputDir "correlation_decisions.csv"
    Invoke-Build | Out-Null
    return (Resolve-Path $built).Path
}

function Invoke-Install {
    Assert-NoSqxProcess
    Assert-TargetAllowed $TargetCsv
    $source = Resolve-TagCsvForInstall
    $summary = Get-CsvSummary $source
    if (-not $summary.schemaOk) {
        throw "Tag CSV schema mismatch: $source"
    }
    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BackupRoot "$Version`_$stamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $existed = Test-Path -LiteralPath $TargetCsv -PathType Leaf
    $backupPath = Join-Path $backupDir "correlation_decisions.csv"
    if ($existed) {
        Copy-Item -LiteralPath $TargetCsv -Destination $backupPath -Force
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $TargetCsv) | Out-Null
    Copy-Item -LiteralPath $source -Destination $TargetCsv -Force
    $evidence = [pscustomobject]@{
        ok = $true
        version = $Version
        action = "install"
        installedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        backupId = Split-Path -Leaf $backupDir
        existed = $existed
        beforeHash = if ($existed) { Get-Sha256OrNull $backupPath } else { $null }
        afterHash = Get-Sha256OrNull $TargetCsv
        sourceHash = Get-Sha256OrNull $source
        rows = (Get-CsvSummary $TargetCsv).rows
        target = "user\extend\SQXEdge\Correlation\correlation_decisions.csv"
        guards = @{
            sqx_runtime_started = $false
            data_db_write_allowed = $false
            user_projects_write_allowed = $false
            databank_delete_allowed = $false
            tag_csv_only = $true
        }
    }
    $evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $backupDir "rollback_manifest.json") -Encoding UTF8
    $evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $LocalRoot "$Version`_install_$stamp.json") -Encoding UTF8
    $evidence | ConvertTo-Json -Depth 5
}

function Resolve-BackupDir {
    if ($BackupId.Trim()) {
        $candidate = Join-Path $BackupRoot $BackupId
        if (Test-Path -LiteralPath $candidate -PathType Container) { return $candidate }
        throw "BackupId not found: $BackupId"
    }
    $latest = Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) { throw "No data smoke backup available for rollback." }
    return $latest.FullName
}

function Invoke-Rollback {
    Assert-NoSqxProcess
    Assert-TargetAllowed $TargetCsv
    $backupDir = Resolve-BackupDir
    $manifest = Get-Content -LiteralPath (Join-Path $backupDir "rollback_manifest.json") -Raw | ConvertFrom-Json
    $backupCsv = Join-Path $backupDir "correlation_decisions.csv"
    if ($manifest.existed -eq $true) {
        Copy-Item -LiteralPath $backupCsv -Destination $TargetCsv -Force
        $actionTaken = "restored"
    } elseif (Test-Path -LiteralPath $TargetCsv -PathType Leaf) {
        Remove-Item -LiteralPath $TargetCsv -Force
        $actionTaken = "removed_installed_file"
    } else {
        $actionTaken = "already_absent"
    }
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "rollback"
        backupId = Split-Path -Leaf $backupDir
        result = $actionTaken
        target = Get-CsvSummary $TargetCsv
    } | ConvertTo-Json -Depth 5
}

switch ($Action) {
    "status" { Invoke-Status }
    "build" { Invoke-Build }
    "install" { Invoke-Install }
    "rollback" { Invoke-Rollback }
}
