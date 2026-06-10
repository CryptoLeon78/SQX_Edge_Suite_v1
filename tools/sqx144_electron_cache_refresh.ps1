[CmdletBinding()]
param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'plan', 'refresh')]
  [string]$Action = 'status',

  [string]$SqxRoot = '',
  [string]$Approval = '',
  [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-electron-cache-refresh-v1'
$StatusMarker = 'sqx144_electron_cache_refresh_ready_move_only'
$AppliedStatusMarker = 'sqx144_electron_cache_refreshed_move_only_preserved_state'
$ExpectedHostProfile = 'sqx144_full'
$ExpectedRootName = 'SQX_144_Full'
$ApprovalPhrase = 'APRUEBO SQX144 ELECTRON CACHE REFRESH host=sqx144_full move_cache_only preserve_local_storage_indexeddb_preferences'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$CacheNames = @(
  'Cache',
  'Code Cache',
  'GPUCache',
  'DawnCache',
  'DawnGraphiteCache',
  'DawnWebGPUCache',
  'blob_storage',
  'Network',
  'Session Storage',
  'Shared Dictionary',
  'shared_proto_db',
  'VideoDecodeStats'
)

$ForbiddenStateNames = @(
  'Local Storage',
  'IndexedDB',
  'WebStorage',
  'Preferences',
  'Local State',
  'main-window-state.json',
  'DIPS',
  'SharedStorage'
)

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
$ResolvedSqxRootFull = ''
if ($ResolvedSqxRoot) {
  try {
    $ResolvedSqxRootFull = [System.IO.Path]::GetFullPath($ResolvedSqxRoot).TrimEnd('\')
  } catch {
    $ResolvedSqxRootFull = ''
  }
}
$UserDataRoot = if ($ResolvedSqxRootFull) { Join-Path $ResolvedSqxRootFull 'internal\electron\resources\userData\SQUANT' } else { '' }
$UserDataRootFull = if ($UserDataRoot) { [System.IO.Path]::GetFullPath($UserDataRoot).TrimEnd('\') } else { '' }
$BackupRoot = if ($ResolvedSqxRootFull) { Join-Path $ResolvedSqxRootFull '.local_cache_backups' } else { '' }

function ConvertTo-Result {
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
    phase = 'SQX144-CACHE1'
    action = $Action
    status = $Status
    dryRun = -not [bool]$Apply
    hostProfile = $ExpectedHostProfile
    statusMarker = $StatusMarker
    approvalTemplate = $ApprovalPhrase
    moveOnly = $true
    deletesCache = $false
    writesSqxHost = $true
    writesSqxOverlayHost = $false
    writesDataDb = $false
    writesUserProjects = $false
    mutatesDatabanks = $false
    runsSqxTasks = $false
    launchesMt5 = $false
    runsMt5Ea = $false
    usesMigrationTool = $false
    directDbWriteAllowed = $false
    directDbHistoryInsertAllowed = $false
    historyImportAllowed = $false
    preservesLocalStorage = $true
    preservesIndexedDb = $true
    preservesWebStorage = $true
    preservesPreferences = $true
    expectedRootName = $ExpectedRootName
    sqxRootLeaf = if ($ResolvedSqxRootFull) { Split-Path $ResolvedSqxRootFull -Leaf } else { '' }
    userDataLeaf = if ($UserDataRootFull) { Split-Path $UserDataRootFull -Leaf } else { '' }
    cacheCandidates = $CacheNames
    preservedState = $ForbiddenStateNames
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

function Test-SqxRootProfile {
  if (-not $ResolvedSqxRootFull) { return $false }
  $leaf = Split-Path $ResolvedSqxRootFull -Leaf
  if ($leaf -ne $ExpectedRootName) { return $false }
  if ($ResolvedSqxRootFull -match '144\.2953|SQX_144_2953|SQX144_FULL_UPDATE2') { return $false }
  return $true
}

function Test-SqxExecutable {
  if (-not $ResolvedSqxRootFull) { return $false }
  foreach ($name in @('StrategyQuantX.exe', 'StrategyQuantX_nocheck.exe')) {
    if (Test-Path -LiteralPath (Join-Path $ResolvedSqxRootFull $name)) { return $true }
  }
  return $false
}

function Get-SqxProcesses {
  if (-not $ResolvedSqxRootFull) { return @() }
  $rootNeedle = $ResolvedSqxRootFull.Replace('/', '\')
  return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $name = [string]$_.Name
    $cmd = ([string]$_.CommandLine).Replace('/', '\')
    ($name -match 'StrategyQuantX|SQUANT|electron|javaw?') -and
    ($cmd.IndexOf($rootNeedle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
  })
}

function Get-DirStats {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    return @{ exists = $false; bytes = 0; files = 0 }
  }
  $files = @(Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue)
  $bytes = 0L
  foreach ($file in $files) { $bytes += [int64]$file.Length }
  return @{ exists = $true; bytes = $bytes; files = $files.Count }
}

function Get-CacheInventory {
  $items = New-Object System.Collections.ArrayList
  foreach ($name in $CacheNames) {
    $path = Join-Path $UserDataRootFull $name
    $stats = Get-DirStats -Path $path
    [void]$items.Add([ordered]@{
      name = $name
      exists = [bool]$stats.exists
      bytes = [int64]$stats.bytes
      files = [int]$stats.files
    })
  }
  return $items
}

function Test-ChildPath {
  param(
    [string]$Parent,
    [string]$Child
  )
  $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
  $childFull = [System.IO.Path]::GetFullPath($Child)
  return $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-Readiness {
  $blockers = @()
  if (-not $ResolvedSqxRootFull) { $blockers += 'sqx_root_not_configured' }
  if ($ResolvedSqxRootFull -and -not (Test-SqxRootProfile)) { $blockers += 'sqx144_full_root_mismatch' }
  if ($ResolvedSqxRootFull -and -not (Test-Path -LiteralPath $ResolvedSqxRootFull)) { $blockers += 'sqx_root_missing' }
  if ($ResolvedSqxRootFull -and -not (Test-SqxExecutable)) { $blockers += 'sqx_executable_missing' }
  if (-not $UserDataRootFull -or -not (Test-Path -LiteralPath $UserDataRootFull)) { $blockers += 'electron_user_data_missing' }
  if ($UserDataRootFull -and $ResolvedSqxRootFull -and -not (Test-ChildPath -Parent $ResolvedSqxRootFull -Child $UserDataRootFull)) { $blockers += 'electron_user_data_outside_host_root' }
  $processes = Get-SqxProcesses
  if ($processes.Count -gt 0) { $blockers += 'sqx_process_running' }
  return @{
    blockers = $blockers
    processCount = $processes.Count
    inventory = if ($UserDataRootFull -and (Test-Path -LiteralPath $UserDataRootFull)) { Get-CacheInventory } else { @() }
  }
}

function Invoke-Refresh {
  $readiness = Test-Readiness
  if ($readiness.blockers.Count -gt 0) {
    return ConvertTo-Result -Ok $false -Status 'blocked' -Blockers $readiness.blockers -Extra @{
      processCount = $readiness.processCount
      inventory = $readiness.inventory
    }
  }
  if (-not $Apply) {
    return ConvertTo-Result -Ok $true -Status 'ready_to_refresh' -Extra @{
      requiresApply = $true
      processCount = $readiness.processCount
      inventory = $readiness.inventory
    }
  }
  if ($Approval -ne $ApprovalPhrase) {
    return ConvertTo-Result -Ok $false -Status 'blocked' -Blockers @('approval_phrase_required') -Extra @{
      requiresApply = $true
      processCount = $readiness.processCount
    }
  }

  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $backup = Join-Path $BackupRoot "electron_squant_sqx144_$stamp"
  New-Item -ItemType Directory -Force -Path $backup | Out-Null

  $moved = New-Object System.Collections.ArrayList
  foreach ($name in $CacheNames) {
    $src = Join-Path $UserDataRootFull $name
    if (-not (Test-Path -LiteralPath $src)) { continue }
    if (-not (Test-ChildPath -Parent $UserDataRootFull -Child $src)) {
      throw "Refusing to move outside Electron userData: $name"
    }
    $dest = Join-Path $backup $name
    Move-Item -LiteralPath $src -Destination $dest -Force
    [void]$moved.Add($name)
  }

  $manifest = [ordered]@{
    version = $Version
    statusMarker = $AppliedStatusMarker
    backupId = Split-Path $backup -Leaf
    createdAt = (Get-Date).ToString('o')
    moved = $moved
    preservedState = $ForbiddenStateNames
    moveOnly = $true
    deletesCache = $false
    privacy = @{ localPathsReturned = $false }
  }
  $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $backup 'cache_refresh_manifest.json') -Encoding UTF8

  return ConvertTo-Result -Ok $true -Status 'refreshed' -Extra @{
    statusMarker = $AppliedStatusMarker
    backupRef = (Split-Path $backup -Leaf)
    moved = $moved
    processCount = 0
  }
}

if ($Action -eq 'status') {
  $readiness = Test-Readiness
  $warnings = @()
  if ($readiness.processCount -gt 0) { $warnings += 'sqx_process_running' }
  ConvertTo-Result -Ok $true -Status 'status' -Warnings $warnings -Extra @{
    hostRootAccepted = (Test-SqxRootProfile)
    processCount = $readiness.processCount
    inventory = $readiness.inventory
  } | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'plan') {
  $readiness = Test-Readiness
  ConvertTo-Result -Ok ($readiness.blockers.Count -eq 0) -Status 'refresh_plan' -Blockers $readiness.blockers -Extra @{
    hostRootAccepted = (Test-SqxRootProfile)
    requiresApply = $true
    processCount = $readiness.processCount
    inventory = $readiness.inventory
  } | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'refresh') {
  Invoke-Refresh | ConvertTo-Json -Depth 8
  exit 0
}
