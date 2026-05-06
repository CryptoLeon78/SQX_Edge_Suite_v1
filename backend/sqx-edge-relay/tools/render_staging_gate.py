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
DEFAULT_OUTPUT_DIR = ROOT / "data" / "render_staging_gate"
DEFAULT_HANDSHAKE_DIR = ROOT / "data" / "render_preflight_evidence"


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_credentials_handshake = _load_module(
    "sqx_edge_render_credentials_handshake_gate",
    "tools/render_credentials_handshake.py",
)
render_api_preflight = _load_module(
    "sqx_edge_render_api_preflight_gate",
    "tools/render_api_preflight.py",
)
staging_evidence = _load_module(
    "sqx_edge_relay_staging_evidence_gate",
    "tools/staging_evidence.py",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def latest_handshake_file(handshake_dir: Path) -> Path | None:
    files = sorted(handshake_dir.glob("render_credential_handshake_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def decision_from(handshake: dict[str, Any], staging: dict[str, Any] | None, base_url: str) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if not handshake.get("decision", {}).get("go"):
        blockers.append("render_credential_handshake_not_go")
        blockers.extend(handshake.get("decision", {}).get("blockers", []))
    if not base_url:
        blockers.append("render_staging_url_missing")
    if staging is None:
        warnings.append("staging_evidence_not_run")
    elif not staging.get("decision", {}).get("go"):
        blockers.append("render_staging_evidence_not_go")
        blockers.extend(staging.get("decision", {}).get("blockers", []))
        warnings.extend(staging.get("decision", {}).get("warnings", []))

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
        "# SQX Edge Render Staging Gate",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Base URL: `{report.get('base_url') or 'not configured'}`",
        f"- Handshake source: `{report['handshake_source']}`",
        "",
        "## Blockers",
    ]
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.extend([
        "",
        "## Gate Rules",
        "",
        "- Render credential handshake must be `GO`.",
        "- Staging URL must be configured.",
        "- Remote staging evidence must be `GO` before connecting payments.",
        "- Account passwords are never accepted as deployment credentials.",
    ])
    return "\n".join(lines) + "\n"


def write_gate(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"render_staging_gate_{current_stamp}.json"
    md_path = output_dir / f"render_staging_gate_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_gate(
    api_key: str = "",
    owner_id: str = "",
    blueprint_path: Path | None = None,
    handshake_file: Path | None = None,
    base_url: str = "",
    operator_token: str = "",
    lemon_secret: str = "",
    send_webhook: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    if handshake_file:
        handshake = load_json(handshake_file)
        handshake_source = str(handshake_file)
    else:
        handshake = render_credentials_handshake.collect_handshake(
            api_key=api_key,
            owner_id=owner_id,
            blueprint_path=blueprint_path or render_api_preflight.DEFAULT_BLUEPRINT,
            write=write,
        )
        handshake_source = "fresh_handshake"

    staging = None
    if handshake.get("decision", {}).get("go") and base_url:
        staging = staging_evidence.collect_evidence(
            provider="render",
            base_url=base_url,
            operator_token=operator_token,
            lemon_secret=lemon_secret,
            send_webhook=send_webhook,
        )
        if write:
            staging["evidence_paths"] = staging_evidence.write_evidence(staging, staging_evidence.DEFAULT_OUTPUT_DIR)

    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": "render",
        "base_url": base_url,
        "send_webhook": send_webhook,
        "handshake_source": handshake_source,
        "handshake": handshake,
        "staging_evidence": staging,
        "decision": decision_from(handshake, staging, base_url),
    }
    if write:
        report["evidence_paths"] = write_gate(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge Render staging go/no-go gate")
    parser.add_argument("--api-key", default=env_value("RENDER_API_KEY"))
    parser.add_argument("--owner-id", default=env_value("RENDER_OWNER_ID"))
    parser.add_argument("--blueprint", default=env_value("SQX_RENDER_STAGING_BLUEPRINT", str(render_api_preflight.DEFAULT_BLUEPRINT)))
    parser.add_argument("--handshake-file", default="")
    parser.add_argument("--use-latest-handshake", action="store_true")
    parser.add_argument("--base-url", default=env_value("SQX_RELAY_STAGING_BASE_URL"))
    parser.add_argument("--operator-token", default=env_value("SQX_RELAY_OPERATOR_TOKEN"))
    parser.add_argument("--lemon-secret", default=env_value("SQX_LEMON_WEBHOOK_SECRET"))
    parser.add_argument("--send-webhook", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    handshake_file = Path(args.handshake_file) if args.handshake_file else None
    if args.use_latest_handshake and handshake_file is None:
        handshake_file = latest_handshake_file(DEFAULT_HANDSHAKE_DIR)
        if handshake_file is None:
            print(json.dumps({"ok": False, "error": "render_handshake_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_gate(
        api_key=args.api_key,
        owner_id=args.owner_id,
        blueprint_path=Path(args.blueprint),
        handshake_file=handshake_file,
        base_url=args.base_url,
        operator_token=args.operator_token,
        lemon_secret=args.lemon_secret,
        send_webhook=args.send_webhook,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
