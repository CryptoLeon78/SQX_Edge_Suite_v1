from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from api import server
from core import sqx144_mt5_auto7_dukascopy_metadata_mirror as auto7


def _write_project(root: Path, db: Path) -> Path:
    tool_root = root / "backend" / "sqx-edge-tool"
    tool_root.mkdir(parents=True)
    (tool_root / "config.json").write_text(
        json.dumps({
            "sqx_host_profile": "sqx144_full",
            "sqx_data_db": str(db),
        }),
        encoding="utf-8",
    )
    return root


def _insert_instrument(
    conn: sqlite3.Connection,
    instrument: str,
    *,
    broker_id: int,
    spread: float,
    point_value: float,
    tick_size: float,
    tick_step: float,
    slippage: float = 0.0,
    multiplier: float = 1.0,
    order_step: float = 0.01,
    commissions: str = '<Method type="SizeBased" value="5" />',
    swap: str = '<Swap use="true" long="-9" short="3" />',
) -> None:
    conn.execute(
        """
        INSERT INTO INSTRUMENTS (
          INSTRUMENT, BROKER_ID, DEFAULTSPREAD, POINTVALUE, TICKSIZE, TICKSTEP,
          DEFAULTSLIPPAGE, ORDERSIZEMULTIPLIER, ORDERSIZESTEP, COMMISSIONS, SWAP
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (instrument, broker_id, spread, point_value, tick_size, tick_step, slippage, multiplier, order_step, commissions, swap),
    )


def _write_db(path: Path, *, missing_source: bool = False, missing_target: bool = False) -> Path:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE BROKER (ID INTEGER, NAME TEXT, POSTFIX TEXT, DESC TEXT);
            CREATE TABLE INSTRUMENTS (
              INSTRUMENT TEXT,
              BROKER_ID INTEGER,
              DEFAULTSPREAD REAL,
              POINTVALUE REAL,
              TICKSIZE REAL,
              TICKSTEP REAL,
              DEFAULTSLIPPAGE REAL,
              ORDERSIZEMULTIPLIER REAL,
              ORDERSIZESTEP REAL,
              COMMISSIONS TEXT,
              SWAP TEXT
            );
            CREATE TABLE DATA (
              SYMBOL TEXT,
              INSTRUMENT TEXT,
              TIMEFRAME TEXT,
              SOURCE INTEGER,
              BROKER_ID INTEGER,
              ROWS INTEGER,
              DATEFROM INTEGER,
              DATETO INTEGER,
              USYMBOL TEXT
            );
            """
        )
        conn.execute("INSERT INTO BROKER (ID, NAME, POSTFIX, DESC) VALUES (4, 'Darwinex', '_darwinex', 'Darwinex')")
        conn.execute("INSERT INTO BROKER (ID, NAME, POSTFIX, DESC) VALUES (3, 'Dukascopy', '_dukascopy', 'Dukascopy')")
        if not missing_source:
            _insert_instrument(
                conn,
                "EURGBP_darwinex",
                broker_id=4,
                spread=0.5,
                point_value=129882.0,
                tick_size=0.0001,
                tick_step=0.00001,
            )
        if not missing_target:
            _insert_instrument(
                conn,
                "EURGBP_dukascopy",
                broker_id=3,
                spread=0.7,
                point_value=129994.0,
                tick_size=0.0001,
                tick_step=0.00001,
                commissions='<Method type="None" />',
                swap='<Swap use="false" />',
            )
        conn.execute(
            """
            INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, DATEFROM, DATETO, USYMBOL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("EURGBP_dukascopy", "EURGBP_darwinex", "TICK", 2, 4, 356085471, 1262311200452, 1780369176946, "EURGBP"),
        )
        conn.commit()
    finally:
        conn.close()
    return path


def _row(db: Path, instrument: str) -> dict[str, object]:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        return dict(conn.execute("SELECT * FROM INSTRUMENTS WHERE INSTRUMENT=?", (instrument,)).fetchone())
    finally:
        conn.close()


def _db_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_auto7_plan_mirrors_dukascopy_from_darwinex_without_mt5(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    before = _db_hash(db)

    plan = auto7.plan_payload(root, symbol="EURGBP_dukascopy", db_path=db)

    assert plan["version"] == auto7.SQX144_MT5_AUTO7_VERSION
    assert plan["readMode"] == "sqlite_uri_mode_ro_query_only"
    assert plan["consumesMt5BridgeResponse"] is False
    assert plan["writesMt5Files"] is False
    assert plan["sourceInstrument"] == "EURGBP_darwinex"
    assert plan["targetInstrument"] == "EURGBP_dukascopy"
    assert plan["changes"]["DEFAULTSPREAD"] == {"old": 0.7, "new": 0.5}
    assert plan["changes"]["POINTVALUE"] == {"old": 129994.0, "new": 129882.0}
    assert plan["changes"]["COMMISSIONS"]["new"] == '<Method type="SizeBased" value="5" />'
    assert plan["changes"]["SWAP"]["new"] == '<Swap use="true" long="-9" short="3" />'
    assert plan["invariants"]["targetBrokerId"] == 3
    assert plan["preserved"]["DATA"] == "preserve_sqx_history_catalog"
    assert "no_mt5 no_migration_tool" in plan["approvalTemplate"]
    assert _db_hash(db) == before


def test_auto7_data_symbol_linked_to_darwinex_instrument_is_noop(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    conn = sqlite3.connect(db)
    try:
        _insert_instrument(
            conn,
            "GDAXI_darwinex",
            broker_id=4,
            spread=14.0,
            point_value=11.66292,
            tick_size=0.1,
            tick_step=0.1,
            commissions='<Method type="None" />',
            swap='<Swap use="true" long="-26.62" short="9.55" />',
        )
        conn.execute(
            """
            INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, DATEFROM, DATETO, USYMBOL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("DAX40_dukascopy", "GDAXI_darwinex", "M1", 2, 4, 3750631, 1380492000000, 1780369176946, "DEUIDXEUR"),
        )
        conn.commit()
    finally:
        conn.close()
    before = _db_hash(db)

    plan = auto7.plan_payload(
        root,
        symbol="DAX40_dukascopy",
        linked_instrument="GDAXI_Darwinex",
        db_path=db,
    )

    assert plan["ok"] is True
    assert plan["status"] == "plan_ready_noop_data_symbol_uses_darwinex_instrument"
    assert plan["dataSymbol"] == "DAX40_dukascopy"
    assert plan["linkedInstrument"] == "GDAXI_darwinex"
    assert plan["sourceInstrument"] == "GDAXI_darwinex"
    assert plan["targetInstrument"] == "GDAXI_darwinex"
    assert plan["dataSymbolUsesDarwinexInstrument"] is True
    assert plan["futureApplyRequired"] is False
    assert plan["changes"] == {}
    assert plan["noops"]["DEFAULTSPREAD"] == 14.0
    assert plan["noops"]["POINTVALUE"] == 11.66292
    assert plan["approvalTemplate"] == ""
    assert plan["blockers"] == []
    assert "dukascopy_data_symbol_already_uses_darwinex_instrument" in plan["warnings"]
    assert _db_hash(db) == before


