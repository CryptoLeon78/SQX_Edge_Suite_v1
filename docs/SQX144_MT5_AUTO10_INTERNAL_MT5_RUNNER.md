# SQX144-MT5-AUTO10 - Internal MT5/EA Runner

Status: `auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`

Install applied status: `auto10_install_source_completed`

Launch correction status: `auto10_launch_wrong_terminal_aborted_route_corrected_no_relaunch`

Current launch status: `auto10_launch_correct_target_bridge_timeout_manual_ea_attach_required`

Marker: `sqx144-mt5-auto10-internal-mt5-runner-v1`

Host: `sqx144_full`

## Purpose

AUTO10 opens the governed design/source-ready phase for an internal MT5 runner. The goal is that a future Data Manager Darwinex flow can prepare the MT5 bridge without requiring the operator to manually open MT5 or attach `SQXInfoBridge`.

This phase does not install the bridge into MT5, does not compile it, does not launch MT5, does not run the EA and does not write a smoke request. It only adds source, API and wrapper contracts that are closed behind exact approvals.

## Scope

AUTO10 adds:

- core module `backend/sqx-edge-tool/core/sqx144_mt5_auto10_internal_runner.py`
- wrapper `tools/sqx144_mt5_auto10_internal_runner.ps1 status|discover|preflight|plan|install-source|launch|stop|verify|approval-template`
- local endpoints:
  - `/api/sqx144/mt5-auto10/status`
  - `/api/sqx144/mt5-auto10/preflight`
  - `/api/sqx144/mt5-auto10/plan`
  - `/api/sqx144/mt5-auto10/launch`
  - `/api/sqx144/mt5-auto10/stop`
  - `/api/sqx144/mt5-auto10/verify`
- tests:
  - `backend/sqx-edge-tool/test_sqx144_mt5_auto10_internal_runner.py`
  - `tests/js/contracts/sqx144_mt5_auto10_internal_runner_contracts.mjs`

Discovery and preflight report public-safe booleans, file names and hashes only. They do not return local terminal paths, account data, tokens, secrets or license material.

## Gates

Install-source gate:

`APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER INSTALL host=sqx144_full mt5=darwinex no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool`

Only after that exact gate may AUTO10 copy/update `SQXInfoBridge.mq5` when the source hash differs and compile it with `MetaEditor64.exe`.

Install evidence after exact approval on 2026-06-10:

- Approval: `APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER INSTALL host=sqx144_full mt5=darwinex no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool`
- Backup id: `auto10_install_20260610_184357`
- Result status: `auto10_install_source_completed`
- `copiedBridgeSource=false` because installed source already matched repo source.
- `compiledBridgeSource=true`
- `compile.returnCode=0`
- Installed `SQXInfoBridge.mq5` SHA256: `DB8FBB56697710CE333CD94F5EC87D37705DA9E2E0C3AEA3A81721C2C898B897`
- Installed `SQXInfoBridge.ex5` SHA256: `43E4BC74069C44B88C8F92D1B7D72809B0A387F1C324487C7E81FBB5AA54F693`
- Post-install preflight: `auto10_preflight_ready_no_launch`, blockers `[]`, warnings `[]`, `sourceHashMatchesInstalled=true`, `processCount=0`.
- Post-install process check: `terminal64ProcessCount=0`, `metaeditor64ProcessCount=0`.
- No launch gate was supplied at install closeout, so `launchesMt5=false`, `runsMt5Ea=false`, `writesMt5Files=false`, no smoke request and no heartbeat verify were executed during the install step.

Launch gate:

`APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER LAUNCH host=sqx144_full mt5=darwinex hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool`

Only after that exact gate may AUTO10 reuse an already open MT5 process or launch `terminal64.exe` hidden/minimized, write a controlled smoke request, wait for a fresh bridge heartbeat and stop only a process it recorded as AUTO10-managed.

Launch abort and route correction after exact approval on 2026-06-10:

