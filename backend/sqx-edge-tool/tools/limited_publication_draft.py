from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "limited_publication_draft.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "limited_publication_draft"
DEFAULT_GATE_DIR = TOOL_ROOT / "data" / "controlled_publication_gate"
EXPECTED_STATE = "limited_publication_draft_ready"


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


def latest_gate_file(directory: Path = DEFAULT_GATE_DIR) -> Path | None:
    return latest_file(directory, "controlled_publication_gate_*.json")


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
    gate_config_path = project_path(str(depends_on.get("controlledPublicationGateConfig", "")))
    if not gate_config_path.is_file():
        return ["controlled_publication_gate_config_missing"]
    gate_config = load_json(gate_config_path)
    if gate_config.get("state") != depends_on.get("controlledPublicationGateState"):
        return ["controlled_publication_gate_state_invalid"]
    return []


def validate_gate(gate: dict[str, Any] | None, allow_no_go_gate: bool) -> list[str]:
    if gate is None:
        return ["controlled_publication_gate_evidence_missing"]
    decision = gate.get("decision", {})
    if not decision.get("go") and not allow_no_go_gate:
        return ["controlled_publication_gate_not_go", *decision.get("blockers", [])]
    if gate.get("publication_decision") != "prepare_limited_publication" and not allow_no_go_gate:
        return ["m76_did_not_select_prepare_limited_publication"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r<>]", value))


def contains_blocked_claim(text: str, patterns: list[str]) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in patterns if pattern.lower() in lowered]


def draft_checklist() -> list[str]:
    return [
        "Load M76 controlled publication gate evidence before drafting.",
        "Keep copy limited, factual and free of financial outcome promises.",
        "Include support path, rollback note, pause rule and basic-user instructions.",
        "Keep channel and audience cap small enough for manual review.",
        "Record only redacted draft metadata and operator next action.",
    ]


