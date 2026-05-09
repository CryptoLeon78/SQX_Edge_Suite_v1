param(
  [switch]$SkipTests,
  [switch]$SkipPackage,
  [switch]$RequireCleanGit,
  [int]$PortableApiPort = 5059
)

$ErrorActionPreference = "Stop"

$ToolRoot = Split-Path -Parent $PSScriptRoot
$BackendRoot = Split-Path -Parent $ToolRoot
$ProjectRoot = Split-Path -Parent $BackendRoot
$PythonExe = Join-Path $ToolRoot "venv\Scripts\python.exe"
$EmbeddedPythonExe = Join-Path $ToolRoot "runtime\python\python.exe"
$PackageScript = Join-Path $PSScriptRoot "package_portable.ps1"
$DistributionAuditScript = Join-Path $PSScriptRoot "audit_distribution.ps1"
$SummaryPath = Join-Path (Join-Path $ProjectRoot "dist") "SQX_release_summary.txt"

function Write-Step {
  param([string]$Message)
  Write-Host ""
  Write-Host "== $Message =="
}

function Invoke-Checked {
  param(
    [Parameter(Mandatory=$true)][string]$Label,
    [Parameter(Mandatory=$true)][scriptblock]$Command
  )
  Write-Step $Label
  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE"
  }
}

function Assert-File {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Required file missing: $Path"
  }
}

function Assert-DirExcluded {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path) {
    throw "Path should not be present in portable package: $Path"
  }
}

function Get-GitStatusText {
  return (git status --short --branch | Out-String).Trim()
}

function Assert-CleanGit {
  $StatusLines = @(git status --porcelain)
  if ($StatusLines.Count -gt 0) {
    Write-Host "Git working tree is not clean:"
    git status --short
    throw "Commit or stash local changes before running a strict release checklist."
  }
}

