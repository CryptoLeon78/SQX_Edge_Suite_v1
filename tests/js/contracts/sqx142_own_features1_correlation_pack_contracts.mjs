import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const packageRoot = path.join(repoRoot, 'integrations/sqx142/own_features/correlation_pack');
const scriptPath = path.join(repoRoot, 'tools/sqx142_own_features_correlation_pack.ps1');
const manifest = JSON.parse(fs.readFileSync(path.join(packageRoot, 'manifest.json'), 'utf8'));
const script = fs.readFileSync(scriptPath, 'utf8');
const tagger = fs.readFileSync(path.join(packageRoot, 'Snippets/SQ/CustomAnalysis/SQXEdgeCorrelationTagger.java'), 'utf8');
const view = fs.readFileSync(path.join(packageRoot, 'views/SQX EDGE CORRELATION REVIEW.vw'), 'utf8');
const sampleCsv = fs.readFileSync(path.join(packageRoot, 'samples/correlation_decisions.csv'), 'utf8');

assert.equal(manifest.version, 'sqx142-own-features1-correlation-pack-v1');
assert.equal(manifest.mode, 'lab-only');
assert.equal(manifest.defaultEnabled, false);
assert.deepEqual(manifest.tagCsvSchema, [
  'strategyRef',
  'candidateId',
  'decision',
  'reason',
  'score',
  'maxObservedCorrelation',
  'correlationStatus',
  'nearestWinnerId',
  'portfolioRank',
  'generatedAt',
  'version',
]);

[
  'SQXEdgeCorrelationTagger.java',
  'SQXEdgeCorrDecision.java',
  'SQXEdgeCorrRank.java',
  'SQXEdgeCorrScore.java',
  'SQXEdgeMaxCorr.java',
  'SQXEdgeCorrStatus.java',
  'SQXEdgeNearestWinner.java',
].forEach((filename) => {
  const matches = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      if (entry.isFile() && entry.name === filename) matches.push(full);
    }
  }
  walk(packageRoot);
  assert.equal(matches.length, 1, `${filename} should be packaged exactly once`);
});

[
  'SQXEdgeCorrDecision.java',
  'SQXEdgeCorrRank.java',
  'SQXEdgeCorrScore.java',
  'SQXEdgeMaxCorr.java',
  'SQXEdgeCorrStatus.java',
  'SQXEdgeNearestWinner.java',
].forEach((filename) => {
  const source = fs.readFileSync(path.join(packageRoot, 'Snippets/SQ/Columns/Databanks', filename), 'utf8');
  assert.match(source, /compute\(SQStats stats, StatsTypeCombination combination, OrdersList ordersList,\s*SettingsMap settings, SQStats statsLong, SQStats statsShort\) throws Exception/);
  assert.doesNotMatch(source, /compute\(ResultsGroup results, String resultKey/);
});

assert.match(tagger, /TYPE_FILTER_STRATEGY/);
assert.match(tagger, /return true;/);
assert.match(tagger, /SQX_EDGE_CORRELATION_TAG_CSV/);
assert.match(tagger, /System\.getProperty\("user\.dir"\)/);
assert.match(tagger, /"strategy_" \+ hex\.substring\(0, 16\)/);
assert.doesNotMatch(tagger, /return false;/);

[
  'SQXEdgeCorrDecision',
  'SQXEdgeCorrRank',
  'SQXEdgeCorrScore',
  'SQXEdgeMaxCorr',
  'SQXEdgeCorrStatus',
  'SQXEdgeNearestWinner',
].forEach((columnClass) => {
  assert.match(view, new RegExp(`class="${columnClass}"`));
});

assert.equal(sampleCsv.split(/\r?\n/)[0], manifest.tagCsvSchema.join(','));
assert.match(sampleCsv, /strategy_sample00000001/);
assert.doesNotMatch(sampleCsv, /AUDCAD_H4_A|MACD_A|Ivan|SQX_142_Crack/);

assert.match(script, /\[ValidateSet\("status", "install", "rollback"\)\]/);
assert.match(script, /Assert-NoSqxProcess/);
assert.doesNotMatch(script, /Stop-Process/);
assert.doesNotMatch(script, /Remove-Item\s+-Recurse/);
assert.match(script, /Get-FileHash -Algorithm SHA256/);
assert.match(script, /rollback_manifest\.json/);
assert.match(script, /user\\extend\\Snippets\\SQ\\CustomAnalysis/);
assert.match(script, /user\\extend\\Snippets\\SQ\\Columns\\Databanks/);
assert.match(script, /user\\settings\\views\\databanks/);
assert.match(script, /user\\extend\\SQXEdge\\Correlation/);
assert.doesNotMatch(script, /Copy-Item[^\n]+data\.db/i);
assert.doesNotMatch(script, /Copy-Item[^\n]+user\\projects/i);
assert.doesNotMatch(script, /Copy-Item[^\n]+plugins/i);

console.log('sqx142 own features correlation pack contracts ok');
