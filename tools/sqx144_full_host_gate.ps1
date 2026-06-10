[CmdletBinding(PositionalBinding = $true)]
param(
    [Parameter(Position = 0)]
    [ValidateSet("status", "preflight")]
    [string]$Mode = "status",

    [string]$SqxRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SqxRoot)) {
    $SqxRoot = [string]$env:SQX144_FULL_ROOT
}

if ([string]::IsNullOrWhiteSpace($SqxRoot)) {
    throw "Missing SQX 144 Full root. Pass -SqxRoot or set SQX144_FULL_ROOT."
}

function Get-ShaRef {
    param([string]$Value)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($bytes)
        -join ($hash[0..7] | ForEach-Object { $_.ToString("x2") })
    } finally {
        $sha.Dispose()
    }
}

function Test-PathBool {
    param([string]$Path)
    return [bool](Test-Path -LiteralPath $Path)
}

function Get-DirectoryCount {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return 0
    }
    return @(
        Get-ChildItem -LiteralPath $Path -Directory -Force -ErrorAction SilentlyContinue
    ).Count
}

function Get-TargetProcessSnapshot {
    param([string]$Root)
    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd("\", "/")
    $processes = @()
    try {
        $processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $name = [string]$_.Name
                $exePath = [string]$_.ExecutablePath
                $name -match "^(StrategyQuantX|StrategyQuantX_ui|sqcli)(\.exe)?$" -or
                ($exePath -and $exePath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase))
            } |
            Select-Object ProcessId, Name, ExecutablePath
    } catch {
        $processes = @()
    }

    $items = @($processes | ForEach-Object {
        [ordered]@{
            processRef = "process_$(Get-ShaRef "$($_.ProcessId)|$($_.Name)")"
            name = $_.Name
            underTargetRoot = [bool](
                $_.ExecutablePath -and
                ([string]$_.ExecutablePath).StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)
            )
        }
    })

    return [ordered]@{
        count = $items.Count
        items = $items
    }
}

$root = [System.IO.Path]::GetFullPath($SqxRoot)
$exe = Join-Path $root "StrategyQuantX.exe"
$dataDb = Join-Path $root "user\data\data.db"
$projects = Join-Path $root "user\projects"
$resultsPlugins = Join-Path $root "user\extend\ResultsPlugins"
$readinessPanel = Join-Path $resultsPlugins "SQX Edge Readiness Panel"

$processSnapshot = Get-TargetProcessSnapshot -Root $root
$requiredChecks = [ordered]@{
    rootExists = Test-PathBool $root
    executableExists = Test-PathBool $exe
    dataDbExists = Test-PathBool $dataDb
    projectsDirExists = Test-PathBool $projects
    resultsPluginsDirExists = Test-PathBool $resultsPlugins
    noRelevantProcesses = ($processSnapshot.count -eq 0)
}

$gatePassed = -not ($requiredChecks.Values -contains $false)
$decision = if ($gatePassed) {
    "sqx144_full_host_gate_passed"
} elseif (-not $requiredChecks.noRelevantProcesses) {
    "blocked_relevant_processes_running"
} else {
    "blocked_missing_required_host_shape"
}

$report = [ordered]@{
    ok = $gatePassed
    schema = "sqx-edge.sqx144-full-host-gate-v1"
    phase = "SQX144-FULL-PROMOTE1 Host Promotion Gate"
    mode = $Mode
    decision = $decision
    target = [ordered]@{
        label = "SQX_144_Full"
        pathRef = "path_$(Get-ShaRef $root)"
        hostProfile = "sqx144_full"
        version = "144"
    }
    checks = $requiredChecks
    summary = [ordered]@{
        projectDirCount = Get-DirectoryCount $projects
        resultsPluginCount = Get-DirectoryCount $resultsPlugins
        sqxEdgeReadinessPanelPresent = Test-PathBool $readinessPanel
        relevantProcessCount = $processSnapshot.count
    }
    processes = $processSnapshot
    guards = [ordered]@{
        readOnly = $true
        copyExecuted = $false
        sqxRuntimeStarted = $false
        projectRunStarted = $false
        migrationToolUsed = $false
        dataDbWriteAllowed = $false
        userProjectsWriteAllowed = $false
        engineBinaryCopyAllowed = $false
        licenseMaterialHandled = $false
        bypassAttempted = $false
    }
    rollback = [ordered]@{
        rollbackExceptionHostProfile = "sqx142"
        legacyFallbackHostProfile = "deprecated_sqx142_not_active_fallback"
        rollbackRequired = $false
        rollbackAction = "manual_exception_restore_ignored_local_config_backup_or_reselect_previous_sqx142_host"
        activeFallback = $false
    }
    privacy = [ordered]@{
        localPathsReturned = $false
        rawProjectNamesReturned = $false
        rawPluginNamesReturned = $false
        licenseMaterialReturned = $false
        tokensReturned = $false
    }
}

$report | ConvertTo-Json -Depth 8

if ($Mode -eq "preflight" -and -not $gatePassed) {
    exit 1
}

exit 0
