from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.remote_workspaces import append_workspace_audit_event, public_workspace_context


REMOTE_WORKSPACE_OUTPUT_VERSION = "remote-workspace-output-v1"


def workspace_outputs_dir(workspace_context: Mapping[str, Any]) -> Path:
    paths = workspace_context.get("_paths")
    if not workspace_context.get("ok") or not isinstance(paths, Mapping) or not isinstance(paths.get("outputs"), Path):
        raise ValueError("workspace_outputs_path_missing")
    outputs_dir = paths["outputs"]
    outputs_dir.mkdir(parents=True, exist_ok=True)
    return outputs_dir


def workspace_output_uri(filename: str | None = None) -> str:
    safe_name = Path(str(filename or "")).name.strip()
    return "workspace://outputs/" + safe_name if safe_name else "workspace://outputs"


def list_workspace_outputs(workspace_context: Mapping[str, Any], *, audit: bool = False) -> dict[str, Any]:
    outputs_dir = workspace_outputs_dir(workspace_context)
    files = []
    for path in sorted(outputs_dir.glob("*.cfx"), key=lambda item: item.stat().st_mtime, reverse=True):
        stat = path.stat()
        files.append({
            "name": path.name,
            "path": workspace_output_uri(path.name),
            "size_kb": round(stat.st_size / 1024, 1),
            "mtime": stat.st_mtime,
            "mtime_ms": int(stat.st_mtime * 1000),
        })
    if audit:
        append_workspace_audit_event(workspace_context, {
            "type": "remote_workspace_outputs_list",
            "action": "project_generator_output_list",
            "fileCount": len(files),
            "version": REMOTE_WORKSPACE_OUTPUT_VERSION,
        })
    return {
        "ok": True,
        "version": REMOTE_WORKSPACE_OUTPUT_VERSION,
        "scope": "remote_workspace",
        "output_dir": workspace_output_uri(),
        "output_label": "Workspace outputs",
        "workspace": public_workspace_context(workspace_context),
        "files": files,
        "privacy": {"local_paths_returned": False},
    }


def output_response_fields(workspace_context: Mapping[str, Any], output_path: str | Path) -> dict[str, Any]:
    filename = Path(str(output_path)).name
    return {
        "output_path": workspace_output_uri(filename),
        "output": {
            "version": REMOTE_WORKSPACE_OUTPUT_VERSION,
            "scope": "remote_workspace",
            "output_dir": workspace_output_uri(),
            "filename": filename,
            "workspace": public_workspace_context(workspace_context),
        },
        "privacy": {"local_paths_returned": False},
    }


def record_workspace_output_generated(
    workspace_context: Mapping[str, Any],
    *,
    endpoint: str,
    filename: str,
    capa: int | None = None,
    mining: int | None = None,
) -> dict[str, Any]:
    return append_workspace_audit_event(workspace_context, {
        "type": "remote_workspace_output_generated",
        "action": endpoint,
        "filename": Path(str(filename)).name,
        "capa": capa,
        "mining": mining,
        "version": REMOTE_WORKSPACE_OUTPUT_VERSION,
    })
