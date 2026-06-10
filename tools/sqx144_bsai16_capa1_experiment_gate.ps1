param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'plan', 'prepare')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',

  [string]$RemapSuffix = 'SQX144DARWINEX',

  [double]$RetentionRatio = 0.65,

  [int]$AbsoluteFloor = 120
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai16-capa1-experiment-prereg-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi16Capa1ExperimentGate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai16_capa1_experiment_gate',
      $Action,
      '--project-root', $RepoRoot,
      '--candidate-id', $CandidateId,
      '--remap-suffix', $RemapSuffix,
      '--retention-ratio', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}', $RetentionRatio)),
      '--absolute-floor', ([string]$AbsoluteFloor)
    )

    if ($Action -eq 'prepare') {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai16_capa1_experiment_gate_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi16Capa1ExperimentGate | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai16_version_mismatch' }
$public | ConvertTo-Json -Depth 96
