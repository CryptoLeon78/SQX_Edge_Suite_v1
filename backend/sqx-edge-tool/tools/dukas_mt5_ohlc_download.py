"""
Internal A58 MT5/Dukascopy OHLC download gate.

This operator-only tool downloads reviewable OHLC CSV files for the A55/A56
real-data pipeline. It intentionally keeps the MetaTrader5 dependency optional
and out of portable buyer builds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "dukas_mt5_download.json"

TIMEFRAME_ATTRS = {
    "M5": "TIMEFRAME_M5",
    "M15": "TIMEFRAME_M15",
    "M30": "TIMEFRAME_M30",
    "H1": "TIMEFRAME_H1",
    "H4": "TIMEFRAME_H4",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def parse_date(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("date cannot be empty")
    return datetime.fromisoformat(text)


def utc_iso_from_timestamp(value: Any) -> str:
    return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(tzinfo=None).isoformat()


def normalize_timeframe(value: str) -> str:
    tf = str(value or "").strip().upper()
    if tf not in TIMEFRAME_ATTRS:
        raise ValueError(f"unsupported timeframe: {value}")
    return tf


def select_timeframes(config: dict[str, Any], cli_timeframes: list[str] | None = None) -> list[str]:
    source = cli_timeframes if cli_timeframes else config.get("timeframes", [])
    timeframes: list[str] = []
    for raw in source:
        tf = normalize_timeframe(raw)
        if tf not in timeframes:
            timeframes.append(tf)
    if not timeframes:
        raise ValueError("at least one timeframe is required")
    return timeframes


def select_assets(config: dict[str, Any], cli_assets: list[str] | None = None) -> dict[str, str]:
    symbol_map = {str(key).upper(): str(value) for key, value in config.get("symbolMap", {}).items()}
    if not symbol_map:
        raise ValueError("symbolMap cannot be empty")
    if not cli_assets:
        return symbol_map
    selected: dict[str, str] = {}
    for raw in cli_assets:
        asset = str(raw or "").strip().upper()
        if not asset:
            continue
        if asset not in symbol_map:
            raise ValueError(f"asset is not configured: {asset}")
        selected[asset] = symbol_map[asset]
    if not selected:
        raise ValueError("at least one asset is required")
    return selected


def import_mt5_module() -> Any:
    return importlib.import_module("MetaTrader5")


def timeframe_code(mt5: Any, tf: str) -> Any:
    attr = TIMEFRAME_ATTRS[tf]
    if not hasattr(mt5, attr):
        raise ValueError(f"MetaTrader5 module does not expose {attr}")
    return getattr(mt5, attr)


def get_row_value(row: Any, key: str) -> Any:
    if isinstance(row, dict):
        return row.get(key)
    try:
        return row[key]
    except (KeyError, TypeError, IndexError, ValueError):
        return getattr(row, key, None)


def rows_from_rates(rates: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if rates is None:
        return rows
    for row in rates:
        timestamp = get_row_value(row, "time")
        volume = get_row_value(row, "tick_volume")
        if volume is None:
            volume = get_row_value(row, "real_volume")
        rows.append(
            {
                "time": utc_iso_from_timestamp(timestamp),
                "open": get_row_value(row, "open"),
                "high": get_row_value(row, "high"),
                "low": get_row_value(row, "low"),
                "close": get_row_value(row, "close"),
                "volume": volume if volume is not None else 0,
            }
        )
    return rows


def write_ohlc_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_with_retry(
    mt5: Any,
    symbol: str,
    tf_code: Any,
    start: datetime,
    end: datetime,
    retries: int,
    delay_seconds: float,
) -> tuple[Any, int]:
    attempts = max(1, int(retries))
    for attempt in range(1, attempts + 1):
        rates = mt5.copy_rates_range(symbol, tf_code, start, end)
        if rates is not None and len(rates) > 0:
            return rates, attempt
        if attempt < attempts and delay_seconds > 0:
            time.sleep(delay_seconds)
    return rates, attempts


def build_record(
    *,
    asset: str,
    symbol: str,
    timeframe: str,
    status: str,
    bars: int = 0,
    attempts: int = 0,
    path: Path | None = None,
    message: str = "",
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "asset": asset,
        "symbol": symbol,
        "timeframe": timeframe,
        "status": status,
        "bars": bars,
        "attempts": attempts,
    }
    if message:
        record["message"] = message
    if path:
        record["path"] = str(path)
        if path.exists():
            record["fileSizeBytes"] = path.stat().st_size
            record["sha256"] = file_sha256(path)
    return record


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SQX A58 Dukascopy MT5 OHLC Download",
        "",
        f"Status: {report['status']}",
        f"Generated: {report['metadata']['generatedAt']}",
        f"Output: `{report['metadata']['outputDir']}`",
        f"Coverage: `{report['metadata']['coverageDir']}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- {key}: {value}")
    if report["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in report["failures"]:
            lines.append(f"- {failure}")
    lines.extend(["", "## Coverage", "", "| Asset | TF | Symbol | Status | Bars | File |", "| --- | --- | --- | --- | ---: | --- |"])
    for record in report["coverage"]:
        lines.append(
            "| {asset} | {timeframe} | {symbol} | {status} | {bars} | {path} |".format(
                asset=record["asset"],
                timeframe=record["timeframe"],
                symbol=record["symbol"],
                status=record["status"],
                bars=record.get("bars", 0),
                path=record.get("path", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_coverage_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["asset", "symbol", "timeframe", "status", "bars", "attempts", "path", "fileSizeBytes", "sha256", "message"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def persist_report(report: dict[str, Any], coverage_dir: Path) -> dict[str, str]:
    coverage_dir.mkdir(parents=True, exist_ok=True)
    json_path = coverage_dir / "a58_dukas_mt5_download.json"
    md_path = coverage_dir / "a58_dukas_mt5_download.md"
    csv_path = coverage_dir / "a58_dukas_mt5_download_coverage.csv"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    write_coverage_csv(csv_path, report["coverage"])
    return {"coverageJson": str(json_path), "coverageMarkdown": str(md_path), "coverageCsv": str(csv_path)}


def base_report(config: dict[str, Any], output_dir: Path, coverage_dir: Path, timeframes: list[str]) -> dict[str, Any]:
    return {
        "metadata": {
            "phase": config.get("phase", "A58"),
            "state": config.get("state", "dukas_mt5_ohlc_download_gate_ready"),
            "mode": config.get("mode", "internal_operator_optional"),
            "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "terminalPath": config.get("terminalPath", ""),
            "outputDir": str(output_dir),
            "coverageDir": str(coverage_dir),
            "startDate": config.get("startDate"),
            "endDate": config.get("endDate"),
            "timeframes": timeframes,
            "nextAction": config.get("nextPhase", ""),
        },
        "status": "NO_GO",
        "summary": {},
        "coverage": [],
        "failures": [],
        "outputs": {},
    }


def complete_summary(report: dict[str, Any], assets_requested: int, assets_activated: int, missing_symbols: int) -> None:
    records = report["coverage"]
    failed = [item for item in records if item["status"] not in {"downloaded", "skipped_existing"}]
    report["summary"] = {
        "assetsRequested": assets_requested,
        "assetsActivated": assets_activated,
        "missingSymbols": missing_symbols,
        "jobs": len(records),
        "downloaded": sum(1 for item in records if item["status"] == "downloaded"),
        "skippedExisting": sum(1 for item in records if item["status"] == "skipped_existing"),
        "failed": len(failed),
        "totalBars": sum(int(item.get("bars", 0) or 0) for item in records),
    }
    report["status"] = "GO" if records and not failed and missing_symbols == 0 else "NO_GO"


def download_ohlc(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    terminal_path: str | None = None,
    output_dir: str | Path | None = None,
    coverage_dir: str | Path | None = None,
    timeframes: list[str] | None = None,
    assets: list[str] | None = None,
    mt5_module: Any | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    config = read_json(config_path)
    selected_timeframes = select_timeframes(config, timeframes)
    selected_assets = select_assets(config, assets)
    out_dir = resolve_project_path(output_dir or config["outputDir"])
    cov_dir = resolve_project_path(coverage_dir or config["coverageDir"])
    report = base_report(config, out_dir, cov_dir, selected_timeframes)
    terminal = terminal_path or config.get("terminalPath", "")
    report["metadata"]["terminalPath"] = str(terminal)

    if dry_run:
        for asset, symbol in selected_assets.items():
            for tf in selected_timeframes:
                path = out_dir / f"{asset}_{tf}.csv"
                report["coverage"].append(build_record(asset=asset, symbol=symbol, timeframe=tf, status="dry_run", path=path))
        report["summary"] = {
            "assetsRequested": len(selected_assets),
            "assetsActivated": 0,
            "missingSymbols": 0,
            "jobs": len(report["coverage"]),
            "downloaded": 0,
            "skippedExisting": 0,
            "failed": 0,
            "totalBars": 0,
        }
        report["status"] = "GO"
        report["outputs"] = persist_report(report, cov_dir)
        return report

    try:
        mt5 = mt5_module if mt5_module is not None else import_mt5_module()
    except ImportError as exc:
        report["failures"].append(f"MetaTrader5 dependency is not installed: {exc}")
        complete_summary(report, len(selected_assets), 0, len(selected_assets))
        report["outputs"] = persist_report(report, cov_dir)
        return report

    start = parse_date(config["startDate"])
    end = parse_date(config["endDate"])
    min_bars = int(config.get("minimumBars", 120))
    retries = int(config.get("retryCount", 3))
    retry_delay = float(config.get("retryDelaySeconds", 4.0))
    skip_existing_bytes = int(float(config.get("skipExistingMinKb", 50)) * 1024)
    activated: dict[str, str] = {}
    missing_symbols = 0
    initialized = False

    try:
        initialized = bool(mt5.initialize(path=str(terminal))) if terminal else bool(mt5.initialize())
        if not initialized:
            last_error = mt5.last_error() if hasattr(mt5, "last_error") else "unknown"
            report["failures"].append(f"MT5 initialize failed: {last_error}")
            complete_summary(report, len(selected_assets), 0, len(selected_assets))
            report["outputs"] = persist_report(report, cov_dir)
            return report

        for asset, symbol in selected_assets.items():
            if hasattr(mt5, "symbol_info") and mt5.symbol_info(symbol) is None:
                missing_symbols += 1
                report["failures"].append(f"{asset}: MT5 symbol not found: {symbol}")
                for tf in selected_timeframes:
                    report["coverage"].append(
                        build_record(asset=asset, symbol=symbol, timeframe=tf, status="missing_symbol", message="MT5 symbol not found")
                    )
                continue
            if hasattr(mt5, "symbol_select") and not mt5.symbol_select(symbol, True):
                missing_symbols += 1
                report["failures"].append(f"{asset}: MT5 symbol could not be selected: {symbol}")
                for tf in selected_timeframes:
                    report["coverage"].append(
                        build_record(asset=asset, symbol=symbol, timeframe=tf, status="symbol_select_failed", message="MT5 symbol_select failed")
                    )
                continue
            activated[asset] = symbol

        startup_delay = float(config.get("startupDelaySeconds", 8))
        if startup_delay > 0 and activated:
            time.sleep(startup_delay)

        for asset, symbol in activated.items():
            for tf in selected_timeframes:
                path = out_dir / f"{asset}_{tf}.csv"
                if path.exists() and path.stat().st_size >= skip_existing_bytes and not force:
                    report["coverage"].append(
                        build_record(asset=asset, symbol=symbol, timeframe=tf, status="skipped_existing", path=path)
                    )
                    continue
                tf_code = timeframe_code(mt5, tf)
                rates, attempts = fetch_with_retry(mt5, symbol, tf_code, start, end, retries, retry_delay)
                bars = len(rates) if rates is not None else 0
                if rates is None or bars == 0:
                    message = "no bars returned"
                    report["failures"].append(f"{asset}_{tf}: {message}")
                    report["coverage"].append(
                        build_record(asset=asset, symbol=symbol, timeframe=tf, status="no_data", bars=bars, attempts=attempts, message=message)
                    )
                    continue
                if bars < min_bars:
                    message = f"bars below minimum {min_bars}"
                    report["failures"].append(f"{asset}_{tf}: {message}")
                    report["coverage"].append(
                        build_record(asset=asset, symbol=symbol, timeframe=tf, status="too_few_bars", bars=bars, attempts=attempts, message=message)
                    )
                    continue
                rows = rows_from_rates(rates)
                write_ohlc_csv(path, rows)
                report["coverage"].append(
                    build_record(asset=asset, symbol=symbol, timeframe=tf, status="downloaded", bars=bars, attempts=attempts, path=path)
                )
    finally:
        if initialized and hasattr(mt5, "shutdown"):
            mt5.shutdown()

    complete_summary(report, len(selected_assets), len(activated), missing_symbols)
    report["outputs"] = persist_report(report, cov_dir)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download MT5/Dukascopy OHLC CSVs for the SQX A56 real-data pipeline.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--terminal-path", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--coverage-dir", default=None)
    parser.add_argument("--tf", action="append", dest="timeframes", help="Timeframe to download. Repeatable.")
    parser.add_argument("--asset", action="append", dest="assets", help="Asset id to download. Repeatable.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = download_ohlc(
        config_path=Path(args.config),
        terminal_path=args.terminal_path,
        output_dir=args.output_dir,
        coverage_dir=args.coverage_dir,
        timeframes=args.timeframes,
        assets=args.assets,
        dry_run=args.dry_run,
        force=args.force,
    )
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print(render_markdown(report))
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
