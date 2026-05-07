from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_1_feedback_cohort.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_1_feedback_cohort"
DEFAULT_SALES_REGISTER_DIR = TOOL_ROOT / "data" / "template_pack_1_sales_register"


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


def latest_sales_register_file(directory: Path = DEFAULT_SALES_REGISTER_DIR) -> Path | None:
    return latest_file(directory, "template_pack_1_sales_register_*.json")


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
    sales_config_path = project_path(str(depends_on.get("salesRegisterConfig", "")))
    if not sales_config_path.is_file():
        return ["template_pack_1_sales_register_config_missing"]
    sales_config = load_json(sales_config_path)
    if sales_config.get("state") != depends_on.get("salesRegisterState"):
        return ["template_pack_1_sales_register_state_invalid"]
    return []


def validate_sales_register(sales_register: dict[str, Any] | None, allow_no_go_sales_register: bool) -> list[str]:
    if sales_register is None:
        return ["template_pack_1_sales_register_evidence_missing"]
    decision = sales_register.get("decision", {})
    if not decision.get("go") and not allow_no_go_sales_register:
        return ["template_pack_1_sales_register_not_go", *decision.get("blockers", [])]
    return []


def feedback_checklist() -> list[str]:
    return [
        "Confirm sales register evidence and buyer cohort size.",
        "Summarize feedback themes without raw messages or personal data.",
        "Record bugs, activation friction, documentation gaps and feature requests.",
        "Record support, refunds and fulfillment risk before deciding roadmap.",
        "Review safe claims before changing public copy or traffic.",
        "Decide expand_traffic, iterate_offer, build_template_pack_2 or pause_sales.",
    ]


