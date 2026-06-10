from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


LOCAL_AI_AGENT_VERSION = "local-ai-agent-v1"
AGENT_AUDIT_VERSION = "local-ai-agent-audit-v1"

RiskLevel = Literal["read", "navigate", "dry_run", "write_confirmed", "blocked"]


@dataclass(frozen=True)
class AgentAction:
    id: str
    label: str
    risk: RiskLevel
    profile: str
    description: str
    requires_confirmation: bool
    ui_command: dict[str, Any] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)

    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "risk": self.risk,
            "profile": self.profile,
            "description": self.description,
            "requiresConfirmation": self.requires_confirmation,
            "inputs": list(self.inputs),
        }


PLAN_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "profile": {"type": "string"},
        "recommendedAction": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "label": {"type": "string"},
                "reason": {"type": "string"},
                "arguments": {"type": "object"},
            },
            "required": ["id", "label", "reason"],
        },
        "blockers": {"type": "array", "items": {"type": "string"}},
        "requiresConfirmation": {"type": "boolean"},
    },
    "required": ["reply", "profile", "recommendedAction", "blockers", "requiresConfirmation"],
}


def safe_plan_response(
    *,
    reply: str,
    profile: str,
    action: AgentAction,
    reason: str,
    blockers: list[str] | None = None,
    arguments: dict[str, Any] | None = None,
    source: str = "heuristic",
) -> dict[str, Any]:
    return {
        "ok": True,
        "version": LOCAL_AI_AGENT_VERSION,
        "source": source,
        "reply": reply,
        "profile": profile,
        "recommendedAction": {
            "id": action.id,
            "label": action.label,
            "risk": action.risk,
            "reason": reason,
            "arguments": arguments or {},
            "requiresConfirmation": action.requires_confirmation,
        },
        "blockers": blockers or [],
        "requiresConfirmation": action.requires_confirmation,
        "privacy": {
            "local_paths_returned": False,
            "raw_email_returned": False,
            "protected_url_returned": False,
            "prompt_persisted": False,
        },
    }
