import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
PACKAGING_ROOT = PROJECT_ROOT / "packaging"


class EmbeddedPackagingTestCase(unittest.TestCase):
    def test_embedded_launchers_and_tools_exist(self):
        expected = [
            PROJECT_ROOT / "START_SQX_EDGE.bat",
            PROJECT_ROOT / "STOP_SQX_EDGE.bat",
            PROJECT_ROOT / "RELEASE_SQX_EDGE.bat",
            PACKAGING_ROOT / "START_SQX_EDGE.bat",
            PACKAGING_ROOT / "STOP_SQX_EDGE.bat",
            TOOL_ROOT / "run-embedded.bat",
            TOOL_ROOT / "run-web-embedded.bat",
            TOOL_ROOT / "tools" / "bootstrap_embedded_python.ps1",
            TOOL_ROOT / "tools" / "audit_distribution.ps1",
            TOOL_ROOT / "tools" / "package_portable.ps1",
            TOOL_ROOT / "tools" / "release_checklist.ps1",
            TOOL_ROOT / "tools" / "license_keypair.ps1",
            TOOL_ROOT / "tools" / "license_issue.py",
            TOOL_ROOT / "tools" / "prepare_customer_delivery.ps1",
            TOOL_ROOT / "tools" / "checkout_live_readiness.py",
            TOOL_ROOT / "tools" / "commercial_release_candidate.py",
            TOOL_ROOT / "tools" / "pilot_purchase_kit.py",
            TOOL_ROOT / "tools" / "limited_public_launch.py",
            TOOL_ROOT / "tools" / "post_launch_control.py",
            TOOL_ROOT / "tools" / "commercial_feedback_loop.py",
            TOOL_ROOT / "tools" / "public_offer_pack.py",
            TOOL_ROOT / "tools" / "launch_assets_kit.py",
            TOOL_ROOT / "tools" / "public_release_gate.py",
            TOOL_ROOT / "tools" / "release_publication_record.py",
            TOOL_ROOT / "tools" / "post_release_monitor.py",
            TOOL_ROOT / "tools" / "hotfix_rollback_release.py",
            TOOL_ROOT / "tools" / "fulfillment_request.py",
            TOOL_ROOT / "tools" / "fulfill_from_request.ps1",
            TOOL_ROOT / "tools" / "relay_bundle.py",
        ]
        for path in expected:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), path)

    def test_launchers_use_project_local_runtime(self):
        for name in ("run-embedded.bat", "run-web-embedded.bat"):
            text = (TOOL_ROOT / name).read_text(encoding="utf-8-sig")
            with self.subTest(name=name):
                self.assertIn("runtime\\python\\python.exe", text)
                self.assertIn("bootstrap_embedded_python.ps1", text)

    def test_one_click_launcher_opens_embedded_stack(self):
        text = (PROJECT_ROOT / "START_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("packaging\\START_SQX_EDGE.bat", text)
        text = (PACKAGING_ROOT / "START_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("run-web-embedded.bat", text)
        self.assertIn("app\\SQX_Dashboard_v6.html", text)
        self.assertIn("http://127.0.0.1:5050/api/health", text)

    def test_portable_package_includes_embedded_runtime(self):
        text = (TOOL_ROOT / "tools" / "package_portable.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('"runtime\\python\\python.exe"', text)
        self.assertNotIn('"runtime"', text)
        self.assertIn('"\\\\backend\\\\sqx-edge-tool\\\\runtime\\\\downloads\\\\",', text)
        self.assertIn('"node_modules"', text)
        self.assertIn("RELEASE_SQX_EDGE", text)
        self.assertIn("license\\.json", text)
        self.assertIn("license_signer\\.py", text)
        self.assertIn("license_keypair\\.ps1", text)
        self.assertIn("license_issue\\.py", text)
        self.assertIn("prepare_customer_delivery\\.ps1", text)
        self.assertIn("checkout_live_readiness\\.py", text)
        self.assertIn("commercial_release_candidate\\.py", text)
        self.assertIn("pilot_purchase_kit\\.py", text)
        self.assertIn("limited_public_launch\\.py", text)
        self.assertIn("post_launch_control\\.py", text)
        self.assertIn("commercial_feedback_loop\\.py", text)
        self.assertIn("public_offer_pack\\.py", text)
        self.assertIn("launch_assets_kit\\.py", text)
        self.assertIn("public_release_gate\\.py", text)
        self.assertIn("release_publication_record\\.py", text)
        self.assertIn("post_release_monitor\\.py", text)
        self.assertIn("hotfix_rollback_release\\.py", text)
        self.assertIn("fulfillment_request\\.py", text)
        self.assertIn("fulfill_from_request\\.ps1", text)
        self.assertIn("relay_bundle\\.py", text)
        self.assertIn('"sqx-edge-relay"', text)
        self.assertIn("_private_key\\.json", text)
        self.assertIn("license_signed_", text)
        self.assertIn("license_payload_", text)
        self.assertIn("fulfillment_request_", text)
        self.assertIn("webhook_event_", text)
        self.assertIn("relay_event_", text)
        self.assertIn('"fulfillment_requests"', text)
        self.assertIn('"license_keys"', text)
        self.assertIn("\\\\.env", text)

    def test_release_checklist_validates_portable_user_flow(self):
        text = (TOOL_ROOT / "tools" / "release_checklist.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("module_contracts.mjs", text)
        self.assertIn("-m pytest", text)
        self.assertIn("package_portable.ps1", text)
        self.assertIn("audit_distribution.ps1", text)
        self.assertIn("Distribution audit", text)
        self.assertIn("Get-FileHash", text)
        self.assertIn("ZIP SHA256", text)
        self.assertIn("START_SQX_EDGE.bat", text)
        self.assertIn("project-generator-dom.js", text)
        self.assertIn("RELEASE_SQX_EDGE.bat", text)
        self.assertIn("license_signer.py", text)
        self.assertIn("license_keypair.ps1", text)
        self.assertIn("license_issue.py", text)
        self.assertIn("prepare_customer_delivery.ps1", text)
        self.assertIn("checkout_live_readiness.py", text)
        self.assertIn("commercial_release_candidate.py", text)
        self.assertIn("pilot_purchase_kit.py", text)
        self.assertIn("limited_public_launch.py", text)
        self.assertIn("post_launch_control.py", text)
        self.assertIn("commercial_feedback_loop.py", text)
        self.assertIn("public_offer_pack.py", text)
        self.assertIn("launch_assets_kit.py", text)
        self.assertIn("public_release_gate.py", text)
        self.assertIn("release_publication_record.py", text)
        self.assertIn("post_release_monitor.py", text)
        self.assertIn("hotfix_rollback_release.py", text)
        self.assertIn("fulfillment_request.py", text)
        self.assertIn("fulfill_from_request.ps1", text)
        self.assertIn("relay_bundle.py", text)
        self.assertIn("sqx-edge-relay", text)
        self.assertIn("fulfillment_requests", text)
        self.assertIn("license_keys", text)
        self.assertIn("private_keys", text)
        self.assertIn("/api/health", text)
        self.assertIn("runtime\\python\\python.exe", text)
        self.assertIn("RequireCleanGit", text)
        self.assertIn("SQX_release_summary.txt", text)
        self.assertIn("Clean Git working tree", text)

    def test_distribution_audit_guards_sensitive_release_content(self):
        text = (TOOL_ROOT / "tools" / "audit_distribution.ps1").read_text(encoding="utf-8-sig")
        for pattern in (
            "config.json",
            "license.json",
            "license_signer.py",
            "license_keypair.ps1",
            "license_issue.py",
            "prepare_customer_delivery.ps1",
            "checkout_live_readiness.py",
            "commercial_release_candidate.py",
            "pilot_purchase_kit.py",
            "limited_public_launch.py",
            "post_launch_control.py",
            "commercial_feedback_loop.py",
            "public_offer_pack.py",
            "launch_assets_kit.py",
            "public_release_gate.py",
            "release_publication_record.py",
            "post_release_monitor.py",
            "hotfix_rollback_release.py",
            "fulfillment_request.py",
            "fulfill_from_request.ps1",
            "relay_bundle.py",
            "sqx-edge-relay",
            "license_keys",
            "private_keys",
            "_private_key\\.json",
            "license_signed_",
            "license_payload_",
            "fulfillment_request_",
            "webhook_event_",
            "relay_event_",
            ".env",
            ".git",
            "node_modules",
            "backups",
            "Get-FileHash",
            "SQX_distribution_audit.txt",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_release_bat_runs_strict_checklist(self):
        text = (PROJECT_ROOT / "RELEASE_SQX_EDGE.bat").read_text(encoding="utf-8-sig")
        self.assertIn("release_checklist.ps1", text)
        self.assertIn("-RequireCleanGit", text)
        self.assertIn("pause", text.lower())

    def test_roadmap_marks_f7_done(self):
        readme = (TOOL_ROOT / "README.md").read_text(encoding="utf-8-sig")
        self.assertIn("[x] **F7**", readme)


if __name__ == "__main__":
    unittest.main()
