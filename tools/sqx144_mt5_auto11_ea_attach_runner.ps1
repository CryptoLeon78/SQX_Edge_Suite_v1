param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'profile-catalog', 'preflight', 'plan', 'attach-plan', 'ui-fallback-plan', 'approval-template')]
  [string]$Action = 'status',

  [string]$HostProfile = 'sqx144_full',
  [string]$Mt5Profile = 'darwinex',
  [string]$Mt5Root = '',
  [string]$Mt5FilesDir = '',
  [string]$Mt5ExpertsDir = '',
  [string]$Symbol = 'USDJPY_Darwinex',
  [string]$Timeframe = 'M1',
  [string]$Approval = '',
  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto11-ea-attach-runner-v1'
$Phase = 'SQX144-MT5-AUTO11'
$SourceReadyStatus = 'auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool'
$AttachApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO11 EA ATTACH RUNNER APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool'
$UiFallbackApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO11 UI FALLBACK APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 visible_operator_control no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool'
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
    '-m', 'core.sqx144_mt5_auto11_ea_attach_runner',
    $Action,
    '--project-root', $RepoRoot,
    '--host', $HostProfile,
    '--mt5-profile', $Mt5Profile,
    '--symbol', $Symbol,
    '--timeframe', $Timeframe
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
  if ($Apply) {
    $argsList += '--apply'
  }

  $raw = & $PythonExe @argsList
  if ($LASTEXITCODE -ne 0) {
    throw "sqx144_mt5_auto11_ea_attach_runner_python_failed"
  }
  $payload = ($raw -join "`n") | ConvertFrom-Json
} finally {
  $env:PYTHONPATH = $oldPythonPath
}

$defaults = [ordered]@{
  wrapperVersion = $Version
  phase = $Phase
  sourceReadyStatus = $SourceReadyStatus
  genericMt5SqxProfileAware = $true
  autoStartAllowed = $false
  attachAllowedByGate = $false
  uiFallbackAllowedByGate = $false
  writesMt5Profile = $false
  writesMt5Template = $false
  writesMt5StartupConfig = $false
  writesDataDb = $false
  writesUserProjects = $false
  mutatesDatabanks = $false
  runsSqxTasks = $false
  launchesMt5 = $false
  runsMt5Ea = $false
  placesOrders = $false
  usesMigrationTool = $false
  directDbHistoryInsertAllowed = $false
  historyImportAllowed = $false
  usesDataSourceHistoryImport = $false
}

foreach ($key in $defaults.Keys) {
  if ($payload.PSObject.Properties.Name -notcontains $key) {
    $payload | Add-Member -NotePropertyName $key -NotePropertyValue $defaults[$key] -Force
  }
}

if ($payload.PSObject.Properties.Name -notcontains 'approvalTemplates') {
  $payload | Add-Member -NotePropertyName approvalTemplates -NotePropertyValue ([ordered]@{
    attach = $AttachApprovalPhrase
    uiFallback = $UiFallbackApprovalPhrase
  }) -Force
}

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName tokensReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName licenseMaterialReturned -NotePropertyValue $false -Force

$payload | ConvertTo-Json -Depth 32
