# SQX144-MT5-AUTO7 - Dukascopy Metadata Mirror

Marker: `sqx144-mt5-auto7-dukascopy-metadata-mirror-v1`
Status marker: `auto7_dukascopy_metadata_mirror_source_ready_no_apply_no_install`
Data Manager install status: `auto7_datamanager_dukascopy_mirror_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5`
Data Manager data-symbol guard status: `auto7_datamanager_data_symbol_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5`
Host: `sqx144_full`

## Purpose

AUTO7 records the operator rule that every SQX `*_dukascopy` instrument must use the same instrument metadata parameters as its `*_darwinex` sibling.

This is not an MT5 metadata read. For Dukascopy rows the bridge should not call MT5, should not write `SQXInfoBridge.request.ini`, and should not validate `SQXInfoBridge.latest.json`. The source of truth is the existing SQX Darwinex sibling row in `INSTRUMENTS`.

Examples:

- `EURGBP_dukascopy` mirrors from `EURGBP_darwinex`.
- `AUDCAD_dukascopy` mirrors from `AUDCAD_darwinex`.
- `USDJPY_dukascopy` mirrors from `USDJPY_darwinex`.

## Current Scope

AUTO7 keeps its core gate in source/no-apply mode and has the Data Manager overlay installed on the governed `sqx144_full` host. The install writes only the Data Manager web overlay assets and `SQMANAGER` includes; it has not applied any DB mutation.

Source/core:

- `backend/sqx-edge-tool/core/sqx144_mt5_auto7_dukascopy_metadata_mirror.py`
- `tools/sqx144_mt5_auto7_dukascopy_metadata_mirror.ps1 status|audit|plan|backup|apply|verify|rollback`
- local endpoints `/api/sqx144/mt5-auto7/status`, `/api/sqx144/mt5-auto7/audit`, `/api/sqx144/mt5-auto7/plan`, `/api/sqx144/mt5-auto7/backup`, `/api/sqx144/mt5-auto7/apply`, `/api/sqx144/mt5-auto7/verify`, `/api/sqx144/mt5-auto7/rollback`

Data Manager behavior:

- selected symbols ending `_dukascopy` are routed to AUTO7 `/plan`;
- `Edit symbol` dialogs prefer visible `Data symbol name` values such as `DAX40_dukascopy` over linked-instrument dropdown values such as `GDAXI_darwinex`;
- the overlay sends `linkedInstrument` separately so AUTO7 can detect SQX Data rows already using a Darwinex instrument;
- if `DATA.SYMBOL=<asset>_dukascopy` already points to a valid Darwinex instrument row, AUTO7 returns `plan_ready_noop_data_symbol_uses_darwinex_instrument` and does not require a DB apply;
- AUTO2 does not write a MT5 request for `_dukascopy`;
- AUTO3 `bridge-validate` and AUTO6 `evaluate` are not used for `_dukascopy` mirror checks;
- the panel displays the Darwinex source, Dukascopy target, mirror policy and pending field differences.

Overlay install was executed after exact approval:

`APRUEBO SQX144 MT5 AUTO7 DATAMANAGER DUKASCOPY MIRROR INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5`

Install evidence:

- status: `auto7_datamanager_dukascopy_mirror_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5`
- current data-symbol guard status: `auto7_datamanager_data_symbol_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5`
- backup: `sqx144_mt5_auto2_button_20260609_203359`
- latest overlay backup: `sqx144_mt5_auto2_button_20260609_210550`
- asset version: `sqx144-mt5-auto7-datamanager-data-symbol-selection-guard-v1`
- `targetHasAuto7=true`
- `targetHasAuto7DataSymbolGuard=true`
- `targetHasAuto6=true`
- `targetHasSelectionGuard=true`
- target JS SHA256: `4373C90C97F3F1C3645497D50CD6DDC4631851644FADA2D3C06CB4CC6026F638`
- `includeCount=2`
- `processCount=0`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `launchesMt5=false`
- `usesMigrationTool=false`

## Mirror Fields

AUTO7 compares and can later copy only approved `INSTRUMENTS` metadata columns:

- `DEFAULTSPREAD`
- `POINTVALUE`
- `TICKSIZE`
- `TICKSTEP`
- `DEFAULTSLIPPAGE`
- `ORDERSIZEMULTIPLIER`
- `ORDERSIZESTEP`
- `COMMISSIONS`
- `SWAP`

