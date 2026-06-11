param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'preflight', 'plan', 'install', 'rollback', 'approval-template', 'report')]
  [string]$Action = 'status',

  [string]$SqxRoot = '',
  [string]$Approval = '',
  [string]$BackupId = '',
  [switch]$Apply,
  [switch]$WriteEvidence
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-custom-results3-optional-manual-install-gate-v1'
$Phase = 'SQX144-CUSTOM-RESULTS3 - Optional Manual Install Gate'
$SourceReadyStatus = 'custom_results3_optional_manual_install_gate_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool'
$InstallApprovalPhrase = 'APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code'
$RollbackApprovalPhrase = 'APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL ROLLBACK host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback no_db_no_projects_no_databanks_no_tasks no_migration_tool'
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
    '-m', 'core.sqx144_custom_results3_install_gate',
    $Action,
    '--project-root', $RepoRoot
  )

  if (-not [string]::IsNullOrWhiteSpace($SqxRoot)) {
    $argsList += @('--sqx-root', $SqxRoot)
  }
  if (-not [string]::IsNullOrWhiteSpace($Approval)) {
    $argsList += @('--approval', $Approval)
  }
  if (-not [string]::IsNullOrWhiteSpace($BackupId)) {
    $argsList += @('--backup-id', $BackupId)
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
    throw 'sqx144_custom_results3_install_gate_failed'
  }
} finally {
  $env:PYTHONPATH = $oldPythonPath
}

if ([string]$payload.version -ne $Version) { throw 'sqx144_custom_results3_install_gate_version_mismatch' }
if ([string]$payload.phaseLabel -ne $Phase) { throw 'sqx144_custom_results3_install_gate_phase_mismatch' }

$defaults = [ordered]@{
  wrapperVersion = $Version
  sourceReadyStatus = $SourceReadyStatus
  installExecuted = $false
  rollbackExecuted = $false
  downloadedPluginsInstalled = $false
  copiesDownloadedThirdPartyPlugins = $false
  copiesSqxEdgeOwnedBundleOnly = $true
  writesDataDb = $false
  writesUserProjects = $false
  mutatesDatabanks = $false
  runsSqxTasks = $false
  launchesSqxRuntime = $false
  usesMigrationTool = $false
  approvalTemplates = [ordered]@{
    install = $InstallApprovalPhrase
    rollback = $RollbackApprovalPhrase
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