function Test-PortableZip {
  param([string]$ZipPath)

  Write-Step "Validate portable ZIP"
  $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $TempRoot = Join-Path $env:TEMP "SQX_release_check_$Stamp"
  New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null

  try {
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $TempRoot -Force

    Assert-File (Join-Path $TempRoot "START_SQX_EDGE.bat")
    Assert-File (Join-Path $TempRoot "STOP_SQX_EDGE.bat")
    Assert-File (Join-Path $TempRoot "packaging\START_SQX_EDGE.bat")
    Assert-File (Join-Path $TempRoot "app\SQX_Dashboard_v6.html")
    Assert-File (Join-Path $TempRoot "app\js\project-generator-main.js")
    Assert-File (Join-Path $TempRoot "app\js\modules\project-generator-dom.js")
    Assert-File (Join-Path $TempRoot "backend\sqx-edge-tool\run-web-embedded.bat")
    Assert-File (Join-Path $TempRoot "backend\sqx-edge-tool\runtime\python\python.exe")

    Assert-DirExcluded (Join-Path $TempRoot "backups")
    Assert-DirExcluded (Join-Path $TempRoot "dist")
    Assert-DirExcluded (Join-Path $TempRoot "node_modules")
    Assert-DirExcluded (Join-Path $TempRoot "RELEASE_SQX_EDGE.bat")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\license_signer.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\license_keypair.ps1")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\license_issue.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\prepare_customer_delivery.ps1")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\checkout_live_readiness.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\commercial_release_candidate.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\pilot_purchase_kit.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\limited_public_launch.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\post_launch_control.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\commercial_feedback_loop.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\public_offer_pack.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\launch_assets_kit.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\public_release_gate.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\release_publication_record.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\post_release_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\hotfix_rollback_release.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\customer_success_renewal.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\pro_buyer_pack.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\buyer_onboarding_support_gate.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_delivery.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_offer.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_publication.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_purchase_drill.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_handoff.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_sales_register.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_feedback_cohort.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_1_action_plan.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_specs.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_assets.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_offer_pack.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_publication.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_purchase_drill.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_handoff.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_sales_register.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\template_pack_2_feedback_cohort.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\buyer_ready_checkout_closeout.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\public_buyer_page_cadence.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\first_controlled_buyer_log.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\post_sale_improvement_loop.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\post_sale_micro_updates.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\next_controlled_buyer_readiness.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\next_controlled_buyer_outcome.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_distribution_step.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_distribution_review.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\next_buyer_facing_asset.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\private_asset_review.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_publication_gate.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\limited_publication_draft.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\operator_publication_review.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\manual_limited_publication_record.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\manual_publication_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_traffic_expansion_review.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_traffic_expansion_step.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_traffic_expansion_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_traffic_expansion_decision.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_traffic_expansion_execution.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_traffic_expansion_execution_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_commercial_next_movement.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_commercial_next_movement_execution.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\controlled_commercial_next_movement_execution_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\next_controlled_commercial_movement_decision.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\approved_controlled_commercial_movement_execution.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\approved_controlled_commercial_movement_execution_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\next_controlled_commercial_movement_from_m92_decision.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\approved_controlled_commercial_movement_from_m93_execution.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\approved_controlled_commercial_movement_from_m93_execution_monitor.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\next_controlled_commercial_movement_from_m95_decision.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\private_commercial_split.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\fulfillment_request.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\fulfill_from_request.ps1")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\relay_bundle.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\dukas_mt5_ohlc_download.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\tools\mt5_ipc_diagnostic.py")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\config\dukas_mt5_download.json")
    Assert-DirExcluded (Join-Path $TempRoot "data\ohlc")
    Assert-DirExcluded (Join-Path $TempRoot "analysis_output")
    Assert-DirExcluded (Join-Path $TempRoot "analysis_output\dukas_mt5_download")
    Assert-DirExcluded (Join-Path $TempRoot "analysis_output\mt5_ipc_diagnostic")
    Assert-DirExcluded (Join-Path $TempRoot "analysis_output\real_mtf_pipeline_run")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-relay")
    Assert-DirExcluded (Join-Path $TempRoot "license_keys")
    Assert-DirExcluded (Join-Path $TempRoot "private_keys")
    Assert-DirExcluded (Join-Path $TempRoot "licenses_private")
    Assert-DirExcluded (Join-Path $TempRoot "fulfillment_requests")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\customer_success_renewal")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\customer_cockpit")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\pro_buyer_pack")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\buyer_onboarding_support_gate")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_delivery")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_offer")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_publication")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_purchase_drill")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_handoff")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_sales_register")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_feedback_cohort")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_1_action_plan")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_specs")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_assets")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_offer_pack")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_publication")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_purchase_drill")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_handoff")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_sales_register")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\template_pack_2_feedback_cohort")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\buyer_ready_checkout_closeout")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\public_buyer_page_cadence")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\first_controlled_buyer_log")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\post_sale_improvement_loop")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\post_sale_micro_updates")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\next_controlled_buyer_readiness")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\next_controlled_buyer_outcome")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_distribution_step")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_distribution_review")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\next_buyer_facing_asset")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\private_asset_review")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_publication_gate")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\limited_publication_draft")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\operator_publication_review")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\manual_limited_publication_record")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\manual_publication_monitor")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_traffic_expansion_review")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_traffic_expansion_step")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_traffic_expansion_monitor")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_traffic_expansion_decision")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_traffic_expansion_execution")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_traffic_expansion_execution_monitor")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_commercial_next_movement")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_commercial_next_movement_execution")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\controlled_commercial_next_movement_execution_monitor")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\next_controlled_commercial_movement_decision")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\approved_controlled_commercial_movement_execution")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\approved_controlled_commercial_movement_execution_monitor")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\next_controlled_commercial_movement_from_m92_decision")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\approved_controlled_commercial_movement_from_m93_execution")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\approved_controlled_commercial_movement_from_m93_execution_monitor")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\data\next_controlled_commercial_movement_from_m95_decision")
    Assert-DirExcluded (Join-Path $TempRoot "docs\private-commercial")
    Assert-DirExcluded (Join-Path $TempRoot "commercial-private")
    Assert-DirExcluded (Join-Path $TempRoot "private-commercial")
    Assert-DirExcluded (Join-Path $TempRoot "resources\pro-template-pack-1")
    Assert-DirExcluded (Join-Path $TempRoot "resources\pro-template-pack-2")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\venv")
    Assert-DirExcluded (Join-Path $TempRoot "backend\sqx-edge-tool\config.json")

    $PortableTool = Join-Path $TempRoot "backend\sqx-edge-tool"
    $PortablePython = Join-Path $PortableTool "runtime\python\python.exe"
    & $PortablePython -c "import flask; import api.server; print('portable imports ok')"
    if ($LASTEXITCODE -ne 0) { throw "Portable import check failed" }

    $Process = Start-Process -FilePath $PortablePython -ArgumentList @("-m", "api.server", "--port", "$PortableApiPort") -WorkingDirectory $PortableTool -WindowStyle Hidden -PassThru
    try {
      $Ok = $false
      for ($i = 0; $i -lt 30; $i++) {
        try {
          $Response = Invoke-RestMethod -Uri "http://127.0.0.1:$PortableApiPort/api/health" -TimeoutSec 1
          if ($Response.ok) { $Ok = $true; break }
        } catch {}
        Start-Sleep -Milliseconds 500
      }
      if (-not $Ok) {
        throw "Portable API did not answer /api/health on port $PortableApiPort"
      }
      Write-Host "Portable API health OK: version $($Response.version)"
    } finally {
      if ($Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force
        Wait-Process -Id $Process.Id -Timeout 10 -ErrorAction SilentlyContinue
      }
    }
  } finally {
    $ResolvedTemp = Resolve-Path -LiteralPath $TempRoot -ErrorAction SilentlyContinue
    if ($ResolvedTemp) {
      $TempBase = [System.IO.Path]::GetFullPath($env:TEMP)
      $Target = [System.IO.Path]::GetFullPath($ResolvedTemp.Path)
      if ($Target.StartsWith($TempBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $Target -Recurse -Force
      } else {
        throw "Refusing to remove outside TEMP: $Target"
      }
    }
  }
}

