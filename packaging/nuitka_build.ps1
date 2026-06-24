<#
.SYNOPSIS
    Compile SQX Edge Tool into a standalone Windows directory with Nuitka.

.DESCRIPTION
    Must be run on Windows with Visual Studio Build Tools (MSVC) available.
    See packaging/NUITKA_BUILD.md for full prerequisites and validation steps.

    Pipeline:
    1. packaging/build_inputs.py  — harden product_manifest.json (channel=free,
       real public key required — exits with code 2 if placeholder detected).
    2. This script              — invoke Nuitka --standalone.

    The result is a directory (OutputDir/app_main.dist/) to be distributed via
    Inno Setup as a signed .exe installer.

.PARAMETER OutputDir
    Output directory for the Nuitka .dist folder (default: dist\nuitka_out).

.PARAMETER Port
    Flask listen port; overridable at runtime via SQX_PORT env var (default: 5050).

.PARAMETER StagingDir
    Directory where build_inputs.py writes the hardened manifest
    (default: dist\nuitka_staging).
#>
param(
    [string]$OutputDir   = "dist\nuitka_out",
    [int]   $Port        = 5050,
    [string]$StagingDir  = "dist\nuitka_staging"
)

$ErrorActionPreference = "Stop"

$ProjectRoot    = Split-Path -Parent $PSScriptRoot
$ToolRoot       = Join-Path $ProjectRoot "backend\sqx-edge-tool"
$EntryPoint     = Join-Path $ProjectRoot "packaging\app_main.py"
$AbsStagingDir  = Join-Path $ProjectRoot $StagingDir
$AbsOutputDir   = Join-Path $ProjectRoot $OutputDir

# ── Step 1: harden manifest ────────────────────────────────────────────────────
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

# ── Step 2: verify hardened manifest before compiling ─────────────────────────
$HardenedManifest = Join-Path $AbsStagingDir "product_manifest.json"
$manifest = Get-Content $HardenedManifest -Raw | ConvertFrom-Json
if ($manifest.build.channel -ne "free") {
    Write-Error "Hardened manifest has channel='$($manifest.build.channel)' — expected 'free'. Aborting."
    exit 1
}
Write-Host "    channel = $($manifest.build.channel)   kid = $($manifest.licensing.publicKey.kid)"

# ── Step 3: compile with Nuitka (--standalone; Inno Setup handles distribution) ─
Write-Host "==> Compiling with Nuitka --standalone..."
New-Item -ItemType Directory -Path $AbsOutputDir -Force | Out-Null

& python -m nuitka `
    --standalone `
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
    --include-data-files="$HardenedManifest=config/product_manifest.json" `
    "$EntryPoint"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Nuitka compilation failed."
    exit $LASTEXITCODE
}

$DistDir = Join-Path $AbsOutputDir "SQX_Edge_Tool.exe.dist"
Write-Host ""
Write-Host "Build complete : $DistDir"
Write-Host "Default port   : $Port (override at runtime: set SQX_PORT=$Port)"
Write-Host "Next step      : package $DistDir with Inno Setup into a signed installer."
Write-Host "Validate       : run SQX_Edge_Tool.exe on a clean Windows VM (no Python, no dev tools)."
