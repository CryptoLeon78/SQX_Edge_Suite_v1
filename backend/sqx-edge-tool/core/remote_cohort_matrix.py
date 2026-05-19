from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_COHORT_MATRIX_VERSION = "remote-cohort-matrix-v1"

DEFAULT_ALIAS_PATH = PROJECT_ROOT / ".local" / "remote_service" / "user_aliases.local.json"
DEFAULT_ENTITLEMENTS_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_entitlements.local.json"
DEFAULT_ACCESS_CONTROL_PATH = PROJECT_ROOT / ".local" / "remote_service" / "remote_access_control.local.json"
DEFAULT_SUPPORT_CASES_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "support_cases" / "support_cases.local.jsonl"
)
DEFAULT_DOWNLOAD_SMOKE_PATH = (
    PROJECT_ROOT
    / ".local"
    / "remote_service"
    / "remote_cohort_evidence1"
    / "remote_cohort_download_smoke.local.json"
)
DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT / ".local" / "remote_service" / "remote_cohort_matrix" / "remote_cohort_matrix.local.json"
)

OPEN_SUPPORT_STATUSES = {"open", "triaged"}
FORBIDDEN_PUBLIC_MARKERS = (
    "@" + "gmail.com",
    "@" + "hotmail.com",
    "CF_" + "Authorization",
    "__Host-" + "sqx_remote_session",
    "CLOUDFLARE" + "_API_TOKEN=",
    "SQX_REMOTE" + "_SESSION_SECRET=",
    "SQX_REMOTE" + "_PAYMENT_WEBHOOK_SECRET=",
    "sk_" + "live_",
    "pk_" + "live_",
    "C:" + "\\BOTS\\",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _short(value: Any, size: int = 12) -> str:
    text = str(value or "").strip()
    return text[:size] if text else ""


def _bool_ok(value: Any) -> bool:
    return str(value or "").strip().lower() in {"ok", "true", "passed", "yes", "1"}


def _load_aliases(path: Path) -> list[dict[str, Any]]:
    payload = _read_json(path)
    aliases = payload.get("aliases") if isinstance(payload.get("aliases"), list) else []
    rows: list[dict[str, Any]] = []
    for item in aliases:
        if not isinstance(item, Mapping):
            continue
        alias = str(item.get("alias") or "").strip()
        identity_ref = _short(item.get("identityHashRef"))
        if not alias:
            continue
        rows.append(
            {
                "alias": alias,
                "role": str(item.get("role") or "").strip() or "unknown",
                "identityHashRef": identity_ref,
            }
        )
    return rows


def _grant_index(path: Path) -> dict[str, dict[str, Any]]:
    payload = _read_json(path)
    grants = payload.get("grants") if isinstance(payload.get("grants"), list) else []
    index: dict[str, dict[str, Any]] = {}
    for grant in grants:
        if not isinstance(grant, Mapping):
            continue
        email_hash = str(grant.get("emailHash") or "").strip()
        identity_ref = _short(email_hash)
        if not identity_ref:
            continue
        index[identity_ref] = {
            "status": str(grant.get("status") or "").strip(),
            "entitlementKind": str(grant.get("entitlementKind") or "").strip(),
            "featureScope": str(grant.get("featureScope") or "").strip(),
        }
    return index


def _access_index(path: Path) -> dict[str, dict[str, Any]]:
    payload = _read_json(path)
    identities = payload.get("identities") if isinstance(payload.get("identities"), Mapping) else {}
    index: dict[str, dict[str, Any]] = {}
    for identity_hash, record in identities.items():
        if not isinstance(record, Mapping):
            continue
        identity_ref = _short(record.get("identityHashRef") or identity_hash)
        contexts = record.get("contexts") if isinstance(record.get("contexts"), list) else []
        counts = {"trusted": 0, "pending": 0, "blocked": 0, "revoked": 0}
        context_refs: list[str] = []
        for context in contexts:
            if not isinstance(context, Mapping):
                continue
            status = str(context.get("status") or "").strip()
            if status in counts:
                counts[status] += 1
            context_ref = _short(context.get("contextRef"))
            if context_ref and len(context_refs) < 4:
                context_refs.append(context_ref)
        index[identity_ref] = {
            "identityStatus": str(record.get("status") or "").strip(),
            "trustedContexts": counts["trusted"],
            "pendingContexts": counts["pending"],
            "blockedContexts": counts["blocked"],
            "revokedContexts": counts["revoked"],
            "contextRefs": context_refs,
        }
    return index


def _download_index(path: Path) -> dict[str, dict[str, bool]]:
    payload = _read_json(path)
    cohort = payload.get("cohort") if isinstance(payload.get("cohort"), list) else []
    index: dict[str, dict[str, bool]] = {}
    for item in cohort:
        if not isinstance(item, Mapping):
            continue
        alias = str(item.get("alias") or "").strip()
        if not alias:
            continue
        index[alias] = {
            "accessOk": _bool_ok(item.get("access")),
            "downloadsOk": _bool_ok(item.get("downloadSmoke")),
        }
    return index


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        raw = line.strip()
        if not raw:
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _support_index(path: Path) -> tuple[dict[str, int], int]:
    by_identity: dict[str, int] = {}
    unassigned_open = 0
    for case in _iter_jsonl(path):
        status = str(case.get("status") or "").strip().lower()
        if status not in OPEN_SUPPORT_STATUSES:
            continue
        remote_identity = (
            case.get("remoteIdentityRef") if isinstance(case.get("remoteIdentityRef"), Mapping) else {}
        )
        identity_ref = _short(remote_identity.get("emailHashRef"))
        if identity_ref:
            by_identity[identity_ref] = by_identity.get(identity_ref, 0) + 1
        else:
            unassigned_open += 1
    return by_identity, unassigned_open


def _row_status(row: Mapping[str, Any]) -> tuple[str, list[str]]:
    blockers: list[str] = []
    for key, blocker in (
        ("accessOk", "access_not_confirmed"),
        ("grantOk", "grant_missing_or_inactive"),
        ("antiSharingOk", "anti_sharing_context_not_ready"),
        ("downloadsOk", "download_smoke_not_confirmed"),
    ):
        if not row.get(key):
            blockers.append(blocker)
    if int(row.get("openIncidents") or 0) > 0:
        blockers.append("open_incidents")
    return ("ready" if not blockers else "needs_attention", blockers)


def build_remote_cohort_matrix(
    *,
    aliases_path: str | Path | None = DEFAULT_ALIAS_PATH,
    entitlements_path: str | Path | None = DEFAULT_ENTITLEMENTS_PATH,
    access_control_path: str | Path | None = DEFAULT_ACCESS_CONTROL_PATH,
    support_cases_path: str | Path | None = DEFAULT_SUPPORT_CASES_PATH,
    download_smoke_path: str | Path | None = DEFAULT_DOWNLOAD_SMOKE_PATH,
) -> dict[str, Any]:
    """Build an alias-only REMOTE cohort matrix from ignored local stores."""

    aliases = _load_aliases(Path(aliases_path or DEFAULT_ALIAS_PATH))
    grants = _grant_index(Path(entitlements_path or DEFAULT_ENTITLEMENTS_PATH))
    access = _access_index(Path(access_control_path or DEFAULT_ACCESS_CONTROL_PATH))
    downloads = _download_index(Path(download_smoke_path or DEFAULT_DOWNLOAD_SMOKE_PATH))
    support, unassigned_open = _support_index(Path(support_cases_path or DEFAULT_SUPPORT_CASES_PATH))

    rows: list[dict[str, Any]] = []
    for alias in aliases:
        identity_ref = alias["identityHashRef"]
        grant = grants.get(identity_ref, {})
        access_record = access.get(identity_ref, {})
        download = downloads.get(alias["alias"], {})

        grant_ok = grant.get("status") == "active"
        trusted_contexts = int(access_record.get("trustedContexts") or 0)
        pending_contexts = int(access_record.get("pendingContexts") or 0)
        blocked_contexts = int(access_record.get("blockedContexts") or 0)
        revoked_contexts = int(access_record.get("revokedContexts") or 0)
        anti_sharing_ok = trusted_contexts > 0 and pending_contexts == 0 and blocked_contexts == 0

        row: dict[str, Any] = {
            "alias": alias["alias"],
            "role": alias["role"],
            "identityHashRef": identity_ref,
            "accessOk": bool(download.get("accessOk")),
            "grantOk": grant_ok,
            "grantKind": grant.get("entitlementKind") or "",
            "featureScope": grant.get("featureScope") or "",
            "antiSharingOk": anti_sharing_ok,
            "trustedContexts": trusted_contexts,
            "pendingContexts": pending_contexts,
            "blockedContexts": blocked_contexts,
            "revokedContexts": revoked_contexts,
            "contextRefs": access_record.get("contextRefs") or [],
            "downloadsOk": bool(download.get("downloadsOk")),
            "openIncidents": int(support.get(identity_ref, 0)),
        }
        status, blockers = _row_status(row)
        row["status"] = status
        row["blockers"] = blockers
        rows.append(row)

    ready_count = sum(1 for row in rows if row["status"] == "ready")
    needs_attention = len(rows) - ready_count
    payload = {
        "schemaVersion": REMOTE_COHORT_MATRIX_VERSION,
        "generatedAt": _utc_now(),
        "phase": "REMOTE-COHORT-MATRIX1",
        "summary": {
            "aliasCount": len(rows),
            "readyCount": ready_count,
            "needsAttentionCount": needs_attention,
            "accessOkCount": sum(1 for row in rows if row["accessOk"]),
            "grantOkCount": sum(1 for row in rows if row["grantOk"]),
            "antiSharingOkCount": sum(1 for row in rows if row["antiSharingOk"]),
            "downloadsOkCount": sum(1 for row in rows if row["downloadsOk"]),
            "openIncidents": sum(int(row["openIncidents"]) for row in rows),
            "unassignedOpenIncidents": unassigned_open,
        },
        "rows": rows,
        "privacy": {
            "rawEmailsReturned": False,
            "rawIpsReturned": False,
            "protectedUrlsReturned": False,
            "cookiesReturned": False,
            "tokensReturned": False,
            "localPathsReturned": False,
        },
        "nextGate": "REMOTE-8F / REMOTE-8G decision review",
    }
    _assert_public_safe(payload)
    return payload


def _assert_public_safe(payload: Mapping[str, Any]) -> None:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    for marker in FORBIDDEN_PUBLIC_MARKERS:
        if marker in serialized:
            raise ValueError(f"remote_cohort_matrix_privacy_leak:{marker}")


def write_remote_cohort_matrix(
    payload: Mapping[str, Any],
    output_path: str | Path | None = DEFAULT_OUTPUT_PATH,
) -> Path:
    target = Path(output_path or DEFAULT_OUTPUT_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
