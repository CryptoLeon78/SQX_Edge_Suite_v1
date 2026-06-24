# SQX Edge — Nuitka Desktop Build

> ADR-0003 (Proposed). The portable ZIP remains the official release until the
> compiled .exe passes validation on a clean Windows VM.

## Prerequisites

| Requirement | Notes |
|---|---|
| **Windows 10/11** | Build must run on Windows; cross-compilation is not supported |
| **Visual Studio Build Tools 2022** (or VS Community) | Nuitka requires MSVC. Install "Desktop development with C++" workload. |
| **Python 3.11 or 3.12** | Same version as target end-users. 3.13 may work but is less tested with Nuitka. |
| **Nuitka 4.1.3** (pinned) | Validated version; install via `requirements-build.txt` |
| **WebView2 Runtime** | Required on the **target** machine to display the native window. Windows 11 includes it by default. Windows 10 users must install the [Evergreen Bootstrapper](https://developer.microsoft.com/microsoft-edge/webview2/) (tiny download, auto-updates). The build machine does not need WebView2. |
| **Inno Setup 6** | For producing the signed `.exe` installer from the standalone dist dir |
| **EV Code Signing certificate** | Required before any public release |

## Build venv setup

```powershell
python -m venv .venv-build
.venv-build\Scripts\Activate.ps1
pip install -r packaging/requirements-build.txt
pip install -r backend/sqx-edge-tool/requirements.txt
```

`packaging/requirements-build.txt` pins `nuitka==4.1.3`, `pywebview>=4.0`, and
`pythonnet>=3.0`.  pythonnet is the CLR bridge that pywebview's EdgeChromium
backend uses to host WebView2; listing it explicitly helps Nuitka discover it.

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

# Toolchain spike (insecure, no hardening, opens a console window):
.\packaging\nuitka_build.ps1 -Dev
```

The script runs in two phases:
1. **`build_inputs.py`** — validates the public key and writes a hardened
   `product_manifest.json` (`build.channel = "free"`) to `dist/nuitka_staging/`.
2. **Nuitka** — compiles `packaging/app_main.py` into a standalone directory.

## pywebview bundling

The native window uses pywebview with the EdgeChromium (WebView2) backend.
Nuitka includes the following extra flags to bundle it correctly:

```
--include-package=webview         # pywebview Python package
--include-package-data=webview    # bundles webview/lib/ DLLs + .NET assemblies
--include-package=clr             # pythonnet CLR bridge (EdgeChromium backend)
```

If `--include-package=clr` fails during compilation (Nuitka reports the package
is not found), try one of these alternatives (see comments in `nuitka_build.ps1`):

- `--include-module=clr` — single-module form
- `--include-package=pythonnet` — alternative package name

## Output layout (standalone)

```
dist/nuitka_out/SQX_Edge_Tool.exe.dist/
  SQX_Edge_Tool.exe      <- run this on the target machine
  app/                   <- dashboard HTML/JS (from project root app/)
  templates/             <- .cfx templates (from backend/sqx-edge-tool/templates/)
  config/                <- config files; product_manifest.json is the HARDENED version
  webview/               <- pywebview lib/ DLLs and .NET assemblies (WebView2 host)
  *.dll / *.pyd          <- Python runtime + compiled modules
```

At startup, `app_main.py` sets `SQX_APP_ROOT` to the directory of the exe.
`core.app_paths.app_root()` and `project_root()` then return that directory,
so `config/`, `app/`, and `templates/` resolve correctly without a source tree.

The app opens a native window via `webview.start()`.  Set `SQX_NO_WINDOW=1` to
run headless (API only, no window).

## Packaging with Inno Setup

Point Inno Setup at the `SQX_Edge_Tool.exe.dist/` directory.  Sign the installer
with the EV certificate.  Record the resulting installer SHA256 in
`product_manifest.json` → `checkout.verifiedReleaseCandidate`.

## Validating the output

1. Copy the Inno Setup installer to a **clean Windows VM** (no Python, no Visual Studio, no dev tools).
2. Install and run; confirm the native window opens and loads the dashboard.
3. Confirm `http://127.0.0.1:<port>/api/health` returns `{"ok": true}`.
4. Confirm license gate is enforced (`channel = "free"`, not `"internal"`).
5. Confirm a real signed license activates Pro features.
6. Record SHA256 of the installer in `checkout.verifiedReleaseCandidate`.

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
