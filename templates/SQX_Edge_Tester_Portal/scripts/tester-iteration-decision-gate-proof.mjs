import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localDecisionPath = join(projectRoot, "tester-iteration-decision.local.json");

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

const decisionValues = new Set([
  "repeat_validation",
  "execute_fixes",
  "expand_micro_cohort",
  "pause_tester_access",
  "prepare_next_tester_cycle",
  "escalate_commercial_readiness",
]);

const booleanFields = new Set([
  "t10baResultValidationGo",
  "privateResultEvidenceReady",
  "resultEvidenceKeptOutsideGit",
  "decisionScopeApprovedPrivately",
  "decisionSelectedPrivately",
  "p0P1BlockersReviewedPrivately",
  "supportRiskReviewedPrivately",
  "commercialRiskReviewedPrivately",
  "ownerAssignedPrivately",
  "acceptanceCriteriaDefinedPrivately",
  "rollbackRiskReviewedPrivately",
  "nextGateSelectedPrivately",
  "publicSafeDecisionSummaryReady",
  "iterationDecisionApprovedPrivately",
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
]);

const countFields = new Set([
  "validatedResultCount",
  "acceptedActionCount",
  "repeatActionCount",
  "blockedActionCount",
  "decisionCandidateCount",
  "selectedDecisionCount",
  "failedCheckCount",
]);
const allowedFields = new Set(["phase", "decision", ...booleanFields, ...countFields]);

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
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateDecision(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["iteration decision evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10bb") {
        errors.push("phase must be T10bb");
      }
      continue;
    }

    if (key === "decision") {
      if (!decisionValues.has(value)) {
        errors.push("decision must be an accepted public-safe value");
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
    if (decisionValues.has(value)) {
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
const exampleDecision = parseJson(readProject("tester-iteration-decision.example.json"), "tester-iteration-decision.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10BB_PRIVATE_TESTER_ITERATION_DECISION_GATE.md");
const t10baDoc = readRepo("docs/T10BA_PRIVATE_TESTER_RESULT_VALIDATION_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localDecisionPresent = existsSync(localDecisionPath);
const localDecision = localDecisionPresent
  ? parseJson(readFileSync(localDecisionPath, "utf8"), "tester-iteration-decision.local.json")
  : null;
const localDecisionErrors = localDecisionPresent ? validateDecision(localDecision) : [];

const exampleDecisionSafe =
  exampleDecision.phase === "T10bb" &&
  validateDecision(exampleDecision).length === 0 &&
  decisionValues.has(exampleDecision.decision) &&
  [...booleanFields].every((key) => exampleDecision[key] === false) &&
  [...countFields].every((key) => exampleDecision[key] === 0);

const noPublicLeak =
  !localDecisionPresent ||
  (localDecision.publicRepoContainsTesterEmails === false &&
    localDecision.publicRepoContainsTesterUrl === false &&
    localDecision.publicRepoContainsCredentials === false &&
    localDecision.publicRepoContainsProviderIds === false &&
    localDecision.publicRepoContainsScreenshots === false &&
    localDecision.publicRepoContainsRawFeedback === false &&
    localDecision.publicRepoContainsFeedbackIdentities === false &&
    localDecision.publicRepoContainsPrivateBugDetails === false &&
    localDecision.publicRepoContainsPrivateActionDetails === false &&
    localDecision.publicRepoContainsPrivateExecutionNotes === false &&
    localDecision.publicRepoContainsPrivateResultNotes === false &&
    localDecision.publicRepoContainsPrivateDecisionNotes === false);

const decisionGo =
  localDecisionPresent &&
  localDecisionErrors.length === 0 &&
  localDecision.t10baResultValidationGo === true &&
  localDecision.privateResultEvidenceReady === true &&
  localDecision.resultEvidenceKeptOutsideGit === true &&
  localDecision.decisionScopeApprovedPrivately === true &&
  localDecision.decisionSelectedPrivately === true &&
  localDecision.p0P1BlockersReviewedPrivately === true &&
  localDecision.supportRiskReviewedPrivately === true &&
  localDecision.commercialRiskReviewedPrivately === true &&
  localDecision.ownerAssignedPrivately === true &&
  localDecision.acceptanceCriteriaDefinedPrivately === true &&
  localDecision.rollbackRiskReviewedPrivately === true &&
  localDecision.nextGateSelectedPrivately === true &&
  localDecision.publicSafeDecisionSummaryReady === true &&
  localDecision.iterationDecisionApprovedPrivately === true &&
  decisionValues.has(localDecision.decision) &&
  localDecision.decisionCandidateCount > 0 &&
  localDecision.selectedDecisionCount === 1 &&
  localDecision.failedCheckCount === 0 &&
  noPublicLeak;

const result = localDecisionPresent
  ? decisionGo
    ? "GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_ITERATION_DECISION_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10baDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleDecision, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10bb",
  result,
  provider: "Cloudflare",
  t10baResultValidationGateReady: t10baDoc.includes("GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK"),
  iterationDecisionDocReady:
    doc.includes("T10bb Private Tester Iteration Decision Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK") &&
    doc.includes("T10bc_private_tester_next_iteration_gate"),
  localIterationDecisionIgnored: gitignore.includes("tester-iteration-decision.local.json"),
  localDecisionPresent,
  localDecisionErrors,
  localDecisionSafe: localDecisionPresent ? localDecisionErrors.length === 0 : false,
  exampleDecisionSafe,
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
  providerMutationsPerformed: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-iteration-decision-gate"] === "node scripts/tester-iteration-decision-gate-proof.mjs",
  governanceUpdated: governance.includes("T10bb - Private Tester Iteration Decision Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10bb: private tester iteration decision gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10bb prepara decision privada de iteracion tester"),
  changelogUpdated: changelog.includes("T10bb Private Tester Iteration Decision Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-iteration-decision-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10bc_private_tester_next_iteration_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10baResultValidationGateReady ||
  !proof.iterationDecisionDocReady ||
  !proof.localIterationDecisionIgnored ||
  proof.localDecisionErrors.length > 0 ||
  !proof.exampleDecisionSafe ||
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
  proof.providerMutationsPerformed ||
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
