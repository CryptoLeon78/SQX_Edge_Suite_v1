param(
    [ValidateSet("status", "plan", "apply", "rollback", "record")]
    [string]$Action = "status",
    [string]$SQXRoot = $env:SQX142_ROOT,
    [string]$ProjectKey = "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1",
    [string]$DbPath = "",
    [string]$BackupId = "",
    [switch]$SkipProcessGuard
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonExe = Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"
$ToolPy = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_portfolio_corr2_local_project_integration.py"
$DefaultDb = Join-Path $RepoRoot ".local\sqx142_mining_registry\sqx142_mining_registry.sqlite"

if (-not $DbPath.Trim()) {
    $DbPath = $DefaultDb
}

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    $PythonExe = "python"
}

function Assert-NoSqxProcess {
    param([string]$Root)
    $processes = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match 'StrategyQuant|sqcli|CodeEditor|electron|javaw?|SQUANT' -and
        (([string]$_.CommandLine) -match 'StrategyQuant|SQX|SQUANT' -or ([string]$_.CommandLine) -like "*$Root*")
    } | Select-Object ProcessId, Name
    if ($processes) {
        $names = ($processes | ForEach-Object { "$($_.Name):$($_.ProcessId)" }) -join ", "
        throw "SQX runtime appears open. Close SQX before $Action. Processes: $names"
    }
}

if (($Action -eq "apply" -or $Action -eq "rollback") -and -not $SkipProcessGuard) {
    Assert-NoSqxProcess -Root $SQXRoot
}

$argsList = @(
    $ToolPy,
    "--action", $Action,
    "--sqx-root", $SQXRoot,
    "--project-key", $ProjectKey,
    "--db", $DbPath
)

if ($BackupId.Trim()) { $argsList += @("--backup-id", $BackupId) }
if ($SkipProcessGuard) { $argsList += "--skip-process-guard" }

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
