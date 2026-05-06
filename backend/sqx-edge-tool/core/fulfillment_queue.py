from __future__ import annotations

import hashlib
import hmac
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from core.fulfillment_normalizer import normalize_payload, verify_lemon_signature


ROOT = Path(__file__).resolve().parents[1]
QUEUE_ROOT = ROOT / "fulfillment_requests"
EVENTS_DIR = QUEUE_ROOT / "events"
REQUESTS_DIR = QUEUE_ROOT / "requests"
PROCESSED_DIR = QUEUE_ROOT / "processed"
REQUEST_OPERATOR_STATUSES = {
    "queued",
    "processing",
    "needs_review",
    "failed",
    "completed",
    "ignored",
}


def ensure_queue_dirs() -> None:
    for path in (QUEUE_ROOT, EVENTS_DIR, REQUESTS_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(value or ""))
    cleaned = cleaned.strip("_").lower()
    return cleaned or "event"


def _request_path(filename: str) -> Path:
    if not filename.startswith("fulfillment_request_") or not filename.endswith(".json"):
        raise FileNotFoundError(filename)
    path = (REQUESTS_DIR / filename).resolve(strict=False)
    path.relative_to(REQUESTS_DIR.resolve(strict=False))
    return path


def _processed_path(filename: str) -> Path:
    if not filename.startswith("delivery_receipt_") or not filename.endswith(".json"):
        raise FileNotFoundError(filename)
    path = (PROCESSED_DIR / filename).resolve(strict=False)
    path.relative_to(PROCESSED_DIR.resolve(strict=False))
    return path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _find_existing_request(provider_event_id: str) -> dict[str, Any] | None:
    event_id = str(provider_event_id or "").strip()
    if not event_id:
        return None
    for path in REQUESTS_DIR.glob("fulfillment_request_*.json"):
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if str(payload.get("provider_event_id") or "") == event_id:
            return payload
    return None


def _request_defaults(request: dict[str, Any]) -> dict[str, Any]:
    payload = dict(request)
    eligible = bool(payload.get("eligible_for_fulfillment"))
    payload.setdefault("operator_status", "queued" if eligible else "needs_review")
    payload.setdefault("operator_note", "")
    payload.setdefault("attempt_count", 0)
    payload.setdefault("last_attempt_at", "")
    payload.setdefault("last_error", "")
    payload.setdefault("processed_receipt_file", "")
    payload.setdefault("last_delivery_dir", "")
    payload.setdefault("completed_at", "")
    payload.setdefault("updated_at", payload.get("stored_at", ""))
    return payload


