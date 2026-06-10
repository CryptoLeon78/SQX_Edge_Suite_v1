param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'audit', 'remap')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005',

  [string]$TargetProfile = 'sqxedge_darwinex',

  [string]$RemapSuffix = 'SQX144DARWINEX'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai10-target-resource-compatibility-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ToolRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool'
$PythonExe = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

$writesSqxHost = $false
$writesDataDb = $false
$writesUserProjects = $false
$mutatesDatabanks = $false
$runsSqxTasks = $false
$localPathsReturned = $false
$readOnlyDataDb = $true
$noAutoImport = $true

function Get-SqxProcesses {
  return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @('StrategyQuantX', 'StrategyQuantX_nocheck', 'StrategyQuantX_ui', 'CodeEditor', 'sqcli', 'SQ.Client.CLI')
  })
}

function Invoke-BsAi10Python {
  $oldPythonPath = $env:PYTHONPATH
  try {
    if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
      $env:PYTHONPATH = $ToolRoot
    } else {
      $env:PYTHONPATH = "$ToolRoot;$oldPythonPath"
    }
    $argsList = @(
      '-m', 'core.bsai_resource_compatibility',
      $Action,
      '--project-root', $RepoRoot,
      '--candidate-id', $CandidateId,
      '--target-profile', $TargetProfile,
      '--remap-suffix', $RemapSuffix
    )
    $raw = & $PythonExe @argsList
    if ($LASTEXITCODE -ne 0) {
      throw "bs_ai10_python_failed"
    }
    return ($raw -join "`n") | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $oldPythonPath
  }
}

$payload = Invoke-BsAi10Python
$processCount = (Get-SqxProcesses).Count

$payload | Add-Member -NotePropertyName wrapperVersion -NotePropertyValue $Version -Force
$payload | Add-Member -NotePropertyName processCount -NotePropertyValue $processCount -Force
$payload | Add-Member -NotePropertyName writesSqxHost -NotePropertyValue $writesSqxHost -Force
$payload | Add-Member -NotePropertyName writesDataDb -NotePropertyValue $writesDataDb -Force
$payload | Add-Member -NotePropertyName writesUserProjects -NotePropertyValue $writesUserProjects -Force
$payload | Add-Member -NotePropertyName mutatesDatabanks -NotePropertyValue $mutatesDatabanks -Force
$payload | Add-Member -NotePropertyName runsSqxTasks -NotePropertyValue $runsSqxTasks -Force
$payload | Add-Member -NotePropertyName readOnlyDataDb -NotePropertyValue $readOnlyDataDb -Force
$payload | Add-Member -NotePropertyName noAutoImport -NotePropertyValue $noAutoImport -Force

if (-not $payload.privacy) {
  $payload | Add-Member -NotePropertyName privacy -NotePropertyValue ([ordered]@{}) -Force
}
$payload.privacy | Add-Member -NotePropertyName localPathsReturned -NotePropertyValue $localPathsReturned -Force

$payload | ConvertTo-Json -Depth 24
