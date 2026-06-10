from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from core.remote_access import (
    DEFAULT_ENTITLEMENTS_PATH,
    ENTITLEMENTS_SCHEMA_VERSION,
    FULL_FEATURE_SCOPE,
    email_hash,
    load_entitlement_store,
    normalize_email,
)
from core.remote_access_control import (
    DEFAULT_ACCESS_CONTROL_PATH,
    approve_access_context,
    load_access_control_store,
)
from core.support_incidents import DEFAULT_SUPPORT_CASES_PATH


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
REMOTE_OWNER_ACCESS_VERSION = "remote-owner-access-recovery-v1"
DEFAULT_OWNER_RECOVERY_BACKUP_DIR = PROJECT_ROOT / ".local" / "remote_service" / "owner_access_recovery_backups"

TESTER_GRANT_PRIVATE_KEYS = {
    "grantKeyHash",
    "grant_key_hash",
    "requireGrantKey",
    "require_grant_key",
    "enforceGrantKey",
    "enforce_grant_key",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _identity_from_inputs(email: str = "", identity_ref: str = "") -> tuple[str, str]:
    identity_hash = email_hash(normalize_email(email)) if email else ""
    ref = str(identity_ref or "").strip().lower()
    return identity_hash, ref


def _find_grant(grants: list[dict[str, Any]], *, identity_hash: str = "", identity_ref: str = "") -> tuple[int, dict[str, Any] | None]:
    needle_hash = str(identity_hash or "").strip().lower()
    needle_ref = str(identity_ref or "").strip().lower()
    for index, grant in enumerate(grants):
        grant_hash = str(grant.get("emailHash") or grant.get("email_hash") or "").strip().lower()
        grant_id = str(grant.get("grantId") or grant.get("grant_id") or "").strip().lower()
        if needle_hash and grant_hash == needle_hash:
            return index, grant
        if needle_ref and (grant_hash.startswith(needle_ref) or needle_ref in grant_id):
            return index, grant
    return -1, None


def _find_access_record(identity_ref: str, store_path: str | Path | None = None) -> tuple[str, dict[str, Any] | None]:
    store = load_access_control_store(store_path)
    needle = str(identity_ref or "").strip().lower()
    for identity_hash, record in (store.get("identities") or {}).items():
        if (
            str(identity_hash).lower() == needle
            or str(identity_hash).lower().startswith(needle)
            or str(record.get("identityHashRef") or "").lower() == needle
        ):
            return str(identity_hash), dict(record)
    return "", None


def _latest_pending_context_ref(record: Mapping[str, Any] | None) -> str:
    if not isinstance(record, Mapping):
        return ""
    for item in reversed([ctx for ctx in record.get("contexts") or [] if isinstance(ctx, Mapping)]):
        if str(item.get("status") or "") == "pending":
            return str(item.get("contextRef") or "")
    return ""


def backup_owner_access_stores(
    *,
    backup_dir: str | Path | None = None,
    entitlements_path: str | Path | None = None,
    access_control_path: str | Path | None = None,
    support_cases_path: str | Path | None = None,
) -> dict[str, Any]:
    backup_root = Path(backup_dir or DEFAULT_OWNER_RECOVERY_BACKUP_DIR)
    backup_id = "remote-owner-access-recovery-v1_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target = backup_root / backup_id
    target.mkdir(parents=True, exist_ok=True)
    sources = {
        "remote_entitlements.local.json": Path(entitlements_path or DEFAULT_ENTITLEMENTS_PATH),
        "remote_access_control.local.json": Path(access_control_path or DEFAULT_ACCESS_CONTROL_PATH),
        "support_cases.local.jsonl": Path(support_cases_path or DEFAULT_SUPPORT_CASES_PATH),
    }
    files: dict[str, Any] = {}
    for name, source in sources.items():
        item = {"exists": source.is_file(), "filename": name}
        if source.is_file():
            shutil.copy2(source, target / name)
            item["backedUp"] = True
        else:
            item["backedUp"] = False
        files[name] = item
    manifest = {
        "schemaVersion": REMOTE_OWNER_ACCESS_VERSION,
        "backupId": backup_id,
        "createdAt": _utc_now(),
        "files": files,
        "privacy": {"rawEmailStored": False, "rawIpStored": False, "tokensStored": False, "localPathsReturned": False},
    }
    _write_json(target / "manifest.json", manifest)
    return {"ok": True, "backupId": backup_id, "files": files, "privacy": manifest["privacy"]}


def owner_access_status(
    *,
    email: str = "",
    identity_ref: str = "",
    entitlements_path: str | Path | None = None,
    access_control_path: str | Path | None = None,
) -> dict[str, Any]:
    identity_hash, ref = _identity_from_inputs(email=email, identity_ref=identity_ref)
    store = load_entitlement_store(Path(entitlements_path) if entitlements_path else None)
    grants = [grant for grant in store.get("grants") or [] if isinstance(grant, dict)]
    index, grant = _find_grant(grants, identity_hash=identity_hash, identity_ref=ref)
    if grant and not identity_hash:
        identity_hash = str(grant.get("emailHash") or grant.get("email_hash") or "").strip().lower()
    if not identity_hash and ref:
        access_hash, _record = _find_access_record(ref, access_control_path)
        identity_hash = access_hash
    access_identity_ref = (identity_hash or ref)[:12]
    access_hash, access_record = _find_access_record(access_identity_ref, access_control_path) if access_identity_ref else ("", None)
    context_counts = {"trusted": 0, "pending": 0, "revoked": 0, "blocked": 0}
    for item in (access_record or {}).get("contexts") or []:
        if isinstance(item, Mapping):
            status = str(item.get("status") or "pending")
            if status in context_counts:
                context_counts[status] += 1
    entitlement_kind = str((grant or {}).get("entitlementKind") or (grant or {}).get("entitlement_kind") or "")
    entitlement_status = str((grant or {}).get("status") or "")
    return {
        "ok": True,
        "schemaVersion": REMOTE_OWNER_ACCESS_VERSION,
        "identityHashRef": (identity_hash or access_hash or ref)[:12],
        "ownerGrantFound": index >= 0,
        "ownerGrantActive": entitlement_kind == "internal_operator" and entitlement_status == "active",
        "entitlementKind": entitlement_kind,
        "entitlementStatus": entitlement_status,
        "contextCounts": context_counts,
        "latestPendingContextRef": _latest_pending_context_ref(access_record),
        "privacy": {"rawEmailReturned": False, "rawIpReturned": False, "grantKeysReturned": False, "localPathsReturned": False},
    }


def recover_owner_access(
    *,
    email: str = "",
    identity_ref: str = "",
    context_ref: str = "",
    approve_latest_pending: bool = False,
    note: str = "",
    entitlements_path: str | Path | None = None,
    access_control_path: str | Path | None = None,
    backup_dir: str | Path | None = None,
) -> dict[str, Any]:
    entitlement_path = Path(entitlements_path or DEFAULT_ENTITLEMENTS_PATH)
    access_path = Path(access_control_path or DEFAULT_ACCESS_CONTROL_PATH)
    identity_hash, ref = _identity_from_inputs(email=email, identity_ref=identity_ref)
    store = load_entitlement_store(entitlement_path)
    grants = [grant for grant in store.get("grants") or [] if isinstance(grant, dict)]
    index, existing = _find_grant(grants, identity_hash=identity_hash, identity_ref=ref)
    if existing and not identity_hash:
        identity_hash = str(existing.get("emailHash") or existing.get("email_hash") or "").strip().lower()
    if not identity_hash and ref:
        access_hash, _record = _find_access_record(ref, access_path)
        identity_hash = access_hash
    if not identity_hash:
        return {
            "ok": False,
            "error": "owner_identity_not_found",
            "privacy": {"rawEmailReturned": False, "rawIpReturned": False, "grantKeysReturned": False},
        }

    backup = backup_owner_access_stores(
        backup_dir=backup_dir,
        entitlements_path=entitlement_path,
        access_control_path=access_path,
    )
    now = _utc_now()
    owner_grant = dict(existing or {})
    for key in TESTER_GRANT_PRIVATE_KEYS:
        owner_grant.pop(key, None)
    owner_grant.update({
        "grantId": owner_grant.get("grantId") or f"owner_{identity_hash[:12]}",
        "emailHash": identity_hash,
        "entitlementKind": "internal_operator",
        "status": "active",
        "featureScope": FULL_FEATURE_SCOPE,
        "source": "owner_access_recovery",
        "updatedAt": now,
    })
    owner_grant.setdefault("createdAt", now)
    if index >= 0:
        grants[index] = owner_grant
        grant_status = "updated"
    else:
        grants.append(owner_grant)
        grant_status = "created"
    store["schemaVersion"] = str(store.get("schemaVersion") or ENTITLEMENTS_SCHEMA_VERSION)
    store["grants"] = grants
    _write_json(entitlement_path, store)

    selected_context = str(context_ref or "").strip()
    if not selected_context and approve_latest_pending:
        _access_hash, access_record = _find_access_record(identity_hash[:12], access_path)
        selected_context = _latest_pending_context_ref(access_record)
    approval = {"ok": False, "error": "context_not_requested"}
    if selected_context:
        approval = approve_access_context(identity_hash[:12], selected_context, note=note or "owner_access_recovery", store_path=access_path)

    return {
        "ok": True,
        "schemaVersion": REMOTE_OWNER_ACCESS_VERSION,
        "status": grant_status,
        "identityHashRef": identity_hash[:12],
        "entitlementKind": "internal_operator",
        "ownerGrantActive": True,
        "contextApproval": approval,
        "backupId": backup.get("backupId"),
        "privacy": {"rawEmailReturned": False, "rawIpReturned": False, "grantKeysReturned": False, "localPathsReturned": False},
    }


def rollback_owner_access_recovery(
    backup_id: str,
    *,
    backup_dir: str | Path | None = None,
    entitlements_path: str | Path | None = None,
    access_control_path: str | Path | None = None,
    support_cases_path: str | Path | None = None,
) -> dict[str, Any]:
    backup_root = Path(backup_dir or DEFAULT_OWNER_RECOVERY_BACKUP_DIR)
    source = backup_root / str(backup_id or "").strip()
    manifest = _load_json(source / "manifest.json")
    if not source.is_dir() or not manifest:
        return {"ok": False, "error": "backup_not_found"}
    targets = {
        "remote_entitlements.local.json": Path(entitlements_path or DEFAULT_ENTITLEMENTS_PATH),
        "remote_access_control.local.json": Path(access_control_path or DEFAULT_ACCESS_CONTROL_PATH),
        "support_cases.local.jsonl": Path(support_cases_path or DEFAULT_SUPPORT_CASES_PATH),
    }
    restored: dict[str, bool] = {}
    for name, target in targets.items():
        backup_file = source / name
        if backup_file.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target)
            restored[name] = True
        else:
            restored[name] = False
    return {
        "ok": True,
        "schemaVersion": REMOTE_OWNER_ACCESS_VERSION,
        "backupId": backup_id,
        "restored": restored,
        "privacy": {"rawEmailReturned": False, "rawIpReturned": False, "grantKeysReturned": False, "localPathsReturned": False},
    }
