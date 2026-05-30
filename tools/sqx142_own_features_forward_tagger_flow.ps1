param(
    [ValidateSet("status", "checklist", "validate-export", "record")]
    [string]$Action = "status",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$InputCsv = "",
    [string]$EvidenceDir = "",
    [ValidateSet("unknown", "pass", "blocked", "fail")]
    [string]$Outcome = "unknown",
    [switch]$UntaggedForwardCsvExported,
    [switch]$DataSmokeBuilt,
    [switch]$TagCsvInstalled,
    [switch]$TaggerEnabled,
    [switch]$FilterByResultsDisabled,
    [switch]$ColumnsPopulated,
    [switch]$FinalTaggerCsvExported,
    [string]$OperatorNote = ""
)

$ErrorActionPreference = "Stop"

$Version = "sqx142-own-features5-forward-tagger-flow-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LocalRoot = Join-Path $RepoRoot ".local\sqx142_own_features\forward_tagger_flow"
$DataSmokeScript = Join-Path $RepoRoot "tools\sqx142_own_features_correlation_data_smoke.ps1"
$Features4Script = Join-Path $RepoRoot "tools\sqx142_own_features_clean_mining_path_validation.ps1"

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

function Get-CsvDelimiter {
    param([string]$Path)
    $firstLine = Get-Content -LiteralPath $Path -TotalCount 1 -Encoding UTF8
    if ($firstLine -match ";") { return ";" }
    return ","
}

function Get-TinyHash {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Get-ColumnName {
    param([object[]]$Columns, [string]$Pattern)
    return @($Columns | Where-Object { $_ -like $Pattern })[0]
}

function Invoke-Status {
    $processes = Get-SqxProcesses
    $dataSmoke = $null
    $features4 = $null
    if (Test-Path -LiteralPath $DataSmokeScript -PathType Leaf) {
        $dataSmoke = Convert-ToolOutputToJson (& $DataSmokeScript -Action status -SqxRoot $SqxRoot)
    }
    if (Test-Path -LiteralPath $Features4Script -PathType Leaf) {
        $features4 = Convert-ToolOutputToJson (& $Features4Script -Action status -SqxRoot $SqxRoot)
    }
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "status"
        sqxClosed = $processes.Count -eq 0
        processCount = $processes.Count
        statusMarker = "ready_for_repeatable_forward_tagger_flow"
        features4Status = $features4.statusMarker
        tagCsvInstalled = if ($dataSmoke) { [bool]$dataSmoke.target.exists } else { $false }
        tagCsvSchemaOk = if ($dataSmoke) { [bool]$dataSmoke.target.schemaOk } else { $false }
        tagCsvRows = if ($dataSmoke) { [int]$dataSmoke.target.rows } else { 0 }
        requiredSequence = @(
            "Export Forward CSV before using the SQXEdge tagger as the source for Data Smoke.",
            "Close SQX before installing correlation_decisions.csv.",
            "Reopen SQX and enable SQXEdgeCorrelationTagger in Forward Ranking settings.",
            "Keep Filter by results of custom analysis disabled so all rows remain visible.",
            "Select SQX EDGE CORRELATION REVIEW and export the final tagger-confirmation CSV."
        )
        guards = @{
            sqx_runtime_started_by_script = $false
            data_db_write_allowed = $false
            user_projects_write_allowed = $false
            databank_delete_allowed = $false
            jars_write_allowed = $false
            internal_plugins_write_allowed = $false
            run_project_allowed = $false
            migration_tool_allowed = $false
        }
    } | ConvertTo-Json -Depth 8
}

function Invoke-Checklist {
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "checklist"
        title = "SQX142-OWN-FEATURES5 Forward Tagger Repeatable Flow"
        steps = @(
            [pscustomobject]@{
                step = 1
                action = "In SQX, run or open a clean generated custom whose final survivor databank is Forward/Foward."
                expected = "Project loads without red unresolved resources and the final survivor databank has natural rows."
            },
            [pscustomobject]@{
                step = 2
                action = "Export the Forward/Foward databank CSV before using the SQXEdge tagger as a filter."
                expected = "Source CSV contains strategy names, Filters result, Symbol, TimeFrame and performance columns."
            },
            [pscustomobject]@{
                step = 3
                action = "Close SQX. Run Data Smoke build/install from the exported CSV."
                expected = "Only user/extend/SQXEdge/Correlation/correlation_decisions.csv is installed with backup/hash."
            },
            [pscustomobject]@{
                step = 4
                action = "Reopen SQX, go to Forward task > Full settings > Ranking, and enable SQXEdgeCorrelationTagger Custom Analysis."
                expected = "Use the tagger as annotation; do not use it as the decision engine."
            },
            [pscustomobject]@{
                step = 5
                action = "Leave Filter by results of custom analysis disabled."
                expected = "All Forward rows remain visible; similar/non-portfolio rows are not removed inside SQX."
            },
            [pscustomobject]@{
                step = 6
                action = "Select SQX EDGE CORRELATION REVIEW and export a final tagger-confirmation CSV."
                expected = "SQX Edge Corr Decision/Rank/Score/Status/Nearest Winner columns are populated."
            },
            [pscustomobject]@{
                step = 7
                action = "Run validate-export against the final tagger CSV and record the run."
                expected = "Evidence records row count, decision distribution and no private raw report output."
            }
        )
        blocked = @(
            "Do not click /project/checkResources as a validation shortcut.",
            "Do not enable Filter by results of custom analysis for the lab visualization flow.",
            "Do not delete databank rows inside SQX as part of this tagger confirmation.",
            "Do not patch jars/internal plugins/license/data.db or use run_project/Migration Tool."
        )
    } | ConvertTo-Json -Depth 8
}

