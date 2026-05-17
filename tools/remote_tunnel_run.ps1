[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$CloudflaredPath = "cloudflared",
    [string]$CloudflaredConfig = "",
    [string]$TunnelName = "",
    [switch]$SkipPreflight
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
    if ($null -eq $cmd) { return $null }
    return $cmd.Source
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
if ([string]::IsNullOrWhiteSpace($CloudflaredConfig)) {
    $CloudflaredConfig = Join-Path $repo ".local\remote_service\cloudflared-config.local.yml"
}
$preflight = Join-Path $repo "tools\remote_tunnel_preflight.ps1"
$cloudflared = Resolve-Cloudflared $CloudflaredPath

if (-not $cloudflared) {
    throw "cloudflared is not available. Install Cloudflare Tunnel CLI locally before running REMOTE-2 tunnel."
}
if (-not (Test-Path -LiteralPath $CloudflaredConfig)) {
    throw "Missing local cloudflared config: $CloudflaredConfig"
}
if (-not $SkipPreflight) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $preflight -RepoRoot $repo -CloudflaredPath $cloudflared -RequireEvidence
    if ($LASTEXITCODE -ne 0) {
        throw "REMOTE-2 preflight did not return GO. Tunnel run blocked."
    }
}

$cloudflaredArgs = @("tunnel", "--config", $CloudflaredConfig, "run")
if (-not [string]::IsNullOrWhiteSpace($TunnelName)) {
    $cloudflaredArgs += $TunnelName
}

Write-Host "Starting Cloudflare Tunnel for REMOTE-2"
Write-Host "  Config: $CloudflaredConfig"
Write-Host "  Target must remain http://127.0.0.1:5050 behind Cloudflare Access."
& $cloudflared @cloudflaredArgs
exit $LASTEXITCODE
