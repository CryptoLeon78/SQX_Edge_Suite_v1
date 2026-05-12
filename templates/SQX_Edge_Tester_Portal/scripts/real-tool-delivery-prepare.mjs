import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const portalRoot = join(scriptDir, "..");
const repoRoot = join(portalRoot, "..", "..");
const distDir = join(repoRoot, "dist");
const assetDir = join(portalRoot, ".open-next", "assets", "downloads");
const assetPath = join(assetDir, "SQX_Edge_Tool_Portable_Tester.zip");
const localManifestPath = join(portalRoot, ".local", "real-tool-delivery.local.json");
const downloadPath = "/download/sqx-edge-tool.zip";

function argValue(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? "" : process.argv[index + 1] || "";
}

function latestPortableZip() {
  if (!existsSync(distDir)) {
    throw new Error(`dist directory not found: ${distDir}`);
  }

  const files = readdirSync(distDir);
  const testerCandidates = files
    .filter((name) => /^SQX_Edge_Tool_Portable_Tester_\d{8}_\d{6}\.zip$/.test(name))
    .map((name) => {
      const fullPath = join(distDir, name);
      return { fullPath, stats: statSync(fullPath), releaseProfile: "tester" };
    });
  const genericCandidates = files
    .filter((name) => /^SQX_Edge_Tool_Portable_\d{8}_\d{6}\.zip$/.test(name))
    .map((name) => {
      const fullPath = join(distDir, name);
      return { fullPath, stats: statSync(fullPath), releaseProfile: "generic" };
    });
  const candidates = (testerCandidates.length ? testerCandidates : genericCandidates)
    .sort((a, b) => b.stats.mtimeMs - a.stats.mtimeMs);

  if (candidates.length === 0) {
    throw new Error("No SQX_Edge_Tool_Portable_*.zip or SQX_Edge_Tool_Portable_Tester_*.zip package found in dist.");
  }

  return candidates[0];
}

function sha256(path) {
  const hash = createHash("sha256");
  const data = statSync(path);
  if (!data.isFile()) {
    throw new Error(`not a file: ${path}`);
  }
  hash.update(readFileSync(path));
  return hash.digest("hex").toUpperCase();
}

const selectedPackage = argValue("--zip")
  ? { fullPath: resolve(repoRoot, argValue("--zip")), releaseProfile: "manual" }
  : latestPortableZip();
const inputZip = selectedPackage.fullPath;

if (!existsSync(inputZip)) {
  throw new Error(`portable ZIP not found: ${inputZip}`);
}

mkdirSync(assetDir, { recursive: true });
copyFileSync(inputZip, assetPath);

const stats = statSync(inputZip);
const manifest = {
  phase: "TL11",
  preparedAt: new Date().toISOString(),
  sourceZipName: inputZip.split(/[\\/]/).pop(),
  sourceReleaseProfile: selectedPackage.releaseProfile,
  sourceZipBytes: stats.size,
  sourceZipSha256: sha256(inputZip),
  assetRelativePath: ".open-next/assets/downloads/SQX_Edge_Tool_Portable_Tester.zip",
  protectedDownloadPath: downloadPath,
  accessRequired: true,
  gitIgnored: true,
  testerRedistributionAllowed: false,
};

mkdirSync(dirname(localManifestPath), { recursive: true });
writeFileSync(localManifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");

console.log(
  JSON.stringify(
    {
      ok: true,
      phase: "TL11",
      sourceZip: inputZip,
      sourceReleaseProfile: selectedPackage.releaseProfile,
      assetPath,
      manifestPath: localManifestPath,
      bytes: manifest.sourceZipBytes,
      sha256: manifest.sourceZipSha256,
      protectedDownloadPath: downloadPath,
    },
    null,
    2,
  ),
);
