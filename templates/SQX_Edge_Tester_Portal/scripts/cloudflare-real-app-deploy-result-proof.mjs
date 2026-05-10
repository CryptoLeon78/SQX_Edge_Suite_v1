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
  const path = join(projectRoot, relativePath);
  if (!existsSync(path)) return null;
  return JSON.parse(readFileSync(path, "utf8"));
}

const packageJson = JSON.parse(readProject("package.json"));
const wranglerConfig = JSON.parse(readProject("wrangler.jsonc"));
const localEvidence = readOptionalJson("cloudflare-real-app-deploy.local.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AM_CONTROLLED_REAL_APP_DEPLOY_RESULT.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [doc, governance, nextSteps, readme, changelog, templateReadme].join("\n");
const localEvidenceText = localEvidence ? JSON.stringify(localEvidence) : "";
const forbiddenLocalPatterns = [
  "http://",
  "https://",
  ["@", "gmail.com"].join(""),
  ["@", "hotmail.com"].join(""),
  "CLOUDFLARE_API_TOKEN",
  "CLOUDFLARE_ACCOUNT_ID",
  "CLOUDFLARE_ZONE_ID",
  "deploymentId",
  "deploymentID",
  "versionId",
  "versionID",
  "accountId",
  "accountID",
  "accessAppId",
  "policyId",
  "token",
  "secret",
];

const localEvidenceReady =
  localEvidence?.phase === "T10am" &&
  localEvidence?.workerName === "sqx-edge-tester-portal-preview" &&
  localEvidence?.exactApprovalReceived === true &&
  localEvidence?.prechecksPassed === true &&
  localEvidence?.deployCommandExecuted === true &&
  localEvidence?.wranglerDeploySucceeded === true &&
  localEvidence?.versionUploaded === true &&
  localEvidence?.deploymentRecordPresent === true &&
  localEvidence?.deployTargetsCreated === false &&
  localEvidence?.workersDevPublicTargetEnabled === false &&
  localEvidence?.customDomainAdded === false &&
  localEvidence?.publicRouteAdded === false &&
  localEvidence?.anonymousAccessStillBlockedByExistingAccessEvidence === true &&
  localEvidence?.directAppBodyVisibleToAnonymous === false &&
  localEvidence?.rollbackRequired === false &&
  localEvidence?.testerUrlShared === false &&
  localEvidence?.testerAccountsCreated === false &&
  localEvidence?.testerEmailsIncluded === false;

const proof = Object.freeze({
  phase: "T10am",
  result: localEvidenceReady
    ? "GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL"
    : "NO_GO_REAL_APP_DEPLOY_RESULT_EVIDENCE_REQUIRED",
  provider: "Cloudflare",
  selectedPath: "protected_workers_dev_real_app_version_uploaded_no_public_target",
  localEvidencePresent: localEvidence !== null,
  localEvidenceIgnored: gitignore.includes("cloudflare-real-app-deploy.local.json"),
  localEvidenceHasNoSensitiveFields: !forbiddenLocalPatterns.some((pattern) => localEvidenceText.includes(pattern)),
  exactApprovalReceived: localEvidence?.exactApprovalReceived === true,
  deployCommandExecuted: localEvidence?.deployCommandExecuted === true,
  wranglerDeploySucceeded: localEvidence?.wranglerDeploySucceeded === true,
  versionUploaded: localEvidence?.versionUploaded === true,
  deploymentRecordPresent: localEvidence?.deploymentRecordPresent === true,
  deployTargetsCreated: localEvidence?.deployTargetsCreated === true,
  workersDevPublicTargetEnabled: localEvidence?.workersDevPublicTargetEnabled === true,
  customDomainAdded: localEvidence?.customDomainAdded === true,
  publicRouteAdded: localEvidence?.publicRouteAdded === true,
  anonymousAccessStillBlocked: localEvidence?.anonymousAccessStillBlockedByExistingAccessEvidence === true,
  directAppBodyVisibleToAnonymous: localEvidence?.directAppBodyVisibleToAnonymous === true,
  rollbackRequired: localEvidence?.rollbackRequired === true,
  rollbackPerformed: localEvidence?.rollbackPerformed === true,
  testerUrlShared: localEvidence?.testerUrlShared === true,
  testerAccountsCreated: localEvidence?.testerAccountsCreated === true,
  testerEmailsIncluded: localEvidence?.testerEmailsIncluded === true,
  wranglerWorkersDevDisabled: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerMainIsOpenNextWorker: wranglerConfig.main === ".open-next/worker.js",
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-real-app-deploy-result"] ===
    "node scripts/cloudflare-real-app-deploy-result-proof.mjs",
  docReady:
    doc.includes("T10am Controlled Real App Deploy Result") &&
    doc.includes("GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL") &&
    doc.includes("T10an_protected_tester_publication_target_gate"),
  governanceUpdated: governance.includes("T10am - Controlled Real App Deploy Result"),
  nextStepsUpdated: nextSteps.includes("Phase T10am: execute the approved real app deploy"),
  readmeUpdated: readme.includes("T10am ha subido/desplegado una version real"),
  changelogUpdated: changelog.includes("T10am Controlled Real App Deploy Result"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-real-app-deploy-result"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10an_protected_tester_publication_target_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  proof.result !== "GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL" ||
  !proof.localEvidenceIgnored ||
  !proof.localEvidenceHasNoSensitiveFields ||
  !proof.exactApprovalReceived ||
  !proof.deployCommandExecuted ||
  !proof.wranglerDeploySucceeded ||
  !proof.versionUploaded ||
  !proof.deploymentRecordPresent ||
  proof.deployTargetsCreated ||
  proof.workersDevPublicTargetEnabled ||
  proof.customDomainAdded ||
  proof.publicRouteAdded ||
  !proof.anonymousAccessStillBlocked ||
  proof.directAppBodyVisibleToAnonymous ||
  proof.rollbackRequired ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsIncluded ||
  !proof.wranglerWorkersDevDisabled ||
  !proof.wranglerPreviewUrlsDisabled ||
  !proof.wranglerMainIsOpenNextWorker ||
  !proof.wranglerHasNoRoutesCommitted ||
  !proof.directDeployScriptAbsent ||
  !proof.packageScriptReady ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  !proof.readmeUpdated ||
  !proof.changelogUpdated ||
  !proof.templateReadmeUpdated ||
  !proof.noSensitiveCloudflareEnvCommitted
) {
  process.exitCode = 1;
}
