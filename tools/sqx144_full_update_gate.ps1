[CmdletBinding(PositionalBinding = $true)]
param(
    [Parameter(Position = 0)]
    [ValidateSet("status", "preflight")]
    [string]$Mode = "status",

    [string]$SqxRoot = "",

    [string]$ExpectedBuild = "144.2953",

    [int]$MinProjectDirs = 29,

    [int]$MinResultsPlugins = 5
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SqxRoot)) {
    $SqxRoot = [string]$env:SQX144_UPDATE_ROOT
}

if ([string]::IsNullOrWhiteSpace($SqxRoot)) {
    throw "Missing SQX 144 update root. Pass -SqxRoot or set SQX144_UPDATE_ROOT."
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

function Read-SharedText {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return ""
    }
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite
    )
    try {
        $reader = New-Object System.IO.StreamReader($stream)
        try {
            return $reader.ReadToEnd()
        } finally {
            $reader.Dispose()
        }
    } finally {
        $stream.Dispose()
    }
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
                $name -match "^(StrategyQuantX|StrategyQuantX_ui|SQ_Installer|sqcli)(\.exe)?$" -or
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
$logDir = Join-Path $root "user\log\StrategyQuant"
$latestLog = $null
if (Test-Path -LiteralPath $logDir -PathType Container) {
    $latestLog = Get-ChildItem -LiteralPath $logDir -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}
$logText = if ($latestLog) { Read-SharedText $latestLog.FullName } else { "" }

$processSnapshot = Get-TargetProcessSnapshot -Root $root
$projectDirCount = Get-DirectoryCount $projects
$resultsPluginCount = Get-DirectoryCount $resultsPlugins
$panelPresent = Test-PathBool $readinessPanel
$versionSeen = $logText -match ("SQX version:\s*" + [regex]::Escape($ExpectedBuild))
$licenseDialogSeen = $logText -match "License dialog|Showing license form|licenseDialog\.html"
$snippetCompileDoneSeen = $logText -match "Compiling Snippets done"
$snippetCompileFailureSeen = $logText -match "Compilation FAILED"

$requiredChecks = [ordered]@{
    rootExists = Test-PathBool $root
    executableExists = Test-PathBool $exe
    dataDbExists = Test-PathBool $dataDb
    projectsDirExists = Test-PathBool $projects
    resultsPluginsDirExists = Test-PathBool $resultsPlugins
    noRelevantProcesses = ($processSnapshot.count -eq 0)
    expectedBuildSeenInLog = $versionSeen
    licenseWorkspaceGateClear = (-not $licenseDialogSeen)
    migratedProjectShapePresent = ($projectDirCount -ge $MinProjectDirs)
    migratedResultsPluginShapePresent = ($resultsPluginCount -ge $MinResultsPlugins)
    sqxEdgeReadinessPanelPresent = $panelPresent
    noSnippetCompileFailureSeen = (-not $snippetCompileFailureSeen)
}

$blockers = @()
if (-not $requiredChecks.rootExists -or -not $requiredChecks.executableExists -or -not $requiredChecks.dataDbExists -or -not $requiredChecks.projectsDirExists -or -not $requiredChecks.resultsPluginsDirExists) {
    $blockers += "missing_required_host_shape"
}
if (-not $requiredChecks.noRelevantProcesses) {
    $blockers += "relevant_processes_running"
}
if (-not $requiredChecks.expectedBuildSeenInLog) {
    $blockers += "expected_build_not_confirmed"
}
if (-not $requiredChecks.licenseWorkspaceGateClear) {
    $blockers += "license_activation_pending"
}
if (-not $requiredChecks.migratedProjectShapePresent -or -not $requiredChecks.migratedResultsPluginShapePresent -or -not $requiredChecks.sqxEdgeReadinessPanelPresent) {
    $blockers += "migration_alignment_pending"
}
if (-not $requiredChecks.noSnippetCompileFailureSeen) {
    $blockers += "snippet_compile_failure_seen"
}

$promotionReady = ($blockers.Count -eq 0)
if ($promotionReady) {
    $decision = "sqx144_full_update1_ready_for_promotion"
} elseif (($blockers -contains "license_activation_pending") -and ($blockers -contains "migration_alignment_pending")) {
    $decision = "blocked_license_activation_pending_and_migration_alignment"
} elseif ($blockers -contains "license_activation_pending") {
    $decision = "blocked_license_activation_pending"
} elseif ($blockers -contains "migration_alignment_pending") {
    $decision = "blocked_migration_alignment_pending"
} elseif ($blockers -contains "expected_build_not_confirmed") {
    $decision = "blocked_expected_build_not_confirmed"
} elseif ($blockers -contains "relevant_processes_running") {
    $decision = "blocked_relevant_processes_running"
} else {
    $decision = "blocked_update_gate_not_ready"
}

$report = [ordered]@{
    ok = $promotionReady
    schema = "sqx-edge.sqx144-full-update1-gate-v1"
    phase = "SQX144-FULL-UPDATE1 Controlled Build 144.2953 Update Gate"
    mode = $Mode
    decision = $decision
    blockers = $blockers
    target = [ordered]@{
        label = "SQX144_2953_updated_host_candidate"
        pathRef = "path_$(Get-ShaRef $root)"
        hostProfile = "sqx144_full_update_candidate"
        expectedBuild = $ExpectedBuild
    }
    checks = $requiredChecks
    summary = [ordered]@{
        projectDirCount = $projectDirCount
        resultsPluginCount = $resultsPluginCount
        sqxEdgeReadinessPanelPresent = $panelPresent
        relevantProcessCount = $processSnapshot.count
        versionExpectedSeenInLatestLog = $versionSeen
        licenseDialogSeenInLatestLog = $licenseDialogSeen
        snippetCompileDoneSeenInLatestLog = $snippetCompileDoneSeen
        snippetCompileFailureSeenInLatestLog = $snippetCompileFailureSeen
        latestLogRef = if ($latestLog) { "log_$(Get-ShaRef $latestLog.FullName)" } else { "" }
    }
    processes = $processSnapshot
    guards = [ordered]@{
        readOnly = $true
        updateInstallerExecutedByThisScript = $false
        projectRunStarted = $false
        migrationToolUsedByThisScript = $false
        dataDbWriteAllowed = $false
        userProjectsWriteAllowed = $false
        engineBinaryCopyAllowed = $false
        licenseMaterialHandled = $false
        bypassAttempted = $false
        localConfigSwitched = $false
    }
    rollback = [ordered]@{
        currentCandidateRemains = "sqx144_full_migrated_host"
        rollbackExceptionHostProfile = "sqx142"
        legacyFallbackHostProfile = "deprecated_sqx142_not_active_fallback"
        rollbackRequired = $false
        activeFallback = $false
        nextAction = "operator_activate_or_migrate_updated_host_then_rerun_update_gate"
    }
    privacy = [ordered]@{
        localPathsReturned = $false
        rawProjectNamesReturned = $false
        rawPluginNamesReturned = $false
        rawLogLinesReturned = $false
        licenseMaterialReturned = $false
        tokensReturned = $false
    }
}

$report | ConvertTo-Json -Depth 8

if ($Mode -eq "preflight" -and -not $promotionReady) {
    exit 1
}

exit 0
