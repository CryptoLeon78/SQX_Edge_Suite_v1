const vercelEnv = process.env.VERCEL_ENV || "";
const gitRef = process.env.VERCEL_GIT_COMMIT_REF || "";
const allowedProductionBranches = (process.env.SQX_ALLOWED_PRODUCTION_BRANCHES || "main")
  .split(",")
  .map((branch) => branch.trim())
  .filter(Boolean);

const runningOnVercel = process.env.VERCEL === "1" || Boolean(vercelEnv);
const isProductionTarget = vercelEnv === "production";
const isAllowedProductionBranch = allowedProductionBranches.includes(gitRef);

if (runningOnVercel && isProductionTarget && !isAllowedProductionBranch) {
  console.error(JSON.stringify({
    ok: false,
    phase: "T10b",
    status: "NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH",
    vercelEnv,
    gitRef,
    allowedProductionBranches,
    reason: "SQX tester portal refuses production-target builds from non-production branches",
    requiredNextAction: "Fix Vercel Git target mapping before triggering another tester preview"
  }, null, 2));
  process.exit(43);
}

console.log(JSON.stringify({
  ok: true,
  phase: "T10b",
  status: "GO_TARGET_GUARD_PASSED",
  vercelEnv: vercelEnv || "local",
  gitRef: gitRef || "local",
  allowedProductionBranches,
  productionTargetAllowed: !isProductionTarget || isAllowedProductionBranch
}, null, 2));
