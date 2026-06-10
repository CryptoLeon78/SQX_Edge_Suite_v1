# SQX144-MT5-AUTO9 - Health Watchdog

Status: `auto9_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager source-ready status: `auto9_datamanager_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager installed status: `auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager poll-stop installed status: `auto9_datamanager_health_watchdog_poll_stop_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager single-click UX source-ready status: `auto9_datamanager_single_click_ux_source_ready_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager single-click UX installed status: `auto9_datamanager_single_click_ux_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager checkbox-only selection source-ready status: `auto9_datamanager_checkbox_only_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager checkbox-only selection installed status: `auto9_datamanager_checkbox_only_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager visual Spanish selection source-ready status: `auto9_datamanager_visual_es_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager visual Spanish selection installed status: `auto9_datamanager_visual_es_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager data-symbol priority source-ready status: `auto9_datamanager_data_symbol_priority_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager data-symbol priority installed status: `auto9_datamanager_data_symbol_priority_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Data Manager data-symbol priority visual confirmed status: `auto9_datamanager_data_symbol_priority_operator_visual_confirmed_two_dukascopy_samples`

Marker: `sqx144-mt5-auto9-health-watchdog-v1`

Data Manager marker: `sqx144-mt5-auto9-datamanager-health-watchdog-v1`

Poll-stop marker: `sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1`

Single-click UX marker: `sqx144-mt5-auto9-datamanager-single-click-ux-v1`

Checkbox-only selection marker: `sqx144-mt5-auto9c-datamanager-checked-row-selection-v1`

Visual Spanish selection marker: `sqx144-mt5-auto9c-visual-es-selection-v1`

Data-symbol priority marker: `sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1`

Data-symbol priority visual smoke closeout marker: `sqx144-mt5-auto9d-visual-smoke-closeout-v1`

## Purpose

AUTO9 makes the MT5 bridge state explicit before more metadata apply work. The panel must not look as if it is waiting forever when `SQXInfoBridge.latest.json` is missing, stale, belongs to an old `requestId`, or carries an MT5 bridge error such as `symbol_select_failed`.

The watchdog is observe-only. It reads public request/response metadata, process presence and bridge install prerequisites, then reports operator-level states such as:

- `mt5_bridge_no_responde_o_no_esta_activo`
- `mt5_bridge_ea_no_responde`
- `mt5_bridge_latest_desfasado`
- `mt5_bridge_ready_latest_matches_request`
- `mt5_bridge_error_symbol_select_failed`

## Scope

AUTO9 adds:

- core module `backend/sqx-edge-tool/core/sqx144_mt5_auto9_health_watchdog.py`
- wrapper `tools/sqx144_mt5_auto9_health_watchdog.ps1 status|health|automation-plan|approval-template`
- backend health fields from `core/sqx144_mt5_bridge.py`
- local endpoints:
  - `/api/sqx144/mt5-auto9/status`
  - `/api/sqx144/mt5-auto9/health`
  - `/api/sqx144/mt5-auto9/automation-plan`
  - `/api/sqx144/mt5-auto9/approval-template`
- Data Manager overlay source marker `AUTO9_HEALTH_WATCHDOG_VERSION`
- Data Manager overlay source marker `AUTO9_SINGLE_CLICK_UX_VERSION` for the later AUTO9B first-click UX fix
- Data Manager overlay source marker `AUTO9_CHECKED_ROW_SELECTION_VERSION` for the AUTO9C checkbox-only selection authority fix
- Data Manager overlay source marker `AUTO9_VISUAL_ES_SELECTION_VERSION` for the AUTO9C visual Spanish status and checked-row text fallback fix
- Data Manager overlay source marker `AUTO9_DATA_SYMBOL_PRIORITY_VERSION` for the AUTO9D data-symbol priority fix

The overlay install is not active until a separate exact approval is supplied:

`APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`

Installed status after exact approval:

`auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`

Install evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`
- Backup: `sqx144_mt5_auto2_button_20260610_085714`
- Asset version: `sqx144-mt5-auto9-datamanager-health-watchdog-v1`
- Host status: `targetHasAuto9HealthWatchdog=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `073DE642D10BBB665DF8A574C2431CB6E654F81376B197B82D00FBCDEF16E0C9`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `2CF73D1D4710C9F0AD85C47AEC0A6074E8F8E842DF95C3D2621572EB350B34DD`

