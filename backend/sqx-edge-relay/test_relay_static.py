import unittest
from pathlib import Path


RELAY_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = RELAY_ROOT.parents[1]
PRODUCT_MANIFEST = PROJECT_ROOT / "backend" / "sqx-edge-tool" / "config" / "product_manifest.json"


class RelayStaticTestCase(unittest.TestCase):
    def test_relay_project_files_exist(self):
        expected = [
            RELAY_ROOT / ".env.example",
            RELAY_ROOT / ".dockerignore",
            RELAY_ROOT / "Dockerfile",
            RELAY_ROOT / ".env.staging.example",
            RELAY_ROOT / "README.md",
            RELAY_ROOT / "requirements.txt",
            RELAY_ROOT / "run-web.bat",
            RELAY_ROOT / "run-worker.bat",
            RELAY_ROOT / "api" / "__init__.py",
            RELAY_ROOT / "api" / "server.py",
            RELAY_ROOT / "core" / "__init__.py",
            RELAY_ROOT / "core" / "relay_queue.py",
            RELAY_ROOT / "core" / "relay_observability.py",
            RELAY_ROOT / "core" / "relay_settings.py",
            RELAY_ROOT / "tools" / "__init__.py",
            RELAY_ROOT / "tools" / "deployment_check.py",
            RELAY_ROOT / "tools" / "render_api_preflight.py",
            RELAY_ROOT / "tools" / "simulate_purchase_flow.py",
            RELAY_ROOT / "tools" / "staging_evidence.py",
            RELAY_ROOT / "tools" / "staging_smoke.py",
            RELAY_ROOT / "worker" / "__init__.py",
            RELAY_ROOT / "worker" / "dispatch_worker.py",
            RELAY_ROOT / "deploy" / "docker-compose.yml",
            RELAY_ROOT / "deploy" / "render.yaml.example",
            RELAY_ROOT / "deploy" / "render.staging.yaml.example",
            RELAY_ROOT / "deploy" / "railway.json",
            RELAY_ROOT / "deploy" / "fly.toml.example",
            RELAY_ROOT / "deploy" / "systemd" / "sqx-edge-relay.service",
            RELAY_ROOT / "deploy" / "systemd" / "sqx-edge-relay-worker.service",
        ]
        for path in expected:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), path)

    def test_relay_docs_and_endpoints_are_described(self):
        readme = (RELAY_ROOT / "README.md").read_text(encoding="utf-8-sig")
        server = (RELAY_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        queue = (RELAY_ROOT / "core" / "relay_queue.py").read_text(encoding="utf-8-sig")
        observability = (RELAY_ROOT / "core" / "relay_observability.py").read_text(encoding="utf-8-sig")
        settings = (RELAY_ROOT / "core" / "relay_settings.py").read_text(encoding="utf-8-sig")
        deployment_check = (RELAY_ROOT / "tools" / "deployment_check.py").read_text(encoding="utf-8-sig")
        render_api_preflight = (RELAY_ROOT / "tools" / "render_api_preflight.py").read_text(encoding="utf-8-sig")
        simulation = (RELAY_ROOT / "tools" / "simulate_purchase_flow.py").read_text(encoding="utf-8-sig")
        staging_evidence = (RELAY_ROOT / "tools" / "staging_evidence.py").read_text(encoding="utf-8-sig")
        staging_smoke = (RELAY_ROOT / "tools" / "staging_smoke.py").read_text(encoding="utf-8-sig")
        worker = (RELAY_ROOT / "worker" / "dispatch_worker.py").read_text(encoding="utf-8-sig")
        dockerfile = (RELAY_ROOT / "Dockerfile").read_text(encoding="utf-8-sig")

        for pattern in (
            "/relay/health",
            "/relay/config-check",
            "/relay/observability",
            "/relay/observability/snapshot",
            "/relay/webhook/lemon",
            "/relay/queue",
            "/relay/dispatch",
            "/relay/requeue",
            "SQX_FULFILLMENT_RELAY_SECRET",
            "SQX_RELAY_OPERATOR_TOKEN",
            "SQX_LOCAL_INGEST_URL",
            "SQX_RELAY_WORKER_INTERVAL_SECONDS",
            "deployment_check.py",
            "render_api_preflight.py",
            "staging_evidence.py",
            "staging_smoke.py",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, readme + server + settings)

        self.assertIn("enqueue_lemon_webhook", queue)
        self.assertIn("dispatch_queue_item", queue)
        self.assertIn("log_event", queue)
        self.assertIn("write_snapshot", observability)
        self.assertIn("relay_events.jsonl", observability)
        self.assertIn("production_ready", deployment_check)
        self.assertIn("--strict", deployment_check)
        self.assertIn("RENDER_API_KEY", render_api_preflight)
        self.assertIn("/blueprints/validate", render_api_preflight)
        self.assertIn("multipart/form-data", render_api_preflight)
        self.assertIn("dispatch_queue_item", simulation)
        self.assertIn("SQX_RELAY_STAGING_BASE_URL", staging_smoke)
        self.assertIn("--send-webhook", staging_smoke)
        self.assertIn("wh_m20_staging_demo", staging_smoke)
        self.assertIn("relay_staging_", staging_evidence)
        self.assertIn("NO-GO", staging_evidence)
        self.assertIn("dispatch_due_items", worker)
        self.assertIn("gunicorn api.server:app", dockerfile)
        self.assertIn("backend/sqx-edge-tool/core/fulfillment_normalizer.py", dockerfile)
        self.assertIn("--once", worker)
        self.assertIn("exponential", "exponential backoff remote queue")


if __name__ == "__main__":
    unittest.main()
