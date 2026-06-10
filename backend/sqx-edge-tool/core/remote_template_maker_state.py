from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_workspaces import append_workspace_audit_event, public_workspace_context


REMOTE_TEMPLATE_MAKER_STATE_VERSION = "remote-template-maker-state-v1"
REMOTE_TEMPLATE_MAKER_DB = "template_maker.sqlite"
REMOTE_TEMPLATE_MAKER_SNAPSHOT_KEY = "template_maker_snapshot"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _template_maker_db_path(workspace_context: Mapping[str, Any]) -> Path:
    paths = workspace_context.get("_paths")
    if not workspace_context.get("ok") or not isinstance(paths, Mapping) or not isinstance(paths.get("config"), Path):
        raise ValueError("workspace_config_path_missing")
    config_dir = paths["config"]
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / REMOTE_TEMPLATE_MAKER_DB


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS template_maker_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return conn


def empty_template_maker_snapshot() -> dict[str, Any]:
    return {
        "schemaVersion": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
        "templateMakerSchemaVersion": "sqx-edge-correlation-review-c2-v1",
        "strategies": [],
        "config": {
            "currentCapa": 1,
            "currentPreset": "Generic",
            "thresholds": None,
            "diversitySettings": None,
        },
        "metadata": {
            "source": "empty",
            "recordCount": 0,
            "updatedAt": None,
        },
    }


def _normalize_snapshot(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(snapshot or {})
    strategies = source.get("strategies") if isinstance(source.get("strategies"), list) else []
    config = source.get("config") if isinstance(source.get("config"), Mapping) else {}
    metadata = source.get("metadata") if isinstance(source.get("metadata"), Mapping) else {}
    try:
        current_capa = int(config.get("currentCapa") or 1)
    except (TypeError, ValueError):
        current_capa = 1
    normalized = {
        "schemaVersion": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
        "templateMakerSchemaVersion": str(source.get("templateMakerSchemaVersion") or "sqx-edge-correlation-review-c2-v1"),
        "strategies": strategies,
        "config": {
            "currentCapa": 2 if current_capa == 2 else 1,
            "currentPreset": str(config.get("currentPreset") or "Generic"),
            "thresholds": config.get("thresholds") if isinstance(config.get("thresholds"), Mapping) else None,
            "diversitySettings": config.get("diversitySettings") if isinstance(config.get("diversitySettings"), Mapping) else None,
        },
        "metadata": {
            "source": str(metadata.get("source") or source.get("source") or "dashboard"),
            "recordCount": len(strategies),
            "updatedAt": str(metadata.get("updatedAt") or _utc_now()),
        },
    }
    return normalized


def read_template_maker_state(workspace_context: Mapping[str, Any], *, audit: bool = False) -> dict[str, Any]:
    path = _template_maker_db_path(workspace_context)
    snapshot = empty_template_maker_snapshot()
    if path.is_file():
        with _connect(path) as conn:
            row = conn.execute(
                "SELECT value, updated_at FROM template_maker_state WHERE key = ?",
                (REMOTE_TEMPLATE_MAKER_SNAPSHOT_KEY,),
            ).fetchone()
            if row:
                try:
                    loaded = json.loads(row[0])
                    if isinstance(loaded, Mapping):
                        snapshot = _normalize_snapshot(loaded)
                        snapshot["metadata"]["updatedAt"] = row[1]
                except json.JSONDecodeError:
                    snapshot = empty_template_maker_snapshot()
    if audit:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_template_maker_state_read",
            "action": "template_maker_bootstrap",
            "recordCount": len(snapshot.get("strategies") or []),
            "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
        })
    return snapshot


def write_template_maker_state(
    workspace_context: Mapping[str, Any],
    snapshot: Mapping[str, Any] | None,
    *,
    source: str = "dashboard",
) -> dict[str, Any]:
    incoming_metadata = (snapshot or {}).get("metadata") if isinstance(snapshot, Mapping) else {}
    if not isinstance(incoming_metadata, Mapping):
        incoming_metadata = {}
    normalized = _normalize_snapshot({
        **dict(snapshot or {}),
        "source": source,
        "metadata": {
            **dict(incoming_metadata),
            "source": source,
            "updatedAt": _utc_now(),
        },
    })
    path = _template_maker_db_path(workspace_context)
    encoded = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO template_maker_state(key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (REMOTE_TEMPLATE_MAKER_SNAPSHOT_KEY, encoded, normalized["metadata"]["updatedAt"]),
        )
    audit = append_workspace_audit_event(workspace_context, {
        "type": "remote_template_maker_state_write",
        "action": "template_maker_save",
        "source": source,
        "recordCount": len(normalized.get("strategies") or []),
        "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
    })
    return {
        "ok": True,
        "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
        "workspace": public_workspace_context(workspace_context),
        "recordCount": len(normalized.get("strategies") or []),
        "metadata": normalized.get("metadata") or {},
        "audit": audit.get("audit_event"),
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }


def template_maker_state_public_status(workspace_context: Mapping[str, Any]) -> dict[str, Any]:
    path = _template_maker_db_path(workspace_context)
    snapshot = read_template_maker_state(workspace_context)
    return {
        "ok": True,
        "version": REMOTE_TEMPLATE_MAKER_STATE_VERSION,
        "workspace": public_workspace_context(workspace_context),
        "recordCount": len(snapshot.get("strategies") or []),
        "metadata": snapshot.get("metadata") or {},
        "storage": {
            "mode": "workspace_sqlite",
            "dbName": REMOTE_TEMPLATE_MAKER_DB,
            "exists": path.is_file(),
        },
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }
