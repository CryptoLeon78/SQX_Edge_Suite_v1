import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX } = createLoadedSandbox([
  'app/js/modules/strategies.js',
]);

assert.equal(SQX.modules.strategies, SQX.strategies);

const base = { id: 'A', name: 'Base', mining: 1, template: 'T1', asset: 'EURUSD', tf: 'H1', tier: '1', status: 'DEPLOYED', metrics: { net_profit: 100 }, tests_passed: [], tests_failed: [] };
const user = { id: 'B', name: 'User', mining: 2, template: 'T2', asset: 'GBPUSD', tf: 'M15', tier: '2', status: 'CANDIDATA', metrics: { net_profit: -50 }, tests_passed: [], tests_failed: [], _imported: true };
assert.equal(SQX.strategies.strategyKey(base), 'A|1|T1|EURUSD|H1');
assert.deepEqual(SQX.strategies.getAllStrategies([base], [user], [SQX.strategies.strategyKey(base)]), [user]);
assert.equal(SQX.strategies.filterStrategies([base, user], { mining: '2', template: 'all', tier: 'all', status: 'all' })[0].id, 'B');
assert.equal(SQX.strategies.filterStrategies([base, user], { mining: 'all', template: 'all', tier: 'all', status: 'all', query: 'gbpusd' })[0].id, 'B');
const summary = SQX.strategies.summarize([base, user], { userCount: 1, hiddenCount: 2, baseCount: 1 });
assert.equal(summary.totalProfit, 50);
assert.equal(summary.imported, 1);
assert.equal(summary.hidden, 2);
assert.equal(summary.base, 1);
assert.equal(summary.candidate, 1);
assert.equal(summary.deployed, 1);
assert.match(SQX.strategies.summaryHtml(summary, String), /TIER 1/);
assert.match(SQX.strategies.summaryHtml(summary, String), /Importadas/);
assert.match(SQX.strategies.summaryHtml(summary, String), /Ocultas/);
assert.match(SQX.strategies.summaryHtml(summary, String), /Candidatas/);
assert.match(SQX.strategies.filterOptionsHtml([base, user], 'template'), /<option value="T2">T2<\/option>/);
assert.match(SQX.strategies.strategyCard(base, { escapeHtml: String }), /data-strategy-key="A\|1\|T1\|EURUSD\|H1"/);
assert.match(SQX.strategies.strategyCard(user, { escapeHtml: String }), /strat-source-badge imported/);
assert.equal(SQX.strategies.sortForDisplay([user, base])[0].id, 'A');
assert.equal(SQX.strategies.autoDetectTemplate('EMA, MACD', [{ keywords: ['MACD'], template: 'TREND' }]), 'TREND');

const csv = 'Strategy Name;Net profit;Entry indicators\n"Strategy 1";123.4;"EMA, MACD"\n';
const rows = SQX.strategies.parseCSV(csv, ';');
assert.equal(rows[1][2], 'EMA, MACD');
assert.equal(SQX.strategies.detectSeparator(csv), ';');
const objects = [{ 'Strategy Name': 'Strategy 1', 'Net profit': '123.4', 'Entry indicators': 'EMA, MACD' }];
assert.equal(SQX.strategies.filterCsvRows(objects, { filter: 'macd' }).length, 1);
assert.match(SQX.strategies.csvPreviewTable([{ _idx: 0, ...objects[0] }], { selected: new Set([0]) }, { columns: ['Strategy Name','Net profit'], autoDetectTemplate: () => 'TREND' }), /checked/);
assert.match(SQX.strategies.csvConfirmHtml({ mining: 1, bs: 'BS', template: 'T', dir: 'L', tier: '1', status: 'OK' }, new Set([0]), objects), /1<\/strong> estrategia/);
const imported = SQX.strategies.rowToStrategy({
  'Strategy Name': 'Strategy 7',
  'Entry indicators': 'RSI',
  Symbol: 'eurusd_darwinex',
  TimeFrame: 'h1',
  'Net profit': '55',
}, {
  mining: 3,
  bs: 'BS_Tendencia_v6',
  dir: 'L',
  tier: '1',
  status: 'CANDIDATA',
  autoTemplate: true,
}, {
  columnMap: { 'Net profit': 'm.net_profit' },
  templateRules: [{ keywords: ['RSI'], template: 'MOM' }],
});
assert.equal(imported.id, '7');
assert.equal(imported.asset, 'EURUSD');
assert.equal(imported.template, 'MOM');
assert.equal(imported.metrics.net_profit, 55);

const manual = SQX.strategies.manualStrategyFromValues({ id: '9', mining: '4', testsPassed: 'A, B', netProfit: '12.5' }, '2026-05-05');
assert.equal(manual.metrics.net_profit, 12.5);
assert.deepEqual(Array.from(manual.tests_passed), ['A', 'B']);
assert.equal(SQX.strategies.exportCsvRows([user]).length, 2);
assert.equal(SQX.strategies.dedupeImportedStrategies([base], [], [base, user]).duplicates, 1);
assert.equal(JSON.parse(SQX.strategies.consolidateJson([user])).strategies[0]._imported, undefined);
assert.match(SQX.strategies.consolidatedPopupHtml('{"a":1}', 1), /Copiar al portapapeles/);

console.log('strategies granular contracts ok');
