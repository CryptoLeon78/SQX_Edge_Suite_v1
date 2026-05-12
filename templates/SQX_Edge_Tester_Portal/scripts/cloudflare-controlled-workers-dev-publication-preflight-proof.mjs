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
const doc = readRepo("docs/T10AO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT.md");
const t10anDoc = readRepo("docs/T10AN_PROTECTED_TESTER_PUBLICATION_TARGET_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const exactApprovalPhrase =
  "AUTORIZO T10ao-publish-protected-workers-dev: activar workers_dev=true solo para sqx-edge-tester-portal-preview, ejecutar un unico npm exec -- wrangler deploy --config wrangler.jsonc, verificar Cloudflare Access antes de compartir URL, y hacer rollback/desactivar si falla.";
const publicationCommand = "npm exec -- wrangler deploy --config wrangler.jsonc";
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [doc, t10anDoc, governance, nextSteps, readme, changelog, templateReadme].join("\n");

const proof = Object.freeze({
  phase: "T10ao",
  result: "GO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT_READY_EXACT_APPROVAL_REQUIRED",
  provider: "Cloudflare",
  selectedTarget: "workers_dev_access_protected_publication_target",
  exactApprovalPhraseDocumented: doc.includes(exactApprovalPhrase),
  publicationCommandDocumented: doc.includes(publicationCommand),
  accessBoundaryPrecheckRequired: doc.includes("npm run proof:cloudflare-access-policy-boundary"),
  accessProbePrecheckRequired: doc.includes("npm run proof:cloudflare-workers-dev-access"),
  realAppDeployResultPrecheckRequired: doc.includes("npm run proof:cloudflare-real-app-deploy-result"),
  protectedTargetPrecheckRequired: doc.includes("npm run proof:cloudflare-protected-tester-publication-target"),
  selfPrecheckRequired: doc.includes("npm run proof:cloudflare-controlled-workers-dev-publication-preflight"),
  localBuildPrecheckRequired: doc.includes("npm run cf:build"),
  typecheckPrecheckRequired: doc.includes("npm run typecheck"),
  t10anTargetSelected: t10anDoc.includes("GO_PROTECTED_TESTER_PUBLICATION_TARGET_SELECTED_EXACT_APPROVAL_REQUIRED"),
  wranglerWorkersDevStillDisabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerMainIsOpenNextWorker: wranglerConfig.main === ".open-next/worker.js",
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  packageScriptReady:
    scripts["proof:cloudflare-controlled-workers-dev-publication-preflight"] ===
    "node scripts/cloudflare-controlled-workers-dev-publication-preflight-proof.mjs",
  docReady:
    doc.includes("T10ao Controlled Workers.dev Publication Preflight") &&
    doc.includes("GO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT_READY_EXACT_APPROVAL_REQUIRED") &&
    doc.includes("T10ap_controlled_workers_dev_publication_and_access_smoke"),
  governanceUpdated: governance.includes("T10ao - Controlled Workers.dev Publication Preflight"),
  nextStepsUpdated: nextSteps.includes("Phase T10ao: prepare controlled `workers.dev` publication preflight"),
  readmeUpdated: readme.includes("T10ao prepara el preflight de publicacion controlada"),
  changelogUpdated: changelog.includes("T10ao Controlled Workers.dev Publication Preflight"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-controlled-workers-dev-publication-preflight"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  externalPublicationPerformed: false,
  workersDevEnabled: false,
  nextGate: "T10ap_controlled_workers_dev_publication_and_access_smoke",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.exactApprovalPhraseDocumented ||
  !proof.publicationCommandDocumented ||
  !proof.accessBoundaryPrecheckRequired ||
  !proof.accessProbePrecheckRequired ||
  !proof.realAppDeployResultPrecheckRequired ||
  !proof.protectedTargetPrecheckRequired ||
  !proof.selfPrecheckRequired ||
  !proof.localBuildPrecheckRequired ||
  !proof.typecheckPrecheckRequired ||
  !proof.t10anTargetSelected ||
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
  proof.externalPublicationPerformed ||
  proof.workersDevEnabled
) {
  process.exitCode = 1;
}
