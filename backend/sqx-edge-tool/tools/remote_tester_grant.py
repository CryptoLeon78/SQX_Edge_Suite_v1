from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.remote_access import (  # noqa: E402
    DEFAULT_ENTITLEMENTS_PATH,
    ENTITLEMENTS_SCHEMA_VERSION,
    FULL_FEATURE_SCOPE,
    email_hash,
    grant_key_hash,
    normalize_email,
)


def _load_store(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schemaVersion": ENTITLEMENTS_SCHEMA_VERSION, "grants": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    grants = payload.get("grants") if isinstance(payload.get("grants"), list) else []
    return {
        **payload,
        "schemaVersion": str(payload.get("schemaVersion") or ENTITLEMENTS_SCHEMA_VERSION),
        "grants": [grant for grant in grants if isinstance(grant, dict)],
    }


def _write_store(path: Path, store: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def build_tester_grant(
    email: str,
    grant_key: str,
    *,
    status: str = "active",
    expires_at: str = "",
    feature_scope: str = FULL_FEATURE_SCOPE,
) -> dict[str, Any]:
    identity = normalize_email(email)
    identity_hash = email_hash(identity)
    key_hash = grant_key_hash(grant_key)
    if not identity_hash:
        raise ValueError("email_required")
    if not key_hash:
        raise ValueError("grant_key_required")
    grant: dict[str, Any] = {
        "grantId": f"tester_{identity_hash[:12]}",
        "emailHash": identity_hash,
        "entitlementKind": "tester_free",
        "status": status,
        "featureScope": feature_scope or FULL_FEATURE_SCOPE,
        "grantKeyHash": key_hash,
        "source": "operator_grant",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    if expires_at:
        grant["expiresAt"] = expires_at
    return grant


def upsert_tester_grant(
    store_path: Path,
    email: str,
    grant_key: str,
    *,
    status: str = "active",
    expires_at: str = "",
) -> dict[str, Any]:
    grant = build_tester_grant(email, grant_key, status=status, expires_at=expires_at)
    store = _load_store(store_path)
    grants = store.setdefault("grants", [])
    identity_hash = grant["emailHash"]
    replaced = False
    for index, existing in enumerate(grants):
        existing_hash = str(existing.get("emailHash") or existing.get("email_hash") or "").strip().lower()
        if existing_hash == identity_hash:
            grants[index] = {**existing, **grant, "updatedAt": datetime.now(timezone.utc).isoformat()}
            replaced = True
            break
    if not replaced:
        grants.append(grant)
    _write_store(store_path, store)
    return {
        "ok": True,
        "schemaVersion": ENTITLEMENTS_SCHEMA_VERSION,
        "status": "updated" if replaced else "created",
        "storePath": str(store_path),
        "grantId": grant["grantId"],
        "emailHashRef": identity_hash[:12],
        "entitlementKind": "tester_free",
        "featureScope": grant["featureScope"],
        "rawEmailReturned": False,
        "grantKeyReturned": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update a local ignored tester-free entitlement grant.")
    parser.add_argument("--email", required=True, help="Approved tester email. Stored as SHA-256 hash only.")
    parser.add_argument("--grant-key", required=True, help="Private tester key. Stored as SHA-256 hash only.")
    parser.add_argument("--status", default="active", choices=["active", "pending", "expired", "denied", "blocked", "cancelled"])
    parser.add_argument("--expires-at", default="", help="Optional ISO date, for example 2026-06-01.")
    parser.add_argument("--store", type=Path, default=DEFAULT_ENTITLEMENTS_PATH, help="Ignored local entitlement store path.")
    args = parser.parse_args()

    result = upsert_tester_grant(
        args.store,
        args.email,
        args.grant_key,
        status=args.status,
        expires_at=args.expires_at,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
