import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const psPath = path.join(repoRoot, 'tools/sqx142_own_features_correlation_lab_project_scaffold.ps1');
const pyPath = path.join(repoRoot, 'backend/sqx-edge-tool/tools/sqx142_correlation_lab_project_scaffold.py');
const ps = fs.readFileSync(psPath, 'utf8');
const py = fs.readFileSync(pyPath, 'utf8');

assert.match(ps, /\[ValidateSet\("status", "plan", "install", "rollback"\)\]/);
assert.match(ps, /Assert-NoSqxProcess/);
assert.match(ps, /SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527/);
assert.match(ps, /sqx142_correlation_lab_project_scaffold\.py/);
assert.doesNotMatch(ps, /Stop-Process/);
assert.doesNotMatch(ps, /Start-Process/);
assert.doesNotMatch(ps, /Remove-Item/);
assert.doesNotMatch(ps, /Copy-Item/);

assert.match(py, /sqx142-own-features3b-correlation-lab-project-scaffold-v1/);
assert.match(py, /SQX EDGE CORRELATION REVIEW/);
assert.match(py, /SQX EDGE CORR TAG/);
assert.match(py, /SQXEdgeCorrelationTagger/);
assert.match(py, /Monkey Test/);
assert.match(py, /Syntetic/);
assert.match(py, /SQX EDGE CORR TAGGED/);
assert.match(py, /shutil\.copytree/);
assert.match(py, /shutil\.move/);
assert.match(py, /projects_quarantine/);
assert.doesNotMatch(py, /rmtree|unlink\(|os\.remove|Stop-Process|Start-Process/);
assert.doesNotMatch(py, /data\.db.*write|run_project permitido|Migration Tool permitido/);

console.log('sqx142 own features3b correlation lab project scaffold contracts ok');
