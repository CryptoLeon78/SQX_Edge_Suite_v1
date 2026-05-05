param(
  [switch]$SkipTests,
  [switch]$SkipPackage,
  [int]$PortableApiPort = 5059
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $PSScriptRoot
$BackendRoot = Split-Path -Parent $ToolRoot
$ProjectRoot = Split-Path -Parent $BackendRoot
$PythonExe = Join-Path $ToolRoot "venv\Scripts\python.exe"
$EmbeddedPythonExe = Join-Path $ToolRoot "runtime\python\python.exe"
$PackageScript = Join-Path $PSScriptRoot "package_portable.ps1"

function Write-Step {
  param([string]$Message)
  Write-Host ""
  Write-Host "== $Message =="
}

function Invoke-Checked {
  param(
    [Parameter(Mandatory=$true)][string]$Label,
    [Parameter(Mandatory=$true)][scriptblock]$Command
  )
  Write-Step $Label
  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE"
  }
}

function Assert-File {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Required file missing: $Path"
  }
}

function Assert-DirExcluded {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path) {
    throw "Path should not be present in portable package: $Path"
  }
}

function Test-PortableZip {
  param([string]$ZipPath)

  Write-Step "Validate portable ZIP"
  $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $TempRoot = Join-Path $env:TEMP "SQX_release_check_$Stamp"
  New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null

  try {
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $TempRoot -Force

    Assert-File (Join-Path $TempRoot "START_SQX_EDGE.bat")
    Assert-File (Join-Path $TempRoot "STOP_SQX_EDGE.bat")
    Assert-File (Join-Path $TempRoot "packaging\START_SQX_EDGE.bat")
    Assert-File (Join-Path $TempRoot "app\SQX_Dashboard_v6.html")
    Assert-File (Join-Path $TempRoot "app\js\project-generator-main.js")
    Assert-File (Join-Path $TempRoot "app\js\modules\project-generator-dom.js")
    Assert-File (Join-Path $TempRoot "backend\sqx-edge-tool\run-web-embedded.bat")
    Assert-File (Join-Path $TempRoot "backend\sqx-edge-tool\runtime\python\python.exe")

    Assert-DirExcluded (Join-Path $TempRoot "backups")
    Assert-DirExcluded (Join-Path $TempRoot "dist")
    Assert-DirExcluded (Join-Path $TempRoot "node_modules")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\venv")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\config.json")

    $PortableTool = Join-Path $TempRoot "backend\sqx-edge-tool"
    $PortablePython = Join-Path $PortableTool "runtime\python\python.exe"
    & $PortablePython -c "import flask; import api.server; print('portable imports ok')"
    if ($LASTEXITCODE -ne 0) { throw "Portable import check failed" }

    $Process = Start-Process -FilePath $PortablePython -ArgumentList @("-m", "api.server", "--port", "$PortableApiPort") -WorkingDirectory $PortableTool -WindowStyle Hidden -PassThru
    try {
      $Ok = $false
      for ($i = 0; $i -lt 30; $i++) {
        try {
          $Response = Invoke-RestMethod -Uri "http://127.0.0.1:$PortableApiPort/api/health" -TimeoutSec 1
          if ($Response.ok) { $Ok = $true; break }
        } catch {}
        Start-Sleep -Milliseconds 500
      }
      if (-not $Ok) {
        throw "Portable API did not answer /api/health on port $PortableApiPort"
      }
      Write-Host "Portable API health OK: version $($Response.version)"
    } finally {
      if ($Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force
        Wait-Process -Id $Process.Id -Timeout 10 -ErrorAction SilentlyContinue
      }
    }
  } finally {
    $ResolvedTemp = Resolve-Path -LiteralPath $TempRoot -ErrorAction SilentlyContinue
    if ($ResolvedTemp) {
      $TempBase = [System.IO.Path]::GetFullPath($env:TEMP)
      $Target = [System.IO.Path]::GetFullPath($ResolvedTemp.Path)
      if ($Target.StartsWith($TempBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $Target -Recurse -Force
      } else {
        throw "Refusing to remove outside TEMP: $Target"
      }
    }
  }
}

Write-Host ""
Write-Host "SQX Edge Suite - Release Checklist"
Write-Host "Project: $ProjectRoot"

Assert-File $PackageScript
Assert-File $EmbeddedPythonExe

Push-Location $ProjectRoot
try {
  if (-not $SkipTests) {
    Assert-File $PythonExe
    Invoke-Checked "Frontend module contracts" { node ".\tests\js\module_contracts.mjs" }
    Invoke-Checked "Python test suite" { & $PythonExe -m pytest }
    Invoke-Checked "Git diff check" { git diff --check }
  }

  if (-not $SkipPackage) {
    Invoke-Checked "Build portable ZIP" {
      powershell -NoProfile -ExecutionPolicy Bypass -File $PackageScript -RequireEmbeddedPython
    }
    $Zip = Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "dist") -Filter "SQX_Edge_Tool_Portable_*.zip" |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
    if (-not $Zip) { throw "Portable ZIP was not created in dist" }
    Test-PortableZip -ZipPath $Zip.FullName
    Write-Host ""
    Write-Host "Release ZIP ready:"
    Write-Host "  $($Zip.FullName)"
  }

  Write-Step "Git status"
  git status --short --branch

  Write-Host ""
  Write-Host "Release checklist completed."
} finally {
  Pop-Location
}
