from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import sqx144_mt5_auto2_datamanager as auto2
from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO9_VERSION = "sqx144-mt5-auto9-health-watchdog-v1"
SQX144_MT5_AUTO9_DATAMANAGER_VERSION = "sqx144-mt5-auto9-datamanager-health-watchdog-v1"
SQX144_MT5_AUTO9_PHASE = "SQX144-MT5-AUTO9"
SQX144_MT5_AUTO9_STATUS = "auto9_health_watchdog_source_ready_no_install_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool"
SQX144_MT5_AUTO9_INSTALL_STATUS = "auto9_datamanager_health_watchdog_installed_verified_no_db_no_projects_no_databanks_no_tasks_no_apply_no_import_no_mt5_no_migration_tool"
AUTO9_APPROVAL_PHRASE = "APRUEBO SQX144 MT5 AUTO9 DATAMANAGER HEALTH WATCHDOG INSTALL host=sqx144_full no_db_no_projects_no_databanks_no_tasks no_apply_no_import no_mt5 no_migration_tool"
AUTO10_PLANNED_PHASE = "SQX144-MT5-AUTO10"


class Auto9Error(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO9_VERSION,
        "dataManagerVersion": SQX144_MT5_AUTO9_DATAMANAGER_VERSION,
        "phase": SQX144_MT5_AUTO9_PHASE,
        "statusMarker": SQX144_MT5_AUTO9_STATUS,
        "action": action,
        "host": "sqx144_full",
        "healthWatchdogObserveOnly": True,
        "autoStartAllowed": False,
        "applyAllowed": False,
        "importAllowed": False,
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
        "doesNotApplyToSqx": True,
        "doesNotApplyInstrumentConfig": True,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def status_payload(project_root: str | Path) -> dict[str, Any]:
    root = _project_root(project_root)
    auto2_status = auto2.status_payload(root)
    health = bridge.health_payload(project_root=root)
    payload = _base_payload("status")
    payload.update({
        "ok": True,
        "status": SQX144_MT5_AUTO9_STATUS,
        "dataManagerInstallStatusPlanned": SQX144_MT5_AUTO9_INSTALL_STATUS,
        "approvalTemplate": AUTO9_APPROVAL_PHRASE,
        "endpoints": [
            "/api/sqx144/mt5-auto9/status",
            "/api/sqx144/mt5-auto9/health",
            "/api/sqx144/mt5-auto9/automation-plan",
            "/api/sqx144/mt5-auto9/approval-template",
        ],
        "auto2": {
            "ok": auto2_status.get("ok"),
            "status": auto2_status.get("status"),
            "installed": auto2_status.get("installed"),
            "sourceHasAuto9HealthWatchdog": auto2_status.get("sourceHasAuto9Health"),
            "targetHasAuto9HealthWatchdog": auto2_status.get("targetHasAuto9Health"),
        },
        "bridgeHealth": _public_health(health),
        "automationNextPhase": AUTO10_PLANNED_PHASE,
    })
    return payload


def health_payload(
    project_root: str | Path,
    *,
    expected_request_id: str | None = None,
    expected_symbol: str | None = None,
    stale_after_seconds: int = bridge.DEFAULT_HEALTH_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    root = _project_root(project_root)
    health = bridge.health_payload(
        project_root=root,
        expected_request_id=expected_request_id,
        expected_symbol=expected_symbol,
        stale_after_seconds=stale_after_seconds,
    )
    payload = _base_payload("health")
    payload.update({
        "ok": True,
        "status": health.get("status"),
        "panelStatus": health.get("panelStatus"),
        "severity": health.get("severity"),
        "nextAction": health.get("nextAction"),
        "bridgeHealth": _public_health(health),
    })
    return payload


def automation_plan_payload(project_root: str | Path) -> dict[str, Any]:
    _project_root(project_root)
    payload = _base_payload("automation-plan")
    payload.update({
        "ok": True,
        "status": "auto10_internal_mt5_runner_design_only_no_execution",
        "plannedPhase": AUTO10_PLANNED_PHASE,
        "goal": "make MT5 bridge execution internal to SQX Edge so the operator does not manually open MT5 or attach the EA",
        "allowedInAuto9": {
            "detectMt5Process": True,
            "inspectBridgeRequestAndLatestResponse": True,
            "showPanelHealth": True,
        },
        "blockedUntilFutureGate": {
            "launchMt5": True,
            "compileMq5": True,
            "attachOrRunEa": True,
            "createMt5Profile": True,
            "hiddenOrMinimizedTerminalRunner": True,
        },
        "futureGateRequirements": [
            "exact operator approval naming host=sqx144_full",
            "no trading and no order placement",
            "heartbeat proving SQXInfoBridge is alive",
            "safe timeout and error panel states",
            "no SQX data.db, history, projects, databanks, tasks or Migration Tool mutation",
        ],
        "riskNotes": [
            "MT5 is not guaranteed to be fully headless; login, broker updates, Algo Trading permissions or modals can surface",
            "AUTO10 should verify a fresh heartbeat before trusting request/response automation",
        ],
    })
    return payload


def approval_template_payload(project_root: str | Path) -> dict[str, Any]:
    _project_root(project_root)
    payload = _base_payload("approval-template")
    payload.update({
        "ok": True,
        "status": "auto9_install_approval_template_ready",
        "approvalTemplate": AUTO9_APPROVAL_PHRASE,
        "notes": "Installs only Data Manager overlay health/status assets; it does not launch MT5, run EA, apply metadata, import history, write data.db or touch projects/databanks/tasks.",
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


def _public_health(payload: dict[str, Any]) -> dict[str, Any]:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO9 health watchdog")
    parser.add_argument("action", choices=("status", "health", "automation-plan", "approval-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--expected-request-id", default=None)
    parser.add_argument("--expected-symbol", default=None)
    parser.add_argument("--stale-after-seconds", type=int, default=bridge.DEFAULT_HEALTH_STALE_AFTER_SECONDS)
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root)
        elif args.action == "health":
            payload = health_payload(
                args.project_root,
                expected_request_id=args.expected_request_id,
                expected_symbol=args.expected_symbol,
                stale_after_seconds=args.stale_after_seconds,
            )
        elif args.action == "automation-plan":
            payload = automation_plan_payload(args.project_root)
        else:
            payload = approval_template_payload(args.project_root)
    except (Auto9Error, bridge.BridgeError) as exc:
        payload = error_payload(args.action, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
