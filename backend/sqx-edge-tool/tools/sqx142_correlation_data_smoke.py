from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sqx142_correlation_filter_external import (  # noqa: E402
    CORRELATION_FILTER_EXTERNAL_VERSION,
    build_correlation_filter_report,
    export_correlation_filter_sqx_tag_csv,
    parse_correlation_input,
)

DATA_SMOKE_VERSION = "sqx142-own-features2-correlation-data-smoke-v1"
TAG_SCHEMA = [
    "strategyRef",
    "candidateId",
    "decision",
    "reason",
    "score",
    "maxObservedCorrelation",
    "correlationStatus",
    "nearestWinnerId",
    "portfolioRank",
    "c2TemplateRank",
    "decisionDomain",
    "generatedAt",
    "version",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _read_payload(input_path: Path) -> Any:
    text = input_path.read_text(encoding="utf-8-sig")
    if input_path.suffix.lower() == ".json":
        return json.loads(text)
    return text


def _normalize_sqx_databank_export(payload: Any) -> Any:
    rows = parse_correlation_input(payload)
    if not rows:
        return payload
    normalized: list[dict[str, Any]] = []
    for row in rows:
        copy = dict(row)
        has_source = any(
            str(copy.get(key) or "").strip()
            for key in ("forwardSource", "Forward Source", "Foward Source", "sourceDatabank", "Source Databank")
        )
        filters_result = str(copy.get("Filters result") or copy.get("filtersResult") or "").strip()
        if filters_result and not copy.get("Forward Status"):
            copy["Forward Status"] = filters_result
        if filters_result.upper() == "PASSED" and not has_source:
            copy["Source Databank"] = "Foward"
            copy["Source Phase"] = "phase28_capa2_forward"
            copy["Pass Source"] = "operator_databank_export"
        normalized.append(copy)
    return normalized


def _csv_row_count(text: str) -> int:
    rows = list(csv.DictReader(text.splitlines()))
    return len(rows)


def _public_report(report: Mapping[str, Any], tag_csv: str, input_path: Path, output_path: Path) -> dict[str, Any]:
    return {
        "ok": True,
        "version": DATA_SMOKE_VERSION,
        "correlationVersion": report.get("version", CORRELATION_FILTER_EXTERNAL_VERSION),
        "generatedAt": _now_iso(),
        "source": {
            "kind": "operator_csv_or_json",
            "sha256": sha256_file(input_path),
            "rows": int(report.get("summary", {}).get("inputRows") or 0),
        },
        "summary": report.get("summary") or {},
        "tagCsv": {
            "schema": TAG_SCHEMA,
            "rows": _csv_row_count(tag_csv),
            "sha256": sha256_bytes(tag_csv.encode("utf-8")),
            "filename": output_path.name,
        },
        "decisions": {
            "portfolio": int(report.get("summary", {}).get("portfolio") or 0),
            "similar": int(report.get("summary", {}).get("similar") or 0),
            "review": int(report.get("summary", {}).get("review") or 0),
        },
        "privacy": {
            "raw_strategy_names_returned": False,
            "local_paths_returned": False,
            "private_fields_returned": False,
            "tokens_returned": False,
        },
        "guards": {
            "sqx_runtime_started": False,
            "data_db_write_allowed": False,
            "user_projects_write_allowed": False,
            "databank_delete_allowed": False,
            "tag_csv_only": True,
        },
    }


def build_smoke_artifacts(
    input_path: Path,
    output_dir: Path,
    *,
    settings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    input_path = input_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = _normalize_sqx_databank_export(_read_payload(input_path))
    report = build_correlation_filter_report(payload, settings=settings)
    tag_csv = export_correlation_filter_sqx_tag_csv(report)
    output_path = output_dir / "correlation_decisions.csv"
    evidence_path = output_dir / "correlation_data_smoke_public.json"
    output_path.write_text(tag_csv, encoding="utf-8", newline="")
    evidence = _public_report(report, tag_csv, input_path, output_path)
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return {
        **evidence,
        "outputs": {
            "tagCsvPath": str(output_path),
            "evidencePath": str(evidence_path),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build SQX142 Correlation Pack data smoke tag CSV.")
    parser.add_argument("--input", required=True, help="CSV or JSON rows exported for the correlation filter.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated tag CSV and public evidence.")
    parser.add_argument("--settings-json", default="", help="Optional correlation settings JSON object.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    settings = json.loads(args.settings_json) if args.settings_json.strip() else None
    if settings is not None and not isinstance(settings, dict):
        raise SystemExit("--settings-json must be a JSON object")
    result = build_smoke_artifacts(Path(args.input), Path(args.output_dir), settings=settings)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
