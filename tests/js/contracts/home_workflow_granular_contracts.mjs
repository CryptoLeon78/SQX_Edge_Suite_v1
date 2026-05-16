import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document, sandbox } = createLoadedSandbox([
  'app/js/modules/home.js',
  'app/js/modules/workflow.js',
]);

assert.equal(SQX.modules.home, SQX.home);
assert.equal(SQX.modules.workflow, SQX.workflow);

assert.equal(SQX.home.escapeHtml('<x>&'), '&lt;x&gt;&amp;');
assert.equal(SQX.home.trimAction('A'.repeat(90), 12), 'AAAAAAAAA...');
const traceItem = SQX.home.createTraceItem('Title', 'Detail', 'ok', new Date('2026-05-05T10:00:00Z'));
assert.equal(traceItem.title, 'Title');
assert.equal(traceItem.level, 'ok');
assert.equal(SQX.home.addTrace([{ title: 'old' }], traceItem, 1).length, 1);
assert.match(SQX.home.traceHtml([traceItem]), /Title/);

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
  'home-audit-output', 'home-audit-output-detail',
  'remote-pro-panel', 'remote-pro-title', 'remote-pro-detail', 'remote-pro-badge',
  'remote-pro-access-item', 'remote-pro-access-status', 'remote-pro-access-detail',
  'remote-pro-workspace-item', 'remote-pro-workspace-status', 'remote-pro-workspace-detail',
  'remote-pro-server-item', 'remote-pro-server-status', 'remote-pro-server-detail',
  'remote-pro-security-item', 'remote-pro-security-status', 'remote-pro-security-detail',
  'remote-pro-privacy-item', 'remote-pro-privacy-status', 'remote-pro-privacy-detail',
  'remote-session-actions', 'remote-session-title', 'remote-session-login-detail',
  'remote-session-key-wrap', 'remote-session-grant-key', 'remote-session-login',
  'remote-pro-refresh', 'remote-session-watermark'
].forEach(id => document.add(new Element(id)));

const model = SQX.home.computeHomeModel({
  assets: [{ type: 'forex' }, { type: 'index' }],
  planMinings: [{ num: 1 }],
  strategies: [{ id: 'A' }],
  strategiesUser: [{ id: 'U' }],
  priorityProgress: { a: true, b: true },
  pipelineState: { nextAction: 'Review candidates' },
  phaseMeta: { 1: {} },
  backendState: { state: 'down', title: 'API down', meta: {} },
  catKeys: ['trend', 'momentum'],
  manifestVersion: 2,
});
assert.equal(model.readiness, 75);
assert.equal(model.auditScore, '2/6');
assert.equal(model.strategiesSub, '1 base · 1 importadas');
SQX.home.applyHomeModel(model, document);
assert.equal(document.getElementById('home-readiness-score').textContent, '75%');
assert.equal(document.getElementById('home-audit-score').textContent, '2/6');
assert.equal(document.getElementById('home-readiness-bar').style.width, '75%');
assert.equal(document.getElementById('home-check-backend').classList.contains('is-warn'), true);
assert.equal(SQX.home.apiBase(), 'http://127.0.0.1:5050/api');
assert.equal(SQX.home.shortWorkspaceId('ws_1234567890abcdef'), 'ws_1234567890a...');
const remotePending = SQX.home.computeRemoteServiceModel({
  access: { mode: 'local_only', authenticated: false, access: { allowed: false, reason: 'identity_missing' } },
  session: { session: { active: false }, access: { allowed: false, reason: 'session_missing' } },
  workspace: { ok: false, error: 'remote_session_required' },
  security: { ok: true, version: 'remote-security-v1', watermark: { enabled: false }, killSwitch: { active: false } },
  health: { ok: false },
});
assert.equal(remotePending.state, 'warn');
SQX.home.applyRemoteServiceModel(remotePending, document);
assert.equal(document.getElementById('remote-pro-access-status').textContent, 'Sin sesion remota');
assert.equal(document.getElementById('remote-pro-security-status').textContent, 'Protecciones activas');
assert.equal(document.getElementById('remote-session-watermark').hidden, true);
assert.match(document.getElementById('remote-pro-privacy-detail').textContent, /no se muestran rutas internas/);

const remoteNeedsTesterLogin = SQX.home.computeRemoteServiceModel({
  access: {
    mode: 'remote_tunnel_only',
    authenticated: true,
    access: { allowed: true, reason: 'access_allowed', feature_scope: 'full' },
    entitlement: { kind: 'tester_free', status: 'active', feature_scope: 'full', grant_key_required: true },
  },
  session: { session: { active: false }, access: { allowed: false, reason: 'session_missing' } },
  workspace: { ok: false, error: 'remote_session_required' },
  security: { ok: true, version: 'remote-security-v1', watermark: { enabled: false }, killSwitch: { active: false } },
  health: { ok: true },
});
assert.equal(remoteNeedsTesterLogin.sessionLogin.visible, true);
assert.equal(remoteNeedsTesterLogin.sessionLogin.requiresGrantKey, true);
SQX.home.applyRemoteServiceModel(remoteNeedsTesterLogin, document);
assert.equal(document.getElementById('remote-session-actions').hidden, false);
assert.equal(document.getElementById('remote-session-key-wrap').hidden, false);
assert.equal(document.getElementById('remote-session-login').textContent, 'Validar tester');

