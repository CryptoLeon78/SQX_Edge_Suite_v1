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

const regimeBlocks = [
  { idx: 1, group: 'BULL' },
  { idx: 2, group: 'BULL' },
  { idx: 3, group: 'BEAR' },
  { idx: 4, group: 'BEAR' },
  { idx: 5, group: 'RANGE' },
  { idx: 6, group: 'RANGE' },
];

const strongOos = {
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'CAGR/Max DD': 3.0, Trades: 80 },
    2: { 'CAGR/Max DD': 2.8, Trades: 80 },
    3: { 'CAGR/Max DD': 1.2, Trades: 80 },
    4: { 'CAGR/Max DD': 1.1, Trades: 80 },
    5: { 'CAGR/Max DD': 1.2, Trades: 80 },
    6: { 'CAGR/Max DD': 1.1, Trades: 80 },
  },
};
const strongEgt = regime.assessEgtV2(strongOos, regimeBlocks);
assert.equal(strongEgt.verdict, 'STRONG');
assert.equal(strongEgt.label, 'COMPLIANT');
assert.equal(strongEgt.dominant_regime, 'BULL');
assert.equal(strongEgt.failed_regimes.length, 0);
assert.equal(strongEgt.insufficient_regimes.length, 0);
assert.equal(strongEgt.stats_by_regime.BULL.count, 2);
assert.ok(strongEgt.strong_by_regime.BULL);

const defensiveOos = {
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'CAGR/Max DD': 1.8 },
    2: { 'CAGR/Max DD': 1.7 },
    3: { 'CAGR/Max DD': 0.3 },
    4: { 'CAGR/Max DD': 0.2 },
    5: { 'CAGR/Max DD': 0.4 },
    6: { 'CAGR/Max DD': 0.3 },
  },
};
const defensiveEgt = regime.assessEgtV2(defensiveOos, regimeBlocks);
assert.equal(defensiveEgt.verdict, 'DEFENSIVE');
assert.equal(defensiveEgt.label, 'FLAT');
assert.equal(defensiveEgt.failed_regimes.length, 0);

const riskOos = {
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'CAGR/Max DD': 2.0 },
    2: { 'CAGR/Max DD': 1.8 },
    3: { 'CAGR/Max DD': -0.2 },
    4: { 'CAGR/Max DD': -0.1 },
    5: { 'CAGR/Max DD': 0.3 },
    6: { 'CAGR/Max DD': 0.2 },
  },
};
const riskEgt = regime.assessEgtV2(riskOos, regimeBlocks);
assert.equal(riskEgt.verdict, 'RISK');
assert.equal(riskEgt.label, 'RISK');
assert.deepEqual(Array.from(riskEgt.failed_regimes), ['BEAR']);

const insufficientEgt = regime.assessEgtV2(strongOos, regimeBlocks, {
  thresholds: { minBlocksPerRegime: 3 },
});
assert.equal(insufficientEgt.verdict, 'INSUFFICIENT');
assert.equal(insufficientEgt.evaluated_regimes.length, 0);
assert.deepEqual(Array.from(insufficientEgt.insufficient_regimes), ['BULL', 'BEAR', 'RANGE']);

const longShortEgt = regime.assessEgtV2(defensiveOos, regimeBlocks, {
  thresholds: { direction: 'long_short' },
});
assert.equal(longShortEgt.direction, 'long_short');
assert.equal(longShortEgt.verdict, 'RISK');
assert.ok(longShortEgt.failed_regimes.includes('BEAR'));

const shortOnlyEgt = regime.assessEgtV2({
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'CAGR/Max DD': 0.4 },
    2: { 'CAGR/Max DD': 0.3 },
    3: { 'CAGR/Max DD': 2.8 },
    4: { 'CAGR/Max DD': 2.6 },
    5: { 'CAGR/Max DD': 0.7 },
    6: { 'CAGR/Max DD': 0.6 },
  },
}, regimeBlocks, { thresholds: { direction: 'short_only' } });
assert.equal(shortOnlyEgt.direction, 'short_only');
assert.equal(shortOnlyEgt.verdict, 'STRONG');
assert.equal(shortOnlyEgt.thresholds.BEAR.strong, 2.5);

