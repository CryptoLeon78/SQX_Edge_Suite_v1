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
DEFAULT_OUTPUT_DIR = TOOL_ROOT / "data" / "checkout_live_readiness"
DEFAULT_PURCHASE_DRILL_DIR = PROJECT_ROOT / "backend" / "sqx-edge-relay" / "data" / "render_staging_purchase_drill"
REQUIRED_VARIANTS = ("pro_monthly", "pro_annual", "setup_assist")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_purchase_drill_file(directory: Path = DEFAULT_PURCHASE_DRILL_DIR) -> Path | None:
    files = sorted(directory.glob("render_staging_purchase_drill_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def is_https_url(value: str) -> bool:
    return bool(re.match(r"^https://[A-Za-z0-9.-]+(?:/.*)?$", value.strip()))


def is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def checkout_data(manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest.get("upgrade", {}).get("checkout", {})


def variant_map(checkout: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("plan") or ""): item for item in checkout.get("variants", []) if isinstance(item, dict)}


def build_public_urls(checkout: dict[str, Any], relay_base_url: str) -> dict[str, str]:
    base = relay_base_url.rstrip("/")
    return {
        "checkout_primary": str(checkout.get("primaryUrl") or checkout.get("primaryUrl") or "").strip(),
        "checkout_fallback": str(checkout.get("fallbackUrl") or "").strip(),
        "lemon_webhook": f"{base}/relay/webhook/lemon" if base else "",
        "relay_health": f"{base}/relay/health" if base else "",
        "relay_config_check": f"{base}/relay/config-check" if base else "",
    }


def rollback_steps() -> list[str]:
    return [
        "Disable or unpublish Lemon Squeezy checkout links.",
        "Remove or pause Lemon webhook delivery to /relay/webhook/lemon.",
        "Pause the Render relay worker service.",
        "Inspect /relay/queue and requeue or resolve failed items manually.",
        "Keep manual signed-license fulfillment available as fallback.",
        "Rotate SQX_LEMON_WEBHOOK_SECRET if any webhook secret was exposed.",
    ]


def decision_from(
    checkout: dict[str, Any],
    variants: dict[str, dict[str, Any]],
    public_urls: dict[str, str],
    support_email: str,
    purchase_drill: dict[str, Any] | None,
    require_purchase_drill_go: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if checkout.get("primaryProvider") != "Lemon Squeezy":
        blockers.append("primary_provider_not_lemon_squeezy")
    if checkout.get("mode") != "hosted_checkout":
        blockers.append("checkout_mode_not_hosted_checkout")
    if checkout.get("fulfillmentMode") not in ("manual_signed_license", "trusted_remote_relay_signed_bundle"):
        blockers.append("unsupported_fulfillment_mode")
    if not is_https_url(public_urls["checkout_primary"]):
        blockers.append("primary_checkout_url_missing_or_not_https")
    if public_urls["checkout_fallback"] and not is_https_url(public_urls["checkout_fallback"]):
        blockers.append("fallback_checkout_url_not_https")
    if not is_https_url(public_urls["lemon_webhook"]):
        blockers.append("relay_public_webhook_url_missing_or_not_https")
    if not is_email(support_email):
        blockers.append("support_email_missing_or_invalid")

    for plan in REQUIRED_VARIANTS:
        variant = variants.get(plan)
        if not variant:
            blockers.append(f"{plan}_variant_missing")
            continue
        if not str(variant.get("providerVariantId") or "").strip():
            blockers.append(f"{plan}_provider_variant_id_missing")
        if not str(variant.get("price") or "").strip():
            blockers.append(f"{plan}_price_missing")
        if not int(variant.get("licenseDurationDays") or 0):
            blockers.append(f"{plan}_license_duration_missing")

    if purchase_drill is None:
        blockers.append("render_staging_purchase_drill_missing")
    elif require_purchase_drill_go and not purchase_drill.get("decision", {}).get("go"):
        blockers.append("render_staging_purchase_drill_not_go")
        blockers.extend(purchase_drill.get("decision", {}).get("blockers", []))

    if checkout.get("status") == "pending_provider_urls":
        warnings.append("checkout_status_pending_provider_urls")
    if checkout.get("fulfillmentMode") == "manual_signed_license":
        warnings.append("manual_fulfillment_still_configured")

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
        "# SQX Edge Checkout Live Readiness",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Manifest: `{report['manifest_path']}`",
        f"- Purchase drill source: `{report.get('purchase_drill_source') or 'none'}`",
        "",
        "## Public URLs",
    ]
    lines.extend(f"- `{key}`: `{value or 'not configured'}`" for key, value in report["public_urls"].items())
    lines.append("")
    lines.append("## Variants")
    for plan, variant in report["variants"].items():
        lines.append(
            f"- `{plan}`: providerVariantId=`{variant.get('providerVariantId') or 'missing'}`, "
            f"price=`{variant.get('price') or 'missing'}`, billing=`{variant.get('billing') or 'missing'}`"
        )
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.append("")
    lines.append("## Rollback")
    lines.extend(f"- {item}" for item in report["rollback_steps"])
    return "\n".join(lines) + "\n"


def write_readiness(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"checkout_live_readiness_{current_stamp}.json"
    md_path = output_dir / f"checkout_live_readiness_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_readiness(
    manifest_path: Path = DEFAULT_MANIFEST,
    relay_base_url: str = "",
    support_email: str = "",
    purchase_drill_file: Path | None = None,
    require_purchase_drill_go: bool = True,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    checkout = checkout_data(manifest)
    variants = variant_map(checkout)
    support = support_email or str(checkout.get("supportEmail") or "").strip()
    public_urls = build_public_urls(checkout, relay_base_url)
    purchase_drill = load_json(purchase_drill_file) if purchase_drill_file else None
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "provider": "Lemon Squeezy",
        "checkout_status": checkout.get("status"),
        "support_email": support,
        "public_urls": public_urls,
        "variants": {plan: variants.get(plan, {}) for plan in REQUIRED_VARIANTS},
        "purchase_drill_source": str(purchase_drill_file) if purchase_drill_file else "",
        "purchase_drill_decision": purchase_drill.get("decision") if purchase_drill else None,
        "rollback_steps": rollback_steps(),
        "decision": decision_from(checkout, variants, public_urls, support, purchase_drill, require_purchase_drill_go),
    }
    if write:
        report["evidence_paths"] = write_readiness(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge checkout live readiness gate")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--relay-base-url", default=env_value("SQX_RELAY_PUBLIC_BASE_URL", env_value("SQX_RELAY_STAGING_BASE_URL")))
    parser.add_argument("--support-email", default=env_value("SQX_SUPPORT_EMAIL"))
    parser.add_argument("--purchase-drill-file", default="")
    parser.add_argument("--use-latest-purchase-drill", action="store_true")
    parser.add_argument("--allow-no-go-purchase-drill", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    purchase_drill_file = Path(args.purchase_drill_file) if args.purchase_drill_file else None
    if args.use_latest_purchase_drill and purchase_drill_file is None:
        purchase_drill_file = latest_purchase_drill_file()
        if purchase_drill_file is None:
            print(json.dumps({"ok": False, "error": "render_staging_purchase_drill_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_readiness(
        manifest_path=Path(args.manifest),
        relay_base_url=args.relay_base_url,
        support_email=args.support_email,
        purchase_drill_file=purchase_drill_file,
        require_purchase_drill_go=not args.allow_no_go_purchase_drill,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
