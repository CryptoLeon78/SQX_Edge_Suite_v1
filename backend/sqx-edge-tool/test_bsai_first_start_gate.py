from __future__ import annotations

import json
from pathlib import Path

import core.bsai_first_start_gate as gate
from core.bsai_first_start_gate import BS_AI13_FIRST_START_GATE_VERSION
from test_bsai_imported_project_review import CANDIDATE_ID, PROJECT_ROOT_STEM, _fixture


CAPA1_PROJECT = f"{PROJECT_ROOT_STEM}_Capa1"
CAPA2_PROJECT = f"{PROJECT_ROOT_STEM}_Capa2"


def _first_start_fixture(root: Path) -> Path:
    repo = _fixture(root)
    config_path = repo / "backend" / "sqx-edge-tool" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["sqx_path"] = str(repo / "host")
    config_path.write_text(json.dumps(config), encoding="utf-8")
    (repo / "host" / "user" / "log" / "StrategyQuant").mkdir(parents=True, exist_ok=True)
    return repo


def _review_ok(monkeypatch) -> None:
    monkeypatch.setattr(
        gate,
        "review_payload",
        lambda *args, **kwargs: {
            "ok": True,
            "status": "imported_project_readonly_review_passed_with_methodology_warnings_no_start",
            "summary": {
                "targetFailCount": 0,
                "targetWarnCount": 2,
            },
        },
    )


def _fake_projects(*, capa1_strategies: int = 0, capa2_strategies: int = 0, unresolved: bool = False) -> dict:
    return {
        "success": True,
        "projects": [
            {
                "projectName": CAPA1_PROJECT,
                "tasks": 14,
                "databanks": 15,
                "strategies": capa1_strategies,
                "hasUnresolvedResources": unresolved,
                "filePath": "C:/must/not/leak/project.cfx",
            },
            {
                "projectName": CAPA2_PROJECT,
                "tasks": 14,
                "databanks": 15,
                "strategies": capa2_strategies,
                "hasUnresolvedResources": unresolved,
                "filePath": "C:/must/not/leak/project.cfx",
            },
        ],
    }


def test_preflight_ready_is_sanitized_first_start_only(tmp_path, monkeypatch):
    root = _first_start_fixture(tmp_path)
    _review_ok(monkeypatch)
    monkeypatch.setattr(gate, "_http_json_get", lambda *args, **kwargs: _fake_projects())

    payload = gate.preflight_payload(root, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI13_FIRST_START_GATE_VERSION
    assert payload["ok"] is True
    assert payload["status"] == "first_start_preflight_ready"
    assert payload["targetProject"] == CAPA1_PROJECT
    assert payload["projectNames"] == [CAPA1_PROJECT, CAPA2_PROJECT]
    assert payload["runsSqxTasks"] is False
    assert payload["projectStartRequested"] is False
    assert payload["capa2StartAllowed"] is False
    assert payload["hostRunMayMutateTargetDatabanks"] is False
    assert payload["evidenceFile"].startswith("bsai13_first_manual_start_gate_preflight_")
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "C:/must/not/leak" not in blob


def test_preflight_blocks_if_capa1_already_has_strategies(tmp_path, monkeypatch):
    root = _first_start_fixture(tmp_path)
    _review_ok(monkeypatch)
    monkeypatch.setattr(gate, "_http_json_get", lambda *args, **kwargs: _fake_projects(capa1_strategies=3))

    payload = gate.preflight_payload(root)

    assert payload["ok"] is False
    assert payload["status"] == "first_start_preflight_blocked"
    assert "capa1_not_first_start_strategies_already_present" in payload["blockers"]
    assert payload["nextAction"] == "fix_blockers_before_start"


def test_start_capa1_posts_only_capa1_and_observes_no_capa2_start(tmp_path, monkeypatch):
    root = _first_start_fixture(tmp_path)
    _review_ok(monkeypatch)
    calls: list[tuple[str, dict]] = []

    monkeypatch.setattr(gate, "_http_json_get", lambda *args, **kwargs: _fake_projects())

    def fake_post(remote_base_url, endpoint, data, timeout=30):
        calls.append((endpoint, data))
        return {"success": True, "error": None}

    monkeypatch.setattr(gate, "_http_json_post_gzip_form", fake_post)

    payload = gate.start_capa1_payload(root, observe_seconds=0, poll_seconds=1, write_evidence=True)

    assert payload["ok"] is True
    assert payload["status"] == "first_start_requested_observed_no_capa2_start"
    assert payload["runsSqxTasks"] is True
    assert payload["hostRunMayMutateTargetDatabanks"] is True
    assert payload["capa2StartAllowed"] is False
    assert payload["observedEffects"]["capa2StartRequested"] is False
    assert payload["nextGate"] == "BS-AI14 monitor Capa1 run and decide Capa2 start"
    assert calls == [("project/start", {"projectName": CAPA1_PROJECT})]
    assert CAPA2_PROJECT not in json.dumps(calls)
    assert payload["startResponse"]["errorPresent"] is False


def test_start_is_blocked_by_preflight_and_does_not_post(tmp_path, monkeypatch):
    root = _first_start_fixture(tmp_path)
    _review_ok(monkeypatch)
    monkeypatch.setattr(gate, "_http_json_get", lambda *args, **kwargs: _fake_projects(capa1_strategies=1))
    monkeypatch.setattr(
        gate,
        "_http_json_post_gzip_form",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("start must not be called")),
    )

    payload = gate.start_capa1_payload(root, observe_seconds=0, poll_seconds=1, write_evidence=False)

    assert payload["ok"] is False
    assert payload["status"] == "first_start_blocked_by_preflight"
    assert payload["projectStartRequested"] is True
    assert payload["preflightBlockers"] == ["capa1_not_first_start_strategies_already_present"]
