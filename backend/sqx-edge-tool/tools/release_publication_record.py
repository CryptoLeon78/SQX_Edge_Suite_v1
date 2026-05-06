from __future__ import annotations

import argparse
import hashlib
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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "release_publication_record"
DEFAULT_PUBLIC_RELEASE_GATE_DIR = TOOL_ROOT / "data" / "public_release_gate"
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


def latest_public_release_gate_file(directory: Path = DEFAULT_PUBLIC_RELEASE_GATE_DIR) -> Path | None:
    return latest_file(directory, "public_release_gate_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def sha256_file_for(zip_path: Path | None) -> Path | None:
    if zip_path is None:
        return None
    candidate = Path(str(zip_path) + ".sha256")
    return candidate if candidate.is_file() else None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_expected_sha256(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8-sig").strip()
    return text.split()[0].upper() if text else ""


def publication_evidence_list() -> list[str]:
    return [
        "git_tag_created",
        "github_release_published",
        "portable_zip_attached",
        "sha256_published_and_matching",
        "download_tested",
        "release_notes_visible",
        "support_window_open",
        "rollback_window_open",
    ]


def valid_https(value: str) -> bool:
    return value.startswith("https://")


def decision_from(
    public_release_gate: dict[str, Any] | None,
    zip_path: Path | None,
    sha256_path: Path | None,
    actual_sha256: str,
    expected_sha256: str,
    release_tag: str,
    release_url: str,
    download_url: str,
    published_by: str,
    git_tag_created: bool,
    github_release_published: bool,
    zip_download_tested: bool,
    sha256_matches_confirmed: bool,
    release_notes_visible: bool,
    support_window_open: bool,
    rollback_window_open: bool,
    allow_no_go_gate: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if public_release_gate is None:
        blockers.append("public_release_gate_missing")
    elif not public_release_gate.get("decision", {}).get("go") and not allow_no_go_gate:
        blockers.append("public_release_gate_not_go")
        blockers.extend(public_release_gate.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if sha256_path is None or not sha256_path.is_file():
        blockers.append("sha256_file_missing")
    elif actual_sha256 and expected_sha256 and actual_sha256 != expected_sha256:
        blockers.append("sha256_mismatch")
    if not release_tag:
        blockers.append("release_tag_missing")
    elif not TAG_PATTERN.match(release_tag):
        blockers.append("release_tag_invalid")
    if not release_url or not valid_https(release_url):
        blockers.append("release_url_missing_or_not_https")
    if download_url and not valid_https(download_url):
        blockers.append("download_url_not_https")
    if not published_by:
        blockers.append("published_by_missing")
    if not git_tag_created:
        blockers.append("git_tag_not_confirmed")
    if not github_release_published:
        blockers.append("github_release_not_published")
    if not zip_download_tested:
        blockers.append("zip_download_not_tested")
    if not sha256_matches_confirmed:
        blockers.append("sha256_not_confirmed")
    if not release_notes_visible:
        blockers.append("release_notes_not_visible")
    if not support_window_open:
        blockers.append("support_window_not_open")
    if not rollback_window_open:
        blockers.append("rollback_window_not_open")
    if not download_url:
        warnings.append("download_url_not_recorded")

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
        "# SQX Edge Release Publication Record",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Public release gate source: `{report.get('public_release_gate_source') or 'none'}`",
        f"- Release tag: `{report.get('release_tag') or 'missing'}`",
        f"- Release URL: `{report.get('release_url') or 'missing'}`",
        f"- Download URL: `{report.get('download_url') or 'not recorded'}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        f"- ZIP SHA256: `{report.get('actual_sha256') or 'not calculated'}`",
        "",
        "## Publication Evidence",
    ]
    lines.extend(f"- {item}" for item in report["publication_evidence"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_record(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"release_publication_record_{current_stamp}.json"
    md_path = output_dir / f"release_publication_record_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_record(
    manifest_path: Path = DEFAULT_MANIFEST,
    public_release_gate_file: Path | None = None,
    zip_path: Path | None = None,
    sha256_path: Path | None = None,
    release_tag: str = "",
    release_url: str = "",
    download_url: str = "",
    published_by: str = "",
    git_tag_created: bool = False,
    github_release_published: bool = False,
    zip_download_tested: bool = False,
    sha256_matches_confirmed: bool = False,
    release_notes_visible: bool = False,
    support_window_open: bool = False,
    rollback_window_open: bool = False,
    allow_no_go_gate: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    load_json(manifest_path)
    public_release_gate = load_json(public_release_gate_file) if public_release_gate_file else None
    final_zip = zip_path or latest_portable_zip()
    final_sha256_path = sha256_path or sha256_file_for(final_zip)
    actual_sha256 = file_sha256(final_zip) if final_zip and final_zip.is_file() else ""
    expected_sha256 = read_expected_sha256(final_sha256_path)
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "public_release_gate_source": str(public_release_gate_file) if public_release_gate_file else "",
        "public_release_gate_decision": public_release_gate.get("decision") if public_release_gate else None,
        "zip_path": str(final_zip) if final_zip else "",
        "sha256_path": str(final_sha256_path) if final_sha256_path else "",
        "actual_sha256": actual_sha256,
        "expected_sha256": expected_sha256,
        "release_tag": release_tag,
        "release_url": release_url,
        "download_url": download_url,
        "published_by": published_by,
        "git_tag_created": git_tag_created,
        "github_release_published": github_release_published,
        "zip_download_tested": zip_download_tested,
        "sha256_matches_confirmed": sha256_matches_confirmed,
        "release_notes_visible": release_notes_visible,
        "support_window_open": support_window_open,
        "rollback_window_open": rollback_window_open,
        "publication_evidence": publication_evidence_list(),
        "decision": decision_from(
            public_release_gate,
            final_zip,
            final_sha256_path,
            actual_sha256,
            expected_sha256,
            release_tag,
            release_url,
            download_url,
            published_by,
            git_tag_created,
            github_release_published,
            zip_download_tested,
            sha256_matches_confirmed,
            release_notes_visible,
            support_window_open,
            rollback_window_open,
            allow_no_go_gate,
        ),
    }
    if write:
        report["evidence_paths"] = write_record(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge release publication record")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--public-release-gate-file", default="")
    parser.add_argument("--use-latest-public-release-gate", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--sha256-file", default="")
    parser.add_argument("--release-tag", default=env_value("SQX_RELEASE_TAG"))
    parser.add_argument("--release-url", default=env_value("SQX_RELEASE_URL"))
    parser.add_argument("--download-url", default=env_value("SQX_RELEASE_DOWNLOAD_URL"))
    parser.add_argument("--published-by", default=env_value("SQX_RELEASE_PUBLISHED_BY"))
    parser.add_argument("--confirm-git-tag-created", action="store_true")
    parser.add_argument("--confirm-github-release-published", action="store_true")
    parser.add_argument("--confirm-zip-download-tested", action="store_true")
    parser.add_argument("--confirm-sha256-matches", action="store_true")
    parser.add_argument("--confirm-release-notes-visible", action="store_true")
    parser.add_argument("--confirm-support-window-open", action="store_true")
    parser.add_argument("--confirm-rollback-window-open", action="store_true")
    parser.add_argument("--allow-no-go-gate", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    gate_file = Path(args.public_release_gate_file) if args.public_release_gate_file else None
    if args.use_latest_public_release_gate and gate_file is None:
        gate_file = latest_public_release_gate_file()
        if gate_file is None:
            print(json.dumps({"ok": False, "error": "public_release_gate_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_record(
        manifest_path=Path(args.manifest),
        public_release_gate_file=gate_file,
        zip_path=Path(args.zip) if args.zip else None,
        sha256_path=Path(args.sha256_file) if args.sha256_file else None,
        release_tag=args.release_tag,
        release_url=args.release_url,
        download_url=args.download_url,
        published_by=args.published_by,
        git_tag_created=args.confirm_git_tag_created,
        github_release_published=args.confirm_github_release_published,
        zip_download_tested=args.confirm_zip_download_tested,
        sha256_matches_confirmed=args.confirm_sha256_matches,
        release_notes_visible=args.confirm_release_notes_visible,
        support_window_open=args.confirm_support_window_open,
        rollback_window_open=args.confirm_rollback_window_open,
        allow_no_go_gate=args.allow_no_go_gate,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
