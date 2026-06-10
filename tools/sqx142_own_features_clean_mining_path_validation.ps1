param(
    [ValidateSet("status", "checklist", "record")]
    [string]$Action = "status",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$EvidenceDir = "",
    [ValidateSet("unknown", "pass", "blocked", "fail")]
    [string]$Outcome = "unknown",
    [switch]$GeneratedProjectsStable,
    [switch]$FreshCustomGenerated,
    [switch]$FreshMiningRun,
    [switch]$FreshCsvExported,
    [switch]$DataSmokeBuilt,
    [switch]$TagCsvInstalled,
    [switch]$ColumnsPopulated,
    [switch]$NoRetiredDependencies,
    [switch]$NoUnresolvedResources,
    [string]$OperatorNote = ""
)

$ErrorActionPreference = "Stop"

$Version = "sqx142-own-features4-clean-mining-path-validation-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LocalRoot = Join-Path $RepoRoot ".local\sqx142_own_features\clean_mining_path_validation"
$StabilizerScript = Join-Path $RepoRoot "tools\sqx142_project_load_stabilizer.ps1"
$ManualScript = Join-Path $RepoRoot "tools\sqx142_own_features_correlation_manual_confirmation.ps1"
$DataSmokeScript = Join-Path $RepoRoot "tools\sqx142_own_features_correlation_data_smoke.ps1"
$LabScaffoldScript = Join-Path $RepoRoot "tools\sqx142_own_features_correlation_lab_project_scaffold.ps1"

if (-not $EvidenceDir.Trim()) {
    $EvidenceDir = $LocalRoot
}

function Get-SqxProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -like "StrategyQuantX*" -or $_.ProcessName -like "SQX*"
    })
}

function Convert-ToolOutputToJson {
    param([object[]]$Output)
    $raw = $Output | Out-String
    return $raw | ConvertFrom-Json
}

function Assert-ToolExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required tool not found: $Path"
    }
}

function Test-GeneratedProjectsStable {
    param($StabilizerStatus)
    $projects = @($StabilizerStatus.projects)
    if ($projects.Count -eq 0) {
        return $false
    }
    foreach ($project in $projects) {
        if (-not $project.exists -or -not $project.projectCfxExists) {
            return $false
        }
        if (@($project.findings).Count -gt 0 -or @($project.actions).Count -gt 0) {
            return $false
        }
        if (@($project.staleZipTempFiles).Count -gt 0) {
            return $false
        }
    }
    return $true
}

function Get-LatestManualRecord {
    $candidate = Join-Path $EvidenceDir "latest_manual_record.json"
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        try {
            return Get-Content -LiteralPath $candidate -Raw | ConvertFrom-Json
        } catch {
            return $null
        }
    }
    return $null
}

function Get-ManualSteps {
    return @(
        [pscustomobject]@{
            step = 1
            action = "Open SQX142 manually and confirm the generated Capa1/Capa2 projects do not alternate red unresolved-resource status."
            expected = "No red unresolved-resource status on the generated projects after startup."
        },
        [pscustomobject]@{
            step = 2
            action = "Generate or select a fresh custom from Edge Factory using the corrected SQX Edge / Darwinex profile."
            expected = "Fresh project is not copied from the old lab donor databanks."
        },
        [pscustomobject]@{
            step = 3
            action = "Load the fresh custom without clicking Load config using these settings unless SQX forces it."
            expected = "Project stays stable and does not create stale ZIP temp state."
        },
        [pscustomobject]@{
            step = 4
            action = "Run a short fresh mining/retest path and export the fresh output databank CSV."
            expected = "The exported rows come from the fresh path, not Monkey Test/Syntetic from the blocked lab project."
        },
        [pscustomobject]@{
            step = 5
            action = "Build Correlation Pack Data Smoke from the fresh CSV, then close SQX before any tag CSV install."
            expected = "Only correlation_decisions.csv is generated/installed through the existing guarded data-smoke tool."
        },
        [pscustomobject]@{
            step = 6
            action = "Reopen SQX142, select SQX EDGE CORRELATION REVIEW, and inspect the SQXEdge correlation columns."
            expected = "At least one matching fresh row shows non-default values and no strategy is rejected by the tagger."
        }
    )
}

