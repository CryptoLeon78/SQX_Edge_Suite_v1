from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "post_release_monitor"
DEFAULT_RELEASE_PUBLICATION_RECORD_DIR = TOOL_ROOT / "data" / "release_publication_record"
DECISIONS = {"maintain_public", "pause_public", "hotfix_required", "rollback", "scale_public"}


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_release_publication_record_file(directory: Path = DEFAULT_RELEASE_PUBLICATION_RECORD_DIR) -> Path | None:
    return latest_file(directory, "release_publication_record_*.json")


def safe_rate(numerator: int, denominator: int) -> float:
    return 0.0 if denominator <= 0 else numerator / denominator


def monitor_evidence_list() -> list[str]:
    return [
        "downloads_reviewed",
        "paid_sales_reviewed",
        "activations_reviewed",
        "support_tickets_triaged",
        "activation_errors_reviewed",
        "refunds_reviewed",
        "fulfillment_failures_reviewed",
        "rollback_available",
        "hotfix_path_ready",
        "decision_owner_assigned",
    ]


def decision_from(
    release_publication_record: dict[str, Any] | None,
    downloads: int,
    paid_sales: int,
    activations: int,
    support_tickets_open: int,
    severe_incidents_open: int,
    activation_errors: int,
    refunds: int,
    fulfillment_failures_open: int,
    hours_since_release: int,
    decision: str,
    decision_owner: str,
    support_triaged: bool,
    rollback_available: bool,
    hotfix_path_ready: bool,
    allow_no_go_publication: bool,
    max_activation_error_rate: float,
    max_refund_rate: float,
    min_hours_before_scale: int,
    min_paid_sales_before_scale: int,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    activation_error_rate = safe_rate(activation_errors, max(activations, paid_sales))
    refund_rate = safe_rate(refunds, paid_sales)

    if release_publication_record is None:
        blockers.append("release_publication_record_missing")
    elif not release_publication_record.get("decision", {}).get("go") and not allow_no_go_publication:
        blockers.append("release_publication_record_not_go")
        blockers.extend(release_publication_record.get("decision", {}).get("blockers", []))
    if decision not in DECISIONS:
        blockers.append("post_release_decision_missing_or_invalid")
    if not decision_owner:
        blockers.append("decision_owner_missing")
    if not support_triaged:
        blockers.append("support_not_triaged")
    if support_tickets_open > 0:
        blockers.append("support_tickets_open")
    if severe_incidents_open > 0:
        blockers.append("severe_incidents_open")
    if activation_error_rate > max_activation_error_rate:
        blockers.append("activation_error_rate_high")
    if refund_rate > max_refund_rate:
        blockers.append("refund_rate_high")
    if fulfillment_failures_open > 0:
        blockers.append("fulfillment_failures_open")
    if not rollback_available:
        blockers.append("rollback_not_available")
    if not hotfix_path_ready:
        blockers.append("hotfix_path_not_ready")
    if decision == "scale_public":
        if hours_since_release < min_hours_before_scale:
            blockers.append("scale_public_before_monitor_window")
        if paid_sales < min_paid_sales_before_scale:
            blockers.append("scale_public_without_minimum_sales")
        if downloads <= 0:
            blockers.append("scale_public_without_download_signal")
    if decision in {"maintain_public", "scale_public"} and paid_sales == 0:
        warnings.append("no_paid_sales_recorded")
    if decision == "rollback" and severe_incidents_open == 0 and activation_errors == 0:
        warnings.append("rollback_without_recorded_incident_signal")

    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
        "activation_error_rate": round(activation_error_rate, 4),
        "refund_rate": round(refund_rate, 4),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# SQX Edge Post Release Monitor",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Proposed action: `{report.get('post_release_decision') or 'missing'}`",
        f"- Release publication record source: `{report.get('release_publication_record_source') or 'none'}`",
        f"- Downloads: `{report['downloads']}`",
        f"- Paid sales: `{report['paid_sales']}`",
        f"- Activations: `{report['activations']}`",
        f"- Activation error rate: `{decision['activation_error_rate']}`",
        f"- Refund rate: `{decision['refund_rate']}`",
        "",
        "## Monitor Evidence",
    ]
    lines.extend(f"- {item}" for item in report["monitor_evidence"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_monitor(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"post_release_monitor_{current_stamp}.json"
    md_path = output_dir / f"post_release_monitor_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_monitor(
    manifest_path: Path = DEFAULT_MANIFEST,
    release_publication_record_file: Path | None = None,
    downloads: int = 0,
    paid_sales: int = 0,
    activations: int = 0,
    support_tickets_open: int = 0,
    severe_incidents_open: int = 0,
    activation_errors: int = 0,
    refunds: int = 0,
    fulfillment_failures_open: int = 0,
    hours_since_release: int = 0,
    post_release_decision: str = "",
    decision_owner: str = "",
    support_triaged: bool = False,
    rollback_available: bool = False,
    hotfix_path_ready: bool = False,
    allow_no_go_publication: bool = False,
    max_activation_error_rate: float = 0.05,
    max_refund_rate: float = 0.05,
    min_hours_before_scale: int = 24,
    min_paid_sales_before_scale: int = 3,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    release_publication_record = load_json(release_publication_record_file) if release_publication_record_file else None
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "release_publication_record_source": str(release_publication_record_file) if release_publication_record_file else "",
        "release_publication_record_decision": release_publication_record.get("decision") if release_publication_record else None,
        "downloads": downloads,
        "paid_sales": paid_sales,
        "activations": activations,
        "support_tickets_open": support_tickets_open,
        "severe_incidents_open": severe_incidents_open,
        "activation_errors": activation_errors,
        "refunds": refunds,
        "fulfillment_failures_open": fulfillment_failures_open,
        "hours_since_release": hours_since_release,
        "post_release_decision": post_release_decision,
        "decision_owner": decision_owner,
        "support_triaged": support_triaged,
        "rollback_available": rollback_available,
        "hotfix_path_ready": hotfix_path_ready,
        "monitor_evidence": monitor_evidence_list(),
        "decision": decision_from(
            release_publication_record,
            downloads,
            paid_sales,
            activations,
            support_tickets_open,
            severe_incidents_open,
            activation_errors,
            refunds,
            fulfillment_failures_open,
            hours_since_release,
            post_release_decision,
            decision_owner,
            support_triaged,
            rollback_available,
            hotfix_path_ready,
            allow_no_go_publication,
            max_activation_error_rate,
            max_refund_rate,
            min_hours_before_scale,
            min_paid_sales_before_scale,
        ),
    }
    if write:
        report["evidence_paths"] = write_monitor(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge post release monitor")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--release-publication-record-file", default="")
    parser.add_argument("--use-latest-release-publication-record", action="store_true")
    parser.add_argument("--downloads", type=int, default=0)
    parser.add_argument("--paid-sales", type=int, default=0)
    parser.add_argument("--activations", type=int, default=0)
    parser.add_argument("--support-tickets-open", type=int, default=0)
    parser.add_argument("--severe-incidents-open", type=int, default=0)
    parser.add_argument("--activation-errors", type=int, default=0)
    parser.add_argument("--refunds", type=int, default=0)
    parser.add_argument("--fulfillment-failures-open", type=int, default=0)
    parser.add_argument("--hours-since-release", type=int, default=0)
    parser.add_argument("--decision", default=env_value("SQX_POST_RELEASE_DECISION"))
    parser.add_argument("--decision-owner", default=env_value("SQX_POST_RELEASE_DECISION_OWNER"))
    parser.add_argument("--confirm-support-triaged", action="store_true")
    parser.add_argument("--confirm-rollback-available", action="store_true")
    parser.add_argument("--confirm-hotfix-path-ready", action="store_true")
    parser.add_argument("--allow-no-go-publication", action="store_true")
    parser.add_argument("--max-activation-error-rate", type=float, default=0.05)
    parser.add_argument("--max-refund-rate", type=float, default=0.05)
    parser.add_argument("--min-hours-before-scale", type=int, default=24)
    parser.add_argument("--min-paid-sales-before-scale", type=int, default=3)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    record_file = Path(args.release_publication_record_file) if args.release_publication_record_file else None
    if args.use_latest_release_publication_record and record_file is None:
        record_file = latest_release_publication_record_file()
        if record_file is None:
            print(json.dumps({"ok": False, "error": "release_publication_record_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_monitor(
        manifest_path=Path(args.manifest),
        release_publication_record_file=record_file,
        downloads=args.downloads,
        paid_sales=args.paid_sales,
        activations=args.activations,
        support_tickets_open=args.support_tickets_open,
        severe_incidents_open=args.severe_incidents_open,
        activation_errors=args.activation_errors,
        refunds=args.refunds,
        fulfillment_failures_open=args.fulfillment_failures_open,
        hours_since_release=args.hours_since_release,
        post_release_decision=args.decision,
        decision_owner=args.decision_owner,
        support_triaged=args.confirm_support_triaged,
        rollback_available=args.confirm_rollback_available,
        hotfix_path_ready=args.confirm_hotfix_path_ready,
        allow_no_go_publication=args.allow_no_go_publication,
        max_activation_error_rate=args.max_activation_error_rate,
        max_refund_rate=args.max_refund_rate,
        min_hours_before_scale=args.min_hours_before_scale,
        min_paid_sales_before_scale=args.min_paid_sales_before_scale,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
