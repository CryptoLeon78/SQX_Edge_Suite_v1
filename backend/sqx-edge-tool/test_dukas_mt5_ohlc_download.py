from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "dukas_mt5_ohlc_download.py"


def load_module():
    spec = importlib.util.spec_from_file_location("dukas_mt5_ohlc_download", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeMT5:
    TIMEFRAME_M15 = "M15"
    TIMEFRAME_M30 = "M30"
    TIMEFRAME_H1 = "H1"
    TIMEFRAME_H4 = "H4"

    def __init__(self, known_symbols: set[str] | None = None, bars: int = 140):
        self.known_symbols = known_symbols or {"EURUSD", "USA500.IDX"}
        self.bars = bars
        self.initialized_path = None
        self.initialized_timeout = None
        self.shutdown_called = False
        self.from_pos_calls = []

    def initialize(self, path=None, timeout=None):
        self.initialized_path = path
        self.initialized_timeout = timeout
        return True

    def last_error(self):
        return (0, "ok")

    def symbol_info(self, symbol):
        return object() if symbol in self.known_symbols else None

    def symbol_select(self, symbol, enabled):
        return enabled and symbol in self.known_symbols

    def copy_rates_range(self, symbol, tf_code, start, end):
        return self._make_rates(symbol, tf_code, self.bars, int(time.mktime(start.timetuple())))

    def copy_rates_from_pos(self, symbol, tf_code, start_pos, count):
        self.from_pos_calls.append((symbol, tf_code, start_pos, count))
        return self._make_rates(symbol, tf_code, int(count), 1704067200)

    def _make_rates(self, symbol, tf_code, bars, start_ts):
        base = 1.1 if symbol == "EURUSD" else 5000.0
        return [
            {
                "time": start_ts + index * 3600,
                "open": base + index * 0.001,
                "high": base + index * 0.001 + 0.01,
                "low": base + index * 0.001 - 0.01,
                "close": base + index * 0.001 + 0.002,
                "tick_volume": 100 + index,
            }
            for index in range(bars)
        ]

    def shutdown(self):
        self.shutdown_called = True


class AmbiguousRates:
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def __bool__(self):
        raise ValueError("ambiguous truth value")


def write_config(path: Path, output_dir: Path, coverage_dir: Path, **overrides):
    config = {
        "phase": "A58",
        "state": "dukas_mt5_ohlc_download_gate_ready",
        "mode": "internal_operator_optional",
        "terminalPath": "C:/fake/terminal64.exe",
        "outputDir": str(output_dir),
        "coverageDir": str(coverage_dir),
        "startDate": "2024-01-01",
        "endDate": "2024-03-01",
        "startupDelaySeconds": 0,
        "retryCount": 1,
        "retryDelaySeconds": 0,
        "minimumBars": 5,
        "skipExistingMinKb": 50,
        "timeframes": ["H1", "M30"],
        "symbolMap": {"EURUSD": "EURUSD", "US500": "USA500.IDX"},
        "nextPhase": "A59",
    }
    config.update(overrides)
    path.write_text(json.dumps(config), encoding="utf-8")


def test_dukas_download_writes_csv_and_coverage(tmp_path):
    tool = load_module()
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "ohlc"
    coverage_dir = tmp_path / "coverage"
    write_config(config_path, output_dir, coverage_dir)
    mt5 = FakeMT5()

    report = tool.download_ohlc(config_path=config_path, mt5_module=mt5)

    assert report["status"] == "GO"
    assert report["summary"]["jobs"] == 4
    assert report["summary"]["downloaded"] == 4
    assert (output_dir / "EURUSD_H1.csv").is_file()
    assert "time,open,high,low,close,volume" in (output_dir / "EURUSD_H1.csv").read_text(encoding="utf-8")
    assert (coverage_dir / "a58_dukas_mt5_download.json").is_file()
    assert (coverage_dir / "a58_dukas_mt5_download.md").is_file()
    assert mt5.shutdown_called


def test_dukas_download_reports_missing_symbol_no_go(tmp_path):
    tool = load_module()
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "ohlc"
    coverage_dir = tmp_path / "coverage"
    write_config(config_path, output_dir, coverage_dir)

    report = tool.download_ohlc(config_path=config_path, mt5_module=FakeMT5(known_symbols={"EURUSD"}))

    assert report["status"] == "NO_GO"
    assert report["summary"]["missingSymbols"] == 1
    assert any(record["status"] == "missing_symbol" for record in report["coverage"])
    assert any("MT5 symbol not found" in failure for failure in report["failures"])


def test_dukas_download_skips_existing_large_csv(tmp_path):
    tool = load_module()
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "ohlc"
    coverage_dir = tmp_path / "coverage"
    write_config(config_path, output_dir, coverage_dir, timeframes=["H1"], symbolMap={"EURUSD": "EURUSD"}, skipExistingMinKb=0.001)
    existing = output_dir / "EURUSD_H1.csv"
    existing.parent.mkdir(parents=True)
    existing.write_text("time,open,high,low,close,volume\n" + ("x,1,2,0,1,1\n" * 50), encoding="utf-8")

    report = tool.download_ohlc(config_path=config_path, mt5_module=FakeMT5())

    assert report["status"] == "GO"
    assert report["summary"]["skippedExisting"] == 1
    assert report["coverage"][0]["status"] == "skipped_existing"


def test_dukas_download_dry_run_does_not_require_mt5(tmp_path):
    tool = load_module()
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "ohlc"
    coverage_dir = tmp_path / "coverage"
    write_config(config_path, output_dir, coverage_dir, timeframes=["H4"], symbolMap={"US500": "USA500.IDX"})

    report = tool.download_ohlc(config_path=config_path, dry_run=True)

    assert report["status"] == "GO"
    assert report["coverage"][0]["status"] == "dry_run"
    assert report["coverage"][0]["path"].endswith("US500_H4.csv")


def test_dukas_download_can_use_active_terminal_without_path(tmp_path):
    tool = load_module()
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "ohlc"
    coverage_dir = tmp_path / "coverage"
    write_config(config_path, output_dir, coverage_dir, timeframes=["H1"], symbolMap={"EURUSD": "EURUSD"}, initializeTimeoutMs=90000)
    mt5 = FakeMT5()

    report = tool.download_ohlc(config_path=config_path, mt5_module=mt5, use_active_terminal=True)

    assert report["status"] == "GO"
    assert report["metadata"]["initializeMode"] == "active_terminal"
    assert report["metadata"]["terminalPath"] == ""
    assert report["metadata"]["initializeTimeoutMs"] == 90000
    assert mt5.initialized_path is None
    assert mt5.initialized_timeout == 90000


def test_dukas_download_can_fetch_recent_bars_from_position(tmp_path):
    tool = load_module()
    config_path = tmp_path / "config.json"
    output_dir = tmp_path / "ohlc"
    coverage_dir = tmp_path / "coverage"
    write_config(config_path, output_dir, coverage_dir, timeframes=["H1"], symbolMap={"EURUSD": "EURUSD"}, minimumBars=5)
    mt5 = FakeMT5()

    report = tool.download_ohlc(config_path=config_path, mt5_module=mt5, recent_bars=12)

    assert report["status"] == "GO"
    assert report["metadata"]["downloadMode"] == "recent_bars"
    assert report["metadata"]["recentBars"] == 12
    assert report["coverage"][0]["bars"] == 12
    assert mt5.from_pos_calls == [("EURUSD", "H1", 0, 12)]


def test_rows_from_rates_accepts_numpy_like_rates():
    tool = load_module()
    rates = AmbiguousRates(
        [
            {
                "time": 1704067200,
                "open": 1.1,
                "high": 1.2,
                "low": 1.0,
                "close": 1.15,
                "tick_volume": 100,
            }
        ]
    )

    rows = tool.rows_from_rates(rates)

    assert rows[0]["time"] == "2024-01-01T00:00:00"
    assert rows[0]["volume"] == 100