It preserves the target row identity and SQX authorities:

- `BROKER_ID` remains the target Dukascopy broker/profile id.
- `DATA`, `SOURCE`, `ROWS`, `DATEFROM`, `DATETO` and history coverage are not touched.
- No projects, databanks, SQX tasks, MT5 launch/EA, history import or Migration Tool are used.

## Apply Gate

The legacy direct-DB `apply` path is offline-only and blocked unless all are true:

- SQX process count is zero.
- A known AUTO7 backup exists and its hashes verify.
- The exact approval phrase matches the plan id, backup id, source, target and fields.
- `-Apply` is supplied.
- One SQLite transaction updates exactly one `INSTRUMENTS` target row.

Future apply approval template:

`APRUEBO SQX144 MT5 AUTO7 DUKASCOPY MIRROR APPLY host=sqx144_full source=<asset>_darwinex target=<asset>_dukascopy plan=<planId> backup=<backupId> fields=<fields> no_source_broker_data_history no_projects_no_databanks_no_tasks no_mt5 no_migration_tool`

This legacy direct-DB path is not the Data Manager button UX. `SQX144-MT5-AUTO8` separately introduces `Aplicar cambios` through the native Data Manager Save route, so that UI save can work while SQX is open without calling AUTO7 `/apply`.

## Current Smoke Findings

Operator visual native-save apply after AUTO8/AUTO9D:

- `NZDJPY_dukascopy` was selected with exactly one checked Data Manager row, routed through AUTO7 mirror `dukascopy_copies_darwinex_sibling_metadata`, and compared source `NZDJPY_darwinex` to target `NZDJPY_dukascopy`.
- The ready plan showed `DEFAULTSPREAD=2.6`, `POINTVALUE=653.44102`, `TICKSIZE=0.01` and `TICKSTEP=0.001`.
- Pressing `Aplicar cambios` completed through AUTO8 native Data Manager Save with `aplicado_en_data_manager`, plan `auto7_duka_mirror_c7f99cd22c7e1ec0`, fields `DEFAULTSPREAD,POINTVALUE,SWAP`, and SQX toast `Success` / `Instrument modified`.
- Repeating MT5 Bridge on the same single checked `NZDJPY_dukascopy` row after apply showed `Sin cambios en Data Manager.` with `Aplicar cambios` disabled.
- Related native-save closeout marker: `sqx144-mt5-auto8-native-save-visual-apply-closeout-v1`.
- This is visual confirmation of the Data Manager native-save path, not the legacy offline direct-DB AUTO7 `apply` path.

Operator visual smoke after AUTO6:

- `EURGBP_Darwinex` correctly uses MT5 bridge observation and AUTO6 stability, but may block as `blocked_broker_contract_review` when `POINTVALUE` differs materially from SQX.
- `NASDAQ_Darwinex` currently needs alias/catalog work because SQX Data Manager has `NASDAQ_darwinex` data linked to `NDX_darwinex`; this is separate from the Dukascopy mirror rule.
- `EURGBP_dukascopy` must not read MT5; it should use AUTO7 mirror plan from `EURGBP_darwinex`.
- `DAX40_dukascopy` and similar Data tab rows can be valid no-op mirror cases when the SQX data symbol is already linked to `GDAXI_darwinex`; the panel must show the data symbol separately from the linked instrument.

## Verification

Required checks:

- `python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto7_dukascopy_metadata_mirror.py backend\sqx-edge-tool\test_sqx144_mt5_auto2_datamanager.py backend\sqx-edge-tool\test_sqx144_mt5_auto3_broker_catalog.py backend\sqx-edge-tool\test_sqx144_mt5_auto6_metadata_stability.py backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `node --check integrations\sqx144\datamanager_mt5_auto2_overlay\sqx-edge-mt5-auto2.js`
- `node tests\js\contracts\sqx144_mt5_auto7_datamanager_routing_behavior.mjs`
- `node tests\js\contracts\sqx144_mt5_auto7_dukascopy_metadata_mirror_contracts.mjs`
- `node tests\js\contracts\sqx144_mt5_auto6_selection_guard_behavior.mjs`
- `node tests\js\contracts\sqx144_mt5_auto6_metadata_stability_contracts.mjs`
- `node tests\js\contracts\sqx144_mt5_auto3_broker_catalog_contracts.mjs`
- `git diff --check`
