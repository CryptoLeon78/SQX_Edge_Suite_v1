from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from core.bsai21_asset_broker_instrument_review import (
    BS_AI21_ASSET_REVIEW_VERSION,
    BS_AI21_STATUS_OK,
    BS_AI21_STATUS_REQUIRES_WAIVER,
    review_payload,
    status_payload,
)


EXPERIMENT_ID = "BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_profile(root: Path, broker_key: str, *, broker_id: int, source_id: int, postfix: str) -> None:
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config" / "mt5_broker_catalog" / f"{broker_key}.json",
        {
            "version": "sqx144-mt5-auto3-broker-catalog-resolver-v1",
            "brokerKey": broker_key,
            "status": "test_profile",
            "sqxBroker": {
                "expectedBrokerId": broker_id,
                "expectedSourceId": source_id,
                "postfix": postfix,
                "nameMatchers": [broker_key],
            },
            "symbolMapping": {
                "mt5SymbolTemplate": "{asset}",
                "sqxInstrumentTemplate": "{asset}" + postfix,
                "sqxDataSymbolTemplate": "{asset}" + postfix,
            },
            "guards": {},
            "importRoutes": {},
        },
    )


def _create_db(root: Path, *, mismatch: bool = False) -> Path:
    host = root / "fake-host"
    host.mkdir(parents=True, exist_ok=True)
    db = host / "data.db"
    conn = sqlite3.connect(db)
    try:
        conn.execute('CREATE TABLE BROKER (ID INTEGER, NAME TEXT, POSTFIX TEXT, "DESC" TEXT)')
        conn.execute(
            'CREATE TABLE INSTRUMENTS (INSTRUMENT TEXT, BROKER_ID INTEGER, DEFAULTSPREAD REAL, POINTVALUE REAL, '
            'TICKSIZE REAL, TICKSTEP REAL, DEFAULTSLIPPAGE REAL, ORDERSIZEMULTIPLIER REAL, ORDERSIZESTEP REAL, '
            'SWAPLONG REAL, SWAPSHORT REAL, COMMISSION REAL)'
        )
        conn.execute(
            'CREATE TABLE DATA (SYMBOL TEXT, INSTRUMENT TEXT, TIMEFRAME TEXT, SOURCE INTEGER, BROKER_ID INTEGER, '
            'ROWS INTEGER, DATEFROM TEXT, DATETO TEXT, USYMBOL TEXT)'
        )
        conn.executemany(
            "INSERT INTO BROKER VALUES (?, ?, ?, ?)",
            [
                (4, "Darwinex", "_darwinex", "Darwinex test broker"),
                (3, "Dukascopy", "_dukascopy", "Dukascopy test broker"),
            ],
        )
        darwinex = ("AUDCAD_darwinex", 4, 1.3, 71753.512334, 0.0001, 0.00001, 0.0, 100000, 1000, 0.0, 0.0, 0.0)
        if mismatch:
            dukascopy = ("AUDCAD_dukascopy", 3, 1.0, 72157.360772, 0.0001, 0.00001, 0.0, 100000, 1000, 0.0, 0.0, 0.0)
        else:
            dukascopy = ("AUDCAD_dukascopy", 3, 1.3, 71753.512334, 0.0001, 0.00001, 0.0, 100000, 1000, 0.0, 0.0, 0.0)
        conn.executemany("INSERT INTO INSTRUMENTS VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [darwinex, dukascopy])
        conn.executemany(
            "INSERT INTO DATA VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("AUDCAD_darwinex", "AUDCAD_darwinex", "H1", 4, 4, 10000, "2010-01-01", "2026-06-01", "AUDCAD_darwinex"),
                ("AUDCAD_dukascopy", "AUDCAD_dukascopy", "H1", 2, 3, 10000, "2010-01-01", "2026-06-01", "AUDCAD_dukascopy"),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    return db


def _prepare_root(root: Path, *, mismatch: bool = False) -> None:
    db = _create_db(root, mismatch=mismatch)
    _write_json(
        root / "backend" / "sqx-edge-tool" / "config.json",
        {
            "sqx_host_profile": "sqx144_full",
            "sqx_data_db": str(db),
        },
    )
    _write_profile(root, "darwinex", broker_id=4, source_id=4, postfix="_darwinex")
    _write_profile(root, "dukascopy", broker_id=3, source_id=2, postfix="_dukascopy")


def test_bsai21_status_is_readonly():
    payload = status_payload(Path("."), experiment_id=EXPERIMENT_ID)
    assert payload["version"] == BS_AI21_ASSET_REVIEW_VERSION
    assert payload["status"] == "asset_broker_instrument_review_ready_readonly_no_apply"
    assert payload["guards"]["writesDataDb"] is False
    assert payload["guards"]["projectStartRequested"] is False
    assert payload["guards"]["capa2StartAllowed"] is False


def test_review_clean_parity_allows_next_preregistered_capa1_with_controls(tmp_path):
    _prepare_root(tmp_path, mismatch=False)
    payload = review_payload(tmp_path, experiment_id=EXPERIMENT_ID, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI21_ASSET_REVIEW_VERSION
    assert payload["status"] == BS_AI21_STATUS_OK
    assert payload["ok"] is True
    assert payload["contractComparison"]["parityOk"] is True
    assert payload["decision"]["newCapa1AllowedAfterReview"] is True
    assert payload["decision"]["capa2StartAllowed"] is False
    assert payload["guards"]["writesDataDb"] is False
    assert payload["evidenceRef"].startswith("bsai21_asset_broker_instrument_review_review_")
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob
    assert '"sqx_data_db"' not in blob


def test_review_spread_pointvalue_mismatch_requires_fix_or_explicit_waiver(tmp_path):
    _prepare_root(tmp_path, mismatch=True)
    payload = review_payload(tmp_path, experiment_id=EXPERIMENT_ID)
    mismatches = {item["field"]: item for item in payload["contractComparison"]["mismatches"]}

    assert payload["status"] == BS_AI21_STATUS_REQUIRES_WAIVER
    assert payload["ok"] is False
    assert payload["decision"]["requiresFixOrExplicitWaiver"] is True
    assert payload["decision"]["newCapa1AllowedAfterReview"] is False
    assert payload["decision"]["newCapa1AllowedWithExplicitWaiver"] is True
    assert mismatches["DEFAULTSPREAD"]["severity"] == "requires_fix_or_explicit_waiver"
    assert mismatches["POINTVALUE"]["severity"] == "requires_fix_or_explicit_waiver"
    assert "cost_contract_mismatch_requires_fix_or_explicit_waiver_before_next_capa1" in payload["decision"]["warnings"]


def test_review_allows_tick_source_when_reference_history_uses_primary_effective_instrument(tmp_path):
    _prepare_root(tmp_path, mismatch=True)
    db = tmp_path / "fake-host" / "data.db"
    conn = sqlite3.connect(db)
    try:
        conn.execute("DELETE FROM DATA")
        conn.executemany(
            "INSERT INTO DATA VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("AUDCAD_darwinex", "AUDCAD_darwinex", "TICK", 4, 4, 10000, "2010-01-01", "2026-06-01", "AUDCAD"),
                ("AUDCAD_dukascopy", "AUDCAD_darwinex", "TICK", 2, 4, 11000, "2010-01-01", "2026-06-01", "AUDCAD"),
            ],
        )
        conn.commit()
    finally:
        conn.close()
    (tmp_path / "backend" / "sqx-edge-tool" / "config" / "mt5_broker_catalog" / "dukascopy.json").unlink()

    payload = review_payload(tmp_path, experiment_id=EXPERIMENT_ID)

    assert payload["status"] == BS_AI21_STATUS_OK
    assert payload["contractComparison"]["parityOk"] is True
    assert payload["standaloneReferenceComparison"]["parityOk"] is False
    assert payload["reference"]["effectiveInstrument"]["instrument"] == "AUDCAD_darwinex"
    assert payload["reference"]["history"]["usesTickBackingSource"] is True
    assert payload["reference"]["history"]["sourceOnlyFallbackUsed"] is True
    assert "standalone_dukascopy_instrument_differs_but_history_uses_darwinex_effective_instrument" in payload["decision"]["warnings"]
    assert "reference_dukascopy_auto3_profile_missing_using_host_convention" in payload["decision"]["warnings"]


def test_missing_config_blocks_without_host_mutation(tmp_path):
    payload = review_payload(tmp_path, experiment_id=EXPERIMENT_ID)

    assert payload["ok"] is False
    assert payload["status"] == "asset_broker_instrument_review_blocked_no_apply"
    assert "sqx_edge_config_missing" in payload["decision"]["blockers"]
    assert payload["guards"]["projectImportRequested"] is False
    assert payload["guards"]["mutatesDatabanks"] is False
