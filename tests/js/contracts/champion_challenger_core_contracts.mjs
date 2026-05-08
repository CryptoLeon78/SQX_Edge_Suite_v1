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
  'Unknown Col',
]);
assert.equal(aliasResolution.columns.strategy_name, 0);
assert.equal(aliasResolution.columns.symbol, 1);
assert.equal(aliasResolution.columns.profit_factor, 2);
assert.equal(aliasResolution.columns.return_drawdown, 3);
assert.equal(aliasResolution.columns.trades, 4);
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

console.log('champion challenger core contracts ok');
