import json

from api import server
from core.sqx142_correlation_filter_external import (
    CORRELATION_FILTER_EXTERNAL_VERSION,
    build_correlation_filter_report,
    export_correlation_filter_csv,
    export_correlation_filter_sqx_tag_csv,
)


SERIES_A = "0.01|0.02|0.015|0.03|-0.01|0.02|0.01|0.025|0.03|-0.005|0.012|0.02"
SERIES_B = "0.02|0.04|0.03|0.06|-0.02|0.04|0.02|0.05|0.06|-0.01|0.024|0.04"
SERIES_C = "0.03|-0.02|0.01|-0.01|0.02|-0.015|0.018|-0.02|0.014|-0.01|0.016|-0.018"


def _row(name, **overrides):
    row = {
        "strategy": name,
        "asset": "AUDCAD",
        "timeframe": "H1",
        "BlockSetting": "BS_Custom",
        "indicator": name.split("_")[0],
        "sourcePhase": "phase28_capa2_forward",
        "sourceDatabank": "Foward",
        "status": "PASSED",
        "Profit Factor": 1.55,
        "Ret/DD Ratio": 4.2,
        "Max DD %": 18,
        "Number of trades": 140,
        "Stability": 0.72,
        "SQN": 2.1,
        "returnSeries": SERIES_A,
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


def test_correlation_filter_selects_portfolio_and_blocks_correlated_candidate():
    rows = [
        _row("MACD_A", returnSeries=SERIES_A),
        _row("MACD_B", **{"Profit Factor": 1.25, "Ret/DD Ratio": 3.0, "returnSeries": SERIES_B}),
        _row("RSI_C", asset="EURJPY", indicator="RSI", BlockSetting="BS_Alt", returnSeries=SERIES_C),
    ]

    report = build_correlation_filter_report(rows)

    assert report["ok"] is True
    assert report["version"] == CORRELATION_FILTER_EXTERNAL_VERSION
    assert report["mode"] == "external_readonly"
    assert report["summary"]["inputRows"] == 3
    assert report["summary"]["portfolio"] == 2
    assert report["summary"]["similar"] == 1
    assert all(item["strategyRef"].startswith("strategy_") for item in report["items"])
    assert [item["portfolioRank"] for item in report["items"] if item["decision"] == "portfolio"] == [1, 2]
    assert json.dumps(report).find("MACD_A") == -1
    similar = [item for item in report["items"] if item["decision"] == "similar"][0]
    assert similar["correlationStatus"] == "available"
    assert similar["maxObservedCorrelation"] >= 0.99
    assert "correlation >=" in similar["reason"]
    assert similar["nearestWinnerId"].startswith("candidate_")
    _assert_public_safe(report)


def test_correlation_filter_marks_failed_and_sample_rows_for_review():
    rows = [
        _row("MACD_A", returnSeries=SERIES_A),
        _row("FAILED_ROW", status="FAILED", returnSeries=SERIES_C),
        _row("SAMPLE_ROW", **{"Example Only": "true", "returnSeries": SERIES_C}),
    ]

    report = build_correlation_filter_report(rows)

    reviews = [item for item in report["items"] if item["decision"] == "review"]
    assert len(reviews) == 2
    assert any("status != PASSED natural" in item["reason"] for item in reviews)
    assert any("sample/example row rejected" in item["reason"] for item in reviews)


def test_correlation_filter_uses_similarity_only_when_series_are_missing():
    rows = [
        _row("MACD_A", returnSeries=""),
        _row("MACD_B", returnSeries="", **{"Profit Factor": 1.45, "Ret/DD Ratio": 4.0}),
    ]

    report = build_correlation_filter_report(rows)

    assert report["summary"]["portfolio"] == 1
    assert report["summary"]["similar"] == 1
    similar = [item for item in report["items"] if item["decision"] == "similar"][0]
    assert similar["correlationStatus"] == "similarity_only"
    assert "operational similarity >=" in similar["reason"]


def test_correlation_filter_marks_short_series_as_not_comparable_review():
    rows = [
        _row("MACD_A", returnSeries=SERIES_A),
        _row(
            "RSI_SHORT",
            asset="EURJPY",
            timeframe="M15",
            BlockSetting="BS_Alt",
            indicator="RSI",
            returnSeries="0.01|0.02|0.03",
        ),
    ]

    report = build_correlation_filter_report(rows)

    review = [item for item in report["items"] if item["decision"] == "review"][0]
    assert review["correlationStatus"] == "not_comparable"
    assert review["reason"] == "series not comparable"


def test_correlation_filter_redacts_private_markers_and_exports_csv():
    rows = [
        _row(
            "PRIVATE",
            asset=r"C:\\BOTS\\Versiones\\SQX_142_Crack\\AUDCAD",
            operatorEmail="ivan@example.invalid",
            brokerPrivate="token=secret-token-12345",
            localPath=r"C:\\private\\portfolio.csv",
        )
    ]

    report = build_correlation_filter_report(rows)
    csv_export = export_correlation_filter_csv(report)

    assert report["summary"]["redactedFields"] >= 3
    assert "candidateId,decision,reason" in csv_export
    _assert_public_safe(report)
    _assert_public_safe({"csv": csv_export})


def test_correlation_filter_exports_sqx_tag_csv_with_private_strategy_refs():
    rows = [
        _row("MACD_A", returnSeries=SERIES_A),
        _row("MACD_B", **{"Profit Factor": 1.25, "Ret/DD Ratio": 3.0, "returnSeries": SERIES_B}),
    ]

    report = build_correlation_filter_report(rows)
    tag_csv = export_correlation_filter_sqx_tag_csv(report)
    lines = tag_csv.strip().splitlines()

    assert lines[0] == (
        "strategyRef,candidateId,decision,reason,score,maxObservedCorrelation,"
        "correlationStatus,nearestWinnerId,portfolioRank,generatedAt,version"
    )
    assert "strategy_" in tag_csv
    assert "MACD_A" not in tag_csv
    assert "MACD_B" not in tag_csv
    assert CORRELATION_FILTER_EXTERNAL_VERSION in tag_csv
    _assert_public_safe({"sqxTagCsv": tag_csv})


def test_correlation_filter_route_is_local_operator_only_and_returns_optional_csv():
    client = server.app.test_client()
    response = client.post(
        "/api/sqx142/correlation-filter/external",
        json={"rows": [_row("MACD_A")], "includeCsvExport": True, "includeSqxTagCsv": True},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == CORRELATION_FILTER_EXTERNAL_VERSION
    assert data["privacy"]["local_paths_returned"] is False
    assert "csvExport" in data
    assert "sqxTagCsv" in data
    assert data["sqxTagCsv"].splitlines()[0].startswith("strategyRef,candidateId,decision")
    _assert_public_safe(data)

    blocked = client.post(
        "/api/sqx142/correlation-filter/external",
        json={"rows": [_row("MACD_A")]},
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"
