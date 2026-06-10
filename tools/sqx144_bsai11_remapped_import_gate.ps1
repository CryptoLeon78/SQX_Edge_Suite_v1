param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'preflight', 'snapshot', 'launch', 'capture', 'import-capa1', 'import-capa2')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',

  [string]$RemapSuffix = 'SQX144DARWINEX',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080',

  [string]$Phase = 'bsai11'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai11-remapped-manual-import-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$ConfigPath = Join-Path $ToolRoot 'config.json'
$OutputRoot = Join-Path $ToolRoot 'output'
$EvidenceRoot = Join-Path $RepoRoot '.local\blocksettings_ai\import_gate'
$ScreensRoot = Join-Path $EvidenceRoot 'screenshots'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

$Capa1Name = 'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa1.cfx'
$Capa2Name = 'BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_SQX144DARWINEX_Capa2.cfx'

function Get-UtcStamp {
  return (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss')
}

function Read-Config {
  if (-not (Test-Path -LiteralPath $ConfigPath)) { throw 'sqx_edge_config_missing' }
  return Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
}

function Get-SqxProcesses {
  return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @('StrategyQuantX', 'StrategyQuantX_nocheck', 'StrategyQuantX_ui', 'CodeEditor', 'sqcli', 'SQ.Client.CLI')
  })
}

function Test-ZipHasConfigXml {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $false }
  try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
    $zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
    try {
      return [bool]($zip.Entries | Where-Object { $_.FullName -eq 'config.xml' } | Select-Object -First 1)
    } finally {
      $zip.Dispose()
    }
  } catch {
    return $false
  }
}

function Get-OutputFileSnapshot {
  param([string]$Filename)
  $path = Join-Path $OutputRoot $Filename
  if (-not (Test-Path -LiteralPath $path)) { throw "missing_output_file:$Filename" }
  $item = Get-Item -LiteralPath $path
  return @{
    filename = $Filename
    size = [int64]$item.Length
    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
    zipWithConfigXml = (Test-ZipHasConfigXml -Path $path)
  }
}

function Get-FileSnapshot {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return @{ exists = $false } }
  $item = Get-Item -LiteralPath $Path
  $sha256 = $null
  $hashStatus = 'ok'
  $hashError = $null
  try {
    $sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
  } catch {
    $hashStatus = 'unavailable_file_locked_or_unreadable'
    $hashError = $_.Exception.Message
  }
  return @{
    exists = $true
    size = [int64]$item.Length
    sha256 = $sha256
    hashStatus = $hashStatus
    hashError = $hashError
    lastWriteTimeUtc = $item.LastWriteTimeUtc.ToString('o')
  }
}

function Invoke-SqxRemoteGet {
  param(
    [string]$Endpoint,
    [hashtable]$Params = @{}
  )
  $base = $RemoteBaseUrl.TrimEnd('/')
  $queryParts = @()
  foreach ($key in $Params.Keys) {
    $encodedKey = [uri]::EscapeDataString([string]$key)
    $encodedValue = [uri]::EscapeDataString([string]$Params[$key])
    $queryParts += "$encodedKey=$encodedValue"
  }
  $query = if ($queryParts.Count -gt 0) { '?' + ($queryParts -join '&') } else { '' }
  $uri = "$base/$($Endpoint.TrimStart('/'))$query"
  return Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 60
}

