from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import sqx144_mt5_auto10_internal_runner as auto10
from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO11_VERSION = "sqx144-mt5-auto11-ea-attach-runner-v1"
SQX144_MT5_AUTO11_PHASE = "SQX144-MT5-AUTO11"
SQX144_MT5_AUTO11_STATUS = "auto11_ea_attach_runner_source_ready_no_attach_no_launch_no_run_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool"
SQX144_MT5_AUTO11_PROFILE_WRITER_STATUS = "auto11_attach_profile_writer_implemented_no_apply_no_ui_fallback_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool"
AUTO11_ATTACH_APPROVAL_PHRASE = "APRUEBO SQX144 MT5 AUTO11 EA ATTACH RUNNER APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool"
AUTO11_UI_FALLBACK_APPROVAL_PHRASE = "APRUEBO SQX144 MT5 AUTO11 UI FALLBACK APPLY host=sqx144_full mt5=darwinex symbol=USDJPY_Darwinex timeframe=M1 visible_operator_control no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool"

DEFAULT_HOST = "sqx144_full"
DEFAULT_MT5_PROFILE = "darwinex"
DEFAULT_SYMBOL = auto10.DEFAULT_SMOKE_SYMBOL
DEFAULT_TIMEFRAME = "M1"
DEFAULT_PROFILE_PREFIX = "SQX_AUTO11_BRIDGE"
DEFAULT_TEMPLATE_NAME = "SQX_AUTO11_SQXInfoBridge.tpl"
DEFAULT_STARTUP_CONFIG_NAME = "SQX_AUTO11_startup.ini"
DEFAULT_CHART_FILE_NAME = "chart01.chr"
DEFAULT_ORDER_FILE_NAME = "order.wnd"
SUPPORTED_TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}
TIMEFRAME_TO_PERIOD = {
    "M1": (1, 1),
    "M5": (1, 5),
    "M15": (1, 15),
    "M30": (0, 30),
    "H1": (1, 1),
    "H4": (1, 4),
    "D1": (1, 24),
}
TIMEFRAME_TO_MQL5 = {
    "M1": "PERIOD_M1",
    "M5": "PERIOD_M5",
    "M15": "PERIOD_M15",
    "M30": "PERIOD_M30",
    "H1": "PERIOD_H1",
    "H4": "PERIOD_H4",
    "D1": "PERIOD_D1",
}


class Auto11Error(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO11_VERSION,
        "phase": SQX144_MT5_AUTO11_PHASE,
        "statusMarker": SQX144_MT5_AUTO11_STATUS,
        "action": action,
        "host": DEFAULT_HOST,
        "mt5Profile": DEFAULT_MT5_PROFILE,
        "genericMt5SqxProfileAware": True,
        "sourceReadyOnly": True,
        "autoStartAllowed": False,
        "attachAllowedByGate": False,
        "uiFallbackAllowedByGate": False,
        "writesMt5Profile": False,
        "writesMt5Template": False,
        "writesMt5StartupConfig": False,
        "writesMt5Chart": False,
        "writesMt5Files": False,
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "placesOrders": False,
        "usesMigrationTool": False,
        "directDbHistoryInsertAllowed": False,
        "historyImportAllowed": False,
        "usesDataSourceHistoryImport": False,
        "requiresExactAttachGate": True,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "tokensReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def _normalise_timeframe(value: str | None) -> str:
    timeframe = str(value or DEFAULT_TIMEFRAME).upper()
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise Auto11Error("auto11_timeframe_not_supported", details={"timeframe": timeframe})
    return timeframe


def _local_auto11_root(project_root: Path) -> Path:
    return project_root / ".local" / "mt5_auto11"


def _path_is_within(path: Path, parent: Path) -> bool:
    resolved_path = path.resolve(strict=False)
    resolved_parent = parent.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_parent)
    except ValueError:
        return False
    return True


