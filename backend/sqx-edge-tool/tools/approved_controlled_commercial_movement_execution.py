from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_execution.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "approved_controlled_commercial_movement_execution"
DEFAULT_DECISION_DIR = TOOL_ROOT / "data" / "next_controlled_commercial_movement_decision"
EXPECTED_STATE = "approved_controlled_commercial_movement_execution_ready"


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


def latest_decision_file(directory: Path = DEFAULT_DECISION_DIR) -> Path | None:
    return latest_file(directory, "next_controlled_commercial_movement_decision_*.json")


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
        blockers.append("approved_controlled_commercial_movement_execution_state_invalid")
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    decision_config_path = project_path(str(depends_on.get("nextControlledCommercialMovementDecisionConfig", "")))
    if not decision_config_path.is_file():
        return [*blockers, "next_controlled_commercial_movement_decision_config_missing"]
    decision_config = load_json(decision_config_path)
    if decision_config.get("state") != depends_on.get("nextControlledCommercialMovementDecisionState"):
        blockers.append("next_controlled_commercial_movement_decision_state_invalid")
    return blockers


def validate_source(decision_record: dict[str, Any] | None, allow_no_go_decision: bool) -> list[str]:
    if decision_record is None:
        return ["next_controlled_commercial_movement_decision_evidence_missing"]
    decision = decision_record.get("decision", {})
    if not decision.get("go") and not allow_no_go_decision:
        return ["next_controlled_commercial_movement_decision_not_go", *decision.get("blockers", [])]
    return []


def source_next_movement(decision_record: dict[str, Any] | None) -> str:
    return str(decision_record.get("next_movement", "")) if decision_record else ""


def execution_checklist() -> list[str]:
    return [
        "Load the approved M90 next-movement decision before recording execution.",
        "Record only the exact M90-approved manual movement.",
        "Never publish, email, open checkout or issue licenses from this gate.",
        "Keep micro-step preparation within one private link and three invites.",
        "Set the next monitor before considering any further commercial movement.",
    ]


def execution_decision_from(
    config: dict[str, Any],
    decision_record: dict[str, Any] | None,
    source_movement: str,
    execution_result: str,
    new_private_links: int,
    new_invites: int,
    owner: str,
    execution_summary: str,
    next_monitor: str,
    confirmations: dict[str, bool],
    allow_no_go_decision: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_source(decision_record, allow_no_go_decision))

    required_by_movement = config.get("requiredResultByMovement", {})
    expected_result = required_by_movement.get(source_movement)
    if source_movement not in set(config.get("allowedSourceNextMovements", [])):
        blockers.append("approved_controlled_commercial_movement_execution_source_invalid")
    if execution_result not in set(config.get("allowedExecutionResults", [])):
        blockers.append("approved_controlled_commercial_movement_execution_result_invalid")
    if decision_record and source_movement != source_next_movement(decision_record):
        blockers.append("approved_controlled_commercial_movement_execution_source_not_m90_movement")
    if expected_result and execution_result != expected_result:
        blockers.append("approved_controlled_commercial_movement_execution_result_not_allowed_for_m90_movement")
    if any(value < 0 for value in (new_private_links, new_invites)):
        blockers.append("approved_controlled_commercial_movement_execution_metrics_invalid")
    if not safe_text(owner):
        blockers.append("approved_controlled_commercial_movement_execution_owner_missing_or_unsafe")
    if not execution_summary.strip():
        blockers.append("approved_controlled_commercial_movement_execution_summary_missing")
    if not next_monitor.strip():
        blockers.append("approved_controlled_commercial_movement_execution_next_monitor_missing")

    if execution_result == "next_micro_step_prepared":
        if new_private_links > int(config.get("maximumNewPrivateLinks", 1)):
            blockers.append("next_micro_step_prepared_private_link_limit_exceeded")
        if new_invites > int(config.get("maximumNewInvites", 3)):
            blockers.append("next_micro_step_prepared_invite_limit_exceeded")
    elif new_private_links or new_invites:
        blockers.append("non_micro_step_execution_must_not_create_new_traffic")

    if execution_result in {"observation_continued", "fix_hold_recorded", "sales_pause_recorded"}:
        warnings.append(f"operator_execution_{execution_result}")

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
        "# Approved Controlled Commercial Movement Execution Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Source movement: `{report.get('source_movement') or 'missing'}`",
        f"- Execution result: `{report.get('execution_result') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["execution_checklist"])
    lines.append("")
    lines.append("## Redacted Metrics")
    for name in ("new_private_links", "new_invites"):
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
    json_path = output_dir / f"approved_controlled_commercial_movement_execution_{current_stamp}.json"
    md_path = output_dir / f"approved_controlled_commercial_movement_execution_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_execution(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    decision_file: Path | None = None,
    source_movement: str = "",
    execution_result: str = "",
    new_private_links: int = -1,
    new_invites: int = -1,
    owner: str = "",
    execution_summary: str = "",
    next_monitor: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_decision: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    decision_record = load_json(decision_file) if decision_file else None
    confirmations = confirmations or {}
    decision = execution_decision_from(
        config,
        decision_record,
        source_movement,
        execution_result,
        new_private_links,
        new_invites,
        owner,
        execution_summary,
        next_monitor,
        confirmations,
        allow_no_go_decision,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "execution_id": config.get("executionId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_decision_file": str(decision_file) if decision_file else "",
        "source_movement": source_movement,
        "source_decision_status": decision_record.get("decision", {}).get("label", "") if decision_record else "",
        "execution_result": execution_result,
        "new_private_links": new_private_links,
        "new_invites": new_invites,
        "owner": owner,
        "execution_summary": execution_summary,
        "next_monitor": next_monitor,
        "confirmations": confirmations,
        "execution_checklist": execution_checklist(),
        "decision": decision,
        "privacy_policy": config.get("privacyPolicy"),
        "execution_policy": config.get("executionPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record the exact manual execution approved by the M90 next-movement gate.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--decision-file", type=Path)
    parser.add_argument("--use-latest-decision", action="store_true")
    parser.add_argument("--allow-no-go-decision", action="store_true")
    parser.add_argument("--source-movement", default="")
    parser.add_argument("--execution-result", default="")
    parser.add_argument("--new-private-links", default="")
    parser.add_argument("--new-invites", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--execution-summary", default="")
    parser.add_argument("--next-monitor", default="")
    parser.add_argument("--confirm-decision-reviewed", action="store_true")
    parser.add_argument("--confirm-exact-movement", action="store_true")
    parser.add_argument("--confirm-no-automation", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-redacted-evidence", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    decision_file = args.decision_file
    if args.use_latest_decision:
        decision_file = latest_decision_file()
    report = collect_execution(
        config_path=args.config,
        manifest_path=args.manifest,
        decision_file=decision_file,
        source_movement=args.source_movement,
        execution_result=args.execution_result,
        new_private_links=parse_int(args.new_private_links, -1),
        new_invites=parse_int(args.new_invites, -1),
        owner=args.owner,
        execution_summary=args.execution_summary,
        next_monitor=args.next_monitor,
        confirmations={
            "decision_reviewed": args.confirm_decision_reviewed,
            "exact_movement": args.confirm_exact_movement,
            "no_automation": args.confirm_no_automation,
            "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
            "redacted_evidence": args.confirm_redacted_evidence,
        },
        allow_no_go_decision=args.allow_no_go_decision,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
