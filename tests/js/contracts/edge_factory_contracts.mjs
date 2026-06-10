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
assert.equal(SQX.edgeFactory.portfolioLabVersion, 'portfolio-lab-governed-v1');
assert.equal(SQX.edgeFactory.portfolioMasterVersion, 'portfolio-master-contract-v1');
assert.equal(SQX.edgeFactory.portfolioMasterInputsVersion, 'portfolio-master-inputs-pending-v1');
assert.equal(SQX.edgeFactory.backportOperatorPanelVersion, 'ui-integration1-backport-operator-panel-v1');
assert.equal(SQX.edgeFactory.storageKey(), 'sqx_edge_factory_state_v1');
assert.equal(SQX.edgeFactory.steps().length, 8);
assert.equal(SQX.edgeFactory.steps()[0].id, 'session');
assert.equal(SQX.edgeFactory.steps()[0].label, 'Punto de partida');
assert.equal(SQX.edgeFactory.steps()[7].id, 'portfolio');
assert.equal(SQX.edgeFactory.steps()[7].label, 'Portfolio');
assert.equal(SQX.edgeFactory.basicSteps().length, 6);
assert.deepEqual(Array.from(SQX.edgeFactory.basicSteps().map(step => step.id)), [
  'basic-select',
  'basic-download',
  'basic-upload',
  'basic-analyze',
  'basic-export',
  'basic-finish',
]);
assert.equal(SQX.edgeFactory.visibleStepsForMode('basic').length, 6);
assert.equal(SQX.edgeFactory.visibleStepsForMode('advanced').length, 8);
assert.equal(SQX.edgeFactory.defaultState().experienceMode, 'basic');
assert.equal(typeof SQX.edgeFactory.setExperienceMode, 'function');

SQX.edgeFactory.setExperienceMode('advanced');
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1')).experienceMode, 'advanced');
SQX.edgeFactory.setExperienceMode('basic');
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1')).experienceMode, 'basic');

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
  clusterId: 'CL01',
  advancedCapa2AnalysisActive: false
});
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.c2Template.clusterId, 'CL01');
assert.equal(edgeState.activeStep, 'capa2-generate');
assert.equal(edgeState.activeStep === 'capa2-analyze', false);
assert.equal(edgeState.portfolioLab, null);
assert.equal(edgeState.completedSteps.includes('capa2-analyze'), false);
SQX.edgeFactory.recordBasicSelection({
  asset: 'EURGBP',
  timeframe: 'H1',
  direction: 'both',
  blockSetting: 'BS_Estadistico_v6',
});
SQX.edgeFactory.recordBasicDownloadBatch({
  files: [{ name: 'Project_EURGBP_H1_BS_Estadistico_v6_LS_Capa1.cfx' }, { name: 'Project_EURGBP_H1_BS_Estadistico_v6_LS_Capa2.cfx' }],
  results: [{ ok: true, capa: 1 }, { ok: true, capa: 2 }],
});
SQX.edgeFactory.recordBasicFinalFiles([{ name: 'DatabankExport.csv' }, { name: 'winner.sqx' }]);
SQX.edgeFactory.recordBasicTemplateExports({
  files: [{ name: 'template_EURGBP_BS_Estadistico_v6_MACD_CL01_BOTH_H1.sqx' }],
  templates: [{ name: 'template_EURGBP_BS_Estadistico_v6_MACD_CL01_BOTH_H1', asset: 'EURGBP', timeframe: 'H1', direction: 'BOTH' }],
});
SQX.edgeFactory.finishBasicFlow();
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.deepEqual(Array.from(SQX.edgeFactory.basicCompletedSteps(edgeState)), [
  'basic-select',
  'basic-download',
  'basic-upload',
  'basic-analyze',
  'basic-export',
  'basic-finish',
]);

