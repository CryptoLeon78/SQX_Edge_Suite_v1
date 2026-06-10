from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.remote_access_control import approve_access_context, block_identity, revoke_access_context


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate SQX remote anti-sharing access contexts.")
    parser.add_argument("action", choices=("approve-context", "revoke-context", "block-identity"))
    parser.add_argument("--identity", required=True, help="Identity hash or hash ref. Do not pass raw emails in shared logs.")
    parser.add_argument("--context", default="", help="Context ref for approve/revoke actions.")
    parser.add_argument("--note", default="", help="Operator note, redacted before public summaries.")
    parser.add_argument("--store", default="", help="Optional local access-control store path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    store = args.store or None
    if args.action == "approve-context":
        result = approve_access_context(args.identity, args.context, note=args.note, store_path=store)
    elif args.action == "revoke-context":
        result = revoke_access_context(args.identity, args.context, note=args.note, store_path=store)
    else:
        result = block_identity(args.identity, note=args.note, store_path=store)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ok={result.get('ok')} action={args.action} status={result.get('status') or result.get('error')}")
        print("privacy=raw_email_false raw_ip_false tokens_false local_paths_false")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
