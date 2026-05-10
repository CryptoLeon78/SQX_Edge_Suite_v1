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
const doc = readRepo("docs/T10AJE_CLOUDFLARE_READONLY_SHELL_CAPTURE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenDeployFragments = [
  "wrangler deploy",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
];
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");

const proof = Object.freeze({
  phase: "T10aje",
  result: "NO_GO_CLOUDFLARE_WORKER_NOT_FOUND_T10AK_BLOCKED",
  provider: "Cloudflare",
  requestedProjectShellName: "sqx-edge-tester-portal-preview",
  wranglerLoginSucceeded: true,
  wranglerWhoamiAuthenticated: true,
  rawWhoamiOutputCommitted: false,
  deploymentsListResult: "worker_not_found",
  versionsListResult: "worker_not_found",
  secretListResult: "worker_not_found",
  cloudflareErrorCode: 10007,
  providerShellExists: false,
  t10akUnlocked: false,
  packageScriptReady:
    scripts["proof:cloudflare-readonly-shell-capture"] === "node scripts/cloudflare-readonly-shell-capture-proof.mjs",
  deployScriptPublished: Object.keys(scripts).some((scriptName) => /(^|:)deploy($|:)/.test(scriptName)),
  forbiddenDeployFragmentsPresent: Object.values(scripts).some((script) =>
    forbiddenDeployFragments.some((fragment) => String(script).includes(fragment))
  ),
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  docReady: doc.includes("NO_GO_CLOUDFLARE_WORKER_NOT_FOUND_T10AK_BLOCKED"),
  governanceUpdated: governance.includes("T10aje - Cloudflare Read-Only Shell Capture"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajf: choose exact no-deploy Cloudflare shell creation path"),
  cloudflareProjectCreated: false,
  cloudflareDeploymentCreated: false,
  cloudflareAccessApplicationCreated: false,
  cloudflareAccessPolicyCreated: false,
  githubRepositoryConnectedToCloudflare: false,
  cloudflareTokenCommitted: false,
  cloudflareAccountIdCommitted: false,
  testerUrlPublished: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  renewalEmailsSent: false,
  productionDatabaseConnected: false,
  nextGate: "T10ajf_choose_shell_creation_path_or_controlled_deploy_approval",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.packageScriptReady ||
  proof.deployScriptPublished ||
  proof.forbiddenDeployFragmentsPresent ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
