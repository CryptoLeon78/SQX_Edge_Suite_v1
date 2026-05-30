from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import math
import os
import re
import struct
import sys
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sqx142_portfolio_correlation_stability import (  # noqa: E402
    CAPA1_C2_CORRELATION_SELECTION_VERSION,
    PORTFOLIO_CORRELATION_STABILITY_VERSION,
    build_capa1_c2_correlation_selection_report,
    build_portfolio_correlation_stability_report,
    export_portfolio_correlation_stability_csv,
)
from tools.sqx142_mining_registry import (  # noqa: E402
    DEFAULT_DB as REGISTRY_DEFAULT_DB,
    connect as registry_connect,
    safe_json,
)
from tools.sqx142_portfolio_corr2_local_project_integration import (  # noqa: E402
    DEFAULT_SQX_ROOT,
    TAGGED_DATABANK,
    databank_counts,
    guarded_flags,
    load_cfx,
    period_plan,
    project_dir,
    require_sqx_closed,
    sqx_process_snapshot,
)


VERSION = "sqx142-capa1-c2-corr1-registered-decision-v1"
DEPRECATED_PORTFOLIO_ALIAS_VERSION = "sqx142-portfolio-corr1-registered-decision-v1"
LOCAL_ROOT = Path(".local") / "sqx142_portfolio_corr1_registered_decision"
DEFAULT_PROJECT_KEY = "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1"
DEFAULT_DATABANK = TAGGED_DATABANK
DAILY_EQUITY_SUFFIX = "/dailyEquity.bin"
CAPA1_C2_DECISION_NODE = "c2_template_selection_decision"
CAPA1_C2_DECISION_KEY = "capa1_c2_corr1_registered_selection_decision"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sqx_date(value: str, fallback: date) -> date:
    text = str(value or "").strip().replace(".", "-")
    try:
        return date.fromisoformat(text)
    except ValueError:
        return fallback


def java_primitive_payload(data: bytes) -> bytes:
    if not data.startswith(b"\xac\xed\x00\x05"):
        raise ValueError("daily_equity_not_java_serialized")
    pos = 4
    payload = bytearray()
    while pos < len(data):
        tag = data[pos]
        pos += 1
        if tag == 0x77:
            length = data[pos]
            pos += 1
            payload.extend(data[pos:pos + length])
            pos += length
        elif tag == 0x7A:
            length = struct.unpack(">I", data[pos:pos + 4])[0]
            pos += 4
            payload.extend(data[pos:pos + length])
            pos += length
        elif tag == 0x78:
            break
        else:
            raise ValueError(f"daily_equity_unknown_java_token:{tag}")
    return bytes(payload)


def parse_daily_equity(data: bytes) -> list[tuple[date, float]]:
    payload = java_primitive_payload(data)
    if len(payload) < 4:
        raise ValueError("daily_equity_payload_too_short")
    count = struct.unpack(">i", payload[:4])[0]
    expected = 4 + (count * 16)
    if count < 0 or len(payload) < expected:
        raise ValueError("daily_equity_payload_size_mismatch")
    offset = 4
    rows: list[tuple[date, float]] = []
    for _index in range(count):
        timestamp_ms = struct.unpack(">q", payload[offset:offset + 8])[0]
        value = struct.unpack(">d", payload[offset + 8:offset + 16])[0]
        offset += 16
        if math.isfinite(value):
            rows.append((datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc).date(), value))
    return rows


def equity_deltas(equity: list[tuple[date, float]], start: date, end_exclusive: date) -> list[float]:
    returns: list[float] = []
    previous: float | None = None
    for day, value in equity:
        if previous is not None and start <= day < end_exclusive:
            returns.append(round(value - previous, 8))
        previous = value
    return returns


