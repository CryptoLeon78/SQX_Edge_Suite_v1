import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

class ClassList {
  constructor(initial = []) {
    this.values = new Set(initial);
  }
  add(...names) {
    names.forEach(name => this.values.add(name));
  }
  remove(...names) {
    names.forEach(name => this.values.delete(name));
  }
  contains(name) {
    return this.values.has(name);
  }
}

class Element {
  constructor(id, classes = [], dataset = {}) {
    this.id = id;
    this.classList = new ClassList(classes);
    this.dataset = dataset;
    this.listeners = {};
    this.style = { display: '', width: '' };
    this.textContent = '';
    this.innerHTML = '';
    this.checked = false;
    this.tagName = '';
    this.type = '';
  }
  addEventListener(type, handler) {
    this.listeners[type] = this.listeners[type] || [];
    this.listeners[type].push(handler);
  }
  click() {
    (this.listeners.click || []).forEach(handler => handler({ target: this }));
  }
  dispatch(type, event = { target: this }) {
    (this.listeners[type] || []).forEach(handler => handler(event));
  }
}

class FakeDocument {
  constructor() {
    this.elements = new Map();
    this.tabs = [];
    this.panels = [];
  }
  add(element) {
    this.elements.set(element.id, element);
    return element;
  }
  addTab(id, active = false) {
    const tab = this.add(new Element(`tab-btn-${id}`, ['tab'].concat(active ? ['active'] : []), { tab: id }));
    const panel = this.add(new Element(`tab-${id}`, ['tab-content']));
    panel.style.display = active ? 'block' : 'none';
    this.tabs.push(tab);
    this.panels.push(panel);
    return { tab, panel };
  }
  getElementById(id) {
    return this.elements.get(id) || null;
  }
  querySelector(selector) {
    if (selector.startsWith('.tab[data-tab="')) {
      const id = selector.match(/data-tab="([^"]+)"/)[1];
      return this.tabs.find(tab => tab.dataset.tab === id) || null;
    }
    if (selector.includes('.tab.active')) {
      return this.tabs.find(tab => tab.classList.contains('active')) || null;
    }
    return this.querySelectorAll(selector)[0] || null;
  }
  querySelectorAll(selector) {
    if (selector === '.tab') return this.tabs;
    if (selector === '.tab-content') return this.panels;
    if (selector === '.subtab') {
      return Array.from(this.elements.values()).filter(el => el.classList.contains('subtab'));
    }
    if (selector === '.subtab-content') {
      return Array.from(this.elements.values()).filter(el => el.classList.contains('subtab-content'));
    }
    if (selector === '[data-home-tab]') {
      return Array.from(this.elements.values()).filter(el => el.dataset.homeTab);
    }
    if (selector.startsWith('[data-filter-type]')) {
      return Array.from(this.elements.values()).filter(el => el.dataset.filterType);
    }
    if (selector === 'input[type="checkbox"][data-check]') {
      return Array.from(this.elements.values()).filter(el => el.tagName === 'input' && el.type === 'checkbox' && el.dataset.check);
    }
    if (selector === 'button[data-checklist-clear]') {
      return Array.from(this.elements.values()).filter(el => el.tagName === 'button' && el.dataset.checklistClear);
    }
    const checkPrefix = selector.match(/^input\[type="checkbox"\]\[data-check\^="([^"]+)"\]$/);
    if (checkPrefix) {
      return Array.from(this.elements.values()).filter(el => el.tagName === 'input' && el.type === 'checkbox' && (el.dataset.check || '').startsWith(checkPrefix[1]));
    }
    return [];
  }
}

