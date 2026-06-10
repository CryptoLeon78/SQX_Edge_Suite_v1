from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_workspaces import append_workspace_audit_event, public_workspace_context


SQX_READINESS_VERSION = "sqx-edge.sqx-readiness-status-v1"
MANIFEST_PATH = Path(__file__).resolve().parents[1] / "config" / "sqx_readiness_manifest.json"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCAL_STATUS_PATH = PROJECT_ROOT / ".local" / "sqx_readiness" / "status.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_readiness_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or MANIFEST_PATH
    return json.loads(manifest_path.read_text(encoding="utf-8-sig"))


def required_check_ids(manifest: Mapping[str, Any] | None = None) -> list[str]:
    payload = manifest or load_readiness_manifest()
    return [str(item) for item in payload.get("requiredChecklist", []) if str(item).strip()]


def default_status(manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = manifest or load_readiness_manifest()
    checks = {check_id: False for check_id in required_check_ids(payload)}
    return {
        "ok": True,
        "version": SQX_READINESS_VERSION,
        "manifestSchema": payload.get("schema"),
        "complete": False,
        "source": "not_configured",
        "checks": checks,
        "missing": sorted(checks),
        "updatedAt": None,
        "report": None,
        "privacy": {"local_paths_returned": False, "data_db_copied": False},
    }


def summarize_manifest_for_public(manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(manifest or load_readiness_manifest())
    return {
        "ok": True,
        "schema": payload.get("schema"),
        "version": payload.get("version"),
        "label": payload.get("label"),
        "requiredChecklist": payload.get("requiredChecklist") or [],
        "brokerProfiles": payload.get("brokerProfiles") or [],
        "periods": payload.get("periods") or {},
        "curatedAssets": payload.get("curatedAssets") or [],
        "requiredSnippets": payload.get("requiredSnippets") or [],
        "requiredViews": payload.get("requiredViews") or [],
        "blockedPackagePatterns": payload.get("blockedPackagePatterns") or [],
        "privacy": payload.get("privacy") or {},
    }


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "ok", "pass", "passed", "ready", "complete", "completed"}
    return False


def _checks_from_report(report: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, bool]:
    required = required_check_ids(manifest)
    raw_checks = report.get("checks") if isinstance(report.get("checks"), Mapping) else {}
    checks = {check_id: _coerce_bool(raw_checks.get(check_id)) for check_id in required}
    legacy_view_ready = _coerce_bool(raw_checks.get("views_ready")) or _coerce_bool(raw_checks.get("viewsReady"))
    if "correlation_view_ready" in checks:
        checks["correlation_view_ready"] = checks.get("correlation_view_ready", False) or legacy_view_ready

    if isinstance(report.get("summary"), Mapping):
        summary = report["summary"]
        checks["sqx_root_selected"] = checks.get("sqx_root_selected", False) or _coerce_bool(summary.get("sqxRootSelected"))
        checks["sqx_version_compatible"] = checks.get("sqx_version_compatible", False) or _coerce_bool(summary.get("versionCompatible"))
        checks["data_db_found"] = checks.get("data_db_found", False) or _coerce_bool(summary.get("dataDbFound"))
        checks["brokers_validated"] = checks.get("brokers_validated", False) or _coerce_bool(summary.get("brokersValidated"))
        checks["curated_assets_validated"] = checks.get("curated_assets_validated", False) or _coerce_bool(summary.get("curatedAssetsValidated"))
        checks["snippets_ready"] = checks.get("snippets_ready", False) or _coerce_bool(summary.get("snippetsReady"))
        view_ready = _coerce_bool(summary.get("correlationViewReady")) or _coerce_bool(summary.get("viewsReady"))
        if "correlation_view_ready" in checks:
            checks["correlation_view_ready"] = checks.get("correlation_view_ready", False) or view_ready
        if "views_ready" in checks:
            checks["views_ready"] = checks.get("views_ready", False) or view_ready
    if isinstance(report.get("files"), Mapping):
        files = report["files"]
        checks["sensitive_files_excluded"] = checks.get("sensitive_files_excluded", False) or not _coerce_bool(files.get("sensitiveFindings"))
    return checks


def evaluate_readiness_report(report: Mapping[str, Any], manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(report or {})
    active_manifest = manifest or load_readiness_manifest()
    checks = _checks_from_report(payload, active_manifest)
    missing = sorted([check_id for check_id, ok in checks.items() if not ok])
    blockers = list(payload.get("blockers") or [])
    complete = not missing and not blockers
    return {
        "ok": True,
        "version": SQX_READINESS_VERSION,
        "manifestSchema": active_manifest.get("schema"),
        "complete": complete,
        "source": str(payload.get("source") or "checker_report"),
        "checks": checks,
        "missing": missing,
        "blockers": blockers,
        "updatedAt": utc_now(),
        "report": {
            "checkerVersion": payload.get("checkerVersion"),
            "generatedAt": payload.get("generatedAt"),
            "summary": payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {},
        },
        "privacy": {"local_paths_returned": False, "data_db_copied": False},
    }


def _status_path_for_workspace(workspace_context: Mapping[str, Any] | None = None) -> Path:
    if workspace_context and workspace_context.get("ok"):
        paths = workspace_context.get("_paths")
        if isinstance(paths, Mapping) and isinstance(paths.get("config"), Path):
            config_dir = paths["config"]
            config_dir.mkdir(parents=True, exist_ok=True)
            return config_dir / "sqx_readiness_status.json"
    LOCAL_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    return LOCAL_STATUS_PATH


def read_readiness_status(workspace_context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    path = _status_path_for_workspace(workspace_context)
    if not path.is_file():
        status = default_status()
    else:
        try:
            status = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            status = default_status()
            status["source"] = "status_file_invalid"
    status["storage"] = {
        "scope": "remote_workspace" if workspace_context else "local_operator",
        "local_path_returned": False,
        "exists": path.is_file(),
    }
    if workspace_context:
        status["workspace"] = public_workspace_context(workspace_context)
    return status


def write_readiness_status(
    status: Mapping[str, Any],
    workspace_context: Mapping[str, Any] | None = None,
    *,
    source: str = "sqx-readiness",
) -> dict[str, Any]:
    payload = dict(status)
    payload["updatedAt"] = payload.get("updatedAt") or utc_now()
    payload["version"] = SQX_READINESS_VERSION
    payload["privacy"] = {"local_paths_returned": False, "data_db_copied": False}
    path = _status_path_for_workspace(workspace_context)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    if workspace_context:
        audit = append_workspace_audit_event(workspace_context, {
            "type": "sqx_readiness_status_write",
            "action": source,
            "complete": bool(payload.get("complete")),
            "missing": payload.get("missing") or [],
        })
        payload["workspace"] = public_workspace_context(workspace_context)
        payload["audit"] = audit.get("audit_event")
    return payload


def update_manual_status(checks: Mapping[str, Any], workspace_context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    manifest = load_readiness_manifest()
    current = read_readiness_status(workspace_context)
    merged = {check_id: bool(current.get("checks", {}).get(check_id)) for check_id in required_check_ids(manifest)}
    for check_id, value in dict(checks or {}).items():
        if check_id in merged:
            merged[check_id] = _coerce_bool(value)
        elif check_id in {"views_ready", "viewsReady"} and "correlation_view_ready" in merged:
            merged["correlation_view_ready"] = _coerce_bool(value)
    missing = sorted([check_id for check_id, ok in merged.items() if not ok])
    status = {
        "ok": True,
        "version": SQX_READINESS_VERSION,
        "manifestSchema": manifest.get("schema"),
        "complete": not missing,
        "source": "manual_checklist",
        "checks": merged,
        "missing": missing,
        "blockers": [],
        "updatedAt": utc_now(),
        "report": current.get("report"),
        "privacy": {"local_paths_returned": False, "data_db_copied": False},
    }
    return write_readiness_status(status, workspace_context, source="manual_checklist")


def readiness_gate_response(feature: str, status: Mapping[str, Any] | None = None) -> dict[str, Any]:
    current = dict(status or read_readiness_status())
    return {
        "ok": False,
        "allowed": False,
        "error": "sqx_readiness_required",
        "message": "Completa el checklist SQX Edge Readiness antes de usar funciones que dependen de SQX.",
        "required_feature": feature,
        "readiness": {
            "version": SQX_READINESS_VERSION,
            "complete": bool(current.get("complete")),
            "missing": current.get("missing") or [],
            "source": current.get("source"),
        },
        "privacy": {"local_paths_returned": False, "data_db_copied": False},
    }


def query_reference_data_db(db_path: str | Path, manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    active_manifest = manifest or load_readiness_manifest()
    path = Path(db_path)
    if not path.is_file():
        return {"ok": False, "error": "data_db_not_found", "privacy": {"data_db_copied": False}}
    brokers_expected = {int(item["brokerId"]): item for item in active_manifest.get("brokerProfiles", []) if item.get("brokerId") is not None}
    assets_expected = [item.get("asset") for item in active_manifest.get("curatedAssets", []) if item.get("asset")]
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        broker_rows = connection.execute("SELECT ID, NAME, POSTFIX FROM BROKER").fetchall()
        instrument_rows = connection.execute(
            "SELECT INSTRUMENT, TICKSIZE, TICKSTEP, POINTVALUE, DEFAULTSPREAD, DATATYPE FROM INSTRUMENTS"
        ).fetchall()
        data_rows = connection.execute("SELECT INSTRUMENT, SYMBOL, TIMEFRAME, TIMEZONE, DATATYPE, ROWS FROM DATA").fetchall()
    finally:
        connection.close()
    brokers = {int(row["ID"]): {"name": row["NAME"], "postfix": row["POSTFIX"]} for row in broker_rows}
    instruments = {str(row["INSTRUMENT"]): dict(row) for row in instrument_rows}
    data_index = {(str(row["INSTRUMENT"]), str(row["TIMEFRAME"])): dict(row) for row in data_rows}
    missing_brokers = [profile["id"] for broker_id, profile in brokers_expected.items() if broker_id not in brokers]
    missing_assets = [asset for asset in assets_expected if asset not in instruments]
    return {
        "ok": not missing_brokers and not missing_assets,
        "brokerCount": len(brokers),
        "instrumentCount": len(instruments),
        "dataRows": len(data_rows),
        "missingBrokers": missing_brokers,
        "missingAssets": missing_assets,
        "curatedCoverage": {
            asset: sorted([tf for (name, tf), _row in data_index.items() if name == asset])
            for asset in assets_expected
        },
        "privacy": {"data_db_copied": False, "local_paths_returned": False},
    }


def gate_disabled_for_local_internal(is_remote: bool, build_channel: str | None) -> bool:
    if os.environ.get("SQX_READINESS_DISABLE_GATE") == "1":
        return True
    if not is_remote and build_channel == "internal":
        return True
    return False
