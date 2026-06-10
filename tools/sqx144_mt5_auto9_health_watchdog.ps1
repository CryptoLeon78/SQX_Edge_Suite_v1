param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'health', 'automation-plan', 'approval-template')]
  [string]$Action = 'status',

  [string]$ExpectedRequestId = '',
  [string]$ExpectedSymbol = '',
  [int]$StaleAfterSeconds = 45
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto9-health-watchdog-v1'
$DataManagerVersion = 'sqx144-mt5-auto9-datamanager-health-watchdog-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

$oldPythonPath = $env:PYTHONPATH
try {
  if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
    $env:PYTHONPATH = $ToolRoot
  } else {
    $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
  }

  $argsList = @(
    '-m', 'core.sqx144_mt5_auto9_health_watchdog',
    $Action,
    '--project-root', $RepoRoot
  )

  if (-not [string]::IsNullOrWhiteSpace($ExpectedRequestId)) {
    $argsList += @('--expected-request-id', $ExpectedRequestId)
  }
  if (-not [string]::IsNullOrWhiteSpace($ExpectedSymbol)) {
    $argsList += @('--expected-symbol', $ExpectedSymbol)
  }
  if ($StaleAfterSeconds -gt 0) {
    $argsList += @('--stale-after-seconds', [string]$StaleAfterSeconds)
  }

  $raw = & $PythonExe @argsList
  if ($LASTEXITCODE -ne 0) {
    throw "sqx144_mt5_auto9_health_watchdog_python_failed"
  }
  $payload = ($raw -join "`n") | ConvertFrom-Json
} finally {
  $env:PYTHONPATH = $oldPythonPath
}

$payload | Add-Member -NotePropertyName wrapperVersion -NotePropertyValue $Version -Force
$payload | Add-Member -NotePropertyName dataManagerVersion -NotePropertyValue $DataManagerVersion -Force
$payload | Add-Member -NotePropertyName healthWatchdogObserveOnly -NotePropertyValue $true -Force
$payload | Add-Member -NotePropertyName autoStartAllowed -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName writesDataDb -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName writesUserProjects -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName mutatesDatabanks -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName runsSqxTasks -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName launchesMt5 -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName runsMt5Ea -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName usesMigrationTool -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName directDbHistoryInsertAllowed -NotePropertyValue $false -Force
$payload | Add-Member -NotePropertyName historyImportAllowed -NotePropertyValue $false -Force

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName applyApprovalReturned -NotePropertyValue $false -Force

$payload | ConvertTo-Json -Depth 24
