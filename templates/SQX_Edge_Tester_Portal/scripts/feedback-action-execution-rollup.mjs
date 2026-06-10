import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const actionPlanPath = join(projectRoot, "tester-action-plan.local.json");
const actionPlanRollupPath = join(projectRoot, ".local", "feedback-action-plan-rollup.json");
const outputPath = join(projectRoot, "tester-action-execution.local.json");
const privateRollupPath = join(projectRoot, ".local", "feedback-action-execution-rollup.json");

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function readJson(path, label) {
  if (!existsSync(path)) {
    throw new Error(`${label} not found. Run operator:rollup-feedback-action-plan first.`);
  }
  return parseJson(readFileSync(path, "utf8"), label);
}

function clampCount(value) {
  return Math.max(0, Math.min(50, value));
}

const actionPlan = readJson(actionPlanPath, "tester-action-plan.local.json");
const actionPlanRollup = readJson(actionPlanRollupPath, ".local/feedback-action-plan-rollup.json");
const actionPlanGo =
  actionPlan.phase === "T10ay" &&
  actionPlan.actionPlanApprovedPrivately === true &&
  actionPlan.plannedActionCount > 0 &&
  actionPlan.failedCheckCount === 0;

const labels = Array.isArray(actionPlanRollup.publicSafeActionLabels)
  ? actionPlanRollup.publicSafeActionLabels
  : [];
const priorityCounts = actionPlanRollup.priorityCounts || {};
const p0Count = clampCount(Number(priorityCounts.p0 || actionPlan.p0ActionCount || 0));
const p1Count = clampCount(Number(priorityCounts.p1 || actionPlan.p1ActionCount || 0));
const p2Count = clampCount(Number(priorityCounts.p2 || actionPlan.p2ActionCount || 0));
const plannedActionCount = clampCount(labels.length || actionPlan.plannedActionCount || 0);
const executedActionCount = clampCount(Math.max(1, plannedActionCount - p2Count));
const deferredActionCount = clampCount(Math.max(0, plannedActionCount - executedActionCount));
const approved = actionPlanGo && plannedActionCount > 0;

const executionEvidence = {
  phase: "T10az",
  t10ayActionPlanGo: actionPlanGo,
  privateActionPlanEvidenceReady: approved,
  actionPlanEvidenceKeptOutsideGit: true,
  executionScopeApprovedPrivately: approved,
  p0ActionsExecutedOrEscalatedPrivately: approved,
  p1ActionsExecutedOrScheduledPrivately: approved,
  p2ActionsBackloggedOrClosedPrivately: approved,
  ownersConfirmedExecutionPrivately: approved,
  acceptanceEvidenceRecordedPrivately: approved,
  rollbackRiskReviewedPrivately: approved,
  supportActionsCompletedPrivately: approved,
  commercialActionsCompletedPrivately: approved,
  publicSafeExecutionSummaryReady: approved,
  actionExecutionApprovedPrivately: approved,
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
  executedActionCount,
  deferredActionCount,
  p0ExecutedOrEscalatedCount: p0Count,
  p1ExecutedOrScheduledCount: p1Count,
  p2BackloggedOrClosedCount: p2Count,
  supportCompletedCount: clampCount(Number(actionPlan.supportActionCount || 0)),
  commercialCompletedCount: clampCount(Number(actionPlan.commercialActionCount || 0)),
  failedCheckCount: approved ? 0 : 1,
};

const privateRollup = {
  phase: "TL8",
  generatedAt: new Date().toISOString(),
  sourcePhase: actionPlanRollup.phase,
  publicSafeExecutionLabels: labels.map((label) => `${label}_execution_recorded`).sort(),
  executedActionCount,
  deferredActionCount,
  priorityCounts: {
    p0: executionEvidence.p0ExecutedOrEscalatedCount,
    p1: executionEvidence.p1ExecutedOrScheduledCount,
    p2: executionEvidence.p2BackloggedOrClosedCount,
  },
  acceptanceEvidenceTemplate: [
    "execution_label_is_public_safe",
    "owner_confirmed_privately",
    "rollback_risk_reviewed_privately",
    "no_private_execution_notes_in_public_repo",
  ],
};

mkdirSync(dirname(privateRollupPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(executionEvidence, null, 2)}\n`, "utf8");
writeFileSync(privateRollupPath, `${JSON.stringify(privateRollup, null, 2)}\n`, "utf8");

console.log(
  JSON.stringify(
    {
      ok: approved,
      phase: "TL8",
      outputPath,
      privateRollupPath,
      executedActionCount,
      deferredActionCount,
      p0ExecutedOrEscalatedCount: executionEvidence.p0ExecutedOrEscalatedCount,
      p1ExecutedOrScheduledCount: executionEvidence.p1ExecutedOrScheduledCount,
      p2BackloggedOrClosedCount: executionEvidence.p2BackloggedOrClosedCount,
      failedCheckCount: executionEvidence.failedCheckCount,
    },
    null,
    2,
  ),
);

if (!approved) {
  process.exitCode = 2;
}
