# SQX144 CUSTOM RESULTS6 SQX Edge Gate V2

Phase: `SQX144-CUSTOM-RESULTS6 - SQX Edge Gate V2`

Marker: `sqx144-custom-results6-edge-gate-v2`

Source-ready status: `custom_results6_edge_gate_v2_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Installed status: `custom_results6_edge_gate_v2_installed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Date: 2026-06-11

## Purpose

CUSTOM-RESULTS6 evolves the SQX Edge-owned `SQX Edge Gate` ResultsPlugin into the final institutional decision tab. It remains a separate tab and does not replace, merge, rewrite or reinstall the original downloaded Custom Results from CUSTOM-RESULTS4.

This phase was installed after exact operator approval. The installed SQX144 Full host copy now matches the V2 source.

## Plugin Source

- Source: `integrations/sqx144/results_plugins/SQX Edge Gate`
- Runtime files: `index.html`, `edge-gate.js`, `fixtures/fixtures.js`
- Locales: `locales/en.json`, `locales/es.json`
- Wrapper: `tools/sqx144_custom_results5_edge_gate.ps1`
- Core: `backend/sqx-edge-tool/core/sqx144_custom_results5_edge_gate.py`
- Tests: `backend/sqx-edge-tool/test_sqx144_custom_results5_edge_gate.py`
- JS contract: `tests/js/contracts/sqx144_custom_results5_edge_gate_contracts.mjs`
- Render smoke: `tests/js/contracts/sqx144_custom_results5_edge_gate_render_smoke.mjs`

## Message Contract

Default messages:

- `STRATEGY_DATA`
- `SET_THEME`
- `SWITCH_THEME`
- `SET_LANGUAGE`
- `GET_STATS`
- `STATS_RESPONSE`

Opt-in messages:

- `GET_ORDERS`
- `ORDERS_RESPONSE`

`GET_ORDERS opt-in` means the plugin sends no order request on load, no order request after `STRATEGY_DATA`, and no order request after `STATS_RESPONSE`. It only sends `GET_ORDERS` after the operator presses `Activar Order Radar`.

Blocked:

- `GET_SOURCE_CODE`
- remote or local `fetch`
- `localStorage`, `sessionStorage`, `indexedDB`
- plugin create/rename/delete endpoints
- file writes from the runtime
- `data.db`
- `user/projects`
- databanks
- SQX tasks
- Migration Tool

## Stage-Aware Gate

`Pipeline Context` supports auto-detect plus manual override:

- `Build`: trades 120/80/60, PF 1.30/1.05, RetDD 4.0/1.5, missing OOS = REVIEW.
- `Retest 0`: trades 100/70/50, PF 1.25/1.05, RetDD 3.5/1.5, missing OOS = REVIEW.
- `Retest 1`: trades 100/70/50, PF 1.20/1.03, RetDD 3.0/1.3, missing OOS = REVIEW.
- `Tick Real`: trades 80/50/30, PF 1.15/1.00, RetDD 2.0/1.0, optional previous retest trades input, retention PASS >=70%, REVIEW >=40%, BLOCK <40%, missing reference = REVIEW.
- `Forward`: trades 50/30/20, PF 1.15/1.00, RetDD 2.0/1.0, missing internal OOS is marked as `OOS inferred by stage`.
- `Portfolio Candidate`: trades 150/100/70, PF 1.20/1.05, RetDD 4.5/2.0, missing OOS = REVIEW.

Core hard checks remain: `RExpectancy > 0` and `NetProfit > 0`.

## Gate Score

V2 adds `Gate Score 0-100` for ranking REVIEW candidates only. It does not approve by points and does not override `PASS`, `REVIEW` or `BLOCK`.

Weights:

- Evidence 25%
- Profitability 20%
- Risk Efficiency 25%
- Expectancy 15%
- OOS Integrity 15%

## Repair Actions

Reason chips now include repair action text:

- Low trades: no promote; review universe/TF or discard.
- Low PF: do not rescue by touching filters; return to robustness.
- Low Ret/DD: risk is not efficient; review DD clusters.
- Missing OOS: confirm sampleType/OOS before decision.

## Order Radar V2

Order Radar remains opt-in and computes:

- max loss streak
- average loss vs worst loss
- profit decay by thirds
- top 5 trade PnL concentration
- late degradation
- few-order and incomplete timestamp warnings

Order signals can harden `PASS` to `REVIEW`, but cannot promote a candidate into `PASS`.

## Decision Matrix And Export

