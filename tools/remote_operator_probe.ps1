[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$OutFile = "",
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

function Get-OllamaStatus {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/agent/status" -TimeoutSec 8
        $provider = $payload.provider
        $autoStart = if ($provider) { $provider.autoStart } else { $null }
        $model = if ($provider -and $provider.model) { [string]$provider.model } elseif ($provider -and $provider.configuredModel) { [string]$provider.configuredModel } else { "modelo local" }
        $autoReason = if ($autoStart -and $autoStart.reason) { [string]$autoStart.reason } else { "" }
        $detail = if ($autoStart -and [bool]$autoStart.attempted -and $autoReason) { " - autostart: $autoReason" } else { "" }
        return [ordered]@{
            ok = [bool]$payload.active
            model = $model
            autoStart = $autoStart
            text = if ([bool]$payload.active) { "OK - Ollama activo ($model)$detail" } else { "NO-GO - Ollama no disponible ($model)$detail" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            model = $null
            autoStart = $null
            text = "NO-GO - Ollama/IA no comprobable"
        }
    }
}

function Get-SQXCompatStatus {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/sqx142/compat/status" -TimeoutSec 4
        $procCount = if ($payload.processes -and $null -ne $payload.processes.count) { [int]$payload.processes.count } else { 0 }
        return [ordered]@{
            ok = [bool]$payload.ok
            status = if ($payload.status) { [string]$payload.status } else { "unknown" }
            processCount = $procCount
            text = if ([bool]$payload.ok) { "OK - SQX 142 runtime alineado" } else { "WARN - SQX 142 $($payload.status) - procesos: $procCount" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            status = "pending"
            processCount = 0
            text = "Pendiente - backend requerido para comprobar SQX 142"
        }
    }
}

function Get-SQXPerformanceStatus {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/sqx142/performance/status" -TimeoutSec 6
        $profile = if ($payload.activeProfile -and $payload.activeProfile.id) { [string]$payload.activeProfile.id } else { "unknown" }
        $disk = if ($payload.resources -and $payload.resources.disk -and $payload.resources.disk.freeHuman) { [string]$payload.resources.disk.freeHuman } else { "" }
        $intelligence = if ($payload.intelligence) { $payload.intelligence } else { $null }
        $views = if ($intelligence -and $intelligence.views) { $intelligence.views } else { $null }
        $latest = if ($intelligence -and $intelligence.latestEvidence) { $intelligence.latestEvidence } elseif ($payload.latestEvidence) { $payload.latestEvidence } else { $null }
        $recommendation = if ($intelligence -and $intelligence.recommendation) { $intelligence.recommendation } else { $null }
        $liveGuard = if ($intelligence -and $intelligence.liveGuard) { $intelligence.liveGuard } else { $null }
        $viewsText = if ($views -and $null -ne $views.presentCount -and $null -ne $views.expectedCount) { "views $($views.presentCount)/$($views.expectedCount)" } else { "views ?" }
        $latestEvidence = if ($latest -and $latest.filename) { [string]$latest.filename } else { "sin evidencia" }
        $next = if ($recommendation -and $recommendation.label) { [string]$recommendation.label } else { "sin recomendacion" }
        $guardText = if ($liveGuard -and $liveGuard.state) { "guard $($liveGuard.state)/alerts:$($liveGuard.alertCount)" } else { "guard ?" }
        return [ordered]@{
            ok = [bool]$payload.ok
            status = if ($payload.status) { [string]$payload.status } else { "unknown" }
            profile = $profile
            diskFree = $disk
            views = $viewsText
            latestEvidence = $latestEvidence
            liveGuard = $guardText
            recommendation = $next
            text = if ([bool]$payload.ok) { "OK - rendimiento SQX 142 ($profile) - $viewsText - $guardText - next: $next" } else { "WARN - rendimiento SQX 142 $($payload.status) ($profile) - $viewsText - $guardText - next: $next" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            status = "pending"
            profile = "unknown"
            diskFree = ""
            views = "views ?"
            latestEvidence = "sin evidencia"
            liveGuard = "guard ?"
            recommendation = "backend requerido"
            text = "Pendiente - backend requerido para comprobar rendimiento SQX 142"
        }
    }
}

$backend = Test-BackendHealth
$tunnel = Get-TunnelStatus
$ollama = if ([bool]$backend.ok) { Get-OllamaStatus } else { [ordered]@{ ok = $false; model = $null; autoStart = $null; text = "Pendiente - backend requerido para comprobar Ollama" } }
$sqxCompat = if ([bool]$backend.ok) { Get-SQXCompatStatus } else { [ordered]@{ ok = $false; status = "pending"; processCount = 0; text = "Pendiente - backend requerido para comprobar SQX 142" } }
$sqxPerf = if ([bool]$backend.ok) { Get-SQXPerformanceStatus } else { [ordered]@{ ok = $false; status = "pending"; profile = "unknown"; diskFree = ""; text = "Pendiente - backend requerido para comprobar rendimiento SQX 142" } }
$result = [ordered]@{
    ok = [bool]($backend.ok -and $tunnel.ok -and $ollama.ok)
    backend = $backend
    tunnel = $tunnel
    ollama = $ollama
    sqx142Compat = $sqxCompat
    sqx142Performance = $sqxPerf
    checkedAt = (Get-Date).ToString("s")
}

$jsonPayload = $result | ConvertTo-Json -Depth 5 -Compress

if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
    $outDir = Split-Path -Parent $OutFile
    if (-not [string]::IsNullOrWhiteSpace($outDir)) {
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    }
    $tmp = "$OutFile.tmp"
    Set-Content -LiteralPath $tmp -Value $jsonPayload -Encoding UTF8
    Move-Item -LiteralPath $tmp -Destination $OutFile -Force
}

if ($Json) {
    $jsonPayload
} else {
    Write-Host "Backend: $($backend.text)"
    Write-Host "Tunnel: $($tunnel.text)"
    Write-Host "Ollama: $($ollama.text)"
    Write-Host "SQX142: $($sqxCompat.text)"
    Write-Host "SQX142 Performance: $($sqxPerf.text)"
}
