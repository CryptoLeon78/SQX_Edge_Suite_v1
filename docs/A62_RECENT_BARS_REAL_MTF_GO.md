# A62 Recent-Bars Real MTF GO

## Status

- Phase: A62
- Date: 2026-05-08
- Result: GO
- Scope: produce real OHLC coverage from Dukascopy MT5 and validate it through A56.

## What Changed

A62 adds `--recent-bars` to `dukas_mt5_ohlc_download.py`.

This uses `copy_rates_from_pos(symbol, timeframe, 0, N)` instead of a fixed historical date range. The mode is useful when the terminal has recent chart/history data available but a long `copy_rates_range` request returns no bars.

The MT5 symbol map was aligned with the product manifest universe:

- Removed external-draft assets: `AUDCHF`, `NZDCHF`
- Added product assets: `USDMXN`, `USDZAR`

## Commands Run

Smoke:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\dukas_mt5_ohlc_download.py --asset EURUSD --tf H1 --use-active-terminal --initialize-timeout-ms 30000 --recent-bars 500 --coverage-dir analysis_output\dukas_mt5_download --output-dir data\ohlc --json
```

Full universe:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\dukas_mt5_ohlc_download.py --use-active-terminal --initialize-timeout-ms 30000 --recent-bars 500 --coverage-dir analysis_output\dukas_mt5_download --output-dir data\ohlc --json
```

A56 validation:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\real_mtf_pipeline_run.py --input-dir data\ohlc --work-dir analysis_output\real_mtf_pipeline_run --expected-assets-mode manifest --json
```

## Result

Downloader:

- Status: GO
- Assets requested: 33
- Assets activated: 33
- Missing symbols: 0
- Jobs: 132
- Downloaded: 132
- Failed: 0
- Total bars: 66000

A56:

- Status: GO
- A55 OHLC metric builder: GO
- A53 source intake: GO
- A54 guarded plan artifacts: GO
- Failures: none

Generated evidence remains local and ignored by git:

- `data/ohlc/*.csv`
- `analysis_output/dukas_mt5_download/*`
- `analysis_output/real_mtf_pipeline_run/*`

## Next

R44/A63 should refresh the portable/release story now that the read-only MTF evidence path has real A56 GO output available locally.

