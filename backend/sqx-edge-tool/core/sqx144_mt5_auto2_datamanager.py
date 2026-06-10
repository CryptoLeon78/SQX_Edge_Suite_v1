from __future__ import annotations

import re
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO2_VERSION = "sqx144-mt5-auto2-data-manager-button-bridge-v1"
SQX144_MT5_AUTO2_PHASE = "SQX144-MT5-AUTO2"
AUTO2_STATUS_READY = "auto2_overlay_api_install_gate_ready_no_install"
AUTO2_ASSET_VERSION = "sqx144-mt5-auto2-data-manager-button-bridge-v1-data-sources-visible"
AUTO2_STATUS_INSTALLED = "auto2_overlay_installed_verified_no_db_no_projects_no_databanks"
AUTO4_STATUS_INSTALLED = "auto4_overlay_installed_verified_no_db_no_projects_no_databanks_no_tasks"
AUTO9_HEALTH_MARKER = "sqx144-mt5-auto9-datamanager-health-watchdog-v1"
AUTO9_HEALTH_SOURCE_READY_STATUS = "auto9_datamanager_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool"
AUTO9_HEALTH_INSTALLED_STATUS = "auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool"
REQUEST_ID_PREFIX = "sqx_auto2"
EXPECTED_ROOT_NAME = "SQX_144_Full"
OVERLAY_MARKER = "sqx-edge-mt5-auto2"
AUTO4_MARKER = "sqx144-mt5-auto4-datamanager-catalog-triage-v1"
OVERLAY_JS_NAME = "sqx-edge-mt5-auto2.js"
OVERLAY_CSS_NAME = "sqx-edge-mt5-auto2.css"


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO2_VERSION,
        "phase": SQX144_MT5_AUTO2_PHASE,
        "action": action,
        "host": "sqx144_full",
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "placesOrders": False,
        "usesMigrationTool": False,
        "dataManagerButtonInstalled": False,
        "dataManagerButtonPlanned": True,
        "doesNotApplyToSqx": True,
        "doesNotApplyInstrumentConfig": True,
        "writesSqxOverlayHost": False,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def normalize_datamanager_symbol(symbol: str) -> str:
    raw = str(symbol or "").strip()
    if not raw:
        raise bridge.BridgeError("symbol_required")
    raw = re.sub(r"\s+", "", raw)
    if "_" not in raw:
        return raw.upper()
    base, suffix = raw.split("_", 1)
    if suffix.lower() == "darwinex":
        return f"{base.upper()}_Darwinex"
    return f"{base.upper()}_{suffix}"


