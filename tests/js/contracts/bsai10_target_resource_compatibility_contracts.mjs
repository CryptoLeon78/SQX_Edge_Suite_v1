import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai_resource_compat_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/bsai_resource_compatibility.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI10_TARGET_RESOURCE_COMPATIBILITY_GATE.md'), 'utf8');

[
  "bs-ai10-target-resource-compatibility-gate-v1",
  "ValidateSet('status', 'audit', 'remap')",
  "writesSqxHost = $false",
  "writesDataDb = $false",
  "writesUserProjects = $false",
  "mutatesDatabanks = $false",
  "runsSqxTasks = $false",
  "readOnlyDataDb = $true",
  "noAutoImport = $true",
  "core.bsai_resource_compatibility",
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI10 wrapper marker missing: ${marker}`);
});

[
  "bs-ai10-target-resource-compatibility-gate-v1",
  "sqlite_uri_mode_ro_query_only",
  "target_symbol_missing_in_sqx144_catalog",
  "primary_resource_mismatch_for_sqx144_full",
  "methodology_cross_broker_catalog_match",
  "regenerate_with_target_profile_sqxedge_darwinex",
  "remap_ready_for_manual_import_gate_no_import",
  "localPathsReturned",
  "rawXmlReturned",
].forEach((marker) => {
  assert.ok(core.includes(marker), `BS-AI10 core marker missing: ${marker}`);
});

[
  "bs-ai10-target-resource-compatibility-gate-v1",
  "remap_ready_for_manual_import_gate_no_import",
  "AUDCAD_darwinex",
  "AUDCAD_dukascopy",
  "BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx",
  "BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx",
  "BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx",
  "writesSqxHost=false",
  "writesDataDb=false",
  "writesUserProjects=false",
  "mutatesDatabanks=false",
  "runsSqxTasks=false",
  "BS-AI11 remapped manual import gate",
].forEach((marker) => {
  assert.ok(doc.includes(marker), `BS-AI10 doc marker missing: ${marker}`);
});

[
  'Start-Process',
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Set-Content',
  'Add-Content',
  'Load without resolving these issues',
  'Add missing symbols',
  'run_project',
  'Migration Tool allowed',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI10 wrapper must not contain ${forbidden}`);
});

console.log('bsai10 target resource compatibility contracts ok');
