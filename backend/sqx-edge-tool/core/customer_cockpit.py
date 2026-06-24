from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


from core.app_paths import app_root

TOOL_ROOT = app_root()
DEFAULT_CONFIG_PATH = TOOL_ROOT / "config" / "customer_cockpit.json"
DEFAULT_SUCCESS_DIR = TOOL_ROOT / "data" / "customer_success_renewal"
DEFAULT_LIMIT = 12


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def mask_email(value: str) -> str:
    email = (value or "").strip()
    if not email or "@" not in email:
        return ""
    user, domain = email.split("@", 1)
    prefix = user[:2] if len(user) > 2 else user[:1]
    return f"{prefix}***@{domain}"


def customer_ref(record: dict[str, Any]) -> str:
    return (record.get("customer_id") or mask_email(record.get("customer_email", "")) or "customer_pending").strip()


def decision_label(value: str) -> str:
    labels = {
        "maintain_pro": "Mantener Pro",
        "renew": "Renovar",
        "upsell_templates": "Plantillas",
        "offer_setup_assist": "Setup Assist",
        "improve_onboarding": "Mejorar onboarding",
        "pause_or_refund_review": "Revisar pausa/refund",
    }
    return labels.get(value or "", value or "Sin decision")


def risk_level(record: dict[str, Any]) -> str:
    if safe_int(record.get("support_tickets_open")) > 0:
        return "support"
    if safe_int(record.get("activation_errors")) > 0:
        return "activation"
    if safe_int(record.get("refund_risk_flags")) > 0:
        return "refund"
    if not record.get("activation_confirmed"):
        return "activation"
    return "ok"


def next_action(record: dict[str, Any]) -> str:
    risk = risk_level(record)
    decision = record.get("renewal_decision") or ""
    if risk == "support":
        return "Cerrar tickets abiertos antes de renovar."
    if risk == "activation":
        return "Confirmar activacion Pro y eliminar friccion inicial."
    if risk == "refund":
        return "Revisar riesgo de refund con soporte."
    if decision == "upsell_templates":
        return "Preparar oferta de Template Pack."
    if decision == "offer_setup_assist":
        return "Preparar propuesta Setup Assist."
    if decision == "renew":
        return "Contactar renovacion dentro de la ventana."
    return "Mantener seguimiento de valor."


def sanitize_record(record: dict[str, Any], source: str) -> dict[str, Any]:
    renewal_decision = record.get("renewal_decision") or record.get("decision") or ""
    opportunities = record.get("opportunities") if isinstance(record.get("opportunities"), dict) else {}
    return {
        "customer_ref": customer_ref(record),
        "plan": record.get("plan") or "unknown",
        "success_owner": record.get("success_owner") or "sin owner",
        "activation_confirmed": bool(record.get("activation_confirmed")),
        "support_tickets_open": safe_int(record.get("support_tickets_open")),
        "activation_errors": safe_int(record.get("activation_errors")),
        "refund_risk_flags": safe_int(record.get("refund_risk_flags")),
        "value_checkins_completed": safe_int(record.get("value_checkins_completed")),
        "days_to_renewal": safe_int(record.get("days_to_renewal"), 999),
        "renewal_decision": renewal_decision,
        "renewal_label": decision_label(renewal_decision),
        "risk": risk_level(record),
        "next_action": record.get("next_action") or next_action(record),
        "opportunities": {
            "template_pack": bool(record.get("template_pack_offer_ready") or opportunities.get("template_pack")),
            "setup_assist": bool(record.get("setup_assist_offer_ready") or opportunities.get("setup_assist")),
        },
        "source": source,
    }


def load_configured_records(config_path: Path = DEFAULT_CONFIG_PATH) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not config_path.is_file():
        return {}, []
    payload = load_json(config_path)
    records = payload.get("customers") if isinstance(payload.get("customers"), list) else []
    return payload, [sanitize_record(item, "config") for item in records if isinstance(item, dict)]


def load_success_records(success_dir: Path = DEFAULT_SUCCESS_DIR, limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
    if not success_dir.is_dir():
        return []
    files = sorted(success_dir.glob("customer_success_renewal_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    records: list[dict[str, Any]] = []
    for path in files[:limit]:
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        records.append(sanitize_record(payload, path.name))
    return records


def summary_from(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "customers": len(records),
        "active": sum(1 for item in records if item.get("activation_confirmed")),
        "renewal_due": sum(1 for item in records if safe_int(item.get("days_to_renewal"), 999) <= 14),
        "support_open": sum(safe_int(item.get("support_tickets_open")) for item in records),
        "activation_errors": sum(safe_int(item.get("activation_errors")) for item in records),
        "refund_risk": sum(safe_int(item.get("refund_risk_flags")) for item in records),
        "template_opportunities": sum(1 for item in records if item.get("opportunities", {}).get("template_pack")),
        "setup_assist_opportunities": sum(1 for item in records if item.get("opportunities", {}).get("setup_assist")),
    }


def cockpit_overview(
    config_path: Path = DEFAULT_CONFIG_PATH,
    success_dir: Path = DEFAULT_SUCCESS_DIR,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    config, configured_records = load_configured_records(config_path)
    success_records = load_success_records(success_dir, limit=limit)
    records = (success_records + configured_records)[:limit]
    privacy = config.get("privacy") if isinstance(config.get("privacy"), dict) else {}
    return {
        "ok": True,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "state": "customer_cockpit_ready",
        "privacy": {
            "mode": privacy.get("mode", "redacted_operator_summary"),
            "safe_to_render": bool(privacy.get("safeToRender", True)),
            "excluded": privacy.get("excluded") or [
                "license payloads",
                "private keys",
                "raw checkout events",
                "relay secrets",
            ],
        },
        "summary": summary_from(records),
        "customers": records,
        "sources": {
            "config": str(config_path),
            "customer_success_renewal_dir": str(success_dir),
            "configured_records": len(configured_records),
            "success_records": len(success_records),
        },
    }
