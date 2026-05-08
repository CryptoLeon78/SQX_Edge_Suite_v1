from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "multi_timeframe_source_intake.py"


def load_module():
    spec = importlib.util.spec_from_file_location("multi_timeframe_source_intake", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metrics_fixture(tf: str) -> dict:
    return {
        "EURUSD": {
            "type": "forex",
            "subtype": "Major",
            "adx_mean": 22,
            "trend_efficiency_200": 0.28,
            "sma200_persistence_bars": 120,
            "rsi_edge_in_atrs": 0.7,
            "atr_pct_mean": 0.23,
            "vol_of_vol": 0.31,
            "hurst_dist": 0.11,
            f"ou_half_life_{tf.lower()}": 350,
            "kurtosis": 5.1,
            "vwap_rejection_rate": 0.55,
            "round_bounce_rate": 0.43,
        }
    }


def write_metrics(path: Path, tf: str) -> None:
    path.write_text(json.dumps(metrics_fixture(tf), indent=2), encoding="utf-8")


def test_multi_timeframe_source_intake_go_for_complete_real_metric_folder(tmp_path):
    intake = load_module()
    source_dir = tmp_path / "source"
    out_dir = tmp_path / "out"
    source_dir.mkdir()
    write_metrics(source_dir / "asset_metrics.json", "H1")
    write_metrics(source_dir / "asset_metrics_M30.json", "M30")
    write_metrics(source_dir / "asset_metrics_M15.json", "M15")
    write_metrics(source_dir / "asset_metrics_H4.json", "H4")

    report = intake.build_intake_report(
        source_dir=source_dir,
        out_dir=out_dir,
        include_first_party_h1=False,
        expected_assets={"EURUSD"},
    )

    assert report["status"] == "GO"
    assert report["metadata"]["phase"] == "A53"
    assert report["missingRealTimeframes"] == []
    assert report["gate"]["status"] == "GO"
    assert all(item["status"] == "copied" for item in report["bundle"]["files"])
    assert "SQX Multi-Timeframe Source Intake" in intake.render_markdown(report)


def test_multi_timeframe_source_intake_blocks_missing_real_timeframes(tmp_path):
    intake = load_module()
    source_dir = tmp_path / "source"
    out_dir = tmp_path / "out"
    source_dir.mkdir()

    report = intake.build_intake_report(
        source_dir=source_dir,
        out_dir=out_dir,
        include_first_party_h1=True,
    )

    assert report["status"] == "NO_GO"
    assert report["missingRealTimeframes"] == ["M30", "M15", "H4"]
    assert any("synthetic metrics" in failure for failure in report["failures"])
    assert (out_dir / "asset_metrics.json").is_file()
    assert (out_dir / "metric_source_manifest.json").is_file()