function Invoke-Status {
    $processes = Get-SqxProcesses
    Assert-ToolExists $StabilizerScript
    Assert-ToolExists $ManualScript
    Assert-ToolExists $DataSmokeScript
    Assert-ToolExists $LabScaffoldScript
    $stabilizer = Convert-ToolOutputToJson (& $StabilizerScript -Action status -SqxRoot $SqxRoot)
    $manual = Convert-ToolOutputToJson (& $ManualScript -Action status -SqxRoot $SqxRoot)
    $dataSmoke = Convert-ToolOutputToJson (& $DataSmokeScript -Action status -SqxRoot $SqxRoot)
    $lab = Convert-ToolOutputToJson (& $LabScaffoldScript -Action status -SqxRoot $SqxRoot)
    $generatedStable = Test-GeneratedProjectsStable $stabilizer
    $legacyBlocked = [bool]$lab.retiredDependencyPreflight.target.blocked
    $latestRecord = Get-LatestManualRecord
    $completed = $false
    if ($latestRecord -and $latestRecord.outcome -eq "pass") {
        $checks = $latestRecord.manualChecks
        $completed = (
            [bool]$checks.generatedProjectsStable -and
            [bool]$checks.freshCustomGenerated -and
            [bool]$checks.freshMiningRun -and
            [bool]$checks.freshCsvExported -and
            [bool]$checks.dataSmokeBuilt -and
            [bool]$checks.tagCsvInstalled -and
            [bool]$checks.columnsPopulated -and
            [bool]$checks.noRetiredDependencies -and
            [bool]$checks.noUnresolvedResources
        )
    }
    $statusMarker = if ($completed) {
        "pass"
    } else {
        "prepared_readonly_preflight_green_pending_operator_clean_mining"
    }

    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "status"
        sqxRoot = $SqxRoot
        sqxClosed = $processes.Count -eq 0
        processCount = $processes.Count
        statusMarker = $statusMarker
        latestManualRecord = $latestRecord
        generatedProjectsStable = $generatedStable
        generatedProjectStatus = $stabilizer
        correlationPackReady = [bool]$manual.readyForManualSmoke
        tagCsvSchemaOk = [bool]$dataSmoke.target.schemaOk
        tagCsvRows = [int]$dataSmoke.target.rows
        legacyLabBlockedByRetiredDependencies = $legacyBlocked
        legacyLabStatus = $lab.retiredDependencyPreflight.target.status
        readyForOperatorCleanMiningCheck = ($generatedStable -and [bool]$manual.readyForManualSmoke -and $legacyBlocked)
        sqxClosedForFutureTagCsvInstall = ($processes.Count -eq 0)
        freshCsvEvidencePending = (-not $completed)
        nextRequiredManualEvidence = if ($completed) {
            @("Use SQX142-OWN-FEATURES5 Forward Tagger Repeatable Flow for future repeats.")
        } else {
            @(
                "generated projects stable in SQX UI",
                "fresh custom generated with corrected SQX Edge / Darwinex profile",
                "fresh mining/retest output exported as CSV",
                "data smoke rebuilt from fresh CSV",
                "SQX EDGE CORRELATION REVIEW columns populated from fresh rows"
            )
        }
        guards = @{
            sqx_runtime_started_by_script = $false
            sqx_files_written_by_script = $false
            data_db_write_allowed = $false
            user_projects_write_allowed = $false
            jars_write_allowed = $false
            internal_plugins_write_allowed = $false
            license_activation_write_allowed = $false
            databank_delete_allowed = $false
            run_project_allowed = $false
            migration_tool_allowed = $false
            retired_dependency_placeholder_allowed = $false
        }
    } | ConvertTo-Json -Depth 12
}

function Invoke-Checklist {
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "checklist"
        title = "SQX142-OWN-FEATURES4 Clean Mining Path Validation"
        beforeOpeningSqx = Invoke-Status | ConvertFrom-Json
        manualSteps = @(Get-ManualSteps)
        doNotUse = @(
            "blocked lab Monkey Test/Syntetic databanks",
            "ExitAfterDays placeholder snippets",
            "jar patches",
            "data.db writes",
            "run_project",
            "Migration Tool"
        )
        reportBack = "Tell Codex whether generated projects stayed stable, which fresh CSV was exported, and whether SQX EDGE CORRELATION REVIEW populated from fresh rows."
    } | ConvertTo-Json -Depth 12
}

function Invoke-Record {
    New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $record = [pscustomobject]@{
        ok = $true
        version = $Version
        action = "record"
        recordedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        outcome = $Outcome
        manualChecks = @{
            generatedProjectsStable = [bool]$GeneratedProjectsStable
            freshCustomGenerated = [bool]$FreshCustomGenerated
            freshMiningRun = [bool]$FreshMiningRun
            freshCsvExported = [bool]$FreshCsvExported
            dataSmokeBuilt = [bool]$DataSmokeBuilt
            tagCsvInstalled = [bool]$TagCsvInstalled
            columnsPopulated = [bool]$ColumnsPopulated
            noRetiredDependencies = [bool]$NoRetiredDependencies
            noUnresolvedResources = [bool]$NoUnresolvedResources
        }
        operatorNote = $OperatorNote
        status = Invoke-Status | ConvertFrom-Json
        blockedSurfaces = @("jars", "engine binaries", "internal plugins", "license/activation", "data.db", "production base projects", "databank deletion", "run_project", "Migration Tool", "retired dependency placeholders")
    }
    $path = Join-Path $EvidenceDir "$Version`_manual_record_$stamp.json"
    $record | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $path -Encoding UTF8
    $record | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $EvidenceDir "latest_manual_record.json") -Encoding UTF8
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "record"
        evidencePath = $path
        outcome = $Outcome
        manualChecks = $record.manualChecks
    } | ConvertTo-Json -Depth 6
}

switch ($Action) {
    "status" { Invoke-Status }
    "checklist" { Invoke-Checklist }
    "record" { Invoke-Record }
}
