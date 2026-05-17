from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_BROWSER_ACCEPTANCE_VERSION = "remote-browser-acceptance-v1"
DEFAULT_REMOTE_ACCEPT1_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote_accept1_browser_acceptance.local.json"
)
DEFAULT_REMOTE_ACCEPT1_OUTPUT_ROOT = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote_accept1_browser_acceptance"
)

REQUIRED_CHECKS = (
    "cloudflareAccessPassed",
    "welcomeTitleMatches",
    "commercialNameIsSqxEdgeSuite",
    "identityCopyIsUserFriendly",
    "noInternalAppSessionCopy",
    "dashboardButtonClickedOnce",
    "welcomeDidNotBounceBack",
    "dashboardUsableAfterEntry",
    "workspaceVisibleWithoutLocalPaths",
    "noRawEmailTokenCookieUrlOrCloudflareIdCaptured",
    "browserCloseDoesNotKeepAppSessionExpectation",
    "privateEvidenceStoredOutsideGit",
)

ZERO_METRICS = (
    "welcomeBounceBacks",
    "visibleErrorMessages",
    "sessionPersistenceAfterBrowserClose",
    "privateDataLeaksObserved",
)

FORBIDDEN_PUBLIC_MARKERS = (
    "@" + "gmail.com",
    "@" + "hotmail.com",
    "CLOUDFLARE" + "_API_TOKEN=",
    "SQX_REMOTE" + "_SESSION_SECRET=",
    "SQX_REMOTE" + "_PAYMENT_WEBHOOK_SECRET=",
    "__Host-sqx_remote_session",
    "cf_clearance",
    "CF_Authorization",
)

HTTP_URL_RE = re.compile(r"https?://", re.IGNORECASE)
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/]")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("remote_accept1_evidence_must_be_json_object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _safe_text(value: Any, default: str = "unknown") -> str:
    text = str(value or "").strip()
    return text or default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _checks_from_payload(payload: Mapping[str, Any]) -> dict[str, bool]:
    raw = payload.get("checks") if isinstance(payload.get("checks"), Mapping) else {}
    return {check: bool(raw.get(check)) for check in REQUIRED_CHECKS}


def _metrics_from_payload(payload: Mapping[str, Any]) -> dict[str, int]:
    raw = payload.get("metrics") if isinstance(payload.get("metrics"), Mapping) else {}
    return {
        "dashboardButtonClicksRequired": _safe_int(raw.get("dashboardButtonClicksRequired"), 999),
        **{metric: _safe_int(raw.get(metric)) for metric in ZERO_METRICS},
    }


def _summary_leak_markers(summary: Mapping[str, Any]) -> list[str]:
    serialized = json.dumps(summary, sort_keys=True, ensure_ascii=True)
    leaks: list[str] = []
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker in serialized:
            leaks.append(f"forbidden_marker:{marker}")
    if HTTP_URL_RE.search(serialized):
        leaks.append("url_returned")
    if WINDOWS_PATH_RE.search(serialized):
        leaks.append("windows_path_returned")
    return leaks


def build_remote_accept1_browser_acceptance_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a redacted REMOTE-ACCEPT1 browser acceptance summary from private evidence."""
    schema_version = _safe_text(payload.get("schemaVersion"), "")
    operator_approval = bool(payload.get("operatorApproval"))
    checks = _checks_from_payload(payload)
    metrics = _metrics_from_payload(payload)
    missing_checks = [check for check, passed in checks.items() if not passed]
    metric_blockers = []
    if metrics["dashboardButtonClicksRequired"] != 1:
        metric_blockers.append("dashboard_button_click_count_not_one")
    metric_blockers.extend(metric for metric in ZERO_METRICS if metrics[metric] != 0)

    blockers: list[str] = []
    if schema_version != REMOTE_BROWSER_ACCEPTANCE_VERSION:
        blockers.append("remote_accept1_schema_version_mismatch")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if missing_checks:
        blockers.append("required_checks_missing")
    if metric_blockers:
        blockers.append("acceptance_metrics_not_clean")

    ok = not blockers
    browser = payload.get("browser") if isinstance(payload.get("browser"), Mapping) else {}
    summary: dict[str, Any] = {
        "ok": ok,
        "status": (
            "GO_REMOTE_ACCEPT1_BROWSER_ACCEPTANCE_CLEAN"
            if ok else "NO_GO_REMOTE_ACCEPT1_BROWSER_ACCEPTANCE_BLOCKED"
        ),
        "version": REMOTE_BROWSER_ACCEPTANCE_VERSION,
        "generatedAt": _utc_now(),
        "evidence": {
            "phase": _safe_text(payload.get("phase")),
            "capturedAt": _safe_text(payload.get("capturedAt"), ""),
            "testerKind": _safe_text(payload.get("testerKind")),
        },
        "browser": {
            "name": _safe_text(browser.get("name")),
            "mode": _safe_text(browser.get("mode")),
            "closedAndReopened": bool(browser.get("closedAndReopened")),
        },
        "checks": checks,
        "metrics": metrics,
        "missingChecks": missing_checks,
        "metricBlockers": metric_blockers,
        "blockers": blockers,
        "privacy": {
            "rawEmailReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "cookiesReturned": False,
            "tokensReturned": False,
            "cloudflareIdsReturned": False,
        },
        "expansionGate": {
            "allowedToExpandBeyondOneUser": False,
            "reason": "requires_remote8c_observation_even_when_remote_accept1_is_go",
        },
        "nextPhase": "REMOTE-8C-first-user-observation",
    }

    leaks = _summary_leak_markers(summary)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE_ACCEPT1_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
    return summary


def ingest_remote_accept1_browser_acceptance(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored private REMOTE-ACCEPT1 evidence and write a redacted summary."""
    source = (
        Path(evidence_path).expanduser().resolve(strict=False)
        if evidence_path else DEFAULT_REMOTE_ACCEPT1_EVIDENCE_PATH
    )
    output_base = (
        Path(output_root).expanduser().resolve(strict=False)
        if output_root else DEFAULT_REMOTE_ACCEPT1_OUTPUT_ROOT
    )
    summary_path = output_base / "remote_accept1_browser_acceptance.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE_ACCEPT1_PRIVATE_EVIDENCE_MISSING",
            "version": REMOTE_BROWSER_ACCEPTANCE_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote_accept1_private_evidence_missing",
            "missingChecks": list(REQUIRED_CHECKS),
            "blockers": ["private_browser_acceptance_evidence_missing"],
            "privacy": {
                "rawEmailReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "cookiesReturned": False,
                "tokensReturned": False,
                "cloudflareIdsReturned": False,
            },
            "expansionGate": {
                "allowedToExpandBeyondOneUser": False,
                "reason": "real_browser_acceptance_must_be_collected_locally_before_expansion",
            },
            "nextPhase": "REMOTE-ACCEPT1-private-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote_accept1_browser_acceptance_summary(payload)
    _write_json(summary_path, summary)
    return summary
