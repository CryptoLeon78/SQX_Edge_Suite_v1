# TL11 Anti-Redistribution License Gate

## Purpose

TL11 turns the tester ZIP from a protected download into a protected-use package. Cloudflare Access protects delivery, while the local tool now supports tester/pro builds that require a signed license file before Pro capabilities activate.

## Operating Model

- `internal` profile remains for development only.
- `tester` profile rewrites the packaged `product_manifest.json` to:
  - `build.channel = tester`
  - `build.defaultPlan = free`
  - `build.activationMode = signed_tester_file`
- Without `backend/sqx-edge-tool/config/license.json`, tester packages stay in Free/locked mode.
- With a signed tester license, Pro endpoints unlock and `/api/license/status` exposes public-safe traceability fields:
  - `license_id`
  - `customer_email`
  - `machine_limit`
  - `distribution.channel`
  - `distribution.tester_marker`
  - `distribution.redistribution_allowed`

## Packaging

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython -ReleaseProfile tester
```

To package for one approved tester after issuing a signed license outside Git:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython -ReleaseProfile tester -LicensePath C:\PRIVATE\license_signed_tester.json
```

The private key and license issuer remain excluded from portable ZIPs. A signed license may be included only as `backend/sqx-edge-tool/config/license.json`; distribution audit validates that it has signature fields and no private key fields.

## Limits

This phase does not make redistribution impossible. It removes the current high-risk gap where a shared ZIP could run as an internal build. A copied tester ZIP can still be copied together with its signed license, but it becomes traceable and revocable in support policy. Device binding and online revocation remain future phases.
