from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


RELAY_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RELAY_ROOT.parents[1]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
DEFAULT_OUTPUT_DIR = RELAY_ROOT / "data" / "local_ingest_staging_session"
DEFAULT_LOCAL_BASE_URL = "http://127.0.0.1:5050"


def _load_module(name: str, relative_path: str):
    module_path = RELAY_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


local_ingest_tunnel_launcher = _load_module(
    "sqx_edge_local_ingest_tunnel_launcher_session",
    "tools/local_ingest_tunnel_launcher.py",
)
local_ingest_tunnel_check = _load_module(
    "sqx_edge_local_ingest_tunnel_check_session",
    "tools/local_ingest_tunnel_check.py",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def python_executable() -> str:
    candidates = [
        TOOL_ROOT / "venv" / "Scripts" / "python.exe",
        TOOL_ROOT / "runtime" / "python" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def backend_command() -> list[str]:
    return [python_executable(), "-m", "api.server"]


def start_backend_process() -> dict[str, Any]:
    command = backend_command()
    process = subprocess.Popen(
        command,
        cwd=str(TOOL_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return {"started": True, "pid": process.pid, "command": command, "cwd": str(TOOL_ROOT)}


def wait_for_health(local_base_url: str, attempts: int = 12, delay_seconds: float = 0.5) -> dict[str, Any]:
    health_url = local_ingest_tunnel_launcher.health_url(local_base_url)
    last: dict[str, Any] = {"ok": False, "status": 0, "payload": {"error": "not_checked"}}
    for _ in range(attempts):
        last = local_ingest_tunnel_launcher.request_json(health_url)
        if last.get("ok"):
            return last
        time.sleep(delay_seconds)
    return last


def decision_from(
    backend_health: dict[str, Any],
    tunnel: dict[str, Any],
    ingest_check: dict[str, Any] | None,
    start_tunnel: bool,
    relay_secret: str,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if not backend_health.get("ok"):
        blockers.append("local_backend_health_failed")
    if start_tunnel and not tunnel.get("public_url"):
        blockers.append("public_tunnel_url_not_detected")
    if not start_tunnel:
        warnings.append("tunnel_not_started")
    if tunnel.get("public_url"):
        if not relay_secret:
            blockers.append("sqx_fulfillment_relay_secret_missing")
        elif ingest_check is None or not ingest_check.get("decision", {}).get("go"):
            blockers.append("local_ingest_tunnel_check_not_go")
            if ingest_check:
                blockers.extend(ingest_check.get("decision", {}).get("blockers", []))
                warnings.extend(ingest_check.get("decision", {}).get("warnings", []))
    elif not start_tunnel:
        warnings.append("ingest_check_not_run_without_public_url")

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
        "# SQX Edge Local Ingest Staging Session",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Local base URL: `{report['local_base_url']}`",
        f"- Backend started: `{bool(report.get('backend_start'))}`",
        f"- Tunnel provider: `{report['tunnel'].get('provider')}`",
        f"- Public URL: `{report['tunnel'].get('public_url') or 'not detected'}`",
        f"- Ingest URL: `{report['tunnel'].get('ingest_url') or 'not detected'}`",
        "",
        "## Blockers",
    ]
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.extend([
        "",
        "## Next Step",
        "",
        "- Keep backend and tunnel PIDs alive while Render staging is tested.",
        "- Copy the generated ingest URL into the Render staging secrets kit only after this session is `GO`.",
    ])
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"local_ingest_staging_session_{current_stamp}.json"
    md_path = output_dir / f"local_ingest_staging_session_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_session(
    provider: str = "auto",
    local_base_url: str = DEFAULT_LOCAL_BASE_URL,
    relay_secret: str = "",
    start_backend: bool = False,
    start_tunnel: bool = False,
    send_bundle: bool = False,
    timeout_seconds: int = 12,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    normalized_base = local_ingest_tunnel_launcher.normalize_base_url(local_base_url)
    initial_health = wait_for_health(normalized_base, attempts=1, delay_seconds=0)
    backend_start = None
    if start_backend and not initial_health.get("ok"):
        backend_start = start_backend_process()
        backend_health = wait_for_health(normalized_base)
    else:
        backend_health = initial_health

    tunnel = local_ingest_tunnel_launcher.collect_launch(
        provider=provider,
        local_base_url=normalized_base,
        start=start_tunnel,
        timeout_seconds=timeout_seconds,
        write=False,
    )
    ingest_check = None
    if tunnel.get("ingest_url") and relay_secret:
        ingest_check = local_ingest_tunnel_check.collect_check(
            ingest_url=tunnel["ingest_url"],
            relay_secret=relay_secret,
            send_bundle=send_bundle,
            write=False,
        )

    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "local_base_url": normalized_base,
        "backend_command": backend_command(),
        "backend_start": backend_start,
        "backend_health": backend_health,
        "tunnel": tunnel,
        "relay_secret_configured": bool(relay_secret),
        "send_bundle": send_bundle,
        "ingest_check": ingest_check,
        "decision": decision_from(backend_health, tunnel, ingest_check, start_tunnel, relay_secret),
    }
    if write:
        report["evidence_paths"] = write_report(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge local ingest staging session orchestrator")
    parser.add_argument("--provider", default=env_value("SQX_TUNNEL_PROVIDER", "auto"), choices=["auto", "cloudflared", "ngrok", "localtunnel"])
    parser.add_argument("--local-base-url", default=env_value("SQX_LOCAL_BACKEND_URL", DEFAULT_LOCAL_BASE_URL))
    parser.add_argument("--relay-secret", default=env_value("SQX_FULFILLMENT_RELAY_SECRET"))
    parser.add_argument("--start-backend", action="store_true")
    parser.add_argument("--start-tunnel", action="store_true")
    parser.add_argument("--send-bundle", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=12)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_session(
        provider=args.provider,
        local_base_url=args.local_base_url,
        relay_secret=args.relay_secret,
        start_backend=args.start_backend,
        start_tunnel=args.start_tunnel,
        send_bundle=args.send_bundle,
        timeout_seconds=args.timeout_seconds,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
