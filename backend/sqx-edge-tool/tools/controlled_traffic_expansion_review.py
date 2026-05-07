from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "controlled_traffic_expansion_review.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "controlled_traffic_expansion_review"
DEFAULT_RECORD_DIR = TOOL_ROOT / "data" / "manual_publication_monitor"
EXPECTED_STATE = "controlled_traffic_expansion_review_ready"


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


def latest_record_file(directory: Path = DEFAULT_RECORD_DIR) -> Path | None:
    return latest_file(directory, "manual_publication_monitor_*.json")


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
    record_config_path = project_path(str(depends_on.get("manualPublicationMonitorConfig", "")))
    if not record_config_path.is_file():
        return ["manual_publication_monitor_config_missing"]
    record_config = load_json(record_config_path)
    if record_config.get("state") != depends_on.get("manualPublicationMonitorState"):
        return ["manual_publication_monitor_state_invalid"]
    return []


def validate_record(record: dict[str, Any] | None, allow_no_go_record: bool) -> list[str]:
    if record is None:
        return ["manual_publication_monitor_evidence_missing"]
    decision = record.get("decision", {})
    if not decision.get("go") and not allow_no_go_record:
        return ["manual_publication_monitor_not_go", *decision.get("blockers", [])]
    if record.get("monitor_decision") != "prepare_traffic_expansion_review" and not allow_no_go_record:
        return ["m80_did_not_select_prepare_traffic_expansion_review"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def monitor_checklist() -> list[str]:
    return [
        "Load M81 traffic expansion record before monitoring.",
        "Record only redacted counts and operational signals.",
        "Block traffic expansion when support, refunds, claims or incidents are unresolved.",
        "Require enough observation time before expansion review.",
        "Set next action before sharing more traffic.",
    ]


def decision_from(
    config: dict[str, Any],
    record: dict[str, Any] | None,
    observation_hours: int,
    views: int,
    clicks: int,
    support_gaps: int,
    refund_requests: int,
    claims_flags: int,
    incidents: int,
    positive_signals: int,
    support_ready: bool,
    rollback_ready: bool,
    pause_rule_ready: bool,
    decision: str,
    owner: str,
    monitor_notes: str,
    next_action: str,
    confirmations: dict[str, bool],
    allow_no_go_record: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_record(record, allow_no_go_record))

    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("controlled_traffic_expansion_review_decision_invalid")
    if any(value < 0 for value in (observation_hours, views, clicks, support_gaps, refund_requests, claims_flags, incidents, positive_signals)):
        blockers.append("controlled_traffic_expansion_review_metrics_invalid")
    if not is_safe_text(owner):
        blockers.append("controlled_traffic_expansion_review_owner_missing_or_unsafe")
    if not monitor_notes.strip():
        blockers.append("controlled_traffic_expansion_review_notes_missing")
    if not next_action.strip():
        blockers.append("controlled_traffic_expansion_review_next_action_missing")
    if not support_ready:
        blockers.append("controlled_traffic_expansion_review_requires_support_ready")
    if not rollback_ready:
        blockers.append("controlled_traffic_expansion_review_requires_rollback_ready")
    if not pause_rule_ready:
        blockers.append("controlled_traffic_expansion_review_requires_pause_rule")

    risky_counts = {
        "incidents": (incidents, int(config.get("maximumIncidents", 0))),
        "support_gaps": (support_gaps, int(config.get("maximumSupportGaps", 0))),
        "refund_requests": (refund_requests, int(config.get("maximumRefundRequests", 0))),
        "claims_flags": (claims_flags, int(config.get("maximumClaimsFlags", 0))),
    }
    for name, (value, maximum) in risky_counts.items():
        if value > maximum:
            blockers.append(f"controlled_traffic_expansion_review_{name}_require_hold_or_pause")

    if decision == "approve_tiny_traffic_expansion":
        if observation_hours < int(config.get("minimumObservationHours", 24)):
            blockers.append("approve_tiny_traffic_expansion_requires_observation_time")
        if positive_signals < int(config.get("minimumPositiveSignalsForTinyExpansion", 1)):
            blockers.append("approve_tiny_traffic_expansion_requires_positive_signal")
        if any(value > maximum for value, maximum in risky_counts.values()):
            blockers.append("risky_counts_block_tiny_traffic_expansion")
    if decision == "continue_monitoring":
        warnings.append("operator_decision_continue_monitoring")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
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
        "# Controlled Traffic Expansion Review Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Monitor decision: `{report.get('monitor_decision') or 'missing'}`",
        f"- Observation hours: `{report.get('observation_hours')}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["monitor_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("views", "clicks", "support_gaps", "refund_requests", "claims_flags", "incidents", "positive_signals"):
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
    json_path = output_dir / f"controlled_traffic_expansion_review_{current_stamp}.json"
    md_path = output_dir / f"controlled_traffic_expansion_review_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_controlled_traffic_expansion_review(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    record_file: Path | None = None,
    observation_hours: int = -1,
    views: int = -1,
    clicks: int = -1,
    support_gaps: int = -1,
    refund_requests: int = -1,
    claims_flags: int = -1,
    incidents: int = -1,
    positive_signals: int = -1,
    support_ready: bool = False,
    rollback_ready: bool = False,
    pause_rule_ready: bool = False,
    decision: str = "",
    owner: str = "",
    monitor_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_record: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    record = load_json(record_file) if record_file else None
    confirmations = confirmations or {}
    monitor_decision = decision_from(
        config,
        record,
        observation_hours,
        views,
        clicks,
        support_gaps,
        refund_requests,
        claims_flags,
        incidents,
        positive_signals,
        support_ready,
        rollback_ready,
        pause_rule_ready,
        decision,
        owner,
        monitor_notes,
        next_action,
        confirmations,
        allow_no_go_record,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "monitor_id": config.get("monitorId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_record_file": str(record_file) if record_file else "",
        "source_monitor_decision": record.get("monitor_decision", "") if record else "",
        "observation_hours": observation_hours,
        "views": views,
        "clicks": clicks,
        "support_gaps": support_gaps,
        "refund_requests": refund_requests,
        "claims_flags": claims_flags,
        "incidents": incidents,
        "positive_signals": positive_signals,
        "support_ready": support_ready,
        "rollback_ready": rollback_ready,
        "pause_rule_ready": pause_rule_ready,
        "monitor_decision": decision,
        "owner": owner,
        "monitor_notes": monitor_notes,
        "next_action": next_action,
        "confirmations": confirmations,
        "monitor_checklist": monitor_checklist(),
        "decision": monitor_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "review_policy": config.get("reviewPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review whether a tiny controlled traffic expansion is safe.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--record-file", type=Path)
    parser.add_argument("--use-latest-record", action="store_true")
    parser.add_argument("--allow-no-go-record", action="store_true")
    parser.add_argument("--observation-hours", default="")
    parser.add_argument("--views", default="")
    parser.add_argument("--clicks", default="")
    parser.add_argument("--support-gaps", default="")
    parser.add_argument("--refund-requests", default="")
    parser.add_argument("--claims-flags", default="")
    parser.add_argument("--incidents", default="")
    parser.add_argument("--positive-signals", default="")
    parser.add_argument("--support-ready", action="store_true")
    parser.add_argument("--rollback-ready", action="store_true")
    parser.add_argument("--pause-rule-ready", action="store_true")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--monitor-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-record-reviewed", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--confirm-pause-rule", action="store_true")
    parser.add_argument("--confirm-redacted-metrics", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    record_file = args.record_file
    if args.use_latest_record:
        record_file = latest_record_file()
    confirmations = {
        "record_reviewed": args.confirm_record_reviewed,
        "support_ready": args.confirm_support_ready,
        "rollback_ready": args.confirm_rollback_ready,
        "pause_rule": args.confirm_pause_rule,
        "redacted_metrics": args.confirm_redacted_metrics,
    }
    report = collect_controlled_traffic_expansion_review(
        config_path=args.config,
        manifest_path=args.manifest,
        record_file=record_file,
        observation_hours=parse_int(args.observation_hours, -1),
        views=parse_int(args.views, -1),
        clicks=parse_int(args.clicks, -1),
        support_gaps=parse_int(args.support_gaps, -1),
        refund_requests=parse_int(args.refund_requests, -1),
        claims_flags=parse_int(args.claims_flags, -1),
        incidents=parse_int(args.incidents, -1),
        positive_signals=parse_int(args.positive_signals, -1),
        support_ready=args.support_ready,
        rollback_ready=args.rollback_ready,
        pause_rule_ready=args.pause_rule_ready,
        decision=args.decision,
        owner=args.owner,
        monitor_notes=args.monitor_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_record=args.allow_no_go_record,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
