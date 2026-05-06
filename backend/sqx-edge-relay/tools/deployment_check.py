from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


relay_settings = _load_module("sqx_edge_relay_settings_deploy_check", "core/relay_settings.py")


REQUIRED_FILES = [
    ROOT / "Dockerfile",
    ROOT / ".dockerignore",
    ROOT / ".env.example",
    ROOT / "requirements.txt",
    ROOT / "api" / "server.py",
    ROOT / "core" / "relay_queue.py",
    ROOT / "core" / "relay_settings.py",
    ROOT / "core" / "relay_observability.py",
    ROOT / "worker" / "dispatch_worker.py",
    ROOT / "tools" / "simulate_purchase_flow.py",
    ROOT / "deploy" / "docker-compose.yml",
    ROOT / "deploy" / "render.yaml.example",
    ROOT / "deploy" / "railway.json",
    ROOT / "deploy" / "fly.toml.example",
    ROOT / "deploy" / "systemd" / "sqx-edge-relay.service",
    ROOT / "deploy" / "systemd" / "sqx-edge-relay-worker.service",
]


SECRET_VARS = [
    "SQX_LEMON_WEBHOOK_SECRET",
    "SQX_FULFILLMENT_RELAY_SECRET",
    "SQX_RELAY_OPERATOR_TOKEN",
]


PLACEHOLDER_TOKENS = ("replace-", "change-me", "example", "demo", "secret")


def secret_status(name: str) -> dict[str, Any]:
    value = os.environ.get(name, "").strip()
    placeholder = any(token in value.lower() for token in PLACEHOLDER_TOKENS)
    return {
        "name": name,
        "configured": bool(value),
        "length_ok": len(value) >= 32,
        "placeholder": placeholder,
    }


def run_check() -> dict[str, Any]:
    missing_files = [str(path.relative_to(PROJECT_ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    secrets = [secret_status(name) for name in SECRET_VARS]
    secret_ready = all(item["configured"] and item["length_ok"] and not item["placeholder"] for item in secrets)
    config = relay_settings.config_status()
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8-sig") if (ROOT / "Dockerfile").is_file() else ""
    docker_ready = "gunicorn api.server:app" in dockerfile and "0.0.0.0" in dockerfile
    checks = {
        "files_ready": not missing_files,
        "docker_ready": docker_ready,
        "secrets_ready": secret_ready,
        "config_status": config,
        "secrets": secrets,
        "missing_files": missing_files,
        "health_check_path": "/relay/health",
        "config_check_path": "/relay/config-check",
        "observability_path": "/relay/observability",
    }
    checks["production_ready"] = checks["files_ready"] and checks["docker_ready"] and checks["secrets_ready"] and config.get("production_ready")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge relay deployment preflight")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero unless production_ready is true.")
    args = parser.parse_args()
    report = run_check()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.strict and not report["production_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