const sample = [
  'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting,indicator,cluster,Source Phase,Source Databank,Forward Status,Pass Source,Returns',
  'A,AUDCAD,H4,1.7,6.0,18,240,BS_Volatilidad_v6,LinearRegression,CL01,phase28_capa2_forward,Foward,PASSED,natural,0.01|0.02|-0.01|0.03',
  'B,AUDCAD,H1,1.6,5.4,20,260,BS_Tendencia_v6,MACD,CL02,phase28_capa2_forward,Foward,PASSED,natural,',
  'C,AUDCAD,H4,1.62,5.8,19,230,BS_Volatilidad_v6,LinearRegression,CL03,phase28_capa2_forward,Forward,PASSED,natural,0.01|0.02|-0.01|0.03',
  'D,XAUUSD,H1,1.5,4.8,22,330,BS_Tendencia_v6,KER,CL04,phase28_capa2_forward,Foward,PASSED,natural,',
  'E,US500,M15,1.45,4.1,24,420,BS_Volumen_v6_intraday_v6,ATR,CL05,phase28_capa2_forward,Foward,PASSED,natural,',
  'F,EURUSD,M30,1.47,4.4,21,310,BS_MeanReversion_v6,RSI,CL06,phase28_capa2_forward,Forward,PASSED,natural,',
  'G,GBPJPY,H4,1.55,5.1,26,205,BS_Tendencia_v6,SUPER,CL07,phase28_capa2_forward,Foward,PASSED,natural,',
  'H,USDJPY,H1,1.49,4.6,23,286,BS_Volatilidad_v6,ADX,CL08,phase28_capa2_forward,Foward,PASSED,natural,',
  'I,NAS100,M15,1.44,4.3,25,398,BS_Volumen_v6_intraday_v6,CHOPPINESS,CL09,phase28_capa2_forward,Forward,PASSED,natural,',
  'J,GER40,H1,1.46,4.5,24,274,BS_Tendencia_v6,HURST,CL10,phase28_capa2_forward,Foward,PASSED,natural,',
  'K,GBPUSD,M30,1.43,4.2,22,302,BS_Tendencia_v6,MACD,CL11,phase28_capa2_forward,Foward,PASSED,natural,',
  'L,XAGUSD,H4,1.7,6.4,18,250,BS_Volatilidad_v6,LinearRegression,CL12,phase28_capa2_forward,Synthetic,FORCED PASS,forced,0.01|0.01|0.01|0.01',
].join('\n');
const rows = SQX.edgeFactory.parsePortfolioRows(sample);
const report = SQX.edgeFactory.buildPortfolioShortlist(rows);
assert.equal(rows.length, 12);
assert.equal(report.total, 12);
assert.equal(report.winners >= 8 && report.winners <= 12, true);
assert.equal(report.version, 'portfolio-lab-governed-v1');
assert.equal(report.sourcePhase, 'phase28_capa2_forward');
assert.equal(report.sourceDatabank, 'Foward');
assert.equal(report.riskPlan.status, 'target-ready');
assert.equal(report.riskPlan.baseRiskPct, 0.2);
assert.equal(report.riskPlan.maxInitialRiskPct, 0.3);
assert.equal(report.riskPlan.fullDeploymentAllowed, false);
assert.equal(report.riskPlan.aggregateRisk, 'requires_portfolio_master_contract');
assert.equal(report.correlationStatus.state, 'correlation-available');
assert.equal(report.deploymentSteps.some(step => step.id === 'portfolio-master-correlation'), true);
assert.equal(report.rejected, 1);
assert.equal(report.rows.some(row => row.diversityStatus === 'similar'), true);
assert.equal(report.rows.some(row => row.diversityStatus === 'portfolio'), true);
assert.equal(report.rows.find(row => row.strategy === 'L').eligibleForPortfolio, false);
assert.equal(report.rows.find(row => row.strategy === 'L').reason.includes('forced/synthetic pass rejected'), true);
const semicolonRows = SQX.edgeFactory.parsePortfolioRows('Strategy Name;Symbol;TimeFrame;Profit factor;Ret/DD Ratio;Max DD %;# of trades;Source Databank;Forward Status\nD;US500;M15;1,45;4,2;23;410;Foward;PASSED');
assert.equal(semicolonRows[0].profitFactor, 1.45);
assert.equal(semicolonRows[0].asset, 'US500');
const noForward = SQX.edgeFactory.buildPortfolioShortlist('strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,Source Databank,Forward Status\nNoSource,US500,M15,1.5,4,20,200,WFM,PASSED');
assert.equal(noForward.rows[0].eligibleForPortfolio, false);
assert.equal(noForward.rows[0].reason.includes('sourceDatabank != Forward/Foward'), true);
const dirty = SQX.edgeFactory.buildPortfolioShortlist('strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,Source Databank,Forward Status\nC:\\Users\\Ivan SQX\\secret.sqx,US500,M15,1.5,4,20,200,Foward,PASSED');
assert.equal(dirty.rows[0].strategy.includes('C:\\'), false);
const blockedMaster = SQX.edgeFactory.buildPortfolioMasterContract({ labReport: report });
assert.equal(blockedMaster.version, 'portfolio-master-contract-v1');
assert.equal(blockedMaster.status, 'blocked_pending_operator_inputs');
assert.equal(blockedMaster.liveDeploymentAllowed, false);
assert.equal(blockedMaster.artifactGenerationStatus, 'blocked');
assert.equal(blockedMaster.artifactGenerationAllowed, false);
assert.equal(blockedMaster.sqxExecutionAllowed, false);
assert.equal(blockedMaster.fitPortfolioAllowed, false);
assert.equal(blockedMaster.forcedPassAllowed, false);
assert.equal(blockedMaster.inputIntake.version, 'portfolio-master-inputs-pending-v1');
assert.equal(blockedMaster.inputIntake.status, 'pending_inputs');
assert.equal(blockedMaster.requiredInputs.find(item => item.id === 'forward-csv').status, 'blocked');
assert.equal(blockedMaster.requiredInputs.find(item => item.id === 'comparable-equity-returns').status, 'blocked');
assert.equal(blockedMaster.requiredInputs.find(item => item.id === 'account-context').status, 'blocked');
assert.equal(blockedMaster.requiredInputs.find(item => item.id === 'broker-context').status, 'blocked');
assert.equal(blockedMaster.requiredInputs.length, 5);
assert.equal(blockedMaster.outputReadback.aggregateRisk.status, 'unavailable');
const portfolioWinners = report.rows.filter(row => row.diversityStatus === 'portfolio');
const masterSeriesCsv = [
  'strategy,Returns',
  ...portfolioWinners.map((row, index) => {
    const offset = (index + 1) / 1000;
    return `"${row.strategy}","${[0.01 + offset, -0.004 + offset, 0.012 - offset, 0.006 + offset, -0.003 + offset].join('|')}"`;
  }),
].join('\n');
const readyMaster = SQX.edgeFactory.buildPortfolioMasterContract({
  labReport: report,
  forwardCsv: sample,
  comparableSeriesCsv: masterSeriesCsv,
  accountBrokerContext: 'accountModel=demo-forward-review; brokerProfile=ECN; baseCurrency=USD; accountNumber=123456; token=abcdefghijklmnopqrstuvwxyz123456; localPath=C:\\Users\\Ivan SQX\\private.csv',
});
const readyMasterJson = JSON.stringify(readyMaster);
assert.equal(readyMaster.status, 'ready_for_master_review');
assert.equal(readyMaster.inputIntake.status, 'ready_for_operator_review');
assert.equal(readyMaster.inputIntake.missingInputs.length, 0);
assert.equal(readyMaster.liveDeploymentAllowed, false);
assert.equal(readyMaster.deploymentClaim, 'none');
assert.equal(Object.hasOwn(readyMaster, 'deploymentSteps'), false);
assert.equal(readyMaster.readbackSteps.some(step => step.id === 'operator-review'), true);
assert.equal(readyMaster.outputReadback.aggregateRisk.status, 'true_aggregate_risk_ready');
assert.equal(readyMaster.outputReadback.aggregateRisk.trueAggregateRiskAvailable, true);
assert.equal(readyMaster.inputReadback.accountBrokerContext.privateFieldsRemoved >= 2, true);
assert.equal(readyMasterJson.includes('C:\\'), false);
assert.equal(readyMasterJson.includes('123456'), false);
assert.equal(readyMasterJson.includes('abcdefghijklmnopqrstuvwxyz123456'), false);
SQX.edgeFactory.recordPortfolioLab(report);
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.portfolioLab.version, 'portfolio-lab-governed-v1');
assert.equal(edgeState.portfolioMasterContract.version, 'portfolio-master-contract-v1');
assert.equal(edgeState.portfolioMasterContract.status, 'blocked_pending_operator_inputs');
assert.equal(edgeState.portfolioLab.winners >= 8 && edgeState.portfolioLab.winners <= 12, true);
assert.equal(edgeState.portfolioLab.rows.every(row => row.forwardSource != null && row.forwardStatus != null), true);
assert.equal(edgeState.portfolioLab.rows.some(row => Object.hasOwn(row, 'Returns')), false);
assert.equal(edgeState.completedSteps.includes('portfolio'), false);
assert.equal(SQX.edgeFactory.contextSummary(edgeState).portfolio.includes('portfolio-lab-governed-v1'), true);
assert.equal(SQX.edgeFactory.contextSummary({}).session.includes('Pendiente:'), true);
SQX.edgeFactory.recordPortfolioMasterContract({
  labReport: report,
  forwardCsv: sample,
  comparableSeriesCsv: masterSeriesCsv,
  accountBrokerContext: { accountModel: 'demo-forward-review', brokerProfile: 'ECN', baseCurrency: 'USD', accountNumber: '123456' },
});
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.portfolioMasterContract.status, 'ready_for_master_review');
assert.equal(JSON.stringify(edgeState.portfolioMasterContract).includes('123456'), false);
assert.equal(edgeState.completedSteps.includes('portfolio'), true);

