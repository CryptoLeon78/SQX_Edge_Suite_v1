from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core import sqx144_custom_results2_all_modules as custom_results2


SQX144_CUSTOM_RESULTS3_VERSION = "sqx144-custom-results3-optional-manual-install-gate-v1"
SQX144_CUSTOM_RESULTS3_PHASE = "SQX144-CUSTOM-RESULTS3"
SQX144_CUSTOM_RESULTS3_PHASE_LABEL = "SQX144-CUSTOM-RESULTS3 - Optional Manual Install Gate"
SQX144_CUSTOM_RESULTS3_STATUS = "custom_results3_optional_manual_install_gate_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
SQX144_CUSTOM_RESULTS3_INSTALL_STATUS = "custom_results3_all_modules_install_ready_apply_required_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
SQX144_CUSTOM_RESULTS3_INSTALLED_STATUS = "custom_results3_all_modules_manual_install_completed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
SQX144_CUSTOM_RESULTS3_ROLLBACK_STATUS = "custom_results3_all_modules_rollback_ready_apply_required_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
INSTALL_APPROVAL_PHRASE = "APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code"
ROLLBACK_APPROVAL_PHRASE = "APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL ROLLBACK host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback no_db_no_projects_no_databanks_no_tasks no_migration_tool"
EXPECTED_ROOT_NAME = "SQX_144_Full"
PLUGIN_NAME = "SQX Edge Custom Results All Modules"
SOURCE_PLUGIN_RELATIVE = Path("integrations") / "sqx144" / "results_plugins" / PLUGIN_NAME
TARGET_PLUGIN_REF = "sqx144_full/user/extend/ResultsPlugins/SQX Edge Custom Results All Modules"
EVIDENCE_DIR_PARTS = (".local", "sqx144_custom_results3")
SQX_PROCESS_NAMES = {
    "StrategyQuantX.exe",
    "StrategyQuantX_nocheck.exe",
    "StrategyQuantX_ui.exe",
    "SQUANT.exe",
    "sqcli.exe",
    "SQ.Client.CLI.exe",
    "CodeEditor.exe",
}


