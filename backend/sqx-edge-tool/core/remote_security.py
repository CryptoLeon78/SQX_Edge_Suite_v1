from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_SECURITY_VERSION = "remote-security-v1"
SECURITY_POLICY_ENV = "SQX_REMOTE_SECURITY_POLICY_PATH"
DEFAULT_SECURITY_POLICY_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_security.local.json"
DEFAULT_RATE_LIMITS = {
    "remote_status": {"limit": 180, "windowSeconds": 60},
    "remote_session_login": {"limit": 10, "windowSeconds": 60},
    "remote_session_logout": {"limit": 30, "windowSeconds": 60},
    "remote_payment_webhook": {"limit": 90, "windowSeconds": 60},
    "remote_protected_write": {"limit": 30, "windowSeconds": 60},
    "remote_ai": {"limit": 20, "windowSeconds": 60},
}
DEFAULT_WATERMARK = {
    "enabled": True,
    "label": "SQX REMOTE PRO",
}

_RATE_BUCKETS: dict[str, list[float]] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def remote_security_policy_path() -> Path:
    configured = os.environ.get(SECURITY_POLICY_ENV, "").strip()
    return Path(configured).expanduser().resolve(strict=False) if configured else DEFAULT_SECURITY_POLICY_PATH


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _merge_rate_limits(value: Any) -> dict[str, dict[str, int]]:
    merged: dict[str, dict[str, int]] = {key: dict(rule) for key, rule in DEFAULT_RATE_LIMITS.items()}
    if not isinstance(value, Mapping):
        return merged
    for action, rule in value.items():
        if not isinstance(rule, Mapping):
            continue
        try:
            limit = int(rule.get("limit") or merged.get(str(action), {}).get("limit") or 0)
            window = int(rule.get("windowSeconds") or rule.get("window_seconds") or merged.get(str(action), {}).get("windowSeconds") or 60)
        except (TypeError, ValueError):
            continue
        if limit > 0 and window > 0:
            merged[str(action)] = {"limit": limit, "windowSeconds": window}
    return merged


def _audit_recent_events_limit(value: Any) -> int:
    if not isinstance(value, Mapping):
        return 20
    try:
        limit = int(value.get("recentEventsLimit") or value.get("recent_events_limit") or 20)
    except (TypeError, ValueError):
        return 20
    return max(1, min(limit, 100))


