import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const overlayPath = path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js');
const installerPath = path.join(repoRoot, 'tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1');
const wrapperPath = path.join(repoRoot, 'tools/sqx144_mt5_auto9_health_watchdog.ps1');
const serverPath = path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py');
const corePath = path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto9_health_watchdog.py');
const overlay = fs.readFileSync(overlayPath, 'utf8');
const installer = fs.readFileSync(installerPath, 'utf8');
const wrapper = fs.readFileSync(wrapperPath, 'utf8');
const server = fs.readFileSync(serverPath, 'utf8');
const core = fs.readFileSync(corePath, 'utf8');

[
  'AUTO9_HEALTH_WATCHDOG_VERSION',
  'sqx144-mt5-auto9-datamanager-health-watchdog-v1',
  'AUTO9_HEALTH_POLL_STOP_VERSION',
  'sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1',
  'AUTO9_SINGLE_CLICK_UX_VERSION',
  'sqx144-mt5-auto9-datamanager-single-click-ux-v1',
  'AUTO9_CHECKED_ROW_SELECTION_VERSION',
  'sqx144-mt5-auto9c-datamanager-checked-row-selection-v1',
  'AUTO9_VISUAL_ES_SELECTION_VERSION',
  'sqx144-mt5-auto9c-visual-es-selection-v1',
  'AUTO9_DATA_SYMBOL_PRIORITY_VERSION',
  'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1',
  'candidateFromDataRowText',
  'visualMessage',
  'AUTO9_HEALTH_WATCHDOG_CONTRACT',
  'healthWatchdogObserveOnly',
  'autoStartAllowed',
  'bridgeHealthUiState',
  'shouldStopPollingForBridgeHealth',
  'selectedSymbolFromCheckedRows',
  'checkedRowSelectionState',
  'checkedRowTextFromGeometry',
  "input[type='checkbox']:checked",
  'checked_row_required_for_mt5_bridge',
  'multiple_checked_rows_blocked_for_mt5_bridge',
  'addEventListener("pointerdown", handleAngularActionClickFallback, true)',
  'mt5_bridge_no_responde_o_no_esta_activo',
  'mt5_bridge_ea_no_responde',
  'Health',
  'Request age',
  'Latest age',
].forEach((marker) => {
  assert.ok(overlay.includes(marker), `AUTO9 overlay marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto9-health-watchdog-v1',
  'sqx144-mt5-auto9-datamanager-health-watchdog-v1',
  'auto9_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'AUTO10',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO9 core marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto9-datamanager-health-watchdog-v1',
  'sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1',
  'sqx144-mt5-auto9-datamanager-single-click-ux-v1',
  'sqx144-mt5-auto9c-datamanager-checked-row-selection-v1',
  'sqx144-mt5-auto9c-visual-es-selection-v1',
  'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1',
  'auto9_datamanager_data_symbol_priority_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'auto9_datamanager_data_symbol_priority_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO9D DATAMANAGER DATA SYMBOL PRIORITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'Test-SourceHasAuto9DataSymbolPriority',
  'Test-TargetHasAuto9DataSymbolPriority',
  'sourceHasAuto9DataSymbolPriority',
  'targetHasAuto9DataSymbolPriority',
  'auto9_datamanager_visual_es_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'auto9_datamanager_visual_es_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO9C UX ES SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'Test-SourceHasAuto9VisualEsSelection',
  'Test-TargetHasAuto9VisualEsSelection',
  'sourceHasAuto9VisualEsSelection',
  'targetHasAuto9VisualEsSelection',
  'auto9_datamanager_checkbox_only_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'auto9_datamanager_checkbox_only_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO9C DATAMANAGER CHECKBOX ONLY SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'Test-SourceHasAuto9CheckedRowSelection',
  'Test-TargetHasAuto9CheckedRowSelection',
  'sourceHasAuto9CheckedRowSelection',
  'targetHasAuto9CheckedRowSelection',
  'auto9_datamanager_single_click_ux_source_ready_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'auto9_datamanager_single_click_ux_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO9B DATAMANAGER SINGLE CLICK UX INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'auto9_datamanager_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'Test-SourceHasAuto9Health',
  'Test-TargetHasAuto9Health',
  'healthWatchdogObserveOnly = $true',
  'autoStartAllowed = $false',
].forEach((marker) => {
  assert.ok(installer.includes(marker), `AUTO9 installer marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto9-health-watchdog-v1',
  'healthWatchdogObserveOnly',
  'autoStartAllowed',
  'launchesMt5',
  'runsMt5Ea',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO9 wrapper marker missing: ${marker}`);
});

[
  '/api/sqx144/mt5-auto9/status',
  '/api/sqx144/mt5-auto9/health',
  '/api/sqx144/mt5-auto9/automation-plan',
  '/api/sqx144/mt5-auto9/approval-template',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO9 endpoint marker missing: ${marker}`);
});

