from __future__ import annotations

import argparse
import json
import os
import re
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_CONFIG = TOOL_ROOT / "config" / "template_pack_2_publication.json"
DEFAULT_MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"
DEFAULT_OUTPUT = TOOL_ROOT / "data" / "template_pack_2_publication"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def env_value(name: str) -> str:
    return os.environ.get(name, "").strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def project_path(rel_path: str) -> Path:
    return PROJECT_ROOT / rel_path


def is_https_url(value: str) -> bool:
    return bool(re.match(r"^https://[A-Za-z0-9.-]+(?:/.*)?$", value.strip()))


def is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))


def looks_placeholder(value: str, forbidden: list[str]) -> bool:
    lower = value.lower()
    return any(item.lower() in lower for item in forbidden)


def variant_for(manifest: dict[str, Any], plan: str) -> dict[str, Any] | None:
    variants = manifest.get("upgrade", {}).get("checkout", {}).get("variants", [])
    for variant in variants:
        if variant.get("plan") == plan:
            return variant
    return None


def validate_required_files(config: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for item in config.get("requiredFiles", []):
        if not project_path(str(item)).is_file():
            findings.append(f"missing_required_file:{item}")
    return findings


def validate_dependency(config: dict[str, Any]) -> list[str]:
    depends_on = config.get("dependsOn") if isinstance(config.get("dependsOn"), dict) else {}
    offer_path = project_path(str(depends_on.get("offerPackConfig", "")))
    assets_path = project_path(str(depends_on.get("assetsConfig", "")))
    findings: list[str] = []
    if not offer_path.is_file():
        findings.append("template_pack_2_offer_pack_config_missing")
    else:
        offer = load_json(offer_path)
        if offer.get("state") != depends_on.get("offerPackState"):
            findings.append("template_pack_2_offer_pack_state_invalid")
    if not assets_path.is_file():
        findings.append("template_pack_2_assets_config_missing")
    else:
        assets = load_json(assets_path)
        if assets.get("state") != depends_on.get("assetsState"):
            findings.append("template_pack_2_assets_state_invalid")
    return findings


def checkout_values_from_args_or_env(config: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    env = config.get("env", {}) if isinstance(config.get("env"), dict) else {}
    return {
        "checkout_url": args.checkout_url.strip() or env_value(str(env.get("checkoutUrl", ""))),
        "fallback_url": args.fallback_url.strip() or env_value(str(env.get("fallbackUrl", ""))),
        "provider_variant_id": args.provider_variant_id.strip() or env_value(str(env.get("providerVariantId", ""))),
        "support_email": args.support_email.strip() or env_value(str(env.get("supportEmail", ""))),
    }


def validate_values(config: dict[str, Any], manifest: dict[str, Any], values: dict[str, str]) -> list[str]:
    findings: list[str] = []
    forbidden = config.get("forbiddenPlaceholders") if isinstance(config.get("forbiddenPlaceholders"), list) else []
    checkout_url = values["checkout_url"]
    fallback_url = values["fallback_url"]
    provider_variant_id = values["provider_variant_id"]
    support_email = values["support_email"]

    if not is_https_url(checkout_url):
        findings.append("checkout_url_missing_or_not_https")
    elif looks_placeholder(checkout_url, forbidden):
        findings.append("checkout_url_looks_placeholder")

    if fallback_url:
        if not is_https_url(fallback_url):
            findings.append("fallback_url_not_https")
        elif looks_placeholder(fallback_url, forbidden):
            findings.append("fallback_url_looks_placeholder")

    if not provider_variant_id:
        findings.append("provider_variant_id_missing")
    elif len(provider_variant_id) < 5 or looks_placeholder(provider_variant_id, forbidden):
        findings.append("provider_variant_id_looks_placeholder")

    if not is_email(support_email):
        findings.append("support_email_missing_or_invalid")
    elif looks_placeholder(support_email, forbidden):
        findings.append("support_email_looks_placeholder")

    variant = variant_for(manifest, str(config.get("offerId", "template_pack_2")))
    if variant is None:
        findings.append("template_pack_2_variant_missing")
    else:
        if variant.get("price") != config.get("price"):
            findings.append("template_pack_2_price_mismatch")
        if variant.get("billing") != "one_time_addon":
            findings.append("template_pack_2_billing_invalid")
    return findings


def apply_publication_values(
    manifest: dict[str, Any],
    config: dict[str, Any],
    values: dict[str, str],
    applied_at: str,
) -> dict[str, Any]:
    updated = deepcopy(manifest)
    upgrade = updated.setdefault("upgrade", {})
    checkout = upgrade.setdefault("checkout", {})
    offer_id = str(config.get("offerId", "template_pack_2"))
    live_status = str(config.get("liveStatusWhenApplied", "template_pack_2_controlled_publication_live"))

    checkout["status"] = live_status
    checkout["supportEmail"] = values["support_email"]
    checkout["templatePack2LiveCheckout"] = {
        "status": live_status,
        "publicationId": config.get("publicationId"),
        "publicationMode": config.get("publicationMode"),
        "firstSaleCap": config.get("firstSaleCap"),
        "provider": config.get("primaryProvider"),
        "fallbackProvider": config.get("fallbackProvider"),
        "checkoutUrl": values["checkout_url"],
        "fallbackUrl": values["fallback_url"],
        "providerVariantId": values["provider_variant_id"],
        "supportEmail": values["support_email"],
        "rollbackPolicy": checkout.get("rollbackPolicy", "disable_checkout_pause_webhook_pause_worker_manual_fulfillment"),
        "updatedAt": applied_at,
    }
    checkout.setdefault("automation", {})["status"] = live_status

    for plan in upgrade.get("plans", []):
        if plan.get("id") == offer_id:
            plan["checkoutUrl"] = values["checkout_url"]

    variant = variant_for(updated, offer_id)
    if variant is not None:
        variant["providerVariantId"] = values["provider_variant_id"]
    return updated


def decision_from(
    config: dict[str, Any],
    manifest: dict[str, Any],
    values: dict[str, str],
    confirmations: dict[str, bool],
    apply_requested: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for key, value in confirmations.items():
        if not value:
            blockers.append(f"{key}_not_confirmed")

    blockers.extend(validate_required_files(config))
    blockers.extend(validate_dependency(config))
    blockers.extend(validate_values(config, manifest, values))

    if not apply_requested:
        warnings.append("apply_not_requested_manifest_left_unchanged")

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
        "# Template Pack 2 Controlled Publication Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- State: `{report['state']}`",
        f"- Decision: `{decision['label']}`",
        f"- Apply requested: `{report['apply_requested']}`",
        f"- Manifest path: `{report['manifest_path']}`",
        "",
        "## Values",
        f"- Checkout URL: `{values.get('checkout_url') or 'missing'}`",
        f"- Fallback URL: `{values.get('fallback_url') or 'not configured'}`",
        f"- Provider variant ID: `{values.get('provider_variant_id') or 'missing'}`",
        f"- Support email: `{values.get('support_email') or 'missing'}`",
        "",
        "## Purchase Drill Checklist",
    ]
    lines.extend(f"- {item}" for item in report["purchase_drill_checklist"])
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
    lines.append("")
    lines.append("## Applied Manifest")
    lines.append(f"- `{report.get('applied_manifest_path') or 'not applied'}`")
    return "\n".join(lines) + "\n"


def write_evidence(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"template_pack_2_publication_{current_stamp}.json"
    md_path = output_dir / f"template_pack_2_publication_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_publication(
    config_path: Path,
    manifest_path: Path,
    values: dict[str, str],
    confirmations: dict[str, bool],
    apply_requested: bool,
    manifest_output: Path | None,
    output_dir: Path,
    write: bool,
) -> dict[str, Any]:
    config = load_json(config_path)
    manifest = load_json(manifest_path)
    created_at = now_iso()
    decision = decision_from(config, manifest, values, confirmations, apply_requested)
    applied_manifest_path = ""

    if apply_requested and decision["go"]:
        target = manifest_output or manifest_path
        updated = apply_publication_values(manifest, config, values, created_at)
        write_json(target, updated)
        applied_manifest_path = str(target)

    report: dict[str, Any] = {
        "created_at": created_at,
        "state": config.get("state", "template_pack_2_controlled_publication_ready"),
        "config_path": str(config_path),
        "manifest_path": str(manifest_path),
        "apply_requested": apply_requested,
        "applied_manifest_path": applied_manifest_path,
        "values": values,
        "purchase_drill_checklist": config.get("purchaseDrillChecklist", []),
        "confirmations": confirmations,
        "decision": decision,
    }
    if write:
        report["evidence_paths"] = write_evidence(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and optionally apply Template Pack 2 controlled publication values.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--checkout-url", default="")
    parser.add_argument("--fallback-url", default="")
    parser.add_argument("--provider-variant-id", default="")
    parser.add_argument("--support-email", default="")
    parser.add_argument("--confirm-offer-pack-reviewed", action="store_true")
    parser.add_argument("--confirm-checkout-url-tested", action="store_true")
    parser.add_argument("--confirm-provider-variant-confirmed", action="store_true")
    parser.add_argument("--confirm-support-inbox-ready", action="store_true")
    parser.add_argument("--confirm-delivery-macro-ready", action="store_true")
    parser.add_argument("--confirm-rollback-ready", action="store_true")
    parser.add_argument("--confirm-purchase-drill-ready", action="store_true")
    parser.add_argument("--confirm-controlled-publication-approved", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--manifest-output", default="")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    values = checkout_values_from_args_or_env(config, args)
    confirmations = {
        "offer_pack_reviewed": args.confirm_offer_pack_reviewed,
        "checkout_url_tested": args.confirm_checkout_url_tested,
        "provider_variant_confirmed": args.confirm_provider_variant_confirmed,
        "support_inbox_ready": args.confirm_support_inbox_ready,
        "delivery_macro_ready": args.confirm_delivery_macro_ready,
        "rollback_ready": args.confirm_rollback_ready,
        "purchase_drill_ready": args.confirm_purchase_drill_ready,
        "controlled_publication_approved": args.confirm_controlled_publication_approved,
    }
    report = collect_publication(
        config_path=Path(args.config),
        manifest_path=Path(args.manifest),
        values=values,
        confirmations=confirmations,
        apply_requested=args.apply,
        manifest_output=Path(args.manifest_output) if args.manifest_output else None,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
