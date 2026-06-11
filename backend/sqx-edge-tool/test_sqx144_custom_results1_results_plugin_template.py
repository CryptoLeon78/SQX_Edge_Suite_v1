from __future__ import annotations

import json
import zipfile
from pathlib import Path

from core.sqx144_custom_results1_study import (
    SQX144_CUSTOM_RESULTS1_STATUS,
    SQX144_CUSTOM_RESULTS1_VERSION,
    scan_downloads_payload,
    status_payload,
    template_smoke_payload,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _write_zip(path: Path, files: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_status_is_source_ready_no_runtime_no_mutation():
    payload = status_payload(PROJECT_ROOT)

    assert payload["version"] == SQX144_CUSTOM_RESULTS1_VERSION
    assert payload["readOnlyMarker"] == "sqx144-custom-results1-readonly-results-plugin-template-v1"
    assert payload["status"] == SQX144_CUSTOM_RESULTS1_STATUS
    assert payload["phase"] == "SQX144-CUSTOM-RESULTS1"
    assert payload["phaseLabel"] == "SQX144-CUSTOM-RESULTS1 - Read-Only Results Plugin Template"
    assert payload["hostProfile"] == "sqx144_full"
    assert payload["installExecuted"] is False
    assert payload["guards"]["installsIntoSqxHost"] is False
    assert payload["guards"]["sqxInstallAllowed"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["writesUserProjects"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
    assert payload["guards"]["runsSqxTasks"] is False
    assert payload["guards"]["launchesSqxRuntime"] is False
    assert payload["guards"]["usesMigrationTool"] is False
    assert payload["guards"]["usesGetSourceCode"] is False
    assert payload["guards"]["usesGetOrdersByDefault"] is False


def test_scan_accepts_template_and_returns_public_safe_inventory(tmp_path):
    downloads = tmp_path / "downloads"
    _write_zip(
        downloads / "RobustnessScorecard.zip",
        {
            "RobustnessScorecard/index.html": "<script>parent.postMessage({ type: 'GET_STATS' }, '*')</script>",
            "RobustnessScorecard/README.md": "Robustness scorecard",
        },
    )
    _write_zip(
        downloads / "OOSDegradationScorecard.zip",
        {
            "OOSDegradationScorecard/index.html": "<script>const x='STRATEGY_DATA'; const y='STATS_RESPONSE';</script>",
        },
    )
    _write_zip(
        downloads / "Edge-Decay-Max-Loss-Analyzer-1.zip",
        {
            "Edge Decay & Max Loss Analyzer/index.html": "<script>GET_ORDERS; localStorage.setItem('k','v');</script>",
        },
    )
    _write_zip(
        downloads / "WinRateEdge-1.zip",
        {
            "WinRateEdge/index.html": "<script>GET_ORDERS; fetch('./local.json');</script>",
        },
    )

    payload = scan_downloads_payload(downloads)
    blob = json.dumps(payload, ensure_ascii=False)
    matrix = {item["id"]: item for item in payload["comparisonMatrix"]}

    assert payload["ok"] is True
    assert payload["presentCount"] == 4
    assert matrix["robustness_scorecard"]["fit"] == "best_immediate_fit"
    assert matrix["oos_degradation_scorecard"]["fit"] == "best_immediate_fit"
    assert matrix["edge_decay_analyzer"]["requiresOrdersGate"] is True
    assert matrix["edge_decay_analyzer"]["requiresPersistenceWaiver"] is True
    assert matrix["win_rate_edge"]["requiresOrdersGate"] is True
    assert payload["recommendation"]["firstTemplateInputs"] == ["robustness_scorecard", "oos_degradation_scorecard"]
    assert str(tmp_path) not in blob
    assert "localPathReturned\": true" not in blob


def test_scan_blocks_forbidden_results_plugin_messages(tmp_path):
    downloads = tmp_path / "downloads"
    _write_zip(
        downloads / "2-Step-Challenge-Analyzer.zip",
        {
            "2-Step Challenge Analyzer/index.html": (
                "<script>GET_SOURCE_CODE; resultsPlugins/create; "
                "fetch('https://example.invalid/x.json');</script>"
            ),
        },
    )

    payload = scan_downloads_payload(downloads)
    artifact = next(item for item in payload["artifacts"] if item["id"] == "two_step_challenge_analyzer")

    assert artifact["status"] == "scanned"
    assert "GET_SOURCE_CODE" in artifact["scan"]["blockedMarkersDetected"]
    assert "resultsPlugins/create" in artifact["scan"]["blockedMarkersDetected"]
    assert artifact["scan"]["remoteFetchDetected"] is True
    assert artifact["remoteNetworkObserved"] is True
    assert artifact["requiresOrdersGate"] is False


def test_smoke_runs_offline_fixtures_without_sqx_runtime():
    payload = template_smoke_payload(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "custom_results1_readonly_results_plugin_template_smoke_passed_no_install_no_sqx_runtime_no_db_no_projects_no_databanks_no_migration_tool"
    assert payload["templateRef"] == "integrations/sqx144/results_plugins/SQX Edge Custom Results Template"
    assert payload["forbiddenMarkersInTemplate"] == []
    assert payload["missingRequiredMarkers"] == []
    assert payload["fixtureNames"] == ["ready", "review", "blocked", "noStrategy", "missingStats", "largePortfolio"]


def test_payload_does_not_return_local_paths_or_private_strategy_names(tmp_path):
    downloads = tmp_path / "operator" / "CustomResultsSQX"
    _write_zip(
        downloads / "RobustnessScorecard.zip",
        {
            "RobustnessScorecard/index.html": "<script>STRATEGY_DATA; GET_STATS; STATS_RESPONSE;</script>",
        },
    )

    payload = scan_downloads_payload(downloads)
    blob = json.dumps(payload, ensure_ascii=False)

    assert "operator/CustomResultsSQX" not in blob.replace("\\", "/")
    assert str(downloads) not in blob
    assert payload["privacy"]["localPathsReturned"] is False
    assert payload["privacy"]["rawStrategyNamesReturned"] is False
    assert payload["privacy"]["rawOrdersReturned"] is False
