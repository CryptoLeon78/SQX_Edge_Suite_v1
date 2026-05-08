# SB4 Strategy Builder Import/Export Hardening

Phase SB4 hardens the local Strategy Builder handoff path without adding backend, cloud or generation behavior.

## Scope

- Add import validation to `app/js/modules/strategy-builder-core.js`.
- Add local JSON import controls to `tab-strategybuilder`.
- Accept two controlled input types:
  - `sqx-edge.strategy-builder-package`
  - `sqx-edge.strategy-builder-handoff`
- Rebuild imported data through the same `buildPackage` contract used by native previews.
- Require fresh operator review after import before export is allowed.
- The dashboard remains a dedicated tab.
- Keep Strategy Builder as a dedicated tab because the workflow now has enough context, preview and handoff surface to stand alone.

## Import Guardrails

- Imported packages are re-built through the same core contract instead of being trusted as-is.
- Unknown package types are blocked.
- Unsupported assets are blocked when the manifest is available.
- Known raw payload keys are blocked.
- Imported packages default to `blocked_operator_review` until the operator confirms manual review again.
- The import flow remains local browser file reading only.

## Runtime Boundaries

- No backend endpoint.
- No remote calls.
- No generated trading logic.
- No automatic StrategyQuant settings.
- No profitability claim.
- No persistent localStorage write.
- No Top Picks restoration.
- No matrix/heatmap restoration.

## Public Contracts

`SQX.strategyBuilderCore` now additionally exports:

- `importPayload`
- `validateImportPayload`

`SQX.strategyBuilder` now additionally exports:

- `importText`
- `importFile`

## Verification

- JS contracts cover package import, CVC handoff import, re-review gating and blocked raw payload keys.
- Static dashboard tests cover the new public contracts, import controls and SB4 documentation.
- E2E smoke exercises import through the browser-facing `importText` path on desktop and keeps the mobile Strategy Builder flow covered.