function Get-DirectorySnapshot {
  param(
    [string]$Path,
    [string[]]$MatchTokens = @()
  )
  if (-not (Test-Path -LiteralPath $Path)) { return @{ exists = $false } }
  $root = (Resolve-Path -LiteralPath $Path).Path
  $files = @(Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue)
  $dirs = @(Get-ChildItem -LiteralPath $root -Recurse -Directory -ErrorAction SilentlyContinue)
  $hash = [System.Security.Cryptography.SHA256]::Create()
  $matches = @()
  $totalSize = [int64]0
  $latest = $null
  foreach ($file in ($files | Sort-Object FullName)) {
    $totalSize += [int64]$file.Length
    if ($null -eq $latest -or $file.LastWriteTimeUtc -gt $latest) { $latest = $file.LastWriteTimeUtc }
    $relative = $file.FullName.Substring($root.Length).TrimStart('\','/')
    $line = "$relative|$($file.Length)|$($file.LastWriteTimeUtc.Ticks)`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($line)
    [void]$hash.TransformBlock($bytes, 0, $bytes.Length, $bytes, 0)
    foreach ($token in $MatchTokens) {
      if ($relative -like "*$token*") {
        $matches += $relative
        break
      }
    }
  }
  [void]$hash.TransformFinalBlock([byte[]]::new(0), 0, 0)
  return @{
    exists = $true
    fileCount = $files.Count
    dirCount = $dirs.Count
    totalSize = $totalSize
    latestMtimeUtc = if ($latest) { $latest.ToString('o') } else { $null }
    digestRelSizeMtimeTicks = ([System.BitConverter]::ToString($hash.Hash) -replace '-', '')
    matchCount = $matches.Count
    matches = @($matches | Select-Object -First 20)
  }
}

function Invoke-RemappedAudit {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }
    $raw = & $PythonExe -m core.bsai_resource_compatibility audit `
      --project-root $RepoRoot `
      --candidate-id $CandidateId `
      --target-profile sqxedge_darwinex `
      --suffix $RemapSuffix
    if ($LASTEXITCODE -ne 0) { throw 'bsai11_remapped_audit_failed' }
    return ($raw -join "`n") | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

function New-BasePayload {
  param([string]$Status)
  $config = Read-Config
  return [ordered]@{
    ok = $true
    version = $Version
    action = $Action
    status = $Status
    candidateId = $CandidateId
    hostProfile = [string]$config.sqx_host_profile
    remapSuffix = $RemapSuffix
    manualImportApprovedByOperator = $true
    importAttemptAllowed = $true
    sqxLaunchAllowed = $true
    cfxImportAllowed = $true
    runsSqxTasks = $false
    startButtonAllowed = $false
    writesDataDb = $false
    mutatesDatabanks = $false
    officialBlocksettingsPromotion = $false
    migrationToolAllowed = $false
    privacy = @{
      localPathsReturned = $false
      rawXmlReturned = $false
      secretsReturned = $false
      licenseMaterialReturned = $false
    }
  }
}

function Get-Preflight {
  $config = Read-Config
  $capa1 = Join-Path $OutputRoot $Capa1Name
  $capa2 = Join-Path $OutputRoot $Capa2Name
  $audit = Invoke-RemappedAudit
  $blockers = @()
  if ([string]$config.sqx_host_profile -ne 'sqx144_full') { $blockers += 'host_profile_not_sqx144_full' }
  if (-not (Test-Path -LiteralPath (Join-Path ([string]$config.sqx_path) 'StrategyQuantX.exe'))) { $blockers += 'sqx_exe_missing' }
  if (-not (Test-ZipHasConfigXml -Path $capa1)) { $blockers += 'capa1_remapped_cfx_invalid' }
  if (-not (Test-ZipHasConfigXml -Path $capa2)) { $blockers += 'capa2_remapped_cfx_invalid' }
  if (-not [bool]$audit.ok) { $blockers += 'remapped_target_resource_audit_not_ok' }
  $payload = New-BasePayload -Status $(if ($blockers.Count -eq 0) { 'remapped_manual_import_preflight_ready' } else { 'remapped_manual_import_preflight_blocked' })
  $payload.ok = ($blockers.Count -eq 0)
  $payload.blockers = $blockers
  $payload.processCount = (Get-SqxProcesses).Count
  $payload.files = @(
    @{ capa = 1; filename = $Capa1Name; zipWithConfigXml = (Test-ZipHasConfigXml -Path $capa1) },
    @{ capa = 2; filename = $Capa2Name; zipWithConfigXml = (Test-ZipHasConfigXml -Path $capa2) }
  )
  $payload.audit = @{
    ok = [bool]$audit.ok
    status = [string]$audit.status
    targetResourceVerdict = [string]$audit.audit.targetResourceVerdict
    targetFailCount = [int]$audit.audit.targetFailCount
    targetWarnCount = [int]$audit.audit.targetWarnCount
  }
  return $payload
}

function Write-Snapshot {
  param([string]$SnapshotPhase)
  New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
  $config = Read-Config
  $payload = New-BasePayload -Status 'snapshot_recorded'
  $payload.snapshotPhase = $SnapshotPhase
  $payload.createdAt = (Get-Date).ToString('s')
  $payload.processCount = (Get-SqxProcesses).Count
  $payload.dataDb = Get-FileSnapshot -Path ([string]$config.sqx_data_db)
  $payload.projectsDir = Get-DirectorySnapshot -Path ([string]$config.sqx_projects_dir) -MatchTokens @('BSAI','AUDCAD','SQX144DARWINEX')
  $payload.databanksDir = Get-DirectorySnapshot -Path (Join-Path ([string]$config.sqx_path) 'user\databanks') -MatchTokens @('BSAI','AUDCAD')
  $payload.tasksDir = Get-DirectorySnapshot -Path (Join-Path ([string]$config.sqx_path) 'user\tasks') -MatchTokens @('BSAI','AUDCAD')
  $name = "bsai11_${SnapshotPhase}_snapshot_$(Get-UtcStamp).json"
  $target = Join-Path $EvidenceRoot $name
  $payload | ConvertTo-Json -Depth 12 | Out-File -LiteralPath $target -Encoding utf8
  $public = New-BasePayload -Status 'snapshot_recorded'
  $public.snapshotFile = $name
  $public.snapshotPhase = $SnapshotPhase
  $public.processCount = $payload.processCount
  $public.dataDbSha256 = $payload.dataDb.sha256
  $public.dataDbHashStatus = $payload.dataDb.hashStatus
  $public.projectsFileCount = $payload.projectsDir.fileCount
  $public.projectsMatchCount = $payload.projectsDir.matchCount
  return $public
}

function Start-SqxVisible {
  $config = Read-Config
  $exe = Join-Path ([string]$config.sqx_path) 'StrategyQuantX.exe'
  if (-not (Test-Path -LiteralPath $exe)) { throw 'sqx_exe_missing' }
  $existing = Get-SqxProcesses
  if ($existing.Count -eq 0) {
    Start-Process -FilePath $exe -WorkingDirectory ([string]$config.sqx_path) | Out-Null
    Start-Sleep -Seconds 8
  }
  $payload = New-BasePayload -Status 'sqx_visible_launch_requested'
  $payload.processCount = (Get-SqxProcesses).Count
  return $payload
}

function Capture-Screen {
  New-Item -ItemType Directory -Force -Path $ScreensRoot | Out-Null
  Add-Type -AssemblyName System.Windows.Forms
  Add-Type -AssemblyName System.Drawing
  $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
  $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
  $graphics = [System.Drawing.Graphics]::FromImage($bmp)
  try {
    $graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size)
    $name = "bsai11_${Phase}_$(Get-UtcStamp).png"
    $target = Join-Path $ScreensRoot $name
    $bmp.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)
  } finally {
    $graphics.Dispose()
    $bmp.Dispose()
  }
  $payload = New-BasePayload -Status 'screenshot_captured'
  $payload.screenshotFile = $name
  $payload.processCount = (Get-SqxProcesses).Count
  return $payload
}

