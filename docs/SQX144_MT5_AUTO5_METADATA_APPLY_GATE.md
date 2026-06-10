# SQX144-MT5-AUTO5 - Bridge Metadata Apply Gate

Marker: `sqx144-mt5-auto5-metadata-apply-gate-v1`
Base gate status marker retained for source/contract identity: `auto5_metadata_apply_gate_ready_bridge_json_no_apply`
Applied status: `applied_verified_audcad_after_exact_approval`
Operator visual status: `operator_data_manager_visual_confirmed_audcad_values`
Host: `sqx144_full`

## Purpose

AUTO5 prepares the first offline metadata apply from a fresh `SQXInfoBridge.latest.json` response validated through AUTO3.

The pilot target is `AUDCAD_darwinex` from bridge request `sqx_auto2_AUDCAD_Darwinex_20260609_064421`. AUTO3 validated that response as `bridge_validate_ready`; the catalog remained `ready_existing`; the resulting decision before apply was `metadata_diff_only`.

## Current Plan

Approved candidate fields:

- `DEFAULTSPREAD`: `1.0 -> 1.3`
- `POINTVALUE`: `72157.360772 -> 71753.512334`

No-op fields:

- `TICKSIZE`: `0.0001`
- `TICKSTEP`: `0.00001`

Ignored authorities:

- `SOURCE`
- `BROKER_ID`
- `DATA`
- `ROWS`
- `DATEFROM`
- `DATETO`
- `COMMISSIONS`
- `SWAP`
- `DEFAULTSLIPPAGE`

The applied bridge response hash was `efec3ee2fb53d00e1644a6b96a7b9ea2d0c30022112e743f39df1f10ec5d2b17`, spread policy was `p90`, and spread samples were `123050`.

Plan id: `auto5_meta_366093d1a4b782c3`
Prepared backup: `sqx144_mt5_auto5_meta_20260609_074111`
Backup quick check: `ok`
Table counts: `INSTRUMENTS=989`, `DATA=54`, `BROKER=12`

## Apply Result

AUTO5 was applied after exact operator approval:

`APRUEBO SQX144 MT5 AUTO5 METADATA APPLY host=sqx144_full broker=darwinex instrument=AUDCAD_darwinex plan=auto5_meta_366093d1a4b782c3 backup=sqx144_mt5_auto5_meta_20260609_074111 request=sqx_auto2_AUDCAD_Darwinex_20260609_064421 response=efec3ee2fb53d00e1644a6b96a7b9ea2d0c30022112e743f39df1f10ec5d2b17 spreadPolicy=p90 fields=DEFAULTSPREAD,POINTVALUE no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool`

Result: `apply_completed_offline_instruments_only`

Applied columns:

- `DEFAULTSPREAD`: `1.0 -> 1.3`
- `POINTVALUE`: `72157.360772 -> 71753.512334`

Verification:

- `verify_passed_all_approved_fields_match`
- `quickCheck=ok`
- `pendingChanges={}`
- AUTO3 `bridge-validate` returns `decision=ready_existing`
- AUTO3 `metadataDiff={}`

## Operator Visual Confirmation

The operator visually confirmed in SQX Data Manager that `AUDCAD_darwinex` shows:

- `DEFAULTSPREAD=1.3`
- `POINTVALUE=71753.512334`
- `TICKSIZE=0.0001`
- `TICKSTEP=0.00001`

Visual closeout marker: `operator_data_manager_visual_confirmed_audcad_values`

After that visual check, SQX was closed again by the operator.

## Subsequent Bridge Drift

After the visual confirmation, the Data Manager MT5 Bridge panel produced a newer MT5 response:

- Request: `sqx_auto2_AUDCAD_Darwinex_20260609_144542`
- Response hash: `3e25c7f7c1a8b5ecc829a2ab77b5eec57d34554402e7f0351aaef5408cb8d865`
- Spread policy: `p90`
- Samples: `531264`
- Proposed `DEFAULTSPREAD=1.2`
- Proposed `POINTVALUE=71659.930633`

Read-only AUTO3/AUTO5 checks classify this as a new `metadata_diff_only` / `verify_pending_diff_or_blocked` state relative to the applied SQX values:

- `DEFAULTSPREAD`: `1.3 -> 1.2`
- `POINTVALUE`: `71753.512334 -> 71659.930633`

This newer bridge response is not applied in AUTO5. It is recorded as `post_visual_bridge_drift_pending_policy`; any future mutation requires a separate backup, stability decision, exact approval and `no_source_broker_data_history`.

## Gate

Wrapper:

`tools/sqx144_mt5_auto5_metadata_apply_gate.ps1 status|audit|plan|backup|apply|verify|rollback`

Core:

`backend/sqx-edge-tool/core/sqx144_mt5_auto5_metadata_apply.py`

AUTO5 consumes AUTO3 bridge validation and SQX `data.db` read-only with `sqlite_uri_mode_ro_query_only` for `status`, `audit`, `plan` and `verify`.

`backup` requires zero SQX processes and copies `data.db`, `data.db-wal`, `data.db-shm`, SQX Edge config and the bridge response if present into an ignored AUTO5 backup with SHA256 manifest.

`apply` is offline-only and requires all of:

- SQX process count `0`
- known AUTO5 backup
- exact approval phrase
- one SQLite transaction
- update only `INSTRUMENTS`
- target `INSTRUMENT='AUDCAD_darwinex'`
- broker invariant `BROKER_ID=4`
- exactly one row changed

Expected approval phrase shape:

`APRUEBO SQX144 MT5 AUTO5 METADATA APPLY host=sqx144_full broker=darwinex instrument=AUDCAD_darwinex plan=auto5_meta_366093d1a4b782c3 backup=sqx144_mt5_auto5_meta_20260609_074111 request=sqx_auto2_AUDCAD_Darwinex_20260609_064421 response=efec3ee2fb53d00e1644a6b96a7b9ea2d0c30022112e743f39df1f10ec5d2b17 spreadPolicy=p90 fields=DEFAULTSPREAD,POINTVALUE no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool`

## Safety

- `writesDataDb=false` for `status`, `audit`, `plan`, `backup`, `verify` and `rollback`
- `writesDataDb=true` only for gated `apply -Apply`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `launchesMt5=false`
- `runsMt5Ea=false`
- `usesMigrationTool=false`
- `importExecutionAllowed=false`
- `directDbHistoryInsertAllowed=false`

AUTO5 does not create instruments, create brokers, import history, use Data Manager import, use CSV import, press Add missing symbols, load unresolved resources, start/stop projects, or touch SQX144 144.2953.

## Verification

Required before any apply approval:

- `tools/sqx144_mt5_auto5_metadata_apply_gate.ps1 plan -Broker darwinex -Symbol AUDCAD_darwinex`
- `tools/sqx144_mt5_auto5_metadata_apply_gate.ps1 backup`
- `python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto5_metadata_apply.py -q`
- `node tests/js/contracts/sqx144_mt5_auto5_metadata_apply_contracts.mjs`
- `python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- `git diff --check`
