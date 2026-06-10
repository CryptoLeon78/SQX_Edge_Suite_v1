import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai19_post_run_readonly_review.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai19_post_run_readonly_review.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai19_post_run_readonly_review.py'), 'utf8');
const docPath = path.join(repoRoot, 'docs/BS_AI19_POST_RUN_READONLY_REVIEW.md');
const doc = fs.existsSync(docPath) ? fs.readFileSync(docPath, 'utf8') : '';
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'review', 'decision-template')",
  'bs-ai19-post-run-readonly-review-v1',
  'core.bsai19_post_run_readonly_review',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI19 wrapper marker missing: ${marker}`);
});

[
  'BS_AI19_POST_RUN_READONLY_REVIEW_VERSION',
  'post_run_readonly_review_completed_no_capa2',
  'post_run_review_no_capa2_tick_forward_empty',
  'DEFAULT_EXPERIMENT_ID',
  'realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))',
  'tick_databank_empty_no_real_tick_survivors',
  'forward_databank_empty_no_forward_survivors',
  'projectStartRequested',
  'projectStopRequested',
  'projectImportRequested',
  'capa2StartAllowed',
  'directDataDbPatch',
  'directUserProjectsPatch',
  'directDatabankMutation',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI19 core marker missing: ${marker}`);
});

[
  'post_run_review_no_capa2_tick_forward_empty',
  'post_run_review_clean_tick_forward_chain_manual_gate_required_no_auto_capa2',
  'retest1SurvivorsCanSeedCapa2',
  'directDataDbPatch',
].forEach((marker) => {
  assert.ok(test.includes(marker), `BS-AI19 test marker missing: ${marker}`);
});

[
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'loadAsIs',
  'Start-Process',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Add missing symbols',
  'Migration Tool allowed',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI19 wrapper must not contain ${forbidden}`);
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
  'projectStartRequested": true',
  'projectStopRequested": true',
  'projectImportRequested": true',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI19 core must not contain ${forbidden}`);
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
    'bs-ai19-post-run-readonly-review-v1',
    'post_run_readonly_review_completed_no_capa2',
    'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',
    'Results=1321',
    'RETEST 0=112',
    'retest 1=14',
    'TICK=0',
    'Forward=0',
    'post_run_review_no_capa2_tick_forward_empty',
    'No Capa2',
    'read-only',
    'BS-AI20',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI19 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI19 started Capa2',
  'BS-AI19 pressed Start',
  'BS-AI19 pressed Stop',
  'BS-AI19 imported project',
  'BS-AI19 mutated databanks',
  'BS-AI19 relaxed filters to rescue candidate',
  'BS-AI19 forced pass states',
  'BS-AI19 promoted BSAI',
  'BS-AI19 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI19 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai19 post-run read-only review contracts ok');
