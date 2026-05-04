import json
import py_compile
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
ANALYSIS_ROOT = PROJECT_ROOT / "analysis"


class DashboardStaticTestCase(unittest.TestCase):
    def setUp(self):
        self.html_path = APP_ROOT / "SQX_Dashboard_v6.html"
        self.html = self.html_path.read_text(encoding="utf-8-sig")

    def test_script_files_exist_in_expected_order(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        self.assertEqual(
            scripts,
            [
                "js/historical-data.js",
                "js/scores-data.js",
                "js/manifest-data.js",
                "js/app-config.js",
                "js/data.js",
                "js/dashboard.js",
                "js/main.js",
            ],
        )
        for script in scripts:
            self.assertTrue((APP_ROOT / script).is_file(), script)

    def test_tabs_have_matching_panels(self):
        ui_manifest = json.loads((TOOL_ROOT / "config" / "ui_manifest.json").read_text(encoding="utf-8-sig"))
        tabs = [tab["id"] for tab in ui_manifest["tabs"]]
        panels = re.findall(r'id="tab-([^"]+)"', self.html)

        self.assertEqual(len(tabs), 9)
        self.assertEqual(set(tabs), set(panels))
        self.assertEqual(sum(1 for tab in ui_manifest["tabs"] if tab.get("active")), 1)
        self.assertEqual(ui_manifest["tabs"][0]["id"], "inicio")
        self.assertTrue(ui_manifest["tabs"][0].get("active"))
        self.assertNotIn("toppicks", tabs)
        self.assertNotIn("matrix", tabs)

    def test_removed_tabs_have_no_stale_dom_targets(self):
        stale_patterns = (
            "Top Picks",
            "Matriz Completa",
            "toppicks-view",
            "matrix-table",
            "data-tp-dir",
            "data-filter-mat",
        )
        for pattern in stale_patterns:
            with self.subTest(pattern=pattern):
                self.assertNotIn(pattern, self.html)

    def test_home_cockpit_has_operational_sections(self):
        expected_ids = [
            "home-hero-status",
            "home-readiness-score",
            "home-readiness-bar",
            "home-check-manifest",
            "home-check-plan",
            "home-check-strategies",
            "home-check-backend",
            "home-runtime-status",
            "home-audit-score",
            "home-audit-manifest",
            "home-audit-plan",
            "home-audit-backend",
            "home-audit-templates",
            "home-audit-sqx",
            "home-audit-output",
            "home-history-list",
            "home-history-empty",
            "home-history-clear",
            "pg-onboarding-progress",
            "pg-onboarding-title",
            "pg-onboarding-desc",
            "pg-onboarding-bar",
            "pg-onboarding-steps",
            "pg-onboarding-action",
            "pg-onboarding-secondary",
            "pg-onboarding-tertiary",
            "pg-assistant-panel",
            "pg-assistant-next",
            "pg-assistant-hint",
            "pg-assistant-checks",
            "strat-hidden-wrap",
            "strat-hidden-count",
            "strat-restore-hidden-btn",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        self.assertIn("window.updateHomeBackendStatus", dashboard_js)
        self.assertIn("home-audit-score", dashboard_js)
        self.assertIn("window.addHomeTrace", dashboard_js)
        self.assertIn("HOME_TRACE_KEY", dashboard_js)
        self.assertIn("updateHomeBackendStatus", main_js)
        self.assertIn("templates_capa1_exists", main_js)
        self.assertIn("pgTrace(", main_js)
        self.assertIn("function pgRenderOnboarding", main_js)
        self.assertIn("function pgRunOnboardingAction", main_js)
        self.assertIn("function pgRunOnboardingTertiaryAction", main_js)
        self.assertIn("pg-assistant-check", main_js)
        self.assertIn("STRAT_DELETED_KEY", dashboard_js)
        self.assertIn("function removeStrategyClick", dashboard_js)
        self.assertIn("data-strategy-key", dashboard_js)

    def test_external_dataset_scripts_are_valid_assignments(self):
        datasets = {
            "js/historical-data.js": "window.SQX_HISTORICAL_DATA",
                "js/scores-data.js": "window.SQX_SCORES_DATA",
        }
        for rel_path, global_name in datasets.items():
            with self.subTest(rel_path=rel_path):
                text = (APP_ROOT / rel_path).read_text(encoding="utf-8-sig").strip()
                self.assertTrue(text.startswith(global_name + " = "))
                self.assertTrue(text.endswith(";"))
                json_text = text[len(global_name + " = "):-1]
                data = json.loads(json_text)
                self.assertIsInstance(data, dict)
                self.assertGreater(len(data), 0)

    def test_manifest_script_mirrors_json_manifests(self):
        text = (APP_ROOT / "js" / "manifest-data.js").read_text(encoding="utf-8-sig").strip()
        self.assertTrue(text.startswith("window.SQX_MANIFEST = "))
        self.assertTrue(text.endswith(";"))
        manifest = json.loads(text[len("window.SQX_MANIFEST = "):-1])

        plan = json.loads((TOOL_ROOT / "config" / "plan.json").read_text(encoding="utf-8-sig"))
        assets = json.loads((TOOL_ROOT / "config" / "assets.json").read_text(encoding="utf-8-sig"))
        strategies = json.loads((TOOL_ROOT / "config" / "strategies.json").read_text(encoding="utf-8-sig"))
        ui = json.loads((TOOL_ROOT / "config" / "ui_manifest.json").read_text(encoding="utf-8-sig"))

        self.assertEqual(manifest["plan"], plan)
        self.assertEqual(manifest["assets"], assets)
        self.assertEqual(manifest["strategies"], strategies)
        self.assertEqual(manifest["ui"], ui)

    def test_compat_data_layer_has_no_domain_arrays(self):
        data_js = (APP_ROOT / "js" / "data.js").read_text(encoding="utf-8-sig")
        self.assertIn("Source of truth lives in app/js/manifest-data.js", data_js)
        self.assertNotIn("const PLAN_MININGS = [", data_js)
        self.assertNotIn("const STRATEGIES = [", data_js)

    def test_phase1_analysis_scripts_are_present_and_syntax_valid(self):
        scripts = [
            "sqx_analysis_common.py",
            "analyze_assets.py",
            "score_assets.py",
            "plan_recommender.py",
            "download_dukas_bulk.py",
        ]
        for script in scripts:
            with self.subTest(script=script):
                path = ANALYSIS_ROOT / script
                self.assertTrue(path.is_file(), script)
                py_compile.compile(str(path), doraise=True)

        helper = (ANALYSIS_ROOT / "sqx_analysis_common.py").read_text(encoding="utf-8")
        self.assertIn("app/js/manifest-data.js", helper)


if __name__ == "__main__":
    unittest.main()
