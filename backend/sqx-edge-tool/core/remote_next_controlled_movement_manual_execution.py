from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION = (
    "remote-next-controlled-movement-manual-execution-v1"
)
DEFAULT_REMOTE8J_EVIDENCE_PATH = (
    PROJECT_ROOT
    / ".local"
    / "remote_service"
    / "remote8j_next_controlled_movement_manual_execution.local.json"
)
DEFAULT_REMOTE8J_OUTPUT_ROOT = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8j_next_controlled_movement_manual_execution"
)

REQUIRED_SOURCE_STATUS = "GO_REMOTE8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVED"
REQUIRED_SOURCE_DECISION = "approve_execution_record"
VALID_REQUESTED_ACTIONS = {"record_next_controlled_movement_manual_execution"}
VALID_MOVEMENT_TYPES = {
    "add_1_2_users",
    "extend_same_cohort_observation",
    "prepare_paid_micro_offer",
    "schedule_demo_batch",
}
VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}
MAX_NEW_USERS = 2

REQUIRED_CHECKS = (
    "remote8iApprovalConfirmed",
    "remote8hPackageStillMatches",
    "operatorFinalApprovalRecorded",
    "manualExecutionOnly",
    "noAutomationUsed",
    "manualActionRecorded",
    "entitlementsRecordedPrivately",
    "protectedUrlSharedPrivately",
    "supportWindowActive",
    "rollbackPlanStillReady",
    "pauseRuleStillActive",
    "monitoringStarted",
    "privateEvidenceStoredOutsideGit",
)

PER_USER_REQUIRED_FLAGS = (
    "manualInviteSent",
    "manualGrantRecorded",
    "privateMessageSent",
    "protectedUrlSharedPrivately",
    "supportWindowAcknowledged",
)

MANUAL_COUNT_METRICS = (
    "invitesSentManually",
    "grantsRecordedManually",
    "privateMessagesSent",
    "protectedUrlsSharedPrivately",
)

