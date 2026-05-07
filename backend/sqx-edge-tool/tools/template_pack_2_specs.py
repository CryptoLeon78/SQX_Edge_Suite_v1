from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_2_specs.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_2_specs"
DEFAULT_ACTION_PLAN_DIR = TOOL_ROOT / "data" / "template_pack_1_action_plan"


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


def latest_action_plan_file(directory: Path = DEFAULT_ACTION_PLAN_DIR) -> Path | None:
    return latest_file(directory, "template_pack_1_action_plan_*.json")


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
    action_config_path = project_path(str(depends_on.get("actionPlanConfig", "")))
    if not action_config_path.is_file():
        return ["template_pack_1_action_plan_config_missing"]
    action_config = load_json(action_config_path)
    if action_config.get("state") != depends_on.get("actionPlanState"):
        return ["template_pack_1_action_plan_state_invalid"]
    return []


def validate_action_plan(action_plan: dict[str, Any] | None, config: dict[str, Any], allow_no_go_action_plan: bool) -> list[str]:
    if action_plan is None:
        return ["template_pack_1_action_plan_evidence_missing"]
    decision = action_plan.get("decision", {})
    if not decision.get("go") and not allow_no_go_action_plan:
        return ["template_pack_1_action_plan_not_go", *decision.get("blockers", [])]
    required_plan = config.get("dependsOn", {}).get("requiredActionPlan", "template_pack_2")
    if action_plan.get("action_plan") != required_plan:
        return ["template_pack_1_action_plan_not_template_pack_2"]
    if action_plan.get("next_phase") != "M57_template_pack_2_specs":
        return ["template_pack_1_action_plan_next_phase_invalid"]
    return []


def specs_checklist() -> list[str]:
    return [
        "Confirm M56 action plan GO and Template Pack 2 next phase.",
        "Map buyer feedback themes to Pack 2 scope.",
        "Define asset families, preset count and intended buyer value.",
        "Define support boundaries and delivery model before asset work.",
        "Review safe claims and avoid financial performance promises.",
        "Choose draft_pack_2_assets, iterate_pack_1_first or pause_pack_2.",
    ]


