import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localEvidencePath = join(projectRoot, "tester-account-activation.local.json");

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
  "accessStillInterceptsAnonymous",
  "appSessionStillRequiredAfterAccess",
  "privateAuthProviderSelected",
  "privateTesterAccountsPrepared",
  "passwordDeliveryChannelPrivate",
  "renewalCadenceScheduled",
  "supportChannelReadyPrivately",
  "revocationPathReadyPrivately",
  "testerAccountsCreatedPrivately",
  "testerInvitesSentPrivately",
  "testerUrlSharedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
]);

const countFields = new Set(["activatedTesterCount", "pendingTesterCount", "invitedTesterCount"]);
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
];

function validateEvidence(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10ar" && value !== "T10as") {
        errors.push("phase must be T10ar or T10as");
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
const exampleEvidence = parseJson(
  readProject("tester-activation-evidence-ingest.example.json"),
  "tester-activation-evidence-ingest.example.json",
);
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AS_PRIVATE_TESTER_ACTIVATION_EVIDENCE_INGEST.md");
const t10arDoc = readRepo("docs/T10AR_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localEvidencePresent = existsSync(localEvidencePath);
const localEvidence = localEvidencePresent
  ? parseJson(readFileSync(localEvidencePath, "utf8"), "tester-account-activation.local.json")
  : null;
const localEvidenceErrors = localEvidencePresent ? validateEvidence(localEvidence) : [];

const exampleEvidenceSafe =
  exampleEvidence.phase === "T10as" &&
  validateEvidence(exampleEvidence).length === 0 &&
  [...booleanFields].every((key) => exampleEvidence[key] === false) &&
  [...countFields].every((key) => exampleEvidence[key] === 0);

const noPublicLeak =
  !localEvidencePresent ||
  (localEvidence.publicRepoContainsTesterEmails === false &&
    localEvidence.publicRepoContainsTesterUrl === false &&
    localEvidence.publicRepoContainsCredentials === false &&
    localEvidence.publicRepoContainsProviderIds === false);

const activationEvidenceGo =
  localEvidencePresent &&
  localEvidenceErrors.length === 0 &&
  localEvidence.accessStillInterceptsAnonymous === true &&
  localEvidence.appSessionStillRequiredAfterAccess === true &&
  localEvidence.privateAuthProviderSelected === true &&
  localEvidence.privateTesterAccountsPrepared === true &&
  localEvidence.passwordDeliveryChannelPrivate === true &&
  localEvidence.renewalCadenceScheduled === true &&
  localEvidence.supportChannelReadyPrivately === true &&
  localEvidence.revocationPathReadyPrivately === true &&
  localEvidence.testerAccountsCreatedPrivately === true &&
  localEvidence.testerUrlSharedPrivately === false &&
  noPublicLeak;

const result = localEvidencePresent
  ? activationEvidenceGo
    ? "GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10arDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleEvidence, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10as",
  result,
  provider: "Cloudflare",
  t10arGateReady: t10arDoc.includes("GO_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE_READY_NO_GIT_LEAK"),
  activationEvidenceDocReady:
    doc.includes("T10as Private Tester Activation Evidence Ingest") &&
    doc.includes("NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK") &&
    doc.includes("T10at_private_tester_url_share_approval_gate"),
  localActivationEvidenceIgnored: gitignore.includes("tester-account-activation.local.json"),
  localEvidencePresent,
  localEvidenceErrors,
  localEvidenceSafe: localEvidencePresent ? localEvidenceErrors.length === 0 : false,
  exampleEvidenceSafe,
  noDeployPerformed: true,
  testerUrlShared: false,
  credentialsCommitted: false,
  testerEmailsCommitted: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:tester-activation-evidence-ingest"] ===
    "node scripts/tester-activation-evidence-ingest-proof.mjs",
  governanceUpdated: governance.includes("T10as - Private Tester Activation Evidence Ingest"),
  nextStepsUpdated: nextSteps.includes("Phase T10as: private tester activation evidence ingest without Git URL/email leak"),
  readmeUpdated: readme.includes("T10as ingiere evidencia privada de activacion tester"),
  changelogUpdated: changelog.includes("T10as Private Tester Activation Evidence Ingest"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-activation-evidence-ingest"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10at_private_tester_url_share_approval_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10arGateReady ||
  !proof.activationEvidenceDocReady ||
  !proof.localActivationEvidenceIgnored ||
  proof.localEvidenceErrors.length > 0 ||
  !proof.exampleEvidenceSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlShared ||
  proof.credentialsCommitted ||
  proof.testerEmailsCommitted ||
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
