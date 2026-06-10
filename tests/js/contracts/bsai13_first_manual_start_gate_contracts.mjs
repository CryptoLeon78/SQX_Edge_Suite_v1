import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai13_first_start_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai_first_start_gate.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI13_FIRST_MANUAL_START_GATE.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'preflight', 'start-capa1', 'stop-capa1')",
  'bs-ai13-first-manual-start-gate-v1',
  'core.bsai_first_start_gate',
  '--observe-seconds',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI13 wrapper marker missing: ${marker}`);
});

[
  'BS_AI13_FIRST_START_GATE_VERSION',
  'project/start',
  'project/stop',
  'first_start_preflight_ready',
  'first_start_requested_observed_no_capa2_start',
  'hostRunMayMutateTargetDatabanks',
  'capa2StartAllowed',
  'BS-AI14 monitor Capa1 run and decide Capa2 start',
  'bsai13_privacy_guard_failed',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI13 core marker missing: ${marker}`);
});

[
  'taskmanager/openProject',
  'loadAsIs',
  'start-capa2',
  'Start-Process',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Add missing symbols',
  'Migration Tool allowed',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI13 wrapper must not contain ${forbidden}`);
});

[
  'taskmanager/openProject',
  'loadAsIs=true',
  'Add missing symbols',
  'officialBlocksettingsPromotion": true',
  'capa2StartAllowed": true',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI13 core must not contain ${forbidden}`);
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
    'bs-ai13-first-manual-start-gate-v1',
    'first_start_requested_observed_no_capa2_start',
    'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1',
    'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2',
    'project/start',
    'Project execution started.',
    'strategies=0',
    'capa2StartAllowed=false',
    'BS-AI14 monitor Capa1 run and decide Capa2 start',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI13 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI13 started Capa2',
  'BS-AI13 promoted BSAI',
  'BS-AI13 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI13 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai13 first manual start gate contracts ok');
