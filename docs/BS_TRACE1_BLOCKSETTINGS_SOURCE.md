# BS-TRACE1 BlockSettings Source Contract

## Source Of Truth

The official real SQX BlockSettings are versioned under:

`backend/sqx-edge-tool/resources/blocksettings/`

`backend/sqx-edge-tool/tools/build_blocksettings_manifest.py` parses each `.sqb` as a ZIP, reads `config.xml`, hashes the original file and writes:

`backend/sqx-edge-tool/config/blocksettings_manifest.json`

## Resolution Rules

- Capa 1 resolves from methodology family plus timeframe.
- `_v6` is the default Capa 1 source where the real file exists.
- `Volatilidad`, `Volumen` and `SoporteResistencia` use `*_intraday_v6` for `M5/M15/M30/H1`.
- `H4/D1` use the general `_v6` source. `Volatilidad` is now closed with `BS_Volatilidad_v6.sqb` as the general source and `BS_Volatilidad_v6_intraday_v6.sqb` for `M5/M15/M30/H1`.
- Capa 2 is selected manually in Project Generator, with automatic recommendation by timeframe:
  - `M5/M15/M30/H1/H4`: `BS_Filtros_v6`
  - `D1`: `BS_Filtros_v6_D1`
  - fallback: `BS_Filtros_v6`
- `BS_Filtros_v7_M5/M15/M30/H1/H4` exists as preserved compatibility/explicit-selection material only. It is not the implicit Capa 2 default.

## BS-AI1 Candidate Rule

`bs-ai1-blocksettings-generator-contract-v1` adds local AI-assisted candidates without changing the official source of truth:

- Official v6/v7 `.sqb` resources in `backend/sqx-edge-tool/resources/blocksettings/` are preserved.
- AI candidates are written only under `.local/blocksettings_ai/candidates/`.
- AI candidate names must use `BSAI_<Family>_L<layer>_<TF|ALL>_from_<BaseCanonicalId>_rNNN.sqb`.
- AI candidates keep `sourceScope=local_candidate` and `promotionState=local_candidate`.
- AI candidates are injected into generated `.cfx` only through the internal Project Generator override for the matching layer.
- AI candidates are not added to `backend/sqx-edge-tool/config/blocksettings_manifest.json`.
- A candidate that reuses an official `canonicalId` or official filename is invalid.
- If a user requests Capa2 filters without an explicit base, resolution remains `BS_Filtros_v6` or `BS_Filtros_v6_D1`.
- `BS_Filtros_v7_*` may be used only with `explicitBaseCanonicalId`.

## BS-AI7 Panel Rule

`bs-ai7-panel-hardening-v1` adds a UI-side guard on top of the backend version policy:

- The SQX144 `BS-AI` panel clears candidate/project state whenever prompt, asset, timeframe, direction or explicit base changes.
- `Generar .cfx` stays disabled unless the active candidate matches the current form signature.
- The panel must show `Candidato activo`, `Base usada` and `Politica` before offering Capa1/Capa2 links.
- H1 v7 must remain labelled as explicit policy, and D1 blank-base flow must remain labelled as `D1 default v6_D1`.
- UI policy labels must be derived from the selected/resolved base (`_v7` versus `BS_Filtros_v6_D1`), not from loose substrings such as `explicit` inside default/no-explicit policy names.
- This UI guard does not change the official manifest, promote BSAI candidates, import `.cfx` into SQX, write `data.db`, write `user/projects` or mutate databanks.

## BS-AI8 First Import Gate

`bs-ai8-first-import-gate-v1` adds a pre-import approval gate without importing anything into SQX:

- First manual import target is `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`.
- Gate validates candidate metadata, official manifest non-collision and Capa1/Capa2 ZIP `config.xml`.
- Gate returns `importAllowed=false` and `requiresOperatorApproval=true`.
- Gate preserves `writesSqxHost=false`, `writesDataDb=false`, `writesUserProjects=false`, `mutatesDatabanks=false` and `runsSqxTasks=false`.
- Next movement requires the exact operator approval phrase before `BS-AI9 manual import execution after explicit operator approval`.

