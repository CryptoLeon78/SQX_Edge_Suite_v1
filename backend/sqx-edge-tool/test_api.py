import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from api import server
from core.support_incidents import (
    append_support_incident,
    build_support_incident,
    load_support_incidents,
    summarize_support_incidents,
    update_support_incident_status,
)


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

    def test_remote_health_endpoint_redacts_local_paths(self):
        response = self.client.get(
            "/api/health",
            base_url="https://app.sqxedgesuite.org",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertIn("sqx_path_set", data)
        self.assertIn("output_dir_exists", data)
        self.assertNotIn("sqx_path", data)
        self.assertNotIn("output_dir", data)
        self.assertEqual(data["privacy"]["local_paths_returned"], False)

    def test_validate_sqx_path_detects_sqx144_full_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "SQX_144_Full"
            (root / "user" / "data").mkdir(parents=True)
            (root / "user" / "projects").mkdir(parents=True)
            (root / "StrategyQuantX.exe").write_text("", encoding="utf-8")
            (root / "user" / "data" / "data.db").write_text("", encoding="utf-8")

            response = self.client.post("/api/validate-sqx-path", json={"path": str(root)})

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["valid"])
        self.assertEqual(data["version"], "144")
        self.assertEqual(data["sqx_host_profile"], "sqx144_full")
        self.assertTrue(data["checks"]["exe_exists"])

    def test_autodetect_sqx_includes_sqx144_full_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "SQX_144_Full"
            (root / "user" / "data").mkdir(parents=True)
            (root / "user" / "projects").mkdir(parents=True)
            (root / "StrategyQuantX.exe").write_text("", encoding="utf-8")
            (root / "user" / "data" / "data.db").write_text("", encoding="utf-8")
            manifest = {
                "autodetect": {
                    "roots": [str(root)],
                    "driveLetters": [],
                    "versionFolders": [],
                }
            }
            with patch.object(server, "load_manifest", return_value=manifest):
                response = self.client.get("/api/autodetect-sqx")

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertEqual(data["found"], 1)
        self.assertEqual(data["candidates"][0]["version"], "144")
        self.assertEqual(data["candidates"][0]["sqx_host_profile"], "sqx144_full")

    def test_dashboard_api_alias_uses_api_handlers(self):
        response = self.client.get(
            "/dashboard/api/health",
            base_url="https://app.sqxedgesuite.org",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertEqual(data["version"], server.VERSION)
        self.assertNotIn("sqx_path", data)
        self.assertEqual(data["privacy"]["local_paths_returned"], False)

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

    def test_sqx_readiness_manifest_endpoint_is_public_safe(self):
        response = self.client.get("/api/sqx-readiness/manifest")
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertEqual(data["schema"], "sqx-edge.sqx-readiness-manifest-v2")
        self.assertIn("requiredChecklist", data)
        self.assertFalse(data["privacy"]["dataDbCopied"])

    def test_sqx_readiness_report_endpoint_persists_evaluated_status(self):
        captured = []

        def capture(status, workspace_context=None, source=""):
            captured.append((status, workspace_context, source))
            return status

        report = {
            "summary": {
                "sqxRootSelected": True,
                "versionCompatible": True,
                "dataDbFound": True,
                "brokersValidated": True,
                "curatedAssetsValidated": True,
                "snippetsReady": True,
                "viewsReady": True,
            },
            "checks": {
                "portable_source_acknowledged": True,
                "sensitive_files_excluded": True,
            },
        }
        with patch.object(server, "write_readiness_status", side_effect=capture):
            response = self.client.post("/api/sqx-readiness/report", json={"report": report})
        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["complete"])
        self.assertEqual(captured[0][2], "checker_report")

    def test_sqx_readiness_gate_blocks_sensitive_generation_when_remote_incomplete(self):
        incomplete = {
            "ok": True,
            "complete": False,
            "missing": ["data_db_found"],
            "checks": {},
            "source": "not_configured",
        }
        with patch.object(server, "_is_remote_app_request", return_value=True), \
                patch.object(server, "_readiness_workspace_for_request", return_value=(None, None)), \
                patch.object(server, "read_readiness_status", return_value=incomplete):
            response = self.client.post("/api/generate", json={})
        self.assertEqual(response.status_code, 428)
        data = self.get_json(response)
        self.assertEqual(data["error"], "sqx_readiness_required")
        self.assertEqual(data["required_feature"], "project_generator.generate")

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

    def test_support_incident_endpoint_redacts_and_records_case(self):
        captured = []

        def capture(record):
            captured.append(record)
            return {"ok": True, "caseId": record["caseId"], "status": record["status"], "stored": True}

        payload = {
            "category": "generation",
            "severity": "blocker",
            "summary": "Falla en https://privado.example/test con user@example.com",
            "steps": r"Abrir C:\Users\Ivan SQX\Private y pegar Bearer abcdefghijklmnopqrstuvwxyzABCDEFGHIJKL",
            "expected": "Genera .cfx",
            "actual": "__Host-sqx_remote_session=secretvalue no descarga",
            "includeDiagnostic": True,
        }
        with patch.object(server, "append_support_incident", side_effect=capture):
            response = self.client.post("/api/support/incidents", json=payload)

        self.assertEqual(response.status_code, 201)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertRegex(data["caseId"], r"^SQX-SUP-\d{14}-[a-f0-9]{10}$")
        self.assertEqual(data["status"], "open")
        self.assertFalse(data["privacy"]["rawEmailReturned"])
        self.assertEqual(len(captured), 1)
        raw_record = json.dumps(captured[0], ensure_ascii=False)
        self.assertNotIn("user@example.com", raw_record)
        self.assertNotIn("https://privado.example", raw_record)
        self.assertNotIn(r"C:\Users\Ivan SQX", raw_record)
        self.assertNotIn("__Host-sqx_remote_session=secretvalue", raw_record)
        self.assertIn("[REDACTED_EMAIL]", raw_record)
        self.assertIn("[REDACTED_URL]", raw_record)
        self.assertTrue(captured[0]["diagnostic"]["attached"])
        self.assertFalse(captured[0]["privacy"]["tokensStored"])

    def test_support_incident_requires_summary(self):
        response = self.client.post("/api/support/incidents", json={"category": "ui", "severity": "low"})
        self.assertEqual(response.status_code, 400)
        data = self.get_json(response)
        self.assertEqual(data["error"], "support_incident_invalid")
        self.assertIn("summary_required", data["blockers"])

    def test_support_incident_store_and_summary_are_local_redacted(self):
        with tempfile.TemporaryDirectory() as temp:
            cases_path = Path(temp) / "support_cases.local.jsonl"
            record = build_support_incident({
                "category": "access",
                "severity": "high",
                "summary": "Acceso falla para tester@example.com en http://private.local",
            })
            append_support_incident(record, cases_path)
            update = update_support_incident_status(record["caseId"], "resolved", path=cases_path, note="Resuelto sin datos privados.")
            loaded = load_support_incidents(cases_path)
            summary = summarize_support_incidents(cases_path)

        self.assertTrue(update["ok"])
        self.assertEqual(len(loaded), 1)
        self.assertEqual(summary["summary"]["openSupportItems"], 0)
        self.assertFalse(summary["privacy"]["rawEmailReturned"])
        raw_summary = json.dumps(summary, ensure_ascii=False)
        self.assertNotIn("tester@example.com", raw_summary)
        self.assertNotIn("http://private.local", raw_summary)

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

    def test_api_rejects_public_host_without_access_identity_even_from_local_tunnel(self):
        response = self.client.get(
            "/api/health",
            headers={"Host": "app.example.invalid"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.get_json(response)["error"], "local_api_only")

    def test_api_allows_authenticated_cloudflare_access_tunnel_boundary(self):
        response = self.client.get(
            "/api/health",
            headers={
                "Host": "app.example.invalid",
                "Cf-Access-Authenticated-User-Email": "tester@example.invalid",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.get_json(response)["ok"])

    def test_api_rejects_spoofed_access_identity_from_non_local_remote(self):
        response = self.client.get(
            "/api/health",
            headers={
                "Host": "app.example.invalid",
                "Cf-Access-Authenticated-User-Email": "tester@example.invalid",
            },
            environ_base={"REMOTE_ADDR": "192.168.1.50"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.get_json(response)["error"], "local_api_only")

    def test_dashboard_is_served_for_authenticated_cloudflare_access_tunnel(self):
        response = self.client.get(
            "/dashboard",
            headers={
                "Host": "app.example.invalid",
                "X-Forwarded-Proto": "https",
                "Cf-Access-Authenticated-User-Email": "tester@example.invalid",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<title>SQX Edge Suite</title>", response.data)
        self.assertIn(
            b'https://app.example.invalid/assets/brand/sqx-social-preview.png',
            response.data,
        )
        self.assertIn(b'<meta property="og:url" content="https://app.example.invalid/dashboard">', response.data)
        body = response.get_data(as_text=True)
        # Cache-busted protected assets keep the same base paths: href="/dashboard/css/dashboard.css", src="/dashboard/js/main.js".
        self.assertRegex(body, r'href="/dashboard/css/dashboard\.css\?v=\d+"')
        self.assertRegex(body, r'src="/dashboard/js/main\.js\?v=\d+"')
        self.assertRegex(body, r'src="/dashboard/vendor/jszip\.min\.js\?v=\d+"')

        css = self.client.get(
            "/dashboard/css/dashboard.css",
            headers={
                "Host": "app.example.invalid",
                "X-Forwarded-Proto": "https",
                "Cf-Access-Authenticated-User-Email": "tester@example.invalid",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(css.status_code, 200)
        self.assertIn("text/css", css.headers.get("Content-Type", ""))

    def test_root_page_exposes_public_safe_social_metadata(self):
        response = self.client.get(
            "/",
            headers={
                "Host": "app.example.invalid",
                "X-Forwarded-Proto": "https",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        body = response.data.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn("SQX Edge Suite | Plataforma Pro para SQX Traders", body)
        self.assertIn('property="og:image"', body)
        self.assertIn("https://app.example.invalid/assets/brand/sqx-social-preview.png", body)
        self.assertIn('href="https://app.example.invalid/dashboard"', body)
        self.assertIn("Acceso DASHBOARD", body)
        self.assertIn("public", response.headers.get("Cache-Control", ""))
        self.assertIn("max-age=3600", response.headers.get("Cache-Control", ""))
        self.assertEqual(response.headers.get("X-Robots-Tag"), "index, follow")
        self.assertNotIn("remote-welcome-gate", body)
        self.assertNotIn("Cf-Access-Authenticated-User-Email", body)

    def test_link_preview_alias_exposes_public_safe_social_metadata(self):
        response = self.client.get(
            "/link-preview",
            headers={
                "Host": "app.example.invalid",
                "X-Forwarded-Proto": "https",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        body = response.data.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn("SQX Edge Suite | Plataforma Pro para SQX Traders", body)
        self.assertIn('property="og:image"', body)
        self.assertIn("https://app.example.invalid/assets/brand/sqx-social-preview.png", body)
        self.assertIn('href="https://app.example.invalid/dashboard"', body)
        self.assertIn("Acceso DASHBOARD", body)
        self.assertIn("public", response.headers.get("Cache-Control", ""))
        self.assertIn("max-age=3600", response.headers.get("Cache-Control", ""))
        self.assertEqual(response.headers.get("X-Robots-Tag"), "index, follow")
        self.assertNotIn("remote-welcome-gate", body)
        self.assertNotIn("Cf-Access-Authenticated-User-Email", body)

    def test_only_public_link_preview_paths_bypass_access_header_requirement(self):
        root = self.client.get(
            "/",
            headers={"Host": "app.example.invalid", "X-Forwarded-Proto": "https"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(root.status_code, 200)

        dashboard = self.client.get(
            "/dashboard",
            headers={"Host": "app.example.invalid", "X-Forwarded-Proto": "https"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(dashboard.status_code, 403)

        dashboard_css = self.client.get(
            "/dashboard/css/dashboard.css",
            headers={"Host": "app.example.invalid", "X-Forwarded-Proto": "https"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(dashboard_css.status_code, 403)

        image = self.client.get(
            "/assets/brand/sqx-social-preview.png",
            headers={"Host": "app.example.invalid", "X-Forwarded-Proto": "https"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(image.status_code, 200)
        self.assertIn("image/png", image.headers.get("Content-Type", ""))
        self.assertIn("public", image.headers.get("Cache-Control", ""))
        self.assertEqual(image.headers.get("X-Robots-Tag"), "index, follow")

    def test_social_discovery_files_are_public_safe(self):
        for path, expected_content_type in (
            ("/robots.txt", "text/plain"),
            ("/favicon.ico", "image/png"),
            ("/apple-touch-icon.png", "image/png"),
        ):
            with self.subTest(path=path):
                response = self.client.get(
                    path,
                    headers={"Host": "app.example.invalid", "X-Forwarded-Proto": "https"},
                    environ_base={"REMOTE_ADDR": "127.0.0.1"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected_content_type, response.headers.get("Content-Type", ""))
                self.assertIn("public", response.headers.get("Cache-Control", ""))
                self.assertEqual(response.headers.get("X-Robots-Tag"), "index, follow")
                self.assertNotIn(b"Cf-Access-Authenticated-User-Email", response.data)
                self.assertNotIn(b"remote-welcome-gate", response.data)
        robots = self.client.get(
            "/robots.txt",
            headers={"Host": "app.example.invalid", "X-Forwarded-Proto": "https"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertIn(b"Allow: /", robots.data)
        self.assertIn(b"Disallow: /dashboard", robots.data)

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
            generate_pair = self.client.post("/api/generate-pair", json={"asset": "EURUSD", "tf": "H1"})
            generate_all = self.client.post("/api/generate-all", json={"capa": 1})
            clean = self.client.post("/api/sqx-clean", json={"files": ["x.sqx"], "options": {}})

        self.assertEqual(generate.status_code, 402)
        self.assertEqual(generate_custom.status_code, 402)
        self.assertEqual(generate_pair.status_code, 402)
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
        self.assertEqual(gen.call_args.kwargs["target_profile"], {"id": "sq_default_exact"})
        self.assertEqual(self.get_json(response)["target_profile"]["id"], "sq_default_exact")

    def test_generate_custom_accepts_target_profile_remap(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }
        fake_path = str(server.ROOT / "output" / "Custom_EURUSD_H1_Capa1.cfx")
        custom_profile = {
            "id": "custom_user_broker",
            "custom": {
                "brokerPostfix": "_user",
                "symbol": "EURUSD_user",
                "brokerId": "7",
                "sourceId": "8",
                "brokerName": "[[UserBroker]]",
            },
        }
        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", return_value=fake_path) as gen, \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "EURUSD_user",
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
                "target_profile": custom_profile,
            })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertEqual(gen.call_args.kwargs["target_profile"], custom_profile)
        self.assertEqual(data["target_profile"]["id"], "custom_user_broker")
        self.assertEqual(data["target_profile"]["brokerPostfix"], "_user")
        self.assertEqual(data["target_profile"]["symbol"], "EURUSD_user")
        self.assertEqual(data["target_profile"]["brokerId"], 7)
        self.assertEqual(data["target_profile"]["sourceId"], 8)

    def test_generate_pair_creates_capa1_and_capa2_together(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "template_capa2": "templates/Capa2_Base.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }

        def fake_generate(_mining, **kwargs):
            return str(server.ROOT / "output" / f"{kwargs['project_name']}_Capa{kwargs['capa']}.cfx")

        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", side_effect=fake_generate) as gen, \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "EURGBP_darwinex",
                    "spread": 1,
                    "swap_long": -1,
                    "swap_short": 0,
                }):
            response = self.client.post("/api/generate-pair", json={
                "name": "Project EURGBP H1 Basic",
                "asset": "eurgbp",
                "tf": "h1",
                "bs": "BS_Estadistico_v6",
                "dir": "both",
            })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertTrue(data["ok"])
        self.assertEqual(data["asset"], "EURGBP")
        self.assertEqual(data["tf"], "H1")
        self.assertEqual(data["dir"], "both")
        self.assertEqual(data["project_name"], "Project_EURGBP_H1_Basic_LS")
        self.assertEqual([item["name"] for item in data["files"]], [
            "Project_EURGBP_H1_Basic_LS_Capa1.cfx",
            "Project_EURGBP_H1_Basic_LS_Capa2.cfx",
        ])
        self.assertEqual(data["results"]["capa1"]["project_name"], "Project_EURGBP_H1_Basic_LS")
        self.assertEqual(data["results"]["capa2"]["project_name"], "Project_EURGBP_H1_Basic_LS")
        self.assertEqual([call.kwargs["capa"] for call in gen.call_args_list], [1, 2])
        self.assertIsNone(gen.call_args_list[1].kwargs["blocksetting_capa2"])

    def test_generate_pair_reports_partial_failure(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "template_capa2": "templates/Capa2_Base.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }

        def fake_generate(_mining, **kwargs):
            if kwargs["capa"] == 2:
                raise RuntimeError("capa2 boom")
            return str(server.ROOT / "output" / f"{kwargs['project_name']}_Capa1.cfx")

        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", side_effect=fake_generate), \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "EURGBP_darwinex",
                    "spread": 1,
                    "swap_long": -1,
                    "swap_short": 0,
                }):
            response = self.client.post("/api/generate-pair", json={
                "name": "Project EURGBP H1 Basic",
                "asset": "eurgbp",
                "tf": "h1",
                "bs": "BS_Estadistico_v6",
                "dir": "both",
            })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertFalse(data["ok"])
        self.assertEqual(data["ok_count"], 1)
        self.assertEqual(data["fail_count"], 1)
        self.assertTrue(data["results"]["capa1"]["ok"])
        self.assertFalse(data["results"]["capa2"]["ok"])
        self.assertEqual([item["name"] for item in data["files"]], ["Project_EURGBP_H1_Basic_LS_Capa1.cfx"])

    def test_generate_pair_passes_target_profile_to_both_layers(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "template_capa2": "templates/Capa2_Base.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }
        custom_profile = {
            "id": "custom_user_broker",
            "custom": {
                "brokerPostfix": "_user",
                "symbol": "EURGBP_user",
                "brokerId": "7",
                "sourceId": "8",
                "brokerName": "[[UserBroker]]",
            },
        }

        def fake_generate(_mining, **kwargs):
            return str(server.ROOT / "output" / f"{kwargs['project_name']}_Capa{kwargs['capa']}.cfx")

        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", side_effect=fake_generate) as gen, \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "EURGBP_user",
                    "spread": 1,
                    "swap_long": -1,
                    "swap_short": 0,
                }):
            response = self.client.post("/api/generate-pair", json={
                "asset": "eurgbp",
                "tf": "h1",
                "bs": "BS_Estadistico_v6",
                "dir": "long",
                "target_profile": custom_profile,
            })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertEqual([call.kwargs["target_profile"] for call in gen.call_args_list], [custom_profile, custom_profile])
        self.assertEqual(data["target_profile"]["id"], "custom_user_broker")
        self.assertEqual(data["target_profile"]["symbol"], "EURGBP_user")
        self.assertEqual(data["results"]["capa1"]["target_profile"]["brokerId"], 7)
        self.assertEqual(data["results"]["capa2"]["target_profile"]["sourceId"], 8)

    def test_generate_pair_remote_response_uses_workspace_paths(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "template_capa2": "templates/Capa2_Base.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }

        with tempfile.TemporaryDirectory() as tmp:
            workspace_context = {
                "ok": True,
                "workspace": {
                    "id": "ws_1234567890abcdef123456",
                    "version": "remote-workspace-v1",
                    "owner_hash": "ownerhash",
                    "owner_ref": "operator",
                    "entitlement_kind": "tester_free",
                    "feature_scope": "full",
                },
                "_paths": {"outputs": Path(tmp), "logs": Path(tmp) / "logs"},
            }

            def fake_generate(_mining, **kwargs):
                return str(Path(tmp) / f"{kwargs['project_name']}_Capa{kwargs['capa']}.cfx")

            with patch.object(server, "load_config", return_value=cfg), \
                    patch.object(server.os.path, "isfile", return_value=True), \
                    patch.object(server, "_resolve_generation_output", return_value=(tmp, workspace_context, None)), \
                    patch.object(server, "record_workspace_output_generated", return_value={}), \
                    patch.object(server, "generate_project", side_effect=fake_generate), \
                    patch.object(server, "resolve_costs", return_value={
                        "source": "fallback",
                        "symbol": "EURGBP_darwinex",
                        "spread": 1,
                        "swap_long": -1,
                        "swap_short": 0,
                    }):
                response = self.client.post("/api/generate-pair", json={
                    "asset": "eurgbp",
                    "tf": "h1",
                    "bs": "BS_Estadistico_v6",
                    "dir": "short",
                })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        raw = json.dumps(data)
        self.assertFalse(data["privacy"]["local_paths_returned"])
        self.assertEqual(data["results"]["capa1"]["output_path"], "workspace://outputs/Custom_EURGBP_H1_BS_Estadistico_v6_S_Capa1.cfx")
        self.assertEqual(data["results"]["capa2"]["output_path"], "workspace://outputs/Custom_EURGBP_H1_BS_Estadistico_v6_S_Capa2.cfx")
        self.assertEqual([item["path"] for item in data["files"]], [
            "workspace://outputs/Custom_EURGBP_H1_BS_Estadistico_v6_S_Capa1.cfx",
            "workspace://outputs/Custom_EURGBP_H1_BS_Estadistico_v6_S_Capa2.cfx",
        ])
        self.assertIn("workspace://outputs", raw)
        self.assertNotIn(str(Path(tmp)), raw)
        self.assertNotRegex(raw, r"[A-Za-z]:\\\\")

    def test_generate_custom_accepts_project_outside_plan(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }
        fake_path = str(server.ROOT / "output" / "Custom_EURUSD_H1_LS_Capa1.cfx")
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
        self.assertEqual(data["project_name"], "Custom_EURUSD_H1_LS")
        self.assertEqual(data["filename"], "Custom_EURUSD_H1_LS_Capa1.cfx")
        mining = gen.call_args.args[0]
        self.assertEqual(mining.asset, "EURUSD")
        self.assertEqual(mining.tf, "H1")
        self.assertEqual(mining.bs, "BS_Tendencia_v6")
        self.assertEqual(gen.call_args.kwargs["project_name"], "Custom_EURUSD_H1_LS")

    def test_build_custom_mining_forces_direction_suffix_on_typed_names(self):
        base = {
            "name": "Project_EURGBP_H1_BS_Estadistico_v6_estadistico",
            "asset": "eurgbp",
            "tf": "h1",
            "bs": "BS_Estadistico_v6",
            "capa": 2,
        }

        resolved = {
            direction: server.build_custom_mining({**base, "dir": direction})[1]
            for direction in ("long", "short", "both")
        }

        self.assertEqual(resolved["long"], "Project_EURGBP_H1_BS_Estadistico_v6_estadistico_L")
        self.assertEqual(resolved["short"], "Project_EURGBP_H1_BS_Estadistico_v6_estadistico_S")
        self.assertEqual(resolved["both"], "Project_EURGBP_H1_BS_Estadistico_v6_estadistico_LS")
        self.assertEqual(len(set(resolved.values())), 3)

    def test_build_custom_mining_replaces_stale_direction_suffix(self):
        _mining, project_name = server.build_custom_mining({
            "name": "Project_EURGBP_H1_BS_Estadistico_v6_estadistico_L",
            "asset": "eurgbp",
            "tf": "h1",
            "bs": "BS_Estadistico_v6",
            "dir": "short",
            "capa": 2,
        })

        self.assertEqual(project_name, "Project_EURGBP_H1_BS_Estadistico_v6_estadistico_S")

    def test_build_custom_mining_default_name_keeps_direction_suffix(self):
        _mining, project_name = server.build_custom_mining({
            "asset": "eurgbp",
            "tf": "h1",
            "bs": "BS_Custom",
            "dir": "both",
            "capa": 1,
        })

        self.assertEqual(project_name, "Custom_EURGBP_H1_BS_Custom_LS")

    def test_generate_custom_can_request_visual_guide_pdf(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }
        fake_path = str(server.ROOT / "output" / "Custom_EURUSD_H1_LS_Capa1.cfx")
        pdf_result = {
            "ok": True,
            "filename": "Custom_EURUSD_H1_LS_visual_check_guide.pdf",
            "relative_path": "output/pdf/Custom_EURUSD_H1_LS_visual_check_guide.pdf",
            "output_path": "output/pdf/Custom_EURUSD_H1_LS_visual_check_guide.pdf",
            "strict": False,
            "screenshots_pending": True,
            "privacy": {"local_paths_returned": False},
        }
        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", return_value=fake_path), \
                patch.object(server, "render_custom_project_visual_guide_pdf", return_value=pdf_result) as render_pdf, \
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
                "visual_guide_pdf": True,
            })

        self.assertEqual(response.status_code, 200)
        data = self.get_json(response)
        self.assertEqual(data["visual_guide_pdf"]["filename"], "Custom_EURUSD_H1_LS_visual_check_guide.pdf")
        self.assertEqual(data["visual_guide_pdf"]["relative_path"], "output/pdf/Custom_EURUSD_H1_LS_visual_check_guide.pdf")
        self.assertFalse(data["visual_guide_pdf"]["privacy"]["local_paths_returned"])
        self.assertNotIn(str(server.PROJECT_ROOT), json.dumps(data["visual_guide_pdf"]))
        render_pdf.assert_called_once_with("Custom_EURUSD_H1_LS", fake_path)

    def test_generate_custom_visual_guide_pdf_error_redacts_local_paths(self):
        class FailedRun:
            returncode = 1
            stderr = r"failed writing C:\Users\Operator\secret\guide.pdf"
            stdout = ""

        with patch.object(server.subprocess, "run", return_value=FailedRun()):
            result = server.render_custom_project_visual_guide_pdf("Custom EURUSD H1", r"C:\Users\Operator\custom.cfx")

        self.assertFalse(result["ok"])
        self.assertNotIn("C:\\Users", result["error"])
        self.assertIn("[REDACTED_PATH]", result["error"])

    def test_generate_custom_visual_guide_pdf_success_returns_public_relative_path(self):
        class SuccessfulRun:
            returncode = 0
            stderr = ""
            stdout = "PDF generado"

        with patch.object(server.subprocess, "run", return_value=SuccessfulRun()):
            result = server.render_custom_project_visual_guide_pdf("Custom EURUSD H1", r"C:\Users\Operator\custom.cfx")

        self.assertTrue(result["ok"])
        self.assertEqual(result["relative_path"], "output/pdf/Custom_EURUSD_H1_visual_check_guide.pdf")
        self.assertEqual(result["output_path"], "output/pdf/Custom_EURUSD_H1_visual_check_guide.pdf")
        self.assertNotIn("path", result)
        self.assertFalse(result["privacy"]["local_paths_returned"])

    def test_generate_custom_visual_guide_pdf_exception_is_redacted(self):
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
                patch.object(server, "generate_project", return_value=fake_path), \
                patch.object(server, "render_custom_project_visual_guide_pdf", side_effect=RuntimeError(r"C:\Users\Operator\guide.pdf")), \
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
                "capa": 1,
                "visual_guide_pdf": True,
            })

        data = self.get_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data["visual_guide_pdf"]["ok"])
        self.assertNotIn("C:\\Users", data["visual_guide_pdf"]["error"])
        self.assertIn("[REDACTED_PATH]", data["visual_guide_pdf"]["error"])

    def test_generate_custom_ignores_template_family_label(self):
        cfg = {
            "template_capa1": "templates/Capa1_Long.cfx",
            "output_dir": "output",
            "sqx_data_db": "",
            "darwinex_suffix": "_darwinex",
            "asset_aliases": {},
        }
        fake_path = str(server.ROOT / "output" / "Custom_USDJPY_H4_Capa1.cfx")
        with patch.object(server, "load_config", return_value=cfg), \
                patch.object(server.os.path, "isfile", return_value=True), \
                patch.object(server, "generate_project", return_value=fake_path) as gen, \
                patch.object(server, "resolve_costs", return_value={
                    "source": "fallback",
                    "symbol": "USDJPY_darwinex",
                    "spread": 1,
                    "swap_long": -1,
                    "swap_short": 0,
                }):
            response = self.client.post("/api/generate-custom", json={
                "name": "Project_USDJPY_H4_BS_Volatilidad_v6_volatilidad",
                "asset": "usdjpy",
                "tf": "h4",
                "bs": "BS_Volatilidad_v6",
                "dir": "long",
                "capa": 1,
                "template": "VOLATILIDAD",
            })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            gen.call_args.kwargs["template_path"],
            str(server.ROOT / "templates" / "Capa1_Long.cfx"),
        )

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
