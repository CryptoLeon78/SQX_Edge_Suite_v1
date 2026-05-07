from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "controlled_distribution_step.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "controlled_distribution_step"
DEFAULT_OUTCOME_DIR = TOOL_ROOT / "data" / "next_controlled_buyer_outcome"
EXPECTED_STATE = "controlled_distribution_step_ready"


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


def latest_outcome_file(directory: Path = DEFAULT_OUTCOME_DIR) -> Path | None:
    return latest_file(directory, "next_controlled_buyer_outcome_*.json")


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
    outcome_config_path = project_path(str(depends_on.get("nextControlledBuyerOutcomeConfig", "")))
    if not outcome_config_path.is_file():
        return ["next_controlled_buyer_outcome_config_missing"]
    outcome_config = load_json(outcome_config_path)
    if outcome_config.get("state") != depends_on.get("nextControlledBuyerOutcomeState"):
        return ["next_controlled_buyer_outcome_state_invalid"]
    return []


def validate_outcome(outcome: dict[str, Any] | None, allow_no_go_outcome: bool) -> list[str]:
    if outcome is None:
        return ["next_controlled_buyer_outcome_evidence_missing"]
    decision = outcome.get("decision", {})
    if not decision.get("go") and not allow_no_go_outcome:
        return ["next_controlled_buyer_outcome_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def distribution_checklist() -> list[str]:
    return [
        "Load the M71 outcome evidence before choosing any distribution action.",
        "Execute only the selected M71 decision: repeat, widen, hold or pause.",
        "Keep buyer identity, checkout payloads and license files out of the evidence.",
        "Confirm support capacity, follow-up and rollback owner before sharing anything.",
        "Keep the step tiny enough to reverse manually in one session.",
    ]


def expected_action_for(source_decision: str) -> str:
    return {
        "repeat_private_slot": "prepare_single_private_slot",
        "carefully_widen": "open_tiny_private_batch",
        "hold_for_fix": "create_fix_list",
        "pause_sales": "pause_checkout_and_review",
    }.get(source_decision, "")


def decision_from(
    config: dict[str, Any],
    outcome: dict[str, Any] | None,
    source_decision: str,
    action: str,
    checkout_state: str,
    private_slots: int,
    audience_invites: int,
    support_capacity_hours: int,
    followup_hours: int,
    rollback_confirmed: bool,
    owner: str,
    action_notes: str,
    next_review: str,
    confirmations: dict[str, bool],
    allow_no_go_outcome: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_outcome(outcome, allow_no_go_outcome))

    allowed_source = set(config.get("allowedSourceDecisions", []))
    allowed_actions = set(config.get("allowedActions", []))
    allowed_checkout = set(config.get("allowedCheckoutStates", []))

    if source_decision not in allowed_source:
        blockers.append("controlled_distribution_source_decision_invalid")
    if action not in allowed_actions:
        blockers.append("controlled_distribution_action_invalid")
    if checkout_state not in allowed_checkout:
        blockers.append("controlled_distribution_checkout_state_invalid")
    if action != expected_action_for(source_decision):
        blockers.append("controlled_distribution_action_mismatch")
    if outcome and source_decision != outcome.get("outcome_decision"):
        blockers.append("controlled_distribution_source_decision_not_m71_decision")

    if any(value < 0 for value in (private_slots, audience_invites, support_capacity_hours, followup_hours)):
        blockers.append("controlled_distribution_metrics_invalid")
    if not is_safe_text(owner):
        blockers.append("controlled_distribution_owner_missing_or_unsafe")
    if not action_notes.strip():
        blockers.append("controlled_distribution_notes_missing")
    if not next_review.strip():
        blockers.append("controlled_distribution_next_review_missing")
    if support_capacity_hours <= 0:
        blockers.append("controlled_distribution_support_capacity_missing")
    if followup_hours < int(config.get("minimumFollowupHours", 24)):
        blockers.append("controlled_distribution_followup_too_short")

    if source_decision == "repeat_private_slot":
        if private_slots != int(config.get("maximumRepeatPrivateSlots", 1)):
            blockers.append("repeat_private_slot_requires_exactly_one_slot")
        if audience_invites > 1:
            blockers.append("repeat_private_slot_allows_one_private_invite")
        if checkout_state != "ready_private_link":
            blockers.append("repeat_private_slot_requires_private_link")
    if source_decision == "carefully_widen":
        if private_slots < 1 or private_slots > int(config.get("maximumTinyBatchSlots", 3)):
            blockers.append("carefully_widen_slot_limit_invalid")
        if audience_invites < 1 or audience_invites > int(config.get("maximumTinyAudienceInvites", 5)):
            blockers.append("carefully_widen_invite_limit_invalid")
        if checkout_state != "limited_private_link":
            blockers.append("carefully_widen_requires_limited_private_link")
    if source_decision == "hold_for_fix":
        if private_slots or audience_invites:
            blockers.append("hold_for_fix_requires_zero_distribution")
        if checkout_state == "limited_private_link":
            blockers.append("hold_for_fix_must_not_widen_link")
        warnings.append("operator_decision_hold_for_fix")
    if source_decision == "pause_sales":
        if private_slots or audience_invites:
            blockers.append("pause_sales_requires_zero_distribution")
        if checkout_state != "disabled":
            blockers.append("pause_sales_requires_disabled_checkout")
        warnings.append("operator_decision_pause_sales")

    if not rollback_confirmed:
        blockers.append("controlled_distribution_rollback_not_confirmed")

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
        "# Controlled Distribution Step Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Source decision: `{report.get('source_decision') or 'missing'}`",
        f"- Action: `{report.get('action') or 'missing'}`",
        f"- Checkout state: `{report.get('checkout_state') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["distribution_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("private_slots", "audience_invites", "support_capacity_hours", "followup_hours"):
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
    json_path = output_dir / f"controlled_distribution_step_{current_stamp}.json"
    md_path = output_dir / f"controlled_distribution_step_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_controlled_distribution_step(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    outcome_file: Path | None = None,
    source_decision: str = "",
    action: str = "",
    checkout_state: str = "",
    private_slots: int = -1,
    audience_invites: int = -1,
    support_capacity_hours: int = -1,
    followup_hours: int = -1,
    rollback_confirmed: bool = False,
    owner: str = "",
    action_notes: str = "",
    next_review: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_outcome: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    outcome = load_json(outcome_file) if outcome_file else None
    confirmations = confirmations or {}
    decision = decision_from(
        config=config,
        outcome=outcome,
        source_decision=source_decision,
        action=action,
        checkout_state=checkout_state,
        private_slots=private_slots,
        audience_invites=audience_invites,
        support_capacity_hours=support_capacity_hours,
        followup_hours=followup_hours,
        rollback_confirmed=rollback_confirmed,
        owner=owner,
        action_notes=action_notes,
        next_review=next_review,
        confirmations=confirmations,
        allow_no_go_outcome=allow_no_go_outcome,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "review_id": config.get("reviewId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_outcome_file": str(outcome_file) if outcome_file else "",
        "source_decision": source_decision,
        "source_outcome_status": outcome.get("outcome_status", "") if outcome else "",
        "action": action,
        "checkout_state": checkout_state,
        "private_slots": private_slots,
        "audience_invites": audience_invites,
        "support_capacity_hours": support_capacity_hours,
        "followup_hours": followup_hours,
        "rollback_confirmed": rollback_confirmed,
        "owner": owner,
        "action_notes": action_notes,
        "next_review": next_review,
        "confirmations": confirmations,
        "distribution_checklist": distribution_checklist(),
        "decision": decision,
        "privacy_policy": config.get("privacyPolicy"),
        "execution_policy": config.get("executionPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare the tiny reversible distribution step selected by the M71 outcome.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--outcome-file", type=Path)
    parser.add_argument("--use-latest-outcome", action="store_true")
    parser.add_argument("--allow-no-go-outcome", action="store_true")
    parser.add_argument("--source-decision", default="")
    parser.add_argument("--action", default="")
    parser.add_argument("--checkout-state", default="")
    parser.add_argument("--private-slots", default="")
    parser.add_argument("--audience-invites", default="")
    parser.add_argument("--support-capacity-hours", default="")
    parser.add_argument("--followup-hours", default="")
    parser.add_argument("--rollback-confirmed", action="store_true")
    parser.add_argument("--owner", default="")
    parser.add_argument("--action-notes", default="")
    parser.add_argument("--next-review", default="")
    parser.add_argument("--confirm-outcome-reviewed", action="store_true")
    parser.add_argument("--confirm-selected-decision-matched", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outcome_file = args.outcome_file
    if args.use_latest_outcome:
        outcome_file = latest_outcome_file()

    confirmations = {
        "outcome_reviewed": args.confirm_outcome_reviewed,
        "selected_decision_matched": args.confirm_selected_decision_matched,
        "support_ready": args.confirm_support_ready,
        "rollback_ready": args.confirm_rollback_ready,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
    }
    report = collect_controlled_distribution_step(
        config_path=args.config,
        manifest_path=args.manifest,
        outcome_file=outcome_file,
        source_decision=args.source_decision,
        action=args.action,
        checkout_state=args.checkout_state,
        private_slots=parse_int(args.private_slots, -1),
        audience_invites=parse_int(args.audience_invites, -1),
        support_capacity_hours=parse_int(args.support_capacity_hours, -1),
        followup_hours=parse_int(args.followup_hours, -1),
        rollback_confirmed=args.rollback_confirmed,
        owner=args.owner,
        action_notes=args.action_notes,
        next_review=args.next_review,
        confirmations=confirmations,
        allow_no_go_outcome=args.allow_no_go_outcome,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
