from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SQX144_MT5_AUTO1_BRIDGE_VERSION = "sqx144-mt5-auto1-data-manager-bridge-v1"
SQX144_MT5_AUTO1_PHASE = "SQX144-MT5-AUTO1"
DEFAULT_MT5_TERMINAL_ID = "6C3C6A11D1C3791DD4DBF45421BF8028"
DEFAULT_MT5_FILES_DIR = Path("C:/Users/Ivan SQX/AppData/Roaming/MetaQuotes/Terminal") / DEFAULT_MT5_TERMINAL_ID / "MQL5" / "Files"
DEFAULT_MT5_EXPERTS_DIR = Path("C:/Users/Ivan SQX/AppData/Roaming/MetaQuotes/Terminal") / DEFAULT_MT5_TERMINAL_ID / "MQL5" / "Experts"
DEFAULT_REQUEST_FILE = "SQXInfoBridge.request.ini"
DEFAULT_RESPONSE_FILE = "SQXInfoBridge.latest.json"
DEFAULT_SPREAD_POLICY = "p90"
DEFAULT_HEALTH_STALE_AFTER_SECONDS = 45
MT5_PROCESS_NAMES = ("terminal64.exe", "terminal.exe")
ALLOWED_SPREAD_POLICIES = {"p50", "p75", "p90", "p95", "p99", "mean"}
RESPONSE_SAFETY_FALSE_FLAGS = (
    "writesSqxHost",
    "writesDataDb",
    "writesUserProjects",
    "mutatesDatabanks",
    "runsSqxTasks",
    "placesOrders",
    "usesMigrationTool",
)
MT5_FILES_DIR_NOT_ALLOWED = "mt5_files_dir_not_allowed"
MT5_EXPERTS_DIR_NOT_ALLOWED = "mt5_experts_dir_not_allowed"
APPLY_DIR_NOT_ALLOWED_BY_KIND = {
    "mt5_files": MT5_FILES_DIR_NOT_ALLOWED,
    "mt5_experts": MT5_EXPERTS_DIR_NOT_ALLOWED,
}


class BridgeError(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _source_mq5(project_root: Path) -> Path:
    return project_root / "integrations" / "sqx144" / "mt5_bridge" / "SQXInfoBridge.mq5"


def _local_apply_root(project_root: Path) -> Path:
    return project_root / ".local" / "mt5_bridge_auto1"


def _path_is_within(path: Path, parent: Path) -> bool:
    resolved_path = path.resolve(strict=False)
    resolved_parent = parent.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_parent)
    except ValueError:
        return False
    return True


def _require_allowed_apply_dir(path: Path, *, default_dir: Path, project_root: Path, kind: str) -> None:
    resolved = path.resolve(strict=False)
    if resolved == default_dir.resolve(strict=False):
        return
    if _path_is_within(resolved, _local_apply_root(project_root)):
        return
    raise BridgeError(APPLY_DIR_NOT_ALLOWED_BY_KIND.get(kind, f"{kind}_dir_not_allowed"))


def _utc_request_id(symbol: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in symbol)
    return f"sqx_{safe}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "phase": SQX144_MT5_AUTO1_PHASE,
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
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def request_ini(
    *,
    symbol: str,
    request_id: str | None = None,
    spread_timeframe: str = "M1",
    from_year: int = 0,
    to_year: int = 0,
    max_bars: int = 0,
) -> str:
    symbol = str(symbol or "").strip()
    if not symbol:
        raise BridgeError("symbol_required")
    request_id = request_id or _utc_request_id(symbol)
    return "\n".join([
        f"version={SQX144_MT5_AUTO1_BRIDGE_VERSION}",
        f"requestId={request_id}",
        f"symbol={symbol}",
        f"spreadTimeframe={spread_timeframe}",
        f"fromYear={int(from_year or 0)}",
        f"toYear={int(to_year or 0)}",
        f"maxBars={int(max_bars or 0)}",
        "",
    ])


