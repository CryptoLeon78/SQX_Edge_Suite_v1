from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "multi_timeframe_scoring.py"


def load_module():
    spec = importlib.util.spec_from_file_location("multi_timeframe_scoring", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metrics_fixture(tf: str) -> dict:
    hl_key = f"ou_half_life_{tf.lower()}"
    return {
        "EURUSD": {
            "type": "forex",
            "subtype": "Major",
            "adx_mean": 19 if tf == "H1" else 17,
            "trend_efficiency_200": 0.22,
            "sma200_persistence_bars": 110,
            "rsi_edge_in_atrs": 0.8,
            "atr_pct_mean": 0.18,
            "vol_of_vol": 0.24,
            "hurst": 0.63,
            hl_key: 300,
            "kurtosis": 5.0,
            "vwap_rejection_rate": 0.62,
            "round_bounce_rate": 0.44,
        },
        "GBPJPY": {
            "type": "forex",
            "subtype": "Cross",
            "adx_mean": 31,
            "trend_efficiency_200": 0.42,
            "sma200_persistence_bars": 180,
            "rsi_edge_in_atrs": 0.3,
            "atr_pct_mean": 0.62,
            "vol_of_vol": 0.58,
            "hurst": 0.47,
            hl_key: 600,
            "kurtosis": 4.0,
            "vwap_rejection_rate": 0.40,
            "round_bounce_rate": 0.28,
        },
        "XAUUSD": {
            "type": "oro",
            "subtype": "Gold",
            "adx_mean": 28,
            "trend_efficiency_200": 0.37,
            "sma200_persistence_bars": 160,
            "rsi_edge_in_atrs": 0.1,
            "atr_pct_mean": 0.75,
            "vol_of_vol": 0.70,
            "hurst": 0.69,
            hl_key: 450,
            "kurtosis": 7.5,
            "vwap_rejection_rate": 0.52,
            "round_bounce_rate": 0.39,
        },
    }


def test_multi_timeframe_scoring_builds_consensus():
    scoring = load_module()

    report = scoring.build_report(
        metrics_by_tf={
            "H1": metrics_fixture("H1"),
            "M15": metrics_fixture("M15"),
        },
        timeframes=["H1", "M15", "H4"],
        weights={"H1": 0.7, "M15": 0.3},
    )

    assert report["metadata"]["phase"] == "A49"
    assert report["metadata"]["timeframesLoaded"] == ["H1", "M15"]
    assert report["metadata"]["weights"] == {"H1": 0.7, "M15": 0.3}
    assert report["scoresByTimeframe"]["H1"]["GBPJPY"]["tendencia"]["objective"] == "++"
    assert report["consensus"]["GBPJPY"]["tendencia"]["coverage"] == 2
    assert report["consensus"]["GBPJPY"]["tendencia"]["best_tf"] in {"H1", "M15"}
    assert report["consensus"]["XAUUSD"]["volatilidad"]["weighted_composite"] > 0.9
    assert report["consensus"]["EURUSD"]["momentum"]["objective"] == "++"


def test_multi_timeframe_scoring_loads_metric_files_and_renders_markdown(tmp_path):
    scoring = load_module()
    (tmp_path / "asset_metrics.json").write_text(json.dumps(metrics_fixture("H1")), encoding="utf-8")
    (tmp_path / "asset_metrics_M30.json").write_text(json.dumps(metrics_fixture("M30")), encoding="utf-8")

    report = scoring.build_report(metrics_dir=tmp_path, timeframes=["H1", "M30", "H4"])
    markdown = scoring.render_markdown(report, top=4)

    assert report["metadata"]["timeframesLoaded"] == ["H1", "M30"]
    assert "# SQX Multi-Timeframe Scoring" in markdown
    assert "## Top Consensus" in markdown
    assert "| Rank | Asset | Category | Weighted | Rating | Coverage | Consensus | Best TF |" in markdown
    assert "does not download market data" in report["metadata"]["caveat"]
