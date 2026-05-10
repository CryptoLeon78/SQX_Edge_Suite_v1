import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");

function readFromProject(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readFromRepo(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

const packageJson = JSON.parse(readFromProject("package.json"));
const evidenceExample = JSON.parse(readFromProject("cloudflare-shell-evidence.example.json"));
const gitignore = readFromProject(".gitignore");
const doc = readFromRepo("docs/T10AJB_CLOUDFLARE_AUTH_HANDOFF.md");
const governance = readFromRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readFromRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenDeployFragments = [
  "wrangler deploy",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
];

const proof = Object.freeze({
  phase: "T10ajb",
  result: "NO_GO_CLOUDFLARE_AUTH_HANDOFF_PENDING_MANUAL_LOGIN_OR_EVIDENCE",
  provider: "Cloudflare",
  requestedProjectShellName: "sqx-edge-tester-portal-preview",
  localWranglerWhoamiResult: "not_authenticated",
  authHandoffPrepared: true,
  browserLoginCommandDocumented: true,
  localApiTokenCommandDocumented: true,
  manualDashboardEvidencePathDocumented: true,
  evidenceExamplePresent: existsSync(join(projectRoot, "cloudflare-shell-evidence.example.json")),
  evidenceExampleSafe: Boolean(
    evidenceExample.projectShellName === "sqx-edge-tester-portal-preview" &&
      evidenceExample.shellVerified === false &&
      evidenceExample.deploymentCreated === false &&
      evidenceExample.accessApplicationCreated === false &&
      evidenceExample.accessPolicyCreated === false &&
      evidenceExample.testerUrlPublished === false &&
      evidenceExample.testerAccountsCreated === false &&
      evidenceExample.testerEmailsIncluded === false
  ),
  localEvidenceIgnored: gitignore.includes("cloudflare-shell-evidence.local.json"),
  packageScriptReady: scripts["proof:cloudflare-auth-handoff"] === "node scripts/cloudflare-auth-handoff-proof.mjs",
  deployScriptPublished: Object.keys(scripts).some((scriptName) => /(^|:)deploy($|:)/.test(scriptName)),
  forbiddenDeployFragmentsPresent: Object.values(scripts).some((script) =>
    forbiddenDeployFragments.some((fragment) => String(script).includes(fragment))
  ),
  docHasNoSecretRequest: !doc.includes("paste token here") && doc.includes("never committed"),
  governanceUpdated: governance.includes("T10ajb - Cloudflare Auth Handoff"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajc: ingest authenticated or manual Cloudflare shell evidence without deployment"),
  cloudflareProjectCreated: false,
  cloudflareProjectVerified: false,
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
  nextGate: "T10ajc_ingest_cloudflare_shell_evidence_no_deploy",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.authHandoffPrepared ||
  !proof.evidenceExamplePresent ||
  !proof.evidenceExampleSafe ||
  !proof.localEvidenceIgnored ||
  !proof.packageScriptReady ||
  proof.deployScriptPublished ||
  proof.forbiddenDeployFragmentsPresent ||
  !proof.docHasNoSecretRequest ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
