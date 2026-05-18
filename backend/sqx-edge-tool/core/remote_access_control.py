from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_ACCESS_CONTROL_VERSION = "remote-access-control-v1"
ACCESS_CONTROL_COOKIE_NAME = "__Host-sqx_device_id"
ACCESS_CONTROL_ENV = "SQX_REMOTE_ACCESS_CONTROL_PATH"
ACCESS_CONTROL_EVENTS_ENV = "SQX_REMOTE_ACCESS_CONTROL_EVENTS_PATH"
DEFAULT_ACCESS_CONTROL_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_access_control.local.json"
DEFAULT_ACCESS_CONTROL_EVENTS_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_access_events.local.jsonl"

DEFAULT_POLICY = {
    "mode": "strict",
    "maxTrustedContextsPerIdentity": 2,
    "autoTrustWithinLimit": True,
    "blockConcurrentContexts": True,
    "concurrentWindowSeconds": 30 * 60,
}


def _utc_now(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _hash(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ref(value: Any, length: int = 12) -> str:
    text = str(value or "").strip()
    return text[:length] if text else ""


def generate_device_id() -> str:
    return secrets.token_urlsafe(32)


def access_control_path() -> Path:
    configured = os.environ.get(ACCESS_CONTROL_ENV, "").strip()
    return Path(configured).expanduser().resolve(strict=False) if configured else DEFAULT_ACCESS_CONTROL_PATH


def access_control_events_path() -> Path:
    configured = os.environ.get(ACCESS_CONTROL_EVENTS_ENV, "").strip()
    return Path(configured).expanduser().resolve(strict=False) if configured else DEFAULT_ACCESS_CONTROL_EVENTS_PATH


def load_access_control_store(path: str | Path | None = None) -> dict[str, Any]:
    source = Path(path) if path else access_control_path()
    payload: dict[str, Any] = {}
    source_state = "missing_local_store"
    if source.is_file():
        try:
            loaded = json.loads(source.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                payload = loaded
                source_state = "local_store"
            else:
                source_state = "invalid_local_store"
        except (OSError, json.JSONDecodeError):
            source_state = "unreadable_local_store"
    identities = payload.get("identities") if isinstance(payload.get("identities"), Mapping) else {}
    policy = payload.get("policy") if isinstance(payload.get("policy"), Mapping) else {}
    merged_policy = dict(DEFAULT_POLICY)
    merged_policy.update({key: policy[key] for key in policy if key in DEFAULT_POLICY})
    try:
        merged_policy["maxTrustedContextsPerIdentity"] = max(1, int(merged_policy["maxTrustedContextsPerIdentity"]))
    except (TypeError, ValueError):
        merged_policy["maxTrustedContextsPerIdentity"] = DEFAULT_POLICY["maxTrustedContextsPerIdentity"]
    try:
        merged_policy["concurrentWindowSeconds"] = max(60, int(merged_policy["concurrentWindowSeconds"]))
    except (TypeError, ValueError):
        merged_policy["concurrentWindowSeconds"] = DEFAULT_POLICY["concurrentWindowSeconds"]
    return {
        "schemaVersion": str(payload.get("schemaVersion") or REMOTE_ACCESS_CONTROL_VERSION),
        "source": source_state,
        "policy": merged_policy,
        "identities": {str(key): value for key, value in identities.items() if isinstance(value, Mapping)},
        "privacy": {"store_path_returned": False, "raw_ip_returned": False, "raw_email_returned": False},
    }


def save_access_control_store(store: Mapping[str, Any], path: str | Path | None = None) -> None:
    target = Path(path) if path else access_control_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    existing_identities: dict[str, Any] = {}
    if target.is_file():
        try:
            existing_payload = json.loads(target.read_text(encoding="utf-8-sig"))
            existing = existing_payload.get("identities") if isinstance(existing_payload, Mapping) else {}
            if isinstance(existing, Mapping):
                existing_identities = {str(key): value for key, value in existing.items() if isinstance(value, Mapping)}
        except (OSError, json.JSONDecodeError):
            existing_identities = {}
    incoming_identities = store.get("identities") if isinstance(store.get("identities"), Mapping) else {}
    merged_identities: dict[str, Any] = {key: dict(value) for key, value in existing_identities.items()}
    for identity_hash, incoming_record in incoming_identities.items():
        if not isinstance(incoming_record, Mapping):
            continue
        identity_key = str(identity_hash)
        existing_record = merged_identities.get(identity_key) if isinstance(merged_identities.get(identity_key), Mapping) else {}
        merged_record = dict(existing_record)
        merged_record.update(dict(incoming_record))
        existing_contexts = [item for item in existing_record.get("contexts", []) if isinstance(item, Mapping)] if isinstance(existing_record, Mapping) else []
        incoming_contexts = [item for item in incoming_record.get("contexts", []) if isinstance(item, Mapping)]
        contexts_by_hash: dict[str, dict[str, Any]] = {}
        def upsert_context(item: Mapping[str, Any]) -> None:
            context_hash = str(item.get("contextHash") or "").strip()
            context_ref = str(item.get("contextRef") or "").strip()
            key = context_hash or context_ref
            if not key:
                return
            previous_key = ""
            if context_hash and context_hash in contexts_by_hash:
                previous_key = context_hash
            elif context_ref:
                for candidate_key, candidate in contexts_by_hash.items():
                    if str(candidate.get("contextRef") or "") == context_ref:
                        previous_key = candidate_key
                        break
            previous = contexts_by_hash.get(previous_key or key, {})
            if previous_key and previous_key != key:
                contexts_by_hash.pop(previous_key, None)
            merged_context = dict(previous)
            merged_context.update(dict(item))
            if previous.get("status") in {"trusted", "revoked"} and item.get("status") == "pending":
                merged_context["status"] = previous.get("status")
                merged_context["approval"] = previous.get("approval")
            if previous.get("approval") == "operator_approved" and item.get("approval") != "operator_approved":
                merged_context["approval"] = "operator_approved"
                if previous.get("operatorNote"):
                    merged_context["operatorNote"] = previous.get("operatorNote")
                if previous.get("approvedAt"):
                    merged_context["approvedAt"] = previous.get("approvedAt")
            contexts_by_hash[key] = merged_context
        for item in existing_contexts:
            upsert_context(item)
        for item in incoming_contexts:
            upsert_context(item)
        merged_record["contexts"] = list(contexts_by_hash.values())
        merged_identities[identity_key] = merged_record
    payload = {
        "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
        "policy": store.get("policy") if isinstance(store.get("policy"), Mapping) else dict(DEFAULT_POLICY),
        "identities": merged_identities,
        "updatedAt": _utc_now(),
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _header(headers: Mapping[str, Any], name: str) -> str:
    value = headers.get(name)
    if value is not None:
        return str(value).strip()
    lowered = name.lower()
    for key, item in headers.items():
        if str(key).lower() == lowered:
            return str(item).strip()
    return ""


def _client_ip(headers: Mapping[str, Any], remote_addr: str | None) -> tuple[str, str]:
    cf_ip = _header(headers, "CF-Connecting-IP")
    if cf_ip:
        return cf_ip, "cloudflare_cf_connecting_ip"
    return str(remote_addr or "").strip(), "request_remote_addr"


def ensure_device_id(cookies: Mapping[str, Any] | None) -> tuple[str, bool]:
    raw = ""
    if isinstance(cookies, Mapping):
        raw = str(cookies.get(ACCESS_CONTROL_COOKIE_NAME) or "").strip()
    if len(raw) >= 24:
        return raw, False
    return generate_device_id(), True


def build_access_context(
    headers: Mapping[str, Any],
    *,
    cookies: Mapping[str, Any] | None = None,
    remote_addr: str | None = None,
    device_id: str | None = None,
) -> dict[str, Any]:
    selected_device_id = str(device_id or "").strip()
    generated = False
    if not selected_device_id:
        selected_device_id, generated = ensure_device_id(cookies)
    ip, ip_source = _client_ip(headers, remote_addr)
    country = _header(headers, "CF-IPCountry")[:2].upper()
    user_agent = _header(headers, "User-Agent")
    device_hash = _hash(selected_device_id)
    ip_hash = _hash(ip)
    user_agent_hash = _hash(user_agent)
    context_hash = _hash("|".join([device_hash, ip_hash, user_agent_hash]))
    return {
        "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
        "deviceId": selected_device_id,
        "deviceCookieCreated": generated,
        "contextHash": context_hash,
        "contextRef": _ref(context_hash),
        "deviceHash": device_hash,
        "deviceHashRef": _ref(device_hash),
        "ipHash": ip_hash,
        "ipHashRef": _ref(ip_hash),
        "ipSource": ip_source,
        "country": country or "XX",
        "userAgentHash": user_agent_hash,
        "userAgentHashRef": _ref(user_agent_hash),
        "privacy": {"raw_ip_stored": False, "raw_user_agent_stored": False, "device_id_returned": False},
    }


def _identity_record(store: dict[str, Any], identity_hash: str, email_ref: str | None, entitlement_kind: str | None) -> dict[str, Any]:
    identities = store.setdefault("identities", {})
    record = identities.get(identity_hash)
    if not isinstance(record, dict):
        record = {
            "identityHashRef": _ref(identity_hash),
            "emailRef": email_ref or "",
            "entitlementKind": entitlement_kind or "",
            "status": "active",
            "contexts": [],
            "createdAt": _utc_now(),
        }
        identities[identity_hash] = record
    if email_ref:
        record["emailRef"] = email_ref
    if entitlement_kind:
        record["entitlementKind"] = entitlement_kind
    if not isinstance(record.get("contexts"), list):
        record["contexts"] = []
    return record


def _public_context(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contextRef": item.get("contextRef"),
        "status": item.get("status"),
        "deviceHashRef": item.get("deviceHashRef"),
        "ipHashRef": item.get("ipHashRef"),
        "userAgentHashRef": item.get("userAgentHashRef"),
        "country": item.get("country"),
        "firstSeen": item.get("firstSeen"),
        "lastSeen": item.get("lastSeen"),
        "lastDecision": item.get("lastDecision"),
        "approval": item.get("approval"),
    }


def record_access_event(event: Mapping[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else access_control_events_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    safe_event = {
        "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
        "timestamp": event.get("timestamp") or _utc_now(),
        "type": str(event.get("type") or "remote_access_control_event"),
        "identityHashRef": _ref(event.get("identityHash") or event.get("identityHashRef")),
        "contextRef": event.get("contextRef"),
        "decision": event.get("decision"),
        "reason": event.get("reason"),
        "status": event.get("status"),
        "privacy": {"rawEmailStored": False, "rawIpStored": False, "tokensStored": False, "localPathsStored": False},
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe_event, sort_keys=True) + "\n")
    return {"ok": True, "stored": True, "event": safe_event, "privacy": {"event_path_returned": False}}


def _active_other_context(
    record: Mapping[str, Any],
    current_ref: str,
    *,
    policy: Mapping[str, Any],
    now: datetime,
) -> Mapping[str, Any] | None:
    if not bool(policy.get("blockConcurrentContexts")):
        return None
    try:
        window = int(policy.get("concurrentWindowSeconds") or DEFAULT_POLICY["concurrentWindowSeconds"])
    except (TypeError, ValueError):
        window = DEFAULT_POLICY["concurrentWindowSeconds"]
    for item in record.get("contexts") or []:
        if not isinstance(item, Mapping):
            continue
        if item.get("contextRef") == current_ref or item.get("status") != "trusted":
            continue
        last_session = _parse_utc(item.get("lastSessionAt"))
        if last_session and (now - last_session).total_seconds() <= window:
            return item
    return None


def evaluate_access_context(
    identity_hash: str | None,
    context: Mapping[str, Any],
    *,
    email_ref: str | None = None,
    entitlement_kind: str | None = None,
    session_context_ref: str | None = None,
    purpose: str = "status",
    mutate: bool = True,
    store_path: str | Path | None = None,
    events_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    current = now or datetime.now(timezone.utc)
    identity = str(identity_hash or "").strip().lower()
    context_hash = str(context.get("contextHash") or "").strip().lower()
    context_ref = str(context.get("contextRef") or _ref(context_hash)).strip()
    store = load_access_control_store(store_path)
    policy = store.get("policy") if isinstance(store.get("policy"), Mapping) else dict(DEFAULT_POLICY)

    def finish(allowed: bool, reason: str, status: str, item: Mapping[str, Any] | None = None) -> dict[str, Any]:
        event = {
            "type": "remote_access_context_evaluated",
            "identityHash": identity,
            "contextRef": context_ref,
            "decision": "allowed" if allowed else "blocked",
            "reason": reason,
            "status": status,
            "timestamp": _utc_now(current),
        }
        if mutate:
            record_access_event(event, path=events_path)
        return {
            "ok": True,
            "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
            "accessControl": {
                "allowed": allowed,
                "reason": reason,
                "status": status,
                "mode": policy.get("mode") or "strict",
                "contextRef": context_ref,
                "maxTrustedContextsPerIdentity": policy.get("maxTrustedContextsPerIdentity"),
            },
            "context": _public_context(item or {
                "contextRef": context_ref,
                "status": status,
                "deviceHashRef": context.get("deviceHashRef"),
                "ipHashRef": context.get("ipHashRef"),
                "userAgentHashRef": context.get("userAgentHashRef"),
                "country": context.get("country"),
            }),
            "privacy": {"raw_email_returned": False, "raw_ip_returned": False, "device_id_returned": False, "store_path_returned": False},
        }

    if not identity:
        return finish(False, "identity_missing", "blocked")
    if not context_hash:
        return finish(False, "context_missing", "blocked")

    record = _identity_record(store, identity, email_ref, entitlement_kind)
    if record.get("status") in {"blocked", "revoked"}:
        return finish(False, "identity_access_blocked", str(record.get("status") or "blocked"))

    contexts = [item for item in record.get("contexts") or [] if isinstance(item, dict)]
    item = next((
        entry for entry in contexts
        if entry.get("contextHash") == context_hash or str(entry.get("contextRef") or "") == context_ref
    ), None)
    trusted_count = len([entry for entry in contexts if entry.get("status") == "trusted"])
    created = False
    if item is None:
        max_contexts = int(policy.get("maxTrustedContextsPerIdentity") or DEFAULT_POLICY["maxTrustedContextsPerIdentity"])
        status = "trusted" if bool(policy.get("autoTrustWithinLimit", True)) and trusted_count < max_contexts else "pending"
        item = {
            "contextHash": context_hash,
            "contextRef": context_ref,
            "status": status,
            "deviceHashRef": context.get("deviceHashRef"),
            "ipHashRef": context.get("ipHashRef"),
            "userAgentHashRef": context.get("userAgentHashRef"),
            "country": context.get("country"),
            "approval": "auto_within_limit" if status == "trusted" else "operator_required",
            "firstSeen": _utc_now(current),
            "lastSeen": _utc_now(current),
        }
        contexts.append(item)
        record["contexts"] = contexts
        created = True
    else:
        item["contextHash"] = item.get("contextHash") or context_hash
        item["contextRef"] = item.get("contextRef") or context_ref
        item["deviceHashRef"] = item.get("deviceHashRef") or context.get("deviceHashRef")
        item["ipHashRef"] = item.get("ipHashRef") or context.get("ipHashRef")
        item["userAgentHashRef"] = item.get("userAgentHashRef") or context.get("userAgentHashRef")
        item["lastSeen"] = _utc_now(current)
        item["country"] = context.get("country") or item.get("country") or "XX"

    status = str(item.get("status") or "pending")
    allowed = status == "trusted"
    reason = "context_trusted" if allowed else f"context_{status}"
    expected_ref = str(session_context_ref or "").strip()
    if allowed and expected_ref and expected_ref != context_ref:
        allowed = False
        reason = "session_context_mismatch"
    if allowed and purpose == "session_login":
        active_other = _active_other_context(record, context_ref, policy=policy, now=current)
        if active_other:
            allowed = False
            reason = "concurrent_context_active"
    item["lastDecision"] = reason
    if created:
        item["createdBy"] = "remote_access_control"
    if mutate:
        save_access_control_store(store, path=store_path)
    return finish(allowed, reason, status, item)


def record_session_started(
    identity_hash: str,
    context_ref: str,
    session_id: str,
    *,
    store_path: str | Path | None = None,
    events_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    identity = str(identity_hash or "").strip().lower()
    ref = str(context_ref or "").strip()
    if not identity or not ref:
        return {"ok": False, "error": "identity_or_context_missing"}
    store = load_access_control_store(store_path)
    record = _identity_record(store, identity, None, None)
    current = now or datetime.now(timezone.utc)
    for item in record.get("contexts") or []:
        if isinstance(item, dict) and item.get("contextRef") == ref:
            item["lastSessionAt"] = _utc_now(current)
            item["activeSessionHashRef"] = _ref(_hash(session_id))
            item["lastDecision"] = "session_started"
            save_access_control_store(store, path=store_path)
            record_access_event({
                "type": "remote_access_session_started",
                "identityHash": identity,
                "contextRef": ref,
                "decision": "allowed",
                "reason": "session_started",
                "status": item.get("status"),
                "timestamp": _utc_now(current),
            }, path=events_path)
            return {"ok": True, "contextRef": ref, "privacy": {"raw_session_id_returned": False}}
    return {"ok": False, "error": "context_not_found", "contextRef": ref}


def _find_identity(store: Mapping[str, Any], identity_ref: str) -> tuple[str, dict[str, Any]] | tuple[str, None]:
    needle = str(identity_ref or "").strip().lower()
    for identity_hash, record in (store.get("identities") or {}).items():
        if identity_hash == needle or identity_hash.startswith(needle) or str(record.get("identityHashRef") or "") == needle:
            return identity_hash, dict(record)
    return "", None


def approve_access_context(identity_ref: str, context_ref: str, *, note: str = "", store_path: str | Path | None = None) -> dict[str, Any]:
    store = load_access_control_store(store_path)
    identity_hash, record = _find_identity(store, identity_ref)
    if not record:
        return {"ok": False, "error": "identity_not_found"}
    for item in record.get("contexts") or []:
        if isinstance(item, dict) and str(item.get("contextRef") or "") == str(context_ref or ""):
            item["status"] = "trusted"
            item["approval"] = "operator_approved"
            item["operatorNote"] = str(note or "")[:300]
            item["approvedAt"] = _utc_now()
            store["identities"][identity_hash] = record
            save_access_control_store(store, path=store_path)
            return {"ok": True, "identityHashRef": _ref(identity_hash), "contextRef": context_ref, "status": "trusted"}
    return {"ok": False, "error": "context_not_found"}


def revoke_access_context(identity_ref: str, context_ref: str, *, note: str = "", store_path: str | Path | None = None) -> dict[str, Any]:
    store = load_access_control_store(store_path)
    identity_hash, record = _find_identity(store, identity_ref)
    if not record:
        return {"ok": False, "error": "identity_not_found"}
    for item in record.get("contexts") or []:
        if isinstance(item, dict) and str(item.get("contextRef") or "") == str(context_ref or ""):
            item["status"] = "revoked"
            item["revokedAt"] = _utc_now()
            item["operatorNote"] = str(note or "")[:300]
            store["identities"][identity_hash] = record
            save_access_control_store(store, path=store_path)
            return {"ok": True, "identityHashRef": _ref(identity_hash), "contextRef": context_ref, "status": "revoked"}
    return {"ok": False, "error": "context_not_found"}


def block_identity(identity_ref: str, *, note: str = "", store_path: str | Path | None = None) -> dict[str, Any]:
    store = load_access_control_store(store_path)
    identity_hash, record = _find_identity(store, identity_ref)
    if not record:
        return {"ok": False, "error": "identity_not_found"}
    record["status"] = "blocked"
    record["blockedAt"] = _utc_now()
    record["operatorNote"] = str(note or "")[:300]
    store["identities"][identity_hash] = record
    save_access_control_store(store, path=store_path)
    return {"ok": True, "identityHashRef": _ref(identity_hash), "status": "blocked"}


def summarize_access_control(store_path: str | Path | None = None) -> dict[str, Any]:
    store = load_access_control_store(store_path)
    identities = store.get("identities") if isinstance(store.get("identities"), Mapping) else {}
    contexts: list[dict[str, Any]] = []
    blocked_identities = 0
    pending_contexts = 0
    revoked_contexts = 0
    trusted_contexts = 0
    for identity_hash, record in identities.items():
        if not isinstance(record, Mapping):
            continue
        if record.get("status") == "blocked":
            blocked_identities += 1
        for item in record.get("contexts") or []:
            if not isinstance(item, Mapping):
                continue
            status = str(item.get("status") or "pending")
            if status == "trusted":
                trusted_contexts += 1
            elif status == "revoked":
                revoked_contexts += 1
            elif status == "pending":
                pending_contexts += 1
            contexts.append({
                "identityHashRef": _ref(identity_hash),
                "emailRef": record.get("emailRef"),
                **_public_context(item),
            })
    return {
        "ok": True,
        "schemaVersion": REMOTE_ACCESS_CONTROL_VERSION,
        "source": store.get("source"),
        "policy": store.get("policy"),
        "summary": {
            "identityCount": len(identities),
            "trustedContexts": trusted_contexts,
            "pendingContexts": pending_contexts,
            "revokedContexts": revoked_contexts,
            "blockedIdentities": blocked_identities,
            "totalContexts": len(contexts),
        },
        "contexts": contexts[-25:],
        "privacy": {"store_path_returned": False, "raw_email_returned": False, "raw_ip_returned": False},
    }
