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
local_ingest_tunnel_check = _load_module("sqx_edge_relay_local_ingest_tunnel_check_test", "tools/local_ingest_tunnel_check.py")
local_ingest_tunnel_launcher = _load_module("sqx_edge_relay_local_ingest_tunnel_launcher_test", "tools/local_ingest_tunnel_launcher.py")
local_ingest_staging_session = _load_module("sqx_edge_relay_local_ingest_staging_session_test", "tools/local_ingest_staging_session.py")
local_ingest_render_handoff = _load_module("sqx_edge_relay_local_ingest_render_handoff_test", "tools/local_ingest_render_handoff.py")
render_api_preflight = _load_module("sqx_edge_relay_render_api_preflight_test", "tools/render_api_preflight.py")
render_credentials_handshake = _load_module("sqx_edge_relay_render_credentials_handshake_test", "tools/render_credentials_handshake.py")
render_staging_gate = _load_module("sqx_edge_relay_render_staging_gate_test", "tools/render_staging_gate.py")
render_staging_apply_gate = _load_module("sqx_edge_relay_render_staging_apply_gate_test", "tools/render_staging_apply_gate.py")
render_staging_launch_pack = _load_module("sqx_edge_relay_render_staging_launch_pack_test", "tools/render_staging_launch_pack.py")
render_staging_secrets_kit = _load_module("sqx_edge_relay_render_staging_secrets_kit_test", "tools/render_staging_secrets_kit.py")
staging_smoke = _load_module("sqx_edge_relay_staging_smoke_test", "tools/staging_smoke.py")
staging_evidence = _load_module("sqx_edge_relay_staging_evidence_test", "tools/staging_evidence.py")


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

    def test_staging_evidence_marks_no_go_without_remote_url(self):
        preflight = {"files_ready": True, "docker_ready": True, "secrets_ready": True, "config_status": {"warnings": []}}
        with patch.object(staging_evidence.deployment_check, "run_check", return_value=preflight):
            report = staging_evidence.collect_evidence(provider="render")
        self.assertFalse(report["decision"]["go"])
        self.assertIn("remote_staging_url_not_tested", report["decision"]["blockers"])

    def test_staging_evidence_writes_json_and_markdown(self):
        preflight = {"files_ready": True, "docker_ready": True, "secrets_ready": True, "config_status": {"warnings": []}}
        smoke = {"ok": True, "checks": []}
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(staging_evidence.deployment_check, "run_check", return_value=preflight), \
                patch.object(staging_evidence.staging_smoke, "run_smoke", return_value=smoke):
            report = staging_evidence.collect_evidence(provider="render", base_url="https://staging.example.com")
            paths = staging_evidence.write_evidence(report, Path(tmp))
            self.assertTrue(Path(paths["json"]).is_file())
            self.assertTrue(Path(paths["markdown"]).is_file())
            self.assertTrue(report["decision"]["go"])

    def test_render_api_preflight_blocks_without_key(self):
        report = render_api_preflight.run_preflight("", "", render_api_preflight.DEFAULT_BLUEPRINT)
        self.assertFalse(report["ok"])
        self.assertIn("render_api_key_missing", report["blockers"])
        self.assertIn("render_owner_id_missing", report["blockers"])

    def test_render_api_preflight_validates_blueprint_with_api(self):
        responses = [
            {"ok": True, "status": 200, "payload": [{"service": {"name": "existing"}}]},
            {"ok": True, "status": 200, "payload": {"valid": True, "previews": []}},
        ]
        with patch.object(render_api_preflight, "api_request", side_effect=responses) as api_request:
            report = render_api_preflight.run_preflight("render-key", "owner-id", render_api_preflight.DEFAULT_BLUEPRINT)
        self.assertTrue(report["ok"])
        self.assertEqual(api_request.call_count, 2)
        self.assertTrue(report["blueprint_validation"]["payload"]["valid"])

    def test_render_credentials_handshake_blocks_without_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = render_credentials_handshake.collect_handshake(
                "",
                "",
                render_api_preflight.DEFAULT_BLUEPRINT,
                output_dir=Path(tmp),
            )
            self.assertTrue(Path(report["evidence_paths"]["json"]).is_file())
        self.assertFalse(report["decision"]["go"])
        self.assertIn("render_api_key_missing", report["decision"]["blockers"])
        self.assertIn("render_owner_id_missing", report["decision"]["blockers"])
        self.assertIn("render_api_preflight_not_run", report["warnings"])

    def test_render_credentials_handshake_rejects_account_password(self):
        with patch.dict(render_credentials_handshake.os.environ, {"RENDER_ACCOUNT_PASSWORD": "secret"}, clear=False):
            report = render_credentials_handshake.collect_handshake(
                "",
                "",
                render_api_preflight.DEFAULT_BLUEPRINT,
                write=False,
            )
        self.assertIn("render_account_password_present_do_not_use", report["decision"]["blockers"])

    def test_render_credentials_handshake_rejects_placeholders(self):
        fake_module = type("FakePreflight", (), {"run_preflight": staticmethod(lambda _api, _owner, _blueprint: {"ok": True, "blockers": []})})
        with patch.object(render_credentials_handshake, "load_preflight_module", return_value=fake_module):
            report = render_credentials_handshake.collect_handshake(
                "replace-with-render-api-key",
                "replace-with-owner-id",
                render_api_preflight.DEFAULT_BLUEPRINT,
                write=False,
            )
        self.assertFalse(report["decision"]["go"])
        self.assertIn("render_api_key_placeholder", report["decision"]["blockers"])
        self.assertIn("render_owner_id_placeholder", report["decision"]["blockers"])

    def test_render_credentials_handshake_go_with_mocked_preflight(self):
        preflight = {"ok": True, "blockers": [], "warnings": [], "blueprint_validation": {"payload": {"valid": True}}}
        fake_module = type("FakePreflight", (), {"run_preflight": staticmethod(lambda _api, _owner, _blueprint: preflight)})
        with patch.object(render_credentials_handshake, "load_preflight_module", return_value=fake_module):
            report = render_credentials_handshake.collect_handshake(
                "rnd_" + ("k" * 32),
                "owner-123",
                render_api_preflight.DEFAULT_BLUEPRINT,
                write=False,
            )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["credential_policy"], "api_key_only_no_account_password")

    def test_render_staging_gate_blocks_without_go_handshake(self):
        handshake = {"decision": {"go": False, "blockers": ["render_api_key_missing"]}}
        with tempfile.TemporaryDirectory() as tmp:
            handshake_path = Path(tmp) / "render_credential_handshake_demo.json"
            handshake_path.write_text(json.dumps(handshake), encoding="utf-8")
            report = render_staging_gate.collect_gate(handshake_file=handshake_path, output_dir=Path(tmp))
            self.assertTrue(Path(report["evidence_paths"]["json"]).is_file())
        self.assertFalse(report["decision"]["go"])
        self.assertIn("render_credential_handshake_not_go", report["decision"]["blockers"])
        self.assertIn("render_staging_url_missing", report["decision"]["blockers"])

    def test_render_staging_gate_go_with_mocked_remote_evidence(self):
        handshake = {"decision": {"go": True, "blockers": []}}
        staging = {"decision": {"go": True, "blockers": [], "warnings": []}}
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(render_staging_gate.staging_evidence, "collect_evidence", return_value=staging), \
                patch.object(render_staging_gate.staging_evidence, "write_evidence", return_value={"json": "staging.json", "markdown": "staging.md"}):
            handshake_path = Path(tmp) / "render_credential_handshake_demo.json"
            handshake_path.write_text(json.dumps(handshake), encoding="utf-8")
            report = render_staging_gate.collect_gate(
                handshake_file=handshake_path,
                base_url="https://staging.example.com",
                output_dir=Path(tmp),
            )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["staging_evidence"]["evidence_paths"]["json"], "staging.json")

    def test_render_staging_apply_gate_blocks_without_confirmation(self):
        handoff = {
            "decision": {"go": True, "blockers": []},
            "render_env_lines": [
                "SQX_LOCAL_INGEST_URL=https://demo.trycloudflare.com/api/fulfillment/relay-ingest",
                "SQX_RELAY_WORKER_INTERVAL_SECONDS=30",
                "SQX_RELAY_WORKER_LIMIT=10",
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            handoff_path = Path(tmp) / "local_ingest_render_handoff_demo.json"
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
            report = render_staging_apply_gate.collect_apply_gate(
                handoff_file=handoff_path,
                base_url="https://staging.example.com",
                skip_remote_gate=True,
                output_dir=Path(tmp),
            )
        self.assertFalse(report["decision"]["go"])
        self.assertIn("render_env_values_not_confirmed", report["decision"]["blockers"])
        self.assertIn("render_staging_gate_not_run", report["decision"]["blockers"])

    def test_render_staging_apply_gate_go_with_confirmed_gate(self):
        handoff = {
            "decision": {"go": True, "blockers": []},
            "render_env_lines": [
                "SQX_LOCAL_INGEST_URL=https://demo.trycloudflare.com/api/fulfillment/relay-ingest",
                "SQX_RELAY_WORKER_INTERVAL_SECONDS=30",
                "SQX_RELAY_WORKER_LIMIT=10",
            ],
        }
        gate = {"decision": {"go": True, "blockers": [], "warnings": []}}
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(render_staging_apply_gate.render_staging_gate, "collect_gate", return_value=gate):
            handoff_path = Path(tmp) / "local_ingest_render_handoff_demo.json"
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
            report = render_staging_apply_gate.collect_apply_gate(
                handoff_file=handoff_path,
                base_url="https://staging.example.com",
                confirm_env_applied=True,
                output_dir=Path(tmp),
            )
            self.assertTrue(Path(report["evidence_paths"]["json"]).is_file())
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["remote_gate"], gate)

    def test_render_staging_launch_pack_extracts_blueprint_env_keys(self):
        text = "envVars:\n  - key: SQX_LEMON_WEBHOOK_SECRET\n  - key: SQX_LOCAL_INGEST_URL\n"
        self.assertEqual(
            render_staging_launch_pack.extract_env_keys(text),
            ["SQX_LEMON_WEBHOOK_SECRET", "SQX_LOCAL_INGEST_URL"],
        )

    def test_render_staging_launch_pack_writes_no_go_packet(self):
        gate = {"decision": {"go": False, "blockers": ["render_staging_url_missing"], "warnings": []}}
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(render_staging_launch_pack.render_staging_gate, "collect_gate", return_value=gate):
            report = render_staging_launch_pack.collect_launch_pack(
                blueprint_path=render_staging_launch_pack.DEFAULT_BLUEPRINT,
                output_dir=Path(tmp),
            )
            self.assertTrue(Path(report["evidence_paths"]["json"]).is_file())
        self.assertFalse(report["decision"]["go"])
        self.assertIn("render_staging_gate_not_go", report["decision"]["blockers"])
        self.assertIn("SQX_LEMON_WEBHOOK_SECRET", report["required_env_keys"])

    def test_render_staging_secrets_kit_blocks_without_ingest_url(self):
        report = render_staging_secrets_kit.collect_secrets_kit(write=False)
        self.assertFalse(report["decision"]["go"])
        self.assertIn("sqx_local_ingest_url_missing", report["decision"]["blockers"])
        self.assertEqual(len(report["secret_status"]), 3)

    def test_render_staging_secrets_kit_writes_env_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = render_staging_secrets_kit.collect_secrets_kit(
                local_ingest_url="https://sqx-ingest-tunnel.test/api/fulfillment/relay-ingest",
                output_dir=Path(tmp),
            )
            env_path = Path(report["evidence_paths"]["env"])
            env_text = env_path.read_text(encoding="utf-8")
        self.assertTrue(report["decision"]["go"])
        self.assertIn("SQX_LEMON_WEBHOOK_SECRET=", env_text)
        self.assertIn("SQX_FULFILLMENT_RELAY_SECRET=", env_text)
        self.assertIn("SQX_RELAY_OPERATOR_TOKEN=", env_text)

    def test_local_ingest_tunnel_check_blocks_missing_url_and_short_secret(self):
        report = local_ingest_tunnel_check.collect_check("", "short", write=False)
        self.assertFalse(report["decision"]["go"])
        self.assertIn("sqx_local_ingest_url_missing", report["decision"]["blockers"])
        self.assertIn("sqx_fulfillment_relay_secret_too_short", report["decision"]["blockers"])

    def test_local_ingest_tunnel_check_health_only_go(self):
        def fake_request(url, method="GET", body=None, headers=None, timeout=15):
            self.assertIn("/api/health", url)
            return {"ok": True, "status": 200, "payload": {"ok": True}}

        with patch.object(local_ingest_tunnel_check, "request_json", side_effect=fake_request):
            report = local_ingest_tunnel_check.collect_check(
                "https://sqx-ingest-tunnel.test/api/fulfillment/relay-ingest",
                "r" * 40,
                write=False,
            )
        self.assertTrue(report["decision"]["go"])
        self.assertIn("signed_bundle_not_sent", report["decision"]["warnings"])

    def test_local_ingest_tunnel_check_signed_bundle_go(self):
        calls = []

        def fake_request(url, method="GET", body=None, headers=None, timeout=15):
            calls.append({"url": url, "method": method, "headers": headers or {}, "body": body})
            return {"ok": True, "status": 200, "payload": {"ok": True}}

        with patch.object(local_ingest_tunnel_check, "request_json", side_effect=fake_request):
            report = local_ingest_tunnel_check.collect_check(
                "https://sqx-ingest-tunnel.test/api/fulfillment/relay-ingest",
                "r" * 40,
                send_bundle=True,
                write=False,
            )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(calls[1]["method"], "POST")
        self.assertIn("X-SQX-Relay-Signature", calls[1]["headers"])

    def test_local_ingest_tunnel_launcher_parses_public_url(self):
        text = "INF Requesting new quick Tunnel on https://demo.trycloudflare.com"
        self.assertEqual(local_ingest_tunnel_launcher.parse_public_url(text), "https://demo.trycloudflare.com")
        self.assertEqual(
            local_ingest_tunnel_launcher.ingest_url("https://demo.trycloudflare.com"),
            "https://demo.trycloudflare.com/api/fulfillment/relay-ingest",
        )

    def test_local_ingest_tunnel_launcher_dry_run_go_with_provider_and_health(self):
        providers = {
            "cloudflared": {"available": True, "executable": "cloudflared", "recommended": True},
            "ngrok": {"available": False, "executable": "", "recommended": False},
            "localtunnel": {"available": False, "executable": "", "recommended": False},
        }
        with patch.object(local_ingest_tunnel_launcher, "detect_providers", return_value=providers), \
                patch.object(local_ingest_tunnel_launcher, "request_json", return_value={"ok": True, "status": 200, "payload": {"ok": True}}):
            report = local_ingest_tunnel_launcher.collect_launch(write=False)
        self.assertTrue(report["decision"]["go"])
        self.assertIn("tunnel_not_started", report["decision"]["warnings"])
        self.assertEqual(report["command"], ["cloudflared", "tunnel", "--url", "http://127.0.0.1:5050"])

    def test_local_ingest_tunnel_launcher_started_url_go(self):
        providers = {
            "cloudflared": {"available": True, "executable": "cloudflared", "recommended": True},
            "ngrok": {"available": False, "executable": "", "recommended": False},
            "localtunnel": {"available": False, "executable": "", "recommended": False},
        }
        start = {"started": True, "pid": 1234, "returncode": None, "public_url": "https://demo.trycloudflare.com", "output_tail": []}
        with patch.object(local_ingest_tunnel_launcher, "detect_providers", return_value=providers), \
                patch.object(local_ingest_tunnel_launcher, "request_json", return_value={"ok": True, "status": 200, "payload": {"ok": True}}), \
                patch.object(local_ingest_tunnel_launcher, "start_tunnel", return_value=start):
            report = local_ingest_tunnel_launcher.collect_launch(start=True, write=False)
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["ingest_url"], "https://demo.trycloudflare.com/api/fulfillment/relay-ingest")

    def test_local_ingest_staging_session_blocks_when_backend_down(self):
        health = {"ok": False, "status": 0, "payload": {"error": "down"}}
        tunnel = {"provider": "cloudflared", "public_url": "", "ingest_url": "", "decision": {"go": False}}
        with patch.object(local_ingest_staging_session, "wait_for_health", return_value=health), \
                patch.object(local_ingest_staging_session.local_ingest_tunnel_launcher, "collect_launch", return_value=tunnel):
            report = local_ingest_staging_session.collect_session(write=False)
        self.assertFalse(report["decision"]["go"])
        self.assertIn("local_backend_health_failed", report["decision"]["blockers"])

    def test_local_ingest_staging_session_go_with_tunnel_and_check(self):
        health = {"ok": True, "status": 200, "payload": {"ok": True}}
        tunnel = {
            "provider": "cloudflared",
            "public_url": "https://demo.trycloudflare.com",
            "ingest_url": "https://demo.trycloudflare.com/api/fulfillment/relay-ingest",
            "decision": {"go": True, "blockers": [], "warnings": []},
        }
        ingest = {"decision": {"go": True, "blockers": [], "warnings": []}}
        with patch.object(local_ingest_staging_session, "wait_for_health", return_value=health), \
                patch.object(local_ingest_staging_session.local_ingest_tunnel_launcher, "collect_launch", return_value=tunnel), \
                patch.object(local_ingest_staging_session.local_ingest_tunnel_check, "collect_check", return_value=ingest):
            report = local_ingest_staging_session.collect_session(
                relay_secret="r" * 40,
                start_tunnel=True,
                send_bundle=True,
                write=False,
            )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["ingest_check"], ingest)

    def test_local_ingest_render_handoff_blocks_no_go_session(self):
        session = {
            "decision": {"go": False, "blockers": ["local_backend_health_failed"]},
            "tunnel": {"ingest_url": "https://demo.trycloudflare.com/api/fulfillment/relay-ingest"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            session_path = Path(tmp) / "local_ingest_staging_session_demo.json"
            session_path.write_text(json.dumps(session), encoding="utf-8")
            report = local_ingest_render_handoff.collect_handoff(session_file=session_path, output_dir=Path(tmp))
        self.assertFalse(report["decision"]["go"])
        self.assertIn("local_ingest_staging_session_not_go", report["decision"]["blockers"])

    def test_local_ingest_render_handoff_writes_env_from_go_session(self):
        session = {
            "decision": {"go": True, "blockers": []},
            "tunnel": {"ingest_url": "https://demo.trycloudflare.com/api/fulfillment/relay-ingest"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            session_path = Path(tmp) / "local_ingest_staging_session_demo.json"
            session_path.write_text(json.dumps(session), encoding="utf-8")
            report = local_ingest_render_handoff.collect_handoff(session_file=session_path, output_dir=Path(tmp))
            env_text = Path(report["evidence_paths"]["env"]).read_text(encoding="utf-8")
        self.assertTrue(report["decision"]["go"])
        self.assertIn("SQX_LOCAL_INGEST_URL=https://demo.trycloudflare.com/api/fulfillment/relay-ingest", env_text)