## BS-AI9 Manual Import Execution

`bs-ai9-manual-import-execution-v1` executes the approved first visible SQX file-dialog attempt and stops before any unsafe resource action:

- Approved candidate remains `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`.
- Only approved Capa1 was submitted through SQX `Open existing project`; Capa2 was not attempted.
- SQX returned `Resolve project resources` for `AUDCAD` with source `N/A` and status `Not found`.
- The modal actions observed were `Load without resolving these issues`, `Add missing symbols` and `Close`.
- The only accepted action was `Close`.
- Result status is `blocked_resource_resolution_modal_no_import_loaded`.
- Post-attempt checks preserve `dataDbShaUnchanged=true`, `projectsFileCountUnchanged=true`, `noBSAIInHostProjects=true`, `noAUDCADInHostProjects=true`.
- Next gate is `BS-AI10 target-resource compatibility gate` before any further import attempt.

## BS-AI10 Target Resource Compatibility Gate

`bs-ai10-target-resource-compatibility-gate-v1` adds a target-host resource gate before any further SQX file-dialog attempt:

- The gate reads the `sqx144_full` resource catalog in `sqlite_uri_mode_ro_query_only`.
- The original BS-AI9 pair remains blocked because primary resources use `AUDCAD` source `0` / broker `-1`.
- The target catalog expects primary `AUDCAD_darwinex` source `4` / broker `4`.
- `AUDCAD_dukascopy` is present and allowed only as governed cross-broker OOS methodology in the expected retest tasks.
- BS-AI10 generated the separate remapped pair `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx` / `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx`.
- Remapped pair status is `ready_for_manual_import_gate_with_methodology_warnings` and wrapper status is `remap_ready_for_manual_import_gate_no_import`.
- This resource remap does not change the BSAI candidate, official v6/v7 BlockSettings, official manifest or promotion policy.
- Next gate is `BS-AI11 remapped manual import gate` with explicit operator approval.

## BS-AI11 Remapped Manual Import Gate

`bs-ai11-remapped-manual-import-gate-v1` executes the approved import of the remapped pair into `sqx144_full` without changing the BlockSettings source policy.

Status: `remapped_capa1_capa2_imported_visible_no_tasks_started`

- Imported pair is `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx` / `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx`.
- Import used SQX local remote access `taskmanager/openProject` with `loadAsIs=false`.
- SQX returned `hasResourcesXML=false` for both imports, so no unresolved-resource load or `loadAsIs=true` escalation was used.
- Imported Custom Projects are visible as Capa1/Capa2 BSAI projects with `tasks=14`, `databanks=15`, `strategies=0` and `hasUnresolvedResources=false`.
- This import does not change the BSAI candidate, official v6/v7 BlockSettings, official manifest or promotion policy.
- Next gate is `BS-AI12 imported project read-only review`; execution remains blocked until a later explicit operator gate.

## BS-AI12 Imported Project Read-Only Review

`bs-ai12-imported-project-readonly-review-v1` reviews the BS-AI11 imported projects without pressing `Start`.

Status: `imported_project_readonly_review_passed_with_methodology_warnings_no_start`

- Reviewed projects are `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1` and `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2`.
- Remote read-only listing confirms `tasks=14`, `databanks=15`, `strategies=0` and `hasUnresolvedResources=false` for both.
- Capa1 active build trace remains official `BS_Volatilidad_v6_intraday_v6`.
- Capa2 active build trace is local candidate `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`.
- Candidate base remains `BS_Filtros_v7_H1` with `sourceVersionPolicy=explicit_base_preserve_official_v6_v7` and `promotionState=local_candidate`.
- Resource review returns `targetFailCount=0` and `targetWarnCount=2` for expected `methodology_cross_broker_catalog_match`: primary `AUDCAD_darwinex`, governed cross-broker `AUDCAD_dukascopy`.
- The review does not change the BSAI candidate, official v6/v7 BlockSettings, official manifest or promotion policy.
- Next gate is `BS-AI13 first manual Start gate requires explicit operator approval`.

## BS-AI13 First Manual Start Gate

`bs-ai13-first-manual-start-gate-v1` executes the first approved Start on the imported Capa1 project only.

