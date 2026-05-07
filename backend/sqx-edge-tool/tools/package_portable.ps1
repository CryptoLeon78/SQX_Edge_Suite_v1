param(
  [string]$OutputDir = "",
  [switch]$RequireEmbeddedPython
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $PSScriptRoot
$BackendRoot = Split-Path -Parent $ToolRoot
$ProjectRoot = Split-Path -Parent $BackendRoot
if (-not $OutputDir) {
  $OutputDir = Join-Path $ProjectRoot "dist"
}

$OutputDir = (New-Item -ItemType Directory -Path $OutputDir -Force).FullName
$PythonExe = Join-Path $ToolRoot "runtime\python\python.exe"
if ($RequireEmbeddedPython -and -not (Test-Path -LiteralPath $PythonExe)) {
  throw "Embedded Python not found. Run backend\sqx-edge-tool\tools\bootstrap_embedded_python.ps1 first."
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$PackageName = "SQX_Edge_Tool_Portable_$Stamp.zip"
$PackagePath = Join-Path $OutputDir $PackageName
$StageDir = Join-Path $OutputDir "stage_$Stamp"

New-Item -ItemType Directory -Path $StageDir -Force | Out-Null

$excludeNames = @(
  ".git",
  "venv",
  "__pycache__",
  "output",
  "dist",
  "backups",
  ".pytest_cache",
  ".playwright-cli",
  "node_modules",
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
  "pro-template-pack-1",
  "pro-template-pack-2",
  "sqx-edge-relay"
)
$excludePatterns = @(
  "\\backend\\sqx-edge-tool\\runtime\\downloads\\",
  "\\backend\\sqx-edge-tool\\output\\",
  "\\__pycache__\\"
)

function Test-IncludedPath {
  param([string]$Path)
  foreach ($name in $excludeNames) {
    if ($Path -match "\\$([regex]::Escape($name))(\\|$)") { return $false }
  }
  foreach ($pattern in $excludePatterns) {
    if ($Path -match $pattern) { return $false }
  }
  if ($Path -match "\\backend\\sqx-edge-tool\\config\.json$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\config\\license\.json$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\license_signer\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\license_keypair\.ps1$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\license_issue\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\prepare_customer_delivery\.ps1$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\checkout_live_readiness\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\commercial_release_candidate\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\pilot_purchase_kit\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\limited_public_launch\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\post_launch_control\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\commercial_feedback_loop\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\public_offer_pack\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\launch_assets_kit\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\public_release_gate\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\release_publication_record\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\post_release_monitor\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\hotfix_rollback_release\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\customer_success_renewal\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\pro_buyer_pack\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\buyer_onboarding_support_gate\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_delivery\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_offer\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_publication\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_purchase_drill\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_handoff\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_sales_register\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_feedback_cohort\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_1_action_plan\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_2_specs\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_2_assets\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_2_offer_pack\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_2_publication\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_2_purchase_drill\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\template_pack_2_handoff\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\fulfillment_request\.py$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\fulfill_from_request\.ps1$") { return $false }
  if ($Path -match "\\backend\\sqx-edge-tool\\tools\\relay_bundle\.py$") { return $false }
  if ($Path -match "\\[^\\]*_private_key\.json$") { return $false }
  if ($Path -match "\\[^\\]*\.private_key\.json$") { return $false }
  if ($Path -match "\\license_signed_[^\\]*\.json$") { return $false }
  if ($Path -match "\\signed_license_[^\\]*\.json$") { return $false }
  if ($Path -match "\\license_payload_[^\\]*\.json$") { return $false }
  if ($Path -match "\\unsigned_license_[^\\]*\.json$") { return $false }
  if ($Path -match "\\fulfillment_request_[^\\]*\.json$") { return $false }
  if ($Path -match "\\webhook_event_[^\\]*\.json$") { return $false }
  if ($Path -match "\\relay_event_[^\\]*\.json$") { return $false }
  if ($Path -match "\\\.env(\..*)?$") { return $false }
  if ($Path -match "\\RELEASE_SQX_EDGE\.bat$") { return $false }
  if ($Path -match "_backup") { return $false }
  return $true
}

Get-ChildItem -LiteralPath $ProjectRoot -Recurse -File -Force | ForEach-Object {
  if (-not (Test-IncludedPath $_.FullName)) { return }
  $rel = $_.FullName.Substring($ProjectRoot.Length).TrimStart([char[]]@('\', '/'))
  $dest = Join-Path $StageDir $rel
  $destDir = Split-Path -Parent $dest
  New-Item -ItemType Directory -Path $destDir -Force | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
}

if (Test-Path -LiteralPath $PackagePath) {
  Remove-Item -LiteralPath $PackagePath -Force
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($StageDir, $PackagePath, [System.IO.Compression.CompressionLevel]::Optimal, $false)
Remove-Item -LiteralPath $StageDir -Recurse -Force

Write-Host "Portable package created:"
Write-Host "  $PackagePath"
if (Test-Path -LiteralPath $PythonExe) {
  Write-Host "Embedded Python included."
} else {
  Write-Host "Embedded Python not included. Run bootstrap first if you want a self-contained package."
}
