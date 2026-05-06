param(
  [Parameter(Mandatory=$true)][string]$RequestPath,
  [Parameter(Mandatory=$true)][string]$PrivateKey,
  [Parameter(Mandatory=$true)][string]$ZipPath,
  [string]$OutDir = "",
  [string]$SupportEmail = "",
  [switch]$AllowIneligible
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $RequestPath -PathType Leaf)) {
  throw "Fulfillment request not found: $RequestPath"
}
if (-not (Test-Path -LiteralPath $PrivateKey -PathType Leaf)) {
  throw "Private key not found: $PrivateKey"
}
if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
  throw "Portable ZIP not found: $ZipPath"
}
if (-not $OutDir) {
  $OutDir = Join-Path (Get-Location) "dist\customer_deliveries"
}

$ToolRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $ToolRoot "venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
  throw "Python venv not found: $PythonExe"
}

$Request = Get-Content -Raw -LiteralPath $RequestPath | ConvertFrom-Json
if (-not $Request.eligible_for_fulfillment -and -not $AllowIneligible) {
  throw "Request is not eligible for fulfillment: $($Request.fulfillment_status)"
}

function Get-SafeSlug {
  param([string]$Value)
  $slug = ($Value -replace "[^A-Za-z0-9_-]", "_").Trim("_")
  if (-not $slug) { return "customer" }
  return $slug.ToLowerInvariant()
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Slug = Get-SafeSlug "$($Request.customer_name)_$($Request.order_id)"
$WorkDir = Join-Path $OutDir ("work_{0}_{1}" -f $Slug, $Stamp)
New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
$LicensePath = Join-Path $WorkDir "license_signed_$Slug.json"

$LicenseArgs = @(
  (Join-Path $ToolRoot "tools\license_issue.py"),
  "--private-key", $PrivateKey,
  "--out", $LicensePath,
  "--customer-name", [string]$Request.customer_name,
  "--customer-email", [string]$Request.customer_email,
  "--customer-id", [string]$Request.customer_id,
  "--order-id", [string]$Request.order_id,
  "--plan", [string]$Request.plan,
  "--duration-days", [string]$Request.license_duration_days,
  "--machine-limit", [string]$Request.machine_limit,
  "--support-level", [string]$Request.support_level,
  "--notes", ("provider={0}; event={1}; variant={2}" -f [string]$Request.provider, [string]$Request.source_event, [string]$Request.provider_variant_id)
)
& $PythonExe @LicenseArgs
if ($LASTEXITCODE -ne 0) {
  throw "license_issue.py failed with exit code $LASTEXITCODE"
}

$DeliveryArgs = @(
  "-ZipPath", $ZipPath,
  "-LicensePath", $LicensePath,
  "-CustomerSlug", $Slug,
  "-OutDir", $OutDir,
  "-OrderId", [string]$Request.order_id,
  "-Provider", [string]$Request.provider,
  "-SupportEmail", $SupportEmail
)
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ToolRoot "tools\prepare_customer_delivery.ps1") @DeliveryArgs
if ($LASTEXITCODE -ne 0) {
  throw "prepare_customer_delivery.ps1 failed with exit code $LASTEXITCODE"
}

Write-Host "Fulfillment completed for request:"
Write-Host "  $RequestPath"
