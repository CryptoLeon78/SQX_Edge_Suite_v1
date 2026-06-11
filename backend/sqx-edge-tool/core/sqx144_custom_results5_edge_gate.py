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


SQX144_CUSTOM_RESULTS5_VERSION = "sqx144-custom-results5-edge-gate-v1"
SQX144_CUSTOM_RESULTS5_PHASE = "SQX144-CUSTOM-RESULTS5"
SQX144_CUSTOM_RESULTS5_PHASE_LABEL = "SQX144-CUSTOM-RESULTS5 - SQX Edge Gate"
SQX144_CUSTOM_RESULTS5_STATUS = "custom_results5_edge_gate_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
SQX144_CUSTOM_RESULTS5_SMOKE_STATUS = "custom_results5_edge_gate_smoke_passed_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
SQX144_CUSTOM_RESULTS5_INSTALL_STATUS = "custom_results5_edge_gate_install_ready_apply_required_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
SQX144_CUSTOM_RESULTS5_INSTALLED_STATUS = "custom_results5_edge_gate_installed_copy_only_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
INSTALL_APPROVAL_PHRASE = "APRUEBO SQX144 CUSTOM RESULTS5 EDGE GATE INSTALL host=sqx144_full plugin=sqx_edge_gate sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_optin_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_source_code"
EXPECTED_ROOT_NAME = "SQX_144_Full"
PLUGIN_NAME = "SQX Edge Gate"
SOURCE_PLUGIN_RELATIVE = Path("integrations") / "sqx144" / "results_plugins" / PLUGIN_NAME
TARGET_PLUGIN_REF = "sqx144_full/user/extend/ResultsPlugins/SQX Edge Gate"
EVIDENCE_DIR_PARTS = (".local", "sqx144_custom_results5")

RUNTIME_FILES = (
    "index.html",
    "edge-gate.js",
    "fixtures/fixtures.js",
)
EXPECTED_FILES = RUNTIME_FILES + (
    "locales/en.json",
    "locales/es.json",
    "README.md",
)
FORBIDDEN_RUNTIME_MARKERS = (
    "GET_SOURCE_CODE",
    "resultsPlugins/create",
    "resultsPlugins/rename",
    "resultsPlugins/delete",
    "localStorage",
    "sessionStorage",
    "indexedDB",
    "fetch(",
    "run_project",
    "stop_project",
)
REQUIRED_RUNTIME_MARKERS = (
    "SQX_EDGE_GATE_VERSION",
    "sqx144-custom-results5-edge-gate-v1",
    "window.__SQX_EDGE_GATE__",
    "STRATEGY_DATA",
    "GET_STATS",
    "STATS_RESPONSE",
    "GET_ORDERS",
    "ORDERS_RESPONSE",
    "Activar Order Radar",
    "NumberOfTrades",
    "ProfitFactor",
    "ReturnDDRatio",
    "RExpectancy",
    "NetProfit",
    "PASS",
    "REVIEW",
    "BLOCK",
)


class CustomResults5Error(RuntimeError):
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
    return sqx_root / ".local_code_backups" / "sqx144_custom_results5"


def _evidence_root(project_root: Path) -> Path:
    return project_root.joinpath(*EVIDENCE_DIR_PARTS)


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
        rows.append({
            "relativePath": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        })
    return rows


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


