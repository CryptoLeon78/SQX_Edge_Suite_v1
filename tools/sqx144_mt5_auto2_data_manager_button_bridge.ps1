param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'plan', 'install', 'rollback')]
  [string]$Action = 'status',

  [string]$SqxRoot = '',
  [string]$BackupId = '',
  [string]$Approval = '',
  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto2-data-manager-button-bridge-v1'
$LegacyAssetVersion = 'sqx144-mt5-auto2-data-manager-button-bridge-v1-data-sources-visible'
$PreviousAssetVersion = 'sqx144-mt5-auto9c-visual-es-selection-v1'
$AssetVersion = 'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1'
$ReadyStatus = 'auto2_overlay_api_install_gate_ready_no_install'
$InstalledStatus = 'auto2_overlay_installed_verified_no_db_no_projects_no_databanks'
$Auto4InstalledStatus = 'auto4_overlay_installed_verified_no_db_no_projects_no_databanks_no_tasks'
$Auto6SourceReadyStatus = 'auto6_datamanager_stability_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks'
$Auto6InstalledStatus = 'auto6_datamanager_stability_installed_verified_no_db_no_projects_no_databanks_no_tasks'
$Auto6SelectionGuardSourceReadyStatus = 'auto6_datamanager_selection_guard_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks'
$Auto6SelectionGuardInstalledStatus = 'auto6_datamanager_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks'
$Auto7SourceReadyStatus = 'auto7_datamanager_dukascopy_mirror_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_mt5'
$Auto7InstalledStatus = 'auto7_datamanager_dukascopy_mirror_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5'
$Auto7DataSymbolGuardSourceReadyStatus = 'auto7_datamanager_data_symbol_selection_guard_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_mt5'
$Auto7DataSymbolGuardInstalledStatus = 'auto7_datamanager_data_symbol_selection_guard_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_mt5'
$Auto8NativeSaveSourceReadyStatus = 'auto8_datamanager_native_save_apply_source_ready_no_install_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import'
$Auto8NativeSaveInstalledStatus = 'auto8_datamanager_native_save_apply_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import'
$Auto8UxStatusSourceReadyStatus = 'auto8_datamanager_native_save_ux_status_source_ready_no_install_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import'
$Auto8UxStatusInstalledStatus = 'auto8_datamanager_native_save_ux_status_installed_verified_no_direct_db_no_projects_no_databanks_no_tasks_no_mt5_no_history_import'
$Auto9HealthSourceReadyStatus = 'auto9_datamanager_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9HealthInstalledStatus = 'auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9SingleClickUxSourceReadyStatus = 'auto9_datamanager_single_click_ux_source_ready_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9SingleClickUxInstalledStatus = 'auto9_datamanager_single_click_ux_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9CheckedRowSelectionSourceReadyStatus = 'auto9_datamanager_checkbox_only_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9CheckedRowSelectionInstalledStatus = 'auto9_datamanager_checkbox_only_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9VisualEsSelectionSourceReadyStatus = 'auto9_datamanager_visual_es_selection_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9VisualEsSelectionInstalledStatus = 'auto9_datamanager_visual_es_selection_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9DataSymbolPrioritySourceReadyStatus = 'auto9_datamanager_data_symbol_priority_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$Auto9DataSymbolPriorityInstalledStatus = 'auto9_datamanager_data_symbol_priority_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SourceRoot = Join-Path $RepoRoot 'integrations\sqx144\datamanager_mt5_auto2_overlay'
$CssName = 'sqx-edge-mt5-auto2.css'
$JsName = 'sqx-edge-mt5-auto2.js'
$Marker = 'sqx-edge-mt5-auto2'
$Auto4Marker = 'sqx144-mt5-auto4-datamanager-catalog-triage-v1'
$Auto6Marker = 'sqx144-mt5-auto6-metadata-stability-policy-v1'
$SelectionGuardMarker = 'sqx144-mt5-auto6-datamanager-selection-guard-v1'
$Auto7Marker = 'sqx144-mt5-auto7-dukascopy-metadata-mirror-v1'
$Auto7DataSymbolGuardMarker = 'sqx144-mt5-auto7-datamanager-data-symbol-selection-guard-v1'
$Auto8NativeSaveMarker = 'sqx144-mt5-auto8-datamanager-native-save-apply-v1'
$Auto8UxStatusMarker = 'sqx144-mt5-auto8-datamanager-native-save-ux-status-v1'
$Auto9HealthMarker = 'sqx144-mt5-auto9-datamanager-health-watchdog-v1'
$Auto9HealthPollStopMarker = 'sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1'
$Auto9SingleClickUxMarker = 'sqx144-mt5-auto9-datamanager-single-click-ux-v1'
$Auto9CheckedRowSelectionMarker = 'sqx144-mt5-auto9c-datamanager-checked-row-selection-v1'
$Auto9VisualEsSelectionMarker = 'sqx144-mt5-auto9c-visual-es-selection-v1'
$Auto9DataSymbolPriorityMarker = 'sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1'
$LegacyApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO2 DATAMANAGER INSTALL host=sqx144_full no_db_no_projects_no_databanks'
$ApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO4 DATAMANAGER TRIAGE INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks'
$Auto6ApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO6 DATAMANAGER STABILITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import'
$Auto7ApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO7 DATAMANAGER DUKASCOPY MIRROR INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5'
$Auto8ApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO8 DATAMANAGER NATIVE SAVE APPLY INSTALL host=sqx144_full native_save_apply_only no_direct_db no_history_import no_projects_no_databanks_no_tasks no_mt5 no_migration_tool'
$Auto8UxStatusApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO8 DATAMANAGER UX STATUS INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool'
$Auto9HealthApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool'
$Auto9SingleClickUxApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO9B DATAMANAGER SINGLE CLICK UX INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool'
$Auto9CheckedRowSelectionApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO9C DATAMANAGER CHECKBOX ONLY SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool'
$Auto9VisualEsSelectionApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO9C UX ES SELECTION INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool'
$Auto9DataSymbolPriorityApprovalPhrase = 'APRUEBO SQX144 MT5 AUTO9D DATAMANAGER DATA SYMBOL PRIORITY INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool'
$ExpectedHostProfile = 'sqx144_full'
$ExpectedRootName = 'SQX_144_Full'

