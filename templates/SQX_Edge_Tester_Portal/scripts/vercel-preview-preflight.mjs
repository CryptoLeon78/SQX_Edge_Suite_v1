import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();

function read(relativePath) {
  return readFileSync(join(root, relativePath), "utf8");
}

function assertContains(text, pattern, label) {
  if (!text.includes(pattern)) {
    throw new Error(`${label} is missing ${pattern}`);
  }
}

const envExample = read(".env.example");
const vercelJson = JSON.parse(read("vercel.json"));
const gitignore = read(".gitignore");
const securityHardening = read("src/lib/security-hardening.ts");
const deploymentProtection = read("src/lib/deployment-protection.ts");
const workerEntry = read("cloudflare/worker-entry.js");

for (const pattern of [
  'T4_DEMO_LOGIN_ENABLED="false"',
  'T5_DEMO_TESTER_PRO_ENABLED="false"',
  'T7_DEMO_ADMIN_CONSOLE_ENABLED="false"',
  'T8_GLOBAL_KILL_SWITCH_ENABLED="false"',
  'T8_RATE_LIMIT_ENABLED="false"',
  'T8_RATE_LIMIT_MAX_REQUESTS="30"',
  'T8_RATE_LIMIT_WINDOW_SECONDS="60"'
]) {
  assertContains(envExample, pattern, ".env.example");
}

for (const pattern of [
  "T8_GLOBAL_KILL_SWITCH_ENABLED",
  "T8_RATE_LIMIT_ENABLED",
  "globalKillSwitch",
  "evaluateRateLimit",
  "rate_limit_exceeded",
  "buildDemoVisibleWatermark"
]) {
  assertContains(securityHardening, pattern, "security-hardening.ts");
}

for (const pattern of [
  "DEPLOYMENT_PROTECTION_CHECKLIST",
  "Vercel Deployment Protection enabled",
  "externalActionAllowed: false"
]) {
  assertContains(deploymentProtection, pattern, "deployment-protection.ts");
}

for (const pattern of [
  "SECURITY_HEADERS"
]) {
  assertContains(workerEntry, pattern, "cloudflare/worker-entry.js");
}

if (vercelJson.framework !== "nextjs") {
  throw new Error("vercel.json must keep framework=nextjs");
}

if (!Array.isArray(vercelJson.crons) || vercelJson.crons.length === 0) {
  throw new Error("vercel.json must keep cron definitions for expiry dry-run checks");
}

if (existsSync(join(root, ".vercel", "project.json")) && !gitignore.includes(".vercel")) {
  throw new Error(".vercel/project.json is local machine state and .gitignore must include .vercel");
}

console.log(JSON.stringify({
  ok: true,
  phase: "T9b",
  mode: "protected-preview-preflight",
  externalDeployAllowedOnlyAfter: [
    "valid Vercel authentication",
    "Deployment Protection verified in Vercel project settings",
    "preview command verified not to alias production",
    "no tester invites or renewal emails",
    "preview URL kept out of git"
  ],
  recommendedDeployCommand: "manual dashboard/API preview after Deployment Protection verification"
}, null, 2));
