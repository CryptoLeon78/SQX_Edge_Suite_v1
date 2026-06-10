param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'discover', 'preflight', 'plan', 'install-source', 'launch', 'stop', 'verify', 'approval-template')]
  [string]$Action = 'status',

  [string]$Mt5Root = '',
  [string]$Mt5FilesDir = '',
  [string]$Mt5ExpertsDir = '',
  [string]$Approval = '',
  [string]$Symbol = 'USDJPY_Darwinex',
  [ValidateSet('hidden', 'minimized')]
  [string]$WindowStyle = 'minimized',
  [int]$TimeoutSeconds = 45,
  [switch]$Overwrite,
  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto10-internal-mt5-runner-v1'
$Phase = 'SQX144-MT5-AUTO10'
$SourceReadyStatus = 'auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool'
$InstallApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER INSTALL host=sqx144_full mt5=darwinex no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool'
$LaunchApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER LAUNCH host=sqx144_full mt5=darwinex hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool'
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
    '-m', 'core.sqx144_mt5_auto10_internal_runner',
    $Action,
    '--project-root', $RepoRoot,
    '--symbol', $Symbol,
    '--window-style', $WindowStyle,
    '--timeout-seconds', [string]$TimeoutSeconds
  )

  if (-not [string]::IsNullOrWhiteSpace($Mt5Root)) {
    $argsList += @('--mt5-root', $Mt5Root)
  }
  if (-not [string]::IsNullOrWhiteSpace($Mt5FilesDir)) {
    $argsList += @('--mt5-files-dir', $Mt5FilesDir)
  }
  if (-not [string]::IsNullOrWhiteSpace($Mt5ExpertsDir)) {
    $argsList += @('--mt5-experts-dir', $Mt5ExpertsDir)
  }
  if (-not [string]::IsNullOrWhiteSpace($Approval)) {
    $argsList += @('--approval', $Approval)
  }
  if ($Overwrite) {
    $argsList += '--overwrite'
  }
  if ($Apply) {
    $argsList += '--apply'
  }

  $raw = & $PythonExe @argsList
  if ($LASTEXITCODE -ne 0) {
    throw "sqx144_mt5_auto10_internal_runner_python_failed"
  }
  $payload = ($raw -join "`n") | ConvertFrom-Json
} finally {
  $env:PYTHONPATH = $oldPythonPath
}

$defaults = [ordered]@{
  wrapperVersion = $Version
  phase = $Phase
  sourceReadyStatus = $SourceReadyStatus
  autoStartAllowed = $false
  writesDataDb = $false
  writesUserProjects = $false
  mutatesDatabanks = $false
  runsSqxTasks = $false
  placesOrders = $false
  usesMigrationTool = $false
  directDbHistoryInsertAllowed = $false
  historyImportAllowed = $false
  usesDataSourceHistoryImport = $false
  stopsOnlyManagedAuto10Pid = $true
}

foreach ($key in $defaults.Keys) {
  if ($payload.PSObject.Properties.Name -notcontains $key) {
    $payload | Add-Member -NotePropertyName $key -NotePropertyValue $defaults[$key] -Force
  }
}

if ($payload.PSObject.Properties.Name -notcontains 'approvalTemplates') {
  $payload | Add-Member -NotePropertyName approvalTemplates -NotePropertyValue ([ordered]@{
    install = $InstallApprovalPhrase
    launch = $LaunchApprovalPhrase
  }) -Force
}

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName tokensReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName licenseMaterialReturned -NotePropertyValue $false -Force

$payload | ConvertTo-Json -Depth 32
