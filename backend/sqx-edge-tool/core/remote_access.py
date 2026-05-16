from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping
import base64


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_ACCESS_VERSION = "remote-access-v1"
REMOTE_SESSION_VERSION = "remote-session-v1"
ENTITLEMENTS_SCHEMA_VERSION = "remote-entitlements-v1"
DEFAULT_ENTITLEMENTS_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_entitlements.local.json"
SESSION_COOKIE_NAME = "__Host-sqx_remote_session"
DEFAULT_SESSION_TTL_SECONDS = 8 * 60 * 60
MIN_SESSION_SECRET_LENGTH = 32

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


def grant_key_hash(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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


def find_entitlement_for_email_hash(identity_hash: str, store: Mapping[str, Any]) -> dict[str, Any] | None:
    expected = (identity_hash or "").strip().lower()
    if not expected:
        return None
    for grant in store.get("grants") or []:
        if not isinstance(grant, Mapping):
            continue
        grant_hash = str(grant.get("emailHash") or grant.get("email_hash") or "").strip().lower()
        if grant_hash and hmac.compare_digest(grant_hash, expected):
            return dict(grant)
        grant_email_hash = email_hash(str(grant.get("email") or ""))
        if grant_email_hash and hmac.compare_digest(grant_email_hash, expected):
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


def verify_tester_grant_key(grant: Mapping[str, Any], provided_key: str | None) -> dict[str, Any]:
    expected_hash = str(grant.get("grantKeyHash") or grant.get("grant_key_hash") or "").strip().lower()
    if not expected_hash:
        return {"ok": False, "error": "tester_grant_key_not_configured"}
    provided_hash = grant_key_hash(provided_key)
    if not provided_hash:
        return {"ok": False, "error": "tester_grant_key_required"}
    if not hmac.compare_digest(expected_hash, provided_hash):
        return {"ok": False, "error": "tester_grant_key_invalid"}
    return {"ok": True, "error": ""}


def _b64url_encode_json(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode_json(value: str) -> dict[str, Any]:
    padded = value + ("=" * (-len(value) % 4))
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    decoded = json.loads(raw.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("session payload must be object")
    return decoded


def session_secret() -> str:
    return os.environ.get("SQX_REMOTE_SESSION_SECRET", "").strip()


def session_secret_ready(secret: str | None = None) -> bool:
    return len((secret if secret is not None else session_secret()).strip()) >= MIN_SESSION_SECRET_LENGTH


def _session_hmac(payload_part: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def sign_session_payload(payload: Mapping[str, Any], secret: str | None = None) -> str:
    configured_secret = (secret if secret is not None else session_secret()).strip()
    if not session_secret_ready(configured_secret):
        raise ValueError("remote_session_secret_missing_or_short")
    payload_part = _b64url_encode_json(payload)
    return f"{payload_part}.{_session_hmac(payload_part, configured_secret)}"


def verify_session_token(token: str | None, secret: str | None = None, now: datetime | None = None) -> dict[str, Any]:
    raw = (token or "").strip()
    configured_secret = (secret if secret is not None else session_secret()).strip()
    if not raw:
        return {"ok": False, "error": "session_missing"}
    if not session_secret_ready(configured_secret):
        return {"ok": False, "error": "remote_session_secret_missing_or_short"}
    if "." not in raw:
        return {"ok": False, "error": "session_malformed"}
    payload_part, signature = raw.rsplit(".", 1)
    expected = _session_hmac(payload_part, configured_secret)
    if not hmac.compare_digest(signature, expected):
        return {"ok": False, "error": "session_signature_invalid"}
    try:
        payload = _b64url_decode_json(payload_part)
    except Exception:
        return {"ok": False, "error": "session_payload_invalid"}
    if payload.get("v") != REMOTE_SESSION_VERSION:
        return {"ok": False, "error": "session_version_mismatch"}
    current_ts = int((now or datetime.now(timezone.utc)).timestamp())
    try:
        exp = int(payload.get("exp") or 0)
    except (TypeError, ValueError):
        return {"ok": False, "error": "session_exp_missing"}
    if current_ts >= exp:
        return {"ok": False, "error": "session_expired", "payload": payload}
    return {"ok": True, "error": "", "payload": payload}


def create_session_payload(
    email: str,
    entitlement: Mapping[str, Any],
    ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS,
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or datetime.now(timezone.utc)
    iat = int(current.timestamp())
    exp = int((current + timedelta(seconds=ttl_seconds)).timestamp())
    identity = normalize_email(email)
    return {
        "v": REMOTE_SESSION_VERSION,
        "sid": secrets.token_urlsafe(18),
        "email_hash": email_hash(identity),
        "email_ref": redact_email(identity),
        "entitlement_kind": entitlement.get("kind"),
        "grant_id": entitlement.get("grant_id"),
        "feature_scope": entitlement.get("feature_scope"),
        "iat": iat,
        "exp": exp,
    }


def create_signed_session(
    email: str,
    entitlement: Mapping[str, Any],
    ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS,
    now: datetime | None = None,
    secret: str | None = None,
) -> dict[str, Any]:
    payload = create_session_payload(email, entitlement, ttl_seconds=ttl_seconds, now=now)
    token = sign_session_payload(payload, secret=secret)
    return {
        "ok": True,
        "token": token,
        "payload": payload,
        "max_age": ttl_seconds,
        "expires_at": datetime.fromtimestamp(payload["exp"], tz=timezone.utc).isoformat(),
    }


def _public_session_from_payload(payload: Mapping[str, Any], active: bool, reason: str) -> dict[str, Any]:
    expires_at = None
    try:
        expires_at = datetime.fromtimestamp(int(payload.get("exp") or 0), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        expires_at = None
    return {
        "active": active,
        "reason": reason,
        "version": payload.get("v"),
        "email_ref": payload.get("email_ref"),
        "email_hash": payload.get("email_hash"),
        "entitlement_kind": payload.get("entitlement_kind"),
        "grant_id": payload.get("grant_id"),
        "feature_scope": payload.get("feature_scope"),
        "expires_at": expires_at,
    }


def evaluate_remote_session(
    token: str | None,
    store: Mapping[str, Any] | None = None,
    today: date | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    verified = verify_session_token(token, now=now)
    if not verified.get("ok"):
        payload = verified.get("payload") if isinstance(verified.get("payload"), Mapping) else {}
        return {
            "ok": True,
            "version": REMOTE_ACCESS_VERSION,
            "session": _public_session_from_payload(payload, False, str(verified.get("error") or "session_invalid")),
            "access": {"allowed": False, "reason": str(verified.get("error") or "session_invalid"), "feature_scope": "none"},
            "privacy": {"session_token_returned": False, "grant_keys_returned": False},
        }

    payload = verified["payload"]
    loaded_store = dict(store) if isinstance(store, Mapping) else load_entitlement_store()
    grant = find_entitlement_for_email_hash(str(payload.get("email_hash") or ""), loaded_store)
    entitlement = normalize_entitlement(grant, today=today)
    allowed = bool(entitlement["active"])
    reason = "session_access_allowed" if allowed else entitlement["reason"]
    return {
        "ok": True,
        "version": REMOTE_ACCESS_VERSION,
        "schemaVersion": str(loaded_store.get("schemaVersion") or ENTITLEMENTS_SCHEMA_VERSION),
        "session": _public_session_from_payload(payload, allowed, reason),
        "entitlement": entitlement,
        "access": {
            "allowed": allowed,
            "reason": reason,
            "feature_scope": entitlement["feature_scope"] if allowed else "none",
            "features": ["*"] if allowed and entitlement["feature_scope"] == FULL_FEATURE_SCOPE else [],
        },
        "audit_event": {
            "type": "remote_session_evaluated",
            "identity_hash": payload.get("email_hash"),
            "entitlement_kind": entitlement["kind"],
            "entitlement_status": entitlement["status"],
            "allowed": allowed,
        },
        "privacy": {"session_token_returned": False, "grant_keys_returned": False},
    }


def start_remote_session_from_headers(headers: Mapping[str, Any], data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not session_secret_ready():
        return {
            "ok": False,
            "http_status": 503,
            "error": "remote_session_secret_missing_or_short",
            "message": "Set SQX_REMOTE_SESSION_SECRET privately before enabling remote app sessions.",
        }
    payload = data if isinstance(data, Mapping) else {}
    identity = trusted_email_from_headers(headers)
    if not identity:
        return {"ok": False, "http_status": 401, "error": "identity_missing"}
    store = load_entitlement_store()
    grant = find_entitlement_for_email(identity, store)
    entitlement = normalize_entitlement(grant)
    if not entitlement["active"]:
        return {
            "ok": False,
            "http_status": 403,
            "error": entitlement["reason"],
            "entitlement": entitlement,
            "identity": {"email_ref": redact_email(identity), "email_hash": email_hash(identity)},
        }
    if entitlement["kind"] == "tester_free":
        grant_key_result = verify_tester_grant_key(grant or {}, str(payload.get("grant_key") or ""))
        if not grant_key_result["ok"]:
            return {
                "ok": False,
                "http_status": 403,
                "error": grant_key_result["error"],
                "entitlement": entitlement,
                "identity": {"email_ref": redact_email(identity), "email_hash": email_hash(identity)},
                "privacy": {"grant_key_returned": False},
            }
    session = create_signed_session(identity, entitlement)
    return {
        "ok": True,
        "http_status": 200,
        "session_token": session["token"],
        "cookie_name": SESSION_COOKIE_NAME,
        "session": {
            "active": True,
            "version": REMOTE_SESSION_VERSION,
            "email_ref": redact_email(identity),
            "email_hash": email_hash(identity),
            "entitlement_kind": entitlement["kind"],
            "feature_scope": entitlement["feature_scope"],
            "expires_at": session["expires_at"],
            "max_age": session["max_age"],
        },
        "entitlement": entitlement,
        "access": {"allowed": True, "reason": "session_created", "feature_scope": entitlement["feature_scope"], "features": ["*"]},
        "privacy": {"session_token_returned": False, "grant_key_returned": False},
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


def evaluate_remote_request(headers: Mapping[str, Any], session_token: str | None, today: date | None = None) -> dict[str, Any]:
    edge_status = evaluate_remote_access_from_headers(headers, today=today)
    session_status = evaluate_remote_session(session_token, today=today)
    session_allowed = bool(session_status.get("access", {}).get("allowed"))
    edge_allowed = bool(edge_status.get("access", {}).get("allowed"))
    allowed = session_allowed or edge_allowed
    merged = {
        **edge_status,
        "session": session_status.get("session"),
        "session_access": session_status.get("access"),
        "access": {
            "allowed": allowed,
            "reason": "session_access_allowed" if session_allowed else edge_status.get("access", {}).get("reason"),
            "feature_scope": (
                session_status.get("access", {}).get("feature_scope")
                if session_allowed else edge_status.get("access", {}).get("feature_scope")
            ),
            "features": session_status.get("access", {}).get("features") if session_allowed else edge_status.get("access", {}).get("features"),
        },
    }
    merged["auth_layers"]["app_session_verified"] = session_allowed
    return merged
