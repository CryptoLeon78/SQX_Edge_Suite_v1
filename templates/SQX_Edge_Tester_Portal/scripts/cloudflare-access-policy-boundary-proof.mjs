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

function scanEvidence(value, path = []) {
  const findings = [];
  const forbiddenKeys = new Set([
    "accessAppId",
    "accessApplicationId",
    "accessPolicyId",
    "accountId",
    "apiToken",
    "cloudflareAccountId",
    "cloudflareApiToken",
    "cloudflareZoneId",
    "email",
    "emails",
    "hostname",
    "policyId",
    "selectedHostname",
    "testerEmail",
    "testerEmails",
    "testerUrl",
    "token",
    "url",
    "zoneId",
  ]);
  const forbiddenValuePatterns = [
    /@/,
    /https?:\/\//i,
    /\.workers\.dev/i,
    /\.vercel\.app/i,
    /cloudflareaccess\.com/i,
    /CLOUDFLARE_[A-Z_]+/i,
    /-----BEGIN [A-Z ]+PRIVATE KEY-----/,
    /\b[A-Fa-f0-9]{32,}\b/,
  ];

  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      findings.push(...scanEvidence(item, [...path, String(index)]));
    });
    return findings;
  }

  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, nested]) => {
      const keyPath = [...path, key];
      if (forbiddenKeys.has(key)) {
        findings.push(`forbidden_key:${keyPath.join(".")}`);
      }
      findings.push(...scanEvidence(nested, keyPath));
    });
    return findings;
  }

  if (typeof value === "string") {
    forbiddenValuePatterns.forEach((pattern) => {
      if (pattern.test(value)) {
        findings.push(`forbidden_value:${path.join(".")}`);
      }
    });
  }

  return findings;
}

