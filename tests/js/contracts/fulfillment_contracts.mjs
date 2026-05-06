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
assert.equal(productManifest.upgrade.checkout.status, 'limited_public_launch_ready');
assert.ok(productManifest.upgrade.checkout.liveReadinessTool.includes('checkout_live_readiness.py'));
assert.ok(productManifest.upgrade.checkout.liveReadinessEvidenceDir.includes('checkout_live_readiness'));
assert.ok(productManifest.upgrade.checkout.commercialReleaseCandidateTool.includes('commercial_release_candidate.py'));
assert.ok(productManifest.upgrade.checkout.commercialReleaseCandidateEvidenceDir.includes('commercial_release_candidate'));
assert.ok(productManifest.upgrade.checkout.pilotPurchaseKitTool.includes('pilot_purchase_kit.py'));
assert.ok(productManifest.upgrade.checkout.pilotPurchaseKitEvidenceDir.includes('pilot_purchase_kit'));
assert.ok(productManifest.upgrade.checkout.limitedPublicLaunchTool.includes('limited_public_launch.py'));
assert.ok(productManifest.upgrade.checkout.limitedPublicLaunchEvidenceDir.includes('limited_public_launch'));
assert.equal(productManifest.upgrade.checkout.limitedPublicLaunchPolicy, 'soft_launch_first_5_sales_then_review');
assert.equal(productManifest.upgrade.checkout.rollbackPolicy, 'disable_checkout_pause_webhook_pause_worker_manual_fulfillment');
assert.equal(productManifest.upgrade.checkout.automation.status, 'limited_public_launch_ready');
assert.equal(productManifest.upgrade.checkout.automation.relayIngestEndpoint, '/api/fulfillment/relay-ingest');
assert.equal(productManifest.upgrade.checkout.automation.requestStatusEndpoint, '/api/fulfillment/request-status');
assert.equal(productManifest.upgrade.checkout.automation.retryMode, 'manual_retry_with_attempt_log');
assert.equal(productManifest.upgrade.checkout.automation.relayMode, 'trusted_remote_relay_signed_bundle');
assert.equal(productManifest.upgrade.checkout.automation.relayDispatchEndpoint, '/relay/dispatch');
assert.equal(productManifest.upgrade.checkout.automation.relayConfigCheckEndpoint, '/relay/config-check');
assert.equal(productManifest.upgrade.checkout.automation.relayObservabilityEndpoint, '/relay/observability');
assert.equal(productManifest.upgrade.checkout.automation.relaySnapshotEndpoint, '/relay/observability/snapshot');
assert.equal(productManifest.upgrade.checkout.automation.relayOperatorTokenEnv, 'SQX_RELAY_OPERATOR_TOKEN');
assert.ok(productManifest.upgrade.checkout.automation.relayWorkerScript.includes('dispatch_worker.py'));
assert.ok(productManifest.upgrade.checkout.automation.relaySimulationTool.includes('simulate_purchase_flow.py'));
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
assert.ok(productManifest.upgrade.checkout.automation.relayRenderPreflightEvidenceDir.includes('render_preflight_evidence'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingGateEvidenceDir.includes('render_staging_gate'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingApplyGateEvidenceDir.includes('render_staging_apply_gate'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingPurchaseDrillEvidenceDir.includes('render_staging_purchase_drill'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingLaunchPackEvidenceDir.includes('render_staging_launch_pack'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingSecretsKitEvidenceDir.includes('render_staging_secrets_kit'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestTunnelCheckEvidenceDir.includes('local_ingest_tunnel_check'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestTunnelLaunchEvidenceDir.includes('local_ingest_tunnel_launch'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestStagingSessionEvidenceDir.includes('local_ingest_staging_session'));
assert.ok(productManifest.upgrade.checkout.automation.relayLocalIngestRenderHandoffEvidenceDir.includes('local_ingest_render_handoff'));
assert.ok(productManifest.upgrade.checkout.automation.relayStagingEnvExample.includes('.env.staging.example'));
assert.equal(productManifest.upgrade.checkout.automation.relayRecommendedStagingProvider, 'render');
assert.ok(productManifest.upgrade.checkout.automation.relayDockerfile.includes('Dockerfile'));
assert.ok(productManifest.upgrade.checkout.automation.relayDeploymentTargets.includes('docker'));
assert.ok(productManifest.upgrade.checkout.automation.relayRenderStagingBlueprint.includes('render.staging.yaml.example'));
assert.ok(productManifest.upgrade.checkout.automation.relayStagingChecks.includes('/relay/webhook/lemon'));
assert.ok(productManifest.upgrade.checkout.automation.relayStagingChecks.includes('render_blueprint_validation'));
assert.ok(productManifest.upgrade.checkout.automation.relayRequiredProductionSecrets.includes('SQX_RELAY_OPERATOR_TOKEN'));
assert.ok(productManifest.upgrade.checkout.automation.requestStatuses.includes('failed'));
assert.ok(productManifest.upgrade.checkout.automation.operatorPanelEnabled);

console.log('fulfillment contracts ok');