const remoteLoginRequests = [];
sandbox.fetch = (url, options = {}) => {
  remoteLoginRequests.push({ url, options });
  return Promise.resolve({
    status: 200,
    ok: true,
    json: () => Promise.resolve({ ok: true, access: { allowed: true }, privacy: { session_token_returned: false } }),
  });
};
document.getElementById('remote-session-grant-key').value = 'pilot-key';
const remoteLoginResult = await SQX.home.loginRemoteSession(document, () => Promise.resolve(remoteNeedsTesterLogin));
assert.equal(remoteLoginResult.ok, true);
assert.equal(remoteLoginRequests.length, 1);
assert.match(remoteLoginRequests[0].url, /\/remote\/session\/login$/);
assert.equal(remoteLoginRequests[0].options.method, 'POST');
assert.deepEqual(JSON.parse(remoteLoginRequests[0].options.body), { grant_key: 'pilot-key' });
assert.equal(document.getElementById('remote-session-grant-key').value, '');

const remoteActive = SQX.home.computeRemoteServiceModel({
  access: { mode: 'remote_tunnel_only', authenticated: true, access: { allowed: true, reason: 'access_allowed', feature_scope: 'full' }, entitlement: { kind: 'tester_free' } },
  session: { session: { active: true, entitlement_kind: 'tester_free' }, access: { allowed: true, reason: 'session_access_allowed', feature_scope: 'full' } },
  workspace: { ok: true, workspace: { id: 'ws_1234567890abcdef123456', version: 'remote-workspace-v1' } },
  security: { ok: true, version: 'remote-security-v1', killSwitch: { active: false }, watermark: { enabled: true, label: 'SQX REMOTE PRO', marker: 'te***@example.invalid' } },
  health: { ok: true, version: '142', sqx_path_set: true, data_db_exists: true, templates_capa1_exists: true, templates_capa2_exists: true },
});
assert.equal(remoteActive.state, 'active');
SQX.home.applyRemoteServiceModel(remoteActive, document);
assert.equal(document.getElementById('remote-pro-security-status').textContent, 'Protecciones activas');
assert.equal(document.getElementById('remote-session-watermark').hidden, false);
assert.match(document.getElementById('remote-session-watermark').textContent, /SQX REMOTE PRO/);

const tabA = document.add(new Element('wf-main-tab', ['subtab', 'active'], { subtab: 'wf-main' }));
const tabB = document.add(new Element('wf-rules-tab', ['subtab'], { subtab: 'wf-rules' }));
const panelA = document.add(new Element('wf-main', ['subtab-content', 'active']));
const panelB = document.add(new Element('wf-rules', ['subtab-content']));
assert.equal(SQX.workflow.bindSubtabs({ document }), 2);
tabB.click();
assert.equal(tabA.classList.contains('active'), false);
assert.equal(tabB.classList.contains('active'), true);
assert.equal(panelA.classList.contains('active'), false);
assert.equal(panelB.classList.contains('active'), true);
const stepDetail = document.add(new Element('wf-capa1-tree-detail', ['workflow-step-detail']));
stepDetail.hidden = true;
const stepTrigger = document.add(new Element('wf-capa1-step-trigger', ['pipeline-step'], { wfDetailTarget: 'wf-capa1-tree-detail' }));
assert.equal(SQX.workflow.bindStepDetails({ document }), 1);
stepTrigger.click();
assert.equal(stepTrigger.classList.contains('is-active'), true);
assert.equal(stepTrigger.getAttribute('aria-expanded'), 'true');
assert.equal(stepDetail.hidden, false);
stepTrigger.click();
assert.equal(stepTrigger.classList.contains('is-active'), false);
assert.equal(stepTrigger.getAttribute('aria-expanded'), 'false');
assert.equal(stepDetail.hidden, true);
const tabC = document.add(new Element('wf-capa2-tab', ['subtab'], { subtab: 'wf-capa2' }));
const panelC = document.add(new Element('wf-capa2', ['subtab-content']));
const subtabLink = document.add(new Element('wf-capa2-link', [], { workflowSubtabTarget: 'wf-capa2' }));
subtabLink.tagName = 'button';
assert.equal(SQX.workflow.bindSubtabLinks({ document }), 1);
subtabLink.click();
assert.equal(tabC.classList.contains('active'), true);
assert.equal(panelC.classList.contains('active'), true);

const writes = [];
const box = document.add(new Element('check-one', [], { check: 'capa1-alpha' }));
box.tagName = 'input';
box.type = 'checkbox';
const clear = document.add(new Element('clear-capa1', [], { checklistClear: 'capa1' }));
clear.tagName = 'button';
const checklist = SQX.workflow.bindChecklist({
  document,
  key: 'wf-key',
  storage: {
    getJson: () => ({ 'capa1-alpha': true }),
    setJson: (_key, value) => { writes.push(Object.assign({}, value)); return true; },
  },
  confirm: () => true,
});
assert.equal(checklist.key, 'wf-key');
assert.equal(checklist.checkboxCount, 1);
assert.equal(box.checked, true);
box.checked = false;
box.dispatch('change', { target: box });
assert.equal(writes[writes.length - 1]['capa1-alpha'], undefined);
box.checked = true;
box.dispatch('change', { target: box });
clear.click();
assert.equal(box.checked, false);
assert.equal(SQX.workflow.resolveChecklistKey({ storageKey: (_name, fallback) => `x-${fallback}` }, 'fallback'), 'x-fallback');
const planSummary = SQX.workflow.computePlanSummary({
  minings: [{ num: 1, phase: 1, asset: 'EURUSD', tf: 'H1' }, { num: 2, phase: 2, asset: 'GBPUSD', tf: 'M15', _user: true }],
  phases: { 1: {}, 2: {}, 3: {} },
});
assert.equal(planSummary.phaseCount, 2);
assert.equal(planSummary.miningCount, 2);
assert.equal(planSummary.assetCount, 2);
assert.equal(planSummary.userMiningCount, 1);

console.log('home workflow granular contracts ok');