def status_payload(project_root: str | Path, *, mt5_files_dir: str | Path | None = None, mt5_experts_dir: str | Path | None = None) -> dict[str, Any]:
    root = _project_root(project_root)
    files_dir = Path(mt5_files_dir or DEFAULT_MT5_FILES_DIR)
    experts_dir = Path(mt5_experts_dir or DEFAULT_MT5_EXPERTS_DIR)
    source = _source_mq5(root)
    installed = experts_dir / "SQXInfoBridge.mq5"
    payload = _base_payload("status")
    payload.update({
        "ok": source.is_file() and files_dir.is_dir() and experts_dir.is_dir(),
        "status": "bridge_source_ready" if source.is_file() else "bridge_source_missing",
        "sourcePresent": source.is_file(),
        "mt5FilesDirPresent": files_dir.is_dir(),
        "mt5ExpertsDirPresent": experts_dir.is_dir(),
        "installedSourcePresent": installed.is_file(),
        "requestFileName": DEFAULT_REQUEST_FILE,
        "responseFileName": DEFAULT_RESPONSE_FILE,
        "defaultSpreadPolicy": DEFAULT_SPREAD_POLICY,
        "automationContract": "SQX Edge writes a request file, MT5 bridge writes a response file, SQX Edge validates and plans; no SQX DB write in this phase.",
    })
    return payload


def request_template_payload(
    *,
    symbol: str,
    request_id: str | None = None,
    spread_timeframe: str = "M1",
    from_year: int = 0,
    to_year: int = 0,
    max_bars: int = 0,
) -> dict[str, Any]:
    text = request_ini(
        symbol=symbol,
        request_id=request_id,
        spread_timeframe=spread_timeframe,
        from_year=from_year,
        to_year=to_year,
        max_bars=max_bars,
    )
    payload = _base_payload("request-template")
    payload.update({
        "ok": True,
        "status": "request_template_ready",
        "requestFileName": DEFAULT_REQUEST_FILE,
        "request": _ini_to_public_dict(text),
        "requestText": text,
    })
    return payload


def write_request_payload(
    *,
    symbol: str,
    mt5_files_dir: str | Path | None = None,
    project_root: str | Path | None = None,
    request_id: str | None = None,
    spread_timeframe: str = "M1",
    from_year: int = 0,
    to_year: int = 0,
    max_bars: int = 0,
    apply: bool = False,
) -> dict[str, Any]:
    payload = _base_payload("write-request")
    payload["writesMt5Files"] = bool(apply)
    text = request_ini(
        symbol=symbol,
        request_id=request_id,
        spread_timeframe=spread_timeframe,
        from_year=from_year,
        to_year=to_year,
        max_bars=max_bars,
    )
    if not apply:
        payload.update({
            "ok": True,
            "status": "request_ready_apply_required",
            "requestFileName": DEFAULT_REQUEST_FILE,
            "request": _ini_to_public_dict(text),
        })
        return payload
    root = _project_root(project_root)
    files_dir = Path(mt5_files_dir or DEFAULT_MT5_FILES_DIR)
    if not files_dir.is_dir():
        raise BridgeError("mt5_files_dir_missing")
    _require_allowed_apply_dir(files_dir, default_dir=DEFAULT_MT5_FILES_DIR, project_root=root, kind="mt5_files")
    request_path = files_dir / DEFAULT_REQUEST_FILE
    tmp_path = files_dir / f"{DEFAULT_REQUEST_FILE}.tmp"
    tmp_path.write_text(text, encoding="ascii")
    tmp_path.replace(request_path)
    payload.update({
        "ok": True,
        "status": "request_written_for_mt5_bridge",
        "requestFileName": DEFAULT_REQUEST_FILE,
        "request": _ini_to_public_dict(text),
    })
    return payload