The visible UI now prioritizes the institutional decision surface:

- `Decision Matrix` shows every gate axis with stage target, measured detail, score and repair action.
- The previous large `Methodology Guardrails`, `Official Tabs` and `Manual Export` panels are no longer rendered.
- `Order Radar V2` stays collapsed until the operator presses `Activar Order Radar`.
- `Copy Summary` remains a compact header action; it attempts clipboard copy and falls back to a hidden selectable textarea. No files are written from the tab.

The safety contract is preserved in runtime guards, tests, footer copy and the debug API `contractStatus`; it is no longer displayed as a large panel.

## Install Closeout

Applied on 2026-06-11 after exact approval:

`APRUEBO SQX144 CUSTOM RESULTS6 EDGE GATE V2 INSTALL host=sqx144_full plugin=sqx_edge_gate_v2 sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code`

Result:

- `installExecuted=true`
- `currentlyInstalled=true`
- `copiedFiles=6`
- `targetMatchesSource=true`
- SHA256 `803314F33732533A046CC74C1237C352D90BEE94C66C86F36E95B55CAC100BB0`
- `backupCreated=true`
- `backupId=custom_results6_install_20260611_205049`
- Preflight stayed clean with `processCount=0`, blockers `[]` and warning `target_plugin_differs_backup_required`.
- Evidence ref: `.local/sqx144_custom_results6/sqx144_custom_results6_install_20260611_205049.json`.

Installed target:

- `sqx144_full/user/extend/ResultsPlugins/SQX Edge Gate`

Only the SQX Edge-owned `SQX Edge Gate` folder was copied. The original downloaded Custom Results tabs remain separate and untouched.

## Readiness Panel Review

`SQX Edge Readiness Panel` is installed in SQX144 Full, but inspection shows it is a SQX142 carryover:

- Host index hash: `DACE1D0A26A0B013C60A19668C25158FAE0D28D554325821B856073994BFB3F0`.
- SQX142 source index hash: `DACE1D0A26A0B013C60A19668C25158FAE0D28D554325821B856073994BFB3F0`.
- Host fixture hash: `365045FA198DF8B246DE766652EACE54142772F05E522ED0877A7ADCF19A98DB`.
- SQX142 source fixture hash: `365045FA198DF8B246DE766652EACE54142772F05E522ED0877A7ADCF19A98DB`.
- Runtime marker: `sqx142-internal-safe2-readiness-panel-v1`.
- Requests: `GET_STATS`, `GET_LAST_SETTINGS_XML`, `GET_SYMBOL_INFO`.

CUSTOM-RESULTS7 applied that recommendation: the panel was retired from active SQX144 Full `ResultsPlugins` by moving it to backup under `sqx144_custom_results7_readiness_panel_retire_20260611_205723`, not deleting source. It remains preserved as historical/diagnostic material in SQX142 source. See `docs/SQX144_CUSTOM_RESULTS7_READINESS_PANEL_RETIREMENT.md`.

## Install Gate

Future reinstall target, only after exact approval:

- `sqx144_full/user/extend/ResultsPlugins/SQX Edge Gate`

Future reinstall approval phrase:

`APRUEBO SQX144 CUSTOM RESULTS6 EDGE GATE V2 INSTALL host=sqx144_full plugin=sqx_edge_gate_v2 sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code`

Install preflight requires:

- SQX closed and relevant process count zero
- host profile `sqx144_full`
- host root leaf `SQX_144_Full`
- backup/hash/rollback path
- copy only the SQX Edge-owned `SQX Edge Gate` folder
- do not touch the five original downloaded plugins
- do not install `RandomEntries`

## Verification

Required checks:

- `python -m pytest backend\sqx-edge-tool\test_sqx144_custom_results5_edge_gate.py -q`
- `node tests\js\contracts\sqx144_custom_results5_edge_gate_contracts.mjs`
- `node tests\js\contracts\sqx144_custom_results5_edge_gate_render_smoke.mjs`
- `tools\sqx144_custom_results5_edge_gate.ps1 smoke`
- `tools\sqx144_custom_results5_edge_gate.ps1 report`
- `python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `git diff --check`

## Boundaries

- No SQX runtime launch.
- No `data.db` mutation.
- No `user/projects` mutation.
- No databank mutation.
- No SQX tasks.
- No Migration Tool.
- No source-code access/export.
- No replacement or modification of the original Custom Results tabs.
- No profitability guarantee, no risk-zero claim and no automatic promotion inside SQX.
