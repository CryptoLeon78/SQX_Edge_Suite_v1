import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10H_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10h",
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
      reason: ".vercel/project.json is required to prove T10h rollback cleanup",
      requiredNextAction: "Run from the private tester portal working tree linked to the separated preview project"
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
      requiredNextAction: "Verify local Vercel token/team access before any preview deployment retry"
    }, 3);
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
    domains: Array.isArray(project.domains) ? project.domains.length : 0,
    linked: Boolean(project.gitRepository || project.link),
    productionBranch: project.productionBranch ?? project.link?.productionBranch ?? project.gitRepository?.productionBranch ?? null,
    ssoDeploymentType: project.ssoProtection?.deploymentType ?? null
  };
}

const localProject = readLocalProject();

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel project rollback state",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

const project = await vercelGet(`/v9/projects/${localProject.projectId}`, localProject);
const summary = summarizeProject(project);

if (summary.name !== expectedProjectName) {
  fail("NO_GO_WRONG_PREVIEW_PROJECT", {
    project: summary,
    expectedProjectName,
    requiredNextAction: "Relink the local private tester portal working tree to the separated preview project"
  }, 4);
}

if (summary.live || summary.latestDeployment !== "none" || summary.domains !== 0) {
  fail("NO_GO_ROLLBACK_NOT_CLEAN", {
    project: summary,
    requiredNextAction: "Remove deployment/domain surface before any further preview attempt"
  }, 5);
}

console.log(JSON.stringify({
  ok: true,
  phase: "T10h",
  status: "GO_PROTECTED_PREVIEW_ROLLBACK_CLEAN",
  project: summary,
  lastAttempt: {
    requestedTarget: "preview",
    observedTarget: "production",
    guardStatus: "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
    rollbackStatus: "removed"
  },
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "T10i must correct or replace the Vercel preview deployment route before another deployment attempt"
}, null, 2));
