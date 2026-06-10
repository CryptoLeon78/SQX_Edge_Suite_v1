from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path

from core.bsai_resource_compatibility import (
    BS_AI10_RESOURCE_COMPATIBILITY_VERSION,
    audit_target_resource_compatibility,
    load_target_catalog,
)


def _write_cfx(path: Path, files: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.xml", f'<Config name="{path.stem}" />')
        for name, text in files.items():
            archive.writestr(name, text)
    return path


def _task_xml(symbol: str, source: str, broker: str, instrument: str | None = None) -> str:
    instrument = instrument or symbol
    return f"""
    <Task>
      <Data>
        <Setups>
          <Setup session="No Session">
            <Chart symbol="{symbol}" timeframe="H1" />
          </Setup>
        </Setups>
      </Data>
      <BuildTradingOptions>
        <Params><Param key="MarketOpenSession">No Session</Param></Params>
      </BuildTradingOptions>
      <Resources>
        <Symbols>
          <Symbol name="{symbol}" source="{source}" precision="TICK" timezone="EETUS" broker="{broker}">
            <InstrumentInfo instrument="{instrument}" dataType="1" broker="{broker}" />
          </Symbol>
        </Symbols>
        <Brokers><Broker id="4" name="Darwinex" /></Brokers>
        <Sessions />
      </Resources>
    </Task>
    """


def _write_catalog_db(path: Path) -> Path:
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
                (4, "Darwinex", "_darwinex", "Darwinex CFDs"),
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
    return path


def test_target_catalog_uses_read_only_sanitized_summary(tmp_path):
    db = _write_catalog_db(tmp_path / "data.db")

    catalog = load_target_catalog(db, "AUDCAD")

    assert catalog["version"] == BS_AI10_RESOURCE_COMPATIBILITY_VERSION
    assert catalog["readMode"] == "sqlite_uri_mode_ro_query_only"
    assert catalog["exactSymbolPresent"] is False
    assert catalog["targetSymbolPresent"] is True
    assert catalog["crossBrokerSymbolPresent"] is True
    assert catalog["privacy"]["localPathsReturned"] is False


def test_exact_sq_default_symbol_is_blocked_for_sqx144_full_catalog(tmp_path):
    db = _write_catalog_db(tmp_path / "data.db")
    cfx = _write_cfx(
        tmp_path / "BSAI_AUDCAD_H1_SAMPLE_L_Capa1.cfx",
        {"Build-Task1.xml": _task_xml("AUDCAD", "0", "-1")},
    )

    report = audit_target_resource_compatibility([cfx], db, asset="AUDCAD")
    codes = {issue["code"] for issue in report["targetIssues"]}

    assert report["targetResourceVerdict"] == "fail"
    assert report["gateStatus"] == "blocked_target_resource_mismatch"
    assert report["recommendation"] == "regenerate_with_target_profile_sqxedge_darwinex"
    assert "primary_resource_mismatch_for_sqx144_full" in codes
    assert "AUDCAD_darwinex" in report["targetIssues"][0]["detail"]


def test_remapped_darwinex_pair_passes_with_governed_cross_broker_warning(tmp_path):
    db = _write_catalog_db(tmp_path / "data.db")
    capa1 = _write_cfx(
        tmp_path / "BSAI_AUDCAD_H1_SAMPLE_L_SQX144DARWINEX_Capa1.cfx",
        {
            "Build-Task1.xml": _task_xml("AUDCAD_darwinex", "4", "4"),
            "Retest-Task1.xml": _task_xml("AUDCAD_dukascopy", "2", "4", "AUDCAD_darwinex"),
        },
    )
    capa2 = _write_cfx(
        tmp_path / "BSAI_AUDCAD_H1_SAMPLE_L_SQX144DARWINEX_Capa2.cfx",
        {
            "Build-Task1.xml": _task_xml("AUDCAD_darwinex", "4", "4"),
            "AutomaticRetest-Task7.xml": _task_xml("AUDCAD_dukascopy", "2", "4", "AUDCAD_darwinex"),
        },
    )

    report = audit_target_resource_compatibility([capa1, capa2], db, asset="AUDCAD")
    codes = {issue["code"] for issue in report["targetIssues"]}
    public_blob = json.dumps(report, ensure_ascii=False)

    assert report["targetResourceVerdict"] == "warn"
    assert report["targetFailCount"] == 0
    assert report["gateStatus"] == "ready_for_manual_import_gate_with_methodology_warnings"
    assert codes == {"methodology_cross_broker_catalog_match"}
    assert str(tmp_path) not in public_blob
    assert "<Task>" not in public_blob
    assert report["privacy"]["localPathsReturned"] is False
