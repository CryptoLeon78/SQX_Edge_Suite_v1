import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX, sandbox } = createLoadedSandbox([
  'app/js/modules/formatters.js',
  'app/js/modules/datasets.js',
  'app/js/modules/champion-challenger-regime.js',
]);

const growthSeries = Array.from({ length: 72 }, (_value, index) => 100 + index * 1.2);
const flatSeries = Array.from({ length: 72 }, (_value, index) => 100 + Math.sin(index / 2) * 0.5);
const riskSeries = Array.from({ length: 72 }, (_value, index) => index < 60 ? 140 - index * 0.4 : 116 - (index - 60) * 2.1);

sandbox.SQX_HISTORICAL_DATA = {
  EURUSD: { start: '2020-01', v: growthSeries },
  FLATX: { start: '2020-01', v: flatSeries },
  RISKX: { start: '2020-01', v: riskSeries },
  SHORTX: { start: '2024-01', v: [100, 101, 102] },
};
sandbox.SQX_SCORES_DATA = {
  EURUSD: { regimen: { objective: '+', composite_score: 0.67, scope: 'global' }, metrics: { regimen: { sma200_persistence_bars: 32, hurst_dist: 0.01 } } },
  FLATX: { regimen: { objective: '+', composite_score: 0.65, scope: 'global' }, metrics: { regimen: { sma200_persistence_bars: 30 } } },
  RISKX: { regimen: { objective: '-', composite_score: 0.22, scope: 'global' }, metrics: { regimen: { sma200_persistence_bars: 12 } } },
  SHORTX: { regimen: { objective: '+', composite_score: 0.7, scope: 'global' }, metrics: { regimen: {} } },
};

const regime = SQX.championChallengerRegime;
assert.ok(regime, 'champion challenger regime adapter should register');
assert.equal(regime.normalizeSymbol('eur/usd'), 'EURUSD');
assert.equal(regime.resolveSymbol('eur/usd').symbol, 'EURUSD');

const compliant = regime.assessSymbol('eur/usd');
assert.equal(compliant.label, 'COMPLIANT');
assert.equal(compliant.ok, true);
assert.equal(compliant.coverage_months, 72);
assert.equal(compliant.regime_objective, '+');
assert.match(regime.evidenceSummary(compliant), /COMPLIANT \| Reg \+ \| 12m \+/);

const flat = regime.assessSymbol('FLATX');
assert.equal(flat.label, 'FLAT');
assert.ok(flat.reasons.includes('flat_recent_trend'));

const risk = regime.assessSymbol('RISKX');
assert.equal(risk.label, 'RISK');
assert.ok(risk.reasons.includes('regime_score_below_threshold'));

const unknown = regime.assessSymbol('SHORTX');
assert.equal(unknown.label, 'UNKNOWN');
assert.ok(unknown.reasons.includes('coverage_below_threshold'));

const candidateEvidence = regime.assessCandidate({
  symbol: 'EURUSD',
  normalized_metrics: { symbol: 'EURUSD' },
});
assert.equal(candidateEvidence.label, 'COMPLIANT');

console.log('champion challenger regime contracts ok');
