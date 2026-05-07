from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "buyer_onboarding_support_gate.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "buyer_onboarding_support_gate"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def forbidden_hits(text: str, forbidden: list[str]) -> list[str]:
    lower = text.lower()
    return [item for item in forbidden if item.lower() in lower]


def required_file_findings(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    forbidden = config.get("forbiddenClaims") if isinstance(config.get("forbiddenClaims"), list) else []
    for item in config.get("requiredFiles", []):
        path = project_path(str(item))
        if not path.is_file():
            findings.append(f"missing_required_file:{item}")
            continue
        for hit in forbidden_hits(read_text(path), forbidden):
            findings.append(f"forbidden_claim:{item}:{hit}")
    return findings


def dependency_findings(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    pro_pack_path = project_path(str(depends_on.get("proBuyerPackConfig", "")))
    expected_state = depends_on.get("proBuyerPackState")
    if not pro_pack_path.is_file():
        return ["pro_buyer_pack_config_missing"]
    pro_pack = load_json(pro_pack_path)
    if pro_pack.get("state") != expected_state:
        return ["pro_buyer_pack_state_invalid"]
    return []


def decision_from(
    config: dict[str, Any],
    customer_email: str,
    customer_id: str,
    order_id: str,
    plan: str,
    purchase_confirmed: bool,
    portable_zip_ready: bool,
    license_file_ready: bool,
    start_here_attached: bool,
    activation_steps_reviewed: bool,
    support_contact_ready: bool,
    faq_ready: bool,
    safe_claims_reviewed: bool,
    support_tickets_open: int,
    activation_errors: int,
    refund_or_pause_risk_flags: int,
    refund_or_pause_reviewed: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if not customer_email and not customer_id:
        blockers.append("customer_reference_missing")
    if not order_id:
        blockers.append("order_id_missing")
    if plan not in set(config.get("plans", [])):
        blockers.append("plan_missing_or_invalid")
    if not purchase_confirmed:
        blockers.append("purchase_not_confirmed")
    if not portable_zip_ready:
        blockers.append("portable_zip_not_ready")
    if not license_file_ready:
        blockers.append("license_file_not_ready")
    if not start_here_attached:
        blockers.append("start_here_not_attached")
    if not activation_steps_reviewed:
        blockers.append("activation_steps_not_reviewed")
    if not support_contact_ready:
        blockers.append("support_contact_not_ready")
    if not faq_ready:
        blockers.append("faq_not_ready")
    if not safe_claims_reviewed:
        blockers.append("safe_claims_not_reviewed")
    if support_tickets_open > 0:
        blockers.append("support_tickets_open")
    if activation_errors > 0:
        blockers.append("activation_errors_open")
    if refund_or_pause_risk_flags > 0 and not refund_or_pause_reviewed:
        blockers.append("refund_or_pause_risk_unreviewed")
    if min(support_tickets_open, activation_errors, refund_or_pause_risk_flags) < 0:
        blockers.append("negative_metrics_invalid")
    if refund_or_pause_risk_flags > 0 and refund_or_pause_reviewed:
        warnings.append("refund_or_pause_risk_reviewed")

    blockers.extend(required_file_findings(config))
    blockers.extend(dependency_findings(config))
    if any(item.startswith("forbidden_claim:") for item in blockers):
        blockers.append("forbidden_claims_present")

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
        "# Buyer Onboarding Support Gate Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Customer: `{report.get('customer_email') or report.get('customer_id') or 'missing'}`",
        f"- Order: `{report.get('order_id') or 'missing'}`",
        f"- Plan: `{report.get('plan') or 'missing'}`",
        "",
        "## Confirmations",
    ]
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
    json_path = output_dir / f"buyer_onboarding_support_gate_{current_stamp}.json"
    md_path = output_dir / f"buyer_onboarding_support_gate_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_gate(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    customer_email: str = "",
    customer_id: str = "",
    order_id: str = "",
    plan: str = "",
    purchase_confirmed: bool = False,
    portable_zip_ready: bool = False,
    license_file_ready: bool = False,
    start_here_attached: bool = False,
    activation_steps_reviewed: bool = False,
    support_contact_ready: bool = False,
    faq_ready: bool = False,
    safe_claims_reviewed: bool = False,
    support_tickets_open: int = 0,
    activation_errors: int = 0,
    refund_or_pause_risk_flags: int = 0,
    refund_or_pause_reviewed: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    confirmations = {
        "purchase_confirmed": purchase_confirmed,
        "portable_zip_ready": portable_zip_ready,
        "license_file_ready": license_file_ready,
        "start_here_attached": start_here_attached,
        "activation_steps_reviewed": activation_steps_reviewed,
        "support_contact_ready": support_contact_ready,
        "faq_ready": faq_ready,
        "safe_claims_reviewed": safe_claims_reviewed,
        "refund_or_pause_reviewed": refund_or_pause_reviewed,
    }
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "buyer_onboarding_support_gate_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "resource_dir": config.get("resourceDir"),
        "included_in_portable": bool(config.get("includedInPortable")),
        "customer_email": customer_email,
        "customer_id": customer_id,
        "order_id": order_id,
        "plan": plan,
        "support_tickets_open": support_tickets_open,
        "activation_errors": activation_errors,
        "refund_or_pause_risk_flags": refund_or_pause_risk_flags,
        "confirmations": confirmations,
        "refund_pause_criteria": config.get("refundPauseCriteria", []),
        "decision": decision_from(
            config,
            customer_email,
            customer_id,
            order_id,
            plan,
            purchase_confirmed,
            portable_zip_ready,
            license_file_ready,
            start_here_attached,
            activation_steps_reviewed,
            support_contact_ready,
            faq_ready,
            safe_claims_reviewed,
            support_tickets_open,
            activation_errors,
            refund_or_pause_risk_flags,
            refund_or_pause_reviewed,
        ),
    }
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge buyer onboarding and support gate")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--customer-email", default="")
    parser.add_argument("--customer-id", default="")
    parser.add_argument("--order-id", default="")
    parser.add_argument("--plan", default="")
    parser.add_argument("--support-tickets-open", type=int, default=0)
    parser.add_argument("--activation-errors", type=int, default=0)
    parser.add_argument("--refund-or-pause-risk-flags", type=int, default=0)
    parser.add_argument("--confirm-purchase-confirmed", action="store_true")
    parser.add_argument("--confirm-portable-zip-ready", action="store_true")
    parser.add_argument("--confirm-license-file-ready", action="store_true")
    parser.add_argument("--confirm-start-here-attached", action="store_true")
    parser.add_argument("--confirm-activation-steps-reviewed", action="store_true")
    parser.add_argument("--confirm-support-contact-ready", action="store_true")
    parser.add_argument("--confirm-faq-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-refund-or-pause-reviewed", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_gate(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        customer_email=args.customer_email,
        customer_id=args.customer_id,
        order_id=args.order_id,
        plan=args.plan,
        purchase_confirmed=args.confirm_purchase_confirmed,
        portable_zip_ready=args.confirm_portable_zip_ready,
        license_file_ready=args.confirm_license_file_ready,
        start_here_attached=args.confirm_start_here_attached,
        activation_steps_reviewed=args.confirm_activation_steps_reviewed,
        support_contact_ready=args.confirm_support_contact_ready,
        faq_ready=args.confirm_faq_ready,
        safe_claims_reviewed=args.confirm_safe_claims_reviewed,
        support_tickets_open=args.support_tickets_open,
        activation_errors=args.activation_errors,
        refund_or_pause_risk_flags=args.refund_or_pause_risk_flags,
        refund_or_pause_reviewed=args.confirm_refund_or_pause_reviewed,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
