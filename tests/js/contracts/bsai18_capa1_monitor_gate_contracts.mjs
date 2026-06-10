import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai18_capa1_monitor_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai18_capa1_monitor_gate.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai18_capa1_monitor_gate.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI18_CAPA1_MONITOR_GATE.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'monitor', 'decision-template')",
  'bs-ai18-capa1-monitor-gate-v1',
  'core.bsai18_capa1_monitor_gate',
  '--observe-seconds',
  '--poll-seconds',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI18 wrapper marker missing: ${marker}`);
});

[
  'BS_AI18_CAPA1_MONITOR_GATE_VERSION',
  'monitoring_capa1_bsa16_no_capa2',
  'continue_monitoring_capa1_active_no_capa2',
  'taskmanagerListProjectsOnly',
  'projectStartRequested',
  'projectStopRequested',
  'taskmanagerOpenProjectAllowed',
  'capa2StartAllowed',
  'cleanTickForwardChainReady',
  'BS-AI18 continue monitor',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI18 core marker missing: ${marker}`);
});

[
  'continue_monitoring_capa1_active_no_capa2',
  'remote_access_unavailable',
  'taskmanagerOpenProjectAllowed',
  'capa2StartAllowed',
].forEach((marker) => {
  assert.ok(test.includes(marker), `BS-AI18 test marker missing: ${marker}`);
});

[
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'loadAsIs',
  'Start-Process',
  'Add missing symbols',
  'Migration Tool allowed',
  'import-capa1',
  'start-capa1',
  'start-capa2',
  'stop-capa1',
  'Remove-Item',
  'Move-Item',
  'Copy-Item',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI18 wrapper must not contain ${forbidden}`);
});

[
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'loadAsIs=true',
  'Add missing symbols',
  'capa2StartAllowed": True',
  'projectStartRequested": True',
  'projectStopRequested": True',
  'directDataDbPatch": True',
  'directUserProjectsPatch": True',
  'directDatabankMutation": True',
  'officialBlocksettingsPromotion": True',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI18 core must not contain ${forbidden}`);
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
    'bs-ai18-capa1-monitor-gate-v1',
    'monitoring_capa1_bsa16_no_capa2',
    'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',
    'continue_monitoring_capa1_active_no_capa2',
    '65 strategies',
    'No Capa2',
    'read-only',
    'taskmanager/listProjects',
    'clean real TICK/Forward',
    'BS-AI19',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI18 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI18 started Capa2',
  'BS-AI18 pressed Start',
  'BS-AI18 pressed Stop',
  'loadAsIs=true used',
  'Add missing symbols used',
  'Migration Tool used',
  'BS-AI18 promoted BSAI',
  'BS-AI18 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI18 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai18 capa1 monitor gate contracts ok');
