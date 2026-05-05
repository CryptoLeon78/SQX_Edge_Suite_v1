from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.config_loader import load_manifest
from core.license_manager import license_status, load_product_manifest


SENSITIVE_PATH_KEYS = {
    "sqx_path",
    "sqx_data_db",
    "sqx_projects_dir",
    "template_capa1",
    "template_capa2",
    "output_dir",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _path_state(value: Any) -> dict[str, Any]:
    text = str(value or "").strip()
    if not text:
        return {"configured": False, "exists": False, "redacted": True}
    try:
        exists = Path(text).expanduser().exists()
    except OSError:
        exists = False
    return {"configured": True, "exists": exists, "redacted": True}


def _license_summary(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": status.get("state"),
        "plan": status.get("plan"),
        "active": bool(status.get("active")),
        "build_channel": status.get("build_channel"),
        "expires_at": status.get("expires_at"),
        "days_remaining": status.get("days_remaining"),
    }


def _runtime_summary() -> dict[str, Any]:
    executable = str(sys.executable).replace("\\", "/").lower()
    if "/runtime/python/" in executable:
        runtime_type = "embedded"
    elif "/venv/" in executable or "/scripts/python" in executable:
        runtime_type = "venv"
    else:
        runtime_type = "system"
    return {
        "python": platform.python_version(),
        "runtime_type": runtime_type,
        "platform": platform.system(),
        "platform_release": platform.release(),
    }


def _manifest_counts() -> dict[str, Any]:
    ui = load_manifest("ui_manifest.json")
    plan = load_manifest("plan.json")
    assets = load_manifest("assets.json")
    strategies = load_manifest("strategies.json")
    product = load_product_manifest()
    return {
        "tabs": len(ui.get("tabs") or []),
        "assets": len(assets.get("assets") or []),
        "plan_minings": len(plan.get("minings") or []),
        "strategies": len(strategies.get("strategies") or []),
        "features": len(product.get("features") or {}),
        "product_manifest_version": product.get("version"),
    }


def _distribution_summary(project_root: Path) -> dict[str, Any]:
    dist = project_root / "dist"
    latest_zip = None
    if dist.is_dir():
        zips = sorted(dist.glob("SQX_Edge_Tool_Portable_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        if zips:
            zip_path = zips[0]
            latest_zip = {
                "present": True,
                "bytes": zip_path.stat().st_size,
                "sha256_file_present": Path(str(zip_path) + ".sha256").is_file(),
            }
    audit_path = dist / "SQX_distribution_audit.txt"
    audit_status = None
    if audit_path.is_file():
        try:
            text = audit_path.read_text(encoding="utf-8", errors="ignore")
            audit_status = "PASS" if "Status: PASS" in text else ("FAIL" if "Status: FAIL" in text else "UNKNOWN")
        except OSError:
            audit_status = "UNKNOWN"
    return {
        "latest_zip": latest_zip or {"present": False, "sha256_file_present": False},
        "distribution_audit": {
            "present": audit_path.is_file(),
            "status": audit_status,
        },
    }


def _config_summary(cfg: dict[str, Any], config_exists: bool) -> dict[str, Any]:
    editable_keys = sorted(k for k in cfg.keys() if k not in SENSITIVE_PATH_KEYS)
    return {
        "config_exists": config_exists,
        "path_values": {key: _path_state(cfg.get(key)) for key in sorted(SENSITIVE_PATH_KEYS)},
        "asset_aliases_count": len(cfg.get("asset_aliases") or {}),
        "editable_keys": editable_keys,
        "redacted_keys": sorted(SENSITIVE_PATH_KEYS),
    }


def support_diagnostic_id(payload: dict[str, Any]) -> str:
    stable = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(stable).hexdigest()[:12]


def build_support_diagnostics(
    cfg: dict[str, Any],
    *,
    app_version: str,
    config_exists: bool,
    project_root: Path,
) -> dict[str, Any]:
    product = load_product_manifest()
    status = license_status()
    payload: dict[str, Any] = {
        "ok": True,
        "schema_version": 1,
        "generated_at": _utc_now(),
        "privacy": {
            "safe_to_send": True,
            "paths": "redacted",
            "license_payload": "excluded",
            "strategy_files": "excluded",
            "local_storage": "excluded",
        },
        "app": {
            "name": product.get("product", {}).get("publicName") or "SQX Edge Suite",
            "edition": product.get("product", {}).get("edition"),
            "version": app_version,
            "build_channel": product.get("build", {}).get("channel"),
        },
        "runtime": _runtime_summary(),
        "license": _license_summary(status),
        "config": _config_summary(cfg, config_exists),
        "manifests": _manifest_counts(),
        "distribution": _distribution_summary(project_root),
        "checks": {
            "api_boundary": product.get("security", {}).get("apiBoundary", "local_only"),
            "feature_gating": [
                "project_generator.generate",
                "strategy_cleaner.apply",
            ],
            "diagnostics_redacted": True,
        },
    }
    payload["diagnostic_id"] = support_diagnostic_id({
        key: value for key, value in payload.items() if key not in {"generated_at", "diagnostic_id"}
    })
    payload["filename"] = f"SQX_support_diagnostic_{payload['diagnostic_id']}.json"
    return payload
