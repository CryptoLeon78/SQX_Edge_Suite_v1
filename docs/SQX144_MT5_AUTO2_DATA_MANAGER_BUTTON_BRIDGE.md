# SQX144-MT5-AUTO2 - Data Manager Button Bridge

Marker: `sqx144-mt5-auto2-data-manager-button-bridge-v1`
Opened marker: `opened_button_bridge_readonly_design_no_install`
Ready marker: `auto2_overlay_api_install_gate_ready_no_install`
Status: `auto2_overlay_installed_verified_no_db_no_projects_no_databanks`
Host: `sqx144_full`

## Purpose

`SQX144-MT5-AUTO2` opens the Data Manager button phase after AUTO1 produced a real validated MT5 response for `USDJPY_Darwinex`.

AUTO2 exists to add a visible Data Manager control that lets the operator request MT5 metadata for the selected instrument and view the validated SQX Edge proposal without leaving Data Manager.

The current slice installs the local SQX Edge Data Manager overlay after exact operator approval. The installed button requests/validates MT5 bridge data and displays a proposal; it does not apply instrument values.

## Starting Evidence

AUTO2 starts only because AUTO1 reached:

- `real_mt5_response_validated_usdjpy_p90`
- `SQXInfoBridge.latest.json`
- `requestId=sqx_auto1_usdjpy_20260608_194938`
- `USDJPY_Darwinex`
- `mt5Symbol=USDJPY`
- `spreadSamples=768790`
- `DEFAULTSPREAD=0.7`
- `POINTVALUE=624.30546`
- `TICKSIZE=0.01`
- `TICKSTEP=0.001`
- `bridge_response_validated`

## Button Scope

The AUTO2 button is implemented as UI/read-only/request-validate first:

1. Read the selected instrument from SQX Data Manager.
2. Send the symbol to SQX Edge.
3. SQX Edge writes a bridge request for `SQXInfoBridge.mq5`.
4. The running MT5 bridge writes `SQXInfoBridge.latest.json`.
5. SQX Edge validates the response with explicit `spreadPolicy`, default `p90`.
6. The Data Manager overlay displays proposed fields and blockers/warnings.
7. No SQX field is written by AUTO2.

AUTO2 may request MT5 bridge data, but it must not update SQX.

Current implementation files:

- `backend/sqx-edge-tool/core/sqx144_mt5_auto2_datamanager.py`
- `backend/sqx-edge-tool/api/server.py`
- `integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js`
- `integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.css`
- `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1`
- `backend/sqx-edge-tool/test_sqx144_mt5_auto2_datamanager.py`
- `tests/js/contracts/sqx144_mt5_auto2_data_manager_button_contracts.mjs`

Local operator endpoints:

- `GET /api/sqx144/mt5-auto2/status`
- `POST /api/sqx144/mt5-auto2/request`
- `POST /api/sqx144/mt5-auto2/validate`

The Data Manager hook uses `DataManagerActionTools` for the `Data sources` ribbon, `DataManagerActionInstrument` for `Instruments and Sessions`, and controller `SQXEdgeMt5BridgeActionCtrl`. The selected symbol comes from the Data Manager selected row (`instrument`, `name`, `symbol`, `symbolName` or `uSymbol`) and is normalized by SQX Edge before a bridge request is written.

## Visibility Patch

The first visual smoke showed the original button was not visible from the operator's active `Data` tab because the first install registered only `DataManagerActionInstrument`. The visibility patch adds:

- `DataManagerActionTools`
- `group: "data-source"`
- `group1: "instruments-sessions"`
- `sqx-edge-mt5-bridge-data-action`
- `assetVersion=sqx144-mt5-auto2-data-manager-button-bridge-v1-data-sources-visible`
- DOM fallback `sqx-edge-mt5-auto2-launcher` if Angular plugin registration is too late for the current screen.

The fallback is still read-only/request-validate-display only. It does not write SQX instrument fields.

## Desktop App Alignment

A later app-vs-browser smoke showed the button visible in Chrome through `localhost:8080/SQUANT/index.html#/`, but not in the desktop app launched by the operator. Read-only inspection found the desktop shortcut was targeting a parallel SQX144 install, not the governed `SQX_144_Full` host.

