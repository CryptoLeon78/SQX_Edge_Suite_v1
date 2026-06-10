import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto3_broker_catalog.py'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto3_broker_catalog.ps1'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const darwinex = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/mt5_broker_catalog/darwinex.json'), 'utf8');
const axi = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/mt5_broker_catalog/axi.planned.json'), 'utf8');

[
  'sqx144-mt5-auto3-broker-catalog-resolver-v1',
  'SQX144-MT5-AUTO3',
  'opened_broker_catalog_resolver_readonly_design_no_import_no_apply_no_projects_no_databanks_no_tasks',
  'sqlite_uri_mode_ro_query_only',
  'PRAGMA query_only = ON',
  'ready_existing',
  'metadata_diff_only',
  'instrument_missing',
  'history_missing',
  'broker_missing',
  'ambiguous_collision',
  'native_datamanager_mt5_import',
  'dataSourceMt5Api/importData',
  'bridge_csv_file_mass_import',
  'directDbHistoryInsertAllowed',
  'importExecutionAllowed',
  'no_projects_no_databanks_no_tasks',
  'writesDataDb',
  'writesUserProjects',
  'mutatesDatabanks',
  'runsSqxTasks',
  'usesMigrationTool',
  'doesNotApplyToSqx',
  'doesNotApplyInstrumentConfig',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO3 core marker missing: ${marker}`);
});

[
  "ValidateSet('status', 'catalog-audit', 'bridge-validate', 'resolve-plan', 'import-plan', 'approval-template')",
  'sqx144-mt5-auto3-broker-catalog-resolver-v1',
  'core.sqx144_mt5_auto3_broker_catalog',
  'readOnlyDataDb = $true',
  'writesDataDb = $false',
  'writesUserProjects = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'usesMigrationTool = $false',
  'doesNotApplyToSqx = $true',
  'doesNotApplyInstrumentConfig = $true',
  'importExecutionAllowed = $false',
  'directDbHistoryInsertAllowed = $false',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO3 wrapper marker missing: ${marker}`);
});

[
  '/api/sqx144/mt5-auto3/status',
  '/api/sqx144/mt5-auto3/catalog-audit',
  '/api/sqx144/mt5-auto3/bridge-validate',
  '/api/sqx144/mt5-auto3/resolve-plan',
  '/api/sqx144/mt5-auto3/import-plan',
  'mt5_auto3.catalog_audit_payload',
  'mt5_auto3.resolve_plan_payload',
  'mt5_auto3.import_plan_payload',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO3 server marker missing: ${marker}`);
});

[
  '"brokerKey": "darwinex"',
  '"expectedBrokerId": 4',
  '"expectedSourceId": 4',
  '"postfix": "_darwinex"',
  '"spreadPolicy": "p90"',
  '"preferredNativeEndpoint": "dataSourceMt5Api/importData"',
  '"directDbHistoryInsertAllowed": false',
].forEach((marker) => {
  assert.ok(darwinex.includes(marker), `AUTO3 Darwinex config marker missing: ${marker}`);
});

[
  '"brokerKey": "axi"',
  '"expectedBrokerId": null',
  '"expectedSourceId": null',
  '"requiresDiscovery": true',
  '"allowImportExecution": false',
].forEach((marker) => {
  assert.ok(axi.includes(marker), `AUTO3 Axi config marker missing: ${marker}`);
});

[
  'UPDATE INSTRUMENTS',
  'INSERT INTO',
  'DELETE FROM',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Set-Content',
  'Start-Process',
  'Stop-Process',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'loadAsIs',
  'Add missing symbols',
  'Migration Tool allowed',
  'user/projects',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `AUTO3 core must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO3 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto3 broker catalog contracts ok');
