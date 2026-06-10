import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_auto6_metadata_stability.py'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_auto6_metadata_stability_policy.ps1'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/SQX144_MT5_AUTO6_METADATA_STABILITY_POLICY.md'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const overlay = fs.readFileSync(path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js'), 'utf8');

[
  'sqx144-mt5-auto6-metadata-stability-policy-v1',
  'mt5_metadata_stability_v1',
  'metadata_stability_observe_no_apply',
  'stability_policy_not_satisfied',
  'stable_drift_candidate_for_future_auto5',
  'eligible_metadata_update',
  'spreadHysteresisPips',
  'pointValueObserveThresholdPct',
  'auto3.bridge_validate_payload',
  'futureApplyGateAllowed',
  'applyApprovalReturned',
].forEach((marker) => {
  assert.ok(core.includes(marker), `AUTO6 core marker missing: ${marker}`);
});

[
  "[ValidateSet('status', 'evaluate', 'decision-template')]",
  'sqx144-mt5-auto6-metadata-stability-policy-v1',
  'writesDataDb = $false',
  'writesUserProjects = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'usesMigrationTool = $false',
  'directDbHistoryInsertAllowed = $false',
  'applyAllowed = $false',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `AUTO6 wrapper marker missing: ${marker}`);
});

[
  'sqx144-mt5-auto6-metadata-stability-policy-v1',
  'SQX144-MT5-AUTO6',
  'mt5_metadata_stability_v1',
  'metadata_stability_observe_no_apply',
  'stability_insufficient_coverage',
  'stability_policy_not_satisfied',
  'eligible_metadata_update',
  'DEFAULTSPREAD=1.3',
  'POINTVALUE=71753.512334',
  'DEFAULTSPREAD=1.2',
  'POINTVALUE=71659.930633',
  'writesDataDb=false',
  'writesUserProjects=false',
  'mutatesDatabanks=false',
  'runsSqxTasks=false',
  'usesMigrationTool=false',
  'directDbHistoryInsertAllowed=false',
].forEach((marker) => {
  assert.ok(doc.includes(marker), `AUTO6 doc marker missing: ${marker}`);
});

[
  '/api/sqx144/mt5-auto6/status',
  '/api/sqx144/mt5-auto6/evaluate',
  'mt5_auto6.status_payload',
  'mt5_auto6.evaluate_payload',
  '_require_sqx142_local_operator(mt5_auto6.SQX144_MT5_AUTO6_VERSION)',
].forEach((marker) => {
  assert.ok(server.includes(marker), `AUTO6 server marker missing: ${marker}`);
});

[
  'AUTO6_STABILITY_VERSION',
  'SELECTION_GUARD_VERSION',
  'sqx144-mt5-auto6-datamanager-selection-guard-v1',
  'sqx144-mt5-auto6-metadata-stability-policy-v1',
  '/sqx144/mt5-auto6/evaluate',
  'state.stabilityResult',
  'selectedSymbolFromEditDialog',
  'isAllowedBareSymbol',
  'symbolFromSelectionItem',
  'WARRANTY',
  'requestBridge(symbolOverride, options)',
  'state.lastRequestId = ""',
  'bridgeContext',
  'expectedRequestId: bridgeContext.requestId || ""',
  'evaluateStability(bridgeContext).then',
  'evaluateStability',
  'Stability policy',
  'Future gate',
  'blocked_by_policy',
  'hold',
].forEach((marker) => {
  assert.ok(overlay.includes(marker), `AUTO6 overlay marker missing: ${marker}`);
});

[
  'UPDATE INSTRUMENTS',
  'INSERT INTO',
  'DELETE FROM',
  'ALTER TABLE',
  'DROP TABLE',
  'BEGIN IMMEDIATE',
  '_connect_write',
  'commit()',
  'backup_payload',
  'apply_payload',
  'rollback_payload',
  '--apply',
  '-Apply',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Set-Content',
  'Out-File',
  'Start-Process',
  'Stop-Process',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'loadAsIs',
  'Add missing symbols',
  'DataSourceMt5Api/importData',
  'bridge_csv_file_mass_import',
  'Migration Tool allowed',
  'user/projects',
  'APRUEBO SQX144 MT5 AUTO5 METADATA APPLY',
].forEach((forbidden) => {
  assert.ok(!core.includes(forbidden), `AUTO6 core must not contain ${forbidden}`);
  assert.ok(!wrapper.includes(forbidden), `AUTO6 wrapper must not contain ${forbidden}`);
  assert.ok(!overlay.includes(forbidden), `AUTO6 overlay must not contain ${forbidden}`);
});

console.log('sqx144 mt5 auto6 metadata stability contracts ok');
