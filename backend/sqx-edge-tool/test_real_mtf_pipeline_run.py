from __future__ import annotations

import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "real_mtf_pipeline_run.py"


def load_module():
    spec = importlib.util.spec_from_file_location("real_mtf_pipeline_run", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_ohlc(path: Path, *, base: float = 1.1, bars: int = 180) -> None:
    rows = ["time,open,high,low,close,volume"]
    price = base
    for index in range(bars):
        drift = math.sin(index / 11) * 0.001 + 0.00015
        open_ = price
        close = max(0.0001, open_ + drift)
        high = max(open_, close) + 0.0014
        low = min(open_, close) - 0.0014
        volume = 100 + (index % 30)
        rows.append(f"2024-01-01T00:{index % 60:02d}:00,{open_:.5f},{high:.5f},{low:.5f},{close:.5f},{volume}")
        price = close
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_real_mtf_pipeline_no_go_without_input_dir(tmp_path):
    runner = load_module()
    report = runner.run_pipeline(input_dir=tmp_path / "missing", work_dir=tmp_path / "work")

    assert report["status"] == "NO_GO"
    assert "input directory does not exist" in report["failures"][0]
    assert (tmp_path / "work" / "a56_real_mtf_pipeline_run.md").is_file()


def test_real_mtf_pipeline_go_with_complete_observed_fixture(tmp_path):
    runner = load_module()
    input_dir = tmp_path / "ohlc"
    work_dir = tmp_path / "work"
    input_dir.mkdir()
    for tf in ("H1", "M30", "M15", "H4"):
        write_ohlc(input_dir / f"EURUSD_{tf}.csv")
        write_ohlc(input_dir / f"XAUUSD_{tf}.csv", base=2000)

    report = runner.run_pipeline(
        input_dir=input_dir,
        work_dir=work_dir,
        expected_assets_mode="observed",
        include_first_party_h1=False,
    )

    assert report["status"] == "GO"
    assert report["builder"]["status"] == "GO"
    assert report["artifacts"]["status"] == "GO"
    assert len(report["builder"]["outputs"]) == 4
    assert (work_dir / "a56_real_mtf_pipeline_run.json").is_file()
    assert "# SQX Real MTF Pipeline Run" in runner.render_markdown(report)
