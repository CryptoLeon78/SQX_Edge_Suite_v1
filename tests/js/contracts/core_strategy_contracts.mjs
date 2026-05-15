import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX } = createLoadedSandbox();

assert.equal(SQX.formatters.ratingLabel('++').text, 'Estrella');
assert.equal(SQX.formatters.metricClass('PF', 1.6), 'pos');
assert.equal(SQX.formatters.formatNumber('12.345', 1), '12.3');
assert.equal(SQX.formatters.escapeHtml('<x>'), '&lt;x&gt;');

const asset = {
  cats: {
    tendencia: { rating: '++', dir: 'L' },
    momentum: { rating: '+', dir: 'S' },
  }
};
const score = SQX.domain.calcScore(asset, 'all', { '++': 3, '+': 2, '~': 1, '-': 0 });
assert.equal(score.raw, 5);
assert.equal(score.count, 2);
assert.equal(score.norm, 83);
assert.equal(SQX.domain.assetMatchesSqxFilter({ cats: { trend: { dir: 'L' } } }, 'C'), true);
assert.equal(SQX.domain.tfMatch('M15,H1', 'H1'), true);

const manual = SQX.strategies.manualStrategyFromValues({
  id: '17.000001',
  name: 'EMA + MACD',
  mining: '17',
  asset: 'EURUSD',
  tf: 'H1',
  blocksetting: 'BS_Tendencia_v4',
  template: 'PHASE17',
  direction: 'L',
  indicators: 'EMA, MACD',
  exits: 'ATR',
  netProfit: '1234.56',
  trades: '222',
  testsPassed: 'OOS, Forward',
  testsFailed: '',
  tier: '1',
  status: 'CANDIDATA',
}, '2026-05-04');
assert.equal(manual.metrics.net_profit, 1234.56);
assert.equal(manual.metrics.trades, 222);
assert.equal(manual.tests_passed.length, 2);
assert.equal(manual.tests_passed[0], 'OOS');
assert.equal(manual.tests_passed[1], 'Forward');

const baseStrategy = { id: 'A', mining: 1, template: 'T', asset: 'EURUSD', tf: 'H1', metrics: {}, tests_passed: [], tests_failed: [] };
const imported = { id: 'B', mining: 1, template: 'T', asset: 'EURUSD', tf: 'H1', metrics: {}, tests_passed: [], tests_failed: [], _imported: true, _import_id: 'tmp' };
const dedupe = SQX.strategies.dedupeImportedStrategies([baseStrategy], [], [baseStrategy, imported]);
assert.equal(dedupe.fresh.length, 1);
assert.equal(dedupe.duplicates, 1);
const csvRows = SQX.strategies.exportCsvRows([imported]);
assert.equal(csvRows.length, 2);
assert.match(csvRows[1], /"IMPORTED"$/);
const consolidated = SQX.strategies.consolidateJson([imported]);
assert.equal(JSON.parse(consolidated).strategies[0]._imported, undefined);

console.log('core strategy contracts ok');
