from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_ACCESS_VERSION = "remote-access-v1"
ENTITLEMENTS_SCHEMA_VERSION = "remote-entitlements-v1"
DEFAULT_ENTITLEMENTS_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_entitlements.local.json"

VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}
VALID_ENTITLEMENT_STATUSES = {"active", "pending", "expired", "denied", "blocked", "cancelled"}
FULL_FEATURE_SCOPE = "full"
RESTRICTED_FEATURE_SCOPE = "restricted"
EMAIL_HEADERS = (
    "Cf-Access-Authenticated-User-Email",
    "Cf-Access-Jwt-Assertion-Email",
    "X-SQX-Authenticated-Email",
)


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def email_hash(value: str | None) -> str:
    normalized = normalize_email(value)
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def redact_email(value: str | None) -> str | None:
    normalized = normalize_email(value)
    if not normalized or "@" not in normalized:
        return None
    name, domain = normalized.split("@", 1)
    prefix = name[:2] if len(name) >= 2 else name[:1]
    return f"{prefix}***@{domain}"


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None


def _today(current: date | None = None) -> date:
    return current or date.today()


def entitlement_store_path() -> Path:
    configured = os.environ.get("SQX_REMOTE_ENTITLEMENTS_PATH", "").strip()
    return Path(configured).expanduser().resolve(strict=False) if configured else DEFAULT_ENTITLEMENTS_PATH


def load_entitlement_store(path: Path | None = None) -> dict[str, Any]:
    source = path or entitlement_store_path()
    if not source.is_file():
        return {
            "schemaVersion": ENTITLEMENTS_SCHEMA_VERSION,
            "grants": [],
            "source": "missing_local_store",
        }
    try:
        payload = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {
            "schemaVersion": ENTITLEMENTS_SCHEMA_VERSION,
            "grants": [],
            "source": "unreadable_local_store",
        }
    if not isinstance(payload, dict):
        return {
            "schemaVersion": ENTITLEMENTS_SCHEMA_VERSION,
            "grants": [],
            "source": "invalid_local_store",
        }
    grants = payload.get("grants") if isinstance(payload.get("grants"), list) else []
    return {
        **payload,
        "schemaVersion": str(payload.get("schemaVersion") or ENTITLEMENTS_SCHEMA_VERSION),
        "grants": [grant for grant in grants if isinstance(grant, dict)],
        "source": "local_store",
    }


def trusted_email_from_headers(headers: Mapping[str, Any]) -> str:
    for key in EMAIL_HEADERS:
        value = headers.get(key)
        if value:
            return normalize_email(str(value))
    return ""


def _grant_matches_email(grant: Mapping[str, Any], identity_hash: str, identity_email: str) -> bool:
    grant_hash = str(grant.get("emailHash") or grant.get("email_hash") or "").strip().lower()
    if grant_hash and hmac.compare_digest(grant_hash, identity_hash):
        return True
    grant_email = normalize_email(str(grant.get("email") or ""))
    return bool(grant_email and hmac.compare_digest(grant_email, identity_email))


def find_entitlement_for_email(email: str, store: Mapping[str, Any]) -> dict[str, Any] | None:
    identity = normalize_email(email)
    identity_hash = email_hash(identity)
    if not identity or not identity_hash:
        return None
    for grant in store.get("grants") or []:
        if isinstance(grant, Mapping) and _grant_matches_email(grant, identity_hash, identity):
            return dict(grant)
    return None


def normalize_entitlement(grant: Mapping[str, Any] | None, today: date | None = None) -> dict[str, Any]:
    current = _today(today)
    if not grant:
        return {
            "kind": None,
            "status": "missing",
            "feature_scope": "none",
            "active": False,
            "reason": "entitlement_missing",
        }

    kind = str(grant.get("entitlementKind") or grant.get("entitlement_kind") or "").strip()
    status = str(grant.get("status") or "").strip() or "pending"
    feature_scope = str(grant.get("featureScope") or grant.get("feature_scope") or FULL_FEATURE_SCOPE).strip()
    expires_at = _parse_date(grant.get("expiresAt") or grant.get("expires_at"))

    if kind not in VALID_ENTITLEMENT_KINDS:
        status = "denied"
        reason = "invalid_entitlement_kind"
    elif status not in VALID_ENTITLEMENT_STATUSES:
        status = "denied"
        reason = "invalid_entitlement_status"
    elif expires_at and current > expires_at:
        status = "expired"
        reason = "entitlement_expired"
    elif status == "active":
        reason = "active_entitlement"
    else:
        reason = f"entitlement_{status}"

    active = status == "active" and kind in VALID_ENTITLEMENT_KINDS
    if active and kind in {"paid_subscription", "tester_free", "internal_operator"}:
        feature_scope = FULL_FEATURE_SCOPE if feature_scope != RESTRICTED_FEATURE_SCOPE else feature_scope

    return {
        "kind": kind if kind in VALID_ENTITLEMENT_KINDS else None,
        "status": status,
        "feature_scope": feature_scope,
        "active": active,
        "reason": reason,
        "grant_id": grant.get("grantId") or grant.get("grant_id"),
        "grant_key_required": bool(grant.get("grantKeyHash") or grant.get("grant_key_hash")),
        "source": grant.get("source") or ("operator_grant" if kind == "tester_free" else "entitlement_store"),
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


def evaluate_remote_access(
    email: str | None,
    store: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    identity = normalize_email(email)
    loaded_store = dict(store) if isinstance(store, Mapping) else load_entitlement_store()
    grant = find_entitlement_for_email(identity, loaded_store) if identity else None
    entitlement = normalize_entitlement(grant, today=today)
    authenticated = bool(identity)
    allowed = authenticated and entitlement["active"]
    if not authenticated:
        reason = "identity_missing"
    elif not entitlement["active"]:
        reason = entitlement["reason"]
    else:
        reason = "access_allowed"

    return {
        "ok": True,
        "version": REMOTE_ACCESS_VERSION,
        "schemaVersion": str(loaded_store.get("schemaVersion") or ENTITLEMENTS_SCHEMA_VERSION),
        "mode": os.environ.get("SQX_REMOTE_SERVICE_MODE", "local_only"),
        "authenticated": authenticated,
        "identity": {
            "email_ref": redact_email(identity),
            "email_hash": email_hash(identity) if identity else None,
            "source": "cloudflare_access_or_app_header" if authenticated else "none",
        },
        "auth_layers": {
            "edge_identity_present": authenticated,
            "app_session_required": True,
            "app_session_verified": False,
            "grant_key_never_returned": True,
        },
        "entitlement": entitlement,
        "access": {
            "allowed": allowed,
            "reason": reason,
            "feature_scope": entitlement["feature_scope"] if allowed else "none",
            "features": ["*"] if allowed and entitlement["feature_scope"] == FULL_FEATURE_SCOPE else [],
        },
        "audit_event": {
            "type": "remote_access_evaluated",
            "identity_hash": email_hash(identity) if identity else None,
            "entitlement_kind": entitlement["kind"],
            "entitlement_status": entitlement["status"],
            "allowed": allowed,
        },
        "privacy": {
            "raw_email_returned": False,
            "grant_keys_returned": False,
            "store_path_returned": False,
        },
    }


def evaluate_remote_access_from_headers(headers: Mapping[str, Any], today: date | None = None) -> dict[str, Any]:
    return evaluate_remote_access(trusted_email_from_headers(headers), today=today)
