from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "buyer_ready_checkout_closeout.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "buyer_ready_checkout_closeout"
DEFAULT_FEEDBACK_DIR = TOOL_ROOT / "data" / "template_pack_2_feedback_cohort"


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


def latest_feedback_file(directory: Path = DEFAULT_FEEDBACK_DIR) -> Path | None:
    return latest_file(directory, "template_pack_2_feedback_cohort_*.json")


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
        return ["template_pack_2_feedback_cohort_config_missing"]
    feedback_config = load_json(feedback_config_path)
    if feedback_config.get("state") != depends_on.get("feedbackCohortState"):
        return ["template_pack_2_feedback_cohort_state_invalid"]
    return []


def validate_feedback(feedback: dict[str, Any] | None, allow_no_go_feedback: bool) -> list[str]:
    if feedback is None:
        return ["template_pack_2_feedback_cohort_evidence_missing"]
    decision = feedback.get("decision", {})
    if not decision.get("go") and not allow_no_go_feedback:
        return ["template_pack_2_feedback_cohort_not_go", *decision.get("blockers", [])]
    return []


def is_safe_label(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def closeout_checklist() -> list[str]:
    return [
        "Confirm the M64 feedback cohort evidence is GO.",
        "Review checkout copy without financial-result claims.",
        "Confirm portable download, unzip and START_SQX_EDGE.bat flow.",
        "Confirm signed license delivery and import steps.",
        "Confirm support path and basic-user FAQ are visible.",
        "Confirm Template Pack 2 delivery/support macros are ready.",
        "Confirm rollback: pause checkout, pause webhook/worker and return to manual fulfillment.",
    ]


def decision_from(
    config: dict[str, Any],
    feedback: dict[str, Any] | None,
    buyer_steps: int,
    release_channel: str,
    support_label: str,
    closeout_notes: str,
    decision: str,
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
    blockers.extend(validate_feedback(feedback, allow_no_go_feedback))

    if buyer_steps < int(config.get("minimumBuyerSteps", 5)):
        blockers.append("buyer_steps_incomplete")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("closeout_decision_invalid")
    if not is_safe_label(release_channel):
        blockers.append("release_channel_missing_or_unsafe")
    if not is_safe_label(support_label):
        blockers.append("support_label_missing_or_unsafe")
    if not closeout_notes.strip():
        blockers.append("closeout_notes_missing")

    feedback_decision = feedback.get("roadmap_decision", "") if feedback else ""
    if decision == "open_controlled_sales" and feedback_decision not in {"expand_traffic", "iterate_offer"}:
        blockers.append("open_sales_needs_positive_feedback_decision")
    if decision == "open_controlled_sales" and "support_path_reviewed_not_confirmed" in blockers:
        blockers.append("open_sales_blocked_by_support_path")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if decision == "iterate_buyer_pack":
        warnings.append("operator_decision_iterate_buyer_pack")
    if decision == "keep_private_pilot":
        warnings.append("operator_decision_keep_private_pilot")

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
        "# Buyer-Ready Checkout Release Closeout Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Closeout decision: `{report.get('closeout_decision') or 'missing'}`",
        f"- Release channel: `{report.get('release_channel') or 'missing'}`",
        f"- Buyer steps: `{report.get('buyer_steps')}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["closeout_checklist"])
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
    json_path = output_dir / f"buyer_ready_checkout_closeout_{current_stamp}.json"
    md_path = output_dir / f"buyer_ready_checkout_closeout_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_closeout(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    feedback_file: Path | None = None,
    buyer_steps: int = -1,
    release_channel: str = "",
    support_label: str = "",
    closeout_notes: str = "",
    decision: str = "keep_private_pilot",
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
        "state": config.get("state", "buyer_ready_checkout_release_closeout_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "feedback_source": str(feedback_file) if feedback_file else "",
        "feedback_decision": feedback.get("decision") if feedback else None,
        "feedback_roadmap_decision": feedback.get("roadmap_decision") if feedback else "",
        "buyer_steps": buyer_steps,
        "release_channel": release_channel.strip(),
        "support_label": support_label.strip(),
        "closeout_notes": closeout_notes.strip(),
        "closeout_decision": decision,
        "closeout_checklist": closeout_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        feedback,
        buyer_steps,
        release_channel,
        support_label,
        closeout_notes,
        decision,
        final_confirmations,
        allow_no_go_feedback,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Close buyer-ready checkout, release, support and delivery readiness.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--feedback-file", default="")
    parser.add_argument("--use-latest-feedback-cohort", action="store_true")
    parser.add_argument("--allow-no-go-feedback", action="store_true")
    parser.add_argument("--buyer-steps", default="")
    parser.add_argument("--release-channel", default="")
    parser.add_argument("--support-label", default="")
    parser.add_argument("--decision", default="keep_private_pilot")
    parser.add_argument("--closeout-notes", default="")
    parser.add_argument("--confirm-feedback-cohort-go", action="store_true")
    parser.add_argument("--confirm-checkout-copy-reviewed", action="store_true")
    parser.add_argument("--confirm-portable-release-reviewed", action="store_true")
    parser.add_argument("--confirm-license-delivery-reviewed", action="store_true")
    parser.add_argument("--confirm-support-path-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-rollback-reviewed", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    feedback_file = Path(args.feedback_file) if args.feedback_file else None
    if args.use_latest_feedback_cohort and feedback_file is None:
        feedback_file = latest_feedback_file()
        if feedback_file is None:
            print(json.dumps({"ok": False, "error": "template_pack_2_feedback_cohort_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "feedback_cohort_go": args.confirm_feedback_cohort_go,
        "checkout_copy_reviewed": args.confirm_checkout_copy_reviewed,
        "portable_release_reviewed": args.confirm_portable_release_reviewed,
        "license_delivery_reviewed": args.confirm_license_delivery_reviewed,
        "support_path_reviewed": args.confirm_support_path_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "rollback_reviewed": args.confirm_rollback_reviewed,
    }
    report = collect_closeout(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        feedback_file=feedback_file,
        buyer_steps=parse_int(args.buyer_steps, -1),
        release_channel=args.release_channel,
        support_label=args.support_label,
        closeout_notes=args.closeout_notes,
        decision=args.decision.strip(),
        confirmations=confirmations,
        allow_no_go_feedback=args.allow_no_go_feedback,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
