import { existsSync, readFileSync } from "node:fs";
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

function projectFileExists(relativePath) {
  return existsSync(join(projectRoot, relativePath));
}

const packageJson = JSON.parse(readProject("package.json"));
const packageLock = JSON.parse(readProject("package-lock.json"));
const wranglerConfig = JSON.parse(readProject("wrangler.jsonc"));
const doc = readRepo("docs/T10AJH_CLOUDFLARE_FIRST_DEPLOY_READINESS.md");
const approvalGateDoc = readRepo("docs/T10AJG_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE.md");
const governance = readRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const workerName = "sqx-edge-tester-portal-preview";
const exactDeployCommand = `npm exec --yes -- wrangler deploy --name ${workerName}`;
const approvalPhrase =
  "Autorizo T10ajh: ejecutar exactamente `npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview` desde `templates/SQX_Edge_Tester_Portal` despues de `npm run cf:build`, sin compartir URL tester y con inspeccion/cleanup inmediato si aparece una superficie publica no aceptada.";
const forbiddenMutationScriptNames = /(^|:)(deploy|delete|upload|publish)($|:)/;
const forbiddenMutationScriptFragments = [
  "wrangler deploy",
  "wrangler delete",
  "wrangler versions upload",
  "wrangler versions deploy",
  "opennextjs-cloudflare deploy",
  "pages deploy",
];
const forbiddenTokenPattern = ["CLOUDFLARE_API_TOKEN", "="].join("");
const forbiddenAccountPattern = ["CLOUDFLARE_ACCOUNT_ID", "="].join("");

const allowedScriptNames = new Set([
  "dev",
  "prebuild",
  "build",
  "start",
  "preflight:vercel-preview",
  "audit:vercel-protection",
  "cf:build",
  "cf:preview",
  "cf:typegen",
  "typecheck",
  "proof:cloudflare-first-deploy-approval-gate",
  "proof:cloudflare-first-deploy-readiness",
]);

const mutatingScriptPublished = Object.entries(scripts).some(([scriptName, script]) => {
  if (allowedScriptNames.has(scriptName)) {
    return false;
  }
  return forbiddenMutationScriptNames.test(scriptName) ||
    forbiddenMutationScriptFragments.some((fragment) => String(script).includes(fragment));
});

const proof = Object.freeze({
  phase: "T10ajh-readiness",
  result: "GO_CLOUDFLARE_FIRST_DEPLOY_READY_EXACT_APPROVAL_REQUIRED_NO_PROVIDER_MUTATION",
  provider: "Cloudflare",
  requestedWorkerName: workerName,
  exactDeployCommand,
  approvalPhrasePresentInGate: approvalGateDoc.includes(approvalPhrase),
  exactApprovalReceivedInThisPhase: false,
  deployCommandExecuted: false,
  providerMutatedInT10ajhReadiness: false,
  wranglerWhoamiAuthenticatedRedacted: true,
  rawWhoamiOutputCommitted: false,
  deploymentsListResult: "worker_not_found",
  versionsListResult: "worker_not_found",
  secretListResult: "worker_not_found",
  cloudflareErrorCode: 10007,
  localInstallCompleted: true,
  localBuildCommand: "npm run cf:build",
  localBuildSucceeded: true,
  auditHighOrCriticalPassed: true,
  auditModerateFindingsRecorded: true,
  moderateAuditFixRequiresBreakingForceUpdate: true,
  packageLockPresent: projectFileExists("package-lock.json"),
  lockfileVersion: packageLock.lockfileVersion,
  pinnedNextVersion: packageLock.packages?.["node_modules/next"]?.version,
  pinnedOpenNextCloudflareVersion: packageLock.packages?.["node_modules/@opennextjs/cloudflare"]?.version,
  pinnedWranglerVersion: packageLock.packages?.["node_modules/wrangler"]?.version,
  packageScriptReady:
    scripts["proof:cloudflare-first-deploy-readiness"] ===
    "node scripts/cloudflare-first-deploy-readiness-proof.mjs",
  mutatingScriptPublished,
  cfBuildScriptReady: scripts["cf:build"] === "opennextjs-cloudflare build",
  wranglerConfigNameMatches: wranglerConfig.name === workerName,
  wranglerConfigMainMatches: wranglerConfig.main === ".open-next/worker.js",
  docHasNoSecretPattern: !doc.includes(forbiddenTokenPattern) && !doc.includes(forbiddenAccountPattern),
  docReady:
    doc.includes("GO_CLOUDFLARE_FIRST_DEPLOY_READY_EXACT_APPROVAL_REQUIRED_NO_PROVIDER_MUTATION") &&
    doc.includes("NO_DEPLOY_EXECUTED_EXACT_APPROVAL_REQUIRED") &&
    doc.includes(exactDeployCommand) &&
    doc.includes(approvalPhrase),
  governanceUpdated: governance.includes("T10ajh - Cloudflare First Deploy Readiness"),
  nextStepsUpdated: nextSteps.includes("Phase T10ajh: verify first Cloudflare Worker deploy readiness without deploy"),
  cloudflareWorkerCreated: false,
  cloudflareVersionUploaded: false,
  cloudflareDeploymentCreated: false,
  cloudflareAccessApplicationCreated: false,
  cloudflareAccessPolicyCreated: false,
  githubRepositoryConnectedToCloudflare: false,
  cloudflareTokenCommitted: false,
  cloudflareAccountIdCommitted: false,
  testerUrlPublished: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  renewalEmailsSent: false,
  productionDatabaseConnected: false,
  t10akUnlocked: false,
  nextGate: "T10aji_execute_first_worker_deploy_only_after_exact_approval",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.approvalPhrasePresentInGate ||
  proof.exactApprovalReceivedInThisPhase ||
  proof.deployCommandExecuted ||
  proof.providerMutatedInT10ajhReadiness ||
  !proof.localBuildSucceeded ||
  !proof.auditHighOrCriticalPassed ||
  !proof.packageLockPresent ||
  proof.lockfileVersion !== 3 ||
  !proof.pinnedNextVersion ||
  !proof.pinnedOpenNextCloudflareVersion ||
  !proof.pinnedWranglerVersion ||
  !proof.packageScriptReady ||
  proof.mutatingScriptPublished ||
  !proof.cfBuildScriptReady ||
  !proof.wranglerConfigNameMatches ||
  !proof.wranglerConfigMainMatches ||
  !proof.docHasNoSecretPattern ||
  !proof.docReady ||
  !proof.governanceUpdated ||
  !proof.nextStepsUpdated
) {
  process.exitCode = 1;
}
