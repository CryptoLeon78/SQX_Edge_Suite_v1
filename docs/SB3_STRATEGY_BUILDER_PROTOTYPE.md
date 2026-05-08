# SB3 Strategy Builder Read-Only Prototype

Phase SB3 adds the first native Strategy Builder prototype as a local, read-only package builder.

## Scope

- Add `app/js/modules/strategy-builder-core.js` as pure package-building logic.
- Add `app/js/modules/strategy-builder.js` as the dashboard facade for `tab-strategybuilder`.
- Add the `Strategy Builder` tab through `ui_manifest.json` and regenerated `app/js/manifest-data.js`.
- Build and preview `sqx-edge.strategy-builder-package` JSON locally.
- Allow local JSON export only when the operator review checkbox is confirmed.

## Runtime Boundaries

- No backend endpoint.
- No remote calls.
- No generated trading logic.
- No auto-trading, optimizer, broker or exchange integration.
- No profitability claim.
- No raw CSV persistence.
- No Top Picks restoration.
- No matrix/heatmap restoration.

## Package Prototype

The prototype supports:

- `blank` source mode for manual asset/timeframe/archetype packages.
- `cvc_handoff` sample mode using a J6-compatible reduced handoff payload.
- Project Generator profile suggestion.
- SQX Views validation pack suggestion.
- Operator checklist gating.

The package remains blocked until the workflow state reaches `package_exportable`.

## Public Contracts

`SQX.strategyBuilderCore` exports:

- `archetypes`
- `blockedStates`
- `buildContext`
- `buildPackage`
- `defaultValidationPack`
- `sampleCvcHandoff`
- `sourceModes`
- `states`
- `supportedAsset`

`SQX.strategyBuilder` exports:

- `build`
- `clear`
- `exportPackage`
- `ids`
- `init`
- `loadCvcSample`

## Verification

- Static dashboard tests assert script order, tab wiring, docs, exports and runtime boundaries.
- JS contracts assert package creation, blocked states, CVC sample handoff and UI preview behavior.
- E2E smoke opens the Strategy Builder tab on desktop and mobile, builds a CVC sample package and captures screenshots.
