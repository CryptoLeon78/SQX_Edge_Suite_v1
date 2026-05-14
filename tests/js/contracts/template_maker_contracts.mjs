import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const mainJs = fs.readFileSync(path.join(repoRoot, 'app/js/main.js'), 'utf8');
const uiManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/ui_manifest.json'), 'utf8'));

const { SQX } = createLoadedSandbox([
  'app/js/modules/storage.js',
  'app/js/modules/template-maker.js',
  'app/js/modules/template-maker-ui.js',
]);

const tm = SQX.templateMaker;
const requiredApi = [
  'init',
  'reset',
  'clearResultStrategies',
  'deleteResultStrategies',
  'clearCSVStrategies',
  'ingestFiles',
  'computeFileHash',
  'loadFromCSV',
  'loadFromSQX',
  'getStrategies',
  'getStrategyRecords',
  'getIncompleteRecords',
  'getProvenance',
  'getPassingStrategies',
  'setCapa',
  'getCapa',
  'setPreset',
  'getCurrentPreset',
  'getPresets',
  'autoDetectPreset',
  'getThresholds',
  'getRequiredMetricNames',
  'validateMetricsContract',
  'reconcileStrategySources',
  'getStrategyStatus',
  'canGenerateC2',
  'setThreshold',
  'scoreStrategy',
  'getAuditReport',
  'generateC2Template',
  'exportTemplateZip',
  'dbInit',
  'saveStrategies',
  'loadStrategies',
  'clearDB',
];

assert.ok(html.includes('id="tab-templatemaker"'), 'missing Template Maker tab panel');
assert.ok(html.includes('Template Maker Cert'), 'Template Maker should explain the mandatory metric view');
assert.ok(html.includes('id="tm-files-input"'), 'missing unified file input');
assert.ok(html.includes('id="tm-unified-zone"'), 'missing unified upload zone');
assert.ok(html.includes('id="tm-open-cert-view"'), 'missing SQX Views handoff');
assert.ok(html.includes('id="tm-contract-summary"'), 'missing contract summary cards');
assert.ok(html.includes('id="tm-problem-panel"'), 'missing contract problem panel');
assert.ok(html.includes('id="tm-reset-results-btn"'), 'missing results reset');
assert.ok(html.includes('Reset resultados'), 'results reset should be user-facing');
assert.ok(html.includes('id="tm-delete-selected-btn"'), 'missing selected delete action');
assert.ok(html.includes('Borrar seleccionadas'), 'selected delete should be user-facing');
assert.ok(html.includes('id="tm-csv-input"'), 'missing CSV input');
assert.ok(html.includes('id="tm-sqx-input"'), 'missing SQX input');
['Genera la view obligatoria', 'Carga tus fuentes', 'Resuelve el contrato', 'Evalua Perfil Capa 1', 'Resultados y C2'].forEach(step => {
  assert.ok(html.includes(step), `Template Maker guided flow should include ${step}`);
});
assert.ok(!html.includes('data-tm-capa="2"'), 'Template Maker should not expose Capa 2 analysis control');
assert.ok(!html.includes('Capa 2 - Validacion operable'), 'Template Maker should not describe Capa 2 as an active mode');
['Completa', 'Falta SQX', 'Faltan métricas', 'Métricas no compatibles', 'Lista para C2'].forEach(status => {
  assert.ok(html.includes(status) || fs.readFileSync(path.join(repoRoot, 'app/js/modules/template-maker-ui.js'), 'utf8').includes(status), `Template Maker should render status ${status}`);
});
assert.ok(html.includes('Avanzado: cargas separadas'), 'separate loads should be advanced');
assert.ok(html.includes('Avanzado: Umbrales KPI editables'), 'thresholds should be advanced');
assert.ok(!html.includes('tm-help-panel'), 'old quick guide panel should be merged into guided steps');
assert.ok(!html.includes('tm-flow-grid'), 'old source cards should be merged into guided steps');
assert.ok(html.includes('vendor/jszip.min.js'), 'missing local JSZip script');
assert.ok(html.includes('js/modules/template-maker.js'), 'missing template-maker script');
assert.ok(html.includes('js/modules/template-maker-ui.js'), 'missing template-maker-ui script');
assert.ok(!html.includes('id="tab-analyzer"'), 'old analyzer tab should not remain active');
assert.ok(!html.includes('href="css/analyzer.css"'), 'old analyzer stylesheet should not be active');
assert.ok(!mainJs.includes('window.SQX.analyzer.init()'), 'old analyzer init should be retired');
assert.ok(mainJs.includes('window.SQX.templateMakerUI.init()'), 'main should initialize template-maker UI');

const tabIds = uiManifest.tabs.map(tab => tab.id);
assert.ok(tabIds.includes('templatemaker'), 'ui manifest missing Template Maker');
assert.equal(tabIds.indexOf('templatemaker'), tabIds.indexOf('estrategias') - 1, 'Template Maker should sit before Estrategias');

