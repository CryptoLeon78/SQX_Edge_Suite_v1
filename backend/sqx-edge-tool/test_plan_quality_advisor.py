from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "plan_quality_advisor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plan_quality_advisor", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plan_quality_advisor_builds_report():
    advisor = load_module()

    report = advisor.build_report()

    assert report["metadata"]["phase"] == "A50"
    assert report["metadata"]["multiTimeframe"]["available"] is False
    assert report["metadata"]["candidateCount"] >= 14
    assert report["metadata"]["currentPlanCount"] == 14
    assert report["metadata"]["recommendedPlanCount"] == 14
    assert report["currentPlanSummary"]["supported"] >= 1
    assert "verdicts" in report["currentPlanSummary"]
    assert report["currentPlan"][0]["asset"] == "XAUUSD"
    assert report["currentPlan"][0]["category"] == "tendencia"
    assert report["recommendedPlan"][0]["recommended_rank"] == 1
    assert report["diff"]["add"]
    assert report["diff"]["review_not_selected"]


def mtf_metrics_fixture(tf: str) -> dict:
    hl_key = f"ou_half_life_{tf.lower()}"
    return {
        "XAUUSD": {
            "type": "oro",
            "subtype": "Gold",
            "adx_mean": 34,
            "trend_efficiency_200": 0.44,
            "sma200_persistence_bars": 190,
            "rsi_edge_in_atrs": 0.25,
            "atr_pct_mean": 0.8,
            "vol_of_vol": 0.7,
            "hurst": 0.68,
            hl_key: 500,
            "kurtosis": 8.0,
            "vwap_rejection_rate": 0.50,
            "round_bounce_rate": 0.40,
        },
        "EURUSD": {
            "type": "forex",
            "subtype": "Major",
            "adx_mean": 18,
            "trend_efficiency_200": 0.20,
            "sma200_persistence_bars": 95,
            "rsi_edge_in_atrs": 0.7,
            "atr_pct_mean": 0.2,
            "vol_of_vol": 0.3,
            "hurst": 0.58,
            hl_key: 320,
            "kurtosis": 5.0,
            "vwap_rejection_rate": 0.62,
            "round_bounce_rate": 0.48,
        },
        "USTEC": {
            "type": "index",
            "subtype": "Nasdaq",
            "adx_mean": 31,
            "trend_efficiency_200": 0.42,
            "sma200_persistence_bars": 170,
            "rsi_edge_in_atrs": 0.1,
            "atr_pct_mean": 0.6,
            "vol_of_vol": 0.5,
            "hurst": 0.62,
            hl_key: 700,
            "kurtosis": 6.0,
            "vwap_rejection_rate": 0.55,
            "round_bounce_rate": 0.37,
        },
    }


def test_plan_quality_advisor_adds_optional_mtf_evidence():
    advisor = load_module()
    mtf = advisor.load_multi_timeframe_scoring()
    mtf_report = mtf.build_report(
        metrics_by_tf={
            "H1": mtf_metrics_fixture("H1"),
            "M15": mtf_metrics_fixture("M15"),
        },
        timeframes=["H1", "M15"],
    )

    report = advisor.build_report(limit=5, min_composite=70, mtf_report=mtf_report)

    assert report["metadata"]["multiTimeframe"]["available"] is True
    assert report["metadata"]["multiTimeframe"]["timeframesLoaded"] == ["H1", "M15"]
    assert report["multiTimeframePlanSummary"]["covered"] >= 1
    first_xau = next(item for item in report["currentPlan"] if item["asset"] == "XAUUSD")
    assert first_xau["mtf_composite"] is not None
    assert first_xau["mtf_coverage"] == 2
    assert first_xau["mtf_assessment"] in {"strong", "moderate", "weak", "divergent", "limited"}


def test_plan_quality_advisor_markdown_is_operator_readable():
    advisor = load_module()
    report = advisor.build_report(limit=5, min_composite=70)

    markdown = advisor.render_markdown(report)

    assert "# SQX Plan Quality Advisor" in markdown
    assert "## Current Plan Review" in markdown
    assert "## Recommended Plan" in markdown
    assert "H1 baseline" in markdown
    assert "Multi-timeframe" in markdown
    assert "Review, not automatically drop" in markdown
    assert "| # | Asset | TF | BS | Dir | H1 Composite | Verdict | MTF Composite | MTF Evidence |" in markdown
