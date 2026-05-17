param(
  [string]$Cases = ".local\remote_service\support_cases\support_cases.local.jsonl",
  [string]$SetStatusCase = "",
  [string]$Status = "",
  [string]$Note = "",
  [switch]$Json
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Python = "python"
$Tool = Join-Path $Root "backend\sqx-edge-tool\tools\remote_support_status.py"
$CasesPath = if ([System.IO.Path]::IsPathRooted($Cases)) { $Cases } else { Join-Path $Root $Cases }

$argsList = @($Tool, "--cases", $CasesPath)
if ($SetStatusCase) {
  $argsList += @("--set-status-case", $SetStatusCase, "--status", $Status, "--note", $Note)
}
$output = & $Python @argsList
if ($LASTEXITCODE -ne 0) {
  $output | Write-Output
  exit $LASTEXITCODE
}

if ($Json) {
  $output | Write-Output
  exit 0
}

$payload = $output | ConvertFrom-Json
$summary = $payload.summary
Write-Host "SQX Edge Suite - soporte remoto" -ForegroundColor Cyan
Write-Host ("Total casos: {0}" -f $summary.total)
Write-Host ("Abiertos: {0}" -f $summary.openSupportItems)
Write-Host ("Bloqueantes: {0}" -f $summary.unresolvedBlockers)
Write-Host ("Bloquea expansion REMOTE-8C: {0}" -f $payload.remote8c.blocksExpansion)
if ($payload.latest.Count -gt 0) {
  Write-Host ""
  Write-Host "Ultimos casos:" -ForegroundColor Yellow
  foreach ($item in $payload.latest) {
    Write-Host ("- {0} [{1}/{2}/{3}] {4}" -f $item.caseId, $item.status, $item.category, $item.severity, $item.summary)
  }
}
