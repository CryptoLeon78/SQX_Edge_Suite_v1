import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localFeedbackPath = join(projectRoot, "tester-feedback-intake.local.json");

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
  "t10avCohortExpansionGo",
  "privateFeedbackChannelReady",
  "rawFeedbackKeptOutsideGit",
  "redactionPolicyReady",
  "publicSafeSummaryPolicyReady",
  "aggregateCountsOnly",
  "onboardingFrictionBucketReady",
  "uiConfusionBucketReady",
  "missingDocsBucketReady",
  "performanceNotesBucketReady",
  "blockingBugsBucketReady",
  "commercialObjectionsBucketReady",
  "supportChannelReadyPrivately",
  "revocationPathReadyPrivately",
  "feedbackIntakeApprovedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
  "publicRepoContainsRawFeedback",
  "publicRepoContainsFeedbackIdentities",
]);

const countFields = new Set(["feedbackResponderCount", "redactedThemeCount", "blockingBugCount", "failedCheckCount"]);
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
  /raw[_-]?feedback/i,
  /tester[_-]?identity/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateFeedback(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["feedback intake evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10aw") {
        errors.push("phase must be T10aw");
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
const exampleFeedback = parseJson(readProject("tester-feedback-intake.example.json"), "tester-feedback-intake.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AW_PRIVATE_TESTER_FEEDBACK_INTAKE_GATE.md");
const t10avDoc = readRepo("docs/T10AV_PRIVATE_TESTER_COHORT_EXPANSION_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localFeedbackPresent = existsSync(localFeedbackPath);
const localFeedback = localFeedbackPresent
  ? parseJson(readFileSync(localFeedbackPath, "utf8"), "tester-feedback-intake.local.json")
  : null;
const localFeedbackErrors = localFeedbackPresent ? validateFeedback(localFeedback) : [];

const exampleFeedbackSafe =
  exampleFeedback.phase === "T10aw" &&
  validateFeedback(exampleFeedback).length === 0 &&
  [...booleanFields].every((key) => exampleFeedback[key] === false) &&
  [...countFields].every((key) => exampleFeedback[key] === 0);

const noPublicLeak =
  !localFeedbackPresent ||
  (localFeedback.publicRepoContainsTesterEmails === false &&
    localFeedback.publicRepoContainsTesterUrl === false &&
    localFeedback.publicRepoContainsCredentials === false &&
    localFeedback.publicRepoContainsProviderIds === false &&
    localFeedback.publicRepoContainsScreenshots === false &&
    localFeedback.publicRepoContainsRawFeedback === false &&
    localFeedback.publicRepoContainsFeedbackIdentities === false);

const feedbackGo =
  localFeedbackPresent &&
  localFeedbackErrors.length === 0 &&
  localFeedback.t10avCohortExpansionGo === true &&
  localFeedback.privateFeedbackChannelReady === true &&
  localFeedback.rawFeedbackKeptOutsideGit === true &&
  localFeedback.redactionPolicyReady === true &&
  localFeedback.publicSafeSummaryPolicyReady === true &&
  localFeedback.aggregateCountsOnly === true &&
  localFeedback.onboardingFrictionBucketReady === true &&
  localFeedback.uiConfusionBucketReady === true &&
  localFeedback.missingDocsBucketReady === true &&
  localFeedback.performanceNotesBucketReady === true &&
  localFeedback.blockingBugsBucketReady === true &&
  localFeedback.commercialObjectionsBucketReady === true &&
  localFeedback.supportChannelReadyPrivately === true &&
  localFeedback.revocationPathReadyPrivately === true &&
  localFeedback.feedbackIntakeApprovedPrivately === true &&
  localFeedback.feedbackResponderCount > 0 &&
  localFeedback.redactedThemeCount >= 0 &&
  localFeedback.failedCheckCount === 0 &&
  noPublicLeak;

const result = localFeedbackPresent
  ? feedbackGo
    ? "GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10avDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleFeedback, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10aw",
  result,
  provider: "Cloudflare",
  t10avCohortExpansionGateReady: t10avDoc.includes("GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK"),
  feedbackIntakeDocReady:
    doc.includes("T10aw Private Tester Feedback Intake Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK") &&
    doc.includes("T10ax_private_tester_feedback_triage_gate"),
  localFeedbackIntakeIgnored: gitignore.includes("tester-feedback-intake.local.json"),
  localFeedbackPresent,
  localFeedbackErrors,
  localFeedbackSafe: localFeedbackPresent ? localFeedbackErrors.length === 0 : false,
  exampleFeedbackSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  rawFeedbackCommitted: false,
  feedbackIdentitiesCommitted: false,
  wranglerWorkersDevProtectedTargetEnabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-feedback-intake-gate"] === "node scripts/tester-feedback-intake-gate-proof.mjs",
  governanceUpdated: governance.includes("T10aw - Private Tester Feedback Intake Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10aw: private tester feedback intake gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10aw prepara intake privado de feedback tester"),
  changelogUpdated: changelog.includes("T10aw Private Tester Feedback Intake Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-feedback-intake-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10ax_private_tester_feedback_triage_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10avCohortExpansionGateReady ||
  !proof.feedbackIntakeDocReady ||
  !proof.localFeedbackIntakeIgnored ||
  proof.localFeedbackErrors.length > 0 ||
  !proof.exampleFeedbackSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
  proof.rawFeedbackCommitted ||
  proof.feedbackIdentitiesCommitted ||
  !proof.wranglerWorkersDevProtectedTargetEnabled ||
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
