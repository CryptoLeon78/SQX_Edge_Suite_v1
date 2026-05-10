import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10K_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const expectedProductionBranch = process.env.T10K_EXPECTED_PRODUCTION_BRANCH || "main";
const intendedPreviewBranch = process.env.T10K_PREVIEW_BRANCH || "tester-preview";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10k",
    status,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    ...body
  }, null, 2));
  process.exit(exitCode);
}

function readLocalProject() {
  if (!existsSync(projectPath)) {
    fail("NO_GO_PROJECT_NOT_LINKED_LOCALLY", {
      reason: ".vercel/project.json is required to prove the T10k rollback cleanup",
      requiredNextAction: "Relink the private tester portal working tree to the separated preview project"
    }, 1);
  }
  return JSON.parse(readFileSync(projectPath, "utf8"));
}

async function vercelGet(path, localProject) {
  const url = new URL(`https://api.vercel.com${path}`);
  if (localProject.orgId) {
    url.searchParams.set("teamId", localProject.orgId);
  }
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json"
    }
  });
  if (!response.ok) {
    fail("NO_GO_VERCEL_API_FAILED", {
      httpStatus: response.status,
      apiPath: path,
      requiredNextAction: "Verify local Vercel token and team access before any further route investigation"
    }, 4);
  }
  return response.json();
}

function summarizeProject(project) {
  return {
    id: project.id ? "present" : "missing",
    name: project.name,
    live: Boolean(project.live),
    latestDeployment: project.latestDeployment ? "present" : "none",
    domains: Array.isArray(project.domains) ? project.domains.length : 0
  };
}

function summarizeGit(project) {
  const git = project.gitRepository ?? project.link ?? null;
  const productionBranch = project.productionBranch ?? project.link?.productionBranch ?? project.gitRepository?.productionBranch ?? null;
  return {
    linked: Boolean(git),
    provider: git?.type ?? null,
    productionBranch,
    intendedPreviewBranch,
    previewBranchIsProduction: Boolean(productionBranch) && productionBranch.toLowerCase() === intendedPreviewBranch.toLowerCase()
  };
}

function summarizeProtection(project) {
  return {
    ssoDeploymentType: project.ssoProtection?.deploymentType ?? null,
    passwordDeploymentType: project.passwordProtection?.deploymentType ?? null,
    deploymentProtectionVerified: Boolean(project.ssoProtection?.deploymentType || project.passwordProtection?.deploymentType)
  };
}

const localProject = readLocalProject();

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel project settings",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

const project = await vercelGet(`/v9/projects/${localProject.projectId}`, localProject);
const summary = summarizeProject(project);
const git = summarizeGit(project);
const protection = summarizeProtection(project);

if (summary.name !== expectedProjectName) {
  fail("NO_GO_WRONG_PREVIEW_PROJECT", {
    project: summary,
    expectedProjectName,
    requiredNextAction: "Relink the working tree to the separated preview project before further investigation"
  }, 5);
}

if (summary.live || summary.latestDeployment !== "none" || summary.domains !== 0) {
  fail("NO_GO_ROLLBACK_NOT_CLEAN", {
    project: summary,
    requiredNextAction: "Remove deployment/domain surface before continuing"
  }, 6);
}

if (!git.linked || git.provider !== "github") {
  fail("NO_GO_GIT_SOURCE_NOT_LINKED", {
    project: summary,
    git,
    requiredNextAction: "Reconnect the separated preview project to the private tester portal GitHub repo"
  }, 7);
}

if ((git.productionBranch ?? "").toLowerCase() !== expectedProductionBranch.toLowerCase()) {
  fail("NO_GO_PRODUCTION_BRANCH_UNEXPECTED", {
    project: summary,
    git,
    expectedProductionBranch,
    requiredNextAction: "Correct Vercel branch tracking before another deployment attempt"
  }, 8);
}

if (git.previewBranchIsProduction) {
  fail("NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION", {
    project: summary,
    git,
    requiredNextAction: "Use a non-production preview branch before another deployment attempt"
  }, 9);
}

if (!protection.deploymentProtectionVerified) {
  fail("NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED", {
    project: summary,
    protection,
    requiredNextAction: "Enable or verify Vercel Deployment Protection before another deployment attempt"
  }, 10);
}

console.log(JSON.stringify({
  ok: true,
  phase: "T10k",
  status: "GO_CLI_DEFAULT_PREVIEW_ROLLBACK_CLEAN",
  project: summary,
  git,
  protection,
  lastAttempt: {
    commandShape: "vercel deploy --force --yes --format json",
    requestedRoute: "CLI default preview",
    observedTarget: "production",
    readyState: "ERROR",
    guardStatus: "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
    aliasSurfaceObservedBeforeRemoval: true,
    rollbackStatus: "removed"
  },
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "T10l must investigate or replace the Vercel route without another deployment attempt"
}, null, 2));
