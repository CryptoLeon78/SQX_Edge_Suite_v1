from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path

from core.bsai_imported_project_review import (
    BS_AI12_IMPORTED_PROJECT_REVIEW_VERSION,
    review_payload,
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
                "layer": 2,
                "baseCanonicalId": "BS_Filtros_v7_H1",
                "baseVariant": "v7_h1",
                "baseSha256": "A" * 64,
                "candidateRevision": "r005",
                "sourceVersionPolicy": "explicit_base_preserve_official_v6_v7",
                "promotionState": "local_candidate",
                "activeIndicators": ["Indicators.ADX"],
                "localPath": str(root / "must_not_leak.sqb"),
            },
            "recipe": {
                "asset": "AUDCAD",
                "timeframe": "H1",
                "direction": "long",
                "candidateLayer": 2,
                "baseCanonicalId": "BS_Filtros_v7_H1",
                "sourceVersionPolicy": "explicit_base_preserve_official_v6_v7",
            },
        },
    )


def _write_catalog_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE BROKER (ID INTEGER, NAME TEXT, POSTFIX TEXT, DESC TEXT);
            CREATE TABLE DATA (
              SYMBOL TEXT,
              INSTRUMENT TEXT,
              TIMEFRAME TEXT,
              SOURCE INTEGER,
              BROKER_ID INTEGER,
              ROWS INTEGER,
              USYMBOL TEXT
            );
            CREATE TABLE INSTRUMENTS (
              INSTRUMENT TEXT,
              BROKER_ID INTEGER,
              DEFAULTSPREAD REAL
            );
            """
        )
        conn.executemany(
            "INSERT INTO BROKER (ID, NAME, POSTFIX, DESC) VALUES (?, ?, ?, ?)",
            [
                (4, "Darwinex", "_darwinex", "Darwinex"),
                (3, "Dukascopy", "_dukascopy", "Dukascopy"),
            ],
        )
        conn.executemany(
            "INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, USYMBOL) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("AUDCAD_darwinex", "AUDCAD_darwinex", "TICK", 4, 4, 1000, "AUDCAD"),
                ("AUDCAD_dukascopy", "AUDCAD_darwinex", "TICK", 2, 4, 1000, "AUDCAD"),
            ],
        )
        conn.executemany(
            "INSERT INTO INSTRUMENTS (INSTRUMENT, BROKER_ID, DEFAULTSPREAD) VALUES (?, ?, ?)",
            [
                ("AUDCAD_darwinex", 4, 1.5),
                ("AUDCAD_dukascopy", 3, 1.9),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def _task_xml(symbol: str, source: str, broker: str) -> str:
    return f"""
    <Task>
      <Data><Setups><Setup><Chart symbol="{symbol}" /></Setup></Setups></Data>
      <Resources>
        <Symbols>
          <Symbol name="{symbol}" source="{source}" precision="TICK" timezone="EETUS" broker="{broker}">
            <InstrumentInfo instrument="AUDCAD_darwinex" dataType="1" broker="{broker}" />
          </Symbol>
        </Symbols>
        <Brokers><Broker id="4" name="Darwinex" /></Brokers>
      </Resources>
    </Task>
    """


def _task_plan(capa: int) -> list[tuple[str, str, str]]:
    build_title = (
        "Build BS_Volatilidad_v6_intraday_v6 · Capa1 LONG H1"
        if capa == 1
        else f"Build {CANDIDATE_ID} · Capa2 LONG H1"
    )
    names = [
        ("Build-Task1.xml", "Build", build_title),
        ("Retest-Task1.xml", "Retest", "RETEST 1"),
        ("Retest-Task2.xml", "Retest", "Forward"),
        ("Retest-Task3.xml", "Retest", "RETEST 0"),
        ("Retest-Task4.xml", "Retest", "CORR"),
        ("Retest-Task5.xml", "Retest", "TAG"),
        ("AutomaticRetest-Task1.xml", "AutomaticRetest", "MC"),
        ("AutomaticRetest-Task2.xml", "AutomaticRetest", "TICK REAL"),
        ("AutomaticRetest-Task3.xml", "AutomaticRetest", "Sequential"),
        ("AutomaticRetest-Task4.xml", "AutomaticRetest", "SPP"),
        ("AutomaticRetest-Task5.xml", "AutomaticRetest", "Synthetic"),
        ("AutomaticRetest-Task6.xml", "AutomaticRetest", "Monkey"),
        ("AutomaticRetest-Task7.xml", "AutomaticRetest", "WFM"),
        ("AutomaticRetest-Task8.xml", "AutomaticRetest", "MC2"),
    ]
    return names


def _write_project(projects_dir: Path, project_name: str, capa: int, *, bad_primary: bool = False) -> None:
    target = projects_dir / project_name / "project.cfx"
    target.parent.mkdir(parents=True, exist_ok=True)
    tasks = _task_plan(capa)
    config = [f'<Project name="{project_name}" version="141.2225"><Tasks>']
    for xml_file, task_type, title in tasks:
        config.append(f'<Task type="{task_type}" active="true" taskXMLFile="{xml_file}" title="{title}" />')
    config.append("</Tasks></Project>")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", "".join(config))
        for xml_file, _, _ in tasks:
            is_cross = (capa == 1 and xml_file == "Retest-Task1.xml") or (capa == 2 and xml_file == "AutomaticRetest-Task7.xml")
            if is_cross:
                archive.writestr(xml_file, _task_xml("AUDCAD_dukascopy", "2", "4"))
            elif bad_primary and capa == 2 and xml_file == "Build-Task1.xml":
                archive.writestr(xml_file, _task_xml("AUDCAD", "0", "-1"))
            else:
                archive.writestr(xml_file, _task_xml("AUDCAD_darwinex", "4", "4"))


def _fixture(root: Path, *, bad_primary: bool = False) -> Path:
    projects_dir = root / "host" / "user" / "projects"
    db_path = root / "host" / "user" / "data" / "data.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _write_catalog_db(db_path)
    _write_repo_config(root, projects_dir, db_path)
    _write_candidate(root)
    _write_project(projects_dir, f"{PROJECT_ROOT_STEM}_Capa1", 1)
    _write_project(projects_dir, f"{PROJECT_ROOT_STEM}_Capa2", 2, bad_primary=bad_primary)
    return root


def test_review_is_sanitized_readonly_and_passes_with_methodology_warning(tmp_path):
    root = _fixture(tmp_path)

    payload = review_payload(root, remote_base_url=None, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI12_IMPORTED_PROJECT_REVIEW_VERSION
    assert payload["ok"] is True
    assert payload["status"] == "imported_project_readonly_review_passed_with_methodology_warnings_no_start"
    assert payload["readOnlyReview"] is True
    assert payload["projectStartAllowed"] is False
    assert payload["runsSqxTasks"] is False
    assert payload["writesDataDb"] is False
    assert payload["writesUserProjects"] is False
    assert payload["mutatesDatabanks"] is False
    assert payload["privacy"]["rawXmlReturned"] is False
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "must_not_leak" not in blob
    assert payload["evidenceFile"].startswith("bsai12_imported_project_readonly_review_")


def test_review_identifies_capa1_official_and_capa2_candidate_trace(tmp_path):
    payload = review_payload(_fixture(tmp_path), remote_base_url=None)

    assert payload["candidate"]["baseCanonicalId"] == "BS_Filtros_v7_H1"
    assert payload["candidate"]["sourceVersionPolicy"] == "explicit_base_preserve_official_v6_v7"
    assert payload["summary"]["capa1ActiveBuildBlockSetting"] == "BS_Volatilidad_v6_intraday_v6"
    assert payload["summary"]["capa2ActiveBuildBlockSetting"] == CANDIDATE_ID
    assert payload["summary"]["allTaskCounts14"] is True
    assert payload["summary"]["targetFailCount"] == 0
    assert payload["summary"]["targetWarnCount"] == 2


def test_review_blocks_wrong_primary_resource_after_import(tmp_path):
    payload = review_payload(_fixture(tmp_path, bad_primary=True), remote_base_url=None)

    assert payload["ok"] is False
    assert payload["status"] == "imported_project_readonly_review_blocked_no_start"
    assert payload["summary"]["targetFailCount"] == 1
    assert any("target_resource_fail" in blocker for blocker in payload["blockers"])
