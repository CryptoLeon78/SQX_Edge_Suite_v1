from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core import sqx144_custom_results5_edge_gate as results5


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _fake_sqx144_full(root: Path) -> Path:
    sqx = root / "SQX_144_Full"
    (sqx / "user" / "extend" / "ResultsPlugins").mkdir(parents=True)
    return sqx


def _no_sqx_processes() -> dict:
    return {"known": True, "processCount": 0, "processNames": []}


def test_status_is_source_ready_without_host_mutation():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results5, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results5.status_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["version"] == results5.SQX144_CUSTOM_RESULTS5_VERSION
    assert payload["phaseLabel"] == "SQX144-CUSTOM-RESULTS5 - SQX Edge Gate"
    assert payload["status"] == results5.SQX144_CUSTOM_RESULTS5_STATUS
    assert payload["installExecuted"] is False
    assert payload["currentlyInstalled"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["writesUserProjects"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
    assert payload["guards"]["ordersRequestIsOptIn"] is True
    assert payload["privacy"]["localPathsReturned"] is False


def test_smoke_accepts_edge_gate_runtime_and_fixtures():
    payload = results5.smoke_payload(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == results5.SQX144_CUSTOM_RESULTS5_SMOKE_STATUS
    assert payload["missingFiles"] == []
    assert payload["forbiddenMarkers"] == []
    assert payload["missingRequiredMarkers"] == []
    assert payload["fixtureNames"] == ["pass", "review", "block", "noStrategy", "missingStats", "missingOOS", "ordersOptIn", "largeOrders"]
    assert payload["thresholds"]["NumberOfTrades"] == ">= 120"
    assert payload["thresholds"]["ProfitFactor"] == ">= 1.3"
    assert payload["thresholds"]["ReturnDDRatio"] == ">= 4"


def test_report_declares_copy_only_install_gate_without_apply():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        payload = results5.report_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["ok"] is True
    assert payload["installExecuted"] is False
    assert payload["installPlan"]["copyOnlySqxEdgeOwnedPlugin"] is True
    assert payload["installPlan"]["copyOriginalDownloadedPlugins"] is False
    assert payload["installPlan"]["copyRandomEntries"] is False
    assert results5.INSTALL_APPROVAL_PHRASE in payload["installRequiresExactApproval"]


def test_report_reflects_installed_target_when_hashes_match():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results5, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            results5.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results5.INSTALL_APPROVAL_PHRASE,
            )
        payload = results5.report_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["status"] == results5.SQX144_CUSTOM_RESULTS5_INSTALLED_STATUS
    assert payload["installExecuted"] is True
    assert payload["currentlyInstalled"] is True
    assert payload["targetState"]["targetMatchesSource"] is True


def test_install_dry_run_does_not_copy_to_fake_host():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results5.PLUGIN_NAME
        with patch.object(results5, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results5.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=False)

    assert payload["ok"] is True
    assert payload["status"] == results5.SQX144_CUSTOM_RESULTS5_INSTALL_STATUS
    assert payload["installExecuted"] is False
    assert payload["wouldWriteSqxHost"] is True
    assert not target.exists()


def test_install_apply_requires_exact_approval():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results5, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            with pytest.raises(results5.CustomResults5Error) as raised:
                results5.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=True, approval="APRUEBO EDGE GATE")

    assert raised.value.code == "custom_results5_install_requires_exact_approval"


def test_preflight_blocks_running_sqx_and_non_owned_target():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results5.PLUGIN_NAME
        target.mkdir()
        (target / "index.html").write_text("<html>other plugin</html>", encoding="utf-8")
        with patch.object(
            results5,
            "_detect_sqx_processes",
            return_value={"known": True, "processCount": 1, "processNames": ["StrategyQuantX.exe"]},
        ):
            payload = results5.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=False)

    assert payload["ok"] is False
    assert "sqx_or_java_process_running" in payload["preflight"]["blockers"]
    assert "target_plugin_exists_without_sqx_edge_marker" in payload["preflight"]["blockers"]
    assert payload["guards"]["writesSqxHost"] is False


def test_install_apply_with_exact_approval_copies_only_to_temp_host():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results5.PLUGIN_NAME
        with patch.object(results5, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results5.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results5.INSTALL_APPROVAL_PHRASE,
            )

        assert payload["ok"] is True
        assert payload["status"] == results5.SQX144_CUSTOM_RESULTS5_INSTALLED_STATUS
        assert payload["installExecuted"] is True
        assert payload["targetMatchesSource"] is True
        assert payload["copiedFiles"] >= len(results5.EXPECTED_FILES)
        assert (target / "index.html").is_file()
        assert (target / "edge-gate.js").is_file()


def test_install_apply_backs_up_existing_owned_target():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results5.PLUGIN_NAME
        target.mkdir()
        (target / "index.html").write_text(results5.SQX144_CUSTOM_RESULTS5_VERSION, encoding="utf-8")
        with patch.object(results5, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results5.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results5.INSTALL_APPROVAL_PHRASE,
            )

    assert payload["ok"] is True
    assert payload["backupCreated"] is True
    assert payload["backupId"]
    assert payload["installExecuted"] is True
