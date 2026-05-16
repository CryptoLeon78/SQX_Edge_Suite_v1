from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION = (
    "remote-next-controlled-movement-execution-approval-v1"
)
DEFAULT_REMOTE8I_EVIDENCE_PATH = (
    PROJECT_ROOT
    / ".local"
    / "remote_service"
    / "remote8i_next_controlled_movement_execution_approval.local.json"
)
DEFAULT_REMOTE8I_OUTPUT_ROOT = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8i_next_controlled_movement_execution_approval"
)

REQUIRED_SOURCE_STATUS = "GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY"
VALID_REQUESTED_ACTIONS = {"approve_or_reject_next_controlled_movement_execution"}
VALID_EXECUTION_DECISIONS = {"approve_execution_record", "reject_execution", "defer_execution"}
APPROVAL_DECISION = "approve_execution_record"

REQUIRED_CHECKS = (
    "remote8hPackageReviewed",
    "packageMatchesPrivateEvidence",
    "operatorDecisionRecorded",
    "decisionRationaleRecorded",
    "executionScopeUnchanged",
    "supportWindowStillReady",
    "rollbackStillReady",
    "pauseRuleStillReady",
    "noAutomationConfirmed",
    "executionRecordRequired",
    "privateEvidenceStoredOutsideGit",
)

ZERO_EXECUTION_METRICS = (
    "newUsersInvited",
    "grantsCreated",
    "checkoutLinksCreated",
    "emailsSent",
    "publicUrlsShared",
    "automationJobsStarted",
    "trafficExpanded",
    "paidCampaignStarted",
)

FORBIDDEN_PUBLIC_MARKERS = (
    "CLOUDFLARE" + "_API_TOKEN=",
    "SQX_REMOTE" + "_SESSION_SECRET=",
    "SQX_REMOTE" + "_PAYMENT_WEBHOOK_SECRET=",
    "sk_" + "live_",
    "pk_" + "live_",
    "__Host-sqx_remote_session",
)

HTTP_URL_RE = re.compile(r"https?://", re.IGNORECASE)
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/]")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("remote8i_approval_must_be_json_object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _short(value: Any, size: int = 12) -> str:
    text = str(value or "").strip()
    return text[:size] if text else ""


def _checks_from_payload(payload: Mapping[str, Any]) -> dict[str, bool]:
    raw = payload.get("checks") if isinstance(payload.get("checks"), Mapping) else {}
    return {check: bool(raw.get(check)) for check in REQUIRED_CHECKS}


def _execution_metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("executionMetrics") if isinstance(payload.get("executionMetrics"), Mapping) else {}
    return {metric: _nonnegative_int(raw.get(metric)) for metric in ZERO_EXECUTION_METRICS}


def _source_gate_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    return {
        "remote8hStatus": str(raw.get("remote8hStatus") or "").strip(),
        "remote8hPackageId": _short(raw.get("remote8hPackageId")),
        "remote8hMovementType": str(raw.get("remote8hMovementType") or "").strip(),
        "plannedNewUsers": _nonnegative_int(raw.get("plannedNewUsers")),
        "candidateCount": _nonnegative_int(raw.get("candidateCount")),
    }


def _decision_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("decision") if isinstance(payload.get("decision"), Mapping) else {}
    return {
        "selectedDecision": str(raw.get("selectedDecision") or "").strip(),
        "rationaleCategory": str(raw.get("rationaleCategory") or "").strip(),
        "executionOwner": str(raw.get("executionOwner") or "").strip(),
        "supportWindowHours": _nonnegative_int(raw.get("supportWindowHours")),
        "monitoringWindowHours": _nonnegative_int(raw.get("monitoringWindowHours")),
        "maxExecutionDelayHours": _nonnegative_int(raw.get("maxExecutionDelayHours")),
    }


