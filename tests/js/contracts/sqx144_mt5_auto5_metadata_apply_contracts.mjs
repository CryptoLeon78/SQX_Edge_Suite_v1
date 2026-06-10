import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto5_metadata_apply.py'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto5_metadata_apply_gate.ps1'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/SQX144_MT5_AUTO5_METADATA_APPLY_GATE.md'), 'utf8');

[
  'sqx144-mt5-auto5-metadata-apply-gate-v1',
  'auto5_metadata_apply_gate_ready_bridge_json_no_apply',
  'APPROVED_COLUMNS = ("DEFAULTSPREAD", "POINTVALUE", "TICKSIZE", "TICKSTEP")',
  'auto3.bridge_validate_payload',
  'metadata_apply_requires_separate_exact_gate',
  'no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool',
  'UPDATE INSTRUMENTS SET',
  'BROKER_ID',
  'apply_blocked_bad_approval',
  'sqx_processes_must_be_zero',
  'rollback_restored_known_auto5_backup',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO5 core marker missing: ${marker}`);
});

[
  "[ValidateSet('status', 'audit', 'plan', 'backup', 'apply', 'verify', 'rollback')]",
  'sqx144-mt5-auto5-metadata-apply-gate-v1',
  'writesDataDb = $Action -eq',
  'writesUserProjects = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'usesMigrationTool = $false',
  'directDbHistoryInsertAllowed = $false',
  'offlineApplyOnly = $true',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO5 wrapper marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto5-metadata-apply-gate-v1',
  'auto5_metadata_apply_gate_ready_bridge_json_no_apply',
  'AUDCAD_darwinex',
  'sqx_auto2_AUDCAD_Darwinex_20260609_064421',
  'efec3ee2fb53d00e1644a6b96a7b9ea2d0c30022112e743f39df1f10ec5d2b17',
  'fields=DEFAULTSPREAD,POINTVALUE',
  'writesUserProjects=false',
  'mutatesDatabanks=false',
  'runsSqxTasks=false',
  'usesMigrationTool=false',
  'directDbHistoryInsertAllowed=false',
].forEach((marker) => {
  assert.ok(doc.includes(marker), `AUTO5 doc marker missing: ${marker}`);
});

[
  'user/projects',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'Add missing symbols',
  'loadAsIs',
  'DataSourceMt5Api/importData',
  'bridge_csv_file_mass_import',
  'Migration Tool allowed',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `AUTO5 core must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO5 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto5 metadata apply contracts ok');
