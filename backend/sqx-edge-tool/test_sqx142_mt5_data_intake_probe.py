import json
from datetime import datetime, timedelta

from api import server
from core.sqx142_mt5_data_intake_probe import (
    MT5_DATA_INTAKE_PROBE_VERSION,
    build_mt5_data_intake_probe_report,
    export_mt5_data_intake_probe_csv,
)


def _bars(count=30, start="2026-01-01T00:00:00"):
    base = datetime.fromisoformat(start)
    rows = []
    for index in range(count):
        open_price = 1.1000 + (index * 0.0001)
        close_price = open_price + 0.00005
        rows.append({
            "time": (base + timedelta(hours=index)).isoformat(),
            "open": round(open_price, 5),
            "high": round(close_price + 0.0002, 5),
            "low": round(open_price - 0.0002, 5),
            "close": round(close_price, 5),
            "volume": 100 + index,
        })
    return rows


def _catalog(**overrides):
    row = {
        "SYMBOL": "EURUSD_darwinex",
        "INSTRUMENT": "EURUSD",
        "TIMEFRAME": "H1",
        "DATATYPE": "3",
        "DATEFROM": "2025-01-01",
        "DATETO": "2026-12-31",
        "TIMEZONE": "EETUS",
    }
    row.update(overrides)
    return row


def _assert_public_safe(payload):
    encoded = json.dumps(payload, ensure_ascii=False)
    assert r"C:\\" not in encoded
    assert "SQX_142_Crack" not in encoded
    assert "ivan@example" not in encoded
    assert "token=" not in encoded.lower()
    assert "secret" not in encoded.lower()
    assert "password=" not in encoded.lower()
    assert "EURUSD_darwinex" not in encoded


def test_mt5_data_intake_probe_passes_valid_copy_against_catalog_fixture():
    report = build_mt5_data_intake_probe_report({
        "asset": "EURUSD",
        "timeframe": "H1",
        "rows": _bars(),
        "sqxDataRows": [_catalog()],
    })

    assert report["ok"] is True
    assert report["version"] == MT5_DATA_INTAKE_PROBE_VERSION
    assert report["mode"] == "external_readonly"
    assert report["source"] == "mt5_csv_copy"
    assert report["decision"] == "intake_probe_pass"
    assert report["summary"]["validBars"] == 30
    assert report["summary"]["catalogMatches"] == 1
    assert report["summary"]["bestOverlapDays"] >= 1
    assert report["sqxCatalog"]["matched"] is True
    assert report["guards"]["mt5_ipc_called"] is False
    assert report["guards"]["sqx_data_imported"] is False
    _assert_public_safe(report)


def test_mt5_data_intake_probe_reviews_missing_catalog_match():
    report = build_mt5_data_intake_probe_report({
        "asset": "EURUSD",
        "timeframe": "H1",
        "rows": _bars(),
        "sqxDataRows": [_catalog(SYMBOL="AUDCAD_darwinex", INSTRUMENT="AUDCAD")],
    })

    assert report["decision"] == "intake_probe_review"
    assert "sqx_data_catalog_match_missing" in report["warnings"]
    assert report["summary"]["catalogMatches"] == 0
    _assert_public_safe(report)


def test_mt5_data_intake_probe_fails_invalid_or_short_copy():
    rows = _bars(4)
    rows.append({"time": "2026-01-01T05:00:00", "open": 1.1, "high": 1.0, "low": 1.2, "close": 1.1, "volume": 1})
    report = build_mt5_data_intake_probe_report({
        "asset": "EURUSD",
        "timeframe": "H1",
        "rows": rows,
        "sqxDataRows": [_catalog()],
    })

    assert report["decision"] == "intake_probe_fail"
    assert "not_enough_bars" in report["blockers"]
    assert "invalid_rows_ignored" in report["warnings"]
    assert report["summary"]["invalidRows"] == 1


def test_mt5_data_intake_probe_detects_range_review_and_exports_csv():
    report = build_mt5_data_intake_probe_report({
        "asset": "EURUSD",
        "timeframe": "H1",
        "rows": _bars(),
        "sqxDataRows": [_catalog(DATEFROM="2024-01-01", DATETO="2024-12-31")],
    })
    csv_export = export_mt5_data_intake_probe_csv(report)

    assert report["decision"] == "intake_probe_review"
    assert "sqx_data_range_overlap_missing" in report["warnings"]
    assert "decision,assetRef,timeframe" in csv_export
    _assert_public_safe(report)
    _assert_public_safe({"csv": csv_export})


def test_mt5_data_intake_probe_redacts_private_markers():
    report = build_mt5_data_intake_probe_report({
        "asset": r"C:\\BOTS\\Versiones\\SQX_142_Crack\\EURUSD",
        "timeframe": "H1",
        "rows": _bars(),
        "sqxDataRows": [_catalog()],
        "operatorEmail": "ivan@example.invalid",
        "brokerPrivate": "token=secret-token-12345",
        "localPath": r"C:\\private\\mt5.csv",
    })

    assert report["summary"]["redactedFields"] >= 1
    _assert_public_safe(report)


def test_mt5_data_intake_probe_route_is_local_operator_only_and_returns_optional_csv():
    client = server.app.test_client()
    response = client.post(
        "/api/sqx142/mt5-data-intake/probe",
        json={
            "asset": "EURUSD",
            "timeframe": "H1",
            "rows": _bars(),
            "sqxDataRows": [_catalog()],
            "includeCsvExport": True,
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == MT5_DATA_INTAKE_PROBE_VERSION
    assert data["privacy"]["local_paths_returned"] is False
    assert "csvExport" in data
    _assert_public_safe(data)

    blocked = client.post(
        "/api/sqx142/mt5-data-intake/probe",
        json={"asset": "EURUSD", "timeframe": "H1", "rows": _bars(), "sqxDataRows": [_catalog()]},
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"
