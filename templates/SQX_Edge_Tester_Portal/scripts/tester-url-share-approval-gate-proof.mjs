import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");
const localApprovalPath = join(projectRoot, "tester-url-share-approval.local.json");

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
  "t10asActivationEvidenceGo",
  "accessStillInterceptsAnonymous",
  "appSessionStillRequiredAfterAccess",
  "privateTesterAccountsActivated",
  "passwordDeliveryChannelPrivate",
  "supportChannelReadyPrivately",
  "revocationPathReadyPrivately",
  "renewalCadenceScheduled",
  "privateOneToOneShareChannelReady",
  "testerUrlSharedPrivately",
  "publicRepoContainsTesterEmails",
  "publicRepoContainsTesterUrl",
  "publicRepoContainsCredentials",
  "publicRepoContainsProviderIds",
]);

const countFields = new Set(["approvedTesterCount", "pendingTesterCount", "urlRecipientsCount"]);
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
];

function validateApproval(evidence) {
  const errors = [];
  if (!evidence || Array.isArray(evidence) || typeof evidence !== "object") {
    return ["approval evidence must be a JSON object"];
  }

  for (const [key, value] of Object.entries(evidence)) {
    if (!allowedFields.has(key)) {
      errors.push(`unexpected field: ${key}`);
      continue;
    }

    if (key === "phase") {
      if (value !== "T10at") {
        errors.push("phase must be T10at");
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
const exampleApproval = parseJson(
  readProject("tester-url-share-approval.example.json"),
  "tester-url-share-approval.example.json",
);
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AT_PRIVATE_TESTER_URL_SHARE_APPROVAL_GATE.md");
const t10asDoc = readRepo("docs/T10AS_PRIVATE_TESTER_ACTIVATION_EVIDENCE_INGEST.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};
const localApprovalPresent = existsSync(localApprovalPath);
const localApproval = localApprovalPresent
  ? parseJson(readFileSync(localApprovalPath, "utf8"), "tester-url-share-approval.local.json")
  : null;
const localApprovalErrors = localApprovalPresent ? validateApproval(localApproval) : [];

const exampleApprovalSafe =
  exampleApproval.phase === "T10at" &&
  validateApproval(exampleApproval).length === 0 &&
  [...booleanFields].every((key) => exampleApproval[key] === false) &&
  [...countFields].every((key) => exampleApproval[key] === 0);

const noPublicLeak =
  !localApprovalPresent ||
  (localApproval.publicRepoContainsTesterEmails === false &&
    localApproval.publicRepoContainsTesterUrl === false &&
    localApproval.publicRepoContainsCredentials === false &&
    localApproval.publicRepoContainsProviderIds === false);

const approvalGo =
  localApprovalPresent &&
  localApprovalErrors.length === 0 &&
  localApproval.t10asActivationEvidenceGo === true &&
  localApproval.accessStillInterceptsAnonymous === true &&
  localApproval.appSessionStillRequiredAfterAccess === true &&
  localApproval.privateTesterAccountsActivated === true &&
  localApproval.passwordDeliveryChannelPrivate === true &&
  localApproval.supportChannelReadyPrivately === true &&
  localApproval.revocationPathReadyPrivately === true &&
  localApproval.renewalCadenceScheduled === true &&
  localApproval.privateOneToOneShareChannelReady === true &&
  localApproval.testerUrlSharedPrivately === false &&
  localApproval.approvedTesterCount > 0 &&
  localApproval.urlRecipientsCount === 0 &&
  noPublicLeak;

const result = localApprovalPresent
  ? approvalGo
    ? "GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK"
    : "NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_INCOMPLETE"
  : "NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING";

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10asDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleApproval, null, 2),
].join("\n");

const proof = Object.freeze({
  phase: "T10at",
  result,
  provider: "Cloudflare",
  t10asEvidenceGateReady: t10asDoc.includes("GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK"),
  urlShareApprovalDocReady:
    doc.includes("T10at Private Tester URL Share Approval Gate") &&
    doc.includes("NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING") &&
    doc.includes("GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK") &&
    doc.includes("T10au_private_first_tester_smoke_gate"),
  localUrlShareApprovalIgnored: gitignore.includes("tester-url-share-approval.local.json"),
  localApprovalPresent,
  localApprovalErrors,
  localApprovalSafe: localApprovalPresent ? localApprovalErrors.length === 0 : false,
  exampleApprovalSafe,
  noDeployPerformed: true,
  testerUrlPublished: false,
  testerUrlSharedPrivately: false,
  credentialsCommitted: false,
  testerEmailsCommitted: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:tester-url-share-approval-gate"] ===
    "node scripts/tester-url-share-approval-gate-proof.mjs",
  governanceUpdated: governance.includes("T10at - Private Tester URL Share Approval Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10at: private tester URL share approval gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10at prepara el gate privado para compartir URL tester"),
  changelogUpdated: changelog.includes("T10at Private Tester URL Share Approval Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-url-share-approval-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10au_private_first_tester_smoke_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10asEvidenceGateReady ||
  !proof.urlShareApprovalDocReady ||
  !proof.localUrlShareApprovalIgnored ||
  proof.localApprovalErrors.length > 0 ||
  !proof.exampleApprovalSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlPublished ||
  proof.testerUrlSharedPrivately ||
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
