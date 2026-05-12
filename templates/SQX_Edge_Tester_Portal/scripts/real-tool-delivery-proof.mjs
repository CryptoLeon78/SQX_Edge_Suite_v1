import { existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const workerPath = resolve(root, "cloudflare", "worker-entry.js");
const wranglerPath = resolve(root, "wrangler.jsonc");
const manifestPath = resolve(root, ".local", "real-tool-delivery.local.json");
const CLOUDFLARE_ASSET_FILE_LIMIT_BYTES = 25 * 1024 * 1024;

function assert(condition, message, details = {}) {
  if (!condition) {
    console.error(JSON.stringify({ ok: false, phase: "TL10", message, details }, null, 2));
    process.exit(1);
  }
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

async function loadWorkerWithStubbedOpenNext() {
  const source = readFileSync(workerPath, "utf8").replace(
    'import openNextWorker from "../.open-next/worker.js";',
    'const openNextWorker = { fetch: async () => new Response("open-next-stub", { status: 404 }) };',
  );
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`;
  return import(moduleUrl);
}

const manifest = existsSync(manifestPath) ? readJson(manifestPath) : null;
assert(manifest, "real tool delivery manifest is missing; run npm run operator:prepare-real-tool-delivery first");

const wranglerConfig = readJson(wranglerPath);
assert(
  wranglerConfig.assets?.run_worker_first === true,
  "wrangler assets must run the Worker first so the internal ZIP asset cannot bypass the protected download handler",
);

const assetPath = resolve(root, manifest.assetRelativePath);
assert(existsSync(assetPath), "portable ZIP asset is missing from the ignored OpenNext assets directory", {
  assetPath,
});

const assetStats = statSync(assetPath);
assert(assetStats.size === manifest.sourceZipBytes, "portable ZIP asset size does not match the prepared manifest", {
  expectedBytes: manifest.sourceZipBytes,
  actualBytes: assetStats.size,
});
assert(
  assetStats.size <= CLOUDFLARE_ASSET_FILE_LIMIT_BYTES,
  "portable ZIP exceeds the Cloudflare Workers Assets individual file limit",
  {
    limitBytes: CLOUDFLARE_ASSET_FILE_LIMIT_BYTES,
    actualBytes: assetStats.size,
  },
);

const worker = await loadWorkerWithStubbedOpenNext();
const cookie = "__Host-sqx_tester_session=proof-session";
const accessEmail = "tester@example.test";
const env = {
  T4_DEMO_LOGIN_ENABLED: "true",
  T5_DEMO_TESTER_PRO_ENABLED: "true",
  ASSETS: {
    async fetch(request) {
      const url = new URL(request.url);
      if (url.pathname === "/downloads/SQX_Edge_Tool_Portable_Tester.zip") {
        return new Response("fakezip", {
          status: 200,
          headers: { "content-type": "application/octet-stream" },
        });
      }
      return new Response("not found", { status: 404 });
    },
  },
};

const unauthTool = await worker.default.fetch(new Request("https://example.test/tool"), env, {});
const accessLoginPage = await worker.default.fetch(
  new Request("https://example.test/login?next=/tool", {
    headers: { "Cf-Access-Authenticated-User-Email": accessEmail },
  }),
  env,
  {},
);
const accessLogin = await worker.default.fetch(
  new Request("https://example.test/api/auth/login", {
    method: "POST",
    headers: {
      "Cf-Access-Authenticated-User-Email": accessEmail,
      "content-type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ email: accessEmail, next: "/tool" }),
  }),
  env,
  {},
);
const accessMismatch = await worker.default.fetch(
  new Request("https://example.test/api/auth/login", {
    method: "POST",
    headers: {
      "Cf-Access-Authenticated-User-Email": accessEmail,
      "content-type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({ email: "other@example.test", next: "/tool" }),
  }),
  env,
  {},
);
const tool = await worker.default.fetch(new Request("https://example.test/tool", { headers: { cookie } }), env, {});
const download = await worker.default.fetch(
  new Request("https://example.test/download/sqx-edge-tool.zip", { headers: { cookie } }),
  env,
  {},
);
const missing = await worker.default.fetch(
  new Request("https://example.test/download/sqx-edge-tool.zip", { headers: { cookie } }),
  { ASSETS: { fetch: async () => new Response("missing", { status: 404 }) } },
  {},
);

const accessLoginPageBody = await accessLoginPage.text();
const toolBody = await tool.text();
const downloadBody = await download.text();
const result = {
  unauthToolStatus: unauthTool.status,
  unauthToolLocation: unauthTool.headers.get("location"),
  accessLoginPageStatus: accessLoginPage.status,
  accessLoginPageHasEmail: accessLoginPageBody.includes(accessEmail),
  accessLoginPageHidesCode: !accessLoginPageBody.includes("Access code"),
  accessLoginStatus: accessLogin.status,
  accessLoginLocation: accessLogin.headers.get("location"),
  accessLoginSetCookie: accessLogin.headers.get("set-cookie")?.includes("__Host-sqx_tester_session") || false,
  accessMismatchStatus: accessMismatch.status,
  accessMismatchLocation: accessMismatch.headers.get("location"),
  toolStatus: tool.status,
  toolHasDownload: toolBody.includes("Download portable ZIP"),
  downloadStatus: download.status,
  downloadType: download.headers.get("content-type"),
  downloadDisposition: download.headers.get("content-disposition"),
  downloadBody,
  missingStatus: missing.status,
  manifestBytes: manifest.sourceZipBytes,
  cloudflareAssetLimitBytes: CLOUDFLARE_ASSET_FILE_LIMIT_BYTES,
  runWorkerFirst: wranglerConfig.assets.run_worker_first,
};

assert([302, 303].includes(result.unauthToolStatus), "unauthenticated /tool did not redirect", result);
assert(result.unauthToolLocation === "/login?next=%2Ftool", "unauthenticated /tool redirect target is wrong", result);
assert(result.accessLoginPageStatus === 200, "Cloudflare Access-backed login page is not available", result);
assert(result.accessLoginPageHasEmail && result.accessLoginPageHidesCode, "Cloudflare Access-backed login page still asks for a separate code", result);
assert([302, 303].includes(result.accessLoginStatus), "Cloudflare Access-backed login did not redirect", result);
assert(result.accessLoginLocation === "/tool", "Cloudflare Access-backed login redirect target is wrong", result);
assert(result.accessLoginSetCookie, "Cloudflare Access-backed login did not create an SQX session", result);
assert(result.accessMismatchLocation === "/login?status=access_email_mismatch", "Cloudflare Access-backed login did not reject email mismatch", result);
assert(result.toolStatus === 200 && result.toolHasDownload, "authenticated /tool page is not ready", result);
assert(result.downloadStatus === 200, "authenticated protected download route is not serving the asset", result);
assert(result.downloadType === "application/zip", "protected download content type is wrong", result);
assert(
  result.downloadDisposition?.includes("SQX_Edge_Tool_Portable_Tester.zip"),
  "protected download filename is wrong",
  result,
);
assert(result.downloadBody === "fakezip", "protected download body did not come from ASSETS", result);
assert(result.missingStatus === 404, "missing asset fallback did not report pending package", result);

console.log(
  JSON.stringify(
    {
      ok: true,
      phase: "TL10",
      status: "GO_REAL_TOOL_DELIVERY_PATH_READY_NO_DEPLOY",
      result,
    },
    null,
    2,
  ),
);
