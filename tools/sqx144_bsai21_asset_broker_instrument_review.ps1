param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'review', 'decision-template')]
  [string]$Action = 'status',

  [string]$Asset = 'AUDCAD',
  [string]$Timeframe = 'H1',
  [string]$Direction = 'L',
  [string]$ExperimentId = 'BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai21-asset-broker-instrument-review-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-BsAi21AssetBrokerInstrumentReview {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }

    $args = @(
      '-m', 'core.bsai21_asset_broker_instrument_review',
      $Action,
      '--project-root', $RepoRoot,
      '--asset', $Asset,
      '--timeframe', $Timeframe,
      '--direction', $Direction,
      '--experiment-id', $ExperimentId
    )

    if ($Action -eq 'review') {
      $args += '--write-evidence'
    }

    $raw = & $PythonExe @args
    if ($LASTEXITCODE -ne 0) { throw 'bsai21_asset_broker_instrument_review_failed' }
    $raw -join "`n"
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$public = Invoke-BsAi21AssetBrokerInstrumentReview | ConvertFrom-Json
if ([string]$public.version -ne $Version) { throw 'bsai21_version_mismatch' }
$public | ConvertTo-Json -Depth 96
