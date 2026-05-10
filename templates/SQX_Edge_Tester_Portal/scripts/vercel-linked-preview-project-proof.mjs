import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10G_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const expectedGitOrg = process.env.T10G_GIT_ORG || "CryptoLeon78";
const expectedGitRepo = process.env.T10G_GIT_REPO || "SQX_Edge_Tester_Portal";
const expectedProductionBranch = process.env.T10G_EXPECTED_PRODUCTION_BRANCH || "main";
const intendedPreviewBranch = process.env.T10G_PREVIEW_BRANCH || "tester-preview";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10g",
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
      reason: ".vercel/project.json is required to prove the separated linked preview project",
      requiredNextAction: "Run vercel link against the separated preview project before this proof"
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
      requiredNextAction: "Verify local Vercel token/team access before any preview deployment"
    }, 4);
  }
  return response.json();
}

function summarizeProject(project) {
  return {
    id: project.id ? "present" : "missing",
    name: project.name,
    framework: project.framework ?? null,
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
    source: project.gitRepository ? "gitRepository" : project.link ? "link" : null,
    provider: git?.type ?? null,
    org: git?.org ?? git?.repoOwner ?? null,
    repo: git?.repo ? "present" : null,
    repoId: git?.repoId ? "present" : null,
    repoMatchesExpected: git?.org === expectedGitOrg && git?.repo === expectedGitRepo,
    productionBranch,
    intendedPreviewBranch,
    previewBranchIsProduction: Boolean(productionBranch) && productionBranch.toLowerCase() === intendedPreviewBranch.toLowerCase()
  };
}

function summarizeProtection(project) {
  return {
    ssoDeploymentType: project.ssoProtection?.deploymentType ?? null,
    passwordDeploymentType: project.passwordProtection?.deploymentType ?? null,
    ssoEnabled: Boolean(project.ssoProtection?.deploymentType),
    passwordEnabled: Boolean(project.passwordProtection?.deploymentType),
    deploymentProtectionVerified: Boolean(project.ssoProtection?.deploymentType || project.passwordProtection?.deploymentType)
  };
}

const localProject = readLocalProject();

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel project Git settings",
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
    requiredNextAction: "Relink the local private tester portal working tree to the separated preview project"
  }, 3);
}

if (summary.live || summary.latestDeployment !== "none" || summary.domains !== 0) {
  fail("NO_GO_PROJECT_HAS_PUBLIC_SURFACE", {
    project: summary,
    requiredNextAction: "Remove deployment/domain surface before continuing tester preview setup"
  }, 5);
}

if (!git.linked || git.provider !== "github" || !git.repoMatchesExpected) {
  fail("NO_GO_GIT_LINK_NOT_PRIVATE_TESTER_PORTAL", {
    project: summary,
    git,
    expectedGitOrg,
    expectedGitRepo,
    requiredNextAction: "Connect the separated Vercel project to the private tester portal repository"
  }, 6);
}

if ((git.productionBranch ?? "").toLowerCase() !== expectedProductionBranch.toLowerCase()) {
  fail("NO_GO_PRODUCTION_BRANCH_UNEXPECTED", {
    project: summary,
    git,
    expectedProductionBranch,
    requiredNextAction: "Set or verify production branch before any preview deployment"
  }, 7);
}

if (git.previewBranchIsProduction) {
  fail("NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION", {
    project: summary,
    git,
    requiredNextAction: "Use a non-production branch before any preview deployment"
  }, 8);
}

if (!protection.deploymentProtectionVerified) {
  fail("NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED", {
    project: summary,
    protection,
    requiredNextAction: "Enable or verify Vercel Deployment Protection before any preview deployment"
  }, 9);
}

console.log(JSON.stringify({
  ok: true,
  phase: "T10g",
  status: "GO_LINKED_PREVIEW_PROJECT_READY",
  project: summary,
  git,
  protection,
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "T10h may execute exactly one protected preview deployment with immediate target inspection before any URL is shared"
}, null, 2));