function Resolve-SqxRoot {
  if ($SqxRoot) { return $SqxRoot }
  if ($env:SQX144_ROOT) { return $env:SQX144_ROOT }
  $configPath = Join-Path $RepoRoot 'backend\sqx-edge-tool\config.json'
  if (Test-Path -LiteralPath $configPath) {
    try {
      $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
      if ($config.sqx_path) { return [string]$config.sqx_path }
    } catch {
      return ''
    }
  }
  $defaultRoot = 'C:\BOTS\Versiones\SQX_144_Full'
  if (Test-Path -LiteralPath $defaultRoot) { return $defaultRoot }
  return ''
}

$ResolvedSqxRoot = Resolve-SqxRoot
$IndexPath = if ($ResolvedSqxRoot) { Join-Path $ResolvedSqxRoot 'internal\web\SQMANAGER\index.html' } else { '' }
$CommonRoot = if ($ResolvedSqxRoot) { Join-Path $ResolvedSqxRoot 'internal\web\common' } else { '' }
$BackupRoot = if ($ResolvedSqxRoot) { Join-Path $ResolvedSqxRoot '.local_code_backups' } else { '' }
$CssTarget = if ($CommonRoot) { Join-Path $CommonRoot $CssName } else { '' }
$JsTarget = if ($CommonRoot) { Join-Path $CommonRoot $JsName } else { '' }

function New-Result {
  param(
    [bool]$Ok,
    [string]$Status,
    [string[]]$Blockers = @(),
    [string[]]$Warnings = @(),
    [hashtable]$Extra = @{}
  )
  $payload = [ordered]@{
    ok = $Ok
    version = $Version
    assetVersion = $AssetVersion
    phase = 'SQX144-MT5-AUTO2'
    action = $Action
    status = $Status
    dryRun = -not [bool]$Apply
    dataManagerButtonPlanned = $true
    dataManagerButtonInstalled = $false
    writesSqxHost = $false
    writesDataDb = $false
    writesUserProjects = $false
    mutatesDatabanks = $false
    runsSqxTasks = $false
    launchesMt5 = $false
    runsMt5Ea = $false
    usesMigrationTool = $false
    healthWatchdogObserveOnly = $true
    autoStartAllowed = $false
    doesNotApplyToSqx = $false
    doesNotApplyInstrumentConfig = $false
    doesNotApplyToSqxByDirectDb = $true
    doesNotApplyInstrumentConfigDuringInstall = $true
    nativeDataManagerSaveAllowed = $true
    sqxOpenNativeSaveAllowed = $true
    directDbWriteAllowed = $false
    directDbHistoryInsertAllowed = $false
    historyImportAllowed = $false
    usesDataSourceHistoryImport = $false
    writesSqxOverlayHostOnApply = $false
    hostProfile = $ExpectedHostProfile
    blockers = $Blockers
    warnings = $Warnings
    privacy = @{
      localPathsReturned = $false
      tokensReturned = $false
      licenseMaterialReturned = $false
    }
  }
  foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
  return $payload
}

function Get-SqxProcesses {
  return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @('StrategyQuantX', 'StrategyQuantX_nocheck', 'StrategyQuantX_ui', 'CodeEditor', 'sqcli', 'SQ.Client.CLI')
  })
}

