import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const overlayRoot = path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay');
const js = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-mt5-auto2.js'), 'utf8');
const css = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-mt5-auto2.css'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto2_datamanager.py'), 'utf8');

[
  'sqx144-mt5-auto2-data-manager-button-bridge-v1',
  'DataManagerActionTools',
  'DataManagerActionInstrument',
  'SQXEdgeMt5BridgeActionCtrl',
  'sqx-edge-mt5-bridge-action',
  'sqx-edge-mt5-bridge-data-action',
  'group: "data-source"',
  'group1: "instruments-sessions"',
  'hasVisibleAngularAction',
  'findActiveRibbonHost',
  '/sqx144/mt5-auto2/request',
  '/sqx144/mt5-auto2/validate',
  'safeApiBase',
  'auto2_backend_endpoint_missing_restart_required',
  'api_http_',
  '127.0.0.1',
  'localhost',
  'selectedSymbol',
  'selectedSymbolFromEditDialog',
  'selectedSymbolFromCheckedRows',
  'checkedRowSelectionState',
  'isAllowedBareSymbol',
  'symbolFromSelectionItem',
  'checked_row_required_for_mt5_bridge',
  'requestBridge(symbolOverride, options)',
  'state.lastRequestId = ""',
  'bridgeContext',
  'expectedRequestId: bridgeContext.requestId || ""',
  'expectedSymbol: bridgeContext.symbol || ""',
  'proposedSqxFields',
].forEach((marker) => {
  assert.ok(js.includes(marker), `AUTO2 overlay marker missing: ${marker}`);
});

assert.ok(!js.includes('raw.match(/\\b[A-Z]{6,8}\\b/)'), 'AUTO2 overlay must not accept arbitrary uppercase words such as WARRANTY as symbols');
assert.ok(!js.includes('item.name ||'), 'AUTO2 overlay must not raw-accept item.name as a symbol');

[
  '.sqx-edge-mt5-auto2-panel',
  '.sqx-edge-mt5-auto2-launcher',
  '.sqx-edge-mt5-auto2-grid',
].forEach((marker) => {
  assert.ok(css.includes(marker), `AUTO2 css marker missing: ${marker}`);
});

[
  "[ValidateSet('status', 'plan', 'install', 'rollback')]",
  'sqx144-mt5-auto2-data-manager-button-bridge-v1',
  'sqx144-mt5-auto2-data-manager-button-bridge-v1-data-sources-visible',
  'auto2_overlay_api_install_gate_ready_no_install',
  'auto2_overlay_installed_verified_no_db_no_projects_no_databanks',
  'APRUEBO SQX144 MT5 AUTO2 DATAMANAGER INSTALL host=sqx144_full no_db_no_projects_no_databanks',
  'sqx_process_running',
  'New-Backup',
  'backup_manifest.json',
  'SQMANAGER\\index.html',
  'internal\\web\\common',
  'SQMANAGER/build/layout.js',
  'sqx144_full_root_mismatch',
  'SQX_144_Full',
  'hostRootAccepted',
  'doesNotApplyInstrumentConfig',
  'writesSqxOverlayHostOnApply',
  'writesDataDb = $false',
  'writesUserProjects = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'usesMigrationTool = $false',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO2 wrapper marker missing: ${marker}`);
});

[
  '/api/sqx144/mt5-auto2/status',
  '/api/sqx144/mt5-auto2/request',
  '/api/sqx144/mt5-auto2/validate',
  'mt5_auto2.request_payload',
  'mt5_auto2.validate_payload',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO2 server marker missing: ${marker}`);
});

[
  'SQX144_MT5_AUTO2_VERSION',
  'auto2_overlay_api_install_gate_ready_no_install',
  'normalize_datamanager_symbol',
  'request_payload',
  'validate_payload',
  'doesNotApplyToSqx',
  'doesNotApplyInstrumentConfig',
  'latest_response_symbol_mismatch',
  'writesDataDb',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO2 core marker missing: ${marker}`);
});

[
  'UPDATE INSTRUMENTS',
  'INSERT INTO',
  'DELETE FROM',
  'InstrumentService.editInstrument',
  'massEditInstrument',
  'instruments/add',
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'Add missing symbols',
  'Load without resolving these issues',
  'loadAsIs',
  'Migration Tool allowed',
  'terminal64.exe',
  'Start-Process',
  'data.db',
  'user/projects',
].forEach((forbidden) => {
  assert.ok(!js.includes(forbidden), `AUTO2 overlay must not contain ${forbidden}`);
  assert.ok(!core.includes(forbidden), `AUTO2 core must not contain ${forbidden}`);
});

[
  'UPDATE INSTRUMENTS',
  'InstrumentService.editInstrument',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'Add missing symbols',
  'Load without resolving these issues',
  'loadAsIs',
  'Migration Tool allowed',
  'terminal64.exe',
  'Start-Process',
].forEach((forbidden) => {
  assert.ok(!wrapper.includes(forbidden), `AUTO2 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto2 data manager button contracts ok');
