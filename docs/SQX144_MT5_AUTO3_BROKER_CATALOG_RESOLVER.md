# SQX144-MT5-AUTO3 - Broker Catalog Resolver

Marker: `sqx144-mt5-auto3-broker-catalog-resolver-v1`
Status: `opened_broker_catalog_resolver_readonly_design_no_import_no_apply_no_projects_no_databanks_no_tasks`
Host: `sqx144_full`

## Purpose

AUTO3 connects the AUTO1/AUTO2 MT5 bridge path with the real SQX144 Full Data Manager catalog. It is broker-aware for Darwinex now and Axi-ready for later discovery, but it is still a resolver/planner gate only.

The phase reads `BROKER`, `INSTRUMENTS` and `DATA` through `sqlite_uri_mode_ro_query_only`, validates bridge responses when requested, and emits catalog/import plans. It does not execute creation, history import, metadata apply, project import, databank mutation or SQX task execution.

## Scope

- Core: `backend/sqx-edge-tool/core/sqx144_mt5_auto3_broker_catalog.py`
- Wrapper: `tools/sqx144_mt5_auto3_broker_catalog.ps1`
- Broker catalog config: `backend/sqx-edge-tool/config/mt5_broker_catalog/darwinex.json`
- Planned broker config: `backend/sqx-edge-tool/config/mt5_broker_catalog/axi.planned.json`
- Static contract: `tests/js/contracts/sqx144_mt5_auto3_broker_catalog_contracts.mjs`

## Actions

The wrapper and API expose:

- `status`
- `catalog-audit`
- `bridge-validate`
- `resolve-plan`
- `import-plan`
- `approval-template`

Local API endpoints:

- `GET /api/sqx144/mt5-auto3/status`
- `POST /api/sqx144/mt5-auto3/catalog-audit`
- `POST /api/sqx144/mt5-auto3/bridge-validate`
- `POST /api/sqx144/mt5-auto3/resolve-plan`
- `POST /api/sqx144/mt5-auto3/import-plan`

## Broker Profiles

Darwinex is active:

- `brokerKey=darwinex`
- expected SQX `BROKER.ID=4`
- expected SQX `DATA.SOURCE=4`
- postfix `_darwinex`
- bridge/Data Manager spread policy `p90`
- preferred future history route `native_datamanager_mt5_import`
- native endpoint name recorded as `dataSourceMt5Api/importData`
- fallback route `bridge_csv_file_mass_import`

Axi is planned:

- `brokerKey=axi`
- `expectedBrokerId=null`
- `expectedSourceId=null`
- `requiresDiscovery=true`
- no broker, source, postfix, timezone or MT5 symbol template is invented before read-only discovery.

## Decisions

`resolve-plan` returns one of:

- `ready_existing`
- `metadata_diff_only`
- `instrument_missing`
- `history_missing`
- `broker_missing`
- `ambiguous_collision`

`AUDCAD_darwinex` on Darwinex is expected to resolve as `ready_existing` when broker, instrument and positive-history `DATA` rows are present. `USDJPY_darwinex` can validate bridge `p90` and report `metadata_diff_only` if the bridge proposal differs from current catalog metadata.

## Import Gate Design

History import is designed but not runnable in AUTO3.

Preferred future route:

- `native_datamanager_mt5_import`
- `DataSourceMt5Api/importData`
- SQX Data Manager remains owner of the internal history format.

Fallback route:

- `bridge_csv_file_mass_import`
- bridge exports CSV and Data Manager File/Mass import consumes it only if the native MT5 route is not observable or controllable.

Forbidden in AUTO3:

- direct SQX history row insertion
- broker creation
- instrument creation
- metadata apply
- project/databank mutation
- SQX task start/stop
- Migration Tool

Any real create/import/apply action must be a later phase with backup, verify/rollback and exact approval containing `host=sqx144_full`, broker, instrument, plan id and `no_projects_no_databanks_no_tasks`.

## Safety Flags

- `readOnlyCatalogResolver=true`
- `importAllowed=false`
- `applyAllowed=false`
- `importExecutionAllowed=false`
- `directDbHistoryInsertAllowed=false`
- `writesSqxHost=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `launchesMt5=false`
- `runsMt5Ea=false`
- `usesMigrationTool=false`
- `doesNotApplyToSqx=true`
- `doesNotApplyInstrumentConfig=true`

## AUTO1/AUTO2 Link

AUTO3 builds on:

- `sqx144-mt5-auto1-data-manager-bridge-v1`
- `real_mt5_response_validated_usdjpy_p90`
- `sqx144-mt5-auto2-data-manager-button-bridge-v1`
- `auto2_overlay_installed_verified_no_db_no_projects_no_databanks`

`bridge-validate` preserves AUTO2 stale-response behavior: an old request id returns `waiting_for_requested_response` with `latest_response_request_id_mismatch`; symbol mismatch is evaluated only after the requested response id matches.

## Read-only Smoke

Initial wrapper checks on the governed host returned:

- `status`: `ok=true`, `hostProfile=sqx144_full`, `readMode=sqlite_uri_mode_ro_query_only`, `importExecutionAllowed=false`
- `catalog-audit darwinex AUDCAD_darwinex`: `decision=ready_existing`, broker/instrument/history found
- `resolve-plan axi EURUSD`: `decision=broker_missing`
- `import-plan darwinex GBPUSD_darwinex`: `decision=history_missing`, `importBlocked=true`, `preferredNativeEndpoint=dataSourceMt5Api/importData`
- `bridge-validate darwinex AUDCAD_darwinex`: catalog is `ready_existing`, but current latest bridge response is still `USDJPY_Darwinex`, so validation blocks with `latest_response_symbol_mismatch` until a fresh AUDCAD response is produced.

## Approval Templates

AUTO3 emits future-gate templates only. Example:

`APRUEBO SQX144 MT5 AUTO3 IMPORT HISTORY host=sqx144_full broker=darwinex instrument=<instrument> plan=<planId> native_datamanager_only no_projects_no_databanks_no_tasks`

This template is not executable inside AUTO3.
