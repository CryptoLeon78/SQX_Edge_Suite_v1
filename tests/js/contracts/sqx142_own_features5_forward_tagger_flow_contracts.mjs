import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const scriptPath = path.join(repoRoot, 'tools/sqx142_own_features_forward_tagger_flow.ps1');
const docPath = path.join(repoRoot, 'docs/SQX142_OWN_FEATURES_FORWARD_TAGGER_FLOW.md');
const script = fs.readFileSync(scriptPath, 'utf8');
const doc = fs.readFileSync(docPath, 'utf8');

assert.match(script, /\[ValidateSet\("status", "checklist", "validate-export", "record"\)\]/);
assert.match(script, /sqx142-own-features5-forward-tagger-flow-v1/);
assert.match(script, /SQXEdgeCorrelationTagger/);
assert.match(script, /Filter by results of custom analysis/);
assert.match(script, /SQX EDGE CORRELATION REVIEW/);
assert.match(script, /SQX Edge Corr Decision/);
assert.match(script, /SQX Edge Nearest Winner/);
assert.match(script, /correlation_decisions\.csv/);
assert.match(script, /latest_validate_export\.json/);
assert.match(script, /sqx_runtime_started_by_script = \$false/);
assert.match(script, /data_db_write_allowed = \$false/);
assert.match(script, /user_projects_write_allowed = \$false/);
assert.match(script, /databank_delete_allowed = \$false/);
assert.doesNotMatch(script, /Stop-Process/);
assert.doesNotMatch(script, /Start-Process/);
assert.doesNotMatch(script, /Remove-Item/);
assert.doesNotMatch(script, /Copy-Item/);
assert.doesNotMatch(script, /Set-Content[^\n]+SQX_142_Crack/i);
assert.doesNotMatch(script, /user\\projects[^\n]+Set-Content/i);

assert.match(doc, /SQX142-OWN-FEATURES5 Forward Tagger Repeatable Flow/);
assert.match(doc, /built_from_features4_pass_ready_for_reuse/);
assert.match(doc, /Export Forward\/Foward before using `SQXEdgeCorrelationTagger` as a filter/);
assert.match(doc, /Keep `Filter by results of custom analysis` disabled/);
assert.match(doc, /Data Smoke decisions: `portfolio=1`, `similar=22`, `review=0`/);
assert.match(doc, /Migration Tool/);
assert.doesNotMatch(doc, /guaranteed profitability/);
assert.doesNotMatch(doc, /risk zero/);
assert.doesNotMatch(doc, /run_project permitido/);

console.log('sqx142 own features5 forward tagger flow contracts ok');
