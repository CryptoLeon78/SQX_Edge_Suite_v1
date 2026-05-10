import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10I_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const expectedProductionBranch = process.env.T10I_EXPECTED_PRODUCTION_BRANCH || "main";
const intendedPreviewBranch = process.env.T10I_PREVIEW_BRANCH || "tester-preview";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");
const reservedBranches = new Set(["main", "master", "production", "prod"]);

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10i",
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
      reason: ".vercel/project.json is required to prove the CLI default preview route",
      requiredNextAction: "Link the private tester portal working tree to the separated preview project"
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
      requiredNextAction: "Verify local Vercel token and team access before any deployment attempt"
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
    repo: git?.repo ? "present" : null,
    repoId: git?.repoId ? "present" : null,
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

if (reservedBranches.has(intendedPreviewBranch.toLowerCase())) {
  fail("NO_GO_PREVIEW_BRANCH_RESERVED", {
    intendedPreviewBranch,
    reason: "The preview branch must not be production-like",
    requiredNextAction: "Use a dedicated non-production branch such as tester-preview"
  }, 3);
}

const project = await vercelGet(`/v9/projects/${localProject.projectId}`, localProject);
const summary = summarizeProject(project);
const git = summarizeGit(project);
const protection = summarizeProtection(project);

if (summary.name !== expectedProjectName) {
  fail("NO_GO_WRONG_PREVIEW_PROJECT", {
    project: summary,
    expectedProjectName,
    requiredNextAction: "Relink the working tree to the separated preview project before any deployment"
  }, 5);
}

if (summary.live || summary.latestDeployment !== "none" || summary.domains !== 0) {
  fail("NO_GO_PROJECT_HAS_PUBLIC_SURFACE", {
    project: summary,
    requiredNextAction: "Remove deployment/domain surface before any deployment attempt"
  }, 6);
}

if (!git.linked || git.provider !== "github") {
  fail("NO_GO_GIT_SOURCE_NOT_LINKED", {
    project: summary,
    git,
    requiredNextAction: "Connect the separated preview project to the private tester portal GitHub repo"
  }, 7);
}

if ((git.productionBranch ?? "").toLowerCase() !== expectedProductionBranch.toLowerCase()) {
  fail("NO_GO_PRODUCTION_BRANCH_UNEXPECTED", {
    project: summary,
    git,
    expectedProductionBranch,
    requiredNextAction: "Correct Vercel branch tracking before any deployment attempt"
  }, 8);
}

if (git.previewBranchIsProduction) {
  fail("NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION", {
    project: summary,
    git,
    requiredNextAction: "Use a non-production preview branch before any deployment attempt"
  }, 9);
}

if (!protection.deploymentProtectionVerified) {
  fail("NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED", {
    project: summary,
    protection,
    requiredNextAction: "Enable or verify Vercel Deployment Protection before any deployment attempt"
  }, 10);
}

const approvedCommandShape = {
  command: "vercel deploy --force --yes --format json --skip-domain",
  cwd: "private tester portal working tree",
  requiredAbsentFlags: ["--prod", "--target"],
  requiredImmediateInspection: ["target === preview", "no production alias", "Deployment Protection remains active"],
  requiredRollbackOnMismatch: true
};

console.log(JSON.stringify({
  ok: true,
  phase: "T10i",
  status: "GO_CLI_DEFAULT_PREVIEW_ROUTE_READY",
  project: summary,
  git,
  protection,
  approvedCommandShape,
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "T10j may execute exactly one CLI default preview deployment, then inspect target=preview before any URL is shared"
}, null, 2));
