from __future__ import annotations

from typing import Any

from .schemas import AgentAction


EDGE_STAGE_TO_TOOL = {
    "session": "inicio",
    "asset": "activos",
    "capa1-generate": "projectgen",
    "capa1-analyze": "templatemaker",
    "c2-template": "templatemaker",
    "capa2-generate": "projectgen",
    "capa2-analyze": "workflow",
    "portfolio": "cvc",
}

EDGE_STAGE_LABELS = {
    "session": "Punto de partida",
    "asset": "Elegir edge",
    "capa1-generate": "Generar Capa 1",
    "capa1-analyze": "Certificar Capa 1",
    "c2-template": "Crear Template C2",
    "capa2-generate": "Generar Capa 2",
    "capa2-analyze": "Revisar Capa 2",
    "portfolio": "Portfolio",
}

TOOLS = {
    "inicio": "Control Panel",
    "activos": "Activos",
    "pipeline": "Mining Control",
    "views": "SQX Views",
    "projectgen": "Project Generator",
    "templatemaker": "Template Maker",
    "estrategias": "Strategy Control",
    "cvc": "Champion vs Challenger",
    "filtros": "BlockSettings Info",
    "workflow": "Edge Factory",
}


def _open_tool_action(tool_id: str, profile: str) -> AgentAction:
    return AgentAction(
        id=f"open_tool:{tool_id}",
        label=f"Abrir {TOOLS.get(tool_id, tool_id)}",
        risk="navigate",
        profile=profile,
        description="Navega a una herramienta interna sin modificar datos.",
        requires_confirmation=True,
        ui_command={"type": "open_tool", "tool": tool_id},
        inputs=["tool"],
    )


def build_action_catalog(_profiles: dict[str, Any] | None = None) -> dict[str, AgentAction]:
    actions: dict[str, AgentAction] = {
        "refresh_status": AgentAction(
            id="refresh_status",
            label="Refrescar estado",
            risk="read",
            profile="session",
            description="Comprueba estado local del agente y readiness de la app.",
            requires_confirmation=False,
            ui_command={"type": "refresh_agent_status"},
        ),
        "explain_next": AgentAction(
            id="explain_next",
            label="Explicar siguiente paso",
            risk="read",
            profile="orchestrator",
            description="Resume el siguiente paso sin ejecutar nada.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "capabilities_help": AgentAction(
            id="capabilities_help",
            label="Explicar capacidades del agente",
            risk="read",
            profile="orchestrator",
            description="Explica qué puede y no puede hacer el agente local sin ejecutar acciones.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "inspect_inbox": AgentAction(
            id="inspect_inbox",
            label="Revisar bandeja local",
            risk="dry_run",
            profile="inbox",
            description="Lista nombres redactados de archivos en .local/agent_inbox/incoming.",
            requires_confirmation=True,
            ui_command={"type": "inspect_inbox"},
        ),
        "sqx142_compat_help": AgentAction(
            id="sqx142_compat_help",
            label="Explicar compatibilidad SQX 142/143/144",
            risk="read",
            profile="sqx142-compat",
            description="Resume runtime, procesos, ledger y estado de backport SQX local sin ejecutar cambios.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "sqx142_performance_help": AgentAction(
            id="sqx142_performance_help",
            label="Analizar rendimiento SQX 142",
            risk="read",
            profile="sqx142-performance",
            description="Resume perfil JVM, recursos, disco, views, evidencias y siguiente accion recomendada sin ejecutar cambios.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "sqx_c1_config_help": AgentAction(
            id="sqx_c1_config_help",
            label="Explicar C1-CONFIG1",
            risk="read",
            profile="sqx-c1-config",
            description="Resume fase Capa1 config, ledger local, reglas de promocion selectiva y siguiente paso sin ejecutar cambios.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "sqx_test_guardian_help": AgentAction(
            id="sqx_test_guardian_help",
            label="Recomendar checks SQX",
            risk="read",
            profile="sqx-test-guardian",
            description="Recomienda matriz de checks read-only/dry-run para la fase activa sin ejecutar mutaciones.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "sqx_docs_curator_help": AgentAction(
            id="sqx_docs_curator_help",
            label="Revisar docs SQX",
            risk="read",
            profile="sqx-docs-curator",
            description="Explica docs, manifest y governance pendientes sin inventar estado ni exponer evidencia privada.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "sqx_academic_lopez_help": AgentAction(
            id="sqx_academic_lopez_help",
            label="Consulta academica SQX",
            risk="read",
            profile="sqx-academic-lopez",
            description="Resume criterio academico para OOS, Monte Carlo, data snooping y robustez sin ejecutar mutaciones.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
        "sqx_agent_skills_help": AgentAction(
            id="sqx_agent_skills_help",
            label="Explicar agentes y skills",
            risk="read",
            profile="sqx-agent-skills",
            description="Resume guardianes, handoffs, uso paralelo permitido y limites de autonomia.",
            requires_confirmation=False,
            ui_command={"type": "none"},
        ),
    }
    for stage, tool_id in EDGE_STAGE_TO_TOOL.items():
        actions[f"open_stage_tool:{stage}"] = AgentAction(
            id=f"open_stage_tool:{stage}",
            label=f"Abrir herramienta de {EDGE_STAGE_LABELS.get(stage, stage)}",
            risk="navigate",
            profile=stage,
            description="Abre la herramienta recomendada para la etapa activa de Edge Factory.",
            requires_confirmation=True,
            ui_command={"type": "open_tool", "tool": tool_id, "stage": stage},
            inputs=["stage"],
        )
        actions[f"mark_step:{stage}"] = AgentAction(
            id=f"mark_step:{stage}",
            label=f"Marcar {EDGE_STAGE_LABELS.get(stage, stage)} como completado",
            risk="write_confirmed",
            profile=stage,
            description="Marca una etapa Edge Factory como completada solo tras confirmacion explicita.",
            requires_confirmation=True,
            ui_command={"type": "complete_step", "stage": stage, "done": True},
            inputs=["stage", "done"],
        )
    for tool_id in TOOLS:
        actions[f"open_tool:{tool_id}"] = _open_tool_action(tool_id, "tool")
    return actions


def public_capabilities(profiles: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [action.public() for action in build_action_catalog(profiles).values()]


def recommended_action_for_stage(stage: str) -> str:
    normalized = stage if stage in EDGE_STAGE_TO_TOOL else "session"
    return f"open_stage_tool:{normalized}"
