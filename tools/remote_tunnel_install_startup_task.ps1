[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot = "",
    [string]$TaskName = "SQX Edge Cloudflare Tunnel",
    [switch]$AtStartup
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$tunnelRun = Join-Path $repo "tools\remote_tunnel_run.ps1"

if (-not (Test-Path -LiteralPath $tunnelRun)) {
    throw "Cannot find tunnel runner at $tunnelRun"
}

$trigger = if ($AtStartup) {
    New-ScheduledTaskTrigger -AtStartup
} else {
    New-ScheduledTaskTrigger -AtLogOn
}

$argument = "-NoProfile -ExecutionPolicy Bypass -File `"$tunnelRun`" -RepoRoot `"$repo`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argument
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

if ($PSCmdlet.ShouldProcess($TaskName, "Register REMOTE-2 Cloudflare Tunnel scheduled task")) {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "SQX Edge REMOTE-2 Cloudflare Tunnel runner. Requires private Access/Tunnel evidence and local cloudflared config." `
        -Force | Out-Null

    Write-Host "Registered scheduled task: $TaskName"
    Write-Host "  Trigger: $(if ($AtStartup) { 'AtStartup' } else { 'AtLogOn' })"
    Write-Host "  Command: powershell.exe $argument"
}
