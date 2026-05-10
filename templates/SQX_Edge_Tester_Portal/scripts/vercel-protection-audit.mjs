import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const projectPath = join(root, ".vercel", "project.json");
const acceptedDeploymentTypes = new Set(["prod_deployment_urls_and_all_previews", "all", "preview"]);

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function sanitizeProject(project) {
  return {
    name: project.name,
    framework: project.framework,
    live: Boolean(project.live),
    latestDeployment: project.latestDeployment ? "present" : "none",
    domains: Array.isArray(project.domains) ? project.domains.length : 0
  };
}

function detectProtection(project) {
  const ssoProtection = project.ssoProtection ?? null;
  const passwordProtection = project.passwordProtection ?? null;
  const ssoType = ssoProtection?.deploymentType ?? null;
  const passwordType = passwordProtection?.deploymentType ?? null;

  return {
    ssoProtectionEnabled: Boolean(ssoProtection && acceptedDeploymentTypes.has(ssoType)),
    ssoDeploymentType: ssoType,
    passwordProtectionEnabled: Boolean(passwordProtection && acceptedDeploymentTypes.has(passwordType)),
    passwordDeploymentType: passwordType
  };
}

if (!existsSync(projectPath)) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T9c",
    status: "NO_GO_PROJECT_NOT_LINKED",
    reason: ".vercel/project.json is required locally to audit the linked Vercel project",
    externalDeployAllowed: false
  }, null, 2));
  process.exit(1);
}

const localProject = readJson(projectPath);
const token = process.env.VERCEL_TOKEN;

if (!token) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T9c",
    status: "NO_GO_PROTECTION_NOT_VERIFIED",
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is not available to query project protection settings through the Vercel API",
    requiredProtection: "ssoProtection or passwordProtection with deploymentType preview, prod_deployment_urls_and_all_previews, or all",
    manualFallback: "Verify Settings > Deployment Protection in Vercel dashboard before any deploy retry",
    externalDeployAllowed: false
  }, null, 2));
  process.exit(2);
}

const url = new URL(`https://api.vercel.com/v9/projects/${localProject.projectId}`);
url.searchParams.set("teamId", localProject.orgId);

const response = await fetch(url, {
  headers: {
    Authorization: `Bearer ${token}`,
    Accept: "application/json"
  }
});

if (!response.ok) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T9c",
    status: "NO_GO_API_PROJECT_AUDIT_FAILED",
    projectName: localProject.projectName,
    httpStatus: response.status,
    externalDeployAllowed: false
  }, null, 2));
  process.exit(3);
}

const project = await response.json();
const protection = detectProtection(project);
const projectSummary = sanitizeProject(project);
const protectionVerified = protection.ssoProtectionEnabled || protection.passwordProtectionEnabled;

console.log(JSON.stringify({
  ok: protectionVerified,
  phase: "T9c",
  status: protectionVerified ? "GO_PROTECTION_VERIFIED" : "NO_GO_PROTECTION_NOT_VERIFIED",
  project: projectSummary,
  protection,
  requiredNextAction: protectionVerified
    ? "Use preview-only deploy path and inspect target before sharing any URL"
    : "Enable Vercel Authentication or Password Protection before any deploy retry",
  externalDeployAllowed: protectionVerified
}, null, 2));

process.exit(protectionVerified ? 0 : 4);
