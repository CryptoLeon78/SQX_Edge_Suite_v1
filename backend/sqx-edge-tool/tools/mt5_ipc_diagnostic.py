"""
A61 internal MT5 IPC diagnostic.

Runs quick, traceable MetaTrader5 initialization variants before attempting a
full OHLC download. This stays operator-only and is excluded from buyer builds.
"""
from __future__ import annotations

import argparse
import importlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG_PATH = TOOL_ROOT / "config" / "dukas_mt5_download.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "analysis_output" / "mt5_ipc_diagnostic"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def import_mt5_module() -> Any:
    return importlib.import_module("MetaTrader5")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def collect_python_info(mt5: Any | None = None) -> dict[str, Any]:
    return {
        "python": sys.executable,
        "pythonVersion": sys.version.split()[0],
        "architecture": platform.architecture()[0],
        "platform": platform.platform(),
        "mt5PackageVersion": getattr(mt5, "__version__", None) if mt5 is not None else None,
    }


def collect_terminal_processes() -> list[dict[str, Any]]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Process | Where-Object { $_.ProcessName -eq 'terminal64' } | "
        "Select-Object ProcessName,Id,Responding,MainWindowTitle,Path,StartTime | ConvertTo-Json -Compress",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
    except Exception as exc:
        return [{"status": "error", "message": repr(exc)}]
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [{"status": "parse_error", "raw": result.stdout.strip()}]
    if isinstance(data, dict):
        data = [data]
    return data


def run_initialize_variant(mt5: Any, name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    try:
        ok = bool(mt5.initialize(**kwargs))
        last_error = mt5.last_error() if hasattr(mt5, "last_error") else None
        terminal_info = mt5.terminal_info() if ok and hasattr(mt5, "terminal_info") else None
        account_info = mt5.account_info() if ok and hasattr(mt5, "account_info") else None
    except Exception as exc:
        ok = False
        last_error = repr(exc)
        terminal_info = None
        account_info = None
    finally:
        if "ok" in locals() and ok and hasattr(mt5, "shutdown"):
            mt5.shutdown()
    return {
        "name": name,
        "ok": ok,
        "elapsedSeconds": round(time.time() - started, 2),
        "lastError": last_error,
        "terminalInfoPresent": terminal_info is not None,
        "accountInfoPresent": account_info is not None,
        "terminalCompany": getattr(terminal_info, "company", None) if terminal_info else None,
        "terminalName": getattr(terminal_info, "name", None) if terminal_info else None,
        "accountLoginPresent": getattr(account_info, "login", None) is not None if account_info else False,
    }


def build_variants(terminal_path: str, timeout_ms: int) -> list[tuple[str, dict[str, Any]]]:
    variants: list[tuple[str, dict[str, Any]]] = [
        ("active_terminal", {"timeout": timeout_ms}),
    ]
    if terminal_path:
        variants.insert(0, ("configured_path", {"path": terminal_path, "timeout": timeout_ms}))
        variants.append(("configured_path_portable", {"path": terminal_path, "portable": True, "timeout": timeout_ms}))
    return variants


def classify(report: dict[str, Any]) -> None:
    successes = [item for item in report["initializeVariants"] if item.get("ok")]
    if successes:
        report["status"] = "GO"
        report["decision"] = "MT5 IPC is available. Proceed with A58 smoke download for EURUSD/H1."
        return
    report["status"] = "NO_GO"
    timeout_errors = [item for item in report["initializeVariants"] if "-10005" in str(item.get("lastError")) or "IPC timeout" in str(item.get("lastError"))]
    if timeout_errors:
        report["decision"] = (
            "MT5 process exists but Python IPC is not available. Check terminal login, Market Watch, modal dialogs, "
            "Algo Trading/Python permissions and privilege level before rerunning."
        )
    else:
        report["decision"] = "MT5 IPC did not initialize. Review variant errors before rerunning A58."


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SQX A61 MT5 IPC Diagnostic",
        "",
        f"Status: {report['status']}",
        f"Generated: {report['metadata']['generatedAt']}",
        f"Terminal path: `{report['metadata']['terminalPath']}`",
        "",
        "## Decision",
        "",
        report["decision"],
        "",
        "## Python",
        "",
    ]
    for key, value in report["python"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Terminal Processes", ""])
    if report["terminalProcesses"]:
        for process in report["terminalProcesses"]:
            lines.append(f"- {process}")
    else:
        lines.append("- none")
    lines.extend(["", "## Initialize Variants", "", "| Variant | OK | Seconds | Last Error |", "| --- | --- | ---: | --- |"])
    for item in report["initializeVariants"]:
        lines.append(f"| {item['name']} | {item['ok']} | {item['elapsedSeconds']} | {item.get('lastError')} |")
    lines.extend(
        [
            "",
            "## Next",
            "",
            "- If status is GO, run the A58 `EURUSD/H1` smoke.",
            "- If status is NO_GO with IPC timeout, fix the local terminal session before any full OHLC download.",
            "",
        ]
    )
    return "\n".join(lines)


def persist_report(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "a61_mt5_ipc_diagnostic.json"
    md_path = output_dir / "a61_mt5_ipc_diagnostic.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def run_diagnostic(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    terminal_path: str | None = None,
    timeout_ms: int | None = None,
    mt5_module: Any | None = None,
) -> dict[str, Any]:
    config = read_json(config_path)
    terminal = terminal_path if terminal_path is not None else str(config.get("terminalPath", ""))
    timeout = int(timeout_ms if timeout_ms is not None else config.get("initializeTimeoutMs", 10000))
    out_dir = resolve_project_path(output_dir)
    report: dict[str, Any] = {
        "metadata": {
            "phase": "A61",
            "generatedAt": now_utc(),
            "terminalPath": terminal,
            "timeoutMs": timeout,
            "outputDir": str(out_dir),
        },
        "status": "NO_GO",
        "decision": "",
        "python": {},
        "terminalProcesses": collect_terminal_processes(),
        "initializeVariants": [],
        "outputs": {},
    }
    try:
        mt5 = mt5_module if mt5_module is not None else import_mt5_module()
    except ImportError as exc:
        report["python"] = collect_python_info(None)
        report["decision"] = f"MetaTrader5 dependency is not installed: {exc}"
        report["outputs"] = persist_report(report, out_dir)
        return report

    report["python"] = collect_python_info(mt5)
    for name, kwargs in build_variants(terminal, timeout):
        report["initializeVariants"].append(run_initialize_variant(mt5, name, kwargs))
    classify(report)
    report["outputs"] = persist_report(report, out_dir)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose MetaTrader5 Python IPC readiness before SQX OHLC download.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--terminal-path", default=None)
    parser.add_argument("--timeout-ms", type=int, default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_diagnostic(
        config_path=Path(args.config),
        output_dir=args.output_dir,
        terminal_path=args.terminal_path,
        timeout_ms=args.timeout_ms,
    )
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print(render_markdown(report))
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
