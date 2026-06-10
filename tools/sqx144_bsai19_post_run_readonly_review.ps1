param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'review', 'decision-template')]
  [string]$Action = 'status',

  [string]$ExperimentId = 'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai19-post-run-readonly-review-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi19PostRunReadonlyReview {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai19_post_run_readonly_review',
      $Action,
      '--project-root', $RepoRoot,
      '--experiment-id', $ExperimentId,
      '--remote-base-url', $RemoteBaseUrl
    )

    if ($Action -eq 'review') {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai19_post_run_readonly_review_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi19PostRunReadonlyReview | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai19_version_mismatch' }
$public | ConvertTo-Json -Depth 96