function Test-SqxRootProfile {
  if (-not $ResolvedSqxRoot) { return $false }
  $resolved = $ResolvedSqxRoot
  try {
    $resolved = (Resolve-Path -LiteralPath $ResolvedSqxRoot -ErrorAction Stop).Path
  } catch {
    $resolved = $ResolvedSqxRoot
  }
  $leaf = Split-Path -Leaf $resolved
  if ($leaf -ne $ExpectedRootName) { return $false }
  if ($resolved -match '144\.2953|SQX_144_2953|SQX144_FULL_UPDATE2') { return $false }
  return $true
}

function Get-InstalledState {
  $indexExists = if ($IndexPath) { Test-Path -LiteralPath $IndexPath } else { $false }
  $indexText = if ($indexExists) { Get-Content -LiteralPath $IndexPath -Raw } else { '' }
  $includeMatches = if ($indexText) { [regex]::Matches($indexText, [regex]::Escape($Marker)) } else { @() }
  return @{
    indexExists = $indexExists
    commonExists = if ($CommonRoot) { Test-Path -LiteralPath $CommonRoot } else { $false }
    sourceJsExists = Test-Path -LiteralPath (Join-Path $SourceRoot $JsName)
    sourceCssExists = Test-Path -LiteralPath (Join-Path $SourceRoot $CssName)
    targetJsExists = if ($JsTarget) { Test-Path -LiteralPath $JsTarget } else { $false }
    targetCssExists = if ($CssTarget) { Test-Path -LiteralPath $CssTarget } else { $false }
    includesPresent = $includeMatches.Count -gt 0
    includeCount = $includeMatches.Count
  }
}

function Test-SourceHasAuto4 {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto4Marker)
}

function Test-TargetHasAuto4 {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto4Marker)
}

function Test-SourceHasAuto6 {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto6Marker)
}

function Test-TargetHasAuto6 {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto6Marker)
}

function Test-SourceHasSelectionGuard {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($SelectionGuardMarker)
}

function Test-TargetHasSelectionGuard {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($SelectionGuardMarker)
}

function Test-SourceHasAuto7 {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto7Marker)
}

function Test-TargetHasAuto7 {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto7Marker)
}

function Test-SourceHasAuto7DataSymbolGuard {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto7DataSymbolGuardMarker)
}

function Test-TargetHasAuto7DataSymbolGuard {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto7DataSymbolGuardMarker)
}

function Test-SourceHasAuto8NativeSave {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto8NativeSaveMarker)
}

function Test-TargetHasAuto8NativeSave {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto8NativeSaveMarker)
}

function Test-SourceHasAuto8UxStatus {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto8UxStatusMarker)
}

function Test-TargetHasAuto8UxStatus {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto8UxStatusMarker)
}

function Test-SourceHasAuto9Health {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto9HealthMarker)
}

function Test-TargetHasAuto9Health {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto9HealthMarker)
}

function Test-SourceHasAuto9SingleClickUx {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto9SingleClickUxMarker)
}

function Test-TargetHasAuto9SingleClickUx {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto9SingleClickUxMarker)
}

function Test-SourceHasAuto9CheckedRowSelection {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto9CheckedRowSelectionMarker)
}

function Test-TargetHasAuto9CheckedRowSelection {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto9CheckedRowSelectionMarker)
}

function Test-SourceHasAuto9VisualEsSelection {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto9VisualEsSelectionMarker)
}

function Test-TargetHasAuto9VisualEsSelection {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto9VisualEsSelectionMarker)
}

function Test-SourceHasAuto9DataSymbolPriority {
  $sourceJs = Join-Path $SourceRoot $JsName
  if (-not (Test-Path -LiteralPath $sourceJs)) { return $false }
  $sourceText = Get-Content -LiteralPath $sourceJs -Raw
  return $sourceText.Contains($Auto9DataSymbolPriorityMarker)
}

function Test-TargetHasAuto9DataSymbolPriority {
  if (-not $JsTarget -or -not (Test-Path -LiteralPath $JsTarget)) { return $false }
  $targetText = Get-Content -LiteralPath $JsTarget -Raw
  return $targetText.Contains($Auto9DataSymbolPriorityMarker)
}

