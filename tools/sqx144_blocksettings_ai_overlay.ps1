param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'plan', 'install', 'rollback')]
  [string]$Action = 'status',

  [string]$SqxRoot = '',
  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-blocksettings-ai-overlay-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SourceRoot = Join-Path $RepoRoot 'integrations\sqx144\blocksettings_ai_overlay'
$CssName = 'sqx-edge-bsai.css'
$JsName = 'sqx-edge-bsai.js'
$Marker = 'sqx-edge-bsai'

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
  return ''
}

$ResolvedSqxRoot = Resolve-SqxRoot
$IndexPath = if ($ResolvedSqxRoot) { Join-Path $ResolvedSqxRoot 'internal\web\AlgoWizard\index.html' } else { '' }
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
    action = $Action
    status = $Status
    dryRun = -not [bool]$Apply
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

function Get-InstalledState {
  $indexExists = if ($IndexPath) { Test-Path -LiteralPath $IndexPath } else { $false }
  $indexText = if ($indexExists) { Get-Content -LiteralPath $IndexPath -Raw } else { '' }
  return @{
    indexExists = $indexExists
    commonExists = if ($CommonRoot) { Test-Path -LiteralPath $CommonRoot } else { $false }
    sourceJsExists = Test-Path -LiteralPath (Join-Path $SourceRoot $JsName)
    sourceCssExists = Test-Path -LiteralPath (Join-Path $SourceRoot $CssName)
    targetJsExists = if ($JsTarget) { Test-Path -LiteralPath $JsTarget } else { $false }
    targetCssExists = if ($CssTarget) { Test-Path -LiteralPath $CssTarget } else { $false }
    includesPresent = $indexText.Contains($Marker)
  }
}

function New-Backup {
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $backup = Join-Path $BackupRoot "sqx144_bsai_overlay_$stamp"
  New-Item -ItemType Directory -Force -Path $backup | Out-Null
  Copy-Item -LiteralPath $IndexPath -Destination (Join-Path $backup 'AlgoWizard_index.html') -Force
  if (Test-Path -LiteralPath $CssTarget) {
    Copy-Item -LiteralPath $CssTarget -Destination (Join-Path $backup $CssName) -Force
  }
  if (Test-Path -LiteralPath $JsTarget) {
    Copy-Item -LiteralPath $JsTarget -Destination (Join-Path $backup $JsName) -Force
  }
  return $backup
}

function Test-InstallReadiness {
  $state = Get-InstalledState
  $blockers = @()
  if (-not $ResolvedSqxRoot) { $blockers += 'sqx_root_not_configured' }
  if (-not $state.indexExists) { $blockers += 'algowizard_index_missing' }
  if (-not $state.commonExists) { $blockers += 'common_root_missing' }
  if (-not $state.sourceJsExists) { $blockers += 'source_js_missing' }
  if (-not $state.sourceCssExists) { $blockers += 'source_css_missing' }
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
  if (-not $Apply) {
    return New-Result -Ok $true -Status 'ready_to_install' -Extra @{
      installed = $readiness.state.includesPresent
      processCount = $readiness.processCount
    }
  }

  $backup = New-Backup
  Copy-Item -LiteralPath (Join-Path $SourceRoot $CssName) -Destination $CssTarget -Force
  Copy-Item -LiteralPath (Join-Path $SourceRoot $JsName) -Destination $JsTarget -Force

  $html = Get-Content -LiteralPath $IndexPath -Raw
  $html = [regex]::Replace($html, '(?im)^[^\r\n]*(sqx-edge-bsai\.css|sqx-edge-bsai\.js)(\?v=[^"`'']+)?[^\r\n]*(\r?\n)?', '')
  $include = @(
    "    <link rel=`"stylesheet`" href=`"../common/${CssName}?v=${Version}`">",
    "    <script defer src=`"../common/${JsName}?v=${Version}`"></script>"
  ) -join "`r`n"
  $headMatch = [regex]::Match($html, '</head>', 'IgnoreCase')
  if (-not $headMatch.Success) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('algowizard_head_tag_missing')
  }
  $html = $html.Insert($headMatch.Index, "$include`r`n")
  Set-Content -LiteralPath $IndexPath -Value $html -Encoding UTF8
  return New-Result -Ok $true -Status 'installed' -Extra @{
    backupRef = (Split-Path $backup -Leaf)
    installed = $true
  }
}

function Rollback-Overlay {
  if (-not $ResolvedSqxRoot) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('sqx_root_not_configured')
  }
  $processes = Get-SqxProcesses
  if ($processes.Count -gt 0) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('sqx_process_running')
  }
  $baseline = Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'sqx144_bsai_overlay_*' } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if (-not $baseline) {
    return New-Result -Ok $false -Status 'blocked' -Blockers @('overlay_backup_missing')
  }
  if (-not $Apply) {
    return New-Result -Ok $true -Status 'ready_to_rollback' -Extra @{ backupRef = $baseline.Name }
  }
  Copy-Item -LiteralPath (Join-Path $baseline.FullName 'AlgoWizard_index.html') -Destination $IndexPath -Force
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
  return New-Result -Ok $true -Status 'rolled_back' -Extra @{ backupRef = $baseline.Name }
}

if ($Action -eq 'status') {
  $state = Get-InstalledState
  $processes = Get-SqxProcesses
  $warnings = @()
  if ($processes.Count -gt 0) { $warnings += 'sqx_process_running' }
  if (-not $ResolvedSqxRoot) { $warnings += 'sqx_root_not_configured' }
  New-Result -Ok $true -Status 'status' -Warnings $warnings -Extra @{
    installed = $state.includesPresent
    assetsPresent = ($state.targetJsExists -and $state.targetCssExists)
    sourcesPresent = ($state.sourceJsExists -and $state.sourceCssExists)
    processCount = $processes.Count
  } | ConvertTo-Json -Depth 6
  exit 0
}

if ($Action -eq 'plan') {
  $readiness = Test-InstallReadiness
  New-Result -Ok ($readiness.blockers.Count -eq 0) -Status 'install_plan' -Blockers $readiness.blockers -Extra @{
    installed = $readiness.state.includesPresent
    processCount = $readiness.processCount
    requiresApply = $true
    writesSqxHost = $true
    writesDataDb = $false
    writesUserProjects = $false
    runsSqxTasks = $false
  } | ConvertTo-Json -Depth 6
  exit 0
}

if ($Action -eq 'install') {
  Install-Overlay | ConvertTo-Json -Depth 6
  exit 0
}

if ($Action -eq 'rollback') {
  Rollback-Overlay | ConvertTo-Json -Depth 6
  exit 0
}
