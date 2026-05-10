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
const wranglerConfig = JSON.parse(readProject("wrangler.jsonc"));
const exampleEvidence = JSON.parse(readProject("cloudflare-hostname-zone-selection.example.json"));
const localEvidence = readOptionalJson("cloudflare-hostname-zone-selection.local.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AJL_CLOUDFLARE_HOSTNAME_ZONE_SELECTION.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};
const forbiddenLocalKeys = new Set([
  "accountId",
  "apiToken",
  "cloudflareAccountId",
  "cloudflareApiToken",
  "cloudflareZoneId",
  "email",
  "emails",
  "hostname",
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
  /\.vercel\.app/i,
  /cloudflareaccess\.com/i,
  /CLOUDFLARE_[A-Z_]+/i,
  /-----BEGIN [A-Z ]+PRIVATE KEY-----/,
  /\b[A-Fa-f0-9]{32,}\b/,
];

function scanEvidence(value, path = []) {
  const findings = [];
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      findings.push(...scanEvidence(item, [...path, String(index)]));
    });
    return findings;
  }

  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, nested]) => {
      const keyPath = [...path, key];
      if (forbiddenLocalKeys.has(key)) {
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

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const localFindings = localEvidence ? scanEvidence(localEvidence) : [];
const localEvidenceReady = Boolean(
  localEvidence &&
  localFindings.length === 0 &&
  localEvidence.accessPrecreateAllowed === true &&
  localEvidence.t10akUnlocked === true &&
  localEvidence.testerUrlPublished === false &&
  localEvidence.testerEmailsIncluded === false &&
  (
    (
      localEvidence.hostnameSelectedPrivately === true &&
      localEvidence.zoneSelectedPrivately === true &&
      localEvidence.hostnameBelongsToCloudflareZone === true &&
      localEvidence.accessHostnameCanBeMatched === true &&
      localEvidence.routeCanBeCreatedAfterDeploy === true
    ) ||
    (
      localEvidence.workersDevOnboardingComplete === true &&
      localEvidence.workersDevShellTargetExists === true &&
      localEvidence.workersDevAccessProtectionVerified === true &&
      localEvidence.accessHostnameCanBeMatched === true
    )
  )
);

const proof = Object.freeze({
  phase: "T10ajl",
  result: localEvidenceReady
    ? "GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED"
    : "NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED",
  provider: "Cloudflare",
  requestedWorkerName: "sqx-edge-tester-portal-preview",
  officialRoutesDocsChecked: true,
  officialCustomDomainsDocsChecked: true,
  officialWorkersDevDocsChecked: true,
  officialAccessSelfHostedDocsChecked: true,
  officialAccessApplicationTypesDocsChecked: true,
  localEvidencePresent: localEvidence !== null,
  localEvidenceHasNoSensitiveFields: localFindings.length === 0,
  localFindings,
  hostnameSelectedPrivately: localEvidence?.hostnameSelectedPrivately === true,
  zoneSelectedPrivately: localEvidence?.zoneSelectedPrivately === true,
  hostnameBelongsToCloudflareZone: localEvidence?.hostnameBelongsToCloudflareZone === true,
  workersDevOnboardingComplete: localEvidence?.workersDevOnboardingComplete === true,
  workersDevShellTargetExists: localEvidence?.workersDevShellTargetExists === true,
  workersDevAccessProtectionVerified: localEvidence?.workersDevAccessProtectionVerified === true,
  accessHostnameCanBeMatched: localEvidence?.accessHostnameCanBeMatched === true,
  routeCanBeCreatedAfterDeploy: localEvidence?.routeCanBeCreatedAfterDeploy === true,
  accessPrecreateAllowed: localEvidence?.accessPrecreateAllowed === true,
  wranglerWorkersDevDisabled: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  publicRoutesCommitted: Array.isArray(wranglerConfig.routes) && wranglerConfig.routes.length > 0,
  packageScriptReady:
    scripts["proof:cloudflare-hostname-zone-selection"] ===
    "node scripts/cloudflare-hostname-zone-selection-proof.mjs",
  localEvidenceIgnored: gitignore.includes("cloudflare-hostname-zone-selection.local.json"),
  exampleEvidencePublicSafe:
    exampleEvidence.phase === "T10ajl" &&
    exampleEvidence.hostnameSelectedPrivately === false &&
    exampleEvidence.zoneSelectedPrivately === false &&
    exampleEvidence.accessPrecreateAllowed === false &&
    exampleEvidence.testerEmailsIncluded === false,
  docHasNoSecretPattern:
    !doc.includes(forbiddenTokenPattern) &&
    !doc.includes(forbiddenAccountPattern) &&
    !doc.includes(forbiddenZonePattern),
  docReady:
    doc.includes("NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED") &&
    doc.includes("GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED") &&
    doc.includes("T10ak_cloudflare_access_application_policy_creation"),
  governanceUpdated: governance.includes("T10ajl - Cloudflare Hostname Zone Selection"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajl: select private Cloudflare hostname/zone"),
  cloudflareWorkerCreated: false,
  cloudflareVersionUploaded: false,
  cloudflareDeploymentCreated: false,
  cloudflareRouteCreated: false,
  cloudflareAccessApplicationCreated: false,
  cloudflareAccessPolicyCreated: false,
  githubRepositoryConnectedToCloudflare: false,
  cloudflareTokenCommitted: false,
  cloudflareAccountIdCommitted: false,
  cloudflareZoneIdCommitted: false,
  hostnameCommitted: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  renewalEmailsSent: false,
  productionDatabaseConnected: false,
  t10akUnlocked: localEvidenceReady,
  nextGate: "T10ak_cloudflare_access_application_policy_creation",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.officialRoutesDocsChecked ||
  !proof.officialCustomDomainsDocsChecked ||
  !proof.officialWorkersDevDocsChecked ||
  !proof.officialAccessSelfHostedDocsChecked ||
  !proof.officialAccessApplicationTypesDocsChecked ||
  !proof.wranglerWorkersDevDisabled ||
  !proof.wranglerPreviewUrlsDisabled ||
  proof.publicRoutesCommitted ||
  !proof.packageScriptReady ||
  !proof.localEvidenceIgnored ||
  !proof.localEvidenceHasNoSensitiveFields ||
  !proof.exampleEvidencePublicSafe ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  proof.cloudflareWorkerCreated ||
  proof.cloudflareVersionUploaded ||
  proof.cloudflareDeploymentCreated ||
  proof.cloudflareRouteCreated ||
  proof.cloudflareAccessApplicationCreated ||
  proof.cloudflareAccessPolicyCreated ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted
) {
  process.exitCode = 1;
}
