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
const doc = readRepo("docs/T10AN_PROTECTED_TESTER_PUBLICATION_TARGET_GATE.md");
const t10amDoc = readRepo("docs/T10AM_CONTROLLED_REAL_APP_DEPLOY_RESULT.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const exactApprovalPhrase =
  "AUTORIZO T10ao-publish-protected-workers-dev: activar workers_dev=true solo para sqx-edge-tester-portal-preview, ejecutar un unico npm exec -- wrangler deploy --config wrangler.jsonc, verificar Cloudflare Access antes de compartir URL, y hacer rollback/desactivar si falla.";
const futureDeployCommand = "npm exec -- wrangler deploy --config wrangler.jsonc";
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [doc, t10amDoc, governance, nextSteps, readme, changelog, templateReadme].join("\n");

const proof = Object.freeze({
  phase: "T10an",
  result: "GO_PROTECTED_TESTER_PUBLICATION_TARGET_SELECTED_EXACT_APPROVAL_REQUIRED",
  provider: "Cloudflare",
  selectedTarget: "workers_dev_access_protected_publication_target",
  exactApprovalPhraseDocumented: doc.includes(exactApprovalPhrase),
  futureDeployCommandDocumented: doc.includes(futureDeployCommand),
  accessBoundaryPrecheckRequired: doc.includes("npm run proof:cloudflare-access-policy-boundary"),
  accessProbePrecheckRequired: doc.includes("npm run proof:cloudflare-workers-dev-access"),
  realAppDeployResultPrecheckRequired: doc.includes("npm run proof:cloudflare-real-app-deploy-result"),
  localBuildPrecheckRequired: doc.includes("npm run cf:build"),
  typecheckPrecheckRequired: doc.includes("npm run typecheck"),
  t10amResultRecorded: t10amDoc.includes("GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL"),
  wranglerWorkersDevStillDisabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerMainIsOpenNextWorker: wranglerConfig.main === ".open-next/worker.js",
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-protected-tester-publication-target"] ===
    "node scripts/cloudflare-protected-tester-publication-target-proof.mjs",
  docReady:
    doc.includes("T10an Protected Tester Publication Target Gate") &&
    doc.includes("GO_PROTECTED_TESTER_PUBLICATION_TARGET_SELECTED_EXACT_APPROVAL_REQUIRED") &&
    doc.includes("T10ao_controlled_workers_dev_publication_preflight"),
  governanceUpdated: governance.includes("T10an - Protected Tester Publication Target Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10an: choose and verify the protected tester publication target"),
  readmeUpdated: readme.includes("T10an selecciona `workers.dev` protegido por Cloudflare Access"),
  changelogUpdated: changelog.includes("T10an Protected Tester Publication Target Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-protected-tester-publication-target"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  externalPublicationPerformed: false,
  nextGate: "T10ao_controlled_workers_dev_publication_preflight",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.exactApprovalPhraseDocumented ||
  !proof.futureDeployCommandDocumented ||
  !proof.accessBoundaryPrecheckRequired ||
  !proof.accessProbePrecheckRequired ||
  !proof.realAppDeployResultPrecheckRequired ||
  !proof.localBuildPrecheckRequired ||
  !proof.typecheckPrecheckRequired ||
  !proof.t10amResultRecorded ||
  !proof.wranglerWorkersDevStillDisabled ||
  !proof.wranglerPreviewUrlsDisabled ||
  !proof.wranglerMainIsOpenNextWorker ||
  !proof.wranglerHasNoRoutesCommitted ||
  !proof.directDeployScriptAbsent ||
  !proof.packageScriptReady ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  !proof.readmeUpdated ||
  !proof.changelogUpdated ||
  !proof.templateReadmeUpdated ||
  !proof.noSensitiveCloudflareEnvCommitted ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.externalPublicationPerformed
) {
  process.exitCode = 1;
}
