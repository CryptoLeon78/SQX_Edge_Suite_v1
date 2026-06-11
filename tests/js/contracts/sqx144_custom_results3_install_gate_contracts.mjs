import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const core = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'core', 'sqx144_custom_results3_install_gate.py'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools', 'sqx144_custom_results3_install_gate.ps1'), 'utf8');
const pyTest = fs.readFileSync(path.join(repoRoot, 'backend', 'sqx-edge-tool', 'test_sqx144_custom_results3_install_gate.py'), 'utf8');
const docPath = path.join(repoRoot, 'docs', 'SQX144_CUSTOM_RESULTS3_OPTIONAL_MANUAL_INSTALL_GATE.md');
const doc = fs.readFileSync(docPath, 'utf8');
const readme = fs.readFileSync(path.join(repoRoot, 'README.md'), 'utf8');
const governance = fs.readFileSync(path.join(repoRoot, 'docs', 'PROJECT_GOVERNANCE.md'), 'utf8');
const roadmap = fs.readFileSync(path.join(repoRoot, 'docs', 'SQX144_LAB_INTAKE_ROADMAP.md'), 'utf8');
const changelog = fs.readFileSync(path.join(repoRoot, 'CHANGELOG.md'), 'utf8');
const manifest = fs.readFileSync(path.join(repoRoot, 'docs', 'state_consistency_manifest.json'), 'utf8');
const docsIndex = fs.readFileSync(path.join(repoRoot, 'docs', 'DOCS_CANONICAL_INDEX.md'), 'utf8');

const phaseMarkers = [
  'SQX144-CUSTOM-RESULTS3 - Optional Manual Install Gate',
  'sqx144-custom-results3-optional-manual-install-gate-v1',
  'custom_results3_all_modules_manual_install_completed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool',
  'SQX Edge Custom Results All Modules',
  'integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules',
  'sqx144_full/user/extend/ResultsPlugins/SQX Edge Custom Results All Modules',
  'tools/sqx144_custom_results3_install_gate.ps1',
  'tests/js/contracts/sqx144_custom_results3_install_gate_contracts.mjs',
  'APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code',
  'GET_ORDERS remains privacy/performance-gated',
  'rawOrdersReturnedByTooling=false',
  'installExecuted=true',
  'copiedFiles=3',
  'targetMatchesSource=true',
  '4749A8393AE4418B0121962360C47B637031F171B7078EDFC93FC345B2B5077C',
  'backupCreated=false',
  'No SQX runtime',
  'no data.db',
  'no user/projects',
  'no databank mutation',
  'no tasks',
  'no Migration Tool',
  'downloaded third-party',
];

[
  "ValidateSet('status', 'preflight', 'plan', 'install', 'rollback', 'approval-template', 'report')",
  '$Apply',
  '$Approval',
  '$BackupId',
  'core.sqx144_custom_results3_install_gate',
  '--apply',
  '--approval',
  '--backup-id',
  '--write-evidence',
  'localPathsReturned',
  'rawOrdersReturnedByTooling',
].forEach((marker) => {
  assert.ok(wrapper.includes(marker), `CUSTOM-RESULTS3 wrapper marker missing: ${marker}`);
});

[
  'SQX144_CUSTOM_RESULTS3_VERSION',
  'SQX144_CUSTOM_RESULTS3_PHASE_LABEL',
  'INSTALL_APPROVAL_PHRASE',
  'ROLLBACK_APPROVAL_PHRASE',
  'EXPECTED_ROOT_NAME = "SQX_144_Full"',
  'SOURCE_PLUGIN_RELATIVE',
  'TARGET_PLUGIN_REF',
  'preflight_payload',
  'plan_payload',
  'install_payload',
  'rollback_payload',
  'approval_template_payload',
  '_require_install_approval',
  '_require_rollback_approval',
  '_assert_safe_install_paths',
  '_file_manifest',
  '_combined_manifest_hash',
  'copiesDownloadedThirdPartyPlugins',
  'copiesSqxEdgeOwnedBundleOnly',
  'get_orders_runtime_acknowledged',
  'rawOrdersReturnedByTooling',
  'target_plugin_exists_without_sqx_edge_marker',
  'sqx_or_java_process_running',
].forEach((marker) => {
  assert.ok(core.includes(marker), `CUSTOM-RESULTS3 core marker missing: ${marker}`);
});

[
  'test_status_declares_optional_manual_install_gate_without_host_mutation',
  'test_preflight_ready_when_source_and_fake_host_are_clean',
  'test_preflight_blocks_running_sqx_process_and_wrong_target_marker',
  'test_plan_contains_hash_manifest_and_exact_approval_without_paths',
  'test_install_dry_run_does_not_copy_to_fake_host',
  'test_install_apply_requires_exact_approval',
  'test_install_apply_with_exact_approval_copies_only_to_temp_host',
  'test_rollback_dry_run_requires_backup_id',
].forEach((marker) => {
  assert.ok(pyTest.includes(marker), `CUSTOM-RESULTS3 pytest marker missing: ${marker}`);
});

[
  doc,
  readme,
  governance,
  roadmap,
  changelog,
  manifest,
].forEach((content, indexNumber) => {
  phaseMarkers.forEach((marker) => {
    assert.ok(content.includes(marker), `CUSTOM-RESULTS3 tracked content ${indexNumber} missing: ${marker}`);
  });
});

[
  'docs/SQX144_CUSTOM_RESULTS3_OPTIONAL_MANUAL_INSTALL_GATE.md',
  'SQX144_CUSTOM_RESULTS3_OPTIONAL_MANUAL_INSTALL_GATE',
].forEach((marker) => {
  assert.ok(manifest.includes(marker) || docsIndex.includes(marker) || doc.includes(marker), `CUSTOM-RESULTS3 canonical marker missing: ${marker}`);
});

[
  'GET_SOURCE_CODE permitido',
  'GET_ORDERS permitido por defecto',
  'ORDERS_RESPONSE live by default',
  'downloads third-party plugin installed',
  'downloaded third-party ZIP direct install allowed',
  'launch SQX 144 now',
  'migrate active data into 144 automatically',
  'bulk copy Build 144 internals',
  'CUSTOM-RESULTS3 profit guarantee',
  'CUSTOM-RESULTS3 risk zero',
  'CUSTOM-RESULTS3 Results=passed',
  'writes data.db',
  'mutates user/projects',
  'mutates databanks',
  'uses Migration Tool',
].forEach((forbidden) => {
  [doc, readme, governance, roadmap, changelog].forEach((content, indexNumber) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS3 public content ${indexNumber} must not contain ${forbidden}`);
  });
});

[
  'C:\\Users\\',
  'C:/Users/',
  'licenseMaterialReturned": true',
  'rawOrdersReturned": true',
  'rawOrdersReturnedByTooling": true',
  'localPathsReturned": true',
].forEach((forbidden) => {
  [doc, wrapper].forEach((content, indexNumber) => {
    assert.ok(!content.includes(forbidden), `CUSTOM-RESULTS3 privacy content ${indexNumber} must not contain ${forbidden}`);
  });
});

console.log('sqx144 custom results3 install gate contracts ok');
