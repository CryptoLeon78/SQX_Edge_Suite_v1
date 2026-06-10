param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'audit', 'plan', 'backup', 'apply', 'verify', 'rollback')]
  [string]$Action = 'status',

  [string]$Broker = 'darwinex',

  [string]$Symbol = 'AUDCAD_darwinex',

  [string]$SpreadPolicy = 'p90',

  [string]$BackupId,

  [string]$Approval,

  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto5-metadata-apply-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

$writesSqxHost = $Action -in @('backup', 'apply', 'rollback')
$writesDataDb = $Action -eq 'apply'
$writesUserProjects = $false
$mutatesDatabanks = $false
$runsSqxTasks = $false
$launchesMt5 = $false
$runsMt5Ea = $false
$usesMigrationTool = $false
$directDbHistoryInsertAllowed = $false
$readOnlyDataDb = $Action -in @('status', 'audit', 'plan', 'verify')
$offlineApplyOnly = $true

function Invoke-Auto5Python {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $argsList = @(
      '-m', 'core.sqx144_mt5_auto5_metadata_apply',
      $Action,
      '--project-root', $RepoRoot,
      '--broker', $Broker,
      '--symbol', $Symbol,
      '--spread-policy', $SpreadPolicy
    )

    if (-not [string]::IsNullOrWhiteSpace($BackupId)) {
      $argsList += @('--backup-id', $BackupId)
    }
    if (-not [string]::IsNullOrWhiteSpace($Approval)) {
      $argsList += @('--approval', $Approval)
    }
    if ($Apply.IsPresent) {
      $argsList += '--apply'
    }

    $raw = & $PythonExe @argsList
    if ($LASTEXITCODE -ne 0) {
      throw "sqx144_mt5_auto5_metadata_apply_python_failed"
    }
    return ($raw -join "`n") | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$payload = Invoke-Auto5Python

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
$payload | Add-Member -NotePropertyName offlineApplyOnly -NotePropertyValue $offlineApplyOnly -Force

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $false -Force

$payload | ConvertTo-Json -Depth 24
