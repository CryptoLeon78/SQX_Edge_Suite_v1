import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai20_decision_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai20_decision_gate.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai20_decision_gate.py'), 'utf8');
const docPath = path.join(repoRoot, 'docs/BS_AI20_DECISION_GATE.md');
const doc = fs.existsSync(docPath) ? fs.readFileSync(docPath, 'utf8') : '';
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'decide', 'decision-template')",
  'bs-ai20-decision-gate-v1',
  'core.bsai20_decision_gate',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI20 wrapper marker missing: ${marker}`);
});

[
  'BS_AI20_DECISION_GATE_VERSION',
  'decision_archive_branch_open_asset_broker_instrument_review_no_capa2',
  'archive_branch_and_open_asset_broker_instrument_review_no_capa2',
  'BS-AI21 asset/broker/instrument configuration review',
  'methodology_archive_only_no_host_project_move',
  'deferred_until_asset_broker_instrument_review_or_explicit_waiver',
  'hostProjectArchiveMutationAllowed',
  'projectStartRequested',
  'projectStopRequested',
  'projectImportRequested',
  'capa2StartAllowed',
  'directDataDbPatch',
  'directUserProjectsPatch',
  'directDatabankMutation',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI20 core marker missing: ${marker}`);
});

[
  'archive_branch_and_open_asset_broker_instrument_review_no_capa2',
  'deferred_until_asset_broker_instrument_review_or_explicit_waiver',
  'bsai20_blocked_missing_or_unreadable_bsai19_review',
  'hostProjectArchiveMutationAllowed',
].forEach((marker) => {
  assert.ok(test.includes(marker), `BS-AI20 test marker missing: ${marker}`);
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
  assert.ok(!script.includes(forbidden), `BS-AI20 wrapper must not contain ${forbidden}`);
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
  'hostProjectArchiveMutationAllowed": true',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI20 core must not contain ${forbidden}`);
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
    'bs-ai20-decision-gate-v1',
    'decision_archive_branch_open_asset_broker_instrument_review_no_capa2',
    'archive_branch_and_open_asset_broker_instrument_review_no_capa2',
    'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',
    'BS-AI21 asset/broker/instrument configuration review',
    'No Capa2',
    'No Start',
    'No import',
    'No forced pass',
    'no host project move',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI20 tracked content ${index} missing: ${marker}`);
  });
});

[
  'BS-AI20 started Capa2',
  'BS-AI20 pressed Start',
  'BS-AI20 imported project',
  'BS-AI20 moved host project',
  'BS-AI20 mutated databanks',
  'BS-AI20 relaxed filters to rescue candidate',
  'BS-AI20 forced pass states',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI20 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai20 decision gate contracts ok');
