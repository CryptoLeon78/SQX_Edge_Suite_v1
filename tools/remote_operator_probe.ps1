[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Test-BackendHealth {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/health" -TimeoutSec 2
        return [ordered]@{
            ok = [bool]$payload.ok
            text = if ([bool]$payload.ok) { "OK - backend activo en 127.0.0.1:5050" } else { "NO-GO - backend responde sin OK" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            text = "NO-GO - backend no responde"
        }
    }
}

function Get-TunnelStatus {
    try {
        $process = Get-CimInstance Win32_Process -Filter "Name = 'cloudflared.exe'" -ErrorAction SilentlyContinue |
            Where-Object {
                $_.CommandLine -and (
                    $_.CommandLine -like "*cloudflared-config.local.yml*" -or
                    $_.CommandLine -like "*.local*remote_service*cloudflared-config.local.yml*"
                )
            } |
            Select-Object -First 1

        if ($null -ne $process) {
            return [ordered]@{
                ok = $true
                processId = [int]$process.ProcessId
                text = "OK - tunel Cloudflare activo (PID $($process.ProcessId))"
            }
        }
        return [ordered]@{
            ok = $false
            processId = $null
            text = "NO-GO - tunel no detectado"
        }
    } catch {
        return [ordered]@{
            ok = $false
            processId = $null
            text = "NO-GO - tunel no comprobable: $($_.Exception.Message)"
        }
    }
}

$backend = Test-BackendHealth
$tunnel = Get-TunnelStatus
$result = [ordered]@{
    ok = [bool]($backend.ok -and $tunnel.ok)
    backend = $backend
    tunnel = $tunnel
}

if ($Json) {
    $result | ConvertTo-Json -Depth 5 -Compress
} else {
    Write-Host "Backend: $($backend.text)"
    Write-Host "Tunnel: $($tunnel.text)"
}
