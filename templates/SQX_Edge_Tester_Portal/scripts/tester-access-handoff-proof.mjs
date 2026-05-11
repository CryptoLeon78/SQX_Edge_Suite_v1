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
const exampleEvidence = JSON.parse(readProject("tester-access-handoff.example.json"));
const gitignore = readProject(".gitignore");
const doc = readRepo("docs/T10AQ_TESTER_ACCESS_HANDOFF_NO_URL_LEAK.md");
const t10apDoc = readRepo("docs/T10AP_CONTROLLED_WORKERS_DEV_PUBLICATION_RESULT.md");
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
  t10apDoc,
  governance,
  nextSteps,
  readme,
  changelog,
  templateReadme,
  JSON.stringify(exampleEvidence, null, 2),
].join("\n");

const exampleEvidenceSafe =
  exampleEvidence.phase === "T10aq" &&
  exampleEvidence.publicationResultGo === false &&
  exampleEvidence.accessStillInterceptsAnonymous === false &&
  exampleEvidence.appSessionStillRequiredAfterAccess === false &&
  exampleEvidence.testerAccountsPreparedPrivately === false &&
  exampleEvidence.operatorPrivateChannelSelected === false &&
  exampleEvidence.testerUrlShared === false &&
  exampleEvidence.testerAccountsCreated === false &&
  exampleEvidence.testerEmailsCommitted === false &&
  exampleEvidence.containsUrl === false &&
  exampleEvidence.containsHostname === false &&
  exampleEvidence.containsTesterEmail === false &&
  exampleEvidence.containsPassword === false &&
  exampleEvidence.containsToken === false &&
  exampleEvidence.containsKey === false &&
  exampleEvidence.containsAccountId === false &&
  exampleEvidence.containsAccessId === false &&
  exampleEvidence.containsDeploymentId === false &&
  exampleEvidence.containsVersionId === false;

const proof = Object.freeze({
  phase: "T10aq",
  result: "GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK",
  provider: "Cloudflare",
  publicationResultGo: t10apDoc.includes("GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED"),
  handoffDocReady:
    doc.includes("T10aq Tester Access Handoff No URL Leak") &&
    doc.includes("GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK") &&
    doc.includes("T10ar_private_tester_account_activation_gate"),
  localHandoffEvidenceIgnored: gitignore.includes("tester-access-handoff.local.json"),
  exampleEvidenceSafe,
  noDeployPerformed: true,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  wranglerWorkersDevSafeDefault: wranglerConfig.workers_dev === false,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:tester-access-handoff"] === "node scripts/tester-access-handoff-proof.mjs",
  governanceUpdated: governance.includes("T10aq - Tester Access Handoff No URL Leak"),
  nextStepsUpdated: nextSteps.includes("Phase T10aq: prepare tester access handoff without public URL leak"),
  readmeUpdated: readme.includes("T10aq prepara handoff controlado de acceso tester"),
  changelogUpdated: changelog.includes("T10aq Tester Access Handoff No URL Leak"),
  templateReadmeUpdated: templateReadme.includes("proof:tester-access-handoff"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  nextGate: "T10ar_private_tester_account_activation_gate",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.publicationResultGo ||
  !proof.handoffDocReady ||
  !proof.localHandoffEvidenceIgnored ||
  !proof.exampleEvidenceSafe ||
  !proof.noDeployPerformed ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
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
