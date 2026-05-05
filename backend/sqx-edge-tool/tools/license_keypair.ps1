param(
  [string]$OutDir = "",
  [string]$KeyId = "",
  [int]$Bits = 2048
)

$ErrorActionPreference = "Stop"

if ($Bits -lt 2048) {
  throw "RSA key size must be at least 2048 bits."
}

if (-not $KeyId) {
  $KeyId = "sqx-prod-$(Get-Date -Format 'yyyy-MM')-v1"
}

if (-not $OutDir) {
  $OutDir = Join-Path (Get-Location) "license_keys"
}

function ConvertTo-Base64Url {
  param([byte[]]$Bytes)
  return [Convert]::ToBase64String($Bytes).TrimEnd("=").Replace("+", "-").Replace("/", "_")
}

$ResolvedOut = (New-Item -ItemType Directory -Path $OutDir -Force).FullName
$Rsa = [System.Security.Cryptography.RSA]::Create($Bits)

try {
  $Params = $Rsa.ExportParameters($true)
  $PublicKey = [ordered]@{
    kty = "RSA"
    kid = $KeyId
    alg = "RS256"
    n = ConvertTo-Base64Url $Params.Modulus
    e = ConvertTo-Base64Url $Params.Exponent
  }
  $PrivateKey = [ordered]@{
    kty = "RSA"
    kid = $KeyId
    alg = "RS256"
    n = ConvertTo-Base64Url $Params.Modulus
    e = ConvertTo-Base64Url $Params.Exponent
    d = ConvertTo-Base64Url $Params.D
  }

  $PublicPath = Join-Path $ResolvedOut ("{0}_public_key.json" -f $KeyId)
  $PrivatePath = Join-Path $ResolvedOut ("{0}_private_key.json" -f $KeyId)

  $PublicKey | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $PublicPath -Encoding ASCII
  $PrivateKey | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $PrivatePath -Encoding ASCII

  Write-Host "SQX Edge license keypair created:"
  Write-Host "  Public key:  $PublicPath"
  Write-Host "  Private key: $PrivatePath"
  Write-Host ""
  Write-Host "IMPORTANT: keep the private key outside git, backups and ZIP releases."
  Write-Host "Replace licensing.publicKey in config/product_manifest.json with the public key before selling a production build."
} finally {
  if ($Rsa) {
    $Rsa.Dispose()
  }
}
