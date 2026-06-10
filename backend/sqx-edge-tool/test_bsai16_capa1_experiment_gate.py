from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from core.bsai16_capa1_experiment_gate import (
    BS_AI16_CAPA1_EXPERIMENT_GATE_VERSION,
    BS_AI16_STATUS,
    prepare_payload,
    status_payload,
)


CANDIDATE_ID = "BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005"
PROJECT_ROOT_STEM = f"BSAI_AUDCAD_H1_{CANDIDATE_ID}_L_SQX144DARWINEX"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_repo_config(root: Path, projects_dir: Path, db_path: Path) -> None:
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config.json",
        {
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


def _write_catalog_db(path: Path, *, primary_spread: float = 1.0, cross_spread: float = 1.9) -> Path:
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
                ("AUDCAD_darwinex", 4, primary_spread),
                ("AUDCAD_dukascopy", 3, cross_spread),
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


def _write_project_cfx(path: Path, *, primary_spread: str = "1", cross_spread: str = "1") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", '<Project name="old_project"><Task type="Build" title="old" /></Project>')
        archive.writestr("Build-Task1.xml", _task_xml("AUDCAD_darwinex", primary_spread))
        archive.writestr("Retest-Task3.xml", _task_xml("AUDCAD_darwinex", primary_spread))
        archive.writestr("Retest-Task1.xml", _task_xml("AUDCAD_dukascopy", cross_spread))
        archive.writestr("AutomaticRetest-Task2.xml", _tick_xml(primary_spread))
        archive.writestr("Retest-Task2.xml", _task_xml("AUDCAD_darwinex", primary_spread))
    return path


def _fixture(root: Path, *, db_primary_spread: float = 1.0, cfx_primary_spread: str = "1") -> Path:
    projects_dir = root / "host" / "user" / "projects"
    db_path = root / "host" / "user" / "data" / "data.db"
    _write_repo_config(root, projects_dir, _write_catalog_db(db_path, primary_spread=db_primary_spread))
    _write_candidate(root)
    project_name = f"{PROJECT_ROOT_STEM}_Capa1"
    _write_project_cfx(projects_dir / project_name / "project.cfx", primary_spread=cfx_primary_spread, cross_spread="1")
    return root


def test_status_preregisters_rule_and_flags_spread_warning_without_paths_or_xml(tmp_path):
    payload = status_payload(_fixture(tmp_path), retention_ratio=0.65, absolute_floor=120)
    blob = json.dumps(payload, ensure_ascii=False)

    assert BS_AI16_CAPA1_EXPERIMENT_GATE_VERSION == "bs-ai16-capa1-experiment-prereg-gate-v1"
    assert BS_AI16_STATUS == "preregistered_capa1_tick_rule_ready_no_import_no_start"
    assert payload["version"] == BS_AI16_CAPA1_EXPERIMENT_GATE_VERSION
    assert payload["status"] == BS_AI16_STATUS
    assert payload["ok"] is True
    assert payload["preRegisteredTradeRule"]["formula"] == "realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))"
    assert payload["preRegisteredTradeRule"]["retentionPct"] == 65
    assert payload["preRegisteredTradeRule"]["absoluteFloor"] == 120
    assert {"priorValidationTrades": 300, "requiredRealTickTrades": 195} in payload["preRegisteredTradeRule"]["effectiveThresholdExamples"]
    assert payload["currentTickRealRule"]["absoluteNumberOfTrades"] == "200"
    assert payload["currentTickRealRule"]["relativeNumberOfTradesPct"] == "80"
    assert payload["spreadCostSanity"]["verdict"] == "warn_spread_cost_review_before_run"
    assert payload["spreadCostSanity"]["catalog"]["primaryDefaultSpread"] == 1.0
    assert payload["spreadCostSanity"]["catalog"]["crossBrokerDefaultSpread"] == 1.9
    assert payload["warnings"] == ["spread_cost_sanity_warning"]
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob
    assert "must_not_leak" not in blob


def test_prepare_writes_local_cfx_and_patches_only_preregistered_tick_trade_rule(tmp_path):
    _fixture(tmp_path)
    payload = prepare_payload(tmp_path, retention_ratio=0.65, absolute_floor=120, write_evidence=True)
    experiment_id = payload["experiment"]["id"]
    artifact_path = tmp_path / ".local" / "blocksettings_ai" / "capa1_experiments" / experiment_id / payload["artifact"]["artifactRef"]

    assert payload["ok"] is True
    assert payload["artifact"]["written"] is True
    assert payload["artifact"]["zipValid"] is True
    assert payload["artifact"]["sourceProjectCfxHashUnchanged"] is True
    assert payload["appliedLocalPatch"]["before"]["absoluteNumberOfTrades"] == "200"
    assert payload["appliedLocalPatch"]["before"]["relativeNumberOfTradesPct"] == "80"
    assert payload["appliedLocalPatch"]["after"]["absoluteNumberOfTrades"] == "120"
    assert payload["appliedLocalPatch"]["after"]["relativeNumberOfTradesPct"] == "65"
    assert payload["appliedLocalPatch"]["protectedFiltersUnchanged"] is True
    assert payload["evidenceRef"].startswith("bsai16_capa1_experiment_gate_prepare_")
    assert artifact_path.is_file()

    with zipfile.ZipFile(artifact_path, "r") as archive:
        config_root = ET.fromstring(archive.read("config.xml"))
        tick_root = ET.fromstring(archive.read("AutomaticRetest-Task2.xml"))
    assert config_root.get("name") == experiment_id
    assert tick_root.find(".//Numeric-Value").get("value") == "120"
    pct_values = [item.get("pctRatio") for item in tick_root.findall(".//Column-Value") if item.get("resultType") == "main"]
    assert "65" in pct_values


def test_primary_spread_below_host_catalog_blocks_prepare(tmp_path):
    payload = status_payload(_fixture(tmp_path, db_primary_spread=2.0, cfx_primary_spread="1"))

    assert payload["ok"] is False
    assert "spread_cost_sanity_primary_under_spread" in payload["blockers"]
    assert payload["spreadCostSanity"]["verdict"] == "fail_primary_spread_under_host_catalog"
    assert payload["guards"]["writesSqxHost"] is False
    assert payload["guards"]["projectStartRequested"] is False
    assert payload["guards"]["capa2StartAllowed"] is False