function Invoke-ImportCapa {
  param([int]$Capa)
  $filename = if ($Capa -eq 1) { $Capa1Name } else { $Capa2Name }
  $path = Join-Path $OutputRoot $filename
  if (-not (Test-Path -LiteralPath $path)) { throw "missing_remapped_cfx:$filename" }

  $preflight = Get-Preflight
  if (-not [bool]$preflight.ok) { throw 'bsai11_preflight_not_ready' }

  $response = Invoke-SqxRemoteGet -Endpoint 'taskmanager/openProject' -Params @{
    file = $path
    loadAsIs = 'false'
  }
  $hasResourcesXml = -not [string]::IsNullOrWhiteSpace([string]$response.resourcesXML)
  $hasConfigXml = -not [string]::IsNullOrWhiteSpace([string]$response.configXML)
  $projectName = if ($response.projectName) { [string]$response.projectName } else { $null }

  $projectsAfter = Invoke-SqxRemoteGet -Endpoint 'taskmanager/listProjects'
  $projectMatches = @()
  if ($projectsAfter.projects) {
    foreach ($project in @($projectsAfter.projects)) {
      $name = [string]$project.projectName
      if ($name -like '*BSAI*' -or $name -like '*SQX144DARWINEX*' -or $name -eq $projectName) {
        $projectMatches += @{
          projectName = $name
          tasks = $project.tasks
          databanks = $project.databanks
          strategies = $project.strategies
          hasUnresolvedResources = [bool]$project.hasUnresolvedResources
        }
      }
    }
  }

  $status = if ($hasResourcesXml) {
    'blocked_resources_resolution_required_no_load_as_is'
  } elseif ($projectName) {
    'import_request_accepted_project_visible_no_tasks_started'
  } else {
    'import_request_completed_without_project_name_no_tasks_started'
  }

  $payload = New-BasePayload -Status $status
  $payload.capa = $Capa
  $payload.remoteEndpoint = 'taskmanager/openProject'
  $payload.remoteBaseUrl = 'localhost_8080'
  $payload.loadAsIsRequested = $false
  $payload.loadAsIsEscalated = $false
  $payload.projectStartRequested = $false
  $payload.hostUiImportMayWriteDataDb = $true
  $payload.hostUiImportMayWriteUserProjects = $true
  $payload.file = Get-OutputFileSnapshot -Filename $filename
  $payload.response = @{
    success = $response.success
    error = if ($response.error) { [string]$response.error } else { $null }
    projectName = $projectName
    hasResourcesXML = $hasResourcesXml
    hasConfigXML = $hasConfigXml
    resourcesXmlLength = if ($hasResourcesXml) { ([string]$response.resourcesXML).Length } else { 0 }
    configXmlLength = if ($hasConfigXml) { ([string]$response.configXML).Length } else { 0 }
  }
  $payload.projectMatchesAfter = $projectMatches
  $payload.projectMatchCountAfter = $projectMatches.Count
  $payload.rawXmlStored = $false
  $payload.localPathsReturned = $false

  New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
  $name = "bsai11_api_open_capa${Capa}_$(Get-UtcStamp).json"
  $target = Join-Path $EvidenceRoot $name
  $payload | ConvertTo-Json -Depth 12 | Out-File -LiteralPath $target -Encoding utf8

  $public = New-BasePayload -Status $status
  $public.capa = $Capa
  $public.remoteEndpoint = 'taskmanager/openProject'
  $public.remoteBaseUrl = 'localhost_8080'
  $public.loadAsIsRequested = $false
  $public.loadAsIsEscalated = $false
  $public.projectStartRequested = $false
  $public.hostUiImportMayWriteDataDb = $true
  $public.hostUiImportMayWriteUserProjects = $true
  $public.file = Get-OutputFileSnapshot -Filename $filename
  $public.evidenceFile = $name
  $public.projectName = $projectName
  $public.hasResourcesXML = $hasResourcesXml
  $public.hasConfigXML = $hasConfigXml
  $public.projectMatchCountAfter = $projectMatches.Count
  $public.rawXmlStored = $false
  $public.localPathsReturned = $false
  return $public
}

if ($Action -eq 'status' -or $Action -eq 'preflight') {
  Get-Preflight | ConvertTo-Json -Depth 14
  exit 0
}

if ($Action -eq 'snapshot') {
  Write-Snapshot -SnapshotPhase $Phase | ConvertTo-Json -Depth 14
  exit 0
}

if ($Action -eq 'launch') {
  Start-SqxVisible | ConvertTo-Json -Depth 14
  exit 0
}

if ($Action -eq 'capture') {
  Capture-Screen | ConvertTo-Json -Depth 14
  exit 0
}

if ($Action -eq 'import-capa1') {
  Invoke-ImportCapa -Capa 1 | ConvertTo-Json -Depth 14
  exit 0
}

if ($Action -eq 'import-capa2') {
  Invoke-ImportCapa -Capa 2 | ConvertTo-Json -Depth 14
  exit 0
}
