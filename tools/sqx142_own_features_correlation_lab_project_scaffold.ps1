param(
    [ValidateSet("status", "plan", "install", "rollback")]
    [string]$Action = "status",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$DonorProjectName = "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1",
    [string]$TargetProjectName = "SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527",
    [string]$BackupId = ""
)

$ErrorActionPreference = "Stop"

$Version = "sqx142-own-features3b-correlation-lab-project-scaffold-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonExe = Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"
$ToolPy = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_correlation_lab_project_scaffold.py"

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

function Assert-Tooling {
    if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
        throw "Backend venv python not found: $PythonExe"
    }
    if (-not (Test-Path -LiteralPath $ToolPy -PathType Leaf)) {
        throw "Lab project scaffold tool missing: $ToolPy"
    }
}

if ($Action -eq "install" -or $Action -eq "rollback") {
    Assert-NoSqxProcess
}
Assert-Tooling

$argsList = @(
    $ToolPy,
    "--action", $Action,
    "--sqx-root", $SqxRoot,
    "--donor-project", $DonorProjectName,
    "--target-project", $TargetProjectName
)

if ($BackupId.Trim()) {
    $argsList += @("--backup-id", $BackupId)
}

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
    throw "$Version failed with exit code $LASTEXITCODE"
}