Status: `first_start_requested_observed_no_capa2_start`

- Approved project started through `project/start`: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1`.
- Capa2 project remained not-started: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2`.
- Preflight preserved `tasks=14`, `strategies=0` and `hasUnresolvedResources=false` for both projects, with `capa2StartAllowed=false`.
- SQX returned `Project execution started.` and sanitized logs show Capa1 loading `AUDCAD_darwinex / H1`.
- Capa1 active BlockSetting remains official `BS_Volatilidad_v6_intraday_v6`.
- Capa2 candidate remains local `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`, based on `BS_Filtros_v7_H1`, and was not started.
- Post-outage readback returns `remote_access_unavailable`; local snapshot still shows Capa1 with only the BS-AI13 project log and Capa2 unchanged.
- The Start gate may allow SQX-owned writes in the target project/log/databank area, but it does not change the BSAI candidate, official v6/v7 BlockSettings, official manifest or promotion policy.
- Next gate is `BS-AI14 monitor Capa1 run and decide Capa2 start`.

## BS-AI14 Capa1 Monitor Decision

`bs-ai14-capa1-monitor-decision-v1` monitors the first Capa1 run before any stop/retest/Capa2 decision.

Status: `monitor_ready_stop_or_review_candidate_no_capa2`

- `tools/sqx144_bsai14_capa1_monitor_gate.ps1 status|monitor|decision-template` reads SQX remote state and sanitized local counters.
- Capa1 remains the only started project and reports `tasks=14`, `databanks=15`, `strategies=385`, `hasUnresolvedResources=false`.
- Capa2 remains unstarted with `strategies=0` and empty databanks.
- Capa1 `project.cfx` hash remains OK.
- `RETEST 0` contains 3 `.sqx` files.
- Current recommendation is `stop_or_review_candidate_no_capa2` because the latest log is stale and the `RETEST 0` survivor count is thin.
- Post-stop retest conclusion is `tick_real_pf_failed_trade_threshold_warning_no_capa2`: `RETEST 0` holds 37 `.sqx`, `retest 1` holds 5 `.sqx`, `TICK` holds 0 `.sqx`, and the sanitized `TICK REAL` log attributes the first logged 5/5 rejection to `Profit factor[Main data] >= 1.30`. SQX does not prove later filters would have passed because it appears to stop/log at the first failed active filter. The absolute TICK REAL trade-count filter remains a methodology warning because it gives no tolerance for real-tick precision changing trade count versus simulated-tick gates.
- Stop requires exact operator approval `APRUEBO STOP BS-AI14 CAPA1 SIN CAPA2`; BS-AI14 itself does not stop Capa1.
- Capa2 Start, new import, `loadAsIs`, resource resolution, databank deletion, BSAI promotion, official manifest change and 144.2953 promotion remain blocked.

## BS-AI15 Tick Real Diagnostic

`bs-ai15-tick-real-diagnostic-v1` closes the post-failure diagnostic without changing the BSAI source policy.

Status: `diagnostic_plan_ready_no_capa2_no_filter_relaxation`

- Frozen lot remains `tick_real_pf_failed_trade_threshold_warning_no_capa2`.
- Databank evidence remains `RETEST 0=37`, `retest 1=5`, `TICK=0`.
- No Capa2 and No filter relaxation: the current candidate is failed for Capa2 and is not rescued by changing pass states.
- `tools/sqx144_bsai15_tick_real_diagnostic.ps1 status|audit|plan` reads the 5 `retest 1` `.sqx` ZIPs read-only.
- The 5 survivors show observed pre-real-tick trades 300-311 and public-safe SQStats metrics/proxies, but direct `ProfitFactor` and canonical `DrawdownPct` are not embedded as plain survivor metrics.
- The first logged TICK REAL blocker remains `Profit factor[Main data] >= 1.30`; SQX does not prove the later filters would have passed.
- TICK REAL contains `# of trades >= 200` and `RetestWithHigherPrecision` retention against `main` at 80%, so the next experiment must pre-register the trade-count rule explicitly.
- Proposed BS-AI16 rule shape is `realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))`, as a new Capa1 experiment, not reinterpretation of this lot.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.