function Get-RequiredApprovalPhrase {
  if (Test-SourceHasAuto9DataSymbolPriority) { return $Auto9DataSymbolPriorityApprovalPhrase }
  if (Test-SourceHasAuto9VisualEsSelection) { return $Auto9VisualEsSelectionApprovalPhrase }
  if (Test-SourceHasAuto9CheckedRowSelection) { return $Auto9CheckedRowSelectionApprovalPhrase }
  if (Test-SourceHasAuto9SingleClickUx) { return $Auto9SingleClickUxApprovalPhrase }
  if (Test-SourceHasAuto9Health) { return $Auto9HealthApprovalPhrase }
  if (Test-SourceHasAuto8UxStatus) { return $Auto8UxStatusApprovalPhrase }
  if (Test-SourceHasAuto8NativeSave) { return $Auto8ApprovalPhrase }
  if (Test-SourceHasAuto7) { return $Auto7ApprovalPhrase }
  if (Test-SourceHasAuto6) { return $Auto6ApprovalPhrase }
  if (Test-SourceHasAuto4) { return $ApprovalPhrase }
  return $LegacyApprovalPhrase
}

function Get-InstallStatusMarker {
  param([bool]$Installed)
  if ($Installed -and (Test-TargetHasAuto9DataSymbolPriority)) { return $Auto9DataSymbolPriorityInstalledStatus }
  if (Test-SourceHasAuto9DataSymbolPriority) { return $Auto9DataSymbolPrioritySourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto9VisualEsSelection)) { return $Auto9VisualEsSelectionInstalledStatus }
  if (Test-SourceHasAuto9VisualEsSelection) { return $Auto9VisualEsSelectionSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto9CheckedRowSelection)) { return $Auto9CheckedRowSelectionInstalledStatus }
  if (Test-SourceHasAuto9CheckedRowSelection) { return $Auto9CheckedRowSelectionSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto9SingleClickUx)) { return $Auto9SingleClickUxInstalledStatus }
  if (Test-SourceHasAuto9SingleClickUx) { return $Auto9SingleClickUxSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto9Health)) { return $Auto9HealthInstalledStatus }
  if (Test-SourceHasAuto9Health) { return $Auto9HealthSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto8UxStatus)) { return $Auto8UxStatusInstalledStatus }
  if (Test-SourceHasAuto8UxStatus) { return $Auto8UxStatusSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto8NativeSave)) { return $Auto8NativeSaveInstalledStatus }
  if ((Test-SourceHasAuto8NativeSave) -and -not (Test-TargetHasAuto8NativeSave)) { return $Auto8NativeSaveSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto7DataSymbolGuard)) { return $Auto7DataSymbolGuardInstalledStatus }
  if ((Test-SourceHasAuto7DataSymbolGuard) -and -not (Test-TargetHasAuto7DataSymbolGuard)) { return $Auto7DataSymbolGuardSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto7)) { return $Auto7InstalledStatus }
  if ((Test-SourceHasAuto7) -and -not (Test-TargetHasAuto7)) { return $Auto7SourceReadyStatus }
  if ($Installed -and (Test-TargetHasSelectionGuard)) { return $Auto6SelectionGuardInstalledStatus }
  if ((Test-SourceHasSelectionGuard) -and -not (Test-TargetHasSelectionGuard)) { return $Auto6SelectionGuardSourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto6)) { return $Auto6InstalledStatus }
  if ((Test-SourceHasAuto6) -and -not (Test-TargetHasAuto6)) { return $Auto6SourceReadyStatus }
  if ($Installed -and (Test-TargetHasAuto4)) { return $Auto4InstalledStatus }
  if ($Installed) { return $InstalledStatus }
  return $ReadyStatus
}

function Add-ManifestEntry {
  param(
    [System.Collections.ArrayList]$Entries,
    [string]$Role,
    [string]$Path
  )
  if (Test-Path -LiteralPath $Path) {
    $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $Path
    [void]$Entries.Add([ordered]@{
      role = $Role
      fileName = Split-Path $Path -Leaf
      sha256 = $hash.Hash
      length = (Get-Item -LiteralPath $Path).Length
    })
  } else {
    [void]$Entries.Add([ordered]@{
      role = $Role
      fileName = Split-Path $Path -Leaf
      missing = $true
    })
  }
}

function New-Backup {
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $backup = Join-Path $BackupRoot "sqx144_mt5_auto2_button_$stamp"
  New-Item -ItemType Directory -Force -Path $backup | Out-Null
  Copy-Item -LiteralPath $IndexPath -Destination (Join-Path $backup 'SQMANAGER_index.html') -Force
  if (Test-Path -LiteralPath $CssTarget) {
    Copy-Item -LiteralPath $CssTarget -Destination (Join-Path $backup $CssName) -Force
  }
  if (Test-Path -LiteralPath $JsTarget) {
    Copy-Item -LiteralPath $JsTarget -Destination (Join-Path $backup $JsName) -Force
  }

  $entries = New-Object System.Collections.ArrayList
  Add-ManifestEntry -Entries $entries -Role 'host_index_before' -Path $IndexPath
  Add-ManifestEntry -Entries $entries -Role 'host_css_before' -Path $CssTarget
  Add-ManifestEntry -Entries $entries -Role 'host_js_before' -Path $JsTarget
  $manifest = [ordered]@{
    version = $Version
    backupId = Split-Path $backup -Leaf
    createdAt = (Get-Date).ToString('o')
    files = $entries
    privacy = @{ localPathsReturned = $false }
  }
  $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $backup 'backup_manifest.json') -Encoding UTF8
  return $backup
}

