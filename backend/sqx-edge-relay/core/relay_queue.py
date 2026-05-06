from __future__ import annotations

import hashlib
import hmac
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


RELAY_ROOT = Path(__file__).resolve().parents[1]
TOOL_ROOT = RELAY_ROOT.parent / "sqx-edge-tool"
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.fulfillment_normalizer import normalize_payload, verify_lemon_signature


QUEUE_ROOT = RELAY_ROOT / "data" / "queue"
INCOMING_DIR = QUEUE_ROOT / "incoming"
PENDING_DIR = QUEUE_ROOT / "pending"
SENT_DIR = QUEUE_ROOT / "sent"
FAILED_DIR = QUEUE_ROOT / "failed"
BACKOFF_SECONDS = [5, 25, 125, 625]


def ensure_queue_dirs() -> None:
    for path in (QUEUE_ROOT, INCOMING_DIR, PENDING_DIR, SENT_DIR, FAILED_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(value or ""))
    cleaned = cleaned.strip("_").lower()
    return cleaned or "event"


def _bundle_name(prefix: str, provider_event_id: str) -> str:
    return f"{prefix}_{_stamp()}_{_safe_token(provider_event_id)}.json"


def _all_queue_dirs() -> list[Path]:
    return [PENDING_DIR, SENT_DIR, FAILED_DIR]


def _find_existing(provider_event_id: str) -> dict[str, Any] | None:
    event_id = str(provider_event_id or "").strip()
    if not event_id:
        return None
    for folder in _all_queue_dirs():
        for path in folder.glob("relay_bundle_*.json"):
            try:
                payload = _load_json(path)
            except (OSError, json.JSONDecodeError):
                continue
            if str(payload.get("provider_event_id") or "") == event_id:
                return payload
    return None


