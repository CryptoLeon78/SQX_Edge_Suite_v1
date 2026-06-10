from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.remote_owner_access import (  # noqa: E402
    recover_owner_access,
    owner_access_status,
    rollback_owner_access_recovery,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recover SQX Edge owner access without weakening tester controls.")
    parser.add_argument("action", choices=("status", "recover", "rollback"))
    parser.add_argument("--identity", default="", help="Identity hash/ref. Do not pass raw emails in shared logs.")
    parser.add_argument("--email", default="", help="Optional local-only owner email. Output remains redacted.")
    parser.add_argument("--context", default="", help="Context ref to approve during recovery.")
    parser.add_argument("--approve-latest-pending", action="store_true", help="Approve the latest pending context for this owner identity.")
    parser.add_argument("--note", default="", help="Redacted operator note.")
    parser.add_argument("--backup-id", default="", help="Backup id for rollback.")
    parser.add_argument("--entitlements", default="", help="Optional local entitlement store path.")
    parser.add_argument("--access-control", default="", help="Optional local access-control store path.")
    parser.add_argument("--backup-dir", default="", help="Optional local backup root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    common = {
        "email": args.email,
        "identity_ref": args.identity,
        "entitlements_path": args.entitlements or None,
        "access_control_path": args.access_control or None,
    }
    if args.action == "status":
        result = owner_access_status(**common)
    elif args.action == "recover":
        result = recover_owner_access(
            **common,
            context_ref=args.context,
            approve_latest_pending=args.approve_latest_pending,
            note=args.note,
            backup_dir=args.backup_dir or None,
        )
    else:
        result = rollback_owner_access_recovery(
            args.backup_id,
            backup_dir=args.backup_dir or None,
            entitlements_path=args.entitlements or None,
            access_control_path=args.access_control or None,
        )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ok={result.get('ok')} action={args.action} status={result.get('status') or result.get('error') or 'done'}")
        if result.get("identityHashRef"):
            print(f"identityRef={result.get('identityHashRef')}")
        if result.get("backupId"):
            print(f"backupId={result.get('backupId')}")
        print("privacy=raw_email_false raw_ip_false grant_keys_false local_paths_false")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
