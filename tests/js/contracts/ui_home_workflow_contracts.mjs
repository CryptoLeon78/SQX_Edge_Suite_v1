import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document } = createLoadedSandbox();
const baseStrategy = { id: 'A', mining: 1, template: 'T', asset: 'EURUSD', tf: 'H1', metrics: {}, tests_passed: [], tests_failed: [] };
const imported = { id: 'B', mining: 1, template: 'T', asset: 'EURUSD', tf: 'H1', metrics: {}, tests_passed: [], tests_failed: [], _imported: true };

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
  'home-strategies-count', 'home-strategies-sub',
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
const wfCapa2Tab = document.add(new Element('wf-capa2-tab', ['subtab'], { subtab: 'wf-capa2' }));
const wfCapa2Panel = document.add(new Element('wf-capa2', ['subtab-content']));
const wfCapa2Link = document.add(new Element('wf-capa2-link', [], { workflowSubtabTarget: 'wf-capa2' }));
wfCapa2Link.tagName = 'button';
assert.equal(SQX.workflow.bindSubtabLinks({ document }), 1);
wfCapa2Link.click();
assert.equal(wfCapa2Tab.classList.contains('active'), true);
assert.equal(wfCapa2Panel.classList.contains('active'), true);

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

console.log('ui home workflow contracts ok');
