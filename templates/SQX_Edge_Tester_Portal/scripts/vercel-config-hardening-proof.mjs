import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10M_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const applyChanges = process.env.T10M_APPLY === "1";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");
const desiredPatch = Object.freeze({
  autoAssignCustomDomains: false,
  previewDeploymentsDisabled: false
});

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10m",
    status,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    externalConfigMutationAttempted: applyChanges,
    ...body
  }, null, 2));
  process.exit(exitCode);
}

function readLocalProject() {
  if (!existsSync(projectPath)) {
    fail("NO_GO_PROJECT_NOT_LINKED_LOCALLY", {
      reason: ".vercel/project.json is required for config hardening",
      requiredNextAction: "Relink the private tester portal working tree to the separated preview project"
    }, 1);
  }
  return JSON.parse(readFileSync(projectPath, "utf8"));
}

async function vercelRequest(path, localProject, options = {}) {
  const url = new URL(`https://api.vercel.com${path}`);
  if (localProject.orgId) {
    url.searchParams.set("teamId", localProject.orgId);
  }
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/json"
  };
  if (options.body) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(url, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  if (!response.ok) {
    fail("NO_GO_VERCEL_API_FAILED", {
      httpStatus: response.status,
      apiPath: path,
      method: options.method || "GET",
      requiredNextAction: "Verify local Vercel token, team access and Project API permissions"
    }, 4);
  }
  return response.json();
}

function summarizeProject(project, domainsResponse) {
  const projectDomains = Array.isArray(project.domains) ? project.domains : [];
  const apiDomains = Array.isArray(domainsResponse?.domains) ? domainsResponse.domains : [];
  const systemDomainSuffix = ["vercel", "app"].join(".");
  const systemDomains = apiDomains.filter((domain) => {
    const name = domain?.name ?? "";
    return name.endsWith(`.${systemDomainSuffix}`) || name === systemDomainSuffix;
  });
  const customDomains = apiDomains.length - systemDomains.length;
  return {
    id: project.id ? "present" : "missing",
    name: project.name,
    live: Boolean(project.live),
    hasDeployments: Boolean(project.hasDeployments),
    latestDeployment: project.latestDeployment ? "present" : "none",
    latestDeployments: Array.isArray(project.latestDeployments) ? project.latestDeployments.length : 0,
    projectDomains: projectDomains.length,
    apiDomains: apiDomains.length,
    systemDomains: systemDomains.length,
    customDomains,
    autoAssignCustomDomains: Boolean(project.autoAssignCustomDomains),
    previewDeploymentsDisabled: Boolean(project.previewDeploymentsDisabled),
    productionDeploymentsFastLane: Boolean(project.productionDeploymentsFastLane),
    deploymentProtectionVerified: Boolean(project.ssoProtection?.deploymentType || project.passwordProtection?.deploymentType)
  };
}

function summarizeSettings(before, after) {
  return {
    plannedPatch: desiredPatch,
    applied: applyChanges,
    autoAssignCustomDomainsBefore: before.autoAssignCustomDomains,
    autoAssignCustomDomainsAfter: after.autoAssignCustomDomains,
    previewDeploymentsDisabledBefore: before.previewDeploymentsDisabled,
    previewDeploymentsDisabledAfter: after.previewDeploymentsDisabled,
    automaticCustomDomainsDisabled: after.autoAssignCustomDomains === false,
    previewDeploymentsEnabled: after.previewDeploymentsDisabled === false
  };
}

function remainingBlockers(after) {
  const blockers = [];
  if (after.autoAssignCustomDomains) {
    blockers.push("autoAssignCustomDomains remains enabled");
  }
  if (after.previewDeploymentsDisabled) {
    blockers.push("previewDeploymentsDisabled remains enabled");
  }
  if (after.projectDomains > 0 || after.customDomains > 0) {
    blockers.push("project still has custom domains");
  }
  if (after.live || after.latestDeployment !== "none") {
    blockers.push("project still has public deployment surface");
  }
  if (!after.deploymentProtectionVerified) {
    blockers.push("deployment protection is not verified");
  }
  if (after.productionDeploymentsFastLane) {
    blockers.push("productionDeploymentsFastLane remains reported and requires manual/API review");
  }
  blockers.push("deployment target remains unproven without creating a deployment");
  return blockers;
}

const localProject = readLocalProject();

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect or harden Vercel project settings",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

const projectPathApi = `/v9/projects/${localProject.projectId}`;
const domainsPathApi = `/v9/projects/${localProject.projectId}/domains`;
const beforeProject = await vercelRequest(projectPathApi, localProject);
const beforeDomains = await vercelRequest(domainsPathApi, localProject);
const before = summarizeProject(beforeProject, beforeDomains);

if (before.name !== expectedProjectName) {
  fail("NO_GO_WRONG_PREVIEW_PROJECT", {
    project: before,
    expectedProjectName,
    requiredNextAction: "Relink the working tree to the separated preview project before hardening"
  }, 5);
}

let patchResponse = null;
if (applyChanges) {
  patchResponse = await vercelRequest(projectPathApi, localProject, {
    method: "PATCH",
    body: desiredPatch
  });
}

const afterProject = applyChanges ? await vercelRequest(projectPathApi, localProject) : beforeProject;
const afterDomains = applyChanges ? await vercelRequest(domainsPathApi, localProject) : beforeDomains;
const after = summarizeProject(afterProject, afterDomains);
const settings = summarizeSettings(before, after);
const blockers = remainingBlockers(after);
const configHardened = settings.automaticCustomDomainsDisabled
  && settings.previewDeploymentsEnabled
  && after.projectDomains === 0
  && after.customDomains === 0
  && !after.live
  && after.latestDeployment === "none"
  && after.deploymentProtectionVerified;

if (!applyChanges) {
  console.log(JSON.stringify({
    ok: true,
    phase: "T10m",
    status: "DRY_RUN_VERCEL_CONFIG_HARDENING_READY",
    project: after,
    settings,
    blockers,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    externalConfigMutationAttempted: false,
    requiredNextAction: "Run with T10M_APPLY=1 only after documenting the exact Vercel Project API patch"
  }, null, 2));
  process.exit(0);
}

console.log(JSON.stringify({
  ok: configHardened,
  phase: "T10m",
  status: configHardened
    ? "GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN"
    : "NO_GO_CONFIG_HARDENING_INCOMPLETE",
  project: after,
  settings,
  apiPatchApplied: Boolean(patchResponse),
  blockers,
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  externalConfigMutationAttempted: true,
  requiredNextAction: "T10n must prove or replace the preview route without creating a public tester surface"
}, null, 2));

process.exit(configHardened ? 0 : 10);
