from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "local_ingest_tunnel_check"
INGEST_PATH = "/api/fulfillment/relay-ingest"
HEALTH_PATH = "/api/health"


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in ("replace", "placeholder", "example", "demo", "todo", "your-"))


def redact(value: str) -> str:
    if not value:
        return ""
    return f"{value[:6]}...{value[-6:]}" if len(value) > 16 else "[redacted]"


def normalize_ingest_url(value: str) -> str:
    raw = value.strip().rstrip("/")
    if not raw:
        return ""
    parsed = urlparse.urlparse(raw)
    if parsed.path in ("", "/"):
        return raw + INGEST_PATH
    return raw


def health_url_from_ingest(ingest_url: str) -> str:
    parsed = urlparse.urlparse(ingest_url)
    return urlparse.urlunparse((parsed.scheme, parsed.netloc, HEALTH_PATH, "", "", ""))


def request_json(url: str, method: str = "GET", body: bytes | None = None, headers: dict[str, str] | None = None, timeout: int = 15) -> dict[str, Any]:
    request = urlrequest.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urlrequest.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            payload = json.loads(text) if text.strip().startswith("{") else {"body": text[:1000]}
            return {"ok": 200 <= response.status < 300, "status": response.status, "payload": payload}
    except urlerror.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        payload = json.loads(text) if text.strip().startswith("{") else {"body": text[:1000]}
        return {"ok": False, "status": exc.code, "payload": payload}
    except (urlerror.URLError, TimeoutError) as exc:
        return {"ok": False, "status": 0, "payload": {"error": str(exc)}}


def demo_bundle() -> dict[str, Any]:
    event_id = "wh_m27_local_ingest_demo"
    return {
        "schema_version": 1,
        "relay_event_id": "relay_m27_local_ingest_demo",
        "relay_source": "sqx_edge_m27_local_ingest_check",
        "provider": "lemon",
        "provider_event_id": event_id,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "normalized_request": {
            "schema_version": 1,
            "provider": "Lemon Squeezy",
            "source_event": "order_created",
            "provider_event_id": event_id,
            "order_id": "M27-LOCAL-INGEST-DEMO",
            "customer_name": "SQX Staging Demo",
            "customer_email": "staging-demo@sqx.local",
            "plan": "pro_monthly",
            "license_duration_days": 31,
            "machine_limit": 1,
            "support_level": "standard",
            "eligible_for_fulfillment": True,
            "fulfillment_status": "ready_for_license",
            "operator_status": "queued",
        },
    }


def sign_body(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def check_url_policy(ingest_url: str, relay_secret: str) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if env_value("RENDER_PASSWORD") or env_value("RENDER_ACCOUNT_PASSWORD"):
        blockers.append("render_account_password_present_do_not_use")
    if not ingest_url:
        blockers.append("sqx_local_ingest_url_missing")
    elif is_placeholder(ingest_url):
        blockers.append("sqx_local_ingest_url_placeholder")
    else:
        parsed = urlparse.urlparse(ingest_url)
        local_host = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if parsed.scheme != "https" and not local_host:
            blockers.append("sqx_local_ingest_url_must_be_https")
        if parsed.path != INGEST_PATH:
            warnings.append("sqx_local_ingest_url_path_is_not_standard")
    if not relay_secret:
        blockers.append("sqx_fulfillment_relay_secret_missing")
    elif len(relay_secret) < 32:
        blockers.append("sqx_fulfillment_relay_secret_too_short")
    elif is_placeholder(relay_secret):
        blockers.append("sqx_fulfillment_relay_secret_placeholder")
    return blockers, warnings


def decision_from(blockers: list[str], warnings: list[str], health: dict[str, Any] | None, ingest: dict[str, Any] | None, send_bundle: bool) -> dict[str, Any]:
    if health is not None and not health.get("ok"):
        blockers.append("local_ingest_health_failed")
    if send_bundle:
        if ingest is None or not ingest.get("ok"):
            blockers.append("local_ingest_signed_bundle_failed")
    else:
        warnings.append("signed_bundle_not_sent")
    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# SQX Edge Local Ingest Tunnel Check",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Ingest URL: `{report.get('ingest_url') or 'not configured'}`",
        f"- Health URL: `{report.get('health_url') or 'not configured'}`",
        f"- Relay secret: `{report['relay_secret']['redacted']}`",
        "",
        "## Blockers",
    ]
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.extend([
        "",
        "## Next Commands",
        "",
        "- Run with `--send-bundle` only when the local backend is ready to receive a demo fulfillment request.",
        "- Paste the validated `SQX_LOCAL_INGEST_URL` into Render after the check returns `GO`.",
    ])
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"local_ingest_tunnel_check_{current_stamp}.json"
    md_path = output_dir / f"local_ingest_tunnel_check_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_check(
    ingest_url: str = "",
    relay_secret: str = "",
    send_bundle: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    normalized_url = normalize_ingest_url(ingest_url)
    health_url = health_url_from_ingest(normalized_url) if normalized_url else ""
    blockers, warnings = check_url_policy(normalized_url, relay_secret)
    health = request_json(health_url) if normalized_url and "sqx_local_ingest_url_placeholder" not in blockers else None
    ingest = None
    if send_bundle and normalized_url and relay_secret and not blockers:
        raw = json.dumps(demo_bundle(), indent=2, sort_keys=True).encode("utf-8")
        signature = sign_body(raw, relay_secret)
        ingest = request_json(
            normalized_url,
            method="POST",
            body=raw,
            headers={
                "Content-Type": "application/json",
                "X-SQX-Relay-Signature": signature,
            },
        )
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "ingest_url": normalized_url,
        "health_url": health_url,
        "send_bundle": send_bundle,
        "relay_secret": {
            "configured": bool(relay_secret),
            "length_ok": len(relay_secret) >= 32,
            "redacted": redact(relay_secret),
        },
        "health": health,
        "signed_ingest": ingest,
        "decision": decision_from(blockers, warnings, health, ingest, send_bundle),
    }
    if write:
        report["evidence_paths"] = write_report(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge local ingest tunnel readiness check")
    parser.add_argument("--ingest-url", default=env_value("SQX_LOCAL_INGEST_URL"))
    parser.add_argument("--relay-secret", default=env_value("SQX_FULFILLMENT_RELAY_SECRET"))
    parser.add_argument("--send-bundle", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_check(
        ingest_url=args.ingest_url,
        relay_secret=args.relay_secret,
        send_bundle=args.send_bundle,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
