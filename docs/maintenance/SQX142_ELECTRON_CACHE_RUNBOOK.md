# SQX 142 Electron Cache Runbook

## Purpose

SQX 142 can serve fresh web bundles on `http://127.0.0.1:8080` while the local Electron app still shows stale UI from its persistent Chromium cache. This was confirmed on 2026-05-22 while validating the local Ollama Source Code Translator: `localhost:8080` showed the new translator bundle, but the local SQX app did not until Electron cache directories were moved to backup and SQX was restarted.

## Trigger

Use this runbook when all of the following are true:

- `http://127.0.0.1:8080` serves the expected SQX web UI or bundle changes.
- The local StrategyQuant X app does not show the same UI after a normal restart.
- The change touches `internal/plugins`, `internal/web/common/templates.html`, `internal/web/common/Batch*/libs.js` or `internal/web/common/Batch*/styles.css`.

For the Source Code Translator, the expected local app path is:

`Strategy/result -> Source Code -> Local Ollama Translator`

## Safe Refresh

Run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_electron_cache_refresh.ps1 -SQXRoot $env:SQX142_ROOT -Restart
```

The script:

- stops only StrategyQuant processes whose command line points at the selected SQX root;
- moves Electron cache folders to `SQX142_ROOT\.local_cache_backups\electron_squant_<timestamp>`;
- does not delete projects, databanks, SQX user settings, licenses or repository files;
- restarts `StrategyQuantX_nocheck.exe` when `-Restart` is used.

Moved cache folders:

- `Cache`
- `Code Cache`
- `GPUCache`
- `DawnCache`
- `blob_storage`
- `Network`
- `Session Storage`
- `Shared Dictionary`

## Smoke

After restart:

```powershell
curl.exe -sS --max-time 10 http://127.0.0.1:8080/common/templates.html | Select-String "Local Ollama Translator"
curl.exe -sS --max-time 10 http://127.0.0.1:8080/common/Batch1/libs.js | Select-String "translate-source-code"
curl.exe -sS --max-time 10 http://127.0.0.1:8080/common/Batch1/styles.css | Select-String "source-code-local-translator"
```

Then open the local SQX app and verify the same UI is visible under the `Source Code` result tab.

## Acceptance

- SQX listens on `5052` and `8080`.
- The served bundles contain `Local Ollama Translator`, `Source Code Translator · Local Ollama`, `/api/agent/translate-source-code` and `.source-code-local-translator`.
- The local Electron app shows the same translator control inside `Source Code`.
- A timestamped cache backup exists under `.local_cache_backups`.

## Notes

The build 144 `.sxp` package is useful as source material, but SQX 142 did not expose it as a standalone Result Plugin from `user/extend/ResultsPlugins`. The reliable SQX 142 integration point is the native `internal/plugins/ResultsSourceCode` result tab, with SQX regenerating the served web bundles at startup.
