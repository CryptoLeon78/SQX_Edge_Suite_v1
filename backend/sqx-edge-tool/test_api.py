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
        self.assertEqual(evil.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(evil.headers.get("Cache-Control"), "no-store")

        file_origin = self.client.get("/api/health", headers={"Origin": "null"})
        self.assertEqual(file_origin.headers.get("Access-Control-Allow-Origin"), "null")

        local_origin = self.client.get("/api/health", headers={"Origin": "http://localhost:3000"})
        self.assertEqual(local_origin.headers.get("Access-Control-Allow-Origin"), "http://localhost:3000")

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
            generate_all = self.client.post("/api/generate-all", json={"capa": 1})
            clean = self.client.post("/api/sqx-clean", json={"files": ["x.sqx"], "options": {}})

        self.assertEqual(generate.status_code, 402)
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
