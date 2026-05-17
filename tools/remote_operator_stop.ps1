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
    param([string]$Url)
    try {
        $payload = Invoke-RestMethod -Uri $Url -TimeoutSec 2
        return [bool]$payload.ok
    } catch {
        return $false
    }
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$serverPy = Join-Path $repo "backend\sqx-edge-tool\api\server.py"
$healthUrl = "http://127.0.0.1:5050/api/health"
$stopped = @()

$processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -and (
            ($_.Name -eq "python.exe" -and $_.CommandLine -like "*$serverPy*") -or
            ($_.Name -eq "powershell.exe" -and $_.CommandLine -like "*remote_service_start_server.ps1*" -and $_.CommandLine -like "*$repo*") -or
            ($_.Name -eq "cloudflared.exe" -and $_.CommandLine -like "*cloudflared-config.local.yml*")
        )
    }

foreach ($proc in $processes) {
    try {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
        $stopped += [ordered]@{
            processId = [int]$proc.ProcessId
            name = $proc.Name
            stopped = $true
        }
    } catch {
        $stopped += [ordered]@{
            processId = [int]$proc.ProcessId
            name = $proc.Name
            stopped = $false
            error = $_.Exception.Message
        }
    }
}

Start-Sleep -Seconds 2
$backendStillHealthy = Test-BackendHealth $healthUrl
$tunnelStillRunning = [bool](Get-CimInstance Win32_Process -Filter "Name = 'cloudflared.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -like "*cloudflared-config.local.yml*" } |
    Select-Object -First 1)

$result = [ordered]@{
    ok = [bool](-not $backendStillHealthy -and -not $tunnelStillRunning)
    phase = "REMOTE-RUNBOOK1"
    repoRoot = $repo
    stopped = $stopped
    backend = [ordered]@{
        url = $healthUrl
        stillHealthy = $backendStillHealthy
    }
    tunnel = [ordered]@{
        stillRunning = $tunnelStillRunning
    }
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host ""
    Write-Host "SQX Edge Suite REMOTE operator stop"
    Write-Host "  Procesos cerrados: $($stopped.Count)"
    Write-Host "  Backend sigue vivo: $backendStillHealthy"
    Write-Host "  Tunel sigue vivo:   $tunnelStillRunning"
    Write-Host ""
    if ($result.ok) {
        Write-Host "OK: servicio remoto detenido."
    } else {
        Write-Host "ATENCION: queda algun proceso activo. Revisa los procesos antes de dar servicio."
    }
}

if (-not $result.ok) {
    exit 2
}
