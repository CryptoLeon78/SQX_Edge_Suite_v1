param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'catalog-audit', 'bridge-validate', 'resolve-plan', 'import-plan', 'approval-template')]
  [string]$Action = 'status',

  [string]$Broker = 'darwinex',

  [string]$Symbol = '',

  [string]$DbPath = '',

  [string]$SpreadPolicy = 'p90',

  [string]$ExpectedRequestId = '',

  [string]$Timeframe = 'M1',

  [switch]$WithBridge
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto3-broker-catalog-resolver-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

$readOnlyDataDb = $true
$writesSqxHost = $false
$writesDataDb = $false
$writesUserProjects = $false
$mutatesDatabanks = $false
$runsSqxTasks = $false
$launchesMt5 = $false
$runsMt5Ea = $false
$usesMigrationTool = $false
$doesNotApplyToSqx = $true
$doesNotApplyInstrumentConfig = $true
$importExecutionAllowed = $false
$directDbHistoryInsertAllowed = $false

function Invoke-Auto3Python {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $argsList = @(
      '-m', 'core.sqx144_mt5_auto3_broker_catalog',
      $Action,
      '--project-root', $RepoRoot,
      '--broker', $Broker,
      '--spread-policy', $SpreadPolicy,
      '--timeframe', $Timeframe
    )

    if (-not [string]::IsNullOrWhiteSpace($Symbol)) {
      $argsList += @('--symbol', $Symbol)
    }
    if (-not [string]::IsNullOrWhiteSpace($DbPath)) {
      $argsList += @('--db-path', $DbPath)
    }
    if (-not [string]::IsNullOrWhiteSpace($ExpectedRequestId)) {
      $argsList += @('--expected-request-id', $ExpectedRequestId)
    }
    if ($WithBridge.IsPresent) {
      $argsList += '--with-bridge'
    }

    $raw = & $PythonExe @argsList
    if ($LASTEXITCODE -ne 0) {
      throw "sqx144_mt5_auto3_python_failed"
    }
    return ($raw -join "`n") | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$payload = Invoke-Auto3Python

$payload | Add-Member -NotePropertyName wrapperVersion -NotePropertyValue $Version -Force
$payload | Add-Member -NotePropertyName readOnlyDataDb -NotePropertyValue $readOnlyDataDb -Force
$payload | Add-Member -NotePropertyName writesSqxHost -NotePropertyValue $writesSqxHost -Force
$payload | Add-Member -NotePropertyName writesDataDb -NotePropertyValue $writesDataDb -Force
$payload | Add-Member -NotePropertyName writesUserProjects -NotePropertyValue $writesUserProjects -Force
$payload | Add-Member -NotePropertyName mutatesDatabanks -NotePropertyValue $mutatesDatabanks -Force
$payload | Add-Member -NotePropertyName runsSqxTasks -NotePropertyValue $runsSqxTasks -Force
$payload | Add-Member -NotePropertyName launchesMt5 -NotePropertyValue $launchesMt5 -Force
$payload | Add-Member -NotePropertyName runsMt5Ea -NotePropertyValue $runsMt5Ea -Force
$payload | Add-Member -NotePropertyName usesMigrationTool -NotePropertyValue $usesMigrationTool -Force
$payload | Add-Member -NotePropertyName doesNotApplyToSqx -NotePropertyValue $doesNotApplyToSqx -Force
$payload | Add-Member -NotePropertyName doesNotApplyInstrumentConfig -NotePropertyValue $doesNotApplyInstrumentConfig -Force
$payload | Add-Member -NotePropertyName importExecutionAllowed -NotePropertyValue $importExecutionAllowed -Force
$payload | Add-Member -NotePropertyName directDbHistoryInsertAllowed -NotePropertyValue $directDbHistoryInsertAllowed -Force

$payload | ConvertTo-Json -Depth 32
