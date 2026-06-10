param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'monitor', 'decision-template')]
  [string]$Action = 'status',

  [string]$ExperimentId = 'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080',

  [int]$ObserveSeconds = 60,

  [int]$PollSeconds = 15
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai18-capa1-monitor-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi18MonitorGate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai18_capa1_monitor_gate',
      $Action,
      '--project-root', $RepoRoot,
      '--experiment-id', $ExperimentId,
      '--remote-base-url', $RemoteBaseUrl
    )

    if ($Action -eq 'monitor') {
      $args += @(
        '--observe-seconds', ([string]$ObserveSeconds),
        '--poll-seconds', ([string]$PollSeconds),
        '--write-evidence'
      )
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai18_capa1_monitor_gate_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi18MonitorGate | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai18_version_mismatch' }
$public | ConvertTo-Json -Depth 96
