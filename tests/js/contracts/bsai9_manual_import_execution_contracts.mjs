import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI9_MANUAL_IMPORT_EXECUTION.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  'bs-ai9-manual-import-execution-v1',
  'blocked_resource_resolution_modal_no_import_loaded',
  'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',
  'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx',
  'Resolve project resources',
  'AUDCAD',
  'source: `N/A`',
  'status: `Not found`',
  'action taken: `Close`',
  'dataDbShaUnchanged=true',
  'projectsFileCountUnchanged=true',
  'noBSAIInHostProjects=true',
  'noAUDCADInHostProjects=true',
  'blocked_resource_resolution_modal_closed_no_load_no_add_symbol_no_start',
  'BS-AI10 target-resource compatibility gate',
].forEach((marker) => {
  assert.ok(doc.includes(marker), `BS-AI9 doc marker missing: ${marker}`);
});

[
  [readme, 'README.md'],
  [governance, 'docs/PROJECT_GOVERNANCE.md'],
  [changelog, 'CHANGELOG.md'],
  [trace, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'],
  [manifest, 'docs/state_consistency_manifest.json'],
].forEach(([text, name]) => {
  [
    'bs-ai9-manual-import-execution-v1',
    'blocked_resource_resolution_modal_no_import_loaded',
    'Resolve project resources',
    'AUDCAD',
    'BS-AI10 target-resource compatibility gate',
  ].forEach((marker) => {
    assert.ok(text.includes(marker), `${name} missing BS-AI9 marker: ${marker}`);
  });
});

[
  'BS-AI9 imported into SQX',
  'BS-AI9 wrote data.db',
  'BS-AI9 wrote user/projects',
  'BS-AI9 mutated databanks',
  'BS-AI9 ran SQX tasks',
  'Load without resolving accepted',
  'Add missing symbols accepted',
  'Capa2 import completed',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  assert.ok(!doc.includes(forbidden), `BS-AI9 doc must not contain: ${forbidden}`);
});

console.log('bsai9 manual import execution contracts ok');
