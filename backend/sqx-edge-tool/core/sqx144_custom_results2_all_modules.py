from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core import sqx144_custom_results1_study as custom_results1


SQX144_CUSTOM_RESULTS2_VERSION = "sqx144-custom-results2-all-custom-results-modules-bundle-v1"
SQX144_CUSTOM_RESULTS2_READONLY_MARKER = "sqx144-custom-results2-readonly-all-modules-bundle-v1"
SQX144_CUSTOM_RESULTS2_STATUS = "custom_results2_all_modules_bundle_source_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
EVIDENCE_DIR_PARTS = (".local", "sqx144_custom_results2")
ALL_MODULES_RELATIVE = Path("integrations") / "sqx144" / "results_plugins" / "SQX Edge Custom Results All Modules"

MODULES: tuple[dict[str, Any], ...] = (
    {
        "id": "robustness_scorecard",
        "label": "RobustnessScorecard",
        "sourceCandidate": "RobustnessScorecard.zip",
        "messages": ["STRATEGY_DATA", "GET_STATS", "STATS_RESPONSE"],
        "usesOrders": False,
        "repoImplemented": True,
        "methodologyFit": "core_scorecard",
    },
    {
        "id": "oos_degradation_scorecard",
        "label": "OOSDegradationScorecard",
        "sourceCandidate": "OOSDegradationScorecard.zip",
        "messages": ["STRATEGY_DATA", "GET_STATS", "STATS_RESPONSE"],
        "usesOrders": False,
        "repoImplemented": True,
        "methodologyFit": "core_is_oos_review",
    },
    {
        "id": "edge_decay_analyzer",
        "label": "Edge Decay Analyzer",
        "sourceCandidate": "Edge-Decay-Max-Loss-Analyzer-1.zip",
        "messages": ["STRATEGY_DATA", "GET_STATS", "STATS_RESPONSE", "GET_ORDERS", "ORDERS_RESPONSE"],
        "usesOrders": True,
        "repoImplemented": True,
        "methodologyFit": "orders_research",
    },
    {
        "id": "win_rate_edge",
        "label": "WinRateEdge + RandomEntry",
        "sourceCandidate": "WinRateEdge-1.zip + RandomEntries-1.htm",
        "messages": ["STRATEGY_DATA", "GET_STATS", "STATS_RESPONSE", "GET_ORDERS", "ORDERS_RESPONSE"],
        "usesOrders": True,
        "repoImplemented": True,
        "methodologyFit": "random_baseline_research",
    },
    {
        "id": "two_step_challenge_analyzer",
        "label": "2-Step Challenge Analyzer",
        "sourceCandidate": "2-Step-Challenge-Analyzer.zip",
        "messages": ["STRATEGY_DATA", "GET_STATS", "STATS_RESPONSE", "GET_ORDERS", "ORDERS_RESPONSE"],
        "usesOrders": True,
        "repoImplemented": True,
        "methodologyFit": "optional_commercial_prop_firm",
    },
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _base_payload(action: str) -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_CUSTOM_RESULTS2_VERSION,
        "readOnlyMarker": SQX144_CUSTOM_RESULTS2_READONLY_MARKER,
        "action": action,
        "status": SQX144_CUSTOM_RESULTS2_STATUS,
        "hostProfile": "sqx144_full",
        "phase": "SQX144-CUSTOM-RESULTS2",
        "phaseLabel": "SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle",
        "installExecuted": False,
        "ordersEnabledInRepoBundle": True,
        "getOrdersPolicy": "GET_ORDERS remains privacy/performance-gated",
        "ordersResponsePolicy": "ORDERS_RESPONSE fixture-only until exact future gate",
        "guards": {
            "repoOnlyImplementation": True,
            "installsIntoSqxHost": False,
            "sqxInstallAllowed": False,
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
            "usesGetOrders": True,
            "usesGetOrdersInRepoOnlyBundle": True,
            "browserPersistenceAllowed": False,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawStrategyNamesReturned": False,
            "rawOrdersReturned": False,
            "rawOrdersReturnedByTooling": False,
            "sourceCodeReturned": False,
            "licenseMaterialReturned": False,
            "secretsReturned": False,
        },
    }