def _candidate_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_candidates = payload.get("candidateUsers") if isinstance(payload.get("candidateUsers"), list) else []
    records: list[dict[str, Any]] = []
    for index, candidate in enumerate(raw_candidates, start=1):
        if not isinstance(candidate, Mapping):
            continue
        email = normalize_email(str(candidate.get("email") or ""))
        digest = email_hash(email)
        records.append(
            {
                "index": index,
                "emailRef": redact_email(email),
                "emailHashRef": digest[:12] if digest else "",
                "approvedForExecutionRecord": bool(candidate.get("approvedForExecutionRecord")),
                "_rawEmail": email,
            }
        )
    return records


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    private_review = payload.get("privateReview") if isinstance(payload.get("privateReview"), Mapping) else {}
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
    values.extend(str(value or "").strip() for value in private_review.values())
    values.extend(str(candidate.get("_rawEmail") or "") for candidate in _candidate_records(payload))
    return tuple(value for value in values if value)


def _summary_leak_markers(summary: Mapping[str, Any], payload: Mapping[str, Any]) -> list[str]:
    serialized = json.dumps(summary, sort_keys=True, ensure_ascii=True)
    leaks: list[str] = []
    for value in _private_values(payload):
        if value and value in serialized:
            leaks.append("private_value_returned")
            break
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker in serialized:
            leaks.append(f"forbidden_marker:{marker}")
    if HTTP_URL_RE.search(serialized):
        leaks.append("url_returned")
    if WINDOWS_PATH_RE.search(serialized):
        leaks.append("windows_path_returned")
    return leaks


