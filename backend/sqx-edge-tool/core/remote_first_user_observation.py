from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_FIRST_USER_OBSERVATION_VERSION = "remote-first-user-observation-v1"
DEFAULT_REMOTE8C_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8c_first_user_observation.local.json"
)
DEFAULT_REMOTE8C_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8c_first_user_observation"
MIN_OBSERVATION_HOURS = 24
VALID_REQUESTED_DECISIONS = {"stay_one_user", "fix_blockers", "expand_3_5"}

REQUIRED_SIGNALS = (
    "remote8bEvidenceGo",
    "firstUserCompletedGuidedFlow",
    "supportLoopObserved",
    "tunnelStable",
    "appSessionStable",
    "entitlementStable",
    "workspaceIsolationClean",
    "artifactGenerated",
    "exportDownloaded",
    "revocationRestoreConfidence",
    "noWorkspaceLeakage",
    "noSecurityIncidents",
    "noUnresolvedSupportBlockers",
    "supportEvidenceRedacted",
    "privateEvidenceStoredOutsideGit",
)

MAX_ZERO_METRICS = (
    "openSupportItems",
    "unresolvedBlockers",
    "tunnelDrops",
    "appSessionFailures",
    "workspaceLeakEvents",
    "securityIncidents",
    "generationFailures",
    "entitlementErrors",
    "refundRequests",
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
        raise ValueError("remote8c_observation_must_be_json_object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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


def _metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("metrics") if isinstance(payload.get("metrics"), Mapping) else {}
    metrics = {metric: _nonnegative_int(raw.get(metric)) for metric in MAX_ZERO_METRICS}
    metrics["supportResponseHours"] = _number(raw.get("supportResponseHours"))
    return metrics


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    user = payload.get("pilotUser") if isinstance(payload.get("pilotUser"), Mapping) else {}
    environment = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), Mapping) else {}
    values = [
        normalize_email(str(user.get("email") or "")),
        str(environment.get("protectedUrl") or "").strip(),
        str(environment.get("url") or "").strip(),
        str(environment.get("localPath") or "").strip(),
        str(artifacts.get("localPath") or "").strip(),
        str(artifacts.get("workspacePath") or "").strip(),
    ]
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


def _public_identity(payload: Mapping[str, Any]) -> dict[str, Any]:
    user = payload.get("pilotUser") if isinstance(payload.get("pilotUser"), Mapping) else {}
    email = normalize_email(str(user.get("email") or ""))
    digest = email_hash(email)
    return {
        "userKind": str(user.get("kind") or "").strip() or "unknown",
        "emailRef": redact_email(email),
        "emailHashRef": digest[:12] if digest else "",
    }


def _status_for(valid: bool, requested_decision: str) -> str:
    if not valid:
        return "NO_GO_REMOTE8C_FIRST_USER_OBSERVATION_BLOCKED"
    if requested_decision == "expand_3_5":
        return "GO_REMOTE8C_TINY_COHORT_EXPANSION_READY"
    if requested_decision == "stay_one_user":
        return "GO_REMOTE8C_STAY_ONE_USER_DECISION_RECORDED"
    return "NO_GO_REMOTE8C_FIX_BLOCKERS_SELECTED"


def build_remote8c_observation_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8C first-user observation decision."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    requested_decision = str(payload.get("requestedDecision") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    observation_hours = _number(payload.get("observationWindowHours"))
    signals = _signals_from_payload(payload)
    metrics = _metrics_from_payload(payload)
    missing_signals = [signal for signal, passed in signals.items() if not passed]
    metric_blockers = [metric for metric in MAX_ZERO_METRICS if metrics.get(metric)]
    blockers: list[str] = []
    if schema_version != REMOTE_FIRST_USER_OBSERVATION_VERSION:
        blockers.append("remote8c_schema_version_mismatch")
    if requested_decision not in VALID_REQUESTED_DECISIONS:
        blockers.append("requested_decision_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if observation_hours < MIN_OBSERVATION_HOURS:
        blockers.append("observation_window_too_short")
    if missing_signals:
        blockers.append("required_signals_missing")
    if metric_blockers:
        blockers.append("zero_tolerance_metrics_nonzero")
    if requested_decision == "fix_blockers":
        blockers.append("operator_selected_fix_blockers")

    valid = not blockers
    expansion_allowed = valid and requested_decision == "expand_3_5"
    summary: dict[str, Any] = {
        "ok": valid,
        "status": _status_for(valid, requested_decision),
        "version": REMOTE_FIRST_USER_OBSERVATION_VERSION,
        "generatedAt": _utc_now(),
        "observation": {
            "id": str(payload.get("observationId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "observationWindowHours": observation_hours,
            "requestedDecision": requested_decision,
            **_public_identity(payload),
        },
        "previousGate": {
            "remote8bStatus": str((payload.get("previousGate") or {}).get("remote8bStatus") or "")
            if isinstance(payload.get("previousGate"), Mapping) else "",
            "remote8bEvidenceId": _short((payload.get("previousGate") or {}).get("remote8bEvidenceId"))
            if isinstance(payload.get("previousGate"), Mapping) else "",
        },
        "signals": signals,
        "metrics": metrics,
        "missingSignals": missing_signals,
        "metricBlockers": metric_blockers,
        "blockers": blockers,
        "decision": {
            "recommendedAction": (
                "prepare_tiny_cohort_3_5"
                if expansion_allowed else "stay_one_user_or_fix_blockers"
            ),
            "automationAllowed": False,
            "manualOperatorStepRequired": True,
        },
        "expansionGate": {
            "allowedToExpandToTinyCohort": expansion_allowed,
            "targetTotalUsers": "3-5" if expansion_allowed else "1",
            "reason": (
                "remote8c_evidence_clean_and_operator_requested_tiny_cohort"
                if expansion_allowed else "remote8c_does_not_allow_expansion"
            ),
        },
        "privacy": {
            "rawEmailReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
            "supportLogsReturned": False,
        },
        "nextPhase": "REMOTE-8D-tiny-cohort-activation-package",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8C_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["expansionGate"]["allowedToExpandToTinyCohort"] = False
        summary["expansionGate"]["targetTotalUsers"] = "1"
        summary["expansionGate"]["reason"] = "remote8c_public_summary_privacy_leak"
    return summary


def ingest_remote8c_first_user_observation(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored first-user observation evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8C_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8C_OUTPUT_ROOT
    summary_path = output_base / "remote8c_first_user_observation.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8C_OBSERVATION_EVIDENCE_MISSING",
            "version": REMOTE_FIRST_USER_OBSERVATION_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8c_observation_evidence_missing",
            "missingSignals": list(REQUIRED_SIGNALS),
            "blockers": ["first_user_observation_evidence_missing"],
            "expansionGate": {
                "allowedToExpandToTinyCohort": False,
                "targetTotalUsers": "1",
                "reason": "first_user_observation_must_be_collected_locally_before_expansion",
            },
            "privacy": {
                "rawEmailReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
                "supportLogsReturned": False,
            },
            "nextPhase": "REMOTE-8C-private-observation-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8c_observation_summary(payload)
    _write_json(summary_path, summary)
    return summary
