import json
import py_compile
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class DashboardStaticTestCase(unittest.TestCase):
    def setUp(self):
        self.html_path = ROOT / "SQX_Dashboard_v6.html"
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
            self.assertTrue((ROOT / script).is_file(), script)

    def test_tabs_have_matching_panels(self):
        ui_manifest = json.loads((ROOT / "sqx-edge-tool" / "config" / "ui_manifest.json").read_text(encoding="utf-8-sig"))
        tabs = [tab["id"] for tab in ui_manifest["tabs"]]
        panels = re.findall(r'id="tab-([^"]+)"', self.html)

        self.assertEqual(len(tabs), 8)
        self.assertEqual(set(tabs), set(panels))
        self.assertEqual(sum(1 for tab in ui_manifest["tabs"] if tab.get("active")), 1)
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

    def test_external_dataset_scripts_are_valid_assignments(self):
        datasets = {
            "js/historical-data.js": "window.SQX_HISTORICAL_DATA",
            "js/scores-data.js": "window.SQX_SCORES_DATA",
        }
        for rel_path, global_name in datasets.items():
            with self.subTest(rel_path=rel_path):
                text = (ROOT / rel_path).read_text(encoding="utf-8-sig").strip()
                self.assertTrue(text.startswith(global_name + " = "))
                self.assertTrue(text.endswith(";"))
                json_text = text[len(global_name + " = "):-1]
                data = json.loads(json_text)
                self.assertIsInstance(data, dict)
                self.assertGreater(len(data), 0)

    def test_manifest_script_mirrors_json_manifests(self):
        text = (ROOT / "js" / "manifest-data.js").read_text(encoding="utf-8-sig").strip()
        self.assertTrue(text.startswith("window.SQX_MANIFEST = "))
        self.assertTrue(text.endswith(";"))
        manifest = json.loads(text[len("window.SQX_MANIFEST = "):-1])

        plan = json.loads((ROOT / "sqx-edge-tool" / "config" / "plan.json").read_text(encoding="utf-8-sig"))
        assets = json.loads((ROOT / "sqx-edge-tool" / "config" / "assets.json").read_text(encoding="utf-8-sig"))
        strategies = json.loads((ROOT / "sqx-edge-tool" / "config" / "strategies.json").read_text(encoding="utf-8-sig"))
        ui = json.loads((ROOT / "sqx-edge-tool" / "config" / "ui_manifest.json").read_text(encoding="utf-8-sig"))

        self.assertEqual(manifest["plan"], plan)
        self.assertEqual(manifest["assets"], assets)
        self.assertEqual(manifest["strategies"], strategies)
        self.assertEqual(manifest["ui"], ui)

    def test_compat_data_layer_has_no_domain_arrays(self):
        data_js = (ROOT / "js" / "data.js").read_text(encoding="utf-8-sig")
        self.assertIn("Source of truth lives in js/manifest-data.js", data_js)
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
                path = ROOT / script
                self.assertTrue(path.is_file(), script)
                py_compile.compile(str(path), doraise=True)

        helper = (ROOT / "sqx_analysis_common.py").read_text(encoding="utf-8")
        self.assertIn("js/manifest-data.js", helper)


if __name__ == "__main__":
    unittest.main()
