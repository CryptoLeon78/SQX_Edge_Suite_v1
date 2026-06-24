<#
.SYNOPSIS
    Compile SQX Edge Tool into a standalone Windows directory with Nuitka.

.DESCRIPTION
    Must be run on Windows with Visual Studio Build Tools (MSVC) available.
    See packaging/NUITKA_BUILD.md for full prerequisites and validation steps.

    Pipeline (default / release):
    1. packaging/build_inputs.py - harden product_manifest.json (channel=free,
       real public key required - exits with code 2 if placeholder detected).
    2. Nuitka --standalone compilation.

    Pipeline (-Dev / toolchain spike):
    1. SKIP harden - uses repo product_manifest.json as-is (channel=internal).
    2. Prints an INSECURE DEV BUILD warning (red) and continues.
    3. Nuitka --standalone compilation with the raw repo manifest.
    -Dev builds MUST NOT be distributed to buyers.

    The result is a directory (OutputDir/SQX_Edge_Tool.exe.dist/) to be
    distributed via Inno Setup as a signed .exe installer (release builds only).

.PARAMETER OutputDir
    Output directory for the Nuitka .dist folder (default: dist\nuitka_out).

.PARAMETER Port
    Flask listen port; overridable at runtime via SQX_PORT env var (default: 5050).

.PARAMETER StagingDir
    Directory where build_inputs.py writes the hardened manifest
    (default: dist\nuitka_staging).

.PARAMETER Dev
    Skip manifest hardening and use the repo manifest as-is. For toolchain
    spikes only. The build is insecure and must not be distributed.
#>
param(
    [string]$OutputDir  = "dist\nuitka_out",
    [int]   $Port       = 5050,
    [string]$StagingDir = "dist\nuitka_staging",
    [switch]$Dev
)

$ErrorActionPreference = "Stop"

$ProjectRoot   = Split-Path -Parent $PSScriptRoot
$ToolRoot      = Join-Path $ProjectRoot "backend\sqx-edge-tool"
$EntryPoint    = Join-Path $ProjectRoot "packaging\app_main.py"
$AbsOutputDir  = Join-Path $ProjectRoot $OutputDir

# ---- Manifest selection ------------------------------------------------------
if ($Dev) {
    Write-Host ""
    Write-Host "################################################################" -ForegroundColor Red
    Write-Host "#  INSECURE DEV BUILD - NO DISTRIBUIR                          #" -ForegroundColor Red
    Write-Host "#  channel=internal  |  placeholder public key                 #" -ForegroundColor Red
    Write-Host "#  Use only for local toolchain spikes. Never ship to buyers.  #" -ForegroundColor Red
    Write-Host "################################################################" -ForegroundColor Red
    Write-Host ""
    $ManifestToBundle = Join-Path $ToolRoot "config\product_manifest.json"
    Write-Host "==> Dev mode: using repo manifest as-is ($ManifestToBundle)"
} else {
    # ---- Step 1: harden manifest ---------------------------------------------
    $AbsStagingDir = Join-Path $ProjectRoot $StagingDir
    Write-Host "==> Hardening buyer manifest..."
    & python (Join-Path $ProjectRoot "packaging\build_inputs.py") --staging-dir $AbsStagingDir
    if ($LASTEXITCODE -eq 2) {
        Write-Error "[H2] Cannot build buyer artifact: placeholder public key in product_manifest.json. Replace with the real production key (license_keypair.ps1) and re-run."
        exit 2
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Error "build_inputs.py failed (exit $LASTEXITCODE)."
        exit 1
    }

    # ---- Step 2: verify hardened manifest ------------------------------------
    $HardenedManifest = Join-Path $AbsStagingDir "product_manifest.json"
    $manifest = Get-Content $HardenedManifest -Raw | ConvertFrom-Json
    if ($manifest.build.channel -ne "free") {
        Write-Error "Hardened manifest has channel='$($manifest.build.channel)' - expected 'free'. Aborting."
        exit 1
    }
    Write-Host "    channel = $($manifest.build.channel)   kid = $($manifest.licensing.publicKey.kid)"
    $ManifestToBundle = $HardenedManifest
}

# ---- Step 3: compile with Nuitka --------------------------------------------
Write-Host "==> Compiling with Nuitka --standalone..."
New-Item -ItemType Directory -Path $AbsOutputDir -Force | Out-Null

# Set PYTHONPATH so Nuitka resolves `from api.server import app` and core.*
$env:PYTHONPATH = $ToolRoot

& python -m nuitka `
    --standalone `
    --assume-yes-for-downloads `
    --output-dir="$AbsOutputDir" `
    --output-filename="SQX_Edge_Tool.exe" `
    --enable-console `
    --include-package=flask `
    --include-package=jinja2 `
    --include-package=werkzeug `
    --include-package=click `
    --include-package=blinker `
    --include-package=itsdangerous `
    --include-package=markupsafe `
    --include-package=core `
    --include-package=api `
    --include-data-dir="$ProjectRoot\app=app" `
    --include-data-dir="$ToolRoot\templates=templates" `
    --include-data-dir="$ToolRoot\config=config" `
    --include-data-files="$ManifestToBundle=config/product_manifest.json" `
    "$EntryPoint"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Nuitka compilation failed."
    exit $LASTEXITCODE
}

# Locate the compiled exe rather than hardcoding the .dist folder name
$exe = Get-ChildItem -Recurse -Filter "SQX_Edge_Tool.exe" $AbsOutputDir | Select-Object -First 1
if (-not $exe) {
    Write-Error "SQX_Edge_Tool.exe not found after compilation in $AbsOutputDir."
    exit 1
}
$DistDir = $exe.Directory.FullName

Write-Host ""
if ($Dev) {
    Write-Host "Dev build complete : $DistDir" -ForegroundColor Yellow
    Write-Host "REMINDER: channel=internal, placeholder key - DO NOT DISTRIBUTE." -ForegroundColor Red
} else {
    Write-Host "Build complete : $DistDir"
    Write-Host "Default port   : $Port (override at runtime: set SQX_PORT=$Port)"
    Write-Host "Next step      : package $DistDir with Inno Setup into a signed installer."
    Write-Host "Validate       : run SQX_Edge_Tool.exe on a clean Windows VM (no Python, no dev tools)."
}
