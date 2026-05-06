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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "pilot_purchase_kit"
DEFAULT_RC_DIR = TOOL_ROOT / "data" / "commercial_release_candidate"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist"
VALID_PLANS = ("pro_monthly", "pro_annual", "setup_assist")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def latest_rc_file(directory: Path = DEFAULT_RC_DIR) -> Path | None:
    return latest_file(directory, "commercial_release_candidate_*.json")


def latest_portable_zip(directory: Path = DEFAULT_DIST_DIR) -> Path | None:
    return latest_file(directory, "SQX_Edge_Tool_Portable_*.zip")


def is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def safe_slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.strip())
    cleaned = cleaned.strip("_").lower()
    return cleaned or "pilot_customer"


def build_license_command(
    private_key_path: str,
    license_out_path: str,
    customer_name: str,
    customer_email: str,
    order_id: str,
    plan: str,
) -> str:
    return (
        "python backend\\sqx-edge-tool\\tools\\license_issue.py "
        f"--private-key {private_key_path or '<private-key-json-outside-repo>'} "
        f"--out {license_out_path or 'dist\\pilot_licenses\\SQX_Edge_Pro_license.json'} "
        f"--customer-name \"{customer_name or '<customer-name>'}\" "
        f"--customer-email {customer_email or '<customer-email>'} "
        f"--order-id {order_id or '<lemon-order-id>'} "
        f"--plan {plan}"
    )


def build_delivery_command(zip_path: str, license_path: str, customer_slug: str, order_id: str, support_email: str) -> str:
    return (
        "powershell -NoProfile -ExecutionPolicy Bypass -File backend\\sqx-edge-tool\\tools\\prepare_customer_delivery.ps1 "
        f"-ZipPath {zip_path or 'dist\\SQX_Edge_Tool_Portable_YYYYMMDD_HHMMSS.zip'} "
        f"-LicensePath {license_path or 'dist\\pilot_licenses\\SQX_Edge_Pro_license.json'} "
        f"-CustomerSlug {customer_slug or '<customer-slug>'} "
        f"-OrderId {order_id or '<lemon-order-id>'} "
        f"-SupportEmail {support_email or '<support-email>'}"
    )


def pilot_checklist() -> list[str]:
    return [
        "Open private Lemon checkout link.",
        "Complete one pilot purchase with a real or controlled pilot account.",
        "Confirm Lemon order/subscription id and customer email.",
        "Confirm Render received webhook and relay dispatch succeeded.",
        "Issue signed Pro license with license_issue.py.",
        "Prepare customer delivery with prepare_customer_delivery.ps1.",
        "Open the portable ZIP, import license and confirm Pro state.",
        "Record ZIP SHA256, order id, license id and delivery manifest path.",
    ]


def rollback_steps() -> list[str]:
    return [
        "Refund or void pilot purchase if delivery cannot be completed.",
        "Disable checkout link until the failed step is fixed.",
        "Pause Lemon webhook delivery if duplicate or broken events appear.",
        "Pause Render worker if dispatch loops fail.",
        "Deliver manually with signed license if payment already succeeded.",
    ]


def decision_from(
    rc: dict[str, Any] | None,
    zip_path: Path | None,
    customer_name: str,
    customer_email: str,
    order_id: str,
    plan: str,
    signed_license_path: Path | None,
    delivery_manifest_path: Path | None,
    confirm_license_imported: bool,
    allow_no_go_rc: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if rc is None:
        blockers.append("commercial_release_candidate_missing")
    elif not rc.get("decision", {}).get("go") and not allow_no_go_rc:
        blockers.append("commercial_release_candidate_not_go")
        blockers.extend(rc.get("decision", {}).get("blockers", []))
    if zip_path is None or not zip_path.is_file():
        blockers.append("portable_zip_missing")
    if not customer_name.strip():
        blockers.append("pilot_customer_name_missing")
    if not is_email(customer_email):
        blockers.append("pilot_customer_email_missing_or_invalid")
    if not order_id.strip():
        blockers.append("pilot_order_id_missing")
    if plan not in VALID_PLANS:
        blockers.append("pilot_plan_invalid")
    if signed_license_path is None or not signed_license_path.is_file():
        blockers.append("signed_license_missing")
    if delivery_manifest_path is None or not delivery_manifest_path.is_file():
        blockers.append("customer_delivery_manifest_missing")
    if not confirm_license_imported:
        blockers.append("license_import_not_confirmed")
    if plan == "setup_assist":
        warnings.append("setup_assist_is_service_not_primary_pro_subscription")
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
        "# SQX Edge Pilot Purchase Kit",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Commercial RC source: `{report.get('commercial_rc_source') or 'none'}`",
        f"- ZIP: `{report.get('zip_path') or 'not found'}`",
        f"- Pilot order id: `{report.get('order_id') or 'not configured'}`",
        f"- Pilot customer: `{report.get('customer_email') or 'not configured'}`",
        "",
        "## Commands",
        "",
        f"- `{report['license_command']}`",
        f"- `{report['delivery_command']}`",
        "",
        "## Pilot Checklist",
    ]
    lines.extend(f"- {item}" for item in report["pilot_checklist"])
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


