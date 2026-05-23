from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^\n\r\t\"'<>|]+")
COOKIE_TOKEN_RE = re.compile(
    r"(?i)\b(?:bearer\s+)?(?:__Host-[A-Za-z0-9_-]+|token|secret|password|grant[_-]?key|api[_-]?key|session)[=:]\s*[A-Za-z0-9._~+/=-]{8,}"
)


def redact_text(value: Any) -> str:
    text = str(value if value is not None else "")
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = URL_RE.sub("[REDACTED_URL]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = COOKIE_TOKEN_RE.sub("[REDACTED_SECRET]", text)
    return text


def redact_data(value: Any, *, max_depth: int = 8) -> Any:
    if max_depth <= 0:
        return "[REDACTED_DEPTH]"
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            key = redact_text(raw_key)
            lowered = str(raw_key).lower()
            if any(marker in lowered for marker in ("token", "secret", "password", "cookie", "grant_key", "protected_url")):
                clean[key] = "[REDACTED_SECRET]"
            elif any(marker in lowered for marker in ("path", "dir", "folder")):
                clean[key] = "[REDACTED_PATH]" if raw_value else raw_value
            elif "email" in lowered:
                clean[key] = "[REDACTED_EMAIL]" if raw_value else raw_value
            else:
                clean[key] = redact_data(raw_value, max_depth=max_depth - 1)
        return clean
    if isinstance(value, list):
        return [redact_data(item, max_depth=max_depth - 1) for item in value[:50]]
    if isinstance(value, tuple):
        return [redact_data(item, max_depth=max_depth - 1) for item in value[:50]]
    if isinstance(value, Path):
        return "[REDACTED_PATH]"
    if isinstance(value, str):
        return redact_text(value)
    return value


def redacted_json(value: Any) -> str:
    return json.dumps(redact_data(value), ensure_ascii=False, sort_keys=True)
