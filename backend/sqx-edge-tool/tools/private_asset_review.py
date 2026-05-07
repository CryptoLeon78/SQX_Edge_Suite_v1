from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "private_asset_review.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "private_asset_review"
DEFAULT_ASSET_DIR = TOOL_ROOT / "data" / "next_buyer_facing_asset"
EXPECTED_STATE = "private_asset_review_ready"


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


def latest_asset_file(directory: Path = DEFAULT_ASSET_DIR) -> Path | None:
    return latest_file(directory, "next_buyer_facing_asset_*.json")


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
    asset_config_path = project_path(str(depends_on.get("nextBuyerFacingAssetConfig", "")))
    if not asset_config_path.is_file():
        return ["next_buyer_facing_asset_config_missing"]
    asset_config = load_json(asset_config_path)
    if asset_config.get("state") != depends_on.get("nextBuyerFacingAssetState"):
        return ["next_buyer_facing_asset_state_invalid"]
    return []


def validate_asset(asset: dict[str, Any] | None, allow_no_go_asset: bool) -> list[str]:
    if asset is None:
        return ["next_buyer_facing_asset_evidence_missing"]
    decision = asset.get("decision", {})
    if not decision.get("go") and not allow_no_go_asset:
        return ["next_buyer_facing_asset_not_go", *decision.get("blockers", [])]
    if asset.get("asset_decision") != "prepare_private_review" and not allow_no_go_asset:
        return ["m74_did_not_select_prepare_private_review"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def private_review_checklist() -> list[str]:
    return [
        "Load M74 asset evidence before approving any publication step.",
        "Confirm private review status and reviewer count.",
        "Confirm safe claims, support readiness, release notes and rollback.",
        "Block publication when claims issues or support gaps exist.",
        "Record only redacted status, counts, owner and next action.",
    ]


def decision_from(
    config: dict[str, Any],
    asset: dict[str, Any] | None,
    review_status: str,
    reviewers: int,
    claims_issues: int,
    support_gaps: int,
    safe_claims_approved: bool,
    support_approved: bool,
    release_notes_approved: bool,
    rollback_ready: bool,
    decision: str,
    owner: str,
    review_notes: str,
    next_action: str,
    confirmations: dict[str, bool],
    allow_no_go_asset: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_asset(asset, allow_no_go_asset))

    if review_status not in set(config.get("allowedReviewStatuses", [])):
        blockers.append("private_asset_review_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("private_asset_review_decision_invalid")
    if any(value < 0 for value in (reviewers, claims_issues, support_gaps)):
        blockers.append("private_asset_review_metrics_invalid")
    if reviewers < int(config.get("minimumReviewers", 1)):
        blockers.append("private_asset_review_reviewer_missing")
    if claims_issues > int(config.get("maximumClaimsIssues", 0)):
        blockers.append("private_asset_review_claims_require_hold_or_pause")
    if support_gaps > int(config.get("maximumSupportGaps", 0)):
        blockers.append("private_asset_review_support_gaps_require_hold_or_pause")
    if not is_safe_text(owner):
        blockers.append("private_asset_review_owner_missing_or_unsafe")
    if not review_notes.strip():
        blockers.append("private_asset_review_notes_missing")
    if not next_action.strip():
        blockers.append("private_asset_review_next_action_missing")

    if decision == "prepare_controlled_publication":
        if review_status != "approved_private":
            blockers.append("prepare_controlled_publication_requires_private_approval")
        if not safe_claims_approved:
            blockers.append("prepare_controlled_publication_requires_safe_claims")
        if not support_approved:
            blockers.append("prepare_controlled_publication_requires_support")
        if not release_notes_approved:
            blockers.append("prepare_controlled_publication_requires_release_notes")
        if not rollback_ready:
            blockers.append("prepare_controlled_publication_requires_rollback")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if review_status == "changes_requested" and decision == "prepare_controlled_publication":
        blockers.append("changes_requested_requires_hold_or_pause")
    if review_status == "blocked" and decision not in {"hold_for_fix", "pause_sales"}:
        blockers.append("blocked_asset_review_requires_hold_or_pause")
    if (claims_issues or support_gaps) and decision == "prepare_controlled_publication":
        blockers.append("risk_counts_block_controlled_publication")

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
        "# Private Asset Review Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Review status: `{report.get('review_status') or 'missing'}`",
        f"- Review decision: `{report.get('review_decision') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["private_review_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("reviewers", "claims_issues", "support_gaps"):
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
    json_path = output_dir / f"private_asset_review_{current_stamp}.json"
    md_path = output_dir / f"private_asset_review_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_private_asset_review(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    asset_file: Path | None = None,
    review_status: str = "",
    reviewers: int = -1,
    claims_issues: int = -1,
    support_gaps: int = -1,
    safe_claims_approved: bool = False,
    support_approved: bool = False,
    release_notes_approved: bool = False,
    rollback_ready: bool = False,
    decision: str = "",
    owner: str = "",
    review_notes: str = "",
    next_action: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_asset: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    asset = load_json(asset_file) if asset_file else None
    confirmations = confirmations or {}
    review_decision = decision_from(
        config,
        asset,
        review_status,
        reviewers,
        claims_issues,
        support_gaps,
        safe_claims_approved,
        support_approved,
        release_notes_approved,
        rollback_ready,
        decision,
        owner,
        review_notes,
        next_action,
        confirmations,
        allow_no_go_asset,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "review_id": config.get("reviewId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_asset_file": str(asset_file) if asset_file else "",
        "source_asset_decision": asset.get("asset_decision", "") if asset else "",
        "review_status": review_status,
        "reviewers": reviewers,
        "claims_issues": claims_issues,
        "support_gaps": support_gaps,
        "safe_claims_approved": safe_claims_approved,
        "support_approved": support_approved,
        "release_notes_approved": release_notes_approved,
        "rollback_ready": rollback_ready,
        "review_decision": decision,
        "owner": owner,
        "review_notes": review_notes,
        "next_action": next_action,
        "confirmations": confirmations,
        "private_review_checklist": private_review_checklist(),
        "decision": review_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "review_policy": config.get("reviewPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Privately review the buyer-facing asset before publication.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--asset-file", type=Path)
    parser.add_argument("--use-latest-asset", action="store_true")
    parser.add_argument("--allow-no-go-asset", action="store_true")
    parser.add_argument("--review-status", default="")
    parser.add_argument("--reviewers", default="")
    parser.add_argument("--claims-issues", default="")
    parser.add_argument("--support-gaps", default="")
    parser.add_argument("--safe-claims-approved", action="store_true")
    parser.add_argument("--support-approved", action="store_true")
    parser.add_argument("--release-notes-approved", action="store_true")
    parser.add_argument("--rollback-ready", action="store_true")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--confirm-asset-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-approved", action="store_true")
    parser.add_argument("--confirm-support-approved", action="store_true")
    parser.add_argument("--confirm-release-notes-approved", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    asset_file = args.asset_file
    if args.use_latest_asset:
        asset_file = latest_asset_file()
    confirmations = {
        "asset_reviewed": args.confirm_asset_reviewed,
        "safe_claims_approved": args.confirm_safe_claims_approved,
        "support_approved": args.confirm_support_approved,
        "release_notes_approved": args.confirm_release_notes_approved,
        "rollback_ready": args.confirm_rollback_ready,
    }
    report = collect_private_asset_review(
        config_path=args.config,
        manifest_path=args.manifest,
        asset_file=asset_file,
        review_status=args.review_status,
        reviewers=parse_int(args.reviewers, -1),
        claims_issues=parse_int(args.claims_issues, -1),
        support_gaps=parse_int(args.support_gaps, -1),
        safe_claims_approved=args.safe_claims_approved,
        support_approved=args.support_approved,
        release_notes_approved=args.release_notes_approved,
        rollback_ready=args.rollback_ready,
        decision=args.decision,
        owner=args.owner,
        review_notes=args.review_notes,
        next_action=args.next_action,
        confirmations=confirmations,
        allow_no_go_asset=args.allow_no_go_asset,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
