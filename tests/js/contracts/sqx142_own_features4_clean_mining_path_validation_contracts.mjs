import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const scriptPath = path.join(repoRoot, 'tools/sqx142_own_features_clean_mining_path_validation.ps1');
const docPath = path.join(repoRoot, 'docs/SQX142_OWN_FEATURES_CLEAN_MINING_PATH_VALIDATION.md');
const script = fs.readFileSync(scriptPath, 'utf8');
const doc = fs.readFileSync(docPath, 'utf8');

assert.match(script, /\[ValidateSet\("status", "checklist", "record"\)\]/);
assert.match(script, /sqx142-own-features4-clean-mining-path-validation-v1/);
assert.match(script, /prepared_readonly_preflight_green_pending_operator_clean_mining/);
assert.match(script, /latest_manual_record\.json/);
assert.match(script, /statusMarker = \$statusMarker/);
assert.match(script, /Use SQX142-OWN-FEATURES5 Forward Tagger Repeatable Flow/);
assert.match(script, /sqx142_project_load_stabilizer\.ps1/);
assert.match(script, /sqx142_own_features_correlation_data_smoke\.ps1/);
assert.match(script, /sqx142_own_features_correlation_lab_project_scaffold\.ps1/);
assert.match(script, /SQX EDGE CORRELATION REVIEW/);
assert.match(script, /ExitAfterDays/);
assert.match(script, /latest_manual_record\.json/);
assert.match(script, /sqx_runtime_started_by_script = \$false/);
assert.match(script, /data_db_write_allowed = \$false/);
assert.match(script, /retired_dependency_placeholder_allowed = \$false/);
assert.doesNotMatch(script, /Stop-Process/);
assert.doesNotMatch(script, /Start-Process/);
assert.doesNotMatch(script, /Remove-Item/);
assert.doesNotMatch(script, /Copy-Item/);
assert.doesNotMatch(script, /Set-Content[^\n]+SQX_142_Crack/i);
assert.doesNotMatch(script, /user\\projects[^\n]+Set-Content/i);

assert.match(doc, /SQX142-OWN-FEATURES4 Clean Mining Path Validation/);
assert.match(doc, /Status: `pass`/);
assert.match(doc, /Final visual\/export confirmation/);
assert.match(doc, /SQXEdgeCorrelationTagger/);
assert.match(doc, /Filter by results of custom analysis/);
assert.match(doc, /SQX Edge \/ Darwinex/);
assert.match(doc, /correlation_decisions\.csv/);
assert.match(doc, /ExitAfterDays/);
assert.match(doc, /Migration Tool/);
assert.doesNotMatch(doc, /risk zero guaranteed/);
assert.doesNotMatch(doc, /guaranteed profitability/);
assert.doesNotMatch(doc, /run_project permitido/);
assert.doesNotMatch(doc, /Migration Tool permitido/);

console.log('sqx142 own features4 clean mining path validation contracts ok');
