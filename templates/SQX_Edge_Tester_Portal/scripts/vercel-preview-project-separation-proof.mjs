import { readFileSync } from "node:fs";
import { join } from "node:path";

const expectedPreviewProjectName = process.env.T10F_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const legacyProjectName = process.env.T10F_LEGACY_PROJECT_NAME || "sqx-edge-tester-portal";
const teamId = process.env.T10F_VERCEL_TEAM_ID || readLocalTeamId();
const token = process.env.VERCEL_TOKEN;

function readLocalTeamId() {
  try {
    const localProject = JSON.parse(readFileSync(join(process.cwd(), ".vercel", "project.json"), "utf8"));
    return localProject.orgId || null;
  } catch {
    return null;
  }
}

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10f",
    status,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    ...body
  }, null, 2));
  process.exit(exitCode);
}

async function vercelGet(path) {
  const url = new URL(`https://api.vercel.com${path}`);
  if (teamId) {
    url.searchParams.set("teamId", teamId);
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
      requiredNextAction: "Verify local Vercel token/team access before any preview project work"
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
    domains: Array.isArray(project.domains) ? project.domains.length : 0,
    gitLinked: Boolean(project.gitRepository || project.link)
  };
}

function assertUndeployed(project, label) {
  const summary = summarizeProject(project);
  if (summary.live || summary.latestDeployment !== "none" || summary.domains !== 0) {
    fail("NO_GO_PROJECT_HAS_PUBLIC_SURFACE", {
      label,
      project: summary,
      requiredNextAction: "Remove deployment/domain surface before continuing tester preview setup"
    }, 6);
  }
}

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    reason: "VERCEL_TOKEN is required to inspect Vercel project separation",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 1);
}

if (!teamId) {
  fail("NO_GO_TEAM_NOT_AVAILABLE", {
    reason: "T10F_VERCEL_TEAM_ID or local .vercel/project.json orgId is required",
    requiredNextAction: "Set T10F_VERCEL_TEAM_ID locally for this proof"
  }, 2);
}

const projectList = await vercelGet("/v9/projects");
const projects = Array.isArray(projectList.projects) ? projectList.projects : [];
const previewSummary = projects.find((project) => project.name === expectedPreviewProjectName);
const legacySummary = projects.find((project) => project.name === legacyProjectName);

if (!previewSummary) {
  fail("NO_GO_PREVIEW_PROJECT_MISSING", {
    expectedPreviewProjectName,
    requiredNextAction: "Create the separated preview-only project before continuing"
  }, 3);
}

if (!legacySummary) {
  fail("NO_GO_LEGACY_PROJECT_MISSING", {
    legacyProjectName,
    requiredNextAction: "Confirm the legacy project identity before cleanup or migration decisions"
  }, 5);
}

if (previewSummary.id === legacySummary.id) {
  fail("NO_GO_PROJECT_NOT_SEPARATED", {
    expectedPreviewProjectName,
    legacyProjectName,
    requiredNextAction: "Use a different Vercel project for tester preview setup"
  }, 7);
}

const previewProject = await vercelGet(`/v9/projects/${previewSummary.id}`);
const legacyProject = await vercelGet(`/v9/projects/${legacySummary.id}`);

assertUndeployed(previewProject, "preview");
assertUndeployed(legacyProject, "legacy");

const preview = summarizeProject(previewProject);
if (preview.gitLinked) {
  fail("NO_GO_PREVIEW_PROJECT_ALREADY_LINKED", {
    preview,
    requiredNextAction: "Inspect linked Git settings manually before any deployment; T10g owns linking proof"
  }, 8);
}

console.log(JSON.stringify({
  ok: true,
  phase: "T10f",
  status: "GO_PREVIEW_PROJECT_SEPARATED",
  preview,
  legacy: summarizeProject(legacyProject),
  separation: {
    expectedPreviewProjectName,
    legacyProjectName,
    differentProjects: true
  },
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  requiredNextAction: "T10g must link the private tester portal repo to the separated preview project and prove settings before any deployment"
}, null, 2));
