from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION = "remote-next-controlled-movement-package-v1"
DEFAULT_REMOTE8H_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8h_next_controlled_movement_package.local.json"
)
DEFAULT_REMOTE8H_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8h_next_controlled_movement_package"

LEGACY_SOURCE_STATUS = "GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY"
CURRENT_SOURCE_STATUS = "GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_READY"
VALID_SOURCE_STATUSES = {LEGACY_SOURCE_STATUS, CURRENT_SOURCE_STATUS}
REQUIRED_SOURCE_DECISION = "prepare_next_controlled_movement"
VALID_REQUESTED_ACTIONS = {"prepare_next_controlled_movement_package"}
VALID_MOVEMENT_TYPES = {
    "add_1_2_users",
    "extend_same_cohort_observation",
    "prepare_paid_micro_offer",
    "schedule_demo_batch",
}
VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}
MAX_NEW_USERS = 2

REQUIRED_CHECKS = (
    "sourceDecisionReviewed",
    "oneMovementOnly",
    "scopeLimited",
    "recipientListPrivate",
    "entitlementBoundaryDefined",
    "supportOwnerAssigned",
    "supportWindowReady",
    "rollbackPlanReady",
    "pauseRuleReady",
    "noAutomationConfirmed",
    "executionRequiresSeparateApproval",
    "privateEvidenceStoredOutsideGit",
)

CHECK_ALIASES = {
    "sourceDecisionReviewed": (
        "sourceDecisionReviewed",
        "remote8lDecisionReviewed",
        "remote8gDecisionReviewed",
    ),
}

