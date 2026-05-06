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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "commercial_release_candidate"
DEFAULT_READINESS_DIR = TOOL_ROOT / "data" / "checkout_live_readiness"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_portable_zip(dist_dir: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(dist_dir, "SQX_Edge_Tool_Portable_*.zip")


def latest_readiness_file(directory: Path = DEFAULT_READINESS_DIR) -> Path | None:
    return latest_file(directory, "checkout_live_readiness_*.json")


def manifest_public_key_is_placeholder(manifest: dict[str, Any]) -> bool:
    public_key = manifest.get("licensing", {}).get("publicKey", {})
    kid = str(public_key.get("kid") or "").lower()
    modulus = str(public_key.get("n") or "")
    return "placeholder" in kid or len(modulus) < 100


def checkout_urls_ready(manifest: dict[str, Any]) -> bool:
    checkout = manifest.get("upgrade", {}).get("checkout", {})
    primary = str(checkout.get("primaryUrl") or "").strip()
    return bool(re.match(r"^https://", primary))


def pilot_steps() -> list[str]:
    return [
        "Run checkout_live_readiness.py and require GO evidence.",
        "Publish checkout only to a private pilot link or test audience.",
        "Run one pilot purchase for pro_monthly or pro_annual.",
        "Verify the relay receives the Lemon webhook and dispatches to local ingest.",
        "Issue or confirm the signed license and prepare the customer delivery.",
        "Open the portable ZIP, import license and verify Pro features unlock.",
        "Record order id, customer email, license id, ZIP SHA256 and support contact.",
    ]


def rollback_steps() -> list[str]:
    return [
        "Unpublish checkout links.",
        "Pause Lemon webhook delivery.",
        "Pause Render worker.",
        "Revert to manual signed-license fulfillment.",
        "Rotate webhook and relay secrets if any live secret was exposed.",
        "Notify pilot customer with manual delivery if automation failed after payment.",
    ]


def decision_from(
    manifest: dict[str, Any],
    readiness: dict[str, Any] | None,
    zip_path: Path | None,
    pilot_purchase_confirmed: bool,
    allow_no_go_readiness: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    checkout = manifest.get("upgrade", {}).get("checkout", {})

    if checkout.get("status") != "commercial_release_candidate_ready":
        blockers.append("checkout_status_not_commercial_release_candidate_ready")
    if checkout.get("automation", {}).get("status") != "commercial_release_candidate_ready":
        blockers.append("automation_status_not_commercial_release_candidate_ready")
    if not checkout_urls_ready(manifest):
        blockers.append("primary_checkout_url_missing_or_not_https")
    if manifest_public_key_is_placeholder(manifest):
        blockers.append("production_public_key_placeholder")
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if readiness is None:
        blockers.append("checkout_live_readiness_missing")
    elif not readiness.get("decision", {}).get("go") and not allow_no_go_readiness:
        blockers.append("checkout_live_readiness_not_go")
        blockers.extend(readiness.get("decision", {}).get("blockers", []))
    if not pilot_purchase_confirmed:
        blockers.append("pilot_purchase_not_confirmed")

    if checkout.get("fulfillmentMode") == "manual_signed_license":
        warnings.append("manual_signed_license_fallback_enabled")
    if checkout.get("fallbackProvider") == "Gumroad":
        warnings.append("gumroad_fallback_configured")

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
        "# SQX Edge Commercial Release Candidate",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        f"- ZIP SHA256: `{report.get('zip_sha256') or 'not available'}`",
        f"- Readiness source: `{report.get('readiness_source') or 'none'}`",
        f"- Pilot purchase confirmed: `{report['pilot_purchase_confirmed']}`",
        "",
        "## Pilot Steps",
    ]
    lines.extend(f"- {item}" for item in report["pilot_steps"])
    lines.append("")
    lines.append("## Rollback")
    lines.extend(f"- {item}" for item in report["rollback_steps"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_candidate(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"commercial_release_candidate_{current_stamp}.json"
    md_path = output_dir / f"commercial_release_candidate_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_candidate(
    manifest_path: Path = DEFAULT_MANIFEST,
    readiness_file: Path | None = None,
    zip_path: Path | None = None,
    pilot_purchase_confirmed: bool = False,
    allow_no_go_readiness: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    readiness = load_json(readiness_file) if readiness_file else None
    final_zip = zip_path or latest_portable_zip()
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "readiness_source": str(readiness_file) if readiness_file else "",
        "readiness_decision": readiness.get("decision") if readiness else None,
        "zip_path": str(final_zip) if final_zip else "",
        "zip_sha256": sha256_file(final_zip) if final_zip and final_zip.is_file() else "",
        "pilot_purchase_confirmed": pilot_purchase_confirmed,
        "pilot_steps": pilot_steps(),
        "rollback_steps": rollback_steps(),
        "decision": decision_from(manifest, readiness, final_zip, pilot_purchase_confirmed, allow_no_go_readiness),
    }
    if write:
        report["evidence_paths"] = write_candidate(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge commercial release candidate gate")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--readiness-file", default="")
    parser.add_argument("--use-latest-readiness", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--pilot-purchase-confirmed", action="store_true")
    parser.add_argument("--allow-no-go-readiness", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    readiness_file = Path(args.readiness_file) if args.readiness_file else None
    if args.use_latest_readiness and readiness_file is None:
        readiness_file = latest_readiness_file()
        if readiness_file is None:
            print(json.dumps({"ok": False, "error": "checkout_live_readiness_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_candidate(
        manifest_path=Path(args.manifest),
        readiness_file=readiness_file,
        zip_path=Path(args.zip) if args.zip else None,
        pilot_purchase_confirmed=args.pilot_purchase_confirmed,
        allow_no_go_readiness=args.allow_no_go_readiness,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
