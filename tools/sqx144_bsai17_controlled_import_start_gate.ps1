param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'preflight', 'launch', 'import-capa1', 'start-capa1')]
  [string]$Action = 'status',

  [string]$ExperimentId = 'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080',

  [switch]$AcceptCrossBrokerSpreadWarningForThisTrial,

  [int]$ObserveSeconds = 90,

  [int]$PollSeconds = 10,

  [int]$RemoteWaitSeconds = 240
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai17-controlled-capa1-import-start-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$ConfigPath = Join-Path $ToolRoot 'config.json'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Read-Config {
  if (-not (Test-Path -LiteralPath $ConfigPath)) { throw 'sqx_edge_config_missing' }
  return Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
}

function Get-SqxProcesses {
  return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @('StrategyQuantX', 'StrategyQuantX_nocheck', 'StrategyQuantX_ui', 'CodeEditor', 'sqcli', 'SQ.Client.CLI')
  })
}

function Test-SqxRemoteReady {
  try {
    $base = $RemoteBaseUrl.TrimEnd('/')
    $response = Invoke-RestMethod -Uri "$base/taskmanager/listProjects" -Method Get -TimeoutSec 5
    return @{
      reachable = $true
      projectCount = if ($response.projects) { @($response.projects).Count } else { 0 }
      endpoint = 'taskmanager/listProjects'
    }
  } catch {
    return @{
      reachable = $false
      projectCount = $null
      endpoint = 'taskmanager/listProjects'
      exceptionType = $_.Exception.GetType().Name
    }
  }
}

function New-LaunchPayload {
  param(
    [string]$Status,
    [bool]$Ok,
    [array]$Blockers = @()
  )
  $config = Read-Config
  return [ordered]@{
    ok = $Ok
    version = $Version
    action = 'launch'
    status = $Status
    hostProfile = [string]$config.sqx_host_profile
    experimentId = $ExperimentId
    operatorApproval = @{
      explicitForBSAI17 = $true
      crossBrokerSpreadWarningAccepted = [bool]$AcceptCrossBrokerSpreadWarningForThisTrial
      acceptanceScope = 'this_trial_only'
      futureAssetBrokerInstrumentReviewRequired = $true
    }
    blockers = @($Blockers)
    guards = @{
      sqxLaunchAllowed = $true
      capa1ImportAllowed = $false
      projectStartAllowed = $false
      capa2StartAllowed = $false
      loadAsIsAllowed = $false
      addMissingSymbolsAllowed = $false
      directDataDbPatch = $false
      directUserProjectsPatch = $false
      directDatabankMutation = $false
      migrationToolAllowed = $false
      officialBlocksettingsPromotion = $false
      sqx144UpdatePromotion = $false
    }
    privacy = @{
      localPathsReturned = $false
      rawXmlReturned = $false
      rawLogReturned = $false
      secretsReturned = $false
      licenseMaterialReturned = $false
    }
  }
}

function Start-SqxAndWaitRemote {
  $config = Read-Config
  $blockers = @()
  if ([string]$config.sqx_host_profile -ne 'sqx144_full') { $blockers += 'host_profile_not_sqx144_full' }
  $exe = Join-Path ([string]$config.sqx_path) 'StrategyQuantX.exe'
  if (-not (Test-Path -LiteralPath $exe)) { $blockers += 'sqx_exe_missing' }
  if ($blockers.Count -gt 0) {
    $blocked = New-LaunchPayload -Status 'sqx_launch_blocked' -Ok $false -Blockers $blockers
    $blocked.processCount = (Get-SqxProcesses).Count
    $blocked.remote = Test-SqxRemoteReady
    return $blocked
  }

  $launched = $false
  if ((Get-SqxProcesses).Count -eq 0) {
    Start-Process -FilePath $exe -WorkingDirectory ([string]$config.sqx_path) | Out-Null
    $launched = $true
  }

  $remote = Test-SqxRemoteReady
  $deadline = (Get-Date).AddSeconds([Math]::Max(0, $RemoteWaitSeconds))
  while (-not [bool]$remote.reachable -and (Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 5
    $remote = Test-SqxRemoteReady
  }

  $ready = [bool]$remote.reachable
  $payload = New-LaunchPayload -Status $(if ($ready) { 'sqx_launch_remote_ready' } else { 'sqx_launch_remote_unavailable' }) -Ok $ready
  $payload.launchedNow = $launched
  $payload.processCount = (Get-SqxProcesses).Count
  $payload.remote = $remote
  $payload.remoteWaitSeconds = $RemoteWaitSeconds
  return $payload
}

function Invoke-BsAi17Gate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai17_controlled_import_start_gate',
      $Action,
      '--project-root', $RepoRoot,
      '--experiment-id', $ExperimentId,
      '--remote-base-url', $RemoteBaseUrl
    )

    if ($AcceptCrossBrokerSpreadWarningForThisTrial) {
      $args += '--accept-cross-broker-spread-warning'
    }

    if ($Action -eq 'preflight') {
      $args += '--write-evidence'
    }

    if ($Action -eq 'start-capa1') {
      $args += @(
        '--observe-seconds', ([string]$ObserveSeconds),
        '--poll-seconds', ([string]$PollSeconds)
      )
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai17_controlled_import_start_gate_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

if ($Action -eq 'launch') {
  $public = Start-SqxAndWaitRemote
} else {
  $public = Invoke-BsAi17Gate | ConvertFrom-Json
  if ([string]$public.version -ne $Version) { throw 'bsai17_version_mismatch' }
}

$public | ConvertTo-Json -Depth 96
