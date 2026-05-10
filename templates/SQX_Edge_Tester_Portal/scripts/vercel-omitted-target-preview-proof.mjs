import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const projectPath = join(root, ".vercel", "project.json");
const intendedPreviewBranch = process.env.T10E_PREVIEW_BRANCH || "tester-preview";
const expectedProductionBranch = process.env.T10E_EXPECTED_PRODUCTION_BRANCH || "main";
const reservedBranches = new Set(["main", "master", "production", "prod"]);

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10e",
    status,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    ...body
  }, null, 2));
  process.exit(exitCode);
}

async function fetchProject(localProject, token) {
  const urls = [];
  const withTeam = new URL(`https://api.vercel.com/v9/projects/${localProject.projectId}`);
  if (localProject.orgId) {
    withTeam.searchParams.set("teamId", localProject.orgId);
    urls.push(withTeam);
  }
  urls.push(new URL(`https://api.vercel.com/v9/projects/${localProject.projectId}`));

  let lastStatus = null;
  for (const url of urls) {
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json"
      }
    });
    lastStatus = response.status;
    if (response.ok) {
      return response.json();
    }
    if (response.status !== 404) {
      break;
    }
  }

  fail("NO_GO_API_PROJECT_AUDIT_FAILED", {
    projectName: localProject.projectName,
    httpStatus: lastStatus,
    requiredNextAction: "Verify Vercel token scope and project access before any preview deployment"
  }, 4);
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
    repoId: gitRepository?.repoId || link?.repoId ? "present" : "missing",
    source: gitRepository ? "gitRepository" : link ? "link" : null,
    productionBranch,
    intendedPreviewBranch
  };
}

function buildPreviewPayload(project, git) {
  return {
    name: project.name,
    project: project.id,
    gitSource: {
      type: git.provider,
      ref: intendedPreviewBranch,
      repo: git.repo,
      repoId: git.repoId
    },
    meta: {
      phase: "T10e",
      omittedTargetForPreview: true,
      externalDeployAttempted: false,
      targetInspectionRequiredBeforeUrlShare: true
    }
  };
}

if (!existsSync(projectPath)) {
  fail("NO_GO_PROJECT_NOT_LINKED", {
    reason: ".vercel/project.json is required locally to prove the omitted-target preview path",
    requiredNextAction: "Link the tester portal project locally before running this proof"
  }, 1);
}

const localProject = readJson(projectPath);
const token = process.env.VERCEL_TOKEN;

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel project Git settings",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

if (reservedBranches.has(intendedPreviewBranch.toLowerCase())) {
  fail("NO_GO_PREVIEW_BRANCH_RESERVED", {
    projectName: localProject.projectName,
    intendedPreviewBranch,
    reason: "The preview branch must not be production-like",
    requiredNextAction: "Use a dedicated non-production branch such as tester-preview"
  }, 3);
}

const project = await fetchProject(localProject, token);
const git = summarizeGit(project);
const productionBranch = git.productionBranch || expectedProductionBranch;
const previewBranchIsProduction = intendedPreviewBranch.toLowerCase() === productionBranch.toLowerCase();
const productionBranchMatchesExpected = productionBranch.toLowerCase() === expectedProductionBranch.toLowerCase();

if (!git.linked) {
  fail("NO_GO_GIT_SOURCE_NOT_LINKED", {
    project: summarizeProject(project),
    git,
    reason: "The project must stay linked to the private Git repository before an omitted-target preview deploy can be built",
    requiredNextAction: "Reconnect the private tester portal repository to Vercel"
  }, 5);
}

if (!productionBranchMatchesExpected) {
  fail("NO_GO_PRODUCTION_BRANCH_UNEXPECTED", {
    project: summarizeProject(project),
    git,
    expectedProductionBranch,
    reason: "The Vercel production branch does not match the expected safe branch",
    requiredNextAction: "Correct Vercel Branch Tracking before any preview deployment"
  }, 6);
}

if (previewBranchIsProduction) {
  fail("NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION", {
    project: summarizeProject(project),
    git,
    reason: "The intended preview branch matches the Vercel production branch",
    requiredNextAction: "Use a non-production branch before any preview deployment"
  }, 7);
}

const draftDeploymentRequest = buildPreviewPayload(project, git);

console.log(JSON.stringify({
  ok: true,
  phase: "T10e",
  status: "GO_OMITTED_TARGET_PREVIEW_PATH_READY",
  project: summarizeProject(project),
  git,
  expectedProductionBranch,
  draftDeploymentRequest,
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "Create one omitted-target API deployment, then inspect target=preview before any URL is shared"
}, null, 2));
