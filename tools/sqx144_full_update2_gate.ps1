[CmdletBinding(PositionalBinding = $true)]
param(
    [Parameter(Position = 0)]
    [ValidateSet("status", "preflight")]
    [string]$Mode = "status",

    [string]$SourceRoot = "",

    [string]$CandidateRoot = "",

    [string]$ExpectedBuild = "144.2953",

    [int]$MinProjectDirs = 29,

    [int]$MinResultsPlugins = 5
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    $SourceRoot = [string]$env:SQX144_FULL_ROOT
}

if ([string]::IsNullOrWhiteSpace($CandidateRoot)) {
    $CandidateRoot = [string]$env:SQX144_UPDATE2_ROOT
}

if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    throw "Missing working SQX 144 Full source root. Pass -SourceRoot or set SQX144_FULL_ROOT."
}

if ([string]::IsNullOrWhiteSpace($CandidateRoot)) {
    throw "Missing SQX 144.2953 candidate root. Pass -CandidateRoot or set SQX144_UPDATE2_ROOT."
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
    param([string[]]$Roots)
    $fullRoots = @($Roots | ForEach-Object {
        [System.IO.Path]::GetFullPath($_).TrimEnd("\", "/")
    })

    $processes = @()
    try {
        $processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $name = [string]$_.Name
                $exePath = [string]$_.ExecutablePath
                $sqxName = $name -match "^(StrategyQuantX|StrategyQuantX_ui|SQ_Installer|sqcli)(\.exe)?$"
                $underRoot = $false
                if ($exePath) {
                    foreach ($root in $fullRoots) {
                        if ($exePath.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
                            $underRoot = $true
                        }
                    }
                }
                $sqxName -or $underRoot
            } |
            Select-Object ProcessId, Name, ExecutablePath
    } catch {
        $processes = @()
    }

    $items = @($processes | ForEach-Object {
        $exePath = [string]$_.ExecutablePath
        [ordered]@{
            processRef = "process_$(Get-ShaRef "$($_.ProcessId)|$($_.Name)")"
            name = $_.Name
            underManagedRoot = [bool](
                $exePath -and
                (@($fullRoots | Where-Object {
                    $exePath.StartsWith($_, [System.StringComparison]::OrdinalIgnoreCase)
                }).Count -gt 0)
            )
        }
    })

    return [ordered]@{
        count = $items.Count
        items = $items
    }
}

function Get-HostShape {
    param(
        [string]$Root,
        [string]$ExpectedBuild
    )

    $fullRoot = [System.IO.Path]::GetFullPath($Root)
    $exe = Join-Path $fullRoot "StrategyQuantX.exe"
    $dataDb = Join-Path $fullRoot "user\data\data.db"
    $projects = Join-Path $fullRoot "user\projects"
    $resultsPlugins = Join-Path $fullRoot "user\extend\ResultsPlugins"
    $readinessPanel = Join-Path $resultsPlugins "SQX Edge Readiness Panel"
    $logDir = Join-Path $fullRoot "user\log\StrategyQuant"
    $latestLog = $null
    if (Test-Path -LiteralPath $logDir -PathType Container) {
        $latestLog = Get-ChildItem -LiteralPath $logDir -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
    }
    $logText = if ($latestLog) { Read-SharedText $latestLog.FullName } else { "" }

    $projectDirCount = Get-DirectoryCount $projects
    $resultsPluginCount = Get-DirectoryCount $resultsPlugins
    $panelPresent = Test-PathBool $readinessPanel
    $versionSeen = $logText -match ("SQX version:\s*" + [regex]::Escape($ExpectedBuild))
    $licenseDialogSeen = $logText -match "License dialog|Showing license form|licenseDialog\.html"
    $snippetCompileDoneSeen = $logText -match "Compiling Snippets done"
    $snippetCompileFailureSeen = $logText -match "Compilation FAILED"

    return [ordered]@{
        pathRef = "path_$(Get-ShaRef $fullRoot)"
        checks = [ordered]@{
            rootExists = Test-PathBool $fullRoot
            executableExists = Test-PathBool $exe
            dataDbExists = Test-PathBool $dataDb
            projectsDirExists = Test-PathBool $projects
            resultsPluginsDirExists = Test-PathBool $resultsPlugins
        }
        summary = [ordered]@{
            projectDirCount = $projectDirCount
            resultsPluginCount = $resultsPluginCount
            sqxEdgeReadinessPanelPresent = $panelPresent
            expectedBuildSeenInLatestLog = $versionSeen
            licenseDialogSeenInLatestLog = $licenseDialogSeen
            snippetCompileDoneSeenInLatestLog = $snippetCompileDoneSeen
            snippetCompileFailureSeenInLatestLog = $snippetCompileFailureSeen
            latestLogRef = if ($latestLog) { "log_$(Get-ShaRef $latestLog.FullName)" } else { "" }
        }
    }
}

