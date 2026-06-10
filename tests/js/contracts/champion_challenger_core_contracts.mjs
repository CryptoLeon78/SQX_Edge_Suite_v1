import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX } = createLoadedSandbox([
  'app/js/modules/formatters.js',
  'app/js/modules/champion-challenger-core.js',
]);

const cvc = SQX.championChallengerCore;

assert.ok(cvc, 'champion challenger core module should register');
assert.equal(cvc.normalizeHeader('  Return   / Drawdown  '), 'return / drawdown');
assert.equal(cvc.detectDelimiter('Strategy Name;Symbol;PF\nA;EURUSD;1.5'), ';');
assert.equal(cvc.detectDelimiter('Strategy Name,Symbol,PF\nA,EURUSD,1.5'), ',');

const aliasResolution = cvc.resolveColumnAliases([
  'Strategy Name',
  'Symbol',
  'PF',
  'Ret/DD',
  '# trades',
  'Trades Long',
  'Trades Short',
  'Avg. Bars in Trade',
  'Avg. Trades Per Month',
  'Unknown Col',
]);
assert.equal(aliasResolution.columns.strategy_name, 0);
assert.equal(aliasResolution.columns.symbol, 1);
assert.equal(aliasResolution.columns.profit_factor, 2);
assert.equal(aliasResolution.columns.return_drawdown, 3);
assert.equal(aliasResolution.columns.trades, 4);
assert.equal(aliasResolution.columns.trades_long, 5);
assert.equal(aliasResolution.columns.trades_short, 6);
assert.equal(aliasResolution.columns.avg_bars, 7);
assert.equal(aliasResolution.columns.avg_trades_per_month, 8);
assert.equal(aliasResolution.unknown.length, 1);

assert.equal(cvc.parseNumber('1,42').value, 1.42);
assert.equal(cvc.parseNumber('1,234.56').value, 1234.56);
assert.equal(cvc.parseNumber('1.234,56').value, 1234.56);
assert.equal(cvc.parseNumber('12.5%').value, 12.5);
assert.equal(cvc.parseNumber('').ok, false);

const championCsv = [
  'Strategy Name;Symbol;Profit factor;Return/Drawdown;# trades;Drawdown %;Filters Result',
  '"Champion; Alpha";EURUSD;1,50;4.0;200;5%;PASSED',
].join('\n');
const championParsed = cvc.parseStrategyCsv(championCsv, { role: 'champion' });
assert.equal(championParsed.ok, true);
assert.equal(championParsed.delimiter, ';');
assert.equal(championParsed.records.length, 1);
assert.equal(championParsed.records[0].metrics.strategy_name, 'Champion; Alpha');
assert.equal(championParsed.records[0].metrics.profit_factor, 1.5);
assert.equal(championParsed.records[0].metrics.trades, 200);

const challengerCsv = [
  'Strategy,Asset,PF,CAGR/Max DD,Trades,Max Drawdown %,Filters Result,Indicators',
  '"<script>alert(1)</script>",EURUSD,1.60,3.90,160,5.2,PASSED,"RSI, EMA"',
  'Weak One,EURUSD,1.40,2.00,80,9.0,FAILED,MACD',
].join('\n');
const challengersParsed = cvc.parseStrategyCsv(challengerCsv, { role: 'challenger' });
assert.equal(challengersParsed.ok, true);
assert.equal(challengersParsed.records.length, 2);
assert.equal(challengersParsed.records[0].metrics.entry_indicators, 'RSI, EMA');
assert.equal(challengersParsed.records[0].safe.strategy_name, '&lt;script&gt;alert(1)&lt;/script&gt;');

const ranked = cvc.rankCandidates(championParsed.records[0], challengersParsed.records, {
  enableForwardCheck: true,
});
assert.equal(ranked.length, 2);
assert.equal(ranked[0].formal_fail_count, 0);
assert.equal(ranked[0].formal_pass_count, 3);
assert.equal(ranked[0].advisory_pass_count, 1);
assert.equal(ranked[0].safe_strategy_name, '&lt;script&gt;alert(1)&lt;/script&gt;');
assert.deepEqual(Array.from(ranked[1].failure_reasons), ['profit_factor', 'return_drawdown', 'trades', 'forward_oos_flag']);

const longShortDirection = cvc.detectDirection({ trades_long: 90, trades_short: 80, strategy_name: 'Balanced L+S' });
assert.equal(longShortDirection.direction, 'long_short');
assert.equal(longShortDirection.source, 'trades_split');
assert.equal(longShortDirection.confidence, 'high');

