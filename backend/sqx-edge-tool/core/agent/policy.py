from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from .schemas import AgentAction, LOCAL_AI_AGENT_VERSION


CONFIRMATION_TTL_SECONDS = 300
_CONFIRMATIONS: dict[str, dict[str, Any]] = {}


def is_action_allowed(action: AgentAction | None, *, confirmed: bool = False) -> tuple[bool, str]:
    if not action:
        return False, "agent_action_unknown"
    if action.risk == "blocked":
        return False, "agent_action_blocked"
    if action.requires_confirmation and not confirmed:
        return False, "agent_action_confirmation_required"
    return True, "allowed"


def create_confirmation(action: AgentAction, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    token = secrets.token_urlsafe(24)
    now = datetime.now(timezone.utc)
    _CONFIRMATIONS[token] = {
        "actionId": action.id,
        "arguments": arguments or {},
        "createdAt": now,
        "expiresAt": now + timedelta(seconds=CONFIRMATION_TTL_SECONDS),
    }
    return {
        "ok": True,
        "version": LOCAL_AI_AGENT_VERSION,
        "confirmation": {
            "token": token,
            "actionId": action.id,
            "expiresInSeconds": CONFIRMATION_TTL_SECONDS,
            "requiresConfirmation": action.requires_confirmation,
        },
        "privacy": {"prompt_persisted": False, "local_paths_returned": False},
    }


def consume_confirmation(token: str, action_id: str) -> tuple[bool, str]:
    record = _CONFIRMATIONS.pop(str(token or ""), None)
    if not record:
        return False, "agent_confirmation_missing"
    if record.get("actionId") != action_id:
        return False, "agent_confirmation_action_mismatch"
    expires = record.get("expiresAt")
    if not isinstance(expires, datetime) or expires < datetime.now(timezone.utc):
        return False, "agent_confirmation_expired"
    return True, "confirmed"
