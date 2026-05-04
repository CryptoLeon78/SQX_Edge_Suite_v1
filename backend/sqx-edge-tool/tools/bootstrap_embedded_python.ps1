param(
  [string]$PythonVersion = "3.12.10",
  [ValidateSet("amd64", "win32")]
  [string]$Architecture = "amd64",
  [string]$RuntimeDir = "",
  [string]$ZipPath = "",
  [switch]$SkipDownload,
  [switch]$Force
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $PSScriptRoot
if (-not $RuntimeDir) {
  $RuntimeDir = Join-Path $ToolRoot "runtime"
}

$RuntimeDir = (New-Item -ItemType Directory -Path $RuntimeDir -Force).FullName
$DownloadsDir = Join-Path $RuntimeDir "downloads"
$PythonDir = Join-Path $RuntimeDir "python"
$WheelsDir = Join-Path $RuntimeDir "wheels"
$GetPipPath = Join-Path $DownloadsDir "get-pip.py"
$RequirementsPath = Join-Path $ToolRoot "requirements.txt"

New-Item -ItemType Directory -Path $DownloadsDir -Force | Out-Null
New-Item -ItemType Directory -Path $WheelsDir -Force | Out-Null

$ZipName = "python-$PythonVersion-embed-$Architecture.zip"
$DefaultZipPath = Join-Path $DownloadsDir $ZipName
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$ZipName"
$GetPipUrl = "https://bootstrap.pypa.io/get-pip.py"

if (-not $ZipPath) {
  $ZipPath = $DefaultZipPath
}

Write-Host ""
Write-Host "SQX Edge Tool - Embedded Python bootstrap"
Write-Host "Runtime: $RuntimeDir"
Write-Host "Python:  $PythonVersion ($Architecture)"
Write-Host ""

function Save-Url {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [Parameter(Mandatory=$true)][string]$OutFile,
    [int64]$MinBytes = 1024
  )

  if (Test-Path -LiteralPath $OutFile) {
    Remove-Item -LiteralPath $OutFile -Force
  }

  $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
  if ($curl) {
    & $curl.Source -L --fail --connect-timeout 30 --max-time 300 --retry 2 --retry-delay 2 -o $OutFile $Url
    if ($LASTEXITCODE -ne 0) {
      throw "curl failed downloading $Url with exit code $LASTEXITCODE"
    }
  } else {
    Invoke-WebRequest -Uri $Url -OutFile $OutFile -TimeoutSec 300
  }

  $item = Get-Item -LiteralPath $OutFile -ErrorAction Stop
  if ($item.Length -lt $MinBytes) {
    throw "Downloaded file is unexpectedly small ($($item.Length) bytes): $OutFile"
  }
}

if (-not $SkipDownload) {
  if ($Force -or -not (Test-Path -LiteralPath $ZipPath)) {
    Write-Host "Downloading Python embeddable package..."
    Save-Url -Url $PythonUrl -OutFile $ZipPath -MinBytes 5000000
  } else {
    Write-Host "Python zip already exists: $ZipPath"
  }
} elseif (-not (Test-Path -LiteralPath $ZipPath)) {
  throw "ZipPath does not exist and -SkipDownload was used: $ZipPath"
}

if ($Force -and (Test-Path -LiteralPath $PythonDir)) {
  Write-Host "Removing previous embedded Python runtime..."
  Remove-Item -LiteralPath $PythonDir -Recurse -Force
}

if (-not (Test-Path -LiteralPath (Join-Path $PythonDir "python.exe"))) {
  Write-Host "Expanding Python runtime..."
  New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null
  Expand-Archive -LiteralPath $ZipPath -DestinationPath $PythonDir -Force
} else {
  Write-Host "Embedded Python already expanded: $PythonDir"
}

$PthFile = Get-ChildItem -LiteralPath $PythonDir -Filter "python*._pth" | Select-Object -First 1
if (-not $PthFile) {
  throw "Could not find python*._pth in $PythonDir"
}

$PthText = Get-Content -LiteralPath $PthFile.FullName -Raw
$PthLines = @($PthText -split "\r?\n" | Where-Object { $_ -ne "" })
$PthLines = $PthLines | ForEach-Object {
  if ($_ -eq "#import site") { "import site" } else { $_ }
}
foreach ($required in @(".", "..\..", "Lib\site-packages", "import site")) {
  if ($PthLines -notcontains $required) {
    $PthLines += $required
  }
}
Set-Content -LiteralPath $PthFile.FullName -Value (($PthLines -join "`r`n") + "`r`n") -Encoding ASCII
Write-Host "Configured import paths in $($PthFile.Name)"

$PythonExe = Join-Path $PythonDir "python.exe"
if (-not (Test-Path -LiteralPath $PythonExe)) {
  throw "python.exe not found: $PythonExe"
}

if ($Force -or -not (Test-Path -LiteralPath $GetPipPath)) {
  Write-Host "Downloading get-pip.py..."
  Save-Url -Url $GetPipUrl -OutFile $GetPipPath -MinBytes 1000000
} else {
  Write-Host "get-pip.py already exists: $GetPipPath"
}

Write-Host "Installing pip into embedded Python..."
& $PythonExe $GetPipPath --no-warn-script-location
if ($LASTEXITCODE -ne 0) { throw "get-pip.py failed with exit code $LASTEXITCODE" }

Write-Host "Installing requirements..."
& $PythonExe -m pip install --no-cache-dir --disable-pip-version-check -r $RequirementsPath
if ($LASTEXITCODE -ne 0) { throw "pip install failed with exit code $LASTEXITCODE" }

Write-Host ""
Write-Host "Embedded Python ready."
& $PythonExe -c "import sys, flask; print(sys.version); print('Flask', flask.__version__)"
Write-Host ""
Write-Host "Use:"
Write-Host "  run-embedded.bat list"
Write-Host "  run-web-embedded.bat"
