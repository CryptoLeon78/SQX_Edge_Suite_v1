import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const projectPath = join(root, ".vercel", "project.json");
const acceptedDeploymentTypes = new Set(["prod_deployment_urls_and_all_previews", "all", "preview"]);
const reservedBranches = new Set(["main", "master", "production", "prod"]);
const intendedPreviewBranch = process.env.T9F_PREVIEW_BRANCH || "tester-preview";

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
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

function summarizeProject(project) {
  return {
    name: project.name,
    framework: project.framework,
    live: Boolean(project.live),
    latestDeployment: project.latestDeployment ? "present" : "none",
    domains: Array.isArray(project.domains) ? project.domains.length : 0
  };
}

function summarizeGit(project) {
  const gitRepository = project.gitRepository ?? null;
  const link = project.link ?? null;
  const linked = Boolean(gitRepository || link);
  const productionBranch = project.productionBranch
    ?? gitRepository?.productionBranch
    ?? link?.productionBranch
    ?? null;

  return {
    linked,
    provider: gitRepository?.type ?? link?.type ?? null,
    repo: linked ? "linked" : null,
    source: gitRepository ? "gitRepository" : link ? "link" : null,
    productionBranch,
    intendedPreviewBranch
  };
}

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T9f",
    status,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    ...body
  }, null, 2));
  process.exit(exitCode);
}

if (!existsSync(projectPath)) {
  fail("NO_GO_PROJECT_NOT_LINKED", {
    reason: ".vercel/project.json is required locally to prove the preview path",
    requiredNextAction: "Link the private tester portal project before any preview proof"
  }, 1);
}

const localProject = readJson(projectPath);
const token = process.env.VERCEL_TOKEN;

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel project protection and Git integration",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

if (reservedBranches.has(intendedPreviewBranch.toLowerCase())) {
  fail("NO_GO_PREVIEW_BRANCH_RESERVED", {
    projectName: localProject.projectName,
    intendedPreviewBranch,
    reason: "The intended preview branch must not be a production-like branch name",
    requiredNextAction: "Use a dedicated non-production branch such as tester-preview"
  }, 3);
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
  fail("NO_GO_API_PROJECT_AUDIT_FAILED", {
    projectName: localProject.projectName,
    httpStatus: response.status,
    requiredNextAction: "Verify Vercel token scope and project access before any deploy attempt"
  }, 4);
}

const project = await response.json();
const protection = detectProtection(project);
const protectionVerified = protection.ssoProtectionEnabled || protection.passwordProtectionEnabled;
const git = summarizeGit(project);
const productionBranch = git.productionBranch || "main";
const previewBranchIsProduction = intendedPreviewBranch.toLowerCase() === productionBranch.toLowerCase();

if (!protectionVerified) {
  fail("NO_GO_PROTECTION_NOT_VERIFIED", {
    project: summarizeProject(project),
    protection,
    git,
    reason: "Deployment Protection must be verified before proving any preview path",
    requiredNextAction: "Enable Vercel Authentication or Password Protection first"
  }, 5);
}

if (!git.linked) {
  fail("NO_GO_GIT_PREVIEW_NOT_CONFIGURED", {
    project: summarizeProject(project),
    protection,
    git,
    reason: "The project is not Git-connected, so a PR/branch preview path cannot be proven without using the unsafe local CLI deploy route",
    requiredNextAction: "Connect a private tester portal repository to Vercel and use a non-production preview branch"
  }, 6);
}

if (previewBranchIsProduction) {
  fail("NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION", {
    project: summarizeProject(project),
    protection,
    git,
    reason: "The intended preview branch matches the Vercel production branch",
    requiredNextAction: "Set T9F_PREVIEW_BRANCH to a non-production branch before any preview attempt"
  }, 7);
}

console.log(JSON.stringify({
  ok: true,
  phase: "T9f",
  status: "GO_GIT_PREVIEW_PATH_READY",
  project: summarizeProject(project),
  protection,
  git,
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "Open or update the non-production preview branch through Git integration, then inspect the generated deployment target before sharing any URL"
}, null, 2));