def fingerprint_from_settings(text: str, fallback: str) -> dict[str, Any]:
    match = re.search(
        r'<Fingerprint\s+strategyName="(?P<strategyName>[^"]*)"\s+exact="(?P<exact>[^"]*)"\s+trades="(?P<trades>[^"]*)"\s+profit="(?P<profit>[^"]*)"\s+drawdown="(?P<drawdown>[^"]*)"\s+fitness="(?P<fitness>[^"]*)"',
        text,
    )
    if match:
        raw = dict(match.groupdict())
        raw["strategyName"] = html.unescape(raw.get("strategyName") or fallback)
        return raw
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        root = None
    fingerprint = root.find(".//Fingerprint") if root is not None else None
    if fingerprint is not None:
        raw = dict(fingerprint.attrib)
        raw["strategyName"] = html.unescape(raw.get("strategyName") or fallback)
        return raw
    return {"strategyName": fallback, "exact": "", "trades": "", "profit": "", "drawdown": "", "fitness": ""}


def numeric(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(str(value).replace(",", ".").strip())
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def parse_strategy_sqx(path: Path, *, is_start: date, is_end: date, oos3_start: date, oos3_end: date) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        equity_name = next((name for name in names if name.endswith(DAILY_EQUITY_SUFFIX)), "")
        if not equity_name:
            raise ValueError("daily_equity_missing")
        settings_text = archive.read("settings.xml").decode("utf-8", errors="replace") if "settings.xml" in names else ""
        equity = parse_daily_equity(archive.read(equity_name))
    fingerprint = fingerprint_from_settings(settings_text, path.stem)
    strategy_name = str(fingerprint.get("strategyName") or path.stem)
    profit = numeric(fingerprint.get("profit"))
    drawdown = numeric(fingerprint.get("drawdown"))
    ret_dd = profit / drawdown if drawdown else 0.0
    is_series = equity_deltas(equity, is_start, is_end)
    oos3_series = equity_deltas(equity, oos3_start, oos3_end + timedelta(days=1))
    return {
        "strategy": strategy_name,
        "candidate": {
            "strategy": strategy_name,
            "asset": "AUDCAD",
            "timeframe": "H1",
            "profitFactor": "",
            "retDd": round(ret_dd, 6),
            "maxDd": "",
            "trades": int(numeric(fingerprint.get("trades"))),
            "blockSetting": "BS_Momentum_v6",
        },
        "isRow": {
            "strategy": strategy_name,
            "isReturnSeries": "|".join(str(value) for value in is_series),
        },
        "oos3Row": {
            "strategy": strategy_name,
            "oos3ReturnSeries": "|".join(str(value) for value in oos3_series),
        },
        "fingerprint": {
            "exact": str(fingerprint.get("exact") or ""),
            "trades": int(numeric(fingerprint.get("trades"))),
            "profit": profit,
            "drawdown": drawdown,
            "fitness": numeric(fingerprint.get("fitness")),
            "retDrawdownRatio": round(ret_dd, 6),
            "dailyPoints": len(equity),
            "isPoints": len(is_series),
            "oos3Points": len(oos3_series),
            "sha256": sha256_file(path),
        },
    }


def project_periods(project: Path) -> dict[str, Any]:
    plan = period_plan(load_cfx(project / "project.cfx"))
    corr = plan.get("corr1", {})
    return {
        "raw": plan,
        "isStart": parse_sqx_date(corr.get("dateFrom", ""), date(2017, 10, 2)),
        "isEnd": parse_sqx_date(corr.get("isTo", ""), date(2025, 1, 1)),
        "oos3Start": parse_sqx_date(corr.get("oos3From", ""), date(2025, 1, 1)),
        "oos3End": parse_sqx_date(corr.get("oos3To", ""), date(2026, 4, 8)),
    }


def build_payload_from_registered_databank(project: Path, databank: str) -> dict[str, Any]:
    periods = project_periods(project)
    databank_dir = project / "databanks" / databank
    if not databank_dir.is_dir():
        raise ValueError("registered_databank_missing")
    parsed: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in sorted(databank_dir.glob("*.sqx"), key=lambda item: item.name.lower()):
        try:
            parsed.append(parse_strategy_sqx(
                path,
                is_start=periods["isStart"],
                is_end=periods["isEnd"],
                oos3_start=periods["oos3Start"],
                oos3_end=periods["oos3End"],
            ))
        except Exception as exc:
            errors.append({"fileHash": hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:16], "error": type(exc).__name__})
    return {
        "periods": {
            "isStart": periods["isStart"].isoformat(),
            "isEnd": periods["isEnd"].isoformat(),
            "oos3Start": periods["oos3Start"].isoformat(),
            "oos3End": periods["oos3End"].isoformat(),
            "raw": periods["raw"],
        },
        "rows": [item["candidate"] for item in parsed],
        "isRows": [item["isRow"] for item in parsed],
        "oos3Rows": [item["oos3Row"] for item in parsed],
        "fingerprints": [item["fingerprint"] for item in parsed],
        "parseErrors": errors,
    }


