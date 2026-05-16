from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import email_hash, normalize_email, redact_email


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_LIVE_PILOT_EVIDENCE_VERSION = "remote-live-pilot-evidence-v1"
DEFAULT_REMOTE8B_EVIDENCE_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote8b_live_pilot_evidence.local.json"
)
DEFAULT_REMOTE8B_OUTPUT_ROOT = PROJECT_ROOT / ".local" / "remote_service" / "remote8b_live_pilot_evidence"

REQUIRED_PROOFS = (
    "remote8DrillBaselineGo",
    "edgeAccessBlockedAnonymous",
    "cloudflareAccessPassed",
    "appSessionLoginPassed",
    "entitlementActive",
    "workspaceCreated",
    "artifactGenerated",
    "exportDownloaded",
    "revocationBlockedAccess",
    "restoreAllowedAccess",
    "secondUserIsolationChecked",
    "noWorkspaceLeakage",
    "supportEvidenceRedacted",
    "privateEvidenceStoredOutsideGit",
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
        raise ValueError("remote8b_evidence_must_be_json_object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _short(value: Any, size: int = 12) -> str:
    text = str(value or "").strip()
    return text[:size] if text else ""


def _safe_filename(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    return text.rsplit("/", 1)[-1] if text else ""


def _artifact_hash(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if re.fullmatch(r"[0-9a-f]{64}", text) else ""


def _proofs_from_payload(payload: Mapping[str, Any]) -> dict[str, bool]:
    raw = payload.get("proofs") if isinstance(payload.get("proofs"), Mapping) else {}
    return {proof: bool(raw.get(proof)) for proof in REQUIRED_PROOFS}


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


def build_remote8b_evidence_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a public-safe REMOTE-8B summary from local-only private evidence."""
    schema_version = str(payload.get("schemaVersion") or "").strip()
    operator_approval = bool(payload.get("operatorApproval"))
    proofs = _proofs_from_payload(payload)
    missing_proofs = [proof for proof, passed in proofs.items() if not passed]
    blockers: list[str] = []
    if schema_version != REMOTE_LIVE_PILOT_EVIDENCE_VERSION:
        blockers.append("remote8b_schema_version_mismatch")
    if not operator_approval:
        blockers.append("operator_approval_missing")
    if missing_proofs:
        blockers.append("required_proofs_missing")

    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), Mapping) else {}
    ok = not blockers
    summary: dict[str, Any] = {
        "ok": ok,
        "status": (
            "GO_REMOTE8B_LIVE_PILOT_EVIDENCE_SAFE_NO_GIT_LEAK"
            if ok else "NO_GO_REMOTE8B_LIVE_PILOT_EVIDENCE_BLOCKED"
        ),
        "version": REMOTE_LIVE_PILOT_EVIDENCE_VERSION,
        "generatedAt": _utc_now(),
        "evidence": {
            "id": str(payload.get("evidenceId") or "").strip(),
            "capturedAt": str(payload.get("capturedAt") or "").strip(),
            **_public_identity(payload),
        },
        "environment": {
            "provider": str((payload.get("environment") or {}).get("provider") or "unknown")
            if isinstance(payload.get("environment"), Mapping) else "unknown",
            "windowsPilot": bool((payload.get("environment") or {}).get("windowsPilot"))
            if isinstance(payload.get("environment"), Mapping) else False,
            "protectedUrlSharedPrivately": bool((payload.get("environment") or {}).get("protectedUrlSharedPrivately"))
            if isinstance(payload.get("environment"), Mapping) else False,
        },
        "proofs": proofs,
        "missingProofs": missing_proofs,
        "blockers": blockers,
        "artifacts": {
            "generatedCfxName": _safe_filename(artifacts.get("generatedCfxName")),
            "artifactSha256": _artifact_hash(artifacts.get("artifactSha256")),
            "workspaceIdShort": _short(artifacts.get("workspaceId")),
        },
        "privacy": {
            "rawEmailReturned": False,
            "protectedUrlReturned": False,
            "localPathsReturned": False,
            "secretsReturned": False,
            "sessionTokenReturned": False,
            "grantKeysReturned": False,
        },
        "expansionGate": {
            "allowedToExpandBeyondOneUser": False,
            "reason": "requires_remote8c_observation_and_explicit_operator_approval_even_when_remote8b_is_go",
        },
        "nextPhase": "REMOTE-8C-first-user-support-observation",
    }

    leaks = _summary_leak_markers(summary, payload)
    if leaks:
        summary["ok"] = False
        summary["status"] = "NO_GO_REMOTE8B_PUBLIC_SUMMARY_PRIVACY_LEAK"
        summary["blockers"] = [*summary["blockers"], *leaks]
    return summary


def ingest_remote8b_live_pilot_evidence(
    *,
    evidence_path: str | Path | None = None,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate ignored private live-pilot evidence and write a redacted local summary."""
    source = Path(evidence_path).expanduser().resolve(strict=False) if evidence_path else DEFAULT_REMOTE8B_EVIDENCE_PATH
    output_base = Path(output_root).expanduser().resolve(strict=False) if output_root else DEFAULT_REMOTE8B_OUTPUT_ROOT
    summary_path = output_base / "remote8b_live_pilot_evidence.public.json"

    if not source.is_file():
        summary = {
            "ok": False,
            "status": "NO_GO_REMOTE8B_PRIVATE_EVIDENCE_MISSING",
            "version": REMOTE_LIVE_PILOT_EVIDENCE_VERSION,
            "generatedAt": _utc_now(),
            "error": "remote8b_private_evidence_missing",
            "missingProofs": list(REQUIRED_PROOFS),
            "blockers": ["private_evidence_file_missing"],
            "privacy": {
                "rawEmailReturned": False,
                "protectedUrlReturned": False,
                "localPathsReturned": False,
                "secretsReturned": False,
                "sessionTokenReturned": False,
                "grantKeysReturned": False,
            },
            "expansionGate": {
                "allowedToExpandBeyondOneUser": False,
                "reason": "private_live_evidence_must_be_collected_locally_before_expansion",
            },
            "nextPhase": "REMOTE-8B-private-evidence-required",
        }
        _write_json(summary_path, summary)
        return summary

    payload = _load_json(source)
    summary = build_remote8b_evidence_summary(payload)
    _write_json(summary_path, summary)
    return summary
