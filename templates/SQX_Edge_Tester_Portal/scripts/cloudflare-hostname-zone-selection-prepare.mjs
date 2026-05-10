import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const examplePath = join(projectRoot, "cloudflare-hostname-zone-selection.example.json");
const localPath = join(projectRoot, "cloudflare-hostname-zone-selection.local.json");
const args = new Set(process.argv.slice(2));

const forbiddenLocalKeys = new Set([
  "accountId",
  "apiToken",
  "cloudflareAccountId",
  "cloudflareApiToken",
  "cloudflareZoneId",
  "email",
  "emails",
  "hostname",
  "selectedHostname",
  "testerEmail",
  "testerEmails",
  "testerUrl",
  "token",
  "url",
  "zoneId",
]);

const forbiddenValuePatterns = [
  /@/,
  /https?:\/\//i,
  /\.vercel\.app/i,
  /cloudflareaccess\.com/i,
  /CLOUDFLARE_[A-Z_]+/i,
  /-----BEGIN [A-Z ]+PRIVATE KEY-----/,
  /\b[A-Fa-f0-9]{32,}\b/,
];

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function scanEvidence(value, path = []) {
  const findings = [];
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      findings.push(...scanEvidence(item, [...path, String(index)]));
    });
    return findings;
  }

  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, nested]) => {
      const keyPath = [...path, key];
      if (forbiddenLocalKeys.has(key)) {
        findings.push(`forbidden_key:${keyPath.join(".")}`);
      }
      findings.push(...scanEvidence(nested, keyPath));
    });
    return findings;
  }

  if (typeof value === "string") {
    forbiddenValuePatterns.forEach((pattern) => {
      if (pattern.test(value)) {
        findings.push(`forbidden_value:${path.join(".")}`);
      }
    });
  }

  return findings;
}

function writeLocalEvidence() {
  if (existsSync(localPath) && !args.has("--force")) {
    return "exists";
  }

  const example = readJson(examplePath);
  const initialEvidence = {
    ...example,
    selectedPath: "custom_domain_pending_private_operator_confirmation",
    operatorChecklist: {
      activeCloudflareZoneConfirmed: false,
      hostnameChosenOutsideGit: false,
      hostnameNotSharedWithTesters: true,
      accessAppCanMatchHostname: false,
      noPublicRouteCommitted: true,
      noTesterUrlPublished: true,
    },
  };

  writeFileSync(localPath, `${JSON.stringify(initialEvidence, null, 2)}\n`, "utf8");
  return "created";
}

const shouldWrite = args.has("--write") || args.has("--force");
const writeResult = shouldWrite ? writeLocalEvidence() : "dry_run";
const localEvidence = existsSync(localPath) ? readJson(localPath) : null;
const localFindings = localEvidence ? scanEvidence(localEvidence) : [];
const localEvidenceReady = Boolean(
  localEvidence &&
  localEvidence.accessPrecreateAllowed === true &&
  localEvidence.t10akUnlocked === true &&
  localEvidence.testerUrlPublished === false &&
  localEvidence.testerEmailsIncluded === false &&
  (
    (
      localEvidence.hostnameSelectedPrivately === true &&
      localEvidence.zoneSelectedPrivately === true &&
      localEvidence.hostnameBelongsToCloudflareZone === true &&
      localEvidence.accessHostnameCanBeMatched === true &&
      localEvidence.routeCanBeCreatedAfterDeploy === true
    ) ||
    (
      localEvidence.workersDevOnboardingComplete === true &&
      localEvidence.workersDevShellTargetExists === true &&
      localEvidence.workersDevAccessProtectionVerified === true &&
      localEvidence.accessHostnameCanBeMatched === true
    )
  )
);

const report = Object.freeze({
  phase: "T10ajl_operator_unlock_kit",
  writeResult,
  localEvidenceFile: "cloudflare-hostname-zone-selection.local.json",
  localEvidencePresent: localEvidence !== null,
  localEvidenceHasNoSensitiveFields: localFindings.length === 0,
  localFindings,
  localEvidenceReady,
  nextProofCommand: "npm run proof:cloudflare-hostname-zone-selection",
  nextAllowedPhase: localEvidenceReady
    ? "T10ak_cloudflare_access_application_policy_creation"
    : "repeat_private_cloudflare_hostname_zone_check",
  checklist: [
    "Confirm an active Cloudflare-managed zone or completed workers.dev onboarding outside git.",
    "Choose the protected hostname outside git; do not paste it into this repository.",
    "For workers.dev, deploy/protect only the harmless shell target before marking Access verified.",
    "Confirm Cloudflare Access can match that hostname before tester sharing.",
    "Set only boolean fields to true after each private check is complete.",
    "Keep testerUrlPublished=false and testerEmailsIncluded=false until T11.",
    "Run npm run proof:cloudflare-hostname-zone-selection and continue only on GO.",
  ],
});

console.log(JSON.stringify(report, null, 2));

if (!report.localEvidenceHasNoSensitiveFields) {
  process.exitCode = 1;
}
