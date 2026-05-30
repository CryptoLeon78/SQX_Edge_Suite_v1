from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VERSION = "sqx142-mining-results-registry-v1"
DEFAULT_DB = Path(".local") / "sqx142_mining_registry" / "sqx142_mining_registry.sqlite"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def detect_delimiter(path: Path) -> str:
    first_line = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[0]
    if first_line.count(";") >= first_line.count(","):
        return ";"
    return ","


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], str, list[str]]:
    delimiter = detect_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = [{str(k): ("" if v is None else str(v)) for k, v in row.items()} for row in reader]
        columns = [str(column) for column in (reader.fieldnames or [])]
    return rows, delimiter, columns


def parse_decimal(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("$", "").replace("%", "").replace(" ", "")
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: Any) -> int | None:
    number = parse_decimal(value)
    if number is None:
        return None
    return int(round(number))


def normalize_identifier(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    return clean or "unknown"


def infer_from_rows(rows: list[dict[str, str]], column: str, fallback: str = "") -> str:
    for row in rows:
        value = (row.get(column) or "").strip()
        if value:
            return value
    return fallback


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS registry_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS mining_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_key TEXT NOT NULL UNIQUE,
            version TEXT NOT NULL,
            source_type TEXT NOT NULL,
            project_name TEXT NOT NULL,
            sqx_project_name TEXT NOT NULL,
            asset TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            layer TEXT NOT NULL,
            blocksetting_family TEXT NOT NULL,
            direction TEXT NOT NULL,
            databank TEXT NOT NULL,
            sqx_profile TEXT NOT NULL,
            source_csv_sha256 TEXT,
            tagger_csv_sha256 TEXT,
            source_csv_rows INTEGER NOT NULL DEFAULT 0,
            tagger_csv_rows INTEGER NOT NULL DEFAULT 0,
            spread_base REAL,
            mc2_spread_min REAL,
            mc2_spread_max REAL,
            run_flags_json TEXT NOT NULL,
            data_smoke_json TEXT NOT NULL,
            operator_note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS custom_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_key TEXT NOT NULL UNIQUE,
            run_id INTEGER,
            project_name TEXT NOT NULL,
            sqx_project_name TEXT NOT NULL,
            asset TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            layer TEXT NOT NULL,
            blocksetting_family TEXT NOT NULL,
            direction TEXT NOT NULL,
            sqx_profile TEXT NOT NULL,
            trace_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES mining_runs(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS custom_project_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            step_order INTEGER NOT NULL,
            step_key TEXT NOT NULL,
            step_label TEXT NOT NULL,
            status TEXT NOT NULL,
            input_databank TEXT NOT NULL,
            output_databank TEXT NOT NULL,
            row_count INTEGER,
            passed_count INTEGER,
            failed_count INTEGER,
            details_json TEXT NOT NULL,
            evidence_note TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            UNIQUE(project_id, step_key),
            FOREIGN KEY(project_id) REFERENCES custom_projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS databank_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            run_id INTEGER,
            databank TEXT NOT NULL,
            stage_key TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            passed_count INTEGER NOT NULL,
            failed_count INTEGER NOT NULL,
            portfolio_count INTEGER NOT NULL DEFAULT 0,
            similar_count INTEGER NOT NULL DEFAULT 0,
            review_count INTEGER NOT NULL DEFAULT 0,
            best_strategy_name TEXT NOT NULL,
            best_profit_factor REAL,
            best_ret_dd_ratio REAL,
            best_max_dd_pct REAL,
            best_trades INTEGER,
            metrics_json TEXT NOT NULL,
            source_kind TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            UNIQUE(project_id, databank, stage_key),
            FOREIGN KEY(project_id) REFERENCES custom_projects(id) ON DELETE CASCADE,
            FOREIGN KEY(run_id) REFERENCES mining_runs(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            run_id INTEGER,
            test_key TEXT NOT NULL,
            test_label TEXT NOT NULL,
            status TEXT NOT NULL,
            input_databank TEXT NOT NULL,
            output_databank TEXT NOT NULL,
            rows_in INTEGER,
            rows_out INTEGER,
            passed_count INTEGER,
            failed_count INTEGER,
            metrics_json TEXT NOT NULL,
            evidence_note TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            UNIQUE(project_id, test_key),
            FOREIGN KEY(project_id) REFERENCES custom_projects(id) ON DELETE CASCADE,
            FOREIGN KEY(run_id) REFERENCES mining_runs(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS mining_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            file_name TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            byte_size INTEGER NOT NULL,
            row_count INTEGER NOT NULL,
            delimiter TEXT NOT NULL,
            columns_json TEXT NOT NULL,
            path_redacted INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            UNIQUE(run_id, kind),
            FOREIGN KEY(run_id) REFERENCES mining_runs(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS mining_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            event_note TEXT NOT NULL,
            event_at TEXT NOT NULL,
            FOREIGN KEY(run_id) REFERENCES mining_runs(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS strategy_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            stage TEXT NOT NULL,
            row_index INTEGER NOT NULL,
            strategy_name TEXT NOT NULL,
            filters_result TEXT NOT NULL,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            fitness REAL,
            profit_factor REAL,
            ret_dd_ratio REAL,
            max_dd_pct REAL,
            trades INTEGER,
            corr_decision INTEGER,
            corr_rank INTEGER,
            corr_score REAL,
            corr_max REAL,
            corr_status INTEGER,
            nearest_winner TEXT NOT NULL,
            entry_indicators TEXT NOT NULL,
            exit_indicators TEXT NOT NULL,
            price_indicators TEXT NOT NULL,
            raw_json TEXT NOT NULL,
            UNIQUE(run_id, stage, row_index),
            FOREIGN KEY(run_id) REFERENCES mining_runs(id) ON DELETE CASCADE
        );
        """
    )
    con.execute("INSERT OR REPLACE INTO registry_meta(key, value) VALUES(?, ?)", ("schemaVersion", VERSION))
    con.commit()
    return con


def csv_file_record(path: Path, kind: str) -> dict[str, Any]:
    rows, delimiter, columns = read_csv_rows(path)
    return {
        "kind": kind,
        "file_name": path.name,
        "sha256": sha256_file(path),
        "byte_size": path.stat().st_size,
        "row_count": len(rows),
        "delimiter": delimiter,
        "columns": columns,
        "rows": rows,
    }


def row_value(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row:
            return row.get(name) or ""
    return ""


def insert_strategy_rows(con: sqlite3.Connection, run_id: int, stage: str, rows: list[dict[str, str]]) -> None:
    con.execute("DELETE FROM strategy_results WHERE run_id = ? AND stage = ?", (run_id, stage))
    for index, row in enumerate(rows, start=1):
        con.execute(
            """
            INSERT INTO strategy_results(
                run_id, stage, row_index, strategy_name, filters_result, symbol, timeframe,
                fitness, profit_factor, ret_dd_ratio, max_dd_pct, trades,
                corr_decision, corr_rank, corr_score, corr_max, corr_status, nearest_winner,
                entry_indicators, exit_indicators, price_indicators, raw_json
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                stage,
                index,
                row_value(row, "Strategy Name"),
                row_value(row, "Filters result"),
                row_value(row, "Symbol"),
                row_value(row, "TimeFrame"),
                parse_decimal(row_value(row, "Fitness")),
                parse_decimal(row_value(row, "Profit factor")),
                parse_decimal(row_value(row, "Ret/DD Ratio")),
                parse_decimal(row_value(row, "Max DD %")),
                parse_int(row_value(row, "# of trades")),
                parse_int(row_value(row, "SQX Edge Corr Decision")),
                parse_int(row_value(row, "SQX Edge Corr Rank")),
                parse_decimal(row_value(row, "SQX Edge Corr Score")),
                parse_decimal(row_value(row, "SQX Edge Max Corr")),
                parse_int(row_value(row, "SQX Edge Corr Status")),
                row_value(row, "SQX Edge Nearest Winner"),
                row_value(row, "Entry indicators"),
                row_value(row, "Exit indicators"),
                row_value(row, "Price indicators"),
                safe_json(row),
            ),
        )


def summarize_stage(rows: list[dict[str, str]]) -> dict[str, Any]:
    decisions = [parse_int(row_value(row, "SQX Edge Corr Decision")) for row in rows]
    ranks = [parse_int(row_value(row, "SQX Edge Corr Rank")) for row in rows]
    statuses = [parse_int(row_value(row, "SQX Edge Corr Status")) for row in rows]
    return {
        "rows": len(rows),
        "passed": sum(1 for row in rows if row_value(row, "Filters result").upper() == "PASSED"),
        "portfolio": sum(1 for value in decisions if value == 1),
        "similar": sum(1 for value in decisions if value == 0),
        "untagged": sum(1 for value in decisions if value == -1),
        "ranked": sum(1 for value in ranks if value and value > 0),
        "status_ok": sum(1 for value in statuses if value == 1),
    }


def best_strategy(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {}

    def score(row: dict[str, str]) -> tuple[float, float, float]:
        return (
            parse_decimal(row_value(row, "Profit factor")) or 0.0,
            parse_decimal(row_value(row, "Ret/DD Ratio")) or 0.0,
            -1 * (parse_decimal(row_value(row, "Max DD %")) or 999.0),
        )

    row = sorted(rows, key=score, reverse=True)[0]
    return {
        "strategy_name": row_value(row, "Strategy Name"),
        "profit_factor": parse_decimal(row_value(row, "Profit factor")),
        "ret_dd_ratio": parse_decimal(row_value(row, "Ret/DD Ratio")),
        "max_dd_pct": parse_decimal(row_value(row, "Max DD %")),
        "trades": parse_int(row_value(row, "# of trades")),
    }


def upsert_project_trace(
    con: sqlite3.Connection,
    *,
    run_id: int,
    args: argparse.Namespace,
    project_name: str,
    sqx_project_name: str,
    asset: str,
    symbol: str,
    timeframe: str,
    source_summary: dict[str, Any],
    tagger_summary: dict[str, Any],
    tagger_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    now: str,
) -> int:
    project_key = args.project_key or args.run_key
    trace = {
        "version": VERSION,
        "customProjectTrace": True,
        "sourceType": args.source_type,
        "runKey": args.run_key,
        "projectKey": project_key,
        "databank": args.databank,
        "spread": {
            "base": args.spread_base,
            "mc2Min": args.mc2_spread_min,
            "mc2Max": args.mc2_spread_max,
        },
        "guards": {
            "sqx_data_db_written": False,
            "sqx_jars_patched": False,
            "sqx_runtime_started": False,
            "raw_local_paths_returned": False,
        },
    }
    con.execute(
        """
        INSERT INTO custom_projects(
            project_key, run_id, project_name, sqx_project_name, asset, symbol,
            timeframe, layer, blocksetting_family, direction, sqx_profile,
            trace_json, created_at, updated_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_key) DO UPDATE SET
            run_id=excluded.run_id,
            project_name=excluded.project_name,
            sqx_project_name=excluded.sqx_project_name,
            asset=excluded.asset,
            symbol=excluded.symbol,
            timeframe=excluded.timeframe,
            layer=excluded.layer,
            blocksetting_family=excluded.blocksetting_family,
            direction=excluded.direction,
            sqx_profile=excluded.sqx_profile,
            trace_json=excluded.trace_json,
            updated_at=excluded.updated_at
        """,
        (
            project_key,
            run_id,
            project_name,
            sqx_project_name,
            asset or "",
            symbol or "",
            timeframe or "",
            args.layer,
            args.blocksetting_family,
            args.direction,
            args.sqx_profile,
            safe_json(trace),
            now,
            now,
        ),
    )
    project_id = int(con.execute("SELECT id FROM custom_projects WHERE project_key = ?", (project_key,)).fetchone()["id"])

    con.execute("DELETE FROM custom_project_steps WHERE project_id = ?", (project_id,))
    step_rows = [
        (1, "custom_load", "Custom project loaded in SQX", "passed" if args.sqx_clean_load and args.sqx_no_red else "unknown", "", "Results", None, None, None, {"no_red": bool(args.sqx_no_red)}, "Manual/SQX UI confirmation."),
        (2, "mining_retest", "Mining/retest generated data", "passed" if args.fresh_mining_run else "unknown", "Results", args.databank, source_summary["rows"], source_summary["passed"], max(0, source_summary["rows"] - source_summary["passed"]), {"fresh_mining_run": bool(args.fresh_mining_run)}, "Real test mining/retest run."),
        (3, "data_smoke", "Correlation Data Smoke built decisions", "passed" if tagger_summary["portfolio"] + tagger_summary["similar"] > 0 else "unknown", args.databank, "correlation_decisions.csv", source_summary["rows"], tagger_summary["portfolio"] + tagger_summary["similar"], tagger_summary["untagged"], {"portfolio": tagger_summary["portfolio"], "similar": tagger_summary["similar"]}, "Data Smoke decision pack generated from survivor databank."),
        (4, "tagger_confirmation", "SQX tagger confirmation", "passed" if args.custom_analysis_enabled and args.columns_populated else "unknown", args.databank, args.databank, tagger_summary["rows"], tagger_summary["status_ok"], max(0, tagger_summary["rows"] - tagger_summary["status_ok"]), {"filter_by_results_disabled": bool(args.filter_by_results_disabled), "columns_populated": bool(args.columns_populated)}, "SQXEdgeCorrelationTagger used as annotation/visual confirmation."),
        (5, "config_recovery", "SQX config recovery", "passed" if args.config_corruption_recovered else "not_needed", "", "", None, None, None, {"config_corruption_recovered": bool(args.config_corruption_recovered)}, "Corruption/recovery note for the custom project."),
    ]
    for order, key, label, status, input_db, output_db, rows, passed, failed, details, note in step_rows:
        con.execute(
            """
            INSERT INTO custom_project_steps(
                project_id, step_order, step_key, step_label, status, input_databank,
                output_databank, row_count, passed_count, failed_count, details_json,
                evidence_note, recorded_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, order, key, label, status, input_db, output_db, rows, passed, failed, safe_json(details), note, now),
        )

    final_rows = tagger_rows or source_rows
    final_summary = summarize_stage(final_rows)
    best = best_strategy(final_rows)
    con.execute(
        """
        INSERT INTO databank_snapshots(
            project_id, run_id, databank, stage_key, row_count, passed_count,
            failed_count, portfolio_count, similar_count, review_count,
            best_strategy_name, best_profit_factor, best_ret_dd_ratio,
            best_max_dd_pct, best_trades, metrics_json, source_kind, recorded_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, databank, stage_key) DO UPDATE SET
            run_id=excluded.run_id,
            row_count=excluded.row_count,
            passed_count=excluded.passed_count,
            failed_count=excluded.failed_count,
            portfolio_count=excluded.portfolio_count,
            similar_count=excluded.similar_count,
            review_count=excluded.review_count,
            best_strategy_name=excluded.best_strategy_name,
            best_profit_factor=excluded.best_profit_factor,
            best_ret_dd_ratio=excluded.best_ret_dd_ratio,
            best_max_dd_pct=excluded.best_max_dd_pct,
            best_trades=excluded.best_trades,
            metrics_json=excluded.metrics_json,
            source_kind=excluded.source_kind,
            recorded_at=excluded.recorded_at
        """,
        (
            project_id,
            run_id,
            args.databank,
            "final_survivor_snapshot",
            final_summary["rows"],
            final_summary["passed"],
            max(0, final_summary["rows"] - final_summary["passed"]),
            final_summary["portfolio"],
            final_summary["similar"],
            max(0, final_summary["rows"] - final_summary["portfolio"] - final_summary["similar"]),
            best.get("strategy_name", ""),
            best.get("profit_factor"),
            best.get("ret_dd_ratio"),
            best.get("max_dd_pct"),
            best.get("trades"),
            safe_json({"source": source_summary, "tagger": tagger_summary}),
            "sqx_databank_export",
            now,
        ),
    )

    con.execute("DELETE FROM test_results WHERE project_id = ?", (project_id,))
    tests = [
        ("load_clean", "SQX clean load", "passed" if args.sqx_clean_load and args.sqx_no_red else "unknown", "", "", None, None, None, None, {"no_red": bool(args.sqx_no_red)}, "Operator confirmed the custom was clean on screen."),
        ("forward_export", "Forward databank export", "passed" if source_rows else "unknown", args.databank, args.databank, source_summary["rows"], source_summary["rows"], source_summary["passed"], max(0, source_summary["rows"] - source_summary["passed"]), source_summary, "Forward survivor databank CSV exported."),
        ("correlation_tagger", "Correlation tagger annotation", "passed" if tagger_summary["status_ok"] else "unknown", args.databank, args.databank, source_summary["rows"], tagger_summary["rows"], tagger_summary["status_ok"], max(0, tagger_summary["rows"] - tagger_summary["status_ok"]), tagger_summary, "SQX tagger populated review columns without filtering rows."),
        ("mc2_spread_policy", "MC2 spread policy", "recorded" if args.mc2_spread_min is not None and args.mc2_spread_max is not None else "unknown", "MC", "MC2", None, None, None, None, {"baseSpread": args.spread_base, "stressMin": args.mc2_spread_min, "stressMax": args.mc2_spread_max}, "AUDCAD spread policy recorded for the custom."),
    ]
    for key, label, status, input_db, output_db, rows_in, rows_out, passed, failed, metrics, note in tests:
        con.execute(
            """
            INSERT INTO test_results(
                project_id, run_id, test_key, test_label, status, input_databank,
                output_databank, rows_in, rows_out, passed_count, failed_count,
                metrics_json, evidence_note, recorded_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, run_id, key, label, status, input_db, output_db, rows_in, rows_out, passed, failed, safe_json(metrics), note, now),
        )

    return project_id


def upsert_run(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.source_csv).resolve() if args.source_csv else None
    tagger_path = Path(args.tagger_csv).resolve() if args.tagger_csv else None
    if source_path and not source_path.is_file():
        raise SystemExit(f"source_csv_not_found: {source_path}")
    if tagger_path and not tagger_path.is_file():
        raise SystemExit(f"tagger_csv_not_found: {tagger_path}")
    if not source_path and not tagger_path:
        raise SystemExit("at_least_one_csv_required")

    source_record = csv_file_record(source_path, "forward_source") if source_path else None
    tagger_record = csv_file_record(tagger_path, "forward_tagger") if tagger_path else None
    primary_rows = (tagger_record or source_record or {"rows": []})["rows"]
    source_rows = (source_record or {"rows": []})["rows"]
    tagger_rows = (tagger_record or {"rows": []})["rows"]

    symbol = args.symbol or infer_from_rows(primary_rows, "Symbol")
    timeframe = args.timeframe or infer_from_rows(primary_rows, "TimeFrame")
    asset = args.asset or symbol.split("_", 1)[0] if symbol else args.asset
    project_name = args.project_name or args.run_key
    sqx_project_name = args.sqx_project_name or project_name

    run_flags = {
        "sqx_clean_load": bool(args.sqx_clean_load),
        "sqx_no_red": bool(args.sqx_no_red),
        "config_corruption_recovered": bool(args.config_corruption_recovered),
        "fresh_mining_run": bool(args.fresh_mining_run),
        "custom_analysis_enabled": bool(args.custom_analysis_enabled),
        "filter_by_results_disabled": bool(args.filter_by_results_disabled),
        "columns_populated": bool(args.columns_populated),
        "no_sqx_internal_db_write": True,
        "no_jars_or_internal_plugins_patch": True,
    }
    data_smoke = {
        "portfolio": summarize_stage(tagger_rows).get("portfolio", 0),
        "similar": summarize_stage(tagger_rows).get("similar", 0),
        "review": max(0, len(tagger_rows) - summarize_stage(tagger_rows).get("portfolio", 0) - summarize_stage(tagger_rows).get("similar", 0)),
        "source": "correlation_decisions.csv",
    }

    now = utc_now()
    db_path = Path(args.db)
    with connect(db_path) as con:
        con.execute(
            """
            INSERT INTO mining_runs(
                run_key, version, source_type, project_name, sqx_project_name,
                asset, symbol, timeframe, layer, blocksetting_family, direction,
                databank, sqx_profile, source_csv_sha256, tagger_csv_sha256,
                source_csv_rows, tagger_csv_rows, spread_base, mc2_spread_min, mc2_spread_max,
                run_flags_json, data_smoke_json, operator_note, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_key) DO UPDATE SET
                version=excluded.version,
                source_type=excluded.source_type,
                project_name=excluded.project_name,
                sqx_project_name=excluded.sqx_project_name,
                asset=excluded.asset,
                symbol=excluded.symbol,
                timeframe=excluded.timeframe,
                layer=excluded.layer,
                blocksetting_family=excluded.blocksetting_family,
                direction=excluded.direction,
                databank=excluded.databank,
                sqx_profile=excluded.sqx_profile,
                source_csv_sha256=excluded.source_csv_sha256,
                tagger_csv_sha256=excluded.tagger_csv_sha256,
                source_csv_rows=excluded.source_csv_rows,
                tagger_csv_rows=excluded.tagger_csv_rows,
                spread_base=excluded.spread_base,
                mc2_spread_min=excluded.mc2_spread_min,
                mc2_spread_max=excluded.mc2_spread_max,
                run_flags_json=excluded.run_flags_json,
                data_smoke_json=excluded.data_smoke_json,
                operator_note=excluded.operator_note,
                updated_at=excluded.updated_at
            """,
            (
                args.run_key,
                VERSION,
                args.source_type,
                project_name,
                sqx_project_name,
                asset or "",
                symbol or "",
                timeframe or "",
                args.layer,
                args.blocksetting_family,
                args.direction,
                args.databank,
                args.sqx_profile,
                source_record["sha256"] if source_record else None,
                tagger_record["sha256"] if tagger_record else None,
                len(source_rows),
                len(tagger_rows),
                args.spread_base,
                args.mc2_spread_min,
                args.mc2_spread_max,
                safe_json(run_flags),
                safe_json(data_smoke),
                args.operator_note or "",
                now,
                now,
            ),
        )
        run_id = int(con.execute("SELECT id FROM mining_runs WHERE run_key = ?", (args.run_key,)).fetchone()["id"])
        project_id = upsert_project_trace(
            con,
            run_id=run_id,
            args=args,
            project_name=project_name,
            sqx_project_name=sqx_project_name,
            asset=asset or "",
            symbol=symbol or "",
            timeframe=timeframe or "",
            source_summary=summarize_stage(source_rows),
            tagger_summary=summarize_stage(tagger_rows),
            tagger_rows=tagger_rows,
            source_rows=source_rows,
            now=now,
        )
        for record in [source_record, tagger_record]:
            if not record:
                continue
            con.execute(
                """
                INSERT INTO mining_files(
                    run_id, kind, file_name, sha256, byte_size, row_count,
                    delimiter, columns_json, path_redacted, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(run_id, kind) DO UPDATE SET
                    file_name=excluded.file_name,
                    sha256=excluded.sha256,
                    byte_size=excluded.byte_size,
                    row_count=excluded.row_count,
                    delimiter=excluded.delimiter,
                    columns_json=excluded.columns_json
                """,
                (
                    run_id,
                    record["kind"],
                    record["file_name"],
                    record["sha256"],
                    record["byte_size"],
                    record["row_count"],
                    record["delimiter"],
                    safe_json(record["columns"]),
                    now,
                ),
            )
        insert_strategy_rows(con, run_id, "forward_source", source_rows)
        insert_strategy_rows(con, run_id, "forward_tagger", tagger_rows)
        if args.events:
            con.execute("DELETE FROM mining_events WHERE run_id = ?", (run_id,))
            for event in args.events:
                if "|" in event:
                    event_type, event_note = event.split("|", 1)
                else:
                    event_type, event_note = normalize_identifier(event), event
                con.execute(
                    "INSERT INTO mining_events(run_id, event_type, event_note, event_at) VALUES(?, ?, ?, ?)",
                    (run_id, event_type.strip(), event_note.strip(), now),
                )
        con.commit()

    return {
        "ok": True,
        "version": VERSION,
        "action": "ingest",
        "runKey": args.run_key,
        "projectKey": args.project_key or args.run_key,
        "db": {"name": db_path.name, "local_path_returned": False},
        "summary": {
            "source": summarize_stage(source_rows),
            "tagger": summarize_stage(tagger_rows),
            "asset": asset,
            "symbol": symbol,
            "timeframe": timeframe,
            "layer": args.layer,
            "databank": args.databank,
            "projectId": project_id,
        },
        "guards": {
            "sqx_data_db_written": False,
            "sqx_jars_patched": False,
            "sqx_runtime_started": False,
        },
    }


def status(args: argparse.Namespace) -> dict[str, Any]:
    db_path = Path(args.db)
    if not db_path.is_file():
        return {
            "ok": True,
            "version": VERSION,
            "action": "status",
            "exists": False,
            "db": {"name": db_path.name, "local_path_returned": False},
            "runs": 0,
            "strategyRows": 0,
        }
    with connect(db_path) as con:
        run_count = int(con.execute("SELECT COUNT(*) AS count FROM mining_runs").fetchone()["count"])
        project_count = int(con.execute("SELECT COUNT(*) AS count FROM custom_projects").fetchone()["count"])
        databank_count = int(con.execute("SELECT COUNT(*) AS count FROM databank_snapshots").fetchone()["count"])
        test_count = int(con.execute("SELECT COUNT(*) AS count FROM test_results").fetchone()["count"])
        strategy_count = int(con.execute("SELECT COUNT(*) AS count FROM strategy_results").fetchone()["count"])
        latest = con.execute(
            """
            SELECT project_key, project_name, asset, symbol, timeframe, layer, updated_at
            FROM custom_projects ORDER BY updated_at DESC LIMIT 5
            """
        ).fetchall()
    return {
        "ok": True,
        "version": VERSION,
        "action": "status",
        "exists": True,
        "db": {"name": db_path.name, "local_path_returned": False},
        "runs": run_count,
        "customProjects": project_count,
        "databankSnapshots": databank_count,
        "testResults": test_count,
        "strategyRows": strategy_count,
        "latestProjects": [dict(row) for row in latest],
    }


def export_run(args: argparse.Namespace) -> dict[str, Any]:
    db_path = Path(args.db)
    if not db_path.is_file():
        raise SystemExit("registry_db_not_found")
    with connect(db_path) as con:
        run = con.execute("SELECT * FROM mining_runs WHERE run_key = ?", (args.run_key,)).fetchone()
        if not run:
            raise SystemExit("run_key_not_found")
        files = [dict(row) for row in con.execute("SELECT kind, file_name, sha256, row_count, path_redacted FROM mining_files WHERE run_id = ? ORDER BY kind", (run["id"],)).fetchall()]
        events = [dict(row) for row in con.execute("SELECT event_type, event_note, event_at FROM mining_events WHERE run_id = ? ORDER BY id", (run["id"],)).fetchall()]
        strategy_summary = [dict(row) for row in con.execute(
            """
            SELECT stage, COUNT(*) AS rows, SUM(CASE WHEN corr_decision = 1 THEN 1 ELSE 0 END) AS portfolio,
                   SUM(CASE WHEN corr_decision = 0 THEN 1 ELSE 0 END) AS similar,
                   SUM(CASE WHEN corr_decision = -1 THEN 1 ELSE 0 END) AS untagged
            FROM strategy_results WHERE run_id = ? GROUP BY stage ORDER BY stage
            """,
            (run["id"],),
        ).fetchall()]
    run_dict = dict(run)
    run_dict["run_flags"] = json.loads(run_dict.pop("run_flags_json"))
    run_dict["data_smoke"] = json.loads(run_dict.pop("data_smoke_json"))
    run_dict.pop("id", None)
    return {
        "ok": True,
        "version": VERSION,
        "action": "export-json",
        "run": run_dict,
        "files": files,
        "events": events,
        "strategySummary": strategy_summary,
        "privacy": {"local_paths_returned": False},
    }


def parse_sqx_fingerprint(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file_name": path.name,
        "byte_size": path.stat().st_size,
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
        "strategy_name": path.stem,
        "fingerprint_found": False,
    }
    try:
        with zipfile.ZipFile(path) as archive:
            if "settings.xml" not in archive.namelist():
                return result
            text = archive.read("settings.xml").decode("utf-8", errors="replace")
    except (OSError, zipfile.BadZipFile, KeyError):
        return result
    match = re.search(
        r'<Fingerprint\s+strategyName="(?P<name>[^"]*)"\s+exact="(?P<exact>[^"]*)"\s+trades="(?P<trades>[^"]*)"\s+profit="(?P<profit>[^"]*)"\s+drawdown="(?P<drawdown>[^"]*)"\s+fitness="(?P<fitness>[^"]*)"\s+tradesHash="(?P<trades_hash>[^"]*)"',
        text,
    )
    if not match:
        return result
    profit = parse_decimal(match.group("profit"))
    drawdown = parse_decimal(match.group("drawdown"))
    result.update({
        "strategy_name": match.group("name") or path.stem,
        "exact": match.group("exact"),
        "trades": parse_int(match.group("trades")),
        "profit": profit,
        "drawdown": drawdown,
        "fitness": parse_decimal(match.group("fitness")),
        "trades_hash": match.group("trades_hash"),
        "ret_drawdown_ratio": (profit / drawdown) if profit is not None and drawdown not in (None, 0) else None,
        "fingerprint_found": True,
    })
    return result


def upsert_databank_snapshot(
    con: sqlite3.Connection,
    *,
    project_id: int,
    run_id: int,
    databank: str,
    files: list[Path],
    fingerprints: list[dict[str, Any]],
    now: str,
) -> None:
    parsed = [item for item in fingerprints if item.get("fingerprint_found")]
    best = None
    if parsed:
        best = sorted(
            parsed,
            key=lambda item: (
                item.get("ret_drawdown_ratio") if item.get("ret_drawdown_ratio") is not None else -999999,
                item.get("profit") if item.get("profit") is not None else -999999,
            ),
            reverse=True,
        )[0]
    total_bytes = sum(path.stat().st_size for path in files)
    newest = max((path.stat().st_mtime for path in files), default=0)
    metrics = {
        "source": "sqx_user_projects_databank_folder",
        "sqxFiles": len(files),
        "totalBytes": total_bytes,
        "newestFileUtc": datetime.fromtimestamp(newest, timezone.utc).isoformat(timespec="seconds") if newest else "",
        "fingerprintsParsed": len(parsed),
        "fingerprintLimitApplied": len(fingerprints) < len(files),
    }
    con.execute(
        """
        INSERT INTO databank_snapshots(
            project_id, run_id, databank, stage_key, row_count, passed_count,
            failed_count, portfolio_count, similar_count, review_count,
            best_strategy_name, best_profit_factor, best_ret_dd_ratio,
            best_max_dd_pct, best_trades, metrics_json, source_kind, recorded_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, NULL, ?, NULL, ?, ?, ?, ?)
        ON CONFLICT(project_id, databank, stage_key) DO UPDATE SET
            run_id=excluded.run_id,
            row_count=excluded.row_count,
            passed_count=excluded.passed_count,
            failed_count=excluded.failed_count,
            best_strategy_name=excluded.best_strategy_name,
            best_ret_dd_ratio=excluded.best_ret_dd_ratio,
            best_trades=excluded.best_trades,
            metrics_json=excluded.metrics_json,
            source_kind=excluded.source_kind,
            recorded_at=excluded.recorded_at
        """,
        (
            project_id,
            run_id,
            databank,
            "sqx_local_databank",
            len(files),
            len(files),
            0,
            best.get("strategy_name", "") if best else "",
            best.get("ret_drawdown_ratio") if best else None,
            best.get("trades") if best else None,
            safe_json(metrics),
            "sqx_user_projects_databank_folder",
            now,
        ),
    )


def scan_project_databanks(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        raise SystemExit(f"project_dir_not_found: {project_dir}")
    databanks_dir = project_dir / "databanks"
    if not databanks_dir.is_dir():
        raise SystemExit(f"databanks_dir_not_found: {databanks_dir}")
    project_key = args.project_key or project_dir.name
    now = utc_now()
    db_path = Path(args.db)
    max_parse = max(0, int(args.max_sqx_parse))
    with connect(db_path) as con:
        project = con.execute("SELECT * FROM custom_projects WHERE project_key = ?", (project_key,)).fetchone()
        if not project:
            run_key = args.run_key or project_key
            con.execute(
                """
                INSERT OR IGNORE INTO mining_runs(
                    run_key, version, source_type, project_name, sqx_project_name,
                    asset, symbol, timeframe, layer, blocksetting_family, direction,
                    databank, sqx_profile, source_csv_rows, tagger_csv_rows,
                    run_flags_json, data_smoke_json, operator_note, created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?)
                """,
                (
                    run_key,
                    VERSION,
                    "sqx_local_project_scan",
                    args.project_name or project_dir.name,
                    args.sqx_project_name or project_dir.name,
                    args.asset,
                    args.symbol,
                    args.timeframe,
                    args.layer,
                    args.blocksetting_family,
                    args.direction,
                    args.databank,
                    args.sqx_profile,
                    safe_json({"sqx_local_project_scan": True, "no_sqx_internal_db_write": True}),
                    safe_json({}),
                    args.operator_note or "",
                    now,
                    now,
                ),
            )
            run_id = int(con.execute("SELECT id FROM mining_runs WHERE run_key = ?", (run_key,)).fetchone()["id"])
            con.execute(
                """
                INSERT INTO custom_projects(
                    project_key, run_id, project_name, sqx_project_name, asset, symbol,
                    timeframe, layer, blocksetting_family, direction, sqx_profile,
                    trace_json, created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_key,
                    run_id,
                    args.project_name or project_dir.name,
                    args.sqx_project_name or project_dir.name,
                    args.asset,
                    args.symbol,
                    args.timeframe,
                    args.layer,
                    args.blocksetting_family,
                    args.direction,
                    args.sqx_profile,
                    safe_json({"version": VERSION, "projectKey": project_key, "source": "sqx_local_project_scan"}),
                    now,
                    now,
                ),
            )
            project = con.execute("SELECT * FROM custom_projects WHERE project_key = ?", (project_key,)).fetchone()
        project_id = int(project["id"])
        run_id = int(project["run_id"] or 0)
        if not run_id:
            raise SystemExit("project_run_id_missing")

        scanned = []
        for databank_dir in sorted([item for item in databanks_dir.iterdir() if item.is_dir()], key=lambda p: p.name.lower()):
            files = sorted(databank_dir.glob("*.sqx"), key=lambda p: p.name.lower())
            limit = len(files) if max_parse == 0 else min(len(files), max_parse)
            fingerprints = [parse_sqx_fingerprint(path) for path in files[:limit]]
            upsert_databank_snapshot(
                con,
                project_id=project_id,
                run_id=run_id,
                databank=databank_dir.name,
                files=files,
                fingerprints=fingerprints,
                now=now,
            )
            stage = f"sqx:{databank_dir.name}"
            con.execute("DELETE FROM strategy_results WHERE run_id = ? AND stage = ?", (run_id, stage))
            for index, item in enumerate(fingerprints, start=1):
                con.execute(
                    """
                    INSERT INTO strategy_results(
                        run_id, stage, row_index, strategy_name, filters_result, symbol, timeframe,
                        fitness, profit_factor, ret_dd_ratio, max_dd_pct, trades,
                        corr_decision, corr_rank, corr_score, corr_max, corr_status, nearest_winner,
                        entry_indicators, exit_indicators, price_indicators, raw_json
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, ?, NULL, NULL, NULL, NULL, NULL, '', '', '', '', ?)
                    """,
                    (
                        run_id,
                        stage,
                        index,
                        item.get("strategy_name") or item.get("file_name") or "",
                        "PRESENT_IN_DATABANK",
                        project["symbol"],
                        project["timeframe"],
                        item.get("fitness"),
                        item.get("ret_drawdown_ratio"),
                        item.get("trades"),
                        safe_json(item),
                    ),
                )
            scanned.append({
                "databank": databank_dir.name,
                "sqxFiles": len(files),
                "fingerprintsParsed": sum(1 for item in fingerprints if item.get("fingerprint_found")),
            })
        con.commit()
    return {
        "ok": True,
        "version": VERSION,
        "action": "scan-project",
        "projectKey": project_key,
        "databanksScanned": scanned,
        "db": {"name": db_path.name, "local_path_returned": False},
        "guards": {
            "read_only_sqx_project": True,
            "sqx_data_db_written": False,
            "sqx_jars_patched": False,
            "sqx_runtime_started": False,
        },
    }


def build_funnel_payload(db_path: Path, project_key: str = "", run_key: str = "") -> dict[str, Any]:
    if not db_path.is_file():
        return {
            "ok": True,
            "version": VERSION,
            "action": "funnel-json",
            "exists": False,
            "projects": [],
            "privacy": {"local_paths_returned": False},
        }
    with connect(db_path) as con:
        if project_key or run_key:
            key = project_key or run_key
            projects = con.execute(
                "SELECT * FROM custom_projects WHERE project_key = ? ORDER BY updated_at DESC",
                (key,),
            ).fetchall()
        else:
            projects = con.execute("SELECT * FROM custom_projects ORDER BY updated_at DESC LIMIT 20").fetchall()
        output_projects = []
        for project in projects:
            project_id = int(project["id"])
            steps = [dict(row) for row in con.execute(
                """
                SELECT step_order, step_key, step_label, status, input_databank,
                       output_databank, row_count, passed_count, failed_count,
                       details_json, evidence_note, recorded_at
                FROM custom_project_steps WHERE project_id = ? ORDER BY step_order
                """,
                (project_id,),
            ).fetchall()]
            databanks = [dict(row) for row in con.execute(
                """
                SELECT databank, stage_key, row_count, passed_count, failed_count,
                       portfolio_count, similar_count, review_count, best_strategy_name,
                       best_profit_factor, best_ret_dd_ratio, best_max_dd_pct,
                       best_trades, metrics_json, source_kind, recorded_at
                FROM databank_snapshots WHERE project_id = ? ORDER BY recorded_at, databank
                """,
                (project_id,),
            ).fetchall()]
            tests = [dict(row) for row in con.execute(
                """
                SELECT test_key, test_label, status, input_databank, output_databank,
                       rows_in, rows_out, passed_count, failed_count, metrics_json,
                       evidence_note, recorded_at
                FROM test_results WHERE project_id = ? ORDER BY id
                """,
                (project_id,),
            ).fetchall()]
            for row in steps:
                row["details"] = json.loads(row.pop("details_json"))
            for row in databanks:
                row["metrics"] = json.loads(row.pop("metrics_json"))
            for row in tests:
                row["metrics"] = json.loads(row.pop("metrics_json"))
            trace = json.loads(str(project["trace_json"] or "{}"))
            output_projects.append({
                "projectKey": project["project_key"],
                "projectName": project["project_name"],
                "sqxProjectName": project["sqx_project_name"],
                "asset": project["asset"],
                "symbol": project["symbol"],
                "timeframe": project["timeframe"],
                "layer": project["layer"],
                "blocksettingFamily": project["blocksetting_family"],
                "direction": project["direction"],
                "sqxProfile": project["sqx_profile"],
                "trace": trace,
                "steps": steps,
                "databanks": databanks,
                "tests": tests,
                "edgeFactoryStatePatch": {
                    "selectedCard": {
                        "asset": project["asset"],
                        "timeframe": project["timeframe"],
                        "direction": project["direction"],
                        "family": project["blocksetting_family"],
                        "blockSetting": project["blocksetting_family"],
                        "source": "sqx142-mining-results-registry-v1",
                    },
                    "capa1Analysis": {
                        "version": VERSION,
                        "projectKey": project["project_key"],
                        "status": "recorded",
                        "databanks": databanks,
                        "tests": tests,
                    },
                },
            })
    return {
        "ok": True,
        "version": VERSION,
        "action": "funnel-json",
        "exists": True,
        "projects": output_projects,
        "privacy": {"local_paths_returned": False},
    }


def project_funnel(args: argparse.Namespace) -> dict[str, Any]:
    return build_funnel_payload(Path(args.db), project_key=args.project_key, run_key=args.run_key)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQX142 mining results registry")
    parser.add_argument("--action", choices=["status", "init", "ingest", "export-json", "funnel-json", "scan-project"], default="status")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--run-key", default="")
    parser.add_argument("--project-key", default="")
    parser.add_argument("--source-csv", default="")
    parser.add_argument("--tagger-csv", default="")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--max-sqx-parse", type=int, default=300)
    parser.add_argument("--source-type", default="fresh_mining_test")
    parser.add_argument("--project-name", default="")
    parser.add_argument("--sqx-project-name", default="")
    parser.add_argument("--asset", default="")
    parser.add_argument("--symbol", default="")
    parser.add_argument("--timeframe", default="")
    parser.add_argument("--layer", default="unknown")
    parser.add_argument("--blocksetting-family", default="unknown")
    parser.add_argument("--direction", default="unknown")
    parser.add_argument("--databank", default="Forward")
    parser.add_argument("--sqx-profile", default="SQX Edge / Darwinex")
    parser.add_argument("--spread-base", type=float, default=None)
    parser.add_argument("--mc2-spread-min", type=float, default=None)
    parser.add_argument("--mc2-spread-max", type=float, default=None)
    parser.add_argument("--operator-note", default="")
    parser.add_argument("--event", dest="events", action="append", default=[])
    parser.add_argument("--sqx-clean-load", action="store_true")
    parser.add_argument("--sqx-no-red", action="store_true")
    parser.add_argument("--config-corruption-recovered", action="store_true")
    parser.add_argument("--fresh-mining-run", action="store_true")
    parser.add_argument("--custom-analysis-enabled", action="store_true")
    parser.add_argument("--filter-by-results-disabled", action="store_true")
    parser.add_argument("--columns-populated", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.action == "init":
        with connect(Path(args.db)):
            pass
        result = status(args)
        result["action"] = "init"
    elif args.action == "ingest":
        if not args.run_key:
            seed = args.project_name or args.source_csv or args.tagger_csv or "mining_run"
            args.run_key = normalize_identifier(seed)
        result = upsert_run(args)
    elif args.action == "export-json":
        if not args.run_key:
            raise SystemExit("run_key_required")
        result = export_run(args)
    elif args.action == "funnel-json":
        result = project_funnel(args)
    elif args.action == "scan-project":
        result = scan_project_databanks(args)
    else:
        result = status(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
