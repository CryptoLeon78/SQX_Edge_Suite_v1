# A60 MT5 Active Terminal Mode

## Status

- Phase: A60
- Date: 2026-05-08
- Result: NO_GO operationally, tool improvement complete.
- Scope: retry A59 against an already-open MT5 terminal and add a safer CLI mode for that workflow.

## What Changed

A60 adds two operator controls to `dukas_mt5_ohlc_download.py`:

- `--use-active-terminal`: connects through `MetaTrader5.initialize()` without forcing the configured terminal path.
- `--initialize-timeout-ms`: allows a longer MT5 IPC initialization timeout.

The default config also now includes:

```json
"initializeTimeoutMs": 120000
```

This keeps the default path-based flow intact while allowing a second route when the terminal is already open.

## Local Terminal State

PowerShell confirmed the terminal process was open and responsive:

```text
ProcessName: terminal64
Path: C:\Program Files\Dukascopy MetaTrader 5\terminal64.exe
MainWindowTitle: Dukascopy MetaTrader 5 - Netting - EURUSD,H1
Responding: True
```

## Retry Command

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\dukas_mt5_ohlc_download.py --asset EURUSD --tf H1 --use-active-terminal --initialize-timeout-ms 120000 --coverage-dir analysis_output\dukas_mt5_download --output-dir data\ohlc --json
```

## Result

The terminal still returned:

```text
MT5 initialize failed: (-10005, 'IPC timeout')
```

This means the problem is no longer just the configured executable path. The open terminal is not accepting the Python MetaTrader5 IPC bridge in this environment/session.

## Next Real Checks

Before retrying A60/A61, verify inside Dukascopy MT5:

1. The account is fully logged in and data ticks are updating.
2. `EURUSD` is visible in Market Watch.
3. Algo/automated trading is enabled if the terminal requires it for Python IPC.
4. The terminal and Codex/PowerShell are running at the same privilege level, preferably both non-admin.
5. No modal dialog, update prompt, login prompt or server selection dialog is open.
6. If needed, close MT5 completely, reopen it manually, wait for quotes, then retry the A60 command.

## Promotion Criteria

A61 should only proceed to full OHLC download when the A60 command returns GO and writes:

```text
data\ohlc\EURUSD_H1.csv
```