def _mt5_data_dir_from_paths(
    *,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
) -> Path:
    files_dir = Path(mt5_files_dir or bridge.DEFAULT_MT5_FILES_DIR)
    experts_dir = Path(mt5_experts_dir or bridge.DEFAULT_MT5_EXPERTS_DIR)
    files_data_dir = files_dir.parent.parent
    experts_data_dir = experts_dir.parent.parent
    if files_data_dir.resolve(strict=False) != experts_data_dir.resolve(strict=False):
        raise Auto11Error("auto11_mt5_files_and_experts_dir_mismatch")
    return files_data_dir


def _require_allowed_data_dir(data_dir: Path, *, project_root: Path) -> None:
    default_data_dir = bridge.DEFAULT_MT5_FILES_DIR.parent.parent
    resolved = data_dir.resolve(strict=False)
    if resolved == default_data_dir.resolve(strict=False):
        return
    if _path_is_within(resolved, _local_auto11_root(project_root)):
        return
    raise Auto11Error("auto11_mt5_data_dir_not_allowed")


def _safe_token(value: str, *, fallback: str) -> str:
    token = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(value or ""))
    token = "_".join(part for part in token.split("_") if part)
    return token[:80] or fallback


def _profile_name(*, mt5_profile: str, symbol: str, timeframe: str) -> str:
    return "_".join([
        DEFAULT_PROFILE_PREFIX,
        _safe_token(mt5_profile, fallback="mt5"),
        _safe_token(symbol, fallback="symbol"),
        _safe_token(timeframe, fallback="tf"),
    ])[:120]


def _chart_symbol(symbol: str, mt5_profile: str) -> str:
    value = str(symbol or DEFAULT_SYMBOL)
    if str(mt5_profile or "").lower() == "darwinex":
        for suffix in ("_Darwinex", "_darwinex"):
            if value.endswith(suffix):
                return value[: -len(suffix)]
    return value


