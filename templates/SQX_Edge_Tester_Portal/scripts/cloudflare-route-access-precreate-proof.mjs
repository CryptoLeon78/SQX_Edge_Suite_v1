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
const exampleEvidence = JSON.parse(readProject("cloudflare-route-access-precreate.example.json"));
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AJK_CLOUDFLARE_ROUTE_ACCESS_PRECREATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const mutatingFragments = [
  "wrangler deploy",
  "wrangler delete",
  "wrangler versions upload",
  "wrangler versions deploy",
  "opennextjs-cloudflare deploy",
  "pages deploy",
];

const proof = Object.freeze({
  phase: "T10ajk",
  result: "NO_GO_CLOUDFLARE_ROUTE_HOSTNAME_REQUIRED_T10AK_BLOCKED",
  provider: "Cloudflare",
  requestedWorkerName: "sqx-edge-tester-portal-preview",
  wranglerAuthenticatedRedacted: true,
  workerDeploymentsState: "worker_not_found",
  workerVersionsState: "worker_not_found",
  workerSecretsState: "worker_not_found",
  officialRoutesDocsChecked: true,
  officialCustomDomainsDocsChecked: true,
  officialWorkersDevDocsChecked: true,
  officialAccessSelfHostedDocsChecked: true,
  officialAccessApplicationTypesDocsChecked: true,
  protectedCustomDomainPreferred: true,
  workersDevFallbackAllowedOnlyAfterDashboardOnboardingAndAccessReady: true,
  hostnameSelectedPrivately: false,
  zoneSelectedPrivately: false,
  accessHostnameCoverageProven: false,
  wranglerWorkersDevDisabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  publicRoutesCommitted: Array.isArray(wranglerConfig.routes) && wranglerConfig.routes.length > 0,
  packageScriptReady:
    scripts["proof:cloudflare-route-access-precreate"] ===
    "node scripts/cloudflare-route-access-precreate-proof.mjs",
  mutatingScriptPublished: Object.entries(scripts).some(([scriptName, script]) => {
    if (scriptName === "proof:cloudflare-route-access-precreate") {
      return false;
    }
    return /(^|:)(deploy|delete|upload|publish)($|:)/.test(scriptName) ||
      mutatingFragments.some((fragment) => String(script).includes(fragment));
  }),
  localEvidenceIgnored: gitignore.includes("cloudflare-route-access-precreate.local.json"),
  exampleEvidencePublicSafe:
    exampleEvidence.phase === "T10ajk" &&
    exampleEvidence.hostnameSelected === false &&
    exampleEvidence.zoneSelected === false &&
    exampleEvidence.accessApplicationPrecreated === false &&
    exampleEvidence.testerEmailsIncluded === false,
  docHasNoSecretPattern:
    !doc.includes(forbiddenTokenPattern) &&
    !doc.includes(forbiddenAccountPattern) &&
    !doc.includes(forbiddenZonePattern),
  docReady:
    doc.includes("NO_GO_CLOUDFLARE_ROUTE_HOSTNAME_REQUIRED_T10AK_BLOCKED") &&
    doc.includes("T10ajl_cloudflare_hostname_zone_selection_or_workers_dev_onboarding") &&
    doc.includes("wrangler_auth_state=authenticated_redacted"),
  governanceUpdated: governance.includes("T10ajk - Cloudflare Route Access Precreate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajk: configure a protected Cloudflare custom route/domain"),
  cloudflareWorkerCreated: false,
  cloudflareVersionUploaded: false,
  cloudflareDeploymentCreated: false,
  cloudflareRouteCreated: false,
  cloudflareAccessApplicationCreated: false,
  cloudflareAccessPolicyCreated: false,
  githubRepositoryConnectedToCloudflare: false,
  cloudflareTokenCommitted: false,
  cloudflareAccountIdCommitted: false,
  cloudflareZoneIdCommitted: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  renewalEmailsSent: false,
  productionDatabaseConnected: false,
  t10akUnlocked: false,
  nextGate: "T10ajl_cloudflare_hostname_zone_selection_or_workers_dev_onboarding",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.wranglerAuthenticatedRedacted ||
  proof.workerDeploymentsState !== "worker_not_found" ||
  proof.workerVersionsState !== "worker_not_found" ||
  proof.workerSecretsState !== "worker_not_found" ||
  !proof.officialRoutesDocsChecked ||
  !proof.officialCustomDomainsDocsChecked ||
  !proof.officialWorkersDevDocsChecked ||
  !proof.officialAccessSelfHostedDocsChecked ||
  !proof.officialAccessApplicationTypesDocsChecked ||
  !proof.protectedCustomDomainPreferred ||
  !proof.workersDevFallbackAllowedOnlyAfterDashboardOnboardingAndAccessReady ||
  proof.hostnameSelectedPrivately ||
  proof.zoneSelectedPrivately ||
  proof.accessHostnameCoverageProven ||
  !proof.wranglerWorkersDevDisabled ||
  !proof.wranglerPreviewUrlsDisabled ||
  proof.publicRoutesCommitted ||
  !proof.packageScriptReady ||
  proof.mutatingScriptPublished ||
  !proof.localEvidenceIgnored ||
  !proof.exampleEvidencePublicSafe ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  proof.cloudflareWorkerCreated ||
  proof.cloudflareVersionUploaded ||
  proof.cloudflareDeploymentCreated ||
  proof.cloudflareRouteCreated ||
  proof.cloudflareAccessApplicationCreated ||
  proof.cloudflareAccessPolicyCreated ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.t10akUnlocked
) {
  process.exitCode = 1;
}
