from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "launch_assets_kit"
DEFAULT_PUBLIC_OFFER_DIR = TOOL_ROOT / "data" / "public_offer_pack"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"
DEFAULT_SCREENSHOT_DIR = PROJECT_ROOT / "output" / "playwright"


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_public_offer_file(directory: Path = DEFAULT_PUBLIC_OFFER_DIR) -> Path | None:
    return latest_file(directory, "public_offer_pack_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def screenshot_inventory(directory: Path = DEFAULT_SCREENSHOT_DIR) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(str(path) for path in directory.glob("*.png"))


def launch_asset_list() -> list[str]:
    return [
        "portable_zip",
        "zip_sha256",
        "desktop_screenshots",
        "mobile_screenshots",
        "short_copy",
        "long_copy",
        "commercial_readme",
        "github_release_draft",
        "support_macro",
        "publication_checklist",
    ]


def publication_checklist() -> list[str]:
    return [
        "Attach final portable ZIP and SHA256.",
        "Include short copy and long copy.",
        "Include desktop and mobile screenshots.",
        "Include buyer steps and support path.",
        "Link commercial README and release notes.",
        "Confirm checkout and support inbox before publishing.",
        "Keep rollback owner available during publication window.",
    ]


def decision_from(
    public_offer: dict[str, Any] | None,
    zip_path: Path | None,
    screenshot_paths: list[str],
    short_copy_ready: bool,
    long_copy_ready: bool,
    commercial_readme_ready: bool,
    github_release_draft_ready: bool,
    support_macro_ready: bool,
    publication_checklist_ready: bool,
    zip_sha256_confirmed: bool,
    allow_no_go_offer: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    has_desktop = any("desktop" in Path(path).name.lower() for path in screenshot_paths)
    has_mobile = any("mobile" in Path(path).name.lower() for path in screenshot_paths)

    if public_offer is None:
        blockers.append("public_offer_pack_missing")
    elif not public_offer.get("decision", {}).get("go") and not allow_no_go_offer:
        blockers.append("public_offer_pack_not_go")
        blockers.extend(public_offer.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if not zip_sha256_confirmed:
        blockers.append("zip_sha256_not_confirmed")
    if len(screenshot_paths) < 4:
        blockers.append("launch_screenshots_missing")
    if not has_desktop:
        blockers.append("desktop_screenshot_missing")
    if not has_mobile:
        blockers.append("mobile_screenshot_missing")
    if not short_copy_ready:
        blockers.append("short_copy_not_ready")
    if not long_copy_ready:
        blockers.append("long_copy_not_ready")
    if not commercial_readme_ready:
        blockers.append("commercial_readme_not_ready")
    if not github_release_draft_ready:
        blockers.append("github_release_draft_not_ready")
    if not support_macro_ready:
        blockers.append("support_macro_not_ready")
    if not publication_checklist_ready:
        blockers.append("publication_checklist_not_ready")
    if len(screenshot_paths) < 6:
        warnings.append("screenshot_count_below_recommended_launch_pack")

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
        "# SQX Edge Launch Assets Kit",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Public offer source: `{report.get('public_offer_source') or 'none'}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        f"- Screenshot count: `{len(report['screenshots'])}`",
        "",
        "## Required Assets",
    ]
    lines.extend(f"- {item}" for item in report["launch_assets"])
    lines.append("")
    lines.append("## Publication Checklist")
    lines.extend(f"- {item}" for item in report["publication_checklist"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_kit(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"launch_assets_kit_{current_stamp}.json"
    md_path = output_dir / f"launch_assets_kit_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_kit(
    manifest_path: Path = DEFAULT_MANIFEST,
    public_offer_file: Path | None = None,
    zip_path: Path | None = None,
    short_copy_ready: bool = False,
    long_copy_ready: bool = False,
    commercial_readme_ready: bool = False,
    github_release_draft_ready: bool = False,
    support_macro_ready: bool = False,
    publication_checklist_ready: bool = False,
    zip_sha256_confirmed: bool = False,
    allow_no_go_offer: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    public_offer = load_json(public_offer_file) if public_offer_file else None
    final_zip = zip_path or latest_portable_zip()
    screenshots = screenshot_inventory()
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "public_offer_source": str(public_offer_file) if public_offer_file else "",
        "public_offer_decision": public_offer.get("decision") if public_offer else None,
        "zip_path": str(final_zip) if final_zip else "",
        "screenshots": screenshots,
        "launch_assets": launch_asset_list(),
        "publication_checklist": publication_checklist(),
        "short_copy_ready": short_copy_ready,
        "long_copy_ready": long_copy_ready,
        "commercial_readme_ready": commercial_readme_ready,
        "github_release_draft_ready": github_release_draft_ready,
        "support_macro_ready": support_macro_ready,
        "publication_checklist_ready": publication_checklist_ready,
        "zip_sha256_confirmed": zip_sha256_confirmed,
        "decision": decision_from(
            public_offer,
            final_zip,
            screenshots,
            short_copy_ready,
            long_copy_ready,
            commercial_readme_ready,
            github_release_draft_ready,
            support_macro_ready,
            publication_checklist_ready,
            zip_sha256_confirmed,
            allow_no_go_offer,
        ),
    }
    if write:
        report["evidence_paths"] = write_kit(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge launch assets kit")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--public-offer-file", default="")
    parser.add_argument("--use-latest-public-offer", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--confirm-short-copy", action="store_true")
    parser.add_argument("--confirm-long-copy", action="store_true")
    parser.add_argument("--confirm-commercial-readme", action="store_true")
    parser.add_argument("--confirm-github-release-draft", action="store_true")
    parser.add_argument("--confirm-support-macro", action="store_true")
    parser.add_argument("--confirm-publication-checklist", action="store_true")
    parser.add_argument("--confirm-zip-sha256", action="store_true")
    parser.add_argument("--allow-no-go-offer", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    public_offer_file = Path(args.public_offer_file) if args.public_offer_file else None
    if args.use_latest_public_offer and public_offer_file is None:
        public_offer_file = latest_public_offer_file()
        if public_offer_file is None:
            print(json.dumps({"ok": False, "error": "public_offer_pack_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_kit(
        manifest_path=Path(args.manifest),
        public_offer_file=public_offer_file,
        zip_path=Path(args.zip) if args.zip else None,
        short_copy_ready=args.confirm_short_copy,
        long_copy_ready=args.confirm_long_copy,
        commercial_readme_ready=args.confirm_commercial_readme,
        github_release_draft_ready=args.confirm_github_release_draft,
        support_macro_ready=args.confirm_support_macro,
        publication_checklist_ready=args.confirm_publication_checklist,
        zip_sha256_confirmed=args.confirm_zip_sha256,
        allow_no_go_offer=args.allow_no_go_offer,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
