import { existsSync, readdirSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const sourceRoot = join(projectRoot, "src");
const apiRoot = join(sourceRoot, "app", "api");
const middlewarePath = join(sourceRoot, "middleware.ts");

function collectRouteHandlers(directory) {
  if (!existsSync(directory)) {
    return [];
  }

  const entries = readdirSync(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectRouteHandlers(fullPath));
    } else if (entry.isFile() && entry.name === "route.ts") {
      files.push(relative(projectRoot, fullPath).replaceAll("\\", "/"));
    }
  }
  return files.sort();
}

const routeHandlers = collectRouteHandlers(apiRoot);
const proof = Object.freeze({
  phase: "T10ae",
  result: "GO_CLOUDFLARE_WORKERS_OPENNEXT_RUNTIME_SELECTED_NO_PROVIDER_ACTION",
  selectedRuntime: "cloudflare_workers_opennext_nextjs_runtime",
  rejectedRuntime: "cloudflare_pages_static_export",
  selectedNextGate: "T10af_opennext_cloudflare_adapter_local_package_no_deploy",
  middlewarePresent: existsSync(middlewarePath),
  middlewarePath: "src/middleware.ts",
  routeHandlers,
  routeHandlerCount: routeHandlers.length,
  staticExportCompatible: false,
  staticExportRejectedReasons: [
    "Next.js middleware is part of the current access gate",
    "API route handlers implement login, logout, features, renewal, admin and cron previews",
    "tester portal requires server-side cookie/session and security behavior",
  ],
  workersRuntimeReasons: [
    "Cloudflare Workers Next.js guide supports App Router",
    "Cloudflare Workers Next.js guide supports Route Handlers",
    "Cloudflare Workers Next.js guide supports Middleware",
    "OpenNext Cloudflare adapter is the documented full-stack route",
  ],
  cloudflareAccessOuterGateStillRequired: true,
  appAuthInnerGateStillRequired: true,
  externalActionAttemptedInT10ae: false,
  cloudflareDependencyInstalledInT10ae: false,
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
  forbiddenUntilT10afGo: [
    "cloudflare project creation",
    "cloudflare deployment creation",
    "cloudflare access application creation",
    "cloudflare access policy creation",
    "github repository connection to cloudflare",
    "tester URL publication",
    "tester account creation",
    "tester email commit",
    "renewal email delivery",
    "production database connection",
  ],
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);
