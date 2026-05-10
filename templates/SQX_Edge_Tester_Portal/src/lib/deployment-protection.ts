export const DEPLOYMENT_PROTECTION_CHECKLIST = [
  "Vercel Deployment Protection enabled for preview and production",
  "tester auth enabled before sharing any URL",
  "T8_GLOBAL_KILL_SWITCH_ENABLED tested before pilot",
  "T8_RATE_LIMIT_ENABLED tested before pilot",
  "no public indexing and X-Robots-Tag noindex",
  "no tester invites or renewal emails without explicit approval",
  "no production database secrets committed",
  "watermark visible on protected tester surfaces"
] as const;

export type DeploymentProtectionChecklistItem = (typeof DEPLOYMENT_PROTECTION_CHECKLIST)[number];

export function buildDeploymentProtectionSummary() {
  return {
    mode: "checklist-only",
    requiredBeforePreview: DEPLOYMENT_PROTECTION_CHECKLIST,
    externalActionAllowed: false
  };
}

