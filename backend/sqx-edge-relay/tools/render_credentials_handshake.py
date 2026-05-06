from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "render_preflight_evidence"
PREFLIGHT_PATH = ROOT / "tools" / "render_api_preflight.py"


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("sqx_render_api_preflight", PREFLIGHT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load Render preflight module from {PREFLIGHT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "[redacted]"
    return f"{value[:4]}...{value[-4:]}"


def secret_status(name: str, value: str, min_length: int = 8) -> dict[str, Any]:
    placeholder_markers = ("changeme", "placeholder", "example", "demo", "todo", "replace")
    lowered = value.lower()
    return {
        "name": name,
        "configured": bool(value),
        "length_ok": len(value) >= min_length if value else False,
        "placeholder": any(marker in lowered for marker in placeholder_markers) if value else False,
        "redacted": redact(value),
    }


def decision_from(blockers: list[str], preflight: dict[str, Any] | None) -> dict[str, Any]:
    if preflight and not preflight.get("ok"):
        blockers.extend(preflight.get("blockers", []))
    deduped = sorted(set(blockers))
    return {
        "go": not deduped,
        "label": "GO" if not deduped else "NO-GO",
        "blockers": deduped,
    }


def render_markdown(report: dict[str, Any]) -> str:
    decision = report["decision"]
    secrets = report["credential_status"]
    lines = [
        "# SQX Edge Render Credential Handshake",
        "",
        f"- Fecha UTC: {report['created_at']}",
        f"- Decision: {decision['label']}",
        f"- Blueprint: `{report['blueprint_path']}`",
        "",
        "## Credenciales",
    ]
    for item in secrets:
        configured = "yes" if item["configured"] else "no"
        length_ok = "yes" if item["length_ok"] else "no"
        placeholder = "yes" if item["placeholder"] else "no"
        lines.append(f"- `{item['name']}`: configured={configured}, length_ok={length_ok}, placeholder={placeholder}")
    lines.extend(["", "## Bloqueos"])
    if decision["blockers"]:
        for blocker in decision["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Politica de seguridad",
        "",
        "- No usar password de cuenta Render en scripts, docs ni commits.",
        "- Usar solo Render API key y owner/workspace ID.",
        "- Guardar evidencias en `backend/sqx-edge-relay/data/`, que esta ignorado por git.",
    ])
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"render_credential_handshake_{stamp}.json"
    markdown_path = output_dir / f"render_credential_handshake_{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def collect_handshake(
    api_key: str,
    owner_id: str,
    blueprint_path: Path,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if env_value("RENDER_PASSWORD") or env_value("RENDER_ACCOUNT_PASSWORD"):
        blockers.append("render_account_password_present_do_not_use")
    if not api_key:
        blockers.append("render_api_key_missing")
    if not owner_id:
        blockers.append("render_owner_id_missing")

    credential_status = [
        secret_status("RENDER_API_KEY", api_key, min_length=16),
        secret_status("RENDER_OWNER_ID", owner_id, min_length=4),
    ]
    for item in credential_status:
        if item["configured"] and item["placeholder"]:
            blockers.append(f"{item['name'].lower()}_placeholder")
        if item["configured"] and not item["length_ok"]:
            warnings.append(f"{item['name'].lower()}_short")

    preflight = None
    if api_key and owner_id:
        preflight_module = load_preflight_module()
        preflight = preflight_module.run_preflight(api_key, owner_id, blueprint_path)
    else:
        warnings.append("render_api_preflight_not_run")

    report: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": "render",
        "blueprint_path": str(blueprint_path),
        "credential_policy": "api_key_only_no_account_password",
        "credential_status": credential_status,
        "warnings": sorted(set(warnings)),
        "preflight": preflight,
        "decision": decision_from(blockers, preflight),
    }
    if write:
        report["evidence_paths"] = write_report(report, output_dir)
    return report


def main() -> int:
    preflight_module = load_preflight_module()
    parser = argparse.ArgumentParser(description="SQX Edge Render credential handshake")
    parser.add_argument("--api-key", default=env_value("RENDER_API_KEY"))
    parser.add_argument("--owner-id", default=env_value("RENDER_OWNER_ID"))
    parser.add_argument("--blueprint", default=env_value("SQX_RENDER_STAGING_BLUEPRINT", str(preflight_module.DEFAULT_BLUEPRINT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    report = collect_handshake(
        api_key=args.api_key,
        owner_id=args.owner_id,
        blueprint_path=Path(args.blueprint),
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
