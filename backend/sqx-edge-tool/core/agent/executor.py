from __future__ import annotations

from pathlib import Path
from typing import Any

from .redaction import redact_text
from .schemas import AgentAction, LOCAL_AI_AGENT_VERSION


def inspect_agent_inbox(project_root: Path) -> dict[str, Any]:
    inbox = project_root / ".local" / "agent_inbox" / "incoming"
    inbox.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(inbox.iterdir()):
        if not path.is_file():
            continue
        files.append({
            "name": redact_text(path.name),
            "size": path.stat().st_size,
            "modified": path.stat().st_mtime,
        })
    return {
        "ok": True,
        "files": files[:50],
        "count": len(files),
        "privacy": {"local_paths_returned": False, "file_content_returned": False},
    }


def execute_action(action: AgentAction, *, arguments: dict[str, Any] | None = None, project_root: Path | None = None) -> dict[str, Any]:
    args = arguments or {}
    if action.id == "inspect_inbox":
        result = inspect_agent_inbox(project_root or Path.cwd())
        return {
            "ok": True,
            "version": LOCAL_AI_AGENT_VERSION,
            "action": action.public(),
            "result": result,
            "privacy": {"prompt_persisted": False, "local_paths_returned": False},
        }
    return {
        "ok": True,
        "version": LOCAL_AI_AGENT_VERSION,
        "action": action.public(),
        "uiCommand": action.ui_command,
        "arguments": args,
        "result": {
            "message": "Accion validada. El navegador aplicara el comando permitido.",
        },
        "privacy": {"prompt_persisted": False, "local_paths_returned": False},
    }
