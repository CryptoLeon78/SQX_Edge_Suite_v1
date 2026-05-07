from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "operator_publication_review.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "operator_publication_review"
DEFAULT_DRAFT_DIR = TOOL_ROOT / "data" / "limited_publication_draft"
EXPECTED_STATE = "operator_publication_review_ready"


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


def latest_draft_file(directory: Path = DEFAULT_DRAFT_DIR) -> Path | None:
    return latest_file(directory, "limited_publication_draft_*.json")


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
    draft_config_path = project_path(str(depends_on.get("limitedPublicationDraftConfig", "")))
    if not draft_config_path.is_file():
        return ["limited_publication_draft_config_missing"]
    draft_config = load_json(draft_config_path)
    if draft_config.get("state") != depends_on.get("limitedPublicationDraftState"):
        return ["limited_publication_draft_state_invalid"]
    return []


def validate_draft(draft: dict[str, Any] | None, allow_no_go_draft: bool) -> list[str]:
    if draft is None:
        return ["limited_publication_draft_evidence_missing"]
    decision = draft.get("decision", {})
    if not decision.get("go") and not allow_no_go_draft:
        return ["limited_publication_draft_not_go", *decision.get("blockers", [])]
    if draft.get("draft_decision") != "ready_for_operator_review" and not allow_no_go_draft:
        return ["m77_did_not_select_ready_for_operator_review"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def review_checklist() -> list[str]:
    return [
        "Load M77 draft evidence before approving any manual publication step.",
        "Confirm final copy is safe and channel/audience remain limited.",
        "Confirm support path, rollback, pause rule and basic-user flow.",
        "Block approval when risks remain open or review status is not approved.",
        "Record only redacted review status, counts, owner and next action.",
    ]


def decision_from(
    config: dict[str, Any],
    draft: dict[str, Any] | None,
    review_status: str,
    reviewers: int,
    open_risks: int,
    safe_copy_approved: bool,
    support_path_approved: bool,
    rollback_approved: bool,
    pause_rule_approved: bool,
    limited_channel_approved: bool,
    basic_user_flow_approved: bool,
    decision: str,
    owner: str,
    review_notes: str,
    next_action: str,
    confirmations: dict[str, bool],
    allow_no_go_draft: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_draft(draft, allow_no_go_draft))

    if review_status not in set(config.get("allowedReviewStatuses", [])):
        blockers.append("operator_publication_review_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("operator_publication_review_decision_invalid")
    if any(value < 0 for value in (reviewers, open_risks)):
        blockers.append("operator_publication_review_metrics_invalid")
    if reviewers < int(config.get("minimumReviewers", 1)):
        blockers.append("operator_publication_review_reviewer_missing")
    if open_risks > int(config.get("maximumOpenRisks", 0)):
        blockers.append("operator_publication_review_open_risks_require_hold_or_pause")
    if not is_safe_text(owner):
        blockers.append("operator_publication_review_owner_missing_or_unsafe")
    if not review_notes.strip():
        blockers.append("operator_publication_review_notes_missing")
    if not next_action.strip():
        blockers.append("operator_publication_review_next_action_missing")

    if decision == "approve_manual_limited_publication":
        if review_status != "approved_manual_review":
            blockers.append("approve_manual_limited_publication_requires_approved_review")
        if not safe_copy_approved:
            blockers.append("approve_manual_limited_publication_requires_safe_copy")
        if not support_path_approved:
            blockers.append("approve_manual_limited_publication_requires_support_path")
        if not rollback_approved:
            blockers.append("approve_manual_limited_publication_requires_rollback")
        if not pause_rule_approved:
            blockers.append("approve_manual_limited_publication_requires_pause_rule")
        if not limited_channel_approved:
            blockers.append("approve_manual_limited_publication_requires_limited_channel")
        if not basic_user_flow_approved:
            blockers.append("approve_manual_limited_publication_requires_basic_user_flow")
    if review_status == "changes_requested" and decision == "approve_manual_limited_publication":
        blockers.append("changes_requested_requires_hold_or_pause")
    if review_status == "blocked" and decision not in {"hold_for_final_fix", "pause_sales"}:
        blockers.append("blocked_operator_review_requires_hold_or_pause")
    if decision == "hold_for_final_fix":
        warnings.append("operator_decision_hold_for_final_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if open_risks and decision == "approve_manual_limited_publication":
        blockers.append("open_risks_block_manual_publication_approval")

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
        "# Operator Publication Review Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Review status: `{report.get('review_status') or 'missing'}`",
        f"- Review decision: `{report.get('review_decision') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["review_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("reviewers", "open_risks"):
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
    json_path = output_dir / f"operator_publication_review_{current_stamp}.json"
    md_path = output_dir / f"operator_publication_review_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_operator_publication_review(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    draft_file: Path | None = None,
    review_status: str = "",
    reviewers: int = -1,
    open_risks: int = -1,
    safe_copy_approved: bool = False,
    support_path_approved: bool = False,
    rollback_approved: bool = False,
    pause_rule_approved: bool = False,
    limited_channel_approved: bool = False,
    basic_user_flow_approved: bool = False,
    decision: str = "",
    owner: str = "",
    review_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_draft: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    draft = load_json(draft_file) if draft_file else None
    confirmations = confirmations or {}
    review_decision = decision_from(
        config,
        draft,
        review_status,
        reviewers,
        open_risks,
        safe_copy_approved,
        support_path_approved,
        rollback_approved,
        pause_rule_approved,
        limited_channel_approved,
        basic_user_flow_approved,
        decision,
        owner,
        review_notes,
        next_action,
        confirmations,
        allow_no_go_draft,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "review_id": config.get("reviewId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_draft_file": str(draft_file) if draft_file else "",
        "source_draft_decision": draft.get("draft_decision", "") if draft else "",
        "review_status": review_status,
        "reviewers": reviewers,
        "open_risks": open_risks,
        "safe_copy_approved": safe_copy_approved,
        "support_path_approved": support_path_approved,
        "rollback_approved": rollback_approved,
        "pause_rule_approved": pause_rule_approved,
        "limited_channel_approved": limited_channel_approved,
        "basic_user_flow_approved": basic_user_flow_approved,
        "review_decision": decision,
        "owner": owner,
        "review_notes": review_notes,
        "next_action": next_action,
        "confirmations": confirmations,
        "review_checklist": review_checklist(),
        "decision": review_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "review_policy": config.get("reviewPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review the limited publication draft before any manual publication.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--draft-file", type=Path)
    parser.add_argument("--use-latest-draft", action="store_true")
    parser.add_argument("--allow-no-go-draft", action="store_true")
    parser.add_argument("--review-status", default="")
    parser.add_argument("--reviewers", default="")
    parser.add_argument("--open-risks", default="")
    parser.add_argument("--safe-copy-approved", action="store_true")
    parser.add_argument("--support-path-approved", action="store_true")
    parser.add_argument("--rollback-approved", action="store_true")
    parser.add_argument("--pause-rule-approved", action="store_true")
    parser.add_argument("--limited-channel-approved", action="store_true")
    parser.add_argument("--basic-user-flow-approved", action="store_true")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-draft-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-copy", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--confirm-pause-rule", action="store_true")
    parser.add_argument("--confirm-limited-channel", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    draft_file = args.draft_file
    if args.use_latest_draft:
        draft_file = latest_draft_file()
    confirmations = {
        "draft_reviewed": args.confirm_draft_reviewed,
        "safe_copy": args.confirm_safe_copy,
        "support_ready": args.confirm_support_ready,
        "rollback_ready": args.confirm_rollback_ready,
        "pause_rule": args.confirm_pause_rule,
        "limited_channel": args.confirm_limited_channel,
    }
    report = collect_operator_publication_review(
        config_path=args.config,
        manifest_path=args.manifest,
        draft_file=draft_file,
        review_status=args.review_status,
        reviewers=parse_int(args.reviewers, -1),
        open_risks=parse_int(args.open_risks, -1),
        safe_copy_approved=args.safe_copy_approved,
        support_path_approved=args.support_path_approved,
        rollback_approved=args.rollback_approved,
        pause_rule_approved=args.pause_rule_approved,
        limited_channel_approved=args.limited_channel_approved,
        basic_user_flow_approved=args.basic_user_flow_approved,
        decision=args.decision,
        owner=args.owner,
        review_notes=args.review_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_draft=args.allow_no_go_draft,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
