from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path

import core.bsai17_controlled_import_start_gate as bsai17
from core.bsai16_capa1_experiment_gate import prepare_payload
from core.bsai17_controlled_import_start_gate import (
    BS_AI17_CONTROLLED_IMPORT_START_VERSION,
    import_capa1_payload,
    preflight_payload,
    start_capa1_payload,
)


CANDIDATE_ID = "BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005"
EXPERIMENT_ID = "BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001"
PROJECT_ROOT_STEM = f"BSAI_AUDCAD_H1_{CANDIDATE_ID}_L_SQX144DARWINEX"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_repo_config(root: Path, projects_dir: Path, db_path: Path) -> None:
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config.json",
        {
            "sqx_path": str(root / "host"),
            "sqx_projects_dir": str(projects_dir),
            "sqx_data_db": str(db_path),
            "sqx_host_profile": "sqx144_full",
        },
    )


def _write_candidate(root: Path) -> None:
    _write_json(
        root / ".local" / "blocksettings_ai" / "candidates" / f"{CANDIDATE_ID}.json",
        {
            "entry": {
                "canonicalId": CANDIDATE_ID,
                "baseCanonicalId": "BS_Filtros_v7_H1",
                "promotionState": "local_candidate",
                "localPath": str(root / "must_not_leak.sqb"),
            },
            "recipe": {
                "asset": "AUDCAD",
                "timeframe": "H1",
                "direction": "long",
                "candidateLayer": 2,
                "baseCanonicalId": "BS_Filtros_v7_H1",
            },
        },
    )


