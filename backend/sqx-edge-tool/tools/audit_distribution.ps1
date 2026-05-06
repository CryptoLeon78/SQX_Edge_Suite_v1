param(
  [string]$ZipPath = "",
  [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $PSScriptRoot
$BackendRoot = Split-Path -Parent $ToolRoot
$ProjectRoot = Split-Path -Parent $BackendRoot
$PackageScript = Join-Path $PSScriptRoot "package_portable.ps1"

if (-not $ReportPath) {
  $ReportPath = Join-Path (Join-Path $ProjectRoot "dist") "SQX_distribution_audit.txt"
}

$denySegments = @(
  ".git",
  "venv",
  "node_modules",
  "backups",
  "dist",
  "output",
  "__pycache__",
  ".pytest_cache",
  ".playwright-cli",
  "license_keys",
  "licenses_private",
  "private_keys",
  "fulfillment_requests",
  "sqx-edge-relay"
)

$denyFiles = @(
  "config.json",
  "license.json",
  "license_signer.py",
  "license_keypair.ps1",
  "license_issue.py",
  "prepare_customer_delivery.ps1",
  "checkout_live_readiness.py",
  "commercial_release_candidate.py",
  "pilot_purchase_kit.py",
  "limited_public_launch.py",
  "fulfillment_request.py",
  "fulfill_from_request.ps1",
  "relay_bundle.py",
  ".env",
  "RELEASE_SQX_EDGE.bat"
)

$denyFilePatterns = @(
  ".*_private_key\.json$",
  ".*\.private_key\.json$",
  "license_signed_.*\.json$",
  "signed_license_.*\.json$",
  "license_payload_.*\.json$",
  "unsigned_license_.*\.json$",
  "fulfillment_request_.*\.json$",
  "webhook_event_.*\.json$",
  "relay_event_.*\.json$"
)

$requiredPackageGuards = @(
  '".git"',
  '"venv"',
  '"node_modules"',
  '"backups"',
  '"dist"',
  '"output"',
  '".pytest_cache"',
  '".playwright-cli"',
  '"license_keys"',
  '"licenses_private"',
  '"private_keys"',
  '"sqx-edge-relay"',
  'config\.json',
  'license\.json',
  'license_signer\.py',
  'license_keypair\.ps1',
  'license_issue\.py',
  'prepare_customer_delivery\.ps1',
  'checkout_live_readiness\.py',
  'commercial_release_candidate\.py',
  'pilot_purchase_kit\.py',
  'limited_public_launch\.py',
  'fulfillment_request\.py',
  'fulfill_from_request\.ps1',
  'relay_bundle\.py',
  '_private_key\.json',
  '\.private_key\.json',
  'license_signed_',
  'signed_license_',
  'license_payload_',
  'unsigned_license_',
  'fulfillment_request_',
  'webhook_event_',
  'relay_event_',
  '\\\.env',
  'RELEASE_SQX_EDGE'
)

function Add-Finding {
  param(
    [System.Collections.Generic.List[string]]$Findings,
    [string]$Message
  )
  $Findings.Add($Message) | Out-Null
}

function Test-DeniedEntry {
  param([string]$Name)
  $normalized = $Name.Replace("\", "/").Trim("/")
  $segments = @($normalized.Split("/", [System.StringSplitOptions]::RemoveEmptyEntries))
  foreach ($segment in $segments) {
    if ($denySegments -contains $segment) { return $true }
  }
  foreach ($file in $denyFiles) {
    if ($segments.Count -gt 0 -and $segments[-1] -eq $file) { return $true }
  }
  if ($segments.Count -gt 0) {
    foreach ($pattern in $denyFilePatterns) {
      if ($segments[-1] -match $pattern) { return $true }
    }
  }
  return $false
}

function Test-PackageScriptGuards {
  param([System.Collections.Generic.List[string]]$Findings)
  $text = Get-Content -Raw -LiteralPath $PackageScript
  foreach ($guard in $requiredPackageGuards) {
    if (-not $text.Contains($guard)) {
      Add-Finding $Findings "Missing package exclusion guard: $guard"
    }
  }
}

function Test-ZipContents {
  param(
    [System.Collections.Generic.List[string]]$Findings,
    [string]$Path
  )

  if (-not $Path) { return }
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    Add-Finding $Findings "ZIP not found: $Path"
    return
  }

  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $archive = [System.IO.Compression.ZipFile]::OpenRead($Path)
  try {
    foreach ($entry in $archive.Entries) {
      if (Test-DeniedEntry $entry.FullName) {
        Add-Finding $Findings "Denied entry included in ZIP: $($entry.FullName)"
      }
    }
  } finally {
    $archive.Dispose()
  }
}

$findings = [System.Collections.Generic.List[string]]::new()
Test-PackageScriptGuards -Findings $findings
Test-ZipContents -Findings $findings -Path $ZipPath

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("SQX Edge Suite - Distribution Audit") | Out-Null
$lines.Add("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')") | Out-Null
$lines.Add("Project: $ProjectRoot") | Out-Null
$lines.Add("Package script: $PackageScript") | Out-Null
if ($ZipPath) {
  $lines.Add("ZIP: $ZipPath") | Out-Null
  if (Test-Path -LiteralPath $ZipPath -PathType Leaf) {
    $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $ZipPath
    $checksumPath = "$ZipPath.sha256"
    Set-Content -LiteralPath $checksumPath -Value "$($hash.Hash)  $(Split-Path -Leaf $ZipPath)" -Encoding ASCII
    $lines.Add("SHA256: $($hash.Hash)") | Out-Null
    $lines.Add("Checksum file: $checksumPath") | Out-Null
  }
}
$lines.Add("") | Out-Null
$lines.Add("Denied segments: $($denySegments -join ', ')") | Out-Null
$lines.Add("Denied files: $($denyFiles -join ', ')") | Out-Null
$lines.Add("Denied file patterns: $($denyFilePatterns -join ', ')") | Out-Null
$lines.Add("") | Out-Null

if ($findings.Count -eq 0) {
  $lines.Add("Status: PASS") | Out-Null
  $lines.Add("No denied package entries or missing package guards were found.") | Out-Null
} else {
  $lines.Add("Status: FAIL") | Out-Null
  foreach ($finding in $findings) {
    $lines.Add("- $finding") | Out-Null
  }
}

New-Item -ItemType Directory -Path (Split-Path -Parent $ReportPath) -Force | Out-Null
Set-Content -LiteralPath $ReportPath -Value $lines -Encoding ASCII
Write-Host "Distribution audit report:"
Write-Host "  $ReportPath"
if ($findings.Count -gt 0) {
  throw "Distribution audit failed with $($findings.Count) finding(s)."
}
