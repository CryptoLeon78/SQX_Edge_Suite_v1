import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX } = createLoadedSandbox([
  'app/js/modules/formatters.js',
  'app/js/modules/domain.js',
]);
const plain = value => JSON.parse(JSON.stringify(value));

assert.equal(SQX.modules.formatters, SQX.formatters);
assert.equal(SQX.modules.domain, SQX.domain);

assert.deepEqual(plain(SQX.formatters.ratingLabel('++')), { text: 'Estrella', cls: 'rating-pp' });
assert.equal(SQX.formatters.heatmapClass('+'), 'hm-p');
assert.equal(SQX.formatters.assetDirectionClass('L'), 'dir-long');
assert.equal(SQX.formatters.strategyDirectionClass('S'), 'dir-S');
assert.equal(SQX.formatters.tierClass('1.5'), 'tier-15');
assert.equal(SQX.formatters.tierLabel('tentativa'), 'TENTATIVA');
assert.equal(SQX.formatters.metricClass('PF', 1.51), 'pos');
assert.equal(SQX.formatters.metricClass('PF', 1.25), 'warn');
assert.equal(SQX.formatters.metricClass('PF', 1.1), 'neg');
assert.equal(SQX.formatters.formatNumber('12.345', 2), '12.35');
assert.equal(SQX.formatters.formatNumber('bad', 2), '—');
assert.equal(SQX.formatters.formatInteger(12345.2), '12,345');
assert.equal(SQX.formatters.escapeHtml('<b>&"'), '&lt;b&gt;&amp;&quot;');

const ratingOrder = { '++': 3, '+': 2, '~': 1, '-': 0 };
const asset = {
  id: 'EURUSD',
  cats: {
    trend: { rating: '++', dir: 'L' },
    momentum: { rating: '+', dir: 'S' },
    volume: { rating: '~', dir: 'L/S' },
  },
};
assert.deepEqual(plain(SQX.domain.calcScore(asset, 'all', ratingOrder)), { raw: 6, count: 3, norm: 67 });
assert.deepEqual(plain(SQX.domain.calcScore(asset, 'L', ratingOrder)), { raw: 4, count: 2, norm: 67 });
assert.equal(SQX.domain.getSqxConfig({ cats: { trend: { dir: 'L' } } }).code, 'C');
assert.equal(SQX.domain.getSqxConfig({ cats: { trend: { dir: 'S' } } }).code, 'D');
assert.equal(SQX.domain.getSqxConfig({ cats: { trend: { dir: 'L/S' } } }).code, 'A');
assert.equal(SQX.domain.getSqxConfig({ cats: { trend: { dir: 'L' }, trend_S: { dir: 'S' } } }).code, 'B');
assert.equal(SQX.domain.tfMatch('M15,H1,H4', 'H1'), true);
assert.equal(SQX.domain.assetMatchesSqxFilter(asset, 'C'), true);
assert.equal(SQX.domain.assetMatchesSqxFilter({ type: 'forex', cats: { trend: { dir: 'L/S' } } }, 'D'), true);
assert.equal(SQX.domain.assetMatchesSqxFilter({ type: 'oro', cats: { trend_S: { dir: 'S' } } }, 'D'), false);
assert.equal(SQX.domain.resolveSqxDirection('D', 'L/S'), 'S');
assert.equal(SQX.domain.isShortBlockedAsset({ type: 'index' }), true);

const scores = {
  EURUSD: {
    trend: { objective: '++', composite_score: 0.94 },
    metrics: { trend: { pf: 1.7 } },
  },
};
assert.deepEqual(plain(SQX.domain.scoreFromScores(scores, 'EURUSD', 'trend_S')), {
  base: 'trend',
  objective: '++',
  composite: 0.94,
  metrics: { pf: 1.7 },
});
const assets = [{ id: 'EURUSD', cats: { trend: { rating: '-', dir: 'L' } } }];
SQX.domain.applyObjectiveRatings(assets, scores, SQX.domain.scoreFromScores.bind(null, scores));
assert.equal(assets[0].cats.trend.rating, '++');
assert.equal(assets[0].cats.trend._composite, 0.94);

const sorted = SQX.domain.sortRows([
  { asset: { id: 'B' }, rating: '+' },
  { asset: { id: 'A' }, rating: '++' },
], 'asset', 'asc', ratingOrder);
assert.equal(sorted[0].asset.id, 'A');

console.log('formatters domain contracts ok');
