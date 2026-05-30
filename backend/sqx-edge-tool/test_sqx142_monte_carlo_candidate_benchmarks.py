import json

from api import server
from core.sqx142_monte_carlo_candidate_benchmarks import (
    MONTE_CARLO_BENCHMARKS_VERSION,
    build_monte_carlo_benchmark_report,
    export_monte_carlo_benchmark_csv,
)


STABLE_SERIES = "0.012|0.009|0.014|0.011|0.013|0.008|0.012|0.015|0.01|0.013|0.009|0.012|0.014|0.011|0.01|0.013"
FRAGILE_SERIES = "0.002|-0.035|0.004|-0.04|0.003|-0.03|0.002|-0.045|0.003|-0.025|0.002|-0.035|0.004|-0.03|0.001|-0.025"
SHORT_SERIES = "0.01|0.02|0.03"


def _row(name, **overrides):
    row = {
        "strategy": name,
        "asset": "AUDCAD",
        "timeframe": "H1",
        "BlockSetting": "BS_Custom",
        "returnSeries": STABLE_SERIES,
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


def test_monte_carlo_benchmark_passes_stable_candidate():
    report = build_monte_carlo_benchmark_report([_row("STABLE_A")])

    assert report["ok"] is True
    assert report["version"] == MONTE_CARLO_BENCHMARKS_VERSION
    assert report["mode"] == "external_readonly"
    assert report["summary"]["inputRows"] == 1
    assert report["summary"]["evaluatedRows"] == 1
    assert report["summary"]["benchmarkPass"] == 1
    item = report["items"][0]
    assert item["decision"] == "benchmark_pass"
    assert {result["method"] for result in item["benchmarks"]} == {
        "MACHRBlockRandomization",
        "SimulateParameterJitter",
        "RandomlyDegradeExecution",
    }
    assert {result["status"] for result in item["benchmarks"]} == {"pass"}
    assert item["candidateId"].startswith("candidate_")
    assert item["strategyRef"].startswith("strategy_")
    _assert_public_safe(report)


def test_monte_carlo_benchmark_fails_fragile_candidate():
    report = build_monte_carlo_benchmark_report([_row("FRAGILE_A", returnSeries=FRAGILE_SERIES)])

    assert report["summary"]["benchmarkFail"] == 1
    item = report["items"][0]
    assert item["decision"] == "benchmark_fail"
    assert any(result["status"] == "fail" for result in item["benchmarks"])
    assert item["base"]["maxDrawdownPct"] > 20


def test_monte_carlo_benchmark_reviews_short_or_missing_series():
    report = build_monte_carlo_benchmark_report([
        _row("SHORT_A", returnSeries=SHORT_SERIES),
        _row("MISSING_A", returnSeries=""),
    ])

    assert report["summary"]["benchmarkReview"] == 2
    assert report["summary"]["evaluatedRows"] == 0
    assert all(item["decision"] == "benchmark_review" for item in report["items"])
    assert all("not_enough_series" in item["warnings"] for item in report["items"])


def test_monte_carlo_benchmark_blocks_samples_forced_passes_and_redacts_private_markers():
    report = build_monte_carlo_benchmark_report([
        _row(
            "PRIVATE",
            **{
                "Example Only": "true",
                "result": "manual forced pass",
                "asset": r"C:\\BOTS\\Versiones\\SQX_142_Crack\\AUDCAD",
                "operatorEmail": "ivan@example.invalid",
                "brokerPrivate": "token=secret-token-12345",
                "localPath": r"C:\\private\\portfolio.csv",
            },
        )
    ])

    item = report["items"][0]
    assert item["decision"] == "benchmark_review"
    assert "sample/example row rejected" in item["blockers"]
    assert "forced/manual/synthetic/fabricated pass rejected" in item["blockers"]
    assert report["summary"]["sampleBlocked"] == 1
    assert report["summary"]["redactedFields"] >= 3
    _assert_public_safe(report)


def test_monte_carlo_benchmark_is_deterministic_and_exports_csv():
    rows = [_row("STABLE_A")]
    settings = {"simulations": 16, "seed": "fixed-seed"}
    first = build_monte_carlo_benchmark_report(rows, settings=settings)
    second = build_monte_carlo_benchmark_report(rows, settings=settings)
    csv_export = export_monte_carlo_benchmark_csv(first)

    first["analyzedAt"] = "ignored"
    second["analyzedAt"] = "ignored"
    assert first == second
    assert "candidateId,decision,reason" in csv_export
    assert "MACHRBlockRandomization" in csv_export
    _assert_public_safe({"csv": csv_export})


def test_monte_carlo_benchmark_route_is_local_operator_only_and_returns_optional_csv():
    client = server.app.test_client()
    response = client.post(
        "/api/sqx142/monte-carlo/benchmarks",
        json={"rows": [_row("STABLE_A")], "settings": {"simulations": 8}, "includeCsvExport": True},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == MONTE_CARLO_BENCHMARKS_VERSION
    assert data["privacy"]["local_paths_returned"] is False
    assert "csvExport" in data
    _assert_public_safe(data)

    blocked = client.post(
        "/api/sqx142/monte-carlo/benchmarks",
        json={"rows": [_row("STABLE_A")]},
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"
