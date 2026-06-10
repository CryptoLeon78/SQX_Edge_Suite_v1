# Local Memory Outbox

Marker: `sqx-edge-local-memory-outbox-v1`
Status: `local_mem_fallback_queue_ready_pending_sync`

## Purpose

`LOCAL_MEMORY_OUTBOX` is a temporary local fallback for durable project notes that should go to Mem/gbrain but cannot be written while the free-tier limit is active.

The outbox stores only project decisions, process notes and reusable context that would otherwise be saved to Mem. It is not a replacement for Mem; it is a pending queue for later sync.

## Storage

- Local ignored DB: `.local/memory_outbox/memory_outbox.sqlite`
- Current fallback items: `outboxId=1` through `outboxId=35`
- Current pending state: `pendingCount=35`
- Privacy marker: `localPathsReturned=false`
- Tokens and license material are never stored by this tool: `tokensReturned=false`, `licenseMaterialReturned=false`

## Tooling

Core module:

- `backend/sqx-edge-tool/core/local_memory_outbox.py`

Wrapper:

- `tools/local_memory_outbox.ps1 status`
- `tools/local_memory_outbox.ps1 enqueue`
- `tools/local_memory_outbox.ps1 list`
- `tools/local_memory_outbox.ps1 mark-synced`

The wrapper calls `core.local_memory_outbox` and supports `status|enqueue|list|mark-synced`.

## Current Note

The first queued note (`outboxId=1`) records the 2026-06-08 SQX144 MT5 bridge path:

- AUTO1 installed and compiled `SQXInfoBridge.mq5` in real MT5.
- AUTO1 produced and validated `SQXInfoBridge.latest.json` for `USDJPY_Darwinex`.
- Validated MT5 response hash: `7055EFA2827153270C2A51CAF996BD59A282FD1D1EB9DC50E4A13DDCF84379DC`.
- AUTO2 source/API/installer was prepared as `auto2_overlay_api_install_gate_ready_no_install`.
- AUTO2 is not installed yet and requires the exact Data Manager install approval phrase.

The second queued note (`outboxId=2`) records the approved AUTO2 Data Manager overlay install:

- Status: `auto2_overlay_installed_verified_no_db_no_projects_no_databanks`
- Backup: `sqx144_mt5_auto2_button_20260608_204930`
- Installed evidence: `dataManagerButtonInstalled=true`, `installed=true`, `assetsPresent=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `096FEBDF958056A23053F4B0B6EB572CB90171A3DEA32476AD4AEC20A9246D09`
- CSS SHA256: `C09D5573B4CEC403EA522E14495F464338F8B8AD34D9A79B277E11EE9314CD06`
- Boundaries preserved: `writesDataDb=false`, `writesUserProjects=false`, `mutatesDatabanks=false`, `runsSqxTasks=false`, `usesMigrationTool=false`

The third queued note (`outboxId=3`) records the AUTO2 Data Manager visibility patch:

- Diagnosis: the first approved overlay registered only `DataManagerActionInstrument`, which is not visible from the operator's active `Data` tab / `Data sources` ribbon.
- Patch: added `DataManagerActionTools` for `Data sources`, kept `DataManagerActionInstrument`, and added fallback `sqx-edge-mt5-auto2-launcher`.
- Backup: `sqx144_mt5_auto2_button_20260608_211725`
- Asset version: `sqx144-mt5-auto2-data-manager-button-bridge-v1-data-sources-visible`
- JS SHA256: `37A93F8EAAAC620823481C44110DF50CA6FCE53444952A5348DB7A21356FB1C8`
- Boundaries preserved: `writesDataDb=false`, `writesUserProjects=false`, `mutatesDatabanks=false`, `runsSqxTasks=false`, `usesMigrationTool=false`

The fourth queued note (`outboxId=4`) records the AUTO2 app-vs-browser alignment:

- Finding: Chrome localhost showed the AUTO2 button, while the desktop app did not.
- Cause: desktop shortcut pointed to a parallel SQX144 install and Electron `SQUANT` cache was stale.
- Shortcut backup: `sqx144_shortcut_align_20260608_214950`
- Electron cache backup: `electron_squant_auto2_20260608_215209`
- Moved cache folders: `Cache`, `Code Cache`
- Untouched: `Local Storage`, `IndexedDB`, `WebStorage`, `Preferences`, `data.db`, `user/projects`, databanks and license files
- Verification remained green: AUTO2 installed, MT5 instrument parity verify passed, no SQX task launched.

The fifth queued note (`outboxId=5`) records the Data Manager native-tool inspection that informed AUTO3:

- Native MT5 route observed for future design: `DataSourceMt5Api/importData`
- Native discovery route observed for future design: `dataSourceMt5Api/loadAvailableSymbols`
- Fallback route candidates: Data Manager File import and Mass import
- Related edit surfaces: add/edit/mass edit instrument, broker profile save/load XML, sessions and export tools
- AUTO3 conclusion: use those routes only in later exact gates; the current phase remains catalog/plan only.

Later queued notes (`outboxId=6` through `outboxId=35`) record the AUTO6/AUTO7/AUTO8/AUTO9/AUTO10/AUTO11 MT5 Data Manager stabilization, runner work and BS-AI19/BS-AI20 memory fallback:

- `outboxId=6`: AUTO6 Data Manager stability source ready.
- `outboxId=7`: AUTO6 Data Manager stability installed.
- `outboxId=8`: AUTO6 Data Manager selection guard source ready.
- `outboxId=9`: AUTO6 selection guard installed.
- `outboxId=10`: AUTO7 Dukascopy mirror source ready.
- `outboxId=11`: AUTO7 Data Manager Dukascopy mirror installed.
- `outboxId=12`: AUTO7 Data Symbol Selection Guard installed, including `plan_ready_noop_data_symbol_uses_darwinex_instrument` for Data rows such as `DAX40_dukascopy -> GDAXI_darwinex`.
- `outboxId=13`: SQX144 Electron cache refresh helper.
- `outboxId=14`: AUTO8 UX Status source ready.
- `outboxId=15`: AUTO8 UX Status installed.
- `outboxId=16`: AUTO9 Health Watchdog source ready with `mt5_bridge_no_responde_o_no_esta_activo` diagnostics and AUTO10 internal MT5 runner planned behind a separate gate.
- `outboxId=17`: AUTO9 Health Watchdog installed with backup `sqx144_mt5_auto2_button_20260610_085714`, `targetHasAuto9HealthWatchdog=true`, `includeCount=2`, `processCount=0`, and all DB/project/databank/task/MT5/Migration Tool boundaries preserved.
- `outboxId=18`: AUTO9 Poll Stop Patch installed with backup `sqx144_mt5_auto2_button_20260610_094101`, asset version `sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1`, backend stale-process diagnosis, `shouldStopPollingForBridgeHealth`, JS SHA256 `705B1A49E6BB2021B86DB37275568AEAD3B2DB5ED836ED200C9F1BFB3D04423B`, and all DB/project/databank/task/apply/import/MT5/Migration Tool boundaries preserved.
- `outboxId=19`: AUTO9B Data Manager Single Click UX source ready with marker `sqx144-mt5-auto9-datamanager-single-click-ux-v1`, checked-row detection, capture-phase bridge action fallback, `0/75/200ms` selection settle, `sourceHasAuto9SingleClickUx=true`, `targetHasAuto9SingleClickUx=false`, exact future approval `APRUEBO SQX144 MT5 AUTO9B DATAMANAGER SINGLE CLICK UX INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`, and all DB/project/databank/task/apply/import/MT5/Migration Tool boundaries preserved.
- `outboxId=20`: AUTO9B Data Manager Single Click UX installed with backup `sqx144_mt5_auto2_button_20260610_110008`, asset version `sqx144-mt5-auto9-datamanager-single-click-ux-v1`, `targetHasAuto9SingleClickUx=true`, `includeCount=2`, `processCount=0`, JS SHA256 `8AD7D8A75C245663277F22347EFB2313CAE0D2C039F16B20EBD22612BAF6E3C1`, CSS SHA256 `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`, SQMANAGER index SHA256 `8CA0DCB5CEF3AF7CE611414692147D4355DF5A026BA6FECB844DDBE4F7BE6D6E`, and all DB/project/databank/task/apply/import/MT5/Migration Tool boundaries preserved.
- `outboxId=21`: AUTO9D Data Symbol Priority source ready with marker `sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1`, `sourceHasAuto9DataSymbolPriority=true`, `targetHasAuto9DataSymbolPriority=false`, checked-row suffix priority (`AUDCAD_dukascopy` wins over `AUDCAD_Darwinex` and bare `AUDCAD`), exact future approval `APRUEBO SQX144 MT5 AUTO9D DATAMANAGER DATA SYMBOL PRIORITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`, and all DB/project/databank/task/apply/import/MT5/Migration Tool boundaries preserved.
- `outboxId=22`: AUTO9D Data Symbol Priority installed with backup `sqx144_mt5_auto2_button_20260610_160204`, asset version `sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1`, `targetHasAuto9DataSymbolPriority=true`, `includeCount=2`, `processCount=0`, JS SHA256 `50719D3E00031D8AB331926EAC8B2BD7DF9CDF3FD40A1E3B9AAE5B59D2A44A61`, CSS SHA256 `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`, SQMANAGER index SHA256 `738AF9A830A640AF64FAA15F49D74CC1044AC673D6A037D349B4ED3E56212267`, and all DB/project/databank/task/apply/import/MT5/Migration Tool boundaries preserved.
- `outboxId=23`: AUTO9D Data Symbol Priority visual smoke confirmed with closeout marker `sqx144-mt5-auto9d-visual-smoke-closeout-v1`, `AUDCAD_dukascopy` and `EURGBP_dukascopy` resolving as instrument `*_dukascopy`, mirror `dukascopy_copies_darwinex_sibling_metadata`, source `*_darwinex`, target `*_dukascopy` and `Listo para aplicar en Data Manager.`, confirming AUTO7 mirror/no-MT5 routing.
- `outboxId=24`: AUTO8 native Data Manager Save visual apply confirmed with marker `sqx144-mt5-auto8-native-save-visual-apply-closeout-v1`; `NZDJPY_dukascopy` moved from `Listo para aplicar en Data Manager.` to `aplicado_en_data_manager` after `Aplicar cambios`, plan `auto7_duka_mirror_c7f99cd22c7e1ec0`, fields `DEFAULTSPREAD,POINTVALUE,SWAP`, and SQX toast `Success` / `Instrument modified`, without Codex direct `data.db`, history import, project/databank/task, MT5 or Migration Tool action.
- `outboxId=25`: AUTO8 native Data Manager Save post-apply no-op confirmed with status `auto8_native_save_apply_noop_confirmed_nzdjpy_dukascopy`; repeating MT5 Bridge on the same checked `NZDJPY_dukascopy` row showed `Sin cambios en Data Manager.` and left `Aplicar cambios` disabled, preserving the same no direct `data.db`, history import, project/databank/task, MT5 or Migration Tool boundaries.
- `outboxId=26`: AUTO10 Internal MT5 Runner source-ready with marker `sqx144-mt5-auto10-internal-mt5-runner-v1`, status `auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`, exact future install/launch approval gates, preflight ready with `processCount=0`, and no bridge install/compile, MT5 launch, EA run, smoke request, `data.db`, history import, project/databank/task or Migration Tool action.
- `outboxId=27`: AUTO10 Internal MT5 Runner install applied after exact approval, status `auto10_install_source_completed`, backup `auto10_install_20260610_184357`, `copiedBridgeSource=false`, `compiledBridgeSource=true`, `compile.returnCode=0`, installed source SHA256 `DB8FBB56697710CE333CD94F5EC87D37705DA9E2E0C3AEA3A81721C2C898B897`, installed binary SHA256 `43E4BC74069C44B88C8F92D1B7D72809B0A387F1C324487C7E81FBB5AA54F693`, post-preflight `auto10_preflight_ready_no_launch`, `terminal64ProcessCount=0`, `metaeditor64ProcessCount=0`, and no launch gate, EA run, smoke request, heartbeat verify, `data.db`, history import, project/databank/task or Migration Tool action.
- `outboxId=28`: AUTO10 launch aborted and route corrected with status `auto10_launch_wrong_terminal_aborted_route_corrected_no_relaunch` after the operator flagged the launched MT5 was wrong; first launch returned `auto10_launch_started_managed_mt5_process`, smoke request `sqx_auto10_USDJPY_Darwinex_20260610_165721` timed out as `auto10_verify_bridge_timeout` / `mt5_bridge_ea_no_responde`, wrong terminal was stopped, stale managed PID removed, final `terminal64ProcessCount=0`, `metaeditor64ProcessCount=0`, default AUTO10 terminal route changed from BEPB to standard Darwinex MT5, process detection now reports `targetTerminalProcessRunning` / `targetProcessCount`, launch records `managedPidIsTargetTerminal`, and no relaunch, `data.db`, history import, project/databank/task, SQX task, Migration Tool or order action followed.
- `outboxId=29`: AUTO10 correct Darwinex launch reached `auto10_launch_correct_target_bridge_timeout_manual_ea_attach_required`: `managedPidIsTargetTerminal=true`, `targetTerminalProcessRunning=true`, `targetProcessCount=1`, `otherTerminalProcessCount=0`, request `sqx_auto10_USDJPY_Darwinex_20260610_171523` timed out as `auto10_verify_bridge_timeout` / `mt5_bridge_ea_no_responde`, request file is fresh, latest response is stale from 2026-06-09, no 2026-06-10 MQL5 Experts log entry exists for `SQXInfoBridge`, and next step is manual `SQXInfoBridge` EA attach/enable followed by AUTO10 verify.
- `outboxId=30`: AUTO11 Generic EA Attach Runner source-ready with marker `sqx144-mt5-auto11-ea-attach-runner-v1`, status `auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`, generic `host + mt5Profile + symbol + timeframe` profile contract, wrapper `tools/sqx144_mt5_auto11_ea_attach_runner.ps1 status|profile-catalog|preflight|plan|attach-plan|approval-template`, future exact attach gate, and no attach, MT5 launch, EA run, `data.db`, history import, project/databank/task, Migration Tool or order action.
- `outboxId=31`: AUTO11 Profile Writer Apply implemented with status `auto11_attach_profile_writer_implemented_no_apply_no_ui_fallback_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool`; exact attach gate writes governed MT5 assets `SQX_AUTO11_SQXInfoBridge.tpl`, `chart01.chr`, `order.wnd` and startup config for the selected `host + mt5Profile + symbol + timeframe`, returns file names/hashes only with `localPathsReturned=false`, keeps UI fallback behind a separate visible gate, and preserves no live MT5 launch in this block, no EA run, no `data.db`, no history import, no SQX projects/databanks/tasks, no Migration Tool and no orders.
- `outboxId=32`: AUTO11 Profile Writer applied to the existing standard Darwinex MT5 route with status `auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback`; wrote `profileName=SQX_AUTO11_BRIDGE_darwinex_USDJPY_Darwinex_M1`, `SQX_AUTO11_SQXInfoBridge.tpl`, `chart01.chr`, `order.wnd` and startup config, returned `templateSha256/chartSha256=9402D18BFA300A313F6E04A921CB0D3189377E9070165AA88054A18ACB7CCEFE` and `startupConfigSha256=928A615FE93AC103D060FD9E7DDD1EE5D4C3710A3183E692329E530DA4EC48EB`, then AUTO10 verify wrote `requestId=sqx_auto10_USDJPY_Darwinex_20260610_180543` and timed out as `auto10_verify_bridge_timeout` / `mt5_bridge_ea_no_responde` because the already-open MT5 session did not load the new profile in-place; next action requires the separate UI fallback gate or a future governed profile/config relaunch gate, with no UI automation, no extra MT5 launch, no EA run, no orders, no `data.db`, no history import, no SQX projects/databanks/tasks and no Migration Tool.
- `outboxId=33`: AUTO11 UI fallback applied after exact visible-control approval with status `auto11_ui_fallback_completed_bridge_ready` and marker `auto11_ui_fallback_apply_visible_operator_control_completed`; the already-open standard Darwinex MT5 session loaded `SQXInfoBridge` on active `USDJPY,H1`, Algo Trading was enabled, AUTO11 heartbeat `sqx_auto11_ui_USDJPY_Darwinex_20260610_183515` and AUTO10 verify `sqx_auto10_USDJPY_Darwinex_20260610_183446` both matched fresh `status=ok` responses for `USDJPY_Darwinex`, with no new MT5 launch, no orders, no `data.db`, no history import, no SQX projects/databanks/tasks and no Migration Tool.
- `outboxId=34`: BS-AI19 Post-Run Read-Only Review fallback note with marker `bs-ai19-post-run-readonly-review-v1`, status `post_run_readonly_review_completed_no_capa2`, decision `post_run_review_no_capa2_tick_forward_empty`, evidence `bsai19_post_run_readonly_review_review_20260610_194339.json`, `Results=1321`, `RETEST 0=112`, `retest 1=14`, `TICK=0`, `Forward=0`, and No Capa2/No Start/No Stop/no import/no filter relaxation/no forced pass boundaries.
- `outboxId=35`: BS-AI20 Decision Gate fallback note with marker `bs-ai20-decision-gate-v1`, status `decision_archive_branch_open_asset_broker_instrument_review_no_capa2`, decision `archive_branch_and_open_asset_broker_instrument_review_no_capa2`, evidence `bsai20_decision_gate_decide_20260610_201532.json`, selected next gate `BS-AI21 asset/broker/instrument configuration review`, current branch `BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`, and No Capa2/No Start/No import/No forced pass/no host project move boundaries.

## Sync Rule

When Mem/gbrain writes are available again:

1. Run `tools\local_memory_outbox.ps1 list`.
2. Create or update the appropriate Mem/gbrain page from each pending note.
3. Mark each transferred item with `tools\local_memory_outbox.ps1 mark-synced -OutboxId <id> -MemNoteId <mem-id>`.

Do not mark a note synced until the external memory write actually succeeds.