def export_decision_items_csv(report: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "candidateId",
            "decision",
            "reason",
            "score",
            "maxIsCorrelationToSelected",
            "maxOos3CorrelationToSelected",
            "correlationDriftToSelected",
            "isPoints",
            "oos3Points",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for item in report.get("items", []):
        series_points = item.get("seriesPoints", {}) if isinstance(item, dict) else {}
        writer.writerow({
            "candidateId": item.get("candidateId", ""),
            "decision": item.get("decision", ""),
            "reason": item.get("reason", ""),
            "score": item.get("score", ""),
            "maxIsCorrelationToSelected": item.get("maxIsCorrelationToSelected", ""),
            "maxOos3CorrelationToSelected": item.get("maxOos3CorrelationToSelected", ""),
            "correlationDriftToSelected": item.get("correlationDriftToSelected", ""),
            "isPoints": series_points.get("is", ""),
            "oos3Points": series_points.get("oos3", ""),
        })
    return output.getvalue()


def record_evidence(name: str, payload: dict[str, Any], pair_csv: str = "", decisions_csv: str = "") -> None:
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    (LOCAL_ROOT / f"latest_{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    if pair_csv:
        (LOCAL_ROOT / f"latest_{name}_pairs.csv").write_text(pair_csv, encoding="utf-8", newline="")
    if decisions_csv:
        (LOCAL_ROOT / f"latest_{name}_decisions.csv").write_text(decisions_csv, encoding="utf-8", newline="")


def status_for(project: Path, databank: str, db_path: Path, project_key: str, sqx_root: Path) -> dict[str, Any]:
    counts = databank_counts(project)
    latest_step: dict[str, Any] | None = None
    if db_path.is_file():
        with registry_connect(db_path) as con:
            row = con.execute(
                """
                SELECT s.step_key, s.step_label, s.status, s.row_count, s.passed_count, s.failed_count, s.recorded_at
                FROM custom_project_steps s
                JOIN custom_projects p ON p.id = s.project_id
                WHERE p.project_key = ?
                  AND s.step_key IN (?, 'corr1_registered_stability_decision')
                ORDER BY CASE WHEN s.step_key = ? THEN 0 ELSE 1 END
                """,
                (project_key, CAPA1_C2_DECISION_KEY, CAPA1_C2_DECISION_KEY),
            ).fetchone()
            latest_step = dict(row) if row else None
    return {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "action": "status",
        "decisionDomain": "capa1_c2_template_selection",
        "projectKey": project_key,
        "databank": databank,
        "databankRows": counts.get(databank, 0),
        "periods": project_periods(project)["raw"],
        "latestStep": latest_step,
        "processGuard": sqx_process_snapshot(sqx_root),
        "privacy": {"local_paths_returned": False, "raw_strategy_names_returned": False},
        "guards": {
            **guarded_flags(),
            "sqx_project_write_allowed": False,
            "sqx_databank_write_allowed": False,
        },
    }


def register_analysis(db_path: Path, project_key: str, databank: str, report: dict[str, Any], extraction: dict[str, Any]) -> None:
    now = now_iso()
    summary = dict(report.get("summary", {}))
    with registry_connect(db_path) as con:
        project = con.execute("SELECT * FROM custom_projects WHERE project_key = ?", (project_key,)).fetchone()
        if not project:
            raise ValueError("custom_project_missing_in_registry")
        project_id = int(project["id"])
        run_id = int(project["run_id"] or 0)
        status = str(summary.get("status") or "unknown")
        selected = int(summary.get("selectedByIs") or 0)
        similar = int(summary.get("similarByIs") or 0)
        review = int(summary.get("review") or 0)
        input_rows = int(summary.get("inputRows") or 0)
        details = {
            "version": VERSION,
            "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
            "coreVersion": PORTFOLIO_CORRELATION_STABILITY_VERSION,
            "capa1C2Version": CAPA1_C2_CORRELATION_SELECTION_VERSION,
            "decisionDomain": "capa1_c2_template_selection",
            "decisionNode": CAPA1_C2_DECISION_NODE,
            "summary": summary,
            "periods": extraction.get("periods", {}),
            "parseErrors": extraction.get("parseErrors", []),
            "methodology": report.get("methodology", {}),
            "warnings": report.get("warnings", []),
            "blockers": report.get("blockers", []),
        }
        con.execute(
            """
            INSERT INTO custom_project_steps(
                project_id, step_order, step_key, step_label, status,
                input_databank, output_databank, row_count, passed_count,
                failed_count, details_json, evidence_note, recorded_at
            )
            VALUES(?, 93, ?, 'Capa1 C2 template selection decision', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, step_key) DO UPDATE SET
                step_label=excluded.step_label,
                status=excluded.status,
                input_databank=excluded.input_databank,
                output_databank=excluded.output_databank,
                row_count=excluded.row_count,
                passed_count=excluded.passed_count,
                failed_count=excluded.failed_count,
                details_json=excluded.details_json,
                evidence_note=excluded.evidence_note,
                recorded_at=excluded.recorded_at
            """,
            (
                project_id,
                CAPA1_C2_DECISION_KEY,
                status,
                databank,
                CAPA1_C2_DECISION_NODE,
                input_rows,
                selected,
                similar + review,
                safe_json(details),
                "Capa1 CORR1 selection built from registered SQX local tagged databank daily equity for Template C2 selection.",
                now,
            ),
        )
        con.execute(
            """
            INSERT INTO test_results(
                project_id, run_id, test_key, test_label, status, input_databank,
                output_databank, rows_in, rows_out, passed_count, failed_count,
                metrics_json, evidence_note, recorded_at
            )
            VALUES(?, ?, 'capa1_c2_corr1_registered_decision', 'Capa1 C2 template selection decision', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, test_key) DO UPDATE SET
                status=excluded.status,
                input_databank=excluded.input_databank,
                rows_in=excluded.rows_in,
                rows_out=excluded.rows_out,
                passed_count=excluded.passed_count,
                failed_count=excluded.failed_count,
                metrics_json=excluded.metrics_json,
                evidence_note=excluded.evidence_note,
                recorded_at=excluded.recorded_at
            """,
            (
                project_id,
                run_id,
                status,
                databank,
                CAPA1_C2_DECISION_NODE,
                input_rows,
                selected,
                selected,
                similar + review,
                safe_json(details),
                "Read-only SQX local daily-equity CORR1 audit for Capa1 Template C2 selection.",
                now,
            ),
        )
        con.execute(
            """
            INSERT INTO databank_snapshots(
                project_id, run_id, databank, stage_key, row_count, passed_count,
                failed_count, portfolio_count, similar_count, review_count,
                best_strategy_name, best_profit_factor, best_ret_dd_ratio,
                best_max_dd_pct, best_trades, metrics_json, source_kind, recorded_at
            )
            VALUES(?, ?, ?, 'capa1_c2_corr1_registered_decision', ?, ?, ?, ?, ?, ?, '', NULL, NULL, NULL, NULL, ?, ?, ?)
            ON CONFLICT(project_id, databank, stage_key) DO UPDATE SET
                row_count=excluded.row_count,
                passed_count=excluded.passed_count,
                failed_count=excluded.failed_count,
                portfolio_count=excluded.portfolio_count,
                similar_count=excluded.similar_count,
                review_count=excluded.review_count,
                metrics_json=excluded.metrics_json,
                source_kind=excluded.source_kind,
                recorded_at=excluded.recorded_at
            """,
            (
                project_id,
                run_id,
                databank,
                input_rows,
                input_rows,
                0,
                selected,
                similar,
                review,
                safe_json(details),
                VERSION,
                now,
            ),
        )
        trace = json.loads(str(project["trace_json"] or "{}"))
        trace["capa1C2Corr1RegisteredDecision"] = {
            "version": VERSION,
            "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
            "decisionDomain": "capa1_c2_template_selection",
            "decisionNode": CAPA1_C2_DECISION_NODE,
            "databank": databank,
            "summary": summary,
            "recordedAt": now,
        }
        con.execute(
            "UPDATE custom_projects SET trace_json = ?, updated_at = ? WHERE id = ?",
            (safe_json(trace), now, project_id),
        )
        con.commit()


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    sqx_root = Path(args.sqx_root)
    process_guard = require_sqx_closed(sqx_root, skip=bool(getattr(args, "skip_process_guard", False)))
    project = project_dir(sqx_root, args.project_key)
    extraction = build_payload_from_registered_databank(project, args.databank)
    report = build_capa1_c2_correlation_selection_report({
        "rows": extraction["rows"],
        "isRows": extraction["isRows"],
        "oos3Rows": extraction["oos3Rows"],
        "settings": {
            "maxIsCorrelation": args.max_is_correlation,
            "maxOos3Correlation": args.max_oos3_correlation,
            "warnOos3Correlation": args.warn_oos3_correlation,
            "maxCorrelationDrift": args.max_correlation_drift,
            "minComparablePoints": args.min_comparable_points,
            "maxWinners": args.max_winners,
        },
    })
    report["registeredSource"] = {
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "decisionDomain": "capa1_c2_template_selection",
        "decisionNode": CAPA1_C2_DECISION_NODE,
        "projectKey": args.project_key,
        "databank": args.databank,
        "rowsParsed": len(extraction["rows"]),
        "parseErrors": len(extraction["parseErrors"]),
        "periods": extraction["periods"],
    }
    register_analysis(Path(args.db), args.project_key, args.databank, report, extraction)
    pair_csv = export_portfolio_correlation_stability_csv(report)
    decisions_csv = export_decision_items_csv(report)
    result = {
        "ok": True,
        "version": VERSION,
        "deprecatedAliases": [DEPRECATED_PORTFOLIO_ALIAS_VERSION],
        "action": "analyze",
        "decisionDomain": "capa1_c2_template_selection",
        "projectKey": args.project_key,
        "databank": args.databank,
        "report": report,
        "csvExport": pair_csv,
        "decisionCsvExport": decisions_csv,
        "processGuard": process_guard,
        "privacy": {"local_paths_returned": False, "raw_strategy_names_returned": False},
        "guards": {
            **guarded_flags(),
            "sqx_project_write_allowed": False,
            "sqx_databank_write_allowed": False,
        },
    }
    record_evidence("analyze", result, pair_csv=pair_csv, decisions_csv=decisions_csv)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQX142 CORR1 registered stability decision")
    parser.add_argument("--action", choices=["status", "analyze"], default="status")
    parser.add_argument("--sqx-root", default=str(DEFAULT_SQX_ROOT))
    parser.add_argument("--project-key", default=DEFAULT_PROJECT_KEY)
    parser.add_argument("--databank", default=DEFAULT_DATABANK)
    parser.add_argument("--db", default=str(REGISTRY_DEFAULT_DB))
    parser.add_argument("--max-is-correlation", type=float, default=0.50)
    parser.add_argument("--max-oos3-correlation", type=float, default=0.60)
    parser.add_argument("--warn-oos3-correlation", type=float, default=0.45)
    parser.add_argument("--max-correlation-drift", type=float, default=0.25)
    parser.add_argument("--min-comparable-points", type=int, default=12)
    parser.add_argument("--max-winners", type=int, default=12)
    parser.add_argument("--skip-process-guard", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        project = project_dir(Path(args.sqx_root), args.project_key)
        result = analyze(args) if args.action == "analyze" else status_for(project, args.databank, Path(args.db), args.project_key, Path(args.sqx_root))
    except Exception as exc:
        result = {
            "ok": False,
            "version": VERSION,
            "action": args.action,
            "error": type(exc).__name__,
            "message": str(exc),
            "privacy": {"local_paths_returned": False, "raw_strategy_names_returned": False},
            "guards": guarded_flags(),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
