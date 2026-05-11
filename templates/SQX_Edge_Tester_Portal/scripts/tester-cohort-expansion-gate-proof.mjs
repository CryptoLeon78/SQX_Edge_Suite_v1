import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localExpansionPath = join(projectRoot, "tester-cohort-expansion.local.json");

function readProject(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readRepo(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

const booleanFields = new Set([
  "t10auFirstSmokeGo",
  "firstTesterSmokePassedPrivately",
  "cohortSizeWithinLimit",
  "privateAccountsPreparedForCohort",
  "privateOneToOneShareChannelsReady",
  "supportCapacityReadyPrivately",
  "revocationPathReadyPrivately",
  "renewalCadenceScheduled",
  "feedbackIntakeReadyPrivately",
  "redactedFeedbackPolicyReady",
  "cohortExpansionApprovedPrivately",
  "testerUrlsSharedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
  "publicRepoContainsFeedbackIdentities",
]);

const countFields = new Set(["approvedTesterCount", "targetCohortSize", "supportOwnerCount", "failedCheckCount"]);
const allowedFields = new Set(["phase", ...booleanFields, ...countFields]);

const forbiddenValuePatterns = [
  /@[a-z0-9.-]+\.[a-z]{2,}/i,
  /https?:\/\//i,
  /workers\.dev/i,
  /\.vercel\.app/i,
  /CLOUDFLARE_API_TOKEN/i,
  /CLOUDFLARE_ACCOUNT_ID/i,
  /CLOUDFLARE_ZONE_ID/i,
  /password/i,
  /secret/i,
  /token/i,
  /cookie/i,
  /access[_-]?id/i,
  /account[_-]?id/i,
  /policy[_-]?id/i,
  /deployment[_-]?id/i,
  /version[_-]?id/i,
  /url/i,
  /host/i,
  /domain/i,
  /route/i,
  /screenshot/i,
  /feedback/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateExpansion(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["cohort expansion evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10av") {
        errors.push("phase must be T10av");
      }
      continue;
    }

    if (booleanFields.has(key)) {
      if (typeof value !== "boolean") {
        errors.push(`${key} must be boolean`);
      }
      continue;
    }

    if (!Number.isInteger(value) || value < 0 || value > 50) {
      errors.push(`${key} must be a non-negative integer no greater than 50`);
    }
  }

  for (const value of Object.values(evidence)) {
    if (typeof value !== "string") {
      continue;
    }
    for (const pattern of forbiddenValuePatterns) {
      if (pattern.test(value)) {
        errors.push(`forbidden sensitive pattern detected: ${pattern.source}`);
      }
    }
  }

  return errors;
}

const packageJson = parseJson(readProject("package.json"), "package.json");
const wranglerConfig = parseJson(readProject("wrangler.jsonc"), "wrangler.jsonc");
const exampleExpansion = parseJson(
  readProject("tester-cohort-expansion.example.json"),
  "tester-cohort-expansion.example.json",
);
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AV_PRIVATE_TESTER_COHORT_EXPANSION_GATE.md");
const t10auDoc = readRepo("docs/T10AU_PRIVATE_FIRST_TESTER_SMOKE_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localExpansionPresent = existsSync(localExpansionPath);
const localExpansion = localExpansionPresent
  ? parseJson(readFileSync(localExpansionPath, "utf8"), "tester-cohort-expansion.local.json")
  : null;
const localExpansionErrors = localExpansionPresent ? validateExpansion(localExpansion) : [];

const exampleExpansionSafe =
  exampleExpansion.phase === "T10av" &&
  validateExpansion(exampleExpansion).length === 0 &&
  [...booleanFields].every((key) => exampleExpansion[key] === false) &&
  [...countFields].every((key) => exampleExpansion[key] === 0);

const noPublicLeak =
  !localExpansionPresent ||
  (localExpansion.publicRepoContainsTesterEmails === false &&
    localExpansion.publicRepoContainsTesterUrl === false &&
    localExpansion.publicRepoContainsCredentials === false &&
    localExpansion.publicRepoContainsProviderIds === false &&
    localExpansion.publicRepoContainsScreenshots === false &&
    localExpansion.publicRepoContainsFeedbackIdentities === false);

const cohortSizeReady =
  localExpansionPresent &&
  localExpansion.targetCohortSize >= 2 &&
  localExpansion.targetCohortSize <= 10 &&
  localExpansion.approvedTesterCount >= localExpansion.targetCohortSize;

const expansionGo =
  localExpansionPresent &&
  localExpansionErrors.length === 0 &&
  localExpansion.t10auFirstSmokeGo === true &&
  localExpansion.firstTesterSmokePassedPrivately === true &&
  localExpansion.cohortSizeWithinLimit === true &&
  localExpansion.privateAccountsPreparedForCohort === true &&
  localExpansion.privateOneToOneShareChannelsReady === true &&
  localExpansion.supportCapacityReadyPrivately === true &&
  localExpansion.revocationPathReadyPrivately === true &&
  localExpansion.renewalCadenceScheduled === true &&
  localExpansion.feedbackIntakeReadyPrivately === true &&
  localExpansion.redactedFeedbackPolicyReady === true &&
  localExpansion.cohortExpansionApprovedPrivately === true &&
  localExpansion.testerUrlsSharedPrivately === false &&
  cohortSizeReady &&
  localExpansion.supportOwnerCount > 0 &&
  localExpansion.failedCheckCount === 0 &&
  noPublicLeak;

const result = localExpansionPresent
  ? expansionGo
    ? "GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10auDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleExpansion, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10av",
  result,
  provider: "Cloudflare",
  t10auFirstSmokeGateReady: t10auDoc.includes("GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK"),
  cohortExpansionDocReady:
    doc.includes("T10av Private Tester Cohort Expansion Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK") &&
    doc.includes("T10aw_private_tester_feedback_intake_gate"),
  localCohortExpansionIgnored: gitignore.includes("tester-cohort-expansion.local.json"),
  localExpansionPresent,
  localExpansionErrors,
  localExpansionSafe: localExpansionPresent ? localExpansionErrors.length === 0 : false,
  exampleExpansionSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerUrlsSharedPrivately: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  feedbackIdentitiesCommitted: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:tester-cohort-expansion-gate"] === "node scripts/tester-cohort-expansion-gate-proof.mjs",
  governanceUpdated: governance.includes("T10av - Private Tester Cohort Expansion Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10av: private tester cohort expansion gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10av prepara el gate de expansion privada a micro-cohorte tester"),
  changelogUpdated: changelog.includes("T10av Private Tester Cohort Expansion Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-cohort-expansion-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10aw_private_tester_feedback_intake_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10auFirstSmokeGateReady ||
  !proof.cohortExpansionDocReady ||
  !proof.localCohortExpansionIgnored ||
  proof.localExpansionErrors.length > 0 ||
  !proof.exampleExpansionSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerUrlsSharedPrivately ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
  proof.feedbackIdentitiesCommitted ||
  !proof.wranglerWorkersDevSafeDefault ||
  !proof.wranglerPreviewUrlsDisabled ||
  !proof.wranglerHasNoRoutesCommitted ||
  !proof.directDeployScriptAbsent ||
  !proof.packageScriptReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  !proof.readmeUpdated ||
  !proof.changelogUpdated ||
  !proof.templateReadmeUpdated ||
  !proof.noSensitiveCloudflareEnvCommitted
) {
  process.exitCode = 1;
}
