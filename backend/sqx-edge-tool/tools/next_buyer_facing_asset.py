from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "next_buyer_facing_asset.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "next_buyer_facing_asset"
DEFAULT_REVIEW_DIR = TOOL_ROOT / "data" / "controlled_distribution_review"
EXPECTED_STATE = "next_buyer_facing_asset_ready"


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


def latest_review_file(directory: Path = DEFAULT_REVIEW_DIR) -> Path | None:
    return latest_file(directory, "controlled_distribution_review_*.json")


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
    review_config_path = project_path(str(depends_on.get("controlledDistributionReviewConfig", "")))
    if not review_config_path.is_file():
        return ["controlled_distribution_review_config_missing"]
    review_config = load_json(review_config_path)
    if review_config.get("state") != depends_on.get("controlledDistributionReviewState"):
        return ["controlled_distribution_review_state_invalid"]
    return []


def validate_review(review: dict[str, Any] | None, allow_no_go_review: bool) -> list[str]:
    if review is None:
        return ["controlled_distribution_review_evidence_missing"]
    decision = review.get("decision", {})
    if not decision.get("go") and not allow_no_go_review:
        return ["controlled_distribution_review_not_go", *decision.get("blockers", [])]
    if review.get("review_decision") != "prepare_buyer_facing_asset" and not allow_no_go_review:
        return ["m73_did_not_select_prepare_buyer_facing_asset"]
    return []


def is_safe_text(value: str) -> bool:
    if not value.strip():
        return False
    return not bool(re.search(r"[\r\n<>]", value))


def asset_checklist() -> list[str]:
    return [
        "Load M73 review evidence before preparing any buyer-facing asset.",
        "Keep the asset small, private-review only and reversible.",
        "Confirm safe claims, support readiness and release notes before review.",
        "Store only redacted scope and decision metadata.",
        "Record owner, reviewers and next review before sharing the asset.",
    ]


