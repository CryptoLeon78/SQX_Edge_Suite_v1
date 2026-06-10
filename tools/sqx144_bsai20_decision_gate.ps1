param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'decide', 'decision-template')]
  [string]$Action = 'status',

  [string]$ExperimentId = 'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai20-decision-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi20DecisionGate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai20_decision_gate',
      $Action,
      '--project-root', $RepoRoot,
      '--experiment-id', $ExperimentId
    )

    if ($Action -eq 'decide') {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai20_decision_gate_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi20DecisionGate | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai20_version_mismatch' }
$public | ConvertTo-Json -Depth 96
