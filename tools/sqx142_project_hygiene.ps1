param(
    [ValidateSet("status", "plan", "quarantine", "rollback")]
    [string]$Action = "status",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$BackupId = "",
    [switch]$IncludeKnownRed
)

$ErrorActionPreference = "Stop"

$Version = "sqx142-project-hygiene-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ProjectsRoot = Join-Path $SqxRoot "user\projects"
$QuarantineRoot = Join-Path $SqxRoot "user\projects_quarantine\SQXEdge"
$LocalRoot = Join-Path $RepoRoot ".local\sqx142_project_hygiene"
$BackupRoot = Join-Path $LocalRoot "backups"

$ProtectedNames = @(
    "Builder",
    "Retester",
    "Optimizer",
    "PortfolioComposer",
    "PortfolioMaster",
    "AUTOMATIC RETEST",
    "Capa1_Long_SQX142_Base",
    "Capa1_Long_SQX142_Base(2)",
    "Capa2_Base_SQX142_Base",
    "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa1",
    "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2",
    "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1",
    "IMOX XAU H1 2025(2)"
)

$KnownRedUnresolvedNames = @(
    "Capa1_Long_SQX142_Base",
    "IMOX XAU H1 2025(2)",
    "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2"
)

function Get-SqxProcesses {
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -like "StrategyQuantX*" -or $_.ProcessName -like "SQX*"
    })
}

function Assert-NoSqxProcess {
    $processes = Get-SqxProcesses
    if ($processes.Count -gt 0) {
        $names = ($processes | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ", "
        throw "SQX must be closed before $Action. Running process(es): $names"
    }
}

function Assert-InRoot {
    param([string]$Path, [string]$Root)
    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd("\")
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    if (-not $pathFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path escapes root. path=$pathFull root=$rootFull"
    }
}

function Get-ProjectKind {
    param([string]$Name)
    if ($IncludeKnownRed -and ($KnownRedUnresolvedNames -contains $Name)) { return "known_red_candidate" }
    if ($ProtectedNames -contains $Name) { return "protected" }
    if ($Name -like "E2E_*") { return "quarantine_candidate" }
    if ($Name -like "_PERFQ_*") { return "quarantine_candidate" }
    if ($Name -like "_SMOKE_*") { return "quarantine_candidate" }
    if ($Name -like "CODEx_TEST_*") { return "quarantine_candidate" }
    return "keep"
}

function Is-QuarantineKind {
    param([string]$Kind)
    return $Kind -eq "quarantine_candidate" -or $Kind -eq "known_red_candidate"
}

function Get-DirHash {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $null }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $builder = New-Object System.Text.StringBuilder
        Get-ChildItem -LiteralPath $Path -Recurse -File -Force |
            Sort-Object FullName |
            ForEach-Object {
                $relative = $_.FullName.Substring($Path.Length).TrimStart("\")
                $fileHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
                [void]$builder.AppendLine("$relative|$($_.Length)|$fileHash")
            }
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($builder.ToString())
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Get-ProjectInventory {
    if (-not (Test-Path -LiteralPath $ProjectsRoot -PathType Container)) {
        throw "Projects root not found: $ProjectsRoot"
    }
    Get-ChildItem -LiteralPath $ProjectsRoot -Force -Directory |
        Where-Object { $_.Name -ne "projects_quarantine" } |
        Sort-Object Name |
        ForEach-Object {
            $files = @(Get-ChildItem -LiteralPath $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue)
            [pscustomobject]@{
                name = $_.Name
                kind = Get-ProjectKind $_.Name
                path = $_.FullName
                fileCount = $files.Count
                sizeBytes = ($files | Measure-Object -Property Length -Sum).Sum
                lastWriteTime = $_.LastWriteTime.ToString("s")
            }
        }
}

function Invoke-Status {
    $processes = Get-SqxProcesses
    $inventory = @(Get-ProjectInventory)
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "status"
        sqxClosed = $processes.Count -eq 0
        processCount = $processes.Count
        totalProjects = $inventory.Count
        quarantineCandidates = @($inventory | Where-Object { Is-QuarantineKind $_.kind }).Count
        protectedProjects = @($inventory | Where-Object { $_.kind -eq "protected" }).Count
        keepProjects = @($inventory | Where-Object { $_.kind -eq "keep" }).Count
        latestBackup = (Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
    } | ConvertTo-Json -Depth 4
}

function Invoke-Plan {
    $inventory = @(Get-ProjectInventory)
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "plan"
        candidates = @($inventory | Where-Object { Is-QuarantineKind $_.kind })
        protected = @($inventory | Where-Object { $_.kind -eq "protected" } | Select-Object name,kind,lastWriteTime)
        keep = @($inventory | Where-Object { $_.kind -eq "keep" } | Select-Object name,kind,lastWriteTime)
        blockedSurfaces = @("snippets", "data.db", "license/activation", "jars", "plugins", "run_project", "databank deletion")
    } | ConvertTo-Json -Depth 6
}

function Invoke-Quarantine {
    Assert-NoSqxProcess
    $inventory = @(Get-ProjectInventory | Where-Object { Is-QuarantineKind $_.kind })
    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BackupRoot "$Version`_$stamp"
    $targetRoot = Join-Path $QuarantineRoot "$Version`_$stamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
    $moves = @()
    foreach ($project in $inventory) {
        Assert-InRoot $project.path $ProjectsRoot
        $destination = Join-Path $targetRoot $project.name
        Assert-InRoot $destination $QuarantineRoot
        $beforeHash = Get-DirHash $project.path
        Move-Item -LiteralPath $project.path -Destination $destination
        $afterHash = Get-DirHash $destination
        $moves += [pscustomobject]@{
            name = $project.name
            from = $project.path
            to = $destination
            fileCount = $project.fileCount
            sizeBytes = $project.sizeBytes
            beforeHash = $beforeHash
            afterHash = $afterHash
        }
    }
    $evidence = [pscustomobject]@{
        ok = $true
        version = $Version
        action = "quarantine"
        backupId = Split-Path -Leaf $backupDir
        quarantineRoot = $targetRoot
        movedCount = $moves.Count
        moves = $moves
        blockedSurfaces = @("snippets", "data.db", "license/activation", "jars", "plugins", "run_project", "databank deletion")
    }
    $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $backupDir "rollback_manifest.json") -Encoding UTF8
    $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $LocalRoot "$Version`_quarantine_$stamp.json") -Encoding UTF8
    $evidence | ConvertTo-Json -Depth 8
}