## BS-AI16 Capa1 Experiment Pre-Registration Gate

`bs-ai16-capa1-experiment-prereg-gate-v1` prepares the next Capa1 experiment without changing the BSAI source policy.

Status: `preregistered_capa1_tick_rule_ready_no_import_no_start`

- Frozen lot remains `tick_real_pf_failed_trade_threshold_warning_no_capa2`.
- Pre-registered TICK REAL rule is `realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))`.
- Selected rule point is `retentionRatio=0.65` and `absoluteFloor=120`.
- SQX representation is `NumberOfTrades >= 120` plus `RetestWithHigherPrecision` `NumberOfTrades >= 65%` of `main`.
- `spreadCostSanity` records the low-spread hypothesis before any run: primary `AUDCAD_darwinex` spread `1` matches host catalog `1.0`, while `AUDCAD_dukascopy` spread `1` versus alternate default `1.9` remains a cross-broker methodology warning.
- `tools/sqx144_bsai16_capa1_experiment_gate.ps1 status|plan|prepare` can prepare only ignored local evidence and a local `.cfx` artifact.
- Prepared artifact is `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001.cfx` with evidence `bsai16_capa1_experiment_gate_prepare_20260607_195815.json`; ZIP is valid with `config.xml`, TICK REAL `120/65%`, and PF/Winning/ReturnDD preserved.
- No import, No Start, No Capa2, no `data.db` patch, no `user/projects` patch and no databank mutation are allowed in BS-AI16.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.
- Next gate is `BS-AI17 controlled Capa1 import/start gate after operator approval`.

## BS-AI17 Controlled Import Start Gate

`bs-ai17-controlled-capa1-import-start-gate-v1` executed the approved SQX144 Full import/start path for the BS-AI16 Capa1 artifact without changing the BSAI source policy.

Status: `controlled_capa1_import_start_requested_no_capa2`

- Target artifact/project is `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`.
- The operator accepts the `cross-broker spread warning` for `this trial only`.
- A `future asset/broker/instrument review` remains required because broker/instrument parity is a separate methodology phase.
- Import used `taskmanager/openProject` with `loadAsIs=false` and `hasResourcesXML=false`.
- The imported project was visible with `tasks=14`, `databanks=15`, `strategies=0` and `hasUnresolvedResources=false`.
- Start used `project/start` only for the target Capa1 project and SQX returned `Project execution started.`
- A post-Start readback returned `remote_access_unavailable` / `TimeoutError`, consistent with SQX busy after Start; BS-AI18 owns monitoring.
- No Capa2 is allowed.
- No `loadAsIs=true`, Add missing symbols, resource-resolution bypass, direct `data.db` patch, direct script-side `user/projects` patch, direct databank mutation, Migration Tool, BSAI promotion, official v6/v7 overwrite or 144.2953 promotion is allowed.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.
- Next gate is `BS-AI18 monitor BSAI16 Capa1 run`.

## SQX144 MT5 Instrument Parity Gate

`sqx144-mt5-instrument-parity-gate-v1` closes the first broker/instrument metadata review path raised by BS-AI17 without changing the BSAI source policy.

Status: `operator_data_manager_visual_confirmed_usdjpy_values`

Implementation-ready marker: `implemented_apply_gated_db_offline_usdjpy_pilot_ready`

Applied marker: `applied_verified_usdjpy_pilot_after_exact_approval`

