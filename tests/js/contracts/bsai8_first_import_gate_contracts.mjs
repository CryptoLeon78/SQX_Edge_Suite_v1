import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_bsai_first_import_gate.ps1'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/BS_AI8_FIRST_IMPORT_GATE.md'), 'utf8');

[
  "bs-ai8-first-import-gate-v1",
  "ValidateSet('status', 'plan', 'approval-template')",
  "importAllowed = $false",
  "requiresOperatorApproval = $true",
  "writesSqxHost = $false",
  "writesDataDb = $false",
  "writesUserProjects = $false",
  "mutatesDatabanks = $false",
  "runsSqxTasks = $false",
  "localPathsReturned = $false",
  "approval_required_no_import",
  "operator_approval_template_only",
  "APRUEBO BS-AI8 IMPORT MANUAL CONTROLADA",
  "BS-AI9 manual import execution after explicit operator approval",
  "candidate_collides_with_official_manifest",
  "Test-ZipHasConfigXml",
].forEach((marker) => {
  assert.ok(script.includes(marker), `BS-AI8 gate script marker missing: ${marker}`);
});

[
  "bs-ai8-first-import-gate-v1",
  "checklist_ready_operator_approval_required_no_import",
  "BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005",
  "BS_Filtros_v7_H1",
  "explicit_base_preserve_official_v6_v7",
  "BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx",
  "BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa2.cfx",
  "requiresOperatorApproval=true",
  "writesSqxHost=false",
  "writesDataDb=false",
  "writesUserProjects=false",
  "mutatesDatabanks=false",
  "runsSqxTasks=false",
  "APRUEBO BS-AI8 IMPORT MANUAL CONTROLADA",
  "BS-AI9 manual import execution after explicit operator approval",
].forEach((marker) => {
  assert.ok(doc.includes(marker), `BS-AI8 phase doc marker missing: ${marker}`);
});

[
  'Copy-Item',
  'Move-Item',
  'Remove-Item',
  'Set-Content',
  'Add-Content',
  'Start-Process',
  'Stop-Process',
  'run_project',
  'Migration Tool allowed',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `BS-AI8 gate script must not contain ${forbidden}`);
});

assert.ok(!script.includes('user/projects'), 'script must not reference SQX user/projects path');
assert.ok(!script.includes('data.db'), 'script must not reference SQX data.db path');
assert.ok(!script.includes('144.2953 promotion'), 'script must not promote 144.2953');

console.log('bsai8 first import gate contracts ok');
