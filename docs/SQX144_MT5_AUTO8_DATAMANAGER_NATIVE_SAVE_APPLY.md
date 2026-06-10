# SQX144-MT5-AUTO8 - Data Manager Native Save Apply

Status: `auto8_datamanager_native_save_apply_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import`

Previous source-ready status: `auto8_datamanager_native_save_apply_source_ready_no_install_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import`

Marker: `sqx144-mt5-auto8-datamanager-native-save-apply-v1`

UX status marker: `sqx144-mt5-auto8-datamanager-native-save-ux-status-v1`

UX status: `auto8_datamanager_native_save_ux_status_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import`

Previous UX source-ready status: `auto8_datamanager_native_save_ux_status_source_ready_no_install_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import`

Native-save visual apply closeout marker: `sqx144-mt5-auto8-native-save-visual-apply-closeout-v1`

Native-save visual apply status: `auto8_native_save_apply_visual_confirmed_nzdjpy_dukascopy`

Native-save post-apply no-op status: `auto8_native_save_apply_noop_confirmed_nzdjpy_dukascopy`

## Purpose

AUTO8 changes the Data Manager MT5 Bridge apply UX from an offline direct-DB gate to a native SQX Data Manager save path.

The `Aplicar cambios` button is allowed to work while SQX is open because it uses the same native instrument metadata save route as the Data Manager edit-instrument window:

- Angular/Data Manager service path: `BackendService.getPromise('/instruments/editInstrument', instrumentDetails)`.
- Native model fields: `defaultSpread`, `pointValue`, `tickSize`, `tickStep`, `defaultSlippage`, `orderSizeMultiplier`, `orderSizeStep`, `commissions`, `swap`.
- Overlay function: `applyViaNativeDataManagerSave`.
- Success status: `apply_completed_live_native_datamanager_save`.

## Scope

AUTO8 is installed in `sqx144_full` after exact operator approval.

Install approval:

`APRUEBO SQX144 MT5 AUTO8 DATAMANAGER NATIVE SAVE APPLY INSTALL host=sqx144_full native_save_apply_only no_direct_db no_history_import no_projects_no_databanks_no_tasks no_mt5 no_migration_tool`

Install evidence:

- backup: `sqx144_mt5_auto2_button_20260610_055402`
- status marker: `auto8_datamanager_native_save_apply_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import`
- `targetHasAuto8NativeSave=true`
- `sourceHasAuto8NativeSave=true`
- `includeCount=2`
- `processCount=0`
- JS SHA256: `3AF408D4F4DE8E0DF45AFD080AC878BB878BD3DBC8FE42C75D89666DA98027AF`
- CSS SHA256: `891C395197AE05ACC5ECAAA9CF472F8DA6318409588F98F81596869795D39273`
- SQMANAGER index SHA256: `C63AD05A02EDED23AA70B7F78006D78B552AF37F769456E109798B7EC3C89876`

The installed button may apply already-planned metadata while SQX is open. It does not call the legacy offline apply endpoints.

## UX Status Mini Phase

The UX status mini phase is installed in `sqx144_full` after separate exact overlay-install approval:

`APRUEBO SQX144 MT5 AUTO8 DATAMANAGER UX STATUS INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool`

UX install evidence:

- backup: `sqx144_mt5_auto2_button_20260610_072846`
- status marker: `auto8_datamanager_native_save_ux_status_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import`
- `targetHasAuto8UxStatus=true`
- `sourceHasAuto8UxStatus=true`
- `targetHasAuto8NativeSave=true`
- `includeCount=2`
- `processCount=0`
- JS SHA256: `E5856E2FD2FACCA182CD8342C57109CB59A54B6F7F62D4C220BC5C088A73FFF6`
- CSS SHA256: `6BBF4C59EFD50D7330850DD1B90F5F52315FC7FD8CFDCAACD8DD685019C38A80`
- SQMANAGER index SHA256: `9369EEF7AD44677982C104D6763570EB1812062C0397AC889F00C5871A13FB9D`
- asset version: `sqx144-mt5-auto8-datamanager-native-save-ux-status-v1`

