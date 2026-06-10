from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import (
    ENTITLEMENTS_SCHEMA_VERSION,
    FULL_FEATURE_SCOPE,
    email_hash,
    entitlement_store_path,
    load_entitlement_store,
    normalize_email,
    redact_email,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_PAYMENT_WEBHOOK_VERSION = "remote-payment-webhook-v1"
PAYMENT_WEBHOOK_SECRET_ENV = "SQX_REMOTE_PAYMENT_WEBHOOK_SECRET"
DEFAULT_PAYMENT_AUDIT_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_payment_webhook_events.local.jsonl"

ACTIVE_EVENTS = {"subscription_activated", "subscription_created", "subscription_renewed", "subscription_resumed", "order_paid"}
CANCELLED_EVENTS = {"subscription_cancelled", "subscription_canceled"}
EXPIRED_EVENTS = {"subscription_expired"}
BLOCKED_EVENTS = {"subscription_refunded", "subscription_chargeback", "subscription_blocked"}
SUPPORTED_EVENTS = ACTIVE_EVENTS | CANCELLED_EVENTS | EXPIRED_EVENTS | BLOCKED_EVENTS


def webhook_secret() -> str:
    return os.environ.get(PAYMENT_WEBHOOK_SECRET_ENV, "").strip()


def webhook_secret_ready(secret: str | None = None) -> bool:
    return len((secret if secret is not None else webhook_secret()).strip()) >= 32


def sign_payment_webhook_body(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def verify_payment_webhook_signature(raw_body: bytes, signature: str | None, secret: str | None = None) -> dict[str, Any]:
    configured_secret = (secret if secret is not None else webhook_secret()).strip()
    if not webhook_secret_ready(configured_secret):
        return {"ok": False, "error": "payment_webhook_secret_missing_or_short", "http_status": 503}
    supplied = (signature or "").strip()
    if supplied.startswith("sha256="):
        supplied = supplied.split("=", 1)[1].strip()
    if not supplied:
        return {"ok": False, "error": "payment_webhook_signature_missing", "http_status": 401}
    expected = sign_payment_webhook_body(raw_body, configured_secret)
    if not hmac.compare_digest(supplied.lower(), expected.lower()):
        return {"ok": False, "error": "payment_webhook_signature_invalid", "http_status": 401}
    return {"ok": True, "error": "", "http_status": 200}


def _event_status(event_type: str, payload_status: str = "") -> str | None:
    normalized = event_type.strip().lower()
    if normalized in ACTIVE_EVENTS:
        return "active"
    if normalized in CANCELLED_EVENTS:
        return "cancelled"
    if normalized in EXPIRED_EVENTS:
        return "expired"
    if normalized in BLOCKED_EVENTS:
        return "blocked"
    status = payload_status.strip().lower()
    if status in {"active", "cancelled", "canceled", "expired", "blocked"}:
        return "cancelled" if status == "canceled" else status
    return None


def _dig(mapping: Mapping[str, Any], *keys: str) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def normalize_payment_webhook_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    event_id = str(
        payload.get("eventId")
        or payload.get("event_id")
        or payload.get("id")
        or _dig(payload, "meta", "webhook_id")
        or ""
    ).strip()
    event_type = str(
        payload.get("eventType")
        or payload.get("event_type")
        or payload.get("type")
        or _dig(payload, "meta", "event_name")
        or ""
    ).strip().lower()
    email = normalize_email(
        str(
            payload.get("email")
            or payload.get("customerEmail")
            or payload.get("customer_email")
            or _dig(payload, "data", "attributes", "user_email")
            or _dig(payload, "data", "attributes", "customer_email")
            or _dig(payload, "data", "attributes", "email")
            or ""
        )
    )
    provider_status = str(payload.get("status") or _dig(payload, "data", "attributes", "status") or "")
    status = _event_status(event_type, provider_status)
    if not event_id:
        raise ValueError("payment_webhook_event_id_missing")
    if event_type not in SUPPORTED_EVENTS and status is None:
        raise ValueError("payment_webhook_event_type_unsupported")
    if not email:
        raise ValueError("payment_webhook_email_missing")
    return {
        "event_id": event_id,
        "event_type": event_type,
        "email_hash": email_hash(email),
        "email_ref": redact_email(email),
        "status": status or "active",
        "feature_scope": str(payload.get("featureScope") or payload.get("feature_scope") or FULL_FEATURE_SCOPE).strip() or FULL_FEATURE_SCOPE,
        "provider": str(payload.get("provider") or "remote_payment_webhook").strip(),
        "provider_customer_id": str(payload.get("customerId") or payload.get("customer_id") or _dig(payload, "data", "attributes", "customer_id") or "").strip(),
        "provider_subscription_id": str(payload.get("subscriptionId") or payload.get("subscription_id") or _dig(payload, "data", "id") or "").strip(),
        "expires_at": str(payload.get("expiresAt") or payload.get("expires_at") or _dig(payload, "data", "attributes", "renews_at") or "").strip() or None,
    }


def _processed_events(store: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = store.get("processedWebhookEvents") or []
    return [event for event in raw if isinstance(event, dict)]


def _event_already_processed(store: Mapping[str, Any], event_id: str) -> bool:
    return any(str(event.get("eventId") or "") == event_id for event in _processed_events(store))


def _upsert_paid_entitlement(store: dict[str, Any], event: Mapping[str, Any], now: str) -> dict[str, Any]:
    grants = store.setdefault("grants", [])
    if not isinstance(grants, list):
        grants = []
        store["grants"] = grants
    target_hash = str(event["email_hash"])
    paid_grant: dict[str, Any] | None = None
    for grant in grants:
        if not isinstance(grant, dict):
            continue
        if str(grant.get("emailHash") or grant.get("email_hash") or "").strip().lower() != target_hash:
            continue
        if str(grant.get("entitlementKind") or grant.get("entitlement_kind") or "") == "paid_subscription":
            paid_grant = grant
            break
    if paid_grant is None:
        paid_grant = {
            "emailHash": target_hash,
            "entitlementKind": "paid_subscription",
            "featureScope": event.get("feature_scope") or FULL_FEATURE_SCOPE,
            "source": "payment_webhook",
        }
        grants.append(paid_grant)
    paid_grant.update({
        "status": event["status"],
        "featureScope": event.get("feature_scope") or FULL_FEATURE_SCOPE,
        "source": "payment_webhook",
        "provider": event.get("provider"),
        "providerCustomerId": event.get("provider_customer_id"),
        "providerSubscriptionId": event.get("provider_subscription_id"),
        "lastWebhookEventId": event.get("event_id"),
        "updatedAt": now,
    })
    if event.get("expires_at"):
        paid_grant["expiresAt"] = event["expires_at"]
    elif "expiresAt" in paid_grant and event["status"] in {"cancelled", "expired", "blocked"}:
        paid_grant.pop("expiresAt", None)
    return paid_grant


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def _append_audit_event(payload: Mapping[str, Any], audit_path: Path | None = None) -> None:
    path = audit_path or DEFAULT_PAYMENT_AUDIT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def process_payment_webhook(
    raw_body: bytes,
    signature: str | None,
    store_path: Path | None = None,
    secret: str | None = None,
    audit_path: Path | None = None,
) -> dict[str, Any]:
    signature_result = verify_payment_webhook_signature(raw_body, signature, secret=secret)
    if not signature_result["ok"]:
        return {**signature_result, "version": REMOTE_PAYMENT_WEBHOOK_VERSION}
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"ok": False, "version": REMOTE_PAYMENT_WEBHOOK_VERSION, "error": "payment_webhook_payload_invalid", "http_status": 400}
    if not isinstance(payload, Mapping):
        return {"ok": False, "version": REMOTE_PAYMENT_WEBHOOK_VERSION, "error": "payment_webhook_payload_not_object", "http_status": 400}
    try:
        event = normalize_payment_webhook_payload(payload)
    except ValueError as exc:
        return {"ok": False, "version": REMOTE_PAYMENT_WEBHOOK_VERSION, "error": str(exc), "http_status": 400}

    path = store_path or entitlement_store_path()
    store = load_entitlement_store(path)
    if _event_already_processed(store, event["event_id"]):
        return {
            "ok": True,
            "version": REMOTE_PAYMENT_WEBHOOK_VERSION,
            "http_status": 200,
            "idempotent": True,
            "event": {"id": event["event_id"], "type": event["event_type"]},
            "entitlement": {"kind": "paid_subscription", "status": "unchanged"},
            "identity": {"email_ref": event["email_ref"], "email_hash": event["email_hash"]},
            "privacy": {"raw_email_returned": False, "webhook_secret_returned": False},
        }

    now = datetime.now(timezone.utc).isoformat()
    store.pop("source", None)
    store["schemaVersion"] = str(store.get("schemaVersion") or ENTITLEMENTS_SCHEMA_VERSION)
    grant = _upsert_paid_entitlement(store, event, now)
    processed = _processed_events(store)
    processed.append({
        "eventId": event["event_id"],
        "eventType": event["event_type"],
        "emailHash": event["email_hash"],
        "entitlementKind": "paid_subscription",
        "status": event["status"],
        "processedAt": now,
    })
    store["processedWebhookEvents"] = processed[-200:]
    store["updatedAt"] = now
    _write_json_atomic(path, store)
    audit_event = {
        "type": "remote_payment_webhook_processed",
        "version": REMOTE_PAYMENT_WEBHOOK_VERSION,
        "eventId": event["event_id"],
        "eventType": event["event_type"],
        "identityHash": event["email_hash"],
        "entitlementStatus": event["status"],
        "processedAt": now,
    }
    _append_audit_event(audit_event, audit_path=audit_path)
    return {
        "ok": True,
        "version": REMOTE_PAYMENT_WEBHOOK_VERSION,
        "http_status": 200,
        "idempotent": False,
        "event": {"id": event["event_id"], "type": event["event_type"]},
        "entitlement": {
            "kind": "paid_subscription",
            "status": grant.get("status"),
            "feature_scope": grant.get("featureScope"),
            "source": grant.get("source"),
        },
        "identity": {"email_ref": event["email_ref"], "email_hash": event["email_hash"]},
        "audit_event": audit_event,
        "privacy": {"raw_email_returned": False, "webhook_secret_returned": False},
    }
