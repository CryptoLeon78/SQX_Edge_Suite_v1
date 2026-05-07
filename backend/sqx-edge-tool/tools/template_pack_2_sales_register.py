from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_2_sales_register.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_2_sales_register"
DEFAULT_HANDOFF_DIR = TOOL_ROOT / "data" / "template_pack_2_handoff"


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


def latest_handoff_file(directory: Path = DEFAULT_HANDOFF_DIR) -> Path | None:
    return latest_file(directory, "template_pack_2_handoff_*.json")


def is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def redact_email(value: str) -> str:
    if not is_email(value):
        return ""
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"


def parse_int(value: str, default: int) -> int:
    if value == "":
        return default
    return int(value)


def parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return Decimal("-1")


def decimal_string(value: Decimal) -> str:
    if value < 0:
        return ""
    return format(value.quantize(Decimal("0.01")), "f")


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in config.get("requiredFiles", []):
        if not project_path(str(item)).is_file():
            findings.append(f"missing_required_file:{item}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    handoff_config_path = project_path(str(depends_on.get("handoffConfig", "")))
    if not handoff_config_path.is_file():
        return ["template_pack_2_handoff_config_missing"]
    handoff_config = load_json(handoff_config_path)
    if handoff_config.get("state") != depends_on.get("handoffState"):
        return ["template_pack_2_handoff_state_invalid"]
    return []


def validate_handoff(handoff: dict[str, Any] | None, allow_no_go_handoff: bool) -> list[str]:
    if handoff is None:
        return ["template_pack_2_handoff_evidence_missing"]
    decision = handoff.get("decision", {})
    if not decision.get("go") and not allow_no_go_handoff:
        return ["template_pack_2_handoff_not_go", *decision.get("blockers", [])]
    return []


def sales_register_checklist() -> list[str]:
    return [
        "Confirm handoff evidence and order reference.",
        "Record sale channel, paid amount, currency and add-on sale status.",
        "Record delivery status separately from the base portable ZIP.",
        "Record support status, open support items, refunds and fulfillment failures.",
        "Keep buyer data redacted and avoid raw provider payloads.",
        "Decide keep_tracking, scale_limited or pause_sales before opening more traffic.",
    ]


def decision_from(
    config: dict[str, Any],
    handoff: dict[str, Any] | None,
    buyer_email: str,
    buyer_id: str,
    provider_order_id: str,
    sale_channel: str,
    sale_status: str,
    amount: Decimal,
    currency: str,
    delivery_status: str,
    support_status: str,
    sales_count: int,
    open_support_items: int,
    refund_count: int,
    fulfillment_failures: int,
    scale_decision: str,
    register_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_handoff: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_handoff(handoff, allow_no_go_handoff))

    if not buyer_id and not is_email(buyer_email):
        blockers.append("buyer_reference_missing_or_invalid")
    if not provider_order_id:
        blockers.append("provider_order_id_missing")
    if sale_channel not in set(config.get("allowedChannels", [])):
        blockers.append("sale_channel_invalid")
    if sale_status not in set(config.get("allowedSaleStatuses", [])):
        blockers.append("sale_status_invalid")
    if amount <= 0:
        blockers.append("amount_invalid")
    if currency.upper() not in {"EUR", "USD", "GBP"}:
        blockers.append("currency_invalid")
    if delivery_status not in set(config.get("allowedDeliveryStatuses", [])):
        blockers.append("delivery_status_invalid")
    if support_status not in set(config.get("allowedSupportStatuses", [])):
        blockers.append("support_status_invalid")
    if scale_decision not in set(config.get("allowedDecisions", [])):
        blockers.append("scale_decision_invalid")
    if any(value < 0 for value in (sales_count, open_support_items, refund_count, fulfillment_failures)):
        blockers.append("sales_register_metrics_invalid")
    if not register_notes.strip():
        blockers.append("register_notes_missing")

    if sale_status != "paid" and scale_decision != "pause_sales":
        blockers.append("non_paid_sale_requires_pause_sales")
    if delivery_status != "delivered" and scale_decision != "pause_sales":
        blockers.append("delivery_not_confirmed_requires_pause_sales")
    if support_status == "needs_review" and scale_decision == "scale_limited":
        blockers.append("support_review_blocks_scale_limited")

    max_open_support = int(config.get("maxOpenSupportItemsForScale", 0))
    max_refunds = int(config.get("maxRefundsForScale", 0))
    max_failures = int(config.get("maxFulfillmentFailuresForScale", 0))
    minimum_sales = int(config.get("minimumSalesForScale", 1))

    if open_support_items > max_open_support and scale_decision != "pause_sales":
        blockers.append("open_support_items_require_pause_or_review")
    if refund_count > max_refunds and scale_decision != "pause_sales":
        blockers.append("refunds_require_pause_sales")
    if fulfillment_failures > max_failures and scale_decision != "pause_sales":
        blockers.append("fulfillment_failures_require_pause_sales")
    if scale_decision == "scale_limited":
        if sales_count < minimum_sales:
            blockers.append("scale_limited_needs_minimum_sales")
        if open_support_items > 0 or refund_count > 0 or fulfillment_failures > 0:
            blockers.append("scale_limited_not_supported_by_register")
    if scale_decision == "keep_tracking":
        warnings.append("operator_decision_keep_tracking")
    if scale_decision == "pause_sales":
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
        "# Template Pack 2 Add-On Sales Register Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Buyer: `{report.get('buyer_email_redacted') or report.get('buyer_id') or 'missing'}`",
        f"- Order: `{report.get('provider_order_id') or 'missing'}`",
        f"- Sale status: `{report.get('sale_status') or 'missing'}`",
        f"- Delivery status: `{report.get('delivery_status') or 'missing'}`",
        f"- Support status: `{report.get('support_status') or 'missing'}`",
        f"- Scale decision: `{report.get('scale_decision') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["sales_register_checklist"])
    lines.append("")
    lines.append("## Confirmations")
    for name, value in report["confirmations"].items():
        lines.append(f"- {name}: `{value}`")
    lines.append("")
    lines.append("## Metrics")
    for name in ("sales_count", "open_support_items", "refund_count", "fulfillment_failures"):
        lines.append(f"- {name}: `{report[name]}`")
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def register_record(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "created_at": report["created_at"],
        "state": report["state"],
        "buyer_reference": report.get("buyer_email_redacted") or report.get("buyer_id") or "",
        "provider_order_id": report.get("provider_order_id", ""),
        "sale_channel": report.get("sale_channel", ""),
        "sale_status": report.get("sale_status", ""),
        "amount": report.get("amount", ""),
        "currency": report.get("currency", ""),
        "delivery_status": report.get("delivery_status", ""),
        "support_status": report.get("support_status", ""),
        "sales_count": report.get("sales_count", 0),
        "open_support_items": report.get("open_support_items", 0),
        "refund_count": report.get("refund_count", 0),
        "fulfillment_failures": report.get("fulfillment_failures", 0),
        "scale_decision": report.get("scale_decision", ""),
        "decision": report["decision"],
    }


def write_evidence(report: dict[str, Any], output_dir: Path, append_register: bool) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"template_pack_2_sales_register_{current_stamp}.json"
    md_path = output_dir / f"template_pack_2_sales_register_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    paths = {"json": str(json_path), "markdown": str(md_path)}
    if append_register:
        register_path = output_dir / "template_pack_2_sales_register.jsonl"
        with register_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(register_record(report), sort_keys=True) + "\n")
        paths["register"] = str(register_path)
    return paths


