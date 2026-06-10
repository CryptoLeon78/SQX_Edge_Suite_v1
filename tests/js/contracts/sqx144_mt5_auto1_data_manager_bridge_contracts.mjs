import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto1_data_manager_bridge.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_bridge.py'), 'utf8');
const mq5 = fs.readFileSync(path.join(repoRoot, 'integrations/sqx144/mt5_bridge/SQXInfoBridge.mq5'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/SQX144_MT5_AUTO1_DATA_MANAGER_MT5_BRIDGE.md'), 'utf8');

[
  "sqx144-mt5-auto1-data-manager-bridge-v1",
  "SQX144-MT5-AUTO1",
  "ValidateSet('status', 'request-template', 'write-request', 'install-source', 'validate-response')",
  "writesSqxHost = $false",
  "writesDataDb = $false",
  "writesUserProjects = $false",
  "mutatesDatabanks = $false",
  "runsSqxTasks = $false",
  "launchesMt5 = $false",
  "runsMt5Ea = $false",
  "usesMigrationTool = $false",
  "dataManagerButtonInstalled = $false",
  "defaultSpreadPolicy = 'p90'",
  "[switch]$Apply",
  "[switch]$Overwrite",
  "--overwrite",
  "core.sqx144_mt5_bridge",
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `SQX144 MT5 AUTO1 wrapper marker missing: ${marker}`);
});

[
  "sqx144-mt5-auto1-data-manager-bridge-v1",
  "SQX144-MT5-AUTO1",
  "DEFAULT_REQUEST_FILE = \"SQXInfoBridge.request.ini\"",
  "DEFAULT_RESPONSE_FILE = \"SQXInfoBridge.latest.json\"",
  "DEFAULT_SPREAD_POLICY = \"p90\"",
  "ALLOWED_SPREAD_POLICIES",
  "RESPONSE_SAFETY_FALSE_FLAGS",
  "unsafe_response_flag_",
  "unsafe_response_flag_missing_",
  "_require_allowed_apply_dir",
  "mt5_files_dir_not_allowed",
  "mt5_bridge_source_exists_requires_overwrite",
  "dataManagerButtonInstalled",
  "dataManagerButtonPlanned",
  "doesNotApplyToSqx",
].forEach((marker) => {
  assert.ok(core.includes(marker), `SQX144 MT5 AUTO1 core marker missing: ${marker}`);
});

[
  "sqx144-mt5-auto1-data-manager-bridge-v1",
  "SQXInfoBridge.request.ini",
  "SQXInfoBridge.latest.json",
  "OnTimer",
  "SymbolSelect",
  "ResolveMt5Symbol",
  "CopyRates",
  "mt5Symbol",
  "yearlySpreadStats",
  "p50",
  "p75",
  "p90",
  "p95",
  "p99",
  "writesSqxHost",
  "writesDataDb",
  "writesUserProjects",
  "mutatesDatabanks",
  "runsSqxTasks",
  "placesOrders",
  "usesMigrationTool",
].forEach((marker) => {
  assert.ok(mq5.includes(marker), `SQXInfoBridge.mq5 marker missing: ${marker}`);
});

[
  "sqx144-mt5-auto1-data-manager-bridge-v1",
  "SQX144-MT5-AUTO1",
  "real_mt5_response_validated_usdjpy_p90",
  "SQXInfoBridge.mq5",
  "SQXInfoBridge.request.ini",
  "SQXInfoBridge.latest.json",
  "sqx_auto1_usdjpy_20260608_194938",
  "USDJPY_Darwinex",
  "mt5Symbol=USDJPY",
  "spreadSamples=768790",
  "DEFAULTSPREAD=0.7",
  "POINTVALUE=624.30546",
  "TICKSIZE=0.01",
  "TICKSTEP=0.001",
  "bridge_response_validated",
  "p90",
  "p50",
  "p75",
  "p95",
  "p99",
  "writesDataDb=false",
  "writesUserProjects=false",
  "mutatesDatabanks=false",
  "runsSqxTasks=false",
  "usesMigrationTool=false",
  "No SQX DB mutation in SQX144-MT5-AUTO1 unless a separate DB mutation gate is opened and approved",
].forEach((marker) => {
  assert.ok(doc.includes(marker), `SQX144 MT5 AUTO1 doc marker missing: ${marker}`);
});

[
  'Start-Process',
  'terminal64.exe',
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'Add missing symbols',
  'Load without resolving these issues',
  'Migration Tool allowed',
  'UPDATE INSTRUMENTS',
  'INSERT INTO',
  'DELETE FROM',
  'Remove-Item',
  'Set-Content',
  'Add-Content',
  'Copy-Item',
  'Move-Item',
].forEach((forbidden) => {
  assert.ok(!wrapper.includes(forbidden), `SQX144 MT5 AUTO1 wrapper must not contain ${forbidden}`);
});

[
  'OrderSend',
  'trade.Buy',
  'trade.Sell',
  'ShellExecute',
  'WinExec',
].forEach((forbidden) => {
  assert.ok(!mq5.includes(forbidden), `SQXInfoBridge.mq5 must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto1 data manager bridge contracts ok');
