# SB6 Strategy Builder Review Checklist and Preset Handoff

Phase SB6 makes the Strategy Builder review gate visible and adds a controlled Project Generator preset draft handoff.

## Scope

- Add `reviewChecklistSummary` to `app/js/modules/strategy-builder-core.js`.
- Add `projectGeneratorPresetDraftFromPackage` to `app/js/modules/strategy-builder-core.js`.
- Add `prepareProjectGeneratorPreset` to `app/js/modules/strategy-builder.js`.
- Render the Strategy Builder operator checklist as visible UI, not only inside the JSON preview.
- Add `Preparar preset PG` to fill Project Generator custom fields plus preset name.

## Guardrails

- No automatic preset save.
- No backend endpoint.
- No API call.
- No generated `.cfx`.
- No plan-mining mutation.
- No hidden localStorage write.
- The operator must press `Guardar preset` manually.
- The package must be `package_exportable` before a preset draft can be prepared.

## Preset Draft Mapping

The preset draft reuses the SB5 Project Generator custom mapping and adds a human-readable preset name:

`SB {asset} {timeframe} {archetype}`

Example:

`SB EURUSD H1 trend following`

The draft fills:

- Project Generator custom project fields.
- `Nombre del preset`.
- Custom status text explaining that saving is manual.
- Project Generator log evidence that the draft was prepared, not saved.

## Runtime Boundaries

- The bridge uses existing Project Generator DOM helpers.
- The bridge does not call `saveCustomPreset`.
- The bridge does not click any Project Generator action.
- The bridge keeps review, preset saving and generation under the operator's control.

## Verification

- JS contracts assert checklist summary, preset draft guardrails and UI handoff into Project Generator's preset field.
- Static dashboard tests assert SB6 documentation, public contracts and the new visible controls.
- E2E smoke covers the Strategy Builder tab and Project Generator handoff surface.
