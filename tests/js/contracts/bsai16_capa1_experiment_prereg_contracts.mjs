import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai16_capa1_experiment_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai16_capa1_experiment_gate.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai16_capa1_experiment_gate.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI16_CAPA1_EXPERIMENT_PREREG_GATE.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'plan', 'prepare')",
  'bs-ai16-capa1-experiment-prereg-gate-v1',
  'core.bsai16_capa1_experiment_gate',
  '--retention-ratio',
  '--absolute-floor',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI16 wrapper marker missing: ${marker}`);
});

[
  'BS_AI16_CAPA1_EXPERIMENT_GATE_VERSION',
  'preregistered_capa1_tick_rule_ready_no_import_no_start',
  'realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))',
  'DEFAULT_RETENTION_RATIO = 0.65',
  'DEFAULT_ABSOLUTE_FLOOR = 120',
  'RetestWithHigherPrecision.NumberOfTrades >= main.NumberOfTrades *',
  'too_low_spread_can_inflate_simulated_pf_and_real_tick_can_deflate_pf',
  'primary_spread_below_host_catalog',
  'cross_broker_spread_below_alternate_catalog',
  'filterRelaxationAllowedForFrozenLot',
  'projectStartRequested',
  'writesSqxHost',
  'writesDataDb',
  'writesUserProjects',
  'mutatesDatabanks',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI16 core marker missing: ${marker}`);
});

[
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'loadAsIs',
  'Start-Process',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Add missing symbols',
  'Migration Tool allowed',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI16 wrapper must not contain ${forbidden}`);
});

[
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'loadAsIs=true',
  'Add missing symbols',
  'officialBlocksettingsPromotion": true',
  'capa2StartAllowed": true',
  'filterRelaxationAllowedForFrozenLot": true',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI16 core must not contain ${forbidden}`);
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
    'bs-ai16-capa1-experiment-prereg-gate-v1',
    'preregistered_capa1_tick_rule_ready_no_import_no_start',
    'retentionRatio=0.65',
    'absoluteFloor=120',
    'NumberOfTrades >= 120',
    'RetestWithHigherPrecision',
    '65%',
    'spreadCostSanity',
    'No import',
    'No Start',
    'No Capa2',
    'tick_real_pf_failed_trade_threshold_warning_no_capa2',
    'BS-AI17',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI16 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI16 started Capa2',
  'BS-AI16 imported project',
  'BS-AI16 pressed Start',
  'BS-AI16 rescued frozen lot',
  'BS-AI16 promoted BSAI',
  'BS-AI16 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI16 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai16 capa1 experiment prereg contracts ok');
