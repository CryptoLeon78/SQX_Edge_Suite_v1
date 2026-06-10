from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from api import server
from core import sqx144_mt5_auto3_broker_catalog as auto3
from core import sqx144_mt5_bridge as bridge


DARWINEX_PROFILE = {
    "version": auto3.SQX144_MT5_AUTO3_VERSION,
    "brokerKey": "darwinex",
    "status": "active_current",
    "host": "sqx144_full",
    "spreadPolicy": "p90",
    "sqxBroker": {
        "expectedBrokerId": 4,
        "expectedSourceId": 4,
        "nameMatchers": ["Darwinex", "[[Darwinex]]"],
        "postfix": "_darwinex",
        "allowBrokerCreate": False,
    },
    "symbolMapping": {
        "assetCase": "upper",
        "mt5SymbolTemplate": "{asset}_Darwinex",
        "sqxInstrumentTemplate": "{asset}_darwinex",
        "sqxDataSymbolTemplate": "{asset}_darwinex",
        "selectedSymbolAliases": ["{asset}_Darwinex", "{asset}_darwinex"],
    },
    "importRoutes": {
        "preferred": "native_datamanager_mt5_import",
        "preferredNativeEndpoint": "dataSourceMt5Api/importData",
        "fallback": "bridge_csv_file_mass_import",
        "directDbHistoryInsertAllowed": False,
    },
    "guards": {
        "readOnlyCatalogResolver": True,
        "allowInstrumentCreatePlan": True,
        "allowHistoryImportPlan": True,
        "allowImportExecution": False,
        "requiresExactApprovalForMutation": True,
    },
}

AXI_PROFILE = {
    "version": auto3.SQX144_MT5_AUTO3_VERSION,
    "brokerKey": "axi",
    "status": "planned_discovery_required",
    "host": "sqx144_full",
    "spreadPolicy": "p90",
    "sqxBroker": {
        "expectedBrokerId": None,
        "expectedSourceId": None,
        "nameMatchers": ["Axi", "AxiTrader"],
        "postfix": None,
        "allowBrokerCreate": False,
    },
    "symbolMapping": {
        "assetCase": "upper",
        "mt5SymbolTemplate": None,
        "sqxInstrumentTemplate": None,
        "sqxDataSymbolTemplate": None,
        "selectedSymbolAliases": [],
    },
    "importRoutes": {
        "preferred": "native_datamanager_mt5_import",
        "preferredNativeEndpoint": "dataSourceMt5Api/importData",
        "fallback": "bridge_csv_file_mass_import",
        "directDbHistoryInsertAllowed": False,
    },
    "guards": {
        "readOnlyCatalogResolver": True,
        "requiresDiscovery": True,
        "allowInstrumentCreatePlan": False,
        "allowHistoryImportPlan": False,
        "allowImportExecution": False,
        "requiresExactApprovalForMutation": True,
    },
}


def _write_project(root: Path, db: Path) -> Path:
    tool_root = root / "backend" / "sqx-edge-tool"
    catalog_dir = tool_root / "config" / "mt5_broker_catalog"
    catalog_dir.mkdir(parents=True)
    (tool_root / "config.json").write_text(
        json.dumps({
            "sqx_host_profile": "sqx144_full",
            "sqx_data_db": str(db),
            "asset_aliases": {
                "USTEC": "NDX_darwinex",
                "GER40": "GDAXI_darwinex",
            },
        }),
        encoding="utf-8",
    )
    (catalog_dir / "darwinex.json").write_text(json.dumps(DARWINEX_PROFILE), encoding="utf-8")
    (catalog_dir / "axi.planned.json").write_text(json.dumps(AXI_PROFILE), encoding="utf-8")
    return root


