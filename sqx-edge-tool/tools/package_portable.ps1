param(
  [string]$OutputDir = "",
  [switch]$RequireEmbeddedPython
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ToolRoot = Join-Path $ProjectRoot "sqx-edge-tool"
if (-not $OutputDir) {
  $OutputDir = Join-Path $ProjectRoot "dist"
}

$OutputDir = (New-Item -ItemType Directory -Path $OutputDir -Force).FullName
$PythonExe = Join-Path $ToolRoot "runtime\python\python.exe"
if ($RequireEmbeddedPython -and -not (Test-Path -LiteralPath $PythonExe)) {
  throw "Embedded Python not found. Run sqx-edge-tool\tools\bootstrap_embedded_python.ps1 first."
}

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$PackageName = "SQX_Edge_Tool_Portable_$Stamp.zip"
$PackagePath = Join-Path $OutputDir $PackageName
$StageDir = Join-Path $OutputDir "stage_$Stamp"

New-Item -ItemType Directory -Path $StageDir -Force | Out-Null

$excludeNames = @(".git", "venv", "__pycache__", "output", "dist")
$excludePatterns = @(
  "\\sqx-edge-tool\\runtime\\downloads\\",
  "\\sqx-edge-tool\\output\\",
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
  if ($Path -match "\\sqx-edge-tool\\config\.json$") { return $false }
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
