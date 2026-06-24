# ADR-0003: Desktop Packaging with Nuitka

**Status:** Proposed  
**Date:** 2026-06-24  
**Governance:** G2 / Architecture-Docs

---

## Context

SQX Edge is currently distributed as a portable ZIP (Python/Flask + embedded CPython runtime).
The ZIP is launched via `START_SQX_EDGE.bat` → `run-web-embedded.bat` and requires a
pre-bootstrapped embedded Python tree. This approach works for controlled distribution but
has three friction points:

- Windows Defender and antivirus software flag arbitrary `.py` + embedded-Python ZIPs.
- The operator must run a bootstrap step before the app is usable.
- The `.bat`/`.py` launcher stack is visually distant from a professional desktop app.

## Decision

Package SQX Edge as a compiled Windows desktop application using the following stack:

| Layer | Technology |
|---|---|
| Python compilation | **Nuitka** (compiles `.py` → native `.pyd`/`.exe`) |
| Native window | **pywebview + WebView2** (Chromium-based, ships with Windows 11; bootstrapped on 10) |
| Installer | **Inno Setup** — signed `.exe` installer, NSIS as fallback |
| Code signing | **EV certificate** (Extended Validation) issued to the legal entity |

The compiled `.exe` includes the Flask app, all Python modules, and static assets.
The browser UI (`SQX_Dashboard_v6.html` and friends) is served locally on `127.0.0.1:5050`
exactly as today — no server-side changes required.

## Buyer build hardening (release requirements)

The following two items are **blocking** before any compiled build reaches a buyer:

### H1 — `build.channel` must be `"free"` in buyer artifacts

`backend/sqx-edge-tool/config/product_manifest.json` currently contains
`"channel": "internal"`. The `internal` access level grants `features: ["*"]`
(all features unlocked, no license required). Shipping this manifest bypasses the
entire licensing gate.

**Required action before release:** The Nuitka build pipeline must rewrite (or
substitute) `product_manifest.json` so that `build.channel` is `"free"` in the
compiled artifact. The dev/repo copy remains `"internal"` — only the packaged
buyer artifact is hardened.

### H2 — `licensing.publicKey.kid` must not contain `"placeholder"`

`product_manifest.json` contains `"kid": "sqx-prod-2026-05-placeholder"` and
a stub RSA public key. Any license signed with the real production private key
cannot be verified against this placeholder key.

**Required action before release:** Generate the production RSA keypair with
`backend/sqx-edge-tool/tools/license_keypair.ps1`, embed the real public key
in `product_manifest.json` (buyer build copy only), and keep the private key
off the repo and off the packaged artifact.

## Rollback

The portable ZIP (`dist/SQX_Edge_Tool_Portable_*.zip`) remains the **official
release artifact** until the Nuitka `.exe` installer passes end-to-end validation
on a clean Windows VM (no developer toolchain, no pre-installed Python).

Rollback trigger: any of — antivirus false-positive rate > 5%, WebView2 bootstrap
failure on Windows 10, or license verification regression.

## Consequences

- **Positive:** Professional UX, reduced AV friction, no exposed `.py` source in
  buyer hands, single-file distribution.
- **Negative:** Nuitka build time (~5–10 min), Inno Setup CI step, EV cert renewal
  cost/process, WebView2 bootstrap edge case on Windows 10.
- **Neutral:** Flask API surface is unchanged; all existing tests remain valid.

## Current portable ZIP status (as of 2026-06-24)

Both H1 and H2 are **active blockers** on the current ZIP too, not just the future
Nuitka build. `package_portable.ps1` copies `product_manifest.json` verbatim into
the stage without rewriting the channel or the public key. The ZIP therefore ships
`build.channel = "internal"` and `kid = "sqx-prod-2026-05-placeholder"`.

See `backend/sqx-edge-tool/test_buyer_build_hardening.py` for the guard tests
(currently marked `xfail` pending resolution of both blockers).
