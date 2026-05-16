from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION = "remote-tiny-cohort-decision-review-v1"
DEFAULT_REMOTE8G_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8g_tiny_cohort_decision_review.local.json"
)
DEFAULT_REMOTE8G_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8g_tiny_cohort_decision_review"

MIN_COHORT_SIZE = 3
MAX_COHORT_SIZE = 5
CLEAN_SOURCE_STATUS = "GO_REMOTE8F_TINY_COHORT_MONITORING_CLEAN"
BLOCKED_SOURCE_STATUS = "NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED"
VALID_SOURCE_STATUSES = {CLEAN_SOURCE_STATUS, BLOCKED_SOURCE_STATUS}
VALID_SELECTED_DECISIONS = {
    "continue_observing",
    "fix_blockers",
    "rollback_tiny_cohort",
    "prepare_next_controlled_movement",
}
VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}

REQUIRED_CHECKS = (
    "remote8fMonitoringReviewed",
    "operatorDecisionRecorded",
    "decisionRationaleRecorded",
    "cohortSizeReviewed",
    "supportOwnerConfirmed",
    "rollbackPlanReady",
    "pauseRuleReady",
    "entitlementBoundaryReviewed",
    "workspaceIsolationReviewed",
    "securityReviewCompleted",
    "noAutomationConfirmed",
    "privateEvidenceStoredOutsideGit",
)

PER_USER_REQUIRED_FLAGS = (
    "accessOutcomeReviewed",
    "supportOutcomeReviewed",
    "workspaceOutcomeReviewed",
    "entitlementOutcomeReviewed",
)

ZERO_EXECUTION_METRICS = (
    "newUsersInvited",
    "grantsChanged",
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
        raise ValueError("remote8g_decision_review_must_be_json_object")
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


def _reviewed_user_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_users = payload.get("reviewedUsers") if isinstance(payload.get("reviewedUsers"), list) else []
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
                "reviewFlags": flags,
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
        flags = user.get("reviewFlags") if isinstance(user.get("reviewFlags"), Mapping) else {}
        for flag in PER_USER_REQUIRED_FLAGS:
            if not flags.get(flag):
                blockers.append(f"user_{index}_{flag}_missing")
    return blockers


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
    values.extend(str(user.get("_rawEmail") or "") for user in _reviewed_user_records(payload))
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
        flags = user.get("reviewFlags") if isinstance(user.get("reviewFlags"), Mapping) else {}
        public_users.append(
            {
                "index": user.get("index"),
                "kind": user.get("kind"),
                "featureScope": user.get("featureScope"),
                "emailRef": user.get("emailRef"),
                "emailHashRef": user.get("emailHashRef"),
                "accessOutcomeReviewed": bool(flags.get("accessOutcomeReviewed")),
                "supportOutcomeReviewed": bool(flags.get("supportOutcomeReviewed")),
                "workspaceOutcomeReviewed": bool(flags.get("workspaceOutcomeReviewed")),
                "entitlementOutcomeReviewed": bool(flags.get("entitlementOutcomeReviewed")),
            }
        )
    return public_users


def _allowed_next_action(selected_decision: str, valid: bool) -> str:
    if not valid:
        return "fix_remote8g_blockers"
    if selected_decision == "prepare_next_controlled_movement":
        return "prepare_remote8h_next_controlled_movement_package"
    if selected_decision == "continue_observing":
        return "continue_remote8f_monitoring"
    if selected_decision == "rollback_tiny_cohort":
        return "prepare_manual_rollback_package"
    return "prepare_blocker_fix_plan"


def build_remote8g_decision_review_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8G operator decision review summary."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    selected_decision = str(payload.get("selectedDecision") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    source_gate = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    source_status = str(source_gate.get("remote8fStatus") or "").strip()
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    execution_metrics = _execution_metrics_from_payload(payload)
    execution_blockers = [metric for metric, value in execution_metrics.items() if value]
    users = _reviewed_user_records(payload)
    user_count = len(users)
    monitoring_summary = payload.get("monitoringSummary") if isinstance(payload.get("monitoringSummary"), Mapping) else {}
    monitoring_blockers = _nonnegative_int(monitoring_summary.get("blockerCount"))
    blockers: list[str] = []

    if schema_version != REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION:
        blockers.append("remote8g_schema_version_mismatch")
    if selected_decision not in VALID_SELECTED_DECISIONS:
        blockers.append("selected_decision_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if source_status not in VALID_SOURCE_STATUSES:
        blockers.append("remote8f_status_unrecognized")
    if selected_decision == "prepare_next_controlled_movement" and source_status != CLEAN_SOURCE_STATUS:
        blockers.append("prepare_next_movement_requires_clean_monitoring")
    if selected_decision == "prepare_next_controlled_movement" and monitoring_blockers:
        blockers.append("prepare_next_movement_requires_zero_monitoring_blockers")
    if user_count < MIN_COHORT_SIZE or user_count > MAX_COHORT_SIZE:
        blockers.append("reviewed_user_count_out_of_range")
    if missing_checks:
        blockers.append("required_checks_missing")
    if execution_blockers:
        blockers.append("execution_metrics_must_remain_zero")
    blockers.extend(_user_blockers(users))

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": (
            "GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY"
            if valid
            else "NO_GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_BLOCKED"
        ),
        "version": REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION,
        "generatedAt": _utc_now(),
        "decisionReview": {
            "id": str(payload.get("decisionId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "selectedDecision": selected_decision,
            "reviewedUserCount": user_count,
            "users": _public_users(users),
            "monitoringBlockerCount": monitoring_blockers,
        },
        "sourceGate": {
            "remote8fStatus": source_status,
            "remote8fMonitoringId": _short(source_gate.get("remote8fMonitoringId")),
        },
        "checks": checks,
        "missingChecks": missing_checks,
        "executionMetrics": execution_metrics,
        "executionBlockers": execution_blockers,
        "blockers": blockers,
        "decision": {
            "ready": valid,
            "allowedNextAction": _allowed_next_action(selected_decision, valid),
            "automationAllowed": False,
            "executionAllowedNow": False,
            "requiresSeparateNextPhase": True,
        },
        "safety": {
            "rollbackReady": bool(checks.get("rollbackPlanReady")),
            "pauseRuleReady": bool(checks.get("pauseRuleReady")),
            "nextMovementPreparedOnly": selected_decision == "prepare_next_controlled_movement" and valid,
        },
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "supportLogsReturned": False,
            "decisionRationaleReturned": False,
        },
        "nextPhase": "REMOTE-8H-next-controlled-movement-package",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8G_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["decision"]["ready"] = False
        summary["decision"]["allowedNextAction"] = "fix_remote8g_privacy_leak"
        summary["safety"]["nextMovementPreparedOnly"] = False
    return summary


def ingest_remote8g_tiny_cohort_decision_review(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-8G decision evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8G_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8G_OUTPUT_ROOT
    summary_path = output_base / "remote8g_tiny_cohort_decision_review.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8G_DECISION_REVIEW_EVIDENCE_MISSING",
            "version": REMOTE_TINY_COHORT_DECISION_REVIEW_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8g_decision_review_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["tiny_cohort_decision_review_evidence_missing"],
            "decision": {
                "ready": False,
                "allowedNextAction": "collect_remote8g_private_evidence",
                "automationAllowed": False,
                "executionAllowedNow": False,
                "requiresSeparateNextPhase": True,
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "supportLogsReturned": False,
                "decisionRationaleReturned": False,
            },
            "nextPhase": "REMOTE-8G-private-decision-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8g_decision_review_summary(payload)
    _write_json(summary_path, summary)
    return summary