class CustomResults3Error(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _tool_config(project_root: Path) -> dict[str, Any]:
    config_path = project_root / "backend" / "sqx-edge-tool" / "config.json"
    if not config_path.is_file():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _resolve_sqx_root(project_root: Path, sqx_root: str | Path | None = None) -> Path | None:
    if sqx_root:
        return Path(sqx_root)
    env_root = os.environ.get("SQX144_ROOT")
    if env_root:
        return Path(env_root)
    configured = str(_tool_config(project_root).get("sqx_path") or "").strip()
    if configured:
        return Path(configured)
    fallback = Path("C:/BOTS/Versiones") / EXPECTED_ROOT_NAME
    if fallback.exists():
        return fallback
    return None


def _host_root_accepted(sqx_root: Path | None) -> bool:
    if sqx_root is None:
        return False
    resolved = sqx_root.resolve(strict=False)
    if resolved.name != EXPECTED_ROOT_NAME:
        return False
    return not re.search(r"144\.2953|SQX_144_2953|SQX144_FULL_UPDATE2", str(resolved), flags=re.IGNORECASE)


def _source_plugin_root(project_root: Path) -> Path:
    return project_root / SOURCE_PLUGIN_RELATIVE


def _results_plugins_root(sqx_root: Path | None) -> Path | None:
    if sqx_root is None:
        return None
    return sqx_root / "user" / "extend" / "ResultsPlugins"


def _target_plugin_root(sqx_root: Path | None) -> Path | None:
    root = _results_plugins_root(sqx_root)
    if root is None:
        return None
    return root / PLUGIN_NAME


def _backup_root(sqx_root: Path | None) -> Path | None:
    if sqx_root is None:
        return None
    return sqx_root / ".local_code_backups" / "sqx144_custom_results3"


def _is_relative_to(child: Path, parent: Path) -> bool:
    child_resolved = child.resolve(strict=False)
    parent_resolved = parent.resolve(strict=False)
    try:
        child_resolved.relative_to(parent_resolved)
        return True
    except ValueError:
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _file_manifest(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        rows.append({
            "relativePath": rel,
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        })
    return rows


def _manifest_map(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {str(row["relativePath"]): str(row["sha256"]) for row in rows}


def _required_plugin_files_state(plugin_root: Path) -> list[dict[str, Any]]:
    required = ["index.html", "fixtures/fixtures.js", "README.md"]
    return [{"relativePath": item, "present": (plugin_root / item).is_file()} for item in required]


def _target_state(project_root: Path, sqx_root: Path | None) -> dict[str, Any]:
    source_root = _source_plugin_root(project_root)
    target_root = _target_plugin_root(sqx_root)
    source_manifest = _file_manifest(source_root)
    target_manifest = _file_manifest(target_root) if target_root and target_root.is_dir() else []
    target_index = target_root / "index.html" if target_root else None
    target_marker_present = False
    if target_index and target_index.is_file():
        try:
            target_marker_present = SQX144_CUSTOM_RESULTS3_VERSION in target_index.read_text(encoding="utf-8", errors="ignore") or custom_results2.SQX144_CUSTOM_RESULTS2_VERSION in target_index.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            target_marker_present = False
    return {
        "sourcePluginRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
        "targetPluginRef": TARGET_PLUGIN_REF,
        "sourcePresent": source_root.is_dir(),
        "targetPresent": bool(target_root and target_root.is_dir()),
        "targetOwnedBySqxEdge": target_marker_present,
        "sourceFileCount": len(source_manifest),
        "targetFileCount": len(target_manifest),
        "sourceSha256": _combined_manifest_hash(source_manifest),
        "targetSha256": _combined_manifest_hash(target_manifest) if target_manifest else None,
        "targetMatchesSource": bool(target_manifest) and _manifest_map(source_manifest) == _manifest_map(target_manifest),
        "requiredFiles": _required_plugin_files_state(source_root),
    }


def _combined_manifest_hash(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None
    digest = hashlib.sha256()
    for row in rows:
        digest.update(str(row["relativePath"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(row["sha256"]).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest().upper()


def _detect_sqx_processes() -> dict[str, Any]:
    command = r"""
$items = @(Get-CimInstance Win32_Process | Where-Object {
  $name = $_.Name
  $cmd = [string]$_.CommandLine
  $sqxNames = @('StrategyQuantX.exe','StrategyQuantX_nocheck.exe','StrategyQuantX_ui.exe','SQUANT.exe','sqcli.exe','SQ.Client.CLI.exe','CodeEditor.exe')
  ($sqxNames -contains $name) -or ($name -eq 'java.exe' -and $cmd -match 'StrategyQuant|SQX_144|SQUANT')
} | Select-Object ProcessId,Name)
ConvertTo-Json -InputObject $items -Depth 3
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=6,
            check=False,
        )
    except Exception:
        return {"known": False, "processCount": None, "processNames": []}
    if result.returncode != 0:
        return {"known": False, "processCount": None, "processNames": []}
    raw = (result.stdout or "").strip()
    if not raw:
        return {"known": True, "processCount": 0, "processNames": []}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"known": False, "processCount": None, "processNames": []}
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return {"known": False, "processCount": None, "processNames": []}
    names = sorted({str(item.get("Name") or "") for item in data if isinstance(item, dict) and item.get("Name")})
    return {"known": True, "processCount": len(data), "processNames": names}


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_CUSTOM_RESULTS3_VERSION,
        "phase": SQX144_CUSTOM_RESULTS3_PHASE,
        "phaseLabel": SQX144_CUSTOM_RESULTS3_PHASE_LABEL,
        "status": SQX144_CUSTOM_RESULTS3_STATUS,
        "action": action,
        "hostProfile": "sqx144_full",
        "pluginName": PLUGIN_NAME,
        "installExecuted": False,
        "rollbackExecuted": False,
        "dryRun": True,
        "sourcePluginRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
        "targetPluginRef": TARGET_PLUGIN_REF,
        "downloadedPluginsInstalled": False,
        "copiesDownloadedThirdPartyPlugins": False,
        "copiesSqxEdgeOwnedBundleOnly": True,
        "requiresSqxClosed": True,
        "manualResultsTabConfirmationRequired": True,
        "getOrdersPolicy": "GET_ORDERS remains privacy/performance-gated and requires this exact manual install gate plus operator Results-tab action",
        "ordersResponsePolicy": "ORDERS_RESPONSE may be received by the installed Results panel only after exact approval; repo tooling keeps rawOrdersReturned=false",
        "guards": {
            "writesSqxHost": False,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "runsSqxTasks": False,
            "launchesSqxRuntime": False,
            "usesMigrationTool": False,
            "usesMcpCalls": False,
            "usesPluginCreateRenameDelete": False,
            "usesGetSourceCode": False,
            "directDbWriteAllowed": False,
            "thirdPartyZipDirectInstallAllowed": False,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawOrdersReturned": False,
            "rawOrdersReturnedByTooling": False,
            "rawStrategyNamesReturned": False,
            "sourceCodeReturned": False,
            "tokensReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def status_payload(project_root: str | Path = ".", sqx_root: str | Path | None = None) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    payload = _base_payload("status")
    target = _target_state(root, resolved_sqx_root)
    currently_installed = bool(target["targetMatchesSource"])
    module_status = custom_results2.status_payload(root)
    payload.update({
        "ok": True,
        "actions": ["status", "preflight", "plan", "install", "rollback", "approval-template", "report"],
        "status": SQX144_CUSTOM_RESULTS3_INSTALLED_STATUS if currently_installed else SQX144_CUSTOM_RESULTS3_STATUS,
        "installExecuted": currently_installed,
        "currentlyInstalled": currently_installed,
        "hostRootAccepted": _host_root_accepted(resolved_sqx_root),
        "expectedRootName": EXPECTED_ROOT_NAME,
        "resultsPluginsRootPresent": bool(_results_plugins_root(resolved_sqx_root) and _results_plugins_root(resolved_sqx_root).is_dir()),
        "targetState": target,
        "sourceBundle": {
            "customResults2Version": module_status["version"],
            "status": module_status["status"],
            "allModules": [module["label"] for module in module_status["modules"]],
        },
        "approvalRequiredForInstall": True,
        "approvalRequiredForRollback": True,
        "approvalTemplates": approval_template_payload(root)["approvalTemplates"],
        "nextAction": "run preflight and plan; do not run install -Apply without exact operator approval",
    })
    return payload


def preflight_payload(project_root: str | Path = ".", sqx_root: str | Path | None = None) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    payload = _base_payload("preflight")
    blockers: list[str] = []
    warnings: list[str] = []

    source_root = _source_plugin_root(root)
    results_root = _results_plugins_root(resolved_sqx_root)
    target_root = _target_plugin_root(resolved_sqx_root)
    target = _target_state(root, resolved_sqx_root)
    process_state = _detect_sqx_processes()
    module_smoke = custom_results2.module_smoke_payload(root)

    if not source_root.is_dir():
        blockers.append("source_plugin_missing")
    if not module_smoke.get("ok"):
        blockers.append("custom_results2_module_smoke_failed")
    missing_required = [item["relativePath"] for item in target["requiredFiles"] if not item["present"]]
    if missing_required:
        blockers.append("source_plugin_required_files_missing")
    if resolved_sqx_root is None:
        blockers.append("sqx144_root_not_configured")
    elif not _host_root_accepted(resolved_sqx_root):
        blockers.append("sqx144_full_root_mismatch")
    if results_root is None or not results_root.is_dir():
        blockers.append("results_plugins_root_missing")
    if process_state.get("known") is not True:
        blockers.append("sqx_process_state_unknown")
    elif int(process_state.get("processCount") or 0) > 0:
        blockers.append("sqx_or_java_process_running")
    if target_root and target_root.is_dir() and not target["targetOwnedBySqxEdge"]:
        blockers.append("target_plugin_exists_without_sqx_edge_marker")
    if target["targetPresent"] and target["targetOwnedBySqxEdge"] and not target["targetMatchesSource"]:
        warnings.append("target_plugin_differs_backup_required")
    if target["targetMatchesSource"]:
        warnings.append("target_plugin_already_matches_source")

    ok = not blockers
    payload.update({
        "ok": ok,
        "status": "custom_results3_preflight_ready_no_install" if ok else "custom_results3_preflight_blocked_no_install",
        "blockers": blockers,
        "warnings": warnings,
        "hostRootAccepted": _host_root_accepted(resolved_sqx_root),
        "expectedRootName": EXPECTED_ROOT_NAME,
        "resultsPluginsRootPresent": bool(results_root and results_root.is_dir()),
        "processState": process_state,
        "moduleSmoke": {
            "ok": bool(module_smoke.get("ok")),
            "status": module_smoke.get("status"),
            "pluginRef": module_smoke.get("pluginRef"),
            "forbiddenMarkers": module_smoke.get("forbiddenMarkers"),
            "missingRequiredMarkers": module_smoke.get("missingRequiredMarkers"),
        },
        "targetState": target,
    })
    return payload


def plan_payload(project_root: str | Path = ".", sqx_root: str | Path | None = None) -> dict[str, Any]:
    root = _project_root(project_root)
    preflight = preflight_payload(root, sqx_root=sqx_root)
    payload = _base_payload("plan")
    source_manifest = _file_manifest(_source_plugin_root(root))
    payload.update({
        "ok": bool(preflight.get("ok")),
        "status": "custom_results3_install_plan_ready_no_apply" if preflight.get("ok") else "custom_results3_install_plan_blocked_no_apply",
        "preflight": preflight,
        "fileManifest": source_manifest,
        "fileCount": len(source_manifest),
        "installRequiresExactApproval": INSTALL_APPROVAL_PHRASE,
        "rollbackRequiresExactApproval": ROLLBACK_APPROVAL_PHRASE,
        "plannedCopy": {
            "fromRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
            "toRef": TARGET_PLUGIN_REF,
            "backupIfTargetPresent": True,
            "copyOnlySqxEdgeOwnedBundle": True,
            "copyDownloadedThirdPartyPlugins": False,
            "getOrdersRuntimeAcknowledgementRequired": True,
        },
        "postInstallManualSteps": [
            "Restart SQX144 Full or use the Results tab reload icon.",
            "Open a strategy/backtest in a databank.",
            "Go to Results and select SQX Edge Custom Results All Modules.",
            "Confirm no project run, no databank mutation and no Migration Tool.",
        ],
    })
    return payload


def approval_template_payload(project_root: str | Path = ".") -> dict[str, Any]:
    payload = _base_payload("approval-template")
    payload.update({
        "ok": True,
        "status": "custom_results3_approval_templates_ready",
        "approvalTemplates": {
            "install": INSTALL_APPROVAL_PHRASE,
            "rollback": ROLLBACK_APPROVAL_PHRASE,
        },
        "approvalNotes": [
            "Install copies only the SQX Edge-owned all-modules Results Plugin folder.",
            "Downloaded third-party ZIPs remain not installed directly.",
            "SQX must be closed and preflight must be clean before apply.",
            "The all-modules panel can request historical order data through GET_ORDERS only after this exact gate and manual Results-tab use.",
        ],
    })
    return payload


def _require_install_approval(approval: str | None) -> None:
    if str(approval or "").strip() != INSTALL_APPROVAL_PHRASE:
        raise CustomResults3Error("custom_results3_install_requires_exact_approval")


def _require_rollback_approval(approval: str | None) -> None:
    if str(approval or "").strip() != ROLLBACK_APPROVAL_PHRASE:
        raise CustomResults3Error("custom_results3_rollback_requires_exact_approval")


def _assert_safe_install_paths(project_root: Path, sqx_root: Path | None) -> tuple[Path, Path, Path]:
    if sqx_root is None or not _host_root_accepted(sqx_root):
        raise CustomResults3Error("sqx144_full_root_mismatch")
    source_root = _source_plugin_root(project_root)
    results_root = _results_plugins_root(sqx_root)
    target_root = _target_plugin_root(sqx_root)
    if results_root is None or target_root is None:
        raise CustomResults3Error("results_plugins_root_missing")
    if not _is_relative_to(target_root, results_root):
        raise CustomResults3Error("target_plugin_path_outside_results_plugins")
    if not source_root.is_dir():
        raise CustomResults3Error("source_plugin_missing")
    return source_root, results_root, target_root


def install_payload(
    project_root: str | Path = ".",
    *,
    sqx_root: str | Path | None = None,
    approval: str | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    preflight = preflight_payload(root, sqx_root=resolved_sqx_root)
    payload = _base_payload("install")
    payload.update({
        "ok": bool(preflight.get("ok")),
        "status": SQX144_CUSTOM_RESULTS3_INSTALL_STATUS if preflight.get("ok") else "custom_results3_install_blocked_no_apply",
        "dryRun": not apply,
        "preflight": preflight,
        "installRequiresExactApproval": INSTALL_APPROVAL_PHRASE,
        "wouldWriteSqxHost": bool(preflight.get("ok")),
        "installExecuted": False,
    })
    if not apply:
        return payload

    _require_install_approval(approval)
    if not preflight.get("ok"):
        raise CustomResults3Error("custom_results3_install_preflight_blocked", details={"blockers": preflight.get("blockers", [])})

    source_root, _results_root, target_root = _assert_safe_install_paths(root, resolved_sqx_root)
    backup_id = None
    backup_created = False
    if target_root.exists():
        backup_id = f"custom_results3_install_{_utc_stamp()}"
        backup_target = _backup_root(resolved_sqx_root) / backup_id / PLUGIN_NAME  # type: ignore[operator]
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(target_root, backup_target)
        shutil.rmtree(target_root)
        backup_created = True
    shutil.copytree(source_root, target_root)
    installed_manifest = _file_manifest(target_root)
    payload.update({
        "ok": True,
        "status": SQX144_CUSTOM_RESULTS3_INSTALLED_STATUS,
        "dryRun": False,
        "installExecuted": True,
        "backupCreated": backup_created,
        "backupId": backup_id,
        "copiedFiles": len(installed_manifest),
        "installedSha256": _combined_manifest_hash(installed_manifest),
        "guards": {**payload["guards"], "writesSqxHost": True},
    })
    return payload


def rollback_payload(
    project_root: str | Path = ".",
    *,
    sqx_root: str | Path | None = None,
    backup_id: str | None = None,
    approval: str | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    preflight = preflight_payload(root, sqx_root=resolved_sqx_root)
    payload = _base_payload("rollback")
    backup_id_clean = re.sub(r"[^A-Za-z0-9_-]+", "", str(backup_id or ""))
    backup_source = _backup_root(resolved_sqx_root) / backup_id_clean / PLUGIN_NAME if resolved_sqx_root and backup_id_clean else None  # type: ignore[operator]
    backup_present = bool(backup_source and backup_source.is_dir())
    blockers = list(preflight.get("blockers") or [])
    if not backup_id_clean:
        blockers.append("backup_id_required")
    elif not backup_present:
        blockers.append("backup_not_found")
    ok = not blockers
    payload.update({
        "ok": ok,
        "status": SQX144_CUSTOM_RESULTS3_ROLLBACK_STATUS if ok else "custom_results3_rollback_blocked_no_apply",
        "dryRun": not apply,
        "preflight": preflight,
        "backupId": backup_id_clean or None,
        "backupPresent": backup_present,
        "blockers": blockers,
        "rollbackRequiresExactApproval": ROLLBACK_APPROVAL_PHRASE,
    })
    if not apply:
        return payload

    _require_rollback_approval(approval)
    if not ok:
        raise CustomResults3Error("custom_results3_rollback_preflight_blocked", details={"blockers": blockers})
    _source_root, results_root, target_root = _assert_safe_install_paths(root, resolved_sqx_root)
    if backup_source is None or not _is_relative_to(backup_source, _backup_root(resolved_sqx_root)):  # type: ignore[arg-type]
        raise CustomResults3Error("backup_path_outside_backup_root")
    if target_root.exists():
        shutil.rmtree(target_root)
    shutil.copytree(backup_source, target_root)
    restored_manifest = _file_manifest(target_root)
    payload.update({
        "ok": True,
        "status": "custom_results3_all_modules_rollback_completed_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool",
        "dryRun": False,
        "rollbackExecuted": True,
        "restoredFiles": len(restored_manifest),
        "restoredSha256": _combined_manifest_hash(restored_manifest),
        "guards": {**payload["guards"], "writesSqxHost": True},
    })
    return payload


def report_payload(project_root: str | Path = ".", sqx_root: str | Path | None = None, write_evidence: bool = False) -> dict[str, Any]:
    root = _project_root(project_root)
    preflight = preflight_payload(root, sqx_root=sqx_root)
    plan = plan_payload(root, sqx_root=sqx_root)
    payload = _base_payload("report")
    payload.update({
        "ok": bool(preflight.get("ok")),
        "status": "custom_results3_install_gate_report_ready_no_apply" if preflight.get("ok") else "custom_results3_install_gate_report_blocked_no_apply",
        "preflight": preflight,
        "plan": {
            "ok": plan.get("ok"),
            "status": plan.get("status"),
            "fileCount": plan.get("fileCount"),
            "plannedCopy": plan.get("plannedCopy"),
        },
        "installExecuted": False,
        "rollbackExecuted": False,
        "evidenceWritten": False,
    })
    if write_evidence:
        evidence_dir = root.joinpath(*EVIDENCE_DIR_PARTS)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence_ref = f"sqx144_custom_results3_report_{_utc_stamp()}.json"
        (evidence_dir / evidence_ref).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = evidence_ref
    return payload


def error_payload(action: str, exc: Exception) -> dict[str, Any]:
    payload = _base_payload(action)
    code = exc.code if isinstance(exc, CustomResults3Error) else "custom_results3_unhandled_error"
    payload.update({
        "ok": False,
        "status": code,
        "error": code,
        "details": exc.details if isinstance(exc, CustomResults3Error) else {},
    })
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 CUSTOM-RESULTS3 all modules install gate")
    parser.add_argument("action", choices=("status", "preflight", "plan", "install", "rollback", "approval-template", "report"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--sqx-root", default=None)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--backup-id", default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root, sqx_root=args.sqx_root)
        elif args.action == "preflight":
            payload = preflight_payload(args.project_root, sqx_root=args.sqx_root)
        elif args.action == "plan":
            payload = plan_payload(args.project_root, sqx_root=args.sqx_root)
        elif args.action == "install":
            payload = install_payload(args.project_root, sqx_root=args.sqx_root, approval=args.approval, apply=args.apply)
        elif args.action == "rollback":
            payload = rollback_payload(args.project_root, sqx_root=args.sqx_root, backup_id=args.backup_id, approval=args.approval, apply=args.apply)
        elif args.action == "approval-template":
            payload = approval_template_payload(args.project_root)
        else:
            payload = report_payload(args.project_root, sqx_root=args.sqx_root, write_evidence=args.write_evidence)
    except Exception as exc:
        payload = error_payload(args.action, exc)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
