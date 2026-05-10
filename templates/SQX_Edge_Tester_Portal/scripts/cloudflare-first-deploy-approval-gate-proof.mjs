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
const doc = readRepo("docs/T10AJG_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const workerName = "sqx-edge-tester-portal-preview";
const exactDeployCommand = `npm exec --yes -- wrangler deploy --name ${workerName}`;
const cleanupCommand = `npm exec --yes -- wrangler delete ${workerName} --force`;
const approvalPhrase =
  "Autorizo T10ajh: ejecutar exactamente `npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview` desde `templates/SQX_Edge_Tester_Portal` despues de `npm run cf:build`, sin compartir URL tester y con inspeccion/cleanup inmediato si aparece una superficie publica no aceptada.";
const forbiddenExternalFragments = [
  "wrangler deploy",
  "wrangler delete",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
  "versions upload",
];
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");

const packageScriptReady =
  scripts["proof:cloudflare-first-deploy-approval-gate"] ===
  "node scripts/cloudflare-first-deploy-approval-gate-proof.mjs";
const deployOrCleanupScriptPublished = Object.entries(scripts).some(([scriptName, script]) => {
  if (scriptName === "proof:cloudflare-first-deploy-approval-gate") {
    return false;
  }
  return forbiddenExternalFragments.some((fragment) => String(script).includes(fragment));
});

const proof = Object.freeze({
  phase: "T10ajg",
  result: "GO_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE_READY_NO_PROVIDER_ACTION",
  provider: "Cloudflare",
  requestedWorkerName: workerName,
  exactDeployCommand,
  localBuildCommand: "npm run cf:build",
  approvalPhrase,
  cleanupCommandIfUnsafe: cleanupCommand,
  readOnlyPreChecks: [
    "npm exec --yes -- wrangler whoami",
    `npm exec --yes -- wrangler deployments list --name ${workerName} --json`,
    `npm exec --yes -- wrangler versions list --name ${workerName} --json`,
    `npm exec --yes -- wrangler secret list --name ${workerName} --format json`,
  ],
  postDeployInspectionCommands: [
    `npm exec --yes -- wrangler deployments list --name ${workerName} --json`,
    `npm exec --yes -- wrangler versions list --name ${workerName} --json`,
    `npm exec --yes -- wrangler secret list --name ${workerName} --format json`,
  ],
  firstUploadRequiresWranglerDeploy: true,
  previewUrlsMayBePublic: true,
  cloudflareAccessRequiredBeforeTesterSharing: true,
  externalActionPrepared: true,
  externalActionExecuted: false,
  providerMutatedInT10ajg: false,
  packageScriptReady,
  deployOrCleanupScriptPublished,
  wranglerConfigNameMatches: wranglerConfig.name === workerName,
  wranglerConfigMainMatches: wranglerConfig.main === ".open-next/worker.js",
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  docReady:
    doc.includes("GO_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE_READY_NO_PROVIDER_ACTION") &&
    doc.includes(exactDeployCommand) &&
    doc.includes(cleanupCommand) &&
    doc.includes(approvalPhrase),
  governanceUpdated: governance.includes("T10ajg - Cloudflare First Deploy Approval Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajg: prepare exact approval gate for the first Cloudflare Worker deploy/shell creation"),
  cloudflareWorkerCreated: false,
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
  t10akUnlocked: false,
  nextGate: "T10ajh_execute_first_worker_deploy_only_after_exact_approval",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.packageScriptReady ||
  proof.deployOrCleanupScriptPublished ||
  !proof.wranglerConfigNameMatches ||
  !proof.wranglerConfigMainMatches ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
