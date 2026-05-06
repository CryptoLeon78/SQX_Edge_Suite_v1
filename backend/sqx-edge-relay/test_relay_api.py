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
relay_observability = _load_module("sqx_edge_relay_observability_test", "core/relay_observability.py")
deployment_check = _load_module("sqx_edge_relay_deployment_check_test", "tools/deployment_check.py")
staging_smoke = _load_module("sqx_edge_relay_staging_smoke_test", "tools/staging_smoke.py")


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
        self.assertIn("operator_token_configured", data)

    def test_config_check_reports_missing_secrets(self):
        with patch.dict(server.os.environ, {}, clear=True):
            response = self.client.get("/relay/config-check")
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertIn("SQX_LEMON_WEBHOOK_SECRET", data["config"]["missing"])
        self.assertIn("SQX_FULFILLMENT_RELAY_SECRET", data["config"]["missing"])

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

    def test_operator_token_protects_queue(self):
        with patch.dict(server.os.environ, {"SQX_RELAY_OPERATOR_TOKEN": "operator-token"}, clear=True):
            blocked = self.client.get("/relay/queue")
            allowed = self.client.get("/relay/queue", headers={"X-SQX-Operator-Token": "operator-token"})
        self.assertEqual(blocked.status_code, 401)
        self.assertEqual(allowed.status_code, 200)

    def test_observability_endpoints_are_operator_protected(self):
        status = {"ok": True, "recent_events": [], "summary": {"pending": 0}}
        with patch.dict(server.os.environ, {"SQX_RELAY_OPERATOR_TOKEN": "operator-token"}, clear=True), \
                patch.object(server, "observability_status", return_value=status):
            blocked = self.client.get("/relay/observability")
            allowed = self.client.get("/relay/observability", headers={"Authorization": "Bearer operator-token"})
        self.assertEqual(blocked.status_code, 401)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(self.get_json(allowed)["summary"]["pending"], 0)

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

    def test_simulated_purchase_flow_writes_observability_snapshot(self):
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
                    patch.object(relay_queue, "log_event", relay_observability.log_event):
                relay_queue.ensure_queue_dirs()
                relay_observability.log_event("test_event", provider_event_id="demo", secret_value="hidden")
                snapshot = relay_observability.write_snapshot(relay_queue.queue_overview(), {"ok": True})
                self.assertTrue(snapshot["ok"])
                self.assertTrue((obs_root / "logs" / "relay_events.jsonl").is_file())
                self.assertTrue((obs_root / "snapshots" / snapshot["snapshot_file"]).is_file())
                events = relay_observability.recent_events()
                self.assertEqual(events[0]["secret_value"], "[redacted]")

    def test_deployment_check_reports_secret_readiness(self):
        env = {
            "SQX_LEMON_WEBHOOK_SECRET": "l" * 40,
            "SQX_FULFILLMENT_RELAY_SECRET": "r" * 40,
            "SQX_RELAY_OPERATOR_TOKEN": "o" * 40,
            "SQX_LOCAL_INGEST_URL": "https://relay-target.example.com/api/fulfillment/relay-ingest",
        }
        with patch.dict(deployment_check.os.environ, env, clear=True):
            report = deployment_check.run_check()
        self.assertTrue(report["files_ready"])
        self.assertTrue(report["docker_ready"])
        self.assertTrue(report["secrets_ready"])
        self.assertTrue(report["production_ready"])

    def test_staging_smoke_builds_signed_remote_checks(self):
        calls = []

        class FakeResponse:
            status = 200

            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, _exc_type, _exc, _tb):
                return False

            def read(self):
                return json.dumps(self.payload).encode("utf-8")

        def fake_urlopen(request, timeout=20):
            calls.append({
                "url": request.full_url,
                "method": request.get_method(),
                "headers": dict(request.header_items()),
            })
            return FakeResponse({"ok": True})

        with patch.object(staging_smoke.urlrequest, "urlopen", side_effect=fake_urlopen):
            report = staging_smoke.run_smoke(
                "https://staging.example.com/",
                "operator-token",
                "lemon-secret",
                send_webhook=True,
                timeout=5,
            )
        self.assertTrue(report["ok"])
        self.assertEqual(len(calls), 5)
        self.assertIn("/relay/health", calls[0]["url"])
        self.assertIn("/relay/webhook/lemon", calls[-1]["url"])
        self.assertEqual(calls[-1]["method"], "POST")
        self.assertIn("X-signature", calls[-1]["headers"])
