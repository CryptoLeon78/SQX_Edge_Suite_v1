from __future__ import annotations

import hashlib
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

    (EVENTS_DIR / event_filename).write_text(json.dumps(event_record, indent=2, sort_keys=True), encoding="utf-8")
    (REQUESTS_DIR / request_filename).write_text(json.dumps(request, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": True,
        "stored": True,
        "duplicate": False,
        "provider_event_id": provider_event_id,
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
        rows.append(
            {
                "name": path.name,
                "provider": payload.get("provider"),
                "source_event": payload.get("source_event"),
                "provider_event_id": payload.get("provider_event_id"),
                "order_id": payload.get("order_id"),
                "customer_email": payload.get("customer_email"),
                "plan": payload.get("plan"),
                "eligible_for_fulfillment": bool(payload.get("eligible_for_fulfillment")),
                "fulfillment_status": payload.get("fulfillment_status"),
                "stored_at": payload.get("stored_at"),
            }
        )
    return rows


def load_request(filename: str) -> dict[str, Any]:
    ensure_queue_dirs()
    path = _request_path(filename)
    if not path.is_file():
        raise FileNotFoundError(filename)
    return _load_json(path)


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
                "request_file": payload.get("request_file"),
                "processed_at": payload.get("processed_at"),
                "provider_event_id": payload.get("provider_event_id"),
                "order_id": payload.get("order_id"),
                "delivery_dir": payload.get("delivery_dir"),
            }
        )
    return rows


def process_request(
    *,
    filename: str,
    private_key: str,
    zip_path: str,
    support_email: str = "",
    allow_ineligible: bool = False,
) -> dict[str, Any]:
    ensure_queue_dirs()
    request = load_request(filename)
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
    if result.returncode != 0:
        return {
            "ok": False,
            "error": "fulfillment_failed",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "request": request,
        }

    token = _safe_token(str(request.get("provider_event_id") or request.get("order_id") or filename))
    receipt_filename = f"delivery_receipt_{_stamp()}_{token}.json"
    delivery_dir = ""
    for line in result.stdout.splitlines():
        candidate = line.strip()
        if candidate.lower().endswith(".json") or candidate.lower().endswith(".zip"):
            continue
        if "SQX_delivery_" in candidate:
            delivery_dir = candidate
    receipt = {
        "processed_at": datetime.now().isoformat(timespec="seconds"),
        "request_file": filename,
        "provider_event_id": request.get("provider_event_id"),
        "order_id": request.get("order_id"),
        "customer_email": request.get("customer_email"),
        "plan": request.get("plan"),
        "delivery_dir": delivery_dir,
        "stdout": result.stdout,
    }
    (PROCESSED_DIR / receipt_filename).write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return {"ok": True, "receipt_file": receipt_filename, "receipt": receipt}