const shortDirection = cvc.detectDirection({ strategy_name: 'Mean reversion short engine', symbol: 'EURUSD' });
assert.equal(shortDirection.direction, 'short_only');
assert.equal(shortDirection.source, 'name_pattern');

const defaultDirection = cvc.detectDirection({ strategy_name: 'Neutral Candidate', symbol: 'EURUSD' });
assert.equal(defaultDirection.direction, 'long_only');
assert.equal(defaultDirection.warning, 'direction_defaulted');

const meanRevertArch = cvc.detectArchetype({
  strategy_name: 'AUDCAD short fade',
  entry_indicators: 'ATR SuperTrend RSI',
  avg_bars: 10.5,
  avg_trades_per_month: 16,
});
assert.equal(meanRevertArch.archetype, 'MEAN_REVERT');
assert.equal(meanRevertArch.confidence, 'medium');

const scalperArch = cvc.detectArchetype({
  entry_indicators: 'RSI',
  avg_bars: 2.5,
  avg_trades_per_month: 45,
});
assert.equal(scalperArch.archetype, 'SCALPER');
assert.equal(scalperArch.confidence, 'high');

const timeline = cvc.buildOosTimeline({ symbol: 'NASDAQ', block_count: 4 }, { now: '2026-05' });
assert.equal(timeline.ok, true);
assert.equal(timeline.profile, 'indices');
assert.equal(timeline.blocks.length, 4);
assert.equal(timeline.blocks[0].start, '2018-01');
assert.equal(timeline.blocks[3].end, '2026-04');

const incompleteChampion = cvc.parseStrategyCsv('Strategy Name,Symbol,PF\nOnly,EURUSD,1.2', { role: 'champion' });
assert.equal(incompleteChampion.ok, false);
assert.ok(incompleteChampion.errors.some(error => error.code === 'required_column_missing' && error.field === 'return_drawdown'));
assert.ok(incompleteChampion.errors.some(error => error.code === 'required_column_missing' && error.field === 'trades'));

const duplicateAliases = cvc.parseStrategyCsv(
  'Strategy Name,Strategy,Symbol,PF,Ret/DD,Trades\nA,B,EURUSD,1.4,3.2,100',
  { role: 'champion' }
);
assert.equal(duplicateAliases.ok, true);
assert.ok(duplicateAliases.warnings.some(warning => warning.code === 'duplicate_alias' && warning.field === 'strategy_name'));

const tooManyRows = cvc.parseStrategyCsv(
  'Strategy Name,Symbol,PF,Ret/DD,Trades\nA,EURUSD,1.4,3.2,100\nB,EURUSD,1.5,3.4,110',
  { role: 'champion' }
);
assert.equal(tooManyRows.ok, false);
assert.ok(tooManyRows.errors.some(error => error.code === 'champion_row_count_invalid'));

const oosColumns = cvc.resolveOosColumns([
  'Strategy Name',
  'CAGR/Max DD (OOS1)',
  'Profit Factor (OOS1)',
  'CAGR/Max DD (OOS2)',
  'CAGR/Max DD (OOS4)',
  'Worst Year Profit (OOS4)',
]);
assert.equal(oosColumns.metrics[cvc.normalizeMetricName('CAGR/Max DD')].metric, 'CAGR/Max DD');
assert.equal(oosColumns.metrics[cvc.normalizeMetricName('CAGR/Max DD')].columns[4], 4);
assert.equal(cvc.choosePrimaryOosMetric(oosColumns.metrics), 'CAGR/Max DD');
assert.equal(cvc.extractOosHeader('Profit Factor (OOS12)').block, 12);
assert.equal(cvc.extractOosHeader('Profit Factor OOS12'), null);