CANDIDATE_REQUIRED_FLAGS = (
    "recipientReviewed",
    "entitlementKindReviewed",
    "supportExpectationReviewed",
    "privateHandoffRequired",
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
        raise ValueError("remote8h_package_must_be_json_object")
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
    checks: dict[str, bool] = {}
    for check in REQUIRED_CHECKS:
        aliases = CHECK_ALIASES.get(check, (check,))
        checks[check] = any(bool(raw.get(alias)) for alias in aliases)
    return checks


def _source_gate_from_payload(payload: Mapping[str, Any]) -> dict[str, str]:
    raw = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    source_type = str(raw.get("sourceType") or "").strip()
    if not source_type:
        if raw.get("remote8lStatus") or raw.get("remote8lSelectedDecision"):
            source_type = "remote8l_post_monitoring_decision_review"
        else:
            source_type = "remote8g_tiny_cohort_decision_review"

    if source_type == "remote8l_post_monitoring_decision_review":
        return {
            "sourceType": source_type,
            "status": str(raw.get("remote8lStatus") or raw.get("status") or "").strip(),
            "selectedDecision": str(raw.get("remote8lSelectedDecision") or raw.get("selectedDecision") or "").strip(),
            "decisionId": _short(raw.get("remote8lDecisionId") or raw.get("decisionId")),
        }

    return {
        "sourceType": "remote8g_tiny_cohort_decision_review",
        "status": str(raw.get("remote8gStatus") or raw.get("status") or "").strip(),
        "selectedDecision": str(raw.get("remote8gSelectedDecision") or raw.get("selectedDecision") or "").strip(),
        "decisionId": _short(raw.get("remote8gDecisionId") or raw.get("decisionId")),
    }


def _source_status_blocker_name(source_type: str) -> str:
    if source_type == "remote8l_post_monitoring_decision_review":
        return "remote8l_decision_go_status_missing"
    return "remote8g_decision_go_status_missing"


def _source_decision_blocker_name(source_type: str) -> str:
    if source_type == "remote8l_post_monitoring_decision_review":
        return "remote8l_selected_decision_not_next_movement"
    return "remote8g_selected_decision_not_next_movement"


def _execution_metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("executionMetrics") if isinstance(payload.get("executionMetrics"), Mapping) else {}
    return {metric: _nonnegative_int(raw.get(metric)) for metric in ZERO_EXECUTION_METRICS}


def _movement_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("movement") if isinstance(payload.get("movement"), Mapping) else {}
    return {
        "type": str(raw.get("type") or "").strip(),
        "plannedNewUsers": _nonnegative_int(raw.get("plannedNewUsers")),
        "supportWindowHours": _nonnegative_int(raw.get("supportWindowHours")),
        "maxDurationDays": _nonnegative_int(raw.get("maxDurationDays")),
    }


def _candidate_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_candidates = payload.get("candidateUsers") if isinstance(payload.get("candidateUsers"), list) else []
    records: list[dict[str, Any]] = []
    for index, candidate in enumerate(raw_candidates, start=1):
        if not isinstance(candidate, Mapping):
            continue
        email = normalize_email(str(candidate.get("email") or ""))
        digest = email_hash(email)
        flags = {flag: bool(candidate.get(flag)) for flag in CANDIDATE_REQUIRED_FLAGS}
        records.append(
            {
                "index": index,
                "kind": str(candidate.get("kind") or "").strip(),
                "featureScope": str(candidate.get("featureScope") or "full").strip(),
                "emailRef": redact_email(email),
                "emailHashRef": digest[:12] if digest else "",
                "candidateFlags": flags,
                "_rawEmail": email,
            }
        )
    return records


def _candidate_blockers(candidates: list[Mapping[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for candidate in candidates:
        index = candidate.get("index")
        if candidate.get("kind") not in VALID_ENTITLEMENT_KINDS:
            blockers.append(f"candidate_{index}_kind_invalid")
        if not candidate.get("emailHashRef"):
            blockers.append(f"candidate_{index}_identity_missing")
        flags = candidate.get("candidateFlags") if isinstance(candidate.get("candidateFlags"), Mapping) else {}
        for flag in CANDIDATE_REQUIRED_FLAGS:
            if not flags.get(flag):
                blockers.append(f"candidate_{index}_{flag}_missing")
    return blockers


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
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
        flags = candidate.get("candidateFlags") if isinstance(candidate.get("candidateFlags"), Mapping) else {}
        public_candidates.append(
            {
                "index": candidate.get("index"),
                "kind": candidate.get("kind"),
                "featureScope": candidate.get("featureScope"),
                "emailRef": candidate.get("emailRef"),
                "emailHashRef": candidate.get("emailHashRef"),
                "recipientReviewed": bool(flags.get("recipientReviewed")),
                "entitlementKindReviewed": bool(flags.get("entitlementKindReviewed")),
                "supportExpectationReviewed": bool(flags.get("supportExpectationReviewed")),
                "privateHandoffRequired": bool(flags.get("privateHandoffRequired")),
            }
        )
    return public_candidates


def build_remote8h_movement_package_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8H next controlled movement package summary."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_action = str(payload.get("requestedAction") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    source_gate = _source_gate_from_payload(payload)
    source_status = source_gate["status"]
    source_decision = source_gate["selectedDecision"]
    source_type = source_gate["sourceType"]
    movement = _movement_from_payload(payload)
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    execution_metrics = _execution_metrics_from_payload(payload)
    execution_blockers = [metric for metric, value in execution_metrics.items() if value]
    candidates = _candidate_records(payload)
    candidate_count = len(candidates)
    blockers: list[str] = []

    if schema_version != REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION:
        blockers.append("remote8h_schema_version_mismatch")
    if requested_action not in VALID_REQUESTED_ACTIONS:
        blockers.append("requested_action_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if source_status not in VALID_SOURCE_STATUSES:
        blockers.append(_source_status_blocker_name(source_type))
    if source_decision != REQUIRED_SOURCE_DECISION:
        blockers.append(_source_decision_blocker_name(source_type))
    if movement["type"] not in VALID_MOVEMENT_TYPES:
        blockers.append("movement_type_invalid")
    if movement["plannedNewUsers"] > MAX_NEW_USERS:
        blockers.append("planned_new_users_exceeds_limit")
    if movement["type"] == "add_1_2_users":
        if movement["plannedNewUsers"] < 1:
            blockers.append("add_users_requires_planned_users")
        if candidate_count != movement["plannedNewUsers"]:
            blockers.append("candidate_count_must_match_planned_new_users")
    elif candidate_count:
        blockers.append("non_user_movement_must_not_include_candidates")
    if movement["supportWindowHours"] < 24:
        blockers.append("support_window_too_short")
    if movement["maxDurationDays"] < 1:
        blockers.append("max_duration_days_missing")
    if missing_checks:
        blockers.append("required_checks_missing")
    if execution_blockers:
        blockers.append("execution_metrics_must_remain_zero")
    blockers.extend(_candidate_blockers(candidates))

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": (
            "GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_READY"
            if valid
            else "NO_GO_REMOTE8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE_BLOCKED"
        ),
        "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION,
        "generatedAt": _utc_now(),
        "package": {
            "id": str(payload.get("packageId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedAction": requested_action,
            "movement": movement,
            "candidateCount": candidate_count,
            "candidates": _public_candidates(candidates),
        },
        "sourceGate": {
            "sourceType": source_type,
            "status": source_status,
            "selectedDecision": source_decision,
            "decisionId": source_gate["decisionId"],
            "remote8gStatus": source_status if source_type == "remote8g_tiny_cohort_decision_review" else "",
            "remote8gSelectedDecision": source_decision if source_type == "remote8g_tiny_cohort_decision_review" else "",
            "remote8gDecisionId": source_gate["decisionId"] if source_type == "remote8g_tiny_cohort_decision_review" else "",
            "remote8lStatus": source_status if source_type == "remote8l_post_monitoring_decision_review" else "",
            "remote8lSelectedDecision": source_decision if source_type == "remote8l_post_monitoring_decision_review" else "",
            "remote8lDecisionId": source_gate["decisionId"] if source_type == "remote8l_post_monitoring_decision_review" else "",
        },
        "checks": checks,
        "missingChecks": missing_checks,
        "executionMetrics": execution_metrics,
        "executionBlockers": execution_blockers,
        "blockers": blockers,
        "movementPackage": {
            "ready": valid,
            "allowedNextAction": "request_remote8i_execution_approval" if valid else "fix_remote8h_blockers",
            "automationAllowed": False,
            "executionAllowedNow": False,
            "requiresSeparateExecutionApproval": True,
        },
        "safety": {
            "rollbackReady": bool(checks.get("rollbackPlanReady")),
            "pauseRuleReady": bool(checks.get("pauseRuleReady")),
            "oneMovementOnly": bool(checks.get("oneMovementOnly")),
        },
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "communicationCopyReturned": False,
            "privateEvidenceCommitted": False,
        },
        "nextPhase": "REMOTE-8I-next-controlled-movement-execution-approval",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8H_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["movementPackage"]["ready"] = False
        summary["movementPackage"]["allowedNextAction"] = "fix_remote8h_privacy_leak"
    return summary


def ingest_remote8h_next_controlled_movement_package(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-8H movement package evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8H_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8H_OUTPUT_ROOT
    summary_path = output_base / "remote8h_next_controlled_movement_package.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8H_MOVEMENT_PACKAGE_EVIDENCE_MISSING",
            "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_PACKAGE_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8h_movement_package_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["next_controlled_movement_package_evidence_missing"],
            "movementPackage": {
                "ready": False,
                "allowedNextAction": "collect_remote8h_private_evidence",
                "automationAllowed": False,
                "executionAllowedNow": False,
                "requiresSeparateExecutionApproval": True,
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "communicationCopyReturned": False,
                "privateEvidenceCommitted": False,
            },
            "nextPhase": "REMOTE-8H-private-package-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8h_movement_package_summary(payload)
    _write_json(summary_path, summary)
    return summary
