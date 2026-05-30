import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const psPath = path.join(repoRoot, 'tools/sqx142_own_features_correlation_data_smoke.ps1');
const pyPath = path.join(repoRoot, 'backend/sqx-edge-tool/tools/sqx142_correlation_data_smoke.py');
const sourceSamplePath = path.join(repoRoot, 'integrations/sqx142/own_features/correlation_pack/samples/correlation_source_rows.csv');
const ps = fs.readFileSync(psPath, 'utf8');
const py = fs.readFileSync(pyPath, 'utf8');
const sample = fs.readFileSync(sourceSamplePath, 'utf8');

assert.match(py, /DATA_SMOKE_VERSION = "sqx142-own-features2-correlation-data-smoke-v1"/);
assert.match(py, /export_correlation_filter_sqx_tag_csv/);
assert.match(py, /"c2TemplateRank"/);
assert.match(py, /"decisionDomain"/);
assert.match(py, /"raw_strategy_names_returned": False/);
assert.match(py, /"tag_csv_only": True/);
assert.doesNotMatch(py, /data\.db|user\/projects|run_project|Stop-Process/);

assert.match(ps, /\[ValidateSet\("status", "build", "install", "rollback"\)\]/);
assert.match(ps, /Assert-NoSqxProcess/);
assert.match(ps, /correlation_decisions\.csv/);
assert.match(ps, /Get-FileHash -Algorithm SHA256/);
assert.match(ps, /rollback_manifest\.json/);
assert.match(ps, /Data smoke can only target correlation_decisions\.csv/);
assert.doesNotMatch(ps, /Stop-Process/);
assert.doesNotMatch(ps, /Remove-Item\s+-Recurse/);
assert.doesNotMatch(ps, /Copy-Item[^\n]+data\.db/i);
assert.doesNotMatch(ps, /Copy-Item[^\n]+user\\projects/i);
assert.doesNotMatch(ps, /Copy-Item[^\n]+jars/i);
assert.doesNotMatch(ps, /Copy-Item[^\n]+plugins/i);

assert.match(sample.split(/\r?\n/)[0], /strategy,asset,timeframe/);
assert.match(sample, /returnSeries/);

console.log('sqx142 own features2 correlation data smoke contracts ok');
