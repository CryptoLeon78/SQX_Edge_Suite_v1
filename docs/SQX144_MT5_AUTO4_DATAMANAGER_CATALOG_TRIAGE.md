# SQX144-MT5-AUTO4 - Data Manager Catalog Triage

Marker: `sqx144-mt5-auto4-datamanager-catalog-triage-v1`
Status: `auto4_overlay_installed_verified_no_db_no_projects_no_databanks_no_tasks`
Host: `sqx144_full`

## Purpose

AUTO4 installs the Data Manager MT5 button triage overlay so the installed button consumes AUTO3 before asking MT5 for a fresh bridge response.

This phase installs only Data Manager overlay web assets after exact approval. It does not write `data.db`, create instruments, import history, mutate projects/databanks, run SQX tasks or use Migration Tool.

## Behavior

The overlay source `integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js` now carries marker `sqx144-mt5-auto4-datamanager-catalog-triage-v1` while preserving the AUTO2 button marker.

When the operator clicks the button, the source flow is:

1. Detect selected Data Manager symbol.
2. Call `POST /api/sqx144/mt5-auto3/catalog-audit`.
3. Call `POST /api/sqx144/mt5-auto3/resolve-plan`.
4. If decision is `broker_missing` or `ambiguous_collision`, stop before writing a MT5 request file and show the catalog decision.
5. Otherwise call existing AUTO2 `POST /api/sqx144/mt5-auto2/request`.
6. Poll `POST /api/sqx144/mt5-auto3/bridge-validate` with `expectedRequestId` and selected symbol.

This fixes the operator-facing failure mode where a selected symbol such as `AUDCAD_darwinex` could show generic `validation_failed` while the latest bridge response was still `USDJPY_Darwinex`. AUTO4 makes the catalog status visible, preserves the crossed-response blocker `latest_response_symbol_mismatch`, and keeps stale bridge responses in `waiting_for_requested_response` until a matching MT5 response arrives or the poll finishes.

## Safety

- `readOnlyCatalogResolver=true`
- `importAllowed=false`
- `applyAllowed=false`
- `importExecutionAllowed=false`
- `directDbHistoryInsertAllowed=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `usesMigrationTool=false`
- `doesNotApplyToSqx=true`
- `doesNotApplyInstrumentConfig=true`

AUTO4 source references only local SQX Edge endpoints:

- `/api/sqx144/mt5-auto3/catalog-audit`
- `/api/sqx144/mt5-auto3/resolve-plan`
- `/api/sqx144/mt5-auto3/bridge-validate`
- `/api/sqx144/mt5-auto2/request`

## Install Result

AUTO4 overlay assets were installed after exact operator approval:

- Approval: `APRUEBO SQX144 MT5 AUTO4 DATAMANAGER TRIAGE INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks`
- Backup: `sqx144_mt5_auto2_button_20260609_080600`
- Install marker: `auto4_overlay_installed_verified_no_db_no_projects_no_databanks_no_tasks`
- `targetHasAuto4=true`
- Active JS SHA256: `9DB2D802252731284D122409C1C25C35B0934AD7DB81F53977631967D90DE194`
- Active CSS SHA256: `C09D5573B4CEC403EA522E14495F464338F8B8AD34D9A79B277E11EE9314CD06`

The install wrote only SQX web overlay files (`writesSqxHost=true`, `writesSqxOverlayHost=true`). It preserved `writesDataDb=false`, `writesUserProjects=false`, `mutatesDatabanks=false`, `runsSqxTasks=false`, `usesMigrationTool=false` and `doesNotApplyInstrumentConfig=true`.

## AUTO6 Installed Addendum

The repository overlay source and the active SQX host now include the AUTO6 stability display path after a separate install gate was approved.

Installed marker: `auto6_datamanager_stability_installed_verified_no_db_no_projects_no_databanks_no_tasks`

Install evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO6 DATAMANAGER STABILITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import`
- Backup: `sqx144_mt5_auto2_button_20260609_183452`
- Asset version: `sqx144-mt5-auto6-datamanager-stability-panel-v1`
- `targetHasAuto6=true`
- `processCount=0`

The installed overlay calls `/api/sqx144/mt5-auto6/evaluate` after AUTO3 `bridge-validate` and displays `Stability policy`, `Stability`, `Future gate`, `Coverage`, `blocked_by_policy` and policy reasons. It still does not apply metadata, import history, mutate projects/databanks or run SQX tasks.

## AUTO6 Selection Guard Installed Addendum

The AUTO6 visual smoke confirmed `DAX40_darwinex` -> `GDAXI_darwinex` can reach stability policy and correctly block as `blocked_broker_contract_review`. It also exposed a source bug where an `EURGBP_darwinex` edit modal could still show `WARRANTY` and a stale `DAX40` request.

Installed marker: `auto6_datamanager_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks`

Source marker: `sqx144-mt5-auto6-datamanager-selection-guard-v1`

Install evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO6 DATAMANAGER STABILITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import`
- Backup: `sqx144_mt5_auto2_button_20260609_191932`
- `sourceHasSelectionGuard=true`
- `targetHasSelectionGuard=true`
- `processCount=0`

The installed fix prefers visible `Edit symbol` modal controls over stale selected grid rows, rejects arbitrary uppercase UI words such as `WARRANTY`, clears `lastRequestId` before every new request, and carries one frozen `{symbol, requestId}` context through `bridge-validate` and AUTO6 `evaluate`.

## Verification

Required checks:

- `node tests/js/contracts/sqx144_mt5_auto4_datamanager_catalog_triage_contracts.mjs`
- `node tests/js/contracts/sqx144_mt5_auto2_data_manager_button_contracts.mjs`
- `python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto2_datamanager.py backend\sqx-edge-tool\test_sqx144_mt5_auto3_broker_catalog.py backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `git diff --check`
