param(
  [switch]$Aggressive,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Resolve-InRepo {
  param([string]$RelativePath)
  $target = Join-Path $RepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $target)) {
    return $null
  }
  $resolved = (Resolve-Path -LiteralPath $target).Path
  if (-not ($resolved -eq $RepoRoot -or $resolved.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar))) {
    throw "Refusing to clean outside repository: $resolved"
  }
  return $resolved
}

function Get-RepoRelativePath {
  param([string]$FullPath)
  $resolved = (Resolve-Path -LiteralPath $FullPath).Path
  if ($resolved -eq $RepoRoot) {
    return "."
  }
  return $resolved.Substring($RepoRoot.Length + 1)
}

function Remove-RepoItem {
  param(
    [string]$RelativePath,
    [string]$Reason
  )
  $resolved = Resolve-InRepo $RelativePath
  if ($null -eq $resolved) {
    return
  }
  if ($DryRun) {
    Write-Output "DRY-RUN remove $RelativePath - $Reason"
    return
  }
  Get-ChildItem -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
    try {
      $_.Attributes = "Normal"
    } catch {
      Write-Output "warning could not normalize attributes for $($_.FullName)"
    }
  }
  Remove-Item -LiteralPath $resolved -Recurse -Force
  Write-Output "removed $RelativePath - $Reason"
}

function Remove-PycacheOutsideEmbeddedRuntime {
  $excludedFragments = @(
    "\backend\sqx-edge-tool\runtime\",
    "\backend\sqx-edge-tool\venv\"
  )
  Get-ChildItem -LiteralPath $RepoRoot -Recurse -Force -Directory -Filter "__pycache__" |
    Where-Object {
      $path = $_.FullName
      -not ($excludedFragments | Where-Object { $path.Contains($_) })
    } |
    ForEach-Object {
      $relative = Get-RepoRelativePath $_.FullName
      if ($DryRun) {
        Write-Output "DRY-RUN remove $relative - Python bytecode cache"
      } else {
        Remove-Item -LiteralPath $_.FullName -Recurse -Force
        Write-Output "removed $relative - Python bytecode cache"
      }
    }
}

function Remove-OldDistArtifacts {
  $dist = Resolve-InRepo "dist"
  if ($null -eq $dist) {
    return
  }

  $latestTesterZip = Get-ChildItem -LiteralPath $dist -File -Filter "SQX_Edge_Tool_Portable_Tester_*.zip" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  $keep = @{}
  if ($latestTesterZip) {
    $keep[$latestTesterZip.FullName] = $true
    $sha = $latestTesterZip.FullName + ".sha256"
    if (Test-Path -LiteralPath $sha) {
      $keep[(Resolve-Path -LiteralPath $sha).Path] = $true
    }
  }

  Get-ChildItem -LiteralPath $dist -Force | ForEach-Object {
    if ($keep.ContainsKey($_.FullName)) {
      Write-Output "kept $(Get-RepoRelativePath $_.FullName) - latest tester delivery"
      return
    }

    $isOldPortableZip = $_.PSIsContainer -or $_.Name -like "SQX_Edge_Tool_Portable_*.zip" -or $_.Name -like "SQX_Edge_Tool_Portable_*.zip.sha256" -or $_.Name -in @("SQX_distribution_audit.txt", "SQX_release_summary.txt")
    if (-not $isOldPortableZip) {
      return
    }

    $relative = Get-RepoRelativePath $_.FullName
    if ($DryRun) {
      Write-Output "DRY-RUN remove $relative - generated release artifact"
    } else {
      Remove-Item -LiteralPath $_.FullName -Recurse -Force
      Write-Output "removed $relative - generated release artifact"
    }
  }
}

Remove-RepoItem ".pytest_cache" "pytest cache"
Remove-PycacheOutsideEmbeddedRuntime
Remove-RepoItem "node_modules" "root npm dependencies can be reinstalled from package-lock"
Remove-RepoItem "templates\SQX_Edge_Tester_Portal\node_modules" "tester portal npm dependencies can be reinstalled from package-lock"
Remove-RepoItem "templates\SQX_Edge_Tester_Portal\.next" "Next.js build output"
Remove-RepoItem "templates\SQX_Edge_Tester_Portal\.open-next" "OpenNext build output"
Remove-RepoItem "templates\SQX_Edge_Tester_Portal\tsconfig.tsbuildinfo" "TypeScript incremental cache"
Remove-RepoItem "templates\SQX_Edge_Tester_Portal\backups" "local tester portal backups"

if ($Aggressive) {
  Remove-OldDistArtifacts
}
