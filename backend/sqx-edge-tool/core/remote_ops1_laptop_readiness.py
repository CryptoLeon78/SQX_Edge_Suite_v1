from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_OPS1_LAPTOP_READINESS_VERSION = "remote-ops1-laptop-readiness-v1"
DEFAULT_REMOTE_OPS1_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote_ops1_laptop_readiness.local.json"
)
DEFAULT_REMOTE_OPS1_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote_ops1_laptop_readiness"

REQUIRED_CHECKS = (
    "powerPlanReviewed",
    "sleepDisabled",
    "rebootRecoveryPlanReady",
    "remoteServicePreflightStrictGo",
    "watchdogSmokeGo",
    "backendLocalHealthGo",
    "backendBoundToLocalhostOnly",
    "sqxPathsReady",
    "sqxDataDbReady",
    "templatesReady",
    "outputWritable",
    "workspaceRootReady",
    "cloudflaredInstalled",
    "tunnelPreflightGo",
    "tunnelStartupPlanReady",
    "accessAnonymousBlocked",
    "appSessionSmokeReady",
    "workspaceSmokeReady",
    "artifactGenerationSmokeReady",
    "revocationSmokeReady",
    "restorePlanReady",
    "logsWrittenToIgnoredLocalPath",
    "privateEvidenceStoredOutsideGit",
    "noSecretsInGitConfirmed",
    "noRouterPortsOpened",
    "noUsersInvited",
)

