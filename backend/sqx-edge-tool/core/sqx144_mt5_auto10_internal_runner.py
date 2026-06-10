from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO10_VERSION = "sqx144-mt5-auto10-internal-mt5-runner-v1"
SQX144_MT5_AUTO10_PHASE = "SQX144-MT5-AUTO10"
SQX144_MT5_AUTO10_STATUS = "auto10_internal_mt5_runner_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_history_import_no_migration_tool"
SQX144_MT5_AUTO10_INSTALL_STATUS = "auto10_internal_mt5_runner_install_gate_ready_no_apply"
SQX144_MT5_AUTO10_LAUNCH_STATUS = "auto10_internal_mt5_runner_launch_gate_ready_no_apply"
AUTO10_INSTALL_APPROVAL_PHRASE = "APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER INSTALL host=sqx144_full mt5=darwinex no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool"
AUTO10_LAUNCH_APPROVAL_PHRASE = "APRUEBO SQX144 MT5 AUTO10 INTERNAL RUNNER LAUNCH host=sqx144_full mt5=darwinex hidden_or_minimized no_db_no_projects_no_databanks_no_tasks no_history_import no_migration_tool"

DEFAULT_MT5_ROOT = Path("C:/Program Files/Darwinex MetaTrader 5")
DEFAULT_TERMINAL_EXE_NAME = "terminal64.exe"
DEFAULT_METAEDITOR_EXE_NAME = "MetaEditor64.exe"
DEFAULT_BRIDGE_SOURCE_NAME = "SQXInfoBridge.mq5"
DEFAULT_BRIDGE_BINARY_NAME = "SQXInfoBridge.ex5"
DEFAULT_SMOKE_SYMBOL = "USDJPY_Darwinex"
DEFAULT_READY_TIMEOUT_SECONDS = 45
MANAGED_PID_FILE_NAME = "managed_terminal.json"
MT5_WINDOW_STYLES = {"hidden", "minimized"}


class Auto10Error(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _source_mq5(project_root: Path) -> Path:
    return project_root / "integrations" / "sqx144" / "mt5_bridge" / DEFAULT_BRIDGE_SOURCE_NAME


def _managed_root(project_root: Path) -> Path:
    return project_root / ".local" / "mt5_runner"


def _managed_pid_file(project_root: Path) -> Path:
    return _managed_root(project_root) / MANAGED_PID_FILE_NAME


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _file_state(path: Path, label: str, *, hash_file: bool = False) -> dict[str, Any]:
    state: dict[str, Any] = {
        "label": label,
        "present": path.is_file(),
        "fileName": path.name,
    }
    if hash_file and path.is_file():
        state["sha256"] = _sha256(path)
    return state


def _dir_state(path: Path, label: str) -> dict[str, Any]:
    return {
        "label": label,
        "present": path.is_dir(),
    }


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO10_VERSION,
        "phase": SQX144_MT5_AUTO10_PHASE,
        "statusMarker": SQX144_MT5_AUTO10_STATUS,
        "action": action,
        "host": "sqx144_full",
        "mt5Profile": "darwinex",
        "sourceReadyNoLaunch": True,
        "autoStartAllowed": False,
        "installSourceAllowedByGate": False,
        "launchesMt5AllowedByGate": False,
        "runsMt5EaAllowedByGate": False,
        "writesMt5Source": False,
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
        "doesNotApplyToSqx": True,
        "doesNotApplyInstrumentConfig": True,
        "stopsOnlyManagedAuto10Pid": True,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "tokensReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def _resolve_paths(
    *,
    project_root: Path,
    mt5_root: str | Path | None = None,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
) -> dict[str, Path]:
    root = Path(mt5_root or DEFAULT_MT5_ROOT)
    files_dir = Path(mt5_files_dir or bridge.DEFAULT_MT5_FILES_DIR)
    experts_dir = Path(mt5_experts_dir or bridge.DEFAULT_MT5_EXPERTS_DIR)
    return {
        "source": _source_mq5(project_root),
        "mt5Root": root,
        "terminalExe": root / DEFAULT_TERMINAL_EXE_NAME,
        "metaeditorExe": root / DEFAULT_METAEDITOR_EXE_NAME,
        "filesDir": files_dir,
        "expertsDir": experts_dir,
        "installedMq5": experts_dir / DEFAULT_BRIDGE_SOURCE_NAME,
        "installedEx5": experts_dir / DEFAULT_BRIDGE_BINARY_NAME,
    }


