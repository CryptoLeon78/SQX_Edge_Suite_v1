from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from core.remote_workspaces import append_workspace_audit_event, public_workspace_context


REMOTE_WORKSPACE_STATE_VERSION = "remote-workspace-state-v1"
REMOTE_WORKSPACE_STATE_DB = "workspace_state.sqlite"

REMOTE_STATE_KEYS: dict[str, str] = {
    "planUser": "sqx_plan_user_v1",
    "pipelineState": "sqx_pipeline_state_v1",
    "strategiesUser": "sqx_strategies_user_v1",
    "strategiesDeleted": "sqx_strategies_deleted_v1",
    "sqxReadinessStatus": "sqx_readiness_status_v1",
    "viewCreatorPresets": "sqx_view_creator_presets_v1",
    "edgeFactoryState": "sqx_edge_factory_state_v1",
}

ALLOWED_REMOTE_STATE_KEYS = frozenset(REMOTE_STATE_KEYS.values())


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_db_path(workspace_context: Mapping[str, Any]) -> Path:
    paths = workspace_context.get("_paths")
    if not workspace_context.get("ok") or not isinstance(paths, Mapping) or not isinstance(paths.get("config"), Path):
        raise ValueError("workspace_state_config_path_missing")
    config_dir = paths["config"]
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / REMOTE_WORKSPACE_STATE_DB


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS state_kv (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS state_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "INSERT OR REPLACE INTO state_meta(key, value) VALUES(?, ?)",
        ("schemaVersion", REMOTE_WORKSPACE_STATE_VERSION),
    )
    connection.commit()
    return connection


def _safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _validate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, value in dict(payload or {}).items():
        if key not in ALLOWED_REMOTE_STATE_KEYS:
            continue
        _safe_json(value)
        clean[key] = value
    return clean


def read_workspace_state(
    workspace_context: Mapping[str, Any],
    keys: Sequence[str] | None = None,
    *,
    audit: bool = False,
) -> dict[str, Any]:
    path = _state_db_path(workspace_context)
    requested = [key for key in (keys or ALLOWED_REMOTE_STATE_KEYS) if key in ALLOWED_REMOTE_STATE_KEYS]
    if not requested:
        requested = sorted(ALLOWED_REMOTE_STATE_KEYS)
    state: dict[str, Any] = {}
    with _connect(path) as connection:
        placeholders = ",".join("?" for _ in requested)
        rows = connection.execute(
            f"SELECT key, value_json FROM state_kv WHERE key IN ({placeholders})",
            requested,
        ).fetchall()
    for row in rows:
        try:
            state[str(row["key"])] = json.loads(str(row["value_json"]))
        except json.JSONDecodeError:
            state[str(row["key"])] = None
    if audit:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_state_read",
            "action": "bootstrap",
            "stateKeys": sorted(state.keys()),
        })
    return state


def write_workspace_state(
    workspace_context: Mapping[str, Any],
    payload: Mapping[str, Any],
    *,
    source: str = "dashboard",
) -> dict[str, Any]:
    clean = _validate_payload(payload)
    if not clean:
        return {
            "ok": False,
            "version": REMOTE_WORKSPACE_STATE_VERSION,
            "error": "remote_state_no_allowed_keys",
            "savedKeys": [],
            "privacy": {"local_paths_returned": False},
        }
    path = _state_db_path(workspace_context)
    now = _utc_now()
    with _connect(path) as connection:
        for key, value in clean.items():
            connection.execute(
                """
                INSERT INTO state_kv(key, value_json, updated_at)
                VALUES(?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json=excluded.value_json,
                    updated_at=excluded.updated_at
                """,
                (key, _safe_json(value), now),
            )
        connection.commit()
    audit = append_workspace_audit_event(workspace_context, {
        "type": "remote_workspace_state_write",
        "action": source,
        "stateKeys": sorted(clean.keys()),
    })
    return {
        "ok": True,
        "version": REMOTE_WORKSPACE_STATE_VERSION,
        "savedKeys": sorted(clean.keys()),
        "workspace": public_workspace_context(workspace_context),
        "audit": audit.get("audit_event"),
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }


def workspace_state_public_status(workspace_context: Mapping[str, Any]) -> dict[str, Any]:
    path = _state_db_path(workspace_context)
    state = read_workspace_state(workspace_context)
    return {
        "ok": True,
        "version": REMOTE_WORKSPACE_STATE_VERSION,
        "workspace": public_workspace_context(workspace_context),
        "stateKeys": sorted(state.keys()),
        "configuredKeys": dict(REMOTE_STATE_KEYS),
        "storage": {
            "mode": "workspace_sqlite",
            "dbName": REMOTE_WORKSPACE_STATE_DB,
            "local_path_returned": False,
            "exists": path.is_file(),
        },
        "privacy": {"local_paths_returned": False, "raw_email_returned": False},
    }