def decision_from(
    config: dict[str, Any],
    action_plan: dict[str, Any] | None,
    spec_decision: str,
    asset_families: int,
    preset_count: int,
    feedback_themes_mapped: int,
    support_scope_hours: int,
    claims_risk: int,
    delivery_model: str,
    next_phase: str,
    scope_summary: str,
    support_boundaries: str,
    confirmations: dict[str, bool],
    allow_no_go_action_plan: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_action_plan(action_plan, config, allow_no_go_action_plan))

    if spec_decision not in set(config.get("allowedSpecDecisions", [])):
        blockers.append("spec_decision_invalid")
    if next_phase not in set(config.get("allowedNextPhases", [])):
        blockers.append("next_phase_invalid")
    if any(value < 0 for value in (asset_families, preset_count, feedback_themes_mapped, support_scope_hours, claims_risk)):
        blockers.append("template_pack_2_specs_metrics_invalid")
    if not delivery_model.strip():
        blockers.append("delivery_model_missing")
    if not scope_summary.strip():
        blockers.append("scope_summary_missing")
    if not support_boundaries.strip():
        blockers.append("support_boundaries_missing")

    min_asset_families = int(config.get("minimumAssetFamilies", 2))
    min_presets = int(config.get("minimumPresetCount", 6))
    min_feedback = int(config.get("minimumFeedbackThemesMapped", 2))
    max_claims = int(config.get("maxClaimsRisk", 0))

    if spec_decision == "draft_pack_2_assets":
        if asset_families < min_asset_families:
            blockers.append("draft_pack_2_assets_needs_asset_families")
        if preset_count < min_presets:
            blockers.append("draft_pack_2_assets_needs_presets")
        if feedback_themes_mapped < min_feedback:
            blockers.append("draft_pack_2_assets_needs_feedback_mapping")
        if claims_risk > max_claims:
            blockers.append("draft_pack_2_assets_claims_risk")
        if support_scope_hours <= 0:
            blockers.append("support_scope_hours_missing")
        if next_phase != "M58_template_pack_2_assets":
            blockers.append("draft_pack_2_assets_next_phase_mismatch")
    if spec_decision == "iterate_pack_1_first":
        warnings.append("operator_decision_iterate_pack_1_first")
        if next_phase != "M58_pack_1_iteration":
            blockers.append("iterate_pack_1_first_next_phase_mismatch")
    if spec_decision == "pause_pack_2":
        warnings.append("operator_decision_pause_pack_2")
        if next_phase != "M58_pause_pack_2":
            blockers.append("pause_pack_2_next_phase_mismatch")

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
        "# Template Pack 2 Specs Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Spec decision: `{report.get('spec_decision') or 'missing'}`",
        f"- Next phase: `{report.get('next_phase') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["specs_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("asset_families", "preset_count", "feedback_themes_mapped", "support_scope_hours", "claims_risk"):
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
    json_path = output_dir / f"template_pack_2_specs_{current_stamp}.json"
    md_path = output_dir / f"template_pack_2_specs_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_specs(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    action_plan_file: Path | None = None,
    spec_decision: str = "draft_pack_2_assets",
    asset_families: int = -1,
    preset_count: int = -1,
    feedback_themes_mapped: int = -1,
    support_scope_hours: int = -1,
    claims_risk: int = -1,
    delivery_model: str = "",
    next_phase: str = "",
    scope_summary: str = "",
    support_boundaries: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_action_plan: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    action_plan = load_json(action_plan_file) if action_plan_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_2_specs_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "action_plan_source": str(action_plan_file) if action_plan_file else "",
        "action_plan_decision": action_plan.get("decision") if action_plan else None,
        "action_plan": action_plan.get("action_plan") if action_plan else "",
        "spec_decision": spec_decision,
        "asset_families": asset_families,
        "preset_count": preset_count,
        "feedback_themes_mapped": feedback_themes_mapped,
        "support_scope_hours": support_scope_hours,
        "claims_risk": claims_risk,
        "delivery_model": delivery_model.strip(),
        "next_phase": next_phase,
        "scope_summary": scope_summary.strip(),
        "support_boundaries": support_boundaries.strip(),
        "specs_checklist": specs_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        action_plan,
        spec_decision,
        asset_families,
        preset_count,
        feedback_themes_mapped,
        support_scope_hours,
        claims_risk,
        delivery_model,
        next_phase,
        scope_summary,
        support_boundaries,
        final_confirmations,
        allow_no_go_action_plan,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate initial Template Pack 2 specs from the M56 action plan.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--action-plan-file", default="")
    parser.add_argument("--use-latest-action-plan", action="store_true")
    parser.add_argument("--allow-no-go-action-plan", action="store_true")
    parser.add_argument("--spec-decision", default="draft_pack_2_assets")
    parser.add_argument("--asset-families", default="")
    parser.add_argument("--preset-count", default="")
    parser.add_argument("--feedback-themes-mapped", default="")
    parser.add_argument("--support-scope-hours", default="")
    parser.add_argument("--claims-risk", default="")
    parser.add_argument("--delivery-model", default="")
    parser.add_argument("--next-phase", default="")
    parser.add_argument("--scope-summary", default="")
    parser.add_argument("--support-boundaries", default="")
    parser.add_argument("--confirm-action-plan-go", action="store_true")
    parser.add_argument("--confirm-buyer-feedback-mapped", action="store_true")
    parser.add_argument("--confirm-scope-defined", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-support-boundaries-defined", action="store_true")
    parser.add_argument("--confirm-delivery-model-defined", action="store_true")
    parser.add_argument("--confirm-next-phase-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    action_plan_file = Path(args.action_plan_file) if args.action_plan_file else None
    if args.use_latest_action_plan and action_plan_file is None:
        action_plan_file = latest_action_plan_file()
        if action_plan_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_1_action_plan_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "action_plan_go": args.confirm_action_plan_go,
        "buyer_feedback_mapped": args.confirm_buyer_feedback_mapped,
        "scope_defined": args.confirm_scope_defined,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "support_boundaries_defined": args.confirm_support_boundaries_defined,
        "delivery_model_defined": args.confirm_delivery_model_defined,
        "next_phase_recorded": args.confirm_next_phase_recorded,
    }
    report = collect_specs(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        action_plan_file=action_plan_file,
        spec_decision=args.spec_decision.strip(),
        asset_families=parse_int(args.asset_families, -1),
        preset_count=parse_int(args.preset_count, -1),
        feedback_themes_mapped=parse_int(args.feedback_themes_mapped, -1),
        support_scope_hours=parse_int(args.support_scope_hours, -1),
        claims_risk=parse_int(args.claims_risk, -1),
        delivery_model=args.delivery_model,
        next_phase=args.next_phase.strip(),
        scope_summary=args.scope_summary,
        support_boundaries=args.support_boundaries,
        confirmations=confirmations,
        allow_no_go_action_plan=args.allow_no_go_action_plan,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
