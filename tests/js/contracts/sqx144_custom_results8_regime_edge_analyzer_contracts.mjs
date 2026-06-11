import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const pluginDir = path.join(repoRoot, 'integrations', 'sqx144', 'results_plugins', 'Regime Edge Analyzer');
const index = fs.readFileSync(path.join(pluginDir, 'index.html'), 'utf8');
const logicSource = fs.readFileSync(path.join(pluginDir, 'regime-edge.js'), 'utf8');
const fixturesSource = fs.readFileSync(path.join(pluginDir, 'fixtures', 'fixtures.js'), 'utf8');
const pluginReadme = fs.readFileSync(path.join(pluginDir, 'README.md'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools', 'sqx144_custom_results8_regime_edge_analyzer.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'core', 'sqx144_custom_results8_regime_edge_analyzer.py'), 'utf8');
const pyTest = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'test_sqx144_custom_results8_regime_edge_analyzer.py'), 'utf8');

[
  'Regime Edge Analyzer',
  'sqx144-custom-results8-regime-edge-analyzer-v1',
  'window.__SQX_REGIME_EDGE__',
  'SQX_REGIME_EDGE_LOGIC',
  'STRATEGY_DATA',
  'GET_STATS',
  'STATS_RESPONSE',
  'GET_ORDERS',
  'ORDERS_RESPONSE',
  'Activar Regime Orders',
  'Annual Regime Matrix',
  'Methodology Notes',
  'REGIME_STRONG',
  'REGIME_COMPATIBLE',
  'REGIME_DEFENSIVE',
  'REGIME_MEAN_REVERT',
  'REGIME_MISMATCH_REVIEW',
  'REGIME_ADVERSE_RISK',
  'REGIME_INSUFFICIENT',
  'REGIME_UNKNOWN',
  'BULL',
  'BEAR',
  'SIDEWAYS',
  'MIXED',
  'UNKNOWN',
].forEach((marker) => {
  assert.ok(index.includes(marker) || logicSource.includes(marker) || pluginReadme.includes(marker), `CUSTOM-RESULTS8 runtime marker missing: ${marker}`);
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
  'XMLHttpRequest',
  'WebSocket',
  'EventSource',
  'sendBeacon',
  'eval(',
  'new Function',
  'run_project',
  'stop_project',
  'data.db',
  'user/projects',
  'Migration Tool',
].forEach((forbidden) => {
  [index, logicSource, fixturesSource].forEach((content, idx) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS8 runtime content ${idx} must not contain ${forbidden}`);
  });
});

[
  "ValidateSet('status', 'smoke', 'report', 'approval-template', 'install')",
  'core.sqx144_custom_results8_regime_edge_analyzer',
  '--apply',
  '--approval',
  '--write-evidence',
  'rawOrdersReturnedByTooling',
  'APRUEBO SQX144 CUSTOM RESULTS8 REGIME EDGE ANALYZER INSTALL host=sqx144_full plugin=sqx_regime_edge_analyzer sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `CUSTOM-RESULTS8 wrapper marker missing: ${marker}`);
});

[
  'SQX144_CUSTOM_RESULTS8_VERSION',
  'SQX144_CUSTOM_RESULTS8_PHASE_LABEL',
  'INSTALL_APPROVAL_PHRASE',
  'EXPECTED_ROOT_NAME = "SQX_144_Full"',
  'PLUGIN_NAME = "Regime Edge Analyzer"',
  'smoke_payload',
  'status_payload',
  'report_payload',
  'install_payload',
  '_require_install_approval',
  '_assert_safe_install_paths',
  'ordersRequestIsOptIn',
  'dataManagerProviderIsFutureGated',
  'sqx144-custom-results8-regime-edge-analyzer-v1',
  'target_plugin_exists_without_sqx_edge_marker',
  'sqx_or_java_process_running',
].forEach((marker) => {
  assert.ok(core.includes(marker), `CUSTOM-RESULTS8 core marker missing: ${marker}`);
});

[
  'test_status_is_source_ready_without_host_mutation',
  'test_smoke_accepts_regime_edge_runtime_and_fixtures',
  'test_report_declares_source_ready_copy_only_install_gate_without_apply',
  'test_install_dry_run_does_not_copy_to_fake_host',
  'test_install_apply_requires_exact_approval',
  'test_preflight_blocks_running_sqx_and_non_owned_target',
  'test_install_apply_with_exact_approval_copies_only_to_temp_host',
  'test_install_apply_backs_up_existing_owned_target',
].forEach((marker) => {
  assert.ok(pyTest.includes(marker), `CUSTOM-RESULTS8 pytest marker missing: ${marker}`);
});

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(logicSource, sandbox);
vm.runInContext(fixturesSource, sandbox);

const logic = sandbox.window.SQX_REGIME_EDGE_LOGIC;
const fixtures = sandbox.window.SQX_REGIME_EDGE_FIXTURES;
assert.equal(logic.VERSION, 'sqx144-custom-results8-regime-edge-analyzer-v1', 'version drifted');

function runFixture(name, options = {}) {
  let strategy = null;
  let stats = null;
  let orders = null;
  let market = null;
  for (const message of fixtures[name].messages) {
    if (message.type === 'STRATEGY_DATA') strategy = message.data;
    if (message.type === 'STATS_RESPONSE') stats = message.data;
    if (message.type === 'ORDERS_RESPONSE') orders = message.data;
    if (message.type === 'MARKET_SERIES_RESPONSE') market = message.data.series || message.data;
  }
  return {
    strategy,
    stats,
    orders,
    market,
    decision: logic.evaluateRegime(strategy, stats, orders, market, options),
  };
}

assert.ok(['REGIME_STRONG', 'REGIME_COMPATIBLE', 'REGIME_DEFENSIVE'].includes(runFixture('longBullStrong').decision.label), 'longBullStrong should be aligned evidence');
assert.equal(runFixture('longBullMismatch').decision.label, 'REGIME_MISMATCH_REVIEW', 'longBullMismatch should force review');
assert.ok(['REGIME_STRONG', 'REGIME_COMPATIBLE', 'REGIME_DEFENSIVE'].includes(runFixture('shortBearStrong').decision.label), 'shortBearStrong should be aligned evidence');
assert.equal(runFixture('shortBearMismatch').decision.label, 'REGIME_MISMATCH_REVIEW', 'shortBearMismatch should force review');
assert.equal(runFixture('sidewaysMeanRevert').decision.label, 'REGIME_MEAN_REVERT', 'sidewaysMeanRevert should identify range fit');
assert.equal(runFixture('missingSeries').decision.label, 'REGIME_UNKNOWN', 'missing market series should be unknown');
assert.equal(runFixture('missingTimestamps').decision.label, 'REGIME_UNKNOWN', 'missing timestamps should be unknown');
assert.equal(runFixture('fewTrades').decision.label, 'REGIME_INSUFFICIENT', 'few trades should be insufficient');
assert.equal(runFixture('noStrategy').decision.label, 'REGIME_UNKNOWN', 'no strategy should be unknown');

const annualRegimes = logic.classifyAnnualRegimes(runFixture('longBullStrong').market);
assert.ok(annualRegimes.some(row => row.regime === 'BULL'), 'annual regimes should include BULL');
assert.ok(annualRegimes.some(row => row.regime === 'BEAR'), 'annual regimes should include BEAR');
assert.ok(annualRegimes.some(row => row.regime === 'SIDEWAYS'), 'annual regimes should include SIDEWAYS');

const summary = logic.buildSummary(runFixture('longBullMismatch').decision, runFixture('longBullMismatch').strategy);
assert.ok(summary.includes('Regime Score'), 'summary should include score');
assert.ok(summary.includes('ALIGNED_REGIME_MISMATCH'), 'summary should include primary reason');

const overridden = runFixture('longBullStrong', { directionOverride: 'short_only' }).decision;
assert.equal(overridden.direction, 'short_only', 'manual direction override should be honored');

[
  'longBullStrong',
  'longBullMismatch',
  'longBearSurvival',
  'shortBearStrong',
  'shortBearMismatch',
  'sidewaysMeanRevert',
  'mixedUnknown',
  'missingSeries',
  'missingTimestamps',
  'fewTrades',
  'largeOrders',
  'noStrategy',
].forEach((fixtureName) => {
  assert.ok(Object.hasOwn(fixtures, fixtureName), `fixture missing: ${fixtureName}`);
});

console.log('sqx144 custom results8 regime edge analyzer contracts ok');
