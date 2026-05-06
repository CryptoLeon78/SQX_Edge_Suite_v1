from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, jsonify, request  # type: ignore


def _load_relay_queue_module():
    module_path = ROOT / "core" / "relay_queue.py"
    spec = importlib.util.spec_from_file_location("sqx_edge_relay_queue", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load relay queue module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_relay_settings_module():
    module_path = ROOT / "core" / "relay_settings.py"
    spec = importlib.util.spec_from_file_location("sqx_edge_relay_settings", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load relay settings module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_RELAY_QUEUE = _load_relay_queue_module()
_RELAY_SETTINGS = _load_relay_settings_module()
dispatch_due_items = _RELAY_QUEUE.dispatch_due_items
dispatch_queue_item = _RELAY_QUEUE.dispatch_queue_item
enqueue_lemon_webhook = _RELAY_QUEUE.enqueue_lemon_webhook
load_queue_item = _RELAY_QUEUE.load_queue_item
queue_overview = _RELAY_QUEUE.queue_overview
requeue_failed_item = _RELAY_QUEUE.requeue_failed_item
config_status = _RELAY_SETTINGS.config_status
is_operator_authorized = _RELAY_SETTINGS.is_operator_authorized


app = Flask(__name__)
VERSION = "0.2.0"


def relay_secret() -> str:
    return _RELAY_SETTINGS.relay_secret()


def lemon_secret() -> str:
    return _RELAY_SETTINGS.lemon_secret()


def target_url() -> str:
    return _RELAY_SETTINGS.target_url()


def operator_guard():
    if is_operator_authorized(request.headers):
        return None
    return jsonify({"ok": False, "error": "operator_token_required"}), 401


@app.get("/relay/health")
def health():
    overview = queue_overview()
    status = config_status()
    return jsonify({
        "ok": True,
        "version": VERSION,
        "relay_secret_configured": "SQX_FULFILLMENT_RELAY_SECRET" not in status["missing"],
        "lemon_secret_configured": "SQX_LEMON_WEBHOOK_SECRET" not in status["missing"],
        "operator_token_configured": status["operator_token_configured"],
        "target_url": target_url(),
        "summary": overview["summary"],
    })


@app.get("/relay/config-check")
def config_check():
    return jsonify({"ok": True, "config": config_status()})


@app.post("/relay/webhook/lemon")
def webhook_lemon():
    secret = lemon_secret()
    if not secret:
        return jsonify({"ok": False, "error": "webhook_secret_missing"}), 503
    signature = request.headers.get("X-Signature", "")
    result = enqueue_lemon_webhook(request.get_data(), signature, secret)
    return jsonify(result), 200 if result.get("ok") else 401


@app.get("/relay/queue")
def queue_list():
    guarded = operator_guard()
    if guarded:
        return guarded
    return jsonify({"ok": True, **queue_overview()})


@app.get("/relay/queue/<path:name>")
def queue_detail(name: str):
    guarded = operator_guard()
    if guarded:
        return guarded
    try:
        payload = load_queue_item(name)
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "queue_item_not_found"}), 404
    return jsonify({"ok": True, "bundle": payload})


@app.post("/relay/dispatch")
def dispatch():
    guarded = operator_guard()
    if guarded:
        return guarded
    secret = relay_secret()
    if not secret:
        return jsonify({"ok": False, "error": "relay_secret_missing"}), 503
    data = request.get_json(silent=True) or {}
    name = str(data.get("name") or "").strip()
    url = str(data.get("target_url") or target_url()).strip()
    if name:
        try:
            result = dispatch_queue_item(name, url, secret)
        except FileNotFoundError:
            return jsonify({"ok": False, "error": "queue_item_not_found"}), 404
        return jsonify(result), 200 if result.get("ok") else 502
    limit = int(data.get("limit") or 10)
    return jsonify(dispatch_due_items(url, secret, limit=limit))


@app.post("/relay/requeue")
def requeue():
    guarded = operator_guard()
    if guarded:
        return guarded
    data = request.get_json(silent=True) or {}
    name = str(data.get("name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "missing name"}), 400
    try:
        result = requeue_failed_item(name)
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "queue_item_not_found"}), 404
    return jsonify(result)


def main(host: str = "127.0.0.1", port: int = 6060) -> None:
    print(f"[SQX Relay] http://{host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6060)
    args = parser.parse_args()
    main(args.host, args.port)