function Test-InstallReadiness {
  $state = Get-InstalledState
  $blockers = @()
  if (-not $ResolvedSqxRoot) { $blockers += 'sqx_root_not_configured' }
  if ($ResolvedSqxRoot -and -not (Test-SqxRootProfile)) { $blockers += 'sqx144_full_root_mismatch' }
  if (-not $state.indexExists) { $blockers += 'sqmanager_index_missing' }
  if (-not $state.commonExists) { $blockers += 'common_root_missing' }
  if (-not $state.sourceJsExists) { $blockers += 'source_js_missing' }
  if (-not $state.sourceCssExists) { $blockers += 'source_css_missing' }
  if ($state.includeCount -gt 2) { $blockers += 'duplicate_include_markers' }
  $processes = Get-SqxProcesses
  if ($processes.Count -gt 0) { $blockers += 'sqx_process_running' }
  return @{
    state = $state
    blockers = $blockers
    processCount = $processes.Count
  }
}

function Install-Overlay {
  $readiness = Test-InstallReadiness
  if ($readiness.blockers.Count -gt 0) {
    return New-Result -Ok $false -Status 'blocked' -Blockers $readiness.blockers
  }
  $requiredApproval = Get-RequiredApprovalPhrase
  if (-not $Apply) {
    return New-Result -Ok $true -Status 'ready_to_install' -Extra @{
      installStatusMarker = (Get-InstallStatusMarker -Installed $readiness.state.includesPresent)
      installed = $readiness.state.includesPresent
      processCount = $readiness.processCount
      requiresApply = $true
      approvalTemplate = $requiredApproval
      legacyApprovalTemplate = $LegacyApprovalPhrase
      sourceHasAuto4 = (Test-SourceHasAuto4)
      targetHasAuto4 = (Test-TargetHasAuto4)
      sourceHasAuto6 = (Test-SourceHasAuto6)
      targetHasAuto6 = (Test-TargetHasAuto6)
      sourceHasSelectionGuard = (Test-SourceHasSelectionGuard)
      targetHasSelectionGuard = (Test-TargetHasSelectionGuard)
      sourceHasAuto7 = (Test-SourceHasAuto7)
      targetHasAuto7 = (Test-TargetHasAuto7)
      sourceHasAuto7DataSymbolGuard = (Test-SourceHasAuto7DataSymbolGuard)
      targetHasAuto7DataSymbolGuard = (Test-TargetHasAuto7DataSymbolGuard)
      sourceHasAuto8NativeSave = (Test-SourceHasAuto8NativeSave)
      targetHasAuto8NativeSave = (Test-TargetHasAuto8NativeSave)
      sourceHasAuto8UxStatus = (Test-SourceHasAuto8UxStatus)
      targetHasAuto8UxStatus = (Test-TargetHasAuto8UxStatus)
      sourceHasAuto9HealthWatchdog = (Test-SourceHasAuto9Health)
      targetHasAuto9HealthWatchdog = (Test-TargetHasAuto9Health)
      sourceHasAuto9SingleClickUx = (Test-SourceHasAuto9SingleClickUx)
      targetHasAuto9SingleClickUx = (Test-TargetHasAuto9SingleClickUx)
      sourceHasAuto9CheckedRowSelection = (Test-SourceHasAuto9CheckedRowSelection)
      targetHasAuto9CheckedRowSelection = (Test-TargetHasAuto9CheckedRowSelection)
      sourceHasAuto9VisualEsSelection = (Test-SourceHasAuto9VisualEsSelection)
      targetHasAuto9VisualEsSelection = (Test-TargetHasAuto9VisualEsSelection)
      sourceHasAuto9DataSymbolPriority = (Test-SourceHasAuto9DataSymbolPriority)
      targetHasAuto9DataSymbolPriority = (Test-TargetHasAuto9DataSymbolPriority)
      writesSqxHostOnApply = $true
      writesSqxOverlayHostOnApply = $true
      hostRootAccepted = (Test-SqxRootProfile)
      expectedRootName = $ExpectedRootName
    }
  }
  if ($Approval -ne $requiredApproval) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('approval_phrase_required') -Extra @{
      approvalTemplate = $requiredApproval
      legacyApprovalTemplate = $LegacyApprovalPhrase
      sourceHasAuto4 = (Test-SourceHasAuto4)
      targetHasAuto4 = (Test-TargetHasAuto4)
      sourceHasAuto6 = (Test-SourceHasAuto6)
      targetHasAuto6 = (Test-TargetHasAuto6)
      sourceHasSelectionGuard = (Test-SourceHasSelectionGuard)
      targetHasSelectionGuard = (Test-TargetHasSelectionGuard)
      sourceHasAuto7 = (Test-SourceHasAuto7)
      targetHasAuto7 = (Test-TargetHasAuto7)
      sourceHasAuto7DataSymbolGuard = (Test-SourceHasAuto7DataSymbolGuard)
      targetHasAuto7DataSymbolGuard = (Test-TargetHasAuto7DataSymbolGuard)
      sourceHasAuto8NativeSave = (Test-SourceHasAuto8NativeSave)
      targetHasAuto8NativeSave = (Test-TargetHasAuto8NativeSave)
      sourceHasAuto8UxStatus = (Test-SourceHasAuto8UxStatus)
      targetHasAuto8UxStatus = (Test-TargetHasAuto8UxStatus)
      sourceHasAuto9HealthWatchdog = (Test-SourceHasAuto9Health)
      targetHasAuto9HealthWatchdog = (Test-TargetHasAuto9Health)
      sourceHasAuto9SingleClickUx = (Test-SourceHasAuto9SingleClickUx)
      targetHasAuto9SingleClickUx = (Test-TargetHasAuto9SingleClickUx)
      sourceHasAuto9CheckedRowSelection = (Test-SourceHasAuto9CheckedRowSelection)
      targetHasAuto9CheckedRowSelection = (Test-TargetHasAuto9CheckedRowSelection)
      sourceHasAuto9VisualEsSelection = (Test-SourceHasAuto9VisualEsSelection)
      targetHasAuto9VisualEsSelection = (Test-TargetHasAuto9VisualEsSelection)
      sourceHasAuto9DataSymbolPriority = (Test-SourceHasAuto9DataSymbolPriority)
      targetHasAuto9DataSymbolPriority = (Test-TargetHasAuto9DataSymbolPriority)
    }
  }

  $backup = New-Backup
  Copy-Item -LiteralPath (Join-Path $SourceRoot $CssName) -Destination $CssTarget -Force
  Copy-Item -LiteralPath (Join-Path $SourceRoot $JsName) -Destination $JsTarget -Force

  $html = Get-Content -LiteralPath $IndexPath -Raw
  $html = [regex]::Replace($html, '(?im)^[^\r\n]*(sqx-edge-mt5-auto2\.css|sqx-edge-mt5-auto2\.js)(\?v=[^"`'']+)?[^\r\n]*(\r?\n)?', '')
  $include = @(
    "    <link rel=`"stylesheet`" href=`"common/${CssName}?v=${AssetVersion}`">",
    "    <script src=`"common/${JsName}?v=${AssetVersion}`"></script>"
  ) -join "`r`n"
  $layoutScript = '<script src="SQMANAGER/build/layout.js"></script>'
  if ($html.Contains($layoutScript)) {
    $html = $html.Replace($layoutScript, "$layoutScript`r`n$include")
  } else {
    $headMatch = [regex]::Match($html, '</head>', 'IgnoreCase')
    if (-not $headMatch.Success) {
      return New-Result -Ok $false -Status 'blocked' -Blockers @('sqmanager_head_tag_missing')
    }
    $html = $html.Insert($headMatch.Index, "$include`r`n")
  }
  Set-Content -LiteralPath $IndexPath -Value $html -Encoding UTF8
  return New-Result -Ok $true -Status 'installed' -Extra @{
    backupRef = (Split-Path $backup -Leaf)
    installed = $true
    dataManagerButtonInstalled = $true
    writesSqxHost = $true
    writesSqxHostOnApply = $true
    writesSqxOverlayHostOnApply = $true
    writesSqxOverlayHost = $true
    sourceHasAuto6 = (Test-SourceHasAuto6)
    targetHasAuto6 = (Test-TargetHasAuto6)
    sourceHasSelectionGuard = (Test-SourceHasSelectionGuard)
    targetHasSelectionGuard = (Test-TargetHasSelectionGuard)
    sourceHasAuto7 = (Test-SourceHasAuto7)
    targetHasAuto7 = (Test-TargetHasAuto7)
    sourceHasAuto7DataSymbolGuard = (Test-SourceHasAuto7DataSymbolGuard)
    targetHasAuto7DataSymbolGuard = (Test-TargetHasAuto7DataSymbolGuard)
    sourceHasAuto8NativeSave = (Test-SourceHasAuto8NativeSave)
    targetHasAuto8NativeSave = (Test-TargetHasAuto8NativeSave)
    sourceHasAuto8UxStatus = (Test-SourceHasAuto8UxStatus)
    targetHasAuto8UxStatus = (Test-TargetHasAuto8UxStatus)
    sourceHasAuto9HealthWatchdog = (Test-SourceHasAuto9Health)
    targetHasAuto9HealthWatchdog = (Test-TargetHasAuto9Health)
    sourceHasAuto9SingleClickUx = (Test-SourceHasAuto9SingleClickUx)
    targetHasAuto9SingleClickUx = (Test-TargetHasAuto9SingleClickUx)
    sourceHasAuto9CheckedRowSelection = (Test-SourceHasAuto9CheckedRowSelection)
    targetHasAuto9CheckedRowSelection = (Test-TargetHasAuto9CheckedRowSelection)
    sourceHasAuto9VisualEsSelection = (Test-SourceHasAuto9VisualEsSelection)
    targetHasAuto9VisualEsSelection = (Test-TargetHasAuto9VisualEsSelection)
    sourceHasAuto9DataSymbolPriority = (Test-SourceHasAuto9DataSymbolPriority)
    targetHasAuto9DataSymbolPriority = (Test-TargetHasAuto9DataSymbolPriority)
  }
}

function Resolve-Backup {
  if (-not $BackupRoot -or -not (Test-Path -LiteralPath $BackupRoot)) { return $null }
  if ($BackupId) {
    $candidate = Join-Path $BackupRoot $BackupId
    if ((Test-Path -LiteralPath $candidate) -and ((Split-Path $candidate -Leaf) -like 'sqx144_mt5_auto2_button_*')) {
      return Get-Item -LiteralPath $candidate
    }
    return $null
  }
  return Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'sqx144_mt5_auto2_button_*' } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
}

function Rollback-Overlay {
  if (-not $ResolvedSqxRoot) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('sqx_root_not_configured')
  }
  $processes = Get-SqxProcesses
  if ($processes.Count -gt 0) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('sqx_process_running')
  }
  $baseline = Resolve-Backup
  if (-not $baseline) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('overlay_backup_missing')
  }
  if (-not $Apply) {
    return New-Result -Ok $true -Status 'ready_to_rollback' -Extra @{ backupRef = $baseline.Name }
  }
  Copy-Item -LiteralPath (Join-Path $baseline.FullName 'SQMANAGER_index.html') -Destination $IndexPath -Force
  $backupCss = Join-Path $baseline.FullName $CssName
  $backupJs = Join-Path $baseline.FullName $JsName
  if (Test-Path -LiteralPath $backupCss) {
    Copy-Item -LiteralPath $backupCss -Destination $CssTarget -Force
  } elseif (Test-Path -LiteralPath $CssTarget) {
    Remove-Item -LiteralPath $CssTarget -Force
  }
  if (Test-Path -LiteralPath $backupJs) {
    Copy-Item -LiteralPath $backupJs -Destination $JsTarget -Force
  } elseif (Test-Path -LiteralPath $JsTarget) {
    Remove-Item -LiteralPath $JsTarget -Force
  }
  return New-Result -Ok $true -Status 'rolled_back' -Extra @{
    backupRef = $baseline.Name
    writesSqxHost = $true
    writesSqxOverlayHost = $true
  }
}

if ($Action -eq 'status') {
  $state = Get-InstalledState
  $processes = Get-SqxProcesses
  $warnings = @()
  if ($processes.Count -gt 0) { $warnings += 'sqx_process_running' }
  if (-not $ResolvedSqxRoot) { $warnings += 'sqx_root_not_configured' }
  if ($ResolvedSqxRoot -and -not (Test-SqxRootProfile)) { $warnings += 'sqx144_full_root_mismatch' }
  $isInstalled = $state.includesPresent
  New-Result -Ok $true -Status 'status' -Warnings $warnings -Extra @{
    installStatusMarker = (Get-InstallStatusMarker -Installed $isInstalled)
    installed = $isInstalled
    dataManagerButtonInstalled = $isInstalled
    assetsPresent = ($state.targetJsExists -and $state.targetCssExists)
    sourcesPresent = ($state.sourceJsExists -and $state.sourceCssExists)
    includeCount = $state.includeCount
    processCount = $processes.Count
    hostRootAccepted = (Test-SqxRootProfile)
    expectedRootName = $ExpectedRootName
    sourceHasAuto4 = (Test-SourceHasAuto4)
    targetHasAuto4 = (Test-TargetHasAuto4)
    sourceHasAuto6 = (Test-SourceHasAuto6)
    targetHasAuto6 = (Test-TargetHasAuto6)
    sourceHasSelectionGuard = (Test-SourceHasSelectionGuard)
    targetHasSelectionGuard = (Test-TargetHasSelectionGuard)
    sourceHasAuto7 = (Test-SourceHasAuto7)
    targetHasAuto7 = (Test-TargetHasAuto7)
    sourceHasAuto7DataSymbolGuard = (Test-SourceHasAuto7DataSymbolGuard)
    targetHasAuto7DataSymbolGuard = (Test-TargetHasAuto7DataSymbolGuard)
    sourceHasAuto8NativeSave = (Test-SourceHasAuto8NativeSave)
    targetHasAuto8NativeSave = (Test-TargetHasAuto8NativeSave)
    sourceHasAuto8UxStatus = (Test-SourceHasAuto8UxStatus)
    targetHasAuto8UxStatus = (Test-TargetHasAuto8UxStatus)
    sourceHasAuto9HealthWatchdog = (Test-SourceHasAuto9Health)
    targetHasAuto9HealthWatchdog = (Test-TargetHasAuto9Health)
    sourceHasAuto9SingleClickUx = (Test-SourceHasAuto9SingleClickUx)
    targetHasAuto9SingleClickUx = (Test-TargetHasAuto9SingleClickUx)
    sourceHasAuto9CheckedRowSelection = (Test-SourceHasAuto9CheckedRowSelection)
    targetHasAuto9CheckedRowSelection = (Test-TargetHasAuto9CheckedRowSelection)
    sourceHasAuto9VisualEsSelection = (Test-SourceHasAuto9VisualEsSelection)
    targetHasAuto9VisualEsSelection = (Test-TargetHasAuto9VisualEsSelection)
    sourceHasAuto9DataSymbolPriority = (Test-SourceHasAuto9DataSymbolPriority)
    targetHasAuto9DataSymbolPriority = (Test-TargetHasAuto9DataSymbolPriority)
  } | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'plan') {
  $readiness = Test-InstallReadiness
  $isInstalled = $readiness.state.includesPresent
  New-Result -Ok ($readiness.blockers.Count -eq 0) -Status 'install_plan' -Blockers $readiness.blockers -Extra @{
    installStatusMarker = (Get-InstallStatusMarker -Installed $isInstalled)
    installed = $isInstalled
    dataManagerButtonInstalled = $isInstalled
    processCount = $readiness.processCount
    requiresApply = $true
    approvalTemplate = (Get-RequiredApprovalPhrase)
    legacyApprovalTemplate = $LegacyApprovalPhrase
    sourceHasAuto4 = (Test-SourceHasAuto4)
    targetHasAuto4 = (Test-TargetHasAuto4)
    sourceHasAuto6 = (Test-SourceHasAuto6)
    targetHasAuto6 = (Test-TargetHasAuto6)
    sourceHasSelectionGuard = (Test-SourceHasSelectionGuard)
    targetHasSelectionGuard = (Test-TargetHasSelectionGuard)
    sourceHasAuto7 = (Test-SourceHasAuto7)
    targetHasAuto7 = (Test-TargetHasAuto7)
    sourceHasAuto7DataSymbolGuard = (Test-SourceHasAuto7DataSymbolGuard)
    targetHasAuto7DataSymbolGuard = (Test-TargetHasAuto7DataSymbolGuard)
    sourceHasAuto8NativeSave = (Test-SourceHasAuto8NativeSave)
    targetHasAuto8NativeSave = (Test-TargetHasAuto8NativeSave)
    sourceHasAuto8UxStatus = (Test-SourceHasAuto8UxStatus)
    targetHasAuto8UxStatus = (Test-TargetHasAuto8UxStatus)
    sourceHasAuto9HealthWatchdog = (Test-SourceHasAuto9Health)
    targetHasAuto9HealthWatchdog = (Test-TargetHasAuto9Health)
    sourceHasAuto9SingleClickUx = (Test-SourceHasAuto9SingleClickUx)
    targetHasAuto9SingleClickUx = (Test-TargetHasAuto9SingleClickUx)
    sourceHasAuto9CheckedRowSelection = (Test-SourceHasAuto9CheckedRowSelection)
    targetHasAuto9CheckedRowSelection = (Test-TargetHasAuto9CheckedRowSelection)
    sourceHasAuto9VisualEsSelection = (Test-SourceHasAuto9VisualEsSelection)
    targetHasAuto9VisualEsSelection = (Test-TargetHasAuto9VisualEsSelection)
    sourceHasAuto9DataSymbolPriority = (Test-SourceHasAuto9DataSymbolPriority)
    targetHasAuto9DataSymbolPriority = (Test-TargetHasAuto9DataSymbolPriority)
    writesSqxHostOnApply = $true
    writesSqxOverlayHostOnApply = $true
    hostRootAccepted = (Test-SqxRootProfile)
    expectedRootName = $ExpectedRootName
  } | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'install') {
  Install-Overlay | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'rollback') {
  Rollback-Overlay | ConvertTo-Json -Depth 8
  exit 0
}
