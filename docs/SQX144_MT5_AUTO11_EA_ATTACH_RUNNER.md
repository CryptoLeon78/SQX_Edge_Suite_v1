# SQX144-MT5-AUTO11 - EA Attach/Profile Runner

Marker: `sqx144-mt5-auto11-ea-attach-runner-v1`

Source-ready status: `auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`

Profile writer status: `auto11_attach_profile_writer_implemented_no_apply_no_ui_fallback_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`

Applied writer status: `auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback`

UI fallback applied status: `auto11_ui_fallback_completed_bridge_ready`

AUTO11 automates the step that AUTO10 exposed as manual: preparing an MT5 profile/template/chart with `SQXInfoBridge` attached for a governed `host + mt5Profile + symbol + timeframe`, then handing control back to AUTO10-style heartbeat verification.

The implementation is profile-aware, not hardcoded to one broker install. Every apply is keyed by:

- `host`
- `mt5Profile`
- `symbol`
- `timeframe`

Current wrapper:

`tools/sqx144_mt5_auto11_ea_attach_runner.ps1 status|profile-catalog|preflight|plan|attach-plan|ui-fallback-plan|approval-template`

Local endpoints:

- `/api/sqx144/mt5-auto11/status`
- `/api/sqx144/mt5-auto11/profile-catalog`
- `/api/sqx144/mt5-auto11/preflight`
- `/api/sqx144/mt5-auto11/plan`
- `/api/sqx144/mt5-auto11/attach-plan`
- `/api/sqx144/mt5-auto11/ui-fallback-plan`

## Attach Gate

Writer apply gate:

`APRUEBO SQX144 MT5 AUTO11 EA ATTACH RUNNER APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool`

Without the exact gate:

- `genericMt5SqxProfileAware=true`
- `attachAllowedByGate=false`
- `writesMt5Profile=false`
- `writesMt5Template=false`
- `writesMt5StartupConfig=false`
- `runsMt5Ea=false`
- `launchesMt5=false`
- `writesDataDb=false`
- `historyImportAllowed=false`

With the exact attach gate, AUTO11 writes only governed MT5 profile assets:

- template file: `SQX_AUTO11_SQXInfoBridge.tpl`
- chart file: `chart01.chr`
- chart order file: `order.wnd`
- startup config file: `SQX_AUTO11_startup.ini`

Successful writer statuses:

- `auto11_attach_profile_writer_completed_ready_for_profile_launch`
- `auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback`

The public payload returns file names and hashes only; `privacy.localPathsReturned` remains false.

## Applied Result

The exact attach gate was applied for `sqx144_full + darwinex + USDJPY_Darwinex + M1`.

AUTO11 wrote:

- `profileName=SQX_AUTO11_BRIDGE_darwinex_USDJPY_Darwinex_M1`
- `SQX_AUTO11_SQXInfoBridge.tpl`
- `chart01.chr`
- `order.wnd`
- startup config `SQX_AUTO11_BRIDGE_darwinex_USDJPY_Darwinex_M1_SQX_AUTO11_startup.ini`

Hashes:

- `templateSha256=9402D18BFA300A313F6E04A921CB0D3189377E9070165AA88054A18ACB7CCEFE`
- `chartSha256=9402D18BFA300A313F6E04A921CB0D3189377E9070165AA88054A18ACB7CCEFE`
- `startupConfigSha256=928A615FE93AC103D060FD9E7DDD1EE5D4C3710A3183E692329E530DA4EC48EB`

AUTO10 verify after the writer apply wrote `requestId=sqx_auto10_USDJPY_Darwinex_20260610_180543` and returned `auto10_verify_bridge_timeout` / `mt5_bridge_ea_no_responde`. The already-running MT5 session did not load the newly written profile in-place.

This writer-only result required either the separate UI fallback gate or a future governed profile/config relaunch gate. The separate UI fallback gate was later supplied and is recorded below.

## UI Fallback Gate

Fallback UI automation is separate and remains unavailable unless the operator supplies this exact visible-control gate:

`APRUEBO SQX144 MT5 AUTO11 UI FALLBACK APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 visible_operator_control no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool`

Planning status:

`auto11_ui_fallback_plan_ready_separate_gate_required`

The UI fallback is only for the case where profile/template autoload cannot be proven. It is explicitly visible/operator-controlled and is not part of the profile writer gate.

## UI Fallback Applied Result

The exact UI fallback gate was applied for `sqx144_full + darwinex + USDJPY_Darwinex + M1`.

Result:

- `status=auto11_ui_fallback_completed_bridge_ready`
- `statusMarker=auto11_ui_fallback_apply_visible_operator_control_completed`
- `visibleOperatorControl=true`
- `profileHandoff.method=visible_terminal_profile_config_handoff`
- `profileHandoff.returnCode=0`
- `profileHandoff.targetProcessCountBefore=1`
- `profileHandoff.targetProcessCountAfter=1`
- `profileHandoff.newTargetProcessObserved=false`

