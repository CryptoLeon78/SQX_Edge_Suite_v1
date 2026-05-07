from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_1_action_plan.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_1_action_plan"
DEFAULT_FEEDBACK_DIR = TOOL_ROOT / "data" / "template_pack_1_feedback_cohort"


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


def latest_feedback_cohort_file(directory: Path = DEFAULT_FEEDBACK_DIR) -> Path | None:
    return latest_file(directory, "template_pack_1_feedback_cohort_*.json")


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
    feedback_config_path = project_path(str(depends_on.get("feedbackCohortConfig", "")))
    if not feedback_config_path.is_file():
        return ["template_pack_1_feedback_cohort_config_missing"]
    feedback_config = load_json(feedback_config_path)
    if feedback_config.get("state") != depends_on.get("feedbackCohortState"):
        return ["template_pack_1_feedback_cohort_state_invalid"]
    return []


def validate_feedback_cohort(feedback: dict[str, Any] | None, allow_no_go_feedback: bool) -> list[str]:
    if feedback is None:
        return ["template_pack_1_feedback_cohort_evidence_missing"]
    decision = feedback.get("decision", {})
    if not decision.get("go") and not allow_no_go_feedback:
        return ["template_pack_1_feedback_cohort_not_go", *decision.get("blockers", [])]
    return []


def action_plan_checklist() -> list[str]:
    return [
        "Confirm M55 feedback cohort evidence and roadmap decision.",
        "Convert feedback themes into concrete operator actions.",
        "Assign owner, priority and next phase.",
        "Review support, safe claims and distribution impact.",
        "Keep notes aggregated and buyer-safe.",
        "Choose offer_iteration, traffic_expansion, template_pack_2 or pause_sales.",
    ]


def expected_plan_from_feedback(feedback: dict[str, Any] | None) -> str:
    if not feedback:
        return ""
    roadmap_decision = feedback.get("roadmap_decision", "")
    return {
        "iterate_offer": "offer_iteration",
        "expand_traffic": "traffic_expansion",
        "build_template_pack_2": "template_pack_2",
        "pause_sales": "pause_sales",
    }.get(str(roadmap_decision), "")