- The pilot consumes existing MT5 `InstrumentInfo` XML for `USDJPY_Darwinex` and normalizes it to SQX144 Full `USDJPY_darwinex`.
- The gate audits SQX `data.db` in `sqlite_uri_mode_ro_query_only` and can plan only approved `INSTRUMENTS` metadata fields: `POINTVALUE`, `TICKSIZE`, `TICKSTEP`, `DEFAULTSPREAD`, `DEFAULTSLIPPAGE`, `SWAP`, `ORDERSIZEMULTIPLIER` and `ORDERSIZESTEP`.
- empty MT5 commissions do not overwrite SQX commission.
- SQX remains authoritative for `SOURCE`, `BROKER_ID`, `DATA`, `ROWS`, `DATEFROM` and `DATETO`.
- Apply is offline-only with SQX closed, verified backup, `-Apply` and exact approval phrase; `writesUserProjects=false`, `mutatesDatabanks=false`, `runsSqxTasks=false`, Migration Tool is not used.
- The USDJPY pilot applied `DEFAULTSPREAD`, `POINTVALUE` and `SWAP` under backup `sqx144_mt5_instr_20260608_163934`, plan `mt5meta_d24e57d537569509` and XML hash `42af1ba0d24211c7a465ace91a0dde429848d3145d3bb148b91ca2d9fba78d23`; verify returned `verify_passed_all_approved_fields_match`.
- The operator visually confirmed SQX Data Manager shows `POINTVALUE=624.93`, `DEFAULTSPREAD=0.7`, swap long `5.37`, short `-11.5`, triple swap `WEDNESDAY` and rollout `23:00`.
- SQX is now open, so no further DB apply, catalog sync or mutation step is allowed until SQX is closed and a new explicit operator gate is given.
- This gate does not change BSAI candidate files, official v6/v7 BlockSettings, official manifest or promotion policy.

## SQX144-MT5-AUTO1 Data Manager MT5 Bridge

`sqx144-mt5-auto1-data-manager-bridge-v1` opens the automated MT5 metadata bridge path without changing the BSAI source policy.

Status: `real_mt5_response_validated_usdjpy_p90`

- AUTO1 adds our own `SQXInfoBridge.mq5` bridge source for MT5 and SQX Edge consumer contract.
- The bridge receives a symbol request through `SQXInfoBridge.request.ini` and writes `SQXInfoBridge.latest.json`.
- The bridge calculates MT5 symbol properties and spread percentiles `p50`, `p75`, `p90`, `p95`, `p99` globally and by year over available MT5 data.
- SQX Edge validation proposes `DEFAULTSPREAD` from an explicit `spreadPolicy`; the default is `defaultSpreadPolicy=p90`.
- This answers the spread-origin concern: generated or applied SQX values must not use an unlabelled spread value when percentile evidence is available.
- Real MT5 response validated for `USDJPY_Darwinex`: `requestId=sqx_auto1_usdjpy_20260608_194938`, `mt5Symbol=USDJPY`, `spreadSamples=768790`, `DEFAULTSPREAD=0.7`, `POINTVALUE=624.30546`, `TICKSIZE=0.01`, `TICKSTEP=0.001`, `bridge_response_validated`, no blockers and no warnings.
- A future Data Manager button is planned but not installed in AUTO1: `dataManagerButtonPlanned=true`, `dataManagerButtonInstalled=false`.
- Safety boundaries remain `writesDataDb=false`, `writesUserProjects=false`, `mutatesDatabanks=false`, `runsSqxTasks=false`, `usesMigrationTool=false`.
- No SQX DB mutation in SQX144-MT5-AUTO1 unless a separate DB mutation gate is opened and approved.
- This bridge does not change BSAI candidate files, official v6/v7 BlockSettings, official manifest or promotion policy.

## SQX144-MT5-AUTO2 Data Manager Button Bridge

`sqx144-mt5-auto2-data-manager-button-bridge-v1` installs the Data Manager button bridge path without changing the BSAI source policy.

Opened marker: `opened_button_bridge_readonly_design_no_install`

Ready marker: `auto2_overlay_api_install_gate_ready_no_install`

Status: `auto2_overlay_installed_verified_no_db_no_projects_no_databanks`

