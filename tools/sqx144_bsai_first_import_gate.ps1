param(
  [Parameter(Position = 0)]
  [ValidateSet('status', 'plan', 'approval-template')]
  [string]$Action = 'status',

  [string]$CandidateId = 'BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005'
)

$ErrorActionPreference = 'Stop'

$Version = 'bs-ai8-first-import-gate-v1'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ConfigPath = Join-Path $RepoRoot 'backend\sqx-edge-tool\config.json'
$ManifestPath = Join-Path $RepoRoot 'backend\sqx-edge-tool\config\blocksettings_manifest.json'
$CandidateRoot = Join-Path $RepoRoot '.local\blocksettings_ai\candidates'
$OutputRoot = Join-Path $RepoRoot 'backend\sqx-edge-tool\output'
$PhaseDoc = Join-Path $RepoRoot 'docs\BS_AI7_PANEL_HARDENING.md'

function New-Result {
  param(
    [bool]$Ok,
    [string]$Status,
    [string[]]$Blockers = @(),
    [string[]]$Warnings = @(),
    [hashtable]$Extra = @{}
  )
  $payload = [ordered]@{
    ok = $Ok
    version = $Version
    action = $Action
    status = $Status
    candidateId = $CandidateId
    importAllowed = $false
    requiresOperatorApproval = $true
    writesSqxHost = $false
    writesDataDb = $false
    writesUserProjects = $false
    mutatesDatabanks = $false
    runsSqxTasks = $false
    privacy = @{
      localPathsReturned = $false
      tokensReturned = $false
      licenseMaterialReturned = $false
    }
    blockers = $Blockers
    warnings = $Warnings
  }
  foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
  return $payload
}

function Get-SqxProcesses {
  return @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -in @('StrategyQuantX', 'StrategyQuantX_nocheck', 'StrategyQuantX_ui', 'CodeEditor', 'sqcli', 'SQ.Client.CLI')
  })
}

function Test-ZipHasConfigXml {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $false }
  try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
    $zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
    try {
      return [bool]($zip.Entries | Where-Object { $_.FullName -eq 'config.xml' } | Select-Object -First 1)
    } finally {
      $zip.Dispose()
    }
  } catch {
    return $false
  }
}

function Get-HostProfile {
  if (-not (Test-Path -LiteralPath $ConfigPath)) {
    return @{ configured = $false; profile = '' }
  }
  try {
    $config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
    return @{
      configured = [bool]$config.sqx_path
      profile = [string]($config.sqx_host_profile)
    }
  } catch {
    return @{ configured = $false; profile = '' }
  }
}

