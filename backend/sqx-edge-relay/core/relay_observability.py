from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


RELAY_ROOT = Path(__file__).resolve().parents[1]
OBS_ROOT = RELAY_ROOT / "data" / "observability"
LOG_DIR = OBS_ROOT / "logs"
SNAPSHOT_DIR = OBS_ROOT / "snapshots"
EVENT_LOG = LOG_DIR / "relay_events.jsonl"
MAX_LOG_BYTES = 1_000_000


def ensure_observability_dirs() -> None:
    for path in (OBS_ROOT, LOG_DIR, SNAPSHOT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def utc_stamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(token in lowered for token in ("secret", "signature", "token", "authorization")):
                redacted[key] = "[redacted]"
            else:
                redacted[key] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _rotate_if_needed() -> None:
    if not EVENT_LOG.exists() or EVENT_LOG.stat().st_size < MAX_LOG_BYTES:
        return
    rotated = LOG_DIR / f"relay_events_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.jsonl"
    EVENT_LOG.replace(rotated)


def log_event(event_type: str, **fields: Any) -> dict[str, Any]:
    ensure_observability_dirs()
    _rotate_if_needed()
    record = {
        "ts": utc_stamp(),
        "event_type": event_type,
        **_redact(fields),
    }
    with EVENT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def recent_events(limit: int = 50) -> list[dict[str, Any]]:
    ensure_observability_dirs()
    if not EVENT_LOG.exists():
        return []
    lines = EVENT_LOG.read_text(encoding="utf-8-sig").splitlines()[-max(1, min(limit, 500)):]
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def write_snapshot(queue_overview: dict[str, Any], config_status: dict[str, Any]) -> dict[str, Any]:
    ensure_observability_dirs()
    snapshot = {
        "created_at": utc_stamp(),
        "queue": queue_overview,
        "config": config_status,
        "recent_events": recent_events(limit=25),
    }
    filename = f"relay_snapshot_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
    path = SNAPSHOT_DIR / filename
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    log_event("snapshot_created", snapshot_file=filename, summary=queue_overview.get("summary", {}))
    return {"ok": True, "snapshot_file": filename, "snapshot": snapshot}


def observability_status(queue_overview: dict[str, Any]) -> dict[str, Any]:
    ensure_observability_dirs()
    log_size = EVENT_LOG.stat().st_size if EVENT_LOG.exists() else 0
    return {
        "ok": True,
        "log_file": str(EVENT_LOG),
        "snapshot_dir": str(SNAPSHOT_DIR),
        "log_size_bytes": log_size,
        "summary": queue_overview.get("summary", {}),
        "recent_events": recent_events(limit=10),
    }
