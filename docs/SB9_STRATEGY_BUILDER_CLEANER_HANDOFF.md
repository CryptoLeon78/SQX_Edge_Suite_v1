# SB9 Strategy Builder Strategy Cleaner Draft Handoff

Phase SB9 adds a controlled Strategy Builder handoff to Strategy Cleaner without scanning folders or modifying `.sqx` files.

## Scope

- Add `strategyCleanerDraftFromPackage` to `app/js/modules/strategy-builder-core.js`.
- Add `prepareStrategyCleaner` to `app/js/modules/strategy-builder.js`.
- Add `Preparar Cleaner` to the Strategy Builder tab.
- Pre-fill Strategy Cleaner options inside Project Generator:
  - recursive scan enabled,
  - `ExitAfterBars` cleanup selected,
  - institutional rename selected,
  - rename pattern `{asset}_{tf}_{dir}_{id}`.
- Add the handoff to the visible session audit trail.

## Guardrails

- No backend endpoint.
- No API call from Strategy Builder.
- No folder scan triggered.
- No `.sqx` file mutation.
- No automatic cleanup.
- No hidden localStorage write.
- The operator must select the folder manually.
- The operator must press `Escanear` and `Procesar seleccion` manually.

## Runtime Boundary

Strategy Builder only prepares the draft state in the existing Strategy Cleaner UI. The existing Cleaner remains the owner of real actions:

- `cln-scan` still owns listing files.
- `cln-preview` still owns rename preview.
- `cln-process` still owns cleanup and backup-protected mutation.

This keeps the commercial "only one platform" flow useful without making Strategy Builder an execution surface.

## Verification

- JS contracts assert the pure draft mapping, UI handoff, cleaner options and session audit trail.
- Static dashboard tests assert SB9 documentation, public contracts and the new visible control.
- E2E smoke asserts the Cleaner draft does not scan files and logs the manual cleanup boundary.
