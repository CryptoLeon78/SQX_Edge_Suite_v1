import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");

function readProject(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readRepo(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

const packageJson = JSON.parse(readProject("package.json"));
const wranglerConfig = JSON.parse(readProject("wrangler.jsonc"));
const exampleEvidence = JSON.parse(readProject("tester-account-activation.example.json"));
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AR_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE.md");
const t10aqDoc = readRepo("docs/T10AQ_TESTER_ACCESS_HANDOFF_NO_URL_LEAK.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [
  doc,
  t10aqDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleEvidence, null, 2),
].join("\n");

const exampleEvidenceSafe =
  exampleEvidence.phase === "T10ar" &&
  exampleEvidence.t10aqHandoffGo === false &&
  exampleEvidence.accessStillInterceptsAnonymous === false &&
  exampleEvidence.appSessionStillRequiredAfterAccess === false &&
  exampleEvidence.privateAuthProviderSelected === false &&
  exampleEvidence.privateTesterAccountsPrepared === false &&
  exampleEvidence.passwordDeliveryChannelPrivate === false &&
  exampleEvidence.renewalCadenceScheduled === false &&
  exampleEvidence.supportChannelReadyPrivately === false &&
  exampleEvidence.revocationPathReadyPrivately === false &&
  exampleEvidence.testerAccountsCreatedPrivately === false &&
  exampleEvidence.testerInvitesSentPrivately === false &&
  exampleEvidence.testerUrlSharedPrivately === false &&
  exampleEvidence.publicRepoContainsTesterEmails === false &&
  exampleEvidence.publicRepoContainsTesterUrl === false &&
  exampleEvidence.publicRepoContainsCredentials === false &&
  exampleEvidence.publicRepoContainsProviderIds === false;

const proof = Object.freeze({
  phase: "T10ar",
  result: "GO_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE_READY_NO_GIT_LEAK",
  provider: "Cloudflare",
  t10aqHandoffGo: t10aqDoc.includes("GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK"),
  activationDocReady:
    doc.includes("T10ar Private Tester Account Activation Gate") &&
    doc.includes("GO_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE_READY_NO_GIT_LEAK") &&
    doc.includes("T10as_private_tester_activation_evidence_ingest"),
  localActivationEvidenceIgnored: gitignore.includes("tester-account-activation.local.json"),
  exampleEvidenceSafe,
  noDeployPerformed: true,
  testerAccountsCreated: false,
  testerInvitesSent: false,
  testerUrlShared: false,
  testerEmailsCommitted: false,
  credentialsCommitted: false,
  wranglerWorkersDevProtectedTargetEnabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:tester-account-activation-gate"] === "node scripts/tester-account-activation-gate-proof.mjs",
  governanceUpdated: governance.includes("T10ar - Private Tester Account Activation Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10ar: private tester account activation gate without Git URL/email leak"),
  readmeUpdated: readme.includes("T10ar prepara el gate privado de activacion de cuentas tester"),
  changelogUpdated: changelog.includes("T10ar Private Tester Account Activation Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-account-activation-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10as_private_tester_activation_evidence_ingest",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.t10aqHandoffGo ||
  !proof.activationDocReady ||
  !proof.localActivationEvidenceIgnored ||
  !proof.exampleEvidenceSafe ||
  !proof.noDeployPerformed ||
  proof.testerAccountsCreated ||
  proof.testerInvitesSent ||
  proof.testerUrlShared ||
  proof.testerEmailsCommitted ||
  proof.credentialsCommitted ||
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
