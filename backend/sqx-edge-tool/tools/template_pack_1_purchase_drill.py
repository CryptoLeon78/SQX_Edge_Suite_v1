from __future__ import annotations

import argparse
import json
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_1_purchase_drill.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_1_purchase_drill"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def is_https_url(value: str) -> bool:
    return bool(re.match(r"^https://[A-Za-z0-9.-]+(?:/.*)?$", value.strip()))


def is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def redact_email(value: str) -> str:
    if not is_email(value):
        return ""
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        redacted_local = local[0] + "***"
    else:
        redacted_local = f"{local[0]}***{local[-1]}"
    return f"{redacted_local}@{domain}"


def looks_placeholder(value: str, forbidden: list[str]) -> bool:
    lower = value.lower()
    return any(item.lower() in lower for item in forbidden)


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in config.get("requiredFiles", []):
        if not project_path(str(item)).is_file():
            findings.append(f"missing_required_file:{item}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    publication_path = project_path(str(depends_on.get("publicationConfig", "")))
    delivery_path = project_path(str(depends_on.get("deliveryConfig", "")))
    findings: list[str] = []

    if not publication_path.is_file():
        findings.append("template_pack_1_publication_config_missing")
    else:
        publication = load_json(publication_path)
        if publication.get("state") != depends_on.get("publicationState"):
            findings.append("template_pack_1_publication_state_invalid")

    if not delivery_path.is_file():
        findings.append("template_pack_1_delivery_config_missing")
    else:
        delivery = load_json(delivery_path)
        if delivery.get("state") != depends_on.get("deliveryState"):
            findings.append("template_pack_1_delivery_state_invalid")
    return findings


def checkout_variant(manifest: dict[str, Any], plan: str) -> dict[str, Any] | None:
    for variant in manifest.get("upgrade", {}).get("checkout", {}).get("variants", []):
        if variant.get("plan") == plan:
            return variant
    return None


def validate_manifest_variant(config: dict[str, Any], manifest: dict[str, Any], provider_variant_id: str) -> list[str]:
    findings: list[str] = []
    variant = checkout_variant(manifest, str(config.get("offerId", "template_pack_1")))
    if variant is None:
        return ["template_pack_1_variant_missing"]
    if variant.get("price") != config.get("price"):
        findings.append("template_pack_1_price_mismatch")
    if variant.get("billing") != config.get("billing"):
        findings.append("template_pack_1_billing_mismatch")
    manifest_variant_id = str(variant.get("providerVariantId") or "").strip()
    if manifest_variant_id and provider_variant_id and manifest_variant_id != provider_variant_id:
        findings.append("provider_variant_id_differs_from_manifest")
    return findings


def validate_delivery_package(path_value: str) -> list[str]:
    if not path_value:
        return ["delivery_package_path_missing"]
    path = Path(path_value)
    if not path.is_absolute():
        path = project_path(path_value)
    if not path.is_file():
        return ["delivery_package_missing"]
    if path.suffix.lower() != ".zip":
        return ["delivery_package_not_zip"]
    required_entries = (
        "pro-template-pack-1/README.md",
        "pro-template-pack-1/presets/strategy_import_template_pack_1.csv",
        "pro-template-pack-1/checklists/delivery_checklist.md",
        "pro-template-pack-1/checklists/support_boundaries.md",
    )
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
    return [f"delivery_package_missing_entry:{entry}" for entry in required_entries if entry not in names]


def validate_values(config: dict[str, Any], manifest: dict[str, Any], values: dict[str, str], require_delivery_package: bool) -> list[str]:
    findings: list[str] = []
    forbidden = config.get("forbiddenPlaceholders") if isinstance(config.get("forbiddenPlaceholders"), list) else []
    allowed_statuses = {str(item).lower() for item in config.get("allowedPaymentStatuses", [])}

    if not is_https_url(values["checkout_url"]):
        findings.append("checkout_url_missing_or_not_https")
    elif looks_placeholder(values["checkout_url"], forbidden):
        findings.append("checkout_url_looks_placeholder")

    if not values["provider_variant_id"]:
        findings.append("provider_variant_id_missing")
    elif looks_placeholder(values["provider_variant_id"], forbidden):
        findings.append("provider_variant_id_looks_placeholder")

    if not values["provider_order_id"]:
        findings.append("provider_order_id_missing")
    elif looks_placeholder(values["provider_order_id"], forbidden):
        findings.append("provider_order_id_looks_placeholder")

    if not is_email(values["buyer_email"]):
        findings.append("buyer_email_missing_or_invalid")

    if values["payment_status"].lower() not in allowed_statuses:
        findings.append("payment_status_not_paid")
    if values["amount"] != str(config.get("amount")):
        findings.append("amount_mismatch")
    if values["currency"].upper() != str(config.get("currency")):
        findings.append("currency_mismatch")

    findings.extend(validate_manifest_variant(config, manifest, values["provider_variant_id"]))
    if require_delivery_package:
        findings.extend(validate_delivery_package(values["delivery_package_path"]))
    return findings


def decision_from(
    config: dict[str, Any],
    manifest: dict[str, Any],
    values: dict[str, str],
    confirmations: dict[str, bool],
    require_delivery_package: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    if not require_delivery_package:
        warnings.append("delivery_package_content_not_verified")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_values(config, manifest, values, require_delivery_package))

    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    values = report["values"]
    lines = [
        "# Template Pack 1 Controlled Purchase Drill Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Provider: `{values.get('provider')}`",
        f"- Order: `{values.get('provider_order_id') or 'missing'}`",
        f"- Buyer: `{values.get('buyer_email_redacted') or 'missing'}`",
        f"- Payment: `{values.get('payment_status') or 'missing'}` `{values.get('amount')}` `{values.get('currency')}`",
        f"- Delivery package: `{values.get('delivery_package_path') or 'missing'}`",
        "",
        "## Confirmations",
    ]
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
    json_path = output_dir / f"template_pack_1_purchase_drill_{current_stamp}.json"
    md_path = output_dir / f"template_pack_1_purchase_drill_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_purchase_drill(
    config_path: Path,
    manifest_path: Path,
    values: dict[str, str],
    confirmations: dict[str, bool],
    require_delivery_package: bool,
    output_dir: Path,
    write: bool,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    safe_values = dict(values)
    safe_values["buyer_email_redacted"] = redact_email(values.get("buyer_email", ""))
    safe_values["buyer_email"] = ""
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_1_purchase_drill_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "require_delivery_package": require_delivery_package,
        "values": safe_values,
        "confirmations": confirmations,
        "decision": decision_from(config, manifest, values, confirmations, require_delivery_package),
    }
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a controlled purchase drill for Template Pack 1.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--provider", default="Lemon Squeezy")
    parser.add_argument("--checkout-url", default="")
    parser.add_argument("--provider-variant-id", default="")
    parser.add_argument("--provider-order-id", default="")
    parser.add_argument("--buyer-email", default="")
    parser.add_argument("--payment-status", default="")
    parser.add_argument("--amount", default="")
    parser.add_argument("--currency", default="EUR")
    parser.add_argument("--delivery-package-path", default="")
    parser.add_argument("--confirm-live-checkout-values-confirmed", action="store_true")
    parser.add_argument("--confirm-controlled-purchase-paid", action="store_true")
    parser.add_argument("--confirm-provider-order-recorded", action="store_true")
    parser.add_argument("--confirm-delivery-package-ready", action="store_true")
    parser.add_argument("--confirm-delivery-email-ready", action="store_true")
    parser.add_argument("--confirm-support-inbox-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--confirm-refund-or-pause-ready", action="store_true")
    parser.add_argument("--require-delivery-package", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    values = {
        "provider": args.provider.strip(),
        "checkout_url": args.checkout_url.strip(),
        "provider_variant_id": args.provider_variant_id.strip(),
        "provider_order_id": args.provider_order_id.strip(),
        "buyer_email": args.buyer_email.strip(),
        "payment_status": args.payment_status.strip(),
        "amount": args.amount.strip(),
        "currency": args.currency.strip(),
        "delivery_package_path": args.delivery_package_path.strip(),
    }
    confirmations = {
        "live_checkout_values_confirmed": args.confirm_live_checkout_values_confirmed,
        "controlled_purchase_paid": args.confirm_controlled_purchase_paid,
        "provider_order_recorded": args.confirm_provider_order_recorded,
        "delivery_package_ready": args.confirm_delivery_package_ready,
        "delivery_email_ready": args.confirm_delivery_email_ready,
        "support_inbox_ready": args.confirm_support_inbox_ready,
        "safe_claims_reviewed": args.confirm_safe_claims_reviewed,
        "refund_or_pause_ready": args.confirm_refund_or_pause_ready,
    }
    report = collect_purchase_drill(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        values=values,
        confirmations=confirmations,
        require_delivery_package=args.require_delivery_package,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
