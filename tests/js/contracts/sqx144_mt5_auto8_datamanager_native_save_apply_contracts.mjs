import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const overlayPath = path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js');
const installerPath = path.join(repoRoot, 'tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1');
const overlay = fs.readFileSync(overlayPath, 'utf8');
const installer = fs.readFileSync(installerPath, 'utf8');

[
  'AUTO8_NATIVE_SAVE_VERSION',
  'sqx144-mt5-auto8-datamanager-native-save-apply-v1',
  'AUTO8_UX_STATUS_VERSION',
  'sqx144-mt5-auto8-datamanager-native-save-ux-status-v1',
  'applyViaNativeDataManagerSave',
  'nativeSaveUiState',
  'nativeDataManagerSaveAllowed',
  'sqxOpenNativeSaveAllowed',
  'directDbWriteAllowed',
  'directDbHistoryInsertAllowed',
  'historyImportAllowed',
  'usesDataSourceHistoryImport',
  'apply_completed_live_native_datamanager_save',
  'listo_para_aplicar_en_data_manager',
  'sin_cambios_en_data_manager',
  'Listo para aplicar en Data Manager.',
  'Sin cambios en Data Manager.',
  '/instruments/editInstrument',
  'sqx-edge-mt5-auto8-apply',
  'Aplicar cambios',
].forEach((marker) => {
  assert.ok(overlay.includes(marker), `AUTO8 overlay marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto8-datamanager-native-save-ux-status-v1',
  'sqx144-mt5-auto8-datamanager-native-save-apply-v1',
  'auto8_datamanager_native_save_ux_status_source_ready_no_install_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import',
  'auto8_datamanager_native_save_ux_status_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import',
  'APRUEBO SQX144 MT5 AUTO8 DATAMANAGER UX STATUS INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool',
  'auto8_datamanager_native_save_apply_source_ready_no_install_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import',
  'auto8_datamanager_native_save_apply_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import',
  'native_save_apply_only no_direct_db no_history_import no_projects_no_databanks_no_tasks no_mt5 no_migration_tool',
  'Test-SourceHasAuto8NativeSave',
  'Test-TargetHasAuto8NativeSave',
  'Test-SourceHasAuto8UxStatus',
  'Test-TargetHasAuto8UxStatus',
  'nativeDataManagerSaveAllowed = $true',
  'sqxOpenNativeSaveAllowed = $true',
  'directDbWriteAllowed = $false',
  'directDbHistoryInsertAllowed = $false',
  'historyImportAllowed = $false',
  'usesDataSourceHistoryImport = $false',
].forEach((marker) => {
  assert.ok(installer.includes(marker), `AUTO8 installer marker missing: ${marker}`);
});

[
  '/api/sqx144/mt5-auto7/apply',
  '/sqx144/mt5-auto7/apply',
  '/api/sqx144/mt5-auto5/apply',
  '/sqx144/mt5-auto5/apply',
  '/api/sqx144/mt5-auto7/backup',
  '/api/sqx144/mt5-auto7/rollback',
  'DataSourceMt5Api/importData',
  'dataSourceMt5Api/importData',
  'bridge_csv_file_mass_import',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'Add missing symbols',
  'Migration Tool allowed',
  'user/projects',
].forEach((forbidden) => {
  assert.ok(!overlay.includes(forbidden), `AUTO8 overlay must not contain ${forbidden}`);
  assert.ok(!installer.includes(forbidden), `AUTO8 installer must not contain ${forbidden}`);
});

function visibleNode(text, controls = []) {
  return {
    textContent: text,
    offsetWidth: 100,
    offsetHeight: 20,
    className: '',
    innerHTML: '',
    value: '',
    selectedOptions: [],
    parentNode: null,
    parentElement: null,
    getClientRects: () => [{}],
    querySelectorAll(selector) {
      if (selector === 'input') return controls.filter((control) => control.kind === 'input');
      if (selector === 'select') return controls.filter((control) => control.kind === 'select');
      return [];
    },
    contains: () => false,
    addEventListener: () => {},
    appendChild: () => {},
  };
}

function makeSandbox(planResponse) {
  const panel = visibleNode('');
  const body = visibleNode('');
  const close = visibleNode('');
  const refresh = visibleNode('');
  const apply = visibleNode('');
  const ids = new Map([
    ['sqx-edge-mt5-auto2-panel', panel],
    ['sqx-edge-mt5-auto2-body', body],
    ['sqx-edge-mt5-auto2-close', close],
    ['sqx-edge-mt5-auto2-refresh', refresh],
    ['sqx-edge-mt5-auto8-apply', apply],
  ]);
  const constants = {
    instruments: [
      {
        instrument: 'EURGBP_dukascopy',
        broker: 4,
        dataType: 3,
        description: 'Currency',
        defaultSpread: 0.7,
        pointValue: 129994,
        tickSize: 0.0001,
        tickStep: 0.00001,
        defaultSlippage: 0,
        orderSizeMultiplier: 1,
        orderSizeStep: 0.01,
        commissions: '<Method type="None" use="true"><Params/></Method>',
        swap: '<Swap use="false" type="money" long="0" short="0" />',
      },
    ],
  };
  const nativeSaveCalls = [];
  const fetchCalls = [];
  const checkboxRow = visibleNode('EURGBP_dukascopy EURGBP_darwinex');
  const checkedBox = {
    tagName: 'INPUT',
    value: '',
    className: '',
    parentNode: checkboxRow,
    parentElement: checkboxRow,
    getAttribute: () => '',
    closest: () => checkboxRow,
  };
  const injector = {
    get(name) {
      if (name === 'SQConstants') return { getConstants: () => constants };
      if (name === 'BackendService') {
        return {
          getPromise(url, payload) {
            nativeSaveCalls.push({ url, payload });
            return Promise.resolve({ success: true, data: { success: 'Instrument modified' } });
          },
        };
      }
      if (name === '$rootScope') return { showSuccess: () => {} };
      return null;
    },
  };
  const document = {
    readyState: 'loading',
    body: visibleNode('body'),
    getElementById: (id) => ids.get(id) || null,
    addEventListener: () => {},
    createElement: () => visibleNode('created'),
    querySelectorAll: (selector) => (selector === "input[type='checkbox']:checked" ? [checkedBox] : []),
  };
  const angularModule = { config: () => angularModule, controller: () => angularModule };
  const window = {
    document,
    setInterval: () => 0,
    setTimeout: () => 0,
    getComputedStyle: () => ({ display: 'block', visibility: 'visible', opacity: '1' }),
    fetch: async (url, options = {}) => {
      fetchCalls.push({ url: String(url), options });
      return { ok: true, status: 200, json: async () => planResponse };
    },
    angular: {
      module: () => angularModule,
      element: () => ({ injector: () => injector }),
      copy: (value) => JSON.parse(JSON.stringify(value)),
    },
  };
  window.window = window;
  window.URL = URL;
  return { window, fetchCalls, nativeSaveCalls };
}

const changedPlan = {
  ok: true,
  status: 'plan_ready_apply_native_save',
  planId: 'auto7_mirror_test',
  dataSymbol: 'EURGBP_dukascopy',
  linkedInstrument: 'EURGBP_darwinex',
  sourceInstrument: 'EURGBP_darwinex',
  targetInstrument: 'EURGBP_dukascopy',
  mirrorPolicy: 'dukascopy_copies_darwinex_sibling_metadata',
  warnings: ['dukascopy_metadata_mirror_requires_separate_exact_gate'],
  changes: {
    DEFAULTSPREAD: { old: 0.7, new: 0.5 },
    POINTVALUE: { old: 129994, new: 129882 },
    TICKSIZE: { old: 0.0001, new: 0.0001 },
  },
};

const changed = makeSandbox(changedPlan);
vm.runInNewContext(overlay, changed.window, { filename: 'sqx-edge-mt5-auto2.js' });
changed.window.SQXEdgeMt5Auto2.requestBridge('EURGBP_dukascopy');
for (let i = 0; i < 8; i += 1) await Promise.resolve();
assert.equal(changed.window.SQXEdgeMt5Auto2.nativeSaveUiState(changedPlan, {}, {}).status, 'plan_ready_apply_native_save');
assert.ok(changed.window.document.getElementById('sqx-edge-mt5-auto2-body').innerHTML.includes('Listo para aplicar en Data Manager.'));
assert.ok(!changed.window.document.getElementById('sqx-edge-mt5-auto2-body').innerHTML.includes('dukascopy_metadata_mirror_requires_separate_exact_gate'));
const applied = await changed.window.SQXEdgeMt5Auto2.applyChanges();
for (let i = 0; i < 8; i += 1) await Promise.resolve();

assert.equal(applied.status, 'apply_completed_live_native_datamanager_save');
assert.equal(changed.nativeSaveCalls.length, 1, 'changed mirror plan must call native SQX save once');
assert.equal(changed.nativeSaveCalls[0].url, '/instruments/editInstrument');
assert.equal(changed.nativeSaveCalls[0].payload.instrument, 'EURGBP_dukascopy');
assert.equal(changed.nativeSaveCalls[0].payload.defaultSpread, 0.5);
assert.equal(changed.nativeSaveCalls[0].payload.pointValue, 129882);
assert.equal(changed.nativeSaveCalls[0].payload.tickSize, 0.0001);
assert.equal(changed.nativeSaveCalls[0].payload.broker, 4, 'native payload must preserve broker');
assert.ok(changed.fetchCalls.every((call) => !call.url.includes('/apply')), 'AUTO8 must not call local apply endpoints');

const noopPlan = {
  ok: true,
  status: 'plan_ready_noop_data_symbol_uses_darwinex_instrument',
  dataSymbol: 'EURGBP_dukascopy',
  linkedInstrument: 'EURGBP_darwinex',
  warnings: ['dukascopy_data_symbol_already_uses_darwinex_instrument'],
  changes: {},
  noops: { DEFAULTSPREAD: 0.7, POINTVALUE: 129994 },
};
const noop = makeSandbox(noopPlan);
vm.runInNewContext(overlay, noop.window, { filename: 'sqx-edge-mt5-auto2.js' });
noop.window.SQXEdgeMt5Auto2.requestBridge('EURGBP_dukascopy');
for (let i = 0; i < 8; i += 1) await Promise.resolve();
assert.equal(noop.window.SQXEdgeMt5Auto2.nativeSaveUiState(noopPlan, {}, {}).status, 'plan_ready_noop_data_symbol_uses_darwinex_instrument');
assert.ok(noop.window.document.getElementById('sqx-edge-mt5-auto2-body').innerHTML.includes('Sin cambios en Data Manager.'));
assert.ok(noop.window.document.getElementById('sqx-edge-mt5-auto2-body').innerHTML.includes('disabled="disabled"'));
assert.ok(!noop.window.document.getElementById('sqx-edge-mt5-auto2-body').innerHTML.includes('dukascopy_data_symbol_already_uses_darwinex_instrument'));
const noopApplied = await noop.window.SQXEdgeMt5Auto2.applyChanges();

assert.equal(noopApplied.status, 'apply_noop_no_changes');
assert.equal(noop.nativeSaveCalls.length, 0, 'noop mirror plan must not call native save');

console.log('sqx144 mt5 auto8 datamanager native save apply contracts ok');