const coherentLong = regime.assessDirectionalCoherence({
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'Net Profit': 100 },
    2: { 'Net Profit': 120 },
    3: { 'Net Profit': 20 },
    4: { 'Net Profit': 10 },
    5: { 'Net Profit': 30 },
    6: { 'Net Profit': 25 },
  },
}, regimeBlocks, { direction: 'long_only' });
assert.equal(coherentLong.verdict, 'OK');
assert.equal(coherentLong.bull_check, 'OK');
assert.equal(coherentLong.direction, 'long_only');

const suspiciousLong = regime.assessDirectionalCoherence({
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'Net Profit': 40 },
    2: { 'Net Profit': 30 },
    3: { 'Net Profit': 180 },
    4: { 'Net Profit': 170 },
    5: { 'Net Profit': 30 },
    6: { 'Net Profit': 20 },
  },
}, regimeBlocks, { direction: 'long_only' });
assert.equal(suspiciousLong.verdict, 'SUSPICIOUS');
assert.ok(suspiciousLong.flags.includes('BEAR_SUSPICIOUS'));

const brokenLongShort = regime.assessDirectionalCoherence({
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'Net Profit': 60 },
    2: { 'Net Profit': 50 },
    3: { 'Net Profit': -20 },
    4: { 'Net Profit': -15 },
    5: { 'Net Profit': 10 },
    6: { 'Net Profit': 5 },
  },
}, regimeBlocks, { direction: 'long_short' });
assert.equal(brokenLongShort.verdict, 'BROKEN');
assert.ok(brokenLongShort.flags.includes('BROKEN_BEAR'));

const meanRevertShort = regime.assessDirectionalCoherence({
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'Net Profit': 100 },
    2: { 'Net Profit': 95 },
    3: { 'Net Profit': -20 },
    4: { 'Net Profit': 105 },
    5: { 'Net Profit': 110 },
    6: { 'Net Profit': 120 },
  },
}, [
  { idx: 1, group: 'RANGE' },
  { idx: 2, group: 'RANGE' },
  { idx: 3, group: 'BEAR' },
  { idx: 4, group: 'RANGE' },
  { idx: 5, group: 'RANGE' },
  { idx: 6, group: 'RANGE' },
], { direction: 'short_only' });
assert.equal(meanRevertShort.verdict, 'OK_MEAN_REVERT');
assert.ok(meanRevertShort.flags.includes('MEAN_REVERT_SHORT'));

const volPositive = regime.computeVolatilityCoherence({
  primary_metric: 'CAGR/Max DD',
  metrics_by_block: {
    1: { 'Net Profit': 10 },
    2: { 'Net Profit': 20 },
    3: { 'Net Profit': 30 },
    4: { 'Net Profit': 40 },
  },
}, [
  { idx: 1, group: 'RANGE', volatility: 0.05 },
  { idx: 2, group: 'RANGE', volatility: 0.10 },
  { idx: 3, group: 'RANGE', volatility: 0.15 },
  { idx: 4, group: 'RANGE', volatility: 0.20 },
], { minBlocks: 4 });
assert.equal(volPositive.verdict, 'VOL_POSITIVE');
assert.ok(volPositive.correlation > 0.9);

const minTradesEgt = regime.assessEgtV2(strongOos, regimeBlocks, { minTradesPerBlock: 100 });
assert.equal(minTradesEgt.verdict, 'UNKNOWN');
assert.ok(minTradesEgt.warnings.some(warning => warning.code === 'egt_v2_blocks_skipped_min_trades'));

console.log('champion challenger regime contracts ok');
