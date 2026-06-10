from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.remote_access_control import summarize_access_control


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize SQX remote anti-sharing access contexts.")
    parser.add_argument("--store", default="", help="Optional local access-control store path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    payload = summarize_access_control(args.store or None)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    summary = payload.get("summary") or {}
    print("SQX Edge Suite remote access-control status")
    print(f"Schema: {payload.get('schemaVersion')}")
    print(f"Identidades: {summary.get('identityCount', 0)}")
    print(f"Contextos trusted: {summary.get('trustedContexts', 0)}")
    print(f"Contextos pending: {summary.get('pendingContexts', 0)}")
    print(f"Contextos revoked: {summary.get('revokedContexts', 0)}")
    print(f"Identidades bloqueadas: {summary.get('blockedIdentities', 0)}")
    print("Privacidad: sin emails/IP/rutas/tokens en salida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
