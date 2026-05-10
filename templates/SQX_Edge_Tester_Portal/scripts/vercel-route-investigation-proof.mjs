import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10L_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const expectedProductionBranch = process.env.T10L_EXPECTED_PRODUCTION_BRANCH || "main";
const intendedPreviewBranch = process.env.T10L_PREVIEW_BRANCH || "tester-preview";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10l",
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
      reason: ".vercel/project.json is required for route investigation",
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
      requiredNextAction: "Verify local Vercel token and team access before route investigation"
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
    hasDeployments: Boolean(project.hasDeployments),
    latestDeployment: project.latestDeployment ? "present" : "none",
    latestDeployments: Array.isArray(project.latestDeployments) ? project.latestDeployments.length : 0,
    domains: Array.isArray(project.domains) ? project.domains.length : 0,
    targets: project.targets ? Object.keys(project.targets).length : 0,
    autoAssignCustomDomains: Boolean(project.autoAssignCustomDomains),
    productionDeploymentsFastLane: Boolean(project.productionDeploymentsFastLane),
    sourceFilesOutsideRootDirectory: Boolean(project.sourceFilesOutsideRootDirectory)
  };
}

function summarizeGit(project) {
  const gitRepository = project.gitRepository ?? null;
  const link = project.link ?? null;
  const git = gitRepository ?? link;
  const topLevelProductionBranch = project.productionBranch ?? null;
  const linkedProductionBranch = gitRepository?.productionBranch ?? link?.productionBranch ?? null;
  return {
    linked: Boolean(git),
    source: gitRepository ? "gitRepository" : link ? "link" : null,
    provider: git?.type ?? null,
    repo: git?.repo ? "present" : null,
    repoId: git?.repoId ? "present" : null,
    topLevelProductionBranch,
    linkedProductionBranch,
    expectedProductionBranch,
    intendedPreviewBranch,
    topLevelProductionBranchMissing: !topLevelProductionBranch,
    linkedProductionBranchMatchesExpected: Boolean(linkedProductionBranch)
      && linkedProductionBranch.toLowerCase() === expectedProductionBranch.toLowerCase(),
    previewBranchIsLinkedProduction: Boolean(linkedProductionBranch)
      && linkedProductionBranch.toLowerCase() === intendedPreviewBranch.toLowerCase()
  };
}

function summarizeProtection(project) {
  return {
    ssoDeploymentType: project.ssoProtection?.deploymentType ?? null,
    passwordDeploymentType: project.passwordProtection?.deploymentType ?? null,
    deploymentProtectionVerified: Boolean(project.ssoProtection?.deploymentType || project.passwordProtection?.deploymentType)
  };
}

function summarizeEnv(envs) {
  const values = Array.isArray(envs.envs) ? envs.envs : [];
  const targets = new Set();
  for (const env of values) {
    for (const target of env.target ?? []) {
      targets.add(target);
    }
  }
  return {
    count: values.length,
    targets: Array.from(targets).sort()
  };
}

const localProject = readLocalProject();

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel route settings",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

const project = await vercelGet(`/v9/projects/${localProject.projectId}`, localProject);
const envs = await vercelGet(`/v10/projects/${localProject.projectId}/env`, localProject);
const summary = summarizeProject(project);
const git = summarizeGit(project);
const protection = summarizeProtection(project);
const envSummary = summarizeEnv(envs);

if (summary.name !== expectedProjectName) {
  fail("NO_GO_WRONG_PREVIEW_PROJECT", {
    project: summary,
    expectedProjectName,
    requiredNextAction: "Relink the working tree to the separated preview project before continuing"
  }, 5);
}

if (summary.live || summary.latestDeployment !== "none" || summary.domains !== 0) {
  fail("NO_GO_PROJECT_HAS_PUBLIC_SURFACE", {
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

if (!git.linkedProductionBranchMatchesExpected || git.previewBranchIsLinkedProduction) {
  fail("NO_GO_LINKED_PRODUCTION_BRANCH_UNSAFE", {
    project: summary,
    git,
    requiredNextAction: "Fix Vercel Git production branch before any future deployment"
  }, 8);
}

if (!protection.deploymentProtectionVerified) {
  fail("NO_GO_DEPLOYMENT_PROTECTION_NOT_VERIFIED", {
    project: summary,
    protection,
    requiredNextAction: "Enable or verify Vercel Deployment Protection before any future deployment"
  }, 9);
}

const blockers = [];
if (git.topLevelProductionBranchMissing) {
  blockers.push("project.productionBranch is missing while link.productionBranch is main");
}
if (summary.targets === 0) {
  blockers.push("project.targets is empty");
}
if (summary.autoAssignCustomDomains) {
  blockers.push("autoAssignCustomDomains is enabled");
}
if (summary.productionDeploymentsFastLane) {
  blockers.push("productionDeploymentsFastLane is enabled");
}

console.log(JSON.stringify({
  ok: true,
  phase: "T10l",
  status: "NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT",
  project: summary,
  git,
  protection,
  env: envSummary,
  investigation: {
    noDeploy: true,
    officialCliPreviewRouteExpected: "vercel deploy",
    observedHistory: "CLI/API/default routes repeatedly returned production target",
    blockers,
    conclusion: "Do not run another deployment until dashboard/API target mapping or an alternative host route is proven without deployment"
  },
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "T10m must perform manual dashboard/API correction or define an alternative no-deploy route proof before any further deployment"
}, null, 2));
