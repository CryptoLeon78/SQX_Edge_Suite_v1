# A61 MT5 IPC Diagnostic

## Status

- Phase: A61
- Date: 2026-05-08
- Result: GO for MT5 IPC diagnostic; A58 range smoke still needs a recent-bars mode because the fixed historical range returned no bars.
- Scope: make the MT5 IPC blocker repeatable and traceable before any full OHLC download.

## What Changed

A61 adds:

- `backend/sqx-edge-tool/tools/mt5_ipc_diagnostic.py`
- `backend/sqx-edge-tool/test_mt5_ipc_diagnostic.py`

The diagnostic records:

- Python executable, version and architecture.
- MetaTrader5 package version.
- Open `terminal64` processes and window title.
- Initialization attempts via configured path, active terminal and portable mode.
- JSON/Markdown evidence under `analysis_output/mt5_ipc_diagnostic`.

The tool is internal/operator-only and excluded from buyer portable builds.

## Command

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\mt5_ipc_diagnostic.py --timeout-ms 10000 --json
```

## Current Finding

The local environment has:

- Python 3.14.3, 64-bit.
- `MetaTrader5` 5.0.5735.
- Dukascopy terminal at `C:/Program Files/Dukascopy MetaTrader 5/terminal64.exe`.
- Open terminal window: `Dukascopy MetaTrader 5 - Netting - EURUSD,H1`.

The A61 diagnostic returned GO:

```text
active_terminal: Success
configured_path_portable: Success
```

After IPC was available, a manual market-data probe confirmed `copy_rates_from_pos` returns recent `EURUSD` bars for `M15`, `H1` and `H4`.

The remaining issue is narrower: A58 range mode for `2010-01-01` to `2026-05-01` returned zero bars in this terminal session, while recent-position reads work.

## Next Real Action

Before attempting full OHLC download:

1. Add a controlled recent-bars mode to the A58 downloader.
2. Rerun the `EURUSD/H1` smoke with recent bars.
3. Only after `data\ohlc\EURUSD_H1.csv` exists, attempt broader asset/timeframe coverage.

Only after that should A62 run the full OHLC universe download and A56 validation. A62 must use the product manifest universe (`USDMXN` and `USDZAR`) rather than the external-folder draft universe (`AUDCHF` and `NZDCHF`).
