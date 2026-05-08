# SB5 Strategy Builder to Project Generator Prefill

Phase SB5 connects the Strategy Builder package to Project Generator as a controlled custom-project prefill.

## Scope

- Add `projectGeneratorPrefillFromPackage` to `app/js/modules/strategy-builder-core.js`.
- Add `sendToProjectGenerator` to `app/js/modules/strategy-builder.js`.
- Add the `Enviar a Project Generator` action to `tab-strategybuilder`.
- Fill Project Generator's `Custom libre` form from an exportable Strategy Builder package.
- Switch to the Project Generator tab after the form is filled.

## Guardrails

- Prefill only.
- No backend endpoint.
- No API call.
- No automatic generation.
- No custom preset is saved automatically.
- No plan-mining mutation.
- The operator must press `Generar custom` manually.
- The package must be `package_exportable` unless a contract test explicitly opts into blocked-package mapping.

## Field Mapping

| Strategy Builder package | Project Generator custom field |
| --- | --- |
| `asset_profile.asset` | `Asset / Simbolo` |
| `asset_profile.timeframe` | `Timeframe` |
| `project_generator_handoff.suggested_project_name` | `Nombre del proyecto` |
| `idea_archetype.id` | Blocksetting family |
| `asset_profile.direction_bias` | Direction, falling back to `both` |
| controlled default | `Capa 1` |

## Runtime Boundaries

- The bridge uses existing Project Generator DOM helpers.
- The bridge does not call `generateCustom`.
- The bridge does not click any Project Generator action.
- The bridge leaves review and generation under the operator's control.

## Verification

- JS contracts assert the pure prefill mapping and the UI handoff into Project Generator fields.
- Static dashboard tests assert SB5 documentation, public contracts and the new button.
- E2E smoke clicks the Strategy Builder handoff, verifies Project Generator fields and confirms no generation is triggered.
