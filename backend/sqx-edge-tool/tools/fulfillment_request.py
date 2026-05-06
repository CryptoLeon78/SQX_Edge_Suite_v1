from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.fulfillment_normalizer import normalize_payload, verify_lemon_signature


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize checkout/webhook payloads into SQX fulfillment requests.")
    parser.add_argument("--provider", default="lemon", choices=["lemon"], help="Payment provider payload format.")
    parser.add_argument("--payload", required=True, type=Path, help="Raw provider webhook/order JSON.")
    parser.add_argument("--out", required=True, type=Path, help="Output normalized fulfillment request JSON.")
    parser.add_argument("--signature", default="", help="Provider webhook signature header value.")
    parser.add_argument("--secret", default="", help="Webhook signing secret. Prefer --secret-env in real use.")
    parser.add_argument("--secret-env", default="", help="Environment variable containing the webhook signing secret.")
    args = parser.parse_args()

    raw = args.payload.read_bytes()
    secret = args.secret or (os.environ.get(args.secret_env, "") if args.secret_env else "")
    if secret:
        if not verify_lemon_signature(raw, args.signature, secret):
            print("Invalid Lemon Squeezy webhook signature.", file=sys.stderr)
            return 2

    payload = json.loads(raw.decode("utf-8-sig"))
    request = normalize_payload(payload, provider=args.provider)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(request, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Fulfillment request written: {args.out}")
    print(f"Provider: {request.get('provider')}")
    print(f"Event: {request.get('source_event')}")
    print(f"Plan: {request.get('plan')}")
    print(f"Eligible: {request.get('eligible_for_fulfillment')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