const packageJson = JSON.parse(readProject("package.json"));
const mainWrangler = JSON.parse(readProject("wrangler.jsonc"));
const shellWrangler = JSON.parse(readProject("wrangler.shell.example.jsonc"));
const exampleEvidence = JSON.parse(readProject("cloudflare-access-policy-boundary.example.json"));
const localEvidence = readOptionalJson("cloudflare-access-policy-boundary.local.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AK_ACCESS_POLICY_BOUNDARY.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const localFindings = localEvidence ? scanEvidence(localEvidence) : [];
const combinedPublicText = [doc, governance, nextSteps, readme, changelog, templateReadme].join("\n");

const localBoundaryReady = Boolean(
  localEvidence &&
    localFindings.length === 0 &&
    localEvidence.accessApplicationPresent === true &&
    localEvidence.accessApplicationMatchesWorkersDevShell === true &&
    localEvidence.accessPolicyPresent === true &&
    localEvidence.accessPolicyUsesEmailIdentity === true &&
    localEvidence.accessPolicyAllowsOnlyApprovedPilotUsers === true &&
    localEvidence.anonymousAccessRedirectVerified === true &&
    localEvidence.directShellBodyBlockedForAnonymous === true &&
    localEvidence.workersDevShellTargetExists === true &&
    localEvidence.workersDevAccessProtectionVerified === true &&
    localEvidence.realAppDeployed === false &&
    localEvidence.testerUrlPublished === false &&
    localEvidence.testerEmailsIncluded === false &&
    localEvidence.t10alUnlocked === true &&
    localEvidence.operatorChecklist?.accessAppNameCheckedPrivately === true &&
    localEvidence.operatorChecklist?.accessPolicyNameCheckedPrivately === true &&
    localEvidence.operatorChecklist?.policyAllowlistCheckedPrivately === true &&
    localEvidence.operatorChecklist?.anonymousProbeRedirectsToAccess === true &&
    localEvidence.operatorChecklist?.noPublicTesterUrlShared === true &&
    localEvidence.operatorChecklist?.noRealAppDeployPerformed === true
);

const proof = Object.freeze({
  phase: "T10ak",
  result: localBoundaryReady
    ? "GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY"
    : "NO_GO_ACCESS_POLICY_BOUNDARY_EVIDENCE_REQUIRED",
  provider: "Cloudflare",
  selectedPath: "workers_dev_access_application_policy_boundary",
  localEvidencePresent: localEvidence !== null,
  localEvidenceHasNoSensitiveFields: localFindings.length === 0,
  localFindings,
  accessApplicationPresent: localEvidence?.accessApplicationPresent === true,
  accessApplicationMatchesWorkersDevShell: localEvidence?.accessApplicationMatchesWorkersDevShell === true,
  accessPolicyPresent: localEvidence?.accessPolicyPresent === true,
  accessPolicyUsesEmailIdentity: localEvidence?.accessPolicyUsesEmailIdentity === true,
  accessPolicyAllowsOnlyApprovedPilotUsers: localEvidence?.accessPolicyAllowsOnlyApprovedPilotUsers === true,
  anonymousAccessRedirectVerified: localEvidence?.anonymousAccessRedirectVerified === true,
  directShellBodyBlockedForAnonymous: localEvidence?.directShellBodyBlockedForAnonymous === true,
  workersDevShellTargetExists: localEvidence?.workersDevShellTargetExists === true,
  workersDevAccessProtectionVerified: localEvidence?.workersDevAccessProtectionVerified === true,
  mainWranglerWorkersDevDisabled: mainWrangler.workers_dev === false,
  mainWranglerPreviewUrlsDisabled: mainWrangler.preview_urls === false,
  shellConfigWorkersDevEnabled: shellWrangler.workers_dev === true,
  shellConfigPreviewUrlsDisabled: shellWrangler.preview_urls === false,
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-access-policy-boundary"] ===
    "node scripts/cloudflare-access-policy-boundary-proof.mjs",
  localEvidenceIgnored: gitignore.includes("cloudflare-access-policy-boundary.local.json"),
  exampleEvidencePublicSafe:
    exampleEvidence.phase === "T10ak" &&
    exampleEvidence.accessApplicationPresent === false &&
    exampleEvidence.accessPolicyPresent === false &&
    exampleEvidence.testerUrlPublished === false &&
    exampleEvidence.testerEmailsIncluded === false,
  docReady:
    doc.includes("T10ak Access Policy Boundary") &&
    doc.includes("GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY") &&
    doc.includes("NO_GO_ACCESS_POLICY_BOUNDARY_EVIDENCE_REQUIRED") &&
    doc.includes("T10al_controlled_real_app_deploy_gate"),
  governanceUpdated: governance.includes("T10ak - Access Policy Boundary"),
  nextStepsUpdated: nextSteps.includes("Phase T10ak: record/verify the Cloudflare Access application and policy boundary"),
  readmeUpdated: readme.includes("T10ak anade `proof:cloudflare-access-policy-boundary`"),
  changelogUpdated: changelog.includes("T10ak Access Policy Boundary"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-access-policy-boundary"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  realAppDeployed: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  t10alUnlocked: localBoundaryReady,
  nextGate: localBoundaryReady
    ? "T10al_controlled_real_app_deploy_gate"
    : "T10ak_access_policy_boundary_private_evidence",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.localEvidencePresent ||
  !proof.localEvidenceHasNoSensitiveFields ||
  !proof.accessApplicationPresent ||
  !proof.accessApplicationMatchesWorkersDevShell ||
  !proof.accessPolicyPresent ||
  !proof.accessPolicyUsesEmailIdentity ||
  !proof.accessPolicyAllowsOnlyApprovedPilotUsers ||
  !proof.anonymousAccessRedirectVerified ||
  !proof.directShellBodyBlockedForAnonymous ||
  !proof.workersDevShellTargetExists ||
  !proof.workersDevAccessProtectionVerified ||
  !proof.mainWranglerWorkersDevDisabled ||
  !proof.mainWranglerPreviewUrlsDisabled ||
  !proof.shellConfigWorkersDevEnabled ||
  !proof.shellConfigPreviewUrlsDisabled ||
  !proof.directDeployScriptAbsent ||
  !proof.packageScriptReady ||
  !proof.localEvidenceIgnored ||
  !proof.exampleEvidencePublicSafe ||
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
  proof.testerEmailsCommitted ||
  !proof.t10alUnlocked
) {
  process.exitCode = 1;
}
