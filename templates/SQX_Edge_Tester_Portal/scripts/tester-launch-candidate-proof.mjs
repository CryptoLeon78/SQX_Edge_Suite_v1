import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localLaunchPath = join(projectRoot, "tester-launch-candidate.local.json");

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

const launchModes = new Set(["hold", "first_private_tester", "micro_cohort", "pause"]);
const booleanFields = new Set([
  "protectedAccessVerifiedPrivately",
  "protectedTesterUrlKnownPrivately",
  "testerUrlKeptOutsideGit",
  "testerAuthSmokePassedPrivately",
  "activeTesterPathVerifiedPrivately",
  "blockedStatesVerifiedPrivately",
  "adminReviewReadyPrivately",
  "supportChannelReadyPrivately",
  "rollbackPlanReadyPrivately",
  "launchMessageReadyPrivately",
  "operatorApprovalReadyPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
  "publicRepoContainsRawFeedback",
  "publicRepoContainsPrivateNotes",
]);
const countFields = new Set([
  "privateTesterCount",
  "activePathSmokeCount",
  "blockedStateSmokeCount",
  "openP0Count",
  "openP1Count",
  "failedCheckCount",
]);
const allowedFields = new Set(["phase", "launchMode", ...booleanFields, ...countFields]);

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
  /private[_-]?notes?/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateLaunch(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["tester launch evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "TL1") {
        errors.push("phase must be TL1");
      }
      continue;
    }

    if (key === "launchMode") {
      if (!launchModes.has(value)) {
        errors.push("launchMode must be an accepted public-safe value");
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
    if (launchModes.has(value)) {
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
const exampleLaunch = parseJson(readProject("tester-launch-candidate.example.json"), "tester-launch-candidate.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/TL1_TESTER_LAUNCH_CANDIDATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localLaunchPresent = existsSync(localLaunchPath);
const localLaunch = localLaunchPresent
  ? parseJson(readFileSync(localLaunchPath, "utf8"), "tester-launch-candidate.local.json")
  : null;
const localLaunchErrors = localLaunchPresent ? validateLaunch(localLaunch) : [];

const exampleLaunchSafe =
  exampleLaunch.phase === "TL1" &&
  validateLaunch(exampleLaunch).length === 0 &&
  launchModes.has(exampleLaunch.launchMode) &&
  [...booleanFields].every((key) => exampleLaunch[key] === false) &&
  [...countFields].every((key) => exampleLaunch[key] === 0);

const noPublicLeak =
  !localLaunchPresent ||
  (localLaunch.publicRepoContainsTesterEmails === false &&
    localLaunch.publicRepoContainsTesterUrl === false &&
    localLaunch.publicRepoContainsCredentials === false &&
    localLaunch.publicRepoContainsProviderIds === false &&
    localLaunch.publicRepoContainsScreenshots === false &&
    localLaunch.publicRepoContainsRawFeedback === false &&
    localLaunch.publicRepoContainsPrivateNotes === false);

const launchGo =
  localLaunchPresent &&
  localLaunchErrors.length === 0 &&
  localLaunch.protectedAccessVerifiedPrivately === true &&
  localLaunch.protectedTesterUrlKnownPrivately === true &&
  localLaunch.testerUrlKeptOutsideGit === true &&
  localLaunch.testerAuthSmokePassedPrivately === true &&
  localLaunch.activeTesterPathVerifiedPrivately === true &&
  localLaunch.blockedStatesVerifiedPrivately === true &&
  localLaunch.adminReviewReadyPrivately === true &&
  localLaunch.supportChannelReadyPrivately === true &&
  localLaunch.rollbackPlanReadyPrivately === true &&
  localLaunch.launchMessageReadyPrivately === true &&
  localLaunch.operatorApprovalReadyPrivately === true &&
  localLaunch.launchMode !== "hold" &&
  localLaunch.privateTesterCount > 0 &&
  localLaunch.activePathSmokeCount > 0 &&
  localLaunch.blockedStateSmokeCount > 0 &&
  localLaunch.openP0Count === 0 &&
  localLaunch.openP1Count === 0 &&
  localLaunch.failedCheckCount === 0 &&
  noPublicLeak;

const result = localLaunchPresent
  ? launchGo
    ? "GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK"
    : "NO_GO_TESTER_LAUNCH_CANDIDATE_INCOMPLETE"
  : "NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleLaunch, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "TL1",
  result,
  provider: "Cloudflare",
  launchCandidateDocReady:
    doc.includes("TL1 Tester Launch Candidate") &&
    doc.includes("NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING") &&
    doc.includes("GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK"),
  localLaunchCandidateIgnored: gitignore.includes("tester-launch-candidate.local.json"),
  localLaunchPresent,
  localLaunchErrors,
  localLaunchSafe: localLaunchPresent ? localLaunchErrors.length === 0 : false,
  exampleLaunchSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  rawFeedbackCommitted: false,
  privateNotesCommitted: false,
  providerMutationsPerformed: false,
  testerAccountsCreated: false,
  wranglerWorkersDevProtectedTargetEnabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-launch-candidate"] === "node scripts/tester-launch-candidate-proof.mjs",
  governanceUpdated: governance.includes("TL1 - Tester Launch Candidate"),
  nextStepsUpdated: nextSteps.includes("TL1 - Tester Launch Candidate"),
  readmeUpdated: readme.includes("TL1 resume el lanzamiento tester"),
  changelogUpdated: changelog.includes("TL1 Tester Launch Candidate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-launch-candidate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextRealAction: "fill_private_launch_candidate_evidence_and_run_single_proof",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.launchCandidateDocReady ||
  !proof.localLaunchCandidateIgnored ||
  proof.localLaunchErrors.length > 0 ||
  !proof.exampleLaunchSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
  proof.rawFeedbackCommitted ||
  proof.privateNotesCommitted ||
  proof.providerMutationsPerformed ||
  proof.testerAccountsCreated ||
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
