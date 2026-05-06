import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


server = _load_module("sqx_edge_relay_server_test", "api/server.py")
relay_queue = _load_module("sqx_edge_relay_queue_test", "core/relay_queue.py")


class RelayApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

    def get_json(self, response):
        return json.loads(response.data.decode("utf-8"))

    def test_health_endpoint(self):
        response = self.client.get("/relay/health")
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertIn("summary", data)

    def test_webhook_requires_lemon_secret(self):
        with patch.dict(server.os.environ, {}, clear=True):
            response = self.client.post("/relay/webhook/lemon", data=b"{}")
        self.assertEqual(response.status_code, 503)

    def test_webhook_accepts_event(self):
        stored = {"ok": True, "stored": True, "bundle": {"relay_event_id": "relay_1"}}
        with patch.dict(server.os.environ, {"SQX_LEMON_WEBHOOK_SECRET": "secret"}, clear=False), \
                patch.object(server, "enqueue_lemon_webhook", return_value=stored) as enqueue:
            response = self.client.post("/relay/webhook/lemon", data=b'{"ok":true}', headers={"X-Signature": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_json(response)["bundle"]["relay_event_id"], "relay_1")
        enqueue.assert_called_once_with(b'{"ok":true}', "abc", "secret")

    def test_dispatch_requires_relay_secret(self):
        with patch.dict(server.os.environ, {}, clear=True):
            response = self.client.post("/relay/dispatch", json={})
        self.assertEqual(response.status_code, 503)

    def test_dispatch_single_item(self):
        result = {"ok": True, "bundle": {"status": "sent"}}
        with patch.dict(server.os.environ, {"SQX_FULFILLMENT_RELAY_SECRET": "relay-secret"}, clear=False), \
                patch.object(server, "dispatch_queue_item", return_value=result) as dispatch:
            response = self.client.post("/relay/dispatch", json={"name": "relay_bundle_demo.json", "target_url": "http://127.0.0.1:5050/api/fulfillment/relay-ingest"})
        self.assertEqual(response.status_code, 200)
        dispatch.assert_called_once()


class RelayQueueTestCase(unittest.TestCase):
    def test_enqueue_and_requeue_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(relay_queue, "QUEUE_ROOT", root), \
                    patch.object(relay_queue, "INCOMING_DIR", root / "incoming"), \
                    patch.object(relay_queue, "PENDING_DIR", root / "pending"), \
                    patch.object(relay_queue, "SENT_DIR", root / "sent"), \
                    patch.object(relay_queue, "FAILED_DIR", root / "failed"):
                relay_queue.ensure_queue_dirs()
                payload = {
                    "meta": {"event_name": "order_created", "webhook_id": "wh_demo"},
                    "data": {
                        "type": "orders",
                        "id": "1",
                        "attributes": {
                            "identifier": "ls-order-demo",
                            "customer_id": 9,
                            "user_name": "Cliente Demo",
                            "user_email": "demo@example.com",
                            "status": "paid",
                            "refunded": False,
                            "first_order_item": {"variant_id": "", "variant_name": "SQX Edge Pro Mensual"},
                        },
                    },
                }
                raw = json.dumps(payload).encode("utf-8")
                import hmac, hashlib
                signature = hmac.new(b"secret", raw, hashlib.sha256).hexdigest()
                result = relay_queue.enqueue_lemon_webhook(raw, signature, "secret")
                self.assertTrue(result["ok"])
                overview = relay_queue.queue_overview()
                self.assertEqual(overview["summary"]["pending"], 1)

                name = next((relay_queue.PENDING_DIR).glob("relay_bundle_*.json")).name
                bundle = relay_queue.requeue_failed_item(name)
                self.assertTrue(bundle["ok"])
