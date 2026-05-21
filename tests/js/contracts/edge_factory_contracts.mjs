import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';

const { SQX, sandbox } = createLoadedSandbox([
  'app/js/modules/storage.js',
  'app/js/modules/ui.js',
  'app/js/modules/edge-factory.js',
]);

sandbox.SQX_CONFIG.storageKeys = {
  edgeFactoryState: 'sqx_edge_factory_state_v1',
};

assert.equal(SQX.edgeFactory.version, 'edge-factory-state-v1');
assert.equal(SQX.edgeFactory.storageKey(), 'sqx_edge_factory_state_v1');
assert.equal(SQX.edgeFactory.steps().length, 8);
assert.equal(SQX.edgeFactory.steps()[0].id, 'session');
assert.equal(SQX.edgeFactory.steps()[0].label, 'Punto de partida');
assert.equal(SQX.edgeFactory.steps()[7].id, 'portfolio');
assert.equal(SQX.edgeFactory.steps()[7].label, 'Portfolio');

SQX.edgeFactory.completeStep('session', true);
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1')).completedSteps[0], 'session');
SQX.edgeFactory.setActiveStep('capa1-generate');
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1')).activeStep, 'capa1-generate');

SQX.edgeFactory.recordPlanMining({
  num: 7,
  phase: 2,
  asset: 'US500',
  tf: 'M15',
  dir: 'SHORT',
  bs: 'BS_Volumen_v6_intraday_v6',
  source: 'asset-card',
  blocksettingTrace: { canonicalId: 'BS_Volumen_v6_intraday_v6', filename: 'BS_Volumen_v6_intraday_v6.sqb', sha256Short: 'abc123' }
});
let edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.selectedMining.asset, 'US500');
assert.equal(edgeState.selectedMining.timeframe, 'M15');
assert.equal(edgeState.selectedCard.blockSetting, 'BS_Volumen_v6_intraday_v6');
assert.equal(edgeState.completedSteps.includes('asset'), true);

SQX.edgeFactory.recordProjectGeneration({
  capa: 1,
  mode: 'methodology-selected',
  minings: [{ num: 7, asset: 'US500', tf: 'M15', dir: 'SHORT', bs: 'BS_Volumen_v6_intraday_v6' }],
  results: [{ ok: true, file: 'Mining07_US500_M15_Capa1.cfx' }],
  outputFiles: [{ name: 'Mining07_US500_M15_Capa1.cfx', size: 1234 }]
});
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.capa1Outputs[0].results.ok, 1);
assert.equal(edgeState.completedSteps.includes('capa1-generate'), true);
assert.equal(edgeState.activeStep, 'capa1-analyze');

SQX.edgeFactory.recordTemplateMakerAnalysis({
  report: { total: 32, passed: 5, review: 2, failed: 25, certified: 32, diversity: { clusters: 4, winners: 3 } },
  readyForC2: 3
});
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.capa1Analysis.winners, 3);
assert.equal(edgeState.activeStep, 'c2-template');

SQX.edgeFactory.recordC2Template({
  name: 'template_US500_BS_Volumen_ATR_CL01_SHORT_M15',
  asset: 'US500',
  timeframe: 'M15',
  direction: 'SHORT',
  blockSetting: 'BS_Volumen_v6_intraday_v6',
  indicatorBase: 'ATR',
  clusterId: 'CL01'
});
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.c2Template.clusterId, 'CL01');
assert.equal(edgeState.activeStep, 'capa2-generate');

const sample = [
  'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting,indicator',
  'A,AUDCAD,H4,1.7,6.0,18,240,BS_Volatilidad_v6,LinearRegression',
  'B,AUDCAD,H4,1.65,5.8,19,230,BS_Volatilidad_v6,LinearRegression',
  'C,XAUUSD,H1,1.5,4.8,22,330,BS_Tendencia_v6,KER',
].join('\n');
const rows = SQX.edgeFactory.parsePortfolioRows(sample);
const report = SQX.edgeFactory.buildPortfolioShortlist(rows);
assert.equal(rows.length, 3);
assert.equal(report.total, 3);
assert.equal(report.winners, 2);
assert.equal(report.version, 'portfolio-lab-mvp-v2');
assert.equal(report.rows.some(row => row.diversityStatus === 'similar'), true);
assert.equal(report.rows.some(row => row.diversityStatus === 'portfolio'), true);
const semicolonRows = SQX.edgeFactory.parsePortfolioRows('Strategy Name;Symbol;TimeFrame;Profit factor;Ret/DD Ratio;Max DD %;# of trades\nD;US500;M15;1,45;4,2;23;410');
assert.equal(semicolonRows[0].profitFactor, 1.45);
assert.equal(semicolonRows[0].asset, 'US500');
SQX.edgeFactory.recordPortfolioLab(report);
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.portfolioLab.winners, 2);
assert.equal(edgeState.completedSteps.includes('portfolio'), true);
assert.equal(SQX.edgeFactory.contextSummary(edgeState).portfolio.includes('ganadores diversos'), true);
assert.equal(SQX.edgeFactory.contextSummary({}).session.includes('Pendiente:'), true);

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const appConfig = fs.readFileSync(path.join(repoRoot, 'app/js/app-config.js'), 'utf8');
const indexJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/index.js'), 'utf8');

assert.equal(html.includes('id="edge-factory-shell"'), true);
assert.equal(html.includes('id="edge-tool-drawer"'), true);
assert.equal(html.includes('id="edge-portfolio-lab"'), true);
assert.equal(html.includes('id="edge-portfolio-threshold"'), true);
assert.equal(html.includes('id="edge-portfolio-export-csv"'), true);
assert.equal(html.includes('Del asset al portfolio, sin perder el hilo'), true);
assert.equal(html.includes('Haz: valida estado remoto.'), true);
assert.equal(html.includes('data-edge-context="asset"'), true);
assert.equal(html.includes('data-edge-context="c2-template"'), true);
assert.equal(html.includes('Custom libre avanzado'), true);
assert.equal(html.includes('data-edge-tool="projectgen"'), true);
assert.equal(appConfig.includes('hiddenInPrimary'), true);
assert.equal(indexJs.includes('edge-factory'), true);
assert.equal(indexJs.includes('edge-factory-ui'), true);

console.log('edge factory contracts ok');
