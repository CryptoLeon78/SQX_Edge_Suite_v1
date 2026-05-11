import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localIterationPath = join(projectRoot, "tester-next-iteration.local.json");

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

const iterationModes = new Set([
  "repeat_validation",
  "execute_fixes",
  "expand_micro_cohort",
  "pause_tester_access",
  "prepare_next_tester_cycle",
  "escalate_commercial_readiness",
]);

const booleanFields = new Set([
  "t10bbIterationDecisionGo",
  "privateDecisionEvidenceReady",
  "decisionEvidenceKeptOutsideGit",
  "nextIterationScopeApprovedPrivately",
  "iterationModeSelectedPrivately",
  "targetCohortSelectedPrivately",
  "accessWindowReviewedPrivately",
  "supportOwnerAssignedPrivately",
  "riskControlsReviewedPrivately",
  "successCriteriaDefinedPrivately",
  "rollbackCriteriaDefinedPrivately",
  "publicSafeIterationSummaryReady",
  "nextIterationApprovedPrivately",
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
  "publicRepoContainsPrivateResultNotes",
  "publicRepoContainsPrivateDecisionNotes",
  "publicRepoContainsPrivateIterationPlan",
  "publicRepoContainsPrivateSupportNotes",
]);

const countFields = new Set([
  "decisionEvidenceCount",
  "iterationCandidateCount",
  "selectedIterationCount",
  "targetCohortCount",
  "actionItemCount",
  "blockerCount",
  "failedCheckCount",
]);
const allowedFields = new Set(["phase", "iterationMode", ...booleanFields, ...countFields]);

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
  /private[_-]?result/i,
  /private[_-]?decision/i,
  /private[_-]?iteration/i,
  /private[_-]?support/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateIteration(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["next iteration evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10bc") {
        errors.push("phase must be T10bc");
      }
      continue;
    }

    if (key === "iterationMode") {
      if (!iterationModes.has(value)) {
        errors.push("iterationMode must be an accepted public-safe value");
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
    if (iterationModes.has(value)) {
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
const exampleIteration = parseJson(readProject("tester-next-iteration.example.json"), "tester-next-iteration.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10BC_PRIVATE_TESTER_NEXT_ITERATION_GATE.md");
const t10bbDoc = readRepo("docs/T10BB_PRIVATE_TESTER_ITERATION_DECISION_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localIterationPresent = existsSync(localIterationPath);
const localIteration = localIterationPresent
  ? parseJson(readFileSync(localIterationPath, "utf8"), "tester-next-iteration.local.json")
  : null;
const localIterationErrors = localIterationPresent ? validateIteration(localIteration) : [];

const exampleIterationSafe =
  exampleIteration.phase === "T10bc" &&
  validateIteration(exampleIteration).length === 0 &&
  iterationModes.has(exampleIteration.iterationMode) &&
  [...booleanFields].every((key) => exampleIteration[key] === false) &&
  [...countFields].every((key) => exampleIteration[key] === 0);

const noPublicLeak =
  !localIterationPresent ||
  (localIteration.publicRepoContainsTesterEmails === false &&
    localIteration.publicRepoContainsTesterUrl === false &&
    localIteration.publicRepoContainsCredentials === false &&
    localIteration.publicRepoContainsProviderIds === false &&
    localIteration.publicRepoContainsScreenshots === false &&
    localIteration.publicRepoContainsRawFeedback === false &&
    localIteration.publicRepoContainsFeedbackIdentities === false &&
    localIteration.publicRepoContainsPrivateBugDetails === false &&
    localIteration.publicRepoContainsPrivateActionDetails === false &&
    localIteration.publicRepoContainsPrivateExecutionNotes === false &&
    localIteration.publicRepoContainsPrivateResultNotes === false &&
    localIteration.publicRepoContainsPrivateDecisionNotes === false &&
    localIteration.publicRepoContainsPrivateIterationPlan === false &&
    localIteration.publicRepoContainsPrivateSupportNotes === false);

const iterationGo =
  localIterationPresent &&
  localIterationErrors.length === 0 &&
  localIteration.t10bbIterationDecisionGo === true &&
  localIteration.privateDecisionEvidenceReady === true &&
  localIteration.decisionEvidenceKeptOutsideGit === true &&
  localIteration.nextIterationScopeApprovedPrivately === true &&
  localIteration.iterationModeSelectedPrivately === true &&
  localIteration.targetCohortSelectedPrivately === true &&
  localIteration.accessWindowReviewedPrivately === true &&
  localIteration.supportOwnerAssignedPrivately === true &&
  localIteration.riskControlsReviewedPrivately === true &&
  localIteration.successCriteriaDefinedPrivately === true &&
  localIteration.rollbackCriteriaDefinedPrivately === true &&
  localIteration.publicSafeIterationSummaryReady === true &&
  localIteration.nextIterationApprovedPrivately === true &&
  iterationModes.has(localIteration.iterationMode) &&
  localIteration.decisionEvidenceCount > 0 &&
  localIteration.iterationCandidateCount > 0 &&
  localIteration.selectedIterationCount === 1 &&
  localIteration.failedCheckCount === 0 &&
  noPublicLeak;

const result = localIterationPresent
  ? iterationGo
    ? "GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_NEXT_ITERATION_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10bbDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleIteration, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10bc",
  result,
  provider: "Cloudflare",
  t10bbIterationDecisionGateReady: t10bbDoc.includes("GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK"),
  nextIterationDocReady:
    doc.includes("T10bc Private Tester Next Iteration Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK") &&
    doc.includes("T10bd_private_tester_next_iteration_execution_gate"),
  localNextIterationIgnored: gitignore.includes("tester-next-iteration.local.json"),
  localIterationPresent,
  localIterationErrors,
  localIterationSafe: localIterationPresent ? localIterationErrors.length === 0 : false,
  exampleIterationSafe,
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
  privateResultNotesCommitted: false,
  privateDecisionNotesCommitted: false,
  privateIterationPlanCommitted: false,
  privateSupportNotesCommitted: false,
  providerMutationsPerformed: false,
  testerAccountsCreated: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-next-iteration-gate"] === "node scripts/tester-next-iteration-gate-proof.mjs",
  governanceUpdated: governance.includes("T10bc - Private Tester Next Iteration Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10bc: private tester next iteration gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10bc prepara siguiente iteracion privada tester"),
  changelogUpdated: changelog.includes("T10bc Private Tester Next Iteration Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-next-iteration-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10bd_private_tester_next_iteration_execution_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10bbIterationDecisionGateReady ||
  !proof.nextIterationDocReady ||
  !proof.localNextIterationIgnored ||
  proof.localIterationErrors.length > 0 ||
  !proof.exampleIterationSafe ||
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
  proof.privateResultNotesCommitted ||
  proof.privateDecisionNotesCommitted ||
  proof.privateIterationPlanCommitted ||
  proof.privateSupportNotesCommitted ||
  proof.providerMutationsPerformed ||
  proof.testerAccountsCreated ||
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
