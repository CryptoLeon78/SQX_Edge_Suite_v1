import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const expectedProjectName = process.env.T10N_PREVIEW_PROJECT_NAME || "sqx-edge-tester-preview";
const token = process.env.VERCEL_TOKEN;
const projectPath = join(process.cwd(), ".vercel", "project.json");

function fail(status, body, exitCode) {
  console.log(JSON.stringify({
    ok: false,
    phase: "T10n",
    status,
    externalDeployAllowed: false,
    externalDeployAttempted: false,
    externalConfigMutationAttempted: false,
    ...body
  }, null, 2));
  process.exit(exitCode);
}

function readLocalProject() {
  if (!existsSync(projectPath)) {
    fail("NO_GO_PROJECT_NOT_LINKED_LOCALLY", {
      reason: ".vercel/project.json is required for route decision",
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
      requiredNextAction: "Verify local Vercel token, team access and Project API permissions"
    }, 4);
  }
  return response.json();
}

function summarizeDomains(domainsResponse) {
  const apiDomains = Array.isArray(domainsResponse?.domains) ? domainsResponse.domains : [];
  const systemDomainSuffix = ["vercel", "app"].join(".");
  const systemDomains = apiDomains.filter((domain) => {
    const name = domain?.name ?? "";
    return name.endsWith(`.${systemDomainSuffix}`) || name === systemDomainSuffix;
  });
  return {
    total: apiDomains.length,
    system: systemDomains.length,
    custom: apiDomains.length - systemDomains.length
  };
}

function summarizeProject(project, domains) {
  const gitRepository = project.gitRepository ?? null;
  const link = project.link ?? null;
  const git = gitRepository ?? link;
  return {
    id: project.id ? "present" : "missing",
    name: project.name,
    live: Boolean(project.live),
    hasDeployments: Boolean(project.hasDeployments),
    latestDeployment: project.latestDeployment ? "present" : "none",
    latestDeployments: Array.isArray(project.latestDeployments) ? project.latestDeployments.length : 0,
    customDomains: domains.custom,
    systemDomains: domains.system,
    autoAssignCustomDomains: Boolean(project.autoAssignCustomDomains),
    previewDeploymentsDisabled: Boolean(project.previewDeploymentsDisabled),
    productionDeploymentsFastLane: Boolean(project.productionDeploymentsFastLane),
    deploymentProtectionVerified: Boolean(project.ssoProtection?.deploymentType || project.passwordProtection?.deploymentType),
    gitLinked: Boolean(git),
    gitProvider: git?.type ?? null,
    linkedProductionBranch: gitRepository?.productionBranch ?? link?.productionBranch ?? null,
    topLevelProductionBranch: project.productionBranch ?? null,
    targetsCount: project.targets ? Object.keys(project.targets).length : 0
  };
}

function safeCurrentSurface(project) {
  return !project.live
    && project.latestDeployment === "none"
    && project.customDomains === 0
    && project.autoAssignCustomDomains === false
    && project.previewDeploymentsDisabled === false
    && project.deploymentProtectionVerified;
}

function buildDecision(project) {
  const blockers = [
    "previous Git, explicit API, omitted-target API and CLI default attempts returned production target",
    "future deployment target cannot be proven without creating a deployment"
  ];
  if (project.productionDeploymentsFastLane) {
    blockers.push("productionDeploymentsFastLane remains reported by the Project API");
  }
  if (project.targetsCount === 0) {
    blockers.push("project targets remain empty in the Project API");
  }
  if (!safeCurrentSurface(project)) {
    blockers.push("current project surface is not clean enough for route replacement decision");
  }
  return {
    currentRouteApprovedForDeployment: false,
    replacementRequired: true,
    noDeployGoForCurrentRoute: false,
    blockers,
    allowedNextActions: [
      "manual provider-level proof before deployment",
      "fresh staging route with no-deploy proof before first deployment",
      "non-Vercel controlled tester route if preview-only behavior cannot be proven"
    ]
  };
}

const localProject = readLocalProject();

if (!token) {
  fail("NO_GO_TOKEN_NOT_AVAILABLE", {
    projectName: localProject.projectName,
    reason: "VERCEL_TOKEN is required to inspect Vercel route state",
    requiredNextAction: "Run with a local Vercel token; never commit the token"
  }, 2);
}

const project = await vercelGet(`/v9/projects/${localProject.projectId}`, localProject);
const domainsResponse = await vercelGet(`/v9/projects/${localProject.projectId}/domains`, localProject);
const domains = summarizeDomains(domainsResponse);
const summary = summarizeProject(project, domains);

if (summary.name !== expectedProjectName) {
  fail("NO_GO_WRONG_PREVIEW_PROJECT", {
    project: summary,
    expectedProjectName,
    requiredNextAction: "Relink the working tree to the separated preview project before route decision"
  }, 5);
}

const decision = buildDecision(summary);

console.log(JSON.stringify({
  ok: true,
  phase: "T10n",
  status: "NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED",
  project: summary,
  decision,
  externalDeployAllowed: false,
  externalDeployAttempted: false,
  externalConfigMutationAttempted: false,
  requiredNextAction: "T10o must prepare a replacement route or manual provider-level proof before any deployment"
}, null, 2));