def test_auto7_blocks_non_dukascopy_and_missing_siblings(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)

    try:
        auto7.plan_payload(root, symbol="EURGBP_darwinex", db_path=db)
        raise AssertionError("expected Auto7Error")
    except auto7.Auto7Error as exc:
        assert exc.code == "dukascopy_symbol_required"

    missing_source_db = _write_db(tmp_path / "missing_source.db", missing_source=True)
    root_missing_source = _write_project(tmp_path / "repo-missing-source", missing_source_db)
    missing_source = auto7.plan_payload(root_missing_source, symbol="EURGBP_dukascopy", db_path=missing_source_db)
    assert "darwinex_sibling_missing" in missing_source["blockers"]

    missing_target_db = _write_db(tmp_path / "missing_target.db", missing_target=True)
    root_missing_target = _write_project(tmp_path / "repo-missing-target", missing_target_db)
    missing_target = auto7.plan_payload(root_missing_target, symbol="EURGBP_dukascopy", db_path=missing_target_db)
    assert "dukascopy_target_missing" in missing_target["blockers"]


def test_auto7_backup_apply_verify_and_rollback_are_gated(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    before = _row(db, "EURGBP_dukascopy")

    backup = auto7.backup_payload(root, db_path=db, process_checker=lambda: [])
    plan = auto7.plan_payload(root, symbol="EURGBP_dukascopy", db_path=db, backup_id=backup["backupId"])
    blocked = auto7.apply_payload(
        root,
        symbol="EURGBP_dukascopy",
        db_path=db,
        backup_id=backup["backupId"],
        approval="wrong",
        apply=True,
        process_checker=lambda: [],
    )
    applied = auto7.apply_payload(
        root,
        symbol="EURGBP_dukascopy",
        db_path=db,
        backup_id=backup["backupId"],
        approval=plan["approvalTemplate"],
        apply=True,
        process_checker=lambda: [],
    )
    mirrored = _row(db, "EURGBP_dukascopy")
    verify = auto7.verify_payload(root, symbol="EURGBP_dukascopy", db_path=db)
    rollback = auto7.rollback_payload(root, backup_id=backup["backupId"], db_path=db, process_checker=lambda: [])

    assert backup["status"] == "backup_ready_apply_still_requires_exact_approval"
    assert blocked["status"] == "apply_blocked_bad_approval"
    assert applied["status"] == "apply_completed_offline_dukascopy_instrument_mirror_only"
    assert applied["appliedColumns"] == ["COMMISSIONS", "DEFAULTSPREAD", "POINTVALUE", "SWAP"]
    assert mirrored["BROKER_ID"] == 3
    assert mirrored["DEFAULTSPREAD"] == 0.5
    assert mirrored["POINTVALUE"] == 129882.0
    assert verify["status"] == "verify_passed_dukascopy_matches_darwinex_sibling"
    assert rollback["status"] == "rollback_restored_known_auto7_backup"
    assert _row(db, "EURGBP_dukascopy") == before


def test_auto7_blocks_apply_when_sqx_processes_present(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)

    try:
        auto7.apply_payload(
            root,
            symbol="EURGBP_dukascopy",
            db_path=db,
            backup_id="missing",
            approval="irrelevant",
            apply=True,
            process_checker=lambda: [{"processName": "StrategyQuantX", "pid": 10}],
        )
        raise AssertionError("expected Auto7Error")
    except auto7.Auto7Error as exc:
        assert exc.code == "sqx_processes_must_be_zero"


def test_flask_auto7_plan_endpoint_is_plan_only(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    client = server.app.test_client()

    with patch.object(server, "PROJECT_ROOT", root):
        response = client.post("/api/sqx144/mt5-auto7/plan", json={"symbol": "EURGBP_dukascopy"})

    assert response.status_code == 200
    data = json.loads(response.data.decode("utf-8"))
    assert data["version"] == auto7.SQX144_MT5_AUTO7_VERSION
    assert data["mirrorPolicy"] == "dukascopy_copies_darwinex_sibling_metadata"
    assert data["consumesMt5BridgeResponse"] is False
    assert data["writesDataDb"] is False
    assert data["runsSqxTasks"] is False


def test_flask_auto7_plan_endpoint_accepts_linked_darwinex_instrument(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    conn = sqlite3.connect(db)
    try:
        _insert_instrument(conn, "GDAXI_darwinex", broker_id=4, spread=14.0, point_value=11.66292, tick_size=0.1, tick_step=0.1)
        conn.execute(
            """
            INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, DATEFROM, DATETO, USYMBOL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("DAX40_dukascopy", "GDAXI_darwinex", "M1", 2, 4, 3750631, 1380492000000, 1780369176946, "DEUIDXEUR"),
        )
        conn.commit()
    finally:
        conn.close()
    client = server.app.test_client()

    with patch.object(server, "PROJECT_ROOT", root):
        response = client.post(
            "/api/sqx144/mt5-auto7/plan",
            json={"symbol": "DAX40_dukascopy", "linkedInstrument": "GDAXI_Darwinex"},
        )

    assert response.status_code == 200
    data = json.loads(response.data.decode("utf-8"))
    assert data["status"] == "plan_ready_noop_data_symbol_uses_darwinex_instrument"
    assert data["dataSymbol"] == "DAX40_dukascopy"
    assert data["linkedInstrument"] == "GDAXI_darwinex"
    assert data["changes"] == {}