function Get-CandidatePlan {
  $candidateMeta = Join-Path $CandidateRoot "$CandidateId.json"
  $candidateSqb = Join-Path $CandidateRoot "$CandidateId.sqb"
  $blockers = @()
  $warnings = @()
  $meta = $null
  if (-not (Test-Path -LiteralPath $candidateMeta)) { $blockers += 'candidate_metadata_missing' }
  if (-not (Test-Path -LiteralPath $candidateSqb)) { $blockers += 'candidate_sqb_missing' }
  if (Test-Path -LiteralPath $candidateMeta) {
    try { $meta = Get-Content -LiteralPath $candidateMeta -Raw | ConvertFrom-Json } catch { $blockers += 'candidate_metadata_invalid_json' }
  }

  $entry = if ($meta -and $meta.entry) { $meta.entry } else { $null }
  $recipe = if ($meta -and $meta.recipe) { $meta.recipe } else { $null }
  $asset = if ($recipe -and $recipe.asset) { [string]$recipe.asset } else { 'AUDCAD' }
  $timeframe = if ($recipe -and $recipe.timeframe) { [string]$recipe.timeframe } else { '' }
  $direction = if ($recipe -and $recipe.direction) { [string]$recipe.direction } else { 'long' }
  $side = if ($direction -eq 'short') { 'S' } elseif ($direction -eq 'both') { 'LS' } else { 'L' }
  $capa1Name = "BSAI_${asset}_${timeframe}_${CandidateId}_${side}_Capa1.cfx"
  $capa2Name = "BSAI_${asset}_${timeframe}_${CandidateId}_${side}_Capa2.cfx"
  $capa1Path = Join-Path $OutputRoot $capa1Name
  $capa2Path = Join-Path $OutputRoot $capa2Name

  if ($entry) {
    if ([string]$entry.canonicalId -ne $CandidateId) { $blockers += 'candidate_canonical_id_mismatch' }
    if ([string]$entry.sourceScope -ne 'local_candidate') { $blockers += 'candidate_not_local_scope' }
    if ([string]$entry.promotionState -ne 'local_candidate') { $blockers += 'candidate_not_local_candidate' }
    if (-not ([string]$entry.canonicalId).StartsWith('BSAI_')) { $blockers += 'candidate_namespace_invalid' }
    if (-not $entry.baseCanonicalId) { $blockers += 'candidate_base_missing' }
    if (-not $entry.baseSha256) { $blockers += 'candidate_base_sha_missing' }
  }

  if (-not (Test-ZipHasConfigXml -Path $candidateSqb)) { $blockers += 'candidate_sqb_not_zip_with_config_xml' }
  if (-not (Test-ZipHasConfigXml -Path $capa1Path)) { $blockers += 'capa1_cfx_not_zip_with_config_xml' }
  if (-not (Test-ZipHasConfigXml -Path $capa2Path)) { $blockers += 'capa2_cfx_not_zip_with_config_xml' }

  if (Test-Path -LiteralPath $ManifestPath) {
    try {
      $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
      $officialCollision = @($manifest.entries | Where-Object {
        $_.canonicalId -eq $CandidateId -or $_.filename -eq "$CandidateId.sqb"
      })
      if ($officialCollision.Count -gt 0) { $blockers += 'candidate_collides_with_official_manifest' }
    } catch {
      $warnings += 'official_manifest_unreadable'
    }
  } else {
    $warnings += 'official_manifest_missing'
  }

  if (Test-Path -LiteralPath $PhaseDoc) {
    $phaseText = Get-Content -LiteralPath $PhaseDoc -Raw
    if (-not $phaseText.Contains('operator_panel_hardening_smoke_confirmed_no_import')) {
      $blockers += 'bs_ai7_not_closed'
    }
  } else {
    $blockers += 'bs_ai7_doc_missing'
  }

  $hostInfo = Get-HostProfile
  if (-not $hostInfo.configured) { $blockers += 'sqx144_host_not_configured' }
  if ($hostInfo.profile -ne 'sqx144_full') { $warnings += 'host_profile_not_sqx144_full' }

  $processCount = (Get-SqxProcesses).Count
  if ($processCount -gt 0) { $warnings += 'sqx_process_running_no_automation' }

  $policy = if ($entry -and $entry.sourceVersionPolicy) { [string]$entry.sourceVersionPolicy } else { '' }
  $base = if ($entry -and $entry.baseCanonicalId) { [string]$entry.baseCanonicalId } else { '' }
  $approvalPhrase = "APRUEBO BS-AI8 IMPORT MANUAL CONTROLADA candidate=$CandidateId capa1=$capa1Name capa2=$capa2Name host=sqx144_full no_auto_import"

  return @{
    blockers = $blockers
    warnings = $warnings
    processCount = $processCount
    hostProfile = $hostInfo.profile
    asset = $asset
    timeframe = $timeframe
    direction = $direction
    side = $side
    candidate = @{
      id = $CandidateId
      filename = "$CandidateId.sqb"
      baseCanonicalId = $base
      sourceVersionPolicy = $policy
      promotionState = if ($entry) { [string]$entry.promotionState } else { '' }
      activeBlocks = if ($entry -and $entry.counts) { [int]$entry.counts.activeBlocks } else { 0 }
      activeIndicators = if ($entry -and $entry.counts) { [int]$entry.counts.activeIndicators } else { 0 }
    }
    files = @(
      @{ capa = 1; filename = $capa1Name; zipWithConfigXml = (Test-ZipHasConfigXml -Path $capa1Path) },
      @{ capa = 2; filename = $capa2Name; zipWithConfigXml = (Test-ZipHasConfigXml -Path $capa2Path) }
    )
    approvalPhrase = $approvalPhrase
  }
}

$plan = Get-CandidatePlan
$ok = ($plan.blockers.Count -eq 0)

if ($Action -eq 'status') {
  New-Result -Ok $ok -Status 'first_import_gate_status' -Blockers $plan.blockers -Warnings $plan.warnings -Extra @{
    hostProfile = $plan.hostProfile
    processCount = $plan.processCount
    candidate = $plan.candidate
    files = $plan.files
  } | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'plan') {
  New-Result -Ok $ok -Status 'approval_required_no_import' -Blockers $plan.blockers -Warnings $plan.warnings -Extra @{
    hostProfile = $plan.hostProfile
    processCount = $plan.processCount
    selectedManualImportScope = @{
      asset = $plan.asset
      timeframe = $plan.timeframe
      direction = $plan.direction
      side = $plan.side
      candidate = $plan.candidate
      files = $plan.files
    }
    checklist = @(
      'confirm_sqx144_full_host_only',
      'confirm_candidate_trace_and_policy_on_panel_or_docs',
      'download_or_select_exact_capa1_capa2_files_by_basename',
      'open_sqx_file_dialog_manually_only_after_operator_approval',
      'do_not_save_into_user_projects_until_post_import_review_gate',
      'do_not_run_backtest_retest_optimization_or_tasks',
      'capture_visual_evidence_without_local_paths_or_secrets'
    )
    approvalPhrase = $plan.approvalPhrase
  } | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq 'approval-template') {
  New-Result -Ok $ok -Status 'operator_approval_template_only' -Blockers $plan.blockers -Warnings $plan.warnings -Extra @{
    approvalPhrase = $plan.approvalPhrase
    nextGate = 'BS-AI9 manual import execution after explicit operator approval'
  } | ConvertTo-Json -Depth 8
  exit 0
}