def decision_from(
    config: dict[str, Any],
    sales_register: dict[str, Any] | None,
    buyer_count: int,
    feedback_count: int,
    blocking_bugs: int,
    activation_friction: int,
    docs_gaps: int,
    feature_requests: int,
    positive_signals: int,
    open_support_items: int,
    refund_count: int,
    roadmap_decision: str,
    feedback_themes: str,
    review_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_sales_register: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_sales_register(sales_register, allow_no_go_sales_register))

    metrics = [
        buyer_count,
        feedback_count,
        blocking_bugs,
        activation_friction,
        docs_gaps,
        feature_requests,
        positive_signals,
        open_support_items,
        refund_count,
    ]
    if any(value < 0 for value in metrics):
        blockers.append("feedback_cohort_metrics_invalid")
    if roadmap_decision not in set(config.get("allowedDecisions", [])):
        blockers.append("roadmap_decision_invalid")
    if not feedback_themes.strip():
        blockers.append("feedback_themes_missing")
    if not review_notes.strip():
        blockers.append("review_notes_missing")

    min_buyers = int(config.get("minimumBuyersForExpand", 3))
    min_feedback = int(config.get("minimumFeedbackItems", 2))
    min_positive_tp2 = int(config.get("minimumPositiveSignalsForTemplatePack2", 2))
    max_bugs = int(config.get("maxBlockingBugsForExpand", 0))
    max_friction = int(config.get("maxActivationFrictionForExpand", 0))
    max_support = int(config.get("maxOpenSupportItemsForExpand", 0))
    max_refunds = int(config.get("maxRefundsForExpand", 0))

    if blocking_bugs > 0 and roadmap_decision != "pause_sales":
        blockers.append("blocking_bugs_require_pause_sales")
    if refund_count > 0 and roadmap_decision != "pause_sales":
        blockers.append("refunds_require_pause_sales")
    if open_support_items > 0 and roadmap_decision in {"expand_traffic", "build_template_pack_2"}:
        blockers.append("open_support_blocks_expansion")
    if roadmap_decision == "expand_traffic":
        if buyer_count < min_buyers:
            blockers.append("expand_traffic_needs_minimum_buyers")
        if feedback_count < min_feedback:
            blockers.append("expand_traffic_needs_feedback")
        if blocking_bugs > max_bugs or activation_friction > max_friction:
            blockers.append("expand_traffic_blocked_by_operational_friction")
        if open_support_items > max_support or refund_count > max_refunds:
            blockers.append("expand_traffic_blocked_by_support_or_refunds")
    if roadmap_decision == "build_template_pack_2":
        if positive_signals < min_positive_tp2:
            blockers.append("template_pack_2_needs_positive_signals")
        if blocking_bugs > 0 or activation_friction > 0 or refund_count > 0:
            blockers.append("template_pack_2_blocked_by_risk")
    if roadmap_decision == "iterate_offer":
        warnings.append("operator_decision_iterate_offer")
    if roadmap_decision == "pause_sales":
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
        "# Template Pack 1 Feedback Cohort Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Roadmap decision: `{report.get('roadmap_decision') or 'missing'}`",
        f"- Buyers reviewed: `{report.get('buyer_count')}`",
        f"- Feedback items: `{report.get('feedback_count')}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["feedback_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in (
        "blocking_bugs",
        "activation_friction",
        "docs_gaps",
        "feature_requests",
        "positive_signals",
        "open_support_items",
        "refund_count",
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
    json_path = output_dir / f"template_pack_1_feedback_cohort_{current_stamp}.json"
    md_path = output_dir / f"template_pack_1_feedback_cohort_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_feedback_cohort(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    sales_register_file: Path | None = None,
    buyer_count: int = -1,
    feedback_count: int = -1,
    blocking_bugs: int = -1,
    activation_friction: int = -1,
    docs_gaps: int = -1,
    feature_requests: int = -1,
    positive_signals: int = -1,
    open_support_items: int = -1,
    refund_count: int = -1,
    roadmap_decision: str = "iterate_offer",
    feedback_themes: str = "",
    review_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_sales_register: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    sales_register = load_json(sales_register_file) if sales_register_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_1_feedback_cohort_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "sales_register_source": str(sales_register_file) if sales_register_file else "",
        "sales_register_decision": sales_register.get("decision") if sales_register else None,
        "buyer_count": buyer_count,
        "feedback_count": feedback_count,
        "blocking_bugs": blocking_bugs,
        "activation_friction": activation_friction,
        "docs_gaps": docs_gaps,
        "feature_requests": feature_requests,
        "positive_signals": positive_signals,
        "open_support_items": open_support_items,
        "refund_count": refund_count,
        "roadmap_decision": roadmap_decision,
        "feedback_themes": feedback_themes.strip(),
        "review_notes": review_notes.strip(),
        "feedback_checklist": feedback_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        sales_register,
        buyer_count,
        feedback_count,
        blocking_bugs,
        activation_friction,
        docs_gaps,
        feature_requests,
        positive_signals,
        open_support_items,
        refund_count,
        roadmap_decision,
        feedback_themes,
        review_notes,
        final_confirmations,
        allow_no_go_sales_register,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Review Template Pack 1 add-on buyer feedback cohort before scaling.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--sales-register-file", default="")
    parser.add_argument("--use-latest-sales-register", action="store_true")
    parser.add_argument("--allow-no-go-sales-register", action="store_true")
    parser.add_argument("--buyer-count", default="")
    parser.add_argument("--feedback-count", default="")
    parser.add_argument("--blocking-bugs", default="")
    parser.add_argument("--activation-friction", default="")
    parser.add_argument("--docs-gaps", default="")
    parser.add_argument("--feature-requests", default="")
    parser.add_argument("--positive-signals", default="")
    parser.add_argument("--open-support-items", default="")
    parser.add_argument("--refund-count", default="")
    parser.add_argument("--roadmap-decision", default="iterate_offer")
    parser.add_argument("--feedback-themes", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--confirm-sales-register-go", action="store_true")
    parser.add_argument("--confirm-feedback-reviewed", action="store_true")
    parser.add_argument("--confirm-support-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-roadmap-decision-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    sales_register_file = Path(args.sales_register_file) if args.sales_register_file else None
    if args.use_latest_sales_register and sales_register_file is None:
        sales_register_file = latest_sales_register_file()
        if sales_register_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_1_sales_register_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "sales_register_go": args.confirm_sales_register_go,
        "feedback_reviewed": args.confirm_feedback_reviewed,
        "support_reviewed": args.confirm_support_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "roadmap_decision_recorded": args.confirm_roadmap_decision_recorded,
    }
    report = collect_feedback_cohort(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        sales_register_file=sales_register_file,
        buyer_count=parse_int(args.buyer_count, -1),
        feedback_count=parse_int(args.feedback_count, -1),
        blocking_bugs=parse_int(args.blocking_bugs, -1),
        activation_friction=parse_int(args.activation_friction, -1),
        docs_gaps=parse_int(args.docs_gaps, -1),
        feature_requests=parse_int(args.feature_requests, -1),
        positive_signals=parse_int(args.positive_signals, -1),
        open_support_items=parse_int(args.open_support_items, -1),
        refund_count=parse_int(args.refund_count, -1),
        roadmap_decision=args.roadmap_decision.strip(),
        feedback_themes=args.feedback_themes,
        review_notes=args.review_notes,
        confirmations=confirmations,
        allow_no_go_sales_register=args.allow_no_go_sales_register,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
