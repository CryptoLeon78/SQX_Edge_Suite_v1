from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION = "remote-next-controlled-movement-monitoring-v1"
DEFAULT_REMOTE8K_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8k_next_controlled_movement_monitoring.local.json"
)
DEFAULT_REMOTE8K_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8k_next_controlled_movement_monitoring"

REQUIRED_SOURCE_STATUS = "GO_REMOTE8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION_RECORDED"
MIN_OBSERVATION_HOURS = 24
MAX_EXECUTED_USERS = 2
VALID_REQUESTED_DECISIONS = {
    "continue_monitoring",
    "fix_blockers",
    "rollback_last_movement",
    "prepare_next_decision_review",
}
VALID_MOVEMENT_TYPES = {
    "add_1_2_users",
    "extend_same_cohort_observation",
    "prepare_paid_micro_offer",
    "schedule_demo_batch",
}
VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}

REQUIRED_SIGNALS = (
    "remote8jExecutionGoConfirmed",
    "manualScopeStillMatches",
    "accessStable",
    "cloudflareAccessStable",
    "appSessionStable",
    "entitlementStable",
    "workspaceIsolationClean",
    "artifactGenerationObserved",
    "exportsDownloaded",
    "supportLoopObserved",
    "noWorkspaceLeakage",
    "noSecurityIncidents",
    "noUnresolvedSupportBlockers",
    "rollbackPlanReady",
    "pauseRuleReady",
    "privateEvidenceStoredOutsideGit",
)

PER_USER_REQUIRED_FLAGS = (
    "accessVerified",
    "entitlementChecked",
    "workspaceIsolationChecked",
    "artifactFlowChecked",
    "supportWindowAcknowledged",
    "noCriticalIssue",
)

