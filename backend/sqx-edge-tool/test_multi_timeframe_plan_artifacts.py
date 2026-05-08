from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "multi_timeframe_plan_artifacts.py"


def load_module():
    spec = importlib.util.spec_from_file_location("multi_timeframe_plan_artifacts", TOOL_PATH)
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
        },
        "XAUUSD": {
            "type": "oro",
            "subtype": "Gold",
            "adx_mean": 31,
            "trend_efficiency_200": 0.42,
            "sma200_persistence_bars": 180,
            "rsi_edge_in_atrs": 0.2,
            "atr_pct_mean": 0.75,
            "vol_of_vol": 0.68,
            "hurst_dist": 0.18,
            f"ou_half_life_{tf.lower()}": 480,
            "kurtosis": 7.2,
            "vwap_rejection_rate": 0.50,
            "round_bounce_rate": 0.39,
        },
    }


def write_metrics(path: Path, tf: str) -> None:
    path.write_text(json.dumps(metrics_fixture(tf), indent=2), encoding="utf-8")


def test_multi_timeframe_plan_artifacts_block_when_intake_is_not_go(tmp_path):
    artifacts = load_module()
    source_dir = tmp_path / "source"
    work_dir = tmp_path / "work"
    source_dir.mkdir()

    report = artifacts.build_plan_artifacts(source_dir=source_dir, work_dir=work_dir)

    assert report["status"] == "NO_GO"
    assert "planJson" not in report["artifacts"]
    assert (work_dir / "a53_intake_report.json").is_file()
    assert (work_dir / "a54_plan_artifacts_report.md").is_file()
    assert "not generated" in report["metadata"]["reason"]


def test_multi_timeframe_plan_artifacts_generate_advisor_when_intake_is_go(tmp_path):
    artifacts = load_module()
    source_dir = tmp_path / "source"
    work_dir = tmp_path / "work"
    source_dir.mkdir()
    write_metrics(source_dir / "asset_metrics.json", "H1")
    write_metrics(source_dir / "asset_metrics_M30.json", "M30")
    write_metrics(source_dir / "asset_metrics_M15.json", "M15")
    write_metrics(source_dir / "asset_metrics_H4.json", "H4")

    report = artifacts.build_plan_artifacts(
        source_dir=source_dir,
        work_dir=work_dir,
        include_first_party_h1=False,
        expected_assets={"EURUSD", "XAUUSD"},
        limit=5,
    )

    assert report["status"] == "GO"
    assert report["intake"]["status"] == "GO"
    assert (work_dir / "plan_quality_advisor_mtf.json").is_file()
    assert (work_dir / "plan_quality_advisor_mtf.md").is_file()
    assert report["artifacts"]["planJson"].endswith("plan_quality_advisor_mtf.json")
    assert "# SQX Multi-Timeframe Plan Artifacts" in artifacts.render_markdown(report)
