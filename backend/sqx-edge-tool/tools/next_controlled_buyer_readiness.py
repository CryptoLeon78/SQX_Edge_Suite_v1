from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "next_controlled_buyer_readiness.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "next_controlled_buyer_readiness"
DEFAULT_MICRO_UPDATES_DIR = TOOL_ROOT / "data" / "post_sale_micro_updates"


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


def latest_micro_updates_file(directory: Path = DEFAULT_MICRO_UPDATES_DIR) -> Path | None:
    return latest_file(directory, "post_sale_micro_updates_*.json")


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
    micro_config_path = project_path(str(depends_on.get("postSaleMicroUpdatesConfig", "")))
    if not micro_config_path.is_file():
        return ["post_sale_micro_updates_config_missing"]
    micro_config = load_json(micro_config_path)
    if micro_config.get("state") != depends_on.get("postSaleMicroUpdatesState"):
        return ["post_sale_micro_updates_state_invalid"]
    return []


def validate_micro_updates(micro_updates: dict[str, Any] | None, allow_no_go_micro_updates: bool) -> list[str]:
    if micro_updates is None:
        return ["post_sale_micro_updates_evidence_missing"]
    decision = micro_updates.get("decision", {})
    if not decision.get("go") and not allow_no_go_micro_updates:
        return ["post_sale_micro_updates_not_go", *decision.get("blockers", [])]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def readiness_checklist() -> list[str]:
    return [
        "Confirm post-sale micro-updates evidence is GO.",
        "Confirm only one private buyer slot is open.",
        "Confirm private checkout link is ready but not broadly published.",
        "Confirm ZIP, license issue path and delivery instructions are ready.",
        "Confirm support capacity and follow-up window are realistic.",
        "Confirm safe claims and pause rule before sharing the link.",
    ]


