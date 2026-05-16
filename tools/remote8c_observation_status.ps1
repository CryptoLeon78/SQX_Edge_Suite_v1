[CmdletBinding()]
param(
    [string]$EvidencePath = ".local\remote_service\remote8c_first_user_observation.local.json",
    [string]$OutDir = ".local\remote_service\remote8c_first_user_observation",
    [switch]$Json,
    [switch]$FailOnNoGo
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$toolPath = Join-Path $repoRoot "backend\sqx-edge-tool\tools\remote_first_user_observation.py"

if (-not (Test-Path -LiteralPath $toolPath)) {
    throw "REMOTE-8C observation ingest tool not found."
}

$rawOutput = & python $toolPath --evidence $EvidencePath --out-dir $OutDir 2>&1
$toolExitCode = $LASTEXITCODE
$jsonText = ($rawOutput | Out-String).Trim()

try {
    $summary = $jsonText | ConvertFrom-Json
} catch {
    throw "REMOTE-8C observation tool did not return valid JSON. ExitCode=$toolExitCode Output=$jsonText"
}

$missingSignals = @($summary.missingSignals)
$metricBlockers = @($summary.metricBlockers)
$blockers = @($summary.blockers)
$blockedStatus = "NO_GO_REMOTE8C_FIRST_USER_OBSERVATION_BLOCKED"
$isExpansionReady = [bool]$summary.ok -and $summary.status -eq "GO_REMOTE8C_TINY_COHORT_EXPANSION_READY"
$isStayOneUser = [bool]$summary.ok -and $summary.status -eq "GO_REMOTE8C_STAY_ONE_USER_DECISION_RECORDED"
$isBlocked = $summary.status -eq $blockedStatus

if ($isExpansionReady) {
    $nextAction = "REMOTE-8C is clean. Prepare REMOTE-8D manually only after explicit operator approval."
} elseif ($isStayOneUser) {
    $nextAction = "REMOTE-8C is valid, but decision is to keep observing one user."
} elseif ($isBlocked) {
    $nextAction = "Continue REMOTE-8C. Complete the observation window, missing signals and metric blockers before any expansion."
} else {
    $nextAction = "Continue REMOTE-8C. Complete the observation window, missing signals and metric blockers before any expansion."
}

$result = [ordered]@{
    ok = [bool]$summary.ok
    phase = "REMOTE-8C"
    status = [string]$summary.status
    toolExitCode = $toolExitCode
    evidencePath = "<local-ignored>"
    publicSummaryPath = "<local-ignored>"
    observationWindowHours = $summary.observation.observationWindowHours
    requestedDecision = $summary.observation.requestedDecision
    targetTotalUsers = $summary.expansionGate.targetTotalUsers
    allowedToExpandToTinyCohort = [bool]$summary.expansionGate.allowedToExpandToTinyCohort
    missingSignals = $missingSignals
    metricBlockers = $metricBlockers
    blockers = $blockers
    automationAllowed = [bool]$summary.decision.automationAllowed
    manualOperatorStepRequired = [bool]$summary.decision.manualOperatorStepRequired
    privacy = $summary.privacy
    nextAction = $nextAction
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Host "REMOTE-8C first user observation status"
    Write-Host "  Status: $($result.status)"
    Write-Host "  OK: $($result.ok)"
    Write-Host "  Observation hours: $($result.observationWindowHours)"
    Write-Host "  Requested decision: $($result.requestedDecision)"
    Write-Host "  Target users: $($result.targetTotalUsers)"
    Write-Host "  Expansion allowed: $($result.allowedToExpandToTinyCohort)"
    Write-Host "  Missing signals: $($missingSignals -join ', ')"
    Write-Host "  Metric blockers: $($metricBlockers -join ', ')"
    Write-Host "  Blockers: $($blockers -join ', ')"
    Write-Host "  Next action: $nextAction"
}

if ($FailOnNoGo -and -not [bool]$summary.ok) {
    exit 2
}

exit 0
