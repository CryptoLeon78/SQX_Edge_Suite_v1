from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "public_release_gate"
DEFAULT_LAUNCH_ASSETS_DIR = TOOL_ROOT / "data" / "launch_assets_kit"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"
TAG_PATTERN = re.compile(r"^v?\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_launch_assets_file(directory: Path = DEFAULT_LAUNCH_ASSETS_DIR) -> Path | None:
    return latest_file(directory, "launch_assets_kit_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def release_checklist() -> list[str]:
    return [
        "Confirm final tag matches the published build.",
        "Review GitHub Release title, copy, assets and buyer steps.",
        "Attach the final portable ZIP to the release.",
        "Publish the ZIP SHA256 next to the download.",
        "Confirm checkout is paused or intentionally ready for the release window.",
        "Confirm support inbox and response macro are ready.",
        "Confirm rollback owner can pause checkout, webhook, worker and manual fulfillment.",
    ]


def valid_https(value: str) -> bool:
    return value.startswith("https://")


def decision_from(
    launch_assets: dict[str, Any] | None,
    zip_path: Path | None,
    release_tag: str,
    release_title: str,
    release_draft_url: str,
    rollback_owner: str,
    support_owner: str,
    github_release_reviewed: bool,
    zip_attached: bool,
    sha256_published: bool,
    checkout_paused_or_ready: bool,
    support_ready: bool,
    rollback_ready: bool,
    allow_no_go_assets: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if launch_assets is None:
        blockers.append("launch_assets_kit_missing")
    elif not launch_assets.get("decision", {}).get("go") and not allow_no_go_assets:
        blockers.append("launch_assets_kit_not_go")
        blockers.extend(launch_assets.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if not release_tag:
        blockers.append("release_tag_missing")
    elif not TAG_PATTERN.match(release_tag):
        blockers.append("release_tag_invalid")
    elif not release_tag.startswith("v"):
        warnings.append("release_tag_without_v_prefix")
    if not release_title:
        blockers.append("release_title_missing")
    if not release_draft_url or not valid_https(release_draft_url):
        blockers.append("release_draft_url_missing_or_not_https")
    if not github_release_reviewed:
        blockers.append("github_release_not_reviewed")
    if not zip_attached:
        blockers.append("zip_not_attached")
    if not sha256_published:
        blockers.append("sha256_not_published")
    if not checkout_paused_or_ready:
        blockers.append("checkout_not_confirmed")
    if not support_ready:
        blockers.append("support_not_ready")
    if not rollback_ready:
        blockers.append("rollback_not_ready")
    if not rollback_owner:
        blockers.append("rollback_owner_missing")
    if not support_owner:
        blockers.append("support_owner_missing")

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
        "# SQX Edge Public Release Gate",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Launch assets source: `{report.get('launch_assets_source') or 'none'}`",
        f"- Release tag: `{report.get('release_tag') or 'missing'}`",
        f"- Release URL: `{report.get('release_draft_url') or 'missing'}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        "",
        "## Release Checklist",
    ]
    lines.extend(f"- {item}" for item in report["release_checklist"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_gate(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"public_release_gate_{current_stamp}.json"
    md_path = output_dir / f"public_release_gate_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_gate(
    manifest_path: Path = DEFAULT_MANIFEST,
    launch_assets_file: Path | None = None,
    zip_path: Path | None = None,
    release_tag: str = "",
    release_title: str = "",
    release_draft_url: str = "",
    rollback_owner: str = "",
    support_owner: str = "",
    github_release_reviewed: bool = False,
    zip_attached: bool = False,
    sha256_published: bool = False,
    checkout_paused_or_ready: bool = False,
    support_ready: bool = False,
    rollback_ready: bool = False,
    allow_no_go_assets: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    launch_assets = load_json(launch_assets_file) if launch_assets_file else None
    final_zip = zip_path or latest_portable_zip()
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "launch_assets_source": str(launch_assets_file) if launch_assets_file else "",
        "launch_assets_decision": launch_assets.get("decision") if launch_assets else None,
        "zip_path": str(final_zip) if final_zip else "",
        "release_tag": release_tag,
        "release_title": release_title,
        "release_draft_url": release_draft_url,
        "rollback_owner": rollback_owner,
        "support_owner": support_owner,
        "github_release_reviewed": github_release_reviewed,
        "zip_attached": zip_attached,
        "sha256_published": sha256_published,
        "checkout_paused_or_ready": checkout_paused_or_ready,
        "support_ready": support_ready,
        "rollback_ready": rollback_ready,
        "release_checklist": release_checklist(),
        "decision": decision_from(
            launch_assets,
            final_zip,
            release_tag,
            release_title,
            release_draft_url,
            rollback_owner,
            support_owner,
            github_release_reviewed,
            zip_attached,
            sha256_published,
            checkout_paused_or_ready,
            support_ready,
            rollback_ready,
            allow_no_go_assets,
        ),
    }
    if write:
        report["evidence_paths"] = write_gate(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge public release gate")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--launch-assets-file", default="")
    parser.add_argument("--use-latest-launch-assets", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--release-tag", default=env_value("SQX_RELEASE_TAG"))
    parser.add_argument("--release-title", default=env_value("SQX_RELEASE_TITLE"))
    parser.add_argument("--release-draft-url", default=env_value("SQX_RELEASE_DRAFT_URL"))
    parser.add_argument("--rollback-owner", default=env_value("SQX_RELEASE_ROLLBACK_OWNER"))
    parser.add_argument("--support-owner", default=env_value("SQX_RELEASE_SUPPORT_OWNER"))
    parser.add_argument("--confirm-github-release-reviewed", action="store_true")
    parser.add_argument("--confirm-zip-attached", action="store_true")
    parser.add_argument("--confirm-sha256-published", action="store_true")
    parser.add_argument("--confirm-checkout-paused-or-ready", action="store_true")
    parser.add_argument("--confirm-support-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--allow-no-go-assets", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    launch_assets_file = Path(args.launch_assets_file) if args.launch_assets_file else None
    if args.use_latest_launch_assets and launch_assets_file is None:
        launch_assets_file = latest_launch_assets_file()
        if launch_assets_file is None:
            print(json.dumps({"ok": False, "error": "launch_assets_kit_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_gate(
        manifest_path=Path(args.manifest),
        launch_assets_file=launch_assets_file,
        zip_path=Path(args.zip) if args.zip else None,
        release_tag=args.release_tag,
        release_title=args.release_title,
        release_draft_url=args.release_draft_url,
        rollback_owner=args.rollback_owner,
        support_owner=args.support_owner,
        github_release_reviewed=args.confirm_github_release_reviewed,
        zip_attached=args.confirm_zip_attached,
        sha256_published=args.confirm_sha256_published,
        checkout_paused_or_ready=args.confirm_checkout_paused_or_ready,
        support_ready=args.confirm_support_ready,
        rollback_ready=args.confirm_rollback_ready,
        allow_no_go_assets=args.allow_no_go_assets,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