assert.ok(SQX.modules['template-maker'], 'template-maker module should register');
assert.ok(SQX.modules['template-maker-ui'], 'template-maker-ui module should register');
requiredApi.forEach(method => assert.equal(typeof tm[method], 'function', `API ${method} should be a function`));
assert.equal(tm.getCurrentPreset(), 'Generic', 'default preset should be Generic');
assert.equal(tm.getCapa(), 1, 'default capa should be 1');
assert.ok(tm.getPresets().includes('Generic'), 'Generic preset should exist');
assert.ok(tm.getPresets().includes('Commodities'), 'Commodities preset should exist');
assert.equal(tm.getStrategies().length, 0, 'initial strategies should be empty');
assert.ok(tm.getRequiredMetricNames(1, 'Generic').includes('Net profit'), 'required metrics should include Net profit');
assert.ok(tm.getRequiredMetricNames(1, 'Commodities').includes('Ret/DD Ratio'), 'commodity contract should keep Ret/DD alias');

const emptyScore = tm.scoreStrategy({});
assert.equal(emptyScore.classification, 'FAILED', 'empty score should fail defensively');
assert.equal(emptyScore.total, 0, 'empty score should not count missing KPI as evaluated');

const certCsv = 'Strategy Name;Symbol;TimeFrame;Net profit;# of trades;Profit factor;Max DD %;Sharpe Ratio;Stability;CAGR/Max DD %;Winning Percent;SQN;RecoveryFactor;CalmarRatio;SortinoRatio;% Profitable Months\nStrategy 1;XAUUSD;H1;10000;260;1.45;12;0.9;0.8;1.1;48;2.1;3.5;0.8;1.1;62';
await tm.loadFromCSV(certCsv, { fileName: 'template-maker-cert.csv' });
assert.equal(tm.getStrategies().length, 1, 'CSV load should add one strategy');
assert.equal(tm.getStrategies()[0].Asset, 'Commodities', 'XAUUSD should auto-detect as Commodities');
assert.equal(tm.validateMetricsContract(tm.getStrategies()[0]).valid, true, 'Template Maker Cert CSV should satisfy metric contract');
assert.equal(tm.getStrategyStatus(tm.getStrategies()[0]), 'Falta SQX', 'CSV-only strategies should require SQX for C2');
assert.equal(tm.canGenerateC2(tm.getStrategies()[0]), false, 'CSV-only strategy should not enable C2');
assert.equal(tm.getIncompleteRecords().length, 1, 'CSV-only strategy should be incomplete');
assert.ok(tm.getStrategyRecords()[0].sources.csv, 'strategy records should expose CSV source');
assert.ok(tm.getProvenance(tm.getStrategies()[0]._id).certVersion, 'provenance should expose cert version');
const csvOnlyClear = await tm.clearResultStrategies();
assert.equal(csvOnlyClear.removed, 1, 'clearResultStrategies should remove CSV-only rows');
assert.equal(tm.getStrategies().length, 0, 'results clear should empty CSV rows');
const suffixedCertCsv = [
  'Strategy Name;Symbol (IS);TimeFrame (IS);Net profit (IS);# of trades (IS);Profit factor (IS);Max DD % (IS);Sharpe Ratio (IS);Stability (IS);CAGR/Max DD % (IS);Winning Percent (IS);SQN (IS);RecoveryFactor (IS);CalmarRatio (IS);SortinoRatio (IS);% Profitable Months (IS);Net profit (OOS);# of trades (OOS);Profit factor (OOS);Max DD % (OOS);Sharpe Ratio (OOS);Stability (OOS);CAGR/Max DD % (OOS);Winning Percent (OOS);SQN (OOS);Recovery Factor (OOS);Calmar Ratio (OOS);Sortino Ratio (OOS);% Profitable Months (OOS)',
  'Strategy 4.21.40;XAUUSD_tick_TICK_ESTPlus07;H1;3675,22;218;1,45;18,2;0,69;0,82;0,66;45;1,7;2,4;0,6;0,9;54;5967,27;220;1,72;12,5;1,1;0,68;1,11;49;2,2;3,5;0,8;1,1;62',
].join('\n');
await tm.loadFromCSV(suffixedCertCsv, { fileName: 'DatabankExport.csv' });
const suffixed = tm.getStrategies().find(strategy => strategy['Strategy Name'] === 'Strategy 4.21.40');
assert.ok(suffixed, 'suffixed SQX databank export should add a strategy');
assert.equal(suffixed.Symbol, 'XAUUSD_tick_TICK_ESTPlus07', 'Symbol (IS) should normalize to Symbol');
assert.equal(suffixed.TimeFrame, 'H1', 'TimeFrame (IS) should normalize to TimeFrame');
assert.equal(tm.validateMetricsContract(suffixed).valid, true, 'suffixed IS/OOS columns should satisfy metric contract');
assert.equal(tm.scoreStrategy(suffixed).details['Profit factor'].result, 'pass', 'decimal comma metrics should parse as decimal values, not thousands');
assert.equal(tm.scoreStrategy(suffixed).details['Profit factor'].value, '1,72', 'OOS value should win when only IS/OOS samples exist');
await tm.clearResultStrategies();
await tm.loadFromCSV([
  'Strategy Name;Symbol;TimeFrame;Net profit;# of trades;Profit factor;Max DD %;Sharpe Ratio;Stability;CAGR/Max DD %;Winning Percent;SQN;RecoveryFactor;CalmarRatio;SortinoRatio;% Profitable Months',
  'Delete me;XAUUSD;H1;10000;260;1.45;12;0.9;0.8;1.1;48;2.1;3.5;0.8;1.1;62',
  'Keep me;EURUSD;H1;9000;240;1.4;14;0.8;0.7;1.0;47;1.9;3.2;0.7;1.0;58',
].join('\n'), { fileName: 'template-maker-cert.csv' });
const deleteTargetId = tm.getStrategies()[0]._id;
const selectedDelete = await tm.deleteResultStrategies([deleteTargetId]);
assert.equal(selectedDelete.removed, 1, 'deleteResultStrategies should remove selected rows only');
assert.equal(tm.getStrategies().length, 1, 'selected delete should leave unselected rows');
assert.equal(tm.getStrategies()[0]['Strategy Name'], 'Keep me', 'selected delete should preserve unselected strategy');
await tm.clearResultStrategies();
await tm.loadFromCSV(certCsv, { fileName: 'template-maker-cert.csv' });
const strategyCopy = tm.getStrategies();
strategyCopy.push({ _id: 'mutated' });
assert.equal(tm.getStrategies().length, 1, 'getStrategies should return a copy');
assert.ok(tm.getPassingStrategies().length >= 1, 'loaded sample should pass current thresholds');
assert.equal(tm.getAuditReport().total, 1, 'audit should report loaded strategies');
const sqxLike = {
  _id: 99,
  _source: 'sqx',
  'Strategy Name': 'Strategy 1',
  Symbol: 'XAUUSD',
  TimeFrame: 'H1',
  _fileData: { name: 'Strategy 1.sqx' },
  sources: { sqx: { fileName: 'Strategy 1.sqx', hash: 'hash-1', importedAt: '2026-05-13T00:00:00.000Z' } },
  provenance: { events: [], certVersion: 'TMA2.1', ruleset: 'template-maker-cert-v1' },
};
const merged = tm.reconcileStrategySources([tm.getStrategies()[0], sqxLike]);
assert.equal(merged.length, 1, 'CSV and SQX for same strategy should reconcile into one record');
assert.ok(merged[0].sources.csv, 'reconciled record should keep CSV source');
assert.ok(merged[0].sources.sqx, 'reconciled record should keep SQX source');
assert.equal(tm.validateMetricsContract(merged[0]).valid, true, 'reconciled record should keep valid metrics');
assert.equal(await tm.computeFileHash('abc').then(hash => hash.length >= 8), true, 'computeFileHash should return a stable hash');
await tm.reset();
await tm.loadFromCSV([{
  'Strategy Name': 'Keep SQX',
  Symbol: 'XAUUSD',
  TimeFrame: 'H1',
  'Net profit': 10000,
  '# of trades': 260,
  'Profit factor': 1.45,
  'Max DD %': 12,
  'Sharpe Ratio': 0.9,
  Stability: 0.8,
  'CAGR/Max DD %': 1.1,
  'Winning Percent': 48,
  SQN: 2.1,
  RecoveryFactor: 3.5,
  CalmarRatio: 0.8,
  SortinoRatio: 1.1,
  '% Profitable Months': 62,
  sources: { sqx: { fileName: 'Keep SQX.sqx', hash: 'hash-keep', importedAt: '2026-05-13T00:00:00.000Z' } }
}], { fileName: 'template-maker-cert.csv' });
const clearMerged = await tm.clearResultStrategies();
assert.equal(clearMerged.removed, 1, 'clearResultStrategies should remove reconciled CSV/SQX rows');
assert.equal(tm.getStrategies().length, 0, 'results clear should remove residual SQX rows too');

await tm.setCapa(1);
assert.equal(tm.getCapa(), 1, 'Template Maker contract should stay on Capa 1 for UI workflow');
await tm.setPreset('Forex');
assert.equal(tm.getCurrentPreset(), 'Forex', 'setPreset should update state');
const thresholds = tm.getThresholds();
assert.ok(Object.keys(thresholds).length > 0, 'thresholds should be available');
await tm.setThreshold('Profit factor', 'val', 1.31);
assert.equal(tm.getThresholds()['Profit factor'].val, 1.31, 'setThreshold should update value');
await tm.reset();
assert.equal(tm.getStrategies().length, 0, 'reset should clear strategies');
await tm.loadFromCSV('Strategy Name;Symbol;TimeFrame;Net profit\nBroken;EURUSD;H1;100');
assert.equal(tm.validateMetricsContract(tm.getStrategies()[0]).status, 'Métricas no compatibles', 'missing required columns should be reported');
assert.equal(tm.getStrategyStatus(tm.getStrategies()[0]), 'Métricas no compatibles', 'incompatible CSV should expose user-facing status');
await tm.reset();

console.log('template maker contracts ok');
