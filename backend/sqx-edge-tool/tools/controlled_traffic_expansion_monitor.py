from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "controlled_traffic_expansion_monitor.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "controlled_traffic_expansion_monitor"
DEFAULT_STEP_DIR = TOOL_ROOT / "data" / "controlled_traffic_expansion_step"
EXPECTED_STATE = "controlled_traffic_expansion_monitor_ready"


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


def latest_step_file(directory: Path = DEFAULT_STEP_DIR) -> Path | None:
    return latest_file(directory, "controlled_traffic_expansion_step_*.json")


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
    step_config_path = project_path(str(depends_on.get("controlledTrafficExpansionStepConfig", "")))
    if not step_config_path.is_file():
        return ["controlled_traffic_expansion_step_config_missing"]
    step_config = load_json(step_config_path)
    if step_config.get("state") != depends_on.get("controlledTrafficExpansionStepState"):
        return ["controlled_traffic_expansion_step_state_invalid"]
    return []


def validate_step(step: dict[str, Any] | None, allow_no_go_step: bool) -> list[str]:
    if step is None:
        return ["controlled_traffic_expansion_step_evidence_missing"]
    decision = step.get("decision", {})
    if not decision.get("go") and not allow_no_go_step:
        return ["controlled_traffic_expansion_step_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def monitor_checklist() -> list[str]:
    return [
        "Load the M82 tiny traffic step evidence before choosing a next move.",
        "Record only redacted aggregate counts and operational signals.",
        "Block repeat or review when support, refund, claims or incident risk appears.",
        "Keep any repeat action as small and reversible as M82.",
        "Record owner and next action before any further traffic movement.",
    ]


def decision_from(
    config: dict[str, Any],
    step: dict[str, Any] | None,
    source_action: str,
    monitor_status: str,
    observation_hours: int,
    responses: int,
    positive_signals: int,
    support_items_open: int,
    refund_requests: int,
    claims_issues: int,
    incidents: int,
    decision: str,
    owner: str,
    monitor_notes: str,
    next_action: str,
    confirmations: dict[str, bool],
    allow_no_go_step: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_step(step, allow_no_go_step))

    if source_action not in set(config.get("allowedSourceActions", [])):
        blockers.append("controlled_traffic_expansion_monitor_source_action_invalid")
    if monitor_status not in set(config.get("allowedMonitorStatuses", [])):
        blockers.append("controlled_traffic_expansion_monitor_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("controlled_traffic_expansion_monitor_decision_invalid")
    if step and source_action != step.get("action"):
        blockers.append("controlled_traffic_expansion_monitor_source_action_not_m82_action")
    if any(value < 0 for value in (observation_hours, responses, positive_signals, support_items_open, refund_requests, claims_issues, incidents)):
        blockers.append("controlled_traffic_expansion_monitor_metrics_invalid")
    if not is_safe_text(owner):
        blockers.append("controlled_traffic_expansion_monitor_owner_missing_or_unsafe")
    if not monitor_notes.strip():
        blockers.append("controlled_traffic_expansion_monitor_notes_missing")
    if not next_action.strip():
        blockers.append("controlled_traffic_expansion_monitor_next_action_missing")

    if observation_hours < int(config.get("minimumObservationHours", 24)):
        blockers.append("controlled_traffic_expansion_monitor_requires_observation_time")
    risk_counts = {
        "support_items_open": (support_items_open, int(config.get("maximumOpenSupportItems", 0))),
        "refund_requests": (refund_requests, int(config.get("maximumRefundRequests", 0))),
        "claims_issues": (claims_issues, int(config.get("maximumClaimsIssues", 0))),
        "incidents": (incidents, int(config.get("maximumIncidents", 0))),
    }
    for name, (value, maximum) in risk_counts.items():
        if value > maximum:
            blockers.append(f"controlled_traffic_expansion_monitor_{name}_requires_hold_or_pause")

    if decision == "repeat_tiny_step":
        if monitor_status not in {"completed", "partial"}:
            blockers.append("repeat_tiny_step_requires_completed_or_partial_monitor")
        if positive_signals < int(config.get("minimumPositiveSignalsForRepeat", 1)):
            blockers.append("repeat_tiny_step_requires_positive_signal")
        if any(value > maximum for value, maximum in risk_counts.values()):
            blockers.append("repeat_tiny_step_blocked_by_risk")
    if decision == "prepare_next_private_review":
        if monitor_status != "completed":
            blockers.append("prepare_next_private_review_requires_completed_monitor")
        if positive_signals < int(config.get("minimumPositiveSignalsForReview", 2)):
            blockers.append("prepare_next_private_review_requires_positive_signals")
        if source_action in {"create_fix_list", "pause_checkout_and_review"}:
            blockers.append("prepare_next_private_review_blocked_after_hold_or_pause")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if monitor_status == "paused" and decision != "pause_sales":
        blockers.append("paused_monitor_requires_pause_sales")
    if monitor_status == "blocked" and decision not in {"hold_for_fix", "pause_sales"}:
        blockers.append("blocked_monitor_requires_hold_or_pause")
    if (refund_requests or claims_issues or incidents) and decision != "pause_sales":
        blockers.append("risk_events_require_pause_sales")

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
        "# Controlled Traffic Expansion Monitor Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Monitor decision: `{report.get('monitor_decision') or 'missing'}`",
        f"- Monitor status: `{report.get('monitor_status') or 'missing'}`",
        f"- Source action: `{report.get('source_action') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["monitor_checklist"])
    lines.append("")
    lines.append("## Redacted Metrics")
    for name in ("observation_hours", "responses", "positive_signals", "support_items_open", "refund_requests", "claims_issues", "incidents"):
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
    json_path = output_dir / f"controlled_traffic_expansion_monitor_{current_stamp}.json"
    md_path = output_dir / f"controlled_traffic_expansion_monitor_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_controlled_traffic_expansion_monitor(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    step_file: Path | None = None,
    source_action: str = "",
    monitor_status: str = "",
    observation_hours: int = -1,
    responses: int = -1,
    positive_signals: int = -1,
    support_items_open: int = -1,
    refund_requests: int = -1,
    claims_issues: int = -1,
    incidents: int = -1,
    decision: str = "",
    owner: str = "",
    monitor_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_step: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    step = load_json(step_file) if step_file else None
    confirmations = confirmations or {}
    monitor_decision = decision_from(
        config=config,
        step=step,
        source_action=source_action,
        monitor_status=monitor_status,
        observation_hours=observation_hours,
        responses=responses,
        positive_signals=positive_signals,
        support_items_open=support_items_open,
        refund_requests=refund_requests,
        claims_issues=claims_issues,
        incidents=incidents,
        decision=decision,
        owner=owner,
        monitor_notes=monitor_notes,
        next_action=next_action,
        confirmations=confirmations,
        allow_no_go_step=allow_no_go_step,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "monitor_id": config.get("monitorId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_step_file": str(step_file) if step_file else "",
        "source_action": source_action,
        "source_step_status": step.get("decision", {}).get("label", "") if step else "",
        "monitor_status": monitor_status,
        "observation_hours": observation_hours,
        "responses": responses,
        "positive_signals": positive_signals,
        "support_items_open": support_items_open,
        "refund_requests": refund_requests,
        "claims_issues": claims_issues,
        "incidents": incidents,
        "monitor_decision": decision,
        "owner": owner,
        "monitor_notes": monitor_notes,
        "next_action": next_action,
        "confirmations": confirmations,
        "monitor_checklist": monitor_checklist(),
        "decision": monitor_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "monitor_policy": config.get("monitorPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitor the tiny M82 traffic expansion step before any repeat or wider move.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--step-file", type=Path)
    parser.add_argument("--use-latest-step", action="store_true")
    parser.add_argument("--allow-no-go-step", action="store_true")
    parser.add_argument("--source-action", default="")
    parser.add_argument("--monitor-status", default="")
    parser.add_argument("--observation-hours", default="")
    parser.add_argument("--responses", default="")
    parser.add_argument("--positive-signals", default="")
    parser.add_argument("--support-items-open", default="")
    parser.add_argument("--refund-requests", default="")
    parser.add_argument("--claims-issues", default="")
    parser.add_argument("--incidents", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--monitor-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-step-reviewed", action="store_true")
    parser.add_argument("--confirm-support-clear", action="store_true")
    parser.add_argument("--confirm-claims-clear", action="store_true")
    parser.add_argument("--confirm-refunds-clear", action="store_true")
    parser.add_argument("--confirm-redacted-metrics", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    step_file = args.step_file
    if args.use_latest_step:
        step_file = latest_step_file()
    confirmations = {
        "step_reviewed": args.confirm_step_reviewed,
        "support_clear": args.confirm_support_clear,
        "claims_clear": args.confirm_claims_clear,
        "refunds_clear": args.confirm_refunds_clear,
        "redacted_metrics": args.confirm_redacted_metrics,
    }
    report = collect_controlled_traffic_expansion_monitor(
        config_path=args.config,
        manifest_path=args.manifest,
        step_file=step_file,
        source_action=args.source_action,
        monitor_status=args.monitor_status,
        observation_hours=parse_int(args.observation_hours, -1),
        responses=parse_int(args.responses, -1),
        positive_signals=parse_int(args.positive_signals, -1),
        support_items_open=parse_int(args.support_items_open, -1),
        refund_requests=parse_int(args.refund_requests, -1),
        claims_issues=parse_int(args.claims_issues, -1),
        incidents=parse_int(args.incidents, -1),
        decision=args.decision,
        owner=args.owner,
        monitor_notes=args.monitor_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_step=args.allow_no_go_step,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
