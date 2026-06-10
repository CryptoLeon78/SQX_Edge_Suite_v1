# SQX144 MT5 Instrument Parity Gate

Marker: `sqx144-mt5-instrument-parity-gate-v1`

Status: `operator_data_manager_visual_confirmed_usdjpy_values`

Implementation-ready marker: `implemented_apply_gated_db_offline_usdjpy_pilot_ready`

Applied marker: `applied_verified_usdjpy_pilot_after_exact_approval`

Brain/source decision marker: `mt5-instrument-metadata-import-plan-decisions-v1`

## Scope

This gate implements the first SQX144-only offline importer for MT5 `SQXInfoScript` `InstrumentInfo_*.xml` exports. The pilot target is the existing `USDJPY_Darwinex` export, normalized to the SQX144 Full instrument `USDJPY_darwinex`.

The gate is intentionally local and conservative:

- V1 consumes existing XML exports only.
- V1 does not launch MT5.
- V1 does not run the EA.
- V1 does not add a Data Manager button.
- V1 does not mutate SQX projects or databanks.
- V1 does not use Migration Tool; Migration Tool is not used.
- V1 does not promote or touch SQX144 144.2953.

## Allowed Fields

Only `INSTRUMENTS` metadata fields below may be planned/applied:

- `POINTVALUE`
- `TICKSIZE`
- `TICKSTEP`
- `DEFAULTSPREAD`
- `DEFAULTSLIPPAGE`
- `SWAP`
- `ORDERSIZEMULTIPLIER`
- `ORDERSIZESTEP`
- `COMMISSIONS`, only when MT5 provides explicit non-empty commission XML

For the pilot, empty MT5 commissions do not overwrite SQX commission.

## Preserved Authority

The SQX host remains the authority for broker/source/history coverage. The gate must not update `SOURCE`, `BROKER_ID`, `DATA`, `ROWS`, `DATEFROM`, `DATETO`, user projects, databanks, engine files, license files or SQX144 144.2953 config.

The XML values `rows=0`, `dateFrom=0` and `dateTo=0` are treated as metadata from the EA, not as proof of market-history coverage.

## Actions

`tools/sqx144_mt5_instrument_parity_gate.ps1` exposes:

- `status`
- `audit`
- `plan`
- `backup`
- `apply`
- `verify`
- `rollback`

The core module is `backend/sqx-edge-tool/core/sqx144_mt5_instrument_parity.py`.

`audit`, `plan` and `verify` read SQX `data.db` through `sqlite_uri_mode_ro_query_only`.

`backup` requires zero SQX processes, copies `data.db`, `data.db-wal`, `data.db-shm` if present and the local SQX Edge config into an ignored phase backup, then records SHA256 hashes in a manifest.

`apply` is offline-only and blocked unless all of these are true:

- SQX process count is zero.
- A known backup manifest exists and hashes verify.
- The `-Apply` switch is present.
- The exact approval phrase names `host=sqx144_full`, plan id, backup id, XML hash and target instrument.
- The plan has no host/profile blockers.

`rollback` restores only from a known phase backup after hash verification and SQX-closed checks.

## Public Contract

- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `launchesMt5=false`
- `runsMt5Ea=false`
- `usesMigrationTool=false`
- `localPathsReturned=false`

Next phase, after this offline gate proves safe, may evaluate a Data Manager/SQX button. That is deliberately out of V1 scope.

## Pilot Apply Evidence

The USDJPY pilot was applied while SQX was closed after exact operator approval:

- Backup id: `sqx144_mt5_instr_20260608_163934`
- Plan id: `mt5meta_d24e57d537569509`
- XML hash: `42af1ba0d24211c7a465ace91a0dde429848d3145d3bb148b91ca2d9fba78d23`
- Target instrument: `USDJPY_darwinex`
- Applied columns: `DEFAULTSPREAD`, `POINTVALUE`, `SWAP`
- Applied status: `apply_completed_offline_instruments_only`
- Verify status: `verify_passed_all_approved_fields_match`
- Applied verified status: `applied_verified_usdjpy_pilot_after_exact_approval`
- Operator visual confirmation: `operator_data_manager_visual_confirmed_usdjpy_values`

Post-apply verification returned `quickCheck=ok`, no pending approved-field changes, `processCount=0`, `INSTRUMENTS=989`, `DATA=54` and `BROKER=12`.

The operator then opened SQX144 Full and confirmed in Data Manager that `USDJPY_darwinex` reflects the expected values: `POINTVALUE=624.93`, `DEFAULTSPREAD=0.7`, pip/tick size `0.01`, pip/tick step `0.001`, order size step `0.01`, preserved size-based commission `5`, swap long `5.37`, swap short `-11.5`, triple swap `WEDNESDAY` and rollout hour visible as `23:00`.

Because SQX is now open, no further `backup`, `apply` or `rollback` action should be run until SQX is closed again.
