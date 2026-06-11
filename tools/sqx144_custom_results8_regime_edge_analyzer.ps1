param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'smoke', 'report', 'approval-template', 'install')]
  [string]$Action = 'status',

  [string]$SqxRoot = '',
  [string]$Approval = '',
  [switch]$Apply,
  [switch]$WriteEvidence
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-custom-results8-regime-edge-analyzer-v1'
$Phase = 'SQX144-CUSTOM-RESULTS8 - Regime Edge Analyzer'
$SourceReadyStatus = 'custom_results8_regime_edge_analyzer_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool'
$InstallApprovalPhrase = 'APRUEBO SQX144 CUSTOM RESULTS8 REGIME EDGE ANALYZER INSTALL host=sqx144_full plugin=sqx_regime_edge_analyzer sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code'
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
    '-m', 'core.sqx144_custom_results8_regime_edge_analyzer',
    $Action,
    '--project-root', $RepoRoot
  )

  if (-not [string]::IsNullOrWhiteSpace($SqxRoot)) {
    $argsList += @('--sqx-root', $SqxRoot)
  }
  if (-not [string]::IsNullOrWhiteSpace($Approval)) {
    $argsList += @('--approval', $Approval)
  }
  if ($Apply) {
    $argsList += '--apply'
  }
  if ($WriteEvidence) {
    $argsList += '--write-evidence'
  }

  $raw = & $PythonExe @argsList
  $exitCode = $LASTEXITCODE
  $payload = ($raw -join "`n") | ConvertFrom-Json
  if ($exitCode -ne 0 -and -not $payload) {
    throw 'sqx144_custom_results8_regime_edge_analyzer_failed'
  }
} finally {
  $env:PYTHONPATH = $oldPythonPath
}

if ([string]$payload.version -ne $Version) { throw 'sqx144_custom_results8_regime_edge_analyzer_version_mismatch' }
if ([string]$payload.phaseLabel -ne $Phase) { throw 'sqx144_custom_results8_regime_edge_analyzer_phase_mismatch' }

$defaults = [ordered]@{
  wrapperVersion = $Version
  sourceReadyStatus = $SourceReadyStatus
  installExecuted = $false
  writesDataDb = $false
  writesUserProjects = $false
  mutatesDatabanks = $false
  runsSqxTasks = $false
  launchesSqxRuntime = $false
  usesMigrationTool = $false
  approvalTemplates = [ordered]@{
    install = $InstallApprovalPhrase
  }
}

foreach ($key in $defaults.Keys) {
  if ($payload.PSObject.Properties.Name -notcontains $key) {
    $payload | Add-Member -NotePropertyName $key -NotePropertyValue $defaults[$key] -Force
  }
}

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName rawOrdersReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName rawOrdersReturnedByTooling -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName sourceCodeReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName tokensReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName secretsReturned -NotePropertyValue $false -Force
$payload.privacy | Add-Member -NotePropertyName licenseMaterialReturned -NotePropertyValue $false -Force

$payload | ConvertTo-Json -Depth 96