const oosCsv = [
  'Strategy Name;Symbol;CAGR/Max DD (OOS1);Profit Factor (OOS1);Worst Year Profit (OOS1);CAGR/Max DD (OOS2);Profit Factor (OOS2);Worst Year Profit (OOS2);CAGR/Max DD (OOS3);Profit Factor (OOS3);Worst Year Profit (OOS3)',
  '"<b>Challenger A</b>";EURUSD;2.5;1.6;100;1.5;1.4;-20;-0.5;0.9;50',
  'Challenger B;EURUSD;1.0;1.2;10;1.1;1.3;20;1.2;1.4;30',
].join('\n');
const oosParsed = cvc.parseOosCsv(oosCsv);
assert.equal(oosParsed.ok, true);
assert.equal(oosParsed.delimiter, ';');
assert.equal(oosParsed.records.length, 2);
assert.equal(oosParsed.records[0].primary_metric, 'CAGR/Max DD');
assert.equal(oosParsed.records[0].block_count, 3);
assert.equal(oosParsed.records[0].positive_block_count, 2);
assert.equal(oosParsed.records[0].positive_block_ratio, 2 / 3);
assert.equal(oosParsed.records[0].primary_metric_min, -0.5);
assert.equal(oosParsed.records[0].primary_metric_max, 2.5);
assert.equal(oosParsed.records[0].primary_metric_avg, (2.5 + 1.5 - 0.5) / 3);
assert.equal(oosParsed.records[0].primary_metric_decay, -3);
assert.equal(oosParsed.records[0].max_negative_streak, 1);
assert.equal(oosParsed.records[0].has_negative_worst_year, true);
assert.equal(oosParsed.records[0].stable_enough, true);
assert.equal(oosParsed.records[0].safe_strategy_name, '&lt;b&gt;Challenger A&lt;/b&gt;');
assert.equal(oosParsed.records[1].max_negative_streak, 0);
assert.equal(oosParsed.records[1].has_negative_worst_year, false);

const temporalCsv = [
  'Strategy Name;Symbol;Net Profit (OOS1);Net Profit (OOS2);Net Profit (OOS3);Net Profit (OOS4);Net Profit (OOS5);Net Profit (OOS6);Net Profit (OOS7);Net Profit (OOS8)',
  'Fresh;EURUSD;10;10;10;10;10;50;50;50',
  'Recovered;EURUSD;100;-20;40;60;50;-70;20;10',
  'Declining;EURUSD;100;80;70;-120;-90;10;5;5',
].join('\n');
const temporalParsed = cvc.parseOosCsv(temporalCsv);
const freshHealth = cvc.computeTemporalHealth(temporalParsed.records[0]);
assert.equal(freshHealth.status, 'fresh');
assert.equal(freshHealth.peak_block, 8);
assert.equal(freshHealth.pass_all, true);
assert.equal(freshHealth.source_metric, 'Net Profit');
assert.equal(freshHealth.quality, 'full');

const recoveredHealth = cvc.computeTemporalHealth(temporalParsed.records[1], { maxDdAtClose: 0.4, minRecoveryIndex: -10 });
assert.equal(recoveredHealth.status, 'recovered');
assert.equal(recoveredHealth.peak_block, 5);
assert.equal(recoveredHealth.pass_all, true);
assert.ok(recoveredHealth.recovery_index < 0.70);

const decliningHealth = cvc.computeTemporalHealth(temporalParsed.records[2]);
assert.equal(decliningHealth.status, 'declining');
assert.equal(decliningHealth.pass_all, false);
assert.equal(decliningHealth.pass_drawdown, false);
assert.ok(decliningHealth.dd_at_close >= 0.15);

const fallbackHealth = cvc.computeTemporalHealth(oosParsed.records[1], { minBlocks: 3 });
assert.equal(fallbackHealth.source_metric, 'CAGR/Max DD');
assert.equal(fallbackHealth.quality, 'fallback');
assert.ok(fallbackHealth.warnings.some(warning => warning.code === 'temporal_health_metric_fallback'));

const shortHealth = cvc.computeTemporalHealth(oosParsed.records[0]);
assert.equal(shortHealth.status, 'unknown');
assert.equal(shortHealth.quality, 'insufficient');
assert.ok(shortHealth.warnings.some(warning => warning.code === 'temporal_health_blocks_insufficient'));

const sparseOos = cvc.parseOosCsv([
  'Strategy Name,CAGR/Max DD (OOS1),CAGR/Max DD (OOS3)',
  'Sparse,1.0,2.0',
].join('\n'));
assert.equal(sparseOos.ok, true);
assert.equal(sparseOos.records[0].block_count, 2);
assert.equal(sparseOos.records[0].stable_enough, false);
assert.ok(sparseOos.records[0].warnings.some(warning => warning.code === 'oos_missing_block' && warning.block === 2));

const noOosMetrics = cvc.parseOosCsv('Strategy Name,Symbol\nA,EURUSD');
assert.equal(noOosMetrics.ok, false);
assert.ok(noOosMetrics.errors.some(error => error.code === 'oos_metric_columns_missing'));

console.log('champion challenger core contracts ok');
