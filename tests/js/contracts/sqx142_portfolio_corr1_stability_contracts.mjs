import assert from 'node:assert/strict';
import fs from 'node:fs';

const core = fs.readFileSync('backend/sqx-edge-tool/core/sqx142_portfolio_correlation_stability.py', 'utf8');
const registeredTool = fs.readFileSync('backend/sqx-edge-tool/tools/sqx142_portfolio_corr1_registered_decision.py', 'utf8');
const registeredWrapper = fs.readFileSync('tools/sqx142_portfolio_corr1_registered_decision.ps1', 'utf8');
const server = fs.readFileSync('backend/sqx-edge-tool/api/server.py', 'utf8');
const edgeFactory = fs.readFileSync('app/js/modules/edge-factory.js', 'utf8');
const edgeFactoryUi = fs.readFileSync('app/js/modules/edge-factory-ui.js', 'utf8');
const html = fs.readFileSync('app/SQX_Dashboard_v6.html', 'utf8');
const doc = fs.readFileSync('docs/SQX142_PORTFOLIO_CORR1_STABILITY_AUDIT.md', 'utf8');

assert.match(core, /PORTFOLIO_CORRELATION_STABILITY_VERSION = "sqx142-portfolio-corr1-stability-audit-v1"/);
assert.match(core, /CAPA1_C2_CORRELATION_SELECTION_VERSION = "sqx142-capa1-c2-corr1-template-selection-v1"/);
assert.match(core, /decision_domain: str = "capa2_portfolio_selection"/);
assert.match(core, /build_capa1_c2_correlation_selection_report/);
assert.match(core, /"selectionBasis": "IS_CORR only"/);
assert.match(core, /"auditBasis": "OOS3_CORR stability confirmation only"/);
assert.match(core, /"oos3MaySelectAlternates": False/);
assert.match(core, /nearestOos3Warnings/);
assert.doesNotMatch(core, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(registeredTool, /VERSION = "sqx142-capa1-c2-corr1-registered-decision-v1"/);
assert.match(registeredTool, /DEPRECATED_PORTFOLIO_ALIAS_VERSION = "sqx142-portfolio-corr1-registered-decision-v1"/);
assert.match(registeredTool, /DAILY_EQUITY_SUFFIX = "\/dailyEquity\.bin"/);
assert.match(registeredTool, /capa1_c2_corr1_registered_selection_decision/);
assert.match(registeredTool, /def project_identity/);
assert.doesNotMatch(registeredTool, /"asset": "AUDCAD"/);
assert.doesNotMatch(registeredTool, /"blockSetting": "BS_Momentum_v6"/);
assert.doesNotMatch(registeredTool, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(registeredWrapper, /Assert-NoSqxProcess/);
assert.match(registeredWrapper, /sqx142_portfolio_corr1_registered_decision\.py/);
assert.doesNotMatch(registeredWrapper, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(server, /\/api\/sqx142\/portfolio-correlation\/stability-audit/);
assert.match(server, /\/api\/sqx142\/capa1-c2-correlation\/stability-audit/);
assert.match(server, /\/api\/sqx142\/capa1-c2-corr1\/registered-decision/);
assert.match(server, /\/api\/sqx142\/portfolio-corr1\/registered-decision/);
assert.match(server, /build_portfolio_correlation_stability_report/);
assert.match(server, /build_capa1_c2_correlation_selection_report/);

assert.match(edgeFactory, /portfolioCorrelationStabilityVersion/);
assert.match(edgeFactory, /recordPortfolioCorrelationStability/);
assert.match(edgeFactory, /capa1C2CorrelationSelectionVersion/);
assert.match(edgeFactory, /recordC2TemplateSelection/);
assert.match(edgeFactory, /portfolio-correlation-stability/);
assert.match(edgeFactory, /capa1-c2-correlation-selection/);

assert.match(edgeFactoryUi, /runCorrelationStability/);
assert.match(edgeFactoryUi, /runRegisteredCorrelationDecision/);
assert.match(edgeFactoryUi, /renderCorrelationStability/);
assert.match(edgeFactoryUi, /\/sqx142\/portfolio-correlation\/stability-audit/);
assert.match(edgeFactoryUi, /\/sqx142\/capa1-c2-corr1\/registered-decision/);
assert.match(edgeFactoryUi, /recordC2TemplateSelection/);

assert.match(html, /edge-portfolio-corr-stability/);
assert.match(html, /SQX142-CAPA2-PORTFOLIO-CORR1/);
assert.match(html, /Auditoria Capa2 portfolio IS vs OOS3/);
assert.match(html, /edge-corr-run/);
assert.match(html, /edge-corr-registered/);
assert.match(html, /Analizar Capa1 C2 registrado/);
assert.match(html, /edge-corr1-analyze/);

assert.match(doc, /Status: `implemented_capa2_scope_with_capa1_alias_reclassified`/);
assert.match(doc, /sqx142-capa1-c2-corr1-registered-decision-v1/);
assert.match(doc, /sqx142-portfolio-corr1-registered-decision-v1/);
assert.match(doc, /SQX EDGE CORR1 TAGGED/);
assert.match(doc, /capa1_c2_corr1_registered_selection_decision/);
assert.match(doc, /OOS3 must not select alternates/);
assert.match(doc, /White Reality Check/);

const c1Doc = fs.readFileSync('docs/SQX142_CAPA1_C2_CORRELATION_TEMPLATE_SELECTION.md', 'utf8');
const c2Doc = fs.readFileSync('docs/SQX142_CAPA2_PORTFOLIO_CORRELATION_ADAPTATION.md', 'utf8');
const bridgeDoc = fs.readFileSync('docs/SQX142_CORRELATION_C1_C2_PORTFOLIO_BRIDGE.md', 'utf8');

assert.match(c1Doc, /capa1_c2_template_selection/);
assert.match(c1Doc, /c2_template_selection_decision/);
assert.match(c1Doc, /C2 template winners from IS: `1`/);
assert.match(c2Doc, /capa2_portfolio_selection/);
assert.match(c2Doc, /SQX EDGE C2 CORR1 STABILITY/);
assert.match(bridgeDoc, /edgeFactory\.c2TemplateSelection/);
assert.match(bridgeDoc, /edgeFactory\.portfolioCorrelationStability/);

console.log('sqx142 portfolio corr1 stability contracts ok');
