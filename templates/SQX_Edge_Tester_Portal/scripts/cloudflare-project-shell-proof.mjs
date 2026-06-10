import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const repoRoot = join(projectRoot, "..", "..");

function readFromProject(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readFromRepo(relativePath) {
  return readFileSync(join(repoRoot, relativePath), "utf8");
}

const packageJson = JSON.parse(readFromProject("package.json"));
const wrangler = JSON.parse(readFromProject("wrangler.jsonc"));
const t10ajDoc = readFromRepo("docs/T10AJ_CLOUDFLARE_PROJECT_SHELL.md");
const governance = readFromRepo("docs/PROJECT_GOVERNANCE.md");
const nextSteps = readFromRepo("docs/MODULARIZATION_NEXT_STEPS.md");
const scripts = packageJson.scripts ?? {};

const forbiddenDeployFragments = [
  "wrangler deploy",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
];

const proof = Object.freeze({
  phase: "T10aj",
  result: "NO_GO_CLOUDFLARE_PROJECT_SHELL_NOT_VERIFIED_NO_AUTH_NO_DEPLOY_PATH",
  provider: "Cloudflare",
  requestedProjectShellName: "sqx-edge-tester-portal-preview",
  userExactApprovalCaptured: true,
  approvedAction: "create_or_verify_cloudflare_project_shell_only",
  forbiddenActionsStillForbidden: [
    "cloudflare deployment creation",
    "cloudflare access application creation",
    "cloudflare access policy creation",
    "tester URL publication",
    "tester account creation",
    "tester email commit",
  ],
  localWranglerWhoamiResult: "not_authenticated",
  cloudflareApiTokenPresentLocally: false,
  cloudflareAccountIdPresentLocally: false,
  noDeployShellCreationPathVerified: false,
  wranglerSetupIsLocalConfigurationOnly: true,
  wranglerDeployWouldCreateDeployment: true,
  dryRunDoesNotCreateProviderShell: true,
  wranglerConfigNameMatchesRequestedShell: wrangler.name === "sqx-edge-tester-portal-preview",
  packageScriptReady: scripts["proof:cloudflare-project-shell"] === "node scripts/cloudflare-project-shell-proof.mjs",
  deployScriptPublished: Object.keys(scripts).some((scriptName) => /(^|:)deploy($|:)/.test(scriptName)),
  forbiddenDeployFragmentsPresent: Object.values(scripts).some((script) =>
    forbiddenDeployFragments.some((fragment) => String(script).includes(fragment))
  ),
  t10ajDocPresent: existsSync(join(repoRoot, "docs/T10AJ_CLOUDFLARE_PROJECT_SHELL.md")),
  t10ajDocHasExactApproval: t10ajDoc.includes("sin deploy, sin Access policy"),
  t10xxPlanMemorized: [
    "T10ajb",
    "T10ak",
    "T10al",
    "T10am",
    "T10an",
    "T11",
    "T12",
  ].every((gate) => t10ajDoc.includes(gate) && nextSteps.includes(gate)),
  governanceUpdated: governance.includes("T10aj - Cloudflare Project Shell Gate"),
  cloudflareProjectCreated: false,
  cloudflareProjectVerified: false,
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
  nextGate: "T10ajb_cloudflare_auth_or_manual_shell_verification_no_deploy",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.wranglerConfigNameMatchesRequestedShell ||
  !proof.packageScriptReady ||
  proof.deployScriptPublished ||
  proof.forbiddenDeployFragmentsPresent ||
  !proof.t10ajDocPresent ||
  !proof.t10ajDocHasExactApproval ||
  !proof.t10xxPlanMemorized ||
  !proof.governanceUpdated
) {
  process.exitCode = 1;
}