function Invoke-ValidateExport {
    if (-not $InputCsv.Trim()) {
        throw "InputCsv is required for validate-export."
    }
    if (-not (Test-Path -LiteralPath $InputCsv -PathType Leaf)) {
        throw "InputCsv not found: $InputCsv"
    }
    New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
    $resolved = (Resolve-Path -LiteralPath $InputCsv).Path
    $delimiter = Get-CsvDelimiter $resolved
    $rows = @(Import-Csv -LiteralPath $resolved -Delimiter $delimiter -Encoding UTF8)
    $columns = if ($rows.Count -gt 0) { @($rows[0].PSObject.Properties.Name) } else {
        @((Get-Content -LiteralPath $resolved -TotalCount 1 -Encoding UTF8) -split [regex]::Escape($delimiter) | ForEach-Object { $_.Trim('"') })
    }
    $decisionCol = Get-ColumnName $columns "SQX Edge Corr Deci*"
    $rankCol = Get-ColumnName $columns "SQX Edge Corr Rank*"
    $scoreCol = Get-ColumnName $columns "SQX Edge Corr Score*"
    $maxCorrCol = Get-ColumnName $columns "SQX Edge Max Corr*"
    $statusCol = Get-ColumnName $columns "SQX Edge Corr Stat*"
    $nearestCol = Get-ColumnName $columns "SQX Edge Nearest Winner*"
    $required = @($decisionCol, $rankCol, $scoreCol, $maxCorrCol, $statusCol, $nearestCol)
    $missingCount = @($required | Where-Object { -not $_ }).Count
    $portfolioRows = if ($decisionCol) { @($rows | Where-Object { $_.$decisionCol -eq "1" }).Count } else { 0 }
    $similarRows = if ($decisionCol) { @($rows | Where-Object { $_.$decisionCol -eq "0" }).Count } else { 0 }
    $statusRows = if ($statusCol) { @($rows | Where-Object { $_.$statusCol -and $_.$statusCol -ne "-1" }).Count } else { 0 }
    $nearestRows = if ($nearestCol) { @($rows | Where-Object { $_.$nearestCol }).Count } else { 0 }
    $columnsPopulated = ($rows.Count -gt 0 -and $missingCount -eq 0 -and $statusRows -gt 0 -and ($portfolioRows + $similarRows) -gt 0)
    $filterByResultsLikelyDisabled = ($portfolioRows -gt 0 -and $similarRows -gt 0)
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $evidence = [pscustomobject]@{
        ok = $columnsPopulated
        version = $Version
        action = "validate-export"
        validatedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        source = @{
            sha256 = Get-TinyHash $resolved
            rows = $rows.Count
            delimiter = $delimiter
            rawPathReturned = $false
        }
        columns = @{
            count = $columns.Count
            decision = $decisionCol
            rank = $rankCol
            score = $scoreCol
            maxCorrelation = $maxCorrCol
            status = $statusCol
            nearestWinner = $nearestCol
            missingCount = $missingCount
        }
        decisions = @{
            portfolio = $portfolioRows
            similar = $similarRows
            statusRows = $statusRows
            nearestWinnerRows = $nearestRows
        }
        inferredUiSettings = @{
            taggerEnabled = $columnsPopulated
            filterByResultsDisabled = $filterByResultsLikelyDisabled
        }
        guards = @{
            sqx_runtime_started_by_script = $false
            data_db_write_allowed = $false
            user_projects_write_allowed = $false
            databank_delete_allowed = $false
            tag_csv_only = $true
        }
    }
    $path = Join-Path $EvidenceDir "$Version`_validate_export_$stamp.json"
    $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding UTF8
    $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $EvidenceDir "latest_validate_export.json") -Encoding UTF8
    [pscustomobject]@{
        ok = $evidence.ok
        version = $Version
        action = "validate-export"
        evidencePath = $path
        rows = $rows.Count
        portfolio = $portfolioRows
        similar = $similarRows
        columnsPopulated = $columnsPopulated
        filterByResultsDisabled = $filterByResultsLikelyDisabled
    } | ConvertTo-Json -Depth 6
}

function Invoke-Record {
    New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
    $latestValidation = Join-Path $EvidenceDir "latest_validate_export.json"
    $validation = $null
    if (Test-Path -LiteralPath $latestValidation -PathType Leaf) {
        $validation = Get-Content -LiteralPath $latestValidation -Raw | ConvertFrom-Json
    }
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $record = [pscustomobject]@{
        ok = $true
        version = $Version
        action = "record"
        recordedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        outcome = $Outcome
        manualChecks = @{
            untaggedForwardCsvExported = [bool]$UntaggedForwardCsvExported
            dataSmokeBuilt = [bool]$DataSmokeBuilt
            tagCsvInstalled = [bool]$TagCsvInstalled
            taggerEnabled = [bool]$TaggerEnabled
            filterByResultsDisabled = [bool]$FilterByResultsDisabled
            columnsPopulated = [bool]$ColumnsPopulated
            finalTaggerCsvExported = [bool]$FinalTaggerCsvExported
        }
        latestValidation = $validation
        operatorNote = $OperatorNote
        blockedSurfaces = @("jars", "engine binaries", "internal plugins", "license/activation", "data.db", "user/projects", "databank deletion", "run_project", "Migration Tool")
    }
    $path = Join-Path $EvidenceDir "$Version`_manual_record_$stamp.json"
    $record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $path -Encoding UTF8
    $record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $EvidenceDir "latest_manual_record.json") -Encoding UTF8
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
    "validate-export" { Invoke-ValidateExport }
    "record" { Invoke-Record }
}
