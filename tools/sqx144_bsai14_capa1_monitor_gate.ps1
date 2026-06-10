param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'monitor', 'decision-template')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',

  [string]$RemapSuffix = 'SQX144DARWINEX',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai14-capa1-monitor-decision-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi14MonitorGate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai14_capa1_monitor_gate',
      $Action,
      '--project-root', $RepoRoot,
      '--candidate-id', $CandidateId,
      '--remap-suffix', $RemapSuffix,
      '--remote-base-url', $RemoteBaseUrl
    )

    if ($Action -eq 'monitor') {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai14_capa1_monitor_gate_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi14MonitorGate | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai14_version_mismatch' }
$public | ConvertTo-Json -Depth 32
