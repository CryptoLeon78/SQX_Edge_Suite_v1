import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");

function readProject(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readOptionalProjectJson(relativePath) {
  const fullPath = join(projectRoot, relativePath);
  if (!existsSync(fullPath)) return null;
  return JSON.parse(readFileSync(fullPath, "utf8"));
}

function readRepo(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

const packageJson = JSON.parse(readProject("package.json"));
const wranglerConfig = JSON.parse(readProject("wrangler.jsonc"));
const localEvidence = readOptionalProjectJson("cloudflare-workers-dev-publication.local.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AP_CONTROLLED_WORKERS_DEV_PUBLICATION_RESULT.md");
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

const localEvidenceHasNoSensitiveFields =
  localEvidence !== null &&
  localEvidence.containsHostname === false &&
  localEvidence.containsUrl === false &&
  localEvidence.containsAccountId === false &&
  localEvidence.containsAccessId === false &&
  localEvidence.containsDeploymentId === false &&
  localEvidence.containsVersionId === false &&
  localEvidence.containsTesterEmail === false &&
  localEvidence.containsToken === false &&
  localEvidence.containsKey === false;

const localEvidenceReady =
  localEvidence?.phase === "T10ap" &&
  localEvidence?.exactApprovalReceived === true &&
  localEvidence?.prechecksPassed === true &&
  localEvidence?.changedOnlyWorkersDevForDeploy === true &&
  localEvidence?.deployCommandExecuted === true &&
  localEvidence?.deployCommand === "npm exec -- wrangler deploy --config wrangler.jsonc" &&
  localEvidence?.deployCommandCount === 1 &&
  localEvidence?.wranglerDeploySucceeded === true &&
  localEvidence?.workersDevRemoteTargetEnabled === true &&
  localEvidence?.anonymousRootAccessIntercepted === true &&
  localEvidence?.anonymousHealthAccessIntercepted === true &&
  localEvidence?.anonymousPortalAccessIntercepted === true &&
  localEvidence?.directAppBodyVisibleToAnonymous === false &&
  localEvidence?.previewUrlsEnabled === false &&
  localEvidence?.customRouteAdded === false &&
  localEvidence?.testerUrlShared === false &&
  localEvidence?.testerAccountsCreated === false &&
  localEvidence?.testerEmailsCommitted === false &&
  localEvidence?.rollbackRequired === false &&
  localEvidence?.rollbackPerformed === false &&
  localEvidence?.repoWorkersDevRestoredFalseAfterDeployWithoutSecondDeploy === true &&
  localEvidenceHasNoSensitiveFields;

const proof = Object.freeze({
  phase: "T10ap",
  result: localEvidenceReady
    ? "GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED"
    : "NO_GO_WORKERS_DEV_PUBLICATION_RESULT_EVIDENCE_REQUIRED",
  provider: "Cloudflare",
  selectedTarget: "workers_dev_access_protected_publication_target",
  localEvidencePresent: localEvidence !== null,
  localEvidenceIgnored: gitignore.includes("cloudflare-workers-dev-publication.local.json"),
  localEvidenceHasNoSensitiveFields,
  exactApprovalReceived: localEvidence?.exactApprovalReceived === true,
  prechecksPassed: localEvidence?.prechecksPassed === true,
  changedOnlyWorkersDevForDeploy: localEvidence?.changedOnlyWorkersDevForDeploy === true,
  deployCommandExecuted: localEvidence?.deployCommandExecuted === true,
  deployCommandCountIsOne: localEvidence?.deployCommandCount === 1,
  wranglerDeploySucceeded: localEvidence?.wranglerDeploySucceeded === true,
  workersDevRemoteTargetEnabled: localEvidence?.workersDevRemoteTargetEnabled === true,
  anonymousRootAccessIntercepted: localEvidence?.anonymousRootAccessIntercepted === true,
  anonymousHealthAccessIntercepted: localEvidence?.anonymousHealthAccessIntercepted === true,
  anonymousPortalAccessIntercepted: localEvidence?.anonymousPortalAccessIntercepted === true,
  directAppBodyVisibleToAnonymous: localEvidence?.directAppBodyVisibleToAnonymous === true,
  previewUrlsEnabled: localEvidence?.previewUrlsEnabled === true,
  customRouteAdded: localEvidence?.customRouteAdded === true,
  testerUrlShared: localEvidence?.testerUrlShared === true,
  testerAccountsCreated: localEvidence?.testerAccountsCreated === true,
  testerEmailsCommitted: localEvidence?.testerEmailsCommitted === true,
  rollbackRequired: localEvidence?.rollbackRequired === true,
  rollbackPerformed: localEvidence?.rollbackPerformed === true,
  repoWorkersDevRestoredFalseAfterDeployWithoutSecondDeploy:
    localEvidence?.repoWorkersDevRestoredFalseAfterDeployWithoutSecondDeploy === true,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerMainIsOpenNextWorker: wranglerConfig.main === ".open-next/worker.js",
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-workers-dev-publication-result"] ===
    "node scripts/cloudflare-workers-dev-publication-result-proof.mjs",
  docReady:
    doc.includes("T10ap Controlled Workers.dev Publication Result") &&
    doc.includes("GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED") &&
    doc.includes("T10aq_tester_access_handoff_without_public_url_leak"),
  governanceUpdated: governance.includes("T10ap - Controlled Workers.dev Publication Result"),
  nextStepsUpdated: nextSteps.includes("Phase T10ap: execute controlled `workers.dev` publication"),
  readmeUpdated: readme.includes("T10ap publica el target `workers.dev`"),
  changelogUpdated: changelog.includes("T10ap Controlled Workers.dev Publication Result"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-workers-dev-publication-result"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10aq_tester_access_handoff_without_public_url_leak",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  proof.result !== "GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED" ||
  !proof.localEvidenceIgnored ||
  !proof.localEvidenceHasNoSensitiveFields ||
  !proof.exactApprovalReceived ||
  !proof.prechecksPassed ||
  !proof.changedOnlyWorkersDevForDeploy ||
  !proof.deployCommandExecuted ||
  !proof.deployCommandCountIsOne ||
  !proof.wranglerDeploySucceeded ||
  !proof.workersDevRemoteTargetEnabled ||
  !proof.anonymousRootAccessIntercepted ||
  !proof.anonymousHealthAccessIntercepted ||
  !proof.anonymousPortalAccessIntercepted ||
  proof.directAppBodyVisibleToAnonymous ||
  proof.previewUrlsEnabled ||
  proof.customRouteAdded ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.rollbackRequired ||
  proof.rollbackPerformed ||
  !proof.repoWorkersDevRestoredFalseAfterDeployWithoutSecondDeploy ||
  !proof.wranglerWorkersDevSafeDefault ||
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
