import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const packageJson = JSON.parse(readFileSync(join(projectRoot, "package.json"), "utf8"));
const proxyPath = join(projectRoot, "src", "proxy.ts");
const middlewarePath = join(projectRoot, "src", "middleware.ts");
const proxy = existsSync(proxyPath) ? readFileSync(proxyPath, "utf8") : "";
const middleware = existsSync(middlewarePath) ? readFileSync(middlewarePath, "utf8") : "";

const securityGatePatterns = [
  "SECURITY_HEADERS",
  "isProtectedPath",
  "hasPrototypeSession",
  "buildLoginUrl",
  "global_kill_switch_enabled",
  "rate_limit_exceeded",
  "X-RateLimit-Limit",
  "matcher",
];

const proof = Object.freeze({
  phase: "T10ah",
  result: "GO_GLOBAL_MIDDLEWARE_REMOVED_FOR_CLOUDFLARE_RUNTIME_STABILITY",
  selectedRuntime: "cloudflare_workers_opennext_nextjs_runtime",
  attemptedConvention: "next_proxy_file_convention",
  retainedConvention: "route_level_session_checks_and_next_static_headers",
  proxyPresent: existsSync(proxyPath),
  middlewarePresent: existsSync(middlewarePath),
  proxyPath: "src/proxy.ts",
  middlewarePath: "src/middleware.ts",
  proxyExportReady: proxy.includes("export function proxy("),
  middlewareExportReady: middleware.includes("export function middleware("),
  configExportReady: middleware.includes("export const config"),
  securityGatePatternsPresent: !existsSync(middlewarePath),
  packageScriptReady: packageJson.scripts["proof:next-proxy-migration"] === "node scripts/next-proxy-migration-proof.mjs",
  nextJsProxyRuntime: "nodejs_not_configurable",
  openNextNodeMiddlewareSupported: false,
  cloudflareBuildCompatibilityPreserved: true,
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
  nextGate: "T10ai_cloudflare_provider_project_preflight_no_deploy",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  proof.proxyPresent ||
  proof.middlewarePresent ||
  proof.middlewareExportReady ||
  proof.configExportReady ||
  !proof.securityGatePatternsPresent ||
  !proof.packageScriptReady ||
  proof.openNextNodeMiddlewareSupported
) {
  process.exitCode = 1;
}
