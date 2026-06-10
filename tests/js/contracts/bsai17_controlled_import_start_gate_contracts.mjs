import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai17_controlled_import_start_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai17_controlled_import_start_gate.py'), 'utf8');
const test = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_bsai17_controlled_import_start_gate.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI17_CONTROLLED_IMPORT_START_GATE.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs/PROJECT_GOVERNANCE.md'), 'utf8');
const trace = fs.readFileSync(path.join(repoRoot, 'docs/BS_TRACE1_BLOCKSETTINGS_SOURCE.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs/state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'preflight', 'launch', 'import-capa1', 'start-capa1')",
  'bs-ai17-controlled-capa1-import-start-gate-v1',
  'core.bsai17_controlled_import_start_gate',
  '--accept-cross-broker-spread-warning',
  'AcceptCrossBrokerSpreadWarningForThisTrial',
  'Start-Process',
  'taskmanager/listProjects',
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI17 wrapper marker missing: ${marker}`);
});

[
  'BS_AI17_CONTROLLED_IMPORT_START_VERSION',
  'controlled_capa1_import_start_requested_no_capa2',
  'cross_broker_spread_warning_not_accepted_for_this_trial',
  'cross_broker_spread_warning_accepted_for_this_trial_only',
  'this_trial_only',
  'futureAssetBrokerInstrumentReviewRequired',
  'taskmanager/openProject',
  '"loadAsIs": "false"',
  'project/start',
  'capa2StartAllowed',
  'loadAsIsAllowed',
  'addMissingSymbolsAllowed',
  'directDataDbPatch',
  'directUserProjectsPatch',
  'directDatabankMutation',
  'migrationToolAllowed',
  'officialBlocksettingsPromotion',
  'sqx144UpdatePromotion',
  'BS-AI18 monitor BSAI16 Capa1 run',
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI17 core marker missing: ${marker}`);
});

[
  'cross_broker_spread_warning_not_accepted_for_this_trial',
  'cross_broker_spread_warning_accepted_for_this_trial_only',
  'taskmanager/openProject',
  'loadAsIs',
  'project/start',
  'capa2StartAllowed',
  'must_not_leak',
].forEach((marker) => {
  assert.ok(test.includes(marker), `BS-AI17 test marker missing: ${marker}`);
});

[
  "loadAsIs = 'true'",
  'loadAsIs=$true',
  'Add missing symbols',
  'Migration Tool allowed',
  'import-capa2',
  'start-capa2',
  'Remove-Item',
  'Move-Item',
  'Copy-Item',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI17 wrapper must not contain ${forbidden}`);
});

[
  'loadAsIs=true',
  'loadAsIs": "true"',
  'Add missing symbols',
  'import-capa2',
  'start-capa2',
  'capa2StartAllowed": True',
  'loadAsIsAllowed": True',
  'addMissingSymbolsAllowed": True',
  'directDataDbPatch": True',
  'directUserProjectsPatch": True',
  'directDatabankMutation": True',
  'officialBlocksettingsPromotion": True',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `BS-AI17 core must not contain ${forbidden}`);
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
    'bs-ai17-controlled-capa1-import-start-gate-v1',
    'controlled_capa1_import_start_requested_no_capa2',
    'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',
    'cross-broker spread warning',
    'this trial only',
    'future asset/broker/instrument review',
    'taskmanager/openProject',
    'loadAsIs=false',
    'project/start',
    'No Capa2',
    'BS-AI18',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `BS-AI17 tracked content ${index} missing: ${marker}`);
  });
});

[
  'raw XML stored',
  'local path exposed',
  'BS-AI17 started Capa2',
  'loadAsIs=true used',
  'Add missing symbols used',
  'Migration Tool used',
  'BS-AI17 promoted BSAI',
  'BS-AI17 promoted 144.2953',
  'risk zero guaranteed',
  'guaranteed profitability',
].forEach((forbidden) => {
  [doc, readme, governance, changelog, test].forEach((content, index) => {
    assert.ok(!content.includes(forbidden), `BS-AI17 tracked content ${index} must not contain ${forbidden}`);
  });
});

console.log('bsai17 controlled import start gate contracts ok');
