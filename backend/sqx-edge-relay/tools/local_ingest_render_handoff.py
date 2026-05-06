from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


RELAY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = RELAY_ROOT / "data" / "local_ingest_render_handoff"
DEFAULT_SESSION_DIR = RELAY_ROOT / "data" / "local_ingest_staging_session"


def _load_module(name: str, relative_path: str):
    module_path = RELAY_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


local_ingest_tunnel_check = _load_module(
    "sqx_edge_local_ingest_tunnel_check_handoff",
    "tools/local_ingest_tunnel_check.py",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_session_file(session_dir: Path = DEFAULT_SESSION_DIR) -> Path | None:
    files = sorted(session_dir.glob("local_ingest_staging_session_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def ingest_url_from_session(session: dict[str, Any]) -> str:
    tunnel = session.get("tunnel") or {}
    return str(tunnel.get("ingest_url") or "").strip()


def is_session_go(session: dict[str, Any]) -> bool:
    return bool(session.get("decision", {}).get("go"))


def render_env_lines(ingest_url: str) -> list[str]:
    return [
        f"SQX_LOCAL_INGEST_URL={ingest_url}",
        "SQX_RELAY_WORKER_INTERVAL_SECONDS=30",
        "SQX_RELAY_WORKER_LIMIT=10",
    ]


def decision_from(ingest_url: str, session: dict[str, Any] | None, check: dict[str, Any] | None, require_go_session: bool) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not ingest_url:
        blockers.append("sqx_local_ingest_url_missing")
    if require_go_session and session is not None and not is_session_go(session):
        blockers.append("local_ingest_staging_session_not_go")
        blockers.extend(session.get("decision", {}).get("blockers", []))
    if session is None:
        warnings.append("local_ingest_session_not_attached")
    if check is not None and not check.get("decision", {}).get("go"):
        blockers.append("local_ingest_tunnel_check_not_go")
        blockers.extend(check.get("decision", {}).get("blockers", []))
        warnings.extend(check.get("decision", {}).get("warnings", []))
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
        "# SQX Edge Local Ingest Render Handoff",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Ingest URL: `{report.get('ingest_url') or 'not configured'}`",
        f"- Session source: `{report.get('session_source') or 'none'}`",
        "",
        "## Render Values",
    ]
    lines.extend(f"- `{line}`" for line in report["render_env_lines"] or ["none"])
    lines.append("")
    lines.append("## Blockers")
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.extend([
        "",
        "## Next Commands",
        "",
        "- Paste `SQX_LOCAL_INGEST_URL` into Render staging service and worker.",
        "- Re-run `render_staging_secrets_kit.py` with the same URL if you need a fresh staging `.env`.",
        "- Run `render_staging_gate.py --use-latest-handshake --base-url <render-staging-url>` after Render deploy.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"local_ingest_render_handoff_{current_stamp}.json"
    md_path = output_dir / f"local_ingest_render_handoff_{current_stamp}.md"
    env_path = output_dir / f"local_ingest_render_handoff_{current_stamp}.env"
    env_path.write_text("\n".join(report["render_env_lines"]) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "env": str(env_path)}


def collect_handoff(
    ingest_url: str = "",
    session_file: Path | None = None,
    relay_secret: str = "",
    validate: bool = False,
    require_go_session: bool = True,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    session = load_json(session_file) if session_file else None
    source = str(session_file) if session_file else ""
    final_ingest_url = ingest_url.strip() or (ingest_url_from_session(session) if session else "")
    check = None
    if validate and final_ingest_url and relay_secret:
        check = local_ingest_tunnel_check.collect_check(
            ingest_url=final_ingest_url,
            relay_secret=relay_secret,
            send_bundle=False,
            write=False,
        )
    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "ingest_url": final_ingest_url,
        "session_source": source,
        "session_decision": session.get("decision") if session else None,
        "relay_secret_configured": bool(relay_secret),
        "validation": check,
        "render_env_lines": render_env_lines(final_ingest_url) if final_ingest_url else [],
        "decision": decision_from(final_ingest_url, session, check, require_go_session),
    }
    if write:
        report["evidence_paths"] = write_outputs(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge local ingest Render handoff pack")
    parser.add_argument("--ingest-url", default=env_value("SQX_LOCAL_INGEST_URL"))
    parser.add_argument("--session-file", default="")
    parser.add_argument("--use-latest-session", action="store_true")
    parser.add_argument("--relay-secret", default=env_value("SQX_FULFILLMENT_RELAY_SECRET"))
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--allow-no-go-session", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    session_file = Path(args.session_file) if args.session_file else None
    if args.use_latest_session and session_file is None:
        session_file = latest_session_file()
        if session_file is None:
            print(json.dumps({"ok": False, "error": "local_ingest_session_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_handoff(
        ingest_url=args.ingest_url,
        session_file=session_file,
        relay_secret=args.relay_secret,
        validate=args.validate,
        require_go_session=not args.allow_no_go_session,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
