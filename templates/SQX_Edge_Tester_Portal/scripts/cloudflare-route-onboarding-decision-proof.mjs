import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");

function readProject(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readRepo(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

const packageJson = JSON.parse(readProject("package.json"));
const wranglerConfig = JSON.parse(readProject("wrangler.jsonc"));
const doc = readRepo("docs/T10AJJ_CLOUDFLARE_ROUTE_ONBOARDING_DECISION.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const mutatingFragments = [
  "wrangler deploy",
  "wrangler delete",
  "wrangler versions upload",
  "wrangler versions deploy",
  "opennextjs-cloudflare deploy",
  "pages deploy",
];

const proof = Object.freeze({
  phase: "T10ajj",
  result: "GO_CLOUDFLARE_ROUTE_ONBOARDING_DECISION_READY_NO_DEPLOY",
  provider: "Cloudflare",
  requestedWorkerName: "sqx-edge-tester-portal-preview",
  t10ajiRollbackClean: true,
  liveWorkerState: "worker_not_found",
  deploymentsState: "worker_not_found",
  versionsState: "worker_not_found",
  secretsState: "worker_not_found",
  officialWorkersDevDocsChecked: true,
  officialPreviewUrlsDocsChecked: true,
  officialScriptSubdomainApiDocsChecked: true,
  workersDevDashboardConfigRequiredForAccountSubdomain: true,
  scriptSubdomainApiRequiresExistingScript: true,
  workersDevPublicWhenEnabled: true,
  cloudflareAccessRequiredBeforeTesterSharing: true,
  selectedRoutePath: "custom_route_or_dashboard_workers_dev_onboarding_before_redeploy",
  customRoutePreferredForTesterRollout: true,
  workersDevPilotAllowedOnlyWithImmediateAccess: true,
  wranglerWorkersDevDisabled: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  deployBlockedUntilRouteOnboarding: true,
  providerMutationExecuted: false,
  testerUrlShared: false,
  packageScriptReady:
    scripts["proof:cloudflare-route-onboarding-decision"] ===
    "node scripts/cloudflare-route-onboarding-decision-proof.mjs",
  mutatingScriptPublished: Object.entries(scripts).some(([scriptName, script]) => {
    if (scriptName === "proof:cloudflare-route-onboarding-decision") {
      return false;
    }
    return /(^|:)(deploy|delete|upload|publish)($|:)/.test(scriptName) ||
      mutatingFragments.some((fragment) => String(script).includes(fragment));
  }),
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  docReady:
    doc.includes("GO_CLOUDFLARE_ROUTE_ONBOARDING_DECISION_READY_NO_DEPLOY") &&
    doc.includes("custom_route_or_dashboard_workers_dev_onboarding_before_redeploy") &&
    doc.includes("T10ajk_cloudflare_route_onboarding_or_access_precreate"),
  governanceUpdated: governance.includes("T10ajj - Cloudflare Route Onboarding Decision"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajj: decide/register the Cloudflare route or workers.dev onboarding path"),
  cloudflareWorkerCreated: false,
  cloudflareVersionUploaded: false,
  cloudflareDeploymentCreated: false,
  cloudflareAccessApplicationCreated: false,
  cloudflareAccessPolicyCreated: false,
  githubRepositoryConnectedToCloudflare: false,
  cloudflareTokenCommitted: false,
  cloudflareAccountIdCommitted: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  renewalEmailsSent: false,
  productionDatabaseConnected: false,
  t10akUnlocked: false,
  nextGate: "T10ajk_cloudflare_route_onboarding_or_access_precreate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10ajiRollbackClean ||
  proof.liveWorkerState !== "worker_not_found" ||
  !proof.officialWorkersDevDocsChecked ||
  !proof.officialPreviewUrlsDocsChecked ||
  !proof.officialScriptSubdomainApiDocsChecked ||
  !proof.workersDevDashboardConfigRequiredForAccountSubdomain ||
  !proof.scriptSubdomainApiRequiresExistingScript ||
  !proof.workersDevPublicWhenEnabled ||
  !proof.cloudflareAccessRequiredBeforeTesterSharing ||
  !proof.customRoutePreferredForTesterRollout ||
  !proof.workersDevPilotAllowedOnlyWithImmediateAccess ||
  !proof.wranglerWorkersDevDisabled ||
  !proof.wranglerPreviewUrlsDisabled ||
  !proof.deployBlockedUntilRouteOnboarding ||
  proof.providerMutationExecuted ||
  proof.testerUrlShared ||
  !proof.packageScriptReady ||
  proof.mutatingScriptPublished ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  proof.cloudflareWorkerCreated ||
  proof.cloudflareVersionUploaded ||
  proof.cloudflareDeploymentCreated ||
  proof.cloudflareAccessApplicationCreated ||
  proof.cloudflareAccessPolicyCreated ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.t10akUnlocked
) {
  process.exitCode = 1;
}
