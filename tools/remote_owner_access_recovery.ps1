param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("status", "recover", "rollback")]
    [string]$Action,

    [string]$Identity = "",
    [string]$Email = "",
    [string]$Context = "",
    [switch]$ApproveLatestPending,
    [string]$Note = "",
    [string]$BackupId = "",
    [string]$Entitlements = "",
    [string]$AccessControl = "",
    [string]$BackupDir = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$tool = Join-Path $repo "backend\sqx-edge-tool\tools\remote_owner_access_recovery.py"
if (-not (Test-Path -LiteralPath $tool)) {
    throw "Remote owner access recovery tool not found."
}

$argsList = @($tool, $Action)
if ($Identity) { $argsList += @("--identity", $Identity) }
if ($Email) { $argsList += @("--email", $Email) }
if ($Context) { $argsList += @("--context", $Context) }
if ($ApproveLatestPending) { $argsList += "--approve-latest-pending" }
if ($Note) { $argsList += @("--note", $Note) }
if ($BackupId) { $argsList += @("--backup-id", $BackupId) }
if ($Entitlements) { $argsList += @("--entitlements", $Entitlements) }
if ($AccessControl) { $argsList += @("--access-control", $AccessControl) }
if ($BackupDir) { $argsList += @("--backup-dir", $BackupDir) }
if ($Json) { $argsList += "--json" }

python @argsList
exit $LASTEXITCODE
