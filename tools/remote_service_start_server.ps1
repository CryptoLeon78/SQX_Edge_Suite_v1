[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 5050
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

if ($HostAddress -ne "127.0.0.1" -and $HostAddress -ne "localhost") {
    throw "REMOTE-1 only allows localhost API binding. Refusing HostAddress=$HostAddress"
}

function Resolve-PythonRuntime {
    param([string]$ToolRoot)
    $embeddedPython = Join-Path $ToolRoot "runtime\python\python.exe"
    $venvPython = Join-Path $ToolRoot "venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $embeddedPython) { return $embeddedPython }
    if (Test-Path -LiteralPath $venvPython) { return $venvPython }
    return "python"
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$toolRoot = Join-Path $repo "backend\sqx-edge-tool"
$serverPy = Join-Path $toolRoot "api\server.py"
$python = Resolve-PythonRuntime $toolRoot
$healthUrl = "http://$HostAddress`:$Port/api/health"

if (-not (Test-Path -LiteralPath $serverPy)) {
    throw "Cannot find server.py at $serverPy"
}

try {
    $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
    if ($health.ok) {
        Write-Host "SQX Edge API is already healthy at $healthUrl"
        exit 0
    }
} catch {
    # Not running yet; continue with controlled local start.
}

$env:SQX_REMOTE_SERVICE_MODE = "remote-1-laptop-server-baseline"
$env:SQX_REMOTE_SERVICE_REPO_ROOT = $repo

Write-Host "Starting SQX Edge API for REMOTE-1 laptop server baseline"
Write-Host "  Repo: $repo"
Write-Host "  API:  $healthUrl"
Write-Host "  Bind: $HostAddress only"

Push-Location $toolRoot
try {
    & $python $serverPy --host $HostAddress --port $Port
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
