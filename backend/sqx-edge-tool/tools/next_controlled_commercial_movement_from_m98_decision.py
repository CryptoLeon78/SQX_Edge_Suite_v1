from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "next_controlled_commercial_movement_from_m98_decision.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "next_controlled_commercial_movement_from_m98_decision"
DEFAULT_MONITOR_DIR = TOOL_ROOT / "data" / "approved_controlled_commercial_movement_from_m96_decision_execution_monitor"
EXPECTED_STATE = "next_controlled_commercial_movement_from_m98_decision_ready"


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


def latest_monitor_file(directory: Path = DEFAULT_MONITOR_DIR) -> Path | None:
    return latest_file(directory, "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_*.json")


def parse_int(value: str, default: int) -> int:
    return default if value == "" else int(value)


def safe_text(value: str) -> bool:
    return bool(value.strip()) and not bool(re.search(r"[\r\n<>]", value))


def validate_required_files(config: dict[str, Any]) -> list[str]:
    return [
        f"missing_required_file:{item}"
        for item in config.get("requiredFiles", [])
        if not project_path(str(item)).is_file()
    ]


def validate_dependency(config: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if config.get("state") != EXPECTED_STATE:
        blockers.append("next_controlled_commercial_movement_from_m98_decision_state_invalid")
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    monitor_config_path = project_path(str(depends_on.get("approvedControlledCommercialMovementFromM96DecisionExecutionMonitorConfig", "")))
    if not monitor_config_path.is_file():
        return [*blockers, "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_config_missing"]
    monitor_config = load_json(monitor_config_path)
    if monitor_config.get("state") != depends_on.get("approvedControlledCommercialMovementFromM96DecisionExecutionMonitorState"):
        blockers.append("approved_controlled_commercial_movement_from_m96_decision_execution_monitor_state_invalid")
    return blockers


def validate_monitor(monitor: dict[str, Any] | None, allow_no_go_monitor: bool) -> list[str]:
    if monitor is None:
        return ["approved_controlled_commercial_movement_from_m96_decision_execution_monitor_evidence_missing"]
    decision = monitor.get("decision", {})
    if not decision.get("go") and not allow_no_go_monitor:
        return ["approved_controlled_commercial_movement_from_m96_decision_execution_monitor_not_go", *decision.get("blockers", [])]
    return []


def metric_from(monitor: dict[str, Any] | None, key: str, fallback: int) -> int:
    if not monitor:
        return fallback
    try:
        return int(monitor.get(key, fallback))
    except (TypeError, ValueError):
        return fallback


def monitor_decision(monitor: dict[str, Any] | None) -> str:
    return str(monitor.get("monitor_decision", "")) if monitor else ""


def monitor_status(monitor: dict[str, Any] | None) -> str:
    return str(monitor.get("monitor_status", "")) if monitor else ""


def decision_checklist() -> list[str]:
    return [
        "Load the M98 monitor evidence before deciding any next commercial movement.",
        "Choose exactly one next movement and keep it manual.",
        "Never publish, email, open checkout or issue licenses from this gate.",
        "Pause when refunds, claims, incidents or unresolved support appear.",
        "Record owner, rationale and next gate before any manual follow-up.",
    ]


def decision_from(
    config: dict[str, Any],
    monitor: dict[str, Any] | None,
    source_decision: str,
    next_movement: str,
    observation_hours: int,
    positive_signals: int,
    support_items_open: int,
    refund_requests: int,
    claims_issues: int,
    incidents: int,
    owner: str,
    rationale: str,
    next_gate: str,
    confirmations: dict[str, bool],
    allow_no_go_monitor: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_monitor(monitor, allow_no_go_monitor))

    source_monitor_decision = monitor_decision(monitor)
    source_monitor_status = monitor_status(monitor)
    if source_decision not in set(config.get("allowedSourceMonitorDecisions", [])):
        blockers.append("next_controlled_commercial_movement_from_m98_source_decision_invalid")
    if next_movement not in set(config.get("allowedNextMovements", [])):
        blockers.append("next_controlled_commercial_movement_from_m98_invalid")
    if monitor and source_decision != source_monitor_decision:
        blockers.append("next_controlled_commercial_movement_from_m98_source_not_m98_decision")
    if any(value < 0 for value in (observation_hours, positive_signals, support_items_open, refund_requests, claims_issues, incidents)):
        blockers.append("next_controlled_commercial_movement_from_m98_metrics_invalid")
    if not safe_text(owner):
        blockers.append("next_controlled_commercial_movement_from_m98_owner_missing_or_unsafe")
    if not rationale.strip():
        blockers.append("next_controlled_commercial_movement_from_m98_rationale_missing")
    if not next_gate.strip():
        blockers.append("next_controlled_commercial_movement_from_m98_next_gate_missing")
    if observation_hours < int(config.get("minimumObservationHours", 24)):
        blockers.append("next_controlled_commercial_movement_from_m98_requires_observation_time")

    risk_counts = {
        "support_items_open": (support_items_open, int(config.get("maximumOpenSupportItems", 0))),
        "refund_requests": (refund_requests, int(config.get("maximumRefundRequests", 0))),
        "claims_issues": (claims_issues, int(config.get("maximumClaimsIssues", 0))),
        "incidents": (incidents, int(config.get("maximumIncidents", 0))),
    }
    risk_present = any(value > maximum for value, maximum in risk_counts.values())
    for name, (value, maximum) in risk_counts.items():
        if value > maximum:
            blockers.append(f"next_controlled_commercial_movement_from_m98_{name}_requires_hold_or_pause")

    if next_movement == "prepare_next_micro_step":
        if source_decision != "prepare_next_decision":
            blockers.append("prepare_next_micro_step_requires_m98_prepare_next_decision")
        if positive_signals < int(config.get("minimumPositiveSignalsForMovement", 1)):
            blockers.append("prepare_next_micro_step_requires_positive_signal")
        if risk_present:
            blockers.append("prepare_next_micro_step_blocked_by_risk")
    if next_movement == "prepare_private_review_packet":
        if source_decision not in {"prepare_next_decision", "prepare_private_review_packet"}:
            blockers.append("prepare_private_review_packet_requires_m98_review_or_decision")
        if source_monitor_status not in {"completed", "partial"}:
            blockers.append("prepare_private_review_packet_requires_completed_or_partial_monitor")
        if risk_present:
            blockers.append("prepare_private_review_packet_blocked_by_risk")
    if next_movement == "continue_observation":
        warnings.append("operator_decision_continue_observation")
        if risk_present:
            blockers.append("continue_observation_blocked_by_risk")
    if next_movement == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if next_movement == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if source_monitor_status == "paused" and next_movement != "pause_sales":
        blockers.append("paused_monitor_requires_pause_sales")
    if source_monitor_status == "blocked" and next_movement not in {"hold_for_fix", "pause_sales"}:
        blockers.append("blocked_monitor_requires_hold_or_pause")
    if (refund_requests or claims_issues or incidents) and next_movement != "pause_sales":
        blockers.append("risk_events_require_pause_sales")

    deduped = sorted(set(blockers))
    return {
        "go": not deduped,
        "label": "GO" if not deduped else "NO-GO",
        "blockers": deduped,
        "warnings": sorted(set(warnings)),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# Next Controlled Commercial Movement From M98 Decision Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Source monitor decision: `{report.get('source_monitor_decision') or 'missing'}`",
        f"- Next movement: `{report.get('next_movement') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["decision_checklist"])
    lines.append("")
    lines.append("## Redacted Inputs")
    for name in ("observation_hours", "positive_signals", "support_items_open", "refund_requests", "claims_issues", "incidents"):
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
    json_path = output_dir / f"next_controlled_commercial_movement_from_m98_decision_{current_stamp}.json"
    md_path = output_dir / f"next_controlled_commercial_movement_from_m98_decision_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_decision(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    monitor_file: Path | None = None,
    source_decision: str = "",
    next_movement: str = "",
    observation_hours: int = -1,
    positive_signals: int = -1,
    support_items_open: int = -1,
    refund_requests: int = -1,
    claims_issues: int = -1,
    incidents: int = -1,
    owner: str = "",
    rationale: str = "",
    next_gate: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_monitor: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    monitor = load_json(monitor_file) if monitor_file else None
    confirmations = confirmations or {}
    if monitor:
        observation_hours = observation_hours if observation_hours >= 0 else metric_from(monitor, "observation_hours", -1)
        positive_signals = positive_signals if positive_signals >= 0 else metric_from(monitor, "positive_signals", -1)
        support_items_open = support_items_open if support_items_open >= 0 else metric_from(monitor, "support_items_open", -1)
        refund_requests = refund_requests if refund_requests >= 0 else metric_from(monitor, "refund_requests", -1)
        claims_issues = claims_issues if claims_issues >= 0 else metric_from(monitor, "claims_issues", -1)
        incidents = incidents if incidents >= 0 else metric_from(monitor, "incidents", -1)
    operator_decision = decision_from(
        config=config,
        monitor=monitor,
        source_decision=source_decision,
        next_movement=next_movement,
        observation_hours=observation_hours,
        positive_signals=positive_signals,
        support_items_open=support_items_open,
        refund_requests=refund_requests,
        claims_issues=claims_issues,
        incidents=incidents,
        owner=owner,
        rationale=rationale,
        next_gate=next_gate,
        confirmations=confirmations,
        allow_no_go_monitor=allow_no_go_monitor,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "decision_id": config.get("decisionId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_monitor_file": str(monitor_file) if monitor_file else "",
        "source_monitor_decision": source_decision,
        "source_monitor_status": monitor_status(monitor),
        "next_movement": next_movement,
        "observation_hours": observation_hours,
        "positive_signals": positive_signals,
        "support_items_open": support_items_open,
        "refund_requests": refund_requests,
        "claims_issues": claims_issues,
        "incidents": incidents,
        "owner": owner,
        "rationale": rationale,
        "next_gate": next_gate,
        "confirmations": confirmations,
        "decision_checklist": decision_checklist(),
        "decision": operator_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "decision_policy": config.get("decisionPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Decide the next controlled commercial movement from M98 evidence.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--monitor-file", type=Path)
    parser.add_argument("--use-latest-monitor", action="store_true")
    parser.add_argument("--allow-no-go-monitor", action="store_true")
    parser.add_argument("--source-decision", default="")
    parser.add_argument("--next-movement", default="")
    parser.add_argument("--observation-hours", default="")
    parser.add_argument("--positive-signals", default="")
    parser.add_argument("--support-items-open", default="")
    parser.add_argument("--refund-requests", default="")
    parser.add_argument("--claims-issues", default="")
    parser.add_argument("--incidents", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--rationale", default="")
    parser.add_argument("--next-gate", default="")
    parser.add_argument("--confirm-monitor-reviewed", action="store_true")
    parser.add_argument("--confirm-no-automation", action="store_true")
    parser.add_argument("--confirm-support-clear-or-paused", action="store_true")
    parser.add_argument("--confirm-claims-clear-or-paused", action="store_true")
    parser.add_argument("--confirm-redacted-evidence", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    monitor_file = args.monitor_file
    if args.use_latest_monitor:
        monitor_file = latest_monitor_file()
    report = collect_decision(
        config_path=args.config,
        manifest_path=args.manifest,
        monitor_file=monitor_file,
        source_decision=args.source_decision,
        next_movement=args.next_movement,
        observation_hours=parse_int(args.observation_hours, -1),
        positive_signals=parse_int(args.positive_signals, -1),
        support_items_open=parse_int(args.support_items_open, -1),
        refund_requests=parse_int(args.refund_requests, -1),
        claims_issues=parse_int(args.claims_issues, -1),
        incidents=parse_int(args.incidents, -1),
        owner=args.owner,
        rationale=args.rationale,
        next_gate=args.next_gate,
        confirmations={
            "monitor_reviewed": args.confirm_monitor_reviewed,
            "no_automation": args.confirm_no_automation,
            "support_clear_or_paused": args.confirm_support_clear_or_paused,
            "claims_clear_or_paused": args.confirm_claims_clear_or_paused,
            "redacted_evidence": args.confirm_redacted_evidence,
        },
        allow_no_go_monitor=args.allow_no_go_monitor,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
