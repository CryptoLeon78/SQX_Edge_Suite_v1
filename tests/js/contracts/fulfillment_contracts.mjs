import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const fulfillmentJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/fulfillment.js'), 'utf8');
const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));

for (const exportName of [
  'fetchQueue',
  'handleAction',
  'loadSettings',
  'processRequest',
  'renderQueue',
  'saveSettings',
  'setStatus',
  'storageKey',
  'updateRequestStatus',
]) {
  assert.ok(fulfillmentJs.includes(exportName), `missing fulfillment export ${exportName}`);
}

assert.ok(fulfillmentJs.includes("SQX.registerModule('fulfillment'"));
assert.ok(html.includes('id="fulfillment-panel"'));
assert.ok(html.includes('id="fulfillment-request-list"'));
assert.ok(html.includes('js/modules/fulfillment.js'));
assert.equal(productManifest.upgrade.checkout.automation.status, 'remote_relay_ready');
assert.equal(productManifest.upgrade.checkout.automation.relayIngestEndpoint, '/api/fulfillment/relay-ingest');
assert.equal(productManifest.upgrade.checkout.automation.requestStatusEndpoint, '/api/fulfillment/request-status');
assert.equal(productManifest.upgrade.checkout.automation.retryMode, 'manual_retry_with_attempt_log');
assert.equal(productManifest.upgrade.checkout.automation.relayMode, 'trusted_remote_relay_signed_bundle');
assert.equal(productManifest.upgrade.checkout.automation.relayDispatchEndpoint, '/relay/dispatch');
assert.ok(productManifest.upgrade.checkout.automation.requestStatuses.includes('failed'));
assert.ok(productManifest.upgrade.checkout.automation.operatorPanelEnabled);

console.log('fulfillment contracts ok');