def _request_id(symbol: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", symbol).strip("_") or "symbol"
    return f"{REQUEST_ID_PREFIX}_{safe}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


def _tool_config(project_root: Path) -> dict[str, Any]:
    config_path = project_root / "backend" / "sqx-edge-tool" / "config.json"
    if not config_path.is_file():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _resolve_sqx_root(project_root: Path) -> Path | None:
    env_root = os.environ.get("SQX144_ROOT")
    if env_root:
        return Path(env_root)
    config = _tool_config(project_root)
    configured = str(config.get("sqx_path") or "").strip()
    if configured:
        return Path(configured)
    fallback = Path("C:/BOTS/Versiones") / EXPECTED_ROOT_NAME
    if fallback.exists():
        return fallback
    return None


def _host_root_accepted(sqx_root: Path | None) -> bool:
    if sqx_root is None:
        return False
    root_text = str(sqx_root.resolve(strict=False))
    if sqx_root.resolve(strict=False).name != EXPECTED_ROOT_NAME:
        return False
    return not re.search(r"144\.2953|SQX_144_2953|SQX144_FULL_UPDATE2", root_text, flags=re.IGNORECASE)


def _overlay_source_root(project_root: Path) -> Path:
    return project_root / "integrations" / "sqx144" / "datamanager_mt5_auto2_overlay"


def _installed_state(project_root: Path) -> dict[str, Any]:
    sqx_root = _resolve_sqx_root(project_root)
    source_root = _overlay_source_root(project_root)
    source_js = source_root / OVERLAY_JS_NAME
    source_css = source_root / OVERLAY_CSS_NAME
    index_path = sqx_root / "internal" / "web" / "SQMANAGER" / "index.html" if sqx_root else None
    common_root = sqx_root / "internal" / "web" / "common" if sqx_root else None
    target_js = common_root / OVERLAY_JS_NAME if common_root else None
    target_css = common_root / OVERLAY_CSS_NAME if common_root else None
    index_text = ""
    if index_path and index_path.is_file():
        try:
            index_text = index_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            index_text = ""
    source_text = ""
    if source_js.is_file():
        try:
            source_text = source_js.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            source_text = ""
    target_text = ""
    if target_js and target_js.is_file():
        try:
            target_text = target_js.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            target_text = ""
    include_count = len(re.findall(re.escape(OVERLAY_MARKER), index_text))
    target_has_auto4 = AUTO4_MARKER in target_text
    source_has_auto9 = AUTO9_HEALTH_MARKER in source_text
    target_has_auto9 = AUTO9_HEALTH_MARKER in target_text
    warnings: list[str] = []
    if sqx_root is None:
        warnings.append("sqx_root_not_configured")
    elif not _host_root_accepted(sqx_root):
        warnings.append("sqx144_full_root_mismatch")
    return {
        "installStatusMarker": AUTO9_HEALTH_INSTALLED_STATUS if include_count > 0 and target_has_auto9 else AUTO9_HEALTH_SOURCE_READY_STATUS if source_has_auto9 and not target_has_auto9 else AUTO4_STATUS_INSTALLED if include_count > 0 and target_has_auto4 else AUTO2_STATUS_INSTALLED if include_count > 0 else AUTO2_STATUS_READY,
        "installed": include_count > 0,
        "dataManagerButtonInstalled": include_count > 0,
        "assetsPresent": bool(target_js and target_js.is_file() and target_css and target_css.is_file()),
        "sourcesPresent": source_js.is_file() and source_css.is_file(),
        "sourceHasAuto4": AUTO4_MARKER in source_text,
        "targetHasAuto4": target_has_auto4,
        "sourceHasAuto9Health": source_has_auto9,
        "targetHasAuto9Health": target_has_auto9,
        "includeCount": include_count,
        "hostRootAccepted": _host_root_accepted(sqx_root),
        "expectedRootName": EXPECTED_ROOT_NAME,
        "warnings": warnings,
    }


def _merge_installed_state(payload: dict[str, Any], project_root: Path) -> None:
    installed_state = _installed_state(project_root)
    payload.update({key: value for key, value in installed_state.items() if key != "warnings"})
    if installed_state["warnings"]:
        existing = list(payload.get("warnings") or [])
        payload["warnings"] = sorted(set(existing + installed_state["warnings"]))


def status_payload(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve(strict=False)
    payload = _base_payload("status")
    bridge_status = bridge.status_payload(root)
    installed_state = _installed_state(root)
    payload.update({
        "ok": bool(bridge_status.get("ok")),
        "status": (
            installed_state["installStatusMarker"]
            if installed_state["installed"]
            else AUTO2_STATUS_READY if bridge_status.get("ok") else "auto2_bridge_prerequisites_missing"
        ),
        "assetVersion": AUTO2_ASSET_VERSION,
        "bridge": _public_bridge_status(bridge_status),
        "endpoints": [
            "/api/sqx144/mt5-auto2/status",
            "/api/sqx144/mt5-auto2/request",
            "/api/sqx144/mt5-auto2/validate",
        ],
        "defaultSpreadPolicy": bridge.DEFAULT_SPREAD_POLICY,
        "buttonScope": "selected-instrument request, MT5 bridge validation and proposal display only",
    })
    _merge_installed_state(payload, root)
    return payload


def request_payload(
    project_root: str | Path,
    *,
    symbol: str,
    spread_policy: str = bridge.DEFAULT_SPREAD_POLICY,
    spread_timeframe: str = "M1",
    from_year: int = 0,
    to_year: int = 0,
    max_bars: int = 0,
) -> dict[str, Any]:
    normalized_symbol = normalize_datamanager_symbol(symbol)
    policy = str(spread_policy or bridge.DEFAULT_SPREAD_POLICY).lower()
    if policy not in bridge.ALLOWED_SPREAD_POLICIES:
        raise bridge.BridgeError("spread_policy_invalid", details={"policy": spread_policy})

    request_id = _request_id(normalized_symbol)
    written = bridge.write_request_payload(
        symbol=normalized_symbol,
        project_root=project_root,
        request_id=request_id,
        spread_timeframe=spread_timeframe or "M1",
        from_year=int(from_year or 0),
        to_year=int(to_year or 0),
        max_bars=int(max_bars or 0),
        apply=True,
    )
    payload = _base_payload("request")
    payload.update({
        "ok": bool(written.get("ok")),
        "status": "mt5_bridge_request_written",
        "symbol": normalized_symbol,
        "requestId": request_id,
        "spreadPolicy": policy,
        "requestFileName": bridge.DEFAULT_REQUEST_FILE,
        "responseFileName": bridge.DEFAULT_RESPONSE_FILE,
        "writesMt5Files": True,
        "validationPending": True,
    })
    _merge_installed_state(payload, Path(project_root).resolve(strict=False))
    return payload


def validate_payload(
    *,
    project_root: str | Path | None = None,
    spread_policy: str = bridge.DEFAULT_SPREAD_POLICY,
    expected_request_id: str | None = None,
    expected_symbol: str | None = None,
) -> dict[str, Any]:
    policy = str(spread_policy or bridge.DEFAULT_SPREAD_POLICY).lower()
    validation = bridge.validate_response_payload(spread_policy=policy)
    payload = _base_payload("validate")
    payload.update(validation)
    payload["version"] = SQX144_MT5_AUTO2_VERSION
    payload["phase"] = SQX144_MT5_AUTO2_PHASE
    payload["action"] = "validate"
    payload["dataManagerButtonPlanned"] = True
    payload["doesNotApplyToSqx"] = True
    if project_root is not None:
        _merge_installed_state(payload, Path(project_root).resolve(strict=False))
    if expected_symbol:
        normalized_expected_symbol = normalize_datamanager_symbol(expected_symbol)
        payload["expectedSymbol"] = normalized_expected_symbol
    if expected_request_id:
        payload["expectedRequestId"] = expected_request_id
        if payload.get("requestId") != expected_request_id:
            payload["ok"] = False
            payload["status"] = "waiting_for_requested_response"
            warnings = list(payload.get("warnings") or [])
            warnings.append("latest_response_request_id_mismatch")
            payload["warnings"] = sorted(set(warnings))
            payload["blockers"] = []
    health = bridge.health_payload(
        project_root=project_root,
        expected_request_id=expected_request_id or None,
        expected_symbol=expected_symbol or None,
    )
    payload["bridgeHealth"] = _public_bridge_health(health)
    if payload.get("status") == "waiting_for_requested_response":
        warnings = list(payload.get("warnings") or [])
        health_status = str(health.get("panelStatus") or health.get("status") or "")
        if health_status and health_status not in {"mt5_bridge_health_ok", "mt5_bridge_ready_latest_matches_request"}:
            warnings.append(health_status)
        warnings.extend(list(health.get("warnings") or []))
        payload["warnings"] = sorted(set(warnings))
    request_id_matches = not expected_request_id or payload.get("requestId") == expected_request_id
    if expected_symbol and request_id_matches:
        response_symbol = payload.get("symbol")
        if not response_symbol or normalize_datamanager_symbol(str(response_symbol)) != normalized_expected_symbol:
            payload["ok"] = False
            payload["status"] = "bridge_response_blocked"
            blockers = list(payload.get("blockers") or [])
            blockers.append("latest_response_symbol_mismatch")
            payload["blockers"] = sorted(set(blockers))
    return payload


def error_payload(action: str, error: bridge.BridgeError) -> dict[str, Any]:
    payload = _base_payload(action)
    payload.update({
        "ok": False,
        "status": "blocked",
        "error": error.code,
        "details": error.details,
        "blockers": [error.code],
    })
    return payload


def _public_bridge_status(payload: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "status",
        "sourcePresent",
        "mt5FilesDirPresent",
        "mt5ExpertsDirPresent",
        "installedSourcePresent",
        "requestFileName",
        "responseFileName",
        "defaultSpreadPolicy",
    )
    return {key: payload.get(key) for key in keys if key in payload}


def _public_bridge_health(payload: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "status",
        "panelStatus",
        "severity",
        "nextAction",
        "staleAfterSeconds",
        "mt5FilesDirPresent",
        "mt5ExpertsDirPresent",
        "sourcePresent",
        "installedSourcePresent",
        "terminalProcessRunning",
        "request",
        "latestResponse",
        "expectedRequestId",
        "expectedSymbol",
        "requestIdMatches",
        "symbolMatches",
        "requestNewerThanLatestResponse",
        "latestResponseStale",
        "pendingAgeSeconds",
        "warnings",
        "blockers",
        "launchesMt5",
        "runsMt5Ea",
        "writesDataDb",
        "runsSqxTasks",
        "usesMigrationTool",
    )
    return {key: payload.get(key) for key in keys if key in payload}
