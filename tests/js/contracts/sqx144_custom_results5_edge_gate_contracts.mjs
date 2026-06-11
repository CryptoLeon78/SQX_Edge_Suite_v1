import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const pluginDir = path.join(repoRoot, 'integrations', 'sqx144', 'results_plugins', 'SQX Edge Gate');
const index = fs.readFileSync(path.join(pluginDir, 'index.html'), 'utf8');
const logicSource = fs.readFileSync(path.join(pluginDir, 'edge-gate.js'), 'utf8');
const fixturesSource = fs.readFileSync(path.join(pluginDir, 'fixtures', 'fixtures.js'), 'utf8');
const pluginReadme = fs.readFileSync(path.join(pluginDir, 'README.md'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools', 'sqx144_custom_results5_edge_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'core', 'sqx144_custom_results5_edge_gate.py'), 'utf8');
const pyTest = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'test_sqx144_custom_results5_edge_gate.py'), 'utf8');

[
  'SQX Edge Gate',
  'sqx144-custom-results5-edge-gate-v1',
  'window.__SQX_EDGE_GATE__',
  'STRATEGY_DATA',
  'GET_STATS',
  'STATS_RESPONSE',
  'GET_ORDERS',
  'ORDERS_RESPONSE',
  'Activar Order Radar',
  'PASS',
  'REVIEW',
  'BLOCK',
  'Trading',
].forEach((marker) => {
  assert.ok(index.includes(marker) || logicSource.includes(marker) || pluginReadme.includes(marker), `CUSTOM-RESULTS5 runtime marker missing: ${marker}`);
});

[
  'GET_SOURCE_CODE',
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
  [index, logicSource, fixturesSource].forEach((content, idx) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS5 runtime content ${idx} must not contain ${forbidden}`);
  });
});

[
  "ValidateSet('status', 'smoke', 'report', 'approval-template', 'install')",
  'core.sqx144_custom_results5_edge_gate',
  '--apply',
  '--approval',
  '--write-evidence',
  'rawOrdersReturnedByTooling',
  'APRUEBO SQX144 CUSTOM RESULTS5 EDGE GATE INSTALL host=sqx144_full plugin=sqx_edge_gate sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `CUSTOM-RESULTS5 wrapper marker missing: ${marker}`);
});

[
  'SQX144_CUSTOM_RESULTS5_VERSION',
  'SQX144_CUSTOM_RESULTS5_PHASE_LABEL',
  'INSTALL_APPROVAL_PHRASE',
  'EXPECTED_ROOT_NAME = "SQX_144_Full"',
  'PLUGIN_NAME = "SQX Edge Gate"',
  'smoke_payload',
  'status_payload',
  'report_payload',
  'install_payload',
  '_require_install_approval',
  '_assert_safe_install_paths',
  'ordersRequestIsOptIn',
  'target_plugin_exists_without_sqx_edge_marker',
  'sqx_or_java_process_running',
].forEach((marker) => {
  assert.ok(core.includes(marker), `CUSTOM-RESULTS5 core marker missing: ${marker}`);
});

[
  'test_status_is_source_ready_without_host_mutation',
  'test_smoke_accepts_edge_gate_runtime_and_fixtures',
  'test_report_declares_copy_only_install_gate_without_apply',
  'test_install_dry_run_does_not_copy_to_fake_host',
  'test_install_apply_requires_exact_approval',
  'test_preflight_blocks_running_sqx_and_non_owned_target',
  'test_install_apply_with_exact_approval_copies_only_to_temp_host',
  'test_install_apply_backs_up_existing_owned_target',
].forEach((marker) => {
  assert.ok(pyTest.includes(marker), `CUSTOM-RESULTS5 pytest marker missing: ${marker}`);
});

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(logicSource, sandbox);
vm.runInContext(fixturesSource, sandbox);

const logic = sandbox.window.SQX_EDGE_GATE_LOGIC;
const fixtures = sandbox.window.SQX_EDGE_GATE_FIXTURES;
assert.equal(logic.VERSION, 'sqx144-custom-results5-edge-gate-v1', 'version drifted');
assert.equal(logic.THRESHOLDS.tradesPass, 120, 'trades pass threshold drifted');
assert.equal(logic.THRESHOLDS.profitFactorPass, 1.3, 'PF threshold drifted');
assert.equal(logic.THRESHOLDS.returnDdPass, 4, 'Return/DD threshold drifted');
assert.equal(logic.THRESHOLDS.expectancyPass, 0, 'RExpectancy boundary drifted');
assert.equal(logic.THRESHOLDS.netProfitPass, 0, 'NetProfit boundary drifted');

function runFixture(name) {
  let strategy = null;
  let stats = null;
  let orders = null;
  for (const message of fixtures[name].messages) {
    if (message.type === 'STRATEGY_DATA') strategy = message.data;
    if (message.type === 'STATS_RESPONSE') stats = message.data;
    if (message.type === 'ORDERS_RESPONSE') orders = message.data;
  }
  return { strategy, stats, orders, decision: logic.evaluateGate(strategy, stats) };
}

assert.equal(runFixture('pass').decision.verdict, 'PASS', 'pass fixture should pass');
assert.equal(runFixture('review').decision.verdict, 'REVIEW', 'review fixture should review');
assert.equal(runFixture('block').decision.verdict, 'BLOCK', 'block fixture should block');
assert.equal(runFixture('missingStats').decision.verdict, 'BLOCK', 'missing stats should block');
assert.equal(runFixture('missingOOS').decision.verdict, 'REVIEW', 'missing OOS marker should review');

const zeroExpectancyDecision = logic.evaluateGate(
  { name: 'Zero Expectancy Boundary', sampleType: 'OOS 20' },
  { NumberOfTrades: 140, ProfitFactor: 1.5, ReturnDDRatio: 5, RExpectancy: 0, NetProfit: 1000, sampleType: 'OOS 20' }
);
assert.equal(zeroExpectancyDecision.verdict, 'BLOCK', 'RExpectancy equal to zero must block');

const zeroNetProfitDecision = logic.evaluateGate(
  { name: 'Zero Net Profit Boundary', sampleType: 'OOS 20' },
  { NumberOfTrades: 140, ProfitFactor: 1.5, ReturnDDRatio: 5, RExpectancy: 0.03, NetProfit: 0, sampleType: 'OOS 20' }
);
assert.equal(zeroNetProfitDecision.verdict, 'BLOCK', 'NetProfit equal to zero must block');

const orderAnalysis = logic.analyzeOrders(runFixture('ordersOptIn').orders);
assert.ok(orderAnalysis.count > 0, 'ordersOptIn fixture should provide orders');
assert.ok(orderAnalysis.maxLossStreak >= 1, 'order loss streak should be computed');
assert.ok(['pass', 'review', 'block'].includes(orderAnalysis.severity), 'order severity should be normalized');

const largeOrderAnalysis = logic.analyzeOrders(runFixture('largeOrders').orders);
assert.ok(largeOrderAnalysis.count >= 180, 'largeOrders fixture should be large');

[
  'pass',
  'review',
  'block',
  'noStrategy',
  'missingStats',
  'missingOOS',
  'ordersOptIn',
  'largeOrders',
].forEach((fixtureName) => {
  assert.ok(Object.hasOwn(fixtures, fixtureName), `fixture missing: ${fixtureName}`);
});

console.log('sqx144 custom results5 edge gate contracts ok');
