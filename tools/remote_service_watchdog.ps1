[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ApiUrl = "http://127.0.0.1:5050/api/health",
    [int]$IntervalSeconds = 30,
    [int]$MaxRestarts = 3,
    [switch]$Once,
    [switch]$NoStart,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Test-LocalApiUrl {
    param([string]$Url)
    return $Url -match '^http://(127\.0\.0\.1|localhost)(:\d+)?/'
}

function Write-RemoteServiceLog {
    param(
        [string]$LogPath,
        [string]$Message
    )
    $line = "$(Get-Date -Format o) $Message"
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

function Test-RemoteServiceHealth {
    param([string]$Url)
    try {
        $payload = Invoke-RestMethod -Uri $Url -TimeoutSec 2
        return [ordered]@{
            reachable = $true
            ok = [bool]$payload.ok
            error = $null
            payload = $payload
        }
    } catch {
        return [ordered]@{
            reachable = $false
            ok = $false
            error = $_.Exception.Message
            payload = $null
        }
    }
}

if (-not (Test-LocalApiUrl $ApiUrl)) {
    throw "REMOTE-1 watchdog only accepts localhost API URLs. Refusing ApiUrl=$ApiUrl"
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$localDir = Join-Path $repo ".local\remote_service"
$logPath = Join-Path $localDir "watchdog.log"
$startScript = Join-Path $repo "tools\remote_service_start_server.ps1"
New-Item -ItemType Directory -Force -Path $localDir | Out-Null

if (-not (Test-Path -LiteralPath $startScript)) {
    throw "Cannot find remote service start script at $startScript"
}

$restartCount = 0
$events = @()

do {
    $health = Test-RemoteServiceHealth $ApiUrl
    $action = "healthy"

    if (-not [bool]$health.ok) {
        if ($NoStart) {
            $action = "unhealthy_no_start"
        } elseif ($restartCount -ge $MaxRestarts) {
            $action = "unhealthy_max_restarts_reached"
        } else {
            $restartCount += 1
            $action = "restart_$restartCount"
            $arguments = @(
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", "`"$startScript`"",
                "-RepoRoot", "`"$repo`"",
                "-HostAddress", "127.0.0.1",
                "-Port", "5050"
            )
            Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -WindowStyle Hidden
            Start-Sleep -Seconds 4
            $health = Test-RemoteServiceHealth $ApiUrl
        }
    }

    $event = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        action = $action
        restartCount = $restartCount
        health = $health
    }
    $events += $event
    Write-RemoteServiceLog $logPath ("action=$action restartCount=$restartCount ok=$($health.ok) reachable=$($health.reachable)")

    if (-not $Once) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while (-not $Once)

$result = [ordered]@{
    ok = [bool]$events[-1].health.ok
    phase = "REMOTE-1"
    mode = "laptop_server_watchdog"
    apiUrl = $ApiUrl
    repoRoot = $repo
    noStart = [bool]$NoStart
    maxRestarts = $MaxRestarts
    restartCount = $restartCount
    logPath = $logPath
    events = $events
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host "REMOTE-1 watchdog"
    Write-Host "  OK: $($result.ok)"
    Write-Host "  Restarts: $restartCount"
    Write-Host "  Log: $logPath"
}

if (-not $result.ok -and $NoStart) {
    exit 2
}
