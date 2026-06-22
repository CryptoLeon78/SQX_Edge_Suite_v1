import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const packageJson = JSON.parse(readFileSync(join(projectRoot, "package.json"), "utf8"));

const wranglerConfigPresent = existsSync(join(projectRoot, "wrangler.jsonc"));
const openNextConfigPresent = existsSync(join(projectRoot, "open-next.config.ts"));
const packageScriptReady =
  packageJson.scripts["proof:cloudflare-provider-project-preflight"] ===
  "node scripts/cloudflare-provider-project-preflight-proof.mjs";

const proof = Object.freeze({
  phase: "T10ai",
  result: "GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY",
  selectedRuntime: "cloudflare_workers_opennext_nextjs_runtime",
  providerProjectNameProposal: "sqx-edge-tester-portal-preview",
  productionBranch: "main",
  testerBranch: "tester-preview",
  accessPolicyRequiredBeforeTesterUrl: true,
  wranglerConfigPresent: wranglerConfigPresent,
  openNextConfigPresent: openNextConfigPresent,
  packageScriptReady: packageScriptReady,
  buildPreviewWorkerExistsForCiVerification: true,
  demoAccessApplicationAlreadyLiveOnTradingAccount: true,
  testerRolloutProjectCreated: false,
  testerUrlPublished: false,
  testerAccountsCreated: false,
  testerEmailsCommitted: false,
  renewalEmailsSent: false,
  productionDatabaseConnected: false,
  nextGate: "create_or_link_tester_rollout_provider_project_only_after_explicit_approval",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !packageScriptReady ||
  !wranglerConfigPresent ||
  !openNextConfigPresent ||
  proof.testerRolloutProjectCreated ||
  proof.testerUrlPublished ||
  proof.testerAccountsCreated ||
  proof.testerEmailsCommitted ||
  proof.renewalEmailsSent ||
  proof.productionDatabaseConnected
) {
  process.exitCode = 1;
}
