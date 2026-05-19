param(
    [switch]$Json,
    [string]$Aliases = "",
    [string]$Entitlements = "",
    [string]$AccessControl = "",
    [string]$SupportCases = "",
    [string]$DownloadSmoke = "",
    [string]$Out = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$tool = Join-Path $repo "backend\sqx-edge-tool\tools\remote_cohort_matrix.py"
if (-not (Test-Path -LiteralPath $tool)) {
    throw "Remote cohort matrix tool not found."
}

$argsList = @($tool)
if ($Aliases) { $argsList += @("--aliases", $Aliases) }
if ($Entitlements) { $argsList += @("--entitlements", $Entitlements) }
if ($AccessControl) { $argsList += @("--access-control", $AccessControl) }
if ($SupportCases) { $argsList += @("--support-cases", $SupportCases) }
if ($DownloadSmoke) { $argsList += @("--download-smoke", $DownloadSmoke) }
if ($Out) { $argsList += @("--out", $Out) }
if ($Json) { $argsList += "--json" }

python @argsList
exit $LASTEXITCODE
