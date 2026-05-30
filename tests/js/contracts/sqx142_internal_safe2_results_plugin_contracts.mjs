import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const root = process.cwd();
const pluginDir = path.join(root, 'integrations', 'sqx142', 'results_plugins', 'SQX Edge Readiness Panel');
const indexPath = path.join(pluginDir, 'index.html');
const fixturesPath = path.join(pluginDir, 'fixtures', 'fixtures.js');
const scriptPath = path.join(root, 'tools', 'sqx142_internal_safe2_results_plugin_patch.ps1');

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const index = fs.readFileSync(indexPath, 'utf8');
const fixtures = fs.readFileSync(fixturesPath, 'utf8');
const script = fs.readFileSync(scriptPath, 'utf8');

[
  'sqx142-internal-safe2-readiness-panel-v1',
  'SQX_EDGE_READINESS_PANEL_VERSION',
  'window.__SQX_EDGE_PANEL__',
  'GET_STATS',
  'GET_LAST_SETTINGS_XML',
  'GET_SYMBOL_INFO',
  'user/extend/ResultsPlugins',
  'No engine, data.db, databank, project, license or runtime mutation.'
].forEach((marker) => assert(index.includes(marker), `missing index marker: ${marker}`));

[
  'window.SQX_EDGE_FIXTURES',
  'mock-ready-001',
  'mock-review-001',
  'mock-blocked-001',
  'SYMBOL_INFO_RESPONSE',
  'RExpectancy'
].forEach((marker) => assert(fixtures.includes(marker), `missing fixtures marker: ${marker}`));

[
  'SQX142-INTERNAL-SAFE2',
  'Assert-NoSqxProcess',
  'New-PluginBackup',
  'Install-Plugin',
  'Rollback-Plugin',
  'sqx142_internal_safe2_results_plugin_install_20260526_213000.json',
  'filesWrittenToSqx'
].forEach((marker) => assert(script.includes(marker), `missing script marker: ${marker}`));

const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(fixtures, sandbox);
assert(sandbox.window.SQX_EDGE_FIXTURES.ready.messages.length >= 3, 'ready fixture has insufficient messages');
assert(sandbox.window.SQX_EDGE_FIXTURES.review.messages[1].payload.NumberOfTrades === 44, 'review fixture drifted');
assert(sandbox.window.SQX_EDGE_FIXTURES.blocked.messages[1].payload.ProfitFactor < 1, 'blocked fixture must remain blocked');

console.log('sqx142 internal safe2 results plugin contracts ok');
