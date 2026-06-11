import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const pluginDir = path.join(repoRoot, 'integrations', 'sqx144', 'results_plugins', 'SQX Edge Custom Results All Modules');
const index = fs.readFileSync(path.join(pluginDir, 'index.html'), 'utf8');
const fixtures = fs.readFileSync(path.join(pluginDir, 'fixtures', 'fixtures.js'), 'utf8');
const pluginReadme = fs.readFileSync(path.join(pluginDir, 'README.md'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools', 'sqx144_custom_results2_all_modules_bundle.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'core', 'sqx144_custom_results2_all_modules.py'), 'utf8');
const pyTest = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'test_sqx144_custom_results2_all_modules_bundle.py'), 'utf8');
const docPath = path.join(repoRoot, 'docs', 'SQX144_CUSTOM_RESULTS2_ALL_CUSTOM_RESULTS_MODULES_BUNDLE.md');
const doc = fs.existsSync(docPath) ? fs.readFileSync(docPath, 'utf8') : '';
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs', 'PROJECT_GOVERNANCE.md'), 'utf8');
const roadmap = fs.readFileSync(path.join(repoRoot, 'docs', 'SQX144_LAB_INTAKE_ROADMAP.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs', 'state_consistency_manifest.json'), 'utf8');

[
  "ValidateSet('status', 'scan', 'smoke', 'module-smoke', 'report', 'approval-template')",
  'sqx144-custom-results2-all-custom-results-modules-bundle-v1',
  'SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle',
  'core.sqx144_custom_results2_all_modules',
  '--write-evidence',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `CUSTOM-RESULTS2 wrapper marker missing: ${marker}`);
});

[
  'SQX144_CUSTOM_RESULTS2_VERSION',
  'sqx144-custom-results2-all-custom-results-modules-bundle-v1',
  'sqx144-custom-results2-readonly-all-modules-bundle-v1',
  'custom_results2_all_modules_bundle_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool',
  'SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle',
  'GET_ORDERS remains privacy/performance-gated',
  'ORDERS_RESPONSE fixture-only until exact future gate',
  'usesGetOrdersInRepoOnlyBundle',
  'rawOrdersReturnedByTooling',
  'downloadedPluginsInstalled',
  'RobustnessScorecard.zip',
  'OOSDegradationScorecard.zip',
  'Edge-Decay-Max-Loss-Analyzer-1.zip',
  'WinRateEdge-1.zip',
  '2-Step-Challenge-Analyzer.zip',
].forEach((marker) => {
  assert.ok(core.includes(marker), `CUSTOM-RESULTS2 core marker missing: ${marker}`);
});

[
  'test_status_declares_all_modules_repo_only_and_orders_policy',
  'test_scan_maps_all_downloaded_custom_results_without_installing',
  'test_module_smoke_accepts_orders_bundle_but_blocks_unsafe_markers',
  'test_report_writes_sanitized_evidence_when_requested',
].forEach((marker) => {
  assert.ok(pyTest.includes(marker), `CUSTOM-RESULTS2 pytest marker missing: ${marker}`);
});

[
  'SQX_EDGE_CUSTOM_RESULTS_ALL_MODULES_VERSION',
  'sqx144-custom-results2-all-custom-results-modules-bundle-v1',
  'window.__SQX_EDGE_CUSTOM_RESULTS_ALL_MODULES__',
  'ORDER_LIMIT',
  'STRATEGY_DATA',
  'SET_THEME',
  'GET_STATS',
  'STATS_RESPONSE',
  'GET_ORDERS',
  'ORDERS_RESPONSE',
  'Robustness Scorecard',
  'IS/OOS Degradation',
  'Edge Decay Analyzer',
  'WinRateEdge',
  '2-Step Challenge',
  'escapeHtml',
  'orderCount',
].forEach((marker) => {
  assert.ok(index.includes(marker), `CUSTOM-RESULTS2 index marker missing: ${marker}`);
});

[
  'window.SQX_EDGE_CUSTOM_RESULTS_ALL_MODULES_FIXTURES',
  'allReady',
  'edgeDecay',
  'winRateResearch',
  'propFirm',
  'blockedWeak',
  'missingOrders',
  'ORDERS_RESPONSE',
  'mae',
  'mfe',
].forEach((marker) => {
  assert.ok(fixtures.includes(marker), `CUSTOM-RESULTS2 fixtures marker missing: ${marker}`);
});

