import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const cockpitJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/customer-cockpit.js'), 'utf8');
const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const mainJs = fs.readFileSync(path.join(repoRoot, 'app/js/main.js'), 'utf8');
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));

for (const exportName of [
  'apiBase',
  'endpoint',
  'fetchCockpit',
  'init',
  'renderCockpit',
  'riskClass',
  'riskLabel',
  'setStatus',
]) {
  assert.ok(cockpitJs.includes(exportName), `missing customer cockpit export ${exportName}`);
}

for (const elementId of [
  'customer-cockpit-panel',
  'customer-cockpit-refresh-btn',
  'customer-cockpit-customer-count',
  'customer-cockpit-renewal-count',
  'customer-cockpit-support-count',
  'customer-cockpit-opportunity-count',
  'customer-cockpit-status',
  'customer-cockpit-list',
  'customer-cockpit-empty',
]) {
  assert.ok(html.includes(`id="${elementId}"`), `missing customer cockpit element ${elementId}`);
}

assert.ok(cockpitJs.includes("SQX.registerModule('customer-cockpit'"));
assert.ok(cockpitJs.includes("endpoint('/customer-cockpit')"));
assert.ok(html.includes('js/modules/customer-cockpit.js'));
assert.ok(mainJs.includes('window.SQX.customerCockpit.init()'));
assert.equal(productManifest.upgrade.checkout.status, 'template_pack_1_handoff_ready');
assert.equal(productManifest.upgrade.checkout.automation.status, 'template_pack_1_handoff_ready');
assert.equal(productManifest.upgrade.checkout.customerCockpitEndpoint, '/api/customer-cockpit');
assert.equal(productManifest.upgrade.checkout.customerCockpitConfig, 'backend/sqx-edge-tool/config/customer_cockpit.json');
assert.equal(
  productManifest.upgrade.checkout.customerCockpitPolicy,
  'render_redacted_operator_summary_without_license_payloads_or_raw_events',
);
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/customer_success_renewal'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/customer_cockpit'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/buyer_onboarding_support_gate'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_delivery'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_delivery.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_offer'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_offer.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_publication'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_publication.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_purchase_drill'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_handoff'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_handoff.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('resources/pro-template-pack-1'));

console.log('customer cockpit contracts ok');