function Resolve-BackupDir {
    if ($BackupId.Trim()) {
        $candidate = Join-Path $BackupRoot $BackupId
        if (Test-Path -LiteralPath $candidate -PathType Container) { return $candidate }
        throw "BackupId not found: $BackupId"
    }
    $latest = Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) { throw "No project hygiene backup available for rollback." }
    return $latest.FullName
}

function Invoke-Rollback {
    Assert-NoSqxProcess
    $backupDir = Resolve-BackupDir
    $manifestPath = Join-Path $backupDir "rollback_manifest.json"
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $restored = @()
    foreach ($move in $manifest.moves) {
        Assert-InRoot $move.to $QuarantineRoot
        Assert-InRoot $move.from $ProjectsRoot
        if (Test-Path -LiteralPath $move.from) {
            throw "Rollback target already exists: $($move.from)"
        }
        Move-Item -LiteralPath $move.to -Destination $move.from
        $restored += [pscustomobject]@{
            name = $move.name
            restoredTo = $move.from
            hash = Get-DirHash $move.from
        }
    }
    [pscustomobject]@{
        ok = $true
        version = $Version
        action = "rollback"
        backupId = Split-Path -Leaf $backupDir
        restoredCount = $restored.Count
        restored = $restored
    } | ConvertTo-Json -Depth 6
}

switch ($Action) {
    "status" { Invoke-Status }
    "plan" { Invoke-Plan }
    "quarantine" { Invoke-Quarantine }
    "rollback" { Invoke-Rollback }
}
