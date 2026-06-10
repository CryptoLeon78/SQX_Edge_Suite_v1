import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai11_remapped_import_gate.ps1'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI11_REMAPPED_MANUAL_IMPORT_GATE.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'preflight', 'snapshot', 'launch', 'capture', 'import-capa1', 'import-capa2')",
  'bs-ai11-remapped-manual-import-gate-v1',
  'taskmanager/openProject',
  "loadAsIs = 'false'",
  'loadAsIsEscalated = $false',
  'projectStartRequested = $false',
  'runsSqxTasks = $false',
  'startButtonAllowed = $false',
  'writesDataDb = $false',
  'mutatesDatabanks = $false',
  'hostUiImportMayWriteDataDb = $true',
  'hostUiImportMayWriteUserProjects = $true',
  'rawXmlStored = $false',
  'localPathsReturned = $false',
  'resourcesXmlLength',
  'configXmlLength',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI11 wrapper marker missing: ${marker}`);
});

[
  'project/start',
  "loadAsIs = 'true'",
  'loadAsIs=$true',
  'Load without resolving these issues',
  'Add missing symbols',
  'Stop-Process',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Migration Tool allowed',
  'run_project',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI11 wrapper must not contain ${forbidden}`);
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
    'bs-ai11-remapped-manual-import-gate-v1',
    'remapped_capa1_capa2_imported_visible_no_tasks_started',
    'taskmanager/openProject',
    'loadAsIs=false',
    'hasResourcesXML=false',
    'hasUnresolvedResources=false',
    'BS-AI12 imported project read-only review',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI11 tracked content ${index} missing: ${marker}`);
  });
});

[
  'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1',
  'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2',
  'projectsFileCount=2158',
  'projectsMatchCount=2',
  'no `Start`',
].forEach((marker) => {
  assert.ok((doc + readme + changelog).includes(marker), `BS-AI11 outcome marker missing: ${marker}`);
});

[
  'BS-AI11 ran SQX tasks',
  'BS-AI11 promoted BSAI',
  'BS-AI11 promoted 144.2953',
  'loadAsIs=true used',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI11 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai11 remapped manual import gate contracts ok');