ZERO_TOLERANCE_METRICS = (
    "openSupportItems",
    "unresolvedBlockers",
    "tunnelDrops",
    "appSessionFailures",
    "workspaceLeakEvents",
    "securityIncidents",
    "generationFailures",
    "exportFailures",
    "entitlementErrors",
    "refundRequests",
    "crossUserDataFindings",
    "publicUrlLeaks",
    "automationJobsStarted",
    "trafficExpanded",
    "paidCampaignStarted",
    "checkoutLinksCreated",
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
        raise ValueError("remote8k_monitoring_must_be_json_object")
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


def _signals_from_payload(payload: Mapping[str, Any]) -> dict[str, bool]:
    raw = payload.get("signals") if isinstance(payload.get("signals"), Mapping) else {}
    return {signal: bool(raw.get(signal)) for signal in REQUIRED_SIGNALS}


def _metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("zeroToleranceMetrics") if isinstance(payload.get("zeroToleranceMetrics"), Mapping) else {}
    return {metric: _nonnegative_int(raw.get(metric)) for metric in ZERO_TOLERANCE_METRICS}


def _source_gate_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    return {
        "remote8jStatus": str(raw.get("remote8jStatus") or "").strip(),
        "remote8jExecutionId": _short(raw.get("remote8jExecutionId")),
        "movementType": str(raw.get("movementType") or "").strip(),
        "executedUserCount": _nonnegative_int(raw.get("executedUserCount")),
    }


def _user_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_users = payload.get("monitoredUsers") if isinstance(payload.get("monitoredUsers"), list) else []
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
                "monitoringFlags": flags,
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
        flags = user.get("monitoringFlags") if isinstance(user.get("monitoringFlags"), Mapping) else {}
        for flag in PER_USER_REQUIRED_FLAGS:
            if not flags.get(flag):
                blockers.append(f"user_{index}_{flag}_missing")
    return blockers


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    private_notes = payload.get("privateMonitoring") if isinstance(payload.get("privateMonitoring"), Mapping) else {}
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
    values.extend(str(value or "").strip() for value in private_notes.values())
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
        flags = user.get("monitoringFlags") if isinstance(user.get("monitoringFlags"), Mapping) else {}
        public_users.append(
            {
                "index": user.get("index"),
                "kind": user.get("kind"),
                "featureScope": user.get("featureScope"),
                "emailRef": user.get("emailRef"),
                "emailHashRef": user.get("emailHashRef"),
                "accessVerified": bool(flags.get("accessVerified")),
                "entitlementChecked": bool(flags.get("entitlementChecked")),
                "workspaceIsolationChecked": bool(flags.get("workspaceIsolationChecked")),
                "artifactFlowChecked": bool(flags.get("artifactFlowChecked")),
                "supportWindowAcknowledged": bool(flags.get("supportWindowAcknowledged")),
                "noCriticalIssue": bool(flags.get("noCriticalIssue")),
            }
        )
    return public_users


def _allowed_next_action(requested_decision: str, valid: bool) -> str:
    if not valid:
        return "fix_remote8k_blockers"
    if requested_decision == "prepare_next_decision_review":
        return "prepare_remote8l_post_monitoring_decision_review"
    if requested_decision == "continue_monitoring":
        return "continue_remote8k_monitoring"
    return "operator_review_required"


def build_remote8k_monitoring_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8K post-execution monitoring summary."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_decision = str(payload.get("requestedDecision") or "").strip()
    operator_review = bool(payload.get("operatorReview"))
    observation_hours = _nonnegative_int(payload.get("observationHours"))
    source_gate = _source_gate_from_payload(payload)
    signals = _signals_from_payload(payload)
    missing_signals = [signal for signal, passed in signals.items() if not passed]
    metrics = _metrics_from_payload(payload)
    metric_blockers = [metric for metric, value in metrics.items() if value]
    users = _user_records(payload)
    user_count = len(users)
    blockers: list[str] = []

    if schema_version != REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION:
        blockers.append("remote8k_schema_version_mismatch")
    if requested_decision not in VALID_REQUESTED_DECISIONS:
        blockers.append("requested_decision_invalid")
    if not operator_review:
        blockers.append("operator_review_missing")
    if source_gate["remote8jStatus"] != REQUIRED_SOURCE_STATUS:
        blockers.append("remote8j_manual_execution_go_status_missing")
    if not source_gate["remote8jExecutionId"]:
        blockers.append("remote8j_execution_id_missing")
    if source_gate["movementType"] not in VALID_MOVEMENT_TYPES:
        blockers.append("movement_type_invalid")
    if observation_hours < MIN_OBSERVATION_HOURS:
        blockers.append("minimum_observation_hours_not_met")
    if source_gate["movementType"] == "add_1_2_users":
        if source_gate["executedUserCount"] < 1 or source_gate["executedUserCount"] > MAX_EXECUTED_USERS:
            blockers.append("executed_user_count_out_of_range")
        if user_count != source_gate["executedUserCount"]:
            blockers.append("monitored_user_count_must_match_executed_user_count")
    elif user_count:
        blockers.append("non_user_movement_must_not_include_monitored_users")
    if missing_signals:
        blockers.append("required_signals_missing")
    if metric_blockers:
        blockers.append("zero_tolerance_metrics_nonzero")
    if requested_decision in {"fix_blockers", "rollback_last_movement"} and not (missing_signals or metric_blockers):
        blockers.append("fix_or_rollback_decision_requires_recorded_blockers")
    blockers.extend(_user_blockers(users))

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": (
            "GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_CLEAN"
            if valid
            else "NO_GO_REMOTE8K_NEXT_CONTROLLED_MOVEMENT_MONITORING_BLOCKED"
        ),
        "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION,
        "generatedAt": _utc_now(),
        "monitoring": {
            "id": str(payload.get("monitoringId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedDecision": requested_decision,
            "observationHours": observation_hours,
            "minimumObservationHours": MIN_OBSERVATION_HOURS,
            "movementType": source_gate["movementType"],
            "monitoredUserCount": user_count,
            "users": _public_users(users),
        },
        "sourceGate": source_gate,
        "signals": signals,
        "missingSignals": missing_signals,
        "zeroToleranceMetrics": metrics,
        "metricBlockers": metric_blockers,
        "blockers": blockers,
        "decision": {
            "ready": valid,
            "allowedNextAction": _allowed_next_action(requested_decision, valid),
            "automationAllowed": False,
            "furtherExpansionAllowedNow": False,
            "requiresOperatorApprovalForNextMovement": True,
        },
        "safety": {
            "rollbackReady": bool(signals.get("rollbackPlanReady")),
            "pauseRuleReady": bool(signals.get("pauseRuleReady")),
            "monitoringWindowClean": valid,
        },
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "supportLogsReturned": False,
            "privateNotesReturned": False,
        },
        "nextPhase": "REMOTE-8L-post-monitoring-decision-review",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8K_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["decision"]["ready"] = False
        summary["decision"]["allowedNextAction"] = "fix_remote8k_privacy_leak"
        summary["safety"]["monitoringWindowClean"] = False
    return summary


def ingest_remote8k_next_controlled_movement_monitoring(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-8K monitoring evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8K_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8K_OUTPUT_ROOT
    summary_path = output_base / "remote8k_next_controlled_movement_monitoring.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8K_MONITORING_EVIDENCE_MISSING",
            "version": REMOTE_NEXT_CONTROLLED_MOVEMENT_MONITORING_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8k_monitoring_evidence_missing",
            "missingSignals": list(REQUIRED_SIGNALS),
            "blockers": ["next_controlled_movement_monitoring_evidence_missing"],
            "decision": {
                "ready": False,
                "allowedNextAction": "collect_remote8k_private_evidence",
                "automationAllowed": False,
                "furtherExpansionAllowedNow": False,
                "requiresOperatorApprovalForNextMovement": True,
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "supportLogsReturned": False,
                "privateNotesReturned": False,
            },
            "nextPhase": "REMOTE-8K-private-monitoring-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8k_monitoring_summary(payload)
    _write_json(summary_path, summary)
    return summary
