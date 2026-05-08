# A59 Real Data Validation

## Status

- Phase: A59
- Date: 2026-05-08
- Result: NO_GO
- Scope: local MT5/Dukascopy smoke before full OHLC universe download.

## What Was Verified

- `C:/Program Files/Dukascopy MetaTrader 5/terminal64.exe` exists locally.
- Python package `MetaTrader5` is installed in `backend/sqx-edge-tool/venv`.
- A58 downloader CLI runs and writes traceable coverage output.
- `data/ohlc` had no real OHLC CSV input before the A59 smoke.

## Smoke Command

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\dukas_mt5_ohlc_download.py --asset EURUSD --tf H1 --coverage-dir analysis_output\dukas_mt5_download --output-dir data\ohlc --json
```

## Result

The smoke reached the MT5 initialization boundary but returned:

```text
MT5 initialize failed: (-10005, 'IPC timeout')
```

This means the local terminal did not answer the Python IPC connection in time. A60 added an active-terminal retry mode and confirmed the timeout persists even when MT5 is already open and responsive.

Generated local evidence is intentionally ignored by git:

- `analysis_output/dukas_mt5_download/a58_dukas_mt5_download.json`
- `analysis_output/dukas_mt5_download/a58_dukas_mt5_download.md`
- `analysis_output/dukas_mt5_download/a58_dukas_mt5_download_coverage.csv`

## Next Operator Steps

1. Open Dukascopy MetaTrader 5 manually from `C:/Program Files/Dukascopy MetaTrader 5/terminal64.exe`.
2. Log in to the intended account and leave the terminal open until Market Watch is loaded.
3. Confirm `EURUSD` is visible/available in Market Watch.
4. Rerun the smoke command above.
5. Only after the smoke returns GO, run the full default A58 download:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\dukas_mt5_ohlc_download.py --coverage-dir analysis_output\dukas_mt5_download --output-dir data\ohlc --json
```

6. Then validate the OHLC folder through A56:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\real_mtf_pipeline_run.py --input-dir data\ohlc --work-dir analysis_output\real_mtf_pipeline_run --expected-assets-mode manifest --json
```

## GO Criteria

A59 can be promoted only when:

- A58 smoke for `EURUSD_H1.csv` returns GO.
- Full A58 download produces all required `H1`, `M30`, `M15` and `H4` CSV files for the configured manifest assets.
- A56 returns GO in manifest mode.
- The read-only MTF evidence panel continues to show only validated A56 GO output.