The desktop shortcut was backed up and aligned to the governed `SQX_144_Full` root:

- `shortcutAlignmentStatus=desktop_shortcut_aligned_to_sqx144_full`
- `shortcutAlignmentBackup=sqx144_shortcut_align_20260608_214950`
- `shortcutTargetsGovernedHost=true`
- the parallel install was not modified;
- no `data.db`, `user/projects`, databanks or SQX tasks were touched.

## Electron Cache Refresh

The same app-vs-browser smoke also showed stale Electron cache for the nested Data Manager iframe. The governed host files were correct, but the desktop app cache still contained an old `SQMANAGER/index.html` response and had not requested the AUTO2 asset version.

With SQX closed, only the Electron `SQUANT` cache folders were moved to backup:

- `electronCacheRefreshStatus=electron_squant_cache_moved_to_backup`
- `electronCacheBackup=electron_squant_auto2_20260608_215209`
- moved: `Cache`, `Code Cache`
- untouched: `Local Storage`, `IndexedDB`, `WebStorage`, `Preferences`
- no `data.db`, `user/projects`, databanks, license files or SQX tasks were touched.

## Installation Result

The button was installed after exact approval:

- `dataManagerButtonPlanned=true`
- `dataManagerButtonInstalled=true`
- `installed=true`
- `assetsPresent=true`
- `sourcesPresent=true`
- `processCount=0`
- `blockers=[]`
- `hostRootAccepted=true`
- `expectedRootName=SQX_144_Full`
- `includeCount=2`
- `backupRef=sqx144_mt5_auto2_button_20260608_204930`
- `visibilityPatchBackupRef=sqx144_mt5_auto2_button_20260608_211725`
- `activeJsSha256=37A93F8EAAAC620823481C44110DF50CA6FCE53444952A5348DB7A21356FB1C8`
- `activeCssSha256=C09D5573B4CEC403EA522E14495F464338F8B8AD34D9A79B277E11EE9314CD06`

The approved installation command was gated by:

- SQX closed;
- host root accepted as `SQX_144_Full` / `sqx144_full`;
- backup of the Data Manager web files touched by the overlay;
- hash manifest;
- one JS/CSS include per file;
- rollback path;
- explicit operator approval for install.

Wrapper actions:

- `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 status`
- `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 plan`
- `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 install`
- `tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1 rollback`

Install remains gated by `-Apply` and this exact approval phrase:

`APRUEBO SQX144 MT5 AUTO2 DATAMANAGER INSTALL host=sqx144_full no_db_no_projects_no_databanks`

`install -Apply` reported `writesSqxHost=true` and `writesSqxOverlayHost=true` because the approved install wrote only the SQX Data Manager web include/assets. It still preserved all data boundaries below: no instrument values, DB rows, projects, databanks or SQX tasks were changed by AUTO2.

If the resolved SQX root is not the governed `SQX_144_Full` host, the wrapper blocks with `sqx144_full_root_mismatch`.

## Boundaries

AUTO2 must preserve:

- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `usesMigrationTool=false`
- `doesNotApplyToSqx=true`
- `doesNotApplyInstrumentConfig=true`

Forbidden in AUTO2:

- direct `data.db` patching;
- `UPDATE INSTRUMENTS`;
- `taskmanager/openProject`;
- `project/start`;
- `project/stop`;
- `Add missing symbols`;
- `Load without resolving these issues`;
- `user/projects` mutation;
- databank mutation;
- Migration Tool;
- SQX144 144.2953 promotion;
- engine, binary, internal plugin or license material changes.

Response validation also blocks stale or crossed responses:

- mismatched `requestId` waits as `latest_response_request_id_mismatch`;
- matched `requestId` with another selected symbol blocks as `latest_response_symbol_mismatch`.

## Verification

Current local verification for this slice:

- `python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto2_datamanager.py -q`
- `node tests\js\contracts\sqx144_mt5_auto2_data_manager_button_contracts.mjs`
- `tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 status`
- `tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 plan`

The first visual smoke after approved install should only prove that the selected Data Manager instrument can request and display MT5 bridge data. Instrument apply remains a separate later gate.