def write_kit(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"pilot_purchase_kit_{current_stamp}.json"
    md_path = output_dir / f"pilot_purchase_kit_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_kit(
    manifest_path: Path = DEFAULT_MANIFEST,
    rc_file: Path | None = None,
    zip_path: Path | None = None,
    customer_name: str = "",
    customer_email: str = "",
    order_id: str = "",
    plan: str = "pro_monthly",
    private_key_path: str = "",
    signed_license_path: Path | None = None,
    delivery_manifest_path: Path | None = None,
    support_email: str = "",
    confirm_license_imported: bool = False,
    allow_no_go_rc: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    checkout = manifest.get("upgrade", {}).get("checkout", {})
    final_zip = zip_path or latest_portable_zip()
    rc = load_json(rc_file) if rc_file else None
    customer_slug = safe_slug(customer_email or customer_name)
    license_path_text = str(signed_license_path) if signed_license_path else ""
    zip_path_text = str(final_zip) if final_zip else ""
    support = support_email or str(checkout.get("supportEmail") or "").strip()
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "commercial_rc_source": str(rc_file) if rc_file else "",
        "commercial_rc_decision": rc.get("decision") if rc else None,
        "zip_path": zip_path_text,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_slug": customer_slug,
        "order_id": order_id,
        "plan": plan,
        "signed_license_path": license_path_text,
        "delivery_manifest_path": str(delivery_manifest_path) if delivery_manifest_path else "",
        "confirm_license_imported": confirm_license_imported,
        "license_command": build_license_command(private_key_path, license_path_text, customer_name, customer_email, order_id, plan),
        "delivery_command": build_delivery_command(zip_path_text, license_path_text, customer_slug, order_id, support),
        "pilot_checklist": pilot_checklist(),
        "rollback_steps": rollback_steps(),
        "decision": decision_from(
            rc,
            final_zip,
            customer_name,
            customer_email,
            order_id,
            plan,
            signed_license_path,
            delivery_manifest_path,
            confirm_license_imported,
            allow_no_go_rc,
        ),
    }
    if write:
        report["evidence_paths"] = write_kit(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge pilot purchase kit")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--commercial-rc-file", default="")
    parser.add_argument("--use-latest-commercial-rc", action="store_true")
    parser.add_argument("--zip", default="")
    parser.add_argument("--customer-name", default=env_value("SQX_PILOT_CUSTOMER_NAME"))
    parser.add_argument("--customer-email", default=env_value("SQX_PILOT_CUSTOMER_EMAIL"))
    parser.add_argument("--order-id", default=env_value("SQX_PILOT_ORDER_ID"))
    parser.add_argument("--plan", default=env_value("SQX_PILOT_PLAN", "pro_monthly"), choices=VALID_PLANS)
    parser.add_argument("--private-key", default=env_value("SQX_LICENSE_PRIVATE_KEY"))
    parser.add_argument("--signed-license", default="")
    parser.add_argument("--delivery-manifest", default="")
    parser.add_argument("--support-email", default=env_value("SQX_SUPPORT_EMAIL"))
    parser.add_argument("--confirm-license-imported", action="store_true")
    parser.add_argument("--allow-no-go-commercial-rc", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    rc_file = Path(args.commercial_rc_file) if args.commercial_rc_file else None
    if args.use_latest_commercial_rc and rc_file is None:
        rc_file = latest_rc_file()
        if rc_file is None:
            print(json.dumps({"ok": False, "error": "commercial_release_candidate_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_kit(
        manifest_path=Path(args.manifest),
        rc_file=rc_file,
        zip_path=Path(args.zip) if args.zip else None,
        customer_name=args.customer_name,
        customer_email=args.customer_email,
        order_id=args.order_id,
        plan=args.plan,
        private_key_path=args.private_key,
        signed_license_path=Path(args.signed_license) if args.signed_license else None,
        delivery_manifest_path=Path(args.delivery_manifest) if args.delivery_manifest else None,
        support_email=args.support_email,
        confirm_license_imported=args.confirm_license_imported,
        allow_no_go_rc=args.allow_no_go_commercial_rc,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
