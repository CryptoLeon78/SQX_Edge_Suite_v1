import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localTriagePath = join(projectRoot, "tester-feedback-triage.local.json");

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
  "t10awFeedbackIntakeGo",
  "privateFeedbackEvidenceReady",
  "rawFeedbackKeptOutsideGit",
  "triageBucketsReviewed",
  "severityAssignedPrivately",
  "actionCandidatesCreatedPrivately",
  "publicSafeActionSummaryReady",
  "blockingBugsSeparatedPrivately",
  "supportIssuesSeparatedPrivately",
  "commercialThemesSeparatedPrivately",
  "onboardingThemesSeparatedPrivately",
  "uiThemesSeparatedPrivately",
  "performanceThemesSeparatedPrivately",
  "feedbackTriageApprovedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
  "publicRepoContainsRawFeedback",
  "publicRepoContainsFeedbackIdentities",
  "publicRepoContainsPrivateBugDetails",
]);

const countFields = new Set([
  "triagedThemeCount",
  "p0ThemeCount",
  "p1ThemeCount",
  "p2ThemeCount",
  "actionCandidateCount",
  "failedCheckCount",
]);
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
  /private[_-]?bug/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateTriage(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["feedback triage evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10ax") {
        errors.push("phase must be T10ax");
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
const exampleTriage = parseJson(readProject("tester-feedback-triage.example.json"), "tester-feedback-triage.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AX_PRIVATE_TESTER_FEEDBACK_TRIAGE_GATE.md");
const t10awDoc = readRepo("docs/T10AW_PRIVATE_TESTER_FEEDBACK_INTAKE_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localTriagePresent = existsSync(localTriagePath);
const localTriage = localTriagePresent
  ? parseJson(readFileSync(localTriagePath, "utf8"), "tester-feedback-triage.local.json")
  : null;
const localTriageErrors = localTriagePresent ? validateTriage(localTriage) : [];

const exampleTriageSafe =
  exampleTriage.phase === "T10ax" &&
  validateTriage(exampleTriage).length === 0 &&
  [...booleanFields].every((key) => exampleTriage[key] === false) &&
  [...countFields].every((key) => exampleTriage[key] === 0);

const noPublicLeak =
  !localTriagePresent ||
  (localTriage.publicRepoContainsTesterEmails === false &&
    localTriage.publicRepoContainsTesterUrl === false &&
    localTriage.publicRepoContainsCredentials === false &&
    localTriage.publicRepoContainsProviderIds === false &&
    localTriage.publicRepoContainsScreenshots === false &&
    localTriage.publicRepoContainsRawFeedback === false &&
    localTriage.publicRepoContainsFeedbackIdentities === false &&
    localTriage.publicRepoContainsPrivateBugDetails === false);

const triageGo =
  localTriagePresent &&
  localTriageErrors.length === 0 &&
  localTriage.t10awFeedbackIntakeGo === true &&
  localTriage.privateFeedbackEvidenceReady === true &&
  localTriage.rawFeedbackKeptOutsideGit === true &&
  localTriage.triageBucketsReviewed === true &&
  localTriage.severityAssignedPrivately === true &&
  localTriage.actionCandidatesCreatedPrivately === true &&
  localTriage.publicSafeActionSummaryReady === true &&
  localTriage.blockingBugsSeparatedPrivately === true &&
  localTriage.supportIssuesSeparatedPrivately === true &&
  localTriage.commercialThemesSeparatedPrivately === true &&
  localTriage.onboardingThemesSeparatedPrivately === true &&
  localTriage.uiThemesSeparatedPrivately === true &&
  localTriage.performanceThemesSeparatedPrivately === true &&
  localTriage.feedbackTriageApprovedPrivately === true &&
  localTriage.triagedThemeCount > 0 &&
  localTriage.actionCandidateCount > 0 &&
  localTriage.failedCheckCount === 0 &&
  noPublicLeak;

const result = localTriagePresent
  ? triageGo
    ? "GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10awDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleTriage, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10ax",
  result,
  provider: "Cloudflare",
  t10awFeedbackIntakeGateReady: t10awDoc.includes("GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK"),
  feedbackTriageDocReady:
    doc.includes("T10ax Private Tester Feedback Triage Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK") &&
    doc.includes("T10ay_private_tester_action_plan_gate"),
  localFeedbackTriageIgnored: gitignore.includes("tester-feedback-triage.local.json"),
  localTriagePresent,
  localTriageErrors,
  localTriageSafe: localTriagePresent ? localTriageErrors.length === 0 : false,
  exampleTriageSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  rawFeedbackCommitted: false,
  feedbackIdentitiesCommitted: false,
  privateBugDetailsCommitted: false,
  wranglerWorkersDevProtectedTargetEnabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-feedback-triage-gate"] === "node scripts/tester-feedback-triage-gate-proof.mjs",
  governanceUpdated: governance.includes("T10ax - Private Tester Feedback Triage Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ax: private tester feedback triage gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10ax prepara triage privado de feedback tester"),
  changelogUpdated: changelog.includes("T10ax Private Tester Feedback Triage Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-feedback-triage-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10ay_private_tester_action_plan_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10awFeedbackIntakeGateReady ||
  !proof.feedbackTriageDocReady ||
  !proof.localFeedbackTriageIgnored ||
  proof.localTriageErrors.length > 0 ||
  !proof.exampleTriageSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
  proof.rawFeedbackCommitted ||
  proof.feedbackIdentitiesCommitted ||
  proof.privateBugDetailsCommitted ||
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
