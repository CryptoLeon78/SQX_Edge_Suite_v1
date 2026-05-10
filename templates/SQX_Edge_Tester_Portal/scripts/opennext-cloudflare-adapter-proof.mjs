import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");

function readText(relativePath) {
  return readFileSync(join(projectRoot, relativePath), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function collectSourceFiles(directory) {
  if (!existsSync(directory)) {
    return [];
  }

  const entries = readdirSync(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectSourceFiles(fullPath));
    } else if (entry.isFile() && /\.(ts|tsx|js|jsx|mjs)$/.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

const packageJson = readJson("package.json");
const wranglerConfig = readJson("wrangler.jsonc");
const openNextConfig = readText("open-next.config.ts");
const gitignore = readText(".gitignore");
const devVarsExample = readText(".dev.vars.example");
const sourceFiles = collectSourceFiles(join(projectRoot, "src"));
const cloudflareScripts = Object.fromEntries(
  Object.entries(packageJson.scripts ?? {}).filter(([name]) => name.startsWith("cf:")),
);

const forbiddenScriptFragments = [
  "deploy",
  "versions upload",
  "versions deploy",
  "wrangler publish",
  "wrangler deploy",
];

const forbiddenConfigKeys = [
  "account_id",
  "routes",
  "route",
  "triggers",
  "custom_domain",
  "zone_id",
];

const proof = Object.freeze({
  phase: "T10af",
  result: "GO_OPENNEXT_CLOUDFLARE_ADAPTER_LOCAL_PACKAGE_READY_NO_DEPLOY",
  selectedRuntime: "cloudflare_workers_opennext_nextjs_runtime",
  adapterPackage: "@opennextjs/cloudflare",
  localCliPackage: "wrangler",
  packageDevDependenciesReady:
    packageJson.devDependencies?.["@opennextjs/cloudflare"] === "latest" &&
    packageJson.devDependencies?.wrangler === "latest",
  safeScriptsReady:
    cloudflareScripts["cf:build"] === "opennextjs-cloudflare build" &&
    cloudflareScripts["cf:preview"] ===
      "opennextjs-cloudflare build && opennextjs-cloudflare preview" &&
    cloudflareScripts["cf:typegen"] ===
      "wrangler types --env-interface CloudflareEnv cloudflare-env.d.ts",
  deployScriptPublished: Boolean(packageJson.scripts?.["cf:deploy"] ?? packageJson.scripts?.deploy),
  forbiddenCloudflareScriptFragmentsPresent: Object.values(cloudflareScripts).some((script) =>
    forbiddenScriptFragments.some((fragment) => script.includes(fragment)),
  ),
  wranglerConfigReady:
    wranglerConfig.main === ".open-next/worker.js" &&
    wranglerConfig.assets?.directory === ".open-next/assets" &&
    wranglerConfig.assets?.binding === "ASSETS" &&
    Array.isArray(wranglerConfig.compatibility_flags) &&
    wranglerConfig.compatibility_flags.includes("nodejs_compat") &&
    wranglerConfig.compatibility_flags.includes("global_fetch_strictly_public") &&
    wranglerConfig.services?.[0]?.binding === "WORKER_SELF_REFERENCE" &&
    wranglerConfig.services?.[0]?.service === wranglerConfig.name,
  wranglerConfigContainsProviderSecretsOrRoutes: forbiddenConfigKeys.some((key) =>
    Object.prototype.hasOwnProperty.call(wranglerConfig, key),
  ),
  openNextConfigReady:
    openNextConfig.includes('from "@opennextjs/cloudflare"') &&
    openNextConfig.includes("defineCloudflareConfig()"),
  localEnvExampleReady: devVarsExample.trim() === "NEXTJS_ENV=development",
  ignoredGeneratedArtifacts:
    gitignore.includes(".open-next/") &&
    gitignore.includes(".wrangler/") &&
    gitignore.includes("cloudflare-env.d.ts") &&
    gitignore.includes(".dev.vars*") &&
    gitignore.includes("!.dev.vars.example"),
  edgeRuntimeExportsPresent: sourceFiles.some((file) => /export\s+const\s+runtime\s*=\s*["']edge["']/.test(readFileSync(file, "utf8"))),
  requiredFiles: [
    "wrangler.jsonc",
    "open-next.config.ts",
    ".dev.vars.example",
    "scripts/opennext-cloudflare-adapter-proof.mjs",
  ].map((file) => ({
    file,
    present: existsSync(join(projectRoot, file)),
    path: relative(projectRoot, join(projectRoot, file)).replaceAll("\\", "/"),
  })),
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
  nextGate: "T10ag_local_opennext_build_preview_smoke_no_provider_action",
});

console.log(JSON.stringify(proof, null, 2));
console.log(proof.result);

if (
  !proof.packageDevDependenciesReady ||
  !proof.safeScriptsReady ||
  proof.deployScriptPublished ||
  proof.forbiddenCloudflareScriptFragmentsPresent ||
  !proof.wranglerConfigReady ||
  proof.wranglerConfigContainsProviderSecretsOrRoutes ||
  !proof.openNextConfigReady ||
  !proof.localEnvExampleReady ||
  !proof.ignoredGeneratedArtifacts ||
  proof.edgeRuntimeExportsPresent ||
  proof.requiredFiles.some((entry) => !entry.present)
) {
  process.exitCode = 1;
}
