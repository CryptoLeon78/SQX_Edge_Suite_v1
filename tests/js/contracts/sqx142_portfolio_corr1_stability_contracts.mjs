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
assert.match(core, /"selectionBasis": "IS_CORR only"/);
assert.match(core, /"auditBasis": "OOS3_CORR stability confirmation only"/);
assert.match(core, /"oos3MaySelectAlternates": False/);
assert.match(core, /nearestOos3Warnings/);
assert.doesNotMatch(core, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(registeredTool, /VERSION = "sqx142-portfolio-corr1-registered-decision-v1"/);
assert.match(registeredTool, /DAILY_EQUITY_SUFFIX = "\/dailyEquity\.bin"/);
assert.match(registeredTool, /corr1_registered_stability_decision/);
assert.doesNotMatch(registeredTool, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(registeredWrapper, /Assert-NoSqxProcess/);
assert.match(registeredWrapper, /sqx142_portfolio_corr1_registered_decision\.py/);
assert.doesNotMatch(registeredWrapper, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(server, /\/api\/sqx142\/portfolio-correlation\/stability-audit/);
assert.match(server, /\/api\/sqx142\/portfolio-corr1\/registered-decision/);
assert.match(server, /build_portfolio_correlation_stability_report/);

assert.match(edgeFactory, /portfolioCorrelationStabilityVersion/);
assert.match(edgeFactory, /recordPortfolioCorrelationStability/);
assert.match(edgeFactory, /portfolio-correlation-stability/);

assert.match(edgeFactoryUi, /runCorrelationStability/);
assert.match(edgeFactoryUi, /runRegisteredCorrelationDecision/);
assert.match(edgeFactoryUi, /renderCorrelationStability/);
assert.match(edgeFactoryUi, /\/sqx142\/portfolio-correlation\/stability-audit/);
assert.match(edgeFactoryUi, /\/sqx142\/portfolio-corr1\/registered-decision/);

assert.match(html, /edge-portfolio-corr-stability/);
assert.match(html, /IS selecciona · OOS3 audita · no optimiza Forward/);
assert.match(html, /edge-corr-run/);
assert.match(html, /edge-corr-registered/);
assert.match(html, /edge-corr1-analyze/);

assert.match(doc, /Status: `implemented_registered_sqx_local_decision`/);
assert.match(doc, /sqx142-portfolio-corr1-registered-decision-v1/);
assert.match(doc, /SQX EDGE CORR1 TAGGED/);
assert.match(doc, /corr1_registered_stability_decision/);
assert.match(doc, /OOS3 must not select alternates/);
assert.match(doc, /White Reality Check/);

console.log('sqx142 portfolio corr1 stability contracts ok');
