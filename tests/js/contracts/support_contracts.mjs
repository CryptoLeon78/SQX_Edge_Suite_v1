import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const supportJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/support.js'), 'utf8');
const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));

for (const exportName of [
  'diagnosticsFilename',
  'downloadJson',
  'fetchDiagnostics',
  'generateDiagnostics',
  'collectIncidentPayload',
  'submitIncident',
  'setIncidentStatus',
  'setStatus',
]) {
  assert.ok(supportJs.includes(exportName), `${exportName} should be exported by support module`);
}

assert.ok(supportJs.includes("SQX.registerModule('support'"));
assert.ok(supportJs.includes('/support/diagnostics'));
assert.ok(supportJs.includes('/support/incidents'));
assert.ok(html.includes('id="support-panel"'));
assert.ok(html.includes('id="support-diagnostic-btn"'));
assert.ok(html.includes('id="support-incident-submit"'));
assert.ok(html.includes('id="support-incident-summary"'));
assert.ok(html.includes('id="support-incident-include-diagnostic"'));
assert.ok(html.includes('js/modules/support.js'));
assert.equal(productManifest.support.diagnosticsEndpoint, '/api/support/diagnostics');
assert.equal(productManifest.support.incidentEndpoint, '/api/support/incidents');
assert.equal(productManifest.support.incidentSchemaVersion, 'support-incident-v1');
assert.equal(productManifest.support.incidentEvidenceRoot, '.local/remote_service/support_cases');
assert.equal(productManifest.support.safeToSend, true);
assert.ok(productManifest.support.excludedFromDiagnostics.includes('license payload'));

console.log('support contracts ok');
