# TL12 - Per-Tester Signed License Delivery Flow

## Purpose

TL12 issues one signed tester license per approved pilot tester while keeping private keys, real license files and tester identity mapping outside Git. The active Cloudflare ZIP is not replaced during this phase.

## Current Issuance

- Signing key: local-only `license_keys/`, ignored by Git.
- Signed licenses: local-only `licenses_private/tester_pilot_20260512/`, ignored by Git.
- License count: 6 approved pilot testers.
- Plan: `pro_tester_15`.
- Window: 2026-05-12 to 2026-05-27.
- Machine policy: 1 supported machine per tester.
- Distribution channel: `tester_pilot`.
- Redistribution flag: `false`.

The committed repository contains only the public verification key in `backend/sqx-edge-tool/config/product_manifest.json`. The private key and signed tester license files must never be committed, zipped into the common portal asset or pasted into public channels.

## Tester Delivery Flow

1. Keep the protected tester portal active behind Cloudflare Access.
2. Keep the portal ZIP as a generic tester build without embedded `config/license.json`.
3. Send each tester their own license JSON privately, one-to-one, after they have passed Cloudflare Access.
4. Instruct the tester to download and extract the ZIP from the protected portal.
5. The tester starts SQX Edge with `START_SQX_EDGE.bat`.
6. In the `Inicio` tab, the tester opens `Licencia` and uses `Importar archivo` to select the assigned JSON license.
7. The app posts the license to the local-only endpoint `/api/license/import`.
8. The app should show an active Pro tester state with the expected expiry window.
9. The tester must not share the ZIP or the license file. Any support reply should include only the non-secret tester marker and local status, never the full license JSON.

The textarea paste path remains available as fallback, but the file import path is the recommended route for basic users.

## Operator Verification Before Replacing The Active ZIP

Before replacing the Cloudflare asset, run these checks locally:

1. Validate every local tester license against the committed public key.
2. Regenerate the tester ZIP after the public key update.
3. Confirm the ZIP contains no `config/license.json`, no private key material and no `license_signed_*.json`.
4. Prepare the portal asset locally and run the real-tool-delivery proof.
5. Smoke one private tester flow: Cloudflare Access, portal login, ZIP download, START BAT, import assigned license file, Pro tester status.
6. Replace the active ZIP only after the smoke passes.

## Boundaries

- TL12 is an offline signed-license gate, not full DRM.
- The license is signed and marked per tester, but it is not yet cryptographically bound to a physical device.
- Future hardening can add device fingerprint enrollment, remote revocation and per-tester download URLs.
