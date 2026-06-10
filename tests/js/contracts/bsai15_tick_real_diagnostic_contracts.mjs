import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai15_tick_real_diagnostic.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai15_tick_real_diagnostic.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai15_tick_real_diagnostic.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI15_TICK_REAL_DIAGNOSTIC.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'audit', 'plan')",
  'bs-ai15-tick-real-diagnostic-v1',
  'core.bsai15_tick_real_diagnostic',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI15 wrapper marker missing: ${marker}`);
});

[
  'BS_AI15_TICK_REAL_DIAGNOSTIC_VERSION',
  'diagnostic_plan_ready_no_capa2_no_filter_relaxation',
  'tick_real_pf_failed_trade_threshold_warning_no_capa2',
  'Profit factor[Main data] >= 1.30',
  'NumberOfTrades',
  'RetestWithHigherPrecision',
  'realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))',
  'new_capa1_experiment_with_pre_registered_tick_real_trade_rule_no_capa2',
  'filterRelaxationAllowedForCurrentLot',
  'projectStartRequested',
  'projectStopRequested',
  'writesDataDb',
  'writesUserProjects',
  'mutatesDatabanks',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI15 core marker missing: ${marker}`);
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
  assert.ok(!script.includes(forbidden), `BS-AI15 wrapper must not contain ${forbidden}`);
});

[
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'loadAsIs=true',
  'Add missing symbols',
  'officialBlocksettingsPromotion": true',
  'capa2StartAllowed": true',
  'filterRelaxationAllowedForCurrentLot": true',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI15 core must not contain ${forbidden}`);
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
    'bs-ai15-tick-real-diagnostic-v1',
    'diagnostic_plan_ready_no_capa2_no_filter_relaxation',
    'tick_real_pf_failed_trade_threshold_warning_no_capa2',
    'RETEST 0',
    'retest 1',
    'TICK',
    'Profit factor[Main data] >= 1.30',
    '# of trades >= 200',
    'No Capa2',
    'No filter relaxation',
    'BS-AI16',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI15 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI15 started Capa2',
  'BS-AI15 relaxed filters to rescue candidate',
  'BS-AI15 promoted BSAI',
  'BS-AI15 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI15 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai15 tick real diagnostic contracts ok');