function createSandbox() {
  const document = new FakeDocument();
  const store = new Map();
  const sandbox = {
    console,
    document,
    localStorage: {
      getItem: key => store.has(key) ? store.get(key) : null,
      setItem: (key, value) => store.set(key, String(value)),
      removeItem: key => store.delete(key),
    },
    SQX_CONFIG: { storageKeys: {} },
    SQX: {
      modules: {},
      registerModule(name, module) {
        this.modules[name] = module;
      },
      utils: {
        safeJsonParse(raw, fallback) {
          try { return JSON.parse(raw); } catch (_err) { return fallback; }
        }
      }
    }
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  return sandbox;
}

function loadModule(context, relativePath) {
  const fullPath = path.join(repoRoot, relativePath);
  const code = fs.readFileSync(fullPath, 'utf8');
  vm.runInContext(code, context, { filename: fullPath });
}

const sandbox = createSandbox();
const context = vm.createContext(sandbox);
[
  'app/js/modules/formatters.js',
  'app/js/modules/domain.js',
  'app/js/modules/storage.js',
  'app/js/modules/ui.js',
  'app/js/modules/strategies.js',
  'app/js/modules/home.js',
  'app/js/modules/workflow.js',
  'app/js/modules/project-generator.js',
].forEach(file => loadModule(context, file));

const { SQX, document } = sandbox;

assert.equal(SQX.formatters.ratingLabel('++').text, 'Estrella');
assert.equal(SQX.formatters.metricClass('PF', 1.6), 'pos');
assert.equal(SQX.formatters.formatNumber('12.345', 1), '12.3');
assert.equal(SQX.formatters.escapeHtml('<x>'), '&lt;x&gt;');

const asset = {
  cats: {
    tendencia: { rating: '++', dir: 'L' },
    momentum: { rating: '+', dir: 'S' },
  }
};
const score = SQX.domain.calcScore(asset, 'all', { '++': 3, '+': 2, '~': 1, '-': 0 });
assert.equal(score.raw, 5);
assert.equal(score.count, 2);
assert.equal(score.norm, 83);
assert.equal(SQX.domain.assetMatchesSqxFilter({ cats: { trend: { dir: 'L' } } }, 'C'), true);
assert.equal(SQX.domain.tfMatch('M15,H1', 'H1'), true);

const manual = SQX.strategies.manualStrategyFromValues({
  id: '17.000001',
  name: 'EMA + MACD',
  mining: '17',
  asset: 'EURUSD',
  tf: 'H1',
  blocksetting: 'BS_Tendencia',
  template: 'PHASE17',
  direction: 'L',
  indicators: 'EMA, MACD',
  exits: 'ATR',
  netProfit: '1234.56',
  trades: '222',
  testsPassed: 'OOS, Forward',
  testsFailed: '',
  tier: '1',
  status: 'CANDIDATA',
}, '2026-05-04');
assert.equal(manual.metrics.net_profit, 1234.56);
assert.equal(manual.metrics.trades, 222);
assert.equal(manual.tests_passed.length, 2);
assert.equal(manual.tests_passed[0], 'OOS');
assert.equal(manual.tests_passed[1], 'Forward');

const baseStrategy = { id: 'A', mining: 1, template: 'T', asset: 'EURUSD', tf: 'H1', metrics: {}, tests_passed: [], tests_failed: [] };
const imported = { id: 'B', mining: 1, template: 'T', asset: 'EURUSD', tf: 'H1', metrics: {}, tests_passed: [], tests_failed: [], _imported: true, _import_id: 'tmp' };
const dedupe = SQX.strategies.dedupeImportedStrategies([baseStrategy], [], [baseStrategy, imported]);
assert.equal(dedupe.fresh.length, 1);
assert.equal(dedupe.duplicates, 1);
const csvRows = SQX.strategies.exportCsvRows([imported]);
assert.equal(csvRows.length, 2);
assert.match(csvRows[1], /"IMPORTED"$/);
const consolidated = SQX.strategies.consolidateJson([imported]);
assert.equal(JSON.parse(consolidated).strategies[0]._imported, undefined);

document.addTab('inicio', true);
document.addTab('pipeline', false);
assert.equal(SQX.ui.activateTabById('pipeline', document), true);
assert.equal(document.querySelector('.tab.active[data-tab]').dataset.tab, 'pipeline');

const filterA = document.add(new Element('filter-all', ['filter-btn', 'active'], { filterType: 'all' }));
const filterB = document.add(new Element('filter-forex', ['filter-btn'], { filterType: 'forex' }));
let selectedFilter = null;
let callbackCount = 0;
SQX.ui.bindButtonGroup('[data-filter-type]', 'filterType', value => { selectedFilter = value; }, () => { callbackCount += 1; }, document);
filterB.click();
assert.equal(selectedFilter, 'forex');
assert.equal(callbackCount, 1);
assert.equal(filterA.classList.contains('active'), false);
assert.equal(filterB.classList.contains('active'), true);

[
  'home-assets-count', 'home-assets-sub', 'home-minings-count', 'home-plan-sub',
  'home-strategies-count', 'home-strategies-sub', 'home-priority-count',
  'home-next-action', 'home-backend-status', 'home-data-status',
  'home-readiness-score', 'home-hero-status', 'home-audit-score',
  'home-readiness-bar', 'home-check-manifest', 'home-check-plan',
  'home-check-strategies', 'home-check-backend', 'home-audit-manifest',
  'home-audit-manifest-detail', 'home-audit-plan', 'home-audit-plan-detail',
  'home-audit-backend', 'home-audit-backend-detail', 'home-audit-templates',
  'home-audit-templates-detail', 'home-audit-sqx', 'home-audit-sqx-detail',
  'home-audit-output', 'home-audit-output-detail'
].forEach(id => document.add(new Element(id)));

const model = SQX.home.computeHomeModel({
  assets: [{ type: 'forex' }, { type: 'index' }, { type: 'oro' }],
  planMinings: [{ num: 1 }],
  strategies: [baseStrategy],
  strategiesUser: [imported],
  priorityProgress: { one: {} },
  pipelineState: { nextAction: 'A'.repeat(100) },
  phaseMeta: { 1: {} },
  backendState: { state: 'up', title: 'API OK', meta: { version: '17', templates_capa1_exists: true, templates_capa2_exists: true, sqx_path_set: true, output_dir: 'out', output_dir_exists: true } },
  manifestVersion: 17,
  catKeys: ['trend']
});
assert.equal(model.readiness, 100);
assert.equal(model.auditScore, '6/6');
assert.equal(model.nextAction.endsWith('...'), true);
SQX.home.applyHomeModel(model, document);
assert.equal(document.getElementById('home-readiness-score').textContent, '100%');
assert.equal(document.getElementById('home-audit-score').textContent, '6/6');
assert.equal(document.getElementById('home-readiness-bar').style.width, '100%');

const trace = SQX.home.addTrace([], SQX.home.createTraceItem('Phase 17', 'contracts', 'ok', new Date('2026-05-04T12:00:00Z')), 12);
assert.match(SQX.home.traceHtml(trace), /Phase 17/);

const wfA = document.add(new Element('wf-main', ['subtab', 'active'], { subtab: 'wf-main-panel' }));
const wfB = document.add(new Element('wf-rules-tab', ['subtab'], { subtab: 'wf-rules-panel' }));
const wfMainPanel = document.add(new Element('wf-main-panel', ['subtab-content', 'active']));
const wfRulesPanel = document.add(new Element('wf-rules-panel', ['subtab-content']));
assert.equal(SQX.workflow.bindSubtabs({ document }), 2);
wfB.click();
assert.equal(wfA.classList.contains('active'), false);
assert.equal(wfB.classList.contains('active'), true);
assert.equal(wfMainPanel.classList.contains('active'), false);
assert.equal(wfRulesPanel.classList.contains('active'), true);

const boxC1 = document.add(new Element('check-c1-a', [], { check: 'capa1-a' }));
boxC1.tagName = 'input';
boxC1.type = 'checkbox';
const boxC2 = document.add(new Element('check-c2-a', [], { check: 'capa2-a' }));
boxC2.tagName = 'input';
boxC2.type = 'checkbox';
const clearC1 = document.add(new Element('clear-c1', [], { checklistClear: 'capa1' }));
clearC1.tagName = 'button';
const writes = [];
const checklist = SQX.workflow.bindChecklist({
  document,
  key: 'workflow-test',
  storage: {
    getJson: () => ({ 'capa1-a': true, 'capa2-a': true }),
    setJson: (_key, value) => { writes.push(Object.assign({}, value)); return true; },
  },
  confirm: () => true,
});
assert.equal(checklist.checkboxCount, 2);
assert.equal(checklist.clearCount, 1);
assert.equal(boxC1.checked, true);
boxC2.checked = false;
boxC2.dispatch('change', { target: boxC2 });
assert.equal(writes[writes.length - 1]['capa2-a'], undefined);
clearC1.click();
assert.equal(boxC1.checked, false);
assert.equal(writes[writes.length - 1]['capa1-a'], undefined);

assert.equal(SQX.projectGenerator.escapeHtml('<x>'), '&lt;x&gt;');
const pgApiState = SQX.projectGenerator.computeOnboardingState({
  apiBase: 'http://127.0.0.1:8765',
  connected: false,
  configState: {},
  healthMeta: {},
  minings: [],
  outputFiles: [],
});
assert.equal(pgApiState.completed, 0);
assert.equal(pgApiState.current.id, 'api');
assert.equal(pgApiState.tertiaryVisible, false);

const pgReadyState = SQX.projectGenerator.computeOnboardingState({
  apiBase: 'http://127.0.0.1:8765',
  connected: true,
  configState: { sqx_path: 'C:/SQX', sqx_data_db: 'C:/SQX/data.db' },
  healthMeta: {
    data_db_exists: true,
    output_dir: 'out',
    output_dir_exists: true,
    sqx_path: 'C:/SQX',
    sqx_path_set: true,
    templates_capa1_exists: true,
    templates_capa2_exists: true,
  },
  minings: [{ asset: 'EURUSD', tf: 'H1' }],
  outputFiles: [{ name: 'M01.cfx' }],
});
assert.equal(pgReadyState.completed, 4);
assert.equal(pgReadyState.current, null);
assert.equal(pgReadyState.tertiaryAction, 'refresh');

[
  'pg-onboarding-progress', 'pg-onboarding-title', 'pg-onboarding-desc',
  'pg-onboarding-bar', 'pg-onboarding-steps', 'pg-onboarding-action',
  'pg-onboarding-secondary', 'pg-onboarding-tertiary', 'pg-assistant-next',
  'pg-assistant-hint', 'pg-assistant-checks'
].forEach(id => document.add(new Element(id)));
assert.equal(SQX.projectGenerator.applyOnboardingState(pgReadyState, document), true);
assert.equal(document.getElementById('pg-onboarding-progress').textContent, '4/4');
assert.equal(document.getElementById('pg-onboarding-bar').style.width, '100%');
assert.equal(document.getElementById('pg-onboarding-tertiary').dataset.pgAssistantAction, 'refresh');
assert.match(document.getElementById('pg-onboarding-steps').innerHTML, /pg-step done/);

const prepared = SQX.projectGenerator.prepareRequestOptions({ body: { alpha: 1 }, headers: { Accept: 'application/json' } });
assert.equal(prepared.body, '{"alpha":1}');
assert.equal(prepared.headers['Content-Type'], 'application/json');
assert.equal(prepared.headers.Accept, 'application/json');

let fetchUrl = '';
let fetchOptions = null;
const jsonResult = await SQX.projectGenerator.fetchJson('http://api.local', '/health', { method: 'POST', body: { ok: true } }, async (url, options) => {
  fetchUrl = url;
  fetchOptions = options;
  return { ok: true, status: 200, text: async () => '{"ok":true,"version":"20"}' };
});
assert.equal(fetchUrl, 'http://api.local/health');
assert.equal(fetchOptions.body, '{"ok":true}');
assert.equal(jsonResult.version, '20');

await assert.rejects(
  () => SQX.projectGenerator.fetchJson('', '/bad', {}, async () => ({ ok: false, status: 500, text: async () => 'boom' })),
  /boom/
);

document.add(new Element('pg-status-banner', ['pg-status-loading']));
document.add(new Element('pg-status-title'));
document.add(new Element('pg-status-desc'));
assert.equal(SQX.projectGenerator.applyStatusBanner({ state: 'up', title: 'API OK', desc: 'Lista' }, document), true);
assert.equal(document.getElementById('pg-status-title').textContent, 'API OK');
assert.equal(document.getElementById('pg-status-desc').textContent, 'Lista');
assert.equal(document.getElementById('pg-status-banner').classList.contains('pg-status-up'), true);
assert.equal(document.getElementById('pg-status-banner').classList.contains('pg-status-loading'), false);

const pgAssets = SQX.projectGenerator.uniqueAssets([
  { asset: 'GBPUSD' },
  { asset: 'EURUSD' },
  { asset: 'GBPUSD' },
]);
assert.equal(pgAssets.length, 2);
assert.equal(pgAssets[0], 'EURUSD');
assert.equal(pgAssets[1], 'GBPUSD');
assert.equal(SQX.projectGenerator.directionClass('short'), 'short');
assert.equal(SQX.projectGenerator.directionLabel('both'), 'L+S');
const aliasHtml = SQX.projectGenerator.aliasTableHtml([{ asset: 'EURUSD' }], { EURUSD: 'EURUSD_M1' });
assert.match(aliasHtml, /data-pg-alias="EURUSD"/);
assert.match(aliasHtml, /value="EURUSD_M1"/);
assert.match(SQX.projectGenerator.aliasTableHtml([], {}), /esperando minings/);
const miningHtml = SQX.projectGenerator.miningRowsHtml([{
  num: 7,
  asset: 'EURUSD',
  tf: 'H1',
  bs: 'BS_Tendencia',
  dir: 'long',
  _info: { source: 'db', instrument: 'EURUSD_M1', spread: 1.2, swap_long: -1, swap_short: 0.5 },
}]);
assert.match(miningHtml, /data-pg-gen="7"/);
assert.match(miningHtml, /pgm-dir long/);
assert.match(miningHtml, /EURUSD_M1/);
const outputHtml = SQX.projectGenerator.outputListHtml([{ name: 'M07.cfx', size_kb: 12, mtime: 1770000000 }]);
assert.match(outputHtml, /M07\.cfx/);
assert.match(outputHtml, /12 KB/);
assert.match(SQX.projectGenerator.outputListHtml([]), /No hay \.cfx/);

console.log('module contracts ok');
