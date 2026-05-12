from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from tools.license_signer import sign_license_payload  # noqa: E402


DEFAULT_PLAN_DAYS = {
    "pro_tester_15": 15,
    "pro_monthly": 31,
    "pro_annual": 366,
    "setup_assist": 31,
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _parse_date(value: str | None, field: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError as exc:
        raise ValueError(f"{field} must use YYYY-MM-DD") from exc


def default_license_id(today: date) -> str:
    return f"SQX-{today:%Y%m%d}-{uuid4().hex[:8].upper()}"


def build_license_payload(args: argparse.Namespace, today: date | None = None) -> dict:
    current = today or date.today()
    issued_at = _parse_date(args.issued_at, "issued-at") or current
    expires_at = _parse_date(args.expires_at, "expires-at")
    duration_days = args.duration_days
    if expires_at is None:
        if duration_days is None:
            duration_days = DEFAULT_PLAN_DAYS.get(args.plan, 31)
        expires_at = issued_at + timedelta(days=int(duration_days))

    payload = {
        "schema_version": 1,
        "license_id": args.license_id or default_license_id(current),
        "customer_name": args.customer_name.strip(),
        "plan": args.plan,
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "machine_limit": int(args.machine_limit),
        "support_level": args.support_level,
        "source": "manual_issuer_v1",
    }

    optional_fields = {
        "customer_email": args.customer_email,
        "customer_id": args.customer_id,
        "order_id": args.order_id,
        "notes": args.notes,
    }
    for key, value in optional_fields.items():
        if value:
            payload[key] = str(value).strip()

    if args.grace_days is not None:
        payload["grace_days"] = int(args.grace_days)

    return payload


def issue_license(args: argparse.Namespace, today: date | None = None) -> dict:
    if not args.customer_name or not args.customer_name.strip():
        raise ValueError("customer-name is required")
    if int(args.machine_limit) < 1:
        raise ValueError("machine-limit must be at least 1")
    if args.duration_days is not None and int(args.duration_days) < 1:
        raise ValueError("duration-days must be at least 1")
    if args.grace_days is not None and int(args.grace_days) < 0:
        raise ValueError("grace-days cannot be negative")

    private_key = _load_json(args.private_key)
    payload = build_license_payload(args, today=today)
    signed = sign_license_payload(payload, private_key)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(signed, indent=2, sort_keys=True), encoding="utf-8")
    return signed


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue a signed SQX Edge Pro license for manual sales.")
    parser.add_argument("--private-key", required=True, type=Path, help="Private RSA JSON file kept outside the repo.")
    parser.add_argument("--out", required=True, type=Path, help="Output signed license JSON.")
    parser.add_argument("--customer-name", required=True, help="Customer display name.")
    parser.add_argument("--customer-email", default="", help="Customer email for support traceability.")
    parser.add_argument("--customer-id", default="", help="Payment or CRM customer id.")
    parser.add_argument("--order-id", default="", help="Payment order/subscription id.")
    parser.add_argument("--plan", default="pro_monthly", choices=sorted(DEFAULT_PLAN_DAYS), help="Commercial plan id.")
    parser.add_argument("--license-id", default="", help="Optional explicit license id.")
    parser.add_argument("--issued-at", default="", help="Issue date as YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--expires-at", default="", help="Expiration date as YYYY-MM-DD.")
    parser.add_argument("--duration-days", type=int, default=None, help="Expiration offset when --expires-at is omitted.")
    parser.add_argument("--machine-limit", type=int, default=1, help="Allowed machine count for support policy.")
    parser.add_argument("--support-level", default="standard", choices=["none", "standard", "priority"])
    parser.add_argument("--grace-days", type=int, default=None, help="Optional per-license grace days.")
    parser.add_argument("--notes", default="", help="Private support note stored in the license JSON.")
    args = parser.parse_args()

    signed = issue_license(args)
    print(f"Signed license issued: {args.out}")
    print(f"License id: {signed.get('license_id')}")
    print(f"Customer: {signed.get('customer_name')}")
    print(f"Plan: {signed.get('plan')}")
    print(f"Expires at: {signed.get('expires_at')}")
    print(f"Public key id: {signed.get('public_key_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
