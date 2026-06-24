# SQX Edge — Nuitka Desktop Build

> ADR-0003 (Proposed). The portable ZIP remains the official release until the
> compiled .exe passes validation on a clean Windows VM.

## Prerequisites

| Requirement | Notes |
|---|---|
| **Windows 10/11** | Build must run on Windows; cross-compilation is not supported |
| **Visual Studio Build Tools 2022** (or VS Community) | Nuitka requires MSVC. Install "Desktop development with C++" workload. |
| **Python 3.11 or 3.12** | Same version as target end-users. 3.13 may work but is less tested with Nuitka. |
| **Nuitka 2.4.2** (pinned) | `pip install nuitka==2.4.2` in the build venv |
| **Inno Setup 6** | For producing the signed `.exe` installer from the standalone dist dir |
| **EV Code Signing certificate** | Required before any public release |

## Build venv setup

```powershell
python -m venv .venv-build
.venv-build\Scripts\Activate.ps1
pip install nuitka==2.4.2
pip install -r backend/sqx-edge-tool/requirements.txt
```

## H2 blocker — production public key

Before building a buyer artifact, replace the placeholder public key in
`backend/sqx-edge-tool/config/product_manifest.json`:

```powershell
# Generate the production RSA keypair (private key stays off repo)
.\backend\sqx-edge-tool\tools\license_keypair.ps1

# Verify kid does NOT contain "placeholder":
(Get-Content backend/sqx-edge-tool/config/product_manifest.json | ConvertFrom-Json).licensing.publicKey.kid
```

The build pipeline (`build_inputs.py`) will refuse to continue (exit code 2)
if the placeholder key is still present.

## Running the build

```powershell
# From the project root, with the build venv active:
.\packaging\nuitka_build.ps1

# Custom output dir:
.\packaging\nuitka_build.ps1 -OutputDir dist\release -Port 5050
```

The script runs in two phases:
1. **`build_inputs.py`** — validates the public key and writes a hardened
   `product_manifest.json` (`build.channel = "free"`) to `dist/nuitka_staging/`.
2. **Nuitka** — compiles `packaging/app_main.py` into
   `dist/nuitka_out/SQX_Edge_Tool.exe.dist/`.

## Output layout (standalone)

```
dist/nuitka_out/SQX_Edge_Tool.exe.dist/
  SQX_Edge_Tool.exe      ← run this on the target machine
  app/                   ← dashboard HTML/JS (from project root app/)
  templates/             ← .cfx templates (from backend/sqx-edge-tool/templates/)
  config/                ← config files; product_manifest.json is the HARDENED version
  *.dll / *.pyd          ← Python runtime + compiled modules
```

At startup, `app_main.py` sets `SQX_APP_ROOT` to the directory of the exe.
`core.app_paths.app_root()` and `project_root()` then return that directory,
so `config/`, `app/`, and `templates/` resolve correctly without a source tree.

## Packaging with Inno Setup

Point Inno Setup at the `SQX_Edge_Tool.exe.dist/` directory.  Sign the installer
with the EV certificate.  Record the resulting installer SHA256 in
`product_manifest.json` → `checkout.verifiedReleaseCandidate`.

## Validating the output

1. Copy the Inno Setup installer to a **clean Windows VM** (no Python, no Visual Studio, no dev tools).
2. Install and run; confirm `http://127.0.0.1:5050` loads the dashboard.
3. Confirm license gate is enforced (`channel = "free"`, not `"internal"`).
4. Confirm a real signed license activates Pro features.
5. Record SHA256 of the installer in `checkout.verifiedReleaseCandidate`.

## Rollback

The portable ZIP (`dist/SQX_Edge_Tool_Portable_*.zip`) is the official release
artifact until the Nuitka installer passes the clean-VM validation above.

## Data directories bundled

| Source | Bundle path | Contents |
|---|---|---|
| `app/` (project root) | `app/` | Dashboard HTML/JS |
| `backend/sqx-edge-tool/templates/` | `templates/` | .cfx templates |
| `dist/nuitka_staging/` | `config/` | Hardened `product_manifest.json` |
| `backend/sqx-edge-tool/config/` | `config/` | Other config JSONs |

`config/product_manifest.json` in the bundle is the **hardened** version
(channel=free, real public key), overriding the dev repo version.
