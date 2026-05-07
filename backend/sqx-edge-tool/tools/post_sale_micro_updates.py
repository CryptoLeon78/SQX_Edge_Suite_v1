from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "post_sale_micro_updates.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "post_sale_micro_updates"
DEFAULT_IMPROVEMENT_DIR = TOOL_ROOT / "data" / "post_sale_improvement_loop"


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


def latest_improvement_file(directory: Path = DEFAULT_IMPROVEMENT_DIR) -> Path | None:
    return latest_file(directory, "post_sale_improvement_loop_*.json")


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


def validate_required_markers(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    markers = config.get("requiredMarkers") if isinstance(config.get("requiredMarkers"), dict) else {}
    for rel_path, expected_markers in markers.items():
        path = project_path(str(rel_path))
        if not path.is_file():
            findings.append(f"missing_marker_file:{rel_path}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for marker in expected_markers:
            if str(marker) not in text:
                findings.append(f"missing_marker:{rel_path}:{marker}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    improvement_config_path = project_path(str(depends_on.get("postSaleImprovementLoopConfig", "")))
    if not improvement_config_path.is_file():
        return ["post_sale_improvement_loop_config_missing"]
    improvement_config = load_json(improvement_config_path)
    if improvement_config.get("state") != depends_on.get("postSaleImprovementLoopState"):
        return ["post_sale_improvement_loop_state_invalid"]
    return []


def validate_improvement_loop(improvement: dict[str, Any] | None, allow_no_go_improvement: bool) -> list[str]:
    if improvement is None:
        return ["post_sale_improvement_loop_evidence_missing"]
    decision = improvement.get("decision", {})
    if not decision.get("go") and not allow_no_go_improvement:
        return ["post_sale_improvement_loop_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def readiness_checklist() -> list[str]:
    return [
        "Confirm post-sale improvement loop evidence is GO.",
        "Verify START_HERE explains first value in plain language.",
        "Verify license walkthrough has a quick status check.",
        "Verify support templates ask for exact step and first-value state.",
        "Verify public copy sets a calm first-value expectation.",
        "Record next controlled buyer readiness before sharing another private link.",
    ]


def decision_from(
    config: dict[str, Any],
    improvement: dict[str, Any] | None,
    applied_updates: int,
    onboarding_updates: int,
    support_macro_updates: int,
    public_copy_updates: int,
    safe_claims_updates: int,
    next_buyer_steps: int,
    support_risk: int,
    claims_risk: int,
    decision: str,
    priority: str,
    owner: str,
    next_review: str,
    update_summary: str,
    readiness_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_improvement: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_required_markers(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_improvement_loop(improvement, allow_no_go_improvement))

    counts = [
        applied_updates,
        onboarding_updates,
        support_macro_updates,
        public_copy_updates,
        safe_claims_updates,
        next_buyer_steps,
        support_risk,
        claims_risk,
    ]
    if any(value < 0 for value in counts):
        blockers.append("post_sale_micro_update_metrics_invalid")

    if applied_updates < int(config.get("minimumAppliedUpdates", 4)):
        blockers.append("post_sale_micro_updates_need_minimum_applied_updates")
    if next_buyer_steps < int(config.get("minimumNextBuyerSteps", 4)):
        blockers.append("next_buyer_readiness_steps_incomplete")
    if onboarding_updates <= 0:
        blockers.append("onboarding_micro_update_missing")
    if support_macro_updates <= 0:
        blockers.append("support_macro_micro_update_missing")
    if public_copy_updates <= 0:
        blockers.append("public_copy_micro_update_missing")

    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("post_sale_micro_update_decision_invalid")
    if priority not in set(config.get("allowedPriorities", [])):
        blockers.append("post_sale_micro_update_priority_invalid")
    if not is_safe_text(owner):
        blockers.append("post_sale_micro_update_owner_missing_or_unsafe")
    if not is_safe_text(next_review):
        blockers.append("post_sale_micro_update_next_review_missing_or_unsafe")
    if not update_summary.strip():
        blockers.append("post_sale_micro_update_summary_missing")
    if not readiness_notes.strip():
        blockers.append("next_buyer_readiness_notes_missing")

    improvement_decision = improvement.get("improvement_decision", "") if improvement else ""
    improvement_support_risk = int(improvement.get("support_risk", 0)) if improvement else 0
    improvement_claims_risk = int(improvement.get("claims_risk", 0)) if improvement else 0
    if improvement_decision == "pause_sales" and decision != "pause_sales":
        blockers.append("improvement_pause_sales_requires_pause_sales")
    if support_risk > 0 or improvement_support_risk > 0:
        warnings.append("support_risk_requires_operator_attention")
    if claims_risk > 0 or improvement_claims_risk > 0:
        blockers.append("claims_risk_requires_pause_sales")
    if decision == "next_controlled_buyer_ready":
        if improvement_decision not in {"ship_micro_updates", "revise_onboarding", "revise_support_macros", "revise_public_copy"}:
            blockers.append("next_buyer_ready_requires_improvement_decision")
        if support_risk > 1:
            blockers.append("next_buyer_ready_blocked_by_support_risk")
    if decision == "revise_more":
        warnings.append("operator_decision_revise_more")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if priority == "high":
        warnings.append("high_priority_next_buyer_readiness")

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
        "# Post-Sale Micro Updates Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Readiness decision: `{report.get('readiness_decision') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        f"- Next review: `{report.get('next_review') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["readiness_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in (
        "applied_updates",
        "onboarding_updates",
        "support_macro_updates",
        "public_copy_updates",
        "safe_claims_updates",
        "next_buyer_steps",
        "support_risk",
        "claims_risk",
    ):
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
    json_path = output_dir / f"post_sale_micro_updates_{current_stamp}.json"
    md_path = output_dir / f"post_sale_micro_updates_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_post_sale_micro_updates(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    improvement_file: Path | None = None,
    applied_updates: int = -1,
    onboarding_updates: int = -1,
    support_macro_updates: int = -1,
    public_copy_updates: int = -1,
    safe_claims_updates: int = -1,
    next_buyer_steps: int = -1,
    support_risk: int = -1,
    claims_risk: int = -1,
    decision: str = "next_controlled_buyer_ready",
    priority: str = "medium",
    owner: str = "",
    next_review: str = "",
    update_summary: str = "",
    readiness_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_improvement: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    improvement = load_json(improvement_file) if improvement_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "post_sale_micro_updates_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "improvement_source": str(improvement_file) if improvement_file else "",
        "improvement_decision": improvement.get("decision") if improvement else None,
        "improvement_action": improvement.get("improvement_decision") if improvement else "",
        "applied_updates": applied_updates,
        "onboarding_updates": onboarding_updates,
        "support_macro_updates": support_macro_updates,
        "public_copy_updates": public_copy_updates,
        "safe_claims_updates": safe_claims_updates,
        "next_buyer_steps": next_buyer_steps,
        "support_risk": support_risk,
        "claims_risk": claims_risk,
        "readiness_decision": decision,
        "priority": priority,
        "owner": owner.strip(),
        "next_review": next_review.strip(),
        "update_summary": update_summary.strip(),
        "readiness_notes": readiness_notes.strip(),
        "readiness_checklist": readiness_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        improvement,
        applied_updates,
        onboarding_updates,
        support_macro_updates,
        public_copy_updates,
        safe_claims_updates,
        next_buyer_steps,
        support_risk,
        claims_risk,
        decision,
        priority,
        owner,
        next_review,
        update_summary,
        readiness_notes,
        final_confirmations,
        allow_no_go_improvement,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify post-sale micro-updates and next controlled buyer readiness.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--improvement-file", default="")
    parser.add_argument("--use-latest-improvement-loop", action="store_true")
    parser.add_argument("--allow-no-go-improvement", action="store_true")
    parser.add_argument("--applied-updates", default="")
    parser.add_argument("--onboarding-updates", default="")
    parser.add_argument("--support-macro-updates", default="")
    parser.add_argument("--public-copy-updates", default="")
    parser.add_argument("--safe-claims-updates", default="")
    parser.add_argument("--next-buyer-steps", default="")
    parser.add_argument("--support-risk", default="")
    parser.add_argument("--claims-risk", default="")
    parser.add_argument("--decision", default="next_controlled_buyer_ready")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--owner", default="")
    parser.add_argument("--next-review", default="")
    parser.add_argument("--update-summary", default="")
    parser.add_argument("--readiness-notes", default="")
    parser.add_argument("--confirm-post-sale-improvement-go", action="store_true")
    parser.add_argument("--confirm-start-here-updated", action="store_true")
    parser.add_argument("--confirm-license-walkthrough-updated", action="store_true")
    parser.add_argument("--confirm-support-macros-updated", action="store_true")
    parser.add_argument("--confirm-public-copy-updated", action="store_true")
    parser.add_argument("--confirm-safe-claims-preserved", action="store_true")
    parser.add_argument("--confirm-next-buyer-check-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    improvement_file = Path(args.improvement_file) if args.improvement_file else None
    if args.use_latest_improvement_loop and improvement_file is None:
        improvement_file = latest_improvement_file()
        if improvement_file is None:
            print(json.dumps({"ok": False, "error": "post_sale_improvement_loop_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "post_sale_improvement_go": args.confirm_post_sale_improvement_go,
        "start_here_updated": args.confirm_start_here_updated,
        "license_walkthrough_updated": args.confirm_license_walkthrough_updated,
        "support_macros_updated": args.confirm_support_macros_updated,
        "public_copy_updated": args.confirm_public_copy_updated,
        "safe_claims_preserved": args.confirm_safe_claims_preserved,
        "next_buyer_check_recorded": args.confirm_next_buyer_check_recorded,
    }
    report = collect_post_sale_micro_updates(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        improvement_file=improvement_file,
        applied_updates=parse_int(args.applied_updates, -1),
        onboarding_updates=parse_int(args.onboarding_updates, -1),
        support_macro_updates=parse_int(args.support_macro_updates, -1),
        public_copy_updates=parse_int(args.public_copy_updates, -1),
        safe_claims_updates=parse_int(args.safe_claims_updates, -1),
        next_buyer_steps=parse_int(args.next_buyer_steps, -1),
        support_risk=parse_int(args.support_risk, -1),
        claims_risk=parse_int(args.claims_risk, -1),
        decision=args.decision.strip(),
        priority=args.priority.strip(),
        owner=args.owner,
        next_review=args.next_review,
        update_summary=args.update_summary,
        readiness_notes=args.readiness_notes,
        confirmations=confirmations,
        allow_no_go_improvement=args.allow_no_go_improvement,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
