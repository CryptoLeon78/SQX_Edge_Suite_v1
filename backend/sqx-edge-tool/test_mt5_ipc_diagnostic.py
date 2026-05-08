from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "mt5_ipc_diagnostic.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mt5_ipc_diagnostic", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeInfo:
    company = "MetaQuotes"
    name = "Fake MT5"
    login = 123456


class FakeMT5:
    __version__ = "5.0.test"

    def __init__(self, ok: bool):
        self.ok = ok
        self.calls = []
        self.shutdown_called = False

    def initialize(self, **kwargs):
        self.calls.append(kwargs)
        return self.ok

    def last_error(self):
        return (0, "ok") if self.ok else (-10005, "IPC timeout")

    def terminal_info(self):
        return FakeInfo()

    def account_info(self):
        return FakeInfo()

    def shutdown(self):
        self.shutdown_called = True


def write_config(path: Path, terminal_path: str = "C:/fake/terminal64.exe"):
    path.write_text(
        json.dumps(
            {
                "terminalPath": terminal_path,
                "initializeTimeoutMs": 12345,
            }
        ),
        encoding="utf-8",
    )


def test_mt5_ipc_diagnostic_returns_go_when_variant_connects(tmp_path, monkeypatch):
    tool = load_module()
    config = tmp_path / "config.json"
    out_dir = tmp_path / "out"
    write_config(config)
    monkeypatch.setattr(tool, "collect_terminal_processes", lambda: [{"ProcessName": "terminal64"}])
    mt5 = FakeMT5(ok=True)

    report = tool.run_diagnostic(config_path=config, output_dir=out_dir, mt5_module=mt5)

    assert report["status"] == "GO"
    assert report["python"]["mt5PackageVersion"] == "5.0.test"
    assert report["initializeVariants"][0]["name"] == "configured_path"
    assert report["initializeVariants"][0]["ok"] is True
    assert mt5.calls[0]["timeout"] == 12345
    assert mt5.shutdown_called
    assert (out_dir / "a61_mt5_ipc_diagnostic.json").is_file()
    assert "# SQX A61 MT5 IPC Diagnostic" in (out_dir / "a61_mt5_ipc_diagnostic.md").read_text(encoding="utf-8")


def test_mt5_ipc_diagnostic_returns_no_go_for_ipc_timeout(tmp_path, monkeypatch):
    tool = load_module()
    config = tmp_path / "config.json"
    out_dir = tmp_path / "out"
    write_config(config, terminal_path="")
    monkeypatch.setattr(tool, "collect_terminal_processes", lambda: [{"ProcessName": "terminal64", "Responding": True}])

    report = tool.run_diagnostic(config_path=config, output_dir=out_dir, mt5_module=FakeMT5(ok=False), timeout_ms=5000)

    assert report["status"] == "NO_GO"
    assert "Python IPC is not available" in report["decision"]
    assert report["initializeVariants"][0]["name"] == "active_terminal"
    assert report["initializeVariants"][0]["lastError"] == (-10005, "IPC timeout")