def _write_catalog_db(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE INSTRUMENTS (
              INSTRUMENT TEXT,
              BROKER_ID INTEGER,
              DEFAULTSPREAD REAL
            );
            CREATE TABLE DATA (
              SYMBOL TEXT,
              INSTRUMENT TEXT,
              TIMEFRAME TEXT,
              SOURCE INTEGER,
              BROKER_ID INTEGER,
              ROWS INTEGER,
              USYMBOL TEXT
            );
            """
        )
        conn.executemany(
            "INSERT INTO INSTRUMENTS (INSTRUMENT, BROKER_ID, DEFAULTSPREAD) VALUES (?, ?, ?)",
            [
                ("AUDCAD_darwinex", 4, 1.0),
                ("AUDCAD_dukascopy", 3, 1.9),
            ],
        )
        conn.executemany(
            "INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, USYMBOL) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("AUDCAD_darwinex", "AUDCAD_darwinex", "TICK", 4, 4, 1000, "AUDCAD"),
                ("AUDCAD_dukascopy", "AUDCAD_darwinex", "TICK", 2, 4, 1000, "AUDCAD"),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return path


def _condition(column: str, value: str, comparator: str = ">=") -> str:
    return (
        '<Condition use="true"><Left-Side valueType="column">'
        f'<Column-Value column="{column}" resultType="main" pctRatio="0" />'
        f'</Left-Side><Comparator value="{comparator}" />'
        f'<Right-Side valueType="numeric"><Numeric-Value value="{value}" /></Right-Side></Condition>'
    )


def _relative_number_of_trades(pct: str = "80") -> str:
    return (
        '<Condition use="true"><Left-Side valueType="column">'
        '<Column-Value column="NumberOfTrades" name="# of trades" resultType="RetestWithHigherPrecision" pctRatio="0" />'
        '</Left-Side><Comparator value=">=" /><Right-Side valueType="column">'
        f'<Column-Value column="NumberOfTrades" name="# of trades" resultType="main" pctRatio="{pct}" />'
        "</Right-Side></Condition>"
    )


def _task_xml(symbol: str, spread: str = "1") -> str:
    return f"""
    <Task>
      <Data><Setups><Setup><Chart symbol="{symbol}" timeframe="H1" spread="{spread}" /></Setup></Setups></Data>
      <Resources><Symbols><Symbol name="{symbol}" source="4" broker="4" precision="TICK" /></Symbols></Resources>
    </Task>
    """


def _tick_xml(spread: str = "1") -> str:
    return (
        '<Task><Data><Setups><Setup><Chart symbol="AUDCAD_darwinex" timeframe="H1" spread="'
        + spread
        + '" /></Setup></Setups></Data><Rankings><Conditions>'
        + _condition("NumberOfTrades", "200")
        + _condition("ProfitFactor", "1.3")
        + _condition("WinningPct", "50")
        + _condition("ReturnDDRatio", "4")
        + _relative_number_of_trades("80")
        + "</Conditions></Rankings></Task>"
    )


def _write_project_cfx(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", '<Project name="old_project"><Task type="Build" title="old" /></Project>')
        archive.writestr("Build-Task1.xml", _task_xml("AUDCAD_darwinex"))
        archive.writestr("Retest-Task3.xml", _task_xml("AUDCAD_darwinex"))
        archive.writestr("Retest-Task1.xml", _task_xml("AUDCAD_dukascopy"))
        archive.writestr("AutomaticRetest-Task2.xml", _tick_xml())
        archive.writestr("Retest-Task2.xml", _task_xml("AUDCAD_darwinex"))
    return path


def _fixture(root: Path) -> Path:
    projects_dir = root / "host" / "user" / "projects"
    db_path = root / "host" / "user" / "data" / "data.db"
    _write_repo_config(root, projects_dir, _write_catalog_db(db_path))
    _write_candidate(root)
    project_name = f"{PROJECT_ROOT_STEM}_Capa1"
    _write_project_cfx(projects_dir / project_name / "project.cfx")
    prepared = prepare_payload(root, retention_ratio=0.65, absolute_floor=120)
    assert prepared["experiment"]["id"] == EXPERIMENT_ID
    assert prepared["artifact"]["zipValid"] is True
    return root


def _project_match(project_name: str, *, strategies: int = 0) -> dict:
    return {
        "projectName": project_name,
        "tasks": 14,
        "databanks": 15,
        "strategies": strategies,
        "hasUnresolvedResources": False,
    }


def test_preflight_blocks_cross_broker_warning_until_trial_acceptance(tmp_path, monkeypatch):
    _fixture(tmp_path)

    def fake_get(remote_base_url, endpoint, params=None, timeout=30):
        assert endpoint == "taskmanager/listProjects"
        return {"projects": []}

    monkeypatch.setattr(bsai17, "_http_json_get", fake_get)
    payload = preflight_payload(tmp_path)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI17_CONTROLLED_IMPORT_START_VERSION
    assert payload["ok"] is False
    assert "cross_broker_spread_warning_not_accepted_for_this_trial" in payload["blockers"]
    assert payload["operatorApproval"]["crossBrokerSpreadWarningAccepted"] is False
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob
    assert "must_not_leak" not in blob


def test_preflight_allows_import_after_trial_warning_acceptance(tmp_path, monkeypatch):
    _fixture(tmp_path)

    def fake_get(remote_base_url, endpoint, params=None, timeout=30):
        assert endpoint == "taskmanager/listProjects"
        return {"projects": []}

    monkeypatch.setattr(bsai17, "_http_json_get", fake_get)
    payload = preflight_payload(tmp_path, accept_cross_broker_spread_warning=True)

    assert payload["ok"] is True
    assert payload["status"] == "controlled_capa1_import_start_preflight_ready"
    assert payload["nextAction"] == "import-capa1"
    assert payload["warnings"] == ["cross_broker_spread_warning_accepted_for_this_trial_only"]
    assert payload["guards"]["capa2StartAllowed"] is False
    assert payload["guards"]["loadAsIsAllowed"] is False
    assert payload["privacy"]["localPathsReturned"] is False


def test_import_capa1_uses_load_as_is_false_and_does_not_start(tmp_path, monkeypatch):
    _fixture(tmp_path)
    calls: list[tuple[str, dict | None]] = []

    def fake_get(remote_base_url, endpoint, params=None, timeout=30):
        calls.append((endpoint, params))
        if endpoint == "taskmanager/listProjects":
            if len([call for call in calls if call[0] == "taskmanager/listProjects"]) == 1:
                return {"projects": []}
            return {"projects": [_project_match(EXPERIMENT_ID)]}
        if endpoint == "taskmanager/openProject":
            assert params["loadAsIs"] == "false"
            assert str(params["file"]).endswith(f"{EXPERIMENT_ID}.cfx")
            return {"success": True, "projectName": EXPERIMENT_ID, "resourcesXML": "", "configXML": ""}
        raise AssertionError(endpoint)

    monkeypatch.setattr(bsai17, "_http_json_get", fake_get)
    payload = import_capa1_payload(tmp_path, accept_cross_broker_spread_warning=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["ok"] is True
    assert payload["status"] == "controlled_capa1_imported_visible_no_start"
    assert payload["remoteEndpoint"] == "taskmanager/openProject"
    assert payload["loadAsIsRequested"] is False
    assert payload["loadAsIsEscalated"] is False
    assert payload["projectStartRequested"] is False
    assert payload["guards"]["hostImportMayWriteDataDb"] is True
    assert payload["guards"]["capa2StartAllowed"] is False
    assert "project/start" not in [endpoint for endpoint, _ in calls]
    assert str(tmp_path) not in blob
    assert "<Task" not in blob


def test_start_capa1_posts_only_target_project_and_keeps_capa2_blocked(tmp_path, monkeypatch):
    _fixture(tmp_path)
    calls: list[tuple[str, dict | None]] = []

    def fake_get(remote_base_url, endpoint, params=None, timeout=30):
        calls.append((endpoint, params))
        assert endpoint == "taskmanager/listProjects"
        return {"projects": [_project_match(EXPERIMENT_ID)]}

    def fake_post(remote_base_url, endpoint, data, timeout=30):
        calls.append((endpoint, data))
        assert endpoint == "project/start"
        assert data == {"projectName": EXPERIMENT_ID}
        return {"success": True, "message": "Project execution started."}

    monkeypatch.setattr(bsai17, "_http_json_get", fake_get)
    monkeypatch.setattr(bsai17, "_http_json_post_gzip_form", fake_post)
    payload = start_capa1_payload(
        tmp_path,
        accept_cross_broker_spread_warning=True,
        observe_seconds=0,
        poll_seconds=1,
    )
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["ok"] is True
    assert payload["status"] == "controlled_capa1_import_start_requested_no_capa2"
    assert payload["remoteEndpoint"] == "project/start"
    assert payload["projectStartRequested"] is True
    assert payload["guards"]["projectStartAllowed"] is True
    assert payload["guards"]["capa2StartAllowed"] is False
    assert payload["observedEffects"]["capa2StartRequested"] is False
    assert ("project/start", {"projectName": EXPERIMENT_ID}) in calls
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
