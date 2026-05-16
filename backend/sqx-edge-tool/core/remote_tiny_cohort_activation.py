from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_TINY_COHORT_ACTIVATION_VERSION = "remote-tiny-cohort-activation-v1"
DEFAULT_REMOTE8D_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8d_tiny_cohort_activation.local.json"
)
DEFAULT_REMOTE8D_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8d_tiny_cohort_activation"

MIN_COHORT_SIZE = 3
MAX_COHORT_SIZE = 5
REQUIRED_SOURCE_STATUS = "GO_REMOTE8C_TINY_COHORT_EXPANSION_READY"
VALID_ENTITLEMENT_KINDS = {"paid_subscription", "tester_free", "internal_operator"}
VALID_REQUESTED_ACTIONS = {"prepare_manual_activation_package"}

REQUIRED_CHECKS = (
    "remote8cGoConfirmed",
    "candidateListReviewed",
    "cohortSizeWithinLimit",
    "entitlementBoundariesDefined",
    "supportOwnerAssigned",
    "supportWindowReady",
    "rollbackPlanReady",
    "pauseRuleReady",
    "communicationCopyReviewed",
    "protectedUrlPrivateOnly",
    "workspaceIsolationReminder",
    "securityMonitoringReady",
    "noAutomationConfirmed",
    "privateEvidenceStoredOutsideGit",
)

