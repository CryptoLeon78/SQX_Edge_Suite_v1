import assert from 'node:assert/strict';
import fs from 'node:fs';

const tool = fs.readFileSync('backend/sqx-edge-tool/tools/sqx142_portfolio_corr2_local_project_integration.py', 'utf8');
const wrapper = fs.readFileSync('tools/sqx142_portfolio_corr2_local_project_integration.ps1', 'utf8');
const server = fs.readFileSync('backend/sqx-edge-tool/api/server.py', 'utf8');
const edgeFactoryUi = fs.readFileSync('app/js/modules/edge-factory-ui.js', 'utf8');
const html = fs.readFileSync('app/SQX_Dashboard_v6.html', 'utf8');
const css = fs.readFileSync('app/css/dashboard.css', 'utf8');
const doc = fs.readFileSync('docs/SQX142_PORTFOLIO_CORR2_LOCAL_CUSTOM_PROJECT_INTEGRATION.md', 'utf8');

assert.match(tool, /sqx142-capa1-c2-corr2-local-project-integration-v1/);
assert.match(tool, /DEPRECATED_PORTFOLIO_ALIAS_VERSION = "sqx142-portfolio-corr2-local-custom-project-integration-v1"/);
assert.match(tool, /DECISION_DOMAIN = "capa1_c2_template_selection"/);
assert.match(tool, /STABILITY_TASK_XML = "Retest-Task4.xml"/);
assert.match(tool, /TAG_TASK_XML = "Retest-Task5.xml"/);
assert.match(tool, /SOURCE_DATABANK = "Forward"/);
assert.match(tool, /STABILITY_DATABANK = "SQX EDGE CORR1 STABILITY"/);
assert.match(tool, /TAGGED_DATABANK = "SQX EDGE CORR1 TAGGED"/);
assert.match(tool, /REAL_TICK_PRECISION = "4"/);
assert.match(tool, /CustomAnalysis/);
assert.match(tool, /SQXEdgeCorrelationTagger/);
assert.match(tool, /registry_record_corr2/);
assert.match(tool, /record_manual_status/);
assert.match(tool, /add active task/);
assert.match(tool, /"active": "true"/);
assert.doesNotMatch(tool, /add inactive task/);
assert.doesNotMatch(tool, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(wrapper, /Assert-NoSqxProcess/);
assert.match(wrapper, /portfolio_corr2_local_project_integration/);
assert.doesNotMatch(wrapper, /Start-Process|Stop-Process|Remove-Item/);

assert.match(server, /\/api\/sqx142\/capa1-c2-corr2\/local-project/);
assert.match(server, /\/api\/sqx142\/portfolio-corr2\/local-project/);
assert.match(server, /apply_sqx142_portfolio_corr2_integration/);
assert.match(server, /rollback_sqx142_portfolio_corr2_integration/);
assert.match(server, /record_sqx142_portfolio_corr2_status/);

assert.match(edgeFactoryUi, /corr2LocalProject/);
assert.match(edgeFactoryUi, /\/sqx142\/capa1-c2-corr2\/local-project/);
assert.match(edgeFactoryUi, /SQX EDGE CORR1 STABILITY/);
assert.match(edgeFactoryUi, /SQX EDGE CORR1 TAGGED/);
assert.match(edgeFactoryUi, /corr2LocalProject\('record'\)/);

assert.match(html, /edge-corr2-plan/);
assert.match(html, /edge-corr2-record/);
assert.match(html, /edge-corr2-apply/);
assert.match(html, /ps-corr2-plan/);
assert.match(html, /Parchear Capa1 SQX/);
assert.match(html, /Registrar C2 CORR1/);
assert.match(css, /edge-corr2-controls/);

assert.match(doc, /Status: `implemented_capa1_c2_local_project_patch_ready`/);
assert.match(doc, /sqx142-capa1-c2-corr2-local-project-integration-v1/);
assert.match(doc, /Forward`/);
assert.match(doc, /testPrecision=4/);
assert.match(doc, /no jars/);

console.log('sqx142 portfolio corr2 local project integration contracts ok');