$source = [System.IO.Path]::GetFullPath($SourceRoot)
$candidate = [System.IO.Path]::GetFullPath($CandidateRoot)
$sameRoot = [string]::Equals($source.TrimEnd("\", "/"), $candidate.TrimEnd("\", "/"), [System.StringComparison]::OrdinalIgnoreCase)
$processSnapshot = Get-TargetProcessSnapshot -Roots @($source, $candidate)
$sourceShape = Get-HostShape -Root $source -ExpectedBuild $ExpectedBuild
$candidateShape = Get-HostShape -Root $candidate -ExpectedBuild $ExpectedBuild

$sourceShapeOk = -not ($sourceShape.checks.Values -contains $false)
$candidateShapeOk = -not ($candidateShape.checks.Values -contains $false)
$candidateMigratedShapePresent = (
    $candidateShape.summary.projectDirCount -ge $MinProjectDirs -and
    $candidateShape.summary.resultsPluginCount -ge $MinResultsPlugins -and
    $candidateShape.summary.sqxEdgeReadinessPanelPresent
)
$candidateWorkspaceClear = (-not $candidateShape.summary.licenseDialogSeenInLatestLog)
$candidateBuildConfirmed = [bool]$candidateShape.summary.expectedBuildSeenInLatestLog
$candidateSnippetClear = (-not $candidateShape.summary.snippetCompileFailureSeenInLatestLog)

$checks = [ordered]@{
    distinctSourceAndCandidateRoots = (-not $sameRoot)
    sourceWorkingHostShapePresent = $sourceShapeOk
    sourceReadinessPanelPresent = [bool]$sourceShape.summary.sqxEdgeReadinessPanelPresent
    candidateHostShapePresent = $candidateShapeOk
    noRelevantProcesses = ($processSnapshot.count -eq 0)
    candidateExpectedBuildSeenInLog = $candidateBuildConfirmed
    candidateLicenseWorkspaceGateClear = $candidateWorkspaceClear
    candidateMigratedProjectShapePresent = ($candidateShape.summary.projectDirCount -ge $MinProjectDirs)
    candidateMigratedResultsPluginShapePresent = ($candidateShape.summary.resultsPluginCount -ge $MinResultsPlugins)
    candidateReadinessPanelPresent = [bool]$candidateShape.summary.sqxEdgeReadinessPanelPresent
    candidateNoSnippetCompileFailureSeen = $candidateSnippetClear
}

$blockers = @()
if (-not $checks.distinctSourceAndCandidateRoots) {
    $blockers += "installer_requires_new_candidate_directory"
}
if (-not $checks.sourceWorkingHostShapePresent -or -not $checks.sourceReadinessPanelPresent) {
    $blockers += "working_source_host_not_ready"
}
if (-not $checks.candidateHostShapePresent) {
    $blockers += "candidate_host_shape_missing"
}
if (-not $checks.noRelevantProcesses) {
    $blockers += "relevant_processes_running"
}
if (-not $checks.candidateExpectedBuildSeenInLog) {
    $blockers += "candidate_expected_build_not_confirmed"
}
if (-not $checks.candidateLicenseWorkspaceGateClear) {
    $blockers += "candidate_license_activation_pending"
}
if (-not $candidateMigratedShapePresent) {
    $blockers += "candidate_official_migration_alignment_pending"
}
if (-not $checks.candidateNoSnippetCompileFailureSeen) {
    $blockers += "candidate_snippet_compile_failure_seen"
}

$promotionReady = ($blockers.Count -eq 0)
if ($promotionReady) {
    $decision = "sqx144_full_update2_ready_for_promotion"
} elseif ($blockers -contains "installer_requires_new_candidate_directory") {
    $decision = "blocked_candidate_must_be_new_directory"
} elseif (($blockers -contains "candidate_license_activation_pending") -and ($blockers -contains "candidate_official_migration_alignment_pending")) {
    $decision = "blocked_candidate_license_and_official_migration_alignment_pending"
} elseif ($blockers -contains "candidate_license_activation_pending") {
    $decision = "blocked_candidate_license_activation_pending"
} elseif ($blockers -contains "candidate_official_migration_alignment_pending") {
    $decision = "blocked_candidate_official_migration_alignment_pending"
} elseif ($blockers -contains "candidate_expected_build_not_confirmed") {
    $decision = "blocked_candidate_expected_build_not_confirmed"
} elseif ($blockers -contains "relevant_processes_running") {
    $decision = "blocked_relevant_processes_running"
} else {
    $decision = "blocked_update2_gate_not_ready"
}

$report = [ordered]@{
    ok = $promotionReady
    schema = "sqx-edge.sqx144-full-update2-gate-v1"
    phase = "SQX144-FULL-UPDATE2 New Directory 144.2953 Promotion Gate"
    mode = $Mode
    decision = $decision
    blockers = $blockers
    source = [ordered]@{
        label = "SQX_144_Full_working_migrated_source"
        pathRef = $sourceShape.pathRef
        hostProfile = "sqx144_full"
    }
    candidate = [ordered]@{
        label = "SQX144_2953_new_directory_candidate"
        pathRef = $candidateShape.pathRef
        hostProfile = "sqx144_full_2953_candidate"
        expectedBuild = $ExpectedBuild
    }
    checks = $checks
    sourceSummary = $sourceShape.summary
    candidateSummary = $candidateShape.summary
    processes = $processSnapshot
    guards = [ordered]@{
        readOnly = $true
        installerExecutedByThisScript = $false
        officialMigrationToolExecutedByThisScript = $false
        projectRunStarted = $false
        dataDbWriteAllowed = $false
        userProjectsWriteAllowed = $false
        engineBinaryCopyAllowed = $false
        licenseMaterialHandled = $false
        hostsFileMutationAllowed = $false
        bypassAttempted = $false
        localConfigSwitched = $false
    }
    nextAction = if ($promotionReady) {
        "switch_ignored_local_config_to_sqx144_full_2953_candidate_after_backup"
    } else {
        "operator_install_144_2953_to_new_directory_then_activate_or_use_official_migration_from_working_host_and_rerun_gate"
    }
    rollback = [ordered]@{
        currentCandidateRemains = "sqx144_full_migrated_host"
        rollbackExceptionHostProfile = "sqx142"
        legacyFallbackHostProfile = "deprecated_sqx142_not_active_fallback"
        rollbackRequired = $false
        activeFallback = $false
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