def decision_from(
    config: dict[str, Any],
    gate: dict[str, Any] | None,
    draft_channel: str,
    audience_cap: int,
    copy_sections: int,
    open_risks: int,
    headline: str,
    body: str,
    cta: str,
    support_path_ready: bool,
    rollback_note_ready: bool,
    pause_rule_ready: bool,
    basic_user_instructions_ready: bool,
    decision: str,
    owner: str,
    draft_notes: str,
    next_action: str,
    confirmations: dict[str, bool],
    allow_no_go_gate: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_gate(gate, allow_no_go_gate))

    if draft_channel not in set(config.get("allowedDraftChannels", [])):
        blockers.append("limited_publication_draft_channel_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("limited_publication_draft_decision_invalid")
    if any(value < 0 for value in (audience_cap, copy_sections, open_risks)):
        blockers.append("limited_publication_draft_metrics_invalid")
    if audience_cap <= 0:
        blockers.append("limited_publication_draft_audience_cap_missing")
    if audience_cap > int(config.get("maximumAudienceCap", 10)):
        blockers.append("limited_publication_draft_audience_cap_too_large")
    if copy_sections < int(config.get("minimumCopySections", 4)):
        blockers.append("limited_publication_draft_copy_sections_missing")
    if open_risks > int(config.get("maximumOpenRisks", 0)):
        blockers.append("limited_publication_draft_open_risks_require_hold_or_pause")
    if not is_safe_text(headline):
        blockers.append("limited_publication_draft_headline_missing_or_unsafe")
    if not is_safe_text(body):
        blockers.append("limited_publication_draft_body_missing_or_unsafe")
    if not is_safe_text(cta):
        blockers.append("limited_publication_draft_cta_missing_or_unsafe")
    if not is_safe_text(owner):
        blockers.append("limited_publication_draft_owner_missing_or_unsafe")
    if not draft_notes.strip():
        blockers.append("limited_publication_draft_notes_missing")
    if not next_action.strip():
        blockers.append("limited_publication_draft_next_action_missing")

    blocked_claims = contains_blocked_claim(
        " ".join([headline, body, cta, draft_notes]),
        [str(item) for item in config.get("blockedClaimPatterns", [])],
    )
    blockers.extend(f"blocked_claim_pattern:{claim}" for claim in blocked_claims)

    if decision == "ready_for_operator_review":
        if not support_path_ready:
            blockers.append("ready_for_operator_review_requires_support_path")
        if not rollback_note_ready:
            blockers.append("ready_for_operator_review_requires_rollback_note")
        if not pause_rule_ready:
            blockers.append("ready_for_operator_review_requires_pause_rule")
        if not basic_user_instructions_ready:
            blockers.append("ready_for_operator_review_requires_basic_user_instructions")
    if decision == "hold_for_copy_fix":
        warnings.append("operator_decision_hold_for_copy_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if open_risks and decision == "ready_for_operator_review":
        blockers.append("open_risks_block_operator_review")
    if blocked_claims and decision == "ready_for_operator_review":
        blockers.append("blocked_claims_block_operator_review")

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
        "# Limited Publication Draft Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Draft decision: `{report.get('draft_decision') or 'missing'}`",
        f"- Draft channel: `{report.get('draft_channel') or 'missing'}`",
        f"- Audience cap: `{report.get('audience_cap')}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["draft_checklist"])
    lines.append("")
    lines.append("## Copy")
    lines.append(f"- Headline: `{report.get('headline') or 'missing'}`")
    lines.append(f"- CTA: `{report.get('cta') or 'missing'}`")
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
    json_path = output_dir / f"limited_publication_draft_{current_stamp}.json"
    md_path = output_dir / f"limited_publication_draft_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_limited_publication_draft(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    gate_file: Path | None = None,
    draft_channel: str = "",
    audience_cap: int = -1,
    copy_sections: int = -1,
    open_risks: int = -1,
    headline: str = "",
    body: str = "",
    cta: str = "",
    support_path_ready: bool = False,
    rollback_note_ready: bool = False,
    pause_rule_ready: bool = False,
    basic_user_instructions_ready: bool = False,
    decision: str = "",
    owner: str = "",
    draft_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_gate: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    gate = load_json(gate_file) if gate_file else None
    confirmations = confirmations or {}
    draft_decision = decision_from(
        config,
        gate,
        draft_channel,
        audience_cap,
        copy_sections,
        open_risks,
        headline,
        body,
        cta,
        support_path_ready,
        rollback_note_ready,
        pause_rule_ready,
        basic_user_instructions_ready,
        decision,
        owner,
        draft_notes,
        next_action,
        confirmations,
        allow_no_go_gate,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "draft_id": config.get("draftId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_gate_file": str(gate_file) if gate_file else "",
        "source_publication_decision": gate.get("publication_decision", "") if gate else "",
        "draft_channel": draft_channel,
        "audience_cap": audience_cap,
        "copy_sections": copy_sections,
        "open_risks": open_risks,
        "headline": headline,
        "body": body,
        "cta": cta,
        "support_path_ready": support_path_ready,
        "rollback_note_ready": rollback_note_ready,
        "pause_rule_ready": pause_rule_ready,
        "basic_user_instructions_ready": basic_user_instructions_ready,
        "draft_decision": decision,
        "owner": owner,
        "draft_notes": draft_notes,
        "next_action": next_action,
        "confirmations": confirmations,
        "draft_checklist": draft_checklist(),
        "decision": draft_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "draft_policy": config.get("draftPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a limited publication draft from M76 gate evidence.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--gate-file", type=Path)
    parser.add_argument("--use-latest-gate", action="store_true")
    parser.add_argument("--allow-no-go-gate", action="store_true")
    parser.add_argument("--draft-channel", default="")
    parser.add_argument("--audience-cap", default="")
    parser.add_argument("--copy-sections", default="")
    parser.add_argument("--open-risks", default="")
    parser.add_argument("--headline", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--cta", default="")
    parser.add_argument("--support-path-ready", action="store_true")
    parser.add_argument("--rollback-note-ready", action="store_true")
    parser.add_argument("--pause-rule-ready", action="store_true")
    parser.add_argument("--basic-user-instructions-ready", action="store_true")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--draft-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-m76-go", action="store_true")
    parser.add_argument("--confirm-limited-channel", action="store_true")
    parser.add_argument("--confirm-safe-copy", action="store_true")
    parser.add_argument("--confirm-support-path", action="store_true")
    parser.add_argument("--confirm-rollback-note", action="store_true")
    parser.add_argument("--confirm-pause-rule", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    gate_file = args.gate_file
    if args.use_latest_gate:
        gate_file = latest_gate_file()
    confirmations = {
        "m76_go": args.confirm_m76_go,
        "limited_channel": args.confirm_limited_channel,
        "safe_copy": args.confirm_safe_copy,
        "support_path": args.confirm_support_path,
        "rollback_note": args.confirm_rollback_note,
        "pause_rule": args.confirm_pause_rule,
    }
    report = collect_limited_publication_draft(
        config_path=args.config,
        manifest_path=args.manifest,
        gate_file=gate_file,
        draft_channel=args.draft_channel,
        audience_cap=parse_int(args.audience_cap, -1),
        copy_sections=parse_int(args.copy_sections, -1),
        open_risks=parse_int(args.open_risks, -1),
        headline=args.headline,
        body=args.body,
        cta=args.cta,
        support_path_ready=args.support_path_ready,
        rollback_note_ready=args.rollback_note_ready,
        pause_rule_ready=args.pause_rule_ready,
        basic_user_instructions_ready=args.basic_user_instructions_ready,
        decision=args.decision,
        owner=args.owner,
        draft_notes=args.draft_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_gate=args.allow_no_go_gate,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