def _read_managed_pid_record(project_root: Path) -> dict[str, Any] | None:
    path = _managed_pid_file(project_root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"parseError": True}
    if not isinstance(data, dict):
        return {"parseError": True}
    return data


def _normalise_process_path(value: str | Path) -> str:
    return os.path.normcase(str(Path(value).resolve(strict=False)))


def _terminal_processes() -> list[dict[str, Any]] | None:
    command = (
        "$items = @(Get-CimInstance Win32_Process -Filter \"name='terminal64.exe'\" "
        "| Select-Object ProcessId,ExecutablePath,CreationDate); "
        "ConvertTo-Json -InputObject $items -Depth 4"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    raw = (result.stdout or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return None
    processes: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        processes.append({
            "pid": int(item.get("ProcessId") or 0),
            "executablePath": str(item.get("ExecutablePath") or ""),
            "creationDate": str(item.get("CreationDate") or ""),
        })
    processes.sort(key=lambda item: item.get("creationDate") or "", reverse=True)
    return processes


def _public_process_state(state: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in state.items() if not key.startswith("_")}


def _detect_process_state(target_terminal: Path | None = None) -> dict[str, Any]:
    processes = _terminal_processes()
    if processes is not None:
        state: dict[str, Any] = {
            "known": True,
            "terminalProcessRunning": len(processes) > 0,
            "processCount": len(processes),
        }
        if target_terminal is not None:
            target = _normalise_process_path(target_terminal)
            target_matches = [
                process for process in processes
                if process.get("executablePath") and _normalise_process_path(process["executablePath"]) == target
            ]
            state.update({
                "targetTerminalProcessRunning": len(target_matches) > 0,
                "targetProcessCount": len(target_matches),
                "otherTerminalProcessCount": len(processes) - len(target_matches),
                "_targetPids": [
                    int(process["pid"])
                    for process in target_matches
                    if int(process.get("pid") or 0) > 0
                ],
            })
        return state
    try:
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
    except Exception:
        return {"known": False, "terminalProcessRunning": None, "processCount": None}
    if result.returncode != 0:
        return {"known": False, "terminalProcessRunning": None, "processCount": None}
    output = result.stdout.lower()
    count = sum(output.count(name.lower()) for name in bridge.MT5_PROCESS_NAMES)
    state = {"known": True, "terminalProcessRunning": count > 0, "processCount": count}
    if target_terminal is not None:
        state.update({
            "targetTerminalProcessRunning": None,
            "targetProcessCount": None,
            "otherTerminalProcessCount": None,
        })
    return state


def discover_payload(
    project_root: str | Path,
    *,
    mt5_root: str | Path | None = None,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    paths = _resolve_paths(
        project_root=root,
        mt5_root=mt5_root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
    )
    process = _detect_process_state(paths["terminalExe"])
    source_hash = _sha256(paths["source"])
    installed_hash = _sha256(paths["installedMq5"])
    managed_record = _read_managed_pid_record(root)
    payload = _base_payload("discover")
    payload.update({
        "ok": True,
        "status": "auto10_discovery_ready",
        "pathRefs": {
            "terminal": "darwinex_mt5_terminal_exe",
            "metaeditor": "darwinex_mt5_metaeditor_exe",
            "filesDir": "darwinex_terminal_mql5_files",
            "expertsDir": "darwinex_terminal_mql5_experts",
            "managedPidStore": "repo_local_mt5_runner_state",
        },
        "terminal": _file_state(paths["terminalExe"], "darwinex_mt5_terminal_exe"),
        "metaeditor": _file_state(paths["metaeditorExe"], "darwinex_mt5_metaeditor_exe"),
        "filesDir": _dir_state(paths["filesDir"], "darwinex_terminal_mql5_files"),
        "expertsDir": _dir_state(paths["expertsDir"], "darwinex_terminal_mql5_experts"),
        "bridgeSource": _file_state(paths["source"], "repo_sqx_info_bridge_source", hash_file=True),
        "installedBridgeSource": _file_state(paths["installedMq5"], "installed_sqx_info_bridge_source", hash_file=True),
        "installedBridgeBinary": _file_state(paths["installedEx5"], "installed_sqx_info_bridge_binary"),
        "sourceHashMatchesInstalled": bool(source_hash and installed_hash and source_hash == installed_hash),
        "process": _public_process_state(process),
        "managedPidRecorded": bool(managed_record and not managed_record.get("parseError")),
        "managedPidRecordReadable": managed_record is None or not bool(managed_record.get("parseError")),
        "requestFileName": bridge.DEFAULT_REQUEST_FILE,
        "responseFileName": bridge.DEFAULT_RESPONSE_FILE,
    })
    return payload


def preflight_payload(
    project_root: str | Path,
    *,
    mt5_root: str | Path | None = None,
    mt5_files_dir: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
) -> dict[str, Any]:
    discovery = discover_payload(
        project_root,
        mt5_root=mt5_root,
        mt5_files_dir=mt5_files_dir,
        mt5_experts_dir=mt5_experts_dir,
    )
    blockers: list[str] = []
    warnings: list[str] = []
    if not discovery["terminal"]["present"]:
        blockers.append("mt5_terminal_exe_missing")
    if not discovery["metaeditor"]["present"]:
        blockers.append("mt5_metaeditor_exe_missing")
    if not discovery["filesDir"]["present"]:
        blockers.append("mt5_files_dir_missing")
    if not discovery["expertsDir"]["present"]:
        blockers.append("mt5_experts_dir_missing")
    if not discovery["bridgeSource"]["present"]:
        blockers.append("bridge_source_missing")
    if not discovery["installedBridgeSource"]["present"]:
        warnings.append("bridge_source_not_installed_in_mt5")
    elif not discovery["sourceHashMatchesInstalled"]:
        warnings.append("bridge_source_hash_differs_from_installed")
    if not discovery["installedBridgeBinary"]["present"]:
        warnings.append("bridge_binary_not_detected")
    if discovery["managedPidRecordReadable"] is False:
        warnings.append("auto10_managed_pid_record_unreadable")

    payload = _base_payload("preflight")
    payload.update({
        "ok": not blockers,
        "status": "auto10_preflight_ready_no_launch" if not blockers else "auto10_preflight_blocked_no_launch",
        "blockers": blockers,
        "warnings": sorted(set(warnings)),
        "discovery": discovery,
        "requestWriteProbePlanned": True,
        "requestWriteProbeExecuted": False,
        "compilePlanned": True,
        "compileExecuted": False,
        "launchPlanned": True,
        "launchExecuted": False,
    })
    return payload


def status_payload(project_root: str | Path) -> dict[str, Any]:
    discovery = discover_payload(project_root)
    health = bridge.health_payload(project_root=project_root)
    payload = _base_payload("status")
    payload.update({
        "ok": True,
        "status": SQX144_MT5_AUTO10_STATUS,
        "installGateStatus": SQX144_MT5_AUTO10_INSTALL_STATUS,
        "launchGateStatus": SQX144_MT5_AUTO10_LAUNCH_STATUS,
        "endpoints": [
            "/api/sqx144/mt5-auto10/status",
            "/api/sqx144/mt5-auto10/preflight",
            "/api/sqx144/mt5-auto10/plan",
            "/api/sqx144/mt5-auto10/launch",
            "/api/sqx144/mt5-auto10/stop",
            "/api/sqx144/mt5-auto10/verify",
        ],
        "actions": ["status", "discover", "preflight", "plan", "install-source", "launch", "stop", "verify", "approval-template"],
        "discovery": discovery,
        "bridgeHealth": _public_health(health),
        "approvalTemplates": approval_template_payload(project_root)["approvalTemplates"],
    })
    return payload


def plan_payload(project_root: str | Path) -> dict[str, Any]:
    preflight = preflight_payload(project_root)
    payload = _base_payload("plan")
    payload.update({
        "ok": True,
        "status": SQX144_MT5_AUTO10_STATUS,
        "plannedPhase": SQX144_MT5_AUTO10_PHASE,
        "goal": "internal MT5 bridge runner for Darwinex so Data Manager can prepare MT5 without manual operator launch after a separate gate",
        "sourceReadyOnly": True,
        "preflightStatus": preflight.get("status"),
        "preflightBlockers": preflight.get("blockers", []),
        "preflightWarnings": preflight.get("warnings", []),
        "allowedNow": {
            "discoverPaths": True,
            "reportPreflight": True,
            "returnApprovalTemplates": True,
            "launchMt5": False,
            "compileMq5": False,
            "writeBridgeRequest": False,
            "runEa": False,
        },
        "afterInstallGate": {
            "copyBridgeSourceIfHashDiffers": True,
            "compileBridgeWithMetaEditor": True,
            "launchMt5": False,
        },
        "afterLaunchGate": {
            "reuseExistingMt5": True,
            "launchTerminalHiddenOrMinimized": True,
            "writeSmokeRequest": True,
            "waitForFreshBridgeHeartbeat": True,
            "stopOnlyAuto10ManagedProcess": True,
        },
        "dataManagerRouting": {
            "darwinexUsesAuto10HealthBeforeRequest": True,
            "futureAxiUsesAuto10OnlyAfterBrokerDiscovery": True,
            "dukascopyUsesAuto7NoMt5": True,
            "exactlyOneCheckboxStillRequired": True,
        },
        "approvalTemplates": approval_template_payload(project_root)["approvalTemplates"],
    })
    return payload


def approval_template_payload(project_root: str | Path) -> dict[str, Any]:
    _project_root(project_root)
    payload = _base_payload("approval-template")
    payload.update({
        "ok": True,
        "status": "auto10_approval_templates_ready",
        "approvalTemplates": {
            "install": AUTO10_INSTALL_APPROVAL_PHRASE,
            "launch": AUTO10_LAUNCH_APPROVAL_PHRASE,
        },
        "notes": [
            "Install gate may copy/compile only SQXInfoBridge source for the governed Darwinex terminal.",
            "Launch gate may reuse an open MT5 process or launch terminal hidden/minimized, then prove bridge heartbeat.",
            "Neither gate allows SQX data.db writes, history import, projects, databanks, SQX tasks, orders or Migration Tool.",
        ],
    })
    return payload


def _require_install_approval(approval: str | None) -> None:
    if str(approval or "").strip() != AUTO10_INSTALL_APPROVAL_PHRASE:
        raise Auto10Error("auto10_install_requires_exact_approval")


def _require_launch_approval(approval: str | None) -> None:
    if str(approval or "").strip() != AUTO10_LAUNCH_APPROVAL_PHRASE:
        raise Auto10Error("auto10_launch_requires_exact_approval")


def install_source_payload(
    project_root: str | Path,
    *,
    approval: str | None = None,
    mt5_root: str | Path | None = None,
    mt5_experts_dir: str | Path | None = None,
    apply: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    paths = _resolve_paths(project_root=root, mt5_root=mt5_root, mt5_experts_dir=mt5_experts_dir)
    payload = _base_payload("install-source")
    payload.update({
        "ok": True,
        "status": "auto10_install_source_ready_apply_required",
        "targetFileName": DEFAULT_BRIDGE_SOURCE_NAME,
        "binaryFileName": DEFAULT_BRIDGE_BINARY_NAME,
        "wouldCopyBridgeSource": True,
        "wouldCompileBridgeSource": True,
        "installSourceAllowedByGate": False,
    })
    if not apply:
        return payload
    _require_install_approval(approval)
    preflight = preflight_payload(project_root, mt5_root=mt5_root, mt5_experts_dir=mt5_experts_dir)
    blockers = [code for code in preflight.get("blockers", []) if code not in {"mt5_files_dir_missing"}]
    if blockers:
        raise Auto10Error("auto10_install_preflight_blocked", details={"blockers": blockers})
    source = paths["source"]
    target = paths["installedMq5"]
    source_hash = _sha256(source)
    target_hash = _sha256(target)
    copied = False
    if source_hash != target_hash:
        if target.exists() and not overwrite:
            raise Auto10Error("auto10_install_source_hash_diff_requires_overwrite")
        shutil.copy2(source, target)
        copied = True
    compile_result = _compile_bridge(paths["metaeditorExe"], target)
    payload.update({
        "ok": bool(compile_result.get("ok")),
        "status": "auto10_install_source_completed" if compile_result.get("ok") else "auto10_install_source_compile_failed",
        "installSourceAllowedByGate": True,
        "writesMt5Source": copied,
        "copiedBridgeSource": copied,
        "compiledBridgeSource": bool(compile_result.get("executed")),
        "compile": compile_result,
    })
    return payload


def _compile_bridge(metaeditor_exe: Path, source_path: Path) -> dict[str, Any]:
    if not metaeditor_exe.is_file():
        raise Auto10Error("mt5_metaeditor_exe_missing")
    try:
        result = subprocess.run(
            [str(metaeditor_exe), f"/compile:{source_path}"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "executed": False, "error": type(exc).__name__}
    return {
        "ok": result.returncode == 0,
        "executed": True,
        "returnCode": result.returncode,
        "stdoutBytes": len(result.stdout or ""),
        "stderrBytes": len(result.stderr or ""),
    }


def launch_payload(
    project_root: str | Path,
    *,
    approval: str | None = None,
    mt5_root: str | Path | None = None,
    apply: bool = False,
    window_style: str = "minimized",
) -> dict[str, Any]:
    root = _project_root(project_root)
    style = str(window_style or "minimized").lower()
    if style not in MT5_WINDOW_STYLES:
        raise Auto10Error("auto10_window_style_invalid", details={"windowStyle": window_style})
    payload = _base_payload("launch")
    payload.update({
        "ok": True,
        "status": "auto10_launch_ready_apply_required",
        "wouldReuseExistingMt5": True,
        "wouldLaunchMt5": True,
        "windowStyle": style,
    })
    if not apply:
        return payload
    _require_launch_approval(approval)
    paths = _resolve_paths(project_root=root, mt5_root=mt5_root)
    process = _detect_process_state(paths["terminalExe"])
    if process.get("targetTerminalProcessRunning") is True:
        payload.update({
            "ok": True,
            "status": "auto10_launch_reused_existing_target_mt5_process",
            "launchesMt5AllowedByGate": True,
            "launchesMt5": False,
            "process": _public_process_state(process),
        })
        return payload
    terminal = paths["terminalExe"]
    if not terminal.is_file():
        raise Auto10Error("mt5_terminal_exe_missing")
    startupinfo = None
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
        startupinfo.wShowWindow = 0 if style == "hidden" else 2
    proc = subprocess.Popen(
        [str(terminal)],
        cwd=str(paths["mt5Root"]),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        startupinfo=startupinfo,
        creationflags=creationflags,
    )
    actual_pid = int(proc.pid)
    process_after_launch: dict[str, Any] = process
    for _index in range(10):
        time.sleep(1)
        process_after_launch = _detect_process_state(paths["terminalExe"])
        target_pids = process_after_launch.get("_targetPids") or []
        if target_pids:
            actual_pid = int(target_pids[0])
            break
    _managed_root(root).mkdir(parents=True, exist_ok=True)
    _managed_pid_file(root).write_text(
        json.dumps(
            {
                "version": SQX144_MT5_AUTO10_VERSION,
                "pid": actual_pid,
                "launcherPid": int(proc.pid),
                "createdUtc": datetime.now(timezone.utc).isoformat(),
                "windowStyle": style,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    payload.update({
        "ok": True,
        "status": "auto10_launch_started_managed_mt5_process",
        "launchesMt5AllowedByGate": True,
        "launchesMt5": True,
        "managedPidRecorded": True,
        "managedPidIsTargetTerminal": actual_pid != int(proc.pid) or process_after_launch.get("targetTerminalProcessRunning") is True,
        "process": _public_process_state(process_after_launch),
        "windowStyle": style,
    })
    return payload


def stop_payload(project_root: str | Path, *, apply: bool = False) -> dict[str, Any]:
    root = _project_root(project_root)
    record = _read_managed_pid_record(root)
    payload = _base_payload("stop")
    payload.update({
        "ok": True,
        "status": "auto10_stop_ready_apply_required",
        "managedPidRecorded": bool(record and not record.get("parseError")),
        "wouldStopOnlyManagedAuto10Pid": True,
    })
    if not apply:
        return payload
    if not record or record.get("parseError"):
        raise Auto10Error("auto10_managed_pid_missing")
    pid = int(record.get("pid") or 0)
    if pid <= 0:
        raise Auto10Error("auto10_managed_pid_invalid")
    result = subprocess.run(["taskkill", "/PID", str(pid), "/T"], capture_output=True, text=True, timeout=15, check=False)
    if result.returncode == 0:
        try:
            _managed_pid_file(root).unlink()
        except OSError:
            pass
    payload.update({
        "ok": result.returncode == 0,
        "status": "auto10_stop_completed_managed_pid_only" if result.returncode == 0 else "auto10_stop_failed_managed_pid_only",
        "stopReturnCode": result.returncode,
    })
    return payload


def verify_payload(
    project_root: str | Path,
    *,
    approval: str | None = None,
    symbol: str = DEFAULT_SMOKE_SYMBOL,
    apply: bool = False,
    timeout_seconds: int = DEFAULT_READY_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    payload = _base_payload("verify")
    payload.update({
        "ok": True,
        "status": "auto10_verify_smoke_ready_apply_required",
        "smokeSymbol": symbol,
        "timeoutSeconds": int(timeout_seconds or DEFAULT_READY_TIMEOUT_SECONDS),
        "wouldWriteBridgeRequest": True,
        "wouldWaitForBridgeHeartbeat": True,
    })
    if not apply:
        return payload
    _require_launch_approval(approval)
    request_id = f"sqx_auto10_{''.join(ch if ch.isalnum() else '_' for ch in symbol)}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    request = bridge.write_request_payload(symbol=symbol, project_root=project_root, request_id=request_id, apply=True)
    deadline = time.time() + max(5, int(timeout_seconds or DEFAULT_READY_TIMEOUT_SECONDS))
    latest_health: dict[str, Any] = {}
    while time.time() < deadline:
        latest_health = bridge.health_payload(project_root=project_root, expected_request_id=request_id, expected_symbol=symbol)
        if latest_health.get("panelStatus") == "mt5_bridge_ready_latest_matches_request":
            break
        time.sleep(1)
    payload.update({
        "ok": latest_health.get("panelStatus") == "mt5_bridge_ready_latest_matches_request",
        "status": "auto10_verify_bridge_ready" if latest_health.get("panelStatus") == "mt5_bridge_ready_latest_matches_request" else "auto10_verify_bridge_timeout",
        "writesMt5Files": True,
        "requestWritten": bool(request.get("ok")),
        "requestId": request_id,
        "bridgeHealth": _public_health(latest_health),
    })
    return payload


def _public_health(payload: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "status",
        "panelStatus",
        "severity",
        "nextAction",
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
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO10 internal MT5 runner gate")
    parser.add_argument("action", choices=("status", "discover", "preflight", "plan", "install-source", "launch", "stop", "verify", "approval-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--mt5-root", default=None)
    parser.add_argument("--mt5-files-dir", default=None)
    parser.add_argument("--mt5-experts-dir", default=None)
    parser.add_argument("--approval", default=None)
    parser.add_argument("--symbol", default=DEFAULT_SMOKE_SYMBOL)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_READY_TIMEOUT_SECONDS)
    parser.add_argument("--window-style", default="minimized")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root)
        elif args.action == "discover":
            payload = discover_payload(args.project_root, mt5_root=args.mt5_root, mt5_files_dir=args.mt5_files_dir, mt5_experts_dir=args.mt5_experts_dir)
        elif args.action == "preflight":
            payload = preflight_payload(args.project_root, mt5_root=args.mt5_root, mt5_files_dir=args.mt5_files_dir, mt5_experts_dir=args.mt5_experts_dir)
        elif args.action == "plan":
            payload = plan_payload(args.project_root)
        elif args.action == "install-source":
            payload = install_source_payload(
                args.project_root,
                approval=args.approval,
                mt5_root=args.mt5_root,
                mt5_experts_dir=args.mt5_experts_dir,
                apply=args.apply,
                overwrite=args.overwrite,
            )
        elif args.action == "launch":
            payload = launch_payload(args.project_root, approval=args.approval, mt5_root=args.mt5_root, apply=args.apply, window_style=args.window_style)
        elif args.action == "stop":
            payload = stop_payload(args.project_root, apply=args.apply)
        elif args.action == "verify":
            payload = verify_payload(args.project_root, approval=args.approval, symbol=args.symbol, apply=args.apply, timeout_seconds=args.timeout_seconds)
        else:
            payload = approval_template_payload(args.project_root)
    except (Auto10Error, bridge.BridgeError) as exc:
        payload = error_payload(args.action, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
