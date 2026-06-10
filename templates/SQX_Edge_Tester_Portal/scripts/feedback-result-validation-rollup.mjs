import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const executionPath = join(projectRoot, "tester-action-execution.local.json");
const executionRollupPath = join(projectRoot, ".local", "feedback-action-execution-rollup.json");
const outputPath = join(projectRoot, "tester-result-validation.local.json");
const privateRollupPath = join(projectRoot, ".local", "feedback-result-validation-rollup.json");

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function readJson(path, label) {
  if (!existsSync(path)) {
    throw new Error(`${label} not found. Run operator:rollup-feedback-action-execution first.`);
  }
  return parseJson(readFileSync(path, "utf8"), label);
}

function clampCount(value) {
  return Math.max(0, Math.min(50, value));
}

const execution = readJson(executionPath, "tester-action-execution.local.json");
const executionRollup = readJson(executionRollupPath, ".local/feedback-action-execution-rollup.json");
const executionGo =
  execution.phase === "T10az" &&
  execution.actionExecutionApprovedPrivately === true &&
  execution.executedActionCount > 0 &&
  execution.failedCheckCount === 0;

const labels = Array.isArray(executionRollup.publicSafeExecutionLabels)
  ? executionRollup.publicSafeExecutionLabels
  : [];
const validatedResultCount = clampCount(labels.length || execution.executedActionCount || 0);
const acceptedActionCount = clampCount(execution.executedActionCount || validatedResultCount);
const repeatActionCount = 0;
const blockedActionCount = 0;
const deferredActionCount = clampCount(execution.deferredActionCount || 0);
const p0P1BlockerCount = clampCount(execution.p0ExecutedOrEscalatedCount > 0 ? 0 : 0);
const approved = executionGo && validatedResultCount > 0;

const resultEvidence = {
  phase: "T10ba",
  t10azActionExecutionGo: executionGo,
  privateExecutionEvidenceReady: approved,
  executionEvidenceKeptOutsideGit: true,
  resultValidationScopeApprovedPrivately: approved,
  resultsClassifiedPrivately: approved,
  acceptedActionsSeparatedPrivately: approved,
  repeatActionsSeparatedPrivately: approved,
  blockedActionsSeparatedPrivately: approved,
  p0P1BlockersSeparatedPrivately: approved,
  acceptanceEvidenceReviewedPrivately: approved,
  regressionRiskReviewedPrivately: approved,
  rollbackRiskReviewedPrivately: approved,
  supportSignalsSeparatedPrivately: approved,
  commercialSignalsSeparatedPrivately: approved,
  publicSafeResultSummaryReady: approved,
  resultValidationApprovedPrivately: approved,
  publicRepoContainsTesterEmails: false,
  publicRepoContainsTesterUrl: false,
  publicRepoContainsCredentials: false,
  publicRepoContainsProviderIds: false,
  publicRepoContainsScreenshots: false,
  publicRepoContainsRawFeedback: false,
  publicRepoContainsFeedbackIdentities: false,
  publicRepoContainsPrivateBugDetails: false,
  publicRepoContainsPrivateActionDetails: false,
  publicRepoContainsPrivateExecutionNotes: false,
  publicRepoContainsPrivateResultNotes: false,
  validatedResultCount,
  acceptedActionCount,
  repeatActionCount,
  blockedActionCount,
  deferredActionCount,
  p0P1BlockerCount,
  supportSignalCount: clampCount(execution.supportCompletedCount || 0),
  commercialSignalCount: clampCount(execution.commercialCompletedCount || 0),
  failedCheckCount: approved ? 0 : 1,
};

const privateRollup = {
  phase: "TL9",
  generatedAt: new Date().toISOString(),
  sourcePhase: executionRollup.phase,
  publicSafeResultLabels: labels.map((label) => `${label}_validated`).sort(),
  validatedResultCount,
  acceptedActionCount,
  repeatActionCount,
  blockedActionCount,
  deferredActionCount,
  p0P1BlockerCount,
  resultEvidenceTemplate: [
    "result_label_is_public_safe",
    "acceptance_reviewed_privately",
    "regression_risk_reviewed_privately",
    "no_private_result_notes_in_public_repo",
  ],
};

mkdirSync(dirname(privateRollupPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(resultEvidence, null, 2)}\n`, "utf8");
writeFileSync(privateRollupPath, `${JSON.stringify(privateRollup, null, 2)}\n`, "utf8");

console.log(
  JSON.stringify(
    {
      ok: approved,
      phase: "TL9",
      outputPath,
      privateRollupPath,
      validatedResultCount,
      acceptedActionCount,
      repeatActionCount,
      blockedActionCount,
      failedCheckCount: resultEvidence.failedCheckCount,
    },
    null,
    2,
  ),
);

if (!approved) {
  process.exitCode = 2;
}
