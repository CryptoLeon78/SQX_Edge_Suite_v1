from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

from api import server
from core import sqx144_mt5_auto3_broker_catalog as auto3
from core import sqx144_mt5_auto6_metadata_stability as auto6
from core import sqx144_mt5_bridge as bridge


def _write_project(root: Path, db: Path, *, ghost_profile: bool = False) -> Path:
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
    profile = {
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
        "importRoutes": {"directDbHistoryInsertAllowed": False},
        "guards": {"readOnlyCatalogResolver": True, "allowImportExecution": False},
    }
    (catalog_dir / "darwinex.json").write_text(json.dumps(profile), encoding="utf-8")
    if ghost_profile:
        ghost = dict(profile)
        ghost["brokerKey"] = "ghost"
        ghost["sqxBroker"] = {"expectedBrokerId": 99, "expectedSourceId": 99, "nameMatchers": ["Ghost"], "postfix": "_ghost"}
        (catalog_dir / "ghost.json").write_text(json.dumps(ghost), encoding="utf-8")
    return root


def _write_db(
    path: Path,
    *,
    default_spread: float = 1.3,
    point_value: float = 71753.512334,
    duplicate_instrument: bool = False,
    positive_history: bool = True,
) -> Path:
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
        rows = [("AUDCAD_darwinex", 4, default_spread, point_value, 0.0001, 0.00001, 0.0, "", "")]
        if duplicate_instrument:
            rows.append(("audcad_darwinex", 4, default_spread, point_value, 0.0001, 0.00001, 0.0, "", ""))
        conn.executemany(
            """
            INSERT INTO INSTRUMENTS (
              INSTRUMENT, BROKER_ID, DEFAULTSPREAD, POINTVALUE, TICKSIZE, TICKSTEP,
              DEFAULTSLIPPAGE, COMMISSIONS, SWAP
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.execute(
            """
            INSERT INTO DATA (SYMBOL, INSTRUMENT, TIMEFRAME, SOURCE, BROKER_ID, ROWS, DATEFROM, DATETO, USYMBOL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("AUDCAD_darwinex", "AUDCAD_darwinex", "TICK", 4, 4, 340730947 if positive_history else 0, 20170102, 20260526, "AUDCAD"),
        )
        conn.commit()
    finally:
        conn.close()
    return path


def _response(
    request_id: str,
    *,
    spread: float = 1.2,
    point_value: float = 71659.930633,
    samples: int = 531264,
    years: tuple[int, ...] = (2025, 2026),
    unsafe_flag: bool = False,
) -> dict:
    return {
        "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "requestId": request_id,
        "status": "ok",
        "symbol": "AUDCAD_Darwinex",
        "mt5Symbol": "AUDCAD",
        "properties": {
            "pointValue": point_value,
            "tickSizeForSqx": 0.0001,
            "tickStepForSqx": 0.00001,
        },
        "spreadStats": {"samples": samples, "p50": 0.8, "p75": 1.0, "p90": spread, "p95": spread + 0.4, "p99": spread + 2.0},
        "yearlySpreadStats": [{"year": year} for year in years],
        "writesSqxHost": False,
        "writesDataDb": bool(unsafe_flag),
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "placesOrders": False,
        "usesMigrationTool": False,
    }


def _write_responses(files_dir: Path, responses: list[dict]) -> None:
    files_dir.mkdir(parents=True, exist_ok=True)
    for response in responses[:-1]:
        request_id = response["requestId"]
        (files_dir / f"SQXInfoBridge.response.{request_id}.json").write_text(json.dumps(response), encoding="utf-8")
    (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(json.dumps(responses[-1]), encoding="utf-8")


def _db_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row_count(path: Path) -> int:
    conn = sqlite3.connect(path)
    try:
        return int(conn.execute("SELECT COUNT(*) FROM INSTRUMENTS").fetchone()[0])
    finally:
        conn.close()


def test_auto6_status_is_read_only_and_has_no_mutation_actions(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        status = auto6.status_payload(root)

    assert status["version"] == auto6.SQX144_MT5_AUTO6_VERSION
    assert status["policyId"] == auto6.POLICY_ID
    assert status["ok"] is True
    assert status["readOnlyPolicyGate"] is True
    assert status["applyAllowed"] is False
    assert status["writesDataDb"] is False
    assert status["runsSqxTasks"] is False


def test_auto6_no_diff_returns_stable_no_change(tmp_path):
    db = _write_db(tmp_path / "data.db", default_spread=1.2, point_value=71659.930633)
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert report["status"] == "stable_no_change"
    assert report["decision"] == "stable_no_change"
    assert report["futureApplyGateAllowed"] is False


def test_auto6_audcad_post_visual_single_drift_returns_policy_wait_no_apply(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert report["status"] == "stability_policy_not_satisfied"
    assert report["decision"] == auto6.OBSERVE_DECISION
    assert report["futureApplyGateAllowed"] is False
    assert report["changes"]["DEFAULTSPREAD"] == {"old": 1.3, "new": 1.2}
    assert "spread_delta_inside_hysteresis" in report["policyReasons"]
    assert "pointvalue_delta_below_threshold" in report["policyReasons"]


def test_auto6_repeated_same_direction_drift_becomes_future_auto5_candidate_only(tmp_path):
    db = _write_db(tmp_path / "data.db", default_spread=1.0, point_value=72157.360772)
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    responses = [
        _response("sqx_auto2_AUDCAD_Darwinex_20260608_044421", spread=1.3, point_value=71753.512334, samples=300000, years=(2024, 2025, 2026)),
        _response("sqx_auto2_AUDCAD_Darwinex_20260608_064421", spread=1.3, point_value=71753.512334, samples=300000, years=(2024, 2025, 2026)),
        _response("sqx_auto2_AUDCAD_Darwinex_20260609_064421", spread=1.3, point_value=71753.512334, samples=300000, years=(2024, 2025, 2026)),
    ]
    _write_responses(files_dir, responses)

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert report["status"] == "stable_drift_candidate_for_future_auto5"
    assert report["decision"] == auto6.ELIGIBLE_DECISION
    assert report["futureApplyGateAllowed"] is True
    assert report["observationSet"]["matchingObservationCount"] == 3
    assert report["observationSet"]["matchingObservationWindowHours"] >= 24


def test_auto6_low_samples_and_low_years_hold_policy(tmp_path):
    db = _write_db(tmp_path / "data.db", default_spread=1.0, point_value=72157.360772)
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542", spread=1.3, point_value=71753.512334, samples=999, years=(2026,))])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert report["decision"] == auto6.OBSERVE_DECISION
    assert "stability_insufficient_samples" in report["policyReasons"]
    assert "stability_insufficient_years" in report["policyReasons"]


def test_auto6_blocks_broker_missing_and_ambiguous_collision(tmp_path):
    db_missing = _write_db(tmp_path / "missing.db")
    root_missing = _write_project(tmp_path / "repo-missing", db_missing, ghost_profile=True)
    files_missing = tmp_path / "mt5-missing"
    _write_responses(files_missing, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])
    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_missing):
        missing = auto6.evaluate_payload(root_missing, broker_key="ghost", symbol="AUDCAD_darwinex", db_path=db_missing)

    db_collision = _write_db(tmp_path / "collision.db", duplicate_instrument=True)
    root_collision = _write_project(tmp_path / "repo-collision", db_collision)
    files_collision = tmp_path / "mt5-collision"
    _write_responses(files_collision, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])
    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_collision):
        collision = auto6.evaluate_payload(root_collision, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db_collision)

    assert missing["status"] == "blocked_catalog_not_ready"
    assert "broker_missing" in "".join(missing["blockers"])
    assert collision["status"] == "blocked_catalog_not_ready"
    assert "ambiguous_collision" in "".join(collision["blockers"])