def collect_sales_register(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    handoff_file: Path | None = None,
    buyer_email: str = "",
    buyer_id: str = "",
    provider_order_id: str = "",
    sale_channel: str = "Lemon Squeezy",
    sale_status: str = "paid",
    amount: Decimal = Decimal("-1"),
    currency: str = "EUR",
    delivery_status: str = "delivered",
    support_status: str = "open",
    sales_count: int = -1,
    open_support_items: int = -1,
    refund_count: int = -1,
    fulfillment_failures: int = -1,
    scale_decision: str = "keep_tracking",
    register_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_handoff: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    append_register: bool = False,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    handoff = load_json(handoff_file) if handoff_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_2_sales_register_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "handoff_source": str(handoff_file) if handoff_file else "",
        "handoff_decision": handoff.get("decision") if handoff else None,
        "buyer_email": "",
        "buyer_email_redacted": redact_email(buyer_email),
        "buyer_id": buyer_id,
        "provider_order_id": provider_order_id,
        "sale_channel": sale_channel,
        "sale_status": sale_status,
        "amount": decimal_string(amount),
        "currency": currency.upper(),
        "delivery_status": delivery_status,
        "support_status": support_status,
        "sales_count": sales_count,
        "open_support_items": open_support_items,
        "refund_count": refund_count,
        "fulfillment_failures": fulfillment_failures,
        "scale_decision": scale_decision,
        "register_notes": register_notes.strip(),
        "sales_register_checklist": sales_register_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        handoff,
        buyer_email,
        buyer_id,
        provider_order_id,
        sale_channel,
        sale_status,
        amount,
        currency,
        delivery_status,
        support_status,
        sales_count,
        open_support_items,
        refund_count,
        fulfillment_failures,
        scale_decision,
        register_notes,
        final_confirmations,
        allow_no_go_handoff,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir, append_register)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Template Pack 2 add-on sales register before scaling traffic.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--handoff-file", default="")
    parser.add_argument("--use-latest-handoff", action="store_true")
    parser.add_argument("--allow-no-go-handoff", action="store_true")
    parser.add_argument("--buyer-email", default="")
    parser.add_argument("--buyer-id", default="")
    parser.add_argument("--provider-order-id", default="")
    parser.add_argument("--sale-channel", default="Lemon Squeezy")
    parser.add_argument("--sale-status", default="paid")
    parser.add_argument("--amount", default="")
    parser.add_argument("--currency", default="EUR")
    parser.add_argument("--delivery-status", default="delivered")
    parser.add_argument("--support-status", default="open")
    parser.add_argument("--sales-count", default="")
    parser.add_argument("--open-support-items", default="")
    parser.add_argument("--refund-count", default="")
    parser.add_argument("--fulfillment-failures", default="")
    parser.add_argument("--scale-decision", default="keep_tracking")
    parser.add_argument("--register-notes", default="")
    parser.add_argument("--confirm-handoff-go", action="store_true")
    parser.add_argument("--confirm-sale-recorded", action="store_true")
    parser.add_argument("--confirm-delivery-status-recorded", action="store_true")
    parser.add_argument("--confirm-support-status-recorded", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-scale-decision-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--append-register", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    handoff_file = Path(args.handoff_file) if args.handoff_file else None
    if args.use_latest_handoff and handoff_file is None:
        handoff_file = latest_handoff_file()
        if handoff_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_2_handoff_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "handoff_go": args.confirm_handoff_go,
        "sale_recorded": args.confirm_sale_recorded,
        "delivery_status_recorded": args.confirm_delivery_status_recorded,
        "support_status_recorded": args.confirm_support_status_recorded,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "scale_decision_recorded": args.confirm_scale_decision_recorded,
    }
    report = collect_sales_register(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        handoff_file=handoff_file,
        buyer_email=args.buyer_email.strip(),
        buyer_id=args.buyer_id.strip(),
        provider_order_id=args.provider_order_id.strip(),
        sale_channel=args.sale_channel.strip(),
        sale_status=args.sale_status.strip(),
        amount=parse_decimal(args.amount),
        currency=args.currency.strip(),
        delivery_status=args.delivery_status.strip(),
        support_status=args.support_status.strip(),
        sales_count=parse_int(args.sales_count, -1),
        open_support_items=parse_int(args.open_support_items, -1),
        refund_count=parse_int(args.refund_count, -1),
        fulfillment_failures=parse_int(args.fulfillment_failures, -1),
        scale_decision=args.scale_decision.strip(),
        register_notes=args.register_notes,
        confirmations=confirmations,
        allow_no_go_handoff=args.allow_no_go_handoff,
        output_dir=Path(args.output_dir),
        append_register=args.append_register,
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