- Launch approval supplied: `APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER LAUNCH host=sqx144_full mt5=darwinex hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool`
- First launch result: `auto10_launch_started_managed_mt5_process`, `launchesMt5=true`, `windowStyle=minimized`, `managedPidRecorded=true`.
- Smoke verify result before abort: `auto10_verify_bridge_timeout`, `requestWritten=true`, request id `sqx_auto10_USDJPY_Darwinex_20260610_165721`, bridge health `mt5_bridge_ea_no_responde`.
- Operator corrected the route immediately: the launched MT5 was the wrong Darwinex terminal.
- Abort result: wrong terminal stopped, stale AUTO10 managed PID record removed, final `terminal64ProcessCount=0`, `metaeditor64ProcessCount=0`, `managedPidRecorded=false`.
- Route correction: AUTO10 default terminal now targets the standard Darwinex MT5 install, not the BEPB install; process detection is `targetTerminalProcessRunning` / `targetProcessCount` aware and launch records `managedPidIsTargetTerminal`.
- No relaunch was executed after the route correction. Fresh heartbeat remains unconfirmed.
- Boundaries preserved: no `data.db`, no history import, no projects/databanks/tasks, no SQX task, no Migration Tool and no order placement.

Corrected relaunch status after operator asked to advance:

- Relaunch result: `auto10_launch_started_managed_mt5_process`, `managedPidIsTargetTerminal=true`, `targetTerminalProcessRunning=true`, `targetProcessCount=1`, `otherTerminalProcessCount=0`.
- Correct terminal process observed: standard Darwinex MT5 `terminal64.exe`; no MetaEditor process.
- Smoke verify result: `auto10_verify_bridge_timeout`, request id `sqx_auto10_USDJPY_Darwinex_20260610_171523`, bridge health `mt5_bridge_ea_no_responde`.
- File evidence: fresh `SQXInfoBridge.request.ini` exists, but `SQXInfoBridge.latest.json` remains stale from the previous day.
- Log evidence: `SQXInfoBridge` wrote responses on 2026-06-09, but there is no 2026-06-10 MQL5 Experts log entry after the corrected relaunch.
- Operational next step: manual `SQXInfoBridge` EA attach/enable in the correct Darwinex MT5 session, then rerun AUTO10 verify.
- Boundaries preserved: no `data.db`, no history import, no projects/databanks/tasks, no SQX task, no Migration Tool and no order placement.

## Data Manager Routing

- Darwinex rows may call AUTO10 health/preflight before AUTO2 writes a bridge request in a future overlay phase.
- Future Axi rows remain blocked until broker discovery supplies a governed profile.
- `*_dukascopy` rows must not use AUTO10 or MT5; they keep the AUTO7 mirror path.
- AUTO9C/AUTO9D exactly-one-checkbox authority remains mandatory before any bridge action.

## Boundaries

- `sourceReadyNoLaunch=true`
- `autoStartAllowed=false`
- `installSourceAllowedByGate=false`
- `launchesMt5AllowedByGate=false`
- `runsMt5EaAllowedByGate=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `placesOrders=false`
- `usesMigrationTool=false`
- `directDbHistoryInsertAllowed=false`
- `historyImportAllowed=false`
- `usesDataSourceHistoryImport=false`
- no SQX `data.db` write
- no history import
- no projects, databanks, SQX tasks or `user/projects`
- no order placement
- no Migration Tool
- no license, activation, engine or binary handling
- no SQX144 144.2953 promotion

## Verification

Required source-ready checks:

```powershell
python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto10_internal_runner.py -q
node tests\js\contracts\sqx144_mt5_auto10_internal_runner_contracts.mjs
tools\sqx144_mt5_auto10_internal_runner.ps1 status
tools\sqx144_mt5_auto10_internal_runner.ps1 plan
python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q
git diff --check
```

Do not run `install-source -Apply`, `launch -Apply`, `verify -Apply` or `stop -Apply` until the corresponding exact gate is supplied.