def _summary_rows(folder: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(folder.glob("relay_bundle_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        rows.append(
            {
                "name": path.name,
                "relay_event_id": payload.get("relay_event_id"),
                "provider_event_id": payload.get("provider_event_id"),
                "source_event": payload.get("source_event"),
                "customer_email": payload.get("normalized_request", {}).get("customer_email"),
                "plan": payload.get("normalized_request", {}).get("plan"),
                "status": payload.get("status"),
                "attempt_count": int(payload.get("attempt_count") or 0),
                "last_error": payload.get("last_error", ""),
                "next_attempt_at": payload.get("next_attempt_at", ""),
                "created_at": payload.get("created_at", ""),
            }
        )
    return rows


def queue_overview() -> dict[str, Any]:
    ensure_queue_dirs()
    pending = _summary_rows(PENDING_DIR)
    sent = _summary_rows(SENT_DIR)
    failed = _summary_rows(FAILED_DIR)
    return {
        "pending": pending,
        "sent": sent,
        "failed": failed,
        "summary": {
            "pending": len(pending),
            "sent": len(sent),
            "failed": len(failed),
            "total": len(pending) + len(sent) + len(failed),
        },
    }


def _read_queue_item(name: str) -> tuple[Path, dict[str, Any]]:
    for folder in _all_queue_dirs():
        path = folder / name
        if path.is_file():
            return path, _load_json(path)
    raise FileNotFoundError(name)


def load_queue_item(name: str) -> dict[str, Any]:
    _path, payload = _read_queue_item(name)
    return payload


def sign_bundle(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def enqueue_lemon_webhook(raw_body: bytes, signature: str, secret: str) -> dict[str, Any]:
    ensure_queue_dirs()
    if not verify_lemon_signature(raw_body, signature, secret):
        return {"ok": False, "error": "invalid_signature"}

    payload = json.loads(raw_body.decode("utf-8-sig"))
    normalized_request = normalize_payload(payload, provider="lemon")
    provider_event_id = str(normalized_request.get("provider_event_id") or "") or hashlib.sha256(raw_body).hexdigest()[:16]
    existing = _find_existing(provider_event_id)
    if existing:
        return {"ok": True, "stored": False, "duplicate": True, "bundle": existing}

    relay_event_id = "relay_" + hashlib.sha256((provider_event_id + _stamp()).encode("utf-8")).hexdigest()[:16]
    incoming_name = _bundle_name("incoming_event", provider_event_id)
    bundle_name = _bundle_name("relay_bundle", provider_event_id)
    event_record = {
        "provider": "Lemon Squeezy",
        "stored_at": datetime.now().isoformat(timespec="seconds"),
        "provider_event_id": provider_event_id,
        "payload": payload,
    }
    bundle = {
        "schema_version": 1,
        "relay_event_id": relay_event_id,
        "relay_source": "sqx_edge_remote_relay",
        "provider": "lemon",
        "provider_event_id": provider_event_id,
        "source_event": normalized_request.get("source_event"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "pending",
        "attempt_count": 0,
        "next_attempt_at": "",
        "last_error": "",
        "normalized_request": normalized_request,
        "incoming_event_file": incoming_name,
    }
    _write_json(INCOMING_DIR / incoming_name, event_record)
    _write_json(PENDING_DIR / bundle_name, bundle)
    bundle["name"] = bundle_name
    return {"ok": True, "stored": True, "duplicate": False, "bundle": bundle}


def _move_bundle(path: Path, target_dir: Path, payload: dict[str, Any]) -> Path:
    target = target_dir / path.name
    _write_json(target, payload)
    if path != target and path.exists():
        path.unlink()
    return target


def _can_attempt(payload: dict[str, Any], now: datetime | None = None) -> bool:
    current = now or datetime.now()
    next_attempt_at = str(payload.get("next_attempt_at") or "").strip()
    if not next_attempt_at:
        return True
    try:
        return current >= datetime.fromisoformat(next_attempt_at)
    except ValueError:
        return True


def dispatch_queue_item(name: str, target_url: str, relay_secret: str) -> dict[str, Any]:
    ensure_queue_dirs()
    path, bundle = _read_queue_item(name)
    if not _can_attempt(bundle):
        return {"ok": False, "error": "not_due_yet", "bundle": bundle}

    payload = dict(bundle)
    payload["attempt_count"] = int(payload.get("attempt_count") or 0) + 1
    payload["last_attempt_at"] = datetime.now().isoformat(timespec="seconds")
    raw_body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    signature = sign_bundle(raw_body, relay_secret)
    req = urlrequest.Request(
        target_url,
        data=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-SQX-Relay-Signature": signature,
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8", errors="replace")
            payload["status"] = "sent"
            payload["last_error"] = ""
            payload["last_response_code"] = response.status
            payload["last_response_body"] = body[:1000]
            payload["next_attempt_at"] = ""
            _move_bundle(path, SENT_DIR, payload)
            return {"ok": True, "bundle": payload}
    except (urlerror.URLError, urlerror.HTTPError, TimeoutError) as exc:
        attempts = int(payload.get("attempt_count") or 1)
        delay = BACKOFF_SECONDS[min(attempts - 1, len(BACKOFF_SECONDS) - 1)]
        payload["status"] = "failed"
        payload["last_error"] = str(exc)
        payload["next_attempt_at"] = (datetime.now() + timedelta(seconds=delay)).isoformat(timespec="seconds")
        _move_bundle(path, FAILED_DIR, payload)
        return {"ok": False, "error": "dispatch_failed", "bundle": payload}


def requeue_failed_item(name: str) -> dict[str, Any]:
    ensure_queue_dirs()
    path, bundle = _read_queue_item(name)
    payload = dict(bundle)
    payload["status"] = "pending"
    payload["next_attempt_at"] = ""
    _move_bundle(path, PENDING_DIR, payload)
    return {"ok": True, "bundle": payload}


def dispatch_due_items(target_url: str, relay_secret: str, limit: int = 10) -> dict[str, Any]:
    ensure_queue_dirs()
    results: list[dict[str, Any]] = []
    candidates = sorted(PENDING_DIR.glob("relay_bundle_*.json"), key=lambda item: item.stat().st_mtime)[:limit]
    for path in candidates:
        bundle = _load_json(path)
        if not _can_attempt(bundle):
            continue
        results.append(dispatch_queue_item(path.name, target_url, relay_secret))
    return {"ok": True, "results": results}
