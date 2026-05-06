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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "limited_public_launch"
DEFAULT_PILOT_DIR = TOOL_ROOT / "data" / "pilot_purchase_kit"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"
REQUIRED_VARIANTS = ("pro_monthly", "pro_annual", "setup_assist")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_pilot_file(directory: Path = DEFAULT_PILOT_DIR) -> Path | None:
    return latest_file(directory, "pilot_purchase_kit_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def is_https(value: str) -> bool:
    return value.strip().lower().startswith("https://")


def is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def variant_ids(checkout: dict[str, Any]) -> dict[str, str]:
    variants = {}
    for item in checkout.get("variants", []):
        plan = str(item.get("plan") or "").strip()
        if plan:
            variants[plan] = str(item.get("providerVariantId") or "").strip()
    return variants


def launch_checklist() -> list[str]:
    return [
        "Publish only the limited checkout link.",
        "Keep first-sale cap active until support confidence is proven.",
        "Watch Lemon order, Render relay, local fulfillment queue and support inbox.",
        "Issue or confirm signed Pro license for every paid order.",
        "Send customer delivery and confirm first successful activation.",
        "Record order id, license id, ZIP SHA256 and support outcome.",
        "Keep rollback owner available during the launch window.",
    ]


def rollback_steps() -> list[str]:
    return [
        "Unpublish or pause checkout link.",
        "Pause Lemon webhook delivery if events duplicate or fail.",
        "Pause Render worker if dispatch fails repeatedly.",
        "Switch to manual fulfillment for paid customers.",
        "Refund customers if delivery cannot be completed inside support SLA.",
    ]


def decision_from(
    manifest: dict[str, Any],
    pilot: dict[str, Any] | None,
    zip_path: Path | None,
    support_email: str,
    first_sale_cap: int,
    launch_window: str,
    rollback_owner: str,
    public_checkout_confirmed: bool,
    support_inbox_confirmed: bool,
    allow_no_go_pilot: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    checkout = manifest.get("upgrade", {}).get("checkout", {})
    primary_url = str(checkout.get("primaryUrl") or manifest.get("upgrade", {}).get("checkoutUrl") or "").strip()
    fallback_url = str(checkout.get("fallbackUrl") or "").strip()
    variants = variant_ids(checkout)

    if pilot is None:
        blockers.append("pilot_purchase_kit_missing")
    elif not pilot.get("decision", {}).get("go") and not allow_no_go_pilot:
        blockers.append("pilot_purchase_kit_not_go")
        blockers.extend(pilot.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if not is_https(primary_url):
        blockers.append("primary_checkout_url_missing_or_not_https")
    if fallback_url and not is_https(fallback_url):
        blockers.append("fallback_checkout_url_not_https")
    for plan in REQUIRED_VARIANTS:
        if not variants.get(plan):
            blockers.append(f"provider_variant_missing_{plan}")
    if not is_email(support_email):
        blockers.append("support_email_missing_or_invalid")
    if first_sale_cap < 1 or first_sale_cap > 25:
        blockers.append("first_sale_cap_out_of_range")
    if not launch_window.strip():
        blockers.append("launch_window_missing")
    if not rollback_owner.strip():
        blockers.append("rollback_owner_missing")
    if not public_checkout_confirmed:
        blockers.append("public_checkout_not_confirmed")
    if not support_inbox_confirmed:
        blockers.append("support_inbox_not_confirmed")
    if first_sale_cap > 10:
        warnings.append("first_sale_cap_above_recommended_soft_launch")

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
        "# SQX Edge Limited Public Launch Gate",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Pilot kit source: `{report.get('pilot_kit_source') or 'none'}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        f"- First sale cap: `{report['first_sale_cap']}`",
        f"- Launch window: `{report.get('launch_window') or 'not configured'}`",
        f"- Rollback owner: `{report.get('rollback_owner') or 'not configured'}`",
        "",
        "## Launch Checklist",
    ]
    lines.extend(f"- {item}" for item in report["launch_checklist"])
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


def write_gate(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"limited_public_launch_{current_stamp}.json"
    md_path = output_dir / f"limited_public_launch_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_gate(
    manifest_path: Path = DEFAULT_MANIFEST,
    pilot_file: Path | None = None,
    zip_path: Path | None = None,
    support_email: str = "",
    first_sale_cap: int = 5,
    launch_window: str = "",
    rollback_owner: str = "",
    public_checkout_confirmed: bool = False,
    support_inbox_confirmed: bool = False,
    allow_no_go_pilot: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    checkout = manifest.get("upgrade", {}).get("checkout", {})
    final_zip = zip_path or latest_portable_zip()
    pilot = load_json(pilot_file) if pilot_file else None
    final_support_email = support_email or str(checkout.get("supportEmail") or "").strip()
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "pilot_kit_source": str(pilot_file) if pilot_file else "",
        "pilot_decision": pilot.get("decision") if pilot else None,
        "zip_path": str(final_zip) if final_zip else "",
        "primary_checkout_url": str(checkout.get("primaryUrl") or manifest.get("upgrade", {}).get("checkoutUrl") or "").strip(),
        "fallback_checkout_url": str(checkout.get("fallbackUrl") or "").strip(),
        "variant_ids": variant_ids(checkout),
        "support_email": final_support_email,
        "first_sale_cap": first_sale_cap,
        "launch_window": launch_window,
        "rollback_owner": rollback_owner,
        "public_checkout_confirmed": public_checkout_confirmed,
        "support_inbox_confirmed": support_inbox_confirmed,
        "launch_checklist": launch_checklist(),
        "rollback_steps": rollback_steps(),
        "decision": decision_from(
            manifest,
            pilot,
            final_zip,
            final_support_email,
            first_sale_cap,
            launch_window,
            rollback_owner,
            public_checkout_confirmed,
            support_inbox_confirmed,
            allow_no_go_pilot,
        ),
    }
    if write:
        report["evidence_paths"] = write_gate(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge limited public launch gate")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--pilot-kit-file", default="")
    parser.add_argument("--use-latest-pilot-kit", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--support-email", default=env_value("SQX_SUPPORT_EMAIL"))
    parser.add_argument("--first-sale-cap", type=int, default=int(env_value("SQX_FIRST_SALE_CAP", "5")))
    parser.add_argument("--launch-window", default=env_value("SQX_LAUNCH_WINDOW"))
    parser.add_argument("--rollback-owner", default=env_value("SQX_ROLLBACK_OWNER"))
    parser.add_argument("--confirm-public-checkout", action="store_true")
    parser.add_argument("--confirm-support-inbox", action="store_true")
    parser.add_argument("--allow-no-go-pilot", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    pilot_file = Path(args.pilot_kit_file) if args.pilot_kit_file else None
    if args.use_latest_pilot_kit and pilot_file is None:
        pilot_file = latest_pilot_file()
        if pilot_file is None:
            print(json.dumps({"ok": False, "error": "pilot_purchase_kit_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_gate(
        manifest_path=Path(args.manifest),
        pilot_file=pilot_file,
        zip_path=Path(args.zip) if args.zip else None,
        support_email=args.support_email,
        first_sale_cap=args.first_sale_cap,
        launch_window=args.launch_window,
        rollback_owner=args.rollback_owner,
        public_checkout_confirmed=args.confirm_public_checkout,
        support_inbox_confirmed=args.confirm_support_inbox,
        allow_no_go_pilot=args.allow_no_go_pilot,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
