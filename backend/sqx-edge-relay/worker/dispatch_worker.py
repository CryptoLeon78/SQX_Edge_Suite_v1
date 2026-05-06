from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


relay_queue = _load_module("sqx_edge_relay_queue_worker", "core/relay_queue.py")
relay_settings = _load_module("sqx_edge_relay_settings_worker", "core/relay_settings.py")


def run_once() -> dict:
    secret = relay_settings.relay_secret()
    if not secret:
        return {"ok": False, "error": "relay_secret_missing"}
    return relay_queue.dispatch_due_items(
        relay_settings.target_url(),
        secret,
        limit=relay_settings.worker_limit(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="SQX Edge relay dispatch worker")
    parser.add_argument("--once", action="store_true", help="Run one dispatch pass and exit.")
    args = parser.parse_args()

    while True:
        result = run_once()
        print(result, flush=True)
        if args.once:
            return 0 if result.get("ok") else 2
        time.sleep(relay_settings.worker_interval_seconds())


if __name__ == "__main__":
    sys.exit(main())
