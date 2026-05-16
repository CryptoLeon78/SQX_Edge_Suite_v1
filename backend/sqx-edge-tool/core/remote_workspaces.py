from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_WORKSPACE_VERSION = "remote-workspace-v1"
WORKSPACE_ROOT_ENV = "SQX_REMOTE_WORKSPACES_ROOT"
DEFAULT_WORKSPACES_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "workspaces"
WORKSPACE_SUBDIRS = ("config", "uploads", "outputs", "exports", "logs", "tmp")
IDENTITY_HASH_RE = re.compile(r"^[a-f0-9]{64}$")


def remote_workspaces_root(configured: str | Path | None = None) -> Path:
    value = str(configured or os.environ.get(WORKSPACE_ROOT_ENV, "")).strip()
    return Path(value).expanduser().resolve(strict=False) if value else DEFAULT_WORKSPACES_ROOT


def workspace_id_from_identity_hash(identity_hash: str) -> str:
    normalized = (identity_hash or "").strip().lower()
    if not IDENTITY_HASH_RE.match(normalized):
        raise ValueError("workspace_identity_hash_invalid")
    return "ws_" + normalized[:24]


def _assert_child_path(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("workspace_path_escape_blocked") from exc
    return resolved_candidate


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _public_workspace(context: Mapping[str, Any]) -> dict[str, Any]:
    workspace = context.get("workspace") if isinstance(context.get("workspace"), Mapping) else {}
    return {
        "id": workspace.get("id"),
        "version": workspace.get("version"),
        "owner_hash": workspace.get("owner_hash"),
        "owner_ref": workspace.get("owner_ref"),
        "entitlement_kind": workspace.get("entitlement_kind"),
        "feature_scope": workspace.get("feature_scope"),
        "layout": list(WORKSPACE_SUBDIRS),
        "paths": {"mode": "server_managed", "local_paths_returned": False},
    }


def public_workspace_context(context: Mapping[str, Any]) -> dict[str, Any]:
    return _public_workspace(context)


def derive_remote_workspace(
    session_status: Mapping[str, Any],
    *,
    create: bool = False,
    root: str | Path | None = None,
) -> dict[str, Any]:
    if not bool((session_status.get("access") or {}).get("allowed")):
        return {
            "ok": False,
            "version": REMOTE_WORKSPACE_VERSION,
            "error": "remote_session_required",
            "http_status": 403,
            "workspace": None,
        }
    session = session_status.get("session") if isinstance(session_status.get("session"), Mapping) else {}
    entitlement = session_status.get("entitlement") if isinstance(session_status.get("entitlement"), Mapping) else {}
    identity_hash = str(session.get("email_hash") or "").strip().lower()
    try:
        workspace_id = workspace_id_from_identity_hash(identity_hash)
    except ValueError as exc:
        return {
            "ok": False,
            "version": REMOTE_WORKSPACE_VERSION,
            "error": str(exc),
            "http_status": 403,
            "workspace": None,
        }

    base_root = remote_workspaces_root(root)
    workspace_path = _assert_child_path(base_root, base_root / workspace_id)
    paths = {name: _assert_child_path(workspace_path, workspace_path / name) for name in WORKSPACE_SUBDIRS}
    manifest_path = _assert_child_path(workspace_path, workspace_path / "workspace_manifest.local.json")
    workspace = {
        "id": workspace_id,
        "version": REMOTE_WORKSPACE_VERSION,
        "owner_hash": identity_hash,
        "owner_ref": session.get("email_ref"),
        "entitlement_kind": entitlement.get("kind") or session.get("entitlement_kind"),
        "feature_scope": (session_status.get("access") or {}).get("feature_scope") or session.get("feature_scope"),
    }
    context = {
        "ok": True,
        "version": REMOTE_WORKSPACE_VERSION,
        "workspace": workspace,
        "_path": workspace_path,
        "_paths": paths,
        "_manifest_path": manifest_path,
    }
    if create:
        ensure_remote_workspace(context)
    return context


def ensure_remote_workspace(context: Mapping[str, Any]) -> None:
    if not context.get("ok"):
        return
    workspace_path = context.get("_path")
    paths = context.get("_paths")
    manifest_path = context.get("_manifest_path")
    workspace = context.get("workspace") if isinstance(context.get("workspace"), Mapping) else {}
    if not isinstance(workspace_path, Path) or not isinstance(paths, Mapping) or not isinstance(manifest_path, Path):
        raise ValueError("workspace_context_paths_missing")
    workspace_path.mkdir(parents=True, exist_ok=True)
    for path in paths.values():
        if isinstance(path, Path):
            path.mkdir(parents=True, exist_ok=True)
    now = _utc_now()
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                manifest = loaded
        except (OSError, json.JSONDecodeError):
            manifest = {}
    created_at = str(manifest.get("createdAt") or now)
    manifest = {
        "schemaVersion": REMOTE_WORKSPACE_VERSION,
        "workspaceId": workspace.get("id"),
        "ownerHash": workspace.get("owner_hash"),
        "ownerRef": workspace.get("owner_ref"),
        "entitlementKind": workspace.get("entitlement_kind"),
        "featureScope": workspace.get("feature_scope"),
        "layout": list(WORKSPACE_SUBDIRS),
        "createdAt": created_at,
        "updatedAt": now,
        "privacy": {"raw_email_stored": False, "local_paths_public": False},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def append_workspace_audit_event(context: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, Any]:
    if not context.get("ok"):
        raise ValueError("workspace_context_invalid")
    paths = context.get("_paths")
    workspace = context.get("workspace") if isinstance(context.get("workspace"), Mapping) else {}
    if not isinstance(paths, Mapping) or not isinstance(paths.get("logs"), Path):
        raise ValueError("workspace_logs_path_missing")
    logs_dir = paths["logs"]
    logs_dir.mkdir(parents=True, exist_ok=True)
    audit_path = logs_dir / "audit.local.jsonl"
    payload = {
        **dict(event),
        "workspaceId": workspace.get("id"),
        "workspaceVersion": REMOTE_WORKSPACE_VERSION,
        "timestamp": event.get("timestamp") or _utc_now(),
    }
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return {
        "ok": True,
        "audit_event": {
            "type": payload.get("type"),
            "workspace_id": payload.get("workspaceId"),
            "timestamp": payload.get("timestamp"),
        },
        "privacy": {"local_path_returned": False},
    }
