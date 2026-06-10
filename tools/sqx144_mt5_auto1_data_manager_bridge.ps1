param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('status', 'request-template', 'write-request', 'install-source', 'validate-response')]
    [string]$Action,

    [string]$Symbol = 'USDJPY_Darwinex',
    [string]$RequestId = '',
    [string]$SpreadTimeframe = 'M1',
    [int]$FromYear = 0,
    [int]$ToYear = 0,
    [int]$MaxBars = 0,
    [ValidateSet('p50', 'p75', 'p90', 'p95', 'p99', 'mean')]
    [string]$SpreadPolicy = 'p90',
    [string]$Mt5FilesDir = '',
    [string]$Mt5ExpertsDir = '',
    [string]$ResponsePath = '',
    [switch]$Apply,
    [switch]$Overwrite
)

$ErrorActionPreference = 'Stop'

$Version = 'sqx144-mt5-auto1-data-manager-bridge-v1'
$Phase = 'SQX144-MT5-AUTO1'
$HostProfile = 'sqx144_full'
$writesSqxHost = $false
$writesDataDb = $false
$writesUserProjects = $false
$mutatesDatabanks = $false
$runsSqxTasks = $false
$launchesMt5 = $false
$runsMt5Ea = $false
$usesMigrationTool = $false
$dataManagerButtonInstalled = $false
$defaultSpreadPolicy = 'p90'

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptRoot '..')
$BackendRoot = Join-Path $ProjectRoot 'backend\sqx-edge-tool'
$env:PYTHONPATH = $BackendRoot

$argsList = @(
    '-m', 'core.sqx144_mt5_bridge',
    $Action,
    '--project-root', $ProjectRoot,
    '--symbol', $Symbol,
    '--spread-timeframe', $SpreadTimeframe,
    '--from-year', $FromYear,
    '--to-year', $ToYear,
    '--max-bars', $MaxBars,
    '--spread-policy', $SpreadPolicy
)

if ($RequestId -ne '') {
    $argsList += @('--request-id', $RequestId)
}
if ($Mt5FilesDir -ne '') {
    $argsList += @('--mt5-files-dir', $Mt5FilesDir)
}
if ($Mt5ExpertsDir -ne '') {
    $argsList += @('--mt5-experts-dir', $Mt5ExpertsDir)
}
if ($ResponsePath -ne '') {
    $argsList += @('--response-path', $ResponsePath)
}
if ($Apply) {
    $argsList += '--apply'
}
if ($Overwrite) {
    $argsList += '--overwrite'
}

python @argsList
