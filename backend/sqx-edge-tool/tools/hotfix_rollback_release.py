from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "hotfix_rollback_release"
DEFAULT_POST_RELEASE_MONITOR_DIR = TOOL_ROOT / "data" / "post_release_monitor"
ACTIONS = {"close_no_action", "pause_and_watch", "hotfix", "rollback"}


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_post_release_monitor_file(directory: Path = DEFAULT_POST_RELEASE_MONITOR_DIR) -> Path | None:
    return latest_file(directory, "post_release_monitor_*.json")


def evidence_list() -> list[str]:
    return [
        "post_release_monitor_reviewed",
        "action_owner_assigned",
        "incident_reference_recorded",
        "hotfix_notes_ready",
        "rollback_target_recorded",
        "customer_comms_ready",
        "support_macro_ready",
        "verification_plan_ready",
        "release_package_ready",
        "closure_evidence_ready",
    ]


def decision_from(
    post_release_monitor: dict[str, Any] | None,
    action: str,
    action_owner: str,
    incident_id: str,
    hotfix_version: str,
    rollback_target: str,
    post_action_decision: str,
    hotfix_notes_ready: bool,
    rollback_checklist_ready: bool,
    customer_comms_ready: bool,
    support_macro_ready: bool,
    verification_plan_ready: bool,
    release_package_ready: bool,
    closure_evidence_ready: bool,
    allow_no_go_monitor: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if post_release_monitor is None:
        blockers.append("post_release_monitor_missing")
    elif not post_release_monitor.get("decision", {}).get("go") and not allow_no_go_monitor:
        blockers.append("post_release_monitor_not_go")
        blockers.extend(post_release_monitor.get("decision", {}).get("blockers", []))
    if action not in ACTIONS:
        blockers.append("hotfix_rollback_action_missing_or_invalid")
    if not action_owner:
        blockers.append("action_owner_missing")
    if action in {"hotfix", "rollback", "pause_and_watch"} and not incident_id:
        blockers.append("incident_reference_missing")
    if action == "hotfix":
        if not hotfix_version:
            blockers.append("hotfix_version_missing")
        if not hotfix_notes_ready:
            blockers.append("hotfix_notes_missing")
        if not release_package_ready:
            blockers.append("hotfix_release_package_not_ready")
    if action == "rollback":
        if not rollback_target:
            blockers.append("rollback_target_missing")
        if not rollback_checklist_ready:
            blockers.append("rollback_checklist_not_ready")
    if action in {"hotfix", "rollback"} and not verification_plan_ready:
        blockers.append("verification_plan_not_ready")
    if action in {"hotfix", "rollback", "pause_and_watch"} and not customer_comms_ready:
        blockers.append("customer_comms_not_ready")
    if action in {"hotfix", "rollback", "pause_and_watch"} and not support_macro_ready:
        blockers.append("support_macro_not_ready")
    if not closure_evidence_ready:
        blockers.append("closure_evidence_not_ready")
    if action == "close_no_action" and incident_id:
        warnings.append("incident_reference_present_for_no_action")
    if post_action_decision and post_action_decision not in {"monitor", "reopen", "close", "escalate"}:
        blockers.append("post_action_decision_invalid")

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
        "# SQX Edge Hotfix Rollback Release",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Action: `{report.get('action') or 'missing'}`",
        f"- Owner: `{report.get('action_owner') or 'missing'}`",
        f"- Incident: `{report.get('incident_id') or 'none'}`",
        f"- Hotfix version: `{report.get('hotfix_version') or 'none'}`",
        f"- Rollback target: `{report.get('rollback_target') or 'none'}`",
        "",
        "## Evidence",
    ]
    lines.extend(f"- {item}" for item in report["evidence"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_release(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"hotfix_rollback_release_{current_stamp}.json"
    md_path = output_dir / f"hotfix_rollback_release_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_release(
    manifest_path: Path = DEFAULT_MANIFEST,
    post_release_monitor_file: Path | None = None,
    action: str = "",
    action_owner: str = "",
    incident_id: str = "",
    hotfix_version: str = "",
    rollback_target: str = "",
    post_action_decision: str = "",
    hotfix_notes_ready: bool = False,
    rollback_checklist_ready: bool = False,
    customer_comms_ready: bool = False,
    support_macro_ready: bool = False,
    verification_plan_ready: bool = False,
    release_package_ready: bool = False,
    closure_evidence_ready: bool = False,
    allow_no_go_monitor: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    post_release_monitor = load_json(post_release_monitor_file) if post_release_monitor_file else None
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "post_release_monitor_source": str(post_release_monitor_file) if post_release_monitor_file else "",
        "post_release_monitor_decision": post_release_monitor.get("decision") if post_release_monitor else None,
        "action": action,
        "action_owner": action_owner,
        "incident_id": incident_id,
        "hotfix_version": hotfix_version,
        "rollback_target": rollback_target,
        "post_action_decision": post_action_decision,
        "hotfix_notes_ready": hotfix_notes_ready,
        "rollback_checklist_ready": rollback_checklist_ready,
        "customer_comms_ready": customer_comms_ready,
        "support_macro_ready": support_macro_ready,
        "verification_plan_ready": verification_plan_ready,
        "release_package_ready": release_package_ready,
        "closure_evidence_ready": closure_evidence_ready,
        "evidence": evidence_list(),
        "decision": decision_from(
            post_release_monitor,
            action,
            action_owner,
            incident_id,
            hotfix_version,
            rollback_target,
            post_action_decision,
            hotfix_notes_ready,
            rollback_checklist_ready,
            customer_comms_ready,
            support_macro_ready,
            verification_plan_ready,
            release_package_ready,
            closure_evidence_ready,
            allow_no_go_monitor,
        ),
    }
    if write:
        report["evidence_paths"] = write_release(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge hotfix/rollback release kit")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--post-release-monitor-file", default="")
    parser.add_argument("--use-latest-post-release-monitor", action="store_true")
    parser.add_argument("--action", default=env_value("SQX_HOTFIX_ROLLBACK_ACTION"))
    parser.add_argument("--action-owner", default=env_value("SQX_HOTFIX_ROLLBACK_OWNER"))
    parser.add_argument("--incident-id", default=env_value("SQX_HOTFIX_ROLLBACK_INCIDENT"))
    parser.add_argument("--hotfix-version", default=env_value("SQX_HOTFIX_VERSION"))
    parser.add_argument("--rollback-target", default=env_value("SQX_ROLLBACK_TARGET"))
    parser.add_argument("--post-action-decision", default=env_value("SQX_POST_ACTION_DECISION"))
    parser.add_argument("--confirm-hotfix-notes-ready", action="store_true")
    parser.add_argument("--confirm-rollback-checklist-ready", action="store_true")
    parser.add_argument("--confirm-customer-comms-ready", action="store_true")
    parser.add_argument("--confirm-support-macro-ready", action="store_true")
    parser.add_argument("--confirm-verification-plan-ready", action="store_true")
    parser.add_argument("--confirm-release-package-ready", action="store_true")
    parser.add_argument("--confirm-closure-evidence-ready", action="store_true")
    parser.add_argument("--allow-no-go-monitor", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    monitor_file = Path(args.post_release_monitor_file) if args.post_release_monitor_file else None
    if args.use_latest_post_release_monitor and monitor_file is None:
        monitor_file = latest_post_release_monitor_file()
        if monitor_file is None:
            print(json.dumps({"ok": False, "error": "post_release_monitor_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_release(
        manifest_path=Path(args.manifest),
        post_release_monitor_file=monitor_file,
        action=args.action,
        action_owner=args.action_owner,
        incident_id=args.incident_id,
        hotfix_version=args.hotfix_version,
        rollback_target=args.rollback_target,
        post_action_decision=args.post_action_decision,
        hotfix_notes_ready=args.confirm_hotfix_notes_ready,
        rollback_checklist_ready=args.confirm_rollback_checklist_ready,
        customer_comms_ready=args.confirm_customer_comms_ready,
        support_macro_ready=args.confirm_support_macro_ready,
        verification_plan_ready=args.confirm_verification_plan_ready,
        release_package_ready=args.confirm_release_package_ready,
        closure_evidence_ready=args.confirm_closure_evidence_ready,
        allow_no_go_monitor=args.allow_no_go_monitor,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
