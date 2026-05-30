param(
    [ValidateSet("status", "analyze")]
    [string]$Action = "status",
    [string]$SQXRoot = "",
    [string]$ProjectKey = "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1",
    [string]$Databank = "SQX EDGE CORR1 TAGGED",
    [string]$DbPath = "",
    [double]$MaxIsCorrelation = 0.50,
    [double]$MaxOos3Correlation = 0.60,
    [double]$WarnOos3Correlation = 0.45,
    [double]$MaxCorrelationDrift = 0.25,
    [int]$MinComparablePoints = 12,
    [int]$MaxWinners = 12,
    [switch]$SkipProcessGuard
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonExe = Join-Path $RepoRoot "backend\sqx-edge-tool\venv\Scripts\python.exe"
$ToolPy = Join-Path $RepoRoot "backend\sqx-edge-tool\tools\sqx142_portfolio_corr1_registered_decision.py"
$DefaultDb = Join-Path $RepoRoot ".local\sqx142_mining_registry\sqx142_mining_registry.sqlite"

if (-not $DbPath.Trim()) {
    $DbPath = $DefaultDb
}

if (-not $SQXRoot.Trim()) {
    $SQXRoot = if ($env:SQX142_ROOT) { $env:SQX142_ROOT } else { "<LOCAL_SQX142_ROOT>" }
}

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    $PythonExe = "python"
}

function Assert-NoSqxProcess {
    param([string]$Root)
    $items = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match 'StrategyQuant|sqcli|CodeEditor|electron|javaw?|SQUANT' -and
        ((($_.CommandLine -as [string]) -match 'StrategyQuant|SQX|SQUANT') -or (($_.CommandLine -as [string]) -like ("*" + $Root + "*")))
    }
    if ($items) {
        $names = ($items | Select-Object -ExpandProperty Name -Unique) -join ","
        throw "sqx_runtime_open: $names"
    }
}

if (-not $SkipProcessGuard) {
    Assert-NoSqxProcess -Root $SQXRoot
}

$argsList = @(
    $ToolPy,
    "--action", $Action,
    "--sqx-root", $SQXRoot,
    "--project-key", $ProjectKey,
    "--databank", $Databank,
    "--db", $DbPath,
    "--max-is-correlation", $MaxIsCorrelation.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--max-oos3-correlation", $MaxOos3Correlation.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--warn-oos3-correlation", $WarnOos3Correlation.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--max-correlation-drift", $MaxCorrelationDrift.ToString([Globalization.CultureInfo]::InvariantCulture),
    "--min-comparable-points", [string]$MinComparablePoints,
    "--max-winners", [string]$MaxWinners
)

if ($SkipProcessGuard) {
    $argsList += "--skip-process-guard"
}

& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