ZERO_AUTOMATION_METRICS = (
    "automationJobsStarted",
    "checkoutLinksCreated",
    "publicUrlsShared",
    "automatedEmailsSent",
    "automatedGrantsCreated",
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
        raise ValueError("remote8j_manual_execution_must_be_json_object")
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


def _counts_from_payload(payload: Mapping[str, Any], key: str, metrics: tuple[str, ...]) -> dict[str, int]:
    raw = payload.get(key) if isinstance(payload.get(key), Mapping) else {}
    return {metric: _nonnegative_int(raw.get(metric)) for metric in metrics}


def _source_gate_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    return {
        "remote8iStatus": str(raw.get("remote8iStatus") or "").strip(),
        "remote8iApprovalId": _short(raw.get("remote8iApprovalId")),
        "remote8iSelectedDecision": str(raw.get("remote8iSelectedDecision") or "").strip(),
        "remote8hPackageId": _short(raw.get("remote8hPackageId")),
        "movementType": str(raw.get("movementType") or "").strip(),
        "plannedNewUsers": _nonnegative_int(raw.get("plannedNewUsers")),
        "candidateCount": _nonnegative_int(raw.get("candidateCount")),
    }


def _executed_user_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_users = payload.get("executedUsers") if isinstance(payload.get("executedUsers"), list) else []
    records: list[dict[str, Any]] = []
    for index, user in enumerate(raw_users, start=1):
        if not isinstance(user, Mapping):
            continue
        email = normalize_email(str(user.get("email") or ""))
        digest = email_hash(email)
        flags = {flag: bool(user.get(flag)) for flag in PER_USER_REQUIRED_FLAGS}
        records.append(
            {
                "index": index,
                "kind": str(user.get("kind") or "").strip(),
                "featureScope": str(user.get("featureScope") or "full").strip(),
                "emailRef": redact_email(email),
                "emailHashRef": digest[:12] if digest else "",
                "manualFlags": flags,
                "_rawEmail": email,
            }
        )
    return records


def _user_blockers(users: list[Mapping[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for user in users:
        index = user.get("index")
        if user.get("kind") not in VALID_ENTITLEMENT_KINDS:
            blockers.append(f"user_{index}_kind_invalid")
        if not user.get("emailHashRef"):
            blockers.append(f"user_{index}_identity_missing")
        flags = user.get("manualFlags") if isinstance(user.get("manualFlags"), Mapping) else {}
        for flag in PER_USER_REQUIRED_FLAGS:
            if not flags.get(flag):
                blockers.append(f"user_{index}_{flag}_missing")
    return blockers


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    private_execution = payload.get("privateExecution") if isinstance(payload.get("privateExecution"), Mapping) else {}
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
    values.extend(str(value or "").strip() for value in private_execution.values())
    values.extend(str(user.get("_rawEmail") or "") for user in _executed_user_records(payload))
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


def _public_users(users: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    public_users: list[dict[str, Any]] = []
    for user in users:
        flags = user.get("manualFlags") if isinstance(user.get("manualFlags"), Mapping) else {}
        public_users.append(
            {
                "index": user.get("index"),
                "kind": user.get("kind"),
                "featureScope": user.get("featureScope"),
                "emailRef": user.get("emailRef"),
                "emailHashRef": user.get("emailHashRef"),
                "manualInviteSent": bool(flags.get("manualInviteSent")),
                "manualGrantRecorded": bool(flags.get("manualGrantRecorded")),
                "privateMessageSent": bool(flags.get("privateMessageSent")),
                "protectedUrlSharedPrivately": bool(flags.get("protectedUrlSharedPrivately")),
                "supportWindowAcknowledged": bool(flags.get("supportWindowAcknowledged")),
            }
        )
    return public_users


def build_remote8j_manual_execution_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8J manual execution record."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_action = str(payload.get("requestedAction") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    source_gate = _source_gate_from_payload(payload)
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    manual_counts = _counts_from_payload(payload, "manualCounts", MANUAL_COUNT_METRICS)
    automation_metrics = _counts_from_payload(payload, "automationMetrics", ZERO_AUTOMATION_METRICS)
    users = _executed_user_records(payload)
    user_count = len(users)
    automation_blockers = [metric for metric, value in automation_metrics.items() if value]
    manual_count_blockers = [metric for metric in MANUAL_COUNT_METRICS if manual_counts.get(metric) != user_count]
    blockers: list[str] = []

    if schema_version != REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION:
        blockers.append("remote8j_schema_version_mismatch")
    if requested_action not in VALID_REQUESTED_ACTIONS:
        blockers.append("requested_action_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if source_gate["remote8iStatus"] != REQUIRED_SOURCE_STATUS:
        blockers.append("remote8i_approval_go_status_missing")
    if source_gate["remote8iSelectedDecision"] != REQUIRED_SOURCE_DECISION:
        blockers.append("remote8i_selected_decision_not_execution_approval")
    if not source_gate["remote8iApprovalId"]:
        blockers.append("remote8i_approval_id_missing")
    if source_gate["movementType"] not in VALID_MOVEMENT_TYPES:
        blockers.append("movement_type_invalid")
    if source_gate["movementType"] == "add_1_2_users":
        if source_gate["plannedNewUsers"] < 1:
            blockers.append("add_users_requires_planned_users")
        if source_gate["plannedNewUsers"] > MAX_NEW_USERS:
            blockers.append("planned_new_users_exceeds_limit")
        if source_gate["candidateCount"] != source_gate["plannedNewUsers"]:
            blockers.append("candidate_count_must_match_planned_new_users")
        if user_count != source_gate["plannedNewUsers"]:
            blockers.append("executed_user_count_must_match_planned_new_users")
    elif user_count:
        blockers.append("non_user_movement_must_not_include_executed_users")
    if missing_checks:
        blockers.append("required_checks_missing")
    if automation_blockers:
        blockers.append("automation_metrics_must_remain_zero")
    if source_gate["movementType"] == "add_1_2_users" and manual_count_blockers:
        blockers.append("manual_execution_counts_mismatch")
    blockers.extend(_user_blockers(users))

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": (
            "GO_REMOTE8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_RECORDED"
            if valid
            else "NO_GO_REMOTE8J_MANUAL_EXECUTION_BLOCKED"
        ),
        "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION,
        "generatedAt": _utc_now(),
        "execution": {
            "id": str(payload.get("executionId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedAction": requested_action,
            "mode": "manual_operator_record",
            "movementType": source_gate["movementType"],
            "executedUserCount": user_count,
            "users": _public_users(users),
        },
        "sourceGate": source_gate,
        "checks": checks,
        "missingChecks": missing_checks,
        "manualCounts": manual_counts,
        "automationMetrics": automation_metrics,
        "countBlockers": {
            "automationMetricsNonzero": automation_blockers,
            "manualCountsMismatch": manual_count_blockers,
        },
        "blockers": blockers,
        "record": {
            "ready": valid,
            "allowedNextAction": "start_remote8k_post_execution_monitoring" if valid else "fix_remote8j_blockers",
            "automationAllowed": False,
            "requiresOperatorReview": True,
        },
        "postExecutionGate": {
            "furtherExpansionAllowedNow": False,
            "monitoringRequired": True,
            "rollbackAndPauseRemainActive": True,
        },
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "messageBodyReturned": False,
            "privateEvidenceCommitted": False,
        },
        "nextPhase": "REMOTE-8K-post-execution-monitoring",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8J_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["record"]["ready"] = False
        summary["record"]["allowedNextAction"] = "fix_remote8j_privacy_leak"
    return summary


def ingest_remote8j_next_controlled_movement_manual_execution(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-8J manual execution evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8J_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8J_OUTPUT_ROOT
    summary_path = output_base / "remote8j_next_controlled_movement_manual_execution.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8J_MANUAL_EXECUTION_EVIDENCE_MISSING",
            "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8j_manual_execution_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["next_controlled_movement_manual_execution_evidence_missing"],
            "record": {
                "ready": False,
                "allowedNextAction": "collect_remote8j_private_evidence",
                "automationAllowed": False,
                "requiresOperatorReview": True,
            },
            "postExecutionGate": {
                "furtherExpansionAllowedNow": False,
                "monitoringRequired": True,
                "rollbackAndPauseRemainActive": True,
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "messageBodyReturned": False,
                "privateEvidenceCommitted": False,
            },
            "nextPhase": "REMOTE-8J-private-manual-execution-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8j_manual_execution_summary(payload)
    _write_json(summary_path, summary)
    return summary