const backportOps = SQX.edgeFactory.backportOperatorOperations();
assert.equal(backportOps.length, 8);
assert.equal(backportOps.some(op => op.id === 'mcp-status' && op.method === 'GET' && op.endpoint === '/sqx142/mcp-like/status'), true);
assert.equal(backportOps.some(op => op.id === 'correlation-filter' && op.endpoint === '/sqx142/correlation-filter/external'), true);
assert.equal(backportOps.some(op => op.id === 'portfolio-correlation-stability' && op.endpoint === '/sqx142/portfolio-correlation/stability-audit'), true);
assert.equal(backportOps.some(op => op.id === 'capa1-c2-correlation-selection' && op.endpoint === '/sqx142/capa1-c2-correlation/stability-audit'), true);
assert.equal(backportOps.some(op => op.id === 'monte-carlo-benchmarks' && op.expectedVersion === 'sqx142-monte-carlo-candidate-benchmarks-v1'), true);
assert.equal(backportOps.some(op => op.id === 'mt5-data-probe' && op.endpoint === '/sqx142/mt5-data-intake/probe'), true);
assert.equal(backportOps.some(op => op.id === 'migration-checklist' && op.endpoint === '/sqx142/migration/copy-only-checklist'), true);
assert.equal(SQX.edgeFactory.buildBackportOperatorPayload('mcp-status'), null);
const correlationPayload = SQX.edgeFactory.buildBackportOperatorPayload('correlation-filter', SQX.edgeFactory.backportOperatorSample('correlation-filter'), { maxCorrelation: 0.5 });
assert.equal(correlationPayload.includeCsvExport, true);
assert.equal(correlationPayload.includeSqxTagCsv, true);
assert.equal(correlationPayload.settings.maxCorrelation, 0.5);
assert.match(correlationPayload.csv, /returnSeries/);
const corrStabilityPayload = SQX.edgeFactory.buildBackportOperatorPayload('portfolio-correlation-stability', SQX.edgeFactory.backportOperatorSample('portfolio-correlation-stability'), { maxIsCorrelation: 0.5 });
assert.equal(corrStabilityPayload.includeCsvExport, true);
assert.equal(corrStabilityPayload.settings.maxIsCorrelation, 0.5);
assert.match(corrStabilityPayload.csv, /oos3ReturnSeries/);
const c2SelectionPayload = SQX.edgeFactory.buildBackportOperatorPayload('capa1-c2-correlation-selection', SQX.edgeFactory.backportOperatorSample('capa1-c2-correlation-selection'), { maxIsCorrelation: 0.5 });
assert.equal(c2SelectionPayload.includeCsvExport, true);
assert.equal(c2SelectionPayload.settings.maxIsCorrelation, 0.5);
assert.match(c2SelectionPayload.csv, /oos3ReturnSeries/);
const mt5Payload = SQX.edgeFactory.buildBackportOperatorPayload('mt5-data-probe', SQX.edgeFactory.backportOperatorSample('mt5-data-probe'), { asset: 'AUDCAD', timeframe: 'H1', minBars: 20 });
assert.equal(mt5Payload.asset, 'AUDCAD');
assert.equal(mt5Payload.timeframe, 'H1');
assert.equal(mt5Payload.settings.minBars, 20);
assert.match(mt5Payload.csv, /time,open,high,low,close,volume/);
const migrationPayload = SQX.edgeFactory.buildBackportOperatorPayload('migration-checklist', SQX.edgeFactory.backportOperatorSample('migration-checklist'));
assert.equal(migrationPayload.items.length, 3);
assert.equal(migrationPayload.items[0].relativePath, 'user/extend/ResultsPlugins/SQX Edge Readiness Panel');
const backportSummary = SQX.edgeFactory.summarizeBackportOperatorResult('migration-checklist', {
  ok: true,
  version: 'sqx142-copy-only-migration-checklist-v1',
  summary: { inputItems: 3, allowCopy: 1, reviewCopy: 1, blockCopy: 1 },
  guards: { sqx_runtime_started: false, data_db_write_allowed: false, user_projects_write_allowed: false, remote_tester_access: false },
  privacy: { local_paths_returned: false, tokens_returned: false, private_fields_returned: false },
  csvExport: 'itemId,decision\nx,allow_copy\n',
});
assert.equal(backportSummary.panelVersion, 'ui-integration1-backport-operator-panel-v1');
assert.equal(backportSummary.status, 'ok');
assert.equal(backportSummary.total, 3);
assert.equal(backportSummary.primaryCount, 1);
assert.equal(backportSummary.csvExportAvailable, true);
const correlationSummary = SQX.edgeFactory.summarizeBackportOperatorResult('correlation-filter', {
  ok: true,
  version: 'sqx142-correlation-filter-external-v1',
  summary: { inputRows: 2, portfolio: 1, similar: 1, review: 0 },
  privacy: { local_paths_returned: false, tokens_returned: false, private_fields_returned: false },
  csvExport: 'candidateId,decision\nx,portfolio\n',
  sqxTagCsv: 'strategyRef,candidateId,decision\nstrategy_abc,x,portfolio\n',
});
assert.equal(correlationSummary.sqxTagCsvAvailable, true);
SQX.edgeFactory.recordBackportOperatorResult('migration-checklist', backportSummary.raw);
edgeState = JSON.parse(sandbox.localStorage.getItem('sqx_edge_factory_state_v1'));
assert.equal(edgeState.backportOperatorPanel.version, 'ui-integration1-backport-operator-panel-v1');
assert.equal(edgeState.backportOperatorPanel.lastOperation.endpoint, '/sqx142/migration/copy-only-checklist');