- AUTO2 starts after `real_mt5_response_validated_usdjpy_p90`.
- AUTO2 adds core `backend/sqx-edge-tool/core/sqx144_mt5_auto2_datamanager.py`.
- AUTO2 adds local endpoints `/api/sqx144/mt5-auto2/status`, `/api/sqx144/mt5-auto2/request` and `/api/sqx144/mt5-auto2/validate`.
- The overlay source lives in `integrations/sqx144/datamanager_mt5_auto2_overlay/` and hooks Data Manager through `DataManagerActionTools` for `Data sources`, `DataManagerActionInstrument` for `Instruments and Sessions`, `SQXEdgeMt5BridgeActionCtrl` and fallback DOM `sqx-edge-mt5-auto2-launcher`.
- The guarded installer is `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 status|plan|install|rollback`.
- The button is installed after exact approval `APRUEBO SQX144 MT5 AUTO2 DATAMANAGER INSTALL host=sqx144_full no_db_no_projects_no_databanks`.
- Initial backup is `sqx144_mt5_auto2_button_20260608_204930`; visibility patch backup is `sqx144_mt5_auto2_button_20260608_211725`.
- Visibility patch assetVersion is `sqx144-mt5-auto2-data-manager-button-bridge-v1-data-sources-visible`.
- App-vs-browser smoke found a parallel desktop shortcut and stale Electron cache; shortcut alignment backup is `sqx144_shortcut_align_20260608_214950`, and Electron cache backup is `electron_squant_auto2_20260608_215209`.
- Installed status is `dataManagerButtonPlanned=true`, `dataManagerButtonInstalled=true`, `installed=true`, `assetsPresent=true`, `sourcesPresent=true`, `includeCount=2`, `processCount=0`, `hostRootAccepted=true`, `expectedRootName=SQX_144_Full`.
- Active JS hash is `37A93F8EAAAC620823481C44110DF50CA6FCE53444952A5348DB7A21356FB1C8`; active CSS hash is `C09D5573B4CEC403EA522E14495F464338F8B8AD34D9A79B277E11EE9314CD06`.
- The approved install wrote only Data Manager JS/CSS/include files: `writesSqxHost=true`, `writesSqxOverlayHost=true`.
- AUTO2 preserves `writesDataDb=false`, `writesUserProjects=false`, `mutatesDatabanks=false`, `runsSqxTasks=false`, `usesMigrationTool=false`, `doesNotApplyToSqx=true`, `doesNotApplyInstrumentConfig=true`.
- The installer blocks `sqx144_full_root_mismatch` outside the governed `SQX_144_Full` root.
- Validation blocks crossed MT5 responses with `latest_response_symbol_mismatch`.
- No direct `data.db` patching, `UPDATE INSTRUMENTS`, `taskmanager/openProject`, `project/start`, `project/stop`, Add missing symbols, unresolved load, databank mutation, Migration Tool or 144.2953 promotion is allowed.
- Apply remains a separate later gate.
- AUTO2 does not change BSAI candidate files, official v6/v7 BlockSettings, official manifest or promotion policy.

## Local Memory Outbox

`sqx-edge-local-memory-outbox-v1` records a local pending queue for durable notes while Mem/gbrain write quota is unavailable.

Status: `local_mem_fallback_queue_ready_pending_sync`

