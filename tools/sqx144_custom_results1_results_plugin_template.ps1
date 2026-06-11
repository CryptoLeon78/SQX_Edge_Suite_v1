param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'scan', 'scan-downloads', 'smoke', 'template-smoke', 'report', 'decision-template')]
  [string]$Action = 'status',

  [string]$DownloadRoot = '',
  [switch]$WriteEvidence
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-custom-results1-results-plugin-template-v1'
$Phase = 'SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Resolve-CoreAction {
  param([string]$RequestedAction)
  switch ($RequestedAction) {
    'scan' { 'scan-downloads' }
    'smoke' { 'template-smoke' }
    default { $RequestedAction }
  }
}

function Invoke-Sqx144CustomResults1ResultsPluginTemplate {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $coreAction = Resolve-CoreAction -RequestedAction $Action
    $args = @(
      '-m', 'core.sqx144_custom_results1_study',
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
    if ($LASTEXITCODE -ne 0) { throw 'sqx144_custom_results1_results_plugin_template_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-Sqx144CustomResults1ResultsPluginTemplate | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'sqx144_custom_results1_results_plugin_template_version_mismatch' }
if ([string]$public.phaseLabel -ne $Phase) { throw 'sqx144_custom_results1_results_plugin_template_phase_mismatch' }
$public | ConvertTo-Json -Depth 96
