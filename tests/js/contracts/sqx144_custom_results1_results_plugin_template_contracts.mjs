import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const pluginDir = path.join(repoRoot, 'integrations', 'sqx144', 'results_plugins', 'SQX Edge Custom Results Template');
const index = fs.readFileSync(path.join(pluginDir, 'index.html'), 'utf8');
const fixtures = fs.readFileSync(path.join(pluginDir, 'fixtures', 'fixtures.js'), 'utf8');
const pluginReadme = fs.readFileSync(path.join(pluginDir, 'README.md'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools', 'sqx144_custom_results1_results_plugin_template.ps1'), 'utf8');
const legacyWrapper = fs.readFileSync(path.join(repoRoot, 'tools', 'sqx144_custom_results1_study.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'core', 'sqx144_custom_results1_study.py'), 'utf8');
const pyTest = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'test_sqx144_custom_results1_results_plugin_template.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs', 'SQX144_CUSTOM_RESULTS1_READONLY_RESULTS_PLUGIN_TEMPLATE.md'), 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs', 'PROJECT_GOVERNANCE.md'), 'utf8');
const roadmap = fs.readFileSync(path.join(repoRoot, 'docs', 'SQX144_LAB_INTAKE_ROADMAP.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs', 'state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'scan', 'scan-downloads', 'smoke', 'template-smoke', 'report', 'decision-template')",
  'sqx144-custom-results1-results-plugin-template-v1',
  'SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template',
  'core.sqx144_custom_results1_study',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `CUSTOM-RESULTS1 wrapper marker missing: ${marker}`);
});

[
  'sqx144-custom-results1-results-plugin-template-v1',
  'core.sqx144_custom_results1_study',
].forEach((marker) => {
  assert.ok(legacyWrapper.includes(marker), `CUSTOM-RESULTS1 legacy wrapper marker missing: ${marker}`);
});

[
  'SQX144_CUSTOM_RESULTS1_VERSION',
  'sqx144-custom-results1-results-plugin-template-v1',
  'sqx144-custom-results1-readonly-results-plugin-template-v1',
  'custom_results1_template_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool',
  'SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template',
  'installExecuted',
  'RobustnessScorecard.zip',
  'OOSDegradationScorecard.zip',
  'Edge-Decay-Max-Loss-Analyzer-1.zip',
  'WinRateEdge-1.zip',
  '2-Step-Challenge-Analyzer.zip',
  'GET_STATS',
  'GET_ORDERS',
  'GET_SOURCE_CODE',
  'resultsPlugins/create',
  'resultsPlugins/rename',
  'resultsPlugins/delete',
  'localStorage',
  'remoteFetchDetected',
  'requiresOrdersGate',
  'requiresPersistenceWaiver',
  'browserPersistenceAllowedByDefault',
].forEach((marker) => {
  assert.ok(core.includes(marker), `CUSTOM-RESULTS1 core marker missing: ${marker}`);
});

[
  'test_status_is_source_ready_no_runtime_no_mutation',
  'test_scan_accepts_template_and_returns_public_safe_inventory',
  'test_scan_blocks_forbidden_results_plugin_messages',
  'test_smoke_runs_offline_fixtures_without_sqx_runtime',
  'test_payload_does_not_return_local_paths_or_private_strategy_names',
].forEach((marker) => {
  assert.ok(pyTest.includes(marker), `CUSTOM-RESULTS1 pytest marker missing: ${marker}`);
});

[
  'SQX_EDGE_CUSTOM_RESULTS_TEMPLATE_VERSION',
  'sqx144-custom-results1-results-plugin-template-v1',
  'window.__SQX_EDGE_CUSTOM_RESULTS_TEMPLATE__',
  'STRATEGY_DATA',
  'SET_THEME',
  'SET_LANGUAGE',
  'GET_STATS',
  'STATS_RESPONSE',
  'user/extend/ResultsPlugins',
  'No profitability promise',
  'no SQX host mutation',
].forEach((marker) => {
  assert.ok(index.includes(marker), `CUSTOM-RESULTS1 index marker missing: ${marker}`);
});

[
  'window.SQX_EDGE_CUSTOM_RESULTS_FIXTURES',
  'ready',
  'review',
  'blocked',
  'noStrategy',
  'missingStats',
  'largePortfolio',
  'RExpectancy',
  'ReturnDDRatio',
].forEach((marker) => {
  assert.ok(fixtures.includes(marker), `CUSTOM-RESULTS1 fixtures marker missing: ${marker}`);
});

[
  'GET_SOURCE_CODE',
  'GET_ORDERS',
  'resultsPlugins/create',
  'resultsPlugins/rename',
  'resultsPlugins/delete',
  'localStorage',
  'sessionStorage',
  'indexedDB',
  'fetch(',
  'run_project',
  'stop_project',
].forEach((forbidden) => {
  assert.ok(!index.includes(forbidden), `CUSTOM-RESULTS1 index must not contain ${forbidden}`);
  assert.ok(!fixtures.includes(forbidden), `CUSTOM-RESULTS1 fixtures must not contain ${forbidden}`);
});

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(fixtures, sandbox);
assert.ok(sandbox.window.SQX_EDGE_CUSTOM_RESULTS_FIXTURES.ready.messages.length === 2, 'ready fixture message count drifted');
assert.equal(sandbox.window.SQX_EDGE_CUSTOM_RESULTS_FIXTURES.review.messages[1].payload.NumberOfTrades, 54, 'review fixture drifted');
assert.ok(sandbox.window.SQX_EDGE_CUSTOM_RESULTS_FIXTURES.blocked.messages[1].payload.ProfitFactor < 1, 'blocked fixture must remain blocked');
assert.ok(sandbox.window.SQX_EDGE_CUSTOM_RESULTS_FIXTURES.largePortfolio.messages[1].payload.NumberOfTrades > 3000, 'large portfolio fixture drifted');

[
  doc,
  readme,
  governance,
  roadmap,
  changelog,
  manifest,
  pluginReadme,
].forEach((content, indexNumber) => {
  [
    'SQX144-CUSTOM-RESULTS1',
    'SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template',
    'sqx144-custom-results1-results-plugin-template-v1',
    'sqx144-custom-results1-readonly-results-plugin-template-v1',
    'custom_results1_template_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool',
    'SQX Edge Custom Results Template',
    'integrations/sqx144/results_plugins/SQX Edge Custom Results Template',
    'tools/sqx144_custom_results1_results_plugin_template.ps1',
    'tests/js/contracts/sqx144_custom_results1_results_plugin_template_contracts.mjs',
    'installExecuted=false',
    'No se instala en SQX144',
    'No SQX runtime',
    'no data.db',
    'no user/projects',
    'no databank mutation',
    'no Migration Tool',
    'STRATEGY_DATA',
    'SET_THEME',
    'SET_LANGUAGE',
    'STATS_RESPONSE',
    'GET_STATS',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `CUSTOM-RESULTS1 tracked content ${indexNumber} missing: ${marker}`);
  });
});

[
  'installExecuted=true',
  'GET_SOURCE_CODE permitido',
  'GET_ORDERS permitido por defecto',
  'launch SQX 144 now',
  'SQX 144 sustituye SQX 142',
  'migrate active data into 144 automatically',
  'bulk copy Build 144 internals',
  'profit guarantee',
  'risk zero',
  'Results=passed',
].forEach((forbidden) => {
  [doc, pluginReadme].forEach((content, indexNumber) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS1 new doc content ${indexNumber} must not contain ${forbidden}`);
  });
});

[
  'CUSTOM-RESULTS1 installExecuted=true',
  'CUSTOM-RESULTS1 GET_SOURCE_CODE permitido',
  'CUSTOM-RESULTS1 GET_ORDERS permitido por defecto',
  'CUSTOM-RESULTS1 Results=passed',
].forEach((forbidden) => {
  [readme, governance, roadmap, changelog].forEach((content, indexNumber) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS1 live summary ${indexNumber} must not contain ${forbidden}`);
  });
});

console.log('sqx144 custom results1 results plugin template contracts ok');
