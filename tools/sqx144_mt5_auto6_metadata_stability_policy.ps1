param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'evaluate', 'decision-template')]
  [string]$Action = 'status',

  [string]$Broker = 'darwinex',

  [string]$Symbol = 'AUDCAD_darwinex',

  [string]$SpreadPolicy = 'p90',

  [string]$ExpectedRequestId
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto6-metadata-stability-policy-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

$writesSqxHost = $false
$writesDataDb = $false
$writesUserProjects = $false
$mutatesDatabanks = $false
$runsSqxTasks = $false
$launchesMt5 = $false
$runsMt5Ea = $false
$usesMigrationTool = $false
$directDbHistoryInsertAllowed = $false
$readOnlyDataDb = $true
$applyAllowed = $false

function Invoke-Auto6Python {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $argsList = @(
      '-m', 'core.sqx144_mt5_auto6_metadata_stability',
      $Action,
      '--project-root', $RepoRoot,
      '--broker', $Broker,
      '--symbol', $Symbol,
      '--spread-policy', $SpreadPolicy
    )

    if (-not [string]::IsNullOrWhiteSpace($ExpectedRequestId)) {
      $argsList += @('--expected-request-id', $ExpectedRequestId)
    }

    $raw = & $PythonExe @argsList
    if ($LASTEXITCODE -ne 0) {
      throw "sqx144_mt5_auto6_metadata_stability_python_failed"
    }
    return ($raw -join "`n") | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$payload = Invoke-Auto6Python

$payload | Add-Member -NotePropertyName wrapperVersion -NotePropertyValue $Version -Force
$payload | Add-Member -NotePropertyName writesSqxHost -NotePropertyValue $writesSqxHost -Force
$payload | Add-Member -NotePropertyName writesDataDb -NotePropertyValue $writesDataDb -Force
$payload | Add-Member -NotePropertyName writesUserProjects -NotePropertyValue $writesUserProjects -Force
$payload | Add-Member -NotePropertyName mutatesDatabanks -NotePropertyValue $mutatesDatabanks -Force
$payload | Add-Member -NotePropertyName runsSqxTasks -NotePropertyValue $runsSqxTasks -Force
$payload | Add-Member -NotePropertyName launchesMt5 -NotePropertyValue $launchesMt5 -Force
$payload | Add-Member -NotePropertyName runsMt5Ea -NotePropertyValue $runsMt5Ea -Force
$payload | Add-Member -NotePropertyName usesMigrationTool -NotePropertyValue $usesMigrationTool -Force
$payload | Add-Member -NotePropertyName directDbHistoryInsertAllowed -NotePropertyValue $directDbHistoryInsertAllowed -Force
$payload | Add-Member -NotePropertyName readOnlyDataDb -NotePropertyValue $readOnlyDataDb -Force
$payload | Add-Member -NotePropertyName applyAllowed -NotePropertyValue $applyAllowed -Force

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName applyApprovalReturned -NotePropertyValue $false -Force

$payload | ConvertTo-Json -Depth 24
