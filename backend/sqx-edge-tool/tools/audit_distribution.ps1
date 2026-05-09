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
  "analysis_output",
  "__pycache__",
  ".pytest_cache",
  ".playwright-cli",
  "license_keys",
  "licenses_private",
  "private_keys",
  "fulfillment_requests",
  "customer_success_renewal",
  "customer_cockpit",
  "pro_buyer_pack",
  "buyer_onboarding_support_gate",
  "template_pack_1_delivery",
  "template_pack_1_offer",
  "template_pack_1_publication",
  "template_pack_1_purchase_drill",
  "template_pack_1_handoff",
  "template_pack_1_sales_register",
  "template_pack_1_feedback_cohort",
  "template_pack_1_action_plan",
  "template_pack_2_specs",
  "template_pack_2_assets",
  "template_pack_2_offer_pack",
  "template_pack_2_publication",
  "template_pack_2_purchase_drill",
  "template_pack_2_handoff",
  "template_pack_2_sales_register",
  "template_pack_2_feedback_cohort",
  "buyer_ready_checkout_closeout",
  "public_buyer_page_cadence",
  "first_controlled_buyer_log",
  "post_sale_improvement_loop",
  "post_sale_micro_updates",
  "next_controlled_buyer_readiness",
  "next_controlled_buyer_outcome",
  "controlled_distribution_step",
  "controlled_distribution_review",
  "next_buyer_facing_asset",
  "private_asset_review",
  "controlled_publication_gate",
  "limited_publication_draft",
  "operator_publication_review",
  "manual_limited_publication_record",
  "manual_publication_monitor",
  "controlled_traffic_expansion_review",
  "controlled_traffic_expansion_step",
  "controlled_traffic_expansion_monitor",
  "controlled_traffic_expansion_decision",
  "controlled_traffic_expansion_execution",
  "controlled_traffic_expansion_execution_monitor",
  "controlled_commercial_next_movement",
  "controlled_commercial_next_movement_execution",
  "controlled_commercial_next_movement_execution_monitor",
  "next_controlled_commercial_movement_decision",
  "approved_controlled_commercial_movement_execution",
  "approved_controlled_commercial_movement_execution_monitor",
  "next_controlled_commercial_movement_from_m92_decision",
  "private-commercial",
  "commercial-private",
  "pro-template-pack-1",
  "pro-template-pack-2",
  "sqx-edge-relay",
  "dukas_mt5_download",
  "real_mtf_pipeline_run"
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
  "post_launch_control.py",
  "commercial_feedback_loop.py",
  "public_offer_pack.py",
  "launch_assets_kit.py",
  "public_release_gate.py",
  "release_publication_record.py",
  "post_release_monitor.py",
  "hotfix_rollback_release.py",
  "customer_success_renewal.py",
  "pro_buyer_pack.py",
  "buyer_onboarding_support_gate.py",
  "template_pack_1_delivery.py",
  "template_pack_1_offer.py",
  "template_pack_1_publication.py",
  "template_pack_1_purchase_drill.py",
  "template_pack_1_handoff.py",
  "template_pack_1_sales_register.py",
  "template_pack_1_feedback_cohort.py",
  "template_pack_1_action_plan.py",
  "template_pack_2_specs.py",
  "template_pack_2_assets.py",
  "template_pack_2_offer_pack.py",
  "template_pack_2_publication.py",
  "template_pack_2_purchase_drill.py",
  "template_pack_2_handoff.py",
  "template_pack_2_sales_register.py",
  "template_pack_2_feedback_cohort.py",
  "buyer_ready_checkout_closeout.py",
  "public_buyer_page_cadence.py",
  "first_controlled_buyer_log.py",
  "post_sale_improvement_loop.py",
  "post_sale_micro_updates.py",
  "next_controlled_buyer_readiness.py",
  "next_controlled_buyer_outcome.py",
  "controlled_distribution_step.py",
  "controlled_distribution_review.py",
  "next_buyer_facing_asset.py",
  "private_asset_review.py",
  "controlled_publication_gate.py",
  "limited_publication_draft.py",
  "operator_publication_review.py",
  "manual_limited_publication_record.py",
  "manual_publication_monitor.py",
  "controlled_traffic_expansion_review.py",
  "controlled_traffic_expansion_step.py",
  "controlled_traffic_expansion_monitor.py",
  "controlled_traffic_expansion_decision.py",
  "controlled_traffic_expansion_execution.py",
  "controlled_traffic_expansion_execution_monitor.py",
  "controlled_commercial_next_movement.py",
  "controlled_commercial_next_movement_execution.py",
  "controlled_commercial_next_movement_execution_monitor.py",
  "next_controlled_commercial_movement_decision.py",
  "approved_controlled_commercial_movement_execution.py",
  "approved_controlled_commercial_movement_execution_monitor.py",
  "next_controlled_commercial_movement_from_m92_decision.py",
  "private_commercial_split.py",
  "fulfillment_request.py",
  "fulfill_from_request.ps1",
  "relay_bundle.py",
  "dukas_mt5_ohlc_download.py",
  "mt5_ipc_diagnostic.py",
  "dukas_mt5_download.json",
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
  '"analysis_output"',
  '".pytest_cache"',
  '".playwright-cli"',
  '"license_keys"',
  '"licenses_private"',
  '"private_keys"',
  '"customer_success_renewal"',
  '"customer_cockpit"',
  '"pro_buyer_pack"',
  '"buyer_onboarding_support_gate"',
  '"template_pack_1_delivery"',
  '"template_pack_1_offer"',
  '"template_pack_1_publication"',
  '"template_pack_1_purchase_drill"',
  '"template_pack_1_handoff"',
  '"template_pack_1_sales_register"',
  '"template_pack_1_feedback_cohort"',
  '"template_pack_1_action_plan"',
  '"template_pack_2_specs"',
  '"template_pack_2_assets"',
  '"template_pack_2_offer_pack"',
  '"template_pack_2_publication"',
  '"template_pack_2_purchase_drill"',
  '"template_pack_2_handoff"',
  '"template_pack_2_sales_register"',
  '"template_pack_2_feedback_cohort"',
  '"buyer_ready_checkout_closeout"',
  '"public_buyer_page_cadence"',
  '"first_controlled_buyer_log"',
  '"post_sale_improvement_loop"',
  '"post_sale_micro_updates"',
  '"next_controlled_buyer_readiness"',
  '"next_controlled_buyer_outcome"',
  '"controlled_distribution_step"',
  '"controlled_distribution_review"',
  '"next_buyer_facing_asset"',
  '"private_asset_review"',
  '"controlled_publication_gate"',
  '"limited_publication_draft"',
  '"operator_publication_review"',
  '"manual_limited_publication_record"',
  '"manual_publication_monitor"',
  '"controlled_traffic_expansion_review"',
  '"controlled_traffic_expansion_step"',
  '"controlled_traffic_expansion_monitor"',
  '"controlled_traffic_expansion_decision"',
  '"controlled_traffic_expansion_execution"',
  '"controlled_traffic_expansion_execution_monitor"',
  '"controlled_commercial_next_movement"',
  '"controlled_commercial_next_movement_execution"',
  '"controlled_commercial_next_movement_execution_monitor"',
  '"next_controlled_commercial_movement_decision"',
  '"approved_controlled_commercial_movement_execution"',
  '"approved_controlled_commercial_movement_execution_monitor"',
  '"next_controlled_commercial_movement_from_m92_decision"',
  '"private-commercial"',
  '"commercial-private"',
  '"pro-template-pack-1"',
  '"pro-template-pack-2"',
  '"sqx-edge-relay"',
  '"real_mtf_pipeline_run"',
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
  'post_launch_control\.py',
  'commercial_feedback_loop\.py',
  'public_offer_pack\.py',
  'launch_assets_kit\.py',
  'public_release_gate\.py',
  'release_publication_record\.py',
  'post_release_monitor\.py',
  'hotfix_rollback_release\.py',
  'customer_success_renewal\.py',
  'pro_buyer_pack\.py',
  'buyer_onboarding_support_gate\.py',
  'template_pack_1_delivery\.py',
  'template_pack_1_offer\.py',
  'template_pack_1_publication\.py',
  'template_pack_1_purchase_drill\.py',
  'template_pack_1_handoff\.py',
  'template_pack_1_sales_register\.py',
  'template_pack_1_feedback_cohort\.py',
  'template_pack_1_action_plan\.py',
  'template_pack_2_specs\.py',
  'template_pack_2_assets\.py',
  'template_pack_2_offer_pack\.py',
  'template_pack_2_publication\.py',
  'template_pack_2_purchase_drill\.py',
  'template_pack_2_handoff\.py',
  'template_pack_2_sales_register\.py',
  'template_pack_2_feedback_cohort\.py',
  'buyer_ready_checkout_closeout\.py',
  'public_buyer_page_cadence\.py',
  'first_controlled_buyer_log\.py',
  'post_sale_improvement_loop\.py',
  'post_sale_micro_updates\.py',
  'next_controlled_buyer_readiness\.py',
  'next_controlled_buyer_outcome\.py',
  'controlled_distribution_step\.py',
  'controlled_distribution_review\.py',
  'next_buyer_facing_asset\.py',
  'private_asset_review\.py',
  'controlled_publication_gate\.py',
  'limited_publication_draft\.py',
  'operator_publication_review\.py',
  'manual_limited_publication_record\.py',
  'manual_publication_monitor\.py',
  'controlled_traffic_expansion_review\.py',
  'controlled_traffic_expansion_step\.py',
  'controlled_traffic_expansion_monitor\.py',
  'controlled_traffic_expansion_decision\.py',
  'controlled_traffic_expansion_execution\.py',
  'controlled_traffic_expansion_execution_monitor\.py',
  'controlled_commercial_next_movement\.py',
  'controlled_commercial_next_movement_execution\.py',
  'controlled_commercial_next_movement_execution_monitor\.py',
  'next_controlled_commercial_movement_decision\.py',
  'approved_controlled_commercial_movement_execution\.py',
  'approved_controlled_commercial_movement_execution_monitor\.py',
  'next_controlled_commercial_movement_from_m92_decision\.py',
  'private_commercial_split\.py',
  'fulfillment_request\.py',
  'fulfill_from_request\.ps1',
  'relay_bundle\.py',
  'dukas_mt5_ohlc_download\.py',
  'mt5_ipc_diagnostic\.py',
  'dukas_mt5_download\.json',
  '"dukas_mt5_download"',
  '\\data\\ohlc\\',
  '\\analysis_output\\',
  'mt5_ipc_diagnostic',
  'real_mtf_pipeline_run',
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
