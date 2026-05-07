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
                "js/modules/workflow.js",
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
            "js/modules/workflow.js",
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
        workflow_js = (APP_ROOT / "js" / "modules" / "workflow.js").read_text(encoding="utf-8-sig")
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
        self.assertIn("SQX.workflow", workflow_js)
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
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "hotfix_rollback_release_ready")
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "hotfix_rollback_release_ready")
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
            "setSettingsOpen",
            "writeConfigInputs",
            "bulkGenerateLabel",
            "configSaveBody",
            "configSaveError",
            "configSaveStatus",
            "generateAllConfirmMessage",
            "generateAllResultLines",
            "generateAllResultSummary",
            "generateAllStartMessage",
            "generateAllTrace",
            "generateErrorResult",
            "generateOneResult",
            "generateOneStartMessage",
            "enrichMiningsWithSymbolInfo",
            "miningRowsHtml",
            "miningsCountLabel",
            "outputCountLabel",
            "outputListHtml",
            "outputState",
            "openOutputDisconnectedStatus",
            "openOutputErrorStatus",
            "openOutputSuccessStatus",
            "prepareRequestOptions",
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
        self.assertEqual(product_manifest["upgrade"]["checkout"]["status"], "hotfix_rollback_release_ready")
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
        self.assertEqual(product_manifest["upgrade"]["checkout"]["automation"]["status"], "hotfix_rollback_release_ready")
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

    def test_monetization_docs_capture_m1_to_m44_decisions(self):
        roadmap = MONETIZATION_ROADMAP_DOC.read_text(encoding="utf-8-sig")
        m1 = MONETIZATION_M1_DOC.read_text(encoding="utf-8-sig")
        m2 = MONETIZATION_M2_DOC.read_text(encoding="utf-8-sig")
        m3 = MONETIZATION_M3_DOC.read_text(encoding="utf-8-sig")
        m4 = MONETIZATION_M4_DOC.read_text(encoding="utf-8-sig")
        m5 = MONETIZATION_M5_DOC.read_text(encoding="utf-8-sig")
        m6 = MONETIZATION_M6_DOC.read_text(encoding="utf-8-sig")
        m7 = MONETIZATION_M7_DOC.read_text(encoding="utf-8-sig")
        m8 = MONETIZATION_M8_DOC.read_text(encoding="utf-8-sig")
        m9 = MONETIZATION_M9_DOC.read_text(encoding="utf-8-sig")
        m10 = MONETIZATION_M10_DOC.read_text(encoding="utf-8-sig")
        m11 = MONETIZATION_M11_DOC.read_text(encoding="utf-8-sig")
        m12 = MONETIZATION_M12_DOC.read_text(encoding="utf-8-sig")
        m13 = MONETIZATION_M13_DOC.read_text(encoding="utf-8-sig")
        m14 = MONETIZATION_M14_DOC.read_text(encoding="utf-8-sig")
        m15 = MONETIZATION_M15_DOC.read_text(encoding="utf-8-sig")
        m16 = MONETIZATION_M16_DOC.read_text(encoding="utf-8-sig")
        m17 = MONETIZATION_M17_DOC.read_text(encoding="utf-8-sig")
        m18 = MONETIZATION_M18_DOC.read_text(encoding="utf-8-sig")
        m19 = MONETIZATION_M19_DOC.read_text(encoding="utf-8-sig")
        m20 = MONETIZATION_M20_DOC.read_text(encoding="utf-8-sig")
        m21 = MONETIZATION_M21_DOC.read_text(encoding="utf-8-sig")
        m22 = MONETIZATION_M22_DOC.read_text(encoding="utf-8-sig")
        m23 = MONETIZATION_M23_DOC.read_text(encoding="utf-8-sig")
        m24 = MONETIZATION_M24_DOC.read_text(encoding="utf-8-sig")
        m25 = MONETIZATION_M25_DOC.read_text(encoding="utf-8-sig")
        m26 = MONETIZATION_M26_DOC.read_text(encoding="utf-8-sig")
        m27 = MONETIZATION_M27_DOC.read_text(encoding="utf-8-sig")
        m28 = MONETIZATION_M28_DOC.read_text(encoding="utf-8-sig")
        m29 = MONETIZATION_M29_DOC.read_text(encoding="utf-8-sig")
        m30 = MONETIZATION_M30_DOC.read_text(encoding="utf-8-sig")
        m31 = MONETIZATION_M31_DOC.read_text(encoding="utf-8-sig")
        m32 = MONETIZATION_M32_DOC.read_text(encoding="utf-8-sig")
        m33 = MONETIZATION_M33_DOC.read_text(encoding="utf-8-sig")
        m34 = MONETIZATION_M34_DOC.read_text(encoding="utf-8-sig")
        m35 = MONETIZATION_M35_DOC.read_text(encoding="utf-8-sig")
        m36 = MONETIZATION_M36_DOC.read_text(encoding="utf-8-sig")
        m37 = MONETIZATION_M37_DOC.read_text(encoding="utf-8-sig")
        m38 = MONETIZATION_M38_DOC.read_text(encoding="utf-8-sig")
        m39 = MONETIZATION_M39_DOC.read_text(encoding="utf-8-sig")
        m40 = MONETIZATION_M40_DOC.read_text(encoding="utf-8-sig")
        m41 = MONETIZATION_M41_DOC.read_text(encoding="utf-8-sig")
        m42 = MONETIZATION_M42_DOC.read_text(encoding="utf-8-sig")
        m43 = MONETIZATION_M43_DOC.read_text(encoding="utf-8-sig")
        m44 = MONETIZATION_M44_DOC.read_text(encoding="utf-8-sig")
        sales_runbook = (PROJECT_ROOT / "docs" / "sales" / "SALES_FULFILLMENT_RUNBOOK.md").read_text(encoding="utf-8-sig")
        webhook_notes = (PROJECT_ROOT / "docs" / "sales" / "WEBHOOK_AUTOMATION_NOTES.md").read_text(encoding="utf-8-sig")
        receiver_ops = (PROJECT_ROOT / "docs" / "sales" / "WEBHOOK_RECEIVER_OPERATIONS.md").read_text(encoding="utf-8-sig")
        operator_ops = (PROJECT_ROOT / "docs" / "sales" / "FULFILLMENT_OPERATOR_PLAYBOOK.md").read_text(encoding="utf-8-sig")
        relay_ops = (PROJECT_ROOT / "docs" / "sales" / "RELAY_INGEST_NOTES.md").read_text(encoding="utf-8-sig")
        relay_service_ops = (PROJECT_ROOT / "docs" / "sales" / "RELAY_SERVICE_OPERATIONS.md").read_text(encoding="utf-8-sig")
        commercial_readme = (PROJECT_ROOT / "docs" / "COMMERCIAL_README.md").read_text(encoding="utf-8-sig")
        public_roadmap = (PROJECT_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(encoding="utf-8-sig")
        next_steps = (PROJECT_ROOT / "docs" / "MODULARIZATION_NEXT_STEPS.md").read_text(encoding="utf-8-sig")

        self.assertIn("Phase M1", roadmap)
        self.assertIn("Phase M2", roadmap)
        self.assertIn("Phase M3", roadmap)
        self.assertIn("Phase M4", roadmap)
        self.assertIn("Phase M5", roadmap)
        self.assertIn("Phase M6", roadmap)
        self.assertIn("Phase M7", roadmap)
        self.assertIn("Phase M8", roadmap)
        self.assertIn("Phase M9", roadmap)
        self.assertIn("Phase M10", roadmap)
        self.assertIn("Phase M11", roadmap)
        self.assertIn("Phase M12", roadmap)
        self.assertIn("Phase M13", roadmap)
        self.assertIn("Phase M14", roadmap)
        self.assertIn("Phase M15", roadmap)
        self.assertIn("Phase M16", roadmap)
        self.assertIn("Phase M17", roadmap)
        self.assertIn("Phase M18", roadmap)
        self.assertIn("Phase M19", roadmap)
        self.assertIn("Phase M20", roadmap)
        self.assertIn("Phase M21", roadmap)
        self.assertIn("Phase M22", roadmap)
        self.assertIn("Phase M23", roadmap)
        self.assertIn("Phase M24", roadmap)
        self.assertIn("Phase M25", roadmap)
        self.assertIn("Phase M26", roadmap)
        self.assertIn("Phase M27", roadmap)
        self.assertIn("Phase M28", roadmap)
        self.assertIn("Phase M29", roadmap)
        self.assertIn("Phase M30", roadmap)
        self.assertIn("Phase M31", roadmap)
        self.assertIn("Phase M32", roadmap)
        self.assertIn("Phase M33", roadmap)
        self.assertIn("Phase M34", roadmap)
        self.assertIn("Phase M35", roadmap)
        self.assertIn("Phase M36", roadmap)
        self.assertIn("Phase M37", roadmap)
        self.assertIn("Phase M38", roadmap)
        self.assertIn("Phase M39", roadmap)
        self.assertIn("Phase M40", roadmap)
        self.assertIn("Phase M41", roadmap)
        self.assertIn("Phase M42", roadmap)
        self.assertIn("Phase M43", roadmap)
        self.assertIn("Phase M44", roadmap)
        self.assertIn("Phase M2: design licensing and access model. Done.", next_steps)
        self.assertIn("Phase M3: define distribution channels and paid delivery flow. Done.", next_steps)
        self.assertIn("Phase M4: separate Free/Pro/internal product packaging. Done.", next_steps)
        self.assertIn("Phase M5: prepare branding and go-to-market assets. Done.", next_steps)
        self.assertIn("Phase M6: run security and distribution audit. Done.", next_steps)
        self.assertIn("Phase M7: design support and diagnostics flow. Done.", next_steps)
        self.assertIn("Phase M8: implement offline signed license activation. Done.", next_steps)
        self.assertIn("Phase M9: prepare production license key management and release guardrails. Done.", next_steps)
        self.assertIn("Phase M10: add manual Pro license issuer for first paid sales. Done.", next_steps)
        self.assertIn("Phase M11: prepare checkout wiring and manual sales fulfillment. Done.", next_steps)
        self.assertIn("Phase M12: prepare local webhook-to-fulfillment automation bridge. Done.", next_steps)
        self.assertIn("Phase M13: add private receiver with persistent queue and deduplication. Done.", next_steps)
        self.assertIn("Phase M14: add operator states, retries and dashboard queue cockpit. Done.", next_steps)
        self.assertIn("Phase M15: add trusted relay ingest for remote webhook forwarding. Done.", next_steps)
        self.assertIn("Phase M16: add deployable remote relay service with queue and dispatch. Done.", next_steps)
        self.assertIn("Phase M17: harden relay deployment with config checks, operator token and worker. Done.", next_steps)
        self.assertIn("Phase M18: add relay observability, snapshots and simulated purchase flow. Done.", next_steps)
        self.assertIn("Phase M19: prepare production relay deployment package and provider runbook. Done.", next_steps)
        self.assertIn("Phase M20: add relay staging validation kit and go/no-go checklist. Done.", next_steps)
        self.assertIn("Phase M21: choose Render staging path and add evidence go/no-go collector. Done.", next_steps)
        self.assertIn("Phase M22: add Render API preflight for key, owner and blueprint validation. Done.", next_steps)
        self.assertIn("Phase M23: add Render credential handshake and no-password guardrail. Done.", next_steps)
        self.assertIn("Phase M24: add Render staging go/no-go gate before live deployment. Done.", next_steps)
        self.assertIn("Phase M25: add Render staging launch pack for audited manual deployment. Done.", next_steps)
        self.assertIn("Phase M26: add Render staging secrets kit for safe provider setup. Done.", next_steps)
        self.assertIn("Phase M27: add local ingest tunnel readiness check before Render staging. Done.", next_steps)
        self.assertIn("Phase M28: add local ingest tunnel launcher and provider detection. Done.", next_steps)
        self.assertIn("Phase M29: add local ingest staging session orchestrator. Done.", next_steps)
        self.assertIn("Phase M30: add local ingest Render handoff pack. Done.", next_steps)
        self.assertIn("Phase M31: add Render staging apply gate for handoff confirmation and remote gate evidence. Done.", next_steps)
        self.assertIn("Phase M32: add Render staging purchase drill for webhook, queue and dispatch evidence. Done.", next_steps)
        self.assertIn("Phase M33: add checkout live readiness gate for Lemon Squeezy URLs, variants and rollback. Done.", next_steps)
        self.assertIn("Phase M34: add commercial release candidate gate for ZIP, readiness, pilot purchase and rollback evidence. Done.", next_steps)
        self.assertIn("Phase M35: add pilot purchase kit for private checkout, license issue, delivery and import evidence. Done.", next_steps)
        self.assertIn("Phase M36: add limited public launch gate for first sale cap, support, checkout and rollback evidence. Done.", next_steps)
        self.assertIn("Phase M37: add post-launch control for sales, activations, support, refunds and scale decision evidence. Done.", next_steps)
        self.assertIn("Phase M38: add commercial feedback loop for issue classification, pricing, copy and version decisions. Done.", next_steps)
        self.assertIn("Phase M39: add public offer pack for controlled offer copy, FAQ, release notes and buyer steps. Done.", next_steps)
        self.assertIn("Phase M40: add launch assets kit for screenshots, copy, release draft and publication checklist. Done.", next_steps)
        self.assertIn("Phase M41: add public release gate for tag, GitHub Release, ZIP, SHA256, support and rollback. Done.", next_steps)
        self.assertIn("Phase M42: add release publication record for published tag, release, ZIP, SHA256 and rollback evidence. Done.", next_steps)
        self.assertIn("Phase M43: add post-release monitor for incidents, activation errors, support, refunds and scale decision. Done.", next_steps)
        self.assertIn("Phase M44: add hotfix/rollback release kit for action owner, notes, comms, verification and closure evidence. Done.", next_steps)

        m1_patterns = [
            "SQX Edge Pro",
            "24 EUR/mes",
            "199 EUR/ano",
            "Setup Assist",
            "Premium Template Pack 1",
        ]
        for pattern in m1_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m1)

        m2_patterns = [
            "licencia local firmada",
            "activacion manual por archivo",
            "validacion offline",
            "No basta con ocultar botones en HTML/JS.",
            "required_feature",
            "project_generator.generate",
            "strategy_cleaner.apply",
            "sin trial automatico al inicio",
            "expiracion sin borrado de datos",
        ]
        for pattern in m2_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m2)

        m3_patterns = [
            "Lemon Squeezy como canal principal",
            "ZIP portable de SQX Edge",
            "GitHub Releases",
            "Gumroad como alternativa",
            "Stripe Payment Links solo como alternativa",
            "Paddle como opcion futura",
            "Manual License Flow For V1",
            "first paid beta: Option A",
            "Enable license keys with activation limit 1",
            "SQX_Edge_Suite_Portable_vX.Y.Z.zip",
        ]
        for pattern in m3_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m3)

        m4_patterns = [
            "product_manifest.json",
            "license_manager.py",
            "GET /api/license/status",
            "POST /api/license/check",
            "SQX.license",
            "project_generator.generate",
            "strategy_cleaner.apply",
            "modo `internal`",
            "una licencia sin firma no activa Pro",
        ]
        for pattern in m4_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m4)

        m5_patterns = [
            "SQX Edge Pro",
            "De idea a pipeline operativo SQX",
            "24 EUR/mes",
            "199 EUR/ano",
            "Setup Assist",
            "no promete rentabilidad",
            "Landing Page Copy",
            "Video demo recomendado",
        ]
        for pattern in m5_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m5)
        self.assertIn("SQX Edge Pro", commercial_readme)
        self.assertIn("Responsible Notice", commercial_readme)
        self.assertIn("SQX Edge Free public beta", public_roadmap)

        m6_patterns = [
            "Threat Model",
            "Finding Discovery",
            "Validation",
            "Attack Path Analysis",
            "audit_distribution.ps1",
            "SHA256",
            "local_api_only",
            "project_generator.generate",
            "strategy_cleaner.apply",
            "config/license.json",
        ]
        for pattern in m6_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m6)

        m7_patterns = [
            "GET /api/support/diagnostics",
            "Generar diagnostico",
            "privacy.safe_to_send = true",
            "paths = redacted",
            "license_payload = excluded",
            "strategy_files = excluded",
            "sin telemetria",
        ]
        for pattern in m7_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m7)

        m8_patterns = [
            "rsa_sha256_pkcs1_v1_5",
            "RS256",
            "GET /api/license/status",
            "POST /api/license/import",
            "POST /api/license/clear",
            "license_signer.py",
            "private key",
            "config/license.json",
            "pro_active",
        ]
        for pattern in m8_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m8)

        m9_patterns = [
            "license_keypair.ps1",
            "license_signer.py",
            "private key",
            "public key",
            "product_manifest.json",
            "never_commit_never_ship",
            "package_portable.ps1",
            "audit_distribution.ps1",
            "release_checklist.ps1",
            "placeholder",
        ]
        for pattern in m9_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m9)

        m10_patterns = [
            "license_issue.py",
            "license_signer.py",
            "pro_monthly",
            "pro_annual",
            "customer-name",
            "order-id",
            "machine_limit",
            "support_level",
            "package_portable.ps1",
            "audit_distribution.ps1",
        ]
        for pattern in m10_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m10)

        m11_patterns = [
            "Lemon Squeezy",
            "Gumroad",
            "checkout.primaryUrl",
            "license-checkout-link",
            "license_issue.py",
            "prepare_customer_delivery.ps1",
            "ZIP portable",
            "SQX_Edge_Pro_license.json",
            "webhooks",
            "Estado: Done.",
        ]
        for pattern in m11_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m11)
        self.assertIn("Sale To Delivery", sales_runbook)
        self.assertIn("Customer Email Template", sales_runbook)

        m12_patterns = [
            "fulfillment_request.py",
            "fulfill_from_request.ps1",
            "X-Signature",
            "HMAC SHA256",
            "order_created",
            "subscription_payment_success",
            "eligible_for_fulfillment",
            "Lemon Squeezy",
            "Estado: Done.",
        ]
        for pattern in m12_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m12)
        self.assertIn("Manual To Assisted Automation", webhook_notes)
        self.assertIn("provider_event_id", webhook_notes)

        m13_patterns = [
            "/api/fulfillment/webhook/lemon",
            "/api/fulfillment/requests",
            "/api/fulfillment/process",
            "provider_event_id",
            "private_receiver_ready",
            "SQX_LEMON_WEBHOOK_SECRET",
            "deduplication",
            "persistent queue",
            "Lemon Squeezy",
            "Estado: Done.",
        ]
        for pattern in m13_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m13)
        self.assertIn("Receiver Daily Flow", receiver_ops)
        self.assertIn("Duplicate Event Rule", receiver_ops)

        m14_patterns = [
            "operator_retry_ready",
            "/api/fulfillment/request-status",
            "manual_retry_with_attempt_log",
            "operator_status",
            "attempt_count",
            "queue cockpit",
            "dashboard",
            "Estado: Done.",
        ]
        for pattern in m14_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m14)
        self.assertIn("Retry Loop", operator_ops)
        self.assertIn("Ignore And Requeue Rules", operator_ops)

        m15_patterns = [
            "relay_ingest_ready",
            "/api/fulfillment/relay-ingest",
            "X-SQX-Relay-Signature",
            "SQX_FULFILLMENT_RELAY_SECRET",
            "trusted_remote_relay_signed_bundle",
            "relay_bundle.py",
            "relay_event_id",
            "Estado: Done.",
        ]
        for pattern in m15_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m15)
        self.assertIn("Trusted Relay Flow", relay_ops)
        self.assertIn("Security Notes", relay_ops)

        m16_patterns = [
            "remote_relay_ready",
            "backend/sqx-edge-relay",
            "/relay/health",
            "/relay/webhook/lemon",
            "/relay/dispatch",
            "exponential_backoff_remote_queue",
            "SQX_LOCAL_INGEST_URL",
            "Estado: Done.",
        ]
        for pattern in m16_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m16)
        self.assertIn("Dispatch Loop", relay_service_ops)
        self.assertIn("Failure And Requeue", relay_service_ops)

        m17_patterns = [
            "relay_deployment_ready",
            "/relay/config-check",
            "SQX_RELAY_OPERATOR_TOKEN",
            "dispatch_worker.py",
            "supervised_dispatch_loop",
            ".env.example",
            "Estado: Done.",
        ]
        for pattern in m17_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m17)
        self.assertIn("Production Readiness", relay_service_ops)
        self.assertIn("Worker Operation", relay_service_ops)

        m18_patterns = [
            "relay_observability_ready",
            "/relay/observability",
            "/relay/observability/snapshot",
            "relay_events.jsonl",
            "simulate_purchase_flow.py",
            "jsonl_events_and_queue_snapshots",
            "Estado: Done.",
        ]
        for pattern in m18_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m18)
        self.assertIn("Observability", relay_service_ops)
        self.assertIn("Purchase Flow Simulation", relay_service_ops)

        m19_patterns = [
            "relay_production_deploy_ready",
            "Dockerfile",
            "deployment_check.py",
            "render.yaml.example",
            "railway.json",
            "fly.toml.example",
            "sqx-edge-relay.service",
            "Estado: Done.",
        ]
        for pattern in m19_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m19)
        deployment_guide = (PROJECT_ROOT / "docs" / "sales" / "RELAY_DEPLOYMENT_GUIDE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render", deployment_guide)
        self.assertIn("Railway", deployment_guide)
        self.assertIn("Fly.io", deployment_guide)
        self.assertIn("VPS", deployment_guide)

        m20_patterns = [
            "relay_staging_ready",
            ".env.staging.example",
            "staging_smoke.py",
            "wh_m20_staging_demo",
            "Go/No-Go",
            "Estado: Done.",
        ]
        for pattern in m20_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m20)
        staging_checklist = (PROJECT_ROOT / "docs" / "sales" / "RELAY_STAGING_CHECKLIST.md").read_text(encoding="utf-8-sig")
        self.assertIn("Remote Smoke", staging_checklist)
        self.assertIn("Signed Webhook Smoke", staging_checklist)
        self.assertIn("Lemon Test", staging_checklist)

        m21_patterns = [
            "relay_staging_execution_ready",
            "Render",
            "render.staging.yaml.example",
            "staging_evidence.py",
            "remote_staging_url_not_tested",
            "Estado: Done.",
        ]
        for pattern in m21_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m21)
        render_runbook = (PROJECT_ROOT / "docs" / "sales" / "RELAY_RENDER_STAGING_RUNBOOK.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render", render_runbook)
        self.assertIn("staging_evidence.py", render_runbook)
        self.assertIn("GO", render_runbook)
        self.assertIn("NO-GO", render_runbook)

        m22_patterns = [
            "relay_render_api_preflight_ready",
            "render_api_preflight.py",
            "RENDER_API_KEY",
            "RENDER_OWNER_ID",
            "blueprints/validate",
            "Estado: Done.",
        ]
        for pattern in m22_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m22)
        render_api_preflight = (PROJECT_ROOT / "docs" / "sales" / "RENDER_API_PREFLIGHT.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render API key", render_api_preflight)
        self.assertIn("render_api_key_missing", render_api_preflight)
        self.assertIn("valid: true", render_api_preflight)

        m23_patterns = [
            "relay_render_credentials_handshake_ready",
            "render_credentials_handshake.py",
            "api_key_only_no_account_password",
            "RENDER_ACCOUNT_PASSWORD",
            "render_preflight_evidence",
            "Estado: Done.",
        ]
        for pattern in m23_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m23)
        render_handshake = (PROJECT_ROOT / "docs" / "sales" / "RENDER_CREDENTIAL_HANDSHAKE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render Credential Handshake", render_handshake)
        self.assertIn("NO-GO", render_handshake)
        self.assertIn("RENDER_PASSWORD", render_handshake)

        m24_patterns = [
            "relay_render_staging_gate_ready",
            "render_staging_gate.py",
            "render_credentials_handshake.py",
            "staging_evidence.py",
            "render_staging_gate",
            "Estado: Done.",
        ]
        for pattern in m24_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m24)
        render_gate = (PROJECT_ROOT / "docs" / "sales" / "RENDER_STAGING_GATE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render Staging Gate", render_gate)
        self.assertIn("render_staging_gate.py", render_gate)
        self.assertIn("GO", render_gate)
        self.assertIn("NO-GO", render_gate)

        m25_patterns = [
            "relay_render_staging_launch_pack_ready",
            "render_staging_launch_pack.py",
            "SHA256",
            "render.staging.yaml.example",
            "render_staging_launch_pack",
            "Estado: Done.",
        ]
        for pattern in m25_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m25)
        render_launch_pack = (PROJECT_ROOT / "docs" / "sales" / "RENDER_STAGING_LAUNCH_PACK.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render Staging Launch Pack", render_launch_pack)
        self.assertIn("SQX_LEMON_WEBHOOK_SECRET", render_launch_pack)
        self.assertIn("render_staging_launch_pack.py", render_launch_pack)

        m26_patterns = [
            "relay_render_staging_secrets_kit_ready",
            "render_staging_secrets_kit.py",
            "SQX_LOCAL_INGEST_URL",
            "render_staging_secrets_kit",
            "Estado: Done.",
        ]
        for pattern in m26_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m26)
        render_secrets_kit = (PROJECT_ROOT / "docs" / "sales" / "RENDER_STAGING_SECRETS_KIT.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render Staging Secrets Kit", render_secrets_kit)
        self.assertIn("SQX_FULFILLMENT_RELAY_SECRET", render_secrets_kit)
        self.assertIn("render_staging_gate.py", render_secrets_kit)

        m27_patterns = [
            "relay_local_ingest_tunnel_check_ready",
            "local_ingest_tunnel_check.py",
            "SQX_LOCAL_INGEST_URL",
            "/api/fulfillment/relay-ingest",
            "Estado: Done.",
        ]
        for pattern in m27_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m27)
        local_ingest_check = (PROJECT_ROOT / "docs" / "sales" / "LOCAL_INGEST_TUNNEL_CHECK.md").read_text(encoding="utf-8-sig")
        self.assertIn("Local Ingest Tunnel Check", local_ingest_check)
        self.assertIn("--send-bundle", local_ingest_check)
        self.assertIn("/api/health", local_ingest_check)

        m28_patterns = [
            "relay_local_ingest_tunnel_launcher_ready",
            "local_ingest_tunnel_launcher.py",
            "cloudflared",
            "ngrok",
            "localtunnel",
            "Estado: Done.",
        ]
        for pattern in m28_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m28)
        local_ingest_launcher = (PROJECT_ROOT / "docs" / "sales" / "LOCAL_INGEST_TUNNEL_LAUNCHER.md").read_text(encoding="utf-8-sig")
        self.assertIn("Local Ingest Tunnel Launcher", local_ingest_launcher)
        self.assertIn("--start", local_ingest_launcher)
        self.assertIn("local_ingest_tunnel_check.py", local_ingest_launcher)

        m29_patterns = [
            "relay_local_ingest_staging_session_ready",
            "local_ingest_staging_session.py",
            "--start-backend",
            "--start-tunnel",
            "Estado: Done.",
        ]
        for pattern in m29_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m29)
        local_ingest_session = (PROJECT_ROOT / "docs" / "sales" / "LOCAL_INGEST_STAGING_SESSION.md").read_text(encoding="utf-8-sig")
        self.assertIn("Local Ingest Staging Session", local_ingest_session)
        self.assertIn("--send-bundle", local_ingest_session)
        self.assertIn("SQX_FULFILLMENT_RELAY_SECRET", local_ingest_session)

        m30_patterns = [
            "relay_local_ingest_render_handoff_ready",
            "local_ingest_render_handoff.py",
            "SQX_LOCAL_INGEST_URL",
            "--use-latest-session",
            "Estado: Done.",
        ]
        for pattern in m30_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m30)
        local_ingest_handoff = (PROJECT_ROOT / "docs" / "sales" / "LOCAL_INGEST_RENDER_HANDOFF.md").read_text(encoding="utf-8-sig")
        self.assertIn("Local Ingest Render Handoff", local_ingest_handoff)
        self.assertIn("SQX_LOCAL_INGEST_URL", local_ingest_handoff)
        self.assertIn("render_staging_gate.py", local_ingest_handoff)

        m31_patterns = [
            "relay_render_staging_apply_gate_ready",
            "render_staging_apply_gate.py",
            "--confirm-env-applied",
            "render_staging_gate.py",
            "Estado: Done.",
        ]
        for pattern in m31_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m31)
        render_apply_gate = (PROJECT_ROOT / "docs" / "sales" / "RENDER_STAGING_APPLY_GATE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render Staging Apply Gate", render_apply_gate)
        self.assertIn("--confirm-env-applied", render_apply_gate)
        self.assertIn("render_staging_gate.py", render_apply_gate)

        m32_patterns = [
            "relay_render_staging_purchase_drill_ready",
            "render_staging_purchase_drill.py",
            "--send-webhook",
            "--dispatch",
            "Estado: Done.",
        ]
        for pattern in m32_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m32)
        render_purchase_drill = (PROJECT_ROOT / "docs" / "sales" / "RENDER_STAGING_PURCHASE_DRILL.md").read_text(encoding="utf-8-sig")
        self.assertIn("Render Staging Purchase Drill", render_purchase_drill)
        self.assertIn("/relay/webhook/lemon", render_purchase_drill)
        self.assertIn("/relay/dispatch", render_purchase_drill)

        m33_patterns = [
            "checkout_live_readiness_ready",
            "checkout_live_readiness.py",
            "Lemon Squeezy",
            "rollback",
            "Estado: Done.",
        ]
        for pattern in m33_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m33)
        checkout_live_readiness = (PROJECT_ROOT / "docs" / "sales" / "CHECKOUT_LIVE_READINESS.md").read_text(encoding="utf-8-sig")
        self.assertIn("Checkout Live Readiness", checkout_live_readiness)
        self.assertIn("providerVariantId", checkout_live_readiness)
        self.assertIn("rollback", checkout_live_readiness)

        m34_patterns = [
            "commercial_release_candidate_ready",
            "commercial_release_candidate.py",
            "pilot purchase",
            "ZIP SHA256",
            "Estado: Done.",
        ]
        for pattern in m34_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m34)
        commercial_rc = (PROJECT_ROOT / "docs" / "sales" / "COMMERCIAL_RELEASE_CANDIDATE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Commercial Release Candidate", commercial_rc)
        self.assertIn("pilot purchase", commercial_rc)
        self.assertIn("ZIP SHA256", commercial_rc)

        m35_patterns = [
            "pilot_purchase_kit_ready",
            "pilot_purchase_kit.py",
            "license_issue.py",
            "prepare_customer_delivery.ps1",
            "Estado: Done.",
        ]
        for pattern in m35_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m35)
        pilot_purchase_kit = (PROJECT_ROOT / "docs" / "sales" / "PILOT_PURCHASE_KIT.md").read_text(encoding="utf-8-sig")
        self.assertIn("Pilot Purchase Kit", pilot_purchase_kit)
        self.assertIn("license_issue.py", pilot_purchase_kit)
        self.assertIn("prepare_customer_delivery.ps1", pilot_purchase_kit)

        m36_patterns = [
            "limited_public_launch_ready",
            "limited_public_launch.py",
            "first sale cap",
            "support inbox",
            "Estado: Done.",
        ]
        for pattern in m36_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m36)
        limited_launch = (PROJECT_ROOT / "docs" / "sales" / "LIMITED_PUBLIC_LAUNCH.md").read_text(encoding="utf-8-sig")
        self.assertIn("Limited Public Launch", limited_launch)
        self.assertIn("limited_public_launch.py", limited_launch)
        self.assertIn("first sale cap", limited_launch)

        m37_patterns = [
            "post_launch_control_ready",
            "post_launch_control.py",
            "scale_public",
            "support tickets",
            "Estado: Done.",
        ]
        for pattern in m37_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m37)
        post_launch = (PROJECT_ROOT / "docs" / "sales" / "POST_LAUNCH_CONTROL.md").read_text(encoding="utf-8-sig")
        self.assertIn("Post Launch Control", post_launch)
        self.assertIn("post_launch_control.py", post_launch)
        self.assertIn("support tickets", post_launch)

        m38_patterns = [
            "commercial_feedback_loop_ready",
            "commercial_feedback_loop.py",
            "pricing_decision",
            "copy_decision",
            "Estado: Done.",
        ]
        for pattern in m38_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m38)
        feedback_loop = (PROJECT_ROOT / "docs" / "sales" / "COMMERCIAL_FEEDBACK_LOOP.md").read_text(encoding="utf-8-sig")
        self.assertIn("Commercial Feedback Loop", feedback_loop)
        self.assertIn("commercial_feedback_loop.py", feedback_loop)
        self.assertIn("pricing_decision", feedback_loop)

        m39_patterns = [
            "public_offer_pack_ready",
            "public_offer_pack.py",
            "offer_headline",
            "buyer steps",
            "Estado: Done.",
        ]
        for pattern in m39_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m39)
        public_offer = (PROJECT_ROOT / "docs" / "sales" / "PUBLIC_OFFER_PACK.md").read_text(encoding="utf-8-sig")
        self.assertIn("Public Offer Pack", public_offer)
        self.assertIn("public_offer_pack.py", public_offer)
        self.assertIn("buyer steps", public_offer)

        m40_patterns = [
            "launch_assets_kit_ready",
            "launch_assets_kit.py",
            "github_release_draft",
            "publication checklist",
            "Estado: Done.",
        ]
        for pattern in m40_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m40)
        launch_assets = (PROJECT_ROOT / "docs" / "sales" / "LAUNCH_ASSETS_KIT.md").read_text(encoding="utf-8-sig")
        self.assertIn("Launch Assets Kit", launch_assets)
        self.assertIn("launch_assets_kit.py", launch_assets)
        self.assertIn("publication checklist", launch_assets)

        m41_patterns = [
            "public_release_gate_ready",
            "public_release_gate.py",
            "release_tag",
            "GitHub Release",
            "Estado: Done.",
        ]
        for pattern in m41_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m41)
        public_release_gate = (PROJECT_ROOT / "docs" / "sales" / "PUBLIC_RELEASE_GATE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Public Release Gate", public_release_gate)
        self.assertIn("public_release_gate.py", public_release_gate)
        self.assertIn("release_tag", public_release_gate)

        m42_patterns = [
            "release_publication_record_ready",
            "release_publication_record.py",
            "github_release_published",
            "sha256_mismatch",
            "Estado: Done.",
        ]
        for pattern in m42_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m42)
        publication_record = (PROJECT_ROOT / "docs" / "sales" / "RELEASE_PUBLICATION_RECORD.md").read_text(encoding="utf-8-sig")
        self.assertIn("Release Publication Record", publication_record)
        self.assertIn("release_publication_record.py", publication_record)
        self.assertIn("github_release_published", publication_record)

        m43_patterns = [
            "post_release_monitor_ready",
            "post_release_monitor.py",
            "activation_error_rate_high",
            "scale_public",
            "Estado: Done.",
        ]
        for pattern in m43_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m43)
        post_release_monitor = (PROJECT_ROOT / "docs" / "sales" / "POST_RELEASE_MONITOR.md").read_text(encoding="utf-8-sig")
        self.assertIn("Post Release Monitor", post_release_monitor)
        self.assertIn("post_release_monitor.py", post_release_monitor)
        self.assertIn("activation_error_rate_high", post_release_monitor)

        m44_patterns = [
            "hotfix_rollback_release_ready",
            "hotfix_rollback_release.py",
            "rollback_target_missing",
            "customer_comms_not_ready",
            "Estado: Done.",
        ]
        for pattern in m44_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, m44)
        hotfix_rollback = (PROJECT_ROOT / "docs" / "sales" / "HOTFIX_ROLLBACK_RELEASE.md").read_text(encoding="utf-8-sig")
        self.assertIn("Hotfix Rollback Release", hotfix_rollback)
        self.assertIn("hotfix_rollback_release.py", hotfix_rollback)
        self.assertIn("rollback_target_missing", hotfix_rollback)

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
            "license-panel",
            "license-plan-label",
            "license-state-badge",
            "license-commercial-copy",
            "license-upgrade-list",
            "license-plan-strip",
            "support-panel",
            "support-diagnostic-btn",
            "support-diagnostic-status",
            "fulfillment-panel",
            "fulfillment-queue-count",
            "fulfillment-request-list",
            "fulfillment-private-key",
            "fulfillment-zip-path",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

        dashboard_js = (APP_ROOT / "js" / "dashboard.js").read_text(encoding="utf-8-sig")
        main_js = (APP_ROOT / "js" / "main.js").read_text(encoding="utf-8-sig")
        project_generator_main_js = (APP_ROOT / "js" / "project-generator-main.js").read_text(encoding="utf-8-sig")
        project_generator_core_js = (APP_ROOT / "js" / "modules" / "project-generator-core.js").read_text(encoding="utf-8-sig")
        self.assertIn("window.updateHomeBackendStatus", dashboard_js)
        self.assertIn("home-audit-score", dashboard_js)
        self.assertIn("window.addHomeTrace", dashboard_js)
        self.assertIn("HOME_TRACE_KEY", dashboard_js)
        self.assertIn("renderHome();", main_js)
        self.assertIn("updateHomeBackendStatus", project_generator_main_js)
        self.assertIn("templates_capa1_exists", project_generator_main_js)
        self.assertIn("pgTrace(", project_generator_main_js)
        self.assertIn("function pgRenderOnboarding", project_generator_main_js)
        self.assertIn("function pgRunOnboardingAction", project_generator_main_js)
        self.assertIn("function pgRunOnboardingTertiaryAction", project_generator_main_js)
        self.assertIn("pg-assistant-check", project_generator_core_js)
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
        product = json.loads((TOOL_ROOT / "config" / "product_manifest.json").read_text(encoding="utf-8-sig"))
        assets = json.loads((TOOL_ROOT / "config" / "assets.json").read_text(encoding="utf-8-sig"))
        strategies = json.loads((TOOL_ROOT / "config" / "strategies.json").read_text(encoding="utf-8-sig"))
        ui = json.loads((TOOL_ROOT / "config" / "ui_manifest.json").read_text(encoding="utf-8-sig"))

        self.assertEqual(manifest["plan"], plan)
        self.assertEqual(manifest["product"], product)
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

    def test_checkout_live_readiness_tool_is_present_and_guarded(self):
        path = TOOL_ROOT / "tools" / "checkout_live_readiness.py"
        py_compile.compile(str(path), doraise=True)
        text = path.read_text(encoding="utf-8")
        for pattern in (
            "primary_checkout_url_missing_or_not_https",
            "providerVariantId",
            "render_staging_purchase_drill_missing",
            "rollback_steps",
            "SQX_RELAY_PUBLIC_BASE_URL",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

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


if __name__ == "__main__":
    unittest.main()
