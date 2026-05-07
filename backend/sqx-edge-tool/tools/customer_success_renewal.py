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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "customer_success_renewal"
DEFAULT_HOTFIX_ROLLBACK_DIR = TOOL_ROOT / "data" / "hotfix_rollback_release"
PLANS = {"pro_monthly", "pro_annual", "setup_assist"}
DECISIONS = {
    "maintain_pro",
    "renew",
    "upsell_templates",
    "offer_setup_assist",
    "improve_onboarding",
    "pause_or_refund_review",
}


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_hotfix_rollback_file(directory: Path = DEFAULT_HOTFIX_ROLLBACK_DIR) -> Path | None:
    return latest_file(directory, "hotfix_rollback_release_*.json")


def evidence_list() -> list[str]:
    return [
        "hotfix_rollback_reviewed",
        "customer_reference_recorded",
        "success_owner_assigned",
        "onboarding_checklist_ready",
        "activation_confirmed",
        "support_triaged",
        "value_checkins_recorded",
        "renewal_contact_ready",
        "success_notes_ready",
        "safe_claims_reviewed",
        "expansion_offer_reviewed",
        "renewal_decision_recorded",
    ]


def decision_from(
    hotfix_rollback_release: dict[str, Any] | None,
    customer_id: str,
    customer_email: str,
    plan: str,
    success_owner: str,
    renewal_decision: str,
    days_to_renewal: int,
    support_tickets_open: int,
    activation_errors: int,
    refund_risk_flags: int,
    value_checkins_completed: int,
    onboarding_checklist_ready: bool,
    activation_confirmed: bool,
    support_triaged: bool,
    renewal_contact_ready: bool,
    success_notes_ready: bool,
    safe_claims_reviewed: bool,
    template_pack_offer_ready: bool,
    setup_assist_offer_ready: bool,
    allow_no_go_hotfix: bool,
    min_value_checkins: int,
    renewal_window_days: int,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if hotfix_rollback_release is None:
        blockers.append("hotfix_rollback_release_missing")
    elif not hotfix_rollback_release.get("decision", {}).get("go") and not allow_no_go_hotfix:
        blockers.append("hotfix_rollback_release_not_go")
        blockers.extend(hotfix_rollback_release.get("decision", {}).get("blockers", []))
    if not customer_id and not customer_email:
        blockers.append("customer_reference_missing")
    if plan not in PLANS:
        blockers.append("plan_missing_or_invalid")
    if not success_owner:
        blockers.append("success_owner_missing")
    if renewal_decision not in DECISIONS:
        blockers.append("customer_success_decision_missing_or_invalid")
    if not onboarding_checklist_ready:
        blockers.append("onboarding_checklist_not_ready")
    if not activation_confirmed:
        blockers.append("activation_not_confirmed")
    if not support_triaged:
        blockers.append("support_not_triaged")
    if support_tickets_open > 0:
        blockers.append("support_tickets_open")
    if activation_errors > 0:
        blockers.append("activation_errors_open")
    if refund_risk_flags > 0 and renewal_decision != "pause_or_refund_review":
        blockers.append("refund_risk_unreviewed")
    if value_checkins_completed < min_value_checkins:
        blockers.append("value_checkins_missing")
    if days_to_renewal <= renewal_window_days and not renewal_contact_ready:
        blockers.append("renewal_contact_not_ready")
    if not success_notes_ready:
        blockers.append("success_notes_missing")
    if not safe_claims_reviewed:
        blockers.append("safe_claims_not_reviewed")
    if renewal_decision == "upsell_templates" and not template_pack_offer_ready:
        blockers.append("template_pack_offer_not_ready")
    if renewal_decision == "offer_setup_assist" and not setup_assist_offer_ready:
        blockers.append("setup_assist_offer_not_ready")
    if renewal_decision in {"upsell_templates", "offer_setup_assist"} and value_checkins_completed < 2:
        warnings.append("expansion_decision_with_low_value_checkins")
    if renewal_decision == "renew" and days_to_renewal > renewal_window_days:
        warnings.append("renewal_outside_review_window")
    if min(
        days_to_renewal,
        support_tickets_open,
        activation_errors,
        refund_risk_flags,
        value_checkins_completed,
        min_value_checkins,
        renewal_window_days,
    ) < 0:
        blockers.append("negative_metrics_invalid")

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
        "# SQX Edge Customer Success Renewal",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Customer: `{report.get('customer_id') or report.get('customer_email') or 'missing'}`",
        f"- Plan: `{report.get('plan') or 'missing'}`",
        f"- Success owner: `{report.get('success_owner') or 'missing'}`",
        f"- Renewal decision: `{report.get('renewal_decision') or 'missing'}`",
        f"- Days to renewal: `{report['days_to_renewal']}`",
        f"- Support tickets open: `{report['support_tickets_open']}`",
        f"- Activation errors: `{report['activation_errors']}`",
        "",
        "## Evidence",
    ]
    lines.extend(f"- {item}" for item in report["evidence"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_success_report(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"customer_success_renewal_{current_stamp}.json"
    md_path = output_dir / f"customer_success_renewal_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_success(
    manifest_path: Path = DEFAULT_MANIFEST,
    hotfix_rollback_release_file: Path | None = None,
    customer_id: str = "",
    customer_email: str = "",
    plan: str = "",
    success_owner: str = "",
    renewal_decision: str = "",
    days_to_renewal: int = 30,
    support_tickets_open: int = 0,
    activation_errors: int = 0,
    refund_risk_flags: int = 0,
    value_checkins_completed: int = 0,
    onboarding_checklist_ready: bool = False,
    activation_confirmed: bool = False,
    support_triaged: bool = False,
    renewal_contact_ready: bool = False,
    success_notes_ready: bool = False,
    safe_claims_reviewed: bool = False,
    template_pack_offer_ready: bool = False,
    setup_assist_offer_ready: bool = False,
    allow_no_go_hotfix: bool = False,
    min_value_checkins: int = 1,
    renewal_window_days: int = 14,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    hotfix_rollback_release = load_json(hotfix_rollback_release_file) if hotfix_rollback_release_file else None
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "hotfix_rollback_release_source": str(hotfix_rollback_release_file) if hotfix_rollback_release_file else "",
        "hotfix_rollback_release_decision": hotfix_rollback_release.get("decision") if hotfix_rollback_release else None,
        "customer_id": customer_id,
        "customer_email": customer_email,
        "plan": plan,
        "success_owner": success_owner,
        "renewal_decision": renewal_decision,
        "days_to_renewal": days_to_renewal,
        "support_tickets_open": support_tickets_open,
        "activation_errors": activation_errors,
        "refund_risk_flags": refund_risk_flags,
        "value_checkins_completed": value_checkins_completed,
        "onboarding_checklist_ready": onboarding_checklist_ready,
        "activation_confirmed": activation_confirmed,
        "support_triaged": support_triaged,
        "renewal_contact_ready": renewal_contact_ready,
        "success_notes_ready": success_notes_ready,
        "safe_claims_reviewed": safe_claims_reviewed,
        "template_pack_offer_ready": template_pack_offer_ready,
        "setup_assist_offer_ready": setup_assist_offer_ready,
        "evidence": evidence_list(),
        "decision": decision_from(
            hotfix_rollback_release,
            customer_id,
            customer_email,
            plan,
            success_owner,
            renewal_decision,
            days_to_renewal,
            support_tickets_open,
            activation_errors,
            refund_risk_flags,
            value_checkins_completed,
            onboarding_checklist_ready,
            activation_confirmed,
            support_triaged,
            renewal_contact_ready,
            success_notes_ready,
            safe_claims_reviewed,
            template_pack_offer_ready,
            setup_assist_offer_ready,
            allow_no_go_hotfix,
            min_value_checkins,
            renewal_window_days,
        ),
    }
    if write:
        report["evidence_paths"] = write_success_report(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge customer success and renewal loop")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--hotfix-rollback-release-file", default="")
    parser.add_argument("--use-latest-hotfix-rollback-release", action="store_true")
    parser.add_argument("--customer-id", default=env_value("SQX_CUSTOMER_ID"))
    parser.add_argument("--customer-email", default=env_value("SQX_CUSTOMER_EMAIL"))
    parser.add_argument("--plan", default=env_value("SQX_CUSTOMER_PLAN"))
    parser.add_argument("--success-owner", default=env_value("SQX_SUCCESS_OWNER"))
    parser.add_argument("--decision", default=env_value("SQX_CUSTOMER_SUCCESS_DECISION"))
    parser.add_argument("--days-to-renewal", type=int, default=30)
    parser.add_argument("--support-tickets-open", type=int, default=0)
    parser.add_argument("--activation-errors", type=int, default=0)
    parser.add_argument("--refund-risk-flags", type=int, default=0)
    parser.add_argument("--value-checkins-completed", type=int, default=0)
    parser.add_argument("--confirm-onboarding-checklist-ready", action="store_true")
    parser.add_argument("--confirm-activation-confirmed", action="store_true")
    parser.add_argument("--confirm-support-triaged", action="store_true")
    parser.add_argument("--confirm-renewal-contact-ready", action="store_true")
    parser.add_argument("--confirm-success-notes-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-template-pack-offer-ready", action="store_true")
    parser.add_argument("--confirm-setup-assist-offer-ready", action="store_true")
    parser.add_argument("--allow-no-go-hotfix", action="store_true")
    parser.add_argument("--min-value-checkins", type=int, default=1)
    parser.add_argument("--renewal-window-days", type=int, default=14)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    hotfix_file = Path(args.hotfix_rollback_release_file) if args.hotfix_rollback_release_file else None
    if args.use_latest_hotfix_rollback_release and hotfix_file is None:
        hotfix_file = latest_hotfix_rollback_file()
        if hotfix_file is None:
            print(json.dumps({"ok": False, "error": "hotfix_rollback_release_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_success(
        manifest_path=Path(args.manifest),
        hotfix_rollback_release_file=hotfix_file,
        customer_id=args.customer_id,
        customer_email=args.customer_email,
        plan=args.plan,
        success_owner=args.success_owner,
        renewal_decision=args.decision,
        days_to_renewal=args.days_to_renewal,
        support_tickets_open=args.support_tickets_open,
        activation_errors=args.activation_errors,
        refund_risk_flags=args.refund_risk_flags,
        value_checkins_completed=args.value_checkins_completed,
        onboarding_checklist_ready=args.confirm_onboarding_checklist_ready,
        activation_confirmed=args.confirm_activation_confirmed,
        support_triaged=args.confirm_support_triaged,
        renewal_contact_ready=args.confirm_renewal_contact_ready,
        success_notes_ready=args.confirm_success_notes_ready,
        safe_claims_reviewed=args.confirm_safe_claims_reviewed,
        template_pack_offer_ready=args.confirm_template_pack_offer_ready,
        setup_assist_offer_ready=args.confirm_setup_assist_offer_ready,
        allow_no_go_hotfix=args.allow_no_go_hotfix,
        min_value_checkins=args.min_value_checkins,
        renewal_window_days=args.renewal_window_days,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
