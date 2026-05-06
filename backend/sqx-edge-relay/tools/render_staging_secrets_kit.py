from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "render_staging_secrets_kit"
SECRET_KEYS = [
    "SQX_LEMON_WEBHOOK_SECRET",
    "SQX_FULFILLMENT_RELAY_SECRET",
    "SQX_RELAY_OPERATOR_TOKEN",
]
NON_SECRET_DEFAULTS = {
    "SQX_RELAY_WORKER_INTERVAL_SECONDS": "30",
    "SQX_RELAY_WORKER_LIMIT": "10",
}


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def generated_secret() -> str:
    return secrets.token_urlsafe(48)


def redact(value: str) -> str:
    if not value:
        return ""
    return f"{value[:6]}...{value[-6:]}" if len(value) > 16 else "[redacted]"


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16] if value else ""


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in ("replace", "placeholder", "example", "demo", "todo", "your-"))


def env_line(key: str, value: str) -> str:
    safe = value.replace("\r", "").replace("\n", "")
    return f"{key}={safe}"


def secret_status(key: str, value: str) -> dict[str, Any]:
    return {
        "key": key,
        "configured": bool(value),
        "length": len(value),
        "length_ok": len(value) >= 32,
        "placeholder": is_placeholder(value),
        "redacted": redact(value),
        "fingerprint": fingerprint(value),
    }


def decision_from(values: dict[str, str]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if env_value("RENDER_PASSWORD") or env_value("RENDER_ACCOUNT_PASSWORD"):
        blockers.append("render_account_password_present_do_not_use")

    for key in SECRET_KEYS:
        status = secret_status(key, values.get(key, ""))
        if not status["configured"]:
            blockers.append(f"{key.lower()}_missing")
        if status["configured"] and not status["length_ok"]:
            blockers.append(f"{key.lower()}_too_short")
        if status["placeholder"]:
            blockers.append(f"{key.lower()}_placeholder")

    ingest_url = values.get("SQX_LOCAL_INGEST_URL", "")
    if not ingest_url:
        blockers.append("sqx_local_ingest_url_missing")
    elif is_placeholder(ingest_url):
        blockers.append("sqx_local_ingest_url_placeholder")
    elif not ingest_url.startswith(("https://", "http://127.0.0.1", "http://localhost")):
        warnings.append("sqx_local_ingest_url_unusual_scheme")

    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
    }


def build_values(local_ingest_url: str, worker_interval: str, worker_limit: str, use_existing: bool) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in SECRET_KEYS:
        existing = env_value(key)
        values[key] = existing if use_existing and existing and not is_placeholder(existing) else generated_secret()
    values["SQX_LOCAL_INGEST_URL"] = local_ingest_url
    values["SQX_RELAY_WORKER_INTERVAL_SECONDS"] = worker_interval or NON_SECRET_DEFAULTS["SQX_RELAY_WORKER_INTERVAL_SECONDS"]
    values["SQX_RELAY_WORKER_LIMIT"] = worker_limit or NON_SECRET_DEFAULTS["SQX_RELAY_WORKER_LIMIT"]
    return values


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# SQX Edge Render Staging Secrets Kit",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Env file: `{report.get('env_file') or 'not written'}`",
        "",
        "## Secret Status",
    ]
    for item in report["secret_status"]:
        lines.append(
            f"- `{item['key']}`: length_ok={item['length_ok']}, placeholder={item['placeholder']}, fingerprint={item['fingerprint']}"
        )
    lines.extend([
        "",
        "## Render Env Vars",
        "",
        "- `SQX_LEMON_WEBHOOK_SECRET`: paste from the generated env file.",
        "- `SQX_FULFILLMENT_RELAY_SECRET`: paste from the generated env file.",
        "- `SQX_RELAY_OPERATOR_TOKEN`: paste from the generated env file.",
        "- `SQX_LOCAL_INGEST_URL`: tunnel or HTTPS endpoint for the local ingest.",
        "- `SQX_RELAY_WORKER_INTERVAL_SECONDS`: `30`.",
        "- `SQX_RELAY_WORKER_LIMIT`: `10`.",
        "",
        "## Blockers",
    ])
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Safety Rules")
    lines.extend([
        "",
        "- The generated `.env` contains secrets and must stay inside `backend/sqx-edge-relay/data/`.",
        "- Do not commit the generated `.env`.",
        "- Do not use a Render account password for automation.",
        "- Rotate these staging secrets before production.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], values: dict[str, str], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    env_path = output_dir / f"render_staging_secrets_{current_stamp}.env"
    json_path = output_dir / f"render_staging_secrets_{current_stamp}.json"
    md_path = output_dir / f"render_staging_secrets_{current_stamp}.md"

    ordered_keys = SECRET_KEYS + ["SQX_LOCAL_INGEST_URL", "SQX_RELAY_WORKER_INTERVAL_SECONDS", "SQX_RELAY_WORKER_LIMIT"]
    env_text = "\n".join(env_line(key, values[key]) for key in ordered_keys) + "\n"
    env_path.write_text(env_text, encoding="utf-8")

    report["env_file"] = str(env_path)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"env": str(env_path), "json": str(json_path), "markdown": str(md_path)}


def collect_secrets_kit(
    local_ingest_url: str = "",
    worker_interval: str = "30",
    worker_limit: str = "10",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    use_existing: bool = True,
    write: bool = True,
) -> dict[str, Any]:
    values = build_values(local_ingest_url, worker_interval, worker_limit, use_existing)
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": "render",
        "secret_policy": "generated_or_existing_env_values_never_committed",
        "secret_status": [secret_status(key, values[key]) for key in SECRET_KEYS],
        "non_secret_values": {
            "SQX_LOCAL_INGEST_URL": values["SQX_LOCAL_INGEST_URL"],
            "SQX_RELAY_WORKER_INTERVAL_SECONDS": values["SQX_RELAY_WORKER_INTERVAL_SECONDS"],
            "SQX_RELAY_WORKER_LIMIT": values["SQX_RELAY_WORKER_LIMIT"],
        },
        "decision": decision_from(values),
    }
    if write:
        report["evidence_paths"] = write_outputs(report, values, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge Render staging secrets kit")
    parser.add_argument("--local-ingest-url", default=env_value("SQX_LOCAL_INGEST_URL"))
    parser.add_argument("--worker-interval", default=env_value("SQX_RELAY_WORKER_INTERVAL_SECONDS", "30"))
    parser.add_argument("--worker-limit", default=env_value("SQX_RELAY_WORKER_LIMIT", "10"))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--fresh", action="store_true", help="Ignore existing SQX staging secrets and generate new values.")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_secrets_kit(
        local_ingest_url=args.local_ingest_url,
        worker_interval=args.worker_interval,
        worker_limit=args.worker_limit,
        output_dir=Path(args.output_dir),
        use_existing=not args.fresh,
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
