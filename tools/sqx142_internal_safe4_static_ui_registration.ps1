param(
  [ValidateSet('status', 'install', 'rollback')]
  [string]$Action = 'status',
  [string]$SQXRoot = $env:SQX142_ROOT,
  [string]$BackupId = ''
)

$ErrorActionPreference = 'Stop'

$Phase = 'SQX142-INTERNAL-SAFE4'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$EvidenceDir = Join-Path $RepoRoot '.local\sqx142_internal_safe'
$BackupRoot = Join-Path $EvidenceDir 'backups'
$LatestBackupFile = Join-Path $EvidenceDir 'latest_safe4_backup.txt'
$TargetTemplate = Join-Path $SQXRoot 'internal\web\common\templates.html'
$MarkerBegin = '<!-- SQX142-INTERNAL-SAFE4-BEGIN -->'
$MarkerEnd = '<!-- SQX142-INTERNAL-SAFE4-END -->'
$Anchor = "    <div ng-include=`"'../../../plugins/ResultsSourceCode/terminalConfigPopup.html'`"></div>"

$PatchBlock = @'
    <!-- SQX142-INTERNAL-SAFE4-BEGIN -->
    <div class="sqx-edge-safe4-panel" style="margin:10px 0 12px 0;padding:10px 12px;border:1px solid #2f5d7c;background:#121a20;color:#dce8ee;font-size:12px;line-height:1.35;">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
            <strong style="font-size:13px;color:#ffffff;">SQX Edge Readiness Panel</strong>
            <span style="color:#9fc5d8;">sqx142-internal-safe4-static-ui-registration-v1</span>
        </div>
        <div style="margin-top:7px;color:#b9cad2;">
            Static registration bridge for the SQX Edge 144 backport readiness controls. No engine, project, databank, data.db, license or runtime mutation is performed by this panel.
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:9px;">
            <div style="padding:7px;border:1px solid #294757;background:#18242b;"><span style="display:block;color:#8fb2c4;">Extension</span><strong>installed</strong></div>
            <div style="padding:7px;border:1px solid #294757;background:#18242b;"><span style="display:block;color:#8fb2c4;">MCP-like API</span><strong>read-only</strong></div>
            <div style="padding:7px;border:1px solid #294757;background:#18242b;"><span style="display:block;color:#8fb2c4;">Monte Carlo</span><strong>external bench</strong></div>
            <div style="padding:7px;border:1px solid #294757;background:#18242b;"><span style="display:block;color:#8fb2c4;">Migration</span><strong>copy checklist</strong></div>
        </div>
        <div style="margin-top:8px;color:#94b1bf;">Surface: native ResultsSourceCode template. Rollback: tools\sqx142_internal_safe4_static_ui_registration.ps1 -Action rollback.</div>
    </div>
    <!-- SQX142-INTERNAL-SAFE4-END -->
'@

function Resolve-SafePath {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path) {
    return (Resolve-Path -LiteralPath $Path).Path
  }
  return [System.IO.Path]::GetFullPath($Path)
}

function Assert-UnderPath {
  param([string]$Child, [string]$Parent)
  $childFull = Resolve-SafePath $Child
  $parentFull = Resolve-SafePath $Parent
  if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Unsafe path outside parent: $Child"
  }
}

function Assert-NoSqxProcess {
  $processes = @(Get-Process | Where-Object { $_.ProcessName -match 'StrategyQuant|StrategyQuantX|sqx|java|javaw' } | Select-Object ProcessName, Id)
  if ($processes.Count -gt 0) {
    $summary = ($processes | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ', '
    throw "SQX/Java process detected; close SQX before this action. $summary"
  }
  return $processes
}

function Get-TemplateHash {
  if (-not (Test-Path -LiteralPath $TargetTemplate)) {
    return $null
  }
  return (Get-FileHash -LiteralPath $TargetTemplate -Algorithm SHA256).Hash
}

function Get-TemplateStatus {
  $exists = Test-Path -LiteralPath $TargetTemplate
  $content = if ($exists) { Get-Content -LiteralPath $TargetTemplate -Raw } else { '' }
  $processes = @(Get-Process | Where-Object { $_.ProcessName -match 'StrategyQuant|StrategyQuantX|sqx|java|javaw' } | Select-Object ProcessName, Id)
  return [pscustomobject]@{
    phase = $Phase
    status = 'status'
    targetRef = 'SQX142_ROOT/internal/web/common/templates.html'
    targetExists = $exists
    markerPresent = $content.Contains($MarkerBegin) -and $content.Contains($MarkerEnd)
    anchorPresent = $content.Contains($Anchor)
    targetSha256 = Get-TemplateHash
    processCount = $processes.Count
    processes = $processes
    latestBackupRef = if (Test-Path -LiteralPath $LatestBackupFile) { (Get-Content -LiteralPath $LatestBackupFile -Raw).Trim().Replace($RepoRoot, '.').Replace('\', '/') } else { $null }
  }
}

function New-TemplateBackup {
  New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $backupDir = Join-Path $BackupRoot "sqx142_internal_safe4_static_ui_registration_$stamp"
  New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
  Copy-Item -LiteralPath $TargetTemplate -Destination (Join-Path $backupDir 'templates.html') -Force
  Set-Content -LiteralPath $LatestBackupFile -Value $backupDir -Encoding UTF8
  return $backupDir
}

function Install-Registration {
  Assert-NoSqxProcess | Out-Null
  if (-not (Test-Path -LiteralPath $TargetTemplate)) {
    throw "Missing target template: $TargetTemplate"
  }
  Assert-UnderPath -Child $TargetTemplate -Parent $SQXRoot

  $beforeHash = Get-TemplateHash
  $content = Get-Content -LiteralPath $TargetTemplate -Raw
  if ($content.Contains($MarkerBegin) -or $content.Contains($MarkerEnd)) {
    return [pscustomobject]@{
      phase = $Phase
      status = 'already_registered'
      targetRef = 'SQX142_ROOT/internal/web/common/templates.html'
      targetSha256 = $beforeHash
      markerPresent = $true
      rollback = @{ available = Test-Path -LiteralPath $LatestBackupFile; command = 'tools\sqx142_internal_safe4_static_ui_registration.ps1 -Action rollback' }
    }
  }
  if (-not $content.Contains($Anchor)) {
    throw 'SAFE4 anchor not found in ResultsSourceCode template.'
  }

  $backupDir = New-TemplateBackup
  $patched = $content.Replace($Anchor, ($PatchBlock + [Environment]::NewLine + $Anchor))
  Set-Content -LiteralPath $TargetTemplate -Value $patched -Encoding UTF8
  $afterHash = Get-TemplateHash

  $evidenceName = 'sqx142_internal_safe4_static_ui_registration_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.json'
  $evidencePath = Join-Path $EvidenceDir $evidenceName
  $evidence = [pscustomobject]@{
    phase = $Phase
    status = 'registered_static_ui_with_backup_hash_rollback_ready'
    date = '2026-05-26'
    targetRef = 'SQX142_ROOT/internal/web/common/templates.html'
    surface = 'native ResultsSourceCode template'
    registrationVersion = 'sqx142-internal-safe4-static-ui-registration-v1'
    backupRef = $backupDir.Replace($RepoRoot, '.').Replace('\', '/')
    backupId = Split-Path -Leaf $backupDir
    before = @{ sha256 = $beforeHash; markerPresent = $false }
    after = @{ sha256 = $afterHash; markerPresent = $true }
    mutations = @{
      sqxStarted = $false
      filesWrittenToSqx = $true
      templateOnly = $true
      dataDbWritten = $false
      userProjectsWritten = $false
      databanksWritten = $false
      engineFilesWritten = $false
      jarFilesWritten = $false
      licenseFilesWritten = $false
    }
    blocked = @(
      'engine/binarios/jars',
      'license/activation/bypass',
      'data.db writes',
      'user/projects writes',
      'live databanks',
      'SQX runtime task execution',
      'MT5 direct import',
      'Migration Tool'
    )
    rollback = @{
      available = $true
      command = "tools\sqx142_internal_safe4_static_ui_registration.ps1 -Action rollback -BackupId $(Split-Path -Leaf $backupDir)"
    }
  }
  New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
  $evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $evidencePath -Encoding UTF8
  return $evidence
}

function Rollback-Registration {
  Assert-NoSqxProcess | Out-Null
  $backupDir = $BackupId
  if ([string]::IsNullOrWhiteSpace($backupDir)) {
    if (-not (Test-Path -LiteralPath $LatestBackupFile)) {
      throw "No BackupId supplied and no latest SAFE4 backup marker exists."
    }
    $backupDir = (Get-Content -LiteralPath $LatestBackupFile -Raw).Trim()
  } elseif (-not [System.IO.Path]::IsPathRooted($backupDir)) {
    $backupDir = Join-Path $BackupRoot $backupDir
  }
  $backupTemplate = Join-Path $backupDir 'templates.html'
  if (-not (Test-Path -LiteralPath $backupTemplate)) {
    throw "Backup template not found: $backupTemplate"
  }
  Assert-UnderPath -Child $backupTemplate -Parent $BackupRoot
  Assert-UnderPath -Child $TargetTemplate -Parent $SQXRoot
  Copy-Item -LiteralPath $backupTemplate -Destination $TargetTemplate -Force
  return [pscustomobject]@{
    phase = $Phase
    status = 'rolled_back_from_backup'
    targetRef = 'SQX142_ROOT/internal/web/common/templates.html'
    backupRef = $backupDir.Replace($RepoRoot, '.').Replace('\', '/')
    targetSha256 = Get-TemplateHash
    markerPresent = (Get-Content -LiteralPath $TargetTemplate -Raw).Contains($MarkerBegin)
  }
}

switch ($Action) {
  'install' { Install-Registration | ConvertTo-Json -Depth 8 }
  'rollback' { Rollback-Registration | ConvertTo-Json -Depth 8 }
  default { Get-TemplateStatus | ConvertTo-Json -Depth 8 }
}
