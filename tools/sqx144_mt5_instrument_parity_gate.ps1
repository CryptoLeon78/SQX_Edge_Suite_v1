param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'audit', 'plan', 'backup', 'apply', 'verify', 'rollback')]
  [string]$Action = 'status',

  [string]$XmlPath,

  [string]$TargetInstrument = 'USDJPY_darwinex',

  [string]$BackupId,

  [string]$Approval,

  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-instrument-parity-gate-v1'
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
$localPathsReturned = $false
$readOnlyDataDb = $Action -in @('status', 'audit', 'plan', 'verify')
$offlineApplyOnly = $true

function Invoke-Mt5InstrumentParityPython {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $argsList = @(
      '-m', 'core.sqx144_mt5_instrument_parity',
      $Action,
      '--project-root', $RepoRoot,
      '--target-instrument', $TargetInstrument
    )

    if (-not [string]::IsNullOrWhiteSpace($XmlPath)) {
      $argsList += @('--xml-path', $XmlPath)
    }
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
      throw "sqx144_mt5_instrument_parity_python_failed"
    }
    return ($raw -join "`n") | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$payload = Invoke-Mt5InstrumentParityPython

$payload | Add-Member -NotePropertyName wrapperVersion -NotePropertyValue $Version -Force
$payload | Add-Member -NotePropertyName writesSqxHost -NotePropertyValue $writesSqxHost -Force
$payload | Add-Member -NotePropertyName writesDataDb -NotePropertyValue $writesDataDb -Force
$payload | Add-Member -NotePropertyName writesUserProjects -NotePropertyValue $writesUserProjects -Force
$payload | Add-Member -NotePropertyName mutatesDatabanks -NotePropertyValue $mutatesDatabanks -Force
$payload | Add-Member -NotePropertyName runsSqxTasks -NotePropertyValue $runsSqxTasks -Force
$payload | Add-Member -NotePropertyName launchesMt5 -NotePropertyValue $launchesMt5 -Force
$payload | Add-Member -NotePropertyName runsMt5Ea -NotePropertyValue $runsMt5Ea -Force
$payload | Add-Member -NotePropertyName usesMigrationTool -NotePropertyValue $usesMigrationTool -Force
$payload | Add-Member -NotePropertyName readOnlyDataDb -NotePropertyValue $readOnlyDataDb -Force
$payload | Add-Member -NotePropertyName offlineApplyOnly -NotePropertyValue $offlineApplyOnly -Force

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $localPathsReturned -Force

$payload | ConvertTo-Json -Depth 24