[
  'GET_SOURCE_CODE',
  'SOURCE_CODE_RESPONSE',
  'resultsPlugins/create',
  'resultsPlugins/rename',
  'resultsPlugins/delete',
  'localStorage',
  'sessionStorage',
  'indexedDB',
  'fetch(',
  'XMLHttpRequest',
  'WebSocket',
  'document.cookie',
  'run_project',
  'stop_project',
  'taskmanager/',
  'Blob(',
  'URL.createObjectURL',
].forEach((forbidden) => {
  assert.ok(!index.includes(forbidden), `CUSTOM-RESULTS2 index must not contain ${forbidden}`);
  assert.ok(!fixtures.includes(forbidden), `CUSTOM-RESULTS2 fixtures must not contain ${forbidden}`);
});

[
  'getState: () => JSON.parse(JSON.stringify(state))',
  'strategyName:',
  'orders: state.orders',
].forEach((forbidden) => {
  assert.ok(!index.includes(forbidden), `CUSTOM-RESULTS2 debug API must not expose raw state marker: ${forbidden}`);
});

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(fixtures, sandbox);
const fx = sandbox.window.SQX_EDGE_CUSTOM_RESULTS_ALL_MODULES_FIXTURES;
assert.equal(fx.allReady.messages.length, 3, 'allReady fixture message count drifted');
assert.ok(fx.edgeDecay.messages[2].payload.orders.length >= 10, 'edgeDecay orders missing');
assert.ok(fx.winRateResearch.messages[2].payload.orders.length > fx.allReady.messages[2].payload.orders.length, 'winRate fixture should have larger order sample');
assert.ok(fx.propFirm.messages[1].payload.propProfitTargetPct === 10, 'propFirm fixture drifted');
assert.equal(fx.missingOrders.messages.length, 2, 'missingOrders must omit orders payload');

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
    'SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle',
    'sqx144-custom-results2-all-custom-results-modules-bundle-v1',
    'sqx144-custom-results2-readonly-all-modules-bundle-v1',
    'custom_results2_all_modules_bundle_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool',
    'SQX Edge Custom Results All Modules',
    'integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules',
    'tools/sqx144_custom_results2_all_modules_bundle.ps1',
    'tests/js/contracts/sqx144_custom_results2_all_modules_bundle_contracts.mjs',
    'installExecuted=false',
    'No se instala en SQX144',
    'No SQX runtime',
    'no data.db',
    'no user/projects',
    'no databank mutation',
    'no Migration Tool',
    'STRATEGY_DATA',
    'SET_THEME',
    'GET_STATS',
    'STATS_RESPONSE',
    'GET_ORDERS remains privacy/performance-gated',
    'ORDERS_RESPONSE fixture-only until exact future gate',
    'RobustnessScorecard',
    'OOSDegradationScorecard',
    'Edge Decay Analyzer',
    'WinRateEdge + RandomEntry',
    '2-Step Challenge Analyzer',
  ].forEach((marker) => {
    assert.ok(content.includes(marker), `CUSTOM-RESULTS2 tracked content ${indexNumber} missing: ${marker}`);
  });
});

[
  'installExecuted=true',
  'GET_SOURCE_CODE permitido',
  'GET_ORDERS permitido por defecto',
  'ORDERS_RESPONSE live by default',
  'launch SQX 144 now',
  'SQX 144 sustituye SQX 142',
  'migrate active data into 144 automatically',
  'bulk copy Build 144 internals',
  'profit guarantee',
  'risk zero',
  'Results=passed',
  'data.db write permitido',
  'user/projects write permitido',
  'databank mutation permitido',
  'Migration Tool permitido',
].forEach((forbidden) => {
  [doc, pluginReadme].forEach((content, indexNumber) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS2 new doc content ${indexNumber} must not contain ${forbidden}`);
  });
});

[
  'CUSTOM-RESULTS2 installExecuted=true',
  'CUSTOM-RESULTS2 GET_SOURCE_CODE permitido',
  'CUSTOM-RESULTS2 GET_ORDERS permitido por defecto',
  'CUSTOM-RESULTS2 ORDERS_RESPONSE live by default',
  'CUSTOM-RESULTS2 launch SQX 144 now',
  'CUSTOM-RESULTS2 migrate active data into 144 automatically',
  'CUSTOM-RESULTS2 bulk copy Build 144 internals',
  'CUSTOM-RESULTS2 Results=passed',
  'CUSTOM-RESULTS2 writes data.db',
  'CUSTOM-RESULTS2 mutates user/projects',
  'CUSTOM-RESULTS2 mutates databanks',
  'CUSTOM-RESULTS2 uses Migration Tool',
].forEach((forbidden) => {
  [readme, governance, roadmap, changelog].forEach((content, indexNumber) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS2 live summary ${indexNumber} must not contain ${forbidden}`);
  });
});

console.log('sqx144 custom results2 all modules bundle contracts ok');
