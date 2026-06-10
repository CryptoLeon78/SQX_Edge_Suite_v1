param(
    [switch]$Json,
    [string]$Store = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$tool = Join-Path $repo "backend\sqx-edge-tool\tools\remote_access_control_status.py"
if (-not (Test-Path -LiteralPath $tool)) {
    throw "Remote access-control status tool not found."
}

$argsList = @($tool)
if ($Store) { $argsList += @("--store", $Store) }
if ($Json) { $argsList += "--json" }

python @argsList
exit $LASTEXITCODE
