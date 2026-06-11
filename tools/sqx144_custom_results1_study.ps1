param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'scan-downloads', 'template-smoke', 'report', 'decision-template')]
  [string]$Action = 'status',

  [string]$DownloadRoot = '',
  [switch]$WriteEvidence
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-custom-results1-results-plugin-template-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-Sqx144CustomResults1Study {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.sqx144_custom_results1_study',
      $Action,
      '--project-root', $RepoRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($DownloadRoot)) {
      $args += @('--download-root', $DownloadRoot)
    }
    if ($WriteEvidence) {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'sqx144_custom_results1_study_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-Sqx144CustomResults1Study | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'sqx144_custom_results1_version_mismatch' }
$public | ConvertTo-Json -Depth 96
