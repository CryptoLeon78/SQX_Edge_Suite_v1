import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX } = createLoadedSandbox([
  'app/js/modules/renderers.js',
  'app/js/modules/charts.js',
]);

assert.equal(SQX.modules.renderers, SQX.renderers);
assert.equal(SQX.modules.charts, SQX.charts);

assert.match(SQX.renderers.sqxBadge({ code: 'A', label: 'Both', desc: 'desc' }), /sqx-badge sqx-A/);
assert.match(SQX.renderers.sqxBadge({ code: 'B', label: 'Both', desc: 'desc' }, true), /sqx-mini sqx-B/);
assert.match(SQX.renderers.sqxPreviewHTML('C'), /Only Long/);
assert.match(SQX.renderers.sqxPreviewHTML('D'), /Only Short/);
assert.match(SQX.renderers.ratingPairBadge({
  objective: '++',
  diff: 2,
  composite: 0.82,
  metrics: { pf: 1.7 },
}), /discrepancy-major/);
assert.equal(SQX.renderers.ratingPairBadge(null), '');
assert.match(SQX.renderers.compositeBar({ composite: 0.76 }), /Hipótesis previa 76%/);
assert.equal(SQX.renderers.compositeBar({ composite: null }), '');
assert.match(SQX.renderers.historySection('EURUSD', {}, '<svg></svg>', []), /^$/);
assert.match(SQX.renderers.historySection('EURUSD', { GBPUSD: {} }, '', []), /Sin datos para EURUSD/);
assert.match(SQX.renderers.sqxLegend(['A'], { A: { label: 'Both', desc: 'desc' } }, code => `<x>${code}</x>`), /sqx-config-card/);
assert.match(SQX.renderers.sortableHeader('Asset', 'asset', 'cat', 'k', { col: 'asset', dir: 'asc' }), /sort-asc/);
assert.match(SQX.renderers.sparkHTML({ cats: { trend: { rating: '++' } } }, ['trend', 'missing'], { trend: { color: '#fff', name: 'Trend' } }), /sparkline-seg/);

const chart = SQX.charts.renderHistoryChart('EURUSD', {
  start: '2020-01',
  v: [100, 110, 95, 120, 130, 140, 150, 160, 170, 165, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 330],
}, [{ date: '2021-01', color: '#f00', label: 'Event' }], { width: 400, height: 160, smaPeriod: 3, minBandMonths: 2 });
assert.match(chart, /^<svg class="history-chart"/);
assert.match(chart, /Event \(2021-01\)/);
assert.match(chart, /path d=/);
assert.match(SQX.charts.renderHistoryChart('EURUSD', null), /Sin histórico disponible/);

console.log('renderers charts contracts ok');