The visible MT5 fallback attached `SQXInfoBridge` to the active chart `USDJPY,H1`, with Algo Trading enabled. The requested AUTO11 timeframe remains `M1` for bridge spread requests.

Heartbeat verification:

- AUTO11 request: `sqx_auto11_ui_USDJPY_Darwinex_20260610_183515`
- AUTO11 bridge health: `mt5_bridge_ready_latest_matches_request`
- response `mt5Symbol=USDJPY`
- response `status=ok`
- AUTO10 verify status: `auto10_verify_bridge_ready`
- AUTO10 verify request: `sqx_auto10_USDJPY_Darwinex_20260610_183446`

Boundaries:

- `runsMt5Ea=true` only for `SQXInfoBridge`
- `launchesMt5=false`
- `writesMt5Files=true`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `placesOrders=false`
- `usesMigrationTool=false`
- `historyImportAllowed=false`

## Post-Attach Bridge Observation

After the UI fallback made the bridge ready, the next safe operational block exercised the existing AUTO2/AUTO3/AUTO6 chain for `USDJPY_Darwinex` without opening any apply gate.

AUTO2 wrote only MT5 request `sqx_auto2_USDJPY_Darwinex_20260610_184934` and validated the response as `bridge_response_validated`:

- `spreadPolicy=p90`
- `DEFAULTSPREAD=5.0`
- `POINTVALUE=623.15779`
- `spreadSamples=2755271`
- `yearCount=10`

AUTO3 validated the same request as:

- `bridge_validate_ready`
- `catalogDecision=ready_existing`
- `decision=metadata_diff_only`
- target instrument `USDJPY_darwinex`
- drift `DEFAULTSPREAD 0.7 -> 5.0`
- drift `POINTVALUE 624.93 -> 623.15779`

AUTO6 then held the observation:

- status `stability_policy_not_satisfied`
- decision `metadata_stability_observe_no_apply`
- reason `repeat_observation_window_not_satisfied`
- `matchingObservationCount=2`
- `matchingObservationWindowHours=0.0`

This proves the bridge is operational for the governed MT5/SQX pair, but it does not authorize a metadata apply. The next operational step is repeated bridge observation across the AUTO6 stability window; any future write still requires `eligible_metadata_update` plus a separate exact gate.

Follow-up repeat and second-pair smoke:

- USDJPY repeat request `sqx_auto2_USDJPY_Darwinex_20260610_191729` validated through AUTO2/AUTO3 and returned `DEFAULTSPREAD=1.6`, `POINTVALUE=622.944284`, `spreadSamples=4234681`, `yearCount=14`.
- AUTO6 kept USDJPY at `stability_policy_not_satisfied` / `metadata_stability_observe_no_apply`, reason `repeat_observation_window_not_satisfied`. The repeat did not stabilize the earlier `DEFAULTSPREAD=5.0` candidate.
- `EURGBP_Darwinex` was then tested as a second governed pair after AUTO3 `ready_existing` for target `EURGBP_darwinex`.
- EURGBP request `sqx_auto2_EURGBP_Darwinex_20260610_191736` validated through AUTO2/AUTO3 and returned `DEFAULTSPREAD=0.7`, `POINTVALUE=133731.0`, `spreadSamples=902086`, `yearCount=3`.
- AUTO6 blocked EURGBP as `stability_broker_contract_review_required` / `blocked_broker_contract_review` because `POINTVALUE 129882.0 -> 133731.0` is `relativeDeltaPct=2.963459`, reason `pointvalue_delta_requires_broker_contract_review`.
- Both paths preserved `applyAllowed=false`.

## Automation Plan

Preferred path: `template_profile_autoload_then_auto10_heartbeat_verify`.

AUTO11 prepares a governed MT5 chart/profile/template where `SQXInfoBridge` is attached for the selected `symbol` and `timeframe`. The next step after writer apply is either:

- launch MT5 with the generated profile/config and verify a fresh heartbeat, or
- if the target MT5 is already running, verify the heartbeat from the loaded chart or request the separate UI fallback gate.

The profile/template locations follow MT5's documented advanced startup and data-folder structure: profiles under `MQL5\Profiles\Charts`, templates under `MQL5\Profiles\Templates`, with `/profile:<profile>` and `/config:<file>` reserved for launch integration.

## Routing Boundaries

- Darwinex and future MT5 broker profiles may use AUTO11 only after profile discovery and gate approval.
- `*_dukascopy` remains `AUTO7 mirror/no-MT5`.
- AUTO11 does not import history, does not touch SQX projects/databanks/tasks, does not write `data.db`, does not use Migration Tool and does not place orders.

## Verification

Required checks:

```powershell
python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto11_ea_attach_runner.py -q
node tests\js\contracts\sqx144_mt5_auto11_ea_attach_runner_contracts.mjs
tools\sqx144_mt5_auto11_ea_attach_runner.ps1 status
tools\sqx144_mt5_auto11_ea_attach_runner.ps1 attach-plan
tools\sqx144_mt5_auto11_ea_attach_runner.ps1 ui-fallback-plan
```