const exampleOnlyForward = sample.replace('strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting,indicator,cluster,Source Phase,Source Databank,Forward Status,Pass Source,Returns', 'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting,indicator,cluster,Source Phase,Source Databank,Forward Status,Pass Source,Returns,Example Only')
  .split('\n').map((line, index) => index === 0 ? line : `${line},true`).join('\n');
const sampleBlockedMaster = SQX.edgeFactory.buildPortfolioMasterContract({
  labReport: report,
  forwardCsv: exampleOnlyForward,
  comparableSeriesCsv: masterSeriesCsv,
  accountContext: 'accountModel=demo-forward-review; baseCurrency=USD; riskBudgetMode=0.2 pct base',
  brokerContext: 'brokerProfile=ECN; executionModel=hedging-netting reviewed',
});
assert.equal(sampleBlockedMaster.status, 'blocked_pending_operator_inputs');
assert.equal(sampleBlockedMaster.inputReadback.forwardCsv.sampleRows > 0, true);
assert.equal(sampleBlockedMaster.blockedReasons.some(reason => reason.includes('CSV de ejemplo')), true);

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const dashboardCss = fs.readFileSync(path.join(repoRoot, 'app/css/dashboard.css'), 'utf8');
const appConfig = fs.readFileSync(path.join(repoRoot, 'app/js/app-config.js'), 'utf8');
const indexJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/index.js'), 'utf8');