ZERO_RISK_METRICS = (
    "newUsersInvited",
    "paidUsersActivated",
    "testerGrantsChanged",
    "checkoutLinksCreated",
    "emailsSent",
    "publicUrlsShared",
    "routerPortsOpened",
    "automationJobsStarted",
    "unresolvedSupportIssues",
    "workspaceLeakIncidents",
    "securityIncidents",
    "tunnelDropsDuringSmoke",
    "backendHealthFailures",
    "artifactGenerationFailures",
    "revocationFailures",
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
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("remote_ops1_laptop_readiness_must_be_json_object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _checks_from_payload(payload: Mapping[str, Any]) -> dict[str, bool]:
    raw = payload.get("checks") if isinstance(payload.get("checks"), Mapping) else {}
    return {check: bool(raw.get(check)) for check in REQUIRED_CHECKS}


def _metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("riskMetrics") if isinstance(payload.get("riskMetrics"), Mapping) else {}
    return {metric: _nonnegative_int(raw.get(metric)) for metric in ZERO_RISK_METRICS}


def _environment_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = payload.get("environment") if isinstance(payload.get("environment"), Mapping) else {}
    return {
        "hostClass": str(raw.get("hostClass") or "windows_laptop").strip(),
        "backendPort": _nonnegative_int(raw.get("backendPort") or 5050),
        "backendBind": "localhost_only" if raw.get("backendBind") else "unknown",
        "cloudflareMode": "tunnel_access" if raw.get("cloudflareMode") else "unknown",
        "workspaceMode": "server_derived" if raw.get("workspaceMode") else "unknown",
        "sqxMode": "server_managed" if raw.get("sqxMode") else "unknown",
    }


def _private_values(payload: Mapping[str, Any]) -> tuple[str, ...]:
    raw = payload.get("privateRefs") if isinstance(payload.get("privateRefs"), Mapping) else {}
    values = [
        raw.get("protectedUrl"),
        raw.get("cloudflareAccountId"),
        raw.get("cloudflareTunnelId"),
        raw.get("cloudflareAccessAppId"),
        raw.get("localWorkspaceRoot"),
        raw.get("sqxPath"),
        raw.get("sqxDataDb"),
        raw.get("operatorEmail"),
    ]
    return tuple(str(value).strip() for value in values if str(value or "").strip())


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
    if EMAIL_RE.search(serialized):
        leaks.append("email_returned")
    return leaks


def build_remote_ops1_laptop_readiness_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-OPS1 laptop production readiness summary."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    requested_action = str(payload.get("requestedAction") or "").strip()
    checks = _checks_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    risk_metrics = _metrics_from_payload(payload)
    risk_blockers = [metric for metric, value in risk_metrics.items() if value]
    blockers: list[str] = []

    if schema_version != REMOTE_OPS1_LAPTOP_READINESS_VERSION:
        blockers.append("remote_ops1_schema_version_mismatch")
    if requested_action != "validate_laptop_production_readiness":
        blockers.append("requested_action_invalid")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if missing_checks:
        blockers.append("required_checks_missing")
    if risk_blockers:
        blockers.append("risk_metrics_must_remain_zero")

    valid = not blockers
    summary: dict[str, Any] = {
        "ok": valid,
        "status": "GO_REMOTE_OPS1_LAPTOP_READY" if valid else "NO_GO_REMOTE_OPS1_LAPTOP_READINESS_BLOCKED",
        "version": REMOTE_OPS1_LAPTOP_READINESS_VERSION,
        "generatedAt": _utc_now(),
        "drill": {
            "id": str(payload.get("drillId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            "requestedAction": requested_action,
            "operatorApproval": operator_approval,
            "environment": _environment_summary(payload),
        },
        "checks": checks,
        "missingChecks": missing_checks,
        "riskMetrics": risk_metrics,
        "riskBlockers": risk_blockers,
        "blockers": blockers,
        "readiness": {
            "laptopReady": valid,
            "backendReady": bool(
                checks.get("remoteServicePreflightStrictGo")
                and checks.get("watchdogSmokeGo")
                and checks.get("backendLocalHealthGo")
                and checks.get("backendBoundToLocalhostOnly")
            ),
            "sqxReady": bool(
                checks.get("sqxPathsReady")
                and checks.get("sqxDataDbReady")
                and checks.get("templatesReady")
                and checks.get("outputWritable")
            ),
            "tunnelReady": bool(
                checks.get("cloudflaredInstalled")
                and checks.get("tunnelPreflightGo")
                and checks.get("tunnelStartupPlanReady")
                and checks.get("accessAnonymousBlocked")
            ),
            "pilotSmokeReady": bool(
                checks.get("appSessionSmokeReady")
                and checks.get("workspaceSmokeReady")
                and checks.get("artifactGenerationSmokeReady")
                and checks.get("revocationSmokeReady")
            ),
            "executionAllowedNow": False,
            "userExpansionAllowedNow": False,
            "requiresRemote8hEvidenceBeforeMovement": True,
        },
        "privacy": {
            "rawEmailsReturned": False,
            "protectedUrlReturned": False,
            "cloudflareIdentifiersReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "privateEvidenceCommitted": False,
        },
        "nextPhase": "REMOTE-8H-private-package-evidence" if valid else "REMOTE-OPS1-fix-readiness-blockers",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE_OPS1_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
        summary["readiness"]["laptopReady"] = False
        summary["nextPhase"] = "REMOTE-OPS1-fix-privacy-leak"
    return summary


def ingest_remote_ops1_laptop_readiness(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored REMOTE-OPS1 laptop readiness evidence and write a redacted summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE_OPS1_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE_OPS1_OUTPUT_ROOT
    summary_path = output_base / "remote_ops1_laptop_readiness.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE_OPS1_LAPTOP_READINESS_EVIDENCE_MISSING",
            "version": REMOTE_OPS1_LAPTOP_READINESS_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote_ops1_laptop_readiness_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["remote_ops1_laptop_readiness_evidence_missing"],
            "readiness": {
                "laptopReady": False,
                "executionAllowedNow": False,
                "userExpansionAllowedNow": False,
                "requiresRemote8hEvidenceBeforeMovement": True,
            },
            "privacy": {
                "rawEmailsReturned": False,
                "protectedUrlReturned": False,
                "cloudflareIdentifiersReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "privateEvidenceCommitted": False,
            },
            "nextPhase": "REMOTE-OPS1-private-readiness-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote_ops1_laptop_readiness_summary(payload)
    _write_json(summary_path, summary)
    return summary
