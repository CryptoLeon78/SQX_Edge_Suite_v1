# REMOTE-SQX142 Alignment

## Summary

REMOTE-SQX142 aligns the local remote-service host with the StrategyQuant X 142 environment before any tester movement. The backend was previously healthy against an SQX 139 path; this mini phase switches the ignored local `backend/sqx-edge-tool/config.json` to SQX 142 and validates generation against the SQX 142 `data.db`.

This phase is local operational evidence only. SQX installation folders, `data.db`, generated probes and raw config backups stay outside Git.

## Local Alignment

- Active SQX host source: `C:/BOTS/Versiones/SQX_142_Crack`.
- Active `data.db`: `C:/BOTS/Versiones/SQX_142_Crack/user/data/data.db`.
- Active projects directory: `C:/BOTS/Versiones/SQX_142_Crack/user/projects`.
- Active Darwinex index aliases: `USTEC -> NDX_darwinex` and `GER40 -> GDAXI_darwinex`.
- Previous ignored config was backed up under `.local/remote_service/sqx142_alignment/`.

## Verification

- `/api/health` returns `ok=true` and reports SQX 142 paths.
- `tools/remote_service_preflight.ps1 -RequireSqxReady -Json` returns `ok=true`.
- `/api/validate-sqx-path` confirms executable, `data.db` and `projects` directory exist.
- `data.db` exposes Darwinex broker records, including `_darwinex` symbols.
- Probe `.cfx` generation passed for:
  - `XAUUSD H1 LONG BS_Tendencia_v6`: `costs_source=db`, `data_available=true`.
  - `USDJPY H4 BOTH BS_Volatilidad_v6`: `costs_source=db`, `data_available=false`.
- Internal `.cfx` inspection found matching `Chart symbol` and `Resources/Symbols` entries, with `InstrumentInfo` present and no resource mismatch.

## Operational Notes

- `data_available=false` on a generated probe means the SQX 142 database contains broker cost/resource information but no historical rows for that exact symbol source. It does not block `.cfx` structure, but it should be reviewed before choosing assets for tester demos.
- Project Generator direction input accepts `L/S` or `both` for bidirectional generation; `L+S` is not a backend direction token.
- REMOTE-OPS1 remains blocked only by Cloudflare Tunnel/Access private evidence after this alignment.

## Gate

Before testers use the remote host, the active backend config must continue to pass SQX 142 preflight and at least one generated `.cfx` probe must preserve:

- resolved BlockSetting v6 trace;
- costs from SQX 142 `data.db`;
- aligned `Chart symbol`;
- matching `Resources/Symbols`;
- non-empty `InstrumentInfo`;
- no broker/source null resource errors.