def _verify_signature_hex(raw_body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _request_summary(payload: dict[str, Any]) -> dict[str, Any]:
    request = _request_defaults(payload)
    return {
        "name": request.get("request_file") or "",
        "provider": request.get("provider"),
        "source_event": request.get("source_event"),
        "provider_event_id": request.get("provider_event_id"),
        "order_id": request.get("order_id"),
        "customer_email": request.get("customer_email"),
        "plan": request.get("plan"),
        "eligible_for_fulfillment": bool(request.get("eligible_for_fulfillment")),
        "fulfillment_status": request.get("fulfillment_status"),
        "operator_status": request.get("operator_status"),
        "operator_note": request.get("operator_note"),
        "attempt_count": int(request.get("attempt_count") or 0),
        "last_attempt_at": request.get("last_attempt_at"),
        "last_error": request.get("last_error"),
        "processed_receipt_file": request.get("processed_receipt_file"),
        "stored_at": request.get("stored_at"),
        "updated_at": request.get("updated_at"),
    }


def _save_request(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    request = _request_defaults(payload)
    request["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _write_json(path, request)
    return request


def _request_list_path(filename: str) -> Path:
    path = _request_path(filename)
    if not path.is_file():
        raise FileNotFoundError(filename)
    return path


def _queue_summary(rows: list[dict[str, Any]], processed: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("operator_status") or "queued")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "queued": status_counts.get("queued", 0),
        "processing": status_counts.get("processing", 0),
        "needs_review": status_counts.get("needs_review", 0),
        "failed": status_counts.get("failed", 0),
        "completed": status_counts.get("completed", 0),
        "ignored": status_counts.get("ignored", 0),
        "processed_receipts": len(processed),
        "total_requests": len(rows),
    }


def store_lemon_webhook(
    raw_body: bytes,
    signature: str,
    secret: str,
    *,
    today=None,
) -> dict[str, Any]:
    ensure_queue_dirs()
    if not verify_lemon_signature(raw_body, signature, secret):
        return {"ok": False, "error": "invalid_signature"}

    payload = json.loads(raw_body.decode("utf-8-sig"))
    request = normalize_payload(payload, provider="lemon", today=today)
    provider_event_id = str(request.get("provider_event_id") or "") or hashlib.sha256(raw_body).hexdigest()[:16]
    existing = _find_existing_request(provider_event_id)
    if existing:
        return {
            "ok": True,
            "stored": False,
            "duplicate": True,
            "request": existing,
            "provider_event_id": provider_event_id,
        }

    token = _safe_token(provider_event_id)
    stamp = _stamp()
    event_filename = f"webhook_event_{stamp}_{token}.json"
    request_filename = f"fulfillment_request_{stamp}_{token}.json"

    event_record = {
        "provider": "Lemon Squeezy",
        "stored_at": datetime.now().isoformat(timespec="seconds"),
        "signature_header": "X-Signature",
        "provider_event_id": provider_event_id,
        "payload": payload,
    }
    request["stored_at"] = datetime.now().isoformat(timespec="seconds")
    request["request_file"] = request_filename
    request["raw_event_file"] = event_filename
    request = _request_defaults(request)

    _write_json(EVENTS_DIR / event_filename, event_record)
    _write_json(REQUESTS_DIR / request_filename, request)
    return {
        "ok": True,
        "stored": True,
        "duplicate": False,
        "provider_event_id": provider_event_id,
        "request": request,
    }


def store_relay_bundle(
    raw_body: bytes,
    signature: str,
    secret: str,
) -> dict[str, Any]:
    ensure_queue_dirs()
    if not _verify_signature_hex(raw_body, signature, secret):
        return {"ok": False, "error": "invalid_relay_signature"}

    bundle = json.loads(raw_body.decode("utf-8-sig"))
    raw_request = dict(bundle.get("normalized_request") or {})
    if not raw_request:
        return {"ok": False, "error": "invalid_relay_bundle"}
    request = _request_defaults(raw_request)

    provider_event_id = str(request.get("provider_event_id") or bundle.get("provider_event_id") or "").strip()
    if not provider_event_id:
        provider_event_id = hashlib.sha256(raw_body).hexdigest()[:16]
        request["provider_event_id"] = provider_event_id
    existing = _find_existing_request(provider_event_id)
    if existing:
        return {
            "ok": True,
            "stored": False,
            "duplicate": True,
            "request": _request_defaults(existing),
            "provider_event_id": provider_event_id,
            "relay_event_id": bundle.get("relay_event_id", ""),
        }

    token = _safe_token(provider_event_id)
    stamp = _stamp()
    event_filename = f"relay_event_{stamp}_{token}.json"
    request_filename = f"fulfillment_request_{stamp}_{token}.json"

    event_record = {
        "provider": request.get("provider", bundle.get("provider", "relay")),
        "stored_at": datetime.now().isoformat(timespec="seconds"),
        "signature_header": "X-SQX-Relay-Signature",
        "provider_event_id": provider_event_id,
        "relay_event_id": str(bundle.get("relay_event_id") or ""),
        "bundle": bundle,
    }
    request["stored_at"] = datetime.now().isoformat(timespec="seconds")
    request["request_file"] = request_filename
    request["raw_event_file"] = event_filename
    request["relay_event_id"] = str(bundle.get("relay_event_id") or "")
    request["relay_source"] = str(bundle.get("relay_source") or "trusted_remote_relay")

    request = _request_defaults(request)
    _write_json(EVENTS_DIR / event_filename, event_record)
    _write_json(REQUESTS_DIR / request_filename, request)
    return {
        "ok": True,
        "stored": True,
        "duplicate": False,
        "provider_event_id": provider_event_id,
        "relay_event_id": request.get("relay_event_id"),
        "request": request,
    }


def list_requests() -> list[dict[str, Any]]:
    ensure_queue_dirs()
    rows: list[dict[str, Any]] = []
    for path in sorted(REQUESTS_DIR.glob("fulfillment_request_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        payload["request_file"] = payload.get("request_file") or path.name
        rows.append(_request_summary(payload))
    return rows


def load_request(filename: str) -> dict[str, Any]:
    ensure_queue_dirs()
    return _request_defaults(_load_json(_request_list_path(filename)))


def list_processed_receipts() -> list[dict[str, Any]]:
    ensure_queue_dirs()
    rows: list[dict[str, Any]] = []
    for path in sorted(PROCESSED_DIR.glob("delivery_receipt_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        rows.append(
            {
                "name": path.name,
                "status": payload.get("status", "completed"),
                "request_file": payload.get("request_file"),
                "attempt_number": int(payload.get("attempt_number") or 0),
                "processed_at": payload.get("processed_at"),
                "provider_event_id": payload.get("provider_event_id"),
                "order_id": payload.get("order_id"),
                "delivery_dir": payload.get("delivery_dir"),
                "error": payload.get("error", ""),
            }
        )
    return rows


def queue_overview() -> dict[str, Any]:
    requests = list_requests()
    processed = list_processed_receipts()
    return {
        "requests": requests,
        "processed": processed,
        "summary": _queue_summary(requests, processed),
    }


def update_request_status(*, filename: str, operator_status: str, note: str = "") -> dict[str, Any]:
    ensure_queue_dirs()
    status = str(operator_status or "").strip().lower()
    if status not in REQUEST_OPERATOR_STATUSES:
        raise ValueError(f"unsupported operator_status: {operator_status}")
    path = _request_list_path(filename)
    request = _request_defaults(_load_json(path))
    request["operator_status"] = status
    request["operator_note"] = str(note or "").strip()
    if status == "ignored":
        request["fulfillment_status"] = "ignored_by_operator"
    if status == "queued" and not request.get("eligible_for_fulfillment"):
        request["fulfillment_status"] = "operator_requeued_manual_review"
    request = _save_request(path, request)
    return {"ok": True, "request": request, "summary": _request_summary(request)}


def process_request(
    *,
    filename: str,
    private_key: str,
    zip_path: str,
    support_email: str = "",
    allow_ineligible: bool = False,
) -> dict[str, Any]:
    ensure_queue_dirs()
    path = _request_list_path(filename)
    request = _request_defaults(_load_json(path))
    attempt_number = int(request.get("attempt_count") or 0) + 1
    request["attempt_count"] = attempt_number
    request["last_attempt_at"] = datetime.now().isoformat(timespec="seconds")
    request["operator_status"] = "processing"
    request["last_error"] = ""
    request = _save_request(path, request)
    script = ROOT / "tools" / "fulfill_from_request.ps1"
    args = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-RequestPath",
        str(_request_path(filename)),
        "-PrivateKey",
        private_key,
        "-ZipPath",
        zip_path,
        "-SupportEmail",
        support_email,
    ]
    if allow_ineligible:
        args.append("-AllowIneligible")
    result = subprocess.run(args, text=True, capture_output=True, timeout=120)
    token = _safe_token(str(request.get("provider_event_id") or request.get("order_id") or filename))
    receipt_filename = f"delivery_receipt_{_stamp()}_{token}.json"
    delivery_dir = ""
    for line in result.stdout.splitlines():
        candidate = line.strip()
        if candidate.lower().endswith(".json") or candidate.lower().endswith(".zip"):
            continue
        if "SQX_delivery_" in candidate:
            delivery_dir = candidate
    if result.returncode != 0:
        error_text = (result.stderr or result.stdout or "fulfillment failed").strip()
        request["operator_status"] = "failed"
        request["fulfillment_status"] = "fulfillment_failed"
        request["last_error"] = error_text
        request["processed_receipt_file"] = receipt_filename
        request = _save_request(path, request)
        receipt = {
            "status": "failed",
            "processed_at": datetime.now().isoformat(timespec="seconds"),
            "request_file": filename,
            "attempt_number": attempt_number,
            "provider_event_id": request.get("provider_event_id"),
            "order_id": request.get("order_id"),
            "customer_email": request.get("customer_email"),
            "plan": request.get("plan"),
            "delivery_dir": delivery_dir,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": error_text,
        }
        _write_json(PROCESSED_DIR / receipt_filename, receipt)
        return {"ok": False, "error": "fulfillment_failed", "receipt_file": receipt_filename, "receipt": receipt, "request": request}

    receipt = {
        "status": "completed",
        "processed_at": datetime.now().isoformat(timespec="seconds"),
        "request_file": filename,
        "attempt_number": attempt_number,
        "provider_event_id": request.get("provider_event_id"),
        "order_id": request.get("order_id"),
        "customer_email": request.get("customer_email"),
        "plan": request.get("plan"),
        "delivery_dir": delivery_dir,
        "stdout": result.stdout,
    }
    _write_json(PROCESSED_DIR / receipt_filename, receipt)
    request["operator_status"] = "completed"
    request["fulfillment_status"] = "delivered"
    request["completed_at"] = receipt["processed_at"]
    request["processed_receipt_file"] = receipt_filename
    request["last_delivery_dir"] = delivery_dir
    request["last_error"] = ""
    request = _save_request(path, request)
    return {"ok": True, "receipt_file": receipt_filename, "receipt": receipt, "request": request}
