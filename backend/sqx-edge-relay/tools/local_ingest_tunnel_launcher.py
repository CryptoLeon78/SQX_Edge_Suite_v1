from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "local_ingest_tunnel_launch"
DEFAULT_LOCAL_BASE_URL = "http://127.0.0.1:5050"
INGEST_PATH = "/api/fulfillment/relay-ingest"
HEALTH_PATH = "/api/health"
PUBLIC_URL_RE = re.compile(r"https://[A-Za-z0-9.-]+\.(?:trycloudflare\.com|ngrok-free\.app|ngrok\.io|loca\.lt|localtunnel\.me)")


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def request_json(url: str, timeout: int = 8) -> dict[str, Any]:
    try:
        with urlrequest.urlopen(url, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            payload = json.loads(text) if text.strip().startswith("{") else {"body": text[:1000]}
            return {"ok": 200 <= response.status < 300, "status": response.status, "payload": payload}
    except (urlerror.URLError, TimeoutError) as exc:
        return {"ok": False, "status": 0, "payload": {"error": str(exc)}}


def normalize_base_url(value: str) -> str:
    return value.strip().rstrip("/") or DEFAULT_LOCAL_BASE_URL


def health_url(base_url: str) -> str:
    parsed = urlparse.urlparse(base_url)
    return urlparse.urlunparse((parsed.scheme, parsed.netloc, HEALTH_PATH, "", "", ""))


def ingest_url(public_base_url: str) -> str:
    return public_base_url.rstrip("/") + INGEST_PATH


def executable_path(name: str) -> str:
    return shutil.which(name) or ""


def provider_command(provider: str, local_base_url: str) -> list[str]:
    parsed = urlparse.urlparse(local_base_url)
    port = parsed.port or 5050
    if provider == "cloudflared":
        return ["cloudflared", "tunnel", "--url", local_base_url]
    if provider == "ngrok":
        return ["ngrok", "http", str(port)]
    if provider == "localtunnel":
        return ["npx", "--yes", "localtunnel", "--port", str(port)]
    raise ValueError(f"Unsupported tunnel provider: {provider}")


def detect_providers() -> dict[str, dict[str, Any]]:
    return {
        "cloudflared": {
            "available": bool(executable_path("cloudflared")),
            "executable": executable_path("cloudflared"),
            "recommended": True,
        },
        "ngrok": {
            "available": bool(executable_path("ngrok")),
            "executable": executable_path("ngrok"),
            "recommended": False,
        },
        "localtunnel": {
            "available": bool(executable_path("npx")),
            "executable": executable_path("npx"),
            "recommended": False,
        },
    }


def pick_provider(requested: str, providers: dict[str, dict[str, Any]]) -> str:
    if requested != "auto":
        return requested
    for candidate in ("cloudflared", "ngrok", "localtunnel"):
        if providers.get(candidate, {}).get("available"):
            return candidate
    return "cloudflared"


def parse_public_url(text: str) -> str:
    match = PUBLIC_URL_RE.search(text)
    return match.group(0).rstrip("/") if match else ""


def start_tunnel(command: list[str], timeout_seconds: int = 12) -> dict[str, Any]:
    started_at = time.time()
    lines: list[str] = []
    public_url = ""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        while time.time() - started_at < timeout_seconds:
            if process.stdout is None:
                break
            line = process.stdout.readline()
            if line:
                lines.append(line.rstrip())
                public_url = parse_public_url("\n".join(lines))
                if public_url:
                    break
            elif process.poll() is not None:
                break
            else:
                time.sleep(0.25)
        return {
            "started": True,
            "pid": process.pid,
            "returncode": process.poll(),
            "public_url": public_url,
            "output_tail": lines[-20:],
        }
    except Exception:
        process.terminate()
        raise


def decision_from(provider: str, provider_ready: bool, health: dict[str, Any], start_result: dict[str, Any] | None, start: bool) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not provider_ready:
        blockers.append(f"{provider}_not_available")
    if not health.get("ok"):
        blockers.append("local_backend_health_failed")
    if start:
        if not start_result or not start_result.get("public_url"):
            blockers.append("public_tunnel_url_not_detected")
    else:
        warnings.append("tunnel_not_started")
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
        "# SQX Edge Local Ingest Tunnel Launcher",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Provider: `{report['provider']}`",
        f"- Local base URL: `{report['local_base_url']}`",
        f"- Command: `{' '.join(report['command'])}`",
        f"- Public URL: `{report.get('public_url') or 'not detected'}`",
        f"- Ingest URL: `{report.get('ingest_url') or 'not detected'}`",
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
        "- When a public URL is detected, run `local_ingest_tunnel_check.py` with the generated ingest URL and relay secret.",
        "- Keep the tunnel process alive while Render staging tests run.",
    ])
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"local_ingest_tunnel_launch_{current_stamp}.json"
    md_path = output_dir / f"local_ingest_tunnel_launch_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_launch(
    provider: str = "auto",
    local_base_url: str = DEFAULT_LOCAL_BASE_URL,
    start: bool = False,
    timeout_seconds: int = 12,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    normalized_local_base = normalize_base_url(local_base_url)
    providers = detect_providers()
    selected_provider = pick_provider(provider, providers)
    command = provider_command(selected_provider, normalized_local_base)
    provider_ready = bool(providers.get(selected_provider, {}).get("available"))
    local_health = request_json(health_url(normalized_local_base))
    start_result = start_tunnel(command, timeout_seconds=timeout_seconds) if start and provider_ready and local_health.get("ok") else None
    public_url = start_result.get("public_url", "") if start_result else ""
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": selected_provider,
        "providers": providers,
        "local_base_url": normalized_local_base,
        "health_url": health_url(normalized_local_base),
        "local_health": local_health,
        "command": command,
        "started": bool(start),
        "start_result": start_result,
        "public_url": public_url,
        "ingest_url": ingest_url(public_url) if public_url else "",
        "decision": decision_from(selected_provider, provider_ready, local_health, start_result, start),
    }
    if write:
        report["evidence_paths"] = write_report(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge local ingest tunnel launcher")
    parser.add_argument("--provider", default=env_value("SQX_TUNNEL_PROVIDER", "auto"), choices=["auto", "cloudflared", "ngrok", "localtunnel"])
    parser.add_argument("--local-base-url", default=env_value("SQX_LOCAL_BACKEND_URL", DEFAULT_LOCAL_BASE_URL))
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=12)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_launch(
        provider=args.provider,
        local_base_url=args.local_base_url,
        start=args.start,
        timeout_seconds=args.timeout_seconds,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
