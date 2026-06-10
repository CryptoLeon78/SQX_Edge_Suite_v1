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

const packageJson = JSON.parse(readProject("package.json"));
const example = JSON.parse(readProject("cloudflare-shell-evidence.example.json"));
const doc = readRepo("docs/T10AJD_CLOUDFLARE_SHELL_EVIDENCE_CAPTURE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const gitignore = readProject(".gitignore");
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
  phase: "T10ajd",
  result: "NO_GO_CLOUDFLARE_CAPTURE_PENDING_MANUAL_AUTH_OR_DASHBOARD_EVIDENCE",
  provider: "Cloudflare",
  requestedProjectShellName: "sqx-edge-tester-portal-preview",
  localWranglerWhoamiResult: "not_authenticated",
  manualCaptureChecklistReady: doc.includes("Manual Capture Checklist"),
  localEvidenceTemplateReady: Boolean(
    example.projectShellName === "sqx-edge-tester-portal-preview" &&
      example.shellVerified === false &&
      example.deploymentCreated === false &&
      example.accessApplicationCreated === false &&
      example.accessPolicyCreated === false &&
      example.testerUrlPublished === false &&
      example.testerAccountsCreated === false &&
      example.testerEmailsIncluded === false
  ),
  localEvidenceIgnored: gitignore.includes("cloudflare-shell-evidence.local.json"),
  localEvidenceCurrentlyPresent: existsSync(join(projectRoot, "cloudflare-shell-evidence.local.json")),
  packageScriptReady:
    scripts["proof:cloudflare-shell-evidence-capture"] === "node scripts/cloudflare-shell-evidence-capture-proof.mjs",
  deployScriptPublished: Object.keys(scripts).some((scriptName) => /(^|:)deploy($|:)/.test(scriptName)),
  forbiddenDeployFragmentsPresent: Object.values(scripts).some((script) =>
    forbiddenDeployFragments.some((fragment) => String(script).includes(fragment))
  ),
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  governanceUpdated: governance.includes("T10ajd - Cloudflare Shell Evidence Capture Checklist"),
  nextStepsUpdated: nextSteps.includes("Phase T10aje: execute manual Cloudflare login/dashboard evidence capture outside git"),
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
  nextGate: "T10aje_manual_cloudflare_evidence_capture_then_t10ajc_ingest",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.manualCaptureChecklistReady ||
  !proof.localEvidenceTemplateReady ||
  !proof.localEvidenceIgnored ||
  !proof.packageScriptReady ||
  proof.deployScriptPublished ||
  proof.forbiddenDeployFragmentsPresent ||
  !proof.docHasNoSecretPattern ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
