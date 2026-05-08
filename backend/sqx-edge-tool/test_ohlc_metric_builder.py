from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "ohlc_metric_builder.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ohlc_metric_builder", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_ohlc(path: Path, *, base: float = 1.1, bars: int = 180) -> None:
    rows = ["time,open,high,low,close,volume"]
    price = base
    for index in range(bars):
        drift = math.sin(index / 12) * 0.001 + 0.0002
        open_ = price
        close = max(0.0001, open_ + drift)
        high = max(open_, close) + 0.0015
        low = min(open_, close) - 0.0015
        volume = 100 + (index % 20)
        rows.append(f"2024-01-01T00:{index % 60:02d}:00,{open_:.5f},{high:.5f},{low:.5f},{close:.5f},{volume}")
        price = close
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_ohlc_metric_builder_generates_metric_files(tmp_path):
    builder = load_module()
    input_dir = tmp_path / "input"
    out_dir = tmp_path / "out"
    input_dir.mkdir()
    write_ohlc(input_dir / "EURUSD_M30.csv", base=1.1)
    write_ohlc(input_dir / "XAUUSD_H4.csv", base=2000)

    report = builder.build_metric_files(input_dir=input_dir, out_dir=out_dir)
    m30 = json.loads((out_dir / "asset_metrics_M30.json").read_text(encoding="utf-8"))
    h4 = json.loads((out_dir / "asset_metrics_H4.json").read_text(encoding="utf-8"))

    assert report["status"] == "GO"
    assert "M30" in report["outputs"]
    assert "H4" in report["outputs"]
    assert m30["EURUSD"]["source"] == "operator_supplied_ohlc_csv"
    assert m30["EURUSD"]["bar_count"] == 180
    assert m30["EURUSD"]["ou_half_life_m30"] is not None
    assert h4["XAUUSD"]["type"] == "oro"
    assert (out_dir / "ohlc_metric_source_manifest.json").is_file()
    assert "# SQX OHLC Metric Builder" in builder.render_markdown(report)


def test_ohlc_metric_builder_rejects_too_few_bars(tmp_path):
    builder = load_module()
    input_dir = tmp_path / "input"
    out_dir = tmp_path / "out"
    input_dir.mkdir()
    write_ohlc(input_dir / "EURUSD_M15.csv", bars=20)

    report = builder.build_metric_files(input_dir=input_dir, out_dir=out_dir)

    assert report["status"] == "NO_GO"
    assert not report["outputs"]
    assert any("below minimum" in failure for failure in report["failures"])