def _file_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _profile_paths(
    project_root: Path,
    *,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
    mt5_profile: str = DEFAULT_MT5_PROFILE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> dict[str, Path | str]:
    tf = _normalise_timeframe(timeframe)
    data_dir = _mt5_data_dir_from_paths(mt5_files_dir=mt5_files_dir, mt5_experts_dir=mt5_experts_dir)
    name = _profile_name(mt5_profile=mt5_profile, symbol=symbol, timeframe=tf)
    profile_dir = data_dir / "MQL5" / "Profiles" / "Charts" / name
    templates_dir = data_dir / "MQL5" / "Profiles" / "Templates"
    startup_dir = _local_auto11_root(project_root) / "startup"
    return {
        "dataDir": data_dir,
        "profileName": name,
        "profileDir": profile_dir,
        "chartFile": profile_dir / DEFAULT_CHART_FILE_NAME,
        "orderFile": profile_dir / DEFAULT_ORDER_FILE_NAME,
        "templateFile": templates_dir / DEFAULT_TEMPLATE_NAME,
        "startupConfigFile": startup_dir / f"{name}_{DEFAULT_STARTUP_CONFIG_NAME}",
    }


def _chart_text(*, chart_symbol: str, timeframe: str) -> str:
    tf = _normalise_timeframe(timeframe)
    period_type, period_size = TIMEFRAME_TO_PERIOD[tf]
    mql5_tf = TIMEFRAME_TO_MQL5[tf]
    chart_id = int(time.time() * 1000)
    return f"""<chart>
id={chart_id}
symbol={chart_symbol}
description=SQX AUTO11 SQXInfoBridge
period_type={period_type}
period_size={period_size}
digits=3
tick_size=0.000000
position_time=0
scale_fix=0
scale_fixed_min=0.000000
scale_fixed_max=0.000000
scale_fix11=0
scale_bar=0
scale_bar_val=1.000000
scale=4
mode=1
fore=0
grid=1
volume=0
scroll=1
shift=0
shift_size=20.000000
fixed_pos=0.000000
ohlc=0
one_click=0
one_click_btn=0
bidline=1
askline=0
lastline=0
days=1
descriptions=0
tradelines=0
tradehistory=0
window_left=0
window_top=0
window_right=1100
window_bottom=700
window_type=1
background_color=0
foreground_color=16777215
barup_color=65280
bardown_color=65280
bullcandle_color=0
bearcandle_color=16777215
chartline_color=65280
volumes_color=3329330
grid_color=10061943
bidline_color=10061943
askline_color=255
lastline_color=49152
stops_color=255
windows_total=1

<expert>
name=SQXInfoBridge
path=Experts\\SQXInfoBridge.ex5
expertmode=0
<inputs>
InpRequestFile=SQXInfoBridge.request.ini
InpLatestResponseFile=SQXInfoBridge.latest.json
InpPollSeconds=2
InpDefaultSpreadTimeframe={mql5_tf}
InpFallbackStartYear=2000
InpMaxBars=0
</inputs>
</expert>

<window>
height=100.000000
objects=0

<indicator>
name=Main
path=
apply=1
show_data=1
scale_inherit=0
scale_line=0
scale_line_percent=50
scale_line_value=0.000000
scale_fix_min=0
scale_fix_min_val=0.000000
scale_fix_max=0
scale_fix_max_val=0.000000
expertmode=0
fixed_height=-1
</indicator>
</window>
</chart>
"""


def _startup_config_text(*, chart_symbol: str, timeframe: str, profile_name: str) -> str:
    return f"""[StartUp]
Expert=SQXInfoBridge
Symbol={chart_symbol}
Period={timeframe}
Template={DEFAULT_TEMPLATE_NAME}
Profile={profile_name}

[SQX]
Version={SQX144_MT5_AUTO11_VERSION}
Purpose=SQXInfoBridge profile attach
"""


def _write_text_utf16(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-16")


def _write_profile_assets(
    project_root: Path,
    *,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
    mt5_profile: str = DEFAULT_MT5_PROFILE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> dict[str, Any]:
    paths = _profile_paths(
        project_root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
        mt5_profile=mt5_profile,
        symbol=symbol,
        timeframe=timeframe,
    )
    data_dir = Path(paths["dataDir"])
    _require_allowed_data_dir(data_dir, project_root=project_root)
    tf = _normalise_timeframe(timeframe)
    chart_symbol = _chart_symbol(symbol, mt5_profile)
    chart_text = _chart_text(chart_symbol=chart_symbol, timeframe=tf)
    config_text = _startup_config_text(chart_symbol=chart_symbol, timeframe=tf, profile_name=str(paths["profileName"]))
    _write_text_utf16(Path(paths["templateFile"]), chart_text)
    _write_text_utf16(Path(paths["chartFile"]), chart_text)
    _write_text_utf16(Path(paths["orderFile"]), f"{DEFAULT_CHART_FILE_NAME}\r\n")
    _write_text_utf16(Path(paths["startupConfigFile"]), config_text)
    return {
        "profileName": str(paths["profileName"]),
        "chartSymbol": chart_symbol,
        "templateFileName": Path(paths["templateFile"]).name,
        "chartFileName": Path(paths["chartFile"]).name,
        "orderFileName": Path(paths["orderFile"]).name,
        "startupConfigFileName": Path(paths["startupConfigFile"]).name,
        "templateSha256": _file_hash(Path(paths["templateFile"])),
        "chartSha256": _file_hash(Path(paths["chartFile"])),
        "startupConfigSha256": _file_hash(Path(paths["startupConfigFile"])),
    }


def _resolve_target_terminal(project_root: Path, *, mt5_root: str | Path | None = None) -> Path:
    root = Path(mt5_root or auto10.DEFAULT_MT5_ROOT)
    return root / auto10.DEFAULT_TERMINAL_EXE_NAME


def _target_process_state(target_terminal: Path) -> dict[str, Any]:
    return auto10._detect_process_state(target_terminal)  # noqa: SLF001 - AUTO11 shares the governed AUTO10 target detector.


def _restore_visible_target_window(process_state: dict[str, Any]) -> dict[str, Any]:
    target_pids = [int(pid) for pid in (process_state.get("_targetPids") or []) if int(pid or 0) > 0]
    result: dict[str, Any] = {
        "windowFound": False,
        "windowRestored": False,
        "windowForegroundRequested": False,
        "windowTitleReturned": False,
    }
    if not target_pids:
        return result
    try:
        import win32con  # type: ignore
        import win32gui  # type: ignore
        import win32process  # type: ignore
    except Exception as exc:
        result.update({"windowAutomationAvailable": False, "windowAutomationError": type(exc).__name__})
        return result

    candidates: list[int] = []

    def _enum(hwnd: int, _extra: object) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return
        _thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
        if int(pid or 0) in target_pids:
            candidates.append(hwnd)

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception as exc:
        result.update({"windowAutomationAvailable": False, "windowAutomationError": type(exc).__name__})
        return result
    if not candidates:
        return result
    hwnd = candidates[0]
    result["windowFound"] = True
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            result["windowRestored"] = True
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
            result["windowRestored"] = True
    except Exception as exc:
        result["windowRestoreError"] = type(exc).__name__
    try:
        win32gui.SetForegroundWindow(hwnd)
        result["windowForegroundRequested"] = True
    except Exception as exc:
        result["windowForegroundError"] = type(exc).__name__
    return result


def _profile_handoff_to_mt5(
    *,
    terminal_exe: Path,
    profile_name: str,
    startup_config_file: Path,
    process_before: dict[str, Any],
) -> dict[str, Any]:
    if not terminal_exe.is_file():
        raise Auto11Error("auto11_ui_fallback_terminal_exe_missing")
    if not startup_config_file.is_file():
        raise Auto11Error("auto11_ui_fallback_startup_config_missing")
    before_count = int(process_before.get("targetProcessCount") or 0)
    args = [
        str(terminal_exe),
        f"/profile:{profile_name}",
        f"/config:{startup_config_file}",
    ]
    try:
        proc = subprocess.Popen(
            args,
            cwd=str(terminal_exe.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:
        raise Auto11Error("auto11_ui_fallback_profile_handoff_failed", details={"error": type(exc).__name__}) from exc
    time.sleep(5)
    return_code: int | None
    try:
        return_code = proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        return_code = None
    process_after = _target_process_state(terminal_exe)
    after_count = int(process_after.get("targetProcessCount") or 0)
    return {
        "executed": True,
        "method": "visible_terminal_profile_config_handoff",
        "returnCode": return_code,
        "handoffProcessStillRunning": return_code is None,
        "targetProcessCountBefore": before_count,
        "targetProcessCountAfter": after_count,
        "newTargetProcessObserved": after_count > before_count,
        "process": auto10._public_process_state(process_after),  # noqa: SLF001 - public sanitizer reused from AUTO10.
        "commandLineReturned": False,
        "localPathsReturned": False,
    }


def _verify_ui_fallback_heartbeat(
    project_root: Path,
    *,
    symbol: str,
    timeframe: str,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    request_id = f"sqx_auto11_ui_{''.join(ch if ch.isalnum() else '_' for ch in symbol)}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    request = bridge.write_request_payload(
        symbol=symbol,
        project_root=project_root,
        request_id=request_id,
        spread_timeframe=timeframe,
        apply=True,
    )
    deadline = time.time() + max(5, int(timeout_seconds or 30))
    latest_health: dict[str, Any] = {}
    while time.time() < deadline:
        latest_health = bridge.health_payload(project_root=project_root, expected_request_id=request_id, expected_symbol=symbol)
        if latest_health.get("panelStatus") == "mt5_bridge_ready_latest_matches_request":
            break
        time.sleep(1)
    return {
        "ok": latest_health.get("panelStatus") == "mt5_bridge_ready_latest_matches_request",
        "requestWritten": bool(request.get("ok")),
        "requestId": request_id,
        "status": "auto11_ui_fallback_bridge_ready" if latest_health.get("panelStatus") == "mt5_bridge_ready_latest_matches_request" else "auto11_ui_fallback_bridge_timeout",
        "bridgeHealth": auto10._public_health(latest_health),  # noqa: SLF001 - public sanitizer reused from AUTO10.
    }


def profile_catalog_payload(project_root: str | Path) -> dict[str, Any]:
    _project_root(project_root)
    payload = _base_payload("profile-catalog")
    payload.update({
        "ok": True,
        "status": "auto11_profile_catalog_ready",
        "profileContract": {
            "identity": ["host", "mt5Profile", "symbol", "timeframe"],
            "requiredCapabilities": [
                "terminalExeKnown",
                "mql5FilesDirKnown",
                "mql5ExpertsDirKnown",
                "mql5ProfilesDirKnown",
                "sqxInfoBridgeInstalled",
                "bridgeHeartbeatVerifiable",
            ],
            "brokerProfiles": [
                {
                    "host": DEFAULT_HOST,
                    "mt5Profile": "darwinex",
                    "status": "active_profile_from_auto10",
                    "defaultSymbol": DEFAULT_SYMBOL,
                    "defaultTimeframe": DEFAULT_TIMEFRAME,
                    "usesAuto10LaunchAndVerify": True,
                },
                {
                    "host": DEFAULT_HOST,
                    "mt5Profile": "future_mt5_profile",
                    "status": "planned_requires_discovery",
                    "defaultSymbol": "<broker_symbol>",
                    "defaultTimeframe": DEFAULT_TIMEFRAME,
                    "usesAuto10LaunchAndVerify": True,
                },
            ],
        },
        "nonMt5Routes": {
            "dukascopySuffix": "*_dukascopy",
            "route": "AUTO7 mirror/no-MT5",
        },
    })
    return payload


def preflight_payload(
    project_root: str | Path,
    *,
    mt5_root: str | Path | None = None,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
) -> dict[str, Any]:
    auto10_preflight = auto10.preflight_payload(
        project_root,
        mt5_root=mt5_root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
    )
    health = bridge.health_payload(project_root=project_root)
    payload = _base_payload("preflight")
    blockers = list(auto10_preflight.get("blockers") or [])
    payload.update({
        "ok": not blockers,
        "status": "auto11_preflight_ready_no_attach" if not blockers else "auto11_preflight_blocked_no_attach",
        "blockers": blockers,
        "warnings": list(auto10_preflight.get("warnings") or []),
        "auto10PreflightStatus": auto10_preflight.get("status"),
        "bridgeHealthStatus": health.get("panelStatus"),
        "attachPlanAvailable": True,
        "attachExecuted": False,
    })
    return payload


def plan_payload(
    project_root: str | Path,
    *,
    host: str = DEFAULT_HOST,
    mt5_profile: str = DEFAULT_MT5_PROFILE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
) -> dict[str, Any]:
    _project_root(project_root)
    tf = _normalise_timeframe(timeframe)
    payload = _base_payload("plan")
    payload.update({
        "ok": True,
        "status": SQX144_MT5_AUTO11_STATUS,
        "host": host,
        "mt5Profile": mt5_profile,
        "symbol": symbol,
        "timeframe": tf,
        "goal": "generic EA attach/profile automation for any governed SQX host plus MT5 profile pair",
        "preferredAutomationPath": "template_profile_autoload_then_auto10_heartbeat_verify",
        "candidateApproaches": [
            "prepare governed MT5 chart/profile/template with SQXInfoBridge attached to symbol/timeframe",
            "launch or reuse target MT5 through AUTO10 and verify a fresh bridge heartbeat",
            "use visible operator-approved UI automation only as fallback when MT5 profile/template autoload cannot be proven",
        ],
        "allowedNow": {
            "reportProfileCatalog": True,
            "reportAttachPlan": True,
            "returnApprovalTemplate": True,
            "writeMt5Template": False,
            "writeMt5Profile": False,
            "launchMt5": False,
            "attachEa": False,
            "runEa": False,
        },
        "afterAttachGate": {
            "writeGovernedTemplateOrProfile": True,
            "reuseAuto10Launch": True,
            "verifyFreshHeartbeat": True,
            "stopOnlyManagedAuto10PidWhenRequested": True,
        },
        "fallbackGate": {
            "uiAutomationAllowed": False,
            "requiresSeparateApproval": True,
            "approvalTemplateName": "uiFallback",
        },
        "approvalTemplates": approval_template_payload(project_root)["approvalTemplates"],
    })
    return payload


def attach_plan_payload(
    project_root: str | Path,
    *,
    host: str = DEFAULT_HOST,
    mt5_profile: str = DEFAULT_MT5_PROFILE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
    approval: str | None = None,
    apply: bool = False,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    tf = _normalise_timeframe(timeframe)
    paths = _profile_paths(
        root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
        mt5_profile=mt5_profile,
        symbol=symbol,
        timeframe=tf,
    )
    payload = _base_payload("attach-plan")
    payload.update({
        "ok": True,
        "status": "auto11_attach_plan_ready_apply_required",
        "host": host,
        "mt5Profile": mt5_profile,
        "symbol": symbol,
        "timeframe": tf,
        "profileName": paths["profileName"],
        "templateFileName": DEFAULT_TEMPLATE_NAME,
        "startupConfigFileName": Path(paths["startupConfigFile"]).name,
        "chartSymbol": _chart_symbol(symbol, mt5_profile),
        "wouldWriteMt5Template": True,
        "wouldWriteMt5Profile": True,
        "wouldWriteMt5StartupConfig": True,
        "wouldAttachSqxInfoBridge": True,
        "wouldLaunchOrReuseMt5ViaAuto10": True,
        "wouldVerifyFreshHeartbeat": True,
        "uiFallbackRequired": False,
    })
    if not apply:
        return payload
    if str(approval or "").strip() != AUTO11_ATTACH_APPROVAL_PHRASE:
        raise Auto11Error("auto11_attach_requires_exact_approval")
    assets = _write_profile_assets(
        root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
        mt5_profile=mt5_profile,
        symbol=symbol,
        timeframe=tf,
    )
    auto10_preflight = auto10.preflight_payload(root, mt5_files_dir=mt5_files_dir, mt5_experts_dir=mt5_experts_dir)
    process = (auto10_preflight.get("discovery") or {}).get("process") or {}
    existing_target_running = process.get("targetTerminalProcessRunning") is True
    payload.update({
        "ok": True,
        "status": "auto11_attach_profile_writer_completed_existing_mt5_requires_verify_or_ui_fallback"
        if existing_target_running else "auto11_attach_profile_writer_completed_ready_for_profile_launch",
        "statusMarker": SQX144_MT5_AUTO11_PROFILE_WRITER_STATUS,
        "sourceReadyOnly": False,
        "attachAllowedByGate": True,
        "writesMt5Template": True,
        "writesMt5Profile": True,
        "writesMt5StartupConfig": True,
        "writesMt5Chart": True,
        "writesMt5Files": True,
        "attachExecuted": False,
        "runsMt5Ea": False,
        "launchesMt5": False,
        "profileAssets": assets,
        "existingTargetMt5Running": existing_target_running,
        "nextAction": "run_auto10_verify_if_mt5_loaded_profile_or_use_ui_fallback_gate"
        if existing_target_running else "launch_mt5_with_generated_profile_then_verify_heartbeat",
        "uiFallbackRequired": existing_target_running,
    })
    return payload


def ui_fallback_plan_payload(
    project_root: str | Path,
    *,
    host: str = DEFAULT_HOST,
    mt5_profile: str = DEFAULT_MT5_PROFILE,
    symbol: str = DEFAULT_SYMBOL,
    timeframe: str = DEFAULT_TIMEFRAME,
    mt5_root: str | Path | None = None,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
    approval: str | None = None,
    apply: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    tf = _normalise_timeframe(timeframe)
    paths = _profile_paths(
        root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
        mt5_profile=mt5_profile,
        symbol=symbol,
        timeframe=tf,
    )
    payload = _base_payload("ui-fallback-plan")
    payload.update({
        "ok": True,
        "status": "auto11_ui_fallback_plan_ready_separate_gate_required",
        "host": host,
        "mt5Profile": mt5_profile,
        "symbol": symbol,
        "timeframe": tf,
        "wouldUseVisibleOperatorControl": True,
        "wouldOpenTargetChart": True,
        "wouldAttachSqxInfoBridge": True,
        "wouldAllowAlgoTradingIfPrompted": True,
        "wouldVerifyFreshHeartbeat": True,
        "profileName": paths["profileName"],
        "templateFileName": DEFAULT_TEMPLATE_NAME,
        "startupConfigFileName": Path(paths["startupConfigFile"]).name,
        "uiFallbackAllowedByGate": False,
    })
    if not apply:
        return payload
    if str(approval or "").strip() != AUTO11_UI_FALLBACK_APPROVAL_PHRASE:
        raise Auto11Error("auto11_ui_fallback_requires_exact_approval")
    _require_allowed_data_dir(Path(paths["dataDir"]), project_root=root)
    missing_assets = [
        name
        for name, path in (
            ("template", paths["templateFile"]),
            ("chart", paths["chartFile"]),
            ("order", paths["orderFile"]),
            ("startupConfig", paths["startupConfigFile"]),
        )
        if not Path(path).is_file()
    ]
    if missing_assets:
        raise Auto11Error("auto11_ui_fallback_profile_assets_missing_run_attach_writer_first", details={"missingAssets": missing_assets})
    terminal = _resolve_target_terminal(root, mt5_root=mt5_root)
    process_before = _target_process_state(terminal)
    if process_before.get("targetTerminalProcessRunning") is not True:
        raise Auto11Error("auto11_ui_fallback_requires_existing_target_mt5")
    restore = _restore_visible_target_window(process_before)
    handoff = _profile_handoff_to_mt5(
        terminal_exe=terminal,
        profile_name=str(paths["profileName"]),
        startup_config_file=Path(paths["startupConfigFile"]),
        process_before=process_before,
    )
    verify = _verify_ui_fallback_heartbeat(root, symbol=symbol, timeframe=tf)
    payload.update({
        "ok": bool(verify.get("ok")),
        "status": "auto11_ui_fallback_completed_bridge_ready" if verify.get("ok") else "auto11_ui_fallback_completed_bridge_timeout",
        "statusMarker": "auto11_ui_fallback_apply_visible_operator_control_completed",
        "sourceReadyOnly": False,
        "uiFallbackAllowedByGate": True,
        "visibleOperatorControl": True,
        "windowAutomation": restore,
        "profileHandoff": handoff,
        "heartbeatVerify": verify,
        "writesMt5Files": True,
        "launchesMt5": bool(handoff.get("newTargetProcessObserved")),
        "runsMt5Ea": bool(verify.get("ok")),
        "placesOrders": False,
        "nextAction": "bridge_ready_continue_auto10_flow" if verify.get("ok") else "operator_visible_mt5_check_ea_attach_or_use_profile_config_relaunch_gate",
    })
    return payload


def status_payload(project_root: str | Path) -> dict[str, Any]:
    payload = _base_payload("status")
    payload.update({
        "ok": True,
        "status": SQX144_MT5_AUTO11_STATUS,
        "profileWriterStatus": SQX144_MT5_AUTO11_PROFILE_WRITER_STATUS,
        "actions": ["status", "profile-catalog", "preflight", "plan", "attach-plan", "ui-fallback-plan", "approval-template"],
        "endpoints": [
            "/api/sqx144/mt5-auto11/status",
            "/api/sqx144/mt5-auto11/profile-catalog",
            "/api/sqx144/mt5-auto11/preflight",
            "/api/sqx144/mt5-auto11/plan",
            "/api/sqx144/mt5-auto11/attach-plan",
            "/api/sqx144/mt5-auto11/ui-fallback-plan",
        ],
        "catalog": profile_catalog_payload(project_root).get("profileContract"),
        "approvalTemplates": approval_template_payload(project_root)["approvalTemplates"],
    })
    return payload


def approval_template_payload(project_root: str | Path) -> dict[str, Any]:
    _project_root(project_root)
    payload = _base_payload("approval-template")
    payload.update({
        "ok": True,
        "status": "auto11_approval_templates_ready",
        "approvalTemplates": {
            "attach": AUTO11_ATTACH_APPROVAL_PHRASE,
            "uiFallback": AUTO11_UI_FALLBACK_APPROVAL_PHRASE,
        },
        "notes": [
            "AUTO11 is generic over host, mt5Profile, symbol and timeframe.",
            "The attach gate prepares a governed MT5 profile/template/startup config and then expects heartbeat verification.",
            "The UI fallback gate is separate and visible/operator-controlled.",
            "Neither gate allows data.db writes, history import, projects, databanks, SQX tasks, orders or Migration Tool.",
        ],
    })
    return payload


def error_payload(action: str, error: Exception) -> dict[str, Any]:
    code = getattr(error, "code", str(error))
    payload = _base_payload(action)
    payload.update({
        "status": "blocked",
        "error": code,
        "details": getattr(error, "details", {}),
        "blockers": [code],
    })
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO11 generic EA attach/profile runner gate")
    parser.add_argument("action", choices=("status", "profile-catalog", "preflight", "plan", "attach-plan", "ui-fallback-plan", "approval-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--mt5-profile", default=DEFAULT_MT5_PROFILE)
    parser.add_argument("--mt5-root", default=None)
    parser.add_argument("--mt5-files-dir", default=None)
    parser.add_argument("--mt5-experts-dir", default=None)
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL)
    parser.add_argument("--timeframe", default=DEFAULT_TIMEFRAME)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root)
        elif args.action == "profile-catalog":
            payload = profile_catalog_payload(args.project_root)
        elif args.action == "preflight":
            payload = preflight_payload(args.project_root, mt5_root=args.mt5_root, mt5_files_dir=args.mt5_files_dir, mt5_experts_dir=args.mt5_experts_dir)
        elif args.action == "plan":
            payload = plan_payload(args.project_root, host=args.host, mt5_profile=args.mt5_profile, symbol=args.symbol, timeframe=args.timeframe)
        elif args.action == "attach-plan":
            payload = attach_plan_payload(
                args.project_root,
                host=args.host,
                mt5_profile=args.mt5_profile,
                symbol=args.symbol,
                timeframe=args.timeframe,
                approval=args.approval,
                apply=args.apply,
                mt5_files_dir=args.mt5_files_dir,
                mt5_experts_dir=args.mt5_experts_dir,
            )
        elif args.action == "ui-fallback-plan":
            payload = ui_fallback_plan_payload(
                args.project_root,
                host=args.host,
                mt5_profile=args.mt5_profile,
                symbol=args.symbol,
                timeframe=args.timeframe,
                mt5_root=args.mt5_root,
                mt5_files_dir=args.mt5_files_dir,
                mt5_experts_dir=args.mt5_experts_dir,
                approval=args.approval,
                apply=args.apply,
            )
        else:
            payload = approval_template_payload(args.project_root)
    except (Auto11Error, auto10.Auto10Error, bridge.BridgeError) as exc:
        payload = error_payload(args.action, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