def decision_from(
    config: dict[str, Any],
    micro_updates: dict[str, Any] | None,
    buyer_slots: int,
    private_link_status: str,
    checkout_ready: bool,
    license_delivery_ready: bool,
    delivery_package_ready: bool,
    support_capacity_hours: int,
    followup_window_hours: int,
    open_support_items: int,
    claims_risk: int,
    decision: str,
    owner: str,
    readiness_notes: str,
    confirmations: dict[str, bool],
    allow_no_go_micro_updates: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_micro_updates(micro_updates, allow_no_go_micro_updates))

    if any(value < 0 for value in (buyer_slots, support_capacity_hours, followup_window_hours, open_support_items, claims_risk)):
        blockers.append("next_buyer_readiness_metrics_invalid")
    if private_link_status not in set(config.get("allowedPrivateLinkStatuses", [])):
        blockers.append("private_link_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("next_buyer_readiness_decision_invalid")
    if not is_safe_text(owner):
        blockers.append("next_buyer_owner_missing_or_unsafe")
    if not readiness_notes.strip():
        blockers.append("next_buyer_readiness_notes_missing")
    if buyer_slots < int(config.get("minimumBuyerSlots", 1)):
        blockers.append("next_buyer_slot_missing")
    if buyer_slots > int(config.get("maximumBuyerSlots", 1)):
        blockers.append("next_buyer_slot_limit_exceeded")
    if followup_window_hours < int(config.get("minimumFollowupHours", 24)):
        blockers.append("followup_window_too_short")
    if open_support_items > int(config.get("maximumOpenSupportItems", 0)):
        blockers.append("open_support_items_block_next_buyer")
    if claims_risk > int(config.get("maximumClaimsRisk", 0)):
        blockers.append("claims_risk_requires_pause_sales")
    if not checkout_ready:
        blockers.append("checkout_not_ready")
    if not license_delivery_ready:
        blockers.append("license_delivery_not_ready")
    if not delivery_package_ready:
        blockers.append("delivery_package_not_ready")
    if support_capacity_hours <= 0:
        blockers.append("support_capacity_missing")

    micro_decision = micro_updates.get("readiness_decision", "") if micro_updates else ""
    if decision == "share_private_link":
        if micro_decision != "next_controlled_buyer_ready":
            blockers.append("share_private_link_requires_m69_next_buyer_ready")
        if private_link_status != "ready_private_link":
            blockers.append("share_private_link_requires_ready_private_link")
        if buyer_slots != 1:
            blockers.append("share_private_link_requires_single_buyer_slot")
        if support_capacity_hours < 24:
            warnings.append("support_capacity_under_24h")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
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
        "# Next Controlled Buyer Readiness Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Readiness decision: `{report.get('readiness_decision') or 'missing'}`",
        f"- Private link status: `{report.get('private_link_status') or 'missing'}`",
        f"- Buyer slots: `{report.get('buyer_slots')}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["readiness_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("support_capacity_hours", "followup_window_hours", "open_support_items", "claims_risk"):
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
    json_path = output_dir / f"next_controlled_buyer_readiness_{current_stamp}.json"
    md_path = output_dir / f"next_controlled_buyer_readiness_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_next_buyer_readiness(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    micro_updates_file: Path | None = None,
    buyer_slots: int = -1,
    private_link_status: str = "",
    checkout_ready: bool = False,
    license_delivery_ready: bool = False,
    delivery_package_ready: bool = False,
    support_capacity_hours: int = -1,
    followup_window_hours: int = -1,
    open_support_items: int = -1,
    claims_risk: int = -1,
    decision: str = "share_private_link",
    owner: str = "",
    readiness_notes: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_micro_updates: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    load_json(manifest_path)
    micro_updates = load_json(micro_updates_file) if micro_updates_file else None
    final_confirmations = confirmations or {}
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "next_controlled_buyer_readiness_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "micro_updates_source": str(micro_updates_file) if micro_updates_file else "",
        "micro_updates_decision": micro_updates.get("decision") if micro_updates else None,
        "micro_updates_readiness_decision": micro_updates.get("readiness_decision") if micro_updates else "",
        "buyer_slots": buyer_slots,
        "private_link_status": private_link_status.strip(),
        "checkout_ready": checkout_ready,
        "license_delivery_ready": license_delivery_ready,
        "delivery_package_ready": delivery_package_ready,
        "support_capacity_hours": support_capacity_hours,
        "followup_window_hours": followup_window_hours,
        "open_support_items": open_support_items,
        "claims_risk": claims_risk,
        "readiness_decision": decision,
        "owner": owner.strip(),
        "readiness_notes": readiness_notes.strip(),
        "readiness_checklist": readiness_checklist(),
        "confirmations": final_confirmations,
    }
    report["decision"] = decision_from(
        config,
        micro_updates,
        buyer_slots,
        private_link_status,
        checkout_ready,
        license_delivery_ready,
        delivery_package_ready,
        support_capacity_hours,
        followup_window_hours,
        open_support_items,
        claims_risk,
        decision,
        owner,
        readiness_notes,
        final_confirmations,
        allow_no_go_micro_updates,
    )
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Check readiness before sharing the next controlled buyer private link.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--micro-updates-file", default="")
    parser.add_argument("--use-latest-micro-updates", action="store_true")
    parser.add_argument("--allow-no-go-micro-updates", action="store_true")
    parser.add_argument("--buyer-slots", default="")
    parser.add_argument("--private-link-status", default="")
    parser.add_argument("--checkout-ready", action="store_true")
    parser.add_argument("--license-delivery-ready", action="store_true")
    parser.add_argument("--delivery-package-ready", action="store_true")
    parser.add_argument("--support-capacity-hours", default="")
    parser.add_argument("--followup-window-hours", default="")
    parser.add_argument("--open-support-items", default="")
    parser.add_argument("--claims-risk", default="")
    parser.add_argument("--decision", default="share_private_link")
    parser.add_argument("--owner", default="")
    parser.add_argument("--readiness-notes", default="")
    parser.add_argument("--confirm-post-sale-micro-updates-go", action="store_true")
    parser.add_argument("--confirm-private-link-reviewed", action="store_true")
    parser.add_argument("--confirm-checkout-readiness-reviewed", action="store_true")
    parser.add_argument("--confirm-license-delivery-ready", action="store_true")
    parser.add_argument("--confirm-support-capacity-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-pause-rule-reviewed", action="store_true")
    parser.add_argument("--confirm-followup-window-recorded", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    micro_updates_file = Path(args.micro_updates_file) if args.micro_updates_file else None
    if args.use_latest_micro_updates and micro_updates_file is None:
        micro_updates_file = latest_micro_updates_file()
        if micro_updates_file is None:
            print(json.dumps({"ok": False, "error": "post_sale_micro_updates_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    confirmations = {
        "post_sale_micro_updates_go": args.confirm_post_sale_micro_updates_go,
        "private_link_reviewed": args.confirm_private_link_reviewed,
        "checkout_readiness_reviewed": args.confirm_checkout_readiness_reviewed,
        "license_delivery_ready": args.confirm_license_delivery_ready,
        "support_capacity_ready": args.confirm_support_capacity_ready,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "pause_rule_reviewed": args.confirm_pause_rule_reviewed,
        "followup_window_recorded": args.confirm_followup_window_recorded,
    }
    report = collect_next_buyer_readiness(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        micro_updates_file=micro_updates_file,
        buyer_slots=parse_int(args.buyer_slots, -1),
        private_link_status=args.private_link_status,
        checkout_ready=args.checkout_ready,
        license_delivery_ready=args.license_delivery_ready,
        delivery_package_ready=args.delivery_package_ready,
        support_capacity_hours=parse_int(args.support_capacity_hours, -1),
        followup_window_hours=parse_int(args.followup_window_hours, -1),
        open_support_items=parse_int(args.open_support_items, -1),
        claims_risk=parse_int(args.claims_risk, -1),
        decision=args.decision.strip(),
        owner=args.owner,
        readiness_notes=args.readiness_notes,
        confirmations=confirmations,
        allow_no_go_micro_updates=args.allow_no_go_micro_updates,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
