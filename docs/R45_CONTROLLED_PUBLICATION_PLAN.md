# R45 - Controlled Publication Plan

Date: 2026-05-08
Status: `prepared_not_published`

No publication has been performed in this phase. R45 only prepares the public-safe release plan for the already verified portable ZIP.

## Verified Candidate

- ZIP: `dist/SQX_Edge_Tool_Portable_20260508_201652.zip`
- SHA256: `2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E`
- Size: `15380822` bytes
- Source evidence: `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`
- Draft tag: `v0.2.0-r45`
- Draft release title: `SQX Edge Suite v0.2.0-r45 - Portable Release Candidate`

## Publication Boundary

- Do not publish automatically from Codex unless explicitly requested.
- Do not attach `data/ohlc/`, `analysis_output/`, private commercial docs, license payloads, keys, checkout events or relay evidence.
- Publish only the verified portable ZIP and its `.sha256` sidecar.
- Keep checkout paused unless a controlled buyer window is intentionally open.

## GitHub Release Draft

Suggested public release notes:

```markdown
SQX Edge Suite portable release candidate for Windows.

Included:
- One-click launcher with embedded Python runtime.
- Dashboard, Project Generator, Strategy Cleaner, SQX Views and local support diagnostics.
- Real MTF evidence integration validated internally, without shipping local OHLC data or generated analysis evidence.

Install:
1. Download the ZIP.
2. Extract it into a normal folder.
3. Double click START_SQX_EDGE.bat.
4. Close with STOP_SQX_EDGE.bat when finished.

SHA256:
2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E

Responsible scope:
SQX Edge does not promise trading profitability. It is an operational tool for organization, repeatability and traceability inside a StrategyQuant X workflow.
```

## Pre-Publication Gate

Run only after the GitHub Release draft exists, the ZIP is attached, the SHA256 is visible, support is ready and rollback is assigned:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\public_release_gate.py `
  --zip dist\SQX_Edge_Tool_Portable_20260508_201652.zip `
  --release-tag v0.2.0-r45 `
  --release-title "SQX Edge Suite v0.2.0-r45 - Portable Release Candidate" `
  --release-draft-url "https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/tag/v0.2.0-r45" `
  --rollback-owner "Ivan" `
  --support-owner "Ivan" `
  --confirm-github-release-reviewed `
  --confirm-zip-attached `
  --confirm-sha256-published `
  --confirm-checkout-paused-or-ready `
  --confirm-support-ready `
  --confirm-rollback-ready
```

Expected result before all confirmations are real: `NO-GO`.

## Post-Publication Record

Run only after the tag/release is actually published and the download has been tested:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\release_publication_record.py `
  --use-latest-public-release-gate `
  --zip dist\SQX_Edge_Tool_Portable_20260508_201652.zip `
  --sha256-file dist\SQX_Edge_Tool_Portable_20260508_201652.zip.sha256 `
  --release-tag v0.2.0-r45 `
  --release-url "https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/tag/v0.2.0-r45" `
  --download-url "https://github.com/CryptoLeon78/SQX_Edge_Suite_v1/releases/download/v0.2.0-r45/SQX_Edge_Tool_Portable_20260508_201652.zip" `
  --published-by "Ivan" `
  --confirm-git-tag-created `
  --confirm-github-release-published `
  --confirm-zip-download-tested `
  --confirm-sha256-matches `
  --confirm-release-notes-visible `
  --confirm-support-window-open `
  --confirm-rollback-window-open
```

## Rollback

- Unpublish or mark the GitHub Release as draft.
- Remove or replace the ZIP asset if checksum or packaging is wrong.
- Pause checkout links and manual fulfillment.
- Point buyers back to the previous verified ZIP only if its SHA256 is still documented.
- Record the decision with `hotfix_rollback_release.py` if a buyer-facing release was already live.

## Next Decision

R46 should only publish the GitHub Release if we explicitly decide to make this candidate public. If not publishing yet, continue with PG7 buyer-specific `.cfx` handoff, V10 SQX Views pack comparison or SB1 Strategy Builder discovery.
