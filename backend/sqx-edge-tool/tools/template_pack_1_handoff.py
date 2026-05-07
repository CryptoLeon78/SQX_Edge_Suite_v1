from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_1_handoff.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_1_handoff"
DEFAULT_PURCHASE_DRILL_DIR = TOOL_ROOT / "data" / "template_pack_1_purchase_drill"


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


def latest_purchase_drill_file(directory: Path = DEFAULT_PURCHASE_DRILL_DIR) -> Path | None:
    return latest_file(directory, "template_pack_1_purchase_drill_*.json")


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


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in config.get("requiredFiles", []):
        if not project_path(str(item)).is_file():
            findings.append(f"missing_required_file:{item}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    purchase_config_path = project_path(str(depends_on.get("purchaseDrillConfig", "")))
    if not purchase_config_path.is_file():
        return ["template_pack_1_purchase_drill_config_missing"]
    purchase_config = load_json(purchase_config_path)
    if purchase_config.get("state") != depends_on.get("purchaseDrillState"):
        return ["template_pack_1_purchase_drill_state_invalid"]
    return []


def validate_purchase_drill(purchase_drill: dict[str, Any] | None, allow_no_go_purchase_drill: bool) -> list[str]:
    if purchase_drill is None:
        return ["template_pack_1_purchase_drill_evidence_missing"]
    decision = purchase_drill.get("decision", {})
    if not decision.get("go") and not allow_no_go_purchase_drill:
        return ["template_pack_1_purchase_drill_not_go", *decision.get("blockers", [])]
    return []


def handoff_checklist() -> list[str]:
    return [
        "Confirm purchase drill evidence and order reference.",
        "Confirm add-on ZIP delivery was sent separately from the base portable ZIP.",
        "Confirm buyer acknowledged receipt or first run.",
        "Open a support window and record first response timing.",
        "Record first value without promising financial results.",
        "Decide scale_limited, hold_review or pause_sales.",
    ]


def decision_from(
    config: dict[str, Any],
    purchase_drill: dict[str, Any] | None,
    buyer_email: str,
    buyer_id: str,
    provider_order_id: str,
    handoff_owner: str,
    support_ticket_id: str,
    first_response_hours: int,
    unresolved_support_items: int,
    refund_risk_flags: int,
    scale_decision: str,
    handoff_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_purchase_drill: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    allowed_decisions = set(config.get("allowedDecisions", []))
    max_first_response_hours = int(config.get("maxFirstResponseHours", 24))

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_purchase_drill(purchase_drill, allow_no_go_purchase_drill))

    if not buyer_id and not is_email(buyer_email):
        blockers.append("buyer_reference_missing_or_invalid")
    if not provider_order_id:
        blockers.append("provider_order_id_missing")
    if not handoff_owner:
        blockers.append("handoff_owner_missing")
    if not support_ticket_id:
        blockers.append("support_ticket_id_missing")
    if first_response_hours < 0:
        blockers.append("first_response_hours_invalid")
    elif first_response_hours > max_first_response_hours:
        blockers.append("support_first_response_sla_missed")
    if unresolved_support_items < 0 or refund_risk_flags < 0:
        blockers.append("handoff_metrics_invalid")
    if unresolved_support_items > 0:
        blockers.append("unresolved_support_items")
    if refund_risk_flags > 0 and scale_decision != "pause_sales":
        blockers.append("refund_risk_requires_pause_sales")
    if scale_decision not in allowed_decisions:
        blockers.append("scale_decision_invalid")
    if not handoff_notes.strip():
        blockers.append("handoff_notes_missing")
    if scale_decision == "scale_limited":
        if not confirmations.get("buyer_acknowledged") or not confirmations.get("first_value_confirmed"):
            blockers.append("scale_limited_needs_buyer_acknowledgement_and_first_value")
        if unresolved_support_items > 0 or refund_risk_flags > 0:
            blockers.append("scale_limited_not_supported_by_handoff")
    if scale_decision == "hold_review":
        warnings.append("operator_decision_hold_review")
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
        "# Template Pack 1 Post-Purchase Handoff Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Buyer: `{report.get('buyer_email_redacted') or report.get('buyer_id') or 'missing'}`",
        f"- Order: `{report.get('provider_order_id') or 'missing'}`",
        f"- Handoff owner: `{report.get('handoff_owner') or 'missing'}`",
        f"- Support ticket: `{report.get('support_ticket_id') or 'missing'}`",
        f"- Scale decision: `{report.get('scale_decision') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["handoff_checklist"])
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
    json_path = output_dir / f"template_pack_1_handoff_{current_stamp}.json"
    md_path = output_dir / f"template_pack_1_handoff_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_handoff(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    purchase_drill_file: Path | None = None,
    buyer_email: str = "",
    buyer_id: str = "",
    provider_order_id: str = "",
    handoff_owner: str = "",
    support_ticket_id: str = "",
    first_response_hours: int = -1,
    unresolved_support_items: int = -1,
    refund_risk_flags: int = -1,
    scale_decision: str = "hold_review",
    handoff_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_purchase_drill: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    purchase_drill = load_json(purchase_drill_file) if purchase_drill_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_1_handoff_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "purchase_drill_source": str(purchase_drill_file) if purchase_drill_file else "",
        "purchase_drill_decision": purchase_drill.get("decision") if purchase_drill else None,
        "buyer_email": "",
        "buyer_email_redacted": redact_email(buyer_email),
        "buyer_id": buyer_id,
        "provider_order_id": provider_order_id,
        "handoff_owner": handoff_owner,
        "support_ticket_id": support_ticket_id,
        "first_response_hours": first_response_hours,
        "unresolved_support_items": unresolved_support_items,
        "refund_risk_flags": refund_risk_flags,
        "scale_decision": scale_decision,
        "handoff_notes": handoff_notes.strip(),
        "handoff_checklist": handoff_checklist(),
        "confirmations": final_confirmations,
        "decision": decision_from(
            config,
            purchase_drill,
            buyer_email,
            buyer_id,
            provider_order_id,
            handoff_owner,
            support_ticket_id,
            first_response_hours,
            unresolved_support_items,
            refund_risk_flags,
            scale_decision,
            handoff_notes,
            final_confirmations,
            allow_no_go_purchase_drill,
        ),
    }
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Template Pack 1 post-purchase handoff and scale decision.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--purchase-drill-file", default="")
    parser.add_argument("--use-latest-purchase-drill", action="store_true")
    parser.add_argument("--allow-no-go-purchase-drill", action="store_true")
    parser.add_argument("--buyer-email", default="")
    parser.add_argument("--buyer-id", default="")
    parser.add_argument("--provider-order-id", default="")
    parser.add_argument("--handoff-owner", default="")
    parser.add_argument("--support-ticket-id", default="")
    parser.add_argument("--first-response-hours", default="")
    parser.add_argument("--unresolved-support-items", default="")
    parser.add_argument("--refund-risk-flags", default="")
    parser.add_argument("--scale-decision", default="hold_review")
    parser.add_argument("--handoff-notes", default="")
    parser.add_argument("--confirm-purchase-drill-go", action="store_true")
    parser.add_argument("--confirm-delivery-sent", action="store_true")
    parser.add_argument("--confirm-buyer-acknowledged", action="store_true")
    parser.add_argument("--confirm-support-window-opened", action="store_true")
    parser.add_argument("--confirm-first-value-confirmed", action="store_true")
    parser.add_argument("--confirm-support-notes-recorded", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-scale-or-pause-decision-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    purchase_drill_file = Path(args.purchase_drill_file) if args.purchase_drill_file else None
    if args.use_latest_purchase_drill and purchase_drill_file is None:
        purchase_drill_file = latest_purchase_drill_file()
        if purchase_drill_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_1_purchase_drill_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "purchase_drill_go": args.confirm_purchase_drill_go,
        "delivery_sent": args.confirm_delivery_sent,
        "buyer_acknowledged": args.confirm_buyer_acknowledged,
        "support_window_opened": args.confirm_support_window_opened,
        "first_value_confirmed": args.confirm_first_value_confirmed,
        "support_notes_recorded": args.confirm_support_notes_recorded,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "scale_or_pause_decision_recorded": args.confirm_scale_or_pause_decision_recorded,
    }
    report = collect_handoff(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        purchase_drill_file=purchase_drill_file,
        buyer_email=args.buyer_email.strip(),
        buyer_id=args.buyer_id.strip(),
        provider_order_id=args.provider_order_id.strip(),
        handoff_owner=args.handoff_owner.strip(),
        support_ticket_id=args.support_ticket_id.strip(),
        first_response_hours=parse_int(args.first_response_hours, -1),
        unresolved_support_items=parse_int(args.unresolved_support_items, -1),
        refund_risk_flags=parse_int(args.refund_risk_flags, -1),
        scale_decision=args.scale_decision.strip(),
        handoff_notes=args.handoff_notes,
        confirmations=confirmations,
        allow_no_go_purchase_drill=args.allow_no_go_purchase_drill,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
