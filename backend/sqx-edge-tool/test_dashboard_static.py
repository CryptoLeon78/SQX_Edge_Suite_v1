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
                "js/modules/core.js",
                "js/modules/config.js",
                "js/modules/storage.js",
                "js/modules/ui.js",
                "js/modules/formatters.js",
                "js/modules/domain.js",
                "js/modules/datasets.js",
                "js/modules/renderers.js",
                "js/modules/charts.js",
                "js/modules/strategies.js",
                "js/modules/home.js",
                "js/modules/workflow.js",
                "js/modules/project-generator.js",
                "js/modules/index.js",
                "js/data.js",
                "js/dashboard.js",
                "js/main.js",
            ],
        )
        for script in scripts:
            self.assertTrue((APP_ROOT / script).is_file(), script)

    def test_modular_scaffold_loads_before_legacy_logic(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        module_scripts = [
            "js/modules/core.js",
            "js/modules/config.js",
            "js/modules/storage.js",
            "js/modules/ui.js",
            "js/modules/formatters.js",
            "js/modules/domain.js",
            "js/modules/datasets.js",
            "js/modules/renderers.js",
            "js/modules/charts.js",
            "js/modules/strategies.js",
            "js/modules/home.js",
            "js/modules/workflow.js",
            "js/modules/project-generator.js",
            "js/modules/index.js",
        ]

        for script in module_scripts:
            with self.subTest(script=script):
                self.assertLess(scripts.index(script), scripts.index("js/data.js"))

        core_js = (APP_ROOT / "js" / "modules" / "core.js").read_text(encoding="utf-8-sig")
        config_js = (APP_ROOT / "js" / "modules" / "config.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        ui_js = (APP_ROOT / "js" / "modules" / "ui.js").read_text(encoding="utf-8-sig")
        formatters_js = (APP_ROOT / "js" / "modules" / "formatters.js").read_text(encoding="utf-8-sig")
        domain_js = (APP_ROOT / "js" / "modules" / "domain.js").read_text(encoding="utf-8-sig")
        datasets_js = (APP_ROOT / "js" / "modules" / "datasets.js").read_text(encoding="utf-8-sig")
        renderers_js = (APP_ROOT / "js" / "modules" / "renderers.js").read_text(encoding="utf-8-sig")
        charts_js = (APP_ROOT / "js" / "modules" / "charts.js").read_text(encoding="utf-8-sig")
        strategies_js = (APP_ROOT / "js" / "modules" / "strategies.js").read_text(encoding="utf-8-sig")
        home_js = (APP_ROOT / "js" / "modules" / "home.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")
        project_generator_js = (APP_ROOT / "js" / "modules" / "project-generator.js").read_text(encoding="utf-8-sig")
        index_js = (APP_ROOT / "js" / "modules" / "index.js").read_text(encoding="utf-8-sig")
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")

        self.assertIn("global.SQX = global.SQX || {}", core_js)
        self.assertIn("registerModule", core_js)
        self.assertIn("SQX.config", config_js)
        self.assertIn("SQX.storage", storage_js)
        self.assertIn("SQX.ui", ui_js)
        self.assertIn("SQX.formatters", formatters_js)
        self.assertIn("SQX.domain", domain_js)
        self.assertIn("SQX.datasets", datasets_js)
        self.assertIn("SQX.renderers", renderers_js)
        self.assertIn("SQX.charts", charts_js)
        self.assertIn("SQX.strategies", strategies_js)
        self.assertIn("SQX.home", home_js)
        self.assertIn("SQX.workflow", workflow_js)
        self.assertIn("SQX.projectGenerator", project_generator_js)
        self.assertIn("SQX.boot", index_js)
        self.assertIn("dashboard-legacy", dashboard_js)

    def test_dashboard_history_chart_delegates_to_charts_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        charts_js = (APP_ROOT / "js" / "modules" / "charts.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_CHARTS", dashboard_js)
        self.assertIn("SQX_CHARTS.renderHistoryChart", dashboard_js)
        self.assertIn("renderHistoryChart", charts_js)
        self.assertIn("history-chart", charts_js)

    def test_dashboard_html_helpers_delegate_to_renderers_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        renderers_js = (APP_ROOT / "js" / "modules" / "renderers.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "sqxBadge",
            "sqxPreviewHTML",
            "ratingPairBadge",
            "compositeBar",
            "historySection",
            "sqxLegend",
            "sortableHeader",
            "sparkHTML",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, renderers_js)
                self.assertIn(f"SQX_RENDERERS.{export}", dashboard_js)

    def test_dashboard_strategy_logic_delegates_to_strategies_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        strategies_js = (APP_ROOT / "js" / "modules" / "strategies.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "strategyKey",
            "getAllStrategies",
            "filterStrategies",
            "summarize",
            "summaryHtml",
            "filterOptionsHtml",
            "strategyCard",
            "sortForDisplay",
            "exportCsvRows",
            "dedupeImportedStrategies",
            "consolidateJson",
            "consolidatedPopupHtml",
            "manualStrategyFromValues",
            "autoDetectTemplate",
            "parseCSV",
            "detectSeparator",
            "filterCsvRows",
            "csvPreviewTable",
            "csvConfirmHtml",
            "rowToStrategy",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, strategies_js)
                self.assertIn(f"SQX_STRATEGIES.{export}", dashboard_js)

    def test_dashboard_home_logic_delegates_to_home_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        home_js = (APP_ROOT / "js" / "modules" / "home.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "addTrace",
            "applyHomeModel",
            "computeHomeModel",
            "createTraceItem",
            "escapeHtml",
            "traceHtml",
            "trimAction",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, home_js)
                self.assertIn(f"SQX_HOME.{export}", dashboard_js)

    def test_dashboard_navigation_delegates_to_ui_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        ui_js = (APP_ROOT / "js" / "modules" / "ui.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "activateTabById",
            "bindButtonGroup",
            "bindChange",
            "bindClick",
            "bindHomeTabButtons",
            "bindInput",
            "bindTabs",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, ui_js)
                self.assertIn(f"SQX_UI_MODULE.{export}", dashboard_js)

    def test_workflow_shell_delegates_to_workflow_module(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "bindChecklist",
            "bindSubtabs",
            "init",
            "resolveChecklistKey",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, workflow_js)

        self.assertIn("window.SQX.workflow.init()", main_js)
        self.assertNotIn("CHECKLIST_STATE", main_js)
        self.assertNotIn("data-checklist-clear", main_js)

    def test_project_generator_onboarding_delegates_to_module(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        module_js = (APP_ROOT / "js" / "modules" / "project-generator.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "applyOnboardingState",
            "applyStatusBanner",
            "computeOnboardingState",
            "escapeHtml",
            "fetchJson",
            "prepareRequestOptions",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, module_js)

        self.assertIn("SQX_PG_MODULE.computeOnboardingState", main_js)
        self.assertIn("SQX_PG_MODULE.applyOnboardingState", main_js)
        self.assertIn("SQX_PG_MODULE.applyStatusBanner", main_js)
        self.assertIn("SQX_PG_MODULE.escapeHtml", main_js)
        self.assertIn("SQX_PG_MODULE.fetchJson", main_js)
        self.assertNotIn("const hasSqxInput = ", main_js)
        self.assertNotIn("stepsEl.innerHTML = state.steps.map", main_js)
        self.assertNotIn("await fetch(url, opts)", main_js)
        self.assertNotIn("banner.classList.remove('pg-status-up'", main_js)

    def test_dashboard_dataset_loading_delegates_to_datasets_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        datasets_js = (APP_ROOT / "js" / "modules" / "datasets.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_DATASETS", dashboard_js)
        self.assertIn("SQX_DATASETS.historical", dashboard_js)
        self.assertIn("SQX_DATASETS.scores", dashboard_js)
        self.assertIn("SQX_HISTORICAL_DATA", datasets_js)
        self.assertIn("SQX_SCORES_DATA", datasets_js)
        self.assertIn("readJsonScript", datasets_js)

    def test_dashboard_domain_logic_delegates_to_domain_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        domain_js = (APP_ROOT / "js" / "modules" / "domain.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "calcScore",
            "getSqxConfig",
            "scoreFromScores",
            "applyObjectiveRatings",
            "tfMatch",
            "sortRows",
            "assetMatchesSqxFilter",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, domain_js)
                self.assertIn(f"SQX_DOMAIN.{export}", dashboard_js)

    def test_runtime_config_delegates_through_config_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        config_js = (APP_ROOT / "js" / "modules" / "config.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_CONFIG_API", dashboard_js)
        self.assertIn("SQX_CONFIG_API.value", dashboard_js)
        self.assertIn("SQX_CONFIG_API.statusMeta", dashboard_js)
        self.assertIn("SQX_CONFIG_API.statusSequence", dashboard_js)
        self.assertIn("window.SQX.workflow.init()", main_js)
        self.assertIn("SQX.config", workflow_js)
        self.assertIn("SQX.config.storageKey", storage_js)
        self.assertIn("statusMeta", config_js)
        self.assertIn("statusSequence", config_js)

    def test_legacy_dashboard_helpers_delegate_to_formatter_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        formatters_js = (APP_ROOT / "js" / "modules" / "formatters.js").read_text(encoding="utf-8-sig")

        expected_exports = [
            "ratingLabel",
            "heatmapClass",
            "assetDirectionClass",
            "strategyDirectionClass",
            "tierClass",
            "tierLabel",
            "metricClass",
            "formatNumber",
            "formatInteger",
            "escapeHtml",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, formatters_js)
                self.assertIn(f"SQX_FORMATTERS.{export}", dashboard_js)

    def test_persistent_ui_state_delegates_to_storage_module(self):
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")

        self.assertIn("SQX_STORAGE = SQX_MODULES.storage", dashboard_js)
        self.assertIn("window.SQX.workflow.init()", main_js)
        self.assertIn("getJson", storage_js)
        self.assertIn("setJson", storage_js)

        expected_dashboard_calls = [
            "SQX_STORAGE.getJson(HOME_TRACE_KEY",
            "SQX_STORAGE.setJson(HOME_TRACE_KEY",
            "SQX_STORAGE.getJson(PRIORITY_STATE_KEY",
            "SQX_STORAGE.setJson(PRIORITY_STATE_KEY",
            "SQX_STORAGE.getJson(PLAN_USER_KEY",
            "SQX_STORAGE.setJson(PLAN_USER_KEY",
            "SQX_STORAGE.getJson(PIPELINE_STATE_KEY",
            "SQX_STORAGE.setJson(PIPELINE_STATE_KEY",
            "SQX_STORAGE.getJson(STRAT_USER_KEY",
            "SQX_STORAGE.setJson(STRAT_USER_KEY",
            "SQX_STORAGE.getJson(STRAT_DELETED_KEY",
            "SQX_STORAGE.setJson(STRAT_DELETED_KEY",
        ]
        for call in expected_dashboard_calls:
            with self.subTest(call=call):
                self.assertIn(call, dashboard_js)

        self.assertIn("storage.getJson(key", workflow_js)
        self.assertIn("storage.setJson(key", workflow_js)

    def test_pipeline_mobile_layout_has_overflow_guards(self):
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")

        self.assertIn("#tab-pipeline .card-header", css)
        self.assertIn("flex-wrap:wrap", css)
        self.assertIn("#ps-plan-table", css)
        self.assertIn("overflow-x:auto", css)
        self.assertIn("#tab-pipeline .ps-funnel-step", css)
        self.assertIn("flex-wrap:wrap", css)

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
        project_generator_js = (APP_ROOT / "js" / "modules" / "project-generator.js").read_text(encoding="utf-8-sig")
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
        self.assertIn("pg-assistant-check", project_generator_js)
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
