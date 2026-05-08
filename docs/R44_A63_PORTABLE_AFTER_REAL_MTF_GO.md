# R44/A63 - Portable After Real MTF GO

Date: 2026-05-08

## Objective

Refresh the buyer portable release story after the real A56 multi-timeframe pipeline returned GO, without shipping local OHLC data, generated evidence or internal MT5 operator tools.

## Changes

- Added broad `analysis_output/` exclusion to portable packaging, distribution audit, release checklist and product manifest.
- Added explicit `analysis_output/real_mtf_pipeline_run` / `real_mtf_pipeline_run` guards for the A56 real-data run evidence.
- Kept MT5/Dukascopy downloader, MT5 IPC diagnostic, MT5 config, `data/ohlc/` and generated evidence outside buyer builds.
- Regenerated and validated a fresh portable ZIP after the real MTF GO.

## Verified ZIP

- ZIP: `dist/SQX_Edge_Tool_Portable_20260508_201652.zip`
- SHA256: `2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E`
- Bytes: `15380822`
- Portable API health: GO on port `5059`

## Checks

- `backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool\test_packaging.py backend\sqx-edge-tool\test_dashboard_static.py -q` -> `84 passed, 1367 subtests passed`
- `powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\release_checklist.ps1` -> GO
  - JS module contracts passed.
  - Full Python suite: `196 passed, 1 skipped`.
  - `git diff --check` passed.
  - Distribution audit passed.
  - Extracted portable API import and `/api/health` passed.

## Next

R45 can prepare a controlled publication record for this verified ZIP if we decide to publish it. Otherwise the next practical product tracks are PG7 buyer-specific `.cfx` handoff notes, V10 SQX Views pack comparison or SB1 Strategy Builder discovery.
