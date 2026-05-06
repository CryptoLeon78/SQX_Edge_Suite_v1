from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


relay_queue = _load_module("sqx_edge_relay_queue_simulation", "core/relay_queue.py")
relay_observability = _load_module("sqx_edge_relay_observability_simulation", "core/relay_observability.py")


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        return False

    def read(self) -> bytes:
        return b'{"ok":true,"stored":true}'


def demo_payload() -> dict:
    return {
        "meta": {"event_name": "order_created", "webhook_id": "wh_m18_demo"},
        "data": {
            "type": "orders",
            "id": "m18-demo-order",
            "attributes": {
                "identifier": "ls-order-m18-demo",
                "customer_id": 18,
                "user_name": "Cliente Demo M18",
                "user_email": "m18-demo@example.com",
                "status": "paid",
                "refunded": False,
                "first_order_item": {"variant_id": "", "variant_name": "SQX Edge Pro Mensual"},
            },
        },
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        obs_root = root / "observability"
        with patch.object(relay_queue, "QUEUE_ROOT", root / "queue"), \
                patch.object(relay_queue, "INCOMING_DIR", root / "queue" / "incoming"), \
                patch.object(relay_queue, "PENDING_DIR", root / "queue" / "pending"), \
                patch.object(relay_queue, "SENT_DIR", root / "queue" / "sent"), \
                patch.object(relay_queue, "FAILED_DIR", root / "queue" / "failed"), \
                patch.object(relay_observability, "OBS_ROOT", obs_root), \
                patch.object(relay_observability, "LOG_DIR", obs_root / "logs"), \
                patch.object(relay_observability, "SNAPSHOT_DIR", obs_root / "snapshots"), \
                patch.object(relay_observability, "EVENT_LOG", obs_root / "logs" / "relay_events.jsonl"), \
                patch.object(relay_queue, "log_event", relay_observability.log_event), \
                patch.object(relay_queue.urlrequest, "urlopen", return_value=FakeResponse()):
            raw = json.dumps(demo_payload(), sort_keys=True).encode("utf-8")
            signature = hmac.new(b"lemon-secret", raw, hashlib.sha256).hexdigest()
            enqueue = relay_queue.enqueue_lemon_webhook(raw, signature, "lemon-secret")
            name = enqueue["bundle"]["name"]
            dispatch = relay_queue.dispatch_queue_item(name, "http://127.0.0.1:5050/api/fulfillment/relay-ingest", "relay-secret")
            snapshot = relay_observability.write_snapshot(relay_queue.queue_overview(), {"ok": True, "production_ready": True})
            result = {
                "ok": bool(enqueue.get("ok") and dispatch.get("ok") and snapshot.get("ok")),
                "enqueue": enqueue,
                "dispatch_status": dispatch.get("bundle", {}).get("status"),
                "snapshot_file": snapshot.get("snapshot_file"),
                "summary": snapshot.get("snapshot", {}).get("queue", {}).get("summary", {}),
            }
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
