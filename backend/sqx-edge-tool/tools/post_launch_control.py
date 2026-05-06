from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "post_launch_control"
DEFAULT_LIMITED_LAUNCH_DIR = TOOL_ROOT / "data" / "limited_public_launch"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"
VALID_DECISIONS = ("continue_limited", "scale_public", "pause_sales", "rollback")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_limited_launch_file(directory: Path = DEFAULT_LIMITED_LAUNCH_DIR) -> Path | None:
    return latest_file(directory, "limited_public_launch_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def parse_int(value: str, default: int) -> int:
    if value == "":
        return default
    return int(value)


def post_launch_checklist() -> list[str]:
    return [
        "Review paid orders, activations, support tickets, refunds and failed fulfillments.",
        "Confirm every paid customer has a delivery path or an explicit support owner.",
        "Classify feedback as bug, friction, documentation, pricing or feature request.",
        "Decide continue limited, scale public, pause sales or rollback.",
        "Record the next review date before changing checkout visibility.",
        "Keep rollback path available until activation and support metrics stabilize.",
    ]


def escalation_rules() -> list[str]:
    return [
        "Scale public only with no failed fulfillments and no unresolved support tickets.",
        "Continue limited when sales work but support confidence is still forming.",
        "Pause sales when activation, delivery or support quality is unclear.",
        "Rollback when paid delivery cannot be completed reliably.",
    ]


def decision_from(
    limited_launch: dict[str, Any] | None,
    zip_path: Path | None,
    sales_count: int,
    activation_count: int,
    support_ticket_count: int,
    unresolved_ticket_count: int,
    refund_count: int,
    failed_fulfillment_count: int,
    review_window: str,
    decision_owner: str,
    scale_decision: str,
    metrics_reviewed: bool,
    support_sla_confirmed: bool,
    allow_no_go_launch: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if limited_launch is None:
        blockers.append("limited_public_launch_missing")
    elif not limited_launch.get("decision", {}).get("go") and not allow_no_go_launch:
        blockers.append("limited_public_launch_not_go")
        blockers.extend(limited_launch.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if sales_count < 1:
        blockers.append("no_paid_sales_recorded")
    if activation_count < 0 or support_ticket_count < 0 or unresolved_ticket_count < 0 or refund_count < 0 or failed_fulfillment_count < 0:
        blockers.append("post_launch_metrics_missing")
    if activation_count > sales_count:
        blockers.append("activation_count_exceeds_sales")
    if refund_count > sales_count:
        blockers.append("refund_count_exceeds_sales")
    expected_active_customers = max(sales_count - refund_count, 0)
    if sales_count > 0 and activation_count < expected_active_customers:
        blockers.append("activations_below_paid_sales")
    if unresolved_ticket_count > support_ticket_count:
        blockers.append("unresolved_tickets_exceed_total")
    if unresolved_ticket_count > 0:
        blockers.append("unresolved_support_tickets")
    if failed_fulfillment_count > 0:
        blockers.append("failed_fulfillment_present")
    if sales_count > 0 and refund_count / sales_count > 0.2:
        blockers.append("refund_rate_above_tolerance")
    if not review_window.strip():
        blockers.append("review_window_missing")
    if not decision_owner.strip():
        blockers.append("decision_owner_missing")
    if scale_decision not in VALID_DECISIONS:
        blockers.append("scale_decision_invalid")
    if not metrics_reviewed:
        blockers.append("metrics_not_reviewed")
    if not support_sla_confirmed:
        blockers.append("support_sla_not_confirmed")
    if scale_decision == "scale_public" and (sales_count < 3 or unresolved_ticket_count > 0 or failed_fulfillment_count > 0):
        blockers.append("scale_public_not_supported_by_metrics")
    if scale_decision in ("pause_sales", "rollback"):
        warnings.append(f"operator_decision_{scale_decision}")
    if support_ticket_count > sales_count:
        warnings.append("support_ticket_count_above_sales")

    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# SQX Edge Post Launch Control",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Limited launch source: `{report.get('limited_launch_source') or 'none'}`",
        f"- Scale decision: `{report.get('scale_decision')}`",
        f"- Sales: `{report.get('sales_count')}`",
        f"- Activations: `{report.get('activation_count')}`",
        f"- Support tickets: `{report.get('support_ticket_count')}`",
        f"- Unresolved tickets: `{report.get('unresolved_ticket_count')}`",
        f"- Refunds: `{report.get('refund_count')}`",
        f"- Failed fulfillments: `{report.get('failed_fulfillment_count')}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["post_launch_checklist"])
    lines.append("")
    lines.append("## Escalation Rules")
    lines.extend(f"- {item}" for item in report["escalation_rules"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_control(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"post_launch_control_{current_stamp}.json"
    md_path = output_dir / f"post_launch_control_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_control(
    manifest_path: Path = DEFAULT_MANIFEST,
    limited_launch_file: Path | None = None,
    zip_path: Path | None = None,
    sales_count: int = -1,
    activation_count: int = -1,
    support_ticket_count: int = -1,
    unresolved_ticket_count: int = -1,
    refund_count: int = -1,
    failed_fulfillment_count: int = -1,
    review_window: str = "",
    decision_owner: str = "",
    scale_decision: str = "continue_limited",
    metrics_reviewed: bool = False,
    support_sla_confirmed: bool = False,
    allow_no_go_launch: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    final_zip = zip_path or latest_portable_zip()
    limited_launch = load_json(limited_launch_file) if limited_launch_file else None
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "limited_launch_source": str(limited_launch_file) if limited_launch_file else "",
        "limited_launch_decision": limited_launch.get("decision") if limited_launch else None,
        "zip_path": str(final_zip) if final_zip else "",
        "sales_count": sales_count,
        "activation_count": activation_count,
        "support_ticket_count": support_ticket_count,
        "unresolved_ticket_count": unresolved_ticket_count,
        "refund_count": refund_count,
        "failed_fulfillment_count": failed_fulfillment_count,
        "review_window": review_window,
        "decision_owner": decision_owner,
        "scale_decision": scale_decision,
        "metrics_reviewed": metrics_reviewed,
        "support_sla_confirmed": support_sla_confirmed,
        "post_launch_checklist": post_launch_checklist(),
        "escalation_rules": escalation_rules(),
        "decision": decision_from(
            limited_launch,
            final_zip,
            sales_count,
            activation_count,
            support_ticket_count,
            unresolved_ticket_count,
            refund_count,
            failed_fulfillment_count,
            review_window,
            decision_owner,
            scale_decision,
            metrics_reviewed,
            support_sla_confirmed,
            allow_no_go_launch,
        ),
    }
    if write:
        report["evidence_paths"] = write_control(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge post-launch control gate")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--limited-launch-file", default="")
    parser.add_argument("--use-latest-limited-launch", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--sales-count", type=int, default=parse_int(env_value("SQX_POST_LAUNCH_SALES_COUNT"), -1))
    parser.add_argument("--activation-count", type=int, default=parse_int(env_value("SQX_POST_LAUNCH_ACTIVATION_COUNT"), -1))
    parser.add_argument("--support-ticket-count", type=int, default=parse_int(env_value("SQX_POST_LAUNCH_SUPPORT_TICKET_COUNT"), -1))
    parser.add_argument("--unresolved-ticket-count", type=int, default=parse_int(env_value("SQX_POST_LAUNCH_UNRESOLVED_TICKET_COUNT"), -1))
    parser.add_argument("--refund-count", type=int, default=parse_int(env_value("SQX_POST_LAUNCH_REFUND_COUNT"), -1))
    parser.add_argument("--failed-fulfillment-count", type=int, default=parse_int(env_value("SQX_POST_LAUNCH_FAILED_FULFILLMENT_COUNT"), -1))
    parser.add_argument("--review-window", default=env_value("SQX_POST_LAUNCH_REVIEW_WINDOW"))
    parser.add_argument("--decision-owner", default=env_value("SQX_POST_LAUNCH_DECISION_OWNER"))
    parser.add_argument("--scale-decision", default=env_value("SQX_POST_LAUNCH_SCALE_DECISION", "continue_limited"), choices=VALID_DECISIONS)
    parser.add_argument("--confirm-metrics-reviewed", action="store_true")
    parser.add_argument("--confirm-support-sla", action="store_true")
    parser.add_argument("--allow-no-go-launch", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    limited_launch_file = Path(args.limited_launch_file) if args.limited_launch_file else None
    if args.use_latest_limited_launch and limited_launch_file is None:
        limited_launch_file = latest_limited_launch_file()
        if limited_launch_file is None:
            print(json.dumps({"ok": False, "error": "limited_public_launch_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_control(
        manifest_path=Path(args.manifest),
        limited_launch_file=limited_launch_file,
        zip_path=Path(args.zip) if args.zip else None,
        sales_count=args.sales_count,
        activation_count=args.activation_count,
        support_ticket_count=args.support_ticket_count,
        unresolved_ticket_count=args.unresolved_ticket_count,
        refund_count=args.refund_count,
        failed_fulfillment_count=args.failed_fulfillment_count,
        review_window=args.review_window,
        decision_owner=args.decision_owner,
        scale_decision=args.scale_decision,
        metrics_reviewed=args.confirm_metrics_reviewed,
        support_sla_confirmed=args.confirm_support_sla,
        allow_no_go_launch=args.allow_no_go_launch,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
