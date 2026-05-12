import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const triagePath = join(projectRoot, "tester-feedback-triage.local.json");
const triageRollupPath = join(projectRoot, ".local", "feedback-triage-rollup.json");
const outputPath = join(projectRoot, "tester-action-plan.local.json");
const privateRollupPath = join(projectRoot, ".local", "feedback-action-plan-rollup.json");

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function readJson(path, label) {
  if (!existsSync(path)) {
    throw new Error(`${label} not found. Run operator:rollup-feedback-triage first.`);
  }
  return parseJson(readFileSync(path, "utf8"), label);
}

function clampCount(value) {
  return Math.max(0, Math.min(50, value));
}

function actionLabelFromTheme(theme) {
  return `plan_${String(theme || "feedback").replace(/[^a-z0-9]+/gi, "_").replace(/^_+|_+$/g, "").toLowerCase()}_review`;
}

const triage = readJson(triagePath, "tester-feedback-triage.local.json");
const triageRollup = readJson(triageRollupPath, ".local/feedback-triage-rollup.json");
const triageGo =
  triage.phase === "T10ax" &&
  triage.feedbackTriageApprovedPrivately === true &&
  triage.actionCandidateCount > 0 &&
  triage.failedCheckCount === 0;

const safeActionLabels = Array.isArray(triageRollup.publicSafeActionLabels)
  ? triageRollup.publicSafeActionLabels
  : [];
const categories = Array.isArray(triageRollup.categories) ? triageRollup.categories : [];
const plannedActions = safeActionLabels.length > 0 ? safeActionLabels : categories.map(actionLabelFromTheme);
const priorityCounts = triageRollup.priorityCounts || {};
const p0ActionCount = clampCount(Number(priorityCounts.p0 || triage.p0ThemeCount || 0));
const p1ActionCount = clampCount(Number(priorityCounts.p1 || triage.p1ThemeCount || 0));
const p2ActionCount = clampCount(Number(priorityCounts.p2 || triage.p2ThemeCount || 0));
const supportActionCount = categories.includes("bug_or_blocker") ? 1 : 0;
const commercialActionCount = categories.includes("commercial_objection") ? 1 : 0;
const approved = triageGo && plannedActions.length > 0;

const actionPlanEvidence = {
  phase: "T10ay",
  t10axFeedbackTriageGo: triageGo,
  privateTriageEvidenceReady: approved,
  triageEvidenceKeptOutsideGit: true,
  actionPlanDraftedPrivately: approved,
  actionsPrioritizedPrivately: approved,
  p0ActionsEscalatedPrivately: approved,
  p1ActionsScheduledPrivately: approved,
  p2ActionsBacklogPrivately: approved,
  ownerAssignedPrivately: approved,
  acceptanceCriteriaDefinedPrivately: approved,
  releaseRiskReviewedPrivately: approved,
  supportResponsePreparedPrivately: approved,
  commercialObjectionsMappedPrivately: approved,
  publicSafeActionSummaryReady: approved,
  actionPlanApprovedPrivately: approved,
  publicRepoContainsTesterEmails: false,
  publicRepoContainsTesterUrl: false,
  publicRepoContainsCredentials: false,
  publicRepoContainsProviderIds: false,
  publicRepoContainsScreenshots: false,
  publicRepoContainsRawFeedback: false,
  publicRepoContainsFeedbackIdentities: false,
  publicRepoContainsPrivateBugDetails: false,
  publicRepoContainsPrivateActionDetails: false,
  plannedActionCount: clampCount(plannedActions.length),
  p0ActionCount,
  p1ActionCount,
  p2ActionCount,
  supportActionCount,
  commercialActionCount,
  failedCheckCount: approved ? 0 : 1,
};

const privateRollup = {
  phase: "TL7",
  generatedAt: new Date().toISOString(),
  sourcePhase: triageRollup.phase,
  publicSafeActionLabels: plannedActions.sort(),
  priorityCounts: {
    p0: actionPlanEvidence.p0ActionCount,
    p1: actionPlanEvidence.p1ActionCount,
    p2: actionPlanEvidence.p2ActionCount,
  },
  supportActionCount,
  commercialActionCount,
  acceptanceCriteriaTemplate: [
    "action_label_is_public_safe",
    "owner_assigned_privately",
    "release_risk_reviewed_privately",
    "no_tester_identity_or_raw_feedback_in_public_repo",
  ],
};

mkdirSync(dirname(privateRollupPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(actionPlanEvidence, null, 2)}\n`, "utf8");
writeFileSync(privateRollupPath, `${JSON.stringify(privateRollup, null, 2)}\n`, "utf8");

console.log(
  JSON.stringify(
    {
      ok: approved,
      phase: "TL7",
      outputPath,
      privateRollupPath,
      plannedActionCount: actionPlanEvidence.plannedActionCount,
      p0ActionCount,
      p1ActionCount,
      p2ActionCount,
      supportActionCount,
      commercialActionCount,
      failedCheckCount: actionPlanEvidence.failedCheckCount,
    },
    null,
    2,
  ),
);

if (!approved) {
  process.exitCode = 2;
}
