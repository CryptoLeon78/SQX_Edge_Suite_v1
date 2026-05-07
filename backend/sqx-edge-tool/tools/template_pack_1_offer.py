from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_1_offer.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_1_offer"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def forbidden_hits(text: str, forbidden: list[str]) -> list[str]:
    lower = text.lower()
    return [item for item in forbidden if item.lower() in lower]


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    forbidden = config.get("forbiddenClaims") if isinstance(config.get("forbiddenClaims"), list) else []
    for item in config.get("requiredFiles", []):
        path = project_path(str(item))
        if not path.is_file():
            findings.append(f"missing_required_file:{item}")
            continue
        hits = forbidden_hits(read_text(path), forbidden)
        findings.extend(f"forbidden_claim:{item}:{hit}" for hit in hits)
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    pack_path = project_path(str(depends_on.get("templatePackConfig", "")))
    expected_state = depends_on.get("templatePackState")
    if not pack_path.is_file():
        return ["template_pack_1_config_missing"]
    pack = load_json(pack_path)
    if pack.get("state") != expected_state:
        return ["template_pack_1_state_invalid"]
    return []


def validate_offer_fields(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    offer_path = project_path("resources/pro-template-pack-1/offer/public_offer.md")
    if not offer_path.is_file():
        return ["template_pack_1_public_offer_missing"]
    text = read_text(offer_path).lower()
    for field in config.get("requiredOfferFields", []):
        label = re.sub(r"(?<!^)([A-Z])", r" \1", str(field)).lower()
        if label not in text:
            findings.append(f"offer_field_missing:{field}")
    return findings


def variant_for(manifest: dict[str, Any], plan: str) -> dict[str, Any] | None:
    variants = manifest.get("upgrade", {}).get("checkout", {}).get("variants", [])
    for variant in variants:
        if variant.get("plan") == plan:
            return variant
    return None


def is_https_url(value: str) -> bool:
    return value.startswith("https://") and "." in value


def emailish(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


def validate_checkout_wiring(
    config: dict[str, Any],
    manifest: dict[str, Any],
    checkout_url: str,
    provider_variant_id: str,
    support_email: str,
    require_live_checkout: bool,
) -> list[str]:
    findings: list[str] = []
    plan = str(config.get("offerId", "template_pack_1"))
    variant = variant_for(manifest, plan)
    if variant is None:
        findings.append("template_pack_1_variant_missing")
    else:
        if variant.get("price") != config.get("price"):
            findings.append("template_pack_1_price_mismatch")
        if variant.get("billing") != "one_time_addon":
            findings.append("template_pack_1_billing_invalid")
        provider_variant_id = provider_variant_id or str(variant.get("providerVariantId", "")).strip()

    checkout = manifest.get("upgrade", {}).get("checkout", {})
    checkout_url = checkout_url or str(checkout.get("primaryUrl", "")).strip()
    support_email = support_email or str(checkout.get("supportEmail", "")).strip()

    if require_live_checkout:
        if not is_https_url(checkout_url):
            findings.append("checkout_url_missing_or_not_https")
        if not provider_variant_id:
            findings.append("provider_variant_id_missing")
        if not emailish(support_email):
            findings.append("support_email_missing_or_invalid")
    return findings


def decision_from(
    config: dict[str, Any],
    manifest: dict[str, Any],
    template_pack_delivery_ready: bool,
    offer_copy_reviewed: bool,
    faq_reviewed: bool,
    checkout_draft_ready: bool,
    delivery_macro_ready: bool,
    support_macro_ready: bool,
    safe_claims_reviewed: bool,
    checkout_url: str,
    provider_variant_id: str,
    support_email: str,
    require_live_checkout: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not template_pack_delivery_ready:
        blockers.append("template_pack_delivery_not_ready")
    if not offer_copy_reviewed:
        blockers.append("offer_copy_not_reviewed")
    if not faq_reviewed:
        blockers.append("faq_not_reviewed")
    if not checkout_draft_ready:
        blockers.append("checkout_draft_not_ready")
    if not delivery_macro_ready:
        blockers.append("delivery_macro_not_ready")
    if not support_macro_ready:
        blockers.append("support_macro_not_ready")
    if not safe_claims_reviewed:
        blockers.append("safe_claims_not_reviewed")
    if not require_live_checkout:
        warnings.append("live_checkout_not_required_for_draft")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_offer_fields(config))
    blockers.extend(validate_checkout_wiring(config, manifest, checkout_url, provider_variant_id, support_email, require_live_checkout))
    if any(item.startswith("forbidden_claim:") for item in blockers):
        blockers.append("forbidden_claims_present")

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
        "# Template Pack 1 Public Offer Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Require live checkout: `{report['require_live_checkout']}`",
        f"- Checkout URL: `{report.get('checkout_url') or 'draft'}`",
        f"- Provider variant ID: `{report.get('provider_variant_id') or 'draft'}`",
        f"- Support email: `{report.get('support_email') or 'draft'}`",
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
    json_path = output_dir / f"template_pack_1_offer_{current_stamp}.json"
    md_path = output_dir / f"template_pack_1_offer_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_offer(
    config_path: Path = DEFAULT_CONFIG,
    manifest_path: Path = DEFAULT_MANIFEST,
    template_pack_delivery_ready: bool = False,
    offer_copy_reviewed: bool = False,
    faq_reviewed: bool = False,
    checkout_draft_ready: bool = False,
    delivery_macro_ready: bool = False,
    support_macro_ready: bool = False,
    safe_claims_reviewed: bool = False,
    checkout_url: str = "",
    provider_variant_id: str = "",
    support_email: str = "",
    require_live_checkout: bool = False,
    output_dir: Path = DEFAULT_OUTPUT,
    write: bool = True,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    confirmations = {
        "template_pack_delivery_ready": template_pack_delivery_ready,
        "offer_copy_reviewed": offer_copy_reviewed,
        "faq_reviewed": faq_reviewed,
        "checkout_draft_ready": checkout_draft_ready,
        "delivery_macro_ready": delivery_macro_ready,
        "support_macro_ready": support_macro_ready,
        "safe_claims_reviewed": safe_claims_reviewed,
    }
    report: dict[str, Any] = {
        "created_at": now_iso(),
        "state": config.get("state", "template_pack_1_public_offer_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "offer_id": config.get("offerId"),
        "price": config.get("price"),
        "checkout_mode": config.get("checkoutMode"),
        "require_live_checkout": require_live_checkout,
        "checkout_url": checkout_url,
        "provider_variant_id": provider_variant_id,
        "support_email": support_email,
        "confirmations": confirmations,
        "decision": decision_from(
            config,
            manifest,
            template_pack_delivery_ready,
            offer_copy_reviewed,
            faq_reviewed,
            checkout_draft_ready,
            delivery_macro_ready,
            support_macro_ready,
            safe_claims_reviewed,
            checkout_url,
            provider_variant_id,
            support_email,
            require_live_checkout,
        ),
    }
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Template Pack 1 public add-on offer and checkout wiring.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--confirm-template-pack-delivery-ready", action="store_true")
    parser.add_argument("--confirm-offer-copy-reviewed", action="store_true")
    parser.add_argument("--confirm-faq-reviewed", action="store_true")
    parser.add_argument("--confirm-checkout-draft-ready", action="store_true")
    parser.add_argument("--confirm-delivery-macro-ready", action="store_true")
    parser.add_argument("--confirm-support-macro-ready", action="store_true")
    parser.add_argument("--confirm-safe-claims-reviewed", action="store_true")
    parser.add_argument("--checkout-url", default="")
    parser.add_argument("--provider-variant-id", default="")
    parser.add_argument("--support-email", default="")
    parser.add_argument("--require-live-checkout", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_offer(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        template_pack_delivery_ready=args.confirm_template_pack_delivery_ready,
        offer_copy_reviewed=args.confirm_offer_copy_reviewed,
        faq_reviewed=args.confirm_faq_reviewed,
        checkout_draft_ready=args.confirm_checkout_draft_ready,
        delivery_macro_ready=args.confirm_delivery_macro_ready,
        support_macro_ready=args.confirm_support_macro_ready,
        safe_claims_reviewed=args.confirm_safe_claims_reviewed,
        checkout_url=args.checkout_url,
        provider_variant_id=args.provider_variant_id,
        support_email=args.support_email,
        require_live_checkout=args.require_live_checkout,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
