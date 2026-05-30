param(
    [ValidateSet("status", "checklist", "record")]
    [string]$Action = "status",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$EvidenceDir = "",
    [ValidateSet("unknown", "pass", "blocked", "fail")]
    [string]$Outcome = "unknown",
    [switch]$ViewVisible,
    [switch]$SnippetsCompiled,
    [switch]$TaggerSelectable,
    [switch]$ColumnsPopulated,
    [switch]$NoStrategyRejection,
    [string]$OperatorNote = ""
)

$ErrorActionPreference = "Stop"

$Version = "sqx142-own-features3-correlation-manual-confirmation-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LocalRoot = Join-Path $RepoRoot ".local\sqx142_own_features\manual_confirmation"
$ExpectedSchema = "strategyRef,candidateId,decision,reason,score,maxObservedCorrelation,correlationStatus,nearestWinnerId,portfolioRank,generatedAt,version"
$TagCsvRelative = "user\extend\SQXEdge\Correlation\correlation_decisions.csv"

if (-not $EvidenceDir.Trim()) {
    $EvidenceDir = $LocalRoot
}

function Resolve-SqxPath {
    param([string]$RelativePath)
    return Join-Path $SqxRoot $RelativePath
}

function Get-SqxProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -like "StrategyQuantX*" -or $_.ProcessName -like "SQX*"
    })
}

function Get-Sha256OrNull {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    }
    return $null
}

function Get-CsvSummary {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            exists = $false
            hash = $null
            rows = 0
            schemaOk = $false
            header = ""
        }
    }
    $lines = @(Get-Content -LiteralPath $Path -ErrorAction Stop)
    $header = if ($lines.Count -gt 0) { $lines[0] } else { "" }
    return [pscustomobject]@{
        exists = $true
        hash = Get-Sha256OrNull $Path
        rows = [Math]::Max(0, $lines.Count - 1)
        schemaOk = $header -eq $ExpectedSchema
        header = $header
    }
}

