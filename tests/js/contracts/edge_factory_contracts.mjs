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
assert.equal(SQX.edgeFactory.steps()[7].id, 'portfolio');

SQX.edgeFactory.completeStep('session', true);
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1')).completedSteps[0], 'session');
SQX.edgeFactory.setActiveStep('capa1-generate');
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1')).activeStep, 'capa1-generate');

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
assert.equal(report.rows.some(row => row.diversityStatus === 'similar'), true);

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const appConfig = fs.readFileSync(path.join(repoRoot, 'app/js/app-config.js'), 'utf8');
const indexJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/index.js'), 'utf8');

assert.equal(html.includes('id="edge-factory-shell"'), true);
assert.equal(html.includes('id="edge-tool-drawer"'), true);
assert.equal(html.includes('id="edge-portfolio-lab"'), true);
assert.equal(html.includes('Custom libre avanzado'), true);
assert.equal(html.includes('data-edge-tool="projectgen"'), true);
assert.equal(appConfig.includes('hiddenInPrimary'), true);
assert.equal(indexJs.includes('edge-factory'), true);
assert.equal(indexJs.includes('edge-factory-ui'), true);

console.log('edge factory contracts ok');
