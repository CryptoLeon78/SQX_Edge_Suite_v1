[CmdletBinding()]
param(
    [string]$SQXRoot = "C:\BOTS\Versiones\SQX_142_Crack",
    [switch]$Restart,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Get-SQXProcesses {
    param([string]$Root)
    $normalized = [System.IO.Path]::GetFullPath($Root).TrimEnd("\")
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -like "StrategyQuantX*" -and
            $_.CommandLine -and
            $_.CommandLine.Replace("/", "\").IndexOf($normalized, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
        }
}

function Stop-SQXProcesses {
    param([object[]]$Processes)
    foreach ($proc in $Processes) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
        } catch {
            Write-Warning "Could not stop SQX process $($proc.ProcessId): $($_.Exception.Message)"
        }
    }
}

$root = [System.IO.Path]::GetFullPath($SQXRoot)
$exe = Join-Path $root "StrategyQuantX_nocheck.exe"
$userData = Join-Path $root "internal\electron\resources\userData\SQUANT"
$expectedUserData = [System.IO.Path]::GetFullPath($userData).TrimEnd("\")

if (-not (Test-Path -LiteralPath $exe)) {
    throw "Missing SQX executable: $exe"
}
if (-not (Test-Path -LiteralPath $expectedUserData)) {
    throw "Missing Electron userData path: $expectedUserData"
}

$running = @(Get-SQXProcesses -Root $root)
if ($running.Count -gt 0) {
    if (-not $Restart) {
        throw "SQX is running. Close it first, or rerun with -Restart to stop SQX, refresh Electron cache, and start it again."
    }
    Stop-SQXProcesses -Processes $running
    Start-Sleep -Seconds 3
}

$backupRoot = Join-Path $root (".local_cache_backups\electron_squant_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null

$cacheNames = @(
    "Cache",
    "Code Cache",
    "GPUCache",
    "DawnCache",
    "blob_storage",
    "Network",
    "Session Storage",
    "Shared Dictionary"
)

$moved = @()
foreach ($name in $cacheNames) {
    $src = Join-Path $expectedUserData $name
    if (-not (Test-Path -LiteralPath $src)) {
        continue
    }
    $resolved = [System.IO.Path]::GetFullPath($src)
    if (-not $resolved.StartsWith($expectedUserData, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to move outside Electron userData: $resolved"
    }
    Move-Item -LiteralPath $src -Destination (Join-Path $backupRoot $name) -Force
    $moved += $name
}

$startedPid = $null
if ($Restart) {
    $started = Start-Process -FilePath $exe -WorkingDirectory $root -PassThru
    $startedPid = $started.Id
}

$result = [ordered]@{
    ok = $true
    sqxRoot = $root
    userData = $expectedUserData
    backupRoot = $backupRoot
    moved = $moved
    restarted = [bool]$Restart
    startedPid = $startedPid
}

if ($Json) {
    $result | ConvertTo-Json -Depth 5
} else {
    Write-Host "SQX 142 Electron cache refreshed."
    Write-Host "  Backup: $backupRoot"
    Write-Host "  Moved:  $($moved -join ', ')"
    if ($Restart) {
        Write-Host "  Restarted SQX PID: $startedPid"
    }
}
