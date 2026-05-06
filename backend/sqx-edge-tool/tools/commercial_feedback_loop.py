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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "commercial_feedback_loop"
DEFAULT_POST_LAUNCH_DIR = TOOL_ROOT / "data" / "post_launch_control"
VALID_PRICING_DECISIONS = ("keep_price", "test_discount", "raise_price_later", "pause_pricing_change")
VALID_COPY_DECISIONS = ("keep_copy", "revise_copy", "run_ab_test")
VALID_NEXT_ACTIONS = ("ship_fix", "update_docs", "revise_offer", "continue_observing", "pause_sales")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_post_launch_file(directory: Path = DEFAULT_POST_LAUNCH_DIR) -> Path | None:
    return latest_file(directory, "post_launch_control_*.json")


def parse_int(value: str, default: int) -> int:
    if value == "":
        return default
    return int(value)


def feedback_categories() -> list[str]:
    return [
        "bugs",
        "activation_friction",
        "documentation_gap",
        "feature_request",
        "pricing_objection",
        "copy_confusion",
        "positive_signal",
    ]


def feedback_checklist() -> list[str]:
    return [
        "Classify every feedback item into a single primary category.",
        "Mark severe bugs and activation friction before changing price or copy.",
        "Assign a planned fix version or explicit no-change decision.",
        "Decide whether price stays, changes later, gets discounted or pauses.",
        "Decide whether commercial copy stays, changes or needs an A/B test.",
        "Update roadmap, release notes and support macros before scaling.",
    ]


