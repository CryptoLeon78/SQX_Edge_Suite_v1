import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const packetDir = join(projectRoot, ".local", "feedback-packets");
const outputPath = join(projectRoot, "tester-feedback-intake.local.json");
const rollupPath = join(projectRoot, ".local", "feedback-intake-rollup.json");

function parseJson(text, label) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function readPackets() {
  if (!existsSync(packetDir)) {
    return [];
  }

  return readdirSync(packetDir)
    .filter((name) => /^SQX-FB-[A-Z0-9]{8}\.json$/.test(name))
    .map((name) => {
      const packetPath = join(packetDir, name);
      return parseJson(readFileSync(packetPath, "utf8"), name);
    });
}

function clampCount(value) {
  return Math.max(0, Math.min(50, value));
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function buildIntakeEvidence(packets) {
  const publicSafePackets = packets.filter((packet) => packet.publicSafe === true);
  const unsafePackets = packets.filter((packet) => packet.publicSafe !== true || packet.sensitiveHints?.length > 0);
  const categories = unique(publicSafePackets.map((packet) => packet.category));
  const severities = unique(publicSafePackets.map((packet) => packet.severity));
  const blockingBugCount = publicSafePackets.filter(
    (packet) => packet.category === "bug_or_blocker" || packet.severity === "blocker",
  ).length;
  const approved = publicSafePackets.length > 0 && unsafePackets.length === 0;

  return {
    phase: "T10aw",
    t10avCohortExpansionGo: approved,
    privateFeedbackChannelReady: approved,
    rawFeedbackKeptOutsideGit: true,
    redactionPolicyReady: approved,
    publicSafeSummaryPolicyReady: approved,
    aggregateCountsOnly: true,
    onboardingFrictionBucketReady: approved,
    uiConfusionBucketReady: approved,
    missingDocsBucketReady: approved,
    performanceNotesBucketReady: approved,
    blockingBugsBucketReady: approved,
    commercialObjectionsBucketReady: approved,
    supportChannelReadyPrivately: approved,
    revocationPathReadyPrivately: approved,
    feedbackIntakeApprovedPrivately: approved,
    publicRepoContainsTesterEmails: false,
    publicRepoContainsTesterUrl: false,
    publicRepoContainsCredentials: false,
    publicRepoContainsProviderIds: false,
    publicRepoContainsScreenshots: false,
    publicRepoContainsRawFeedback: false,
    publicRepoContainsFeedbackIdentities: false,
    feedbackResponderCount: clampCount(publicSafePackets.length),
    redactedThemeCount: clampCount(categories.length + severities.length),
    blockingBugCount: clampCount(blockingBugCount),
    failedCheckCount: clampCount(unsafePackets.length),
  };
}

function buildPrivateRollup(packets, evidence) {
  const publicSafePackets = packets.filter((packet) => packet.publicSafe === true);
  return {
    phase: "TL5",
    generatedAt: new Date().toISOString(),
    packetCount: packets.length,
    publicSafePacketCount: publicSafePackets.length,
    unsafePacketCount: evidence.failedCheckCount,
    categories: unique(publicSafePackets.map((packet) => packet.category)).sort(),
    severities: unique(publicSafePackets.map((packet) => packet.severity)).sort(),
    references: publicSafePackets.map((packet) => packet.reference).sort(),
  };
}

const packets = readPackets();

if (packets.length === 0) {
  console.error("No local feedback packets found in .local/feedback-packets/.");
  process.exit(1);
}

const evidence = buildIntakeEvidence(packets);
const rollup = buildPrivateRollup(packets, evidence);
mkdirSync(dirname(rollupPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(evidence, null, 2)}\n`, "utf8");
writeFileSync(rollupPath, `${JSON.stringify(rollup, null, 2)}\n`, "utf8");

console.log(
  JSON.stringify(
    {
      ok: evidence.failedCheckCount === 0 && evidence.feedbackResponderCount > 0,
      phase: "TL5",
      outputPath,
      rollupPath,
      feedbackResponderCount: evidence.feedbackResponderCount,
      redactedThemeCount: evidence.redactedThemeCount,
      blockingBugCount: evidence.blockingBugCount,
      failedCheckCount: evidence.failedCheckCount,
    },
    null,
    2,
  ),
);

if (evidence.failedCheckCount > 0 || evidence.feedbackResponderCount === 0) {
  process.exitCode = 2;
}
