import assert from 'node:assert/strict';
import fs from 'node:fs';

const tool = fs.readFileSync('backend/sqx-edge-tool/tools/sqx142_mining_registry.py', 'utf8');
const wrapper = fs.readFileSync('tools/sqx142_mining_registry.ps1', 'utf8');
const server = fs.readFileSync('backend/sqx-edge-tool/api/server.py', 'utf8');
const edgeFactory = fs.readFileSync('app/js/modules/edge-factory.js', 'utf8');
const edgeFactoryUi = fs.readFileSync('app/js/modules/edge-factory-ui.js', 'utf8');
const dashboard = fs.readFileSync('app/SQX_Dashboard_v6.html', 'utf8');
const css = fs.readFileSync('app/css/dashboard.css', 'utf8');

assert.match(tool, /CREATE TABLE IF NOT EXISTS custom_projects/);
assert.match(tool, /CREATE TABLE IF NOT EXISTS databank_snapshots/);
assert.match(tool, /CREATE TABLE IF NOT EXISTS test_results/);
assert.match(tool, /scan-project/);
assert.match(tool, /sqx_user_projects_databank_folder/);
assert.match(tool, /read_only_sqx_project/);
assert.doesNotMatch(tool, /Start-Process|Stop-Process|Remove-Item|run_project|checkResources/);

assert.match(wrapper, /scan-project/);
assert.match(wrapper, /ProjectDir/);
assert.doesNotMatch(wrapper, /Start-Process|Stop-Process|Remove-Item/);

assert.match(server, /\/api\/sqx142\/mining-registry\/funnel/);
assert.match(server, /\/api\/sqx142\/mining-registry\/scan-project/);
assert.match(server, /build_sqx142_mining_registry_funnel/);
assert.match(server, /scan_sqx142_mining_registry_project/);
assert.match(server, /SQX142_DEFAULT_ROOT \/ "user" \/ "projects"/);

assert.match(edgeFactory, /recordMiningRegistryFunnel/);
assert.match(edgeFactory, /edge-factory-mining-registry-funnel/);

assert.match(edgeFactoryUi, /REGISTRY_DATABANK_ORDER/);
assert.match(edgeFactoryUi, /fetchRegistryFunnel/);
assert.match(edgeFactoryUi, /scanRegistryProject/);
assert.match(edgeFactoryUi, /applyRegistryProject/);
assert.match(edgeFactoryUi, /\/sqx142\/mining-registry\/scan-project/);

assert.match(dashboard, /edge-mining-registry-panel/);
assert.match(dashboard, /ps-registry-card/);
assert.match(dashboard, /Actualizar desde SQX local/);
assert.match(css, /edge-registry-funnel/);

console.log('sqx142 mining registry contracts ok');
