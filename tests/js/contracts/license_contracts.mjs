import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const licenseJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/license.js'), 'utf8');
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));
const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');

for (const exportName of [
  'currentStatus',
  'fetchJson',
  'hasFeature',
  'importLicenseText',
  'renderPanel',
  'refreshBackendStatus',
  'storageKey',
  'checkoutMeta',
]) {
  assert.ok(licenseJs.includes(exportName), `missing license export ${exportName}`);
}

assert.ok(licenseJs.includes("SQX.registerModule('license'"));
assert.equal(productManifest.build.channel, 'internal');
assert.equal(productManifest.licensing.signatureMode, 'rsa_sha256_pkcs1_v1_5');
assert.equal(productManifest.licensing.signatureAlgorithm, 'RS256');
assert.ok(productManifest.licensing.publicKey.n.length > 100);
assert.equal(productManifest.upgrade.headline, 'SQX Edge Pro');
assert.equal(productManifest.upgrade.checkout.primaryProvider, 'Lemon Squeezy');
assert.equal(productManifest.upgrade.checkout.fallbackProvider, 'Gumroad');
assert.equal(productManifest.upgrade.checkout.fulfillmentMode, 'manual_signed_license');
assert.ok(productManifest.upgrade.checkout.deliveryTool.includes('prepare_customer_delivery.ps1'));
assert.equal(productManifest.upgrade.checkout.status, 'template_pack_1_public_offer_ready');
assert.ok(productManifest.upgrade.checkout.liveReadinessTool.includes('checkout_live_readiness.py'));
assert.ok(productManifest.upgrade.checkout.liveReadinessEvidenceDir.includes('checkout_live_readiness'));
assert.ok(productManifest.upgrade.checkout.commercialReleaseCandidateTool.includes('commercial_release_candidate.py'));
assert.ok(productManifest.upgrade.checkout.commercialReleaseCandidateEvidenceDir.includes('commercial_release_candidate'));
assert.ok(productManifest.upgrade.checkout.pilotPurchaseKitTool.includes('pilot_purchase_kit.py'));
assert.ok(productManifest.upgrade.checkout.pilotPurchaseKitEvidenceDir.includes('pilot_purchase_kit'));
assert.ok(productManifest.upgrade.checkout.limitedPublicLaunchTool.includes('limited_public_launch.py'));
assert.ok(productManifest.upgrade.checkout.limitedPublicLaunchEvidenceDir.includes('limited_public_launch'));
assert.equal(productManifest.upgrade.checkout.limitedPublicLaunchPolicy, 'soft_launch_first_5_sales_then_review');
assert.ok(productManifest.upgrade.checkout.postLaunchControlTool.includes('post_launch_control.py'));
assert.ok(productManifest.upgrade.checkout.postLaunchControlEvidenceDir.includes('post_launch_control'));
assert.equal(productManifest.upgrade.checkout.postLaunchControlPolicy, 'review_first_sales_before_scaling');
assert.ok(productManifest.upgrade.checkout.commercialFeedbackLoopTool.includes('commercial_feedback_loop.py'));
assert.ok(productManifest.upgrade.checkout.commercialFeedbackLoopEvidenceDir.includes('commercial_feedback_loop'));
assert.equal(productManifest.upgrade.checkout.commercialFeedbackLoopPolicy, 'classify_feedback_before_offer_changes');
assert.ok(productManifest.upgrade.checkout.publicOfferPackTool.includes('public_offer_pack.py'));
assert.ok(productManifest.upgrade.checkout.publicOfferPackEvidenceDir.includes('public_offer_pack'));
assert.equal(productManifest.upgrade.checkout.publicOfferPackPolicy, 'review_copy_faq_release_notes_before_public_page');
assert.ok(productManifest.upgrade.checkout.launchAssetsKitTool.includes('launch_assets_kit.py'));
assert.ok(productManifest.upgrade.checkout.launchAssetsKitEvidenceDir.includes('launch_assets_kit'));
assert.equal(productManifest.upgrade.checkout.launchAssetsKitPolicy, 'prepare_assets_release_draft_and_publication_checklist');
assert.ok(productManifest.upgrade.checkout.publicReleaseGateTool.includes('public_release_gate.py'));
assert.ok(productManifest.upgrade.checkout.publicReleaseGateEvidenceDir.includes('public_release_gate'));
assert.equal(productManifest.upgrade.checkout.publicReleaseGatePolicy, 'confirm_tag_release_zip_checksum_support_and_rollback');
assert.ok(productManifest.upgrade.checkout.releasePublicationRecordTool.includes('release_publication_record.py'));
assert.ok(productManifest.upgrade.checkout.releasePublicationRecordEvidenceDir.includes('release_publication_record'));
assert.equal(productManifest.upgrade.checkout.releasePublicationRecordPolicy, 'record_tag_release_asset_checksum_support_and_rollback_publication');
assert.ok(productManifest.upgrade.checkout.postReleaseMonitorTool.includes('post_release_monitor.py'));
assert.ok(productManifest.upgrade.checkout.postReleaseMonitorEvidenceDir.includes('post_release_monitor'));
assert.equal(productManifest.upgrade.checkout.postReleaseMonitorPolicy, 'monitor_incidents_activation_support_refunds_and_scale_decision');
assert.ok(productManifest.upgrade.checkout.hotfixRollbackReleaseTool.includes('hotfix_rollback_release.py'));
assert.ok(productManifest.upgrade.checkout.hotfixRollbackReleaseEvidenceDir.includes('hotfix_rollback_release'));
assert.equal(productManifest.upgrade.checkout.hotfixRollbackReleasePolicy, 'prepare_hotfix_or_rollback_release_notes_comms_and_closure_evidence');
assert.ok(productManifest.upgrade.checkout.customerSuccessRenewalTool.includes('customer_success_renewal.py'));
assert.ok(productManifest.upgrade.checkout.customerSuccessRenewalEvidenceDir.includes('customer_success_renewal'));
assert.equal(productManifest.upgrade.checkout.customerSuccessRenewalPolicy, 'track_onboarding_activation_support_renewal_and_safe_expansion');
assert.equal(productManifest.upgrade.checkout.customerCockpitEndpoint, '/api/customer-cockpit');
assert.equal(productManifest.upgrade.checkout.customerCockpitConfig, 'backend/sqx-edge-tool/config/customer_cockpit.json');
assert.equal(productManifest.upgrade.checkout.customerCockpitPolicy, 'render_redacted_operator_summary_without_license_payloads_or_raw_events');
assert.equal(productManifest.upgrade.checkout.proBuyerPackConfig, 'backend/sqx-edge-tool/config/pro_buyer_pack.json');
assert.equal(productManifest.upgrade.checkout.proBuyerPackResourceDir, 'resources/pro-buyer-pack');
assert.ok(productManifest.upgrade.checkout.proBuyerPackValidationTool.includes('pro_buyer_pack.py'));
assert.equal(productManifest.upgrade.checkout.proBuyerPackPolicy, 'ship_safe_buyer_material_without_license_payloads_private_keys_or_financial_promises');
assert.equal(productManifest.upgrade.checkout.buyerOnboardingSupportGateConfig, 'backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json');
assert.equal(productManifest.upgrade.checkout.buyerOnboardingResourceDir, 'resources/pro-buyer-pack/onboarding');
assert.ok(productManifest.upgrade.checkout.buyerOnboardingSupportGateTool.includes('buyer_onboarding_support_gate.py'));
assert.ok(productManifest.upgrade.checkout.buyerOnboardingSupportGateEvidenceDir.includes('buyer_onboarding_support_gate'));
assert.equal(productManifest.upgrade.checkout.buyerOnboardingSupportGatePolicy, 'confirm_purchase_zip_license_start_here_faq_support_and_safe_claims_before_handoff');
assert.equal(productManifest.upgrade.checkout.templatePack1Config, 'backend/sqx-edge-tool/config/template_pack_1.json');
assert.equal(productManifest.upgrade.checkout.templatePack1ResourceDir, 'resources/pro-template-pack-1');
assert.ok(productManifest.upgrade.checkout.templatePack1DeliveryTool.includes('template_pack_1_delivery.py'));
assert.ok(productManifest.upgrade.checkout.templatePack1EvidenceDir.includes('template_pack_1_delivery'));
assert.equal(productManifest.upgrade.checkout.templatePack1Policy, 'deliver_as_separate_addon_zip_after_buyer_onboarding_gate_and_safe_claims_review');
assert.equal(productManifest.upgrade.checkout.templatePack1OfferConfig, 'backend/sqx-edge-tool/config/template_pack_1_offer.json');
assert.equal(productManifest.upgrade.checkout.templatePack1OfferResourceDir, 'resources/pro-template-pack-1/offer');
assert.ok(productManifest.upgrade.checkout.templatePack1OfferTool.includes('template_pack_1_offer.py'));
assert.ok(productManifest.upgrade.checkout.templatePack1OfferEvidenceDir.includes('template_pack_1_offer'));
assert.equal(productManifest.upgrade.checkout.templatePack1OfferPolicy, 'prepare_public_addon_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout');
assert.equal(productManifest.upgrade.checkout.rollbackPolicy, 'disable_checkout_pause_webhook_pause_worker_manual_fulfillment');
assert.equal(productManifest.upgrade.checkout.automation.status, 'template_pack_1_public_offer_ready');
assert.equal(productManifest.upgrade.checkout.automation.webhookSignatureHeader, 'X-Signature');
assert.equal(productManifest.upgrade.checkout.automation.webhookSecretEnv, 'SQX_LEMON_WEBHOOK_SECRET');
assert.equal(productManifest.upgrade.checkout.automation.receiverEndpoint, '/api/fulfillment/webhook/lemon');
assert.equal(productManifest.upgrade.checkout.automation.relayIngestEndpoint, '/api/fulfillment/relay-ingest');
assert.equal(productManifest.upgrade.checkout.automation.relaySecretEnv, 'SQX_FULFILLMENT_RELAY_SECRET');
assert.equal(productManifest.upgrade.checkout.automation.relayServiceProject, 'backend/sqx-edge-relay');
assert.equal(productManifest.upgrade.checkout.automation.relayConfigCheckEndpoint, '/relay/config-check');
assert.equal(productManifest.upgrade.checkout.automation.relayObservabilityEndpoint, '/relay/observability');
assert.equal(productManifest.upgrade.checkout.automation.relayOperatorTokenEnv, 'SQX_RELAY_OPERATOR_TOKEN');
assert.ok(productManifest.upgrade.checkout.automation.relayDeploymentCheckTool.includes('deployment_check.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayStagingSmokeTool.includes('staging_smoke.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayStagingEvidenceTool.includes('staging_evidence.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderApiPreflightTool.includes('render_api_preflight.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderCredentialsHandshakeTool.includes('render_credentials_handshake.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingGateTool.includes('render_staging_gate.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingApplyGateTool.includes('render_staging_apply_gate.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingPurchaseDrillTool.includes('render_staging_purchase_drill.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingLaunchPackTool.includes('render_staging_launch_pack.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingSecretsKitTool.includes('render_staging_secrets_kit.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestTunnelCheckTool.includes('local_ingest_tunnel_check.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestTunnelLauncherTool.includes('local_ingest_tunnel_launcher.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestStagingSessionTool.includes('local_ingest_staging_session.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestRenderHandoffTool.includes('local_ingest_render_handoff.py'));
assert.equal(productManifest.upgrade.checkout.automation.relayRenderCredentialPolicy, 'api_key_only_no_account_password');
assert.equal(productManifest.upgrade.checkout.automation.requestStatusEndpoint, '/api/fulfillment/request-status');
assert.ok(productManifest.upgrade.checkout.automation.normalizerTool.includes('fulfillment_request.py'));
assert.ok(productManifest.upgrade.checkout.automation.relayBundleTool.includes('relay_bundle.py'));
assert.ok(productManifest.upgrade.bullets.length >= 3);
assert.ok(JSON.stringify(productManifest.upgrade).includes('24 EUR/mes'));
assert.ok(JSON.stringify(productManifest.upgrade).includes('49 EUR'));
assert.ok(productManifest.marketing.tagline.includes('pipeline operativo'));
assert.ok(productManifest.features['project_generator.generate']);
assert.ok(productManifest.features['strategy_cleaner.apply']);
assert.deepEqual(productManifest.accessLevels.internal.features, ['*']);
assert.ok(html.includes('id="license-panel"'));
assert.ok(html.includes('id="license-checkout-link"'));
assert.ok(html.includes('id="license-upgrade-list"'));
assert.ok(html.includes('id="license-plan-strip"'));
assert.ok(html.includes('js/modules/license.js'));
assert.ok(licenseJs.includes('/license/import'));
assert.ok(licenseJs.includes('/license/clear'));

console.log('license contracts ok');