assert.equal(html.includes('id="edge-factory-shell"'), true);
assert.equal(html.includes('global-step-nav-top'), true);
assert.equal(html.includes('id="edge-methodology-panel"'), true);
assert.equal(html.includes('Ver pipeline avanzado completo'), true);
assert.equal(html.includes('id="edge-tool-drawer"'), true);
assert.equal(html.includes('data-edge-mode="basic"'), true);
assert.equal(html.includes('data-edge-mode="advanced"'), true);
assert.equal(html.includes('Modo básico'), true);
assert.equal(html.includes('Modo avanzado'), true);
assert.equal(html.includes('data-edge-advanced-only'), true);
assert.equal((html.match(/<label class="edge-manual-check" data-edge-advanced-only>/g) || []).length, 8);
assert.equal(html.includes('<details class="edge-methodology-advanced" data-edge-advanced-only>'), true);
assert.equal(html.includes('<div class="edge-tool-drawer" id="edge-tool-drawer" hidden data-edge-advanced-only>'), true);
assert.equal(html.includes('<details class="edge-advanced-custom" data-edge-advanced-only>'), true);
assert.match(dashboardCss, /\.edge-factory-shell\.edge-mode-basic \[data-edge-advanced-only\]\s*\{\s*display:none !important;\s*\}/);
assert.equal(html.includes('class="edge-factory-command-strip"'), true);
assert.equal(html.includes('data-edge-signal="asset"'), true);
assert.equal(html.includes('data-edge-signal="portfolio"'), true);
assert.equal(html.includes('id="edge-portfolio-lab"'), true);
assert.equal(html.includes('Portfolio Lab Gobernado'), true);
assert.equal(html.includes('id="edge-portfolio-master-contract"'), true);
assert.equal(html.includes('Portfolio Master Contract'), true);
assert.equal(html.includes('id="edge-master-forward-input"'), true);
assert.equal(html.includes('id="edge-master-series-input"'), true);
assert.equal(html.includes('id="edge-master-account-input"'), true);
assert.equal(html.includes('id="edge-master-broker-input"'), true);
assert.equal(html.includes('portfolio-master-inputs-pending-v1'), true);
assert.equal(html.includes('no autoriza despliegue real'), true);
assert.equal(html.includes('id="edge-backport-operator-panel"'), true);
assert.equal(html.includes('UI-INTEGRATION1'), true);
assert.equal(html.includes('ui-integration1-backport-operator-panel-v1'), true);
assert.equal(html.includes('id="edge-backport-operation"'), true);
assert.equal(html.includes('value="correlation-filter"'), true);
assert.equal(html.includes('value="capa1-c2-correlation-selection"'), true);
assert.equal(html.includes('value="monte-carlo-benchmarks"'), true);
assert.equal(html.includes('value="mt5-data-probe"'), true);
assert.equal(html.includes('value="migration-checklist"'), true);
assert.equal(html.includes('id="edge-backport-run"'), true);
assert.equal(html.includes('id="edge-backport-export-sqx-tags"'), true);
assert.equal(html.includes('id="edge-backport-results"'), true);
assert.equal(html.includes('sin data.db writes'), true);
assert.equal(html.includes('sin user/projects writes'), true);
assert.equal(html.includes('lab-only'), true);
assert.equal(html.includes('no borra databank'), true);
assert.equal(html.includes('no filtra en SQX'), true);
assert.equal(html.includes('id="edge-portfolio-threshold"'), true);
assert.equal(html.includes('id="edge-portfolio-export-csv"'), true);
assert.equal(html.includes('portfolio-lab-governed-v1'), true);
assert.equal(html.includes('id="edge-portfolio-max-timeframe"'), true);
assert.equal(html.includes('Contrato Forward/Foward'), true);
assert.equal(html.includes('correlacion real solo con equity/returns comparables'), true);
assert.equal(html.includes('Modo básico: del activo al template C2'), true);
assert.equal(html.includes('perfil SQX destino'), true);
assert.equal(html.includes('SQ default / configurable'), true);
assert.equal(html.includes('Haz: valida estado remoto.'), true);
assert.equal(html.includes('data-edge-context="asset"'), true);
assert.equal(html.includes('data-edge-context="c2-template"'), true);
assert.equal(html.includes('Custom libre avanzado'), true);
assert.equal(html.includes('data-edge-tool="projectgen"'), true);
assert.equal(appConfig.includes('hiddenInPrimary'), true);
assert.equal(indexJs.includes('edge-factory'), true);
assert.equal(indexJs.includes('edge-factory-ui'), true);
assert.equal(typeof SQX.edgeFactory.recordC2TemplateSelection, 'function');
assert.equal(SQX.edgeFactory.backportOperatorOperations().some(item => item.id === 'capa1-c2-correlation-selection'), true);
assert.equal(SQX.edgeFactory.capa1C2CorrelationSelectionVersion, 'sqx142-capa1-c2-corr1-template-selection-v1');

console.log('edge factory contracts ok');
