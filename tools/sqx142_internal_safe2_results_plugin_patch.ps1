param(
  [ValidateSet('status', 'install', 'rollback')]
  [string]$Action = 'status',
  [string]$SQXRoot = $env:SQX142_ROOT,
  [string]$BackupId = ''
)

$ErrorActionPreference = 'Stop'

$Phase = 'SQX142-INTERNAL-SAFE2'
$EvidenceName = 'sqx142_internal_safe2_results_plugin_install_20260526_213000.json'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PluginName = 'SQX Edge Readiness Panel'
$SourcePlugin = Join-Path $RepoRoot 'integrations\sqx142\results_plugins\SQX Edge Readiness Panel'
$TargetPlugin = Join-Path $SQXRoot 'user\extend\ResultsPlugins\SQX Edge Readiness Panel'
$EvidenceDir = Join-Path $RepoRoot '.local\sqx142_internal_safe'
$BackupRoot = Join-Path $EvidenceDir 'backups'
$LatestBackupFile = Join-Path $EvidenceDir 'latest_safe2_backup.txt'
$EvidencePath = Join-Path $EvidenceDir $EvidenceName

function Resolve-SafePath {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path) {
    return (Resolve-Path -LiteralPath $Path).Path
  }
  return [System.IO.Path]::GetFullPath($Path)
}

function Assert-UnderPath {
  param([string]$Child, [string]$Parent)
  $childFull = Resolve-SafePath $Child
  $parentFull = Resolve-SafePath $Parent
  if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Unsafe path outside parent: $Child"
  }
}