def load_remote_security_policy(path: Path | None = None) -> dict[str, Any]:
    source = path or remote_security_policy_path()
    payload: dict[str, Any] = {}
    source_state = "missing_local_policy"
    if source.is_file():
        try:
            loaded = json.loads(source.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                payload = loaded
                source_state = "local_policy"
            else:
                source_state = "invalid_local_policy"
        except (OSError, json.JSONDecodeError):
            source_state = "unreadable_local_policy"

    kill_switch = payload.get("killSwitch") if isinstance(payload.get("killSwitch"), Mapping) else {}
    watermark = payload.get("watermark") if isinstance(payload.get("watermark"), Mapping) else {}
    return {
        "schemaVersion": str(payload.get("schemaVersion") or REMOTE_SECURITY_VERSION),
        "source": source_state,
        "killSwitch": {
            "active": bool(kill_switch.get("active", False)),
            "reason": str(kill_switch.get("reason") or "operator_controlled_pause"),
        },
        "blockedIdentityHashes": _list_of_strings(payload.get("blockedIdentityHashes") or payload.get("blocked_identity_hashes")),
        "revokedSessionIds": _list_of_strings(payload.get("revokedSessionIds") or payload.get("revoked_session_ids")),
        "rateLimits": _merge_rate_limits(payload.get("rateLimits") or payload.get("rate_limits")),
        "watermark": {
            "enabled": bool(watermark.get("enabled", DEFAULT_WATERMARK["enabled"])),
            "label": str(watermark.get("label") or DEFAULT_WATERMARK["label"])[:40],
        },
        "audit": {"recentEventsLimit": _audit_recent_events_limit(payload.get("audit"))},
        "privacy": {"policy_path_returned": False, "raw_emails_returned": False},
    }


def reset_remote_rate_limits() -> None:
    _RATE_BUCKETS.clear()


def is_kill_switch_active(policy: Mapping[str, Any] | None = None) -> bool:
    loaded = policy if isinstance(policy, Mapping) else load_remote_security_policy()
    kill_switch = loaded.get("killSwitch") if isinstance(loaded.get("killSwitch"), Mapping) else {}
    return bool(kill_switch.get("active"))


def identity_blocked(identity_hash: str | None, policy: Mapping[str, Any] | None = None) -> bool:
    expected = (identity_hash or "").strip().lower()
    if not expected:
        return False
    loaded = policy if isinstance(policy, Mapping) else load_remote_security_policy()
    blocked = {str(item).strip().lower() for item in loaded.get("blockedIdentityHashes") or []}
    return expected in blocked


def session_revoked(session_id: str | None, policy: Mapping[str, Any] | None = None) -> bool:
    expected = (session_id or "").strip()
    if not expected:
        return False
    loaded = policy if isinstance(policy, Mapping) else load_remote_security_policy()
    revoked = {str(item).strip() for item in loaded.get("revokedSessionIds") or []}
    return expected in revoked


def check_remote_rate_limit(
    subject: str | None,
    action: str,
    *,
    policy: Mapping[str, Any] | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    loaded = policy if isinstance(policy, Mapping) else load_remote_security_policy()
    rules = loaded.get("rateLimits") if isinstance(loaded.get("rateLimits"), Mapping) else {}
    rule = rules.get(action) if isinstance(rules.get(action), Mapping) else DEFAULT_RATE_LIMITS.get(action, {"limit": 60, "windowSeconds": 60})
    limit = int(rule.get("limit") or 60)
    window = int(rule.get("windowSeconds") or 60)
    current = float(now if now is not None else time.time())
    key = f"{action}:{subject or 'anonymous'}"
    bucket = [stamp for stamp in _RATE_BUCKETS.get(key, []) if stamp > current - window]
    allowed = len(bucket) < limit
    if allowed:
        bucket.append(current)
    _RATE_BUCKETS[key] = bucket
    reset_at = int((bucket[0] + window) if bucket else current + window)
    retry_after = max(0, reset_at - int(current)) if not allowed else 0
    return {
        "ok": True,
        "version": REMOTE_SECURITY_VERSION,
        "allowed": allowed,
        "action": action,
        "limit": limit,
        "windowSeconds": window,
        "remaining": max(0, limit - len(bucket)),
        "retryAfterSeconds": retry_after,
        "resetAt": datetime.fromtimestamp(reset_at, tz=timezone.utc).isoformat(),
        "privacy": {"subject_returned": False},
    }


def public_security_status(
    session_status: Mapping[str, Any] | None = None,
    *,
    policy: Mapping[str, Any] | None = None,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    loaded = policy if isinstance(policy, Mapping) else load_remote_security_policy()
    session = session_status.get("session") if isinstance(session_status, Mapping) and isinstance(session_status.get("session"), Mapping) else {}
    session_security = session_status.get("security") if isinstance(session_status, Mapping) and isinstance(session_status.get("security"), Mapping) else {}
    identity_hash = str(session.get("email_hash") or "").strip().lower()
    session_id = str(session.get("sid") or "").strip()
    watermark = loaded.get("watermark") if isinstance(loaded.get("watermark"), Mapping) else DEFAULT_WATERMARK
    marker = str(session.get("email_ref") or workspace_id or "remote-session")
    return {
        "ok": True,
        "version": REMOTE_SECURITY_VERSION,
        "source": loaded.get("source"),
        "killSwitch": loaded.get("killSwitch"),
        "rateLimits": {
            "enabled": True,
            "actions": sorted((loaded.get("rateLimits") or {}).keys()),
        },
        "revocation": {
            "enabled": True,
            "revokedSessionCount": len(loaded.get("revokedSessionIds") or []),
            "currentSessionRevoked": bool(session_security.get("session_revoked")) or session_revoked(session_id, loaded),
        },
        "blocking": {
            "enabled": True,
            "blockedIdentityCount": len(loaded.get("blockedIdentityHashes") or []),
            "currentIdentityBlocked": bool(session_security.get("identity_blocked")) or identity_blocked(identity_hash, loaded),
        },
        "watermark": {
            "enabled": bool(watermark.get("enabled")),
            "label": str(watermark.get("label") or DEFAULT_WATERMARK["label"]),
            "marker": marker,
        },
        "generatedAt": _utc_now(),
        "privacy": {
            "policy_path_returned": False,
            "raw_email_returned": False,
            "session_token_returned": False,
            "local_paths_returned": False,
        },
    }
