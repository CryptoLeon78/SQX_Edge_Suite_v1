import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai21_asset_broker_instrument_review.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai21_asset_broker_instrument_review.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai21_asset_broker_instrument_review.py'), 'utf8');
const docPath = path.join(repoRoot, 'docs/BS_AI21_ASSET_BROKER_INSTRUMENT_REVIEW.md');
const doc = fs.existsSync(docPath) ? fs.readFileSync(docPath, 'utf8') : '';
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'review', 'decision-template')",
  'bs-ai21-asset-broker-instrument-review-v1',
  'core.bsai21_asset_broker_instrument_review',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI21 wrapper marker missing: ${marker}`);
});

[
  'BS_AI21_ASSET_REVIEW_VERSION',
  'asset_broker_instrument_review_completed_requires_fix_or_explicit_waiver_no_apply',
  'asset_broker_instrument_review_completed_new_capa1_allowed_with_controls_no_apply',
  'bsai21_requires_fix_or_explicit_waiver_before_new_capa1',
  'bsai21_review_clean_new_preregistered_capa1_allowed_with_controls',
  'cross_broker_spread_mismatch_can_inflate_simulated_vs_real_tick_drift',
  'point_value_mismatch_can_change_profit_dd_and_retdd_scale',
  'currentBsAi16BranchRemainsFailedForCapa2',
  'writesDataDb',
  'projectStartRequested',
  'projectImportRequested',
  'capa2StartAllowed',
  'migrationToolAllowed',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI21 core marker missing: ${marker}`);
});

[
  'test_review_clean_parity_allows_next_preregistered_capa1_with_controls',
  'test_review_spread_pointvalue_mismatch_requires_fix_or_explicit_waiver',
  'test_missing_config_blocks_without_host_mutation',
  'cost_contract_mismatch_requires_fix_or_explicit_waiver_before_next_capa1',
].forEach((marker) => {
  assert.ok(test.includes(marker), `BS-AI21 test marker missing: ${marker}`);
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
  assert.ok(!script.includes(forbidden), `BS-AI21 wrapper must not contain ${forbidden}`);
});

[
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'loadAsIs=true',
  'Add missing symbols',
  'officialBlocksettingsPromotion": true',
  'capa2StartAllowed": true',
  'projectStartRequested": true',
  'projectStopRequested": true',
  'projectImportRequested": true',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI21 core must not contain ${forbidden}`);
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
    'bs-ai21-asset-broker-instrument-review-v1',
    'BS-AI21 asset/broker/instrument configuration review',
    'asset_broker_instrument_review',
    'AUDCAD_darwinex',
    'AUDCAD_dukascopy',
    'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',
    'No Capa2',
    'No Start',
    'No import',
    'no data.db',
    'no user/projects',
    'no databank',
    'Migration Tool',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI21 tracked content ${index} missing: ${marker}`);
  });
});

[
  'BS-AI21 started Capa2',
  'BS-AI21 pressed Start',
  'BS-AI21 imported project',
  'BS-AI21 patched data.db',
  'BS-AI21 moved user/projects',
  'BS-AI21 mutated databanks',
  'BS-AI21 forced pass states',
  'BS-AI21 rescued BS-AI16',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI21 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai21 asset broker instrument review contracts ok');
