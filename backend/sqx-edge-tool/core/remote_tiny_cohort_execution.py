from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_TINY_COHORT_EXECUTION_VERSION = "remote-tiny-cohort-execution-v1"
DEFAULT_REMOTE8E_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8e_tiny_cohort_execution.local.json"
)
DEFAULT_REMOTE8E_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8e_tiny_cohort_execution"

MIN_COHORT_SIZE = 3
MAX_COHORT_SIZE = 5
REQUIRED_SOURCE_STATUS = "GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY"
VALID_REQUESTED_ACTIONS = {"record_manual_activation_execution"}
VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}

REQUIRED_CHECKS = (
    "remote8dPackageGoConfirmed",
    "operatorFinalApprovalRecorded",
    "manualExecutionOnly",
    "noAutomationUsed",
    "privateMessagesSent",
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
        raise ValueError("remote8e_execution_must_be_json_object")
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


def _user_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_users = payload.get("activatedUsers") if isinstance(payload.get("activatedUsers"), list) else []
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
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
    values.extend(str(user.get("_rawEmail") or "") for user in _user_records(payload))
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


def build_remote8e_execution_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8E manual tiny cohort execution record."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_action = str(payload.get("requestedAction") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    source_gate = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    source_status = str(source_gate.get("remote8dStatus") or "").strip()
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    manual_counts = _counts_from_payload(payload, "manualCounts", MANUAL_COUNT_METRICS)
    automation_metrics = _counts_from_payload(payload, "automationMetrics", ZERO_AUTOMATION_METRICS)
    users = _user_records(payload)
    user_count = len(users)
    automation_blockers = [metric for metric, value in automation_metrics.items() if value]
    manual_count_blockers = [metric for metric in MANUAL_COUNT_METRICS if manual_counts.get(metric) != user_count]
    blockers: list[str] = []

    if schema_version != REMOTE_TINY_COHORT_EXECUTION_VERSION:
        blockers.append("remote8e_schema_version_mismatch")
    if requested_action not in VALID_REQUESTED_ACTIONS:
        blockers.append("requested_action_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if source_status != REQUIRED_SOURCE_STATUS:
        blockers.append("remote8d_package_go_status_missing")
    if user_count < MIN_COHORT_SIZE or user_count > MAX_COHORT_SIZE:
        blockers.append("activated_user_count_out_of_range")
    if missing_checks:
        blockers.append("required_checks_missing")
    if automation_blockers:
        blockers.append("automation_metrics_must_remain_zero")
    if manual_count_blockers:
        blockers.append("manual_execution_counts_mismatch")
    blockers.extend(_user_blockers(users))

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": (
            "GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED"
            if valid
            else "NO_GO_REMOTE8E_TINY_COHORT_EXECUTION_BLOCKED"
        ),
        "version": REMOTE_TINY_COHORT_EXECUTION_VERSION,
        "generatedAt": _utc_now(),
        "execution": {
            "id": str(payload.get("executionId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedAction": requested_action,
            "mode": "manual_operator_record",
            "activatedUserCount": user_count,
            "users": _public_users(users),
        },
        "sourceGate": {
            "remote8dStatus": source_status,
            "remote8dPackageId": _short(source_gate.get("remote8dPackageId")),
        },
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
            "allowedNextAction": "start_tiny_cohort_monitoring" if valid else "fix_remote8e_blockers",
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
        },
        "nextPhase": "REMOTE-8F-tiny-cohort-monitoring",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8E_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["record"]["ready"] = False
        summary["record"]["allowedNextAction"] = "fix_remote8e_privacy_leak"
    return summary


def ingest_remote8e_tiny_cohort_execution(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-8E execution evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8E_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8E_OUTPUT_ROOT
    summary_path = output_base / "remote8e_tiny_cohort_execution.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8E_EXECUTION_EVIDENCE_MISSING",
            "version": REMOTE_TINY_COHORT_EXECUTION_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8e_execution_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["tiny_cohort_execution_evidence_missing"],
            "record": {
                "ready": False,
                "allowedNextAction": "collect_remote8e_private_evidence",
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
            },
            "nextPhase": "REMOTE-8E-private-execution-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8e_execution_summary(payload)
    _write_json(summary_path, summary)
    return summary