def decision_from(
    config: dict[str, Any],
    review: dict[str, Any] | None,
    asset_type: str,
    asset_status: str,
    asset_scope_items: int,
    reviewers: int,
    safe_claims_confirmed: bool,
    support_ready: bool,
    release_notes_ready: bool,
    decision: str,
    owner: str,
    asset_notes: str,
    next_review: str,
    confirmations: dict[str, bool],
    allow_no_go_review: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_review(review, allow_no_go_review))

    if asset_type not in set(config.get("allowedAssetTypes", [])):
        blockers.append("next_buyer_facing_asset_type_invalid")
    if asset_status not in set(config.get("allowedAssetStatuses", [])):
        blockers.append("next_buyer_facing_asset_status_invalid")
    if decision not in set(config.get("allowedDecisions", [])):
        blockers.append("next_buyer_facing_asset_decision_invalid")
    if any(value < 0 for value in (asset_scope_items, reviewers)):
        blockers.append("next_buyer_facing_asset_metrics_invalid")
    if asset_scope_items > int(config.get("maximumAssetScopeItems", 5)):
        blockers.append("next_buyer_facing_asset_scope_too_large")
    if reviewers < int(config.get("minimumReviewers", 1)):
        blockers.append("next_buyer_facing_asset_reviewer_missing")
    if not is_safe_text(owner):
        blockers.append("next_buyer_facing_asset_owner_missing_or_unsafe")
    if not asset_notes.strip():
        blockers.append("next_buyer_facing_asset_notes_missing")
    if not next_review.strip():
        blockers.append("next_buyer_facing_asset_next_review_missing")

    if decision == "prepare_private_review":
        if asset_status != "ready_private_review":
            blockers.append("prepare_private_review_requires_ready_private_review_status")
        if not safe_claims_confirmed:
            blockers.append("prepare_private_review_requires_safe_claims")
        if not support_ready:
            blockers.append("prepare_private_review_requires_support_ready")
        if not release_notes_ready:
            blockers.append("prepare_private_review_requires_release_notes")
    if decision == "hold_for_fix":
        warnings.append("operator_decision_hold_for_fix")
    if decision == "pause_sales":
        warnings.append("operator_decision_pause_sales")
    if asset_status == "blocked" and decision not in {"hold_for_fix", "pause_sales"}:
        blockers.append("blocked_asset_requires_hold_or_pause")

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
        "# Next Buyer-Facing Asset Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Asset type: `{report.get('asset_type') or 'missing'}`",
        f"- Asset status: `{report.get('asset_status') or 'missing'}`",
        f"- Asset decision: `{report.get('asset_decision') or 'missing'}`",
        f"- Owner: `{report.get('owner') or 'missing'}`",
        "",
        "## Checklist",
    ]
    lines.extend(f"- {item}" for item in report["asset_checklist"])
    lines.append("")
    lines.append("## Metrics")
    for name in ("asset_scope_items", "reviewers"):
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
    json_path = output_dir / f"next_buyer_facing_asset_{current_stamp}.json"
    md_path = output_dir / f"next_buyer_facing_asset_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_next_buyer_facing_asset(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    review_file: Path | None = None,
    asset_type: str = "",
    asset_status: str = "",
    asset_scope_items: int = -1,
    reviewers: int = -1,
    safe_claims_confirmed: bool = False,
    support_ready: bool = False,
    release_notes_ready: bool = False,
    decision: str = "",
    owner: str = "",
    asset_notes: str = "",
    next_review: str = "",
    confirmations: dict[str, bool] | None = None,
    allow_no_go_review: bool = False,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    review = load_json(review_file) if review_file else None
    confirmations = confirmations or {}
    asset_decision = decision_from(
        config,
        review,
        asset_type,
        asset_status,
        asset_scope_items,
        reviewers,
        safe_claims_confirmed,
        support_ready,
        release_notes_ready,
        decision,
        owner,
        asset_notes,
        next_review,
        confirmations,
        allow_no_go_review,
    )
    return {
        "created_at": now_iso(),
        "state": config.get("state"),
        "review_id": config.get("reviewId"),
        "manifest_checkout_status": manifest.get("upgrade", {}).get("checkout", {}).get("status"),
        "source_review_file": str(review_file) if review_file else "",
        "source_review_decision": review.get("review_decision", "") if review else "",
        "asset_type": asset_type,
        "asset_status": asset_status,
        "asset_scope_items": asset_scope_items,
        "reviewers": reviewers,
        "safe_claims_confirmed": safe_claims_confirmed,
        "support_ready": support_ready,
        "release_notes_ready": release_notes_ready,
        "asset_decision": decision,
        "owner": owner,
        "asset_notes": asset_notes,
        "next_review": next_review,
        "confirmations": confirmations,
        "asset_checklist": asset_checklist(),
        "decision": asset_decision,
        "privacy_policy": config.get("privacyPolicy"),
        "asset_policy": config.get("assetPolicy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare the next buyer-facing asset for private review.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--review-file", type=Path)
    parser.add_argument("--use-latest-review", action="store_true")
    parser.add_argument("--allow-no-go-review", action="store_true")
    parser.add_argument("--asset-type", default="")
    parser.add_argument("--asset-status", default="")
    parser.add_argument("--asset-scope-items", default="")
    parser.add_argument("--reviewers", default="")
    parser.add_argument("--safe-claims-confirmed", action="store_true")
    parser.add_argument("--support-ready", action="store_true")
    parser.add_argument("--release-notes-ready", action="store_true")
    parser.add_argument("--decision", default="")
    parser.add_argument("--owner", default="")
    parser.add_argument("--asset-notes", default="")
    parser.add_argument("--next-review", default="")
    parser.add_argument("--confirm-m73-reviewed", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-release-notes-ready", action="store_true")
    parser.add_argument("--confirm-private-review-owner", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    review_file = args.review_file
    if args.use_latest_review:
        review_file = latest_review_file()
    confirmations = {
        "m73_reviewed": args.confirm_m73_reviewed,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "support_ready": args.confirm_support_ready,
        "release_notes_ready": args.confirm_release_notes_ready,
        "private_review_owner": args.confirm_private_review_owner,
    }
    report = collect_next_buyer_facing_asset(
        config_path=args.config,
        manifest_path=args.manifest,
        review_file=review_file,
        asset_type=args.asset_type,
        asset_status=args.asset_status,
        asset_scope_items=parse_int(args.asset_scope_items, -1),
        reviewers=parse_int(args.reviewers, -1),
        safe_claims_confirmed=args.safe_claims_confirmed,
        support_ready=args.support_ready,
        release_notes_ready=args.release_notes_ready,
        decision=args.decision,
        owner=args.owner,
        asset_notes=args.asset_notes,
        next_review=args.next_review,
        confirmations=confirmations,
        allow_no_go_review=args.allow_no_go_review,
    )
    if not args.no_write:
        report["evidence_files"] = write_evidence(report, args.output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
