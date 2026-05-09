# R47 - Controlled Commercial Release Candidate

Date: 2026-05-09

## Objective

Refresh the buyer-ready portable ZIP after the Strategy Builder buyer-session support phases and record the real commercial state before any broader sales push.

This phase does not publish a GitHub Release and does not widen traffic. It prepares a current, tested release candidate for controlled first-buyer delivery only.

## Release Candidate

- Status: `controlled_commercial_candidate_ready`
- Portable ZIP: `dist/SQX_Edge_Tool_Portable_20260509_102131.zip`
- ZIP bytes: `15474256`
- ZIP SHA256: `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`
- Portable API port tested: `5062`
- Version reported by portable API: `0.2.0`

## Verification

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\release_checklist.ps1 -PortableApiPort 5062
```

Results:

- Frontend module contracts: passed.
- Python suite: `201 passed, 1 skipped`.
- `git diff --check`: passed.
- Portable ZIP build: passed.
- Distribution audit: passed.
- Clean extracted portable import check: passed.
- Clean extracted portable `/api/health`: passed.

## Commercial Use

This candidate is suitable for:

- assisted Pro demos;
- controlled early-access buyer delivery;
- manual license handoff;
- founder/beta buyer onboarding;
- support-assisted first sales.

This candidate is not yet suitable for:

- mass self-serve launch;
- public traffic expansion without a manual go/no-go review;
- profit, performance or trading-result claims;
- automatic publication to GitHub Releases.

## Buyer Handoff Notes

For a basic user, delivery should stay simple:

1. Send the ZIP plus the buyer onboarding note.
2. Ask the buyer to extract it into a normal folder such as `C:\SQX_Edge`.
3. Ask the buyer to double click `START_SQX_EDGE.bat`.
4. Send the signed license JSON separately when Pro activation is needed.
5. Keep support and refund/pause boundaries explicit.

## Security Boundary

The release checklist and distribution audit confirm that the portable build excludes private keys, signed customer licenses, local checkout evidence, relay/operator tools, generated OHLC data, backups, `dist`, `node_modules`, virtual environments and private commercial folders.

No publication has been performed in R47.

## Next Gate

Recommended next real step:

- SB17 if Strategy Builder buyer-session evidence needs one clean handoff index.
- M82 if controlled traffic expansion evidence is approved and the move is tiny and reversible.
- R46 only with explicit human approval to publish a GitHub Release.