The overlay now shows operator-level states instead of leaking the older offline-gate status names:

- `listo_para_aplicar_en_data_manager`: AUTO8 can use native Data Manager Save and the `Aplicar cambios` button is enabled.
- `sin_cambios_en_data_manager`: the checked metadata already matches and `Aplicar cambios` is disabled.
- `aplicando_en_data_manager`: native Save is running.
- `aplicado_en_data_manager`: native Save completed.

When a ready/no-op AUTO7 Dukascopy mirror plan is shown, legacy warnings such as `dukascopy_metadata_mirror_requires_separate_exact_gate` and `dukascopy_data_symbol_already_uses_darwinex_instrument` are hidden because AUTO8 owns the native-save UX decision.

## Operator Visual Apply Evidence

The operator visually confirmed the native Data Manager Save path on `2026-06-10` with exactly one checked `NZDJPY_dukascopy` row.

- Before apply, the panel showed `Listo para aplicar en Data Manager.`, mirror `dukascopy_copies_darwinex_sibling_metadata`, source `NZDJPY_darwinex`, target `NZDJPY_dukascopy`, `DEFAULTSPREAD=2.6`, `POINTVALUE=653.44102`, `TICKSIZE=0.01` and `TICKSTEP=0.001`.
- After pressing `Aplicar cambios`, the panel showed `aplicado_en_data_manager`, `Apply=Cambios aplicados en Data Manager.`, plan `auto7_duka_mirror_c7f99cd22c7e1ec0`, and fields `DEFAULTSPREAD,POINTVALUE,SWAP`.
- SQX showed a native success toast: `Success` / `Instrument modified`.
- Post-apply repeat smoke on the same checked `NZDJPY_dukascopy` row showed `Sin cambios en Data Manager.` and left `Aplicar cambios` disabled.
- This confirms `Aplicar cambios` can persist an AUTO7 Dukascopy mirror plan through SQX Data Manager while SQX is open.
- This evidence does not use Codex direct `data.db` writes, AUTO7 `/apply`, AUTO5 `/apply`, history import, projects, databanks, SQX tasks, MT5 launch/EA run or Migration Tool.

## Routing

- `*_dukascopy` still routes through AUTO7 `/api/sqx144/mt5-auto7/plan`.
- AUTO7 remains the mirror resolver: `dukascopy_copies_darwinex_sibling_metadata`.
- AUTO8 is only the UI/native-save apply layer after a ready AUTO7 plan or an eligible AUTO6 stability decision.
- No-op AUTO7 results such as `plan_ready_noop_data_symbol_uses_darwinex_instrument` do not call native save.

## Boundaries

- `nativeDataManagerSaveAllowed=true`.
- `sqxOpenNativeSaveAllowed=true`.
- `directDbWriteAllowed=false`.
- `directDbHistoryInsertAllowed=false`.
- `historyImportAllowed=false`.
- `usesDataSourceHistoryImport=false`.
- No `data.db` direct update from SQX Edge.
- No `/api/sqx144/mt5-auto7/apply`.
- No `/api/sqx144/mt5-auto5/apply`.
- No `DataSourceMt5Api/importData`.
- No MT5 launch or MT5 request for `*_dukascopy`.
- No projects, databanks, SQX tasks, `user/projects`, or Migration Tool.

## Verification

Required checks:

```powershell
node tests\js\contracts\sqx144_mt5_auto8_datamanager_native_save_apply_contracts.mjs
node tests\js\contracts\sqx144_mt5_auto7_datamanager_routing_behavior.mjs
node tests\js\contracts\sqx144_mt5_auto7_dukascopy_metadata_mirror_contracts.mjs
tools\sqx144_mt5_auto2_data_manager_button_bridge.ps1 plan
python -m pytest backend\sqx-edge-tool\test_sqx144_mt5_auto7_dukascopy_metadata_mirror.py backend\sqx-edge-tool\test_docs_state_consistency.py -q
git diff --check
```
