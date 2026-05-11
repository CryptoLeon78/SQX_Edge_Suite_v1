import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localResultPath = join(projectRoot, "tester-result-validation.local.json");

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
  "t10azActionExecutionGo",
  "privateExecutionEvidenceReady",
  "executionEvidenceKeptOutsideGit",
  "resultValidationScopeApprovedPrivately",
  "resultsClassifiedPrivately",
  "acceptedActionsSeparatedPrivately",
  "repeatActionsSeparatedPrivately",
  "blockedActionsSeparatedPrivately",
  "p0P1BlockersSeparatedPrivately",
  "acceptanceEvidenceReviewedPrivately",
  "regressionRiskReviewedPrivately",
  "rollbackRiskReviewedPrivately",
  "supportSignalsSeparatedPrivately",
  "commercialSignalsSeparatedPrivately",
  "publicSafeResultSummaryReady",
  "resultValidationApprovedPrivately",
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
]);

const countFields = new Set([
  "validatedResultCount",
  "acceptedActionCount",
  "repeatActionCount",
  "blockedActionCount",
  "deferredActionCount",
  "p0P1BlockerCount",
  "supportSignalCount",
  "commercialSignalCount",
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
  /private[_-]?result/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateResult(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["result validation evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10ba") {
        errors.push("phase must be T10ba");
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
const exampleResult = parseJson(readProject("tester-result-validation.example.json"), "tester-result-validation.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10BA_PRIVATE_TESTER_RESULT_VALIDATION_GATE.md");
const t10azDoc = readRepo("docs/T10AZ_PRIVATE_TESTER_ACTION_EXECUTION_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localResultPresent = existsSync(localResultPath);
const localResult = localResultPresent
  ? parseJson(readFileSync(localResultPath, "utf8"), "tester-result-validation.local.json")
  : null;
const localResultErrors = localResultPresent ? validateResult(localResult) : [];

const exampleResultSafe =
  exampleResult.phase === "T10ba" &&
  validateResult(exampleResult).length === 0 &&
  [...booleanFields].every((key) => exampleResult[key] === false) &&
  [...countFields].every((key) => exampleResult[key] === 0);

const noPublicLeak =
  !localResultPresent ||
  (localResult.publicRepoContainsTesterEmails === false &&
    localResult.publicRepoContainsTesterUrl === false &&
    localResult.publicRepoContainsCredentials === false &&
    localResult.publicRepoContainsProviderIds === false &&
    localResult.publicRepoContainsScreenshots === false &&
    localResult.publicRepoContainsRawFeedback === false &&
    localResult.publicRepoContainsFeedbackIdentities === false &&
    localResult.publicRepoContainsPrivateBugDetails === false &&
    localResult.publicRepoContainsPrivateActionDetails === false &&
    localResult.publicRepoContainsPrivateExecutionNotes === false &&
    localResult.publicRepoContainsPrivateResultNotes === false);

const resultGo =
  localResultPresent &&
  localResultErrors.length === 0 &&
  localResult.t10azActionExecutionGo === true &&
  localResult.privateExecutionEvidenceReady === true &&
  localResult.executionEvidenceKeptOutsideGit === true &&
  localResult.resultValidationScopeApprovedPrivately === true &&
  localResult.resultsClassifiedPrivately === true &&
  localResult.acceptedActionsSeparatedPrivately === true &&
  localResult.repeatActionsSeparatedPrivately === true &&
  localResult.blockedActionsSeparatedPrivately === true &&
  localResult.p0P1BlockersSeparatedPrivately === true &&
  localResult.acceptanceEvidenceReviewedPrivately === true &&
  localResult.regressionRiskReviewedPrivately === true &&
  localResult.rollbackRiskReviewedPrivately === true &&
  localResult.supportSignalsSeparatedPrivately === true &&
  localResult.commercialSignalsSeparatedPrivately === true &&
  localResult.publicSafeResultSummaryReady === true &&
  localResult.resultValidationApprovedPrivately === true &&
  localResult.validatedResultCount > 0 &&
  localResult.failedCheckCount === 0 &&
  noPublicLeak;

const result = localResultPresent
  ? resultGo
    ? "GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10azDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleResult, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10ba",
  result,
  provider: "Cloudflare",
  t10azActionExecutionGateReady: t10azDoc.includes("GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK"),
  resultValidationDocReady:
    doc.includes("T10ba Private Tester Result Validation Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK") &&
    doc.includes("T10bb_private_tester_iteration_decision_gate"),
  localResultValidationIgnored: gitignore.includes("tester-result-validation.local.json"),
  localResultPresent,
  localResultErrors,
  localResultSafe: localResultPresent ? localResultErrors.length === 0 : false,
  exampleResultSafe,
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
  providerMutationsPerformed: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-result-validation-gate"] === "node scripts/tester-result-validation-gate-proof.mjs",
  governanceUpdated: governance.includes("T10ba - Private Tester Result Validation Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ba: private tester result validation gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10ba prepara validacion privada de resultados tester"),
  changelogUpdated: changelog.includes("T10ba Private Tester Result Validation Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-result-validation-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10bb_private_tester_iteration_decision_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10azActionExecutionGateReady ||
  !proof.resultValidationDocReady ||
  !proof.localResultValidationIgnored ||
  proof.localResultErrors.length > 0 ||
  !proof.exampleResultSafe ||
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
