from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "controlled_distribution_review.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "controlled_distribution_review"
DEFAULT_DISTRIBUTION_DIR = TOOL_ROOT / "data" / "controlled_distribution_step"
EXPECTED_STATE = "controlled_distribution_review_ready"


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


def latest_distribution_file(directory: Path = DEFAULT_DISTRIBUTION_DIR) -> Path | None:
    return latest_file(directory, "controlled_distribution_step_*.json")


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
    distribution_config_path = project_path(str(depends_on.get("controlledDistributionStepConfig", "")))
    if not distribution_config_path.is_file():
        return ["controlled_distribution_step_config_missing"]
    distribution_config = load_json(distribution_config_path)
    if distribution_config.get("state") != depends_on.get("controlledDistributionStepState"):
        return ["controlled_distribution_step_state_invalid"]
    return []


def validate_distribution_step(distribution_step: dict[str, Any] | None, allow_no_go_step: bool) -> list[str]:
    if distribution_step is None:
        return ["controlled_distribution_step_evidence_missing"]
    decision = distribution_step.get("decision", {})
    if not decision.get("go") and not allow_no_go_step:
        return ["controlled_distribution_step_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def review_checklist() -> list[str]:
    return [
        "Load the M72 controlled distribution evidence before choosing a next move.",
        "Record only redacted aggregate outcome metrics.",
        "Check support, refund and safe-claims risk before preparing any buyer-facing asset.",
        "Keep repeat/asset/pause decisions small enough to reverse manually.",
        "Record owner and next action before another distribution step.",
    ]


def decision_from(
    config: dict[str, Any],
    distribution_step: dict[str, Any] | None,
    source_action: str,
    review_status: str,
    positive_signals: int,
    support_items_open: int,
    refund_requests: int,
    claims_issues: int,
    decision: str,
    owner: str,
    review_notes: str,
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
    blockers.extend(validate_distribution_step(distribution_step, allow_no_go_step))

    if source_action not in set(config.get("allowedSourceActions", [])):
        blockers.append("controlled_distribution_review_source_action_invalid")
    if review_status not in set(config.get("allowedReviewStatuses", [])):
        blockers.append("controlled_distribution_review_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("controlled_distribution_review_decision_invalid")
    if distribution_step and source_action != distribution_step.get("action"):
        blockers.append("controlled_distribution_review_source_action_not_m72_action")

    if any(value < 0 for value in (positive_signals, support_items_open, refund_requests, claims_issues)):
        blockers.append("controlled_distribution_review_metrics_invalid")
    if support_items_open > int(config.get("maximumOpenSupportItems", 0)):
        blockers.append("controlled_distribution_review_open_support_requires_hold_or_pause")
    if refund_requests > int(config.get("maximumRefundRequests", 0)):
        blockers.append("controlled_distribution_review_refunds_require_pause")
    if claims_issues > int(config.get("maximumClaimsIssues", 0)):
        blockers.append("controlled_distribution_review_claims_require_pause")
    if not is_safe_text(owner):
        blockers.append("controlled_distribution_review_owner_missing_or_unsafe")
    if not review_notes.strip():
        blockers.append("controlled_distribution_review_notes_missing")
    if not next_action.strip():
        blockers.append("controlled_distribution_review_next_action_missing")

    if decision == "prepare_buyer_facing_asset":
        if review_status != "completed":
            blockers.append("prepare_buyer_facing_asset_requires_completed_review")
        if positive_signals < int(config.get("minimumPositiveSignalsForAsset", 2)):
            blockers.append("prepare_buyer_facing_asset_requires_positive_signals")
        if source_action == "pause_checkout_and_review":
            blockers.append("prepare_buyer_facing_asset_blocked_after_pause")
    if decision == "repeat_distribution_step":
        if review_status not in {"completed", "partial"}:
            blockers.append("repeat_distribution_step_requires_completed_or_partial_review")
        if refund_requests or claims_issues:
            blockers.append("repeat_distribution_step_blocked_by_risk")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if review_status == "paused" and decision != "pause_sales":
        blockers.append("paused_distribution_requires_pause_sales")
    if review_status == "blocked" and decision not in {"hold_for_fix", "pause_sales"}:
        blockers.append("blocked_distribution_requires_hold_or_pause")
    if (refund_requests or claims_issues) and decision != "pause_sales":
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
        "# Controlled Distribution Review Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Review decision: `{report.get('review_decision') or 'missing'}`",
        f"- Review status: `{report.get('review_status') or 'missing'}`",
        f"- Source action: `{report.get('source_action') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["review_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("positive_signals", "support_items_open", "refund_requests", "claims_issues"):
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
    json_path = output_dir / f"controlled_distribution_review_{current_stamp}.json"
    md_path = output_dir / f"controlled_distribution_review_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_controlled_distribution_review(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    distribution_file: Path | None = None,
    source_action: str = "",
    review_status: str = "",
    positive_signals: int = -1,
    support_items_open: int = -1,
    refund_requests: int = -1,
    claims_issues: int = -1,
    decision: str = "",
    owner: str = "",
    review_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_step: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    distribution_step = load_json(distribution_file) if distribution_file else None
    confirmations = confirmations or {}
    review_decision = decision_from(
        config=config,
        distribution_step=distribution_step,
        source_action=source_action,
        review_status=review_status,
        positive_signals=positive_signals,
        support_items_open=support_items_open,
        refund_requests=refund_requests,
        claims_issues=claims_issues,
        decision=decision,
        owner=owner,
        review_notes=review_notes,
        next_action=next_action,
        confirmations=confirmations,
        allow_no_go_step=allow_no_go_step,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "review_id": config.get("reviewId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_distribution_file": str(distribution_file) if distribution_file else "",
        "source_action": source_action,
        "source_decision": distribution_step.get("source_decision", "") if distribution_step else "",
        "review_status": review_status,
        "positive_signals": positive_signals,
        "support_items_open": support_items_open,
        "refund_requests": refund_requests,
        "claims_issues": claims_issues,
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
    parser = argparse.ArgumentParser(
        description="Review M72 controlled distribution evidence and choose the next small move.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--distribution-file", type=Path)
    parser.add_argument("--use-latest-distribution", action="store_true")
    parser.add_argument("--allow-no-go-step", action="store_true")
    parser.add_argument("--source-action", default="")
    parser.add_argument("--review-status", default="")
    parser.add_argument("--positive-signals", default="")
    parser.add_argument("--support-items-open", default="")
    parser.add_argument("--refund-requests", default="")
    parser.add_argument("--claims-issues", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-distribution-reviewed", action="store_true")
    parser.add_argument("--confirm-support-reviewed", action="store_true")
    parser.add_argument("--confirm-refund-risk-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-next-decision-recorded", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    distribution_file = args.distribution_file
    if args.use_latest_distribution:
        distribution_file = latest_distribution_file()

    confirmations = {
        "distribution_reviewed": args.confirm_distribution_reviewed,
        "support_reviewed": args.confirm_support_reviewed,
        "refund_risk_reviewed": args.confirm_refund_risk_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "next_decision_recorded": args.confirm_next_decision_recorded,
    }
    report = collect_controlled_distribution_review(
        config_path=args.config,
        manifest_path=args.manifest,
        distribution_file=distribution_file,
        source_action=args.source_action,
        review_status=args.review_status,
        positive_signals=parse_int(args.positive_signals, -1),
        support_items_open=parse_int(args.support_items_open, -1),
        refund_requests=parse_int(args.refund_requests, -1),
        claims_issues=parse_int(args.claims_issues, -1),
        decision=args.decision,
        owner=args.owner,
        review_notes=args.review_notes,
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
