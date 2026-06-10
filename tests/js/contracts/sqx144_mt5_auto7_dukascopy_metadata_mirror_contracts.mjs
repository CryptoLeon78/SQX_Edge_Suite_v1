import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto7_dukascopy_metadata_mirror.py'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto7_dukascopy_metadata_mirror.ps1'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const overlay = fs.readFileSync(path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js'), 'utf8');
const installer = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1'), 'utf8');

[
  'sqx144-mt5-auto7-dukascopy-metadata-mirror-v1',
  'plan_ready_noop_data_symbol_uses_darwinex_instrument',
  'dataSymbolUsesDarwinexInstrument',
  'linked_instrument',
  '_data_symbol_instrument_count',
  'SQX144-MT5-AUTO7',
  'auto7_dukascopy_metadata_mirror_source_ready_no_apply_no_install',
  'dukascopy_copies_darwinex_sibling_metadata',
  'sqlite_uri_mode_ro_query_only',
  'PRAGMA query_only = ON',
  'DEFAULTSPREAD',
  'POINTVALUE',
  'TICKSIZE',
  'TICKSTEP',
  'DEFAULTSLIPPAGE',
  'ORDERSIZEMULTIPLIER',
  'ORDERSIZESTEP',
  'COMMISSIONS',
  'SWAP',
  'consumesMt5BridgeResponse',
  'writesMt5Files',
  'no_mt5 no_migration_tool',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO7 core marker missing: ${marker}`);
});

[
  "ValidateSet('status', 'audit', 'plan', 'backup', 'apply', 'verify', 'rollback')",
  'core.sqx144_mt5_auto7_dukascopy_metadata_mirror',
  'writesDataDb = $Action -eq',
  'writesUserProjects = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'launchesMt5 = $false',
  'runsMt5Ea = $false',
  'usesMigrationTool = $false',
  'directDbHistoryInsertAllowed = $false',
  'consumesMt5BridgeResponse = $false',
  'writesMt5Files = $false',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO7 wrapper marker missing: ${marker}`);
});

[
  '/api/sqx144/mt5-auto7/status',
  '/api/sqx144/mt5-auto7/audit',
  '/api/sqx144/mt5-auto7/plan',
  '/api/sqx144/mt5-auto7/backup',
  '/api/sqx144/mt5-auto7/apply',
  '/api/sqx144/mt5-auto7/verify',
  '/api/sqx144/mt5-auto7/rollback',
  'mt5_auto7.plan_payload',
  'mt5_auto7.apply_payload',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO7 server marker missing: ${marker}`);
});

[
  'AUTO7_DUKASCOPY_MIRROR_VERSION',
  'sqx144-mt5-auto7-dukascopy-metadata-mirror-v1',
  'AUTO7_DATA_SYMBOL_GUARD_VERSION',
  'sqx144-mt5-auto7-datamanager-data-symbol-selection-guard-v1',
  'selectedDukascopyDataSymbolFromEditDialog',
  'linkedInstrumentFromEditDialog',
  'clearTransientResults',
  'requestBridge(resolved.symbol, { linkedInstrument: resolved.linkedInstrument })',
  'linkedInstrument: linkedInstrument || linkedInstrumentFromEditDialog()',
  'isDukascopyMirrorSymbol',
  '/sqx144/mt5-auto7/plan',
  'mirrorDukascopy',
  'waiting_for_dukascopy_mirror_plan',
  'state.mirrorResult',
].forEach((marker) => {
  assert.ok(overlay.includes(marker), `AUTO7 overlay marker missing: ${marker}`);
});

[
  'Auto7ApprovalPhrase',
  'APRUEBO SQX144 MT5 AUTO7 DATAMANAGER DUKASCOPY MIRROR INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5',
  'Test-SourceHasAuto7',
  'Test-TargetHasAuto7',
  'Test-SourceHasAuto7DataSymbolGuard',
  'Test-TargetHasAuto7DataSymbolGuard',
  "$AssetVersion = 'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1'",
  'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1',
  "$Auto8UxStatusMarker = 'sqx144-mt5-auto8-datamanager-native-save-ux-status-v1'",
  'auto7_datamanager_dukascopy_mirror_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_mt5',
  'auto7_datamanager_dukascopy_mirror_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5',
  'auto7_datamanager_data_symbol_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5',
  'sqx144-mt5-auto8-datamanager-native-save-apply-v1',
  'Test-SourceHasAuto8NativeSave',
  'Test-TargetHasAuto8NativeSave',
].forEach((marker) => {
  assert.ok(installer.includes(marker), `AUTO7 installer marker missing: ${marker}`);
});

[
  'SQXInfoBridge.latest.json',
  'bridge_validate_payload',
  'DataSourceMt5Api/importData',
  'dataSourceMt5Api/importData',
  'bridge_csv_file_mass_import',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'loadAsIs',
  'Add missing symbols',
  'Migration Tool allowed',
  'user/projects',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `AUTO7 core must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO7 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto7 dukascopy metadata mirror contracts ok');
