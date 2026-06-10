# SQX144 Electron Cache Refresh Runbook

Marker: `sqx144-electron-cache-refresh-v1`

## Purpose

Use this when `localhost:8080` serves the expected SQX144 web overlay but the StrategyQuant X desktop app still shows stale Data Manager UI after a normal restart.

This is especially useful after Data Manager overlay phases such as AUTO8, where the browser view may update before Electron's persistent Chromium cache does.

## Safe Scope

The script moves volatile Electron cache directories to a timestamped backup under the SQX144 host:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx144_electron_cache_refresh.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx144_electron_cache_refresh.ps1 plan
```

Real refresh is gated:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx144_electron_cache_refresh.ps1 refresh -Apply -Approval 'APRUEBO SQX144 ELECTRON CACHE REFRESH host=sqx144_full move_cache_only preserve_local_storage_indexeddb_preferences'
```

## Moved Folders

- `Cache`
- `Code Cache`
- `GPUCache`
- `DawnCache`
- `DawnGraphiteCache`
- `DawnWebGPUCache`
- `blob_storage`
- `Network`
- `Session Storage`
- `Shared Dictionary`
- `shared_proto_db`
- `VideoDecodeStats`

## Preserved State

The script must not move or delete:

- `Local Storage`
- `IndexedDB`
- `WebStorage`
- `Preferences`
- `Local State`
- `main-window-state.json`
- `DIPS`
- `SharedStorage`

It does not touch `data.db`, history, projects, databanks, SQX tasks, MT5, license material, or Migration Tool.

## Guards

- Host must resolve to governed `SQX_144_Full` / `sqx144_full`.
- Roots that look like SQX144 144.2953 / UPDATE2 are rejected.
- SQX processes for the target root must be closed.
- The script uses `Move-Item` only; it does not use `Remove-Item`.
- Every moved folder must resolve under Electron `userData\SQUANT`.

## Smoke

After refresh, open SQX144 Data Manager and verify the expected overlay UI appears. For AUTO8, the expected visual signal is the `Aplicar cambios` button in the `MT5 Bridge` panel.
