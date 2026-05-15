import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';
import fs from 'node:fs';
import path from 'node:path';

const { SQX } = createLoadedSandbox([
  'app/js/modules/modal-registry.js',
]);

assert.equal(SQX.modules['modal-registry'], SQX.modalRegistry);

const registry = SQX.modalRegistry.list();
const ids = registry.map(item => item.id);
[
  'tm-modal-audit',
  'tm-modal-c2',
  'strat-modal-backdrop',
  'strat-import-backdrop',
  'ps-add-mining-backdrop',
  'ps-add-phase-backdrop',
  'state-restore-backdrop',
  'sqx-decision-backdrop',
].forEach(id => assert.ok(ids.includes(id), `modal registry should include ${id}`));

registry.forEach(item => {
  assert.ok(item.tab, `${item.id} should declare owner tab`);
  assert.ok(item.owner, `${item.id} should declare owner module`);
  assert.ok(item.action, `${item.id} should declare action`);
  assert.ok(item.trace && item.trace.length, `${item.id} should declare visible trace fields`);
  assert.ok(item.failures && item.failures.length, `${item.id} should declare failure modes`);
});

assert.match(SQX.modalRegistry.tracePanelHtml('Trace', ['Origen', 'Destino']), /modal-trace-panel/);
assert.ok(SQX.modalRegistry.nativeDecisions().includes('reset plan mining'));

const html = fs.readFileSync(path.join(repoRoot, 'app', 'SQX_Dashboard_v6.html'), 'utf8');
assert.ok(html.indexOf('js/modules/modal-registry.js') < html.indexOf('js/modules/state-backup.js'), 'modal registry should load before state backup');
assert.match(html, /id="sqx-decision-backdrop"/);
assert.match(html, /Trazabilidad obligatoria C2/);
assert.match(html, /Alta manual trazable/);
assert.match(html, /Batch de importacion trazable/);
assert.match(html, /Alta de mining trazable/);
assert.match(html, /Fase visible aunque este vacia/);
assert.match(html, /Restore con backup previo automatico/);
assert.doesNotMatch(html, /js\/modules\/analyzer\.js/);
assert.doesNotMatch(html, /tab-analyzer/);

const dashboard = fs.readFileSync(path.join(repoRoot, 'app', 'js', 'dashboard.js'), 'utf8');
assert.match(dashboard, /function decisionConfirm/);
assert.match(dashboard, /function decisionPrompt/);
assert.match(dashboard, /function decisionAlert/);
assert.match(dashboard, /trace:\s*\[/);

console.log('modal trace contracts ok');
