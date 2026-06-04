import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const scriptPath = path.join(repoRoot, 'tools/sqx142_own_features_correlation_manual_confirmation.ps1');
const docPath = path.join(repoRoot, 'docs/SQX142_OWN_FEATURES_CORRELATION_MANUAL_CONFIRMATION.md');
const script = fs.readFileSync(scriptPath, 'utf8');
const doc = fs.readFileSync(docPath, 'utf8');

assert.match(script, /\[ValidateSet\("status", "checklist", "record"\)\]/);
assert.match(script, /sqx142-own-features3-correlation-manual-confirmation-v1/);
assert.match(script, /SQX Edge Correlation Tagger/);
assert.match(script, /SQXEdgeCorrelationTagger/);
assert.match(script, /SQX EDGE CORRELATION REVIEW/);
assert.match(script, /correlation_decisions\.csv/);
assert.match(script, /readyForManualSmoke/);
assert.match(script, /manualConfirmationPending/);
assert.match(script, /latest_manual_record\.json/);
assert.match(script, /sqx_runtime_started_by_script = \$false/);
assert.match(script, /sqx_files_written_by_script = \$false/);
assert.doesNotMatch(script, /Stop-Process/);
assert.doesNotMatch(script, /Start-Process/);
assert.doesNotMatch(script, /Remove-Item/);
assert.doesNotMatch(script, /Copy-Item/);
assert.doesNotMatch(script, /Set-Content[^\n]+Crack/i);
assert.doesNotMatch(script, /user\\projects[^\n]+Set-Content/i);

assert.match(doc, /superseded_by_features4_features5_clean_path/);
assert.match(doc, /FEATURES3 is no longer an open blocker/);
assert.match(doc, /FEATURES4\/5 close the operational confirmation for the clean path/);
assert.match(doc, /SQX Edge Correlation Tagger/);
assert.match(doc, /SQXEdgeCorrelationTagger/);
assert.match(doc, /SQX EDGE CORRELATION REVIEW/);
assert.match(doc, /Tag CSV rows: `86`/);
assert.match(doc, /Edge Factory remains the canonical correlation decision engine/);
assert.doesNotMatch(doc, /preflight_ready_pending_operator_ui_confirmation/);
assert.doesNotMatch(doc, /guaranteed profitability/);
assert.doesNotMatch(doc, /run_project permitido/);
assert.doesNotMatch(doc, /Migration Tool permitido/);

console.log('sqx142 own features3 correlation manual confirmation contracts ok');
