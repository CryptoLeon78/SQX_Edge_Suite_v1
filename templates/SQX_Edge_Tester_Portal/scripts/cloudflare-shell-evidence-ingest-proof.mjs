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

function tryReadJson(path) {
  if (!existsSync(path)) {
    return { exists: false, parsed: null, parseError: null };
  }

  try {
    return { exists: true, parsed: JSON.parse(readFileSync(path, "utf8")), parseError: null };
  } catch (error) {
    return { exists: true, parsed: null, parseError: String(error?.message ?? error) };
  }
}

const packageJson = JSON.parse(readProject("package.json"));
const example = JSON.parse(readProject("cloudflare-shell-evidence.example.json"));
const localEvidencePath = join(projectRoot, "cloudflare-shell-evidence.local.json");
const localEvidence = tryReadJson(localEvidencePath);
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AJC_CLOUDFLARE_SHELL_EVIDENCE_INGEST.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenDeployFragments = [
  "wrangler deploy",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
];

const evidence = localEvidence.parsed ?? example;
const evidenceIsGo = Boolean(
  localEvidence.exists &&
    !localEvidence.parseError &&
    evidence.projectShellName === "sqx-edge-tester-portal-preview" &&
    evidence.shellVerified === true &&
    evidence.deploymentCreated === false &&
    evidence.accessApplicationCreated === false &&
    evidence.accessPolicyCreated === false &&
    evidence.customDomainAttached === false &&
    evidence.testerUrlPublished === false &&
    evidence.testerAccountsCreated === false &&
    evidence.testerEmailsIncluded === false
);

const result = evidenceIsGo
  ? "GO_CLOUDFLARE_SHELL_EVIDENCE_VERIFIED_T10AK_READY_FOR_EXACT_APPROVAL"
  : "NO_GO_CLOUDFLARE_SHELL_EVIDENCE_MISSING_T10AK_BLOCKED";

const proof = Object.freeze({
  phase: "T10ajc",
  result,
  provider: "Cloudflare",
  requestedProjectShellName: "sqx-edge-tester-portal-preview",
  localEvidencePath: "cloudflare-shell-evidence.local.json",
  localEvidencePresent: localEvidence.exists,
  localEvidenceParseError: localEvidence.parseError,
  localEvidenceIgnored: gitignore.includes("cloudflare-shell-evidence.local.json"),
  exampleEvidencePresent: existsSync(join(projectRoot, "cloudflare-shell-evidence.example.json")),
  evidenceShellVerified: evidence.shellVerified === true,
  evidenceDeploymentCreated: evidence.deploymentCreated === true,
  evidenceAccessApplicationCreated: evidence.accessApplicationCreated === true,
  evidenceAccessPolicyCreated: evidence.accessPolicyCreated === true,
  evidenceCustomDomainAttached: evidence.customDomainAttached === true,
  evidenceTesterUrlPublished: evidence.testerUrlPublished === true,
  evidenceTesterAccountsCreated: evidence.testerAccountsCreated === true,
  evidenceTesterEmailsIncluded: evidence.testerEmailsIncluded === true,
  t10akUnlocked: evidenceIsGo,
  packageScriptReady:
    scripts["proof:cloudflare-shell-evidence-ingest"] === "node scripts/cloudflare-shell-evidence-ingest-proof.mjs",
  deployScriptPublished: Object.keys(scripts).some((scriptName) => /(^|:)deploy($|:)/.test(scriptName)),
  forbiddenDeployFragmentsPresent: Object.values(scripts).some((script) =>
    forbiddenDeployFragments.some((fragment) => String(script).includes(fragment))
  ),
  docReady: doc.includes("NO_GO_CLOUDFLARE_SHELL_EVIDENCE_MISSING_T10AK_BLOCKED"),
  governanceUpdated: governance.includes("T10ajc - Cloudflare Shell Evidence Ingest"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajd: capture real Cloudflare shell evidence manually/authenticated before T10ak."),
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
  nextGate: evidenceIsGo
    ? "T10ak_cloudflare_access_policy_exact_approval_required"
    : "T10ajd_capture_real_cloudflare_shell_evidence_no_deploy",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.localEvidenceIgnored ||
  !proof.exampleEvidencePresent ||
  !proof.packageScriptReady ||
  proof.deployScriptPublished ||
  proof.forbiddenDeployFragmentsPresent ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
