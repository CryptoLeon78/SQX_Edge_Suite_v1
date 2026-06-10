import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");

function read(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

const packageJson = JSON.parse(read("package.json"));
const wrangler = JSON.parse(read("wrangler.jsonc"));
const envExample = read(".env.example");
const devVarsExample = read(".dev.vars.example");
const gitignore = read(".gitignore");

const scripts = packageJson.scripts ?? {};
const forbiddenDeployFragments = [
  "wrangler deploy",
  "opennextjs-cloudflare deploy",
  "wrangler versions deploy",
  "pages deploy",
];

const safeLocalScripts = [
  "proof:cloudflare-provider-project-preflight",
  "proof:opennext-cloudflare-adapter",
  "proof:opennext-local-smoke",
  "proof:next-proxy-migration",
  "cf:build",
  "cf:preview",
  "cf:typegen",
];

const proof = Object.freeze({
  phase: "T10ai",
  result: "GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY",
  provider: "Cloudflare",
  selectedRuntime: "cloudflare_workers_opennext_nextjs_runtime",
  projectNameProposal: wrangler.name,
  workerNameProposal: wrangler.name,
  productionBranch: "main",
  testerBranch: "tester-preview",
  branchControlRequired: true,
  allowedTesterBranches: ["tester-preview"],
  accessApplicationRequiredBeforeAnyUrl: true,
  accessLoginMethod: "one-time-pin-or-equivalent-idp",
  testerEmailsStoredInProviderOnly: true,
  appAuthInnerGateStillRequired: true,
  deploymentCommandIntentionallyAbsent: true,
  allowedOperatorCommandsAfterExplicitApproval: [
    "npm install --no-package-lock",
    "npm run proof:cloudflare-provider-project-preflight",
    "npm run cf:build",
    "npx opennextjs-cloudflare preview",
    "npx wrangler whoami",
    "manual Cloudflare dashboard project/access setup after exact approval",
  ],
  forbiddenOperatorCommandsUntilExactApproval: [
    "npx wrangler deploy",
    "npm run deploy",
    "npx opennextjs-cloudflare deploy",
    "npx wrangler pages deploy",
    "cloudflare access application creation",
    "cloudflare access policy creation",
    "github repository connection to cloudflare",
    "tester URL publication",
  ],
  wranglerConfigReady: Boolean(
    wrangler.name === "sqx-edge-tester-portal-preview" &&
    wrangler.main === ".open-next/worker.js" &&
    wrangler.assets?.directory === ".open-next/assets" &&
    wrangler.assets?.binding === "ASSETS" &&
    Array.isArray(wrangler.compatibility_flags) &&
    wrangler.compatibility_flags.includes("nodejs_compat") &&
    wrangler.services?.[0]?.binding === "WORKER_SELF_REFERENCE" &&
    wrangler.services?.[0]?.service === wrangler.name
  ),
  wranglerConfigHasNoProviderBinding: !["account_id", "zone_id", "routes", "route", "custom_domain"].some((key) =>
    Object.prototype.hasOwnProperty.call(wrangler, key)
  ),
  safeLocalScriptsReady: safeLocalScripts.every((scriptName) => typeof scripts[scriptName] === "string"),
  deployScriptPublished: Object.keys(scripts).some((scriptName) => /(^|:)deploy($|:)/.test(scriptName)),
  forbiddenDeployFragmentsPresent: Object.values(scripts).some((script) =>
    forbiddenDeployFragments.some((fragment) => String(script).includes(fragment))
  ),
  envPlaceholdersOnly: [
    "AUTH_SECRET=\"replace-with-random-32-byte-secret\"",
    "TESTER_DB_URL=\"replace-with-private-database-url\"",
    "CRON_SECRET=\"replace-with-random-cron-secret\"",
    "EDGE_CONFIG=\"replace-with-vercel-edge-config-connection-string\"",
  ].every((pattern) => envExample.includes(pattern)),
  devVarsPlaceholderOnly: devVarsExample.trim() === "NEXTJS_ENV=development",
  generatedArtifactsIgnored: [".open-next/", ".wrangler/", ".dev.vars*", "!.dev.vars.example", "cloudflare-env.d.ts"].every(
    (pattern) => gitignore.includes(pattern)
  ),
  localVercelMetadataIgnored: gitignore.includes(".vercel/"),
  cloudflareProjectCreated: false,
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
  nextGate: "T10aj_cloudflare_project_shell_exact_approval_or_keep_local",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.wranglerConfigReady ||
  !proof.wranglerConfigHasNoProviderBinding ||
  !proof.safeLocalScriptsReady ||
  proof.deployScriptPublished ||
  proof.forbiddenDeployFragmentsPresent ||
  !proof.envPlaceholdersOnly ||
  !proof.devVarsPlaceholderOnly ||
  !proof.generatedArtifactsIgnored ||
  !proof.localVercelMetadataIgnored
) {
  process.exitCode = 1;
}
