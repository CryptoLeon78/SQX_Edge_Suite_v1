from __future__ import annotations

import json
from pathlib import Path

import core.bsai18_capa1_monitor_gate as bsai18
from core.bsai18_capa1_monitor_gate import (
    BS_AI18_CAPA1_MONITOR_GATE_VERSION,
    _decision,
    status_payload,
)


EXPERIMENT_ID = "BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_config(root: Path) -> None:
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config.json",
        {
            "sqx_path": str(root / "host"),
            "sqx_projects_dir": str(root / "host" / "user" / "projects"),
            "sqx_data_db": str(root / "host" / "user" / "data" / "data.db"),
            "sqx_host_profile": "sqx144_full",
        },
    )


def _sample(*, strategies: int, log_size: int, reachable: bool = True, found: bool = True, unresolved: bool = False) -> dict:
    return {
        "atUtc": "2026-06-07T21:00:00+00:00",
        "remote": {
            "reachable": reachable,
            "found": found,
            "strategies": strategies,
            "tasks": 14 if found else None,
            "databanks": 15 if found else None,
            "hasUnresolvedResources": unresolved if found else None,
        },
        "latestLog": {"size": log_size, "ageSeconds": 10},
        "databanks": {"items": []},
    }


def test_bsai18_version_marker():
    assert BS_AI18_CAPA1_MONITOR_GATE_VERSION == "bs-ai18-capa1-monitor-gate-v1"


def test_decision_keeps_active_capa1_monitoring_without_capa2():
    decision = _decision([_sample(strategies=65, log_size=100), _sample(strategies=80, log_size=200)])

    assert decision["decision"] == "continue_monitoring_capa1_active_no_capa2"
    assert decision["capa1Strategies"] == 80
    assert decision["strategyDelta"] == 15
    assert decision["latestLogChanged"] is True
    assert decision["capa2StartAllowed"] is False
    assert decision["projectStartAllowed"] is False
    assert decision["projectStopAllowed"] is False


def test_decision_blocks_remote_unavailable_without_enabling_actions():
    decision = _decision([_sample(strategies=0, log_size=100, reachable=False, found=False)])

    assert decision["decision"] == "monitor_blocked_review_required_no_capa2"
    assert "remote_access_unavailable" in decision["blockers"]
    assert decision["capa2StartAllowed"] is False
    assert decision["projectStartAllowed"] is False
    assert decision["projectStopAllowed"] is False


def test_status_payload_is_readonly_and_public_safe(tmp_path, monkeypatch):
    _write_config(tmp_path)

    def fake_remote(remote_base_url, project_name):
        assert project_name == EXPERIMENT_ID
        return {
            "endpoint": "taskmanager/listProjects",
            "reachable": True,
            "projectName": project_name,
            "found": True,
            "tasks": 14,
            "databanks": 15,
            "strategies": 65,
            "hasUnresolvedResources": False,
            "sqxReturnedProjectPath": True,
            "sqxProjectPathStored": False,
        }

    monkeypatch.setattr(bsai18, "_remote_project_match", fake_remote)
    payload = status_payload(tmp_path)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI18_CAPA1_MONITOR_GATE_VERSION
    assert payload["status"] == "monitoring_capa1_bsa16_no_capa2"
    assert payload["guards"]["readOnly"] is True
    assert payload["guards"]["projectStartRequested"] is False
    assert payload["guards"]["projectStopRequested"] is False
    assert payload["guards"]["taskmanagerOpenProjectAllowed"] is False
    assert payload["guards"]["capa2StartAllowed"] is False
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob
