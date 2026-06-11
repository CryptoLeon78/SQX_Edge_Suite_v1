from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core import sqx144_custom_results3_install_gate as results3


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _fake_sqx144_full(root: Path) -> Path:
    sqx = root / "SQX_144_Full"
    (sqx / "user" / "extend" / "ResultsPlugins").mkdir(parents=True)
    return sqx


def _no_sqx_processes() -> dict:
    return {"known": True, "processCount": 0, "processNames": []}


def test_status_declares_optional_manual_install_gate_without_host_mutation():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results3.status_payload(PROJECT_ROOT, sqx_root=sqx)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == "sqx144-custom-results3-optional-manual-install-gate-v1"
    assert payload["phaseLabel"] == "SQX144-CUSTOM-RESULTS3 - Optional Manual Install Gate"
    assert payload["status"] == "custom_results3_optional_manual_install_gate_ready_no_install_no_launch_no_db_no_projects_no_databanks_no_tasks_no_migration_tool"
    assert payload["installExecuted"] is False
    assert payload["copiesSqxEdgeOwnedBundleOnly"] is True
    assert payload["copiesDownloadedThirdPartyPlugins"] is False
    assert payload["downloadedPluginsInstalled"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["writesUserProjects"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
    assert payload["guards"]["usesMigrationTool"] is False
    assert payload["privacy"]["localPathsReturned"] is False
    assert str(sqx) not in blob


def test_preflight_ready_when_source_and_fake_host_are_clean():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results3.preflight_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["ok"] is True
    assert payload["status"] == "custom_results3_preflight_ready_no_install"
    assert payload["blockers"] == []
    assert payload["hostRootAccepted"] is True
    assert payload["resultsPluginsRootPresent"] is True
    assert payload["targetState"]["sourceFileCount"] >= 3
    assert payload["moduleSmoke"]["ok"] is True


def test_preflight_blocks_running_sqx_process_and_wrong_target_marker():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results3.PLUGIN_NAME
        target.mkdir()
        (target / "index.html").write_text("<html>third party plugin</html>", encoding="utf-8")
        with patch.object(
            results3,
            "_detect_sqx_processes",
            return_value={"known": True, "processCount": 1, "processNames": ["StrategyQuantX.exe"]},
        ):
            payload = results3.preflight_payload(PROJECT_ROOT, sqx_root=sqx)

    assert payload["ok"] is False
    assert "sqx_or_java_process_running" in payload["blockers"]
    assert "target_plugin_exists_without_sqx_edge_marker" in payload["blockers"]
    assert payload["guards"]["writesSqxHost"] is False


def test_plan_contains_hash_manifest_and_exact_approval_without_paths():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results3.plan_payload(PROJECT_ROOT, sqx_root=sqx)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["ok"] is True
    assert payload["status"] == "custom_results3_install_plan_ready_no_apply"
    assert payload["fileCount"] >= 3
    assert "index.html" in {row["relativePath"] for row in payload["fileManifest"]}
    assert payload["plannedCopy"]["copyOnlySqxEdgeOwnedBundle"] is True
    assert payload["plannedCopy"]["copyDownloadedThirdPartyPlugins"] is False
    assert payload["plannedCopy"]["getOrdersRuntimeAcknowledgementRequired"] is True
    assert results3.INSTALL_APPROVAL_PHRASE in payload["installRequiresExactApproval"]
    assert str(sqx) not in blob


def test_install_dry_run_does_not_copy_to_fake_host():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results3.PLUGIN_NAME
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results3.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=False)

    assert payload["ok"] is True
    assert payload["status"] == results3.SQX144_CUSTOM_RESULTS3_INSTALL_STATUS
    assert payload["installExecuted"] is False
    assert payload["wouldWriteSqxHost"] is True
    assert not target.exists()


def test_install_apply_requires_exact_approval():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            with pytest.raises(results3.CustomResults3Error) as raised:
                results3.install_payload(PROJECT_ROOT, sqx_root=sqx, apply=True, approval="APRUEBO CUSTOM RESULTS3")

    assert raised.value.code == "custom_results3_install_requires_exact_approval"


def test_install_apply_with_exact_approval_copies_only_to_temp_host():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        target = sqx / "user" / "extend" / "ResultsPlugins" / results3.PLUGIN_NAME
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results3.install_payload(
                PROJECT_ROOT,
                sqx_root=sqx,
                apply=True,
                approval=results3.INSTALL_APPROVAL_PHRASE,
            )

        assert payload["ok"] is True
        assert payload["status"] == results3.SQX144_CUSTOM_RESULTS3_INSTALLED_STATUS
        assert payload["installExecuted"] is True
        assert payload["copiedFiles"] >= 3
        assert payload["guards"]["writesSqxHost"] is True
        assert (target / "index.html").is_file()


def test_rollback_dry_run_requires_backup_id():
    with tempfile.TemporaryDirectory() as tmp:
        sqx = _fake_sqx144_full(Path(tmp))
        with patch.object(results3, "_detect_sqx_processes", return_value=_no_sqx_processes()):
            payload = results3.rollback_payload(PROJECT_ROOT, sqx_root=sqx, apply=False)

    assert payload["ok"] is False
    assert payload["rollbackExecuted"] is False
    assert "backup_id_required" in payload["blockers"]