def status_payload(project_root: str | Path = ".") -> dict[str, Any]:
    root = _project_root(project_root)
    plugin_root = root / ALL_MODULES_RELATIVE
    payload = _base_payload("status")
    payload.update({
        "ok": True,
        "actions": ["status", "scan", "module-smoke", "report", "approval-template"],
        "plugin": {
            "ref": str(ALL_MODULES_RELATIVE).replace("\\", "/"),
            "present": plugin_root.exists(),
            "expectedFiles": ["index.html", "fixtures/fixtures.js", "README.md"],
        },
        "modules": list(MODULES),
        "downloadRootRef": "operator_downloads_custom_results_sqx",
        "nextAction": "run module-smoke and report before any future install gate",
    })
    return payload


def scan_payload(download_root: str | Path | None = None) -> dict[str, Any]:
    source_scan = custom_results1.scan_downloads_payload(download_root)
    artifact_by_id = {item["id"]: item for item in source_scan["artifacts"]}
    module_matrix = []
    for module in MODULES:
        candidate = artifact_by_id.get(module["id"], {})
        if module["id"] == "win_rate_edge":
            random_entries = artifact_by_id.get("random_entries", {})
            present = bool(candidate.get("present")) and bool(random_entries.get("present"))
        else:
            present = bool(candidate.get("present"))
        module_matrix.append({
            "id": module["id"],
            "label": module["label"],
            "repoImplemented": module["repoImplemented"],
            "downloadPresent": present,
            "usesOrders": module["usesOrders"],
            "messages": module["messages"],
            "methodologyFit": module["methodologyFit"],
            "sourceCandidate": module["sourceCandidate"],
            "candidateScan": {
                "fit": candidate.get("fit"),
                "requiresOrdersGate": candidate.get("requiresOrdersGate", False),
                "requiresPersistenceWaiver": candidate.get("requiresPersistenceWaiver", False),
                "remoteNetworkObserved": candidate.get("remoteNetworkObserved", False),
            },
        })
    payload = _base_payload("scan")
    payload.update({
        "ok": source_scan["ok"],
        "status": "custom_results2_all_modules_bundle_scan_completed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool",
        "sourceScanStatus": source_scan["status"],
        "downloadRootRef": source_scan["downloadRootRef"],
        "downloadRootPresent": source_scan["downloadRootPresent"],
        "artifactCount": source_scan["artifactCount"],
        "presentCount": source_scan["presentCount"],
        "moduleMatrix": module_matrix,
        "allModulesImplemented": all(item["repoImplemented"] for item in module_matrix),
        "downloadedPluginsInstalled": False,
    })
    return payload


