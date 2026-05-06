from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "staging_evidence"


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


deployment_check = _load_module("sqx_edge_relay_deployment_check_evidence", "tools/deployment_check.py")
staging_smoke = _load_module("sqx_edge_relay_staging_smoke_evidence", "tools/staging_smoke.py")


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def safe_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value.lower())
    return cleaned.strip("_") or "staging"


def decision_from_checks(preflight: dict[str, Any], remote_smoke: dict[str, Any] | None) -> dict[str, Any]:
    blockers = []
    warnings = []
    if not preflight.get("files_ready"):
        blockers.append("deployment_files_missing")
    if not preflight.get("docker_ready"):
        blockers.append("docker_not_ready")
    if not preflight.get("secrets_ready"):
        blockers.append("staging_secrets_not_ready")
    if remote_smoke is None:
        blockers.append("remote_staging_url_not_tested")
    elif not remote_smoke.get("ok"):
        blockers.append("remote_smoke_failed")
    if preflight.get("config_status", {}).get("warnings"):
        warnings.extend(preflight["config_status"]["warnings"])
    return {
        "go": not blockers,
        "blockers": blockers,
        "warnings": warnings,
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]
    lines = [
        "# SQX Relay Staging Evidence",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Provider: `{report['provider']}`",
        f"- Base URL: `{report.get('base_url') or 'not configured'}`",
        f"- Decision: `{'GO' if decision['go'] else 'NO-GO'}`",
        "",
        "## Blockers",
    ]
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.append("")
    lines.append("## Checks")
    lines.append(f"- Files ready: `{report['preflight'].get('files_ready')}`")
    lines.append(f"- Docker ready: `{report['preflight'].get('docker_ready')}`")
    lines.append(f"- Secrets ready: `{report['preflight'].get('secrets_ready')}`")
    if report.get("remote_smoke") is None:
        lines.append("- Remote smoke: `not run`")
    else:
        lines.append(f"- Remote smoke: `{report['remote_smoke'].get('ok')}`")
    return "\n".join(lines) + "\n"


def collect_evidence(
    provider: str,
    base_url: str = "",
    operator_token: str = "",
    lemon_secret: str = "",
    send_webhook: bool = False,
) -> dict[str, Any]:
    preflight = deployment_check.run_check()
    remote_smoke = None
    if base_url:
        remote_smoke = staging_smoke.run_smoke(
            base_url,
            operator_token,
            lemon_secret,
            send_webhook=send_webhook,
        )
    decision = decision_from_checks(preflight, remote_smoke)
    return {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": provider,
        "base_url": base_url,
        "send_webhook": send_webhook,
        "preflight": preflight,
        "remote_smoke": remote_smoke,
        "decision": decision,
    }


def write_evidence(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"relay_staging_{safe_name(report['provider'])}_{stamp()}"
    json_path = output_dir / f"{prefix}.json"
    md_path = output_dir / f"{prefix}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge relay staging evidence collector")
    parser.add_argument("--provider", default=env_value("SQX_RELAY_STAGING_PROVIDER", "render"))
    parser.add_argument("--base-url", default=env_value("SQX_RELAY_STAGING_BASE_URL"))
    parser.add_argument("--operator-token", default=env_value("SQX_RELAY_OPERATOR_TOKEN"))
    parser.add_argument("--lemon-secret", default=env_value("SQX_LEMON_WEBHOOK_SECRET"))
    parser.add_argument("--send-webhook", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    report = collect_evidence(
        provider=args.provider,
        base_url=args.base_url,
        operator_token=args.operator_token,
        lemon_secret=args.lemon_secret,
        send_webhook=args.send_webhook,
    )
    paths = write_evidence(report, Path(args.output_dir))
    print(json.dumps({"ok": True, "decision": report["decision"], "paths": paths}, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