def _insert_instrument(conn: sqlite3.Connection, instrument: str, *, broker_id: int = 4, spread: float = 1.0, point_value: float = 1.0) -> None:
    conn.execute(
        """
        INSERT INTO INSTRUMENTS (
          INSTRUMENT, BROKER_ID, DEFAULTSPREAD, POINTVALUE, TICKSIZE, TICKSTEP,
          DEFAULTSLIPPAGE, ORDERSIZEMULTIPLIER, ORDERSIZESTEP
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (instrument, broker_id, spread, point_value, 0.01, 0.001, 0.0, 1.0, 0.01),
    )


def _insert_data(conn: sqlite3.Connection, symbol: str, *, rows: int, instrument: str | None = None, broker_id: int = 4, source: int = 4) -> None:
    conn.execute(
        """
        INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, DATEFROM, DATETO, USYMBOL)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (symbol, instrument or symbol, "TICK", source, broker_id, rows, 20170102, 20260526, symbol.split("_", 1)[0]),
    )


def _write_db(path: Path, *, duplicate_case: bool = False) -> Path:
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
              ORDERSIZESTEP REAL
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
        conn.execute("INSERT INTO BROKER (ID, NAME, POSTFIX, DESC) VALUES (12, 'Darwinex Legacy', 'darwinex', 'legacy')")
        _insert_instrument(conn, "AUDCAD_darwinex", spread=1.0, point_value=10.0)
        _insert_instrument(conn, "USDJPY_darwinex", spread=1.0, point_value=627.0)
        _insert_instrument(conn, "GBPUSD_darwinex", spread=0.8, point_value=10.0)
        _insert_instrument(conn, "NDX_darwinex", spread=2.0, point_value=1.0)
        _insert_data(conn, "AUDCAD_darwinex", rows=340730947, instrument="AUDCAD_darwinex")
        _insert_data(conn, "USDJPY_darwinex", rows=8375601, instrument="USDJPY_darwinex")
        _insert_data(conn, "GBPUSD_darwinex", rows=0, instrument="GBPUSD_darwinex")
        _insert_data(conn, "NDX_darwinex", rows=617123454, instrument="NDX_darwinex")
        if duplicate_case:
            _insert_instrument(conn, "EURUSD_darwinex", spread=0.6, point_value=10.0)
            _insert_instrument(conn, "eurusd_darwinex", spread=0.6, point_value=10.0)
            _insert_data(conn, "EURUSD_darwinex", rows=10, instrument="EURUSD_darwinex")
        conn.commit()
    finally:
        conn.close()
    return path


def _counts(db: Path) -> tuple[int, int, int]:
    conn = sqlite3.connect(db)
    try:
        broker = conn.execute("SELECT COUNT(*) FROM BROKER").fetchone()[0]
        instruments = conn.execute("SELECT COUNT(*) FROM INSTRUMENTS").fetchone()[0]
        data = conn.execute("SELECT COUNT(*) FROM DATA").fetchone()[0]
        return broker, instruments, data
    finally:
        conn.close()


def _valid_response(request_id: str = "req_1", symbol: str = "USDJPY_Darwinex") -> dict:
    return {
        "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "requestId": request_id,
        "status": "ok",
        "symbol": symbol,
        "mt5Symbol": "USDJPY",
        "properties": {"pointValue": 624.30546, "tickSizeForSqx": 0.01, "tickStepForSqx": 0.001},
        "spreadStats": {"samples": 768790, "p50": 0.4, "p75": 0.6, "p90": 0.7, "p95": 1.2, "p99": 6.5},
        "yearlySpreadStats": [{"year": 2024}, {"year": 2025}, {"year": 2026}],
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "placesOrders": False,
        "usesMigrationTool": False,
    }


