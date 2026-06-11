from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core import sqx144_custom_results8_regime_edge_analyzer as results8


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
        with patch.object(results8, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results8.status_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["version"] == results8.SQX144_CUSTOM_RESULTS8_VERSION
    assert payload["phaseLabel"] == "SQX144-CUSTOM-RESULTS8 - Regime Edge Analyzer"
    assert payload["status"] == results8.SQX144_CUSTOM_RESULTS8_STATUS
    assert payload["installExecuted"] is False
    assert payload["currentlyInstalled"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["writesUserProjects"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
    assert payload["guards"]["ordersRequestIsOptIn"] is True
    assert payload["guards"]["dataManagerProviderIsFutureGated"] is True
    assert payload["privacy"]["localPathsReturned"] is False


def test_smoke_accepts_regime_edge_runtime_and_fixtures():
    payload = results8.smoke_payload(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == results8.SQX144_CUSTOM_RESULTS8_SMOKE_STATUS
    assert payload["missingFiles"] == []
    assert payload["forbiddenMarkers"] == []
    assert payload["missingRequiredMarkers"] == []
    assert payload["fixtureNames"] == [
        "longBullStrong",
        "longBullMismatch",
        "longBearSurvival",
        "shortBearStrong",
        "shortBearMismatch",
        "sidewaysMeanRevert",
        "mixedUnknown",
        "missingSeries",
        "missingTimestamps",
        "fewTrades",
        "largeOrders",
        "noStrategy",
    ]
    assert "BULL" in payload["regimeLabels"]
    assert "REGIME_MISMATCH_REVIEW" in payload["decisionLabels"]
    assert "Bailey Lopez de Prado Deflated Sharpe Ratio" in payload["academicSources"]


def test_report_declares_source_ready_copy_only_install_gate_without_apply():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        payload = results8.report_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["ok"] is True
    assert payload["installExecuted"] is False
    assert payload["installPlan"]["copyOnlySqxEdgeOwnedPlugin"] is True
    assert payload["installPlan"]["copyOriginalDownloadedPlugins"] is False
    assert payload["installPlan"]["copyRandomEntries"] is False
    assert payload["methodology"]["selectedStrategyOnlyV1"] is True
    assert payload["methodology"]["fullDatabankV2RequiresSeparateProvider"] is True
    assert results8.INSTALL_APPROVAL_PHRASE in payload["installRequiresExactApproval"]


def test_report_reflects_installed_target_when_hashes_match():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results8, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            results8.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results8.INSTALL_APPROVAL_PHRASE,
            )
        payload = results8.report_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["status"] == results8.SQX144_CUSTOM_RESULTS8_INSTALLED_STATUS
    assert payload["installExecuted"] is True
    assert payload["currentlyInstalled"] is True
    assert payload["targetState"]["targetMatchesSource"] is True


def test_install_dry_run_does_not_copy_to_fake_host():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results8.PLUGIN_NAME
        with patch.object(results8, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results8.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=False)

    assert payload["ok"] is True
    assert payload["status"] == results8.SQX144_CUSTOM_RESULTS8_INSTALL_STATUS
    assert payload["installExecuted"] is False
    assert payload["wouldWriteSqxHost"] is True
    assert not target.exists()


def test_install_apply_requires_exact_approval():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results8, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            with pytest.raises(results8.CustomResults8Error) as raised:
                results8.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=True, approval="APRUEBO REGIME")

    assert raised.value.code == "custom_results8_regime_edge_analyzer_install_requires_exact_approval"


def test_preflight_blocks_running_sqx_and_non_owned_target():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results8.PLUGIN_NAME
        target.mkdir()
        (target / "index.html").write_text("<html>other plugin</html>", encoding="utf-8")
        with patch.object(
            results8,
            "_detect_sqx_processes",
            return_value={"known": True, "processCount": 1, "processNames": ["StrategyQuantX.exe"]},
        ):
            payload = results8.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=False)

    assert payload["ok"] is False
    assert "sqx_or_java_process_running" in payload["preflight"]["blockers"]
    assert "target_plugin_exists_without_sqx_edge_marker" in payload["preflight"]["blockers"]
    assert payload["guards"]["writesSqxHost"] is False


def test_install_apply_with_exact_approval_copies_only_to_temp_host():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results8.PLUGIN_NAME
        with patch.object(results8, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results8.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results8.INSTALL_APPROVAL_PHRASE,
            )

        assert payload["ok"] is True
        assert payload["status"] == results8.SQX144_CUSTOM_RESULTS8_INSTALLED_STATUS
        assert payload["installExecuted"] is True
        assert payload["targetMatchesSource"] is True
        assert payload["copiedFiles"] >= len(results8.EXPECTED_FILES)
        assert (target / "index.html").is_file()
        assert (target / "regime-edge.js").is_file()


def test_install_apply_backs_up_existing_owned_target():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results8.PLUGIN_NAME
        target.mkdir()
        (target / "index.html").write_text(results8.SQX144_CUSTOM_RESULTS8_VERSION, encoding="utf-8")
        with patch.object(results8, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results8.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results8.INSTALL_APPROVAL_PHRASE,
            )

    assert payload["ok"] is True
    assert payload["backupCreated"] is True
    assert payload["backupId"]
    assert payload["installExecuted"] is True
