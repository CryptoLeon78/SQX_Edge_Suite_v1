from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
SUPPORT_INCIDENT_VERSION = "support-incident-v1"
DEFAULT_SUPPORT_CASES_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "support_cases"
DEFAULT_SUPPORT_CASES_PATH = DEFAULT_SUPPORT_CASES_ROOT / "support_cases.local.jsonl"

ALLOWED_CATEGORIES = {"access", "session", "workspace", "generation", "export", "ui", "other"}
ALLOWED_SEVERITIES = {"low", "medium", "high", "blocker"}
ALLOWED_STATUSES = {"open", "triaged", "resolved", "dismissed"}

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)
WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:[\\/][^\r\n<>'\"]+")
COOKIE_RE = re.compile(r"(__Host-sqx_remote_session|CF_Authorization|cf_clearance)=\S+", re.IGNORECASE)
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}", re.IGNORECASE)
SECRET_ASSIGNMENT_RE = re.compile(
    r"\b([A-Z0-9_]*(?:SECRET|TOKEN|KEY|PASSWORD|COOKIE)[A-Z0-9_]*)\s*[:=]\s*([^\s,;]+)",
    re.IGNORECASE,
)
LONG_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_\-]{40,}\b")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def redact_support_text(value: Any) -> str:
    """Redact common private markers before incident text is persisted."""
    text = str(value or "").replace("\x00", "").strip()
    if not text:
        return ""
    text = COOKIE_RE.sub("[REDACTED_COOKIE]", text)
    text = BEARER_RE.sub("Bearer [REDACTED_TOKEN]", text)
    text = SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}=[REDACTED_SECRET]", text)
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = URL_RE.sub("[REDACTED_URL]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = LONG_TOKEN_RE.sub("[REDACTED_TOKEN]", text)
    return text[:3000]


def _normalize_choice(value: Any, allowed: set[str], fallback: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    return normalized if normalized in allowed else fallback


def _diagnostic_summary(payload: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(payload, Mapping) or not payload:
        return None
    privacy = payload.get("privacy") if isinstance(payload.get("privacy"), Mapping) else {}
    if privacy and not bool(privacy.get("safe_to_send", True)):
        return {
            "attached": False,
            "reason": "diagnostic_not_marked_safe_to_send",
            "privacy": {"raw_payload_stored": False},
        }
    return {
        "attached": True,
        "diagnosticId": str(payload.get("diagnostic_id") or "").strip()[:40],
        "filename": str(payload.get("filename") or "").strip()[:120],
        "generatedAt": str(payload.get("generated_at") or "").strip()[:40],
        "schemaVersion": payload.get("schema_version"),
        "app": payload.get("app") if isinstance(payload.get("app"), Mapping) else {},
        "runtime": payload.get("runtime") if isinstance(payload.get("runtime"), Mapping) else {},
        "checks": payload.get("checks") if isinstance(payload.get("checks"), Mapping) else {},
        "privacy": {
            "raw_payload_stored": False,
            "paths_returned": False,
            "license_payload_returned": False,
            "strategy_files_returned": False,
        },
    }


def _remote_identity_ref(session_status: Mapping[str, Any] | None) -> dict[str, Any]:
    session = session_status.get("session") if isinstance(session_status, Mapping) and isinstance(session_status.get("session"), Mapping) else {}
    email_hash = str(session.get("email_hash") or "").strip()
    return {
        "sessionActive": bool(session.get("active")),
        "emailRef": str(session.get("email_ref") or "").strip(),
        "emailHashRef": email_hash[:12] if email_hash else "",
        "entitlementKind": str(session.get("entitlement_kind") or "").strip(),
        "rawEmailStored": False,
    }


def _workspace_ref(workspace_context: Mapping[str, Any] | None) -> dict[str, Any]:
    workspace = workspace_context.get("workspace") if isinstance(workspace_context, Mapping) and isinstance(workspace_context.get("workspace"), Mapping) else {}
    owner_hash = str(workspace.get("owner_hash") or "").strip()
    return {
        "id": str(workspace.get("id") or "").strip(),
        "ownerHashRef": owner_hash[:12] if owner_hash else "",
        "localPathStored": False,
    }


def _case_id(seed: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(seed, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()[:10]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"SQX-SUP-{stamp}-{digest}"


def build_support_incident(
    data: Mapping[str, Any],
    *,
    session_status: Mapping[str, Any] | None = None,
    workspace_context: Mapping[str, Any] | None = None,
    diagnostic_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    now = _utc_now()
    category = _normalize_choice(data.get("category"), ALLOWED_CATEGORIES, "other")
    severity = _normalize_choice(data.get("severity"), ALLOWED_SEVERITIES, "medium")
    record = {
        "schemaVersion": SUPPORT_INCIDENT_VERSION,
        "createdAt": now,
        "source": "remote_control_panel",
        "category": category,
        "severity": severity,
        "summary": redact_support_text(data.get("summary")),
        "steps": redact_support_text(data.get("steps")),
        "expected": redact_support_text(data.get("expected")),
        "actual": redact_support_text(data.get("actual")),
        "diagnostic": _diagnostic_summary(diagnostic_payload),
        "remoteIdentityRef": _remote_identity_ref(session_status),
        "workspaceRef": _workspace_ref(workspace_context),
        "status": "open",
        "privacy": {
            "rawEmailStored": False,
            "protectedUrlStored": False,
            "localPathsStored": False,
            "tokensStored": False,
            "diagnosticRawPayloadStored": False,
        },
    }
    record["diagnosticId"] = (record["diagnostic"] or {}).get("diagnosticId") if record.get("diagnostic") else ""
    record["caseId"] = _case_id({
        "createdAt": now,
        "category": category,
        "severity": severity,
        "summary": record["summary"],
        "emailHashRef": record["remoteIdentityRef"]["emailHashRef"],
    })
    return record


def validate_support_incident(record: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not str(record.get("summary") or "").strip():
        blockers.append("summary_required")
    if str(record.get("category") or "") not in ALLOWED_CATEGORIES:
        blockers.append("category_invalid")
    if str(record.get("severity") or "") not in ALLOWED_SEVERITIES:
        blockers.append("severity_invalid")
    return blockers


def append_support_incident(record: Mapping[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_SUPPORT_CASES_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), sort_keys=True) + "\n")
    return {
        "ok": True,
        "caseId": record.get("caseId"),
        "status": record.get("status"),
        "stored": True,
        "path": str(target),
    }


def load_support_incidents(path: str | Path | None = None) -> list[dict[str, Any]]:
    target = Path(path) if path else DEFAULT_SUPPORT_CASES_PATH
    if not target.is_file():
        return []
    incidents: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            incidents.append(payload)
    return incidents


def write_support_incidents(incidents: list[Mapping[str, Any]], path: str | Path | None = None) -> None:
    target = Path(path) if path else DEFAULT_SUPPORT_CASES_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(dict(item), sort_keys=True) for item in incidents]
    target.write_text(("\n".join(lines) + "\n") if lines else "", encoding="utf-8")


def update_support_incident_status(
    case_id: str,
    status: str,
    *,
    path: str | Path | None = None,
    note: str = "",
) -> dict[str, Any]:
    normalized_status = _normalize_choice(status, ALLOWED_STATUSES, "")
    if not normalized_status:
        return {"ok": False, "error": "support_status_invalid", "caseId": case_id}
    incidents = load_support_incidents(path)
    updated = False
    for item in incidents:
        if str(item.get("caseId") or "") == case_id:
            item["status"] = normalized_status
            item["updatedAt"] = _utc_now()
            if note:
                item["operatorNote"] = redact_support_text(note)[:500]
            updated = True
            break
    if not updated:
        return {"ok": False, "error": "support_case_not_found", "caseId": case_id}
    write_support_incidents(incidents, path)
    return {
        "ok": True,
        "caseId": case_id,
        "status": normalized_status,
        "privacy": {"rawEmailReturned": False, "localPathsReturned": False, "tokensReturned": False},
    }


def support_incident_public_response(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "schemaVersion": SUPPORT_INCIDENT_VERSION,
        "caseId": record.get("caseId"),
        "status": record.get("status"),
        "category": record.get("category"),
        "severity": record.get("severity"),
        "diagnosticId": record.get("diagnosticId") or "",
        "message": "Incidencia registrada. Guarda el identificador para seguimiento.",
        "privacy": {
            "rawEmailReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "tokensReturned": False,
            "storedUnderGit": False,
        },
    }


def summarize_support_incidents(path: str | Path | None = None) -> dict[str, Any]:
    incidents = load_support_incidents(path)
    open_items = [item for item in incidents if str(item.get("status") or "open") in {"open", "triaged"}]
    blocker_items = [item for item in open_items if item.get("severity") == "blocker"]
    by_severity = {severity: 0 for severity in sorted(ALLOWED_SEVERITIES)}
    for item in incidents:
        severity = str(item.get("severity") or "medium")
        if severity in by_severity:
            by_severity[severity] += 1
    latest = [
        {
            "caseId": item.get("caseId"),
            "createdAt": item.get("createdAt"),
            "category": item.get("category"),
            "severity": item.get("severity"),
            "status": item.get("status"),
            "summary": redact_support_text(item.get("summary"))[:180],
        }
        for item in incidents[-5:]
    ]
    return {
        "ok": True,
        "schemaVersion": SUPPORT_INCIDENT_VERSION,
        "generatedAt": _utc_now(),
        "summary": {
            "total": len(incidents),
            "openSupportItems": len(open_items),
            "unresolvedBlockers": len(blocker_items),
            "bySeverity": by_severity,
        },
        "latest": latest,
        "remote8c": {
            "supportLoopObservedCandidate": len(incidents) > 0,
            "blocksExpansion": bool(open_items or blocker_items),
            "operatorMustUpdateEvidenceManually": True,
        },
        "privacy": {
            "rawEmailReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "tokensReturned": False,
            "supportLogsReturned": False,
        },
    }
