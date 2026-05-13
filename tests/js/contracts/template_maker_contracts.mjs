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
  'loadFromCSV',
  'loadFromSQX',
  'getStrategies',
  'getPassingStrategies',
  'setCapa',
  'getCapa',
  'setPreset',
  'getCurrentPreset',
  'getPresets',
  'autoDetectPreset',
  'getThresholds',
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
assert.ok(html.includes('id="tm-csv-input"'), 'missing CSV input');
assert.ok(html.includes('id="tm-sqx-input"'), 'missing SQX input');
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

const emptyScore = tm.scoreStrategy({});
assert.equal(emptyScore.classification, 'FAILED', 'empty score should fail defensively');
assert.equal(emptyScore.total, 0, 'empty score should not count missing KPI as evaluated');

await tm.loadFromCSV('Strategy Name;Symbol;TimeFrame;Net profit;# of trades;Profit factor;Max DD %;Sharpe Ratio;Stability;CAGR/Max DD %;Winning Percent;SQN;RecoveryFactor\nStrategy 1;XAUUSD;H1;10000;260;1.45;12;0.9;0.8;1.1;48;2.1;3.5');
assert.equal(tm.getStrategies().length, 1, 'CSV load should add one strategy');
assert.equal(tm.getStrategies()[0].Asset, 'Commodities', 'XAUUSD should auto-detect as Commodities');
const strategyCopy = tm.getStrategies();
strategyCopy.push({ _id: 'mutated' });
assert.equal(tm.getStrategies().length, 1, 'getStrategies should return a copy');
assert.ok(tm.getPassingStrategies().length >= 1, 'loaded sample should pass current thresholds');
assert.equal(tm.getAuditReport().total, 1, 'audit should report loaded strategies');

await tm.setCapa(2);
assert.equal(tm.getCapa(), 2, 'setCapa should update state');
await tm.setPreset('Forex');
assert.equal(tm.getCurrentPreset(), 'Forex', 'setPreset should update state');
const thresholds = tm.getThresholds();
assert.ok(Object.keys(thresholds).length > 0, 'thresholds should be available');
await tm.setThreshold('Profit factor', 'val', 1.31);
assert.equal(tm.getThresholds()['Profit factor'].val, 1.31, 'setThreshold should update value');
await tm.reset();
assert.equal(tm.getStrategies().length, 0, 'reset should clear strategies');

console.log('template maker contracts ok');