[
  'Start-Process',
  'Stop-Process',
  'terminal64.exe',
  'MetaEditor64.exe',
  'DataSourceMt5Api/importData',
  'dataSourceMt5Api/importData',
  'UPDATE INSTRUMENTS',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'Add missing symbols',
  'Migration Tool allowed',
  'user/projects',
].forEach((forbidden) => {
  assert.ok(!overlay.includes(forbidden), `AUTO9 overlay must not contain ${forbidden}`);
  assert.ok(!installer.includes(forbidden), `AUTO9 installer must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO9 wrapper must not contain ${forbidden}`);
});
assert.ok(!overlay.includes('selectedSymbol({ allowLast: false }) || state.lastSymbol || ""'), 'AUTO9B fallback must not reuse stale lastSymbol');
assert.ok(!overlay.includes('document.addEventListener("click", rememberClickedSymbol, true)'), 'AUTO9C must not remember visual row clicks as bridge selection');
assert.ok(!overlay.includes('candidateFromText(symbolOverride) || selectedSymbol({ allowLast: false })'), 'AUTO9C requestBridge must not fall back to visual/modal selection');
assert.ok(!overlay.includes('requestBridge(state.lastSymbol || selectedSymbol({ allowLast: false }))'), 'AUTO9C refresh must re-check table checkboxes');
assert.ok(!overlay.includes('symbol = modalSymbol || symbol || selectedSymbol({ allowLast: false })'), 'AUTO9C payload resolver must not prefer modal/visual selection');

function visibleNode(text) {
  return {
    textContent: text,
    offsetWidth: 100,
    offsetHeight: 20,
    className: '',
    innerHTML: '',
    getClientRects: () => [{}],
    querySelectorAll: () => [],
    addEventListener: () => {},
    appendChild: () => {},
    contains: () => false,
  };
}

const document = {
  readyState: 'loading',
  body: visibleNode('body'),
  getElementById: () => null,
  addEventListener: () => {},
  createElement: () => visibleNode('created'),
  querySelectorAll: () => [],
};
let checkedBoxes = [];
let selectedNodes = [];
let geometryCells = [];
let fetchCalls = [];
const angularModule = { config: () => angularModule, controller: () => angularModule };
const window = {
  document,
  setInterval: () => 0,
  setTimeout: () => 0,
  getComputedStyle: () => ({ display: 'block', visibility: 'visible', opacity: '1' }),
  fetch: async (url) => {
    fetchCalls.push(String(url));
    return { ok: true, status: 200, json: async () => ({ ok: true }) };
  },
  angular: {
    module: () => angularModule,
    element: () => ({ injector: () => null }),
    copy: (value) => JSON.parse(JSON.stringify(value)),
  },
};
window.window = window;
window.URL = URL;
vm.runInNewContext(overlay, window, { filename: 'sqx-edge-mt5-auto2.js' });
document.getElementById = () => visibleNode('panel-node');

const checkedRow = visibleNode('NASDAQ_darwinex NDX_darwinex');
checkedRow.tagName = 'TR';
checkedRow.parentElement = document.body;
checkedRow.getAttribute = () => '';
const checkedBox = {
  value: '',
  parentElement: checkedRow,
  closest: () => checkedRow,
};
const secondCheckedRow = visibleNode('AUDCAD_darwinex AUDCAD_darwinex');
secondCheckedRow.tagName = 'TR';
secondCheckedRow.parentElement = document.body;
secondCheckedRow.getAttribute = () => '';
const secondCheckedBox = {
  value: '',
  parentElement: secondCheckedRow,
  closest: () => secondCheckedRow,
};
document.querySelectorAll = (selector) => {
  if (selector === "input[type='checkbox']:checked") return checkedBoxes;
  if (selector === 'tr.selected' || selector === "tr[class*='selected']") return selectedNodes;
  if (selector === 'td') return geometryCells;
  return [];
};
checkedBoxes = [checkedBox];

