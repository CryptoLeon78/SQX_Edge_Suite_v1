from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "post_sale_improvement_loop.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "post_sale_improvement_loop"
DEFAULT_FIRST_BUYER_DIR = TOOL_ROOT / "data" / "first_controlled_buyer_log"


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


def latest_first_buyer_file(directory: Path = DEFAULT_FIRST_BUYER_DIR) -> Path | None:
    return latest_file(directory, "first_controlled_buyer_log_*.json")


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
    first_buyer_config_path = project_path(str(depends_on.get("firstControlledBuyerLogConfig", "")))
    if not first_buyer_config_path.is_file():
        return ["first_controlled_buyer_log_config_missing"]
    first_buyer_config = load_json(first_buyer_config_path)
    if first_buyer_config.get("state") != depends_on.get("firstControlledBuyerLogState"):
        return ["first_controlled_buyer_log_state_invalid"]
    return []


def validate_first_buyer_log(first_buyer: dict[str, Any] | None, allow_no_go_first_buyer: bool) -> list[str]:
    if first_buyer is None:
        return ["first_controlled_buyer_log_evidence_missing"]
    decision = first_buyer.get("decision", {})
    if not decision.get("go") and not allow_no_go_first_buyer:
        return ["first_controlled_buyer_log_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def improvement_checklist() -> list[str]:
    return [
        "Confirm first controlled buyer log evidence is GO.",
        "Convert onboarding friction into small buyer-facing updates.",
        "Convert support questions into reusable macros.",
        "Tighten public copy only where expectations were unclear.",
        "Re-check safe claims before publishing any wording change.",
        "Assign owner and next review before exposing more traffic.",
    ]


def decision_from(
    config: dict[str, Any],
    first_buyer: dict[str, Any] | None,
    onboarding_updates: int,
    support_macro_updates: int,
    public_copy_updates: int,
    safe_claims_updates: int,
    followup_actions: int,
    support_risk: int,
    claims_risk: int,
    decision: str,
    priority: str,
    owner: str,
    next_review: str,
    improvement_summary: str,
    review_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_first_buyer: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_first_buyer_log(first_buyer, allow_no_go_first_buyer))

    counts = [
        onboarding_updates,
        support_macro_updates,
        public_copy_updates,
        safe_claims_updates,
        followup_actions,
        support_risk,
        claims_risk,
    ]
    if any(value < 0 for value in counts):
        blockers.append("post_sale_improvement_metrics_invalid")

    total_updates = onboarding_updates + support_macro_updates + public_copy_updates + safe_claims_updates
    if total_updates < int(config.get("minimumTotalUpdates", 2)):
        blockers.append("post_sale_improvement_needs_minimum_updates")
    if onboarding_updates + support_macro_updates + public_copy_updates <= 0:
        blockers.append("post_sale_improvement_needs_buyer_facing_update")
    if followup_actions <= 0:
        blockers.append("post_sale_improvement_needs_followup_action")

    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("post_sale_improvement_decision_invalid")
    if priority not in set(config.get("allowedPriorities", [])):
        blockers.append("post_sale_improvement_priority_invalid")
    if not is_safe_text(owner):
        blockers.append("post_sale_improvement_owner_missing_or_unsafe")
    if not is_safe_text(next_review):
        blockers.append("post_sale_improvement_next_review_missing_or_unsafe")
    if not improvement_summary.strip():
        blockers.append("post_sale_improvement_summary_missing")
    if not review_notes.strip():
        blockers.append("post_sale_improvement_review_notes_missing")

    first_buyer_decision = first_buyer.get("post_sale_decision", "") if first_buyer else ""
    first_value_status = first_buyer.get("first_value_status", "") if first_buyer else ""
    open_support_items = int(first_buyer.get("open_support_items", 0)) if first_buyer else 0
    refund_count = int(first_buyer.get("refund_count", 0)) if first_buyer else 0
    fulfillment_failures = int(first_buyer.get("fulfillment_failures", 0)) if first_buyer else 0

    if first_buyer_decision == "pause_sales" and decision != "pause_sales":
        blockers.append("first_buyer_pause_sales_requires_pause_sales")
    if fulfillment_failures > 0 and decision != "pause_sales":
        blockers.append("fulfillment_failures_require_pause_sales")
    if refund_count > 0 and decision != "pause_sales":
        blockers.append("refunds_require_pause_sales")
    if claims_risk > int(config.get("maximumClaimsRiskForShipping", 0)) and decision != "pause_sales":
        blockers.append("claims_risk_requires_pause_sales")
    if support_risk > int(config.get("maximumSupportRiskForShipping", 1)) and decision == "ship_micro_updates":
        blockers.append("ship_micro_updates_blocked_by_support_risk")
    if open_support_items > 0 and decision == "ship_micro_updates":
        blockers.append("ship_micro_updates_blocked_by_open_support")
    if support_risk > 0 and support_macro_updates <= 0:
        blockers.append("support_risk_needs_support_macro_update")
    if claims_risk > 0 and safe_claims_updates <= 0:
        blockers.append("claims_risk_needs_safe_claims_update")

    if decision == "revise_onboarding" and onboarding_updates <= 0:
        blockers.append("revise_onboarding_needs_onboarding_update")
    if decision == "revise_support_macros" and support_macro_updates <= 0:
        blockers.append("revise_support_macros_needs_support_macro_update")
    if decision == "revise_public_copy" and public_copy_updates <= 0:
        blockers.append("revise_public_copy_needs_public_copy_update")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if first_value_status != "confirmed":
        warnings.append("first_value_not_yet_confirmed")
    if priority == "high":
        warnings.append("high_priority_post_sale_update")

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
        "# Post-Sale Improvement Loop Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Improvement decision: `{report.get('improvement_decision') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        f"- Next review: `{report.get('next_review') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["improvement_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in (
        "onboarding_updates",
        "support_macro_updates",
        "public_copy_updates",
        "safe_claims_updates",
        "followup_actions",
        "support_risk",
        "claims_risk",
    ):
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
    json_path = output_dir / f"post_sale_improvement_loop_{current_stamp}.json"
    md_path = output_dir / f"post_sale_improvement_loop_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_post_sale_improvement(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    first_buyer_file: Path | None = None,
    onboarding_updates: int = -1,
    support_macro_updates: int = -1,
    public_copy_updates: int = -1,
    safe_claims_updates: int = -1,
    followup_actions: int = -1,
    support_risk: int = -1,
    claims_risk: int = -1,
    decision: str = "ship_micro_updates",
    priority: str = "medium",
    owner: str = "",
    next_review: str = "",
    improvement_summary: str = "",
    review_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_first_buyer: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    first_buyer = load_json(first_buyer_file) if first_buyer_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "post_sale_improvement_loop_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "first_buyer_source": str(first_buyer_file) if first_buyer_file else "",
        "first_buyer_decision": first_buyer.get("decision") if first_buyer else None,
        "first_buyer_post_sale_decision": first_buyer.get("post_sale_decision") if first_buyer else "",
        "first_buyer_first_value_status": first_buyer.get("first_value_status") if first_buyer else "",
        "onboarding_updates": onboarding_updates,
        "support_macro_updates": support_macro_updates,
        "public_copy_updates": public_copy_updates,
        "safe_claims_updates": safe_claims_updates,
        "followup_actions": followup_actions,
        "support_risk": support_risk,
        "claims_risk": claims_risk,
        "improvement_decision": decision,
        "priority": priority,
        "owner": owner.strip(),
        "next_review": next_review.strip(),
        "improvement_summary": improvement_summary.strip(),
        "review_notes": review_notes.strip(),
        "improvement_checklist": improvement_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        first_buyer,
        onboarding_updates,
        support_macro_updates,
        public_copy_updates,
        safe_claims_updates,
        followup_actions,
        support_risk,
        claims_risk,
        decision,
        priority,
        owner,
        next_review,
        improvement_summary,
        review_notes,
        final_confirmations,
        allow_no_go_first_buyer,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare post-sale improvement loop from first controlled buyer evidence.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--first-buyer-log-file", default="")
    parser.add_argument("--use-latest-first-buyer-log", action="store_true")
    parser.add_argument("--allow-no-go-first-buyer", action="store_true")
    parser.add_argument("--onboarding-updates", default="")
    parser.add_argument("--support-macro-updates", default="")
    parser.add_argument("--public-copy-updates", default="")
    parser.add_argument("--safe-claims-updates", default="")
    parser.add_argument("--followup-actions", default="")
    parser.add_argument("--support-risk", default="")
    parser.add_argument("--claims-risk", default="")
    parser.add_argument("--decision", default="ship_micro_updates")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--owner", default="")
    parser.add_argument("--next-review", default="")
    parser.add_argument("--improvement-summary", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--confirm-first-buyer-log-go", action="store_true")
    parser.add_argument("--confirm-onboarding-reviewed", action="store_true")
    parser.add_argument("--confirm-support-macros-reviewed", action="store_true")
    parser.add_argument("--confirm-public-copy-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-owner-assigned", action="store_true")
    parser.add_argument("--confirm-next-review-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    first_buyer_file = Path(args.first_buyer_log_file) if args.first_buyer_log_file else None
    if args.use_latest_first_buyer_log and first_buyer_file is None:
        first_buyer_file = latest_first_buyer_file()
        if first_buyer_file is None:
            print(json.dumps({"ok": False, "error": "first_controlled_buyer_log_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "first_buyer_log_go": args.confirm_first_buyer_log_go,
        "onboarding_reviewed": args.confirm_onboarding_reviewed,
        "support_macros_reviewed": args.confirm_support_macros_reviewed,
        "public_copy_reviewed": args.confirm_public_copy_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "owner_assigned": args.confirm_owner_assigned,
        "next_review_recorded": args.confirm_next_review_recorded,
    }
    report = collect_post_sale_improvement(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        first_buyer_file=first_buyer_file,
        onboarding_updates=parse_int(args.onboarding_updates, -1),
        support_macro_updates=parse_int(args.support_macro_updates, -1),
        public_copy_updates=parse_int(args.public_copy_updates, -1),
        safe_claims_updates=parse_int(args.safe_claims_updates, -1),
        followup_actions=parse_int(args.followup_actions, -1),
        support_risk=parse_int(args.support_risk, -1),
        claims_risk=parse_int(args.claims_risk, -1),
        decision=args.decision.strip(),
        priority=args.priority.strip(),
        owner=args.owner,
        next_review=args.next_review,
        improvement_summary=args.improvement_summary,
        review_notes=args.review_notes,
        confirmations=confirmations,
        allow_no_go_first_buyer=args.allow_no_go_first_buyer,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
