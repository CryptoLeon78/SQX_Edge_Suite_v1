[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$CloudflaredPath = "C:\Tools\cloudflared\cloudflared.exe",
    [int]$WaitSeconds = 45,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Resolve-Cloudflared {
    param([string]$Value)
    if ([System.IO.Path]::IsPathRooted($Value) -and (Test-Path -LiteralPath $Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    $cmd = Get-Command $Value -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return $cmd.Source }

    $fallback = "C:\Tools\cloudflared\cloudflared.exe"
    if (Test-Path -LiteralPath $fallback) {
        return $fallback
    }
    return $null
}

function Test-BackendHealth {
    param([string]$Url)
    try {
        $payload = Invoke-RestMethod -Uri $Url -TimeoutSec 2
        return [ordered]@{
            ok = [bool]$payload.ok
            reachable = $true
            error = $null
            payload = $payload
        }
    } catch {
        return [ordered]@{
            ok = $false
            reachable = $false
            error = $_.Exception.Message
            payload = $null
        }
    }
}

function Get-TunnelProcess {
    param([string]$ConfigName)
    $escaped = $ConfigName.Replace("\", "\\")
    return Get-CimInstance Win32_Process -Filter "Name = 'cloudflared.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -and (
                $_.CommandLine -like "*$ConfigName*" -or
                $_.CommandLine -match [regex]::Escape($ConfigName) -or
                $_.CommandLine -match [regex]::Escape($escaped)
            )
        } |
        Select-Object -First 1
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$localDir = Join-Path $repo ".local\remote_service"
$backendStart = Join-Path $repo "tools\remote_service_start_server.ps1"
$tunnelRun = Join-Path $repo "tools\remote_tunnel_run.ps1"
$tunnelConfig = Join-Path $repo ".local\remote_service\cloudflared-config.local.yml"
$healthUrl = "http://127.0.0.1:5050/api/health"
$cloudflared = Resolve-Cloudflared $CloudflaredPath
$runStamp = Get-Date -Format "yyyyMMdd-HHmmssfff"

New-Item -ItemType Directory -Force -Path $localDir | Out-Null

if (-not (Test-Path -LiteralPath $backendStart)) {
    throw "Missing backend start script: $backendStart"
}
if (-not (Test-Path -LiteralPath $tunnelRun)) {
    throw "Missing tunnel runner script: $tunnelRun"
}
if (-not (Test-Path -LiteralPath $tunnelConfig)) {
    throw "Missing local-only Cloudflare config: $tunnelConfig"
}
if (-not $cloudflared) {
    throw "cloudflared is not available. Expected C:\Tools\cloudflared\cloudflared.exe or cloudflared in PATH."
}

$startedBackend = $false
$startedTunnel = $false
$backendHealth = Test-BackendHealth $healthUrl

if (-not $backendHealth.ok) {
    $backendOut = Join-Path $localDir "remote_operator_backend_$runStamp.out.log"
    $backendErr = Join-Path $localDir "remote_operator_backend_$runStamp.err.log"
    $backendArgs = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$backendStart`"",
        "-RepoRoot", "`"$repo`"",
        "-HostAddress", "127.0.0.1",
        "-Port", "5050"
    )
    $process = Start-Process -FilePath "powershell.exe" `
        -ArgumentList $backendArgs `
        -WorkingDirectory $repo `
        -WindowStyle Hidden `
        -RedirectStandardOutput $backendOut `
        -RedirectStandardError $backendErr `
        -PassThru
    $startedBackend = $true
    Set-Content -LiteralPath (Join-Path $localDir "remote_operator_backend.pid") -Value $process.Id -Encoding ASCII
}

$deadline = (Get-Date).AddSeconds($WaitSeconds)
do {
    $backendHealth = Test-BackendHealth $healthUrl
    if ($backendHealth.ok) { break }
    Start-Sleep -Seconds 1
} while ((Get-Date) -lt $deadline)

if (-not $backendHealth.ok) {
    throw "Backend did not become healthy at $healthUrl within $WaitSeconds seconds."
}

$tunnelProcess = Get-TunnelProcess "cloudflared-config.local.yml"
if ($null -eq $tunnelProcess) {
    $tunnelOut = Join-Path $localDir "remote_operator_tunnel_$runStamp.out.log"
    $tunnelErr = Join-Path $localDir "remote_operator_tunnel_$runStamp.err.log"
    $tunnelArgs = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$tunnelRun`"",
        "-RepoRoot", "`"$repo`"",
        "-CloudflaredPath", "`"$cloudflared`"",
        "-CloudflaredConfig", "`"$tunnelConfig`""
    )
    $process = Start-Process -FilePath "powershell.exe" `
        -ArgumentList $tunnelArgs `
        -WorkingDirectory $repo `
        -WindowStyle Hidden `
        -RedirectStandardOutput $tunnelOut `
        -RedirectStandardError $tunnelErr `
        -PassThru
    $startedTunnel = $true
    Set-Content -LiteralPath (Join-Path $localDir "remote_operator_tunnel.pid") -Value $process.Id -Encoding ASCII

    Start-Sleep -Seconds 5
    $tunnelProcess = Get-TunnelProcess "cloudflared-config.local.yml"
}

$result = [ordered]@{
    ok = [bool]($backendHealth.ok -and $null -ne $tunnelProcess)
    phase = "REMOTE-RUNBOOK1"
    repoRoot = $repo
    backend = [ordered]@{
        url = $healthUrl
        ok = [bool]$backendHealth.ok
        startedByRunbook = $startedBackend
    }
    tunnel = [ordered]@{
        ok = [bool]($null -ne $tunnelProcess)
        processId = if ($null -ne $tunnelProcess) { [int]$tunnelProcess.ProcessId } else { $null }
        startedByRunbook = $startedTunnel
        config = ".local/remote_service/cloudflared-config.local.yml"
    }
    logs = [ordered]@{
        pattern = ".local/remote_service/remote_operator_*.log"
    }
    nextStep = "Open the protected Cloudflare URL privately and run REMOTE-ACCEPT1 browser evidence."
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host ""
    Write-Host "SQX Edge Suite REMOTE operator start"
    Write-Host "  Backend: $($result.backend.ok)  $healthUrl"
    Write-Host "  Tunnel:  $($result.tunnel.ok)  cloudflared process $($result.tunnel.processId)"
    Write-Host "  Logs:    .local\remote_service\remote_operator_*.log"
    Write-Host ""
    if ($result.ok) {
        Write-Host "OK: servicio remoto listo para abrir el enlace protegido."
    } else {
        Write-Host "NO-GO: backend o tunel no quedaron listos."
    }
}

if (-not $result.ok) {
    exit 2
}
