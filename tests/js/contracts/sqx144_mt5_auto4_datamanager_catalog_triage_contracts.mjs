import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const js = fs.readFileSync(path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/SQX144_MT5_AUTO4_DATAMANAGER_CATALOG_TRIAGE.md'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto2_data_manager_button_bridge.ps1'), 'utf8');

[
  'sqx144-mt5-auto4-datamanager-catalog-triage-v1',
  'sqx144-mt5-auto6-metadata-stability-policy-v1',
  'sqx144-mt5-auto6-datamanager-selection-guard-v1',
  'CATALOG_TRIAGE_VERSION',
  'AUTO6_STABILITY_VERSION',
  'SELECTION_GUARD_VERSION',
  'DEFAULT_BROKER',
  'catalogResult',
  'stabilityResult',
  'selectedSymbolFromEditDialog',
  'detectEditDialogSymbol',
  'isAllowedBareSymbol',
  'symbolFromSelectionItem',
  'WARRANTY',
  'allowLast === false',
  'selectedSymbolFromCheckedRows()',
  'requestBridge(resolved.symbol',
  'state.lastRequestId = ""',
  'bridgeContext',
  'symbol: bridgeContext.symbol || ""',
  'expectedRequestId: bridgeContext.requestId || ""',
  'expectedSymbol: bridgeContext.symbol || ""',
  'evaluateStability(bridgeContext).then',
  'resolvePlan',
  'auditCatalog',
  'resolveCatalogPlan',
  'evaluateStability',
  '/sqx144/mt5-auto3/catalog-audit',
  '/sqx144/mt5-auto3/resolve-plan',
  '/sqx144/mt5-auto3/bridge-validate',
  '/sqx144/mt5-auto6/evaluate',
  '/sqx144/mt5-auto2/request',
  'auto6_backend_endpoint_missing_restart_required',
  'auto3_backend_endpoint_missing_restart_required',
  'broker_missing',
  'ambiguous_collision',
  'waiting_for_requested_response',
  'latest_response_symbol_mismatch',
  'Stability policy',
  'Stability',
  'Future gate',
  'blocked_by_policy',
  'hold',
  'catalog_',
  'Plan',
  'Next',
].forEach((marker) => {
  assert.ok(js.includes(marker), `AUTO4 overlay marker missing: ${marker}`);
});

assert.ok(!js.includes('item.name ||'), 'AUTO4 overlay must validate item.name through candidateFromText before using it as a symbol');

[
  'sqx144-mt5-auto4-datamanager-catalog-triage-v1',
  'auto4_overlay_installed_verified_no_db_no_projects_no_databanks_no_tasks',
  'sqx144_mt5_auto2_button_20260609_080600',
  'targetHasAuto4=true',
  '9DB2D802252731284D122409C1C25C35B0934AD7DB81F53977631967D90DE194',
  'C09D5573B4CEC403EA522E14495F464338F8B8AD34D9A79B277E11EE9314CD06',
  '/api/sqx144/mt5-auto3/catalog-audit',
  '/api/sqx144/mt5-auto3/resolve-plan',
  '/api/sqx144/mt5-auto3/bridge-validate',
  '/api/sqx144/mt5-auto2/request',
  'importExecutionAllowed=false',
  'directDbHistoryInsertAllowed=false',
  'writesDataDb=false',
  'writesUserProjects=false',
  'mutatesDatabanks=false',
  'runsSqxTasks=false',
  'usesMigrationTool=false',
  'doesNotApplyToSqx=true',
  'doesNotApplyInstrumentConfig=true',
  'APRUEBO SQX144 MT5 AUTO4 DATAMANAGER TRIAGE INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks',
].forEach((marker) => {
  assert.ok(doc.includes(marker), `AUTO4 doc marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto4-datamanager-catalog-triage-v1',
  'Test-SourceHasAuto4',
  'Test-SourceHasAuto6',
  'Get-RequiredApprovalPhrase',
  'Test-SourceHasSelectionGuard',
  'Test-TargetHasSelectionGuard',
  'auto6_datamanager_selection_guard_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks',
  'sourceHasAuto4',
  'sourceHasAuto6',
  'sourceHasSelectionGuard',
  'targetHasSelectionGuard',
  'targetHasAuto6',
  'sqx144-mt5-auto6-metadata-stability-policy-v1',
  'auto6_datamanager_stability_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks',
  'APRUEBO SQX144 MT5 AUTO6 DATAMANAGER STABILITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import',
  'legacyApprovalTemplate',
  'APRUEBO SQX144 MT5 AUTO4 DATAMANAGER TRIAGE INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO4 wrapper marker missing: ${marker}`);
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
  'dataSourceMt5Api/importData',
].forEach((forbidden) => {
  assert.ok(!js.includes(forbidden), `AUTO4 overlay source must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto4 datamanager catalog triage contracts ok');