const ui = window.SQXEdgeMt5Auto2.nativeSaveUiState({
  ok: false,
  status: 'waiting_for_requested_response',
  bridgeHealth: {
    panelStatus: 'mt5_bridge_no_responde_o_no_esta_activo',
    severity: 'bad',
    terminalProcessRunning: false,
    latestResponseStale: true,
  },
}, {}, {});

assert.equal(ui.status, 'mt5_bridge_no_responde_o_no_esta_activo');
assert.equal(ui.className, 'bad');
assert.equal(ui.canApply, false);
assert.equal(window.SQXEdgeMt5Auto2.auto9HealthPollStopVersion, 'sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1');
assert.equal(window.SQXEdgeMt5Auto2.auto9SingleClickUxVersion, 'sqx144-mt5-auto9-datamanager-single-click-ux-v1');
assert.equal(window.SQXEdgeMt5Auto2.auto9CheckedRowSelectionVersion, 'sqx144-mt5-auto9c-datamanager-checked-row-selection-v1');
assert.equal(window.SQXEdgeMt5Auto2.auto9VisualEsSelectionVersion, 'sqx144-mt5-auto9c-visual-es-selection-v1');
assert.equal(window.SQXEdgeMt5Auto2.auto9DataSymbolPriorityVersion, 'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1');
assert.equal(
  window.SQXEdgeMt5Auto2.visualMessage('checked_row_required_for_mt5_bridge'),
  'Marca una unica fila con el check antes de usar MT5 Bridge.',
);
assert.equal(
  window.SQXEdgeMt5Auto2.candidateFromDataRowText('AUDCAD AUDCAD_Darwinex AUDCAD_dukascopy'),
  'AUDCAD_dukascopy',
  'AUTO9D should prefer the checked data symbol suffix over the linked Darwinex instrument and bare underlying',
);
assert.equal(window.SQXEdgeMt5Auto2.detectCheckedRowSymbol(), 'NASDAQ_Darwinex');
assert.equal(window.SQXEdgeMt5Auto2.detectSymbol({ allowLast: false }), 'NASDAQ_Darwinex');
const checkedState = window.SQXEdgeMt5Auto2.checkedRowSelectionState();
assert.equal(checkedState.ok, true);
assert.equal(checkedState.count, 1);
assert.equal(checkedState.status, 'checked_row_selection_ready');
assert.equal(checkedState.symbol, 'NASDAQ_Darwinex');
assert.equal(checkedState.linkedInstrument, 'NDX_Darwinex');
const blankCheckedRow = visibleNode('');
blankCheckedRow.tagName = 'TR';
blankCheckedRow.parentElement = document.body;
blankCheckedRow.getAttribute = () => '';
blankCheckedRow.getBoundingClientRect = () => ({ top: 200, height: 20 });
const blankCheckedBox = {
  value: '',
  parentElement: blankCheckedRow,
  closest: () => blankCheckedRow,
  getBoundingClientRect: () => ({ top: 205, height: 10 }),
};
const geometryCell = visibleNode('DAX40_darwinex GDAXI_darwinex');
geometryCell.getBoundingClientRect = () => ({ top: 200, height: 20 });
checkedBoxes = [blankCheckedBox];
geometryCells = [geometryCell];
const geometryState = window.SQXEdgeMt5Auto2.checkedRowSelectionState();
assert.equal(geometryState.ok, true, 'AUTO9C should resolve symbol from same-row visual cells when checkbox pane has no text');
assert.equal(geometryState.status, 'checked_row_selection_ready');
assert.equal(geometryState.symbol, 'DAX40_Darwinex');
assert.equal(geometryState.linkedInstrument, 'GDAXI_Darwinex');
geometryCells = [];
const dukascopyBlankRow = visibleNode('');
dukascopyBlankRow.tagName = 'TR';
dukascopyBlankRow.parentElement = document.body;
dukascopyBlankRow.getAttribute = () => '';
dukascopyBlankRow.getBoundingClientRect = () => ({ top: 260, height: 20 });
const dukascopyCheckedBox = {
  value: '',
  parentElement: dukascopyBlankRow,
  closest: () => dukascopyBlankRow,
  getBoundingClientRect: () => ({ top: 265, height: 10 }),
};
const dukascopyBareCell = visibleNode('AUDCAD');
dukascopyBareCell.getBoundingClientRect = () => ({ top: 260, height: 20 });
const dukascopyLinkedCell = visibleNode('AUDCAD_Darwinex');
dukascopyLinkedCell.getBoundingClientRect = () => ({ top: 260, height: 20 });
const dukascopyDataCell = visibleNode('AUDCAD_dukascopy');
dukascopyDataCell.getBoundingClientRect = () => ({ top: 260, height: 20 });
checkedBoxes = [dukascopyCheckedBox];
geometryCells = [dukascopyBareCell, dukascopyLinkedCell, dukascopyDataCell];
const dukascopyState = window.SQXEdgeMt5Auto2.checkedRowSelectionState();
assert.equal(dukascopyState.ok, true, 'AUTO9D should resolve a single checked dukascopy data row from split visual cells');
assert.equal(dukascopyState.symbol, 'AUDCAD_dukascopy');
assert.equal(dukascopyState.linkedInstrument, 'AUDCAD_Darwinex');
assert.equal(window.SQXEdgeMt5Auto2.isDukascopyMirrorSymbol(dukascopyState.symbol), true);
geometryCells = [];
checkedBoxes = [];
selectedNodes = [visibleNode('AUDCAD_darwinex AUDCAD_darwinex')];
assert.equal(window.SQXEdgeMt5Auto2.checkedRowSelectionState().status, 'checked_row_required_for_mt5_bridge');
fetchCalls = [];
window.SQXEdgeMt5Auto2.requestBridge('AUDCAD_Darwinex');
assert.equal(fetchCalls.length, 0, 'AUTO9C must not request with visual-only selection');
checkedBoxes = [checkedBox, secondCheckedBox];
assert.equal(window.SQXEdgeMt5Auto2.checkedRowSelectionState().status, 'multiple_checked_rows_blocked_for_mt5_bridge');
fetchCalls = [];
window.SQXEdgeMt5Auto2.requestBridge('NASDAQ_Darwinex');
assert.equal(fetchCalls.length, 0, 'AUTO9C must not request with multiple checked rows');
checkedBoxes = [checkedBox];
fetchCalls = [];
window.SQXEdgeMt5Auto2.requestBridge('AUDCAD_Darwinex');
assert.equal(fetchCalls.length, 0, 'AUTO9C must not request when explicit symbol mismatches the checked row');
checkedBoxes = [];
const applyWithoutCheck = await window.SQXEdgeMt5Auto2.applyChanges();
assert.equal(applyWithoutCheck.status, 'checked_row_required_for_mt5_bridge');
assert.equal(window.SQXEdgeMt5Auto2.shouldStopPollingForBridgeHealth({
  status: 'waiting_for_requested_response',
  bridgeHealth: {
    panelStatus: 'mt5_bridge_no_responde_o_no_esta_activo',
    severity: 'bad',
  },
}), true);
assert.equal(window.SQXEdgeMt5Auto2.shouldStopPollingForBridgeHealth({
  status: 'waiting_for_requested_response',
}), false);
assert.equal(window.SQXEdgeMt5Auto2.healthWatchdogContract.autoStartAllowed, false);
assert.equal(window.SQXEdgeMt5Auto2.healthWatchdogContract.launchesMt5, false);
assert.equal(window.SQXEdgeMt5Auto2.healthWatchdogContract.runsMt5Ea, false);
checkedBoxes = [dukascopyCheckedBox];
geometryCells = [dukascopyBareCell, dukascopyLinkedCell, dukascopyDataCell];
fetchCalls = [];
window.SQXEdgeMt5Auto2.requestBridge('AUDCAD_dukascopy');
assert.ok(fetchCalls.some((url) => url.includes('/mt5-auto7/plan')), 'AUTO9D should route *_dukascopy checked rows to AUTO7 mirror');
assert.ok(!fetchCalls.some((url) => url.includes('/mt5-auto2/request')), 'AUTO9D must not request MT5 for *_dukascopy checked rows');

console.log('sqx144 mt5 auto9 health watchdog contracts ok');
