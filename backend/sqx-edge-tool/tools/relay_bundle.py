from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.fulfillment_normalizer import normalize_payload, verify_lemon_signature


def sign_bundle(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a trusted relay bundle for local SQX fulfillment ingest.")
    parser.add_argument("--payload", required=True, type=Path, help="Raw provider webhook JSON.")
    parser.add_argument("--out", required=True, type=Path, help="Output relay bundle JSON.")
    parser.add_argument("--provider", default="lemon", choices=["lemon"], help="Upstream payment provider.")
    parser.add_argument("--relay-event-id", default="", help="Optional relay event id. Auto-generated if omitted.")
    parser.add_argument("--relay-source", default="trusted_remote_relay", help="Relay source label.")
    parser.add_argument("--relay-secret", default="", help="Relay signing secret.")
    parser.add_argument("--relay-secret-env", default="", help="Environment variable containing relay signing secret.")
    parser.add_argument("--provider-signature", default="", help="Provider signature header value.")
    parser.add_argument("--provider-secret", default="", help="Provider webhook secret.")
    parser.add_argument("--provider-secret-env", default="", help="Environment variable containing provider webhook secret.")
    args = parser.parse_args()

    raw = args.payload.read_bytes()
    provider_secret = args.provider_secret or (os.environ.get(args.provider_secret_env, "") if args.provider_secret_env else "")
    if provider_secret:
        if not verify_lemon_signature(raw, args.provider_signature, provider_secret):
            print("Invalid provider signature.", file=sys.stderr)
            return 2

    payload = json.loads(raw.decode("utf-8-sig"))
    request = normalize_payload(payload, provider=args.provider)
    relay_event_id = args.relay_event_id.strip() or ("relay_" + hashlib.sha256(raw).hexdigest()[:16])
    bundle = {
        "schema_version": 1,
        "relay_event_id": relay_event_id,
        "relay_source": args.relay_source,
        "provider": args.provider,
        "provider_event_id": request.get("provider_event_id", ""),
        "verified_upstream": bool(provider_secret),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "normalized_request": request,
        "payload": payload,
    }
    encoded = json.dumps(bundle, indent=2, sort_keys=True).encode("utf-8")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(encoded)
    relay_secret = args.relay_secret or (os.environ.get(args.relay_secret_env, "") if args.relay_secret_env else "")
    print(f"Relay bundle written: {args.out}")
    print(f"Relay event id: {relay_event_id}")
    if relay_secret:
        print(f"Relay signature: {sign_bundle(encoded, relay_secret)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
