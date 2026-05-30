param(
    [ValidateSet("status", "init", "ingest", "export-json", "funnel-json", "scan-project")]
    [string]$Action = "status",
    [string]$DbPath = "",
    [string]$RunKey = "",
    [string]$ProjectKey = "",
    [string]$SourceCsv = "",
    [string]$TaggerCsv = "",
    [string]$ProjectDir = "",
    [int]$MaxSqxParse = 300,
    [string]$SourceType = "fresh_mining_test",
    [string]$ProjectName = "",
    [string]$SqxProjectName = "",
    [string]$Asset = "",
    [string]$Symbol = "",
    [string]$Timeframe = "",
    [string]$Layer = "unknown",
    [string]$BlocksettingFamily = "unknown",
    [string]$Direction = "unknown",
    [string]$Databank = "Forward",
    [string]$SqxProfile = "SQX Edge / Darwinex",
    [Nullable[double]]$SpreadBase = $null,
    [Nullable[double]]$Mc2SpreadMin = $null,
    [Nullable[double]]$Mc2SpreadMax = $null,
    [string]$OperatorNote = "",
    [string[]]$Event = @(),
    [switch]$SqxCleanLoad,
    [switch]$SqxNoRed,
    [switch]$ConfigCorruptionRecovered,
    [switch]$FreshMiningRun,
    [switch]$CustomAnalysisEnabled,
    [switch]$FilterByResultsDisabled,
    [switch]$ColumnsPopulated
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonExe = Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"
$RegistryPy = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_mining_registry.py"
$DefaultDb = Join-Path $RepoRoot ".local\sqx142_mining_registry\sqx142_mining_registry.sqlite"

if (-not $DbPath.Trim()) {
    $DbPath = $DefaultDb
}

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    $PythonExe = "python"
}

$argsList = @(
    $RegistryPy,
    "--action", $Action,
    "--db", $DbPath,
    "--source-type", $SourceType,
    "--layer", $Layer,
    "--blocksetting-family", $BlocksettingFamily,
    "--direction", $Direction,
    "--databank", $Databank,
    "--sqx-profile", $SqxProfile
)

if ($RunKey.Trim()) { $argsList += @("--run-key", $RunKey) }
if ($ProjectKey.Trim()) { $argsList += @("--project-key", $ProjectKey) }
if ($SourceCsv.Trim()) { $argsList += @("--source-csv", $SourceCsv) }
if ($TaggerCsv.Trim()) { $argsList += @("--tagger-csv", $TaggerCsv) }
if ($ProjectDir.Trim()) { $argsList += @("--project-dir", $ProjectDir) }
if ($MaxSqxParse -ge 0) { $argsList += @("--max-sqx-parse", [string]$MaxSqxParse) }
if ($ProjectName.Trim()) { $argsList += @("--project-name", $ProjectName) }
if ($SqxProjectName.Trim()) { $argsList += @("--sqx-project-name", $SqxProjectName) }
if ($Asset.Trim()) { $argsList += @("--asset", $Asset) }
if ($Symbol.Trim()) { $argsList += @("--symbol", $Symbol) }
if ($Timeframe.Trim()) { $argsList += @("--timeframe", $Timeframe) }
if ($OperatorNote.Trim()) { $argsList += @("--operator-note", $OperatorNote) }
if ($null -ne $SpreadBase) { $argsList += @("--spread-base", $SpreadBase.ToString([Globalization.CultureInfo]::InvariantCulture)) }
if ($null -ne $Mc2SpreadMin) { $argsList += @("--mc2-spread-min", $Mc2SpreadMin.ToString([Globalization.CultureInfo]::InvariantCulture)) }
if ($null -ne $Mc2SpreadMax) { $argsList += @("--mc2-spread-max", $Mc2SpreadMax.ToString([Globalization.CultureInfo]::InvariantCulture)) }
foreach ($item in $Event) {
    if ($item.Trim()) { $argsList += @("--event", $item) }
}
if ($SqxCleanLoad) { $argsList += "--sqx-clean-load" }
if ($SqxNoRed) { $argsList += "--sqx-no-red" }
if ($ConfigCorruptionRecovered) { $argsList += "--config-corruption-recovered" }
if ($FreshMiningRun) { $argsList += "--fresh-mining-run" }
if ($CustomAnalysisEnabled) { $argsList += "--custom-analysis-enabled" }
if ($FilterByResultsDisabled) { $argsList += "--filter-by-results-disabled" }
if ($ColumnsPopulated) { $argsList += "--columns-populated" }

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
