from __future__ import annotations

import hashlib
import hmac
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
PRODUCT_MANIFEST_PATH = CONFIG_DIR / "product_manifest.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_product_manifest() -> dict[str, Any]:
    return _load_json(PRODUCT_MANIFEST_PATH)


def verify_lemon_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _manifest_variants(product: dict[str, Any]) -> list[dict[str, Any]]:
    checkout = product.get("upgrade", {}).get("checkout", {})
    return list(checkout.get("variants") or [])


def _plan_from_variant(product: dict[str, Any], variant_id: Any, variant_name: str = "") -> dict[str, Any]:
    variants = _manifest_variants(product)
    variant_id_text = str(variant_id or "").strip()
    variant_name_text = str(variant_name or "").lower()
    for variant in variants:
        provider_variant_id = str(variant.get("providerVariantId") or "").strip()
        if provider_variant_id and provider_variant_id == variant_id_text:
            return dict(variant)
    for variant in variants:
        label = str(variant.get("label") or "").lower()
        plan = str(variant.get("plan") or "").lower()
        if label and label in variant_name_text:
            return dict(variant)
        if plan and plan.replace("_", " ") in variant_name_text:
            return dict(variant)
    if "annual" in variant_name_text or "anual" in variant_name_text:
        return next((dict(v) for v in variants if v.get("plan") == "pro_annual"), {"plan": "pro_annual"})
    if "setup" in variant_name_text:
        return next((dict(v) for v in variants if v.get("plan") == "setup_assist"), {"plan": "setup_assist"})
    return next((dict(v) for v in variants if v.get("plan") == "pro_monthly"), {"plan": "pro_monthly"})


def _event_name(payload: dict[str, Any]) -> str:
    return str(payload.get("meta", {}).get("event_name") or payload.get("event_name") or "").strip()


def _data_and_attrs(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    data = dict(payload.get("data") or {})
    attrs = dict(data.get("attributes") or payload.get("attributes") or {})
    return data, attrs


def _first_order_item(attrs: dict[str, Any]) -> dict[str, Any]:
    return dict(attrs.get("first_order_item") or {})


def normalize_lemon_order(payload: dict[str, Any], product: dict[str, Any] | None = None, today: date | None = None) -> dict[str, Any]:
    manifest = product or load_product_manifest()
    current = today or date.today()
    data, attrs = _data_and_attrs(payload)
    item = _first_order_item(attrs)
    variant = _plan_from_variant(manifest, item.get("variant_id"), item.get("variant_name", ""))
    status = str(attrs.get("status") or "").lower()
    refunded = bool(attrs.get("refunded") or attrs.get("refunded_at"))
    eligible = status in {"paid", "created", ""} and not refunded
    order_id = str(attrs.get("identifier") or attrs.get("order_number") or data.get("id") or "")

    return {
        "schema_version": 1,
        "provider": "Lemon Squeezy",
        "source_event": _event_name(payload) or "order_created",
        "provider_event_id": str(payload.get("meta", {}).get("webhook_id") or data.get("id") or ""),
        "provider_order_id": str(data.get("id") or ""),
        "order_id": order_id,
        "customer_name": str(attrs.get("user_name") or "SQX Customer"),
        "customer_email": str(attrs.get("user_email") or ""),
        "customer_id": str(attrs.get("customer_id") or ""),
        "plan": str(variant.get("plan") or "pro_monthly"),
        "provider_variant_id": str(item.get("variant_id") or ""),
        "provider_variant_name": str(item.get("variant_name") or ""),
        "license_duration_days": int(variant.get("licenseDurationDays") or 31),
        "machine_limit": int(variant.get("activationLimit") or 1),
        "support_level": "priority" if variant.get("plan") == "setup_assist" else "standard",
        "status": status or "paid",
        "test_mode": bool(attrs.get("test_mode") or item.get("test_mode")),
        "receipt_url": str((attrs.get("urls") or {}).get("receipt") or ""),
        "eligible_for_fulfillment": eligible,
        "fulfillment_status": "ready_for_license" if eligible else "ignored",
        "generated_at": current.isoformat(),
    }


def normalize_lemon_subscription(payload: dict[str, Any], product: dict[str, Any] | None = None, today: date | None = None) -> dict[str, Any]:
    manifest = product or load_product_manifest()
    current = today or date.today()
    data, attrs = _data_and_attrs(payload)
    variant = _plan_from_variant(manifest, attrs.get("variant_id"), attrs.get("variant_name", ""))
    event = _event_name(payload) or "subscription_updated"
    status = str(attrs.get("status") or "").lower()
    eligible = event in {"subscription_created", "subscription_payment_success", "subscription_payment_recovered"} and status not in {"cancelled", "expired", "unpaid", "past_due"}

    return {
        "schema_version": 1,
        "provider": "Lemon Squeezy",
        "source_event": event,
        "provider_event_id": str(payload.get("meta", {}).get("webhook_id") or data.get("id") or ""),
        "provider_subscription_id": str(data.get("id") or ""),
        "order_id": str(attrs.get("order_id") or data.get("id") or ""),
        "customer_name": str(attrs.get("user_name") or attrs.get("customer_name") or "SQX Customer"),
        "customer_email": str(attrs.get("user_email") or attrs.get("customer_email") or ""),
        "customer_id": str(attrs.get("customer_id") or ""),
        "plan": str(variant.get("plan") or "pro_monthly"),
        "provider_variant_id": str(attrs.get("variant_id") or ""),
        "provider_variant_name": str(attrs.get("variant_name") or ""),
        "license_duration_days": int(variant.get("licenseDurationDays") or 31),
        "machine_limit": int(variant.get("activationLimit") or 1),
        "support_level": "standard",
        "status": status or "active",
        "renews_at": attrs.get("renews_at"),
        "ends_at": attrs.get("ends_at"),
        "test_mode": bool(attrs.get("test_mode")),
        "eligible_for_fulfillment": eligible,
        "fulfillment_status": "ready_for_license" if eligible else "accounting_only",
        "generated_at": current.isoformat(),
    }


def normalize_payload(payload: dict[str, Any], provider: str = "lemon", product: dict[str, Any] | None = None, today: date | None = None) -> dict[str, Any]:
    provider_name = provider.lower().strip()
    if provider_name not in {"lemon", "lemon_squeezy", "lemonsqueezy"}:
        raise ValueError(f"unsupported provider: {provider}")
    data, _attrs = _data_and_attrs(payload)
    data_type = str(data.get("type") or "").lower()
    event = _event_name(payload)
    if data_type == "subscriptions" or event.startswith("subscription_"):
        return normalize_lemon_subscription(payload, product=product, today=today)
    return normalize_lemon_order(payload, product=product, today=today)
