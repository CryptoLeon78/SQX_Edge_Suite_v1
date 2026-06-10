param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("approve-context", "revoke-context", "block-identity")]
    [string]$Action,

    [Parameter(Mandatory = $true)]
    [string]$Identity,

    [string]$Context = "",
    [string]$Note = "",
    [string]$Store = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$tool = Join-Path $repo "backend\sqx-edge-tool\tools\remote_access_control_admin.py"
if (-not (Test-Path -LiteralPath $tool)) {
    throw "Remote access-control admin tool not found."
}

$argsList = @($tool, $Action, "--identity", $Identity)
if ($Context) { $argsList += @("--context", $Context) }
if ($Note) { $argsList += @("--note", $Note) }
if ($Store) { $argsList += @("--store", $Store) }
if ($Json) { $argsList += "--json" }

python @argsList
exit $LASTEXITCODE
