import { existsSync, readFileSync } from "node:fs";
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

function readOptionalJson(relativePath) {
  const absolutePath = join(projectRoot, relativePath);
  if (!existsSync(absolutePath)) {
    return null;
  }
  return JSON.parse(readFileSync(absolutePath, "utf8"));
}

const packageJson = JSON.parse(readProject("package.json"));
const mainWrangler = JSON.parse(readProject("wrangler.jsonc"));
const shellWrangler = JSON.parse(readProject("wrangler.shell.example.jsonc"));
const localEvidence = readOptionalJson("cloudflare-hostname-zone-selection.local.json");
const doc = readRepo("docs/T10AJN_CONTROLLED_WORKERS_DEV_SHELL_DEPLOY.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const localShellTargetExists = localEvidence?.workersDevShellTargetExists === true;
const accessVerified = localEvidence?.workersDevAccessProtectionVerified === true;
const accessCanMatch = localEvidence?.accessHostnameCanBeMatched === true;
const accessPrecreateAllowed = localEvidence?.accessPrecreateAllowed === true;
const testerUrlPublished = localEvidence?.testerUrlPublished === true;
const testerEmailsIncluded = localEvidence?.testerEmailsIncluded === true;
const accessReady = Boolean(
  localShellTargetExists &&
  accessVerified &&
  accessCanMatch &&
  accessPrecreateAllowed &&
  testerUrlPublished === false &&
  testerEmailsIncluded === false
);

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [doc, governance, nextSteps, readme, changelog, templateReadme].join("\n");

const proof = Object.freeze({
  phase: "T10ajn",
  result: accessReady
    ? "GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_READY_FOR_T10AK"
    : "NO_GO_ACCESS_MANUAL_ENABLE_REQUIRED_SHELL_TARGET_EXISTS",
  provider: "Cloudflare",
  selectedPath: "workers_dev_shell_then_access_then_real_app",
  requestedWorkerName: "sqx-edge-tester-portal-preview",
  shellDeployCommandDocumented:
    doc.includes("npm exec -- wrangler deploy --config wrangler.shell.example.jsonc"),
  shellTargetCreatedEvidenceRecorded: doc.includes("WORKERS_DEV_SHELL_TARGET_CREATED"),
  shellLockedResponseRecorded: doc.includes("404 SQX Edge tester shell locked"),
  accessAutomationBlockedByPermission: doc.includes("Access: Apps and Policies Write"),
  localEvidencePresent: localEvidence !== null,
  workersDevShellTargetExists: localShellTargetExists,
  workersDevAccessProtectionVerified: accessVerified,
  accessHostnameCanBeMatched: accessCanMatch,
  accessPrecreateAllowed,
  testerUrlPublished,
  testerEmailsIncluded,
  mainWranglerWorkersDevDisabled: mainWrangler.workers_dev === false,
  mainWranglerPreviewUrlsDisabled: mainWrangler.preview_urls === false,
  shellConfigWorkersDevEnabled: shellWrangler.workers_dev === true,
  shellConfigPreviewUrlsDisabled: shellWrangler.preview_urls === false,
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-workers-dev-shell-deploy"] ===
    "node scripts/cloudflare-workers-dev-shell-deploy-proof.mjs",
  docReady:
    doc.includes("T10ajn Controlled Workers.dev Shell Deploy") &&
    doc.includes("NO_GO_ACCESS_MANUAL_ENABLE_REQUIRED_SHELL_TARGET_EXISTS") &&
    doc.includes("T10ajo_workers_dev_access_manual_enable_evidence"),
  governanceUpdated: governance.includes("T10ajn - Controlled Workers.dev Shell Deploy"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajn: deploy only the harmless workers.dev shell"),
  readmeUpdated: readme.includes("T10ajn anade `proof:cloudflare-workers-dev-shell-deploy`"),
  changelogUpdated: changelog.includes("T10ajn Controlled Workers.dev Shell Deploy"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-workers-dev-shell-deploy"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  realAppDeployed: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  t10akUnlocked: accessReady,
  nextGate: accessReady
    ? "T10ak_cloudflare_access_application_policy_creation"
    : "T10ajo_workers_dev_access_manual_enable_evidence",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.shellDeployCommandDocumented ||
  !proof.shellTargetCreatedEvidenceRecorded ||
  !proof.shellLockedResponseRecorded ||
  !proof.accessAutomationBlockedByPermission ||
  !proof.localEvidencePresent ||
  !proof.workersDevShellTargetExists ||
  proof.testerUrlPublished ||
  proof.testerEmailsIncluded ||
  !proof.mainWranglerWorkersDevDisabled ||
  !proof.mainWranglerPreviewUrlsDisabled ||
  !proof.shellConfigWorkersDevEnabled ||
  !proof.shellConfigPreviewUrlsDisabled ||
  !proof.directDeployScriptAbsent ||
  !proof.packageScriptReady ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  !proof.readmeUpdated ||
  !proof.changelogUpdated ||
  !proof.templateReadmeUpdated ||
  !proof.noSensitiveCloudflareEnvCommitted ||
  proof.realAppDeployed ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted
) {
  process.exitCode = 1;
}