function New-ExpectedTargets {
    $rows = @(
        @{ Kind = "custom_analysis"; Relative = "user\extend\Snippets\SQ\CustomAnalysis\SQXEdgeCorrelationTagger.java" },
        @{ Kind = "databank_column"; Relative = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrDecision.java" },
        @{ Kind = "databank_column"; Relative = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrRank.java" },
        @{ Kind = "databank_column"; Relative = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrScore.java" },
        @{ Kind = "databank_column"; Relative = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeMaxCorr.java" },
        @{ Kind = "databank_column"; Relative = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrStatus.java" },
        @{ Kind = "databank_column"; Relative = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeNearestWinner.java" },
        @{ Kind = "databank_view"; Relative = "user\settings\views\databanks\SQX EDGE CORRELATION REVIEW.vw" },
        @{ Kind = "tag_csv"; Relative = $TagCsvRelative }
    )
    return $rows | ForEach-Object {
        $target = Resolve-SqxPath $_.Relative
        [pscustomobject]@{
            kind = $_.Kind
            relativeTarget = $_.Relative
            exists = Test-Path -LiteralPath $target -PathType Leaf
            hash = Get-Sha256OrNull $target
        }
    }
}

function Get-ManualSteps {
    return @(
        [pscustomobject]@{
            step = 1
            action = "Open SQX142 lab manually."
            expected = "SQX opens normally; no license or compile error blocks the workspace."
        },
        [pscustomobject]@{
            step = 2
            action = "If snippets compilation appears, compile all snippets and keep the dialog only if there are errors."
            expected = "No red error for SQXEdgeCorrelationTagger or SQXEdgeCorr* columns."
        },
        [pscustomobject]@{
            step = 3
            action = "Use only a cloned/lab custom project or databank with strategy names matching the installed tag CSV."
            expected = "No production Capa1/Capa2 template is changed."
        },
        [pscustomobject]@{
            step = 4
            action = "Select the databank view named SQX EDGE CORRELATION REVIEW."
            expected = "The six SQXEdge correlation columns are visible."
        },
        [pscustomobject]@{
            step = 5
            action = "Enable/select Custom Analysis display SQX Edge Correlation Tagger, or code id SQXEdgeCorrelationTagger if SQX shows internal names."
            expected = "The tagger is selectable; it never rejects strategies."
        },
        [pscustomobject]@{
            step = 6
            action = "Run the lab task/tagger and inspect SQXEdgeCorrDecision, SQXEdgeCorrRank, SQXEdgeCorrScore, SQXEdgeMaxCorr, SQXEdgeCorrStatus and SQXEdgeNearestWinner."
            expected = "At least one matching row has non-default values; all -1/missing means the tag CSV does not match the databank names."
        }
    )
}

function Invoke-Status {
    $processes = Get-SqxProcesses
    $targets = @(New-ExpectedTargets)
    $tagCsv = Get-CsvSummary (Resolve-SqxPath $TagCsvRelative)
    $missingTargets = @($targets | Where-Object { -not $_.exists })
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "status"
        sqxRoot = $SqxRoot
        sqxClosed = $processes.Count -eq 0
        processCount = $processes.Count
        packageTargetsInstalled = $missingTargets.Count -eq 0
        missingTargets = @($missingTargets | ForEach-Object { $_.relativeTarget })
        tagCsv = $tagCsv
        readyForManualSmoke = ($missingTargets.Count -eq 0 -and $tagCsv.schemaOk -and $tagCsv.rows -gt 0)
        exactCustomAnalysisDisplay = "SQX Edge Correlation Tagger"
        exactCustomAnalysisCodeId = "SQXEdgeCorrelationTagger"
        exactViewName = "SQX EDGE CORRELATION REVIEW"
        manualConfirmationPending = $true
        targets = $targets
        guards = @{
            sqx_runtime_started_by_script = $false
            sqx_files_written_by_script = $false
            data_db_write_allowed = $false
            user_projects_write_allowed = $false
            databank_delete_allowed = $false
            run_project_allowed = $false
            migration_tool_allowed = $false
        }
    } | ConvertTo-Json -Depth 6
}

function Invoke-Checklist {
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "checklist"
        title = "SQX142-OWN-FEATURES3 Correlation Pack Manual Confirmation"
        beforeOpeningSqx = Invoke-Status | ConvertFrom-Json
        manualSteps = @(Get-ManualSteps)
        expectedColumns = @(
            "SQXEdgeCorrDecision",
            "SQXEdgeCorrRank",
            "SQXEdgeCorrScore",
            "SQXEdgeMaxCorr",
            "SQXEdgeCorrStatus",
            "SQXEdgeNearestWinner"
        )
        reportBack = "Tell Codex whether the view is visible, whether SQX Edge Correlation Tagger is selectable, and whether any rows show non-default values."
    } | ConvertTo-Json -Depth 8
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
            viewVisible = [bool]$ViewVisible
            snippetsCompiled = [bool]$SnippetsCompiled
            taggerSelectable = [bool]$TaggerSelectable
            columnsPopulated = [bool]$ColumnsPopulated
            noStrategyRejection = [bool]$NoStrategyRejection
        }
        operatorNote = $OperatorNote
        status = Invoke-Status | ConvertFrom-Json
        blockedSurfaces = @("jars", "internal plugins", "license/activation", "data.db", "user/projects", "databank deletion", "run_project", "Migration Tool")
    }
    $path = Join-Path $EvidenceDir "$Version`_manual_record_$stamp.json"
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding UTF8
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $EvidenceDir "latest_manual_record.json") -Encoding UTF8
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "record"
        evidencePath = $path
        outcome = $Outcome
        manualChecks = $record.manualChecks
    } | ConvertTo-Json -Depth 5
}

switch ($Action) {
    "status" { Invoke-Status }
    "checklist" { Invoke-Checklist }
    "record" { Invoke-Record }
}
