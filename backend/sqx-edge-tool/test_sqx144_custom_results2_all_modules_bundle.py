from __future__ import annotations

import json
import zipfile
from pathlib import Path

from core.sqx144_custom_results2_all_modules import (
    SQX144_CUSTOM_RESULTS2_STATUS,
    SQX144_CUSTOM_RESULTS2_VERSION,
    module_smoke_payload,
    report_payload,
    scan_payload,
    status_payload,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_zip(path: Path, files: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def _prepare_downloads(root: Path) -> Path:
    downloads = root / "downloads"
    _write_zip(downloads / "RobustnessScorecard.zip", {"RobustnessScorecard/index.html": "STRATEGY_DATA GET_STATS STATS_RESPONSE"})
    _write_zip(downloads / "OOSDegradationScorecard.zip", {"OOSDegradationScorecard/index.html": "STRATEGY_DATA GET_STATS STATS_RESPONSE"})
    _write_zip(downloads / "Edge-Decay-Max-Loss-Analyzer-1.zip", {"Edge Decay/index.html": "STRATEGY_DATA GET_STATS STATS_RESPONSE GET_ORDERS ORDERS_RESPONSE localStorage.setItem"})
    _write_zip(downloads / "WinRateEdge-1.zip", {"WinRateEdge/index.html": "STRATEGY_DATA GET_ORDERS ORDERS_RESPONSE"})
    _write_zip(downloads / "2-Step-Challenge-Analyzer.zip", {"2-Step/index.html": "STRATEGY_DATA GET_STATS GET_ORDERS ORDERS_RESPONSE"})
    _write_zip(
        downloads / "RandomEntries-1.htm",
        {
            "extend/Snippets/SQ/Blocks/RandomEntry/RandomEntry.java": "public class RandomEntry { @BuildingBlock void x(){ Math.random(); } }",
            "extend/Code/MetaTrader5/blocks/RandomEntry.tpl": "random",
        },
    )
    return downloads


def test_status_declares_all_modules_repo_only_and_orders_policy():
    payload = status_payload(PROJECT_ROOT)

    assert payload["version"] == SQX144_CUSTOM_RESULTS2_VERSION
    assert payload["readOnlyMarker"] == "sqx144-custom-results2-readonly-all-modules-bundle-v1"
    assert payload["status"] == SQX144_CUSTOM_RESULTS2_STATUS
    assert payload["phase"] == "SQX144-CUSTOM-RESULTS2"
    assert payload["phaseLabel"] == "SQX144-CUSTOM-RESULTS2 - All Custom Results Modules Bundle"
    assert payload["installExecuted"] is False
    assert payload["ordersEnabledInRepoBundle"] is True
    assert payload["getOrdersPolicy"] == "GET_ORDERS remains privacy/performance-gated"
    assert payload["ordersResponsePolicy"] == "ORDERS_RESPONSE fixture-only until exact future gate"
    assert payload["guards"]["usesGetOrders"] is True
    assert payload["guards"]["usesGetOrdersInRepoOnlyBundle"] is True
    assert payload["guards"]["usesGetSourceCode"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["writesUserProjects"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
    assert payload["guards"]["launchesSqxRuntime"] is False
    assert payload["guards"]["usesMigrationTool"] is False
    assert len(payload["modules"]) == 5
    assert payload["privacy"]["rawOrdersReturned"] is False


def test_scan_maps_all_downloaded_custom_results_without_installing(tmp_path):
    downloads = _prepare_downloads(tmp_path)
    payload = scan_payload(downloads)
    blob = json.dumps(payload, ensure_ascii=False)
    matrix = {item["id"]: item for item in payload["moduleMatrix"]}

    assert payload["ok"] is True
    assert payload["allModulesImplemented"] is True
    assert payload["downloadedPluginsInstalled"] is False
    assert matrix["robustness_scorecard"]["downloadPresent"] is True
    assert matrix["oos_degradation_scorecard"]["downloadPresent"] is True
    assert matrix["edge_decay_analyzer"]["usesOrders"] is True
    assert matrix["win_rate_edge"]["downloadPresent"] is True
    assert matrix["two_step_challenge_analyzer"]["methodologyFit"] == "optional_commercial_prop_firm"
    assert "GET_ORDERS" in matrix["edge_decay_analyzer"]["messages"]
    assert str(tmp_path) not in blob
    assert payload["privacy"]["rawOrdersReturnedByTooling"] is False


def test_module_smoke_accepts_orders_bundle_but_blocks_unsafe_markers():
    payload = module_smoke_payload(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "custom_results2_all_modules_bundle_smoke_passed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool"
    assert payload["pluginRef"] == "integrations/sqx144/results_plugins/SQX Edge Custom Results All Modules"
    assert payload["missingRequiredMarkers"] == []
    assert payload["forbiddenMarkers"] == []
    assert payload["fixtureNames"] == ["allReady", "edgeDecay", "winRateResearch", "propFirm", "blockedWeak", "missingOrders"]


def test_report_writes_sanitized_evidence_when_requested(tmp_path):
    downloads = _prepare_downloads(tmp_path)
    payload = report_payload(PROJECT_ROOT, downloads, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["ok"] is True
    assert payload["status"] == "custom_results2_all_modules_bundle_report_completed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool"
    assert payload["decision"]["allModulesRepoImplemented"] is True
    assert payload["decision"]["installApproved"] is False
    assert payload["decision"]["downloadedPluginsInstalled"] is False
    assert payload["evidenceWritten"] is True
    assert payload["evidenceRef"].startswith("sqx144_custom_results2_report_")
    assert str(tmp_path) not in blob
