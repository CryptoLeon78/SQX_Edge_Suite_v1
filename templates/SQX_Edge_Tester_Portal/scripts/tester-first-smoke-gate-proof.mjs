import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localSmokePath = join(projectRoot, "tester-first-smoke.local.json");

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
  "t10atUrlShareApprovalGo",
  "privateUrlSharedWithSingleTester",
  "accessBlocksAnonymous",
  "accessAllowsApprovedTester",
  "appLoginRequiredAfterAccess",
  "appPortalLoadsForTester",
  "testerProEntitlementsVisible",
  "adminRoutesBlockedForTester",
  "logoutClearsSession",
  "supportChannelReadyPrivately",
  "revocationPathReadyPrivately",
  "testerSmokeCompletedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
  "publicRepoContainsScreenshots",
]);

const countFields = new Set(["smokedTesterCount", "failedCheckCount"]);
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
  /\.(png|jpe?g|webp|gif)$/i,
];

function validateSmoke(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["smoke evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10au") {
        errors.push("phase must be T10au");
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
const exampleSmoke = parseJson(readProject("tester-first-smoke.example.json"), "tester-first-smoke.example.json");
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AU_PRIVATE_FIRST_TESTER_SMOKE_GATE.md");
const t10atDoc = readRepo("docs/T10AT_PRIVATE_TESTER_URL_SHARE_APPROVAL_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localSmokePresent = existsSync(localSmokePath);
const localSmoke = localSmokePresent
  ? parseJson(readFileSync(localSmokePath, "utf8"), "tester-first-smoke.local.json")
  : null;
const localSmokeErrors = localSmokePresent ? validateSmoke(localSmoke) : [];

const exampleSmokeSafe =
  exampleSmoke.phase === "T10au" &&
  validateSmoke(exampleSmoke).length === 0 &&
  [...booleanFields].every((key) => exampleSmoke[key] === false) &&
  [...countFields].every((key) => exampleSmoke[key] === 0);

const noPublicLeak =
  !localSmokePresent ||
  (localSmoke.publicRepoContainsTesterEmails === false &&
    localSmoke.publicRepoContainsTesterUrl === false &&
    localSmoke.publicRepoContainsCredentials === false &&
    localSmoke.publicRepoContainsProviderIds === false &&
    localSmoke.publicRepoContainsScreenshots === false);

const smokeGo =
  localSmokePresent &&
  localSmokeErrors.length === 0 &&
  localSmoke.t10atUrlShareApprovalGo === true &&
  localSmoke.privateUrlSharedWithSingleTester === true &&
  localSmoke.accessBlocksAnonymous === true &&
  localSmoke.accessAllowsApprovedTester === true &&
  localSmoke.appLoginRequiredAfterAccess === true &&
  localSmoke.appPortalLoadsForTester === true &&
  localSmoke.testerProEntitlementsVisible === true &&
  localSmoke.adminRoutesBlockedForTester === true &&
  localSmoke.logoutClearsSession === true &&
  localSmoke.supportChannelReadyPrivately === true &&
  localSmoke.revocationPathReadyPrivately === true &&
  localSmoke.testerSmokeCompletedPrivately === true &&
  localSmoke.smokedTesterCount === 1 &&
  localSmoke.failedCheckCount === 0 &&
  noPublicLeak;

const result = localSmokePresent
  ? smokeGo
    ? "GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_FIRST_TESTER_SMOKE_INCOMPLETE"
  : "NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10atDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleSmoke, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10au",
  result,
  provider: "Cloudflare",
  t10atUrlShareApprovalGateReady: t10atDoc.includes("GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK"),
  firstTesterSmokeDocReady:
    doc.includes("T10au Private First Tester Smoke Gate") &&
    doc.includes("NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK") &&
    doc.includes("T10av_private_tester_cohort_expansion_gate"),
  localFirstSmokeIgnored: gitignore.includes("tester-first-smoke.local.json"),
  localSmokePresent,
  localSmokeErrors,
  localSmokeSafe: localSmokePresent ? localSmokeErrors.length === 0 : false,
  exampleSmokeSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  screenshotsCommitted: false,
  wranglerWorkersDevProtectedTargetEnabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady: scripts["proof:tester-first-smoke-gate"] === "node scripts/tester-first-smoke-gate-proof.mjs",
  governanceUpdated: governance.includes("T10au - Private First Tester Smoke Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10au: private first tester smoke gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10au prepara el gate de primer smoke privado tester"),
  changelogUpdated: changelog.includes("T10au Private First Tester Smoke Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-first-smoke-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10av_private_tester_cohort_expansion_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10atUrlShareApprovalGateReady ||
  !proof.firstTesterSmokeDocReady ||
  !proof.localFirstSmokeIgnored ||
  proof.localSmokeErrors.length > 0 ||
  !proof.exampleSmokeSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
  proof.screenshotsCommitted ||
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