def decision_from(
    post_launch: dict[str, Any] | None,
    bug_count: int,
    activation_friction_count: int,
    documentation_gap_count: int,
    feature_request_count: int,
    pricing_objection_count: int,
    copy_confusion_count: int,
    positive_signal_count: int,
    severe_bug_count: int,
    planned_fix_version: str,
    pricing_decision: str,
    copy_decision: str,
    next_action: str,
    feedback_reviewed: bool,
    roadmap_updated: bool,
    release_notes_owner: str,
    allow_no_go_post_launch: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    counts = [
        bug_count,
        activation_friction_count,
        documentation_gap_count,
        feature_request_count,
        pricing_objection_count,
        copy_confusion_count,
        positive_signal_count,
        severe_bug_count,
    ]

    if post_launch is None:
        blockers.append("post_launch_control_missing")
    elif not post_launch.get("decision", {}).get("go") and not allow_no_go_post_launch:
        blockers.append("post_launch_control_not_go")
        blockers.extend(post_launch.get("decision", {}).get("blockers", []))
    if any(count < 0 for count in counts):
        blockers.append("feedback_counts_missing")
    if sum(counts[:7]) <= 0:
        blockers.append("no_feedback_recorded")
    if severe_bug_count > bug_count:
        blockers.append("severe_bug_count_exceeds_bug_count")
    if severe_bug_count > 0 and next_action != "ship_fix":
        blockers.append("severe_bug_requires_ship_fix")
    if activation_friction_count > 0 and next_action not in ("ship_fix", "update_docs"):
        blockers.append("activation_friction_requires_fix_or_docs")
    if pricing_objection_count > 0 and pricing_decision == "raise_price_later":
        blockers.append("pricing_objection_blocks_raise_price")
    if copy_confusion_count > 0 and copy_decision == "keep_copy":
        blockers.append("copy_confusion_blocks_keep_copy")
    if pricing_decision not in VALID_PRICING_DECISIONS:
        blockers.append("pricing_decision_invalid")
    if copy_decision not in VALID_COPY_DECISIONS:
        blockers.append("copy_decision_invalid")
    if next_action not in VALID_NEXT_ACTIONS:
        blockers.append("next_action_invalid")
    if not planned_fix_version.strip():
        blockers.append("planned_fix_version_missing")
    if not feedback_reviewed:
        blockers.append("feedback_not_reviewed")
    if not roadmap_updated:
        blockers.append("roadmap_not_updated")
    if not release_notes_owner.strip():
        blockers.append("release_notes_owner_missing")
    valid_feedback_counts = all(count >= 0 for count in counts[:7])
    if valid_feedback_counts and feature_request_count > bug_count + activation_friction_count + documentation_gap_count:
        warnings.append("feature_requests_dominate_feedback")
    if valid_feedback_counts and positive_signal_count > 0 and sum(counts[:6]) == 0:
        warnings.append("positive_only_feedback")
    if next_action == "pause_sales":
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
        "# SQX Edge Commercial Feedback Loop",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Post-launch source: `{report.get('post_launch_source') or 'none'}`",
        f"- Planned fix version: `{report.get('planned_fix_version') or 'not configured'}`",
        f"- Pricing decision: `{report.get('pricing_decision')}`",
        f"- Copy decision: `{report.get('copy_decision')}`",
        f"- Next action: `{report.get('next_action')}`",
        "",
        "## Feedback Counts",
        "",
    ]
    for key, value in report["feedback_counts"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Checklist")
    lines.extend(f"- {item}" for item in report["feedback_checklist"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_loop(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"commercial_feedback_loop_{current_stamp}.json"
    md_path = output_dir / f"commercial_feedback_loop_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_loop(
    manifest_path: Path = DEFAULT_MANIFEST,
    post_launch_file: Path | None = None,
    bug_count: int = -1,
    activation_friction_count: int = -1,
    documentation_gap_count: int = -1,
    feature_request_count: int = -1,
    pricing_objection_count: int = -1,
    copy_confusion_count: int = -1,
    positive_signal_count: int = -1,
    severe_bug_count: int = -1,
    planned_fix_version: str = "",
    pricing_decision: str = "keep_price",
    copy_decision: str = "keep_copy",
    next_action: str = "continue_observing",
    feedback_reviewed: bool = False,
    roadmap_updated: bool = False,
    release_notes_owner: str = "",
    allow_no_go_post_launch: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    post_launch = load_json(post_launch_file) if post_launch_file else None
    counts = {
        "bugs": bug_count,
        "activation_friction": activation_friction_count,
        "documentation_gap": documentation_gap_count,
        "feature_request": feature_request_count,
        "pricing_objection": pricing_objection_count,
        "copy_confusion": copy_confusion_count,
        "positive_signal": positive_signal_count,
        "severe_bug": severe_bug_count,
    }
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "post_launch_source": str(post_launch_file) if post_launch_file else "",
        "post_launch_decision": post_launch.get("decision") if post_launch else None,
        "feedback_categories": feedback_categories(),
        "feedback_counts": counts,
        "planned_fix_version": planned_fix_version,
        "pricing_decision": pricing_decision,
        "copy_decision": copy_decision,
        "next_action": next_action,
        "feedback_reviewed": feedback_reviewed,
        "roadmap_updated": roadmap_updated,
        "release_notes_owner": release_notes_owner,
        "feedback_checklist": feedback_checklist(),
        "decision": decision_from(
            post_launch,
            bug_count,
            activation_friction_count,
            documentation_gap_count,
            feature_request_count,
            pricing_objection_count,
            copy_confusion_count,
            positive_signal_count,
            severe_bug_count,
            planned_fix_version,
            pricing_decision,
            copy_decision,
            next_action,
            feedback_reviewed,
            roadmap_updated,
            release_notes_owner,
            allow_no_go_post_launch,
        ),
    }
    if write:
        report["evidence_paths"] = write_loop(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge commercial feedback loop")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--post-launch-file", default="")
    parser.add_argument("--use-latest-post-launch", action="store_true")
    parser.add_argument("--bug-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_BUG_COUNT"), -1))
    parser.add_argument("--activation-friction-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_ACTIVATION_FRICTION_COUNT"), -1))
    parser.add_argument("--documentation-gap-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_DOCUMENTATION_GAP_COUNT"), -1))
    parser.add_argument("--feature-request-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_FEATURE_REQUEST_COUNT"), -1))
    parser.add_argument("--pricing-objection-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_PRICING_OBJECTION_COUNT"), -1))
    parser.add_argument("--copy-confusion-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_COPY_CONFUSION_COUNT"), -1))
    parser.add_argument("--positive-signal-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_POSITIVE_SIGNAL_COUNT"), -1))
    parser.add_argument("--severe-bug-count", type=int, default=parse_int(env_value("SQX_FEEDBACK_SEVERE_BUG_COUNT"), -1))
    parser.add_argument("--planned-fix-version", default=env_value("SQX_FEEDBACK_PLANNED_FIX_VERSION"))
    parser.add_argument("--pricing-decision", default=env_value("SQX_FEEDBACK_PRICING_DECISION", "keep_price"), choices=VALID_PRICING_DECISIONS)
    parser.add_argument("--copy-decision", default=env_value("SQX_FEEDBACK_COPY_DECISION", "keep_copy"), choices=VALID_COPY_DECISIONS)
    parser.add_argument("--next-action", default=env_value("SQX_FEEDBACK_NEXT_ACTION", "continue_observing"), choices=VALID_NEXT_ACTIONS)
    parser.add_argument("--confirm-feedback-reviewed", action="store_true")
    parser.add_argument("--confirm-roadmap-updated", action="store_true")
    parser.add_argument("--release-notes-owner", default=env_value("SQX_FEEDBACK_RELEASE_NOTES_OWNER"))
    parser.add_argument("--allow-no-go-post-launch", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    post_launch_file = Path(args.post_launch_file) if args.post_launch_file else None
    if args.use_latest_post_launch and post_launch_file is None:
        post_launch_file = latest_post_launch_file()
        if post_launch_file is None:
            print(json.dumps({"ok": False, "error": "post_launch_control_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_loop(
        manifest_path=Path(args.manifest),
        post_launch_file=post_launch_file,
        bug_count=args.bug_count,
        activation_friction_count=args.activation_friction_count,
        documentation_gap_count=args.documentation_gap_count,
        feature_request_count=args.feature_request_count,
        pricing_objection_count=args.pricing_objection_count,
        copy_confusion_count=args.copy_confusion_count,
        positive_signal_count=args.positive_signal_count,
        severe_bug_count=args.severe_bug_count,
        planned_fix_version=args.planned_fix_version,
        pricing_decision=args.pricing_decision,
        copy_decision=args.copy_decision,
        next_action=args.next_action,
        feedback_reviewed=args.confirm_feedback_reviewed,
        roadmap_updated=args.confirm_roadmap_updated,
        release_notes_owner=args.release_notes_owner,
        allow_no_go_post_launch=args.allow_no_go_post_launch,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
