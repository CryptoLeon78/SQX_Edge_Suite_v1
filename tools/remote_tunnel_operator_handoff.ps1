[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$CloudflaredPath = "cloudflared",
    [string]$TunnelName = "sqx-edge-remote-pilot",
    [string]$ProtectedHostname = "",
    [string]$LocalServiceUrl = "http://127.0.0.1:5050",
    [string]$EvidencePath = "",
    [string]$HandoffPath = "",
    [string]$ConfigTemplatePath = "",
    [switch]$LaunchLogin,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Resolve-Cloudflared {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Value) -and (Test-Path -LiteralPath $Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    $cmd = Get-Command $Value -ErrorAction SilentlyContinue
    if ($null -eq $cmd) { return $null }
    return $cmd.Source
}

function Test-LocalHttpUrl {
    param([string]$Url)
    return $Url -match '^http://(127\.0\.0\.1|localhost)(:\d+)?(/|$)'
}

function Get-OriginCertCandidates {
    $items = @()
    if (-not [string]::IsNullOrWhiteSpace($env:TUNNEL_ORIGIN_CERT)) {
        $items += $env:TUNNEL_ORIGIN_CERT
    }
    $items += (Join-Path $HOME ".cloudflared\cert.pem")
    $items += (Join-Path $HOME ".cloudflare-warp\cert.pem")
    $items += (Join-Path $HOME "cloudflare-warp\cert.pem")
    return $items
}

function Get-CloudflaredVersion {
    param([string]$Path)
    if (-not $Path) { return $null }
    try {
        return (& $Path --version 2>$null | Select-Object -First 1)
    } catch {
        return $null
    }
}

function Write-Utf8File {
    param(
        [string]$Path,
        [string]$Content
    )
    New-Item -ItemType Directory -Path (Split-Path $Path) -Force | Out-Null
    Set-Content -Path $Path -Value $Content -Encoding UTF8
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$localRoot = Join-Path $repo ".local\remote_service"
New-Item -ItemType Directory -Path $localRoot -Force | Out-Null

if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
    $EvidencePath = Join-Path $localRoot "cloudflare_tunnel.local.json"
}
if ([string]::IsNullOrWhiteSpace($HandoffPath)) {
    $HandoffPath = Join-Path $localRoot "cloudflare_tunnel_operator_handoff.local.md"
}
if ([string]::IsNullOrWhiteSpace($ConfigTemplatePath)) {
    $ConfigTemplatePath = Join-Path $localRoot "cloudflared-config.local.yml.template"
}

$cloudflared = Resolve-Cloudflared $CloudflaredPath
$cloudflaredVersion = Get-CloudflaredVersion $cloudflared
$originCertCandidates = Get-OriginCertCandidates
$originCert = $originCertCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
$originCertPresent = -not [string]::IsNullOrWhiteSpace($originCert)
$hostnamePlaceholder = if ([string]::IsNullOrWhiteSpace($ProtectedHostname)) { "<private-protected-hostname>" } else { $ProtectedHostname.Trim() }
$cloudflaredDisplay = if ($cloudflared) { $cloudflared } else { "cloudflared" }
$cloudflaredCmd = if ($cloudflaredDisplay -match '\s') { "& `"$cloudflaredDisplay`"" } else { "& $cloudflaredDisplay" }

if (-not (Test-Path -LiteralPath $EvidencePath)) {
    $example = Join-Path $repo "docs\examples\remote_tunnel.local.example.json"
    if (Test-Path -LiteralPath $example) {
        Copy-Item -LiteralPath $example -Destination $EvidencePath -Force
    }
}

$configTemplate = @"
tunnel: <TUNNEL-UUID-OR-NAME>
credentials-file: <FULL-PATH-TO-TUNNEL-CREDENTIALS-JSON>

ingress:
  - hostname: $hostnamePlaceholder
    service: $LocalServiceUrl
  - service: http_status:404
"@
Write-Utf8File -Path $ConfigTemplatePath -Content $configTemplate

$handoff = @"
# REMOTE-OPS1B Cloudflare Operator Handoff

This local file is ignored by Git. It may contain private operational notes, but do not paste secrets unless they are needed for your own local execution.

## Current Local Status

- cloudflared detected: $([bool]$cloudflared)
- cloudflared version: $cloudflaredVersion
- origin cert present: $originCertPresent
- local service target: $LocalServiceUrl
- tunnel evidence file: $EvidencePath
- config template file: $ConfigTemplatePath

## Safe Operator Sequence

1. Authenticate cloudflared if origin cert present is false:

~~~powershell
$cloudflaredCmd tunnel login
~~~

2. Create or reuse one named tunnel:

~~~powershell
$cloudflaredCmd tunnel create $TunnelName
$cloudflaredCmd tunnel list
~~~

3. Route the protected hostname to the tunnel:

~~~powershell
$cloudflaredCmd tunnel route dns $TunnelName <private-protected-hostname>
~~~

4. Create the real ignored config from the generated template:

~~~powershell
Copy-Item "$ConfigTemplatePath" ".local\remote_service\cloudflared-config.local.yml"
notepad ".local\remote_service\cloudflared-config.local.yml"
~~~

Replace `<TUNNEL-UUID-OR-NAME>`, `<FULL-PATH-TO-TUNNEL-CREDENTIALS-JSON>` and `<private-protected-hostname>`.

5. In Cloudflare Zero Trust, create a self-hosted Access application for the same hostname. Policy must allow only approved tester/operator identities.

6. Run private preflight and anonymous Access smoke:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_preflight.ps1 -CloudflaredPath "$cloudflaredDisplay" -RequireEvidence
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_smoke.ps1 -ProtectedUrl "https://<private-protected-hostname>"
~~~

7. Flip only boolean evidence in .local\remote_service\cloudflare_tunnel.local.json.

8. Re-run REMOTE-OPS1:

~~~powershell
python backend\sqx-edge-tool\tools\remote_ops1_laptop_readiness.py --evidence .local\remote_service\remote_ops1_laptop_readiness.local.json --out-dir .local\remote_service\remote_ops1_laptop_readiness
~~~

## GO Boundary

Do not share tester links until:

- remote_tunnel_preflight.ps1 -RequireEvidence returns GO_REMOTE2_TUNNEL_ACCESS_READY_NO_GIT_LEAK.
- remote_tunnel_smoke.ps1 proves anonymous users see Cloudflare Access, not SQX Edge.
- remote_ops1_laptop_readiness.py returns GO_REMOTE_OPS1_LAPTOP_READY.
"@
Write-Utf8File -Path $HandoffPath -Content $handoff

if ($LaunchLogin) {
    if (-not $cloudflared) {
        throw "cloudflared is not available; cannot launch login."
    }
    & $cloudflared tunnel login
}

$result = [ordered]@{
    ok = $true
    phase = "REMOTE-OPS1B"
    mode = "cloudflare_operator_handoff"
    cloudflaredDetected = [bool]$cloudflared
    cloudflaredVersion = $cloudflaredVersion
    originCertPresentPrivately = [bool]$originCertPresent
    localServiceUrlSafe = Test-LocalHttpUrl $LocalServiceUrl
    evidencePath = ".local/remote_service/cloudflare_tunnel.local.json"
    handoffPath = ".local/remote_service/cloudflare_tunnel_operator_handoff.local.md"
    configTemplatePath = ".local/remote_service/cloudflared-config.local.yml.template"
    nextOperatorAction = if ($originCertPresent) { "create_or_verify_tunnel_route_and_access_policy" } else { "run_cloudflared_tunnel_login" }
    externalMutationPerformed = [bool]$LaunchLogin
}

if ($Json) {
    $result | ConvertTo-Json -Depth 6
} else {
    Write-Host "REMOTE-OPS1B Cloudflare operator handoff"
    Write-Host "  cloudflared detected: $($result.cloudflaredDetected)"
    Write-Host "  origin cert present: $($result.originCertPresentPrivately)"
    Write-Host "  handoff: $($result.handoffPath)"
    Write-Host "  config template: $($result.configTemplatePath)"
    Write-Host "  next: $($result.nextOperatorAction)"
}
