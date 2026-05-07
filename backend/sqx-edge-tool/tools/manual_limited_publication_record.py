from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "manual_limited_publication_record.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "manual_limited_publication_record"
DEFAULT_REVIEW_DIR = TOOL_ROOT / "data" / "operator_publication_review"
EXPECTED_STATE = "manual_limited_publication_record_ready"


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
    return latest_file(directory, "operator_publication_review_*.json")


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
    review_config_path = project_path(str(depends_on.get("operatorPublicationReviewConfig", "")))
    if not review_config_path.is_file():
        return ["operator_publication_review_config_missing"]
    review_config = load_json(review_config_path)
    if review_config.get("state") != depends_on.get("operatorPublicationReviewState"):
        return ["operator_publication_review_state_invalid"]
    return []


def validate_review(review: dict[str, Any] | None, allow_no_go_review: bool) -> list[str]:
    if review is None:
        return ["operator_publication_review_evidence_missing"]
    decision = review.get("decision", {})
    if not decision.get("go") and not allow_no_go_review:
        return ["operator_publication_review_not_go", *decision.get("blockers", [])]
    if review.get("review_decision") != "approve_manual_limited_publication" and not allow_no_go_review:
        return ["m78_did_not_select_approve_manual_limited_publication"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def is_redacted_url(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered:
        return False
    return lowered.startswith(("redacted:", "private:", "limited:"))


def record_checklist() -> list[str]:
    return [
        "Load M78 operator review evidence before recording publication.",
        "Record only redacted URL/channel data, never buyer identity or checkout payloads.",
        "Confirm support, rollback, pause rule and monitoring window.",
        "Keep audience cap limited and manually controlled.",
        "Set the next review action before sharing more traffic.",
    ]


def decision_from(
    config: dict[str, Any],
    review: dict[str, Any] | None,
    channel: str,
    redacted_url: str,
    audience_cap: int,
    evidence_items: int,
    open_risks: int,
    support_ready: bool,
    rollback_ready: bool,
    pause_rule_ready: bool,
    monitoring_ready: bool,
    decision: str,
    owner: str,
    publication_notes: str,
    next_action: str,
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

    if channel not in set(config.get("allowedChannels", [])):
        blockers.append("manual_limited_publication_channel_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("manual_limited_publication_decision_invalid")
    if any(value < 0 for value in (audience_cap, evidence_items, open_risks)):
        blockers.append("manual_limited_publication_metrics_invalid")
    if audience_cap <= 0:
        blockers.append("manual_limited_publication_audience_cap_missing")
    if audience_cap > int(config.get("maximumAudienceCap", 10)):
        blockers.append("manual_limited_publication_audience_cap_too_large")
    if evidence_items < int(config.get("minimumEvidenceItems", 4)):
        blockers.append("manual_limited_publication_evidence_items_missing")
    if open_risks > int(config.get("maximumOpenRisks", 0)):
        blockers.append("manual_limited_publication_open_risks_require_hold_or_pause")
    if not is_redacted_url(redacted_url):
        blockers.append("manual_limited_publication_redacted_url_missing_or_unsafe")
    if not is_safe_text(owner):
        blockers.append("manual_limited_publication_owner_missing_or_unsafe")
    if not publication_notes.strip():
        blockers.append("manual_limited_publication_notes_missing")
    if not next_action.strip():
        blockers.append("manual_limited_publication_next_action_missing")

    if decision == "record_manual_publication":
        if not support_ready:
            blockers.append("record_manual_publication_requires_support")
        if not rollback_ready:
            blockers.append("record_manual_publication_requires_rollback")
        if not pause_rule_ready:
            blockers.append("record_manual_publication_requires_pause_rule")
        if not monitoring_ready:
            blockers.append("record_manual_publication_requires_monitoring")
    if decision == "hold_publication":
        warnings.append("operator_decision_hold_publication")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if open_risks and decision == "record_manual_publication":
        blockers.append("open_risks_block_manual_publication_record")

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
        "# Manual Limited Publication Record Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Publication decision: `{report.get('publication_decision') or 'missing'}`",
        f"- Channel: `{report.get('channel') or 'missing'}`",
        f"- Redacted URL: `{report.get('redacted_url') or 'missing'}`",
        f"- Audience cap: `{report.get('audience_cap')}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["record_checklist"])
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
    json_path = output_dir / f"manual_limited_publication_record_{current_stamp}.json"
    md_path = output_dir / f"manual_limited_publication_record_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_manual_limited_publication_record(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    review_file: Path | None = None,
    channel: str = "",
    redacted_url: str = "",
    audience_cap: int = -1,
    evidence_items: int = -1,
    open_risks: int = -1,
    support_ready: bool = False,
    rollback_ready: bool = False,
    pause_rule_ready: bool = False,
    monitoring_ready: bool = False,
    decision: str = "",
    owner: str = "",
    publication_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_review: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    review = load_json(review_file) if review_file else None
    confirmations = confirmations or {}
    publication_decision = decision_from(
        config,
        review,
        channel,
        redacted_url,
        audience_cap,
        evidence_items,
        open_risks,
        support_ready,
        rollback_ready,
        pause_rule_ready,
        monitoring_ready,
        decision,
        owner,
        publication_notes,
        next_action,
        confirmations,
        allow_no_go_review,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "record_id": config.get("recordId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_review_file": str(review_file) if review_file else "",
        "source_review_decision": review.get("review_decision", "") if review else "",
        "channel": channel,
        "redacted_url": redacted_url,
        "audience_cap": audience_cap,
        "evidence_items": evidence_items,
        "open_risks": open_risks,
        "support_ready": support_ready,
        "rollback_ready": rollback_ready,
        "pause_rule_ready": pause_rule_ready,
        "monitoring_ready": monitoring_ready,
        "publication_decision": decision,
        "owner": owner,
        "publication_notes": publication_notes,
        "next_action": next_action,
        "confirmations": confirmations,
        "record_checklist": record_checklist(),
        "decision": publication_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "record_policy": config.get("recordPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record a manual limited publication after M78 approval.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--review-file", type=Path)
    parser.add_argument("--use-latest-review", action="store_true")
    parser.add_argument("--allow-no-go-review", action="store_true")
    parser.add_argument("--channel", default="")
    parser.add_argument("--redacted-url", default="")
    parser.add_argument("--audience-cap", default="")
    parser.add_argument("--evidence-items", default="")
    parser.add_argument("--open-risks", default="")
    parser.add_argument("--support-ready", action="store_true")
    parser.add_argument("--rollback-ready", action="store_true")
    parser.add_argument("--pause-rule-ready", action="store_true")
    parser.add_argument("--monitoring-ready", action="store_true")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--publication-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-m78-approved", action="store_true")
    parser.add_argument("--confirm-redacted-url", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--confirm-pause-rule", action="store_true")
    parser.add_argument("--confirm-monitoring-ready", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    review_file = args.review_file
    if args.use_latest_review:
        review_file = latest_review_file()
    confirmations = {
        "m78_approved": args.confirm_m78_approved,
        "redacted_url": args.confirm_redacted_url,
        "support_ready": args.confirm_support_ready,
        "rollback_ready": args.confirm_rollback_ready,
        "pause_rule": args.confirm_pause_rule,
        "monitoring_ready": args.confirm_monitoring_ready,
    }
    report = collect_manual_limited_publication_record(
        config_path=args.config,
        manifest_path=args.manifest,
        review_file=review_file,
        channel=args.channel,
        redacted_url=args.redacted_url,
        audience_cap=parse_int(args.audience_cap, -1),
        evidence_items=parse_int(args.evidence_items, -1),
        open_risks=parse_int(args.open_risks, -1),
        support_ready=args.support_ready,
        rollback_ready=args.rollback_ready,
        pause_rule_ready=args.pause_rule_ready,
        monitoring_ready=args.monitoring_ready,
        decision=args.decision,
        owner=args.owner,
        publication_notes=args.publication_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_review=args.allow_no_go_review,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
