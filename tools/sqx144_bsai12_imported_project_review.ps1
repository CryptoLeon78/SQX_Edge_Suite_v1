param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'review')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',

  [string]$RemapSuffix = 'SQX144DARWINEX',

  [string]$RemoteBaseUrl = 'http://127.0.0.1:8080'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai12-imported-project-readonly-review-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi12Review {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai_imported_project_review',
      $Action,
      '--project-root', $RepoRoot,
      '--candidate-id', $CandidateId,
      '--remap-suffix', $RemapSuffix,
      '--remote-base-url', $RemoteBaseUrl
    )
    if ($Action -eq 'review') {
      $args += '--write-evidence'
    }
    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai12_imported_project_review_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi12Review | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai12_version_mismatch' }
$public | ConvertTo-Json -Depth 24
