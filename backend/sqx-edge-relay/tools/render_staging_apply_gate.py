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
DEFAULT_OUTPUT_DIR = ROOT / "data" / "render_staging_apply_gate"
DEFAULT_HANDOFF_DIR = ROOT / "data" / "local_ingest_render_handoff"
DEFAULT_HANDSHAKE_DIR = ROOT / "data" / "render_preflight_evidence"


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_staging_gate = _load_module(
    "sqx_edge_render_staging_gate_apply",
    "tools/render_staging_gate.py",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def handoff_env_values(handoff: dict[str, Any]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in handoff.get("render_env_lines", []):
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def build_apply_commands(handoff_file: str, base_url: str) -> list[str]:
    commands = [
        "python backend\\sqx-edge-relay\\tools\\local_ingest_render_handoff.py --use-latest-session",
        "python backend\\sqx-edge-relay\\tools\\render_staging_apply_gate.py --use-latest-handoff --confirm-env-applied --base-url https://your-render-staging-url.onrender.com --use-latest-handshake",
    ]
    if handoff_file:
        commands[1] = (
            f"python backend\\sqx-edge-relay\\tools\\render_staging_apply_gate.py --handoff-file {handoff_file} "
            "--confirm-env-applied --base-url https://your-render-staging-url.onrender.com --use-latest-handshake"
        )
    if base_url:
        commands.append(
            f"python backend\\sqx-edge-relay\\tools\\render_staging_gate.py --use-latest-handshake --base-url {base_url}"
        )
        commands.append(
            f"python backend\\sqx-edge-relay\\tools\\render_staging_gate.py --use-latest-handshake --base-url {base_url} --send-webhook"
        )
    return commands


def decision_from(
    handoff: dict[str, Any] | None,
    env_values: dict[str, str],
    base_url: str,
    confirm_env_applied: bool,
    gate: dict[str, Any] | None,
    skip_remote_gate: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if handoff is None:
        blockers.append("local_ingest_render_handoff_missing")
    elif not handoff.get("decision", {}).get("go"):
        blockers.append("local_ingest_render_handoff_not_go")
        blockers.extend(handoff.get("decision", {}).get("blockers", []))

    for key in ("SQX_LOCAL_INGEST_URL", "SQX_RELAY_WORKER_INTERVAL_SECONDS", "SQX_RELAY_WORKER_LIMIT"):
        if not env_values.get(key):
            blockers.append(f"{key.lower()}_missing")

    if not confirm_env_applied:
        blockers.append("render_env_values_not_confirmed")
    if not base_url:
        blockers.append("render_staging_url_missing")

    if skip_remote_gate:
        blockers.append("render_staging_gate_not_run")
    elif gate is None:
        blockers.append("render_staging_gate_missing")
    elif not gate.get("decision", {}).get("go"):
        blockers.append("render_staging_gate_not_go")
        blockers.extend(gate.get("decision", {}).get("blockers", []))
        warnings.extend(gate.get("decision", {}).get("warnings", []))

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
        "# SQX Edge Render Staging Apply Gate",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Base URL: `{report.get('base_url') or 'not configured'}`",
        f"- Handoff source: `{report.get('handoff_source') or 'none'}`",
        f"- Env applied confirmed: `{report['confirm_env_applied']}`",
        "",
        "## Render Values To Apply",
    ]
    for key, value in report["render_env_values"].items():
        lines.append(f"- `{key}={value}`")
    if not report["render_env_values"]:
        lines.append("- `none`")
    lines.append("")
    lines.append("## Apply Checklist")
    lines.extend([
        "- Paste the handoff values into the Render web service and worker.",
        "- Deploy or redeploy both Render services.",
        "- Run this gate with `--confirm-env-applied` only after the values are visible in Render.",
        "- Keep Render API keys, Lemon secrets and relay tokens outside git.",
        "- Connect live checkout webhooks only after this gate returns `GO`.",
    ])
    lines.append("")
    lines.append("## Operator Commands")
    lines.extend(f"- `{command}`" for command in report["operator_commands"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    return "\n".join(lines) + "\n"


def write_gate(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"render_staging_apply_gate_{current_stamp}.json"
    md_path = output_dir / f"render_staging_apply_gate_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_apply_gate(
    handoff_file: Path | None = None,
    handshake_file: Path | None = None,
    base_url: str = "",
    confirm_env_applied: bool = False,
    operator_token: str = "",
    lemon_secret: str = "",
    send_webhook: bool = False,
    skip_remote_gate: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    handoff = load_json(handoff_file) if handoff_file else None
    env_values = handoff_env_values(handoff or {})
    gate = None
    if not skip_remote_gate and base_url:
        gate = render_staging_gate.collect_gate(
            handshake_file=handshake_file,
            base_url=base_url,
            operator_token=operator_token,
            lemon_secret=lemon_secret,
            send_webhook=send_webhook,
            write=write,
        )

    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": "render",
        "base_url": base_url,
        "handoff_source": str(handoff_file) if handoff_file else "",
        "handoff_decision": handoff.get("decision") if handoff else None,
        "render_env_values": env_values,
        "confirm_env_applied": confirm_env_applied,
        "send_webhook": send_webhook,
        "remote_gate": gate,
        "operator_commands": build_apply_commands(str(handoff_file) if handoff_file else "", base_url),
        "decision": decision_from(handoff, env_values, base_url, confirm_env_applied, gate, skip_remote_gate),
    }
    if write:
        report["evidence_paths"] = write_gate(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge Render staging apply gate")
    parser.add_argument("--handoff-file", default="")
    parser.add_argument("--use-latest-handoff", action="store_true")
    parser.add_argument("--handshake-file", default="")
    parser.add_argument("--use-latest-handshake", action="store_true")
    parser.add_argument("--base-url", default=env_value("SQX_RELAY_STAGING_BASE_URL"))
    parser.add_argument("--confirm-env-applied", action="store_true")
    parser.add_argument("--operator-token", default=env_value("SQX_RELAY_OPERATOR_TOKEN"))
    parser.add_argument("--lemon-secret", default=env_value("SQX_LEMON_WEBHOOK_SECRET"))
    parser.add_argument("--send-webhook", action="store_true")
    parser.add_argument("--skip-remote-gate", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    handoff_file = Path(args.handoff_file) if args.handoff_file else None
    if args.use_latest_handoff and handoff_file is None:
        handoff_file = latest_file(DEFAULT_HANDOFF_DIR, "local_ingest_render_handoff_*.json")
        if handoff_file is None:
            print(json.dumps({"ok": False, "error": "local_ingest_render_handoff_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    handshake_file = Path(args.handshake_file) if args.handshake_file else None
    if args.use_latest_handshake and handshake_file is None:
        handshake_file = latest_file(DEFAULT_HANDSHAKE_DIR, "render_credential_handshake_*.json")
        if handshake_file is None and not args.skip_remote_gate:
            print(json.dumps({"ok": False, "error": "render_handshake_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_apply_gate(
        handoff_file=handoff_file,
        handshake_file=handshake_file,
        base_url=args.base_url,
        confirm_env_applied=args.confirm_env_applied,
        operator_token=args.operator_token,
        lemon_secret=args.lemon_secret,
        send_webhook=args.send_webhook,
        skip_remote_gate=args.skip_remote_gate,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