Write-Host ""
Write-Host "SQX Edge Suite - Release Checklist"
Write-Host "Project: $ProjectRoot"

Assert-File $PackageScript
Assert-File $DistributionAuditScript
Assert-File $EmbeddedPythonExe

Push-Location $ProjectRoot
try {
  if ($RequireCleanGit) {
    Invoke-Checked "Clean Git working tree" { Assert-CleanGit }
  }

  if (-not $SkipTests) {
    Assert-File $PythonExe
    Invoke-Checked "Frontend module contracts" { node ".\tests\js\module_contracts.mjs" }
    Invoke-Checked "Python test suite" { & $PythonExe -m pytest }
    Invoke-Checked "Git diff check" { git diff --check }
  }

  if (-not $SkipPackage) {
    Invoke-Checked "Build portable ZIP" {
      powershell -NoProfile -ExecutionPolicy Bypass -File $PackageScript -RequireEmbeddedPython
    }
    $Zip = Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "dist") -Filter "SQX_Edge_Tool_Portable_*.zip" |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
    if (-not $Zip) { throw "Portable ZIP was not created in dist" }
    Invoke-Checked "Distribution audit" {
      powershell -NoProfile -ExecutionPolicy Bypass -File $DistributionAuditScript -ZipPath $Zip.FullName
    }
    Test-PortableZip -ZipPath $Zip.FullName
    Write-Host ""
    Write-Host "Release ZIP ready:"
    Write-Host "  $($Zip.FullName)"
  }

  Write-Step "Git status"
  $GitStatus = Get-GitStatusText
  Write-Host $GitStatus

  if (-not $SkipPackage -and $Zip) {
    $ZipItem = Get-Item -LiteralPath $Zip.FullName
    $ZipHash = Get-FileHash -Algorithm SHA256 -LiteralPath $Zip.FullName
    $Summary = @(
      "SQX Edge Suite - Release Summary",
      "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
      "ZIP: $($ZipItem.FullName)",
      "ZIP bytes: $($ZipItem.Length)",
      "ZIP SHA256: $($ZipHash.Hash)",
      "Portable API port tested: $PortableApiPort",
      "",
      "Git status:",
      $GitStatus
    )
    New-Item -ItemType Directory -Path (Split-Path -Parent $SummaryPath) -Force | Out-Null
    Set-Content -LiteralPath $SummaryPath -Value $Summary -Encoding ASCII
    Write-Host ""
    Write-Host "Release summary:"
    Write-Host "  $SummaryPath"
  }

  Write-Host ""
  Write-Host "Release checklist completed."
} finally {
  Pop-Location
}
