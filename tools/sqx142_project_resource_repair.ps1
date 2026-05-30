param(
    [ValidateSet("plan", "repair", "rebuild-capa1", "repair-capa2-config", "rebuild-capa2", "rollback")]
    [string]$Action = "plan",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$BackupId = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"
$Tool = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_project_resource_repair.py"

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

if ($Action -in @("repair", "rebuild-capa1", "repair-capa2-config", "rebuild-capa2", "rollback")) {
    Assert-NoSqxProcess
}

$argsList = @($Tool, "--action", $Action, "--sqx-root", $SqxRoot, "--repo-root", $RepoRoot)
if ($BackupId.Trim()) {
    $argsList += @("--backup-id", $BackupId)
}

& $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "sqx142 project resource repair failed with exit code $LASTEXITCODE"
}