- Local ignored storage is `.local/memory_outbox/memory_outbox.sqlite`.
- Current queued notes are `outboxId=1` through `outboxId=35` with `pendingCount=35`, including `outboxId=16` for AUTO9 Health Watchdog source-ready, `outboxId=17` for AUTO9 Health Watchdog installed, `outboxId=18` for AUTO9 Poll Stop Patch installed, `outboxId=19` for AUTO9B Single Click UX source-ready, `outboxId=20` for AUTO9B Single Click UX installed, `outboxId=21` for AUTO9D Data Symbol Priority source-ready, `outboxId=22` for AUTO9D Data Symbol Priority installed, `outboxId=23` for AUTO9D Data Symbol Priority visual smoke confirmed with marker `sqx144-mt5-auto9d-visual-smoke-closeout-v1`, `outboxId=24` for AUTO8 native Save visual apply confirmed with marker `sqx144-mt5-auto8-native-save-visual-apply-closeout-v1`, `outboxId=25` for AUTO8 native Save post-apply no-op confirmed with status `auto8_native_save_apply_noop_confirmed_nzdjpy_dukascopy`, `outboxId=26` for AUTO10 Internal MT5 Runner source-ready with marker `sqx144-mt5-auto10-internal-mt5-runner-v1`, `outboxId=27` for AUTO10 Internal MT5 Runner install applied with status `auto10_install_source_completed`, `outboxId=28` for AUTO10 launch aborted by wrong terminal route corrected with status `auto10_launch_wrong_terminal_aborted_route_corrected_no_relaunch`, `outboxId=29` for AUTO10 correct Darwinex launch requiring EA attach with status `auto10_launch_correct_target_bridge_timeout_manual_ea_attach_required`, `outboxId=30` for AUTO11 Generic EA Attach Runner source-ready with marker `sqx144-mt5-auto11-ea-attach-runner-v1`, `outboxId=31` for AUTO11 Profile Writer Apply implemented with status `auto11_attach_profile_writer_implemented_no_apply_no_ui_fallback_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`, `outboxId=32` for AUTO11 Profile Writer applied existing MT5 needs fallback with status `auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback`, `outboxId=33` for AUTO11 UI fallback applied/verified with status `auto11_ui_fallback_completed_bridge_ready`, `outboxId=34` for BS-AI19 Post-Run Read-Only Review with status `post_run_readonly_review_completed_no_capa2`, and `outboxId=35` for BS-AI20 Decision Gate with status `decision_archive_branch_open_asset_broker_instrument_review_no_capa2`.
- Tooling is `backend/sqx-edge-tool/core/local_memory_outbox.py` and `tools/local_memory_outbox.ps1 status|enqueue|list|mark-synced`.
- Notes are marked synced only after the external Mem/gbrain write succeeds.
- This fallback does not change BSAI candidate files, official v6/v7 BlockSettings, official manifest or promotion policy.

## BS-AI18 Capa1 Monitor Gate

`bs-ai18-capa1-monitor-gate-v1` monitors the BS-AI16 Capa1 run without changing the BSAI source policy.

Status: `monitoring_capa1_bsa16_no_capa2`

- Target project remains `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`.
- The gate is read-only and may query only `taskmanager/listProjects` plus sanitized local snapshots.
- First readback after BS-AI17 shows Capa1 visible with 65 strategies, `tasks=14`, `databanks=15` and `hasUnresolvedResources=false`.
- First monitor evidence `bsai18_capa1_monitor_gate_monitor_20260607_220331.json` shows Capa1 visible with 75 strategies after 75 seconds / 4 samples.
- Sanitized databank counts remain `RETEST 0=0`, `retest 1=0`, `TICK=0`, `Forward=0`.
- Capa1 `project.cfx` hash remains preserved.
- Clean real TICK/Forward evidence is not ready yet.
- Current decision is `continue_monitoring_capa1_active_no_capa2`.
- No Capa2, No Start, No Stop, no import, no `taskmanager/openProject`, no `loadAsIs`, no Add missing symbols, no direct `data.db` patch, no direct script-side `user/projects` patch, no direct databank mutation, no Migration Tool, no BSAI promotion, no official v6/v7 overwrite or 144.2953 promotion is allowed.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.
- BS-AI19 is reserved for post-run read-only review when Capa1 is idle or clean real TICK/Forward evidence exists.

### BS-AI18 Repeat Monitor 2026-06-10

`bs-ai18-repeat-monitor-20260610-v1` repeats the BS-AI18 monitor without changing the BSAI source policy.

- Evidence: `bsai18_capa1_monitor_gate_monitor_20260610_192852.json`.
- Remote state is `remote_access_unavailable`.
- Local sanitized databanks show `Results=1321`, `RETEST 0=112`, `retest 1=14`, `TICK=0`, `Forward=0`.
- No SQX/Java/StrategyQuant process was observed in a read-only process check; only MT5 was visible.
- Decision: `monitor_blocked_review_required_no_capa2`.
- Clean real TICK/Forward remains `false`.
- No Capa2, no Start, no Stop, no import and no mutation were performed.
- BS-AI19 is allowed by the idle criterion as a future read-only review gate, but it was not executed.

## BS-AI19 Post-Run Read-Only Review

`bs-ai19-post-run-readonly-review-v1` closes the idle BS-AI16 Capa1 branch without changing the BSAI source policy.

Status: `post_run_readonly_review_completed_no_capa2`

