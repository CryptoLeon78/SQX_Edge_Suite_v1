# SQX144 CUSTOM RESULTS5 SQX Edge Gate

Phase: `SQX144-CUSTOM-RESULTS5 - SQX Edge Gate`

Marker: `sqx144-custom-results5-edge-gate-v1`

Source-ready status: `custom_results5_edge_gate_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Installed status: `custom_results5_edge_gate_installed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool`

Date: 2026-06-11

## Purpose

CUSTOM-RESULTS5 creates an SQX Edge-owned ResultsPlugin called `SQX Edge Gate`. It is a separate tab candidate for SQX144 Full and does not replace, merge, rewrite or reinstall the original downloaded Custom Results from CUSTOM-RESULTS4.

The plugin identity is `Decision Gate` with a `Trading Radar` presentation. V1 is `Hybrid Gated`: it evaluates institutional stats by default and requests orders only after an explicit in-tab operator action.

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

`GET_ORDERS opt-in` means the plugin sends no order request on load, no order request after `STRATEGY_DATA`, and no order request after `STATS_RESPONSE`. It only sends `GET_ORDERS` after the operator presses `Activar Order Radar` inside the `SQX Edge Gate` tab.

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

## Institutional Decision Gate

The gate returns `PASS` only when all core institutional stats are present and pass:

- `NumberOfTrades >= 120`
- `ProfitFactor >= 1.3`
- `ReturnDDRatio >= 4`
- `RExpectancy > 0`
- `NetProfit > 0`

`REVIEW` covers intermediate metrics or missing non-critical OOS evidence. If SQX does not return separated OOS evidence, `OOS Integrity` is marked as review instead of inventing a conclusion.

`BLOCK` covers missing stats, very low evidence, clearly weak profitability/risk, negative expectancy or non-positive net profit.

## Trading Radar UI

The tab shows:

- Dominant verdict: `PASS`, `REVIEW` or `BLOCK`
- Radar axes: `Evidence`, `Profitability`, `Risk Efficiency`, `Expectancy`, `OOS Integrity`
- Reason chips with exact causes
- `Next Action`
- Optional `Order Radar` drawer for loss streaks, loss distribution and degradation signals after order opt-in
- Diagnostic disclaimer: no pass-state promotion and no host mutation

The debug API is exposed as `window.__SQX_EDGE_GATE__` for offline fixture smoke and contract tests.

## Install Closeout

Applied on 2026-06-11 after exact approval:

`APRUEBO SQX144 CUSTOM RESULTS5 EDGE GATE INSTALL host=sqx144_full plugin=sqx_edge_gate sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code`

Result:

- `installExecuted=true`
- `currentlyInstalled=true`
- `copiedFiles=6`
- `targetMatchesSource=true`
- SHA256 `203CEF7459211E371AA00A3FA8F25FE0E7AFC973036F833038B8416190657A1D`
- `backupCreated=false` because the target plugin folder did not exist before copy.
- Preflight stayed clean with `processCount=0`, blockers `[]` and warnings `[]`.
- Evidence ref: `.local/sqx144_custom_results5/sqx144_custom_results5_install_20260611_164955.json`.

Installed target:

- `sqx144_full/user/extend/ResultsPlugins/SQX Edge Gate`

Only the SQX Edge-owned `SQX Edge Gate` folder was copied. The original downloaded Custom Results tabs remain separate and untouched.

## Install Gate

The wrapper supports:

- `status`
- `smoke`
- `report`
- `approval-template`
- `install`

Current delivery is installed copy-only after the exact approval above. Future reinstall still requires a new clean preflight and the exact approval phrase.

Future install target, only after exact approval:

- `sqx144_full/user/extend/ResultsPlugins/SQX Edge Gate`

Future approval phrase:

`APRUEBO SQX144 CUSTOM RESULTS5 EDGE GATE INSTALL host=sqx144_full plugin=sqx_edge_gate sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code`

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