def _public_candidates(candidates: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    public_candidates: list[dict[str, Any]] = []
    for candidate in candidates:
        public_candidates.append(
            {
                "index": candidate.get("index"),
                "emailRef": candidate.get("emailRef"),
                "emailHashRef": candidate.get("emailHashRef"),
                "approvedForExecutionRecord": bool(candidate.get("approvedForExecutionRecord")),
            }
        )
    return public_candidates


def _status_for_clean_decision(selected_decision: str) -> str:
    if selected_decision == "approve_execution_record":
        return "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVED"
    if selected_decision == "reject_execution":
        return "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_REJECTED"
    if selected_decision == "defer_execution":
        return "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_DEFERRED"
    return "NO_GO_REMOTE8I_EXECUTION_APPROVAL_BLOCKED"


def _next_phase_for_clean_decision(selected_decision: str) -> str:
    if selected_decision == "approve_execution_record":
        return "REMOTE-8J-manual-execution-record"
    if selected_decision == "reject_execution":
        return "REMOTE-8H-or-8G-replan"
    if selected_decision == "defer_execution":
        return "REMOTE-8I-revisit-execution-approval"
    return "REMOTE-8I-blockers"


def build_remote8i_execution_approval_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8I execution approval summary without executing anything."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_action = str(payload.get("requestedAction") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    source_gate = _source_gate_from_payload(payload)
    decision = _decision_from_payload(payload)
    selected_decision = decision["selectedDecision"]
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    execution_metrics = _execution_metrics_from_payload(payload)
    execution_blockers = [metric for metric, value in execution_metrics.items() if value]
    candidates = _candidate_records(payload)
    blockers: list[str] = []

    if schema_version != REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION:
        blockers.append("remote8i_schema_version_mismatch")
    if requested_action not in VALID_REQUESTED_ACTIONS:
        blockers.append("requested_action_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if source_gate["remote8hStatus"] != REQUIRED_SOURCE_STATUS:
        blockers.append("remote8h_package_go_status_missing")
    if not source_gate["remote8hPackageId"]:
        blockers.append("remote8h_package_id_missing")
    if source_gate["remote8hMovementType"] == "add_1_2_users":
        if source_gate["plannedNewUsers"] < 1:
            blockers.append("add_users_requires_planned_users")
        if source_gate["plannedNewUsers"] > 2:
            blockers.append("planned_new_users_exceeds_limit")
        if source_gate["candidateCount"] != source_gate["plannedNewUsers"]:
            blockers.append("candidate_count_must_match_planned_new_users")
    if selected_decision not in VALID_EXECUTION_DECISIONS:
        blockers.append("execution_decision_invalid")
    if selected_decision == APPROVAL_DECISION:
        if not decision["executionOwner"]:
            blockers.append("execution_owner_missing")
        if decision["supportWindowHours"] < 24:
            blockers.append("support_window_too_short")
        if decision["monitoringWindowHours"] < 24:
            blockers.append("monitoring_window_too_short")
        if decision["maxExecutionDelayHours"] < 1:
            blockers.append("execution_delay_window_missing")
        if candidates and len(candidates) != source_gate["candidateCount"]:
            blockers.append("candidate_approval_count_mismatch")
        for candidate in candidates:
            if not candidate.get("emailHashRef"):
                blockers.append(f"candidate_{candidate.get('index')}_identity_missing")
            if not candidate.get("approvedForExecutionRecord"):
                blockers.append(f"candidate_{candidate.get('index')}_approval_missing")
    if missing_checks:
        blockers.append("required_checks_missing")
    if execution_blockers:
        blockers.append("execution_metrics_must_remain_zero")

    valid = not blockers
    approved = valid and selected_decision == APPROVAL_DECISION
    summary: dict[str, Any] = {
        "ok": valid,
        "status": _status_for_clean_decision(selected_decision) if valid else "NO_GO_REMOTE8I_EXECUTION_APPROVAL_BLOCKED",
        "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION,
        "generatedAt": _utc_now(),
        "approval": {
            "id": str(payload.get("approvalId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedAction": requested_action,
            "selectedDecision": selected_decision,
            "rationaleCategory": decision["rationaleCategory"],
            "rationaleRecorded": bool(checks.get("decisionRationaleRecorded")),
            "approvedForManualExecutionRecord": approved,
            "executionPerformedNow": False,
            "automationAllowed": False,
            "requiresSeparateExecutionRecord": True,
            "allowedNextAction": (
                "create_remote8j_manual_execution_record"
                if approved
                else ("replan_remote8h_or_remote8g" if selected_decision == "reject_execution" else "revisit_remote8i_decision")
            ),
        },
        "sourceGate": source_gate,
        "decisionReadiness": {
            "executionOwnerAssigned": bool(decision["executionOwner"]),
            "supportWindowHours": decision["supportWindowHours"],
            "monitoringWindowHours": decision["monitoringWindowHours"],
            "maxExecutionDelayHours": decision["maxExecutionDelayHours"],
            "candidateApprovals": _public_candidates(candidates),
        },
        "checks": checks,
        "missingChecks": missing_checks,
        "executionMetrics": execution_metrics,
        "executionBlockers": execution_blockers,
        "blockers": blockers,
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "communicationCopyReturned": False,
            "decisionRationaleReturned": False,
            "privateEvidenceCommitted": False,
        },
        "nextPhase": _next_phase_for_clean_decision(selected_decision) if valid else "REMOTE-8I-blockers",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8I_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["approval"]["approvedForManualExecutionRecord"] = False
        summary["approval"]["allowedNextAction"] = "fix_remote8i_privacy_leak"
        summary["nextPhase"] = "REMOTE-8I-privacy-fix"
    return summary


def ingest_remote8i_next_controlled_movement_execution_approval(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-8I approval evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8I_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8I_OUTPUT_ROOT
    summary_path = output_base / "remote8i_next_controlled_movement_execution_approval.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8I_EXECUTION_APPROVAL_EVIDENCE_MISSING",
            "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8i_execution_approval_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["next_controlled_movement_execution_approval_evidence_missing"],
            "approval": {
                "approvedForManualExecutionRecord": False,
                "executionPerformedNow": False,
                "automationAllowed": False,
                "requiresSeparateExecutionRecord": True,
                "allowedNextAction": "collect_remote8i_private_evidence",
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "communicationCopyReturned": False,
                "decisionRationaleReturned": False,
                "privateEvidenceCommitted": False,
            },
            "nextPhase": "REMOTE-8I-private-approval-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8i_execution_approval_summary(payload)
    _write_json(summary_path, summary)
    return summary
