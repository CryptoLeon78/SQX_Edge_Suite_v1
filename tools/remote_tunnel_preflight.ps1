[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$ApiUrl = "http://127.0.0.1:5050/api/health",
    [string]$EvidencePath = "",
    [string]$CloudflaredPath = "cloudflared",
    [switch]$RequireEvidence,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Test-LocalApiUrl {
    param([string]$Url)
    return $Url -match '^http://(127\.0\.0\.1|localhost)(:\d+)?(/|$)'
}

function Get-BooleanEvidence {
    param(
        [object]$Evidence,
        [string]$Name
    )
    if ($null -eq $Evidence) { return $false }
    $prop = $Evidence.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $false }
    return [bool]$prop.Value
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

function Test-SensitiveEvidenceText {
    param([string]$Text)
    $patterns = @(
        '@[A-Za-z0-9._%+-]+\.[A-Za-z]{2,}',
        'https?://',
        'account[_-]?id',
        'zone[_-]?id',
        'tunnel[_-]?id',
        'access[_-]?id',
        'api[_-]?token',
        '-----BEGIN',
        ('sk_' + 'live_'),
        ('pk_' + 'live_')
    )
    foreach ($pattern in $patterns) {
        if ($Text -match $pattern) {
            return $false
        }
    }
    return $true
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
    $EvidencePath = Join-Path $repo ".local\remote_service\cloudflare_tunnel.local.json"
}
$remote1Preflight = Join-Path $repo "tools\remote_service_preflight.ps1"
$cloudflared = Resolve-Cloudflared $CloudflaredPath
$cloudflaredVersion = $null
if ($cloudflared) {
    try {
        $cloudflaredVersion = (& $cloudflared --version 2>$null | Select-Object -First 1)
    } catch {
        $cloudflaredVersion = $null
    }
}

$remote1 = $null
$remote1Ok = $false
if (Test-Path -LiteralPath $remote1Preflight) {
    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $remote1Preflight -RepoRoot $repo -ApiUrl $ApiUrl -RequireSqxReady -Json
        $remote1 = ($raw | Out-String | ConvertFrom-Json)
        $remote1Ok = [bool]$remote1.ok
    } catch {
        $remote1Ok = $false
    }
}

$evidence = $null
$evidenceText = ""
$evidencePresent = Test-Path -LiteralPath $EvidencePath
$evidenceReadable = $false
if ($evidencePresent) {
    try {
        $evidenceText = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8
        $evidence = $evidenceText | ConvertFrom-Json
        $evidenceReadable = $true
    } catch {
        $evidenceReadable = $false
    }
}

$targetUrl = "http://127.0.0.1:5050"
if ($null -ne $evidence -and $null -ne $evidence.PSObject.Properties["targetUrl"]) {
    $targetUrl = [string]$evidence.targetUrl
}

$checks = [ordered]@{
    remote1PreflightOk = $remote1Ok
    apiUrlLocalOnly = Test-LocalApiUrl $ApiUrl
    targetUrlLocalOnly = Test-LocalApiUrl $targetUrl
    cloudflaredInstalled = [bool]$cloudflared
    evidencePresent = $evidencePresent
    evidenceReadable = $evidenceReadable
    evidencePublicSafeShape = (-not $evidencePresent) -or (Test-SensitiveEvidenceText $evidenceText)
    hostnameConfiguredPrivately = Get-BooleanEvidence $evidence "hostnameConfiguredPrivately"
    customDomainOwnedPrivately = Get-BooleanEvidence $evidence "customDomainOwnedPrivately"
    cloudflaredAuthenticatedPrivately = Get-BooleanEvidence $evidence "cloudflaredAuthenticatedPrivately"
    tunnelCreatedPrivately = Get-BooleanEvidence $evidence "tunnelCreatedPrivately"
    tunnelRouteConfiguredPrivately = Get-BooleanEvidence $evidence "tunnelRouteConfiguredPrivately"
    cloudflareAccessApplicationCreatedPrivately = Get-BooleanEvidence $evidence "cloudflareAccessApplicationCreatedPrivately"
    cloudflareAccessPolicyCreatedPrivately = Get-BooleanEvidence $evidence "cloudflareAccessPolicyCreatedPrivately"
    accessBlocksAnonymous = Get-BooleanEvidence $evidence "accessBlocksAnonymous"
    accessAllowsApprovedIdentity = Get-BooleanEvidence $evidence "accessAllowsApprovedIdentity"
    routerPortsClosed = -not (Get-BooleanEvidence $evidence "routerPortsOpened")
    publicRepoContainsHostname = Get-BooleanEvidence $evidence "publicRepoContainsHostname"
    publicRepoContainsCredentials = Get-BooleanEvidence $evidence "publicRepoContainsCredentials"
    publicRepoContainsProviderIds = Get-BooleanEvidence $evidence "publicRepoContainsProviderIds"
    publicRepoContainsAccessPolicyIds = Get-BooleanEvidence $evidence "publicRepoContainsAccessPolicyIds"
}

$required = @(
    "remote1PreflightOk",
    "apiUrlLocalOnly",
    "targetUrlLocalOnly",
    "cloudflaredInstalled",
    "routerPortsClosed"
)
if ($RequireEvidence) {
    $required += @(
        "evidencePresent",
        "evidenceReadable",
        "evidencePublicSafeShape",
        "hostnameConfiguredPrivately",
        "customDomainOwnedPrivately",
        "cloudflaredAuthenticatedPrivately",
        "tunnelCreatedPrivately",
        "tunnelRouteConfiguredPrivately",
        "cloudflareAccessApplicationCreatedPrivately",
        "cloudflareAccessPolicyCreatedPrivately",
        "accessBlocksAnonymous",
        "accessAllowsApprovedIdentity"
    )
}

$missing = @()
foreach ($name in $required) {
    if (-not [bool]$checks[$name]) {
        $missing += $name
    }
}
foreach ($leakCheck in @("publicRepoContainsHostname", "publicRepoContainsCredentials", "publicRepoContainsProviderIds", "publicRepoContainsAccessPolicyIds")) {
    if ([bool]$checks[$leakCheck]) {
        $missing += $leakCheck
    }
}

$status = if ($missing.Count -eq 0) {
    "GO_REMOTE2_TUNNEL_ACCESS_READY_NO_GIT_LEAK"
} else {
    "NO_GO_REMOTE2_PRIVATE_TUNNEL_ACCESS_EVIDENCE_MISSING"
}

$result = [ordered]@{
    ok = ($missing.Count -eq 0)
    phase = "REMOTE-2"
    mode = "cloudflare_tunnel_access_preflight"
    status = $status
    repoRoot = $repo
    apiUrl = $ApiUrl
    evidencePath = ".local/remote_service/cloudflare_tunnel.local.json"
    requireEvidence = [bool]$RequireEvidence
    cloudflaredDetected = [bool]$cloudflared
    cloudflaredVersion = $cloudflaredVersion
    checks = $checks
    missingRequired = $missing
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host "REMOTE-2 Cloudflare Tunnel/Access preflight"
    Write-Host "  Status: $status"
    Write-Host "  OK: $($result.ok)"
    Write-Host "  cloudflared detected: $($result.cloudflaredDetected)"
    Write-Host "  Evidence: $($result.evidencePath)"
    if ($missing.Count -gt 0) {
        Write-Host "  Missing/unsafe checks: $($missing -join ', ')"
    }
    Write-Host "  Use -Json for machine-readable output."
}

if (-not $result.ok) {
    exit 1
}
