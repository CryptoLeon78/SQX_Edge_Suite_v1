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
const doc = readRepo("docs/T10AJF_CLOUDFLARE_SHELL_CREATION_DECISION.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenExternalFragments = [
  "wrangler deploy",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
  "versions upload",
];
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");

const proof = Object.freeze({
  phase: "T10ajf",
  result: "NO_GO_NO_INVISIBLE_CLOUDFLARE_SHELL_PATH_ACCEPTED",
  provider: "Cloudflare",
  requestedProjectShellName: "sqx-edge-tester-portal-preview",
  providerShellExistsFromT10aje: false,
  noDeployShellPathAccepted: false,
  firstUploadRequiresWranglerDeploy: true,
  versionsUploadCreatesProviderArtifact: true,
  versionsUploadCannotCreateFirstWorker: true,
  versionsUploadCanReturnPreviewUrl: true,
  deployCreatesTrafficDeployment: true,
  t10akUnlocked: false,
  nextActionRequiresExactApproval: true,
  candidateNextGate: "T10ajg_first_worker_deploy_approval_gate",
  packageScriptReady:
    scripts["proof:cloudflare-shell-creation-decision"] === "node scripts/cloudflare-shell-creation-decision-proof.mjs",
  deployOrUploadScriptPublished: Object.entries(scripts).some(([scriptName, script]) => {
    if (scriptName === "proof:cloudflare-shell-creation-decision") {
      return false;
    }
    return forbiddenExternalFragments.some((fragment) => String(script).includes(fragment));
  }),
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  docReady:
    doc.includes("NO_GO_NO_INVISIBLE_CLOUDFLARE_SHELL_PATH_ACCEPTED") &&
    doc.includes("using `wrangler versions upload` for the first upload will fail") &&
    doc.includes("npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview"),
  governanceUpdated: governance.includes("T10ajf - Cloudflare Shell Creation Decision"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajg: prepare exact approval gate for the first Cloudflare Worker deploy/shell creation"),
  cloudflareProjectCreated: false,
  cloudflareVersionUploaded: false,
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
  nextGate: "T10ajg_first_worker_deploy_approval_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.packageScriptReady ||
  proof.deployOrUploadScriptPublished ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
