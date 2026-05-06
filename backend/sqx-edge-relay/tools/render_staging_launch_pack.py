from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BLUEPRINT = ROOT / "deploy" / "render.staging.yaml.example"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "render_staging_launch_pack"


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_staging_gate = _load_module(
    "sqx_edge_render_staging_gate_launch_pack",
    "tools/render_staging_gate.py",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_env_keys(blueprint_text: str) -> list[str]:
    keys = re.findall(r"^\s*-\s*key:\s*([A-Z0-9_]+)\s*$", blueprint_text, flags=re.MULTILINE)
    return sorted(set(keys))


def build_operator_commands(base_url: str) -> list[str]:
    commands = [
        "python backend\\sqx-edge-relay\\tools\\render_credentials_handshake.py",
        "python backend\\sqx-edge-relay\\tools\\render_staging_gate.py --use-latest-handshake",
    ]
    if base_url:
        commands.append(
            f"python backend\\sqx-edge-relay\\tools\\render_staging_gate.py --use-latest-handshake --base-url {base_url}"
        )
        commands.append(
            f"python backend\\sqx-edge-relay\\tools\\render_staging_gate.py --use-latest-handshake --base-url {base_url} --send-webhook"
        )
    else:
        commands.append(
            "python backend\\sqx-edge-relay\\tools\\render_staging_gate.py --use-latest-handshake --base-url https://your-render-staging-url.onrender.com"
        )
    return commands


def decision_from(gate: dict[str, Any], blueprint_ready: bool, env_keys: list[str]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not blueprint_ready:
        blockers.append("render_staging_blueprint_missing")
    if not env_keys:
        blockers.append("render_staging_env_keys_missing")
    if not gate.get("decision", {}).get("go"):
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
        "# SQX Edge Render Staging Launch Pack",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Blueprint: `{report['blueprint']['path']}`",
        f"- Blueprint SHA256: `{report['blueprint'].get('sha256') or 'missing'}`",
        f"- Base URL: `{report.get('base_url') or 'not configured'}`",
        "",
        "## Required Render Env Vars",
    ]
    lines.extend(f"- `{item}`" for item in report["required_env_keys"] or ["none"])
    lines.append("")
    lines.append("## Operator Commands")
    for command in report["operator_commands"]:
        lines.append(f"- `{command}`")
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.extend([
        "",
        "## Safety Rules",
        "",
        "- Do not paste account passwords into env files, scripts or commits.",
        "- Use Render API key only for preflight.",
        "- Set Render service secrets in Render, not in the repository.",
        "- Connect Lemon Squeezy webhooks only after this launch pack and staging gate return `GO`.",
    ])
    return "\n".join(lines) + "\n"


def write_pack(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"render_staging_launch_pack_{current_stamp}.json"
    md_path = output_dir / f"render_staging_launch_pack_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_launch_pack(
    blueprint_path: Path = DEFAULT_BLUEPRINT,
    base_url: str = "",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    blueprint_ready = blueprint_path.is_file()
    blueprint_text = blueprint_path.read_text(encoding="utf-8-sig") if blueprint_ready else ""
    env_keys = extract_env_keys(blueprint_text)
    gate = render_staging_gate.collect_gate(
        api_key=env_value("RENDER_API_KEY"),
        owner_id=env_value("RENDER_OWNER_ID"),
        blueprint_path=blueprint_path,
        base_url=base_url,
        operator_token=env_value("SQX_RELAY_OPERATOR_TOKEN"),
        lemon_secret=env_value("SQX_LEMON_WEBHOOK_SECRET"),
        write=False,
    )
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": "render",
        "base_url": base_url,
        "blueprint": {
            "path": str(blueprint_path),
            "exists": blueprint_ready,
            "sha256": sha256_file(blueprint_path) if blueprint_ready else "",
        },
        "required_env_keys": env_keys,
        "operator_commands": build_operator_commands(base_url),
        "gate": gate,
        "decision": decision_from(gate, blueprint_ready, env_keys),
    }
    if write:
        report["evidence_paths"] = write_pack(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge Render staging launch pack")
    parser.add_argument("--blueprint", default=env_value("SQX_RENDER_STAGING_BLUEPRINT", str(DEFAULT_BLUEPRINT)))
    parser.add_argument("--base-url", default=env_value("SQX_RELAY_STAGING_BASE_URL"))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_launch_pack(
        blueprint_path=Path(args.blueprint),
        base_url=args.base_url,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
