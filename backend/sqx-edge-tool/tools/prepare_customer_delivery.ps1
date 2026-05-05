param(
  [Parameter(Mandatory=$true)][string]$ZipPath,
  [Parameter(Mandatory=$true)][string]$LicensePath,
  [string]$CustomerSlug = "",
  [string]$OutDir = "",
  [string]$OrderId = "",
  [string]$Provider = "Lemon Squeezy",
  [string]$SupportEmail = ""
)

$ErrorActionPreference = "Stop"

function Get-SafeSlug {
  param([string]$Value)
  $slug = ($Value -replace "[^A-Za-z0-9_-]", "_").Trim("_")
  if (-not $slug) { return "customer" }
  return $slug.ToLowerInvariant()
}

function Add-FileInfo {
  param(
    [System.Collections.Generic.List[object]]$Files,
    [string]$Path
  )
  $item = Get-Item -LiteralPath $Path
  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $item.FullName
  $Files.Add([ordered]@{
    name = $item.Name
    bytes = $item.Length
    sha256 = $hash.Hash
  }) | Out-Null
}

if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
  throw "Portable ZIP not found: $ZipPath"
}
if (-not (Test-Path -LiteralPath $LicensePath -PathType Leaf)) {
  throw "Signed license not found: $LicensePath"
}
if (-not $OutDir) {
  $OutDir = Join-Path (Get-Location) "dist\customer_deliveries"
}

$Slug = Get-SafeSlug $CustomerSlug
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DeliveryDir = Join-Path $OutDir ("SQX_delivery_{0}_{1}" -f $Slug, $Stamp)
New-Item -ItemType Directory -Path $DeliveryDir -Force | Out-Null

$ZipItem = Get-Item -LiteralPath $ZipPath
$LicenseItem = Get-Item -LiteralPath $LicensePath
$ZipDest = Join-Path $DeliveryDir $ZipItem.Name
$LicenseDest = Join-Path $DeliveryDir "SQX_Edge_Pro_license.json"
Copy-Item -LiteralPath $ZipItem.FullName -Destination $ZipDest -Force
Copy-Item -LiteralPath $LicenseItem.FullName -Destination $LicenseDest -Force

$ReadmePath = Join-Path $DeliveryDir "LEEME_PRIMERO.txt"
$Readme = @(
  "SQX Edge Pro - Entrega",
  "",
  "1. Descomprime el ZIP portable en una carpeta local.",
  "2. Ejecuta START_SQX_EDGE.bat.",
  "3. En la pestana Inicio, pega el contenido de SQX_Edge_Pro_license.json en el panel Licencia.",
  "4. Pulsa Cargar licencia.",
  "5. Conserva este archivo de licencia y no lo publiques.",
  "",
  "Soporte: $SupportEmail",
  "Pedido: $OrderId",
  "Proveedor: $Provider"
)
Set-Content -LiteralPath $ReadmePath -Value $Readme -Encoding ASCII

$Files = [System.Collections.Generic.List[object]]::new()
Add-FileInfo -Files $Files -Path $ZipDest
Add-FileInfo -Files $Files -Path $LicenseDest
Add-FileInfo -Files $Files -Path $ReadmePath

$Manifest = [ordered]@{
  generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  provider = $Provider
  order_id = $OrderId
  customer_slug = $Slug
  support_email = $SupportEmail
  delivery_dir = $DeliveryDir
  files = $Files
}
$ManifestPath = Join-Path $DeliveryDir "delivery_manifest.json"
$Manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestPath -Encoding ASCII

Write-Host "Customer delivery prepared:"
Write-Host "  $DeliveryDir"
Write-Host "Files:"
Write-Host "  $ZipDest"
Write-Host "  $LicenseDest"
Write-Host "  $ReadmePath"
Write-Host "  $ManifestPath"
