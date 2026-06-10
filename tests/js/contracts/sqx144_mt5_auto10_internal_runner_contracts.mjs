import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const docPath = path.join(repoRoot, 'docs/SQX144_MT5_AUTO10_INTERNAL_MT5_RUNNER.md');
const corePath = path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto10_internal_runner.py');
const wrapperPath = path.join(repoRoot, 'tools/sqx144_mt5_auto10_internal_runner.ps1');
const serverPath = path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py');

const doc = fs.readFileSync(docPath, 'utf8');
const core = fs.readFileSync(corePath, 'utf8');
const wrapper = fs.readFileSync(wrapperPath, 'utf8');
const server = fs.readFileSync(serverPath, 'utf8');

[
  'sqx144-mt5-auto10-internal-mt5-runner-v1',
  'auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'SQX144-MT5-AUTO10',
  'status|discover|preflight|plan|install-source|launch|stop|verify|approval-template',
  'APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER INSTALL host=sqx144_full mt5=darwinex no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER LAUNCH host=sqx144_full mt5=darwinex hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'sourceReadyNoLaunch=true',
  'autoStartAllowed=false',
  'launchesMt5AllowedByGate=false',
  'runsMt5EaAllowedByGate=false',
  'writesDataDb=false',
  'historyImportAllowed=false',
  '*_dukascopy',
  'AUTO7',
].forEach((marker) => {
  assert.ok(doc.includes(marker), `AUTO10 doc marker missing: ${marker}`);
});

[
  'SQX144_MT5_AUTO10_VERSION',
  'sqx144-mt5-auto10-internal-mt5-runner-v1',
  'AUTO10_INSTALL_APPROVAL_PHRASE',
  'AUTO10_LAUNCH_APPROVAL_PHRASE',
  'auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'def discover_payload',
  'def preflight_payload',
  'def plan_payload',
  'def install_source_payload',
  'def launch_payload',
  'def stop_payload',
  'def verify_payload',
  'DEFAULT_MT5_ROOT = Path("C:/Program Files/Darwinex MetaTrader 5")',
  'targetTerminalProcessRunning',
  'managedPidIsTargetTerminal',
  'apply: bool = False',
  'auto10_install_requires_exact_approval',
  'auto10_launch_requires_exact_approval',
  'stopsOnlyManagedAuto10Pid',
  'localPathsReturned',
  'writesDataDb',
  'historyImportAllowed',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO10 core marker missing: ${marker}`);
});

assert.ok(!core.includes('Darwinex MetaTrader 5 BEPB'), 'AUTO10 core must not default to Darwinex BEPB');

[
  'sqx144-mt5-auto10-internal-mt5-runner-v1',
  "ValidateSet('status', 'discover', 'preflight', 'plan', 'install-source', 'launch', 'stop', 'verify', 'approval-template')",
  'auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER INSTALL host=sqx144_full mt5=darwinex no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER LAUNCH host=sqx144_full mt5=darwinex hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'autoStartAllowed = $false',
  'writesDataDb = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'historyImportAllowed = $false',
  'usesDataSourceHistoryImport = $false',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO10 wrapper marker missing: ${marker}`);
});

[
  'from core import sqx144_mt5_auto10_internal_runner as mt5_auto10',
  '/api/sqx144/mt5-auto10/status',
  '/api/sqx144/mt5-auto10/preflight',
  '/api/sqx144/mt5-auto10/plan',
  '/api/sqx144/mt5-auto10/launch',
  '/api/sqx144/mt5-auto10/stop',
  '/api/sqx144/mt5-auto10/verify',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO10 server marker missing: ${marker}`);
});

[
  'DataSourceMt5Api/importData',
  'dataSourceMt5Api/importData',
  'UPDATE INSTRUMENTS',
  'sqlite3.connect',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'Add missing symbols',
  'Migration Tool allowed',
  'user/projects',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `AUTO10 core must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO10 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto10 internal runner contracts ok');
