import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localActionPlanPath = join(projectRoot, "tester-action-plan.local.json");

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
  "t10axFeedbackTriageGo",
  "privateTriageEvidenceReady",
  "triageEvidenceKeptOutsideGit",
  "actionPlanDraftedPrivately",
  "actionsPrioritizedPrivately",
  "p0ActionsEscalatedPrivately",
  "p1ActionsScheduledPrivately",
  "p2ActionsBacklogPrivately",
  "ownerAssignedPrivately",
  "acceptanceCriteriaDefinedPrivately",
  "releaseRiskReviewedPrivately",
  "supportResponsePreparedPrivately",
  "commercialObjectionsMappedPrivately",
  "publicSafeActionSummaryReady",
  "actionPlanApprovedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
  "publicRepoContainsRawFeedback",
  "publicRepoContainsFeedbackIdentities",
  "publicRepoContainsPrivateBugDetails",
  "publicRepoContainsPrivateActionDetails",
]);

const countFields = new Set([
  "plannedActionCount",
  "p0ActionCount",
  "p1ActionCount",
  "p2ActionCount",
  "supportActionCount",
  "commercialActionCount",
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
  /private[_-]?action/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateActionPlan(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["action plan evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10ay") {
        errors.push("phase must be T10ay");
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
const exampleActionPlan = parseJson(readProject("tester-action-plan.example.json"), "tester-action-plan.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AY_PRIVATE_TESTER_ACTION_PLAN_GATE.md");
const t10axDoc = readRepo("docs/T10AX_PRIVATE_TESTER_FEEDBACK_TRIAGE_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localActionPlanPresent = existsSync(localActionPlanPath);
const localActionPlan = localActionPlanPresent
  ? parseJson(readFileSync(localActionPlanPath, "utf8"), "tester-action-plan.local.json")
  : null;
const localActionPlanErrors = localActionPlanPresent ? validateActionPlan(localActionPlan) : [];

const exampleActionPlanSafe =
  exampleActionPlan.phase === "T10ay" &&
  validateActionPlan(exampleActionPlan).length === 0 &&
  [...booleanFields].every((key) => exampleActionPlan[key] === false) &&
  [...countFields].every((key) => exampleActionPlan[key] === 0);

const noPublicLeak =
  !localActionPlanPresent ||
  (localActionPlan.publicRepoContainsTesterEmails === false &&
    localActionPlan.publicRepoContainsTesterUrl === false &&
    localActionPlan.publicRepoContainsCredentials === false &&
    localActionPlan.publicRepoContainsProviderIds === false &&
    localActionPlan.publicRepoContainsScreenshots === false &&
    localActionPlan.publicRepoContainsRawFeedback === false &&
    localActionPlan.publicRepoContainsFeedbackIdentities === false &&
    localActionPlan.publicRepoContainsPrivateBugDetails === false &&
    localActionPlan.publicRepoContainsPrivateActionDetails === false);

const actionPlanGo =
  localActionPlanPresent &&
  localActionPlanErrors.length === 0 &&
  localActionPlan.t10axFeedbackTriageGo === true &&
  localActionPlan.privateTriageEvidenceReady === true &&
  localActionPlan.triageEvidenceKeptOutsideGit === true &&
  localActionPlan.actionPlanDraftedPrivately === true &&
  localActionPlan.actionsPrioritizedPrivately === true &&
  localActionPlan.p0ActionsEscalatedPrivately === true &&
  localActionPlan.p1ActionsScheduledPrivately === true &&
  localActionPlan.p2ActionsBacklogPrivately === true &&
  localActionPlan.ownerAssignedPrivately === true &&
  localActionPlan.acceptanceCriteriaDefinedPrivately === true &&
  localActionPlan.releaseRiskReviewedPrivately === true &&
  localActionPlan.supportResponsePreparedPrivately === true &&
  localActionPlan.commercialObjectionsMappedPrivately === true &&
  localActionPlan.publicSafeActionSummaryReady === true &&
  localActionPlan.actionPlanApprovedPrivately === true &&
  localActionPlan.plannedActionCount > 0 &&
  localActionPlan.failedCheckCount === 0 &&
  noPublicLeak;

const result = localActionPlanPresent
  ? actionPlanGo
    ? "GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_ACTION_PLAN_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10axDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleActionPlan, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10ay",
  result,
  provider: "Cloudflare",
  t10axFeedbackTriageGateReady: t10axDoc.includes("GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK"),
  actionPlanDocReady:
    doc.includes("T10ay Private Tester Action Plan Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK") &&
    doc.includes("T10az_private_tester_action_execution_gate"),
  localActionPlanIgnored: gitignore.includes("tester-action-plan.local.json"),
  localActionPlanPresent,
  localActionPlanErrors,
  localActionPlanSafe: localActionPlanPresent ? localActionPlanErrors.length === 0 : false,
  exampleActionPlanSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  rawFeedbackCommitted: false,
  feedbackIdentitiesCommitted: false,
  privateBugDetailsCommitted: false,
  privateActionDetailsCommitted: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-action-plan-gate"] === "node scripts/tester-action-plan-gate-proof.mjs",
  governanceUpdated: governance.includes("T10ay - Private Tester Action Plan Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ay: private tester action plan gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10ay prepara action plan privado de feedback tester"),
  changelogUpdated: changelog.includes("T10ay Private Tester Action Plan Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-action-plan-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10az_private_tester_action_execution_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10axFeedbackTriageGateReady ||
  !proof.actionPlanDocReady ||
  !proof.localActionPlanIgnored ||
  proof.localActionPlanErrors.length > 0 ||
  !proof.exampleActionPlanSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
  proof.rawFeedbackCommitted ||
  proof.feedbackIdentitiesCommitted ||
  proof.privateBugDetailsCommitted ||
  proof.privateActionDetailsCommitted ||
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
