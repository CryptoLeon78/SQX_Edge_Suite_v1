from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_cohort_matrix import (
    DEFAULT_OUTPUT_PATH as DEFAULT_MATRIX_OUTPUT_PATH,
    FORBIDDEN_PUBLIC_MARKERS,
    build_remote_cohort_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_COHORT_CONTEXT_RECONCILE_VERSION = "remote-cohort-context-reconcile-v1"
DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT
    / ".local"
    / "remote_service"
    / "remote_cohort_matrix"
    / "remote_cohort_context_reconcile.local.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _display_path(path: str | Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return ".local/remote_service/remote_cohort_matrix/remote_cohort_matrix.local.json"


def _classify_active_row(row: Mapping[str, Any]) -> dict[str, Any]:
    alias = str(row.get("alias") or "")
    open_incidents = int(row.get("openIncidents") or 0)
    base = {
        "alias": alias,
        "identityHashRef": row.get("identityHashRef") or "",
        "monitoringScope": row.get("monitoringScope") or "active",
        "status": row.get("status") or "unknown",
        "contextRefs": row.get("contextRefs") or [],
        "trustedContexts": int(row.get("trustedContexts") or 0),
        "pendingContexts": int(row.get("pendingContexts") or 0),
        "blockedContexts": int(row.get("blockedContexts") or 0),
        "revokedContexts": int(row.get("revokedContexts") or 0),
        "openIncidents": open_incidents,
    }
    if row.get("antiSharingOk"):
        return {
            **base,
            "action": "none",
            "severity": "ok",
            "reason": "anti_sharing_context_ready",
            "operatorInstruction": "No action needed.",
        }
    if int(row.get("pendingContexts") or 0) > 0:
        return {
            **base,
            "action": "operator_review_pending_context",
            "severity": "high",
            "reason": "pending_context_requires_operator_approval",
            "operatorInstruction": (
                "Run tools/remote_access_control_status.ps1, identify the alias contextRef, "
                "then approve or reject with tools/remote_access_control_admin.ps1."
            ),
        }
    if int(row.get("blockedContexts") or 0) > 0 or int(row.get("revokedContexts") or 0) > 0:
        return {
            **base,
            "action": "operator_review_blocked_context",
            "severity": "high",
            "reason": "blocked_or_revoked_context_requires_manual_decision",
            "operatorInstruction": "Review the context before restoring access. Do not auto-approve.",
        }
    if row.get("accessOk") and row.get("grantOk") and row.get("downloadsOk") and open_incidents == 0:
        return {
            **base,
            "action": "recapture_context",
            "severity": "medium",
            "reason": "human_smoke_ok_but_anti_sharing_context_missing",
            "operatorInstruction": (
                "Ask this alias to open the protected link again, press Actualizar estado or "
                "Acceso DASHBOARD, then rerun tools/remote_cohort_matrix.ps1. If the context "
                "appears as pending, approve it with the admin tool only after confirming the alias."
            ),
        }
    return {
        **base,
        "action": "repeat_access_download_smoke",
        "severity": "high",
        "reason": "missing_access_grant_download_or_incident_signal",
        "operatorInstruction": "Repeat the access/download smoke before approving any context.",
    }


def build_remote_cohort_context_reconcile(
    *,
    matrix_payload: Mapping[str, Any] | None = None,
    matrix_output_path: str | Path | None = DEFAULT_MATRIX_OUTPUT_PATH,
    **matrix_kwargs: Any,
) -> dict[str, Any]:
    """Build a public-safe operator plan for active aliases missing anti-sharing context."""

    if matrix_payload is None:
        matrix_payload = build_remote_cohort_matrix(**matrix_kwargs)
    rows = matrix_payload.get("rows") if isinstance(matrix_payload.get("rows"), list) else []
    active_rows = [
        row for row in rows
        if isinstance(row, Mapping) and str(row.get("monitoringScope") or "active") == "active"
    ]
    actions = [_classify_active_row(row) for row in active_rows]
    needs_action = [item for item in actions if item["action"] != "none"]
    recapture_required = [item for item in actions if item["action"] == "recapture_context"]
    operator_review_required = [
        item for item in actions
        if item["action"] in {"operator_review_pending_context", "operator_review_blocked_context"}
    ]
    repeat_smoke_required = [item for item in actions if item["action"] == "repeat_access_download_smoke"]
    payload = {
        "schemaVersion": REMOTE_COHORT_CONTEXT_RECONCILE_VERSION,
        "phase": "REMOTE-COHORT-FIX2",
        "generatedAt": _utc_now(),
        "summary": {
            "activeAliasCount": len(active_rows),
            "readyAliasCount": len([item for item in actions if item["action"] == "none"]),
            "needsActionCount": len(needs_action),
            "recaptureRequiredCount": len(recapture_required),
            "operatorReviewRequiredCount": len(operator_review_required),
            "repeatSmokeRequiredCount": len(repeat_smoke_required),
            "canTreatActiveCohortAsClean": len(needs_action) == 0,
        },
        "actions": actions,
        "sourceMatrix": {
            "schemaVersion": matrix_payload.get("schemaVersion"),
            "phase": matrix_payload.get("phase"),
            "localOutput": _display_path(matrix_output_path or DEFAULT_MATRIX_OUTPUT_PATH),
            "localOutputReturned": False,
        },
        "privacy": {
            "rawEmailsReturned": False,
            "rawIpsReturned": False,
            "protectedUrlsReturned": False,
            "cookiesReturned": False,
            "tokensReturned": False,
            "localPathsReturned": False,
        },
        "nextStep": (
            "Recapture or review active anti-sharing contexts, rerun the matrix, "
            "then continue REMOTE-8F/8G only when active aliases are clean."
        ),
    }
    _assert_public_safe(payload)
    return payload


def _assert_public_safe(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker in serialized:
            raise ValueError(f"remote_cohort_context_reconcile_privacy_leak:{marker}")


def write_remote_cohort_context_reconcile(
    payload: Mapping[str, Any],
    output_path: str | Path | None = DEFAULT_OUTPUT_PATH,
) -> Path:
    target = Path(output_path or DEFAULT_OUTPUT_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
