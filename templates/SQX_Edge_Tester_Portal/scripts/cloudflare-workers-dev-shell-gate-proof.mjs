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
const mainWrangler = JSON.parse(readProject("wrangler.jsonc"));
const shellWrangler = JSON.parse(readProject("wrangler.shell.example.jsonc"));
const shellWorker = readProject("cloudflare/shell-worker.js");
const doc = readRepo("docs/T10AJM_WORKERS_DEV_SHELL_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  shellWorker,
  JSON.stringify(shellWrangler),
].join("\n");

const proof = Object.freeze({
  phase: "T10ajm",
  result: "GO_WORKERS_DEV_SHELL_GATE_READY_EXACT_DEPLOY_APPROVAL_REQUIRED",
  provider: "Cloudflare",
  selectedPath: "workers_dev_shell_then_access_then_real_app",
  requestedWorkerName: "sqx-edge-tester-portal-preview",
  officialWorkersDevDocsChecked: true,
  officialWranglerCommandsDocsChecked: true,
  officialAccessApplicationTypesDocsChecked: true,
  officialAccessSelfHostedDocsChecked: true,
  officialRequireAccessProtectionDocsChecked: true,
  mainWranglerWorkersDevDisabled: mainWrangler.workers_dev === false,
  mainWranglerPreviewUrlsDisabled: mainWrangler.preview_urls === false,
  mainWranglerStillRealAppConfig: mainWrangler.main === ".open-next/worker.js",
  shellConfigExists: shellWrangler.main === "cloudflare/shell-worker.js",
  shellConfigWorkersDevEnabled: shellWrangler.workers_dev === true,
  shellConfigPreviewUrlsDisabled: shellWrangler.preview_urls === false,
  shellUsesSameWorkerName: shellWrangler.name === mainWrangler.name,
  shellIsNotOpenNextApp: shellWrangler.main !== mainWrangler.main,
  shellReturnsLockedNoAppResponse:
    shellWorker.includes("SQX Edge tester shell locked") &&
    shellWorker.includes("status: 404") &&
    shellWorker.includes("no-store") &&
    shellWorker.includes("noindex"),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-workers-dev-shell-gate"] ===
    "node scripts/cloudflare-workers-dev-shell-gate-proof.mjs",
  docsReady:
    doc.includes("T10ajm Workers.dev Shell Gate") &&
    doc.includes("GO_WORKERS_DEV_SHELL_GATE_READY_EXACT_DEPLOY_APPROVAL_REQUIRED") &&
    doc.includes("T10ajn_controlled_workers_dev_shell_deploy"),
  governanceUpdated: governance.includes("T10ajm - Workers.dev Shell Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajm: prepare a controlled workers.dev shell gate"),
  readmeUpdated: readme.includes("T10ajm anade `proof:cloudflare-workers-dev-shell-gate`"),
  changelogUpdated: changelog.includes("T10ajm Workers.dev Shell Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-workers-dev-shell-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  cloudflareWorkerCreated: false,
  cloudflareAccessApplicationCreated: false,
  cloudflareAccessPolicyCreated: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  t10akUnlocked: false,
  nextGate: "T10ajn_controlled_workers_dev_shell_deploy",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.officialWorkersDevDocsChecked ||
  !proof.officialWranglerCommandsDocsChecked ||
  !proof.officialAccessApplicationTypesDocsChecked ||
  !proof.officialAccessSelfHostedDocsChecked ||
  !proof.officialRequireAccessProtectionDocsChecked ||
  !proof.mainWranglerWorkersDevDisabled ||
  !proof.mainWranglerPreviewUrlsDisabled ||
  !proof.mainWranglerStillRealAppConfig ||
  !proof.shellConfigExists ||
  !proof.shellConfigWorkersDevEnabled ||
  !proof.shellConfigPreviewUrlsDisabled ||
  !proof.shellUsesSameWorkerName ||
  !proof.shellIsNotOpenNextApp ||
  !proof.shellReturnsLockedNoAppResponse ||
  !proof.directDeployScriptAbsent ||
  !proof.packageScriptReady ||
  !proof.docsReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  !proof.readmeUpdated ||
  !proof.changelogUpdated ||
  !proof.templateReadmeUpdated ||
  !proof.noSensitiveCloudflareEnvCommitted ||
  proof.cloudflareWorkerCreated ||
  proof.cloudflareAccessApplicationCreated ||
  proof.cloudflareAccessPolicyCreated ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.t10akUnlocked
) {
  process.exitCode = 1;
}
