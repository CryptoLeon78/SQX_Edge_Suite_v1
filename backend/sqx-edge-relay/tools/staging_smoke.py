from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


DEFAULT_TIMEOUT_SECONDS = 20


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def demo_payload() -> dict[str, Any]:
    return {
        "meta": {"event_name": "order_created", "webhook_id": "wh_m20_staging_demo"},
        "data": {
            "type": "orders",
            "id": "m20-staging-order",
            "attributes": {
                "identifier": "ls-order-m20-staging",
                "customer_id": 20,
                "user_name": "Cliente Staging M20",
                "user_email": "m20-staging@example.com",
                "status": "paid",
                "refunded": False,
                "first_order_item": {"variant_id": "", "variant_name": "SQX Edge Pro Mensual"},
            },
        },
    }


def sign_body(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def request_json(
    url: str,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    request = urlrequest.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urlrequest.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            payload = json.loads(text) if text.strip() else {}
            return {"ok": 200 <= response.status < 300, "status": response.status, "payload": payload}
    except urlerror.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        payload = json.loads(text) if text.strip().startswith("{") else {"error": text}
        return {"ok": False, "status": exc.code, "payload": payload}
    except (urlerror.URLError, TimeoutError) as exc:
        return {"ok": False, "status": 0, "payload": {"error": str(exc)}}


def auth_headers(operator_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {operator_token}"} if operator_token else {}


def run_smoke(
    base_url: str,
    operator_token: str,
    lemon_secret: str,
    send_webhook: bool = False,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    base = normalize_base_url(base_url)
    checks: list[dict[str, Any]] = []

    def add_check(name: str, result: dict[str, Any]) -> None:
        checks.append({"name": name, **result})

    add_check("health", request_json(f"{base}/relay/health", timeout=timeout))
    add_check("config_check", request_json(f"{base}/relay/config-check", timeout=timeout))
    add_check("observability", request_json(f"{base}/relay/observability", headers=auth_headers(operator_token), timeout=timeout))
    add_check(
        "snapshot",
        request_json(
            f"{base}/relay/observability/snapshot",
            method="POST",
            headers={"Content-Type": "application/json", **auth_headers(operator_token)},
            body=b"{}",
            timeout=timeout,
        ),
    )

    if send_webhook:
        raw = json.dumps(demo_payload(), sort_keys=True).encode("utf-8")
        add_check(
            "webhook_test_event",
            request_json(
                f"{base}/relay/webhook/lemon",
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": sign_body(raw, lemon_secret),
                },
                body=raw,
                timeout=timeout,
            ),
        )

    return {
        "ok": all(item.get("ok") for item in checks),
        "base_url": base,
        "sent_webhook": send_webhook,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge relay staging smoke test")
    parser.add_argument("--base-url", default=env_value("SQX_RELAY_STAGING_BASE_URL"))
    parser.add_argument("--operator-token", default=env_value("SQX_RELAY_OPERATOR_TOKEN"))
    parser.add_argument("--lemon-secret", default=env_value("SQX_LEMON_WEBHOOK_SECRET"))
    parser.add_argument("--send-webhook", action="store_true", help="Send a signed demo Lemon event to staging.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()

    if not args.base_url:
        print(json.dumps({"ok": False, "error": "missing_base_url"}, indent=2))
        return 2
    if args.send_webhook and not args.lemon_secret:
        print(json.dumps({"ok": False, "error": "missing_lemon_secret"}, indent=2))
        return 2

    result = run_smoke(args.base_url, args.operator_token, args.lemon_secret, args.send_webhook, args.timeout)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
