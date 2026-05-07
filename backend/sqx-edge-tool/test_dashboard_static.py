import json
import py_compile
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
ANALYSIS_ROOT = PROJECT_ROOT / "analysis"
ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
PROJECT_GOVERNANCE_DOC = PROJECT_ROOT / "docs" / "PROJECT_GOVERNANCE.md"
GOVERNANCE_ADR_DOC = PROJECT_ROOT / "docs" / "decisions" / "ADR-0001-specialist-agent-governance.md"
MONETIZATION_ROADMAP_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_ROADMAP.md"
MONETIZATION_M1_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M1.md"
MONETIZATION_M2_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M2.md"
MONETIZATION_M3_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M3.md"
MONETIZATION_M4_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M4.md"
MONETIZATION_M5_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M5.md"
MONETIZATION_M6_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M6.md"
MONETIZATION_M7_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M7.md"
MONETIZATION_M8_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M8.md"
MONETIZATION_M9_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M9.md"
MONETIZATION_M10_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M10.md"
MONETIZATION_M11_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M11.md"
MONETIZATION_M12_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M12.md"
MONETIZATION_M13_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M13.md"
MONETIZATION_M14_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M14.md"
MONETIZATION_M15_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M15.md"
MONETIZATION_M16_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M16.md"
MONETIZATION_M17_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M17.md"
MONETIZATION_M18_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M18.md"
MONETIZATION_M19_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M19.md"
MONETIZATION_M20_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M20.md"
MONETIZATION_M21_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M21.md"
MONETIZATION_M22_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M22.md"
MONETIZATION_M23_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M23.md"
MONETIZATION_M24_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M24.md"
MONETIZATION_M25_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M25.md"
MONETIZATION_M26_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M26.md"
MONETIZATION_M27_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M27.md"
MONETIZATION_M28_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M28.md"
MONETIZATION_M29_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M29.md"
MONETIZATION_M30_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M30.md"
MONETIZATION_M31_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M31.md"
MONETIZATION_M32_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M32.md"
MONETIZATION_M33_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M33.md"
MONETIZATION_M34_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M34.md"
MONETIZATION_M35_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M35.md"
MONETIZATION_M36_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M36.md"
MONETIZATION_M37_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M37.md"
MONETIZATION_M38_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M38.md"
MONETIZATION_M39_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M39.md"
MONETIZATION_M40_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M40.md"
MONETIZATION_M41_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M41.md"
MONETIZATION_M42_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M42.md"
MONETIZATION_M43_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M43.md"
MONETIZATION_M44_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M44.md"
MONETIZATION_M45_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M45.md"
MONETIZATION_M46_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M46.md"
MONETIZATION_M47_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M47.md"
MONETIZATION_M48_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M48.md"
MONETIZATION_M49_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M49.md"
MONETIZATION_M50_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M50.md"
MONETIZATION_M51_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M51.md"
MONETIZATION_M52_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M52.md"
MONETIZATION_M53_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M53.md"
MONETIZATION_M54_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M54.md"
MONETIZATION_M55_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M55.md"
MONETIZATION_M56_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M56.md"
MONETIZATION_M57_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M57.md"
MONETIZATION_M58_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M58.md"
MONETIZATION_M59_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M59.md"
MONETIZATION_M60_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M60.md"
MONETIZATION_M61_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M61.md"
MONETIZATION_M62_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M62.md"
MONETIZATION_M63_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M63.md"
MONETIZATION_M64_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M64.md"
MONETIZATION_M65_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M65.md"
MONETIZATION_M66_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M66.md"
MONETIZATION_M67_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M67.md"
MONETIZATION_M68_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M68.md"
MONETIZATION_M69_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M69.md"
MONETIZATION_M70_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M70.md"
MONETIZATION_M72_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M72.md"
MONETIZATION_M73_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M73.md"
MONETIZATION_M74_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M74.md"
MONETIZATION_M75_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M75.md"
MONETIZATION_M76_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M76.md"
MONETIZATION_M77_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M77.md"
MONETIZATION_M78_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M78.md"
MONETIZATION_M79_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M79.md"
MONETIZATION_M80_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M80.md"
MONETIZATION_M81_DOC = PROJECT_ROOT / "docs" / "MONETIZATION_M81.md"


