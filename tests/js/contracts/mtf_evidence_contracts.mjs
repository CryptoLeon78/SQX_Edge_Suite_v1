import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const mtfEvidenceJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/mtf-evidence.js'), 'utf8');
const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const mainJs = fs.readFileSync(path.join(repoRoot, 'app/js/main.js'), 'utf8');
const serverPy = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const mtfEvidencePy = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/mtf_evidence.py'), 'utf8');

for (const exportName of [
  'apiBase',
  'endpoint',
  'fetchEvidence',
  'refreshEvidence',
  'renderEvidence',
  'setStatus',
  'statusClass',
  'updatePriorityStrip',
]) {
  assert.ok(mtfEvidenceJs.includes(exportName), `${exportName} should be exported by mtf evidence module`);
}

for (const elementId of [
  'mtf-evidence-panel',
  'mtf-evidence-refresh-btn',
  'mtf-evidence-tf-count',
  'mtf-evidence-asset-count',
  'mtf-evidence-covered-count',
  'mtf-evidence-status',
  'priority-source-current',
  'priority-source-note',
]) {
  assert.ok(html.includes(`id="${elementId}"`), `${elementId} should exist in dashboard html`);
}

assert.ok(mtfEvidenceJs.includes("SQX.registerModule('mtf-evidence'"));
assert.ok(mtfEvidenceJs.includes('/mtf/evidence'));
assert.ok(mtfEvidenceJs.includes("payload.available && payload.status === 'GO'"));
assert.ok(mainJs.includes('window.SQX.mtfEvidence.init()'));
assert.ok(serverPy.includes('/api/mtf/evidence'));
assert.ok(serverPy.includes('build_mtf_evidence'));
assert.ok(mtfEvidencePy.includes('read_only_after_a56_go'));
assert.ok(mtfEvidencePy.includes('a56_real_mtf_pipeline_run.json'));

console.log('mtf evidence contracts ok');