def decision_from(
    config: dict[str, Any],
    feedback: dict[str, Any] | None,
    action_plan: str,
    action_owner: str,
    priority: str,
    action_count: int,
    support_impact: int,
    distribution_impact: int,
    claims_risk: int,
    next_phase: str,
    action_summary: str,
    plan_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_feedback: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_feedback_cohort(feedback, allow_no_go_feedback))

    if action_plan not in set(config.get("allowedPlans", [])):
        blockers.append("action_plan_invalid")
    if priority not in set(config.get("allowedPriorities", [])):
        blockers.append("priority_invalid")
    if next_phase not in set(config.get("allowedNextPhases", [])):
        blockers.append("next_phase_invalid")
    if not action_owner.strip():
        blockers.append("action_owner_missing")
    if not action_summary.strip():
        blockers.append("action_summary_missing")
    if not plan_notes.strip():
        blockers.append("plan_notes_missing")
    if any(value < 0 for value in (action_count, support_impact, distribution_impact, claims_risk)):
        blockers.append("action_plan_metrics_invalid")

    minimum_actions = int(config.get("minimumActions", 3))
    if action_count < minimum_actions:
        blockers.append("action_plan_needs_minimum_actions")

    expected_plan = expected_plan_from_feedback(feedback)
    if expected_plan and action_plan != expected_plan:
        warnings.append(f"feedback_recommended_{expected_plan}")

    if action_plan == "traffic_expansion":
        max_support = int(config.get("maxSupportImpactForTrafficExpansion", 1))
        if support_impact > max_support:
            blockers.append("traffic_expansion_support_impact_too_high")
        if claims_risk > 0:
            blockers.append("traffic_expansion_claims_risk")
        if next_phase != "M57_traffic_expansion":
            blockers.append("traffic_expansion_next_phase_mismatch")
    if action_plan == "template_pack_2":
        if feedback and int(feedback.get("positive_signals", 0)) < 2:
            blockers.append("template_pack_2_needs_positive_feedback")
        if support_impact > 1 or claims_risk > 0:
            blockers.append("template_pack_2_blocked_by_support_or_claims")
        if next_phase != "M57_template_pack_2_specs":
            blockers.append("template_pack_2_next_phase_mismatch")
    if action_plan == "offer_iteration" and next_phase != "M57_offer_iteration":
        blockers.append("offer_iteration_next_phase_mismatch")
    if action_plan == "pause_sales" and next_phase != "M57_pause_and_fix":
        blockers.append("pause_sales_next_phase_mismatch")

    if distribution_impact > 0 and not confirmations.get("distribution_impact_reviewed"):
        blockers.append("distribution_impact_not_reviewed")

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
        "# Template Pack 1 Action Plan Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Action plan: `{report.get('action_plan') or 'missing'}`",
        f"- Owner: `{report.get('action_owner') or 'missing'}`",
        f"- Next phase: `{report.get('next_phase') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["action_plan_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("action_count", "support_impact", "distribution_impact", "claims_risk"):
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
    json_path = output_dir / f"template_pack_1_action_plan_{current_stamp}.json"
    md_path = output_dir / f"template_pack_1_action_plan_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_action_plan(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    feedback_file: Path | None = None,
    action_plan: str = "offer_iteration",
    action_owner: str = "",
    priority: str = "medium",
    action_count: int = -1,
    support_impact: int = -1,
    distribution_impact: int = -1,
    claims_risk: int = -1,
    next_phase: str = "",
    action_summary: str = "",
    plan_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_feedback: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    feedback = load_json(feedback_file) if feedback_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_1_action_plan_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "feedback_source": str(feedback_file) if feedback_file else "",
        "feedback_decision": feedback.get("decision") if feedback else None,
        "feedback_roadmap_decision": feedback.get("roadmap_decision") if feedback else "",
        "action_plan": action_plan,
        "action_owner": action_owner.strip(),
        "priority": priority,
        "action_count": action_count,
        "support_impact": support_impact,
        "distribution_impact": distribution_impact,
        "claims_risk": claims_risk,
        "next_phase": next_phase,
        "action_summary": action_summary.strip(),
        "plan_notes": plan_notes.strip(),
        "action_plan_checklist": action_plan_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        feedback,
        action_plan,
        action_owner,
        priority,
        action_count,
        support_impact,
        distribution_impact,
        claims_risk,
        next_phase,
        action_summary,
        plan_notes,
        final_confirmations,
        allow_no_go_feedback,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Template Pack 1 feedback cohort into an actionable next-phase plan.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--feedback-file", default="")
    parser.add_argument("--use-latest-feedback-cohort", action="store_true")
    parser.add_argument("--allow-no-go-feedback", action="store_true")
    parser.add_argument("--action-plan", default="offer_iteration")
    parser.add_argument("--action-owner", default="")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--action-count", default="")
    parser.add_argument("--support-impact", default="")
    parser.add_argument("--distribution-impact", default="")
    parser.add_argument("--claims-risk", default="")
    parser.add_argument("--next-phase", default="")
    parser.add_argument("--action-summary", default="")
    parser.add_argument("--plan-notes", default="")
    parser.add_argument("--confirm-feedback-cohort-go", action="store_true")
    parser.add_argument("--confirm-action-owner-assigned", action="store_true")
    parser.add_argument("--confirm-support-impact-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-distribution-impact-reviewed", action="store_true")
    parser.add_argument("--confirm-next-phase-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    feedback_file = Path(args.feedback_file) if args.feedback_file else None
    if args.use_latest_feedback_cohort and feedback_file is None:
        feedback_file = latest_feedback_cohort_file()
        if feedback_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_1_feedback_cohort_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "feedback_cohort_go": args.confirm_feedback_cohort_go,
        "action_owner_assigned": args.confirm_action_owner_assigned,
        "support_impact_reviewed": args.confirm_support_impact_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "distribution_impact_reviewed": args.confirm_distribution_impact_reviewed,
        "next_phase_recorded": args.confirm_next_phase_recorded,
    }
    report = collect_action_plan(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        feedback_file=feedback_file,
        action_plan=args.action_plan.strip(),
        action_owner=args.action_owner.strip(),
        priority=args.priority.strip(),
        action_count=parse_int(args.action_count, -1),
        support_impact=parse_int(args.support_impact, -1),
        distribution_impact=parse_int(args.distribution_impact, -1),
        claims_risk=parse_int(args.claims_risk, -1),
        next_phase=args.next_phase.strip(),
        action_summary=args.action_summary,
        plan_notes=args.plan_notes,
        confirmations=confirmations,
        allow_no_go_feedback=args.allow_no_go_feedback,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
