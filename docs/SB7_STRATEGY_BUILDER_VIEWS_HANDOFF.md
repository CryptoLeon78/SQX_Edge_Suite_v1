# SB7 Strategy Builder SQX Views Handoff

Phase SB7 connects Strategy Builder packages to SQX Views validation packs without saving templates automatically.

## Scope

- Add `sqxViewsHandoffFromPackage` to `app/js/modules/strategy-builder-core.js`.
- Add `sendToViews` to `app/js/modules/strategy-builder.js`.
- Add `Enviar a SQX Views` to the Strategy Builder tab.
- Reuse the existing `SQX.viewCreator.openHandoff` contract to activate SQX Views, set the view name and apply the suggested validation preset.
- Keep the handoff local, reviewable and operator-controlled.

## Guardrails

- No automatic template save.
- No automatic `.vw` download.
- No backend endpoint.
- No API call.
- No generated trading logic.
- No plan-mining mutation.
- No hidden localStorage write.
- The package must be `package_exportable` before a SQX Views handoff can be prepared.
- The operator must press `Guardar preset` or `Descargar .vw` manually inside SQX Views.

## Handoff Mapping

The Strategy Builder core maps the package validation pack to an SQX Views preset:

| Validation pack | SQX Views preset | View name shape |
| --- | --- | --- |
| `robustness` | `robustness` | `SB {asset} {timeframe} Robustness` |
| `risk-capital-review` | `risk` | `SB {asset} {timeframe} Risk Review` |
| `asset-family-review` | `robustness` | `SB {asset} {timeframe} Asset Family Review` |
| `pro-setup-assist` | `risk` | `SB {asset} {timeframe} Pro Setup Review` |
| `free-core-validation` | `egt-core` | `SB {asset} {timeframe} Core Validation` |

Unknown validation packs fall back to the robustness view shape and return a warning.

## Runtime Boundaries

- Strategy Builder builds a pure handoff object first.
- The UI calls `SQX.viewCreator.openHandoff` only after the package passes the exportable gate.
- SQX Views receives field values and preset intent, then updates its preview.
- The bridge does not call `saveCurrentPreset`, `downloadView`, `buildPresetPackage` or any import/save helper.

## Verification

- JS contracts assert the pure handoff mapping, the UI button, SQX Views activation and the no-save boundary.
- Static dashboard tests assert SB7 documentation, public contracts and the new visible control.
- E2E smoke covers the Strategy Builder to SQX Views handoff and captures the prepared view.
