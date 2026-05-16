[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot = "",
    [string]$TaskName = "SQX Edge Remote Service Watchdog",
    [switch]$AtStartup
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$watchdog = Join-Path $repo "tools\remote_service_watchdog.ps1"

if (-not (Test-Path -LiteralPath $watchdog)) {
    throw "Cannot find watchdog script at $watchdog"
}

$trigger = if ($AtStartup) {
    New-ScheduledTaskTrigger -AtStartup
} else {
    New-ScheduledTaskTrigger -AtLogOn
}

$argument = "-NoProfile -ExecutionPolicy Bypass -File `"$watchdog`" -RepoRoot `"$repo`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argument
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

if ($PSCmdlet.ShouldProcess($TaskName, "Register REMOTE-1 watchdog scheduled task")) {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "SQX Edge REMOTE-1 localhost watchdog. Keeps backend ready for Cloudflare Tunnel phases without opening public ports." `
        -Force | Out-Null

    Write-Host "Registered scheduled task: $TaskName"
    Write-Host "  Trigger: $(if ($AtStartup) { 'AtStartup' } else { 'AtLogOn' })"
    Write-Host "  Command: powershell.exe $argument"
}