ZERO_AUTOMATION_METRICS = (
    "invitesSent",
    "grantsCreated",
    "checkoutLinksCreated",
    "emailsSent",
    "publicUrlsShared",
    "automationJobsStarted",
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
        raise ValueError("remote8d_activation_must_be_json_object")
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


def _automation_metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("automationMetrics") if isinstance(payload.get("automationMetrics"), Mapping) else {}
    return {metric: _nonnegative_int(raw.get(metric)) for metric in ZERO_AUTOMATION_METRICS}


def _candidate_records(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
    records: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, Mapping):
            continue
        email = normalize_email(str(candidate.get("email") or ""))
        digest = email_hash(email)
        records.append({
            "index": index,
            "kind": str(candidate.get("kind") or "").strip(),
            "featureScope": str(candidate.get("featureScope") or "full").strip(),
            "emailRef": redact_email(email),
            "emailHashRef": digest[:12] if digest else "",
            "_rawEmail": email,
        })
    return records


def _candidate_kind_blockers(candidates: list[Mapping[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for candidate in candidates:
        if candidate.get("kind") not in VALID_ENTITLEMENT_KINDS:
            blockers.append(f"candidate_{candidate.get('index')}_kind_invalid")
        if not candidate.get("emailHashRef"):
            blockers.append(f"candidate_{candidate.get('index')}_identity_missing")
    return blockers


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    candidates = _candidate_records(payload)
    values = [
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
    ]
    values.extend(str(candidate.get("_rawEmail") or "") for candidate in candidates)
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
    return [
        {
            "index": candidate.get("index"),
            "kind": candidate.get("kind"),
            "featureScope": candidate.get("featureScope"),
            "emailRef": candidate.get("emailRef"),
            "emailHashRef": candidate.get("emailHashRef"),
        }
        for candidate in candidates
    ]


def build_remote8d_activation_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8D tiny cohort activation package summary."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_action = str(payload.get("requestedAction") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    target_size = _nonnegative_int(payload.get("targetCohortSize"))
    source_gate = payload.get("sourceGate") if isinstance(payload.get("sourceGate"), Mapping) else {}
    source_status = str(source_gate.get("remote8cStatus") or "").strip()
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    automation_metrics = _automation_metrics_from_payload(payload)
    automation_blockers = [metric for metric, value in automation_metrics.items() if value]
    candidates = _candidate_records(payload)
    candidate_count = len(candidates)
    blockers: list[str] = []

    if schema_version != REMOTE_TINY_COHORT_ACTIVATION_VERSION:
        blockers.append("remote8d_schema_version_mismatch")
    if requested_action not in VALID_REQUESTED_ACTIONS:
        blockers.append("requested_action_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if source_status != REQUIRED_SOURCE_STATUS:
        blockers.append("remote8c_go_status_missing")
    if target_size < MIN_COHORT_SIZE or target_size > MAX_COHORT_SIZE:
        blockers.append("target_cohort_size_out_of_range")
    if candidate_count < MIN_COHORT_SIZE or candidate_count > MAX_COHORT_SIZE:
        blockers.append("candidate_count_out_of_range")
    if target_size and candidate_count and target_size != candidate_count:
        blockers.append("target_cohort_size_candidate_count_mismatch")
    if missing_checks:
        blockers.append("required_checks_missing")
    if automation_blockers:
        blockers.append("automation_must_remain_zero")
    blockers.extend(_candidate_kind_blockers(candidates))

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": (
            "GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY"
            if valid else "NO_GO_REMOTE8D_TINY_COHORT_ACTIVATION_BLOCKED"
        ),
        "version": REMOTE_TINY_COHORT_ACTIVATION_VERSION,
        "generatedAt": _utc_now(),
        "package": {
            "id": str(payload.get("packageId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedAction": requested_action,
            "targetCohortSize": target_size,
            "candidateCount": candidate_count,
            "candidates": _public_candidates(candidates),
        },
        "sourceGate": {
            "remote8cStatus": source_status,
            "remote8cObservationId": _short(source_gate.get("remote8cObservationId")),
        },
        "checks": checks,
        "missingChecks": missing_checks,
        "automationMetrics": automation_metrics,
        "automationBlockers": automation_blockers,
        "blockers": blockers,
        "manualPackage": {
            "ready": valid,
            "allowedNextAction": "prepare_private_manual_cohort_activation" if valid else "fix_remote8d_blockers",
            "mustNotExecuteAutomatically": True,
            "requiresOperatorFinalConfirmation": True,
            "includes": [
                "private_recipient_list_refs",
                "entitlement_kind_boundaries",
                "support_window",
                "rollback_plan",
                "pause_rule",
                "private_communication_copy",
            ],
        },
        "executionGate": {
            "invitesAllowedNow": False,
            "grantMutationAllowedNow": False,
            "checkoutAllowedNow": False,
            "emailSendingAllowedNow": False,
            "protectedUrlSharingAllowedNow": False,
            "reason": "remote8d_prepares_manual_package_only",
        },
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "communicationCopyReturned": False,
        },
        "nextPhase": "REMOTE-8E-tiny-cohort-manual-execution-record",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8D_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["manualPackage"]["ready"] = False
        summary["manualPackage"]["allowedNextAction"] = "fix_remote8d_privacy_leak"
    return summary


def ingest_remote8d_tiny_cohort_activation(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored tiny cohort activation package evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8D_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8D_OUTPUT_ROOT
    summary_path = output_base / "remote8d_tiny_cohort_activation.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8D_ACTIVATION_PACKAGE_EVIDENCE_MISSING",
            "version": REMOTE_TINY_COHORT_ACTIVATION_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8d_activation_package_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["tiny_cohort_activation_package_evidence_missing"],
            "manualPackage": {
                "ready": False,
                "allowedNextAction": "collect_remote8d_private_evidence",
                "mustNotExecuteAutomatically": True,
                "requiresOperatorFinalConfirmation": True,
            },
            "executionGate": {
                "invitesAllowedNow": False,
                "grantMutationAllowedNow": False,
                "checkoutAllowedNow": False,
                "emailSendingAllowedNow": False,
                "protectedUrlSharingAllowedNow": False,
                "reason": "private_activation_package_evidence_required",
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "communicationCopyReturned": False,
            },
            "nextPhase": "REMOTE-8D-private-activation-package-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8d_activation_summary(payload)
    _write_json(summary_path, summary)
    return summary