- Target project remains `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`.
- Evidence: `bsai19_post_run_readonly_review_review_20260610_194339.json`.
- Decision: `post_run_review_no_capa2_tick_forward_empty`.
- Local sanitized databanks show `Results=1321`, `RETEST 0=112`, `retest 1=14`, `TICK=0`, `Forward=0`.
- The 14 `retest 1` survivors are learning evidence only: observed pre-real-tick trades 265-360, median 295, `NetProfitIS` 3440.5601-6314.8599.
- Direct PF is not embedded as a plain survivor metric, and after-real-tick metrics are absent because `TICK=0`.
- BS-AI16 TICK REAL rule remains `NumberOfTrades >= 120`, `RetestWithHigherPrecision` `NumberOfTrades >= 65%`, `ProfitFactor >= 1.3`, `WinningPct >= 50`, `ReturnDDRatio >= 4`.
- No Capa2, no Start, no Stop, no import, no filter relaxation, no forced pass, no `taskmanager/openProject`, no `loadAsIs`, no Add missing symbols, no direct `data.db`, no direct `user/projects`, no databank mutation and no Migration Tool.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.
- Next gate: BS-AI20 for archive, a new preregistered Capa1 experiment, or dedicated asset/broker/instrument configuration review.

## BS-AI20 Decision Gate

`bs-ai20-decision-gate-v1` closes the BS-AI20 choice without changing the BSAI source policy.

Status: `decision_archive_branch_open_asset_broker_instrument_review_no_capa2`

- Target project remains `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`.
- Evidence: `bsai20_decision_gate_decide_20260610_201532.json`.
- Decision: `archive_branch_and_open_asset_broker_instrument_review_no_capa2`.
- Latest BS-AI19 input remains `Results=1321`, `RETEST 0=112`, `retest 1=14`, `TICK=0`, `Forward=0`.
- The archive is methodology-only: `methodology_archive_only_no_host_project_move`.
- Selected next gate is `BS-AI21 asset/broker/instrument configuration review`.
- New Capa1 design is deferred until BS-AI21 completes or is explicitly waived in a later operator-approved methodology gate.
- No Capa2, No Start, No import, No forced pass, no host project move, no filter relaxation, no `taskmanager/openProject`, no `loadAsIs`, no Add missing symbols, no direct `data.db`, no direct `user/projects`, no databank mutation and no Migration Tool.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.

## BS-AI18 RetDD TICK REAL Methodology Observation

`bs-ai18-retdd-tick-real-methodology-observation-v1` records a read-only academic/SQX review while BS-AI18 Capa1 is running.

Status: `methodology_observation_no_running_project_mutation_no_capa2`

- The exact BS-AI16 artifact has an earlier soft main RetDD check at `ReturnDDRatio >= 1.2`.
- TICK REAL preserves hard `ReturnDDRatio >= 4`.
- The methodology concern is asymmetric final quality-gate calibration, not a proven failure cause.
- BS-AI16 preserved PF/Winning/ReturnDD while changing only the TICK REAL trade-count rule.
- Active BS-AI18 run must not be changed: no RetDD relaxation, no forced pass, no import, no Start/Stop action and No Capa2.
- If RetDD becomes the explicit post-run blocker, classify it as `retdd_asymmetric_final_gate_warning_no_capa2`.
- Any future RetDD change must be a new preregistered experiment: diagnostic-only RetDD, explicit RetDD ladder or stable relative RetDD retention.
- BSAI candidate files, official v6/v7 BlockSettings, official manifest and promotion policy remain unchanged.

## Traceability Rule

Every mining or generated project should keep:

- `family`
- `canonicalId`
- `filename`
- `sha256`
- `layer`
- `timeframeRule`
- origin (`manual`, `asset-card`, `csv-import`, or generated)
- for BS-AI candidates: `baseCanonicalId`, `baseVariant`, `baseSha256`, `candidateRevision`, `sourceVersionPolicy` and `promotionState`

Legacy labels such as `BS_Tendencia` and the previous v4/v5/v7 files remain aliases/resources for compatibility, but functional generation must use the resolved real v6 `.sqb` unless the operator explicitly chooses a legacy file.
