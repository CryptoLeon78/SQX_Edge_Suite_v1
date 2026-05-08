from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "multi_timeframe_metric_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("multi_timeframe_metric_gate", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complete_metrics(tf: str, *, asset: str = "EURUSD") -> dict:
    hl_key = f"ou_half_life_{tf.lower()}"
    return {
        asset: {
            "type": "forex",
            "subtype": "Major",
            "adx_mean": 22,
            "trend_efficiency_200": 0.28,
            "sma200_persistence_bars": 120,
            "rsi_edge_in_atrs": 0.7,
            "atr_pct_mean": 0.23,
            "vol_of_vol": 0.31,
            "hurst": 0.61,
            hl_key: 350,
            "kurtosis": 5.1,
            "vwap_rejection_rate": 0.55,
            "round_bounce_rate": 0.43,
        }
    }


def write_metrics(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_metric_gate_go_report_for_complete_metric_files(tmp_path):
    gate = load_module()
    write_metrics(tmp_path / "asset_metrics.json", complete_metrics("H1", asset="EURUSD"))
    write_metrics(tmp_path / "asset_metrics_M15.json", complete_metrics("M15", asset="XAUUSD"))

    report = gate.build_gate_report(
        metrics_dir=tmp_path,
        timeframes=["H1", "M15"],
        expected_assets={"EURUSD", "XAUUSD"},
        min_asset_coverage=0.5,
        min_metric_completeness=1.0,
    )
    markdown = gate.render_markdown(report)

    assert report["status"] == "GO"
    assert report["metadata"]["phase"] == "A51"
    assert report["scoringSummary"]["timeframesLoaded"] == ["H1", "M15"]
    assert len(report["files"][0]["sha256"]) == 64
    assert "# SQX Multi-Timeframe Metric Gate" in markdown
    assert "| TF | Exists | Asset Coverage | Metric Completeness | Unknown Assets | SHA256 |" in markdown


def test_metric_gate_rejects_missing_and_unknown_assets(tmp_path):
    gate = load_module()
    write_metrics(tmp_path / "asset_metrics.json", complete_metrics("H1", asset="UNKNOWN"))

    report = gate.build_gate_report(
        metrics_dir=tmp_path,
        timeframes=["H1", "M30"],
        expected_assets={"EURUSD", "XAUUSD"},
        min_asset_coverage=0.5,
        min_metric_completeness=0.5,
    )

    assert report["status"] == "NO_GO"
    assert any("missing metric file for M30" in failure for failure in report["failures"])
    assert any("unknown assets" in failure for failure in report["failures"])
    assert report["files"][0]["unknownAssets"] == ["UNKNOWN"]
