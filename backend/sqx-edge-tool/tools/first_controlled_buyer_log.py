from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "first_controlled_buyer_log.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "first_controlled_buyer_log"
DEFAULT_PUBLIC_PAGE_DIR = TOOL_ROOT / "data" / "public_buyer_page_cadence"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_public_page_file(directory: Path = DEFAULT_PUBLIC_PAGE_DIR) -> Path | None:
    return latest_file(directory, "public_buyer_page_cadence_*.json")


def parse_int(value: str, default: int) -> int:
    if value == "":
        return default
    return int(value)


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in config.get("requiredFiles", []):
        if not project_path(str(item)).is_file():
            findings.append(f"missing_required_file:{item}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    cadence_config_path = project_path(str(depends_on.get("publicBuyerPageCadenceConfig", "")))
    if not cadence_config_path.is_file():
        return ["public_buyer_page_cadence_config_missing"]
    cadence_config = load_json(cadence_config_path)
    if cadence_config.get("state") != depends_on.get("publicBuyerPageCadenceState"):
        return ["public_buyer_page_cadence_state_invalid"]
    return []


def validate_public_page_cadence(cadence: dict[str, Any] | None, allow_no_go_cadence: bool) -> list[str]:
    if cadence is None:
        return ["public_buyer_page_cadence_evidence_missing"]
    decision = cadence.get("decision", {})
    if not decision.get("go") and not allow_no_go_cadence:
        return ["public_buyer_page_cadence_not_go", *decision.get("blockers", [])]
    return []


def is_safe_reference(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[@\s<>/\\]", value))


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def operating_checklist() -> list[str]:
    return [
        "Confirm public buyer page cadence evidence is GO.",
        "Record a non-sensitive order reference and sale channel.",
        "Confirm payment, delivery and license activation status.",
        "Record support status, open items, refunds and fulfillment failures.",
        "Summarize buyer feedback without raw messages or personal data.",
        "Decide continue, iterate, follow up or pause before more sales.",
    ]


def decision_from(
    config: dict[str, Any],
    cadence: dict[str, Any] | None,
    order_ref: str,
    sale_channel: str,
    payment_status: str,
    delivery_status: str,
    license_activation_status: str,
    activation_events: int,
    open_support_items: int,
    refund_count: int,
    fulfillment_failures: int,
    first_value_status: str,
    decision: str,
    feedback_summary: str,
    review_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_cadence: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_public_page_cadence(cadence, allow_no_go_cadence))

    if not is_safe_reference(order_ref):
        blockers.append("order_ref_missing_or_unsafe")
    if not is_safe_text(sale_channel):
        blockers.append("sale_channel_missing_or_unsafe")
    if payment_status != "paid":
        blockers.append("payment_not_confirmed_paid")
    if delivery_status != "delivered":
        blockers.append("delivery_not_confirmed")
    if license_activation_status not in {"reviewed", "activated"}:
        blockers.append("license_activation_not_reviewed")
    if activation_events < int(config.get("minimumActivationEvents", 1)):
        blockers.append("activation_events_missing")
    if min(open_support_items, refund_count, fulfillment_failures) < 0:
        blockers.append("first_buyer_metrics_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("post_sale_decision_invalid")
    if not is_safe_text(first_value_status):
        blockers.append("first_value_status_missing_or_unsafe")
    if not feedback_summary.strip():
        blockers.append("feedback_summary_missing")
    if not review_notes.strip():
        blockers.append("review_notes_missing")

    max_support = int(config.get("maximumOpenSupportItemsForContinue", 0))
    max_refunds = int(config.get("maximumRefundsForContinue", 0))
    if fulfillment_failures > 0 and decision != "pause_sales":
        blockers.append("fulfillment_failures_require_pause_sales")
    if refund_count > 0 and decision != "pause_sales":
        blockers.append("refunds_require_pause_sales")
    if open_support_items > 0 and decision == "continue_private_sales":
        blockers.append("continue_private_sales_blocked_by_open_support")
    if decision == "continue_private_sales":
        if open_support_items > max_support or refund_count > max_refunds:
            blockers.append("continue_private_sales_blocked_by_support_or_refunds")
        if first_value_status != "confirmed":
            blockers.append("continue_private_sales_needs_first_value_confirmed")
    if decision == "schedule_followup":
        warnings.append("operator_decision_schedule_followup")
    if decision == "iterate_onboarding":
        warnings.append("operator_decision_iterate_onboarding")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")

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
        "# First Controlled Buyer Operating Log Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Post-sale decision: `{report.get('post_sale_decision') or 'missing'}`",
        f"- Order ref: `{report.get('order_ref') or 'missing'}`",
        f"- First value status: `{report.get('first_value_status') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["operating_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("activation_events", "open_support_items", "refund_count", "fulfillment_failures"):
        lines.append(f"- {name}: `{report[name]}`")
    lines.append("")
    lines.append("## Confirmations")
    for name, value in report["confirmations"].items():
        lines.append(f"- {name}: `{value}`")
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_evidence(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"first_controlled_buyer_log_{current_stamp}.json"
    md_path = output_dir / f"first_controlled_buyer_log_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_first_buyer_log(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    public_page_file: Path | None = None,
    order_ref: str = "",
    sale_channel: str = "",
    payment_status: str = "",
    delivery_status: str = "",
    license_activation_status: str = "",
    activation_events: int = -1,
    open_support_items: int = -1,
    refund_count: int = -1,
    fulfillment_failures: int = -1,
    first_value_status: str = "",
    decision: str = "schedule_followup",
    feedback_summary: str = "",
    review_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_cadence: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    cadence = load_json(public_page_file) if public_page_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "first_controlled_buyer_log_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "public_page_source": str(public_page_file) if public_page_file else "",
        "public_page_decision": cadence.get("decision") if cadence else None,
        "public_page_status": cadence.get("page_status") if cadence else "",
        "order_ref": order_ref.strip(),
        "sale_channel": sale_channel.strip(),
        "payment_status": payment_status.strip(),
        "delivery_status": delivery_status.strip(),
        "license_activation_status": license_activation_status.strip(),
        "activation_events": activation_events,
        "open_support_items": open_support_items,
        "refund_count": refund_count,
        "fulfillment_failures": fulfillment_failures,
        "first_value_status": first_value_status.strip(),
        "post_sale_decision": decision,
        "feedback_summary": feedback_summary.strip(),
        "review_notes": review_notes.strip(),
        "operating_checklist": operating_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        cadence,
        order_ref,
        sale_channel,
        payment_status,
        delivery_status,
        license_activation_status,
        activation_events,
        open_support_items,
        refund_count,
        fulfillment_failures,
        first_value_status,
        decision,
        feedback_summary,
        review_notes,
        final_confirmations,
        allow_no_go_cadence,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Record first controlled buyer operating log and post-sale review.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--public-page-cadence-file", default="")
    parser.add_argument("--use-latest-public-page-cadence", action="store_true")
    parser.add_argument("--allow-no-go-cadence", action="store_true")
    parser.add_argument("--order-ref", default="")
    parser.add_argument("--sale-channel", default="")
    parser.add_argument("--payment-status", default="")
    parser.add_argument("--delivery-status", default="")
    parser.add_argument("--license-activation-status", default="")
    parser.add_argument("--activation-events", default="")
    parser.add_argument("--open-support-items", default="")
    parser.add_argument("--refund-count", default="")
    parser.add_argument("--fulfillment-failures", default="")
    parser.add_argument("--first-value-status", default="")
    parser.add_argument("--decision", default="schedule_followup")
    parser.add_argument("--feedback-summary", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--confirm-public-page-cadence-go", action="store_true")
    parser.add_argument("--confirm-sale-recorded", action="store_true")
    parser.add_argument("--confirm-delivery-confirmed", action="store_true")
    parser.add_argument("--confirm-license-activation-reviewed", action="store_true")
    parser.add_argument("--confirm-support-reviewed", action="store_true")
    parser.add_argument("--confirm-feedback-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-post-sale-decision-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    public_page_file = Path(args.public_page_cadence_file) if args.public_page_cadence_file else None
    if args.use_latest_public_page_cadence and public_page_file is None:
        public_page_file = latest_public_page_file()
        if public_page_file is None:
            print(json.dumps({"ok": False, "error": "public_buyer_page_cadence_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "public_page_cadence_go": args.confirm_public_page_cadence_go,
        "sale_recorded": args.confirm_sale_recorded,
        "delivery_confirmed": args.confirm_delivery_confirmed,
        "license_activation_reviewed": args.confirm_license_activation_reviewed,
        "support_reviewed": args.confirm_support_reviewed,
        "feedback_reviewed": args.confirm_feedback_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "post_sale_decision_recorded": args.confirm_post_sale_decision_recorded,
    }
    report = collect_first_buyer_log(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        public_page_file=public_page_file,
        order_ref=args.order_ref,
        sale_channel=args.sale_channel,
        payment_status=args.payment_status,
        delivery_status=args.delivery_status,
        license_activation_status=args.license_activation_status,
        activation_events=parse_int(args.activation_events, -1),
        open_support_items=parse_int(args.open_support_items, -1),
        refund_count=parse_int(args.refund_count, -1),
        fulfillment_failures=parse_int(args.fulfillment_failures, -1),
        first_value_status=args.first_value_status,
        decision=args.decision.strip(),
        feedback_summary=args.feedback_summary,
        review_notes=args.review_notes,
        confirmations=confirmations,
        allow_no_go_cadence=args.allow_no_go_cadence,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
