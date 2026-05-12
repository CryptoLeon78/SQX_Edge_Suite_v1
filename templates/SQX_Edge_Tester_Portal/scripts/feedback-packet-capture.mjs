import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(scriptDir, "..");
const defaultOutputDir = join(projectRoot, ".local", "feedback-packets");

const forbiddenPublicPatterns = [
  /https?:\/\//i,
  /workers\.dev/i,
  /\.vercel\.app/i,
  /password/i,
  /secret/i,
  /token/i,
  /cookie/i,
  /access[_ -]?code/i,
  /screenshot/i,
  /\.(png|jpe?g|webp|gif)$/i,
];

function usage() {
  return [
    "Usage:",
    "  node scripts/feedback-packet-capture.mjs --file .local/packet.txt",
    "  node scripts/feedback-packet-capture.mjs --text \"Reference: SQX-FB-1234ABCD...\"",
    "",
    "The output is written to .local/feedback-packets/ and must stay outside Git.",
  ].join("\n");
}

function argValue(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? "" : process.argv[index + 1] || "";
}

function readInput() {
  const filePath = argValue("--file");
  const inlineText = argValue("--text");

  if (filePath) {
    const absolutePath = resolve(projectRoot, filePath);
    if (!existsSync(absolutePath)) {
      throw new Error(`packet file not found: ${absolutePath}`);
    }
    return readFileSync(absolutePath, "utf8");
  }

  if (inlineText) {
    return inlineText;
  }

  throw new Error(usage());
}

function extractField(text, label) {
  const pattern = new RegExp(`^${label}:\\s*(.+)$`, "im");
  return pattern.exec(text)?.[1]?.trim() || "";
}

function normalize(value, fallback, maxLength) {
  const normalized = String(value || "")
    .replace(/\s+/g, " ")
    .trim();
  return (normalized || fallback).slice(0, maxLength);
}

function detectSensitiveHints(values) {
  const joined = values.join("\n");
  return forbiddenPublicPatterns
    .filter((pattern) => pattern.test(joined))
    .map((pattern) => pattern.source);
}

function parsePacket(text) {
  const reference = normalize(extractField(text, "Reference"), "", 32);
  const category = normalize(extractField(text, "Category"), "uncategorized", 80);
  const severity = normalize(extractField(text, "Severity"), "signal", 40);
  const summary = normalize(extractField(text, "Summary"), "No summary provided.", 800);

  if (!/^SQX-FB-[A-Z0-9]{8}$/.test(reference)) {
    throw new Error("packet reference must match SQX-FB-XXXXXXXX");
  }

  const sensitiveHints = detectSensitiveHints([category, severity, summary]);
  return {
    phase: "TL4",
    reference,
    capturedAt: new Date().toISOString(),
    category,
    severity,
    summary,
    sensitiveHints,
    privateStorage: true,
    publicSafe: sensitiveHints.length === 0,
  };
}

function writePacket(packet) {
  mkdirSync(defaultOutputDir, { recursive: true });
  const outputPath = join(defaultOutputDir, `${packet.reference}.json`);
  writeFileSync(outputPath, `${JSON.stringify(packet, null, 2)}\n`, "utf8");
  return outputPath;
}

try {
  const packet = parsePacket(readInput());
  const outputPath = writePacket(packet);
  console.log(
    JSON.stringify(
      {
        ok: true,
        phase: "TL4",
        reference: packet.reference,
        outputPath,
        publicSafe: packet.publicSafe,
        sensitiveHintCount: packet.sensitiveHints.length,
      },
      null,
      2,
    ),
  );
  if (!packet.publicSafe) {
    process.exitCode = 2;
  }
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