class DashboardStaticTestCase(unittest.TestCase):
    def setUp(self):
        self.html_path = APP_ROOT / "SQX_Dashboard_v6.html"
        self.html = self.html_path.read_text(encoding="utf-8-sig")

    def assert_public_redaction_pointer(self, path):
        text = path.read_text(encoding="utf-8-sig")
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        lowered = text.lower()
        self.assertTrue(
            "public redaction" in lowered or "public_redaction" in lowered or "publicredaction" in lowered,
            text,
        )
        self.assertIn(rel.lower(), lowered)
        self.assertIn("https://github.com/cryptoleon78/sqx-edge-commercial-private", lowered)
        self.assertIn("ed79719", lowered)

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
                "js/modules/license.js",
                "js/modules/ui.js",
                "js/modules/formatters.js",
                "js/modules/domain.js",
                "js/modules/datasets.js",
                "js/modules/renderers.js",
                "js/modules/charts.js",
                "js/modules/strategies.js",
                "js/modules/home.js",
                "js/modules/support.js",
                "js/modules/fulfillment.js",
                "js/modules/customer-cockpit.js",
                "js/modules/workflow.js",
                "js/modules/view-creator.js",
                "js/modules/project-generator-core.js",
                "js/modules/project-generator-config.js",
                "js/modules/project-generator-dom.js",
                "js/modules/project-generator-bindings.js",
                "js/modules/project-generator-renderers.js",
                "js/modules/project-generator-status.js",
                "js/modules/project-generator-cleaner.js",
                "js/modules/project-generator.js",
                "js/modules/index.js",
                "js/data.js",
                "js/dashboard.js",
                "js/main.js",
                "js/project-generator-main.js",
            ],
        )
        for script in scripts:
            self.assertTrue((APP_ROOT / script).is_file(), script)

    def test_architecture_doc_matches_dashboard_load_order(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        architecture = ARCHITECTURE_DOC.read_text(encoding="utf-8-sig")
        match = re.search(
            r"## Frontend Load Order\s+.*?(?=\n## )",
            architecture,
            flags=re.S,
        )
        self.assertIsNotNone(match, "ARCHITECTURE.md is missing Frontend Load Order section")
        documented_scripts = re.findall(r"^\d+\.\s+`([^`]+)`", match.group(0), flags=re.M)

        self.assertEqual(documented_scripts, scripts)

    def test_project_governance_defines_agent_ownership_and_m46_entry(self):
        governance = PROJECT_GOVERNANCE_DOC.read_text(encoding="utf-8-sig")
        adr = GOVERNANCE_ADR_DOC.read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8-sig")

        for pattern in (
            "G1 - Specialist Agent Operating Model",
            "G2 - Governance Lookup Before Work",
            "Frontend/UI",
            "Backend/API",
            "QA/Release",
            "Monetization/Product",
            "Security/Distribution",
            "Architecture/Docs",
            "M46 Entry Criteria",
            "Before every work phase/message",
            "Specialist Agents ownership matrix",
            "active ownership",
            "Customer cockpit source of truth",
            "no license payloads",
            "Use prefixed phase IDs",
            "Never commit `backend/sqx-edge-tool/config/license.json`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, governance)

        for pattern in (
            "ADR-0001",
            "Status: Accepted",
            "Frontend/UI",
            "Mxx",
            "G1: Specialist Agent Operating Model",
            "G2 extends the baseline",
            "consult `docs/PROJECT_GOVERNANCE.md`",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, adr)

        self.assertIn("Phase G1: define specialist agent ownership, phase namespaces, workflow and M46 entry criteria. Done.", next_steps)
        self.assertIn("Phase G2: require governance/ownership lookup before each work phase/message. Done.", next_steps)
        self.assertIn("docs/PROJECT_GOVERNANCE.md", readme)
        self.assertIn("consulta obligatoria antes de fases/mensajes de trabajo", readme)

    def test_modular_scaffold_loads_before_legacy_logic(self):
        scripts = re.findall(r'<script\s+src="([^"]+)"', self.html)
        module_scripts = [
            "js/modules/core.js",
            "js/modules/config.js",
            "js/modules/storage.js",
            "js/modules/license.js",
            "js/modules/ui.js",
            "js/modules/formatters.js",
            "js/modules/domain.js",
            "js/modules/datasets.js",
            "js/modules/renderers.js",
            "js/modules/charts.js",
            "js/modules/strategies.js",
            "js/modules/home.js",
            "js/modules/support.js",
            "js/modules/fulfillment.js",
            "js/modules/customer-cockpit.js",
            "js/modules/workflow.js",
            "js/modules/view-creator.js",
            "js/modules/project-generator-core.js",
            "js/modules/project-generator-config.js",
            "js/modules/project-generator-dom.js",
            "js/modules/project-generator-bindings.js",
            "js/modules/project-generator-renderers.js",
            "js/modules/project-generator-status.js",
            "js/modules/project-generator-cleaner.js",
            "js/modules/project-generator.js",
            "js/modules/index.js",
        ]

        for script in module_scripts:
            with self.subTest(script=script):
                self.assertLess(scripts.index(script), scripts.index("js/data.js"))

        core_js = (APP_ROOT / "js" / "modules" / "core.js").read_text(encoding="utf-8-sig")
        config_js = (APP_ROOT / "js" / "modules" / "config.js").read_text(encoding="utf-8-sig")
        storage_js = (APP_ROOT / "js" / "modules" / "storage.js").read_text(encoding="utf-8-sig")
        license_js = (APP_ROOT / "js" / "modules" / "license.js").read_text(encoding="utf-8-sig")
        ui_js = (APP_ROOT / "js" / "modules" / "ui.js").read_text(encoding="utf-8-sig")
        formatters_js = (APP_ROOT / "js" / "modules" / "formatters.js").read_text(encoding="utf-8-sig")
        domain_js = (APP_ROOT / "js" / "modules" / "domain.js").read_text(encoding="utf-8-sig")
        datasets_js = (APP_ROOT / "js" / "modules" / "datasets.js").read_text(encoding="utf-8-sig")
        renderers_js = (APP_ROOT / "js" / "modules" / "renderers.js").read_text(encoding="utf-8-sig")
        charts_js = (APP_ROOT / "js" / "modules" / "charts.js").read_text(encoding="utf-8-sig")
        strategies_js = (APP_ROOT / "js" / "modules" / "strategies.js").read_text(encoding="utf-8-sig")
        home_js = (APP_ROOT / "js" / "modules" / "home.js").read_text(encoding="utf-8-sig")
        support_js = (APP_ROOT / "js" / "modules" / "support.js").read_text(encoding="utf-8-sig")
        fulfillment_js = (APP_ROOT / "js" / "modules" / "fulfillment.js").read_text(encoding="utf-8-sig")
        customer_cockpit_js = (APP_ROOT / "js" / "modules" / "customer-cockpit.js").read_text(encoding="utf-8-sig")
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")
        view_creator_js = (APP_ROOT / "js" / "modules" / "view-creator.js").read_text(encoding="utf-8-sig")
        project_generator_core_js = (APP_ROOT / "js" / "modules" / "project-generator-core.js").read_text(encoding="utf-8-sig")
        project_generator_config_js = (APP_ROOT / "js" / "modules" / "project-generator-config.js").read_text(encoding="utf-8-sig")
        project_generator_dom_js = (APP_ROOT / "js" / "modules" / "project-generator-dom.js").read_text(encoding="utf-8-sig")
        project_generator_bindings_js = (APP_ROOT / "js" / "modules" / "project-generator-bindings.js").read_text(encoding="utf-8-sig")
        project_generator_renderers_js = (APP_ROOT / "js" / "modules" / "project-generator-renderers.js").read_text(encoding="utf-8-sig")
        project_generator_status_js = (APP_ROOT / "js" / "modules" / "project-generator-status.js").read_text(encoding="utf-8-sig")
        project_generator_cleaner_js = (APP_ROOT / "js" / "modules" / "project-generator-cleaner.js").read_text(encoding="utf-8-sig")
        project_generator_js = (APP_ROOT / "js" / "modules" / "project-generator.js").read_text(encoding="utf-8-sig")
        index_js = (APP_ROOT / "js" / "modules" / "index.js").read_text(encoding="utf-8-sig")
        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")

        self.assertIn("global.SQX = global.SQX || {}", core_js)
        self.assertIn("registerModule", core_js)
        self.assertIn("SQX.config", config_js)
        self.assertIn("SQX.storage", storage_js)
        self.assertIn("SQX.license", license_js)
        self.assertIn("SQX.ui", ui_js)
        self.assertIn("SQX.formatters", formatters_js)
        self.assertIn("SQX.domain", domain_js)
        self.assertIn("SQX.datasets", datasets_js)
        self.assertIn("SQX.renderers", renderers_js)
        self.assertIn("SQX.charts", charts_js)
        self.assertIn("SQX.strategies", strategies_js)
        self.assertIn("SQX.home", home_js)
        self.assertIn("SQX.support", support_js)
        self.assertIn("SQX.fulfillment", fulfillment_js)
        self.assertIn("SQX.customerCockpit", customer_cockpit_js)
        self.assertIn("SQX.workflow", workflow_js)
        self.assertIn("SQX.viewCreator", view_creator_js)
        self.assertIn("buildViewXml", view_creator_js)
        self.assertIn("SQX.projectGenerator", project_generator_core_js)
        self.assertIn("SQX.projectGenerator", project_generator_config_js)
        self.assertIn("SQX.projectGenerator", project_generator_dom_js)
        self.assertIn("SQX.projectGenerator", project_generator_bindings_js)
        self.assertIn("SQX.projectGenerator", project_generator_renderers_js)
        self.assertIn("SQX.projectGenerator", project_generator_status_js)
        self.assertIn("SQX.projectGenerator", project_generator_cleaner_js)
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

    def test_support_diagnostics_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        support_js = (APP_ROOT / "js" / "modules" / "support.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        support_py = (TOOL_ROOT / "core" / "support_diagnostics.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_ids = [
            "support-panel",
            "support-diagnostic-btn",
            "support-diagnostic-status",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "diagnosticsFilename",
            "downloadJson",
            "fetchDiagnostics",
            "generateDiagnostics",
            "setStatus",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, support_js)

        self.assertIn("js/modules/support.js", self.html)
        self.assertIn("window.SQX.support.init()", main_js)
        self.assertIn("/api/support/diagnostics", server_py)
        self.assertIn("build_support_diagnostics", server_py)
        self.assertIn("safe_to_send", support_py)
        self.assertIn("license_payload", support_py)
        self.assertIn("strategy_files", support_py)
        self.assertEqual(product_manifest["support"]["diagnosticsEndpoint"], "/api/support/diagnostics")
        self.assertTrue(product_manifest["support"]["safeToSend"])

    def test_fulfillment_operator_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        fulfillment_js = (APP_ROOT / "js" / "modules" / "fulfillment.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_ids = [
            "fulfillment-panel",
            "fulfillment-refresh-btn",
            "fulfillment-queue-count",
            "fulfillment-needs-review-count",
            "fulfillment-failed-count",
            "fulfillment-processed-count",
            "fulfillment-private-key",
            "fulfillment-zip-path",
            "fulfillment-support-email",
            "fulfillment-queue-status",
            "fulfillment-request-list",
            "fulfillment-empty",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "fetchQueue",
            "handleAction",
            "loadSettings",
            "processRequest",
            "renderQueue",
            "saveSettings",
            "setStatus",
            "storageKey",
            "updateRequestStatus",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, fulfillment_js)

        self.assertIn("js/modules/fulfillment.js", self.html)
        self.assertIn("window.SQX.fulfillment.init()", main_js)
        self.assertIn("/api/fulfillment/request-status", server_py)
        self.assertIn("/api/fulfillment/relay-ingest", server_py)
        self.assertIn("fulfillment_queue_overview", server_py)
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "controlled_traffic_expansion_review_ready")
        self.assertIn("checkout_live_readiness.py", product_manifest["upgrade"]["checkout"]["liveReadinessTool"])
        self.assertIn("commercial_release_candidate.py", product_manifest["upgrade"]["checkout"]["commercialReleaseCandidateTool"])
        self.assertIn("pilot_purchase_kit.py", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitTool"])
        self.assertIn("pilot_purchase_kit", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitEvidenceDir"])
        self.assertIn("limited_public_launch.py", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchTool"])
        self.assertIn("limited_public_launch", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchEvidenceDir"])
        self.assertIn("post_launch_control.py", product_manifest["upgrade"]["checkout"]["postLaunchControlTool"])
        self.assertIn("post_launch_control", product_manifest["upgrade"]["checkout"]["postLaunchControlEvidenceDir"])
        self.assertIn("commercial_feedback_loop.py", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopTool"])
        self.assertIn("commercial_feedback_loop", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopEvidenceDir"])
        self.assertIn("public_offer_pack.py", product_manifest["upgrade"]["checkout"]["publicOfferPackTool"])
        self.assertIn("public_offer_pack", product_manifest["upgrade"]["checkout"]["publicOfferPackEvidenceDir"])
        self.assertIn("launch_assets_kit.py", product_manifest["upgrade"]["checkout"]["launchAssetsKitTool"])
        self.assertIn("launch_assets_kit", product_manifest["upgrade"]["checkout"]["launchAssetsKitEvidenceDir"])
        self.assertIn("public_release_gate.py", product_manifest["upgrade"]["checkout"]["publicReleaseGateTool"])
        self.assertIn("public_release_gate", product_manifest["upgrade"]["checkout"]["publicReleaseGateEvidenceDir"])
        self.assertIn("release_publication_record.py", product_manifest["upgrade"]["checkout"]["releasePublicationRecordTool"])
        self.assertIn("release_publication_record", product_manifest["upgrade"]["checkout"]["releasePublicationRecordEvidenceDir"])
        self.assertIn("post_release_monitor.py", product_manifest["upgrade"]["checkout"]["postReleaseMonitorTool"])
        self.assertIn("post_release_monitor", product_manifest["upgrade"]["checkout"]["postReleaseMonitorEvidenceDir"])
        self.assertIn("hotfix_rollback_release.py", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseTool"])
        self.assertIn("hotfix_rollback_release", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseEvidenceDir"])
        self.assertIn("customer_success_renewal.py", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalTool"])
        self.assertIn("customer_success_renewal", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayIngestEndpoint"], "/api/fulfillment/relay-ingest")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayConfigCheckEndpoint"], "/relay/config-check")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayObservabilityEndpoint"], "/relay/observability")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySnapshotEndpoint"], "/relay/observability/snapshot")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayDispatchEndpoint"], "/relay/dispatch")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayOperatorTokenEnv"], "SQX_RELAY_OPERATOR_TOKEN")
        self.assertIn("dispatch_worker.py", product_manifest["upgrade"]["checkout"]["automation"]["relayWorkerScript"])
        self.assertIn("simulate_purchase_flow.py", product_manifest["upgrade"]["checkout"]["automation"]["relaySimulationTool"])
        self.assertIn("deployment_check.py", product_manifest["upgrade"]["checkout"]["automation"]["relayDeploymentCheckTool"])
        self.assertIn("staging_smoke.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingSmokeTool"])
        self.assertIn("staging_evidence.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingEvidenceTool"])
        self.assertIn("render_api_preflight.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderApiPreflightTool"])
        self.assertIn("render_credentials_handshake.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderCredentialsHandshakeTool"])
        self.assertIn("render_staging_gate.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderStagingGateTool"])
        self.assertIn("render_staging_launch_pack.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderStagingLaunchPackTool"])
        self.assertIn("render_staging_secrets_kit.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderStagingSecretsKitTool"])
        self.assertIn("local_ingest_tunnel_check.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestTunnelCheckTool"])
        self.assertIn("local_ingest_tunnel_launcher.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestTunnelLauncherTool"])
        self.assertIn("local_ingest_staging_session.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestStagingSessionTool"])
        self.assertIn("local_ingest_render_handoff.py", product_manifest["upgrade"]["checkout"]["automation"]["relayLocalIngestRenderHandoffTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRenderCredentialPolicy"], "api_key_only_no_account_password")
        self.assertIn(".env.staging.example", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingEnvExample"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRecommendedStagingProvider"], "render")
        self.assertIn("Dockerfile", product_manifest["upgrade"]["checkout"]["automation"]["relayDockerfile"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["requestStatusEndpoint"], "/api/fulfillment/request-status")
        self.assertTrue(product_manifest["upgrade"]["checkout"]["automation"]["operatorPanelEnabled"])

    def test_customer_cockpit_module_and_ui_are_wired(self):
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        customer_cockpit_js = (APP_ROOT / "js" / "modules" / "customer-cockpit.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        customer_cockpit_py = (TOOL_ROOT / "core" / "customer_cockpit.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_ids = [
            "customer-cockpit-panel",
            "customer-cockpit-refresh-btn",
            "customer-cockpit-customer-count",
            "customer-cockpit-renewal-count",
            "customer-cockpit-support-count",
            "customer-cockpit-opportunity-count",
            "customer-cockpit-status",
            "customer-cockpit-list",
            "customer-cockpit-empty",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        for export in [
            "apiBase",
            "endpoint",
            "fetchCockpit",
            "init",
            "renderCockpit",
            "riskClass",
            "riskLabel",
            "setStatus",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, customer_cockpit_js)

        self.assertIn("SQX.registerModule('customer-cockpit'", customer_cockpit_js)
        self.assertIn("js/modules/customer-cockpit.js", self.html)
        self.assertIn("window.SQX.customerCockpit.init()", main_js)
        self.assertIn("/api/customer-cockpit", server_py)
        self.assertIn("customer_cockpit_overview", server_py)
        self.assertIn("redacted_operator_summary", customer_cockpit_py)
        self.assertIn("license payloads", customer_cockpit_py)
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitEndpoint"], "/api/customer-cockpit")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitConfig"], "backend/sqx-edge-tool/config/customer_cockpit.json")
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["customerCockpitPolicy"],
            "render_redacted_operator_summary_without_license_payloads_or_raw_events",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackConfig"], "backend/sqx-edge-tool/config/pro_buyer_pack.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackResourceDir"], "resources/pro-buyer-pack")
        self.assertIn("pro_buyer_pack.py", product_manifest["upgrade"]["checkout"]["proBuyerPackValidationTool"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["proBuyerPackPolicy"],
            "ship_safe_buyer_material_without_license_payloads_private_keys_or_financial_promises",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateConfig"],
            "backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["buyerOnboardingResourceDir"], "resources/pro-buyer-pack/onboarding")
        self.assertIn("buyer_onboarding_support_gate.py", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateTool"])
        self.assertIn("buyer_onboarding_support_gate", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGatePolicy"],
            "confirm_purchase_zip_license_start_here_faq_support_and_safe_claims_before_handoff",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1Config"], "backend/sqx-edge-tool/config/template_pack_1.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1ResourceDir"], "resources/pro-template-pack-1")
        self.assertIn("template_pack_1_delivery.py", product_manifest["upgrade"]["checkout"]["templatePack1DeliveryTool"])
        self.assertIn("template_pack_1_delivery", product_manifest["upgrade"]["checkout"]["templatePack1EvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1Policy"],
            "deliver_as_separate_addon_zip_after_buyer_onboarding_gate_and_safe_claims_review",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferConfig"], "backend/sqx-edge-tool/config/template_pack_1_offer.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferResourceDir"], "resources/pro-template-pack-1/offer")
        self.assertIn("template_pack_1_offer.py", product_manifest["upgrade"]["checkout"]["templatePack1OfferTool"])
        self.assertIn("template_pack_1_offer", product_manifest["upgrade"]["checkout"]["templatePack1OfferEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1PublicationConfig"], "backend/sqx-edge-tool/config/template_pack_1_publication.json")
        self.assertIn("template_pack_1_publication.py", product_manifest["upgrade"]["checkout"]["templatePack1PublicationTool"])
        self.assertIn("template_pack_1_publication", product_manifest["upgrade"]["checkout"]["templatePack1PublicationEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1OfferPolicy"],
            "prepare_public_addon_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1PublicationConfig"],
            "backend/sqx-edge-tool/config/template_pack_1_publication.json",
        )
        self.assertIn("template_pack_1_publication.py", product_manifest["upgrade"]["checkout"]["templatePack1PublicationTool"])
        self.assertIn("template_pack_1_publication", product_manifest["upgrade"]["checkout"]["templatePack1PublicationEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1PublicationPolicy"],
            "require_real_checkout_url_variant_support_email_and_rollback_before_controlled_publication",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillConfig"], "backend/sqx-edge-tool/config/template_pack_1_purchase_drill.json")
        self.assertIn("template_pack_1_purchase_drill.py", product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillTool"])
        self.assertIn("template_pack_1_purchase_drill", product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1PurchaseDrillPolicy"],
            "record_controlled_addon_order_payment_delivery_support_and_refund_pause_before_scaling",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1HandoffConfig"], "backend/sqx-edge-tool/config/template_pack_1_handoff.json")
        self.assertIn("template_pack_1_handoff.py", product_manifest["upgrade"]["checkout"]["templatePack1HandoffTool"])
        self.assertIn("template_pack_1_handoff", product_manifest["upgrade"]["checkout"]["templatePack1HandoffEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1HandoffPolicy"],
            "confirm_delivery_support_first_value_and_scale_or_pause_decision_after_controlled_purchase",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterConfig"], "backend/sqx-edge-tool/config/template_pack_1_sales_register.json")
        self.assertIn("template_pack_1_sales_register.py", product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterTool"])
        self.assertIn("template_pack_1_sales_register", product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1SalesRegisterPolicy"],
            "track_redacted_addon_sales_delivery_support_refunds_and_scale_decision_before_more_traffic",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortConfig"], "backend/sqx-edge-tool/config/template_pack_1_feedback_cohort.json")
        self.assertIn("template_pack_1_feedback_cohort.py", product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortTool"])
        self.assertIn("template_pack_1_feedback_cohort", product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1FeedbackCohortPolicy"],
            "review_redacted_buyer_feedback_support_refunds_and_positive_signals_before_scaling_or_template_pack_2",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanConfig"], "backend/sqx-edge-tool/config/template_pack_1_action_plan.json")
        self.assertIn("template_pack_1_action_plan.py", product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanTool"])
        self.assertIn("template_pack_1_action_plan", product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack1ActionPlanPolicy"],
            "convert_feedback_cohort_into_owner_priority_support_claims_distribution_and_next_phase_actions",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2SpecsConfig"], "backend/sqx-edge-tool/config/template_pack_2_specs.json")
        self.assertIn("template_pack_2_specs.py", product_manifest["upgrade"]["checkout"]["templatePack2SpecsTool"])
        self.assertIn("template_pack_2_specs", product_manifest["upgrade"]["checkout"]["templatePack2SpecsEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2SpecsPolicy"],
            "define_pack_2_scope_assets_presets_support_delivery_and_next_phase_before_building_resources",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2AssetsConfig"], "backend/sqx-edge-tool/config/template_pack_2_assets.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2ResourceDir"], "resources/pro-template-pack-2")
        self.assertIn("template_pack_2_assets.py", product_manifest["upgrade"]["checkout"]["templatePack2AssetsTool"])
        self.assertIn("template_pack_2_assets", product_manifest["upgrade"]["checkout"]["templatePack2AssetsEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2AssetsPolicy"],
            "deliver_initial_pack_2_assets_as_separate_addon_zip_after_specs_gate_and_safe_claims_review",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2OfferPackConfig"], "backend/sqx-edge-tool/config/template_pack_2_offer_pack.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2OfferPackResourceDir"], "resources/pro-template-pack-2/offer")
        self.assertIn("template_pack_2_offer_pack.py", product_manifest["upgrade"]["checkout"]["templatePack2OfferPackTool"])
        self.assertIn("template_pack_2_offer_pack", product_manifest["upgrade"]["checkout"]["templatePack2OfferPackEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2OfferPackPolicy"],
            "prepare_pack_2_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2PublicationConfig"], "backend/sqx-edge-tool/config/template_pack_2_publication.json")
        self.assertIn("template_pack_2_publication.py", product_manifest["upgrade"]["checkout"]["templatePack2PublicationTool"])
        self.assertIn("template_pack_2_publication", product_manifest["upgrade"]["checkout"]["templatePack2PublicationEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2PublicationPolicy"],
            "require_real_checkout_url_variant_support_rollback_and_purchase_drill_before_controlled_publication",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillConfig"], "backend/sqx-edge-tool/config/template_pack_2_purchase_drill.json")
        self.assertIn("template_pack_2_purchase_drill.py", product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillTool"])
        self.assertIn("template_pack_2_purchase_drill", product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2PurchaseDrillPolicy"],
            "record_controlled_pack_2_order_payment_delivery_support_and_refund_pause_before_scaling",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2HandoffConfig"], "backend/sqx-edge-tool/config/template_pack_2_handoff.json")
        self.assertIn("template_pack_2_handoff.py", product_manifest["upgrade"]["checkout"]["templatePack2HandoffTool"])
        self.assertIn("template_pack_2_handoff", product_manifest["upgrade"]["checkout"]["templatePack2HandoffEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2HandoffPolicy"],
            "confirm_delivery_support_first_value_and_scale_or_pause_decision_after_controlled_pack_2_purchase",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterConfig"], "backend/sqx-edge-tool/config/template_pack_2_sales_register.json")
        self.assertIn("template_pack_2_sales_register.py", product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterTool"])
        self.assertIn("template_pack_2_sales_register", product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2SalesRegisterPolicy"],
            "track_redacted_pack_2_sales_delivery_support_refunds_and_scale_decision_before_more_traffic",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortConfig"], "backend/sqx-edge-tool/config/template_pack_2_feedback_cohort.json")
        self.assertIn("template_pack_2_feedback_cohort.py", product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortTool"])
        self.assertIn("template_pack_2_feedback_cohort", product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["templatePack2FeedbackCohortPolicy"],
            "review_redacted_pack_2_buyer_feedback_support_refunds_and_positive_signals_before_expanding_traffic",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutConfig"], "backend/sqx-edge-tool/config/buyer_ready_checkout_closeout.json")
        self.assertIn("buyer_ready_checkout_closeout.py", product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutTool"])
        self.assertIn("buyer_ready_checkout_closeout", product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerReadyCheckoutCloseoutPolicy"],
            "confirm_basic_user_checkout_release_license_support_and_rollback_before_controlled_sales",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["publicBuyerPageCadenceConfig"], "backend/sqx-edge-tool/config/public_buyer_page_cadence.json")
        self.assertIn("public_buyer_page_cadence.py", product_manifest["upgrade"]["checkout"]["publicBuyerPageCadenceTool"])
        self.assertIn("public_buyer_page_cadence", product_manifest["upgrade"]["checkout"]["publicBuyerPageCadenceEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["publicBuyerPageCadencePolicy"],
            "prepare_public_buyer_page_checklist_support_cadence_and_first_sale_operations_before_wider_distribution",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogConfig"], "backend/sqx-edge-tool/config/first_controlled_buyer_log.json")
        self.assertIn("first_controlled_buyer_log.py", product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogTool"])
        self.assertIn("first_controlled_buyer_log", product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["firstControlledBuyerLogPolicy"],
            "record_first_controlled_buyer_activation_support_feedback_and_post_sale_decision_without_personal_data",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopConfig"], "backend/sqx-edge-tool/config/post_sale_improvement_loop.json")
        self.assertIn("post_sale_improvement_loop.py", product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopTool"])
        self.assertIn("post_sale_improvement_loop", product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["postSaleImprovementLoopPolicy"],
            "convert_first_controlled_buyer_feedback_into_onboarding_support_macro_public_copy_and_safe_claim_micro_updates",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesConfig"], "backend/sqx-edge-tool/config/post_sale_micro_updates.json")
        self.assertIn("post_sale_micro_updates.py", product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesTool"])
        self.assertIn("post_sale_micro_updates", product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["postSaleMicroUpdatesPolicy"],
            "verify_applied_buyer_facing_micro_updates_and_next_controlled_buyer_readiness",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessConfig"],
            "backend/sqx-edge-tool/config/next_controlled_buyer_readiness.json",
        )
        self.assertIn("next_controlled_buyer_readiness.py", product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessTool"])
        self.assertIn("next_controlled_buyer_readiness", product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerReadinessPolicy"],
            "confirm_single_private_buyer_slot_checkout_license_delivery_support_followup_safe_claims_and_pause_rule",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomeConfig"],
            "backend/sqx-edge-tool/config/next_controlled_buyer_outcome.json",
        )
        self.assertIn("next_controlled_buyer_outcome.py", product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomeTool"])
        self.assertIn("next_controlled_buyer_outcome", product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomeEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextControlledBuyerOutcomePolicy"],
            "record_redacted_controlled_buyer_result_activation_first_value_support_refund_claims_and_next_distribution_decision",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionStepConfig"],
            "backend/sqx-edge-tool/config/controlled_distribution_step.json",
        )
        self.assertIn("controlled_distribution_step.py", product_manifest["upgrade"]["checkout"]["controlledDistributionStepTool"])
        self.assertIn("controlled_distribution_step", product_manifest["upgrade"]["checkout"]["controlledDistributionStepEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionStepPolicy"],
            "execute_selected_m71_decision_as_tiny_reversible_distribution_step",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionReviewConfig"],
            "backend/sqx-edge-tool/config/controlled_distribution_review.json",
        )
        self.assertIn("controlled_distribution_review.py", product_manifest["upgrade"]["checkout"]["controlledDistributionReviewTool"])
        self.assertIn("controlled_distribution_review", product_manifest["upgrade"]["checkout"]["controlledDistributionReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledDistributionReviewPolicy"],
            "review_m72_evidence_before_repeating_holding_pausing_or_preparing_next_buyer_facing_asset",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetConfig"],
            "backend/sqx-edge-tool/config/next_buyer_facing_asset.json",
        )
        self.assertIn("next_buyer_facing_asset.py", product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetTool"])
        self.assertIn("next_buyer_facing_asset", product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["nextBuyerFacingAssetPolicy"],
            "prepare_one_small_buyer_facing_asset_for_private_review_only_after_m73",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["privateAssetReviewConfig"],
            "backend/sqx-edge-tool/config/private_asset_review.json",
        )
        self.assertIn("private_asset_review.py", product_manifest["upgrade"]["checkout"]["privateAssetReviewTool"])
        self.assertIn("private_asset_review", product_manifest["upgrade"]["checkout"]["privateAssetReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["privateAssetReviewPolicy"],
            "approve_asset_for_controlled_publication_only_after_private_review_safe_claims_support_release_notes_and_rollback",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledPublicationGateConfig"],
            "backend/sqx-edge-tool/config/controlled_publication_gate.json",
        )
        self.assertIn("controlled_publication_gate.py", product_manifest["upgrade"]["checkout"]["controlledPublicationGateTool"])
        self.assertIn("controlled_publication_gate", product_manifest["upgrade"]["checkout"]["controlledPublicationGateEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledPublicationGatePolicy"],
            "prepare_controlled_publication_only_after_private_asset_review_support_safe_claims_release_notes_rollback_and_pause_rule_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["limitedPublicationDraftConfig"],
            "backend/sqx-edge-tool/config/limited_publication_draft.json",
        )
        self.assertIn("limited_publication_draft.py", product_manifest["upgrade"]["checkout"]["limitedPublicationDraftTool"])
        self.assertIn("limited_publication_draft", product_manifest["upgrade"]["checkout"]["limitedPublicationDraftEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["limitedPublicationDraftPolicy"],
            "prepare_limited_publication_copy_for_operator_review_only_after_m76_support_safe_claims_rollback_pause_rule_and_channel_limits_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["operatorPublicationReviewConfig"],
            "backend/sqx-edge-tool/config/operator_publication_review.json",
        )
        self.assertIn("operator_publication_review.py", product_manifest["upgrade"]["checkout"]["operatorPublicationReviewTool"])
        self.assertIn("operator_publication_review", product_manifest["upgrade"]["checkout"]["operatorPublicationReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["operatorPublicationReviewPolicy"],
            "approve_manual_limited_publication_only_after_human_review_safe_copy_support_rollback_pause_rule_channel_limit_and_basic_user_flow_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordConfig"],
            "backend/sqx-edge-tool/config/manual_limited_publication_record.json",
        )
        self.assertIn("manual_limited_publication_record.py", product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordTool"])
        self.assertIn("manual_limited_publication_record", product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualLimitedPublicationRecordPolicy"],
            "record_manual_limited_publication_only_after_m78_approval_support_rollback_pause_rule_monitoring_and_redacted_channel_evidence_are_ready",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualPublicationMonitorConfig"],
            "backend/sqx-edge-tool/config/manual_publication_monitor.json",
        )
        self.assertIn("manual_publication_monitor.py", product_manifest["upgrade"]["checkout"]["manualPublicationMonitorTool"])
        self.assertIn("manual_publication_monitor", product_manifest["upgrade"]["checkout"]["manualPublicationMonitorEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["manualPublicationMonitorPolicy"],
            "monitor_manual_limited_publication_before_any_traffic_expansion_and_block_scaling_when_support_claims_refunds_or_incidents_are_unresolved",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewConfig"],
            "backend/sqx-edge-tool/config/controlled_traffic_expansion_review.json",
        )
        self.assertIn("controlled_traffic_expansion_review.py", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewTool"])
        self.assertIn("controlled_traffic_expansion_review", product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewEvidenceDir"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["controlledTrafficExpansionReviewPolicy"],
            "approve_only_tiny_controlled_traffic_expansion_after_m80_monitoring_support_claims_refunds_incidents_rollback_and_pause_rule_are_clean",
        )

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
        project_generator_main_js = (APP_ROOT / "js" / "project-generator-main.js").read_text(encoding="utf-8-sig")
        project_generator_files = [
            "project-generator-core.js",
            "project-generator-config.js",
            "project-generator-dom.js",
            "project-generator-bindings.js",
            "project-generator-renderers.js",
            "project-generator-status.js",
            "project-generator-cleaner.js",
            "project-generator.js",
        ]
        module_js = "\n".join(
            (APP_ROOT / "js" / "modules" / filename).read_text(encoding="utf-8-sig")
            for filename in project_generator_files
        )

        expected_exports = [
            "aliasTableHtml",
            "aliasAutoSuggestResult",
            "aliasAutoSuggestStartMessage",
            "aliasChoiceValue",
            "aliasProposedMessage",
            "aliasSuggestionEmptyMessage",
            "aliasSuggestionPrompt",
            "aliasTopSuggestions",
            "applyOnboardingState",
            "applyStatusBanner",
            "autodetectCandidatesHtml",
            "cleanerTableHtml",
            "cleanerConfirmMessage",
            "cleanerErrorStatus",
            "cleanerHasAction",
            "cleanerMissingDirStatus",
            "cleanerNoActionStatus",
            "cleanerNoSelectionStatus",
            "cleanerOptions",
            "cleanerPreviewHeader",
            "cleanerPreviewLines",
            "cleanerPreviewPattern",
            "cleanerProcessingStatus",
            "cleanerProcessErrorTrace",
            "cleanerResultLevel",
            "cleanerResultLines",
            "cleanerResultSummary",
            "cleanerResultTrace",
            "cleanerScanMessage",
            "cleanerScanningStatus",
            "cleanerSelectedLabel",
            "cleanerSelectedMap",
            "computeOnboardingState",
            "directionClass",
            "directionLabel",
            "escapeHtml",
            "fetchJson",
            "appendLog",
            "bindProjectGeneratorEvents",
            "bindProjectGeneratorPolling",
            "bindStrategyCleanerEvents",
            "readConfigInputs",
            "readCustomProjectInputs",
            "setCustomProjectStatus",
            "setSettingsOpen",
            "writeConfigInputs",
            "bulkGenerateLabel",
            "configSaveBody",
            "configSaveError",
            "configSaveStatus",
            "customPresetIdFromName",
            "customProjectPresetCountLabel",
            "customProjectPresetOptionsHtml",
            "deleteCustomProjectPreset",
            "findCustomProjectPreset",
            "getCustomProjectPresets",
            "generateAllConfirmMessage",
            "generateAllResultLines",
            "generateAllResultSummary",
            "generateAllStartMessage",
            "generateAllTrace",
            "generateCustomMissingStatus",
            "generateCustomResult",
            "generateCustomStartMessage",
            "generateErrorResult",
            "generateOneResult",
            "generateOneStartMessage",
            "enrichMiningsWithSymbolInfo",
            "miningRowsHtml",
            "miningsCountLabel",
            "normalizeCustomPreset",
            "normalizeCustomProjectConfig",
            "outputCountLabel",
            "outputListHtml",
            "outputState",
            "openOutputDisconnectedStatus",
            "openOutputErrorStatus",
            "openOutputSuccessStatus",
            "prepareRequestOptions",
            "setCustomProjectPresets",
            "sqxCandidateFields",
            "sqxCandidateSelectedStatus",
            "sqxAppliedHtml",
            "sqxNotFoundHtml",
            "validateSqxMissingPathHtml",
            "validateSqxPathHtml",
            "validateSqxResolvedFields",
            "validateSqxShouldApply",
            "validateSqxTrace",
            "uniqueAssets",
            "upsertCustomProjectPreset",
        ]
        for export in expected_exports:
            with self.subTest(export=export):
                self.assertIn(export, module_js)

        self.assertIn("SQX_PG_MODULE.computeOnboardingState", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.applyOnboardingState", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.applyStatusBanner", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.aliasSuggestionPrompt", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.aliasChoiceValue", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.aliasAutoSuggestResult", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.escapeHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.fetchJson", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.generateOneResult", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.generateAllConfirmMessage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.generateAllResultLines", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.configSaveBody", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.configSaveStatus", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.sqxCandidateFields", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.validateSqxShouldApply", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.enrichMiningsWithSymbolInfo", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.outputState", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.openOutputSuccessStatus", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerNoSelectionStatus", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerResultTrace", project_generator_main_js)
        self.assertIn("const SQX_PG_DOM = SQX_PG_MODULE.dom", project_generator_main_js)
        self.assertIn("SQX_PG_DOM.readConfigInputs", project_generator_main_js)
        self.assertIn("SQX_PG_DOM.writeConfigInputs", project_generator_main_js)
        self.assertIn("SQX_PG_DOM.appendLog", project_generator_main_js)
        self.assertIn("const SQX_PG_BINDINGS = SQX_PG_MODULE.bindings", project_generator_main_js)
        self.assertIn("SQX_PG_BINDINGS.bindProjectGeneratorEvents", project_generator_main_js)
        self.assertIn("SQX_PG_BINDINGS.bindStrategyCleanerEvents", project_generator_main_js)
        self.assertIn("SQX_PG_BINDINGS.bindProjectGeneratorPolling", project_generator_main_js)
        self.assertIn("const PG_STATE = {", project_generator_main_js)
        self.assertIn("const CLN_STATE = {", project_generator_main_js)
        self.assertIn("PG_STATE.connected", project_generator_main_js)
        self.assertIn("CLN_STATE.selected", project_generator_main_js)
        self.assertNotIn("function bindProjectGeneratorEvents()", project_generator_main_js)
        self.assertNotIn("function bindStrategyCleanerEvents()", project_generator_main_js)
        self.assertNotIn("function bindProjectGeneratorPolling()", project_generator_main_js)
        self.assertNotIn("sqxPath: pgTrimmedInputValue('pg-sqx-path')", project_generator_main_js)
        self.assertNotIn("pgSetInputValue('pg-sqx-path', c.sqx_path)", project_generator_main_js)
        self.assertIn("function pgApplySqxCandidate(candidate, outputEl)", project_generator_main_js)
        self.assertIn("function pgApplyValidatedSqxPath(path, response)", project_generator_main_js)
        self.assertIn("function pgUpdateMiningSummary(count)", project_generator_main_js)
        self.assertIn("function pgRenderMiningsList(infos)", project_generator_main_js)
        self.assertIn("function pgRenderOutputState(output)", project_generator_main_js)
        self.assertNotIn("bindProjectGeneratorEvents();", project_generator_main_js)
        self.assertNotIn("bindStrategyCleanerEvents();", project_generator_main_js)
        self.assertNotIn("bindProjectGeneratorPolling();", project_generator_main_js)
        self.assertNotIn("SQX_PG_MODULE", main_js)
        self.assertNotIn("const PG_STATE = {", main_js)
        for old_state in [
            "let PG_CONNECTED",
            "let PG_HEALTH_TIMER",
            "let PG_PLAN_COUNT",
            "let PG_LAST_TRACE_STATE",
            "let PG_HEALTH_META",
            "let PG_CONFIG_STATE",
            "let PG_MININGS",
            "let PG_OUTPUT_FILES",
            "let PG_OUTPUT_DIR",
            "let PG_ALIASES",
            "let CLN_FILES",
            "let CLN_SELECTED",
        ]:
            with self.subTest(old_state=old_state):
                self.assertNotIn(old_state, project_generator_main_js)
        self.assertNotIn("const hasSqxInput = ", project_generator_main_js)
        self.assertNotIn("stepsEl.innerHTML = state.steps.map", project_generator_main_js)
        self.assertNotIn("await fetch(url, opts)", project_generator_main_js)
        self.assertNotIn("banner.classList.remove('pg-status-up'", project_generator_main_js)
        self.assertNotIn("function pgDirClass", project_generator_main_js)
        self.assertNotIn("function pgDirLabel", project_generator_main_js)
        self.assertNotIn("fetch(PG_API + '/minings'", project_generator_main_js)
        self.assertNotIn("const opts = top.map", project_generator_main_js)
        self.assertNotIn("const idx = parseInt(choice, 10)", project_generator_main_js)
        self.assertNotIn("Auto-suggest: ' + found", project_generator_main_js)
        self.assertNotIn("const countLabel = PG_PLAN_COUNT", project_generator_main_js)
        self.assertNotIn("String(x.mining).padStart", project_generator_main_js)
        self.assertNotIn("'OK: ' + r.ok_count", project_generator_main_js)
        self.assertNotIn("msg.textContent = '✓ Guardado: '", project_generator_main_js)
        self.assertNotIn("r.updated_keys.join(', ')", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-sqx-db').value = r.resolved.data_db", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-sqx-path').value = c.sqx_path", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-sqx-path').value.trim()", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-minings-count').textContent", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-output-count').textContent", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-minings-table').innerHTML", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-output-list').innerHTML", project_generator_main_js)
        self.assertNotIn("minings.length + ' minings'", project_generator_main_js)
        self.assertNotIn("r.files.length + ' archivos'", project_generator_main_js)
        self.assertNotIn("Promise.all(minings.map", project_generator_main_js)
        self.assertNotIn("info.textContent = 'Pon una carpeta primero.'", project_generator_main_js)
        self.assertNotIn("info.textContent = '🔍 Escaneando...'", project_generator_main_js)
        self.assertNotIn("'Procesando ' + CLN_SELECTED.size", project_generator_main_js)
        self.assertIn("openOutputFolder: pgOpenOutputFolder", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-open-output').addEventListener('click', async function", project_generator_main_js)
        self.assertNotIn("pgLog('📁 Abierta carpeta output'", project_generator_main_js)
        self.assertNotIn("pg-output-empty", project_generator_main_js)
        self.assertIn("autodetectSqx: pgAutodetectSqx", project_generator_main_js)
        self.assertIn("validateSqxPath: pgValidateSqxPath", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-autodetect').addEventListener('click', async function", project_generator_main_js)
        self.assertNotIn("document.getElementById('pg-validate').addEventListener('click', async function", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerTableHtml", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerOptions", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerConfirmMessage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerPreviewLines", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerResultSummary", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerScanMessage", project_generator_main_js)
        self.assertIn("SQX_PG_MODULE.cleanerSelectedMap", project_generator_main_js)
        self.assertNotIn("CLN_FILES.map(f =>", project_generator_main_js)
        self.assertNotIn("Object.fromEntries([...CLN_SELECTED]", project_generator_main_js)
        self.assertNotIn("Preview rename para ' + r.previews.length", project_generator_main_js)
        self.assertNotIn("cln-row-check\" data-path=\"'+pgEsc", project_generator_main_js)
        self.assertNotIn("const msg = `", project_generator_main_js)
        self.assertNotIn("const fname = x.path.split", project_generator_main_js)

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

    def test_license_module_and_product_manifest_are_wired(self):
        app_config_js = (APP_ROOT / "js" / "app-config.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        license_js = (APP_ROOT / "js" / "modules" / "license.js").read_text(encoding="utf-8-sig")
        server_py = (TOOL_ROOT / "api" / "server.py").read_text(encoding="utf-8-sig")
        license_py = (TOOL_ROOT / "core" / "license_manager.py").read_text(encoding="utf-8-sig")
        product_manifest = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))

        expected_dom_ids = [
            "license-panel",
            "license-plan-label",
            "license-state-badge",
            "license-status-detail",
            "license-commercial-copy",
            "license-upgrade-list",
            "license-plan-strip",
            "license-feature-list",
            "license-key-input",
            "license-checkout-link",
            "license-import-btn",
            "license-clear-btn",
            "license-upgrade-note",
            "license-feedback",
        ]
        for element_id in expected_dom_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        self.assertIn("const product = manifest.product", app_config_js)
        self.assertIn("window.SQX.license.init()", main_js)
        for export in [
            "currentStatus",
            "hasFeature",
            "importLicenseText",
            "renderPanel",
            "refreshBackendStatus",
            "storageKey",
        ]:
            with self.subTest(export=export):
                self.assertIn(export, license_js)

        self.assertEqual(product_manifest["build"]["channel"], "internal")
        self.assertIn("project_generator.generate", product_manifest["features"])
        self.assertIn("strategy_cleaner.apply", product_manifest["features"])
        self.assertIn("*", product_manifest["accessLevels"]["internal"]["features"])
        self.assertEqual(product_manifest["upgrade"]["headline"], "SQX Edge Pro")
        self.assertIn("24 EUR/mes", json.dumps(product_manifest["upgrade"], ensure_ascii=False))
        self.assertEqual(product_manifest["upgrade"]["checkout"]["primaryProvider"], "Lemon Squeezy")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["fallbackProvider"], "Gumroad")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["fulfillmentMode"], "manual_signed_license")
        self.assertIn("license_issue.py", product_manifest["upgrade"]["checkout"]["licenseIssuerTool"])
        self.assertIn("prepare_customer_delivery.ps1", product_manifest["upgrade"]["checkout"]["deliveryTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["rollbackPolicy"], "disable_checkout_pause_webhook_pause_worker_manual_fulfillment")
        self.assertIn("checkout_live_readiness.py", product_manifest["upgrade"]["checkout"]["liveReadinessTool"])
        self.assertIn("checkout_live_readiness", product_manifest["upgrade"]["checkout"]["liveReadinessEvidenceDir"])
        self.assertIn("commercial_release_candidate.py", product_manifest["upgrade"]["checkout"]["commercialReleaseCandidateTool"])
        self.assertIn("commercial_release_candidate", product_manifest["upgrade"]["checkout"]["commercialReleaseCandidateEvidenceDir"])
        self.assertIn("pilot_purchase_kit.py", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitTool"])
        self.assertIn("pilot_purchase_kit", product_manifest["upgrade"]["checkout"]["pilotPurchaseKitEvidenceDir"])
        self.assertIn("limited_public_launch.py", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchTool"])
        self.assertIn("limited_public_launch", product_manifest["upgrade"]["checkout"]["limitedPublicLaunchEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["limitedPublicLaunchPolicy"], "soft_launch_first_5_sales_then_review")
        self.assertIn("post_launch_control.py", product_manifest["upgrade"]["checkout"]["postLaunchControlTool"])
        self.assertIn("post_launch_control", product_manifest["upgrade"]["checkout"]["postLaunchControlEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postLaunchControlPolicy"], "review_first_sales_before_scaling")
        self.assertIn("commercial_feedback_loop.py", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopTool"])
        self.assertIn("commercial_feedback_loop", product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["commercialFeedbackLoopPolicy"], "classify_feedback_before_offer_changes")
        self.assertIn("public_offer_pack.py", product_manifest["upgrade"]["checkout"]["publicOfferPackTool"])
        self.assertIn("public_offer_pack", product_manifest["upgrade"]["checkout"]["publicOfferPackEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["publicOfferPackPolicy"], "review_copy_faq_release_notes_before_public_page")
        self.assertIn("launch_assets_kit.py", product_manifest["upgrade"]["checkout"]["launchAssetsKitTool"])
        self.assertIn("launch_assets_kit", product_manifest["upgrade"]["checkout"]["launchAssetsKitEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["launchAssetsKitPolicy"], "prepare_assets_release_draft_and_publication_checklist")
        self.assertIn("public_release_gate.py", product_manifest["upgrade"]["checkout"]["publicReleaseGateTool"])
        self.assertIn("public_release_gate", product_manifest["upgrade"]["checkout"]["publicReleaseGateEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["publicReleaseGatePolicy"], "confirm_tag_release_zip_checksum_support_and_rollback")
        self.assertIn("backend/sqx-edge-tool/tools/public_release_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("release_publication_record.py", product_manifest["upgrade"]["checkout"]["releasePublicationRecordTool"])
        self.assertIn("release_publication_record", product_manifest["upgrade"]["checkout"]["releasePublicationRecordEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["releasePublicationRecordPolicy"], "record_tag_release_asset_checksum_support_and_rollback_publication")
        self.assertIn("backend/sqx-edge-tool/tools/release_publication_record.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("post_release_monitor.py", product_manifest["upgrade"]["checkout"]["postReleaseMonitorTool"])
        self.assertIn("post_release_monitor", product_manifest["upgrade"]["checkout"]["postReleaseMonitorEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["postReleaseMonitorPolicy"], "monitor_incidents_activation_support_refunds_and_scale_decision")
        self.assertIn("backend/sqx-edge-tool/tools/post_release_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("hotfix_rollback_release.py", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseTool"])
        self.assertIn("hotfix_rollback_release", product_manifest["upgrade"]["checkout"]["hotfixRollbackReleaseEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["hotfixRollbackReleasePolicy"], "prepare_hotfix_or_rollback_release_notes_comms_and_closure_evidence")
        self.assertIn("backend/sqx-edge-tool/tools/hotfix_rollback_release.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("customer_success_renewal.py", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalTool"])
        self.assertIn("customer_success_renewal", product_manifest["upgrade"]["checkout"]["customerSuccessRenewalEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerSuccessRenewalPolicy"], "track_onboarding_activation_support_renewal_and_safe_expansion")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitEndpoint"], "/api/customer-cockpit")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["customerCockpitConfig"], "backend/sqx-edge-tool/config/customer_cockpit.json")
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["customerCockpitPolicy"],
            "render_redacted_operator_summary_without_license_payloads_or_raw_events",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackConfig"], "backend/sqx-edge-tool/config/pro_buyer_pack.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["proBuyerPackResourceDir"], "resources/pro-buyer-pack")
        self.assertIn("pro_buyer_pack.py", product_manifest["upgrade"]["checkout"]["proBuyerPackValidationTool"])
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["proBuyerPackPolicy"],
            "ship_safe_buyer_material_without_license_payloads_private_keys_or_financial_promises",
        )
        self.assertEqual(
            product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateConfig"],
            "backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json",
        )
        self.assertEqual(product_manifest["upgrade"]["checkout"]["buyerOnboardingResourceDir"], "resources/pro-buyer-pack/onboarding")
        self.assertIn("buyer_onboarding_support_gate.py", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateTool"])
        self.assertIn("buyer_onboarding_support_gate", product_manifest["upgrade"]["checkout"]["buyerOnboardingSupportGateEvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1Config"], "backend/sqx-edge-tool/config/template_pack_1.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1ResourceDir"], "resources/pro-template-pack-1")
        self.assertIn("template_pack_1_delivery.py", product_manifest["upgrade"]["checkout"]["templatePack1DeliveryTool"])
        self.assertIn("template_pack_1_delivery", product_manifest["upgrade"]["checkout"]["templatePack1EvidenceDir"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferConfig"], "backend/sqx-edge-tool/config/template_pack_1_offer.json")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["templatePack1OfferResourceDir"], "resources/pro-template-pack-1/offer")
        self.assertIn("template_pack_1_offer.py", product_manifest["upgrade"]["checkout"]["templatePack1OfferTool"])
        self.assertIn("template_pack_1_offer", product_manifest["upgrade"]["checkout"]["templatePack1OfferEvidenceDir"])
        self.assertIn("backend/sqx-edge-tool/tools/customer_success_renewal.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_success_renewal", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_cockpit", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/pro_buyer_pack", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/pro_buyer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/buyer_onboarding_support_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_delivery", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_delivery.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_offer", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_offer.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_publication", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_publication.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_purchase_drill", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_handoff", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_handoff.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_sales_register", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_sales_register.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_feedback_cohort", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_feedback_cohort.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_action_plan", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_action_plan.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_specs", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_specs.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_assets", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_assets.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_offer_pack", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_publication", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_publication.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_purchase_drill", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_purchase_drill.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_handoff", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_handoff.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_sales_register", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_sales_register.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_feedback_cohort", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_2_feedback_cohort.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/buyer_ready_checkout_closeout", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/buyer_ready_checkout_closeout.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/public_buyer_page_cadence", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/public_buyer_page_cadence.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/first_controlled_buyer_log", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/first_controlled_buyer_log.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/post_sale_improvement_loop", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/post_sale_improvement_loop.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/post_sale_micro_updates", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/post_sale_micro_updates.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_readiness", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_outcome", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_step", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_step.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_buyer_facing_asset", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_buyer_facing_asset.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/private_asset_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_asset_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_publication_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_publication_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/limited_publication_draft", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/limited_publication_draft.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/operator_publication_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/operator_publication_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_limited_publication_record", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_limited_publication_record.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_publication_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_publication_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_commercial_split.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("resources/pro-template-pack-1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("resources/pro-template-pack-2", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["webhookSignatureHeader"], "X-Signature")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["webhookSigningAlgorithm"], "hmac_sha256_hex")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["webhookSecretEnv"], "SQX_LEMON_WEBHOOK_SECRET")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["receiverEndpoint"], "/api/fulfillment/webhook/lemon")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayIngestEndpoint"], "/api/fulfillment/relay-ingest")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySignatureHeader"], "X-SQX-Relay-Signature")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySecretEnv"], "SQX_FULFILLMENT_RELAY_SECRET")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayServiceProject"], "backend/sqx-edge-relay")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayHealthEndpoint"], "/relay/health")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayConfigCheckEndpoint"], "/relay/config-check")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayObservabilityEndpoint"], "/relay/observability")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relaySnapshotEndpoint"], "/relay/observability/snapshot")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayWebhookEndpoint"], "/relay/webhook/lemon")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayQueueEndpoint"], "/relay/queue")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayDispatchEndpoint"], "/relay/dispatch")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRequeueEndpoint"], "/relay/requeue")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayOperatorTokenEnv"], "SQX_RELAY_OPERATOR_TOKEN")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayWorkerMode"], "supervised_dispatch_loop")
        self.assertIn("dispatch_worker.py", product_manifest["upgrade"]["checkout"]["automation"]["relayWorkerScript"])
        self.assertIn("simulate_purchase_flow.py", product_manifest["upgrade"]["checkout"]["automation"]["relaySimulationTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayObservabilityMode"], "jsonl_events_and_queue_snapshots")
        self.assertIn("deployment_check.py", product_manifest["upgrade"]["checkout"]["automation"]["relayDeploymentCheckTool"])
        self.assertIn("staging_smoke.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingSmokeTool"])
        self.assertIn("staging_evidence.py", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingEvidenceTool"])
        self.assertIn("render_api_preflight.py", product_manifest["upgrade"]["checkout"]["automation"]["relayRenderApiPreflightTool"])
        self.assertIn("Dockerfile", product_manifest["upgrade"]["checkout"]["automation"]["relayDockerfile"])
        self.assertIn("docker", product_manifest["upgrade"]["checkout"]["automation"]["relayDeploymentTargets"])
        self.assertIn("/relay/webhook/lemon", product_manifest["upgrade"]["checkout"]["automation"]["relayStagingChecks"])
        self.assertIn("SQX_RELAY_OPERATOR_TOKEN", product_manifest["upgrade"]["checkout"]["automation"]["relayRequiredProductionSecrets"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["queueListEndpoint"], "/api/fulfillment/requests")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["processEndpoint"], "/api/fulfillment/process")
        self.assertIn("fulfillment_request.py", product_manifest["upgrade"]["checkout"]["automation"]["normalizerTool"])
        self.assertIn("fulfill_from_request.ps1", product_manifest["upgrade"]["checkout"]["automation"]["fulfillmentTool"])
        self.assertIn("relay_bundle.py", product_manifest["upgrade"]["checkout"]["automation"]["relayBundleTool"])
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["deduplicationKey"], "provider_event_id")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["relayRetryPolicy"], "exponential_backoff_remote_queue")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["variants"][0]["plan"], "pro_monthly")
        self.assertIn("No promete rentabilidad", product_manifest["upgrade"]["disclaimer"])
        self.assertIn("De idea a pipeline operativo SQX", product_manifest["marketing"]["tagline"])
        self.assertEqual(product_manifest["security"]["apiBoundary"], "local_only")
        self.assertIn("config/license.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertEqual(product_manifest["licensing"]["signatureMode"], "rsa_sha256_pkcs1_v1_5")
        self.assertEqual(product_manifest["licensing"]["signatureAlgorithm"], "RS256")
        self.assertIn("publicKey", product_manifest["licensing"])
        self.assertTrue(product_manifest["licensing"]["keyManagement"]["productionKeyRequired"])
        self.assertTrue(product_manifest["licensing"]["keyManagement"]["publicKeyReplacementRequiredBeforePublicSale"])
        self.assertEqual(product_manifest["licensing"]["keyManagement"]["privateKeyPolicy"], "never_commit_never_ship")
        self.assertIn("license_keypair.ps1", product_manifest["licensing"]["keyManagement"]["keypairTool"])
        self.assertIn("license_signer.py", product_manifest["licensing"]["keyManagement"]["signerTool"])
        self.assertIn("license_issue.py", product_manifest["licensing"]["keyManagement"]["issuerTool"])
        self.assertIn("license_keys", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("*_private_key.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/license_keypair.ps1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/license_issue.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/checkout_live_readiness.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/commercial_release_candidate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/pilot_purchase_kit.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/limited_public_launch.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/post_launch_control.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/commercial_feedback_loop.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/public_offer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/launch_assets_kit.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_readiness", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_outcome", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_step", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_step.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_distribution_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/next_buyer_facing_asset", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/next_buyer_facing_asset.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/private_asset_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_asset_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_publication_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_publication_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/limited_publication_draft", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/limited_publication_draft.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/operator_publication_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/operator_publication_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_limited_publication_record", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_limited_publication_record.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/manual_publication_monitor", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/manual_publication_monitor.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_review", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/controlled_traffic_expansion_review.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/private_commercial_split.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_success_renewal", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/customer_cockpit", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/pro_buyer_pack", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/pro_buyer_pack.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/buyer_onboarding_support_gate", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_delivery", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_delivery.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_offer", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_offer.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_publication", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_publication.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_purchase_drill", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_handoff", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/template_pack_1_handoff.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("resources/pro-template-pack-1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/fulfillment_request.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/fulfill_from_request.ps1", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("backend/sqx-edge-tool/tools/relay_bundle.py", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("fulfillment_request_*.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("webhook_event_*.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("relay_event_*.json", product_manifest["security"]["sensitiveFilesExcludedFromPortable"])
        self.assertIn("/api/license/status", server_py)
        self.assertIn("/api/license/check", server_py)
        self.assertIn("/api/license/import", server_py)
        self.assertIn("/api/license/clear", server_py)
        self.assertIn("store_relay_bundle", server_py)
        self.assertIn("def require_feature", server_py)
        self.assertIn('require_feature("project_generator.generate")', server_py)
        self.assertIn('require_feature("strategy_cleaner.apply")', server_py)
        self.assertIn("def check_feature", license_py)
        self.assertIn("verify_license_signature", license_py)
        self.assertIn("rsa_sha256_pkcs1_v1_5", license_py)
        self.assertIn("pro_active", license_py)

    def test_pipeline_mobile_layout_has_overflow_guards(self):
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")

        self.assertIn("#tab-pipeline .card-header", css)
        self.assertIn("flex-wrap:wrap", css)
        self.assertIn("#ps-plan-table", css)
        self.assertIn("overflow-x:auto", css)
        self.assertIn("#tab-pipeline .ps-funnel-step", css)
        self.assertIn("flex-wrap:wrap", css)

    def test_phase46_operational_visual_polish_is_present(self):
        css = (APP_ROOT / "css" / "dashboard.css").read_text(encoding="utf-8-sig")

        expected_patterns = [
            "Phase 46: operational visual polish",
            "--phase46-grid",
            ".pg-status-banner::after",
            ".pg-mining-row:nth-child(even)",
            "#pg-log",
            ".strat-summary-card::after",
            ".strat-card .sc-indicators",
            ".csv-preview-table tr:hover td",
            "@media (max-width: 980px)",
            "@media (max-width: 640px)",
        ]
        for pattern in expected_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, css)

    def test_public_commercial_docs_are_redacted_and_traceable(self):
        manifest = json.loads((PROJECT_ROOT / "docs" / "private_commercial_manifest.json").read_text(encoding="utf-8-sig"))
        pointer_index = (PROJECT_ROOT / "docs" / "PUBLIC_COMMERCIAL_POINTERS.md").read_text(encoding="utf-8-sig")
        private_repo = "https://github.com/CryptoLeon78/sqx-edge-commercial-private"
        private_commit = "ed79719"
        marker = "Public Redaction Pointer"
        allowed_redaction_phases = {
            "S5_public_commercial_redaction",
            "M71_next_controlled_buyer_outcome",
            "M72_controlled_distribution_step",
            "M73_controlled_distribution_review",
            "M74_next_buyer_facing_asset",
            "M75_private_asset_review",
            "M76_controlled_publication_gate",
            "M77_limited_publication_draft",
            "M78_operator_publication_review",
            "M79_manual_limited_publication_record",
            "M80_manual_publication_monitor",
            "M81_controlled_traffic_expansion_review",
        }

        self.assertEqual(manifest["migrationStage"], "public_redacted_private_repo_published")
        self.assertEqual(manifest["phase"], "M81_controlled_traffic_expansion_review")
        self.assertEqual(manifest["latestPrivateCommercialPhase"], "M81")
        self.assertEqual(manifest["privateRepositoryUrl"], private_repo)
        self.assertEqual(manifest["privateBaselineCommit"], private_commit)
        self.assertIn("public_repository_keeps_only_traceability_pointers", manifest["publicRedactionPolicy"])

        for pattern in (
            "docs/MONETIZATION_ROADMAP.md",
            "docs/MONETIZATION_M*.md",
            "docs/sales/",
            "resources/pro-buyer-pack/",
            "resources/pro-template-pack-1/",
            "resources/pro-template-pack-2/",
            private_repo,
            private_commit,
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, pointer_index)

        markdown_targets = [
            MONETIZATION_ROADMAP_DOC,
            *sorted((PROJECT_ROOT / "docs").glob("MONETIZATION_M*.md")),
            *sorted((PROJECT_ROOT / "docs" / "sales").glob("*.md")),
            *sorted((PROJECT_ROOT / "resources" / "pro-buyer-pack").rglob("*.md")),
            *sorted((PROJECT_ROOT / "resources" / "pro-template-pack-1").rglob("*.md")),
            *sorted((PROJECT_ROOT / "resources" / "pro-template-pack-2").rglob("*.md")),
        ]
        self.assertGreater(len(markdown_targets), 120)
        for path in markdown_targets:
            text = path.read_text(encoding="utf-8-sig")
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            with self.subTest(path=rel):
                self.assertIn(marker, text)
                self.assertIn(f"Original path: {rel}", text)
                self.assertIn(private_repo, text)
                self.assertIn(private_commit, text)
                self.assertTrue(any(phase in text for phase in allowed_redaction_phases), text)

        for path in sorted((PROJECT_ROOT / "resources").glob("pro-*/**/*")):
            if not path.is_file() or path.suffix.lower() == ".md":
                continue
            text = path.read_text(encoding="utf-8-sig")
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            with self.subTest(path=rel):
                lowered = text.lower()
                self.assertTrue("public_redaction" in lowered or "publicredaction" in lowered, text)
                self.assertIn(rel.lower(), lowered)
                self.assertIn(private_repo.lower(), lowered)
                self.assertIn(private_commit, text)
    def test_commercial_release_candidate_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "commercial_release_candidate.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "commercial_release_candidate_ready",
            "production_public_key_placeholder",
            "pilot_purchase_not_confirmed",
            "ZIP SHA256",
            "checkout_live_readiness_not_go",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_pilot_purchase_kit_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "pilot_purchase_kit.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "pilot_purchase_kit",
            "pilot_order_id_missing",
            "license_import_not_confirmed",
            "prepare_customer_delivery.ps1",
            "license_issue.py",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_limited_public_launch_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "limited_public_launch.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "limited_public_launch",
            "pilot_purchase_kit_not_go",
            "public_checkout_not_confirmed",
            "support_inbox_not_confirmed",
            "first_sale_cap_out_of_range",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_post_launch_control_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "post_launch_control.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "post_launch_control",
            "limited_public_launch_not_go",
            "no_paid_sales_recorded",
            "activations_below_paid_sales",
            "scale_public_not_supported_by_metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_commercial_feedback_loop_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "commercial_feedback_loop.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "commercial_feedback_loop",
            "post_launch_control_not_go",
            "no_feedback_recorded",
            "pricing_objection_blocks_raise_price",
            "copy_confusion_blocks_keep_copy",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_public_offer_pack_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "public_offer_pack.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "public_offer_pack",
            "commercial_feedback_loop_not_go",
            "offer_headline_missing",
            "forbidden_claims_present",
            "buyer_steps_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_launch_assets_kit_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "launch_assets_kit.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "launch_assets_kit",
            "public_offer_pack_not_go",
            "github_release_draft_not_ready",
            "zip_sha256_not_confirmed",
            "publication_checklist_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_public_release_gate_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "public_release_gate.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "public_release_gate",
            "launch_assets_kit_not_go",
            "release_tag_missing",
            "sha256_not_published",
            "rollback_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_release_publication_record_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "release_publication_record.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "release_publication_record",
            "public_release_gate_not_go",
            "github_release_not_published",
            "sha256_mismatch",
            "rollback_window_not_open",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_post_release_monitor_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "post_release_monitor.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "post_release_monitor",
            "release_publication_record_not_go",
            "severe_incidents_open",
            "activation_error_rate_high",
            "rollback_not_available",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_hotfix_rollback_release_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "hotfix_rollback_release.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "hotfix_rollback_release",
            "post_release_monitor_not_go",
            "rollback_target_missing",
            "hotfix_notes_missing",
            "customer_comms_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_customer_success_renewal_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "customer_success_renewal.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "customer_success_renewal",
            "hotfix_rollback_release_not_go",
            "customer_reference_missing",
            "activation_not_confirmed",
            "support_tickets_open",
            "safe_claims_not_reviewed",
            "template_pack_offer_not_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_customer_cockpit_core_is_present_and_redacted(self):
        path = TOOL_ROOT / "core" / "customer_cockpit.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "customer_cockpit_ready",
            "redacted_operator_summary",
            "mask_email",
            "license payloads",
            "raw checkout events",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_pro_buyer_pack_resources_and_validator_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "pro_buyer_pack.py"
        config_path = TOOL_ROOT / "config" / "pro_buyer_pack.json"
        pack_root = PROJECT_ROOT / "resources" / "pro-buyer-pack"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "pro_buyer_pack_ready")
        self.assertTrue(config["includedInPortable"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in pack_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "asset_universe_must_have_33_rows",
            "strategy_csv_missing_column",
            "forbidden_claim",
            "pro_buyer_pack_ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_buyer_onboarding_support_gate_resources_and_validator_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "buyer_onboarding_support_gate.py"
        config_path = TOOL_ROOT / "config" / "buyer_onboarding_support_gate.json"
        onboarding_root = PROJECT_ROOT / "resources" / "pro-buyer-pack" / "onboarding"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "buyer_onboarding_support_gate_ready")
        self.assertTrue(config["includedInPortable"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in onboarding_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "buyer_onboarding_support_gate_ready",
            "purchase_not_confirmed",
            "portable_zip_not_ready",
            "license_file_not_ready",
            "refund_or_pause_risk_unreviewed",
            "forbidden_claims_present",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_resources_and_packager_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_delivery.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1.json"
        pack_root = PROJECT_ROOT / "resources" / "pro-template-pack-1"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_delivery_ready")
        self.assertFalse(config["includedInPortable"])
        self.assertTrue(config["includedInAddOnDelivery"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        profiles = sorted((pack_root / "profiles").glob("*.json"))
        self.assertEqual(len(profiles), 3)
        for resource_path in pack_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "template_pack_1_delivery_ready",
            "buyer_onboarding_gate_not_go",
            "addon_order_not_confirmed",
            "pack_zip_not_ready",
            "template_pack_1_csv_missing_column",
            "forbidden_claims_present",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_offer_resources_and_gate_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_offer.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_offer.json"
        offer_root = PROJECT_ROOT / "resources" / "pro-template-pack-1" / "offer"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_public_offer_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertTrue(config["allowDraftCheckout"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in offer_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "template_pack_1_public_offer_ready",
            "template_pack_delivery_not_ready",
            "checkout_draft_not_ready",
            "checkout_url_missing_or_not_https",
            "provider_variant_id_missing",
            "support_email_missing_or_invalid",
            "forbidden_claims_present",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_publication_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_publication.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_publication.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_live_checkout_gate_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["publicationMode"], "controlled_first_sales")
        self.assertEqual(config["firstSaleCap"], 5)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        self.assertEqual(config["env"]["checkoutUrl"], "SQX_TEMPLATE_PACK_1_CHECKOUT_URL")
        self.assertEqual(config["env"]["providerVariantId"], "SQX_TEMPLATE_PACK_1_PROVIDER_VARIANT_ID")
        self.assertEqual(config["env"]["supportEmail"], "SQX_TEMPLATE_PACK_1_SUPPORT_EMAIL")

        for pattern in (
            "checkout_url_missing_or_not_https",
            "checkout_url_looks_placeholder",
            "provider_variant_id_missing",
            "support_email_missing_or_invalid",
            "_not_confirmed",
            "template_pack_1_controlled_publication_live",
            "apply_publication_values",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_purchase_drill_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_purchase_drill.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_purchase_drill.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_purchase_drill_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["amount"], "49.00")
        self.assertEqual(config["currency"], "EUR")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_email_and_order_reference_only")
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "redact_email",
            "checkout_url_missing_or_not_https",
            "provider_order_id_missing",
            "payment_status_not_paid",
            "delivery_package_missing_entry",
            "delivery_package_content_not_verified",
            "buyer_email_redacted",
            "--require-delivery-package",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_handoff_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_handoff.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_handoff.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_handoff_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_handoff_notes_and_scale_decision_only")
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("hold_review", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_purchase_drill_file",
            "buyer_email_redacted",
            "template_pack_1_purchase_drill_evidence_missing",
            "support_first_response_sla_missed",
            "scale_limited_not_supported_by_handoff",
            "refund_risk_requires_pause_sales",
            "--use-latest-purchase-drill",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_sales_register_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_sales_register.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_sales_register.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_sales_register_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_order_status_support_metrics_and_scale_decision_only")
        self.assertIn("keep_tracking", config["allowedDecisions"])
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_handoff_file",
            "buyer_email_redacted",
            "template_pack_1_handoff_evidence_missing",
            "open_support_items_require_pause_or_review",
            "scale_limited_not_supported_by_register",
            "register_record",
            "--append-register",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_feedback_cohort_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_feedback_cohort.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_feedback_cohort.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_feedback_cohort_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_cohort_metrics_feedback_themes_support_counts_and_roadmap_decision_only")
        self.assertIn("expand_traffic", config["allowedDecisions"])
        self.assertIn("iterate_offer", config["allowedDecisions"])
        self.assertIn("build_template_pack_2", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_sales_register_file",
            "template_pack_1_sales_register_evidence_missing",
            "expand_traffic_needs_minimum_buyers",
            "open_support_blocks_expansion",
            "template_pack_2_needs_positive_signals",
            "--use-latest-sales-register",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_1_action_plan_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_1_action_plan.py"
        config_path = TOOL_ROOT / "config" / "template_pack_1_action_plan.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_1_action_plan_ready")
        self.assertEqual(config["offerId"], "template_pack_1")
        self.assertEqual(config["privacyPolicy"], "store_redacted_action_plan_owner_priority_support_claims_distribution_and_next_phase_only")
        self.assertIn("offer_iteration", config["allowedPlans"])
        self.assertIn("traffic_expansion", config["allowedPlans"])
        self.assertIn("template_pack_2", config["allowedPlans"])
        self.assertIn("pause_sales", config["allowedPlans"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_feedback_cohort_file",
            "template_pack_1_feedback_cohort_evidence_missing",
            "traffic_expansion_support_impact_too_high",
            "template_pack_2_next_phase_mismatch",
            "feedback_recommended_",
            "--use-latest-feedback-cohort",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_specs_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_specs.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_specs.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_specs_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["privacyPolicy"], "store_redacted_pack_2_scope_assets_support_delivery_and_next_phase_only")
        self.assertIn("draft_pack_2_assets", config["allowedSpecDecisions"])
        self.assertIn("iterate_pack_1_first", config["allowedSpecDecisions"])
        self.assertIn("pause_pack_2", config["allowedSpecDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "latest_action_plan_file",
            "template_pack_1_action_plan_evidence_missing",
            "template_pack_1_action_plan_not_template_pack_2",
            "draft_pack_2_assets_needs_asset_families",
            "draft_pack_2_assets_next_phase_mismatch",
            "--use-latest-action-plan",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_assets_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_assets.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_assets.json"
        resource_dir = PROJECT_ROOT / "resources" / "pro-template-pack-2"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_assets_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["resourceDir"], "resources/pro-template-pack-2")
        self.assertFalse(config["includedInPortable"])
        self.assertTrue(config["includedInAddOnDelivery"])
        self.assertEqual(config["minimumPresetRows"], 8)
        self.assertEqual(config["dependsOn"]["requiredSpecDecision"], "draft_pack_2_assets")
        self.assertEqual(config["dependsOn"]["requiredNextPhase"], "M58_template_pack_2_assets")
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        profiles = sorted((resource_dir / "profiles").glob("*.json"))
        self.assertGreaterEqual(len(profiles), 3)
        for resource_path in resource_dir.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)

        for pattern in (
            "latest_specs_file",
            "template_pack_2_specs_evidence_missing",
            "template_pack_2_specs_decision_invalid",
            "template_pack_2_csv_needs_eight_rows",
            "template_pack_2_csv_needs_asset_families",
            "--use-latest-specs",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_offer_pack_resources_and_gate_are_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_offer_pack.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_offer_pack.json"
        offer_root = PROJECT_ROOT / "resources" / "pro-template-pack-2" / "offer"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_offer_pack_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["price"], "79 EUR")
        self.assertTrue(config["allowDraftCheckout"])
        self.assertEqual(config["dependsOn"]["templatePack2AssetsState"], "template_pack_2_assets_ready")
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for resource_path in offer_root.rglob("*"):
            if resource_path.is_file():
                with self.subTest(resource=resource_path.name):
                    self.assert_public_redaction_pointer(resource_path)
        for pattern in (
            "template_pack_2_offer_pack_ready",
            "template_pack_2_assets_state_invalid",
            "template_pack_2_variant_missing",
            "checkout_url_missing_or_not_https",
            "--confirm-template-pack-2-assets-ready",
            "--require-live-checkout",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_publication_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_publication.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_publication.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_controlled_publication_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["price"], "79 EUR")
        self.assertEqual(config["dependsOn"]["offerPackState"], "template_pack_2_offer_pack_ready")
        self.assertEqual(config["dependsOn"]["assetsState"], "template_pack_2_assets_ready")
        self.assertEqual(config["env"]["checkoutUrl"], "SQX_TEMPLATE_PACK_2_CHECKOUT_URL")
        self.assertIn("purchaseDrillChecklist", config)
        self.assertGreaterEqual(len(config["purchaseDrillChecklist"]), 4)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_controlled_publication_ready",
            "template_pack_2_offer_pack_state_invalid",
            "template_pack_2_assets_state_invalid",
            "checkout_url_missing_or_not_https",
            "provider_variant_id_looks_placeholder",
            "templatePack2LiveCheckout",
            "--confirm-purchase-drill-ready",
            "--apply",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_purchase_drill_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_purchase_drill.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_purchase_drill.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_purchase_drill_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["price"], "79 EUR")
        self.assertEqual(config["amount"], "79.00")
        self.assertEqual(config["currency"], "EUR")
        self.assertEqual(config["dependsOn"]["publicationState"], "template_pack_2_controlled_publication_ready")
        self.assertEqual(config["dependsOn"]["assetsState"], "template_pack_2_assets_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_email_and_order_reference_only")
        self.assertIn("paid", config["allowedPaymentStatuses"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_purchase_drill_ready",
            "template_pack_2_publication_state_invalid",
            "template_pack_2_assets_state_invalid",
            "checkout_url_missing_or_not_https",
            "buyer_email_missing_or_invalid",
            "delivery_package_missing_entry",
            "buyer_email_redacted",
            "--require-delivery-package",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_handoff_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_handoff.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_handoff.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_handoff_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["dependsOn"]["purchaseDrillState"], "template_pack_2_purchase_drill_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_handoff_notes_and_scale_decision_only")
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("hold_review", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_handoff_ready",
            "template_pack_2_purchase_drill_state_invalid",
            "template_pack_2_purchase_drill_evidence_missing",
            "buyer_reference_missing_or_invalid",
            "support_first_response_sla_missed",
            "refund_risk_requires_pause_sales",
            "scale_limited_needs_buyer_acknowledgement_and_first_value",
            "buyer_email_redacted",
            "--use-latest-purchase-drill",
            "--scale-decision",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_sales_register_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_sales_register.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_sales_register.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_sales_register_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["dependsOn"]["handoffState"], "template_pack_2_handoff_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_buyer_reference_order_status_support_metrics_and_scale_decision_only")
        self.assertIn("keep_tracking", config["allowedDecisions"])
        self.assertIn("scale_limited", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_sales_register_ready",
            "template_pack_2_handoff_state_invalid",
            "template_pack_2_handoff_evidence_missing",
            "buyer_reference_missing_or_invalid",
            "non_paid_sale_requires_pause_sales",
            "delivery_not_confirmed_requires_pause_sales",
            "scale_limited_needs_minimum_sales",
            "template_pack_2_sales_register.jsonl",
            "--append-register",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_template_pack_2_feedback_cohort_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "template_pack_2_feedback_cohort.py"
        config_path = TOOL_ROOT / "config" / "template_pack_2_feedback_cohort.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "template_pack_2_feedback_cohort_ready")
        self.assertEqual(config["offerId"], "template_pack_2")
        self.assertEqual(config["dependsOn"]["salesRegisterState"], "template_pack_2_sales_register_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_cohort_metrics_feedback_themes_support_counts_and_roadmap_decision_only")
        self.assertIn("expand_traffic", config["allowedDecisions"])
        self.assertIn("iterate_offer", config["allowedDecisions"])
        self.assertIn("prepare_pack_3", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "template_pack_2_feedback_cohort_ready",
            "template_pack_2_sales_register_state_invalid",
            "template_pack_2_sales_register_evidence_missing",
            "feedback_cohort_metrics_invalid",
            "expand_traffic_needs_minimum_buyers",
            "pack_3_needs_positive_signals",
            "--use-latest-sales-register",
            "--roadmap-decision",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_buyer_ready_checkout_closeout_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "buyer_ready_checkout_closeout.py"
        config_path = TOOL_ROOT / "config" / "buyer_ready_checkout_closeout.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "buyer_ready_checkout_release_closeout_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_and_template_pack_2")
        self.assertEqual(config["dependsOn"]["feedbackCohortState"], "template_pack_2_feedback_cohort_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_checkout_release_support_and_delivery_readiness_only")
        self.assertIn("open_controlled_sales", config["allowedDecisions"])
        self.assertIn("keep_private_pilot", config["allowedDecisions"])
        self.assertIn("iterate_buyer_pack", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "buyer_ready_checkout_release_closeout_ready",
            "template_pack_2_feedback_cohort_state_invalid",
            "template_pack_2_feedback_cohort_evidence_missing",
            "buyer_steps_incomplete",
            "support_label_missing_or_unsafe",
            "open_sales_needs_positive_feedback_decision",
            "--use-latest-feedback-cohort",
            "--confirm-license-delivery-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_public_buyer_page_cadence_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "public_buyer_page_cadence.py"
        config_path = TOOL_ROOT / "config" / "public_buyer_page_cadence.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "public_buyer_page_cadence_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_public_buyer_page")
        self.assertEqual(config["dependsOn"]["buyerReadyCloseoutState"], "buyer_ready_checkout_release_closeout_ready")
        self.assertEqual(config["privacyPolicy"], "store_public_page_checklist_and_first_sale_cadence_without_customer_data")
        self.assertIn("publish_private_page", config["allowedDecisions"])
        self.assertIn("keep_draft", config["allowedDecisions"])
        self.assertIn("revise_copy", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "public_buyer_page_cadence_ready",
            "buyer_ready_checkout_closeout_state_invalid",
            "buyer_ready_checkout_closeout_evidence_missing",
            "public_page_sections_incomplete",
            "first_sale_cadence_incomplete",
            "publish_private_page_needs_private_link_ready",
            "--use-latest-buyer-ready-closeout",
            "--confirm-first-sale-cadence-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_first_controlled_buyer_log_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "first_controlled_buyer_log.py"
        config_path = TOOL_ROOT / "config" / "first_controlled_buyer_log.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "first_controlled_buyer_log_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_first_controlled_buyer")
        self.assertEqual(config["dependsOn"]["publicBuyerPageCadenceState"], "public_buyer_page_cadence_ready")
        self.assertEqual(config["privacyPolicy"], "store_redacted_first_buyer_order_activation_support_feedback_and_decision_only")
        self.assertIn("continue_private_sales", config["allowedDecisions"])
        self.assertIn("iterate_onboarding", config["allowedDecisions"])
        self.assertIn("schedule_followup", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "first_controlled_buyer_log_ready",
            "public_buyer_page_cadence_state_invalid",
            "public_buyer_page_cadence_evidence_missing",
            "order_ref_missing_or_unsafe",
            "continue_private_sales_needs_first_value_confirmed",
            "fulfillment_failures_require_pause_sales",
            "--use-latest-public-page-cadence",
            "--confirm-license-activation-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_post_sale_improvement_loop_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "post_sale_improvement_loop.py"
        config_path = TOOL_ROOT / "config" / "post_sale_improvement_loop.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "post_sale_improvement_loop_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_post_sale_improvement")
        self.assertEqual(config["dependsOn"]["firstControlledBuyerLogState"], "first_controlled_buyer_log_ready")
        self.assertEqual(config["privacyPolicy"], "store_aggregated_post_sale_improvement_actions_without_personal_data_or_raw_buyer_messages")
        self.assertIn("ship_micro_updates", config["allowedDecisions"])
        self.assertIn("revise_onboarding", config["allowedDecisions"])
        self.assertIn("revise_support_macros", config["allowedDecisions"])
        self.assertIn("revise_public_copy", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "post_sale_improvement_loop_ready",
            "first_controlled_buyer_log_state_invalid",
            "first_controlled_buyer_log_evidence_missing",
            "post_sale_improvement_needs_minimum_updates",
            "ship_micro_updates_blocked_by_support_risk",
            "claims_risk_requires_pause_sales",
            "--use-latest-first-buyer-log",
            "--confirm-support-macros-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_post_sale_micro_updates_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "post_sale_micro_updates.py"
        config_path = TOOL_ROOT / "config" / "post_sale_micro_updates.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "post_sale_micro_updates_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_buyer")
        self.assertEqual(config["dependsOn"]["postSaleImprovementLoopState"], "post_sale_improvement_loop_ready")
        self.assertEqual(config["privacyPolicy"], "store_applied_micro_update_counts_and_next_buyer_readiness_without_personal_data")
        self.assertIn("next_controlled_buyer_ready", config["allowedDecisions"])
        self.assertIn("revise_more", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for rel_path, markers in config["requiredMarkers"].items():
            path = PROJECT_ROOT / rel_path
            text = path.read_text(encoding="utf-8-sig")
            lowered = text.lower()
            if "public redaction" in lowered or "public_redaction" in lowered or "publicredaction" in lowered:
                with self.subTest(required_marker_source=rel_path):
                    self.assert_public_redaction_pointer(path)
                continue
            for marker in markers:
                with self.subTest(marker=marker):
                    self.assertIn(marker, text)

        for pattern in (
            "post_sale_micro_updates_ready",
            "post_sale_improvement_loop_state_invalid",
            "post_sale_improvement_loop_evidence_missing",
            "missing_marker",
            "post_sale_micro_updates_need_minimum_applied_updates",
            "next_buyer_readiness_steps_incomplete",
            "claims_risk_requires_pause_sales",
            "--use-latest-improvement-loop",
            "--confirm-next-buyer-check-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_buyer_readiness_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_buyer_readiness.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_buyer_readiness.json"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_buyer_readiness_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_private_buyer")
        self.assertEqual(config["dependsOn"]["postSaleMicroUpdatesState"], "post_sale_micro_updates_ready")
        self.assertEqual(config["privacyPolicy"], "store_next_buyer_readiness_counts_and_decision_without_personal_data_or_checkout_payloads")
        self.assertIn("share_private_link", config["allowedDecisions"])
        self.assertIn("hold_for_fix", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)

        for pattern in (
            "next_controlled_buyer_readiness_ready",
            "post_sale_micro_updates_state_invalid",
            "post_sale_micro_updates_evidence_missing",
            "share_private_link_requires_ready_private_link",
            "share_private_link_requires_single_buyer_slot",
            "claims_risk_requires_pause_sales",
            "--use-latest-micro-updates",
            "--confirm-followup-window-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_controlled_buyer_outcome_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_controlled_buyer_outcome.py"
        config_path = TOOL_ROOT / "config" / "next_controlled_buyer_outcome.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_CONTROLLED_BUYER_OUTCOME.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_controlled_buyer_outcome_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_controlled_private_buyer")
        self.assertEqual(config["dependsOn"]["nextControlledBuyerReadinessState"], "next_controlled_buyer_readiness_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_redacted_next_buyer_outcome_metrics_decision_and_actions_without_personal_data_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_private_slot", config["allowedDecisions"])
        self.assertIn("carefully_widen", config["allowedDecisions"])
        self.assertIn("hold_for_fix", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)

        for pattern in (
            "next_controlled_buyer_outcome_ready",
            "next_controlled_buyer_readiness_state_invalid",
            "next_controlled_buyer_readiness_evidence_missing",
            "carefully_widen_requires_completed_outcome",
            "repeat_private_slot_blocked_by_risk",
            "failed_or_refunded_outcome_requires_pause_sales",
            "--use-latest-readiness",
            "--confirm-next-decision-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_distribution_step_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_distribution_step.py"
        config_path = TOOL_ROOT / "config" / "controlled_distribution_step.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_DISTRIBUTION_STEP.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_distribution_step_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_distribution_step")
        self.assertEqual(config["dependsOn"]["nextControlledBuyerOutcomeState"], "next_controlled_buyer_outcome_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_distribution_action_metrics_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("repeat_private_slot", config["allowedSourceDecisions"])
        self.assertIn("carefully_widen", config["allowedSourceDecisions"])
        self.assertIn("hold_for_fix", config["allowedSourceDecisions"])
        self.assertIn("pause_sales", config["allowedSourceDecisions"])
        self.assertIn("prepare_single_private_slot", config["allowedActions"])
        self.assertIn("open_tiny_private_batch", config["allowedActions"])
        self.assertEqual(config["maximumTinyBatchSlots"], 3)
        self.assertEqual(config["maximumTinyAudienceInvites"], 5)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M72_DOC)

        for pattern in (
            "controlled_distribution_step_ready",
            "next_controlled_buyer_outcome_state_invalid",
            "next_controlled_buyer_outcome_evidence_missing",
            "controlled_distribution_action_mismatch",
            "carefully_widen_slot_limit_invalid",
            "pause_sales_requires_disabled_checkout",
            "--use-latest-outcome",
            "--confirm-selected-decision-matched",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_distribution_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_distribution_review.py"
        config_path = TOOL_ROOT / "config" / "controlled_distribution_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_DISTRIBUTION_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_distribution_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_distribution_review")
        self.assertEqual(config["dependsOn"]["controlledDistributionStepState"], "controlled_distribution_step_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_distribution_review_metrics_decision_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_single_private_slot", config["allowedSourceActions"])
        self.assertIn("open_tiny_private_batch", config["allowedSourceActions"])
        self.assertIn("prepare_buyer_facing_asset", config["allowedDecisions"])
        self.assertIn("repeat_distribution_step", config["allowedDecisions"])
        self.assertIn("pause_sales", config["allowedDecisions"])
        self.assertEqual(config["minimumPositiveSignalsForAsset"], 2)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M73_DOC)

        for pattern in (
            "controlled_distribution_review_ready",
            "controlled_distribution_step_state_invalid",
            "controlled_distribution_step_evidence_missing",
            "controlled_distribution_review_source_action_not_m72_action",
            "prepare_buyer_facing_asset_requires_positive_signals",
            "paused_distribution_requires_pause_sales",
            "--use-latest-distribution",
            "--confirm-next-decision-recorded",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_next_buyer_facing_asset_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "next_buyer_facing_asset.py"
        config_path = TOOL_ROOT / "config" / "next_buyer_facing_asset.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "NEXT_BUYER_FACING_ASSET.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "next_buyer_facing_asset_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_next_buyer_facing_asset")
        self.assertEqual(config["dependsOn"]["controlledDistributionReviewState"], "controlled_distribution_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_asset_scope_status_decision_and_review_metadata_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_buyer_facing_asset", config["allowedReviewDecisions"])
        self.assertIn("public_offer_section", config["allowedAssetTypes"])
        self.assertIn("ready_private_review", config["allowedAssetStatuses"])
        self.assertIn("prepare_private_review", config["allowedDecisions"])
        self.assertEqual(config["maximumAssetScopeItems"], 5)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M74_DOC)

        for pattern in (
            "next_buyer_facing_asset_ready",
            "controlled_distribution_review_state_invalid",
            "controlled_distribution_review_evidence_missing",
            "m73_did_not_select_prepare_buyer_facing_asset",
            "prepare_private_review_requires_safe_claims",
            "blocked_asset_requires_hold_or_pause",
            "--use-latest-review",
            "--confirm-private-review-owner",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_private_asset_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "private_asset_review.py"
        config_path = TOOL_ROOT / "config" / "private_asset_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "PRIVATE_ASSET_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "private_asset_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_private_asset_review")
        self.assertEqual(config["dependsOn"]["nextBuyerFacingAssetState"], "next_buyer_facing_asset_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_private_review_status_decision_and_risk_counts_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_private_review", config["allowedSourceDecisions"])
        self.assertIn("approved_private", config["allowedReviewStatuses"])
        self.assertIn("prepare_controlled_publication", config["allowedDecisions"])
        self.assertEqual(config["minimumReviewers"], 1)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M75_DOC)

        for pattern in (
            "private_asset_review_ready",
            "next_buyer_facing_asset_state_invalid",
            "next_buyer_facing_asset_evidence_missing",
            "m74_did_not_select_prepare_private_review",
            "prepare_controlled_publication_requires_safe_claims",
            "blocked_asset_review_requires_hold_or_pause",
            "--use-latest-asset",
            "--confirm-rollback-ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_publication_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_publication_gate.py"
        config_path = TOOL_ROOT / "config" / "controlled_publication_gate.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_PUBLICATION_GATE.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_publication_gate_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_publication_gate")
        self.assertEqual(config["dependsOn"]["privateAssetReviewState"], "private_asset_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_publication_channel_cap_decision_owner_and_risk_counts_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_controlled_publication", config["allowedSourceDecisions"])
        self.assertIn("private_link", config["allowedChannels"])
        self.assertIn("prepare_limited_publication", config["allowedDecisions"])
        self.assertEqual(config["maximumAudienceCap"], 10)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M76_DOC)

        for pattern in (
            "controlled_publication_gate_ready",
            "private_asset_review_state_invalid",
            "private_asset_review_evidence_missing",
            "m75_did_not_select_prepare_controlled_publication",
            "prepare_limited_publication_requires_pause_rule",
            "open_risks_block_limited_publication",
            "--use-latest-review",
            "--confirm-pause-rule-ready",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_limited_publication_draft_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "limited_publication_draft.py"
        config_path = TOOL_ROOT / "config" / "limited_publication_draft.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "LIMITED_PUBLICATION_DRAFT.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "limited_publication_draft_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_limited_publication_draft")
        self.assertEqual(config["dependsOn"]["controlledPublicationGateState"], "controlled_publication_gate_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_publication_draft_metadata_copy_checks_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("prepare_limited_publication", config["allowedSourceDecisions"])
        self.assertIn("private_link", config["allowedDraftChannels"])
        self.assertIn("ready_for_operator_review", config["allowedDecisions"])
        self.assertEqual(config["maximumAudienceCap"], 10)
        self.assertIn("rentabilidad asegurada", config["blockedClaimPatterns"])
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M77_DOC)

        for pattern in (
            "limited_publication_draft_ready",
            "controlled_publication_gate_state_invalid",
            "controlled_publication_gate_evidence_missing",
            "m76_did_not_select_prepare_limited_publication",
            "ready_for_operator_review_requires_basic_user_instructions",
            "blocked_claims_block_operator_review",
            "--use-latest-gate",
            "--confirm-safe-copy",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_operator_publication_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "operator_publication_review.py"
        config_path = TOOL_ROOT / "config" / "operator_publication_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "OPERATOR_PUBLICATION_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "operator_publication_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_operator_publication_review")
        self.assertEqual(config["dependsOn"]["limitedPublicationDraftState"], "limited_publication_draft_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_operator_review_status_decision_owner_and_risk_counts_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("ready_for_operator_review", config["allowedSourceDecisions"])
        self.assertIn("approved_manual_review", config["allowedReviewStatuses"])
        self.assertIn("approve_manual_limited_publication", config["allowedDecisions"])
        self.assertEqual(config["minimumReviewers"], 1)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M78_DOC)

        for pattern in (
            "operator_publication_review_ready",
            "limited_publication_draft_state_invalid",
            "limited_publication_draft_evidence_missing",
            "m77_did_not_select_ready_for_operator_review",
            "approve_manual_limited_publication_requires_basic_user_flow",
            "blocked_operator_review_requires_hold_or_pause",
            "--use-latest-draft",
            "--confirm-draft-reviewed",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_manual_limited_publication_record_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "manual_limited_publication_record.py"
        config_path = TOOL_ROOT / "config" / "manual_limited_publication_record.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "MANUAL_LIMITED_PUBLICATION_RECORD.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "manual_limited_publication_record_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_manual_limited_publication_record")
        self.assertEqual(config["dependsOn"]["operatorPublicationReviewState"], "operator_publication_review_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_manual_publication_channel_url_owner_time_audience_counts_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("approve_manual_limited_publication", config["allowedSourceDecisions"])
        self.assertIn("private_link", config["allowedChannels"])
        self.assertIn("record_manual_publication", config["allowedDecisions"])
        self.assertEqual(config["maximumAudienceCap"], 10)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M79_DOC)

        for pattern in (
            "manual_limited_publication_record_ready",
            "operator_publication_review_state_invalid",
            "operator_publication_review_evidence_missing",
            "m78_did_not_select_approve_manual_limited_publication",
            "manual_limited_publication_redacted_url_missing_or_unsafe",
            "record_manual_publication_requires_monitoring",
            "--use-latest-review",
            "--confirm-redacted-url",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_manual_publication_monitor_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "manual_publication_monitor.py"
        config_path = TOOL_ROOT / "config" / "manual_publication_monitor.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "MANUAL_PUBLICATION_MONITOR.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "manual_publication_monitor_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_manual_publication_monitor")
        self.assertEqual(config["dependsOn"]["manualLimitedPublicationRecordState"], "manual_limited_publication_record_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_monitoring_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertIn("record_manual_publication", config["allowedSourceDecisions"])
        self.assertIn("prepare_traffic_expansion_review", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["maximumIncidents"], 0)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M80_DOC)

        for pattern in (
            "manual_publication_monitor_ready",
            "manual_limited_publication_record_state_invalid",
            "manual_limited_publication_record_evidence_missing",
            "m79_did_not_select_record_manual_publication",
            "prepare_traffic_expansion_review_requires_observation_time",
            "risky_counts_block_traffic_expansion_review",
            "--use-latest-record",
            "--confirm-redacted-metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)

    def test_controlled_traffic_expansion_review_gate_is_present(self):
        tool_path = TOOL_ROOT / "tools" / "controlled_traffic_expansion_review.py"
        config_path = TOOL_ROOT / "config" / "controlled_traffic_expansion_review.json"
        public_doc = PROJECT_ROOT / "docs" / "sales" / "CONTROLLED_TRAFFIC_EXPANSION_REVIEW.md"
        py_compile.compile(str(tool_path), doraise=True)
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        tool_text = tool_path.read_text(encoding="utf-8")

        self.assertEqual(config["state"], "controlled_traffic_expansion_review_ready")
        self.assertEqual(config["offerId"], "sqx_edge_pro_controlled_traffic_expansion_review")
        self.assertEqual(config["dependsOn"]["manualPublicationMonitorState"], "manual_publication_monitor_ready")
        self.assertEqual(
            config["privacyPolicy"],
            "store_only_redacted_monitoring_counts_decision_owner_and_next_action_without_buyer_identity_checkout_payloads_or_license_files",
        )
        self.assertEqual(
            config["reviewPolicy"],
            "approve_only_tiny_controlled_traffic_expansion_after_m80_monitoring_support_claims_refunds_incidents_rollback_and_pause_rule_are_clean",
        )
        self.assertIn("prepare_traffic_expansion_review", config["allowedSourceDecisions"])
        self.assertIn("approve_tiny_traffic_expansion", config["allowedDecisions"])
        self.assertEqual(config["minimumObservationHours"], 24)
        self.assertEqual(config["maximumIncidents"], 0)
        self.assertEqual(config["minimumPositiveSignalsForTinyExpansion"], 1)
        for required in config["requiredFiles"]:
            with self.subTest(required=required):
                self.assertTrue((PROJECT_ROOT / required).is_file(), required)
        self.assert_public_redaction_pointer(public_doc)
        self.assert_public_redaction_pointer(MONETIZATION_M81_DOC)

        for pattern in (
            "controlled_traffic_expansion_review_ready",
            "manual_publication_monitor_state_invalid",
            "manual_publication_monitor_evidence_missing",
            "m80_did_not_select_prepare_traffic_expansion_review",
            "approve_tiny_traffic_expansion_requires_observation_time",
            "risky_counts_block_tiny_traffic_expansion",
            "--use-latest-record",
            "--confirm-redacted-metrics",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, tool_text)


if __name__ == "__main__":
    unittest.main()