def test_auto6_waits_for_expected_request_id_without_symbol_mismatch(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(
            root,
            broker_key="darwinex",
            symbol="AUDCAD_darwinex",
            expected_request_id="sqx_auto2_AUDCAD_Darwinex_20260609_150000",
            db_path=db,
        )

    assert report["status"] == "blocked_bridge_not_ready"
    assert "bridge_validation_not_ready" in report["blockers"]


def test_auto6_blocks_unsafe_bridge_flags(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542", unsafe_flag=True)])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert report["status"] == "blocked_bridge_not_ready"
    assert "bridge_validation_not_ready" in report["blockers"]


def test_auto6_does_not_change_db_hash_or_row_counts(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])
    before_hash = _db_hash(db)
    before_count = _row_count(db)

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)

    assert _db_hash(db) == before_hash
    assert _row_count(db) == before_count


def test_auto6_sanitizes_paths_raw_response_and_apply_approval(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])

    with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
        report = auto6.evaluate_payload(root, broker_key="darwinex", symbol="AUDCAD_darwinex", db_path=db)
        template = auto6.decision_template_payload(root)

    raw = json.dumps({"report": report, "template": template}, sort_keys=True)
    assert str(tmp_path) not in raw
    assert '"properties"' not in raw
    assert "APRUEBO SQX144 MT5 AUTO5 METADATA APPLY" not in raw
    assert report["privacy"]["localPathsReturned"] is False
    assert report["privacy"]["applyApprovalReturned"] is False


def test_flask_auto6_evaluate_endpoint_is_read_only_policy_only(tmp_path):
    db = _write_db(tmp_path / "data.db")
    root = _write_project(tmp_path / "repo", db)
    files_dir = tmp_path / "mt5-files"
    _write_responses(files_dir, [_response("sqx_auto2_AUDCAD_Darwinex_20260609_144542")])
    client = server.app.test_client()

    with patch.object(server, "PROJECT_ROOT", root), patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
      response = client.post("/api/sqx144/mt5-auto6/evaluate", json={
          "broker": "darwinex",
          "symbol": "AUDCAD_darwinex",
          "spreadPolicy": "p90",
          "expectedRequestId": "sqx_auto2_AUDCAD_Darwinex_20260609_144542",
      })

    assert response.status_code == 200
    data = json.loads(response.data.decode("utf-8"))
    assert data["version"] == auto6.SQX144_MT5_AUTO6_VERSION
    assert data["policyId"] == auto6.POLICY_ID
    assert data["decision"] == auto6.OBSERVE_DECISION
    assert data["writesDataDb"] is False
    assert data["writesUserProjects"] is False
    assert data["mutatesDatabanks"] is False
    assert data["runsSqxTasks"] is False
    assert data["directDbHistoryInsertAllowed"] is False
