param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'scan', 'smoke', 'module-smoke', 'report', 'approval-template')]
  [string]$Action = 'status',

  [string]$DownloadRoot = '',
  [switch]$WriteEvidence
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-custom-results2-all-custom-results-modules-bundle-v1'
$Phase = 'SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Resolve-CoreAction {
  param([string]$RequestedAction)
  switch ($RequestedAction) {
    'smoke' { 'module-smoke' }
    default { $RequestedAction }
  }
}

function Invoke-Sqx144CustomResults2AllModulesBundle {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $coreAction = Resolve-CoreAction -RequestedAction $Action
    $args = @(
      '-m', 'core.sqx144_custom_results2_all_modules',
      $coreAction,
      '--project-root', $RepoRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($DownloadRoot)) {
      $args += @('--download-root', $DownloadRoot)
    }
    if ($WriteEvidence) {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'sqx144_custom_results2_all_modules_bundle_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-Sqx144CustomResults2AllModulesBundle | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'sqx144_custom_results2_all_modules_bundle_version_mismatch' }
if ([string]$public.phaseLabel -ne $Phase) { throw 'sqx144_custom_results2_all_modules_bundle_phase_mismatch' }
$public | ConvertTo-Json -Depth 96
