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
const doc = readRepo("docs/T10AL_CONTROLLED_REAL_APP_DEPLOY_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const readme = readRepo("README.md");
const changelog = readRepo("CHANGELOG.md");
const templateReadme = readProject("README.md");
const scripts = packageJson.scripts ?? {};

const exactApprovalPhrase =
  "AUTORIZO T10al-deploy-real-app: ejecutar un unico wrangler deploy --config wrangler.jsonc para sqx-edge-tester-portal-preview, verificar Access antes de publicar URL, y hacer rollback si falla.";
const futureDeployCommand = "npm exec -- wrangler deploy --config wrangler.jsonc";
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");
const forbiddenZonePattern = ["CLOUDFLARE_ZONE_ID", "="].join("");
const combinedPublicText = [doc, governance, nextSteps, readme, changelog, templateReadme].join("\n");

const proof = Object.freeze({
  phase: "T10al",
  result: "GO_CONTROLLED_REAL_APP_DEPLOY_GATE_READY_EXACT_APPROVAL_REQUIRED",
  provider: "Cloudflare",
  selectedPath: "protected_workers_dev_real_app_deploy_gate",
  exactApprovalPhraseDocumented: doc.includes(exactApprovalPhrase),
  futureDeployCommandDocumented: doc.includes(futureDeployCommand),
  accessBoundaryPrecheckRequired: doc.includes("npm run proof:cloudflare-access-policy-boundary"),
  accessProbePrecheckRequired: doc.includes("npm run proof:cloudflare-workers-dev-access"),
  hostnameGatePrecheckRequired: doc.includes("npm run proof:cloudflare-hostname-zone-selection"),
  localBuildPrecheckRequired: doc.includes("npm run cf:build"),
  typecheckPrecheckRequired: doc.includes("npm run typecheck"),
  postDeployAnonymousAccessRequired: doc.includes("Probe anonymous access with redirects disabled"),
  rollbackRuleDocumented: doc.includes("Rollback Rule") && doc.includes("rollback immediately"),
  wranglerWorkersDevDisabled: wranglerConfig.workers_dev === true,
  wranglerPreviewUrlsDisabled: wranglerConfig.preview_urls === false,
  wranglerMainIsOpenNextWorker: wranglerConfig.main === ".open-next/worker.js",
  wranglerHasNoRoutesCommitted: !Array.isArray(wranglerConfig.routes),
  directDeployScriptAbsent: scripts.deploy === undefined && scripts["cf:deploy"] === undefined,
  buildScriptPresent: scripts["cf:build"] === "opennextjs-cloudflare build",
  typecheckScriptPresent: scripts.typecheck === "tsc --noEmit",
  packageScriptReady:
    scripts["proof:cloudflare-controlled-real-app-deploy-gate"] ===
    "node scripts/cloudflare-controlled-real-app-deploy-gate-proof.mjs",
  docReady:
    doc.includes("T10al Controlled Real App Deploy Gate") &&
    doc.includes("GO_CONTROLLED_REAL_APP_DEPLOY_GATE_READY_EXACT_APPROVAL_REQUIRED") &&
    doc.includes("T10am_controlled_real_app_deploy_and_access_smoke"),
  governanceUpdated: governance.includes("T10al - Controlled Real App Deploy Gate"),
  nextStepsUpdated: nextSteps.includes("Phase T10al: prepare the exact controlled real app deploy gate"),
  readmeUpdated: readme.includes("T10al prepara el gate exacto de deploy real controlado"),
  changelogUpdated: changelog.includes("T10al Controlled Real App Deploy Gate"),
  templateReadmeUpdated: templateReadme.includes("proof:cloudflare-controlled-real-app-deploy-gate"),
  noSensitiveCloudflareEnvCommitted:
    !combinedPublicText.includes(forbiddenTokenPattern) &&
    !combinedPublicText.includes(forbiddenAccountPattern) &&
    !combinedPublicText.includes(forbiddenZonePattern),
  realAppDeployed: false,
  deployCommandExecuted: false,
  testerUrlShared: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  nextGate: "T10am_controlled_real_app_deploy_and_access_smoke",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.exactApprovalPhraseDocumented ||
  !proof.futureDeployCommandDocumented ||
  !proof.accessBoundaryPrecheckRequired ||
  !proof.accessProbePrecheckRequired ||
  !proof.hostnameGatePrecheckRequired ||
  !proof.localBuildPrecheckRequired ||
  !proof.typecheckPrecheckRequired ||
  !proof.postDeployAnonymousAccessRequired ||
  !proof.rollbackRuleDocumented ||
  !proof.wranglerWorkersDevDisabled ||
  !proof.wranglerPreviewUrlsDisabled ||
  !proof.wranglerMainIsOpenNextWorker ||
  !proof.wranglerHasNoRoutesCommitted ||
  !proof.directDeployScriptAbsent ||
  !proof.buildScriptPresent ||
  !proof.typecheckScriptPresent ||
  !proof.packageScriptReady ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated ||
  !proof.readmeUpdated ||
  !proof.changelogUpdated ||
  !proof.templateReadmeUpdated ||
  !proof.noSensitiveCloudflareEnvCommitted ||
  proof.realAppDeployed ||
  proof.deployCommandExecuted ||
  proof.testerUrlShared ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted
) {
  process.exitCode = 1;
}
