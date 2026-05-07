from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "next_controlled_buyer_outcome.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "next_controlled_buyer_outcome"
DEFAULT_READINESS_DIR = TOOL_ROOT / "data" / "next_controlled_buyer_readiness"


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


def latest_readiness_file(directory: Path = DEFAULT_READINESS_DIR) -> Path | None:
    return latest_file(directory, "next_controlled_buyer_readiness_*.json")


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
    readiness_config_path = project_path(str(depends_on.get("nextControlledBuyerReadinessConfig", "")))
    if not readiness_config_path.is_file():
        return ["next_controlled_buyer_readiness_config_missing"]
    readiness_config = load_json(readiness_config_path)
    if readiness_config.get("state") != depends_on.get("nextControlledBuyerReadinessState"):
        return ["next_controlled_buyer_readiness_state_invalid"]
    return []


def validate_readiness(readiness: dict[str, Any] | None, allow_no_go_readiness: bool) -> list[str]:
    if readiness is None:
        return ["next_controlled_buyer_readiness_evidence_missing"]
    decision = readiness.get("decision", {})
    if not decision.get("go") and not allow_no_go_readiness:
        return ["next_controlled_buyer_readiness_not_go", *decision.get("blockers", [])]
    readiness_decision = readiness.get("readiness_decision", "")
    if readiness_decision != "share_private_link" and not allow_no_go_readiness:
        return ["next_controlled_buyer_readiness_not_shared"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def outcome_checklist() -> list[str]:
    return [
        "Confirm the previous readiness evidence was GO before the buyer link was shared.",
        "Record only redacted purchase and activation outcome metrics.",
        "Confirm first value, support state and follow-up were reviewed.",
        "Check refund, fulfillment and safe-claims risk before any wider distribution.",
        "Choose repeat, hold, pause or carefully widen with an explicit owner.",
    ]


def decision_from(
    config: dict[str, Any],
    readiness: dict[str, Any] | None,
    outcome_status: str,
    activation_confirmed: bool,
    first_value_confirmed: bool,
    first_value_score: int,
    followup_completed: bool,
    support_items_open: int,
    refund_requests: int,
    fulfillment_failures: int,
    claims_issues: int,
    decision: str,
    owner: str,
    outcome_notes: str,
    next_action: str,
    confirmations: dict[str, bool],
    allow_no_go_readiness: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_readiness(readiness, allow_no_go_readiness))

    if outcome_status not in set(config.get("allowedOutcomeStatuses", [])):
        blockers.append("next_buyer_outcome_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("next_buyer_outcome_decision_invalid")
    if not is_safe_text(owner):
        blockers.append("next_buyer_outcome_owner_missing_or_unsafe")
    if not outcome_notes.strip():
        blockers.append("next_buyer_outcome_notes_missing")
    if not next_action.strip():
        blockers.append("next_buyer_next_action_missing")

    metrics = [first_value_score, support_items_open, refund_requests, fulfillment_failures, claims_issues]
    if any(value < 0 for value in metrics):
        blockers.append("next_buyer_outcome_metrics_invalid")
    if support_items_open > int(config.get("maximumOpenSupportItems", 0)):
        blockers.append("open_support_items_require_hold_or_pause")
    if refund_requests > int(config.get("maximumRefundRequests", 0)):
        blockers.append("refund_requests_require_pause_sales")
    if fulfillment_failures > int(config.get("maximumFulfillmentFailures", 0)):
        blockers.append("fulfillment_failures_require_pause_sales")
    if claims_issues > int(config.get("maximumClaimsIssues", 0)):
        blockers.append("claims_issues_require_pause_sales")

    if decision == "carefully_widen":
        if outcome_status != "completed":
            blockers.append("carefully_widen_requires_completed_outcome")
        if not activation_confirmed:
            blockers.append("carefully_widen_requires_activation")
        if not first_value_confirmed:
            blockers.append("carefully_widen_requires_first_value")
        if first_value_score < int(config.get("minimumFirstValueScore", 7)):
            blockers.append("carefully_widen_requires_first_value_score")
        if not followup_completed:
            blockers.append("carefully_widen_requires_followup")
    if decision == "repeat_private_slot":
        if outcome_status not in {"completed", "partial"}:
            blockers.append("repeat_private_slot_requires_completed_or_partial_outcome")
        if refund_requests or fulfillment_failures or claims_issues:
            blockers.append("repeat_private_slot_blocked_by_risk")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if outcome_status in {"failed", "refunded"} and decision != "pause_sales":
        blockers.append("failed_or_refunded_outcome_requires_pause_sales")
    if outcome_status == "no_show" and decision not in {"hold_for_fix", "pause_sales"}:
        blockers.append("no_show_requires_hold_or_pause")

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
        "# Next Controlled Buyer Outcome Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Outcome decision: `{report.get('outcome_decision') or 'missing'}`",
        f"- Outcome status: `{report.get('outcome_status') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["outcome_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("first_value_score", "support_items_open", "refund_requests", "fulfillment_failures", "claims_issues"):
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
    json_path = output_dir / f"next_controlled_buyer_outcome_{current_stamp}.json"
    md_path = output_dir / f"next_controlled_buyer_outcome_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_next_buyer_outcome(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    readiness_file: Path | None = None,
    outcome_status: str = "",
    activation_confirmed: bool = False,
    first_value_confirmed: bool = False,
    first_value_score: int = -1,
    followup_completed: bool = False,
    support_items_open: int = -1,
    refund_requests: int = -1,
    fulfillment_failures: int = -1,
    claims_issues: int = -1,
    decision: str = "repeat_private_slot",
    owner: str = "",
    outcome_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_readiness: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    readiness = load_json(readiness_file) if readiness_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "next_controlled_buyer_outcome_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "readiness_source": str(readiness_file) if readiness_file else "",
        "readiness_decision": readiness.get("decision") if readiness else None,
        "readiness_action": readiness.get("readiness_decision") if readiness else "",
        "outcome_status": outcome_status.strip(),
        "activation_confirmed": activation_confirmed,
        "first_value_confirmed": first_value_confirmed,
        "first_value_score": first_value_score,
        "followup_completed": followup_completed,
        "support_items_open": support_items_open,
        "refund_requests": refund_requests,
        "fulfillment_failures": fulfillment_failures,
        "claims_issues": claims_issues,
        "outcome_decision": decision.strip(),
        "owner": owner.strip(),
        "outcome_notes": outcome_notes.strip(),
        "next_action": next_action.strip(),
        "outcome_checklist": outcome_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        readiness,
        outcome_status.strip(),
        activation_confirmed,
        first_value_confirmed,
        first_value_score,
        followup_completed,
        support_items_open,
        refund_requests,
        fulfillment_failures,
        claims_issues,
        decision.strip(),
        owner,
        outcome_notes,
        next_action,
        final_confirmations,
        allow_no_go_readiness,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Record the next controlled buyer outcome and next distribution decision.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--readiness-file", default="")
    parser.add_argument("--use-latest-readiness", action="store_true")
    parser.add_argument("--allow-no-go-readiness", action="store_true")
    parser.add_argument("--outcome-status", default="")
    parser.add_argument("--activation-confirmed", action="store_true")
    parser.add_argument("--first-value-confirmed", action="store_true")
    parser.add_argument("--first-value-score", default="")
    parser.add_argument("--followup-completed", action="store_true")
    parser.add_argument("--support-items-open", default="")
    parser.add_argument("--refund-requests", default="")
    parser.add_argument("--fulfillment-failures", default="")
    parser.add_argument("--claims-issues", default="")
    parser.add_argument("--decision", default="repeat_private_slot")
    parser.add_argument("--owner", default="")
    parser.add_argument("--outcome-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-readiness-go-reviewed", action="store_true")
    parser.add_argument("--confirm-purchase-outcome-recorded", action="store_true")
    parser.add_argument("--confirm-license-activation-reviewed", action="store_true")
    parser.add_argument("--confirm-first-value-reviewed", action="store_true")
    parser.add_argument("--confirm-support-outcome-reviewed", action="store_true")
    parser.add_argument("--confirm-refund-risk-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-next-decision-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    readiness_file = Path(args.readiness_file) if args.readiness_file else None
    if args.use_latest_readiness and readiness_file is None:
        readiness_file = latest_readiness_file()
        if readiness_file is None:
            print(json.dumps({"ok": False, "error": "next_controlled_buyer_readiness_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "readiness_go_reviewed": args.confirm_readiness_go_reviewed,
        "purchase_outcome_recorded": args.confirm_purchase_outcome_recorded,
        "license_activation_reviewed": args.confirm_license_activation_reviewed,
        "first_value_reviewed": args.confirm_first_value_reviewed,
        "support_outcome_reviewed": args.confirm_support_outcome_reviewed,
        "refund_risk_reviewed": args.confirm_refund_risk_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "next_decision_recorded": args.confirm_next_decision_recorded,
    }
    report = collect_next_buyer_outcome(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        readiness_file=readiness_file,
        outcome_status=args.outcome_status,
        activation_confirmed=args.activation_confirmed,
        first_value_confirmed=args.first_value_confirmed,
        first_value_score=parse_int(args.first_value_score, -1),
        followup_completed=args.followup_completed,
        support_items_open=parse_int(args.support_items_open, -1),
        refund_requests=parse_int(args.refund_requests, -1),
        fulfillment_failures=parse_int(args.fulfillment_failures, -1),
        claims_issues=parse_int(args.claims_issues, -1),
        decision=args.decision,
        owner=args.owner,
        outcome_notes=args.outcome_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_readiness=args.allow_no_go_readiness,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
