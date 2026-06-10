import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const docPath = path.join(repoRoot, 'docs/SQX144_MT5_AUTO11_EA_ATTACH_RUNNER.md');
const corePath = path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto11_ea_attach_runner.py');
const wrapperPath = path.join(repoRoot, 'tools/sqx144_mt5_auto11_ea_attach_runner.ps1');
const serverPath = path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py');

const doc = fs.readFileSync(docPath, 'utf8');
const core = fs.readFileSync(corePath, 'utf8');
const wrapper = fs.readFileSync(wrapperPath, 'utf8');
const server = fs.readFileSync(serverPath, 'utf8');

[
  'sqx144-mt5-auto11-ea-attach-runner-v1',
  'auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'auto11_attach_profile_writer_implemented_no_apply_no_ui_fallback_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'SQX144-MT5-AUTO11',
  'status|profile-catalog|preflight|plan|attach-plan|ui-fallback-plan|approval-template',
  'APRUEBO SQX144 MT5 AUTO11 EA ATTACH RUNNER APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO11 UI FALLBACK APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 visible_operator_control no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'genericMt5SqxProfileAware=true',
  'attachAllowedByGate=false',
  'writesMt5Profile=false',
  'writesMt5Template=false',
  'writesMt5StartupConfig=false',
  'runsMt5Ea=false',
  'SQX_AUTO11_SQXInfoBridge.tpl',
  'auto11_attach_profile_writer_completed_ready_for_profile_launch',
  'auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback',
  'auto11_ui_fallback_plan_ready_separate_gate_required',
  'auto11_ui_fallback_completed_bridge_ready',
  'auto11_ui_fallback_apply_visible_operator_control_completed',
  '*_dukascopy',
  'AUTO7 mirror/no-MT5',
].forEach((marker) => {
  assert.ok(doc.includes(marker), `AUTO11 doc marker missing: ${marker}`);
});

[
  'SQX144_MT5_AUTO11_VERSION',
  'SQX144_MT5_AUTO11_PROFILE_WRITER_STATUS',
  'sqx144-mt5-auto11-ea-attach-runner-v1',
  'AUTO11_ATTACH_APPROVAL_PHRASE',
  'AUTO11_UI_FALLBACK_APPROVAL_PHRASE',
  'auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'def profile_catalog_payload',
  'def preflight_payload',
  'def plan_payload',
  'def attach_plan_payload',
  'def ui_fallback_plan_payload',
  'def status_payload',
  'def _write_profile_assets',
  'def _chart_text',
  'def _startup_config_text',
  'genericMt5SqxProfileAware',
  'template_profile_autoload_then_auto10_heartbeat_verify',
  'auto11_attach_requires_exact_approval',
  'auto11_attach_profile_writer_completed_ready_for_profile_launch',
  'auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback',
  'auto11_ui_fallback_requires_exact_approval',
  'auto11_ui_fallback_completed_bridge_ready',
  'auto11_ui_fallback_apply_visible_operator_control_completed',
  'SQX_AUTO11_SQXInfoBridge.tpl',
  'writesMt5StartupConfig',
  'writesDataDb',
  'historyImportAllowed',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO11 core marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto11-ea-attach-runner-v1',
  "ValidateSet('status', 'profile-catalog', 'preflight', 'plan', 'attach-plan', 'ui-fallback-plan', 'approval-template')",
  'auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO11 EA ATTACH RUNNER APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'APRUEBO SQX144 MT5 AUTO11 UI FALLBACK APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 visible_operator_control no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool',
  'genericMt5SqxProfileAware = $true',
  'writesMt5Profile = $false',
  'writesMt5Template = $false',
  'writesMt5StartupConfig = $false',
  'uiFallbackAllowedByGate = $false',
  'runsMt5Ea = $false',
  'historyImportAllowed = $false',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO11 wrapper marker missing: ${marker}`);
});

[
  'from core import sqx144_mt5_auto11_ea_attach_runner as mt5_auto11',
  '/api/sqx144/mt5-auto11/status',
  '/api/sqx144/mt5-auto11/profile-catalog',
  '/api/sqx144/mt5-auto11/preflight',
  '/api/sqx144/mt5-auto11/plan',
  '/api/sqx144/mt5-auto11/attach-plan',
  '/api/sqx144/mt5-auto11/ui-fallback-plan',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO11 server marker missing: ${marker}`);
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
  assert.ok(!core.includes(forbidden), `AUTO11 core must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO11 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto11 ea attach runner contracts ok');
