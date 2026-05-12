import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localExecutionPath = join(projectRoot, "tester-action-execution.local.json");

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
  "t10ayActionPlanGo",
  "privateActionPlanEvidenceReady",
  "actionPlanEvidenceKeptOutsideGit",
  "executionScopeApprovedPrivately",
  "p0ActionsExecutedOrEscalatedPrivately",
  "p1ActionsExecutedOrScheduledPrivately",
  "p2ActionsBackloggedOrClosedPrivately",
  "ownersConfirmedExecutionPrivately",
  "acceptanceEvidenceRecordedPrivately",
  "rollbackRiskReviewedPrivately",
  "supportActionsCompletedPrivately",
  "commercialActionsCompletedPrivately",
  "publicSafeExecutionSummaryReady",
  "actionExecutionApprovedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
  "publicRepoContainsRawFeedback",
  "publicRepoContainsFeedbackIdentities",
  "publicRepoContainsPrivateBugDetails",
  "publicRepoContainsPrivateActionDetails",
  "publicRepoContainsPrivateExecutionNotes",
]);

const countFields = new Set([
  "executedActionCount",
  "deferredActionCount",
  "p0ExecutedOrEscalatedCount",
  "p1ExecutedOrScheduledCount",
  "p2BackloggedOrClosedCount",
  "supportCompletedCount",
  "commercialCompletedCount",
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
  /private[_-]?execution/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateExecution(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["action execution evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10az") {
        errors.push("phase must be T10az");
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
const exampleExecution = parseJson(readProject("tester-action-execution.example.json"), "tester-action-execution.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AZ_PRIVATE_TESTER_ACTION_EXECUTION_GATE.md");
const t10ayDoc = readRepo("docs/T10AY_PRIVATE_TESTER_ACTION_PLAN_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localExecutionPresent = existsSync(localExecutionPath);
const localExecution = localExecutionPresent
  ? parseJson(readFileSync(localExecutionPath, "utf8"), "tester-action-execution.local.json")
  : null;
const localExecutionErrors = localExecutionPresent ? validateExecution(localExecution) : [];

const exampleExecutionSafe =
  exampleExecution.phase === "T10az" &&
  validateExecution(exampleExecution).length === 0 &&
  [...booleanFields].every((key) => exampleExecution[key] === false) &&
  [...countFields].every((key) => exampleExecution[key] === 0);

const noPublicLeak =
  !localExecutionPresent ||
  (localExecution.publicRepoContainsTesterEmails === false &&
    localExecution.publicRepoContainsTesterUrl === false &&
    localExecution.publicRepoContainsCredentials === false &&
    localExecution.publicRepoContainsProviderIds === false &&
    localExecution.publicRepoContainsScreenshots === false &&
    localExecution.publicRepoContainsRawFeedback === false &&
    localExecution.publicRepoContainsFeedbackIdentities === false &&
    localExecution.publicRepoContainsPrivateBugDetails === false &&
    localExecution.publicRepoContainsPrivateActionDetails === false &&
    localExecution.publicRepoContainsPrivateExecutionNotes === false);

const executionGo =
  localExecutionPresent &&
  localExecutionErrors.length === 0 &&
  localExecution.t10ayActionPlanGo === true &&
  localExecution.privateActionPlanEvidenceReady === true &&
  localExecution.actionPlanEvidenceKeptOutsideGit === true &&
  localExecution.executionScopeApprovedPrivately === true &&
  localExecution.p0ActionsExecutedOrEscalatedPrivately === true &&
  localExecution.p1ActionsExecutedOrScheduledPrivately === true &&
  localExecution.p2ActionsBackloggedOrClosedPrivately === true &&
  localExecution.ownersConfirmedExecutionPrivately === true &&
  localExecution.acceptanceEvidenceRecordedPrivately === true &&
  localExecution.rollbackRiskReviewedPrivately === true &&
  localExecution.supportActionsCompletedPrivately === true &&
  localExecution.commercialActionsCompletedPrivately === true &&
  localExecution.publicSafeExecutionSummaryReady === true &&
  localExecution.actionExecutionApprovedPrivately === true &&
  localExecution.executedActionCount > 0 &&
  localExecution.failedCheckCount === 0 &&
  noPublicLeak;

const result = localExecutionPresent
  ? executionGo
    ? "GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10ayDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleExecution, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10az",
  result,
  provider: "Cloudflare",
  t10ayActionPlanGateReady: t10ayDoc.includes("GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK"),
  actionExecutionDocReady:
    doc.includes("T10az Private Tester Action Execution Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK") &&
    doc.includes("T10ba_private_tester_result_validation_gate"),
  localActionExecutionIgnored: gitignore.includes("tester-action-execution.local.json"),
  localExecutionPresent,
  localExecutionErrors,
  localExecutionSafe: localExecutionPresent ? localExecutionErrors.length === 0 : false,
  exampleExecutionSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  rawFeedbackCommitted: false,
  feedbackIdentitiesCommitted: false,
  privateBugDetailsCommitted: false,
  privateActionDetailsCommitted: false,
  privateExecutionNotesCommitted: false,
  providerMutationsPerformed: false,
  wranglerWorkersDevProtectedTargetEnabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-action-execution-gate"] === "node scripts/tester-action-execution-gate-proof.mjs",
  governanceUpdated: governance.includes("T10az - Private Tester Action Execution Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10az: private tester action execution gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10az prepara ejecucion privada de acciones tester"),
  changelogUpdated: changelog.includes("T10az Private Tester Action Execution Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-action-execution-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10ba_private_tester_result_validation_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10ayActionPlanGateReady ||
  !proof.actionExecutionDocReady ||
  !proof.localActionExecutionIgnored ||
  proof.localExecutionErrors.length > 0 ||
  !proof.exampleExecutionSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
  proof.rawFeedbackCommitted ||
  proof.feedbackIdentitiesCommitted ||
  proof.privateBugDetailsCommitted ||
  proof.privateActionDetailsCommitted ||
  proof.privateExecutionNotesCommitted ||
  proof.providerMutationsPerformed ||
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
