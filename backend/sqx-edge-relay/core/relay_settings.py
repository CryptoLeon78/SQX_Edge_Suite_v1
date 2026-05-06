from __future__ import annotations

import os
from typing import Any


DEFAULT_TARGET_URL = "http://127.0.0.1:5050/api/fulfillment/relay-ingest"
DEFAULT_WORKER_INTERVAL_SECONDS = 30
DEFAULT_WORKER_LIMIT = 10


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def lemon_secret() -> str:
    return env_value("SQX_LEMON_WEBHOOK_SECRET")


def relay_secret() -> str:
    return env_value("SQX_FULFILLMENT_RELAY_SECRET")


def operator_token() -> str:
    return env_value("SQX_RELAY_OPERATOR_TOKEN")


def target_url() -> str:
    return env_value("SQX_LOCAL_INGEST_URL", DEFAULT_TARGET_URL)


def worker_interval_seconds() -> int:
    value = env_value("SQX_RELAY_WORKER_INTERVAL_SECONDS", str(DEFAULT_WORKER_INTERVAL_SECONDS))
    try:
        return max(5, int(value))
    except ValueError:
        return DEFAULT_WORKER_INTERVAL_SECONDS


def worker_limit() -> int:
    value = env_value("SQX_RELAY_WORKER_LIMIT", str(DEFAULT_WORKER_LIMIT))
    try:
        return max(1, min(100, int(value)))
    except ValueError:
        return DEFAULT_WORKER_LIMIT


def is_operator_authorized(headers: Any) -> bool:
    expected = operator_token()
    if not expected:
        return True
    provided = str(headers.get("X-SQX-Operator-Token", "") or "").strip()
    bearer = str(headers.get("Authorization", "") or "").strip()
    if bearer.lower().startswith("bearer "):
        provided = bearer[7:].strip()
    return provided == expected


def config_status() -> dict[str, Any]:
    missing = []
    warnings = []
    if not lemon_secret():
        missing.append("SQX_LEMON_WEBHOOK_SECRET")
    if not relay_secret():
        missing.append("SQX_FULFILLMENT_RELAY_SECRET")
    if not operator_token():
        warnings.append("SQX_RELAY_OPERATOR_TOKEN is not set; operator endpoints are unprotected.")
    if target_url() == DEFAULT_TARGET_URL:
        warnings.append("SQX_LOCAL_INGEST_URL uses the local default target.")
    return {
        "ok": not missing,
        "production_ready": not missing and bool(operator_token()),
        "missing": missing,
        "warnings": warnings,
        "target_url": target_url(),
        "operator_token_configured": bool(operator_token()),
        "worker_interval_seconds": worker_interval_seconds(),
        "worker_limit": worker_limit(),
    }