def module_smoke_payload(project_root: str | Path = ".") -> dict[str, Any]:
    root = _project_root(project_root)
    plugin_root = root / ALL_MODULES_RELATIVE
    expected = ["index.html", "fixtures/fixtures.js", "README.md"]
    files = {name: plugin_root / name for name in expected}
    index_text = files["index.html"].read_text(encoding="utf-8") if files["index.html"].exists() else ""
    fixtures_text = files["fixtures/fixtures.js"].read_text(encoding="utf-8") if files["fixtures/fixtures.js"].exists() else ""
    readme_text = files["README.md"].read_text(encoding="utf-8") if files["README.md"].exists() else ""
    required_markers = [
        "SQX_EDGE_CUSTOM_RESULTS_ALL_MODULES_VERSION",
        SQX144_CUSTOM_RESULTS2_VERSION,
        "Robustness Scorecard",
        "IS/OOS Degradation",
        "Edge Decay Analyzer",
        "WinRateEdge",
        "2-Step Challenge",
        "STRATEGY_DATA",
        "GET_STATS",
        "STATS_RESPONSE",
        "GET_ORDERS",
        "ORDERS_RESPONSE",
        "allReady",
        "edgeDecay",
        "winRateResearch",
        "propFirm",
        "blockedWeak",
        "missingOrders",
    ]
    forbidden_markers = [
        marker
        for marker in (
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
        if marker in index_text or marker in fixtures_text
    ]
    missing = [marker for marker in required_markers if marker not in index_text and marker not in fixtures_text and marker not in readme_text]
    ok = plugin_root.exists() and all(path.exists() for path in files.values()) and not forbidden_markers and not missing
    payload = _base_payload("module-smoke")
    payload.update({
        "ok": ok,
        "status": "custom_results2_all_modules_bundle_smoke_passed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool" if ok else "custom_results2_all_modules_bundle_smoke_failed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool",
        "pluginRef": str(ALL_MODULES_RELATIVE).replace("\\", "/"),
        "files": [{"name": name, "present": path.exists()} for name, path in files.items()],
        "missingRequiredMarkers": missing,
        "forbiddenMarkers": forbidden_markers,
        "fixtureNames": ["allReady", "edgeDecay", "winRateResearch", "propFirm", "blockedWeak", "missingOrders"],
        "moduleIds": [module["id"] for module in MODULES],
    })
    return payload


def report_payload(project_root: str | Path = ".", download_root: str | Path | None = None, write_evidence: bool = False) -> dict[str, Any]:
    scan = scan_payload(download_root)
    smoke = module_smoke_payload(project_root)
    payload = _base_payload("report")
    ok = scan["ok"] and smoke["ok"]
    payload.update({
        "ok": ok,
        "status": "custom_results2_all_modules_bundle_report_completed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool" if ok else "custom_results2_all_modules_bundle_report_completed_with_blockers_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool",
        "scan": scan,
        "moduleSmoke": smoke,
        "decision": {
            "allModulesRepoImplemented": smoke["ok"],
            "installApproved": False,
            "downloadedPluginsInstalled": False,
            "nextRecommendedGate": "SQX144-CUSTOM-RESULTS3 optional manual install of SQX Edge-owned all-modules bundle",
            "installRequiresExactGate": "APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code",
            "methodology": "All modules are diagnostic/research panels only; they do not promote strategies or alter pass states.",
        },
        "evidenceWritten": False,
    })
    if write_evidence:
        payload["evidenceRef"] = write_evidence_file(_project_root(project_root), "report", payload)
        payload["evidenceWritten"] = True
    return payload


def approval_template_payload(project_root: str | Path = ".") -> dict[str, Any]:
    payload = status_payload(project_root)
    payload["action"] = "approval-template"
    payload["approvalNotRequiredForRepoWork"] = True
    payload["futureInstallApproval"] = "APRUEBO SQX144 CUSTOM RESULTS3 ALL MODULES MANUAL INSTALL host=sqx144_full plugin=sqx_edge_custom_results_all_modules sqx_closed backup_hash_rollback copy_only_sqx_edge_owned_plugin get_orders_runtime_acknowledged no_db_no_projects_no_databanks_no_tasks no_migration_tool no_downloaded_plugins no_source_code"
    payload["blockedWithoutFutureApproval"] = [
        "COPIAR A SQX144 FULL",
        "INSTALAR PLUGINS DESCARGADOS DIRECTAMENTE",
        "LANZAR SQX",
        "ESCRIBIR data.db",
        "MUTAR user/projects",
        "MUTAR databanks",
        "USAR Migration Tool",
    ]
    return payload


def write_evidence_file(project_root: Path, action: str, payload: dict[str, Any]) -> str:
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"sqx144_custom_results2_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "scan", "module-smoke", "report", "approval-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--download-root", default=None)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "scan":
        payload = scan_payload(args.download_root)
    elif args.action == "module-smoke":
        payload = module_smoke_payload(args.project_root)
    elif args.action == "report":
        payload = report_payload(args.project_root, args.download_root, write_evidence=args.write_evidence)
    elif args.action == "approval-template":
        payload = approval_template_payload(args.project_root)
    else:
        payload = status_payload(args.project_root)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