function Assert-NoSqxProcess {
  $processes = @(Get-Process | Where-Object { $_.ProcessName -match 'StrategyQuant|StrategyQuantX|sqx|java|javaw' } | Select-Object ProcessName, Id)
  if ($processes.Count -gt 0) {
    $summary = ($processes | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ', '
    throw "SQX/Java process detected; close SQX before this action. $summary"
  }
  return $processes
}

function Get-FileInventory {
  param([string]$Root)
  if (-not (Test-Path -LiteralPath $Root)) {
    return @()
  }
  $rootFull = (Resolve-Path -LiteralPath $Root).Path
  return @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force | Sort-Object FullName | ForEach-Object {
    [pscustomobject]@{
      rel = $_.FullName.Substring($rootFull.Length + 1).Replace('\', '/')
      bytes = $_.Length
      sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    }
  })
}

function New-PluginBackup {
  New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $backupDir = Join-Path $BackupRoot "sqx142_internal_safe2_readiness_panel_$stamp"
  $backupPlugin = Join-Path $backupDir $PluginName
  New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
  if (Test-Path -LiteralPath $TargetPlugin) {
    Copy-Item -LiteralPath $TargetPlugin -Destination $backupPlugin -Recurse -Force
  }
  Set-Content -LiteralPath $LatestBackupFile -Value $backupDir -Encoding UTF8
  return $backupDir
}

function Install-Plugin {
  Assert-NoSqxProcess | Out-Null
  if (-not (Test-Path -LiteralPath $SourcePlugin)) {
    throw "Missing source plugin: $SourcePlugin"
  }
  Assert-UnderPath -Child $TargetPlugin -Parent $SQXRoot
  Assert-UnderPath -Child $SourcePlugin -Parent $RepoRoot
  New-Item -ItemType Directory -Force -Path $TargetPlugin | Out-Null

  $before = Get-FileInventory -Root $TargetPlugin
  $source = Get-FileInventory -Root $SourcePlugin
  $backupDir = New-PluginBackup

  Copy-Item -LiteralPath (Join-Path $SourcePlugin 'index.html') -Destination (Join-Path $TargetPlugin 'index.html') -Force
  New-Item -ItemType Directory -Force -Path (Join-Path $TargetPlugin 'fixtures') | Out-Null
  Copy-Item -LiteralPath (Join-Path $SourcePlugin 'fixtures\fixtures.js') -Destination (Join-Path $TargetPlugin 'fixtures\fixtures.js') -Force

  $after = Get-FileInventory -Root $TargetPlugin
  $evidence = [pscustomobject]@{
    phase = $Phase
    status = 'installed_with_backup_hash_rollback_ready'
    date = '2026-05-26'
    pluginRef = 'SQX142_ROOT/user/extend/ResultsPlugins/SQX Edge Readiness Panel'
    sourceRef = 'integrations/sqx142/results_plugins/SQX Edge Readiness Panel'
    backupRef = $backupDir.Replace($RepoRoot, '.').Replace('\', '/')
    backupId = Split-Path -Leaf $backupDir
    processSweep = @{ sqxJavaProcessCount = 0; processes = @() }
    before = $before
    source = $source
    after = $after
    mutations = @{
      sqxStarted = $false
      filesWrittenToSqx = $true
      dataDbWritten = $false
      userProjectsWritten = $false
      databanksWritten = $false
      engineFilesWritten = $false
      licenseFilesWritten = $false
    }
    rollback = @{
      available = $true
      command = "tools\sqx142_internal_safe2_results_plugin_patch.ps1 -Action rollback -BackupId $(Split-Path -Leaf $backupDir)"
    }
  }
  New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
  $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8
  return $evidence
}

function Rollback-Plugin {
  Assert-NoSqxProcess | Out-Null
  $backupDir = $BackupId
  if ([string]::IsNullOrWhiteSpace($backupDir)) {
    if (-not (Test-Path -LiteralPath $LatestBackupFile)) {
      throw "No BackupId supplied and no latest backup marker exists."
    }
    $backupDir = (Get-Content -LiteralPath $LatestBackupFile -Raw).Trim()
  } elseif (-not [System.IO.Path]::IsPathRooted($backupDir)) {
    $backupDir = Join-Path $BackupRoot $backupDir
  }
  $backupPlugin = Join-Path $backupDir $PluginName
  if (-not (Test-Path -LiteralPath $backupPlugin)) {
    throw "Backup plugin not found: $backupPlugin"
  }
  Assert-UnderPath -Child $backupPlugin -Parent $BackupRoot
  Assert-UnderPath -Child $TargetPlugin -Parent $SQXRoot
  New-Item -ItemType Directory -Force -Path $TargetPlugin | Out-Null
  Copy-Item -LiteralPath (Join-Path $backupPlugin 'index.html') -Destination (Join-Path $TargetPlugin 'index.html') -Force
  if (Test-Path -LiteralPath (Join-Path $backupPlugin 'fixtures\fixtures.js')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $TargetPlugin 'fixtures') | Out-Null
    Copy-Item -LiteralPath (Join-Path $backupPlugin 'fixtures\fixtures.js') -Destination (Join-Path $TargetPlugin 'fixtures\fixtures.js') -Force
  }
  return [pscustomobject]@{
    phase = $Phase
    status = 'rolled_back_from_backup'
    backupRef = $backupDir.Replace($RepoRoot, '.').Replace('\', '/')
    after = Get-FileInventory -Root $TargetPlugin
  }
}

function Get-Status {
  $processes = @(Get-Process | Where-Object { $_.ProcessName -match 'StrategyQuant|StrategyQuantX|sqx|java|javaw' } | Select-Object ProcessName, Id)
  return [pscustomobject]@{
    phase = $Phase
    status = 'status'
    processCount = $processes.Count
    pluginExists = Test-Path -LiteralPath $TargetPlugin
    sourceExists = Test-Path -LiteralPath $SourcePlugin
    latestBackupRef = if (Test-Path -LiteralPath $LatestBackupFile) { (Get-Content -LiteralPath $LatestBackupFile -Raw).Trim().Replace($RepoRoot, '.').Replace('\', '/') } else { $null }
    installed = Get-FileInventory -Root $TargetPlugin
    source = Get-FileInventory -Root $SourcePlugin
  }
}

switch ($Action) {
  'install' { Install-Plugin | ConvertTo-Json -Depth 8 }
  'rollback' { Rollback-Plugin | ConvertTo-Json -Depth 8 }
  default { Get-Status | ConvertTo-Json -Depth 8 }
}
