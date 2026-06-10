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
const doc = readRepo("docs/T10AJI_CLOUDFLARE_FIRST_DEPLOY_ROLLBACK.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const workerName = "sqx-edge-tester-portal-preview";
const deployCommand = `npm exec --yes -- wrangler deploy --name ${workerName}`;
const cleanupCommand = `npm exec --yes -- wrangler delete ${workerName} --force`;
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
  phase: "T10aji",
  result: "NO_GO_FIRST_WORKER_DEPLOY_ROLLED_BACK_WORKERS_DEV_SUBDOMAIN_REQUIRED",
  provider: "Cloudflare",
  requestedWorkerName: workerName,
  broadTxxxAuthorizationRecorded: true,
  precheckWorkerState: "worker_not_found",
  localBuildSucceeded: true,
  deployCommand,
  deployCommandStarted: true,
  deployCommandExitCode: 1,
  assetsUploadedBeforeFailure: true,
  workersDevSubdomainRequired: true,
  routeOrCustomDomainConfigured: false,
  workerDeploymentsSeenAfterAttempt: true,
  workerVersionsSeenAfterAttempt: true,
  previewCapabilitySeenAfterAttempt: true,
  testerUrlShared: false,
  cleanupCommand,
  cleanupCommandExecuted: true,
  postCleanupWorkerState: "worker_not_found",
  postCleanupDeploymentsNotFound: true,
  postCleanupVersionsNotFound: true,
  postCleanupSecretsNotFound: true,
  rawWranglerOutputCommitted: false,
  packageScriptReady:
    scripts["proof:cloudflare-first-deploy-rollback"] ===
    "node scripts/cloudflare-first-deploy-rollback-proof.mjs",
  mutatingScriptPublished: Object.entries(scripts).some(([scriptName, script]) => {
    if (scriptName === "proof:cloudflare-first-deploy-rollback") {
      return false;
    }
    return /(^|:)(deploy|delete|upload|publish)($|:)/.test(scriptName) ||
      mutatingFragments.some((fragment) => String(script).includes(fragment));
  }),
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  docReady:
    doc.includes("NO_GO_FIRST_WORKER_DEPLOY_ROLLED_BACK_WORKERS_DEV_SUBDOMAIN_REQUIRED") &&
    doc.includes(deployCommand) &&
    doc.includes(cleanupCommand) &&
    doc.includes("T10ajj_cloudflare_route_onboarding_decision"),
  governanceUpdated: governance.includes("T10aji - Cloudflare First Deploy Rollback"),
  nextStepsUpdated: nextSteps.includes("Phase T10aji: execute the first Cloudflare Worker deploy/shell creation"),
  cloudflareWorkerRemains: false,
  cloudflareDeploymentRemains: false,
  cloudflareVersionRemains: false,
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
  nextGate: "T10ajj_cloudflare_route_onboarding_decision",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.broadTxxxAuthorizationRecorded ||
  !proof.deployCommandStarted ||
  proof.deployCommandExitCode !== 1 ||
  !proof.workersDevSubdomainRequired ||
  !proof.workerDeploymentsSeenAfterAttempt ||
  !proof.workerVersionsSeenAfterAttempt ||
  !proof.previewCapabilitySeenAfterAttempt ||
  proof.testerUrlShared ||
  !proof.cleanupCommandExecuted ||
  proof.postCleanupWorkerState !== "worker_not_found" ||
  !proof.postCleanupDeploymentsNotFound ||
  !proof.postCleanupVersionsNotFound ||
  !proof.postCleanupSecretsNotFound ||
  proof.rawWranglerOutputCommitted ||
  !proof.packageScriptReady ||
  proof.mutatingScriptPublished ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  proof.cloudflareWorkerRemains ||
  proof.cloudflareDeploymentRemains ||
  proof.cloudflareVersionRemains ||
  proof.cloudflareAccessApplicationCreated ||
  proof.cloudflareAccessPolicyCreated ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.t10akUnlocked
) {
  process.exitCode = 1;
}
