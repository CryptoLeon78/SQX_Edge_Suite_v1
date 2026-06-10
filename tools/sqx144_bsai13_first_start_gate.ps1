param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'preflight', 'start-capa1', 'stop-capa1')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',

  [string]$RemapSuffix = 'SQX144DARWINEX',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080',

  [int]$ObserveSeconds = 90,

  [int]$PollSeconds = 10
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai13-first-manual-start-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi13FirstStartGate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai_first_start_gate',
      $Action,
      '--project-root', $RepoRoot,
      '--candidate-id', $CandidateId,
      '--remap-suffix', $RemapSuffix,
      '--remote-base-url', $RemoteBaseUrl
    )

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
    if ($LASTEXITCODE -ne 0) { throw 'bsai13_first_start_gate_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi13FirstStartGate | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai13_version_mismatch' }
$public | ConvertTo-Json -Depth 32