Poll-stop patch evidence after operator visual smoke:

- Visual symptom: Darwinex symbols with MT5 closed still showed `waiting_for_mt5_bridge` / `latest_response_request_id_mismatch`.
- Diagnosis: the local backend process was stale before AUTO9 endpoints were loaded, and the overlay kept polling `waiting_for_requested_response` without rendering bad `bridgeHealth` while busy.
- Backend action: local backend on `127.0.0.1:5050` was restarted; `/api/sqx144/mt5-auto9/status` and AUTO3 `bridge-validate` now return `panelStatus=mt5_bridge_no_responde_o_no_esta_activo`, `severity=bad`, `terminalProcessRunning=false` and `requestNewerThanLatestResponse=true`.
- Overlay action: added `AUTO9_HEALTH_POLL_STOP_VERSION`, `shouldStopPollingForBridgeHealth` and priority rendering for `bridgeHealthUiState`.
- Approval reused within the same AUTO9 boundary: `APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`
- Backup: `sqx144_mt5_auto2_button_20260610_094101`
- Asset version: `sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1`
- Host status: `targetHasAuto9HealthWatchdog=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `705B1A49E6BB2021B86DB37275568AEAD3B2DB5ED836ED200C9F1BFB3D04423B`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `A50133CC861D326BC1858FDBB76F527572A6BF64DDBF1D432AD9BC322F937326`

AUTO9B single-click UX source-ready evidence after operator smoke:

- Visual symptom: with AUTO9 health working, some Darwinex clicks still needed pressing `MT5 bridge` twice before the panel/request settled.
- Diagnosis: Data Manager selection can lag the toolbar action; the old fallback listened after Angular and could reuse stale `state.lastSymbol`.
- Overlay source action: added `AUTO9_SINGLE_CLICK_UX_VERSION`, `selectedSymbolFromCheckedRows`, `input[type='checkbox']:checked` row detection, capture-phase `pointerdown`/`click` fallback, a `0/75/200ms` selection-settle loop with `resolviendo_seleccion_data_manager`, and `selected_symbol_not_found` when no current row can be proven.
- Installer plan action: `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 plan` now reports `sourceHasAuto9SingleClickUx=true`, `targetHasAuto9SingleClickUx=false`, source status `auto9_datamanager_single_click_ux_source_ready_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`, asset version `sqx144-mt5-auto9-datamanager-single-click-ux-v1`, and approval template `APRUEBO SQX144 MT5 AUTO9B DATAMANAGER SINGLE CLICK UX INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`.
- No host install, DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this source-ready step.

AUTO9B single-click UX installed evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO9B DATAMANAGER SINGLE CLICK UX INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`
- Installed status: `auto9_datamanager_single_click_ux_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`
- Backup: `sqx144_mt5_auto2_button_20260610_110008`
- Asset version: `sqx144-mt5-auto9-datamanager-single-click-ux-v1`
- Host status: `targetHasAuto9SingleClickUx=true`, `sourceHasAuto9SingleClickUx=true`, `targetHasAuto9HealthWatchdog=true`, `targetHasAuto8NativeSave=true`, `targetHasAuto8UxStatus=true`, `targetHasAuto7=true`, `targetHasAuto6=true`, `targetHasSelectionGuard=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `8AD7D8A75C245663277F22347EFB2313CAE0D2C039F16B20EBD22612BAF6E3C1`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `8CA0DCB5CEF3AF7CE611414692147D4355DF5A026BA6FECB844DDBE4F7BE6D6E`
- No DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this install.

AUTO9C checkbox-only selection source-ready evidence after operator clarification:

- Visual symptom: Data Manager has three different selection surfaces: checkbox selection, single-click visual row/cell selection and double-click edit dialog selection. The operator confirmed two apparent selections can coexist, so the MT5 bridge must not trust the visual blue row or the edit dialog as action authority.
- Decision: MT5 bridge action authority is exactly one checked Data Manager row. A single-click visual selection without a checked row must do nothing; a double-click edit dialog must not change the target; two or more checked rows must show a notification/status and perform no request or apply.
- Overlay source action: added `AUTO9_CHECKED_ROW_SELECTION_VERSION`, `checkedRowSelectionState`, `checked_row_required_for_mt5_bridge` and `multiple_checked_rows_blocked_for_mt5_bridge`. `requestBridge`, `Refresh` and `Aplicar cambios` re-check the current checkbox state before any request/apply and clear stale `state.lastSymbol` authority.
- Installer plan action: `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 status|plan` now reports `sourceHasAuto9CheckedRowSelection=true`, `targetHasAuto9CheckedRowSelection=false`, source status `auto9_datamanager_checkbox_only_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`, asset version `sqx144-mt5-auto9c-datamanager-checked-row-selection-v1`, and approval template `APRUEBO SQX144 MT5 AUTO9C DATAMANAGER CHECKBOX ONLY SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`.
- No host install, DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this source-ready step.

AUTO9C checkbox-only selection installed evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO9C DATAMANAGER CHECKBOX ONLY SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`
- Installed status: `auto9_datamanager_checkbox_only_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`
- Backup: `sqx144_mt5_auto2_button_20260610_123721`
- Asset version: `sqx144-mt5-auto9c-datamanager-checked-row-selection-v1`
- Host status: `targetHasAuto9CheckedRowSelection=true`, `sourceHasAuto9CheckedRowSelection=true`, `targetHasAuto9SingleClickUx=true`, `targetHasAuto9HealthWatchdog=true`, `targetHasAuto8NativeSave=true`, `targetHasAuto8UxStatus=true`, `targetHasAuto7=true`, `targetHasAuto6=true`, `targetHasSelectionGuard=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `2E27AE2E741DC22DBBD45B6F449B7CB4FA98EAA769F4310B8C148D5201ED8ACE`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `31E8BD06FC7C979A349FED46A8EFA5F49089DB9BA625B9F75659623E4D32A735`
- Verification: AUTO8 native save apply contract OK, AUTO9 health/checked-row contract OK, pytest `7 passed, 13394 subtests passed`.
- No DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this install.

AUTO9C visual Spanish selection source-ready evidence after operator smoke:

- Visual symptom: with a single checkbox marked, SQX can render the checkbox in a pane whose DOM row text does not include the instrument cells, so the previous resolver could return `checked_row_symbol_not_found` even though exactly one row was checked.
- Operator UX request: warning/status texts should be shown in Spanish for the panel only, while internal codes stay unchanged to avoid destabilizing existing gates.
- Overlay source action: added `AUTO9_VISUAL_ES_SELECTION_VERSION`, `visualMessage`, same-row visual-cell fallback through `checkedRowTextFromGeometry`, and broader checked-row text extraction through `checkedRowTextFromAncestors` before falling back to geometry.
- Wrapper plan action: `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 status|plan` now reports `sourceHasAuto9VisualEsSelection=true`, `targetHasAuto9VisualEsSelection=false`, source status `auto9_datamanager_visual_es_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`, asset version `sqx144-mt5-auto9c-visual-es-selection-v1`, and approval template `APRUEBO SQX144 MT5 AUTO9C UX ES SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`.
- No host install, DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this source-ready step.

AUTO9C visual Spanish selection installed evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO9C UX ES SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`
- Installed status: `auto9_datamanager_visual_es_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`
- Backup: `sqx144_mt5_auto2_button_20260610_141114`
- Asset version: `sqx144-mt5-auto9c-visual-es-selection-v1`
- Host status: `targetHasAuto9VisualEsSelection=true`, `sourceHasAuto9VisualEsSelection=true`, `targetHasAuto9CheckedRowSelection=true`, `targetHasAuto9SingleClickUx=true`, `targetHasAuto9HealthWatchdog=true`, `targetHasAuto8NativeSave=true`, `targetHasAuto8UxStatus=true`, `targetHasAuto7=true`, `targetHasAuto7DataSymbolGuard=true`, `targetHasAuto6=true`, `targetHasSelectionGuard=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `769A70357BAB8D7CCC9A46B6CDDBBE82BB86458C0D412C50FCCACF7C475AE402`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `6520618AE2E3667DB0C64C08E0E1875ED745B9EBC5FF9A8BD9E9E91D657E2357`
- No DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this install.

AUTO9D data-symbol priority source-ready evidence after operator smoke:

- Visual symptom: zero checks and multiple checks now block correctly in Spanish, but a single checked `*_dukascopy` row could still resolve as bare underlying such as `AUDCAD`, then route through Darwinex/MT5 health instead of AUTO7 mirror.
- Decision: checked-row authority stays exactly one checkbox, but row symbol extraction must prefer suffixed Data Manager data symbols. When a row contains both `*_dukascopy` and linked `*_darwinex`, the `*_dukascopy` data symbol wins; bare underlying symbols are last-resort only.
- Overlay source action: added `AUTO9_DATA_SYMBOL_PRIORITY_VERSION`, `candidateFromDataRowText`, suffixed broker candidate collection and combined same-row geometry scoring so split visual cells preserve `AUDCAD_dukascopy` plus `AUDCAD_Darwinex` linked instrument.
- Wrapper plan action: `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 status|plan` now reports `sourceHasAuto9DataSymbolPriority=true`, `targetHasAuto9DataSymbolPriority=false`, source status `auto9_datamanager_data_symbol_priority_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`, asset version `sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1`, and approval template `APRUEBO SQX144 MT5 AUTO9D DATAMANAGER DATA SYMBOL PRIORITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`.
- No host install, DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this source-ready step.

AUTO9D data-symbol priority installed evidence:

- Approval: `APRUEBO SQX144 MT5 AUTO9D DATAMANAGER DATA SYMBOL PRIORITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`
- Installed status: `auto9_datamanager_data_symbol_priority_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool`
- Backup: `sqx144_mt5_auto2_button_20260610_160204`
- Asset version: `sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1`
- Host status: `sourceHasAuto9DataSymbolPriority=true`, `targetHasAuto9DataSymbolPriority=true`, `targetHasAuto9VisualEsSelection=true`, `targetHasAuto9CheckedRowSelection=true`, `targetHasAuto9SingleClickUx=true`, `targetHasAuto9HealthWatchdog=true`, `targetHasAuto8NativeSave=true`, `targetHasAuto8UxStatus=true`, `targetHasAuto7=true`, `targetHasAuto7DataSymbolGuard=true`, `targetHasAuto6=true`, `targetHasSelectionGuard=true`, `includeCount=2`, `processCount=0`
- JS SHA256: `50719D3E00031D8AB331926EAC8B2BD7DF9CDF3FD40A1E3B9AAE5B59D2A44A61`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `738AF9A830A640AF64FAA15F49D74CC1044AC673D6A037D349B4ED3E56212267`
- No DB write, metadata apply, history import, MT5 launch, EA run, project/databank/task mutation or Migration Tool action was executed in this install.

AUTO9D visual smoke evidence:

- Marker: `sqx144-mt5-auto9d-visual-smoke-closeout-v1`
- Visual status: `auto9_datamanager_data_symbol_priority_operator_visual_confirmed_two_dukascopy_samples`
- Sample 1: `AUDCAD_dukascopy` resolved as instrument `AUDCAD_dukascopy`, mirror `dukascopy_copies_darwinex_sibling_metadata`, source `AUDCAD_darwinex`, target `AUDCAD_dukascopy`, and visual status `Listo para aplicar en Data Manager.`
- Sample 1 values: `DEFAULTSPREAD=1.3`, `POINTVALUE=71753.512334`, `TICKSIZE=0.0001`, `TICKSTEP=0.00001`
- Sample 2: `EURGBP_dukascopy` resolved as instrument `EURGBP_dukascopy`, mirror `dukascopy_copies_darwinex_sibling_metadata`, source `EURGBP_darwinex`, target `EURGBP_dukascopy`, and visual status `Listo para aplicar en Data Manager.`
- Sample 2 values: `DEFAULTSPREAD=0.5`, `POINTVALUE=129882`, `TICKSIZE=0.0001`, `TICKSTEP=0.00001`
- Conclusion: exactly-one-checkbox Dukascopy rows now route to AUTO7 mirror/no-MT5 path instead of bare-underlying Darwinex/MT5 health fallback.
- SQX was left closed after the operator smoke. No code, DB, project, databank, task, apply/import, MT5 launch/EA run or Migration Tool action was executed for this visual confirmation.

## Panel UX

When a Darwinex symbol waits on MT5, the panel now receives `bridgeHealth` with:

- `panelStatus`
- `severity`
- `terminalProcessRunning`
- `request.ageSeconds`
- `latestResponse.ageSeconds`
- `latestResponse.status`
- `latestResponse.error`

The UI shows `Health`, `MT5`, `Request age` and `Latest age` rows, disables `Aplicar cambios`, and keeps polling only while the status is still the normal fresh-wait state `waiting_for_requested_response`.

After the poll-stop patch, bad health states such as `mt5_bridge_no_responde_o_no_esta_activo`, `mt5_bridge_ea_no_responde`, `mt5_bridge_latest_desfasado` and `mt5_bridge_error_symbol_select_failed` stop polling and render immediately through `shouldStopPollingForBridgeHealth`.

AUTO9B prepared the first-click path, but AUTO9C supersedes its selection authority. The bridge now trusts only `input[type='checkbox']:checked` in the Data Manager grid. Modal, visible grid selection, single-click row/cell selection, Angular selection payloads, double-click edit dialog context and stale `state.lastSymbol` are non-authoritative for MT5 bridge execution.

AUTO9C panel outcomes:

- exactly one checked row: continue with that checked row only;
- zero checked rows: internal `checked_row_required_for_mt5_bridge`, visual Spanish message, no request and no apply;
- multiple checked rows: internal `multiple_checked_rows_blocked_for_mt5_bridge`, visual Spanish message, no request and no apply;
- explicit target mismatch: internal `checked_row_target_mismatch_for_mt5_bridge`, visual Spanish message, no request and no apply.

The visual Spanish layer is display-only: `visualMessage` maps internal codes such as `checked_row_required_for_mt5_bridge`, `multiple_checked_rows_blocked_for_mt5_bridge`, `checked_row_symbol_not_found`, `latest_response_request_id_mismatch` and `mt5_bridge_no_responde_o_no_esta_activo` to Spanish panel text while preserving the original values in state, API payloads, blockers and tests.

AUTO9D refines the exactly-one-checkbox path: Data Manager checked rows prefer suffixed data symbols (`*_dukascopy`, `*_darwinex`, future broker suffixes) over bare underlying symbols. For `*_dukascopy` rows, this keeps the bridge on the AUTO7 no-MT5 mirror path while preserving the linked `*_darwinex` instrument for metadata comparison.

## Internal Automation Track

The operator requirement is that the future bridge should not depend on manually opening MT5 or attaching the EA. AUTO9 records that as the next planned phase, not as an implicit permission in this phase.

AUTO10 will need a separate gate before any of these are allowed:

- launch `terminal64.exe` hidden or minimized
- compile `SQXInfoBridge.mq5`
- attach or run `SQXInfoBridge` automatically
- maintain a bridge profile/chart
- check heartbeat and recover stale response loops

Risk note: MT5 is not guaranteed to be truly headless. Login prompts, broker updates, Algo Trading permissions or modals can still appear. AUTO10 must prove heartbeat and failure handling before it becomes background infrastructure.

## Boundaries

- `healthWatchdogObserveOnly=true`
- `autoStartAllowed=false`
- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `launchesMt5=false`
- `runsMt5Ea=false`
- `placesOrders=false`
- `usesMigrationTool=false`
- `directDbHistoryInsertAllowed=false`
- `historyImportAllowed=false`
- no metadata apply
- no history import
- no `data.db` direct write
- no projects, databanks, tasks or `user/projects`

## Verification

Required install verification checks:

```powershell
node --check integrations\sqx144\datamanager_mt5_auto2_overlay\sqx-edge-mt5-auto2.js
node tests\js\contracts\sqx144_mt5_auto9_health_watchdog_contracts.mjs
node tests\js\contracts\sqx144_mt5_auto8_datamanager_native_save_apply_contracts.mjs
python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto9_health_watchdog.py backend\sqx-edge-tool\test_docs_state_consistency.py -q
tools\sqx144_mt5_auto9_health_watchdog.ps1 status
tools\sqx144_mt5_auto9_health_watchdog.ps1 health
tools\sqx144_mt5_auto9_health_watchdog.ps1 automation-plan
tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 status
tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 plan
git diff --check
```
