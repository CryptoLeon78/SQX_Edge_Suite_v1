from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "controlled_traffic_expansion_step.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "controlled_traffic_expansion_step"
DEFAULT_REVIEW_DIR = TOOL_ROOT / "data" / "controlled_traffic_expansion_review"
EXPECTED_STATE = "controlled_traffic_expansion_step_ready"


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


def latest_review_file(directory: Path = DEFAULT_REVIEW_DIR) -> Path | None:
    return latest_file(directory, "controlled_traffic_expansion_review_*.json")


def parse_int(value: str, default: int) -> int:
    if value == "":
        return default
    return int(value)


def validate_required_files(config: dict[str, Any]) -> list[str]:
    return [
        f"missing_required_file:{item}"
        for item in config.get("requiredFiles", [])
        if not project_path(str(item)).is_file()
    ]


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    review_config_path = project_path(str(depends_on.get("controlledTrafficExpansionReviewConfig", "")))
    if not review_config_path.is_file():
        return ["controlled_traffic_expansion_review_config_missing"]
    review_config = load_json(review_config_path)
    if review_config.get("state") != depends_on.get("controlledTrafficExpansionReviewState"):
        return ["controlled_traffic_expansion_review_state_invalid"]
    return []


def validate_review(review: dict[str, Any] | None, allow_no_go_review: bool) -> list[str]:
    if review is None:
        return ["controlled_traffic_expansion_review_evidence_missing"]
    decision = review.get("decision", {})
    if not decision.get("go") and not allow_no_go_review:
        return ["controlled_traffic_expansion_review_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def step_checklist() -> list[str]:
    return [
        "Load the M81 review evidence before taking any traffic action.",
        "Use one private channel only and keep the action manually reversible.",
        "Store only redacted counts; never store buyer identity, checkout payloads or license files.",
        "Confirm support capacity, rollback owner, pause rule and safe claims before sharing.",
        "Set the next review time before inviting anyone.",
    ]


def expected_actions(source_decision: str) -> set[str]:
    return {
        "approve_tiny_traffic_expansion": {"share_one_private_link", "invite_tiny_watchlist"},
        "continue_monitoring": {"continue_observation"},
        "hold_for_fix": {"create_fix_list"},
        "pause_sales": {"pause_checkout_and_review"},
    }.get(source_decision, set())


def decision_from(
    config: dict[str, Any],
    review: dict[str, Any] | None,
    source_decision: str,
    action: str,
    channel: str,
    private_links: int,
    audience_invites: int,
    support_capacity_hours: int,
    followup_hours: int,
    checkout_shared: bool,
    support_ready: bool,
    rollback_ready: bool,
    pause_rule_ready: bool,
    safe_claims_ready: bool,
    owner: str,
    action_notes: str,
    next_review: str,
    confirmations: dict[str, bool],
    allow_no_go_review: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_review(review, allow_no_go_review))

    if source_decision not in set(config.get("allowedSourceDecisions", [])):
        blockers.append("controlled_traffic_expansion_step_source_decision_invalid")
    if action not in set(config.get("allowedActions", [])):
        blockers.append("controlled_traffic_expansion_step_action_invalid")
    if channel not in set(config.get("allowedChannels", [])):
        blockers.append("controlled_traffic_expansion_step_channel_invalid")
    if action not in expected_actions(source_decision):
        blockers.append("controlled_traffic_expansion_step_action_mismatch")
    if review and source_decision != review.get("monitor_decision"):
        blockers.append("controlled_traffic_expansion_step_source_decision_not_m81_decision")
    if review and source_decision == "approve_tiny_traffic_expansion" and not review.get("decision", {}).get("go"):
        blockers.append("controlled_traffic_expansion_step_requires_m81_go")

    if any(value < 0 for value in (private_links, audience_invites, support_capacity_hours, followup_hours)):
        blockers.append("controlled_traffic_expansion_step_metrics_invalid")
    if not is_safe_text(owner):
        blockers.append("controlled_traffic_expansion_step_owner_missing_or_unsafe")
    if not action_notes.strip():
        blockers.append("controlled_traffic_expansion_step_notes_missing")
    if not next_review.strip():
        blockers.append("controlled_traffic_expansion_step_next_review_missing")
    if support_capacity_hours <= 0 and source_decision == "approve_tiny_traffic_expansion":
        blockers.append("controlled_traffic_expansion_step_support_capacity_missing")
    if followup_hours < int(config.get("minimumFollowupHours", 24)):
        blockers.append("controlled_traffic_expansion_step_followup_too_short")
    if not support_ready:
        blockers.append("controlled_traffic_expansion_step_requires_support_ready")
    if not rollback_ready:
        blockers.append("controlled_traffic_expansion_step_requires_rollback_ready")
    if not pause_rule_ready:
        blockers.append("controlled_traffic_expansion_step_requires_pause_rule")
    if not safe_claims_ready:
        blockers.append("controlled_traffic_expansion_step_requires_safe_claims")

    if source_decision == "approve_tiny_traffic_expansion":
        if channel == "none":
            blockers.append("approved_traffic_step_requires_private_channel")
        if private_links > int(config.get("maximumPrivateLinks", 1)):
            blockers.append("tiny_traffic_step_private_link_limit_invalid")
        if audience_invites < 1 or audience_invites > int(config.get("maximumAudienceInvites", 3)):
            blockers.append("tiny_traffic_step_invite_limit_invalid")
        if action == "share_one_private_link" and (private_links != 1 or audience_invites > 1):
            blockers.append("share_one_private_link_requires_one_link_and_one_invite_max")
        if action == "invite_tiny_watchlist" and private_links > 1:
            blockers.append("invite_tiny_watchlist_allows_one_private_link_max")
    if source_decision in {"continue_monitoring", "hold_for_fix", "pause_sales"}:
        if private_links or audience_invites or checkout_shared:
            blockers.append("non_expansion_decision_requires_zero_distribution")
        if channel != "none":
            blockers.append("non_expansion_decision_requires_no_channel")
        warnings.append(f"operator_decision_{source_decision}")
    if source_decision == "pause_sales" and action != "pause_checkout_and_review":
        blockers.append("pause_sales_requires_pause_checkout_and_review")

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
        "# Controlled Traffic Expansion Step Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Source decision: `{report.get('source_decision') or 'missing'}`",
        f"- Action: `{report.get('action') or 'missing'}`",
        f"- Channel: `{report.get('channel') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["step_checklist"])
    lines.append("")
    lines.append("## Redacted Metrics")
    for name in ("private_links", "audience_invites", "support_capacity_hours", "followup_hours"):
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
    json_path = output_dir / f"controlled_traffic_expansion_step_{current_stamp}.json"
    md_path = output_dir / f"controlled_traffic_expansion_step_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_controlled_traffic_expansion_step(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    review_file: Path | None = None,
    source_decision: str = "",
    action: str = "",
    channel: str = "",
    private_links: int = -1,
    audience_invites: int = -1,
    support_capacity_hours: int = -1,
    followup_hours: int = -1,
    checkout_shared: bool = False,
    support_ready: bool = False,
    rollback_ready: bool = False,
    pause_rule_ready: bool = False,
    safe_claims_ready: bool = False,
    owner: str = "",
    action_notes: str = "",
    next_review: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_review: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    review = load_json(review_file) if review_file else None
    confirmations = confirmations or {}
    decision = decision_from(
        config=config,
        review=review,
        source_decision=source_decision,
        action=action,
        channel=channel,
        private_links=private_links,
        audience_invites=audience_invites,
        support_capacity_hours=support_capacity_hours,
        followup_hours=followup_hours,
        checkout_shared=checkout_shared,
        support_ready=support_ready,
        rollback_ready=rollback_ready,
        pause_rule_ready=pause_rule_ready,
        safe_claims_ready=safe_claims_ready,
        owner=owner,
        action_notes=action_notes,
        next_review=next_review,
        confirmations=confirmations,
        allow_no_go_review=allow_no_go_review,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "step_id": config.get("stepId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_review_file": str(review_file) if review_file else "",
        "source_decision": source_decision,
        "source_review_status": review.get("decision", {}).get("label", "") if review else "",
        "action": action,
        "channel": channel,
        "private_links": private_links,
        "audience_invites": audience_invites,
        "support_capacity_hours": support_capacity_hours,
        "followup_hours": followup_hours,
        "checkout_shared": checkout_shared,
        "support_ready": support_ready,
        "rollback_ready": rollback_ready,
        "pause_rule_ready": pause_rule_ready,
        "safe_claims_ready": safe_claims_ready,
        "owner": owner,
        "action_notes": action_notes,
        "next_review": next_review,
        "confirmations": confirmations,
        "step_checklist": step_checklist(),
        "decision": decision,
        "privacy_policy": config.get("privacyPolicy"),
        "execution_policy": config.get("executionPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record one tiny reversible traffic expansion step after M81 approval.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--review-file", type=Path)
    parser.add_argument("--use-latest-review", action="store_true")
    parser.add_argument("--allow-no-go-review", action="store_true")
    parser.add_argument("--source-decision", default="")
    parser.add_argument("--action", default="")
    parser.add_argument("--channel", default="")
    parser.add_argument("--private-links", default="")
    parser.add_argument("--audience-invites", default="")
    parser.add_argument("--support-capacity-hours", default="")
    parser.add_argument("--followup-hours", default="")
    parser.add_argument("--checkout-shared", action="store_true")
    parser.add_argument("--support-ready", action="store_true")
    parser.add_argument("--rollback-ready", action="store_true")
    parser.add_argument("--pause-rule-ready", action="store_true")
    parser.add_argument("--safe-claims-ready", action="store_true")
    parser.add_argument("--owner", default="")
    parser.add_argument("--action-notes", default="")
    parser.add_argument("--next-review", default="")
    parser.add_argument("--confirm-review-approved", action="store_true")
    parser.add_argument("--confirm-private-channel", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--confirm-pause-rule", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-redacted-evidence", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    review_file = args.review_file
    if args.use_latest_review:
        review_file = latest_review_file()
    confirmations = {
        "review_approved": args.confirm_review_approved,
        "private_channel": args.confirm_private_channel,
        "support_ready": args.confirm_support_ready,
        "rollback_ready": args.confirm_rollback_ready,
        "pause_rule": args.confirm_pause_rule,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "redacted_evidence": args.confirm_redacted_evidence,
    }
    report = collect_controlled_traffic_expansion_step(
        config_path=args.config,
        manifest_path=args.manifest,
        review_file=review_file,
        source_decision=args.source_decision,
        action=args.action,
        channel=args.channel,
        private_links=parse_int(args.private_links, -1),
        audience_invites=parse_int(args.audience_invites, -1),
        support_capacity_hours=parse_int(args.support_capacity_hours, -1),
        followup_hours=parse_int(args.followup_hours, -1),
        checkout_shared=args.checkout_shared,
        support_ready=args.support_ready,
        rollback_ready=args.rollback_ready,
        pause_rule_ready=args.pause_rule_ready,
        safe_claims_ready=args.safe_claims_ready,
        owner=args.owner,
        action_notes=args.action_notes,
        next_review=args.next_review,
        confirmations=confirmations,
        allow_no_go_review=args.allow_no_go_review,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
