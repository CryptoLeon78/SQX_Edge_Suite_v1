import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from api import server


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

    def get_json(self, response):
        return json.loads(response.data.decode("utf-8"))

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertEqual(data["version"], server.VERSION)
        self.assertIn("license", data)
        self.assertEqual(data["license"]["build_channel"], "internal")
        self.assertIn("config_exists", data)
        self.assertIn("output_dir", data)
        self.assertIn("output_dir_exists", data)

    def test_manifest_endpoint_exposes_shared_config(self):
        response = self.client.get("/api/manifest")
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertIn("tabs", data["ui"])
        self.assertIn("accessLevels", data["product"])
        self.assertIn("minings", data["plan"])
        self.assertIn("assets", data["assets"])
        self.assertIn("strategies", data["strategies"])
        self.assertIn("entries", data["blocksettings"])
        self.assertGreaterEqual(len(data["blocksettings"]["entries"]), 17)

    def test_license_status_and_feature_check_endpoints(self):
        response = self.client.get("/api/license/status")
        self.assertEqual(response.status_code, 200)
        status = self.get_json(response)
        self.assertTrue(status["ok"])
        self.assertEqual(status["state"], "internal")
        self.assertIn("*", status["features"])

        allowed = self.client.post("/api/license/check", json={"feature": "project_generator.generate"})
        self.assertEqual(allowed.status_code, 200)
        allowed_data = self.get_json(allowed)
        self.assertTrue(allowed_data["allowed"])
        self.assertEqual(allowed_data["required_feature"], "project_generator.generate")

        missing = self.client.post("/api/license/check", json={})
        self.assertEqual(missing.status_code, 400)

    def test_license_import_and_clear_endpoints_delegate_to_manager(self):
        imported = {
            "ok": True,
            "installed": True,
            "status": {"ok": True, "state": "pro_active"},
        }
        with patch.object(server, "import_license_payload", return_value=imported) as importer:
            response = self.client.post("/api/license/import", json={"license_id": "LIC-1", "plan": "pro_monthly"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.get_json(response)["installed"])
        importer.assert_called_once()

        rejected = {"ok": False, "installed": False, "error": "invalid_signature"}
        with patch.object(server, "import_license_payload", return_value=rejected):
            bad = self.client.post("/api/license/import", json={"license_id": "LIC-1"})
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(self.get_json(bad)["error"], "invalid_signature")

        with patch.object(server, "clear_license_file", return_value={"ok": True, "removed": True}):
            cleared = self.client.post("/api/license/clear")
        self.assertEqual(cleared.status_code, 200)
        self.assertTrue(self.get_json(cleared)["removed"])

    def test_support_diagnostics_endpoint_redacts_sensitive_values(self):
        sensitive_path = r"C:\Users\Ivan SQX\Private\StrategyQuantX"
        cfg = {
            "sqx_path": sensitive_path,
            "sqx_data_db": sensitive_path + r"\user\data\data.db",
            "sqx_projects_dir": sensitive_path + r"\user\projects",
            "template_capa1": sensitive_path + r"\templates\Capa1.cfx",
            "template_capa2": sensitive_path + r"\templates\Capa2.cfx",
            "output_dir": sensitive_path + r"\output",
            "asset_aliases": {"USTEC": "NDXm"},
            "darwinex_suffix": "_darwinex",
        }
        with patch.object(server, "load_config", return_value=cfg):
            response = self.client.get("/api/support/diagnostics")

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        raw = json.dumps(data, ensure_ascii=False)
        self.assertTrue(data["ok"])
        self.assertTrue(data["privacy"]["safe_to_send"])
        self.assertEqual(data["privacy"]["paths"], "redacted")
        self.assertEqual(data["privacy"]["license_payload"], "excluded")
        self.assertEqual(data["privacy"]["strategy_files"], "excluded")
        self.assertEqual(data["config"]["asset_aliases_count"], 1)
        self.assertTrue(data["config"]["path_values"]["sqx_path"]["redacted"])
        self.assertNotIn(sensitive_path, raw)
        self.assertNotIn("Private", raw)
        self.assertNotIn("NDXm", raw)
        self.assertRegex(data["filename"], r"^SQX_support_diagnostic_[a-f0-9]{12}\.json$")

    def test_fulfillment_receiver_requires_secret(self):
        with patch.dict(server.os.environ, {}, clear=True):
            response = self.client.post("/api/fulfillment/webhook/lemon", data=b"{}")
        self.assertEqual(response.status_code, 503)
        data = self.get_json(response)
        self.assertEqual(data["error"], "webhook_secret_missing")

    def test_fulfillment_receiver_accepts_signed_event(self):
        stored = {
            "ok": True,
            "stored": True,
            "duplicate": False,
            "provider_event_id": "wh_123",
            "request": {"request_file": "fulfillment_request_1.json"},
        }
        with patch.dict(server.os.environ, {"SQX_LEMON_WEBHOOK_SECRET": "secret"}, clear=False), \
                patch.object(server, "store_lemon_webhook", return_value=stored) as store:
            response = self.client.post(
                "/api/fulfillment/webhook/lemon",
                data=b'{"ok":true}',
                headers={"X-Signature": "abc123"},
            )
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["stored"])
        store.assert_called_once_with(b'{"ok":true}', "abc123", "secret")

    def test_fulfillment_relay_ingest_requires_secret(self):
        with patch.dict(server.os.environ, {}, clear=True):
            response = self.client.post("/api/fulfillment/relay-ingest", data=b"{}")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.get_json(response)["error"], "relay_secret_missing")

    def test_fulfillment_relay_ingest_accepts_signed_bundle(self):
        stored = {
            "ok": True,
            "stored": True,
            "duplicate": False,
            "provider_event_id": "wh_456",
            "relay_event_id": "relay_456",
            "request": {"request_file": "fulfillment_request_2.json"},
        }
        with patch.dict(server.os.environ, {"SQX_FULFILLMENT_RELAY_SECRET": "relay-secret"}, clear=False), \
                patch.object(server, "store_relay_bundle", return_value=stored) as store:
            response = self.client.post(
                "/api/fulfillment/relay-ingest",
                data=b'{"relay":true}',
                headers={"X-SQX-Relay-Signature": "sig123"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_json(response)["relay_event_id"], "relay_456")
        store.assert_called_once_with(b'{"relay":true}', "sig123", "relay-secret")

    def test_fulfillment_queue_endpoints(self):
        queued = [{
            "name": "fulfillment_request_20260506_1.json",
            "provider_event_id": "wh_123",
            "order_id": "LS-001",
            "plan": "pro_monthly",
            "eligible_for_fulfillment": True,
            "operator_status": "queued",
            "attempt_count": 0,
        }]
        processed = [{
            "name": "delivery_receipt_20260506_1.json",
            "request_file": "fulfillment_request_20260506_1.json",
            "status": "completed",
        }]
        overview = {
            "requests": queued,
            "processed": processed,
            "summary": {
                "queued": 1,
                "processing": 0,
                "needs_review": 0,
                "failed": 0,
                "completed": 0,
                "ignored": 0,
                "processed_receipts": 1,
                "total_requests": 1,
            },
        }
        detail = {
            "request_file": "fulfillment_request_20260506_1.json",
            "provider_event_id": "wh_123",
            "plan": "pro_monthly",
        }
        done = {"ok": True, "receipt_file": "delivery_receipt_20260506_1.json"}

        with patch.object(server, "fulfillment_queue_overview", return_value=overview), \
                patch.dict(server.os.environ, {"SQX_LEMON_WEBHOOK_SECRET": "secret", "SQX_FULFILLMENT_RELAY_SECRET": "relay-secret"}, clear=False):
            listed = self.client.get("/api/fulfillment/requests")
        self.assertEqual(listed.status_code, 200)
        listed_data = self.get_json(listed)
        self.assertEqual(len(listed_data["requests"]), 1)
        self.assertEqual(len(listed_data["processed"]), 1)
        self.assertEqual(listed_data["summary"]["queued"], 1)
        self.assertTrue(listed_data["receiver"]["secret_configured"])
        self.assertTrue(listed_data["receiver"]["relay_secret_configured"])

        with patch.object(server, "load_fulfillment_request", return_value=detail):
            got = self.client.get("/api/fulfillment/requests/fulfillment_request_20260506_1.json")
        self.assertEqual(got.status_code, 200)
        self.assertEqual(self.get_json(got)["request"]["plan"], "pro_monthly")

        with patch.object(server, "load_fulfillment_request", side_effect=FileNotFoundError):
            missing = self.client.get("/api/fulfillment/requests/fulfillment_request_missing.json")
        self.assertEqual(missing.status_code, 404)

        with patch.object(server, "process_fulfillment_request", return_value=done) as process:
            processed_response = self.client.post(
                "/api/fulfillment/process",
                json={
                    "request_file": "fulfillment_request_20260506_1.json",
                    "private_key": "C:/private/key.json",
                    "zip_path": "C:/dist/SQX.zip",
                    "support_email": "support@example.com",
                },
            )
        self.assertEqual(processed_response.status_code, 200)
        self.assertTrue(self.get_json(processed_response)["ok"])
        process.assert_called_once()

    def test_fulfillment_operator_status_endpoint(self):
        updated = {
            "ok": True,
            "summary": {
                "name": "fulfillment_request_20260506_1.json",
                "operator_status": "ignored",
            },
        }
        with patch.object(server, "set_fulfillment_request_status", return_value=updated) as setter:
            response = self.client.post(
                "/api/fulfillment/request-status",
                json={
                    "request_file": "fulfillment_request_20260506_1.json",
                    "operator_status": "ignored",
                    "note": "manual skip",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_json(response)["summary"]["operator_status"], "ignored")
        setter.assert_called_once()

        with patch.object(server, "set_fulfillment_request_status", side_effect=ValueError("bad status")):
            invalid = self.client.post(
                "/api/fulfillment/request-status",
                json={"request_file": "fulfillment_request_20260506_1.json", "operator_status": "bad"},
            )
        self.assertEqual(invalid.status_code, 400)

    def test_customer_cockpit_endpoint_returns_redacted_summary(self):
        overview = {
            "ok": True,
            "state": "customer_cockpit_ready",
            "privacy": {
                "mode": "redacted_operator_summary",
                "safe_to_render": True,
                "excluded": ["license payloads", "private keys", "raw checkout events"],
            },
            "summary": {"customers": 1, "renewal_due": 1, "support_open": 0},
            "customers": [{"customer_ref": "iv***@example.com", "plan": "pro_monthly"}],
        }
        with patch.object(server, "customer_cockpit_overview", return_value=overview) as cockpit:
            response = self.client.get("/api/customer-cockpit")

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertEqual(data["state"], "customer_cockpit_ready")
        self.assertEqual(data["customers"][0]["customer_ref"], "iv***@example.com")
        self.assertIn("license payloads", data["privacy"]["excluded"])
        self.assertNotIn("ivan@example.com", json.dumps(data, ensure_ascii=False))
        cockpit.assert_called_once()

    def test_minings_follow_plan_manifest(self):
        response = self.client.get("/api/minings")
        self.assertEqual(response.status_code, 200)
        minings = self.get_json(response)
        plan = json.loads((server.ROOT / "config" / "plan.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(len(minings), len(plan["minings"]))
        self.assertEqual(minings[0]["num"], plan["minings"][0]["num"])

    def test_cors_allows_only_local_origins(self):
        evil = self.client.get("/api/health", headers={"Origin": "https://example.com"})
        self.assertIsNone(evil.headers.get("Access-Control-Allow-Origin"))
        self.assertIsNone(evil.headers.get("Access-Control-Allow-Credentials"))
        self.assertEqual(evil.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(evil.headers.get("Cache-Control"), "no-store")

        file_origin = self.client.get("/api/health", headers={"Origin": "null"})
        self.assertEqual(file_origin.headers.get("Access-Control-Allow-Origin"), "null")
        self.assertEqual(file_origin.headers.get("Access-Control-Allow-Credentials"), "true")

        local_origin = self.client.get("/api/health", headers={"Origin": "http://localhost:3000"})
        self.assertEqual(local_origin.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000")
        self.assertEqual(local_origin.headers.get("Access-Control-Allow-Credentials"), "true")

    def test_api_rejects_non_local_boundary(self):
        response = self.client.get(
            "/api/health",
            headers={"Host": "192.168.1.20:5050"},
            environ_base={"REMOTE_ADDR": "192.168.1.50"},
        )
        self.assertEqual(response.status_code, 403)
        data = self.get_json(response)
        self.assertEqual(data["error"], "local_api_only")

    def test_pro_write_endpoints_are_feature_gated(self):
        denied = {
            "ok": False,
            "allowed": False,
            "error": "pro_required",
            "message": "Esta funcion requiere SQX Edge Pro.",
        }
        with patch.object(server, "check_feature", return_value=denied):
            generate = self.client.post("/api/generate", json={"mining": 1, "capa": 1})
            generate_custom = self.client.post("/api/generate-custom", json={"asset": "EURUSD", "tf": "H1", "capa": 1})
            generate_all = self.client.post("/api/generate-all", json={"capa": 1})
            clean = self.client.post("/api/sqx-clean", json={"files": ["x.sqx"], "options": {}})

        self.assertEqual(generate.status_code, 402)
        self.assertEqual(generate_custom.status_code, 402)
        self.assertEqual(generate_all.status_code, 402)
        self.assertEqual(clean.status_code, 402)
        self.assertEqual(self.get_json(generate)["error"], "pro_required")

    def test_sqx_list_rejects_paths_outside_allowed_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = self.client.post("/api/sqx-list", json={"dir": tmp, "recursive": True})
        self.assertEqual(response.status_code, 403)
        data = self.get_json(response)
        self.assertFalse(data["ok"])
        self.assertIn("allowed_roots", data)

    def test_sqx_clean_creates_backup_for_allowed_file(self):
        with tempfile.TemporaryDirectory(dir=server.ROOT) as tmp:
            sqx_path = Path(tmp) / "Strategy 1.1.1.sqx"
            param = '<Param key="#ExitAfterBars.ExitAfterBars#" exitMethod="true">12</Param>'
            with zipfile.ZipFile(sqx_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("settings.xml", f"<Root>{param}</Root>")
                zf.writestr("lastSettings.xml", "<Root></Root>")
                zf.writestr("strategy_Portfolio.xml", "<Root></Root>")

            response = self.client.post(
                "/api/sqx-clean",
                json={"files": [str(sqx_path)], "options": {"remove_exit_bars": True}},
            )

            self.assertEqual(response.status_code, 200)
            data = self.get_json(response)
            self.assertTrue(data["ok"])
            result = data["results"][0]
            self.assertIn("backup_path", result)
            self.assertTrue(Path(result["backup_path"]).is_file())

            with zipfile.ZipFile(sqx_path, "r") as zf:
                content = zf.read("settings.xml").decode("utf-8")
            self.assertIn(">0</Param>", content)

    def test_symbol_endpoints_when_db_configured(self):
        cfg = server.load_config()
        db_path = cfg.get("sqx_data_db")
        if not db_path or not Path(db_path).is_file():
            self.skipTest("SQX data.db no configurado en este entorno")

        for path in (
            "/api/symbol-info/USTEC",
            "/api/symbol-info/XAUUSD",
            "/api/suggest-instruments/USTEC",
            "/api/instruments",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(self.get_json(response)["ok"])

    def test_generate_passes_configured_aliases(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {"USTEC": "NDXm"},
        }

        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", return_value=str(server.ROOT / "output" / "fake.cfx")) as gen, \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "USTEC_darwinex",
                    "spread": 0,
                    "swap_long": 0,
                    "swap_short": 0,
                }):
            response = self.client.post("/api/generate", json={"mining": 10, "capa": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(gen.call_args.kwargs["alias_override"], {"USTEC": "NDXm"})

    def test_generate_custom_accepts_project_outside_plan(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }
        fake_path = str(server.ROOT / "output" / "Custom_EURUSD_H1_Capa1.cfx")
        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", return_value=fake_path) as gen, \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "EURUSD_darwinex",
                    "spread": 1,
                    "swap_long": -1,
                    "swap_short": 0,
                }):
            response = self.client.post("/api/generate-custom", json={
                "name": "Custom EURUSD H1",
                "asset": "eurusd",
                "tf": "h1",
                "bs": "BS_Tendencia_v6",
                "dir": "both",
                "capa": 1,
            })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["custom"])
        self.assertEqual(data["asset"], "EURUSD")
        self.assertEqual(data["tf"], "H1")
        self.assertEqual(data["dir"], "both")
        self.assertEqual(data["project_name"], "Custom_EURUSD_H1")
        mining = gen.call_args.args[0]
        self.assertEqual(mining.asset, "EURUSD")
        self.assertEqual(mining.tf, "H1")
        self.assertEqual(mining.bs, "BS_Tendencia_v6")
        self.assertEqual(gen.call_args.kwargs["project_name"], "Custom_EURUSD_H1")

    def test_generate_custom_requires_asset_and_timeframe(self):
        response = self.client.post("/api/generate-custom", json={"asset": "EURUSD", "capa": 1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.get_json(response)["error"], "missing 'tf'")

    def test_state_backup_roundtrip_uses_safe_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            backup_dir = Path(tmp)
            with patch.object(server, "STATE_BACKUP_DIR", backup_dir):
                response = self.client.post(
                    "/api/state/backup",
                    json={"sqx_priority_progress_v1": {"EURUSD|tendencia": "current"}},
                )
                self.assertEqual(response.status_code, 200)
                created = self.get_json(response)
                self.assertTrue(created["ok"])
                self.assertTrue(created["filename"].startswith("state_backup_"))

                listed = self.get_json(self.client.get("/api/state/backups"))
                self.assertEqual(len(listed["backups"]), 1)

                restored = self.client.get(f"/api/state/restore/{created['filename']}")
                self.assertEqual(restored.status_code, 200)
                payload = self.get_json(restored)["payload"]
                self.assertIn("_meta", payload)
                self.assertEqual(
                    payload["data"]["sqx_priority_progress_v1"]["EURUSD|tendencia"],
                    "current",
                )

                rejected = self.client.get("/api/state/restore/../config.json")
                self.assertEqual(rejected.status_code, 404)


if __name__ == "__main__":
    unittest.main()
