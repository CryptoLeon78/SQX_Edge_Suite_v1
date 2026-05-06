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
DEFAULT_OUTPUT_DIR = ROOT / "data" / "render_staging_purchase_drill"
DEFAULT_APPLY_GATE_DIR = ROOT / "data" / "render_staging_apply_gate"


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


staging_smoke = _load_module(
    "sqx_edge_staging_smoke_purchase_drill",
    "tools/staging_smoke.py",
)


def env_value(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_apply_gate_file(directory: Path = DEFAULT_APPLY_GATE_DIR) -> Path | None:
    files = sorted(directory.glob("render_staging_apply_gate_*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return files[0] if files else None


def auth_headers(operator_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {operator_token}"} if operator_token else {}


def queue_request(base_url: str, operator_token: str, timeout: int) -> dict[str, Any]:
    return staging_smoke.request_json(
        f"{staging_smoke.normalize_base_url(base_url)}/relay/queue",
        headers=auth_headers(operator_token),
        timeout=timeout,
    )


def dispatch_request(base_url: str, operator_token: str, limit: int, timeout: int) -> dict[str, Any]:
    raw = json.dumps({"limit": limit}, sort_keys=True).encode("utf-8")
    return staging_smoke.request_json(
        f"{staging_smoke.normalize_base_url(base_url)}/relay/dispatch",
        method="POST",
        headers={"Content-Type": "application/json", **auth_headers(operator_token)},
        body=raw,
        timeout=timeout,
    )


def webhook_request(base_url: str, lemon_secret: str, timeout: int) -> dict[str, Any]:
    raw = json.dumps(staging_smoke.demo_payload(), sort_keys=True).encode("utf-8")
    return staging_smoke.request_json(
        f"{staging_smoke.normalize_base_url(base_url)}/relay/webhook/lemon",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Signature": staging_smoke.sign_body(raw, lemon_secret),
        },
        body=raw,
        timeout=timeout,
    )


def decision_from(
    apply_gate: dict[str, Any] | None,
    base_url: str,
    operator_token: str,
    lemon_secret: str,
    send_webhook: bool,
    run_dispatch: bool,
    queue_before: dict[str, Any] | None,
    webhook: dict[str, Any] | None,
    queue_after_webhook: dict[str, Any] | None,
    dispatch: dict[str, Any] | None,
    queue_after_dispatch: dict[str, Any] | None,
    allow_no_go_apply_gate: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if apply_gate is None:
        blockers.append("render_staging_apply_gate_missing")
    elif not apply_gate.get("decision", {}).get("go") and not allow_no_go_apply_gate:
        blockers.append("render_staging_apply_gate_not_go")
        blockers.extend(apply_gate.get("decision", {}).get("blockers", []))
    if not base_url:
        blockers.append("render_staging_url_missing")
    if not operator_token:
        blockers.append("sqx_relay_operator_token_missing")
    if not lemon_secret:
        blockers.append("sqx_lemon_webhook_secret_missing")
    if not send_webhook:
        blockers.append("staging_purchase_webhook_not_sent")
    if not run_dispatch:
        blockers.append("staging_purchase_dispatch_not_run")

    for name, result in (
        ("queue_before_failed", queue_before),
        ("webhook_demo_failed", webhook),
        ("queue_after_webhook_failed", queue_after_webhook),
        ("dispatch_failed", dispatch),
        ("queue_after_dispatch_failed", queue_after_dispatch),
    ):
        if result is not None and not result.get("ok"):
            blockers.append(name)

    if dispatch is not None:
        results = dispatch.get("payload", {}).get("results", [])
        if isinstance(results, list) and not results:
            warnings.append("dispatch_returned_no_items")

    deduped_blockers = sorted(set(blockers))
    return {
        "go": not deduped_blockers,
        "label": "GO" if not deduped_blockers else "NO-GO",
        "blockers": deduped_blockers,
        "warnings": sorted(set(warnings)),
    }


def markdown_report(report: dict[str, Any]) -> str:
    decision = report["decision"]

    def ok_value(name: str) -> bool:
        value = report.get(name)
        return bool(value.get("ok")) if isinstance(value, dict) else False

    lines = [
        "# SQX Edge Render Staging Purchase Drill",
        "",
        f"- Created: `{report['created_at']}`",
        f"- Decision: `{decision['label']}`",
        f"- Base URL: `{report.get('base_url') or 'not configured'}`",
        f"- Apply gate source: `{report.get('apply_gate_source') or 'none'}`",
        f"- Webhook sent: `{report['send_webhook']}`",
        f"- Dispatch run: `{report['run_dispatch']}`",
        "",
        "## Remote Flow",
        "",
        f"- Queue before: `{ok_value('queue_before')}`",
        f"- Webhook demo: `{ok_value('webhook_demo')}`",
        f"- Queue after webhook: `{ok_value('queue_after_webhook')}`",
        f"- Dispatch: `{ok_value('dispatch')}`",
        f"- Queue after dispatch: `{ok_value('queue_after_dispatch')}`",
        "",
        "## Blockers",
    ]
    lines.extend(f"- `{item}`" for item in decision["blockers"] or ["none"])
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- `{item}`" for item in decision["warnings"] or ["none"])
    lines.extend([
        "",
        "## Safety Rules",
        "",
        "- Use this only against staging services.",
        "- Keep Lemon and relay secrets in environment variables or Render settings.",
        "- Do not connect live checkout until this drill and the apply gate are `GO`.",
    ])
    return "\n".join(lines) + "\n"


def write_drill(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_stamp = stamp()
    json_path = output_dir / f"render_staging_purchase_drill_{current_stamp}.json"
    md_path = output_dir / f"render_staging_purchase_drill_{current_stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def collect_purchase_drill(
    apply_gate_file: Path | None = None,
    base_url: str = "",
    operator_token: str = "",
    lemon_secret: str = "",
    send_webhook: bool = False,
    run_dispatch: bool = False,
    dispatch_limit: int = 1,
    timeout: int = staging_smoke.DEFAULT_TIMEOUT_SECONDS,
    allow_no_go_apply_gate: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write: bool = True,
) -> dict[str, Any]:
    apply_gate = load_json(apply_gate_file) if apply_gate_file else None
    queue_before = None
    webhook = None
    queue_after_webhook = None
    dispatch = None
    queue_after_dispatch = None

    if base_url and operator_token:
        queue_before = queue_request(base_url, operator_token, timeout)
    if base_url and lemon_secret and send_webhook:
        webhook = webhook_request(base_url, lemon_secret, timeout)
    if base_url and operator_token and send_webhook:
        queue_after_webhook = queue_request(base_url, operator_token, timeout)
    if base_url and operator_token and run_dispatch:
        dispatch = dispatch_request(base_url, operator_token, dispatch_limit, timeout)
        queue_after_dispatch = queue_request(base_url, operator_token, timeout)

    report: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "provider": "render",
        "base_url": base_url,
        "apply_gate_source": str(apply_gate_file) if apply_gate_file else "",
        "apply_gate_decision": apply_gate.get("decision") if apply_gate else None,
        "send_webhook": send_webhook,
        "run_dispatch": run_dispatch,
        "dispatch_limit": dispatch_limit,
        "queue_before": queue_before,
        "webhook_demo": webhook,
        "queue_after_webhook": queue_after_webhook,
        "dispatch": dispatch,
        "queue_after_dispatch": queue_after_dispatch,
        "decision": decision_from(
            apply_gate,
            base_url,
            operator_token,
            lemon_secret,
            send_webhook,
            run_dispatch,
            queue_before,
            webhook,
            queue_after_webhook,
            dispatch,
            queue_after_dispatch,
            allow_no_go_apply_gate,
        ),
    }
    if write:
        report["evidence_paths"] = write_drill(report, output_dir)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge Render staging purchase drill")
    parser.add_argument("--apply-gate-file", default="")
    parser.add_argument("--use-latest-apply-gate", action="store_true")
    parser.add_argument("--base-url", default=env_value("SQX_RELAY_STAGING_BASE_URL"))
    parser.add_argument("--operator-token", default=env_value("SQX_RELAY_OPERATOR_TOKEN"))
    parser.add_argument("--lemon-secret", default=env_value("SQX_LEMON_WEBHOOK_SECRET"))
    parser.add_argument("--send-webhook", action="store_true")
    parser.add_argument("--dispatch", action="store_true")
    parser.add_argument("--dispatch-limit", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=staging_smoke.DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--allow-no-go-apply-gate", action="store_true")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    apply_gate_file = Path(args.apply_gate_file) if args.apply_gate_file else None
    if args.use_latest_apply_gate and apply_gate_file is None:
        apply_gate_file = latest_apply_gate_file()
        if apply_gate_file is None:
            print(json.dumps({"ok": False, "error": "render_staging_apply_gate_evidence_missing"}, indent=2, sort_keys=True))
            return 2

    report = collect_purchase_drill(
        apply_gate_file=apply_gate_file,
        base_url=args.base_url,
        operator_token=args.operator_token,
        lemon_secret=args.lemon_secret,
        send_webhook=args.send_webhook,
        run_dispatch=args.dispatch,
        dispatch_limit=args.dispatch_limit,
        timeout=args.timeout,
        allow_no_go_apply_gate=args.allow_no_go_apply_gate,
        output_dir=Path(args.output_dir),
        write=not args.no_write,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["go"] else 2


if __name__ == "__main__":
    sys.exit(main())
