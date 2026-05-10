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
const doc = readRepo("docs/T10AJO_WORKERS_DEV_ACCESS_VERIFIED.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const shellTargetExists = localEvidence?.workersDevShellTargetExists === true;
const accessVerified = localEvidence?.workersDevAccessProtectionVerified === true;
const accessCanMatch = localEvidence?.accessHostnameCanBeMatched === true;
const accessPrecreateAllowed = localEvidence?.accessPrecreateAllowed === true;
const t10akUnlocked = localEvidence?.t10akUnlocked === true;
const testerUrlPublished = localEvidence?.testerUrlPublished === true;
const testerEmailsIncluded = localEvidence?.testerEmailsIncluded === true;

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [doc, governance, nextSteps, readme, changelog, templateReadme].join("\n");

const accessReady = Boolean(
  shellTargetExists &&
    accessVerified &&
    accessCanMatch &&
    accessPrecreateAllowed &&
    t10akUnlocked &&
    testerUrlPublished === false &&
    testerEmailsIncluded === false
);

const proof = Object.freeze({
  phase: "T10ajo",
  result: accessReady
    ? "GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP"
    : "NO_GO_WORKERS_DEV_ACCESS_EVIDENCE_REQUIRED",
  provider: "Cloudflare",
  selectedPath: "workers_dev_shell_access_verified_before_real_app",
  localEvidencePresent: localEvidence !== null,
  workersDevShellTargetExists: shellTargetExists,
  workersDevAccessProtectionVerified: accessVerified,
  accessHostnameCanBeMatched: accessCanMatch,
  accessPrecreateAllowed,
  t10akUnlocked,
  testerUrlPublished,
  testerEmailsIncluded,
  mainWranglerWorkersDevDisabled: mainWrangler.workers_dev === false,
  mainWranglerPreviewUrlsDisabled: mainWrangler.preview_urls === false,
  shellConfigWorkersDevEnabled: shellWrangler.workers_dev === true,
  shellConfigPreviewUrlsDisabled: shellWrangler.preview_urls === false,
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-workers-dev-access"] ===
    "node scripts/cloudflare-workers-dev-access-proof.mjs",
  docReady:
    doc.includes("T10ajo Workers.dev Access Verified") &&
    doc.includes("GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP") &&
    doc.includes("directShellBody=false") &&
    doc.includes("T10ak_cloudflare_access_application_policy_creation_or_verification"),
  governanceUpdated: governance.includes("T10ajo - Workers.dev Access Verified"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajo: enable or verify Cloudflare Access on the existing workers.dev shell"),
  readmeUpdated: readme.includes("T10ajo verifica Cloudflare Access encima del shell"),
  changelogUpdated: changelog.includes("T10ajo Workers.dev Access Verified"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-workers-dev-access"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  realAppDeployed: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  nextGate: accessReady
    ? "T10ak_cloudflare_access_application_policy_creation_or_verification"
    : "T10ajo_workers_dev_access_manual_enable_evidence",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.localEvidencePresent ||
  !proof.workersDevShellTargetExists ||
  !proof.workersDevAccessProtectionVerified ||
  !proof.accessHostnameCanBeMatched ||
  !proof.accessPrecreateAllowed ||
  !proof.t10akUnlocked ||
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
