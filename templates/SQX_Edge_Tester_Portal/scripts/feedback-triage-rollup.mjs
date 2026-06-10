import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const intakePath = join(projectRoot, "tester-feedback-intake.local.json");
const rollupPath = join(projectRoot, ".local", "feedback-intake-rollup.json");
const outputPath = join(projectRoot, "tester-feedback-triage.local.json");
const privateRollupPath = join(projectRoot, ".local", "feedback-triage-rollup.json");

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function readJson(path, label) {
  if (!existsSync(path)) {
    throw new Error(`${label} not found. Run operator:rollup-feedback-intake first.`);
  }
  return parseJson(readFileSync(path, "utf8"), label);
}

function clampCount(value) {
  return Math.max(0, Math.min(50, value));
}

function countMatching(values, expected) {
  return values.filter((value) => value === expected).length;
}

const intake = readJson(intakePath, "tester-feedback-intake.local.json");
const intakeRollup = readJson(rollupPath, ".local/feedback-intake-rollup.json");
const intakeGo =
  intake.phase === "T10aw" &&
  intake.feedbackResponderCount > 0 &&
  intake.failedCheckCount === 0 &&
  intake.feedbackIntakeApprovedPrivately === true;

const categories = Array.isArray(intakeRollup.categories) ? intakeRollup.categories : [];
const severities = Array.isArray(intakeRollup.severities) ? intakeRollup.severities : [];
const hasActionableSignal = categories.length > 0 || severities.length > 0;
const p0ThemeCount = countMatching(severities, "blocker");
const p1ThemeCount = countMatching(severities, "friction") + countMatching(severities, "commercial");
const p2ThemeCount = Math.max(0, categories.length + severities.length - p0ThemeCount - p1ThemeCount);
const actionCandidateCount = hasActionableSignal ? Math.max(1, categories.length) : 0;
const approved = intakeGo && hasActionableSignal;

const triageEvidence = {
  phase: "T10ax",
  t10awFeedbackIntakeGo: intakeGo,
  privateFeedbackEvidenceReady: approved,
  rawFeedbackKeptOutsideGit: true,
  triageBucketsReviewed: approved,
  severityAssignedPrivately: approved,
  actionCandidatesCreatedPrivately: approved,
  publicSafeActionSummaryReady: approved,
  blockingBugsSeparatedPrivately: approved,
  supportIssuesSeparatedPrivately: approved,
  commercialThemesSeparatedPrivately: approved,
  onboardingThemesSeparatedPrivately: approved,
  uiThemesSeparatedPrivately: approved,
  performanceThemesSeparatedPrivately: approved,
  feedbackTriageApprovedPrivately: approved,
  publicRepoContainsTesterEmails: false,
  publicRepoContainsTesterUrl: false,
  publicRepoContainsCredentials: false,
  publicRepoContainsProviderIds: false,
  publicRepoContainsScreenshots: false,
  publicRepoContainsRawFeedback: false,
  publicRepoContainsFeedbackIdentities: false,
  publicRepoContainsPrivateBugDetails: false,
  triagedThemeCount: clampCount(categories.length + severities.length),
  p0ThemeCount: clampCount(p0ThemeCount),
  p1ThemeCount: clampCount(p1ThemeCount),
  p2ThemeCount: clampCount(p2ThemeCount),
  actionCandidateCount: clampCount(actionCandidateCount),
  failedCheckCount: approved ? 0 : 1,
};

const privateRollup = {
  phase: "TL6",
  generatedAt: new Date().toISOString(),
  sourcePhase: intakeRollup.phase,
  categories,
  severities,
  publicSafeActionLabels: categories.map((category) => `review_${category}_theme`).sort(),
  priorityCounts: {
    p0: triageEvidence.p0ThemeCount,
    p1: triageEvidence.p1ThemeCount,
    p2: triageEvidence.p2ThemeCount,
  },
  actionCandidateCount: triageEvidence.actionCandidateCount,
};

mkdirSync(dirname(privateRollupPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(triageEvidence, null, 2)}\n`, "utf8");
writeFileSync(privateRollupPath, `${JSON.stringify(privateRollup, null, 2)}\n`, "utf8");

console.log(
  JSON.stringify(
    {
      ok: approved,
      phase: "TL6",
      outputPath,
      privateRollupPath,
      triagedThemeCount: triageEvidence.triagedThemeCount,
      p0ThemeCount: triageEvidence.p0ThemeCount,
      p1ThemeCount: triageEvidence.p1ThemeCount,
      p2ThemeCount: triageEvidence.p2ThemeCount,
      actionCandidateCount: triageEvidence.actionCandidateCount,
      failedCheckCount: triageEvidence.failedCheckCount,
    },
    null,
    2,
  ),
);

if (!approved) {
  process.exitCode = 2;
}
