param(
    [ValidateSet("status", "plan", "stabilize", "rollback", "clear-ui-cache")]
    [string]$Action = "plan",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string[]]$Project = @(),
    [string]$BackupId = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonCandidates = @(
    (Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"),
    (Join-Path $RepoRoot "backend\sqx-edge-tool\runtime\python\python.exe"),
    "python"
)
$Tool = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_project_load_stabilizer.py"

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

if ($Action -in @("stabilize", "rollback", "clear-ui-cache")) {
    Assert-NoSqxProcess
}

$Python = $null
foreach ($candidate in $PythonCandidates) {
    if ($candidate -eq "python") {
        $Python = $candidate
        break
    }
    if (Test-Path -LiteralPath $candidate) {
        $Python = $candidate
        break
    }
}

if (-not (Test-Path -LiteralPath $Tool)) {
    throw "SQX142 project load stabilizer tool not found: $Tool"
}

$argsList = @($Tool, "--action", $Action, "--sqx-root", $SqxRoot, "--repo-root", $RepoRoot)
foreach ($name in $Project) {
    if (-not [string]::IsNullOrWhiteSpace($name)) {
        $argsList += @("--project", $name)
    }
}
if (-not [string]::IsNullOrWhiteSpace($BackupId)) {
    $argsList += @("--backup-id", $BackupId)
}

& $Python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "sqx142 project load stabilizer failed with exit code $LASTEXITCODE"
}
