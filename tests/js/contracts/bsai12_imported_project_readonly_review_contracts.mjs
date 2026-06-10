import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai12_imported_project_review.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai_imported_project_review.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI12_IMPORTED_PROJECT_READONLY_REVIEW.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'review')",
  'bs-ai12-imported-project-readonly-review-v1',
  'core.bsai_imported_project_review',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI12 wrapper marker missing: ${marker}`);
});

[
  'BS_AI12_IMPORTED_PROJECT_REVIEW_VERSION',
  'EXPECTED_IMPORTED_TASKS = 14',
  'taskmanager/listProjects',
  'imported_project_readonly_review_passed_with_methodology_warnings_no_start',
  'projectStartAllowed',
  'projectStartRequested',
  'runsSqxTasks',
  'writesDataDb',
  'writesUserProjects',
  'mutatesDatabanks',
  'officialBlocksettingsPromotion',
  'BS-AI13 first manual Start gate requires explicit operator approval',
  'bsai12_privacy_guard_failed',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI12 core marker missing: ${marker}`);
});

[
  'taskmanager/openProject',
  'project/start',
  'loadAsIs',
  'Start-Process',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Add missing symbols',
  'Migration Tool allowed',
  'run_project',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI12 wrapper must not contain ${forbidden}`);
});

[
  doc,
  readme,
  governance,
  trace,
  changelog,
  manifest,
].forEach((content, index) => {
  [
    'bs-ai12-imported-project-readonly-review-v1',
    'imported_project_readonly_review_passed_with_methodology_warnings_no_start',
    'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1',
    'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2',
    'tasks=14',
    'strategies=0',
    'hasUnresolvedResources=false',
    'BS-AI13 first manual Start gate requires explicit operator approval',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI12 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI12 ran SQX tasks',
  'BS-AI12 pressed Start',
  'BS-AI12 promoted BSAI',
  'BS-AI12 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI12 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai12 imported project readonly review contracts ok');
