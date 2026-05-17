import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const mainJs = fs.readFileSync(path.join(repoRoot, 'app/js/main.js'), 'utf8');
const uiManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/ui_manifest.json'), 'utf8'));

const { SQX, sandbox } = createLoadedSandbox([
  'app/js/modules/storage.js',
  'app/js/modules/exit-policy.js',
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
  'getContractDiagnostics',
  'extractLogicFeatures',
  'formatLogicIndicators',
  'computeTemplateSimilarity',
  'buildDiversityClusters',
  'getDiversityReport',
  'getDiversitySettings',
  'setDiversitySetting',
  'getDiversityStatus',
  'detectExitComponents',
  'getC2GenerationPreview',
  'getExitAuditReport',
  'reconcileStrategySources',
  'getStrategyStatus',
  'canGenerateC2',
  'setThreshold',
  'scoreStrategy',
  'getAuditReport',
  'resolveC2Trace',
  'buildC2TemplateName',
  'generateC2Template',
  'exportTemplateZip',
  'buildRemoteSnapshot',
  'applyRemoteSnapshot',
  'bootstrapRemoteState',
  'saveRemoteState',
  'getRemotePersistenceStatus',
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
assert.ok(html.includes('id="tm-contract-diagnostics"'), 'missing contract diagnostics panel');
assert.ok(html.includes('id="tm-diversity-settings-grid"'), 'missing diversity settings grid');
assert.ok(html.includes('Descorrelación de templates'), 'Template Maker should expose diversity controls');
assert.ok(html.includes('id="tm-c2-selected-btn"'), 'missing external selected C2 action');
assert.ok(html.includes('id="tm-c2-cluster"'), 'missing C2 cluster trace field');
assert.ok(html.includes('id="tm-c2-name-preview"'), 'missing C2 traceable filename preview');
assert.ok(html.includes('id="tm-c2-exit-list"'), 'missing C2 exit policy list');
assert.ok(html.includes('Salidas y randomización'), 'C2 modal should expose exit/randomization control');
assert.ok(html.includes('value="BS_Tendencia_v6"'), 'C2 block selector should use real versioned BS_* values');
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
assert.ok(html.includes('js/modules/exit-policy.js'), 'missing global exit policy script');
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
assert.ok(SQX.modules['exit-policy'], 'exit-policy module should register');
requiredApi.forEach(method => assert.equal(typeof tm[method], 'function', `API ${method} should be a function`));
assert.equal(tm.getCurrentPreset(), 'Generic', 'default preset should be Generic');
assert.equal(tm.getCapa(), 1, 'default capa should be 1');
assert.ok(tm.getPresets().includes('Generic'), 'Generic preset should exist');
assert.ok(tm.getPresets().includes('Commodities'), 'Commodities preset should exist');
assert.equal(tm.getStrategies().length, 0, 'initial strategies should be empty');
assert.ok(tm.getRequiredMetricNames(1, 'Generic').includes('Net profit'), 'required metrics should include Net profit');
assert.ok(tm.getRequiredMetricNames(1, 'Commodities').includes('Ret/DD Ratio'), 'commodity contract should keep Ret/DD alias');
assert.equal(tm.getContractDiagnostics().schemaVersion, 'template-maker-cert-v2', 'contract diagnostics should expose v2 schema');

const emptyScore = tm.scoreStrategy({});
assert.equal(emptyScore.classification, 'FAILED', 'empty score should fail defensively');
assert.equal(emptyScore.total, 0, 'empty score should not count missing KPI as evaluated');
assert.equal(tm.getDiversitySettings().structuralThreshold, 0.70, 'default structural diversity threshold should be 0.70');
assert.equal(tm.extractLogicFeatures({ _strategyXml: '<Strategy><Rule name="Long entry"><Item categoryType="indicator" key="EMA"><Param key="#Period#">21</Param></Item></Rule></Strategy>' }).indicators[0], 'ema', 'logic extraction should read indicator keys from SQX XML');
const sqxXmlFixture = fs.readFileSync(path.join(repoRoot, 'resources/template-maker-tool/strategy_example.xml')).toString('utf16le');
const sqxXmlFeatures = tm.extractLogicFeatures({ _strategyXml: sqxXmlFixture });
assert.ok(sqxXmlFeatures.indicators.length > 0, 'tracked SQX XML fixture should expose indicator tokens');
assert.ok(sqxXmlFeatures.indicatorLabels.length > 0, 'SQX indicator extraction should keep readable indicator labels');
assert.equal(tm.formatLogicIndicators({ _strategyXml: '<Strategy><Item categoryType="indicator" key="HullMovingAverageATRBands"/></Strategy>' }).compact, 'hullmovingaverageatrbands', 'logic formatter should expose compact indicator token for names');

const certV2Csv = fs.readFileSync(path.join(repoRoot, 'resources/template-maker-tool/template_maker_cert_v2_sample.csv'), 'utf8');
['Strategy TM.01.sqx', 'Strategy TM.02.sqx', 'Strategy TM.03.sqx'].forEach(fileName => {
  assert.ok(fs.existsSync(path.join(repoRoot, 'resources/template-maker-tool', fileName)), `missing tracked diversity SQX fixture ${fileName}`);
});
assert.ok(fs.existsSync(path.join(repoRoot, 'resources/template-maker-tool', 'Strategy TM ExitPolicy.sqx')), 'missing tracked exit policy SQX fixture');
await tm.loadFromCSV(certV2Csv, { fileName: 'template-maker-cert-v2.csv' });
assert.equal(tm.getStrategies().length, 3, 'realistic Template Maker Cert v2 fixture should load all rows');
const certV2Strategy = tm.getStrategies()[0];
const certV2Contract = tm.validateMetricsContract(certV2Strategy);
assert.equal(certV2Contract.schemaVersion, 'template-maker-cert-v2', 'v2 contract should expose schemaVersion');
assert.equal(certV2Contract.valid, true, 'v2 CSV should satisfy metric contract without Ret/DD column');
assert.equal(certV2Contract.missingRequired.length, 0, 'v2 CSV should not report missing required columns');
assert.ok(certV2Contract.requiredColumns.includes('Calmar Ratio'), 'v2 required columns should include Calmar Ratio');
assert.ok(certV2Contract.recognizedColumns.includes('Recovery Factor'), 'v2 parser should accept RecoveryFactor without space');
assert.ok(certV2Contract.derivedMetrics.includes('Ret/DD Ratio <- CAGR/Max DD %'), 'Ret/DD should be derived from CAGR/Max DD %');
await tm.setPreset('Commodities');
assert.equal(tm.scoreStrategy(certV2Strategy).details['Ret/DD Ratio'].value, '0.44', 'Ret/DD scoring should use derived CAGR/Max DD % value');
await tm.setPreset('Generic');
const v2Diagnostics = tm.getContractDiagnostics();
assert.equal(v2Diagnostics.detectedCsvProfile, 'Template Maker Cert v2', 'diagnostics should identify v2 CSV');
assert.equal(v2Diagnostics.missingRequired.length, 0, 'diagnostics should not report v2 missing columns');
await tm.clearResultStrategies();
const [certV2Header, certV2FirstRow] = certV2Csv.trim().split(/\r?\n/);
const certV2Rows32 = Array.from({ length: 32 }, (_, index) => certV2FirstRow.replace('Strategy TM.01', `Strategy TM.${String(index + 1).padStart(2, '0')}`));
await tm.loadFromCSV([certV2Header].concat(certV2Rows32).join('\n'), { fileName: 'template-maker-cert-v2-32.csv' });
const sqxRecords32 = Array.from({ length: 32 }, (_, index) => ({
  _id: 1000 + index,
  _source: 'sqx',
  'Strategy Name': `Strategy TM.${String(index + 1).padStart(2, '0')}`,
  Symbol: 'XAUUSD_darwinex',
  TimeFrame: 'H1',
  sources: { sqx: { fileName: `Strategy TM.${String(index + 1).padStart(2, '0')}.sqx`, hash: `hash-${index + 1}`, importedAt: '2026-05-15T00:00:00.000Z' } },
  provenance: { events: [], certVersion: 'TMA2.1', ruleset: 'template-maker-cert-v1' },
}));
const reconciled32 = tm.reconcileStrategySources(tm.getStrategies().concat(sqxRecords32));
assert.equal(reconciled32.length, 32, 'CSV + 32 SQX records should reconcile into 32 strategy records');
assert.ok(reconciled32.every(strategy => strategy.sources.csv && strategy.sources.sqx), 'each reconciled v2 record should keep csv+sqx sources');
assert.ok(reconciled32.every(strategy => tm.validateMetricsContract(strategy).valid), 'all reconciled v2 records should keep valid metrics');
await tm.clearResultStrategies();

function diversityStrategy(name, indicator, profitFactor, cagr, drawdown, trades, fitness = 0.9) {
  return {
    'Strategy Name': name,
    Symbol: 'XAUUSD_darwinex',
    TimeFrame: 'H1',
    Fitness: fitness,
    'Net profit': 10000,
    '# of trades': trades,
    'Profit factor': profitFactor,
    'Max DD %': drawdown,
    'Sharpe Ratio': 0.9,
    Stability: 0.8,
    'CAGR/Max DD %': cagr,
    'Winning Percent': 52,
    SQN: 2.1,
    RecoveryFactor: 3.5,
    CalmarRatio: 0.8,
    SortinoRatio: 1.1,
    '% Profitable Months': 62,
    sources: { sqx: { fileName: `${name}.sqx`, hash: `hash-${name}`, importedAt: '2026-05-15T00:00:00.000Z' } },
    logic: {
      features: {
        indicators: [indicator],
        operators: ['crossesabove'],
        params: [`${indicator}:period=20`],
        rules: ['long_entry'],
        signature: `${indicator}|crossesabove`
      }
    }
  };
}

await tm.loadFromCSV([
  diversityStrategy('TM Div 01', 'hma_atr_bands', 1.50, 0.72, 1.9, 280, 0.8),
  diversityStrategy('TM Div 02', 'hma_atr_bands', 1.64, 0.84, 1.6, 320, 0.9),
  diversityStrategy('TM Div 03', 'keltner_channel', 1.42, 0.66, 2.4, 260, 0.7),
], { fileName: 'template-maker-cert-v2-diversity.csv' });
const diversityStrategies = tm.getStrategies();
const similaritySame = tm.computeTemplateSimilarity(diversityStrategies[0], diversityStrategies[1]);
const similarityDifferent = tm.computeTemplateSimilarity(diversityStrategies[0], diversityStrategies[2]);
assert.equal(similaritySame.clusterMatch, true, 'same indicator templates should cluster');
assert.equal(similarityDifferent.clusterMatch, false, 'different indicator templates should remain diverse even with valid metrics');
const diversityReport = tm.getDiversityReport();
assert.equal(diversityReport.candidates, 3, 'all complete passed strategies should be diversity candidates');
assert.equal(diversityReport.clusters.length, 2, 'diversity should produce one similar cluster and one singleton');
const div01 = tm.getDiversityStatus(diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 01'));
const div02 = tm.getDiversityStatus(diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 02'));
const div03 = tm.getDiversityStatus(diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 03'));
assert.equal(div02.status, 'Ganador cluster', 'best score should win similar cluster');
assert.equal(div01.status, 'Similar descartada', 'non-winner similar template should be blocked');
assert.equal(div03.status, 'Diverso', 'structurally different template should stay diverse');
assert.equal(tm.canGenerateC2(diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 01')), false, 'non-winner cluster member should not generate C2');
assert.equal(tm.canGenerateC2(diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 02')), true, 'cluster winner should generate C2');
assert.equal(tm.canGenerateC2(diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 03')), true, 'diverse singleton should generate C2');
const c2Winner = diversityStrategies.find(strategy => strategy['Strategy Name'] === 'TM Div 02');
const c2Trace = tm.resolveC2Trace(c2Winner, { blockSetting: 'BS_Tendencia_v6', direction: 'LONG' });
assert.equal(c2Trace.indicatorBase, 'hma_atr_bands', 'C2 trace should prefill indicator base from logic features');
assert.equal(c2Trace.clusterId, div02.clusterId, 'C2 trace should prefill NumCluster from diversity status');
assert.equal(c2Trace.blockSetting, 'BS_Tendencia_v6', 'C2 trace should keep real BS_* blocksetting');
assert.ok(c2Trace.name.includes('BS_Tendencia_v6'), 'C2 name should include blocksetting');
assert.ok(c2Trace.name.includes('hma_atr_bands'), 'C2 name should include base indicator');
assert.ok(c2Trace.name.includes(div02.clusterId), 'C2 name should include cluster id');
assert.ok(c2Trace.name.includes('TM_Div_02'), 'C2 name should include source strategy');
assert.equal(tm.buildC2TemplateName(c2Winner, c2Trace), c2Trace.name, 'C2 name builder should be the single source of truth');
const lacityExitXml = fs.readFileSync(path.join(repoRoot, 'resources/template-maker-tool/exit_policy_lacity_strategy.xml'), 'utf8');
const exitPreview = await tm.getC2GenerationPreview(Object.assign({}, c2Winner, { _strategyXml: lacityExitXml }), { blockSetting: 'BS_Tendencia_v6' });
assert.equal(exitPreview.exitPolicyVersion, 'sqx-exit-policy-v1', 'C2 preview should expose exit policy version');
assert.ok(exitPreview.exitSummary.disabled.includes('Exit After Days LaCity'), 'C2 preview should disable ExitAfterDays');
assert.ok(exitPreview.exitSummary.disabled.includes('Exit After TDays LaCity'), 'C2 preview should disable ExitAfterTDays');
assert.ok(exitPreview.exitSummary.randomized.includes('Profit Target'), 'C2 preview should randomize Profit Target');
assert.ok(tm.detectExitComponents({ _strategyXml: lacityExitXml }).some(component => component.kind === 'exit_after_days'), 'Template Maker should expose detected ExitAfterDays');
assert.ok(tm.getExitAuditReport({ _strategyXml: lacityExitXml }).summary.disabled.includes('Exit After Bars'), 'Template Maker exit audit should use the global policy');
await tm.setDiversitySetting('structuralThreshold', 0.99);
assert.equal(tm.getDiversitySettings().structuralThreshold, 0.99, 'diversity setting should be editable');
await tm.clearResultStrategies();

const certCsv = 'Strategy Name;Symbol;TimeFrame;Fitness;Net profit;# of trades;Profit factor;Max DD %;Sharpe Ratio;Stability;CAGR/Max DD %;Winning Percent;SQN;RecoveryFactor;CalmarRatio;SortinoRatio;% Profitable Months\nStrategy 1;XAUUSD;H1;0.91;10000;260;1.45;12;0.9;0.8;1.1;48;2.1;3.5;0.8;1.1;62';
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
  'Strategy Name;Symbol (IS);TimeFrame (IS);Fitness;Net profit (IS);# of trades (IS);Profit factor (IS);Max DD % (IS);Sharpe Ratio (IS);Stability (IS);CAGR/Max DD % (IS);Winning Percent (IS);SQN (IS);RecoveryFactor (IS);CalmarRatio (IS);SortinoRatio (IS);% Profitable Months (IS);Net profit (OOS);# of trades (OOS);Profit factor (OOS);Max DD % (OOS);Sharpe Ratio (OOS);Stability (OOS);CAGR/Max DD % (OOS);Winning Percent (OOS);SQN (OOS);Recovery Factor (OOS);Calmar Ratio (OOS);Sortino Ratio (OOS);% Profitable Months (OOS)',
  'Strategy 4.21.40;XAUUSD_tick_TICK_ESTPlus07;H1;0,88;3675,22;218;1,45;18,2;0,69;0,82;0,66;45;1,7;2,4;0,6;0,9;54;5967,27;220;1,72;12,5;1,1;0,68;1,11;49;2,2;3,5;0,8;1,1;62',
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
  'Strategy Name;Symbol;TimeFrame;Fitness;Net profit;# of trades;Profit factor;Max DD %;Sharpe Ratio;Stability;CAGR/Max DD %;Winning Percent;SQN;RecoveryFactor;CalmarRatio;SortinoRatio;% Profitable Months',
  'Delete me;XAUUSD;H1;0.91;10000;260;1.45;12;0.9;0.8;1.1;48;2.1;3.5;0.8;1.1;62',
  'Keep me;EURUSD;H1;0.87;9000;240;1.4;14;0.8;0.7;1.0;47;1.9;3.2;0.7;1.0;58',
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
assert.equal(tm.getProvenance(merged[0]).ruleset, 'template-maker-cert-v2', 'reconciled provenance should stay on v2 ruleset');
assert.equal(await tm.computeFileHash('abc').then(hash => hash.length >= 8), true, 'computeFileHash should return a stable hash');
await tm.reset();
await tm.loadFromCSV([{
  'Strategy Name': 'Keep SQX',
  Symbol: 'XAUUSD',
  TimeFrame: 'H1',
  Fitness: 0.91,
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

tm.applyRemoteSnapshot({
  templateMakerSchemaVersion: 'template-maker-cert-v2',
  strategies: [{
    _id: 701,
    'Strategy Name': 'Remote TM',
    Symbol: 'XAUUSD',
    TimeFrame: 'H1',
    Fitness: '0.9',
    'Net profit': 1000,
    '# of trades': 250,
    'Profit factor': 1.4,
    'Max DD %': 10,
    'Sharpe Ratio': 0.8,
    Stability: 0.7,
    'CAGR/Max DD %': 1.2,
    'Winning Percent': 55,
    SQN: 2,
    'Recovery Factor': 3,
    'Calmar Ratio': 0.9,
    'Sortino Ratio': 1.1,
    '% Profitable Months': 60
  }],
  config: { currentCapa: 1, currentPreset: 'Commodities' }
});
assert.equal(tm.getStrategies()[0].Symbol, 'XAUUSD', 'remote snapshot should hydrate strategies');
assert.equal(tm.getCurrentPreset(), 'Commodities', 'remote snapshot should hydrate config');
const remoteSnapshot = tm.buildRemoteSnapshot();
assert.equal(remoteSnapshot.schemaVersion, 'remote-template-maker-state-v1', 'remote snapshot should expose schema');
assert.equal(remoteSnapshot.strategies.length, 1, 'remote snapshot should include strategies');
assert.equal(remoteSnapshot.config.currentPreset, 'Commodities', 'remote snapshot should include config');

let remoteSavePath = '';
let remoteSavePayload = null;
sandbox.fetch = async (url, options = {}) => {
  remoteSavePath = String(url);
  assert.equal(options.credentials, 'include', 'remote Template Maker request should include credentials');
  if (remoteSavePath.endsWith('/remote/template-maker/bootstrap')) {
    return {
      ok: true,
      json: async () => ({ ok: true, workspace: { id: 'ws_test' }, state: remoteSnapshot, recordCount: 1 })
    };
  }
  remoteSavePayload = JSON.parse(options.body || '{}');
  return {
    ok: true,
    json: async () => ({ ok: true, workspace: { id: 'ws_test' }, recordCount: 1 })
  };
};
const bootstrapResult = await tm.bootstrapRemoteState();
assert.ok(bootstrapResult.ok, 'remote bootstrap should resolve ok');
assert.equal(tm.getRemotePersistenceStatus().enabled, true, 'remote persistence should enable after bootstrap');
assert.equal(tm.getRemotePersistenceStatus().workspace.id, 'ws_test', 'remote persistence should remember workspace after bootstrap');
const saveResult = await tm.saveRemoteState('contract-test');
assert.ok(saveResult.ok, 'remote save should resolve ok');
assert.ok(remoteSavePath.endsWith('/remote/template-maker/save'), 'remote save should use Template Maker endpoint');
assert.equal(remoteSavePayload.source, 'contract-test', 'remote save should include source trace');
assert.equal(tm.getRemotePersistenceStatus().workspace.id, 'ws_test', 'remote persistence should remember workspace');
await tm.reset();

console.log('template maker contracts ok');
