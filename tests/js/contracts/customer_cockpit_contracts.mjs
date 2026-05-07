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
assert.equal(productManifest.upgrade.checkout.status, 'limited_publication_draft_ready');
assert.equal(productManifest.upgrade.checkout.automation.status, 'limited_publication_draft_ready');
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
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_sales_register'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_sales_register.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_feedback_cohort'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_feedback_cohort.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_1_action_plan'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_1_action_plan.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_2_specs'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_2_specs.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_2_assets'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_2_assets.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_2_offer_pack'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_2_publication'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_2_publication.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/template_pack_2_feedback_cohort'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/template_pack_2_feedback_cohort.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/buyer_ready_checkout_closeout'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/buyer_ready_checkout_closeout.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/public_buyer_page_cadence'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/public_buyer_page_cadence.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/first_controlled_buyer_log'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/first_controlled_buyer_log.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/post_sale_improvement_loop'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/post_sale_improvement_loop.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/post_sale_micro_updates'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/post_sale_micro_updates.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/next_controlled_buyer_readiness'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/next_controlled_buyer_outcome'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/controlled_distribution_step'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/controlled_distribution_step.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/controlled_distribution_review'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/controlled_distribution_review.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/next_buyer_facing_asset'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/next_buyer_facing_asset.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/private_asset_review'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/private_asset_review.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/controlled_publication_gate'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/controlled_publication_gate.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/data/limited_publication_draft'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('backend/sqx-edge-tool/tools/limited_publication_draft.py'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('resources/pro-template-pack-1'));
assert.ok(productManifest.security.sensitiveFilesExcludedFromPortable.includes('resources/pro-template-pack-2'));

console.log('customer cockpit contracts ok');
