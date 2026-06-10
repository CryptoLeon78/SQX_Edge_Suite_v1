from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from core import sqx144_mt5_auto5_metadata_apply as auto5
from core import sqx144_mt5_bridge as bridge
from core import sqx144_mt5_auto3_broker_catalog as auto3


def _write_project(root: Path, db: Path) -> Path:
    tool_root = root / "backend" / "sqx-edge-tool"
    catalog_dir = tool_root / "config" / "mt5_broker_catalog"
    catalog_dir.mkdir(parents=True)
    (tool_root / "config.json").write_text(
        json.dumps({
            "sqx_host_profile": "sqx144_full",
            "sqx_data_db": str(db),
        }),
        encoding="utf-8",
    )
    (catalog_dir / "darwinex.json").write_text(
        json.dumps({
            "version": auto3.SQX144_MT5_AUTO3_VERSION,
            "brokerKey": "darwinex",
            "status": "active_current",
            "host": "sqx144_full",
            "spreadPolicy": "p90",
            "sqxBroker": {"expectedBrokerId": 4, "expectedSourceId": 4, "nameMatchers": ["Darwinex"], "postfix": "_darwinex"},
            "symbolMapping": {
                "mt5SymbolTemplate": "{asset}_Darwinex",
                "sqxInstrumentTemplate": "{asset}_darwinex",
                "sqxDataSymbolTemplate": "{asset}_darwinex",
            },
            "importRoutes": {
                "preferred": "native_datamanager_mt5_import",
                "preferredNativeEndpoint": "DataSourceMt5Api/importData",
                "fallback": "bridge_csv_file_mass_import",
                "directDbHistoryInsertAllowed": False,
            },
            "guards": {"readOnlyCatalogResolver": True, "allowImportExecution": False},
        }),
        encoding="utf-8",
    )
    return root


def _write_db(path: Path) -> Path:
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
        conn.execute(
            """
            INSERT INTO INSTRUMENTS (
              INSTRUMENT, BROKER_ID, DEFAULTSPREAD, POINTVALUE, TICKSIZE, TICKSTEP,
              DEFAULTSLIPPAGE, COMMISSIONS, SWAP
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "AUDCAD_darwinex",
                4,
                1.0,
                72157.360772,
                0.0001,
                0.00001,
                0.0,
                '<Method type="None" />',
                '<Swap use="false" />',
            ),
        )
        conn.execute(
            """
            INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, DATEFROM, DATETO, USYMBOL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("AUDCAD_darwinex", "AUDCAD_darwinex", "TICK", 4, 4, 340730947, 20170102, 20260526, "AUDCAD"),
        )
        conn.commit()
    finally:
        conn.close()
    return path


def _response(request_id: str = "sqx_auto2_AUDCAD_Darwinex_20260609_064421") -> dict:
    return {
        "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "requestId": request_id,
        "status": "ok",
        "symbol": "AUDCAD_Darwinex",
        "mt5Symbol": "AUDCAD",
        "properties": {
            "pointValue": 71753.512334,
            "tickSizeForSqx": 0.0001,
            "tickStepForSqx": 0.00001,
        },
        "spreadStats": {"samples": 300000, "p50": 0.7, "p75": 1.0, "p90": 1.3, "p95": 1.8, "p99": 4.2},
        "yearlySpreadStats": [{"year": 2024}, {"year": 2025}, {"year": 2026}],
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "placesOrders": False,
        "usesMigrationTool": False,
    }


def _write_response(files_dir: Path, payload: dict | None = None) -> Path:
    files_dir.mkdir(parents=True, exist_ok=True)
    base = payload or _response()
    for request_id in (
        "sqx_auto2_AUDCAD_Darwinex_20260608_044421",
        "sqx_auto2_AUDCAD_Darwinex_20260608_064421",
    ):
        historical = dict(base)
        historical["requestId"] = request_id
        (files_dir / f"SQXInfoBridge.response.{request_id}.json").write_text(json.dumps(historical), encoding="utf-8")
    path = files_dir / bridge.DEFAULT_RESPONSE_FILE
    path.write_text(json.dumps(base), encoding="utf-8")
    return path


def _row(db: Path) -> dict[str, object]:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        return dict(conn.execute("SELECT * FROM INSTRUMENTS WHERE INSTRUMENT='AUDCAD_darwinex'").fetchone())
    finally:
        conn.close()


def test_auto5_plan_consumes_bridge_response_and_is_read_only(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_response(files_dir)
    before = _row(db)

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        plan = auto5.build_plan(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert plan["version"] == auto5.SQX144_MT5_AUTO5_VERSION
    assert plan["ok"] is True
    assert plan["targetInstrument"] == "AUDCAD_darwinex"
    assert plan["decision" if "decision" in plan else "bridgeValidation"]
    assert plan["changes"]["DEFAULTSPREAD"] == {"old": 1.0, "new": 1.3}
    assert plan["changes"]["POINTVALUE"] == {"old": 72157.360772, "new": 71753.512334}
    assert "TICKSIZE" in plan["noops"]
    assert "TICKSTEP" in plan["noops"]
    assert plan["ignored"]["SOURCE"] == "preserve_sqx_source_authority"
    assert "response=" in plan["approvalTemplate"]
    assert "spreadPolicy=p90" in plan["approvalTemplate"]
    assert "fields=DEFAULTSPREAD,POINTVALUE" in plan["approvalTemplate"]
    assert "no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool" in plan["approvalTemplate"]
    assert _row(db) == before


def test_auto5_backup_apply_verify_and_rollback_are_gated(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_response(files_dir)
    before = _row(db)

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        backup = auto5.backup_payload(root, db_path=db, process_checker=lambda: [])
        plan = auto5.build_plan(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db, backup_id=backup["backupId"])
        blocked = auto5.apply_payload(
            root,
            broker_key="darwinex",
            symbol="AUDCAD_darwinex",
            db_path=db,
            backup_id=backup["backupId"],
            approval="wrong",
            apply=True,
            process_checker=lambda: [],
        )
        applied = auto5.apply_payload(
            root,
            broker_key="darwinex",
            symbol="AUDCAD_darwinex",
            db_path=db,
            backup_id=backup["backupId"],
            approval=plan["approvalTemplate"],
            apply=True,
            process_checker=lambda: [],
        )
        verify = auto5.verify_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)
        rollback = auto5.rollback_payload(root, backup_id=backup["backupId"], db_path=db, process_checker=lambda: [])

    assert backup["ok"] is True
    assert blocked["status"] == "apply_blocked_bad_approval"
    assert applied["status"] == "apply_completed_offline_instruments_only"
    assert applied["appliedColumns"] == ["DEFAULTSPREAD", "POINTVALUE"]
    assert verify["status"] == "verify_passed_all_approved_fields_match"
    assert _row(db) == before
    assert rollback["status"] == "rollback_restored_known_auto5_backup"


def test_auto5_blocks_apply_when_sqx_processes_present(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_response(files_dir)

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        try:
            auto5.apply_payload(
                root,
                broker_key="darwinex",
                symbol="AUDCAD_darwinex",
                db_path=db,
                backup_id="missing",
                approval="irrelevant",
                apply=True,
                process_checker=lambda: [{"processName": "StrategyQuantX", "pid": 10}],
            )
            raise AssertionError("expected Auto5Error")
        except auto5.Auto5Error as exc:
            assert exc.code == "sqx_processes_must_be_zero"