def install_source_payload(project_root: str | Path, *, mt5_experts_dir: str | Path | None = None, apply: bool = False, overwrite: bool = False) -> dict[str, Any]:
    root = _project_root(project_root)
    source = _source_mq5(root)
    experts_dir = Path(mt5_experts_dir or DEFAULT_MT5_EXPERTS_DIR)
    target = experts_dir / "SQXInfoBridge.mq5"
    payload = _base_payload("install-source")
    payload["writesMt5Source"] = bool(apply)
    if not source.is_file():
        raise BridgeError("bridge_source_missing")
    if not experts_dir.is_dir():
        raise BridgeError("mt5_experts_dir_missing")
    if apply:
        _require_allowed_apply_dir(experts_dir, default_dir=DEFAULT_MT5_EXPERTS_DIR, project_root=root, kind="mt5_experts")
        if target.exists() and not overwrite:
            raise BridgeError("mt5_bridge_source_exists_requires_overwrite")
    if not apply:
        payload.update({
            "ok": True,
            "status": "install_source_ready_apply_required",
            "targetFileName": "SQXInfoBridge.mq5",
        })
        return payload
    shutil.copy2(source, target)
    payload.update({
        "ok": True,
        "status": "bridge_source_installed_to_mt5_experts",
        "targetFileName": "SQXInfoBridge.mq5",
        "overwroteExistingSource": bool(overwrite),
    })
    return payload


def validate_response_payload(*, response_path: str | Path | None = None, spread_policy: str = DEFAULT_SPREAD_POLICY) -> dict[str, Any]:
    path = Path(response_path or (DEFAULT_MT5_FILES_DIR / DEFAULT_RESPONSE_FILE))
    payload = _base_payload("validate-response")
    if not path.is_file():
        payload.update({"status": "response_missing", "blockers": ["response_missing"]})
        return payload
    try:
        response = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise BridgeError("response_json_invalid", details={"error": str(exc)}) from exc
    validation = validate_bridge_response(response, spread_policy=spread_policy)
    payload.update(validation)
    return payload


