param(
    [ValidateSet("status", "install", "rollback")]
    [string]$Action = "status",
    [string]$SqxRoot = $env:SQX142_ROOT,
    [string]$BackupId = ""
)

$ErrorActionPreference = "Stop"

$PackageVersion = "sqx142-own-features1-correlation-pack-v1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PackageRoot = Join-Path $RepoRoot "integrations\sqx142\own_features\correlation_pack"
$LocalRoot = Join-Path $RepoRoot ".local\sqx142_own_features"
$BackupRoot = Join-Path $LocalRoot "backups"

function Resolve-TargetPath {
    param([string]$RelativePath)
    return (Join-Path $SqxRoot $RelativePath)
}

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

function Assert-AllowedTarget {
    param([string]$Path)
    $root = (Resolve-Path $SqxRoot).Path.TrimEnd("\")
    $resolved = [System.IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Target escapes SQX root: $resolved"
    }
    $relative = $resolved.Substring($root.Length).TrimStart("\").Replace("/", "\")
    $lower = $relative.ToLowerInvariant()
    $allowed = (
        $lower.StartsWith("user\extend\snippets\sq\customanalysis\") -or
        $lower.StartsWith("user\extend\snippets\sq\columns\databanks\") -or
        $lower.StartsWith("user\settings\views\databanks\") -or
        $lower.StartsWith("user\extend\sqxedge\correlation\")
    )
    $blocked = (
        $lower.Contains("\jars\") -or
        $lower.Contains("\plugins\") -or
        $lower.Contains("\license\") -or
        $lower.Contains("\activation\") -or
        $lower.EndsWith("data.db") -or
        $lower.StartsWith("user\projects\") -or
        $lower.Contains("run_project") -or
        $lower.Contains("migration")
    )
    if (-not $allowed -or $blocked) {
        throw "Target is outside supported SQX surfaces: $relative"
    }
}

function Get-Sha256OrNull {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    }
    return $null
}

function New-FileMap {
    $rows = @(
        @{ Source = "Snippets\SQ\CustomAnalysis\SQXEdgeCorrelationTagger.java"; Target = "user\extend\Snippets\SQ\CustomAnalysis\SQXEdgeCorrelationTagger.java"; CopyWhenMissingOnly = $false },
        @{ Source = "Snippets\SQ\Columns\Databanks\SQXEdgeCorrDecision.java"; Target = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrDecision.java"; CopyWhenMissingOnly = $false },
        @{ Source = "Snippets\SQ\Columns\Databanks\SQXEdgeCorrRank.java"; Target = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrRank.java"; CopyWhenMissingOnly = $false },
        @{ Source = "Snippets\SQ\Columns\Databanks\SQXEdgeCorrScore.java"; Target = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrScore.java"; CopyWhenMissingOnly = $false },
        @{ Source = "Snippets\SQ\Columns\Databanks\SQXEdgeMaxCorr.java"; Target = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeMaxCorr.java"; CopyWhenMissingOnly = $false },
        @{ Source = "Snippets\SQ\Columns\Databanks\SQXEdgeCorrStatus.java"; Target = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeCorrStatus.java"; CopyWhenMissingOnly = $false },
        @{ Source = "Snippets\SQ\Columns\Databanks\SQXEdgeNearestWinner.java"; Target = "user\extend\Snippets\SQ\Columns\Databanks\SQXEdgeNearestWinner.java"; CopyWhenMissingOnly = $false },
        @{ Source = "views\SQX EDGE CORRELATION REVIEW.vw"; Target = "user\settings\views\databanks\SQX EDGE CORRELATION REVIEW.vw"; CopyWhenMissingOnly = $false },
        @{ Source = "samples\correlation_decisions.csv"; Target = "user\extend\SQXEdge\Correlation\correlation_decisions.sample.csv"; CopyWhenMissingOnly = $false },
        @{ Source = "samples\correlation_decisions.csv"; Target = "user\extend\SQXEdge\Correlation\correlation_decisions.csv"; CopyWhenMissingOnly = $true }
    )
    return $rows | ForEach-Object {
        [pscustomobject]@{
            Source = Join-Path $PackageRoot $_.Source
            Target = Resolve-TargetPath $_.Target
            RelativeTarget = $_.Target
            CopyWhenMissingOnly = [bool]$_.CopyWhenMissingOnly
        }
    }
}

function Invoke-Status {
    $processes = Get-SqxProcesses
    $files = New-FileMap | ForEach-Object {
        [pscustomobject]@{
            relativeTarget = $_.RelativeTarget
            exists = Test-Path -LiteralPath $_.Target -PathType Leaf
            hash = Get-Sha256OrNull $_.Target
        }
    }
    $latestBackup = Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    [pscustomobject]@{
        ok = $true
        version = $PackageVersion
        action = "status"
        sqxRoot = $SqxRoot
        sqxClosed = $processes.Count -eq 0
        processCount = $processes.Count
        processes = @($processes | ForEach-Object { [pscustomobject]@{ name = $_.ProcessName; id = $_.Id } })
        targets = @($files)
        latestBackup = if ($latestBackup) { $latestBackup.Name } else { $null }
    } | ConvertTo-Json -Depth 5
}

function Invoke-Install {
    Assert-NoSqxProcess
    New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BackupRoot "$PackageVersion`_$stamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $entries = @()
    foreach ($file in New-FileMap) {
        if (-not (Test-Path -LiteralPath $file.Source -PathType Leaf)) {
            throw "Package source missing: $($file.Source)"
        }
        Assert-AllowedTarget $file.Target
        $targetExists = Test-Path -LiteralPath $file.Target -PathType Leaf
        $backupPath = $null
        if ($targetExists) {
            $backupPath = Join-Path $backupDir $file.RelativeTarget
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
            Copy-Item -LiteralPath $file.Target -Destination $backupPath -Force
        }
        if (-not ($file.CopyWhenMissingOnly -and $targetExists)) {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $file.Target) | Out-Null
            Copy-Item -LiteralPath $file.Source -Destination $file.Target -Force
        }
        $entries += [pscustomobject]@{
            relativeTarget = $file.RelativeTarget
            target = $file.Target
            existed = $targetExists
            backupPath = $backupPath
            beforeHash = if ($targetExists) { Get-Sha256OrNull $backupPath } else { $null }
            afterHash = Get-Sha256OrNull $file.Target
            copied = -not ($file.CopyWhenMissingOnly -and $targetExists)
        }
    }
    $evidence = [pscustomobject]@{
        ok = $true
        version = $PackageVersion
        action = "install"
        installedAt = (Get-Date).ToUniversalTime().ToString("s") + "Z"
        sqxRoot = $SqxRoot
        backupId = Split-Path -Leaf $backupDir
        backupDir = $backupDir
        files = $entries
        blockedSurfaces = @("jars", "plugins internal", "license/activation", "data.db", "user/projects", "databank deletion", "run_project", "Migration Tool")
    }
    $manifestPath = Join-Path $backupDir "rollback_manifest.json"
    $evidence | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    $evidencePath = Join-Path $LocalRoot "$PackageVersion`_install_$stamp.json"
    New-Item -ItemType Directory -Force -Path $LocalRoot | Out-Null
    $evidence | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $evidencePath -Encoding UTF8
    $evidence | ConvertTo-Json -Depth 6
}

function Resolve-BackupDir {
    if ($BackupId.Trim().Length -gt 0) {
        $candidate = Join-Path $BackupRoot $BackupId
        if (Test-Path -LiteralPath $candidate -PathType Container) { return $candidate }
        throw "BackupId not found: $BackupId"
    }
    $latest = Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $latest) { throw "No backup available for rollback." }
    return $latest.FullName
}

function Invoke-Rollback {
    Assert-NoSqxProcess
    $backupDir = Resolve-BackupDir
    $manifestPath = Join-Path $backupDir "rollback_manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Rollback manifest missing: $manifestPath"
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $entries = @()
    foreach ($file in $manifest.files) {
        Assert-AllowedTarget $file.target
        if ($file.existed -eq $true) {
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $file.target) | Out-Null
            Copy-Item -LiteralPath $file.backupPath -Destination $file.target -Force
            $actionTaken = "restored"
        } elseif (Test-Path -LiteralPath $file.target -PathType Leaf) {
            Remove-Item -LiteralPath $file.target -Force
            $actionTaken = "removed_installed_file"
        } else {
            $actionTaken = "already_absent"
        }
        $entries += [pscustomobject]@{
            relativeTarget = $file.relativeTarget
            action = $actionTaken
            hash = Get-Sha256OrNull $file.target
        }
    }
    [pscustomobject]@{
        ok = $true
        version = $PackageVersion
        action = "rollback"
        backupId = Split-Path -Leaf $backupDir
        files = $entries
    } | ConvertTo-Json -Depth 5
}

switch ($Action) {
    "status" { Invoke-Status }
    "install" { Invoke-Install }
    "rollback" { Invoke-Rollback }
}
