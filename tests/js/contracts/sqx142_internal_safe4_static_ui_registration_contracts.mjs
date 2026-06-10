import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const scriptPath = path.join(repoRoot, "tools", "sqx142_internal_safe4_static_ui_registration.ps1");

const script = fs.readFileSync(scriptPath, "utf8");

const requiredMarkers = [
  "SQX142-INTERNAL-SAFE4",
  "sqx142-internal-safe4-static-ui-registration-v1",
  "SQX142_ROOT/internal/web/common/templates.html",
  "Assert-NoSqxProcess",
  "New-TemplateBackup",
  "Get-FileHash",
  "rollback",
  "engineFilesWritten = $false",
  "jarFilesWritten = $false",
  "licenseFilesWritten = $false",
  "dataDbWritten = $false",
  "userProjectsWritten = $false",
  "databanksWritten = $false",
  "native ResultsSourceCode template",
];

for (const marker of requiredMarkers) {
  if (!script.includes(marker)) {
    throw new Error(`SAFE4 script missing marker: ${marker}`);
  }
}

const forbiddenMarkers = [
  "StrategyQuantX.exe",
  "Stop-Process",
  "Remove-Item -Recurse",
  "run_project",
];

for (const marker of forbiddenMarkers) {
  if (script.includes(marker)) {
    throw new Error(`SAFE4 script contains forbidden marker: ${marker}`);
  }
}

if (!script.includes("'data.db writes'") || !script.includes("'Migration Tool'") || !script.includes("'license/activation/bypass'")) {
  throw new Error("SAFE4 script should mention blocked data.db writes, Migration Tool and license boundary.");
}

console.log("sqx142 internal safe4 static ui registration contracts ok");