def _manifest_map(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {str(row["relativePath"]): str(row["sha256"]) for row in rows}


def _read_runtime_text(source_root: Path) -> str:
    chunks: list[str] = []
    for relative in RUNTIME_FILES:
        path = source_root / relative
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def _target_owned_by_sqx_edge(target_root: Path | None) -> bool:
    if target_root is None or not target_root.is_dir():
        return False
    for relative in ("index.html", "edge-gate.js", "README.md"):
        path = target_root / relative
        if path.is_file() and SQX144_CUSTOM_RESULTS5_VERSION in path.read_text(encoding="utf-8", errors="ignore"):
            return True
    return False


def _target_state(project_root: Path, sqx_root: Path | None) -> dict[str, Any]:
    source_root = _source_plugin_root(project_root)
    target_root = _target_plugin_root(sqx_root)
    source_manifest = _file_manifest(source_root)
    target_manifest = _file_manifest(target_root) if target_root and target_root.is_dir() else []
    return {
        "sourcePluginRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
        "targetPluginRef": TARGET_PLUGIN_REF,
        "sourcePresent": source_root.is_dir(),
        "targetPresent": bool(target_root and target_root.is_dir()),
        "targetOwnedBySqxEdge": _target_owned_by_sqx_edge(target_root),
        "sourceFileCount": len(source_manifest),
        "targetFileCount": len(target_manifest),
        "sourceSha256": _combined_manifest_hash(source_manifest),
        "targetSha256": _combined_manifest_hash(target_manifest) if target_manifest else None,
        "targetMatchesSource": bool(target_manifest) and _manifest_map(source_manifest) == _manifest_map(target_manifest),
        "expectedFiles": [{"relativePath": item, "present": (source_root / item).is_file()} for item in EXPECTED_FILES],
    }


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
        "version": SQX144_CUSTOM_RESULTS5_VERSION,
        "phase": SQX144_CUSTOM_RESULTS5_PHASE,
        "phaseLabel": SQX144_CUSTOM_RESULTS5_PHASE_LABEL,
        "status": SQX144_CUSTOM_RESULTS5_STATUS,
        "action": action,
        "hostProfile": "sqx144_full",
        "pluginName": PLUGIN_NAME,
        "sourcePluginRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
        "targetPluginRef": TARGET_PLUGIN_REF,
        "installExecuted": False,
        "dryRun": True,
        "ordersPolicy": "GET_ORDERS is opt-in only after operator presses Activar Order Radar",
        "approvalRequiredForInstall": True,
        "approvalTemplate": INSTALL_APPROVAL_PHRASE,
        "guards": {
            "writesSqxHost": False,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "runsSqxTasks": False,
            "launchesSqxRuntime": False,
            "usesMigrationTool": False,
            "usesGetSourceCode": False,
            "usesRemoteFetch": False,
            "usesBrowserPersistence": False,
            "usesPluginCreateRenameDelete": False,
            "ordersRequestIsOptIn": True,
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


def smoke_payload(project_root: str | Path = ".") -> dict[str, Any]:
    root = _project_root(project_root)
    source_root = _source_plugin_root(root)
    runtime_text = _read_runtime_text(source_root)
    missing_files = [relative for relative in EXPECTED_FILES if not (source_root / relative).is_file()]
    forbidden = [marker for marker in FORBIDDEN_RUNTIME_MARKERS if marker in runtime_text]
    missing_markers = [marker for marker in REQUIRED_RUNTIME_MARKERS if marker not in runtime_text]
    ok = source_root.is_dir() and not missing_files and not forbidden and not missing_markers
    payload = _base_payload("smoke")
    payload.update({
        "ok": ok,
        "status": SQX144_CUSTOM_RESULTS5_SMOKE_STATUS if ok else "custom_results5_edge_gate_smoke_failed_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool",
        "pluginRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
        "missingFiles": missing_files,
        "forbiddenMarkers": forbidden,
        "missingRequiredMarkers": missing_markers,
        "fixtureNames": ["pass", "review", "block", "noStrategy", "missingStats", "missingOOS", "ordersOptIn", "largeOrders"],
        "thresholds": {
            "NumberOfTrades": ">= 120",
            "ProfitFactor": ">= 1.3",
            "ReturnDDRatio": ">= 4",
            "RExpectancy": "> 0",
            "NetProfit": "> 0",
        },
    })
    return payload


def status_payload(project_root: str | Path = ".", sqx_root: str | Path | None = None) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    target = _target_state(root, resolved_sqx_root)
    currently_installed = bool(target["targetMatchesSource"])
    payload = _base_payload("status")
    payload.update({
        "ok": True,
        "actions": ["status", "smoke", "report", "approval-template", "install"],
        "status": SQX144_CUSTOM_RESULTS5_INSTALLED_STATUS if currently_installed else SQX144_CUSTOM_RESULTS5_STATUS,
        "installExecuted": currently_installed,
        "currentlyInstalled": currently_installed,
        "hostRootAccepted": _host_root_accepted(resolved_sqx_root),
        "expectedRootName": EXPECTED_ROOT_NAME,
        "targetState": target,
        "nextAction": "run smoke and report; do not run install -Apply without exact approval",
    })
    return payload


def _install_preflight(project_root: Path, sqx_root: Path | None) -> dict[str, Any]:
    source_root = _source_plugin_root(project_root)
    results_root = _results_plugins_root(sqx_root)
    target_root = _target_plugin_root(sqx_root)
    smoke = smoke_payload(project_root)
    target = _target_state(project_root, sqx_root)
    processes = _detect_sqx_processes()
    blockers: list[str] = []
    warnings: list[str] = []

    if not smoke["ok"]:
        blockers.append("custom_results5_smoke_failed")
    if not source_root.is_dir():
        blockers.append("source_plugin_missing")
    if sqx_root is None:
        blockers.append("sqx144_root_not_configured")
    elif not _host_root_accepted(sqx_root):
        blockers.append("sqx144_full_root_mismatch")
    if results_root is None or not results_root.is_dir():
        blockers.append("results_plugins_root_missing")
    if processes.get("known") is not True:
        blockers.append("sqx_process_state_unknown")
    elif int(processes.get("processCount") or 0) > 0:
        blockers.append("sqx_or_java_process_running")
    if target_root and target_root.is_dir() and not target["targetOwnedBySqxEdge"]:
        blockers.append("target_plugin_exists_without_sqx_edge_marker")
    if target["targetMatchesSource"]:
        warnings.append("target_plugin_already_matches_source")
    elif target["targetOwnedBySqxEdge"]:
        warnings.append("target_plugin_differs_backup_required")

    return {
        "ok": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "processState": processes,
        "smoke": {"ok": smoke["ok"], "status": smoke["status"], "forbiddenMarkers": smoke["forbiddenMarkers"], "missingRequiredMarkers": smoke["missingRequiredMarkers"]},
        "targetState": target,
        "hostRootAccepted": _host_root_accepted(sqx_root),
    }


def report_payload(
    project_root: str | Path = ".",
    *,
    sqx_root: str | Path | None = None,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    smoke = smoke_payload(root)
    target = _target_state(root, resolved_sqx_root)
    currently_installed = bool(target["targetMatchesSource"])
    source_manifest = _file_manifest(_source_plugin_root(root))
    payload = _base_payload("report")
    payload.update({
        "ok": bool(smoke["ok"]),
        "status": SQX144_CUSTOM_RESULTS5_INSTALLED_STATUS if currently_installed else (SQX144_CUSTOM_RESULTS5_STATUS if smoke["ok"] else "custom_results5_edge_gate_report_blocked_no_install"),
        "installExecuted": currently_installed,
        "currentlyInstalled": currently_installed,
        "smoke": smoke,
        "targetState": target,
        "sourceFileCount": len(source_manifest),
        "sourceSha256": _combined_manifest_hash(source_manifest),
        "installRequiresExactApproval": INSTALL_APPROVAL_PHRASE,
        "installPlan": {
            "fromRef": SOURCE_PLUGIN_RELATIVE.as_posix(),
            "toRef": TARGET_PLUGIN_REF,
            "copyOnlySqxEdgeOwnedPlugin": True,
            "copyOriginalDownloadedPlugins": False,
            "copyRandomEntries": False,
            "requiresSqxClosed": True,
        },
    })
    if write_evidence:
        evidence_root = _evidence_root(root)
        evidence_root.mkdir(parents=True, exist_ok=True)
        evidence_path = evidence_root / f"sqx144_custom_results5_report_{_utc_stamp()}.json"
        evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidenceRef"] = f".local/sqx144_custom_results5/{evidence_path.name}"
    return payload


def approval_template_payload(project_root: str | Path = ".") -> dict[str, Any]:
    payload = _base_payload("approval-template")
    payload.update({
        "ok": True,
        "status": "custom_results5_edge_gate_approval_template_ready",
        "approvalTemplates": {
            "install": INSTALL_APPROVAL_PHRASE,
        },
        "approvalNotes": [
            "Install copies only the SQX Edge-owned SQX Edge Gate ResultsPlugin folder.",
            "Downloaded original Custom Results remain separate and are not touched.",
            "GET_ORDERS remains opt-in inside the tab after operator action.",
            "SQX must be closed and preflight clean before apply.",
        ],
    })
    return payload


def _require_install_approval(approval: str | None) -> None:
    if str(approval or "").strip() != INSTALL_APPROVAL_PHRASE:
        raise CustomResults5Error("custom_results5_install_requires_exact_approval")


def _assert_safe_install_paths(project_root: Path, sqx_root: Path | None) -> tuple[Path, Path, Path]:
    if sqx_root is None or not _host_root_accepted(sqx_root):
        raise CustomResults5Error("sqx144_full_root_mismatch")
    source_root = _source_plugin_root(project_root)
    results_root = _results_plugins_root(sqx_root)
    target_root = _target_plugin_root(sqx_root)
    if results_root is None or target_root is None or not results_root.is_dir():
        raise CustomResults5Error("results_plugins_root_missing")
    if not _is_relative_to(target_root, results_root):
        raise CustomResults5Error("target_plugin_path_outside_results_plugins")
    if not source_root.is_dir():
        raise CustomResults5Error("source_plugin_missing")
    return source_root, results_root, target_root


def install_payload(
    project_root: str | Path = ".",
    *,
    sqx_root: str | Path | None = None,
    approval: str | None = None,
    apply: bool = False,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    resolved_sqx_root = _resolve_sqx_root(root, sqx_root)
    preflight = _install_preflight(root, resolved_sqx_root)
    payload = _base_payload("install")
    payload.update({
        "ok": bool(preflight["ok"]),
        "status": SQX144_CUSTOM_RESULTS5_INSTALL_STATUS if preflight["ok"] else "custom_results5_edge_gate_install_blocked_no_apply",
        "dryRun": not apply,
        "preflight": preflight,
        "installRequiresExactApproval": INSTALL_APPROVAL_PHRASE,
        "wouldWriteSqxHost": bool(preflight["ok"]),
        "installExecuted": False,
    })
    if not apply:
        return payload

    _require_install_approval(approval)
    if not preflight["ok"]:
        raise CustomResults5Error("custom_results5_install_preflight_blocked", details={"blockers": preflight["blockers"]})

    source_root, _results_root, target_root = _assert_safe_install_paths(root, resolved_sqx_root)
    backup_id = None
    backup_created = False
    if target_root.exists():
        backup_id = f"custom_results5_install_{_utc_stamp()}"
        backup_base = _backup_root(resolved_sqx_root)
        if backup_base is None:
            raise CustomResults5Error("backup_root_missing")
        backup_target = backup_base / backup_id / PLUGIN_NAME
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(target_root, backup_target)
        shutil.rmtree(target_root)
        backup_created = True
    shutil.copytree(source_root, target_root)
    installed_manifest = _file_manifest(target_root)
    source_manifest = _file_manifest(source_root)
    payload.update({
        "ok": True,
        "status": SQX144_CUSTOM_RESULTS5_INSTALLED_STATUS,
        "dryRun": False,
        "installExecuted": True,
        "backupCreated": backup_created,
        "backupId": backup_id,
        "copiedFiles": len(installed_manifest),
        "installedSha256": _combined_manifest_hash(installed_manifest),
        "targetMatchesSource": _manifest_map(source_manifest) == _manifest_map(installed_manifest),
        "guards": {**payload["guards"], "writesSqxHost": True},
    })
    if write_evidence:
        evidence_root = _evidence_root(root)
        evidence_root.mkdir(parents=True, exist_ok=True)
        evidence_path = evidence_root / f"sqx144_custom_results5_install_{_utc_stamp()}.json"
        evidence_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidenceRef"] = f".local/sqx144_custom_results5/{evidence_path.name}"
    return payload


def _print_payload(payload: dict[str, Any], return_code: int = 0) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return return_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 CUSTOM-RESULTS5 SQX Edge Gate")
    parser.add_argument("action", choices=("status", "smoke", "report", "approval-template", "install"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--sqx-root", default=None)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.action == "status":
            payload = status_payload(args.project_root, sqx_root=args.sqx_root)
        elif args.action == "smoke":
            payload = smoke_payload(args.project_root)
        elif args.action == "report":
            payload = report_payload(args.project_root, sqx_root=args.sqx_root, write_evidence=args.write_evidence)
        elif args.action == "approval-template":
            payload = approval_template_payload(args.project_root)
        else:
            payload = install_payload(
                args.project_root,
                sqx_root=args.sqx_root,
                approval=args.approval,
                apply=args.apply,
                write_evidence=args.write_evidence,
            )
        return _print_payload(payload, 0 if payload.get("ok") else 2)
    except CustomResults5Error as exc:
        payload = _base_payload(args.action)
        payload.update({"ok": False, "status": exc.code, "error": exc.code, "details": exc.details})
        return _print_payload(payload, 2)


if __name__ == "__main__":
    raise SystemExit(main())