def test_catalog_audit_darwinex_existing_audcad_is_read_only(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    before = _counts(db)

    audit = auto3.catalog_audit_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert audit["version"] == auto3.SQX144_MT5_AUTO3_VERSION
    assert audit["readMode"] == "sqlite_uri_mode_ro_query_only"
    assert audit["decision"] == "ready_existing"
    assert audit["brokerProfile"]["expectedBrokerId"] == 4
    assert audit["instrumentRows"][0]["brokerId"] == 4
    assert audit["dataRows"][0]["source"] == 4
    assert audit["historyFound"] is True
    assert audit["writesDataDb"] is False
    assert audit["mutatesDatabanks"] is False
    assert _counts(db) == before


def test_alias_symbol_resolves_to_existing_darwinex_catalog(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)

    plan = auto3.resolve_plan_payload(root, broker_key="darwinex", symbol="USTEC", db_path=db)

    assert plan["decision"] == "ready_existing"
    assert plan["symbolResolution"]["aliasUsed"] is True
    assert plan["symbolResolution"]["targetInstrument"] == "NDX_darwinex"


def test_bridge_validate_usdjpy_uses_p90_and_reports_metadata_diff_only(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    files_dir.mkdir()
    (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(json.dumps(_valid_response("req_ok")), encoding="utf-8")

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        payload = auto3.bridge_validate_payload(root, broker_key="darwinex", symbol="USDJPY_darwinex", spread_policy="p90", db_path=db)

    assert payload["ok"] is True
    assert payload["decision"] == "metadata_diff_only"
    assert payload["proposedSqxFields"]["DEFAULTSPREAD"] == 0.7
    assert payload["metadataDiff"]["DEFAULTSPREAD"] == {"old": 1.0, "new": 0.7}
    assert payload["doesNotApplyToSqx"] is True
    assert payload["importExecutionAllowed"] is False


def test_bridge_validate_waits_for_request_id_before_symbol_mismatch(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    files_dir.mkdir()
    (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(json.dumps(_valid_response("old_req", symbol="USDJPY_Darwinex")), encoding="utf-8")

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        payload = auto3.bridge_validate_payload(
            root,
            broker_key="darwinex",
            symbol="AUDCAD_darwinex",
            spread_policy="p90",
            expected_request_id="new_req",
            db_path=db,
        )

    assert payload["ok"] is False
    assert payload["status"] == "waiting_for_requested_response"
    assert "latest_response_request_id_mismatch" in payload["warnings"]
    assert "latest_response_symbol_mismatch" not in payload["blockers"]


def test_axi_returns_broker_missing_without_inventing_ids(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)

    plan = auto3.resolve_plan_payload(root, broker_key="axi", symbol="EURUSD", db_path=db)

    assert plan["decision"] == "broker_missing"
    assert plan["brokerProfile"]["expectedBrokerId"] is None
    assert plan["brokerProfile"]["expectedSourceId"] is None
    assert plan["brokerProfile"]["requiresDiscovery"] is True
    assert "broker_missing_discovery_required" in plan["blockers"]


def test_history_missing_import_plan_is_blocked_until_future_gate(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)

    plan = auto3.resolve_plan_payload(root, broker_key="darwinex", symbol="GBPUSD_darwinex", db_path=db)
    import_plan = auto3.import_plan_payload(root, broker_key="darwinex", symbol="GBPUSD_darwinex", timeframe="M1", db_path=db)

    assert plan["decision"] == "history_missing"
    assert import_plan["decision"] == "history_missing"
    assert import_plan["importNeeded"] is True
    assert import_plan["importBlocked"] is True
    assert import_plan["importExecutionAllowed"] is False
    assert import_plan["preferredNativeEndpoint"] == "dataSourceMt5Api/importData"
    assert import_plan["directDbHistoryInsertAllowed"] is False
    assert "future_exact_import_gate_required" in import_plan["blockers"]


def test_duplicate_case_collision_blocks(tmp_path):
    db = _write_db(tmp_path / "data.db", duplicate_case=True)
    root = _write_project(tmp_path / "repo", db)

    plan = auto3.resolve_plan_payload(root, broker_key="darwinex", symbol="EURUSD_darwinex", db_path=db)

    assert plan["decision"] == "ambiguous_collision"
    assert "ambiguous_collision_manual_review_required" in plan["blockers"]


def test_flask_auto3_catalog_audit_endpoint_is_plan_only(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    client = server.app.test_client()

    with patch.object(server, "PROJECT_ROOT", root):
        response = client.post("/api/sqx144/mt5-auto3/catalog-audit", json={"broker": "darwinex", "symbol": "AUDCAD_darwinex"})

    assert response.status_code == 200
    data = json.loads(response.data.decode("utf-8"))
    assert data["version"] == auto3.SQX144_MT5_AUTO3_VERSION
    assert data["decision"] == "ready_existing"
    assert data["writesDataDb"] is False
    assert data["runsSqxTasks"] is False