def health_payload(
    *,
    project_root: str | Path | None = None,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
    expected_request_id: str | None = None,
    expected_symbol: str | None = None,
    stale_after_seconds: int = DEFAULT_HEALTH_STALE_AFTER_SECONDS,
    now: float | None = None,
    mt5_process_running: bool | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    files_dir = Path(mt5_files_dir or DEFAULT_MT5_FILES_DIR)
    experts_dir = Path(mt5_experts_dir or DEFAULT_MT5_EXPERTS_DIR)
    request_path = files_dir / DEFAULT_REQUEST_FILE
    response_path = files_dir / DEFAULT_RESPONSE_FILE
    source = _source_mq5(root)
    installed = experts_dir / "SQXInfoBridge.mq5"
    now_ts = time.time() if now is None else float(now)
    stale_after = max(5, int(stale_after_seconds or DEFAULT_HEALTH_STALE_AFTER_SECONDS))
    request = _public_file_probe(request_path, now_ts=now_ts, parser=_read_ini_file_public)
    response = _public_file_probe(response_path, now_ts=now_ts, parser=_read_json_file_public)
    if mt5_process_running is None:
        mt5_process_running = _detect_mt5_process_running()

    warnings: list[str] = []
    blockers: list[str] = []
    if not files_dir.is_dir():
        blockers.append("mt5_files_dir_missing")
    if not experts_dir.is_dir():
        blockers.append("mt5_experts_dir_missing")
    if not source.is_file():
        blockers.append("bridge_source_missing")
    if not installed.is_file():
        warnings.append("mt5_bridge_ea_source_not_installed")
    if response.get("parseError"):
        blockers.append("latest_response_json_invalid")

    request_fields = request.get("fields") if isinstance(request.get("fields"), dict) else {}
    response_fields = response.get("fields") if isinstance(response.get("fields"), dict) else {}
    current_request_id = str(expected_request_id or request_fields.get("requestId") or "").strip()
    current_symbol = str(expected_symbol or request_fields.get("symbol") or "").strip()
    latest_request_id = str(response_fields.get("requestId") or "").strip()
    latest_symbol = str(response_fields.get("symbol") or "").strip()
    request_id_matches = bool(current_request_id and latest_request_id == current_request_id)
    symbol_matches = _same_symbol(current_symbol, latest_symbol) if current_symbol and latest_symbol else None
    request_newer_than_response = bool(request.get("present") and response.get("present") and float(request.get("mtime") or 0) > float(response.get("mtime") or 0))
    latest_response_stale = bool(response.get("present") and float(response.get("ageSeconds") or 0) > stale_after)
    pending_age = request.get("ageSeconds") if request.get("present") else None
    response_error = str(response_fields.get("error") or "").strip()
    response_status = str(response_fields.get("status") or "").strip()

    if response_error:
        warnings.append(f"bridge_error_{response_error}")
    if expected_request_id and latest_request_id != expected_request_id:
        warnings.append("latest_response_request_id_mismatch")
    if latest_response_stale:
        warnings.append("latest_response_stale")
    if request_newer_than_response:
        warnings.append("request_newer_than_latest_response")

    status = "mt5_bridge_health_ok"
    panel_status = "mt5_bridge_health_ok"
    severity = "ok"
    next_action = "bridge_ready"
    if blockers:
        status = "mt5_bridge_prerequisites_missing"
        panel_status = status
        severity = "bad"
        next_action = "check_bridge_install_paths"
    elif not request.get("present"):
        status = "mt5_bridge_no_request_pending"
        panel_status = status
        severity = "ok"
        next_action = "select_symbol_and_press_mt5_bridge"
    elif not response.get("present"):
        status, panel_status, severity, next_action = _pending_health_status(mt5_process_running)
        warnings.append("latest_response_missing")
    elif response.get("parseError"):
        status = "mt5_bridge_latest_json_invalid"
        panel_status = status
        severity = "bad"
        next_action = "restart_or_repair_bridge_response"
    elif expected_request_id and not request_id_matches:
        status, panel_status, severity, next_action = _pending_health_status(mt5_process_running)
    elif request_newer_than_response and (pending_age is None or float(pending_age) >= stale_after):
        status, panel_status, severity, next_action = _pending_health_status(mt5_process_running)
    elif response_status and response_status not in {"ok", "warning"}:
        status = "mt5_bridge_latest_response_error"
        panel_status = f"mt5_bridge_error_{response_error}" if response_error else status
        severity = "bad"
        next_action = "repair_mt5_bridge_symbol_or_ea"
    elif latest_response_stale and not request_id_matches:
        status = "mt5_bridge_latest_desfasado"
        panel_status = status
        severity = "hold"
        next_action = "wait_for_fresh_bridge_response_or_restart_bridge"
    elif expected_symbol and symbol_matches is False:
        status = "mt5_bridge_latest_symbol_mismatch"
        panel_status = status
        severity = "bad"
        next_action = "discard_crossed_response_and_request_again"
    elif expected_request_id and request_id_matches:
        status = "mt5_bridge_ready_latest_matches_request"
        panel_status = status
        severity = "ok"
        next_action = "validate_bridge_payload"
    elif request.get("present") and not expected_request_id:
        status = "mt5_bridge_request_observed"
        panel_status = status
        severity = "hold"
        next_action = "validate_expected_request"

    return {
        "ok": True,
        "version": SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "phase": SQX144_MT5_AUTO1_PHASE,
        "action": "health",
        "status": status,
        "panelStatus": panel_status,
        "severity": severity,
        "nextAction": next_action,
        "host": "sqx144_full",
        "staleAfterSeconds": stale_after,
        "mt5FilesDirPresent": files_dir.is_dir(),
        "mt5ExpertsDirPresent": experts_dir.is_dir(),
        "sourcePresent": source.is_file(),
        "installedSourcePresent": installed.is_file(),
        "terminalProcessRunning": mt5_process_running,
        "mt5ProcessNames": list(MT5_PROCESS_NAMES),
        "request": _public_health_file(request, fields=("requestId", "symbol", "spreadTimeframe", "fromYear", "toYear", "maxBars")),
        "latestResponse": _public_health_file(response, fields=("requestId", "symbol", "mt5Symbol", "status", "error", "mt5Error")),
        "expectedRequestId": expected_request_id or None,
        "expectedSymbol": expected_symbol or None,
        "requestIdMatches": request_id_matches if expected_request_id else None,
        "symbolMatches": symbol_matches,
        "requestNewerThanLatestResponse": request_newer_than_response,
        "latestResponseStale": latest_response_stale,
        "pendingAgeSeconds": _rounded_age(pending_age),
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "placesOrders": False,
        "usesMigrationTool": False,
        "doesNotApplyToSqx": True,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def validate_bridge_response(response: dict[str, Any], *, spread_policy: str = DEFAULT_SPREAD_POLICY) -> dict[str, Any]:
    policy = str(spread_policy or DEFAULT_SPREAD_POLICY).lower()
    if policy not in ALLOWED_SPREAD_POLICIES:
        raise BridgeError("spread_policy_invalid", details={"policy": spread_policy})
    blockers: list[str] = []
    warnings: list[str] = []
    if response.get("version") != SQX144_MT5_AUTO1_BRIDGE_VERSION:
        blockers.append("bridge_version_mismatch")
    if response.get("status") not in {"ok", "warning"}:
        blockers.append("bridge_response_not_ok")
    for flag in RESPONSE_SAFETY_FALSE_FLAGS:
        if flag not in response:
            blockers.append(f"unsafe_response_flag_missing_{flag}")
        elif response.get(flag) is not False:
            blockers.append(f"unsafe_response_flag_{flag}")
    stats = response.get("spreadStats") if isinstance(response.get("spreadStats"), dict) else {}
    samples = int(stats.get("samples") or 0)
    if samples <= 0:
        blockers.append("spread_samples_missing")
    proposed_spread = _number(stats.get(policy))
    if proposed_spread is None or proposed_spread <= 0:
        blockers.append("spread_policy_value_missing")
    if samples and samples < 1000:
        warnings.append("spread_sample_count_low")
    properties = response.get("properties") if isinstance(response.get("properties"), dict) else {}
    proposed = {
        "DEFAULTSPREAD": proposed_spread,
        "spreadPolicy": policy,
        "spreadSamples": samples,
        "POINTVALUE": _number(properties.get("pointValue")),
        "TICKSIZE": _number(properties.get("tickSizeForSqx")),
        "TICKSTEP": _number(properties.get("tickStepForSqx")),
    }
    return {
        "ok": not blockers,
        "status": "bridge_response_validated" if not blockers else "bridge_response_blocked",
        "symbol": response.get("symbol"),
        "requestId": response.get("requestId"),
        "spreadPolicy": policy,
        "proposedSqxFields": proposed,
        "yearCount": len(response.get("yearlySpreadStats") or []),
        "consumesMt5BridgeResponse": True,
        "doesNotApplyToSqx": True,
        "blockers": blockers,
        "warnings": sorted(set(warnings + list(response.get("warnings") or []))),
    }


def _number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _ini_to_public_dict(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value
    return result


def _same_symbol(left: str, right: str) -> bool:
    return str(left or "").strip().lower() == str(right or "").strip().lower()


def _rounded_age(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    if not math.isfinite(parsed):
        return None
    return round(max(0.0, parsed), 3)


def _iso_from_timestamp(value: float | None) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    except Exception:
        return None


def _read_ini_file_public(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="ascii", errors="ignore")
    return {"fields": _ini_to_public_dict(text)}


def _read_json_file_public(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise ValueError("latest_response_not_object")
    return {"fields": raw}


def _public_file_probe(path: Path, *, now_ts: float, parser) -> dict[str, Any]:
    if not path.is_file():
        return {"present": False, "fileName": path.name}
    stat = path.stat()
    payload: dict[str, Any] = {
        "present": True,
        "fileName": path.name,
        "mtime": stat.st_mtime,
        "mtimeUtc": _iso_from_timestamp(stat.st_mtime),
        "ageSeconds": _rounded_age(now_ts - stat.st_mtime),
    }
    try:
        parsed = parser(path)
        if isinstance(parsed, dict):
            payload.update(parsed)
    except Exception as exc:
        payload["parseError"] = type(exc).__name__
    return payload


def _public_health_file(probe: dict[str, Any], *, fields: tuple[str, ...]) -> dict[str, Any]:
    result = {
        "present": bool(probe.get("present")),
        "fileName": probe.get("fileName"),
        "ageSeconds": _rounded_age(probe.get("ageSeconds")),
        "mtimeUtc": probe.get("mtimeUtc"),
    }
    if probe.get("parseError"):
        result["parseError"] = probe.get("parseError")
    source_fields = probe.get("fields") if isinstance(probe.get("fields"), dict) else {}
    for key in fields:
        if key in source_fields:
            result[key] = source_fields.get(key)
    return result


def _pending_health_status(mt5_process_running: bool | None) -> tuple[str, str, str, str]:
    if mt5_process_running is False:
        return (
            "mt5_bridge_no_responde_o_no_esta_activo",
            "mt5_bridge_no_responde_o_no_esta_activo",
            "bad",
            "start_or_repair_internal_mt5_bridge_runner",
        )
    if mt5_process_running is True:
        return (
            "mt5_bridge_ea_no_responde",
            "mt5_bridge_ea_no_responde",
            "bad",
            "check_ea_attached_algo_trading_or_restart_bridge",
        )
    return (
        "mt5_bridge_latest_desfasado",
        "mt5_bridge_latest_desfasado",
        "hold",
        "wait_or_check_mt5_bridge_runner",
    )


def _detect_mt5_process_running() -> bool | None:
    if not subprocess:
        return None
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    output = result.stdout.lower()
    return any(name.lower() in output for name in MT5_PROCESS_NAMES)


def _handle_error(action: str, error: BridgeError) -> dict[str, Any]:
    payload = _base_payload(action)
    payload.update({
        "ok": False,
        "status": "blocked",
        "error": error.code,
        "details": error.details,
        "blockers": [error.code],
    })
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 bridge gate")
    parser.add_argument("action", choices=("status", "request-template", "write-request", "install-source", "validate-response", "health"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--symbol", default="USDJPY_Darwinex")
    parser.add_argument("--request-id", default=None)
    parser.add_argument("--spread-timeframe", default="M1")
    parser.add_argument("--from-year", type=int, default=0)
    parser.add_argument("--to-year", type=int, default=0)
    parser.add_argument("--max-bars", type=int, default=0)
    parser.add_argument("--spread-policy", default=DEFAULT_SPREAD_POLICY)
    parser.add_argument("--mt5-files-dir", default=None)
    parser.add_argument("--mt5-experts-dir", default=None)
    parser.add_argument("--response-path", default=None)
    parser.add_argument("--expected-request-id", default=None)
    parser.add_argument("--expected-symbol", default=None)
    parser.add_argument("--stale-after-seconds", type=int, default=DEFAULT_HEALTH_STALE_AFTER_SECONDS)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root, mt5_files_dir=args.mt5_files_dir, mt5_experts_dir=args.mt5_experts_dir)
        elif args.action == "request-template":
            payload = request_template_payload(
                symbol=args.symbol,
                request_id=args.request_id,
                spread_timeframe=args.spread_timeframe,
                from_year=args.from_year,
                to_year=args.to_year,
                max_bars=args.max_bars,
            )
        elif args.action == "write-request":
            payload = write_request_payload(
                symbol=args.symbol,
                mt5_files_dir=args.mt5_files_dir,
                project_root=args.project_root,
                request_id=args.request_id,
                spread_timeframe=args.spread_timeframe,
                from_year=args.from_year,
                to_year=args.to_year,
                max_bars=args.max_bars,
                apply=args.apply,
            )
        elif args.action == "install-source":
            payload = install_source_payload(args.project_root, mt5_experts_dir=args.mt5_experts_dir, apply=args.apply, overwrite=args.overwrite)
        elif args.action == "validate-response":
            payload = validate_response_payload(response_path=args.response_path, spread_policy=args.spread_policy)
        else:
            payload = health_payload(
                project_root=args.project_root,
                mt5_files_dir=args.mt5_files_dir,
                mt5_experts_dir=args.mt5_experts_dir,
                expected_request_id=args.expected_request_id,
                expected_symbol=args.expected_symbol,
                stale_after_seconds=args.stale_after_seconds,
            )
    except BridgeError as exc:
        payload = _handle_error(args.action, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
