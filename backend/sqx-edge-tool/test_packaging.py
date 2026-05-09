import json
import py_compile
import subprocess
import sys
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
            TOOL_ROOT / "tools" / "customer_success_renewal.py",
            TOOL_ROOT / "tools" / "pro_buyer_pack.py",
            TOOL_ROOT / "tools" / "buyer_onboarding_support_gate.py",
            TOOL_ROOT / "tools" / "template_pack_1_delivery.py",
            TOOL_ROOT / "tools" / "template_pack_1_offer.py",
            TOOL_ROOT / "tools" / "template_pack_1_publication.py",
            TOOL_ROOT / "tools" / "template_pack_1_purchase_drill.py",
            TOOL_ROOT / "tools" / "template_pack_1_handoff.py",
            TOOL_ROOT / "tools" / "template_pack_1_sales_register.py",
            TOOL_ROOT / "tools" / "template_pack_1_feedback_cohort.py",
            TOOL_ROOT / "tools" / "template_pack_1_action_plan.py",
            TOOL_ROOT / "tools" / "template_pack_2_specs.py",
            TOOL_ROOT / "tools" / "template_pack_2_assets.py",
            TOOL_ROOT / "tools" / "template_pack_2_offer_pack.py",
            TOOL_ROOT / "tools" / "template_pack_2_publication.py",
            TOOL_ROOT / "tools" / "template_pack_2_purchase_drill.py",
            TOOL_ROOT / "tools" / "template_pack_2_handoff.py",
            TOOL_ROOT / "tools" / "template_pack_2_sales_register.py",
            TOOL_ROOT / "tools" / "template_pack_2_feedback_cohort.py",
            TOOL_ROOT / "tools" / "buyer_ready_checkout_closeout.py",
            TOOL_ROOT / "tools" / "public_buyer_page_cadence.py",
            TOOL_ROOT / "tools" / "first_controlled_buyer_log.py",
            TOOL_ROOT / "tools" / "post_sale_improvement_loop.py",
            TOOL_ROOT / "tools" / "post_sale_micro_updates.py",
            TOOL_ROOT / "tools" / "next_controlled_buyer_readiness.py",
            TOOL_ROOT / "tools" / "next_controlled_buyer_outcome.py",
            TOOL_ROOT / "tools" / "controlled_distribution_step.py",
            TOOL_ROOT / "tools" / "controlled_distribution_review.py",
            TOOL_ROOT / "tools" / "next_buyer_facing_asset.py",
            TOOL_ROOT / "tools" / "private_asset_review.py",
            TOOL_ROOT / "tools" / "controlled_publication_gate.py",
            TOOL_ROOT / "tools" / "limited_publication_draft.py",
            TOOL_ROOT / "tools" / "operator_publication_review.py",
            TOOL_ROOT / "tools" / "manual_limited_publication_record.py",
            TOOL_ROOT / "tools" / "manual_publication_monitor.py",
            TOOL_ROOT / "tools" / "controlled_traffic_expansion_review.py",
            TOOL_ROOT / "tools" / "controlled_traffic_expansion_step.py",
            TOOL_ROOT / "tools" / "controlled_traffic_expansion_monitor.py",
            TOOL_ROOT / "tools" / "controlled_traffic_expansion_decision.py",
            TOOL_ROOT / "tools" / "controlled_traffic_expansion_execution.py",
            TOOL_ROOT / "tools" / "controlled_traffic_expansion_execution_monitor.py",
            TOOL_ROOT / "tools" / "controlled_commercial_next_movement.py",
            TOOL_ROOT / "tools" / "controlled_commercial_next_movement_execution.py",
            TOOL_ROOT / "tools" / "controlled_commercial_next_movement_execution_monitor.py",
            TOOL_ROOT / "tools" / "next_controlled_commercial_movement_decision.py",
            TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_execution.py",
            TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_execution_monitor.py",
            TOOL_ROOT / "tools" / "next_controlled_commercial_movement_from_m92_decision.py",
            TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m93_execution.py",
            TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m93_execution_monitor.py",
            TOOL_ROOT / "tools" / "next_controlled_commercial_movement_from_m95_decision.py",
            TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m96_decision_execution.py",
            TOOL_ROOT / "tools" / "approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py",
            TOOL_ROOT / "tools" / "private_commercial_split.py",
            TOOL_ROOT / "tools" / "fulfillment_request.py",
            TOOL_ROOT / "tools" / "fulfill_from_request.ps1",
            TOOL_ROOT / "tools" / "relay_bundle.py",
            TOOL_ROOT / "tools" / "dukas_mt5_ohlc_download.py",
            TOOL_ROOT / "tools" / "mt5_ipc_diagnostic.py",
            TOOL_ROOT / "config" / "dukas_mt5_download.json",
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
        self.assertIn('"analysis_output"', text)
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
        self.assertIn("customer_success_renewal\\.py", text)
        self.assertIn("pro_buyer_pack\\.py", text)
        self.assertIn("buyer_onboarding_support_gate\\.py", text)
        self.assertIn("template_pack_1_delivery\\.py", text)
        self.assertIn("template_pack_1_offer\\.py", text)
        self.assertIn("template_pack_1_publication\\.py", text)
        self.assertIn("template_pack_1_purchase_drill\\.py", text)
        self.assertIn("template_pack_1_handoff\\.py", text)
        self.assertIn("template_pack_1_sales_register\\.py", text)
        self.assertIn("template_pack_1_feedback_cohort\\.py", text)
        self.assertIn("template_pack_1_action_plan\\.py", text)
        self.assertIn("template_pack_2_specs\\.py", text)
        self.assertIn("template_pack_2_assets\\.py", text)
        self.assertIn("template_pack_2_offer_pack\\.py", text)
        self.assertIn("template_pack_2_publication\\.py", text)
        self.assertIn("template_pack_2_purchase_drill\\.py", text)
        self.assertIn("template_pack_2_handoff\\.py", text)
        self.assertIn("template_pack_2_sales_register\\.py", text)
        self.assertIn("template_pack_2_feedback_cohort\\.py", text)
        self.assertIn("buyer_ready_checkout_closeout\\.py", text)
        self.assertIn("public_buyer_page_cadence\\.py", text)
        self.assertIn("first_controlled_buyer_log\\.py", text)
        self.assertIn("post_sale_improvement_loop\\.py", text)
        self.assertIn("post_sale_micro_updates\\.py", text)
        self.assertIn("next_controlled_buyer_readiness\\.py", text)
        self.assertIn("next_controlled_buyer_outcome\\.py", text)
        self.assertIn("controlled_distribution_step\\.py", text)
        self.assertIn("controlled_distribution_review\\.py", text)
        self.assertIn("next_buyer_facing_asset\\.py", text)
        self.assertIn("private_asset_review\\.py", text)
        self.assertIn("controlled_publication_gate\\.py", text)
        self.assertIn("limited_publication_draft\\.py", text)
        self.assertIn("operator_publication_review\\.py", text)
        self.assertIn("manual_limited_publication_record\\.py", text)
        self.assertIn("manual_publication_monitor\\.py", text)
        self.assertIn("controlled_traffic_expansion_review\\.py", text)
        self.assertIn("controlled_traffic_expansion_step\\.py", text)
        self.assertIn("controlled_traffic_expansion_monitor\\.py", text)
        self.assertIn("controlled_traffic_expansion_decision\\.py", text)
        self.assertIn("controlled_traffic_expansion_execution\\.py", text)
        self.assertIn("controlled_traffic_expansion_execution_monitor\\.py", text)
        self.assertIn("controlled_commercial_next_movement\\.py", text)
        self.assertIn("controlled_commercial_next_movement_execution\\.py", text)
        self.assertIn("controlled_commercial_next_movement_execution_monitor\\.py", text)
        self.assertIn("next_controlled_commercial_movement_decision\\.py", text)
        self.assertIn("approved_controlled_commercial_movement_execution\\.py", text)
        self.assertIn("approved_controlled_commercial_movement_execution_monitor\\.py", text)
        self.assertIn("next_controlled_commercial_movement_from_m92_decision\\.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m93_execution\\.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m93_execution_monitor\\.py", text)
        self.assertIn("next_controlled_commercial_movement_from_m95_decision\\.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution\\.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution_monitor\\.py", text)
        self.assertIn("private_commercial_split\\.py", text)
        self.assertIn("fulfillment_request\\.py", text)
        self.assertIn("fulfill_from_request\\.ps1", text)
        self.assertIn("relay_bundle\\.py", text)
        self.assertIn("dukas_mt5_ohlc_download\\.py", text)
        self.assertIn("mt5_ipc_diagnostic\\.py", text)
        self.assertIn("dukas_mt5_download\\.json", text)
        self.assertIn('"dukas_mt5_download"', text)
        self.assertIn('"real_mtf_pipeline_run"', text)
        self.assertIn("\\\\data\\\\ohlc\\\\", text)
        self.assertIn("\\\\analysis_output\\\\", text)
        self.assertIn("mt5_ipc_diagnostic", text)
        self.assertIn("real_mtf_pipeline_run", text)
        self.assertIn('"sqx-edge-relay"', text)
        self.assertIn("_private_key\\.json", text)
        self.assertIn("license_signed_", text)
        self.assertIn("license_payload_", text)
        self.assertIn("fulfillment_request_", text)
        self.assertIn("webhook_event_", text)
        self.assertIn("relay_event_", text)
        self.assertIn('"fulfillment_requests"', text)
        self.assertIn('"customer_success_renewal"', text)
        self.assertIn('"customer_cockpit"', text)
        self.assertIn('"pro_buyer_pack"', text)
        self.assertIn('"buyer_onboarding_support_gate"', text)
        self.assertIn('"template_pack_1_delivery"', text)
        self.assertIn('"template_pack_1_offer"', text)
        self.assertIn('"template_pack_1_publication"', text)
        self.assertIn('"template_pack_1_purchase_drill"', text)
        self.assertIn('"template_pack_1_handoff"', text)
        self.assertIn('"template_pack_1_sales_register"', text)
        self.assertIn('"template_pack_1_feedback_cohort"', text)
        self.assertIn('"template_pack_1_action_plan"', text)
        self.assertIn('"template_pack_2_specs"', text)
        self.assertIn('"template_pack_2_assets"', text)
        self.assertIn('"template_pack_2_offer_pack"', text)
        self.assertIn('"template_pack_2_publication"', text)
        self.assertIn('"template_pack_2_purchase_drill"', text)
        self.assertIn('"template_pack_2_handoff"', text)
        self.assertIn('"template_pack_2_sales_register"', text)
        self.assertIn('"template_pack_2_feedback_cohort"', text)
        self.assertIn('"buyer_ready_checkout_closeout"', text)
        self.assertIn('"public_buyer_page_cadence"', text)
        self.assertIn('"first_controlled_buyer_log"', text)
        self.assertIn('"post_sale_improvement_loop"', text)
        self.assertIn('"post_sale_micro_updates"', text)
        self.assertIn('"next_controlled_buyer_readiness"', text)
        self.assertIn('"next_controlled_buyer_outcome"', text)
        self.assertIn('"controlled_distribution_step"', text)
        self.assertIn('"controlled_distribution_review"', text)
        self.assertIn('"next_buyer_facing_asset"', text)
        self.assertIn('"private_asset_review"', text)
        self.assertIn('"controlled_publication_gate"', text)
        self.assertIn('"limited_publication_draft"', text)
        self.assertIn('"operator_publication_review"', text)
        self.assertIn('"manual_limited_publication_record"', text)
        self.assertIn('"manual_publication_monitor"', text)
        self.assertIn('"controlled_traffic_expansion_review"', text)
        self.assertIn('"controlled_traffic_expansion_step"', text)
        self.assertIn('"controlled_traffic_expansion_monitor"', text)
        self.assertIn('"controlled_traffic_expansion_decision"', text)
        self.assertIn('"controlled_traffic_expansion_execution"', text)
        self.assertIn('"controlled_traffic_expansion_execution_monitor"', text)
        self.assertIn('"controlled_commercial_next_movement"', text)
        self.assertIn('"controlled_commercial_next_movement_execution"', text)
        self.assertIn('"controlled_commercial_next_movement_execution_monitor"', text)
        self.assertIn('"next_controlled_commercial_movement_decision"', text)
        self.assertIn('"approved_controlled_commercial_movement_execution"', text)
        self.assertIn('"approved_controlled_commercial_movement_execution_monitor"', text)
        self.assertIn('"next_controlled_commercial_movement_from_m92_decision"', text)
        self.assertIn('"approved_controlled_commercial_movement_from_m93_execution"', text)
        self.assertIn('"approved_controlled_commercial_movement_from_m93_execution_monitor"', text)
        self.assertIn('"next_controlled_commercial_movement_from_m95_decision"', text)
        self.assertIn('"approved_controlled_commercial_movement_from_m96_decision_execution"', text)
        self.assertIn('"approved_controlled_commercial_movement_from_m96_decision_execution_monitor"', text)
        self.assertIn('"private-commercial"', text)
        self.assertIn('"commercial-private"', text)
        self.assertIn('"pro-template-pack-1"', text)
        self.assertIn('"pro-template-pack-2"', text)
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
        self.assertIn("customer_success_renewal.py", text)
        self.assertIn("pro_buyer_pack.py", text)
        self.assertIn("buyer_onboarding_support_gate.py", text)
        self.assertIn("template_pack_1_delivery.py", text)
        self.assertIn("template_pack_1_offer.py", text)
        self.assertIn("template_pack_1_publication.py", text)
        self.assertIn("template_pack_1_purchase_drill.py", text)
        self.assertIn("template_pack_1_handoff.py", text)
        self.assertIn("template_pack_1_sales_register.py", text)
        self.assertIn("template_pack_1_feedback_cohort.py", text)
        self.assertIn("template_pack_1_action_plan.py", text)
        self.assertIn("template_pack_2_specs.py", text)
        self.assertIn("template_pack_2_assets.py", text)
        self.assertIn("template_pack_2_offer_pack.py", text)
        self.assertIn("template_pack_2_publication.py", text)
        self.assertIn("template_pack_2_purchase_drill.py", text)
        self.assertIn("template_pack_2_handoff.py", text)
        self.assertIn("template_pack_2_sales_register.py", text)
        self.assertIn("template_pack_2_feedback_cohort.py", text)
        self.assertIn("buyer_ready_checkout_closeout.py", text)
        self.assertIn("public_buyer_page_cadence.py", text)
        self.assertIn("first_controlled_buyer_log.py", text)
        self.assertIn("post_sale_improvement_loop.py", text)
        self.assertIn("post_sale_micro_updates.py", text)
        self.assertIn("next_controlled_buyer_readiness.py", text)
        self.assertIn("next_controlled_buyer_outcome.py", text)
        self.assertIn("controlled_distribution_step.py", text)
        self.assertIn("controlled_distribution_review.py", text)
        self.assertIn("next_buyer_facing_asset.py", text)
        self.assertIn("private_asset_review.py", text)
        self.assertIn("controlled_publication_gate.py", text)
        self.assertIn("limited_publication_draft.py", text)
        self.assertIn("operator_publication_review.py", text)
        self.assertIn("manual_limited_publication_record.py", text)
        self.assertIn("manual_publication_monitor.py", text)
        self.assertIn("controlled_traffic_expansion_review.py", text)
        self.assertIn("controlled_traffic_expansion_step.py", text)
        self.assertIn("controlled_traffic_expansion_monitor.py", text)
        self.assertIn("controlled_traffic_expansion_decision.py", text)
        self.assertIn("controlled_traffic_expansion_execution.py", text)
        self.assertIn("controlled_traffic_expansion_execution_monitor.py", text)
        self.assertIn("controlled_commercial_next_movement.py", text)
        self.assertIn("controlled_commercial_next_movement_execution.py", text)
        self.assertIn("controlled_commercial_next_movement_execution_monitor.py", text)
        self.assertIn("next_controlled_commercial_movement_decision.py", text)
        self.assertIn("approved_controlled_commercial_movement_execution.py", text)
        self.assertIn("approved_controlled_commercial_movement_execution_monitor.py", text)
        self.assertIn("next_controlled_commercial_movement_from_m92_decision.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m93_execution.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m93_execution_monitor.py", text)
        self.assertIn("next_controlled_commercial_movement_from_m95_decision.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution.py", text)
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py", text)
        self.assertIn("private_commercial_split.py", text)
        self.assertIn("fulfillment_request.py", text)
        self.assertIn("fulfill_from_request.ps1", text)
        self.assertIn("relay_bundle.py", text)
        self.assertIn("dukas_mt5_ohlc_download.py", text)
        self.assertIn("mt5_ipc_diagnostic.py", text)
        self.assertIn("dukas_mt5_download.json", text)
        self.assertIn("data\\ohlc", text)
        self.assertIn("analysis_output", text)
        self.assertIn("real_mtf_pipeline_run", text)
        self.assertIn("sqx-edge-relay", text)
        self.assertIn("fulfillment_requests", text)
        self.assertIn("customer_success_renewal", text)
        self.assertIn("customer_cockpit", text)
        self.assertIn("pro_buyer_pack", text)
        self.assertIn("buyer_onboarding_support_gate", text)
        self.assertIn("template_pack_1_delivery", text)
        self.assertIn("template_pack_1_offer", text)
        self.assertIn("template_pack_1_publication", text)
        self.assertIn("template_pack_1_purchase_drill", text)
        self.assertIn("template_pack_1_handoff", text)
        self.assertIn("template_pack_1_sales_register", text)
        self.assertIn("template_pack_1_feedback_cohort", text)
        self.assertIn("template_pack_1_action_plan", text)
        self.assertIn("template_pack_2_specs", text)
        self.assertIn("template_pack_2_assets", text)
        self.assertIn("template_pack_2_offer_pack", text)
        self.assertIn("template_pack_2_publication", text)
        self.assertIn("template_pack_2_purchase_drill", text)
        self.assertIn("template_pack_2_handoff", text)
        self.assertIn("template_pack_2_sales_register", text)
        self.assertIn("template_pack_2_feedback_cohort", text)
        self.assertIn("buyer_ready_checkout_closeout", text)
        self.assertIn("public_buyer_page_cadence", text)
        self.assertIn("first_controlled_buyer_log", text)
        self.assertIn("post_sale_improvement_loop", text)
        self.assertIn("post_sale_micro_updates", text)
        self.assertIn("next_controlled_buyer_readiness", text)
        self.assertIn("next_controlled_buyer_outcome", text)
        self.assertIn("controlled_distribution_step", text)
        self.assertIn("controlled_distribution_review", text)
        self.assertIn("next_buyer_facing_asset", text)
        self.assertIn("private_asset_review", text)
        self.assertIn("controlled_publication_gate", text)
        self.assertIn("limited_publication_draft", text)
        self.assertIn("operator_publication_review", text)
        self.assertIn("manual_limited_publication_record", text)
        self.assertIn("manual_publication_monitor", text)
        self.assertIn("controlled_traffic_expansion_review", text)
        self.assertIn("controlled_traffic_expansion_step", text)
        self.assertIn("controlled_traffic_expansion_monitor", text)
        self.assertIn("controlled_traffic_expansion_decision", text)
        self.assertIn("controlled_traffic_expansion_execution", text)
        self.assertIn("controlled_traffic_expansion_execution_monitor", text)
        self.assertIn("controlled_commercial_next_movement", text)
        self.assertIn("private-commercial", text)
        self.assertIn("commercial-private", text)
        self.assertIn("pro-template-pack-1", text)
        self.assertIn("pro-template-pack-2", text)
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
            "customer_success_renewal.py",
            "pro_buyer_pack.py",
            "buyer_onboarding_support_gate.py",
            "template_pack_1_delivery.py",
            "template_pack_1_offer.py",
            "template_pack_1_publication.py",
            "template_pack_1_purchase_drill.py",
            "template_pack_1_handoff.py",
            "template_pack_1_sales_register.py",
            "template_pack_1_feedback_cohort.py",
            "template_pack_1_action_plan.py",
            "template_pack_2_specs.py",
            "template_pack_2_assets.py",
            "template_pack_2_offer_pack.py",
            "template_pack_2_publication.py",
            "template_pack_2_purchase_drill.py",
            "template_pack_2_handoff.py",
            "template_pack_2_sales_register.py",
            "template_pack_2_feedback_cohort.py",
            "buyer_ready_checkout_closeout.py",
            "public_buyer_page_cadence.py",
            "first_controlled_buyer_log.py",
            "post_sale_improvement_loop.py",
            "post_sale_micro_updates.py",
            "next_controlled_buyer_readiness.py",
            "next_controlled_buyer_outcome.py",
            "controlled_distribution_step.py",
            "controlled_distribution_review.py",
            "next_buyer_facing_asset.py",
            "private_asset_review.py",
            "controlled_publication_gate.py",
            "limited_publication_draft.py",
            "operator_publication_review.py",
            "manual_limited_publication_record.py",
            "manual_publication_monitor.py",
            "controlled_traffic_expansion_review.py",
            "controlled_traffic_expansion_step.py",
            "controlled_traffic_expansion_monitor.py",
            "controlled_traffic_expansion_decision.py",
            "controlled_traffic_expansion_execution.py",
            "controlled_traffic_expansion_execution_monitor.py",
            "controlled_commercial_next_movement.py",
            "controlled_commercial_next_movement_execution.py",
            "controlled_commercial_next_movement_execution_monitor.py",
            "next_controlled_commercial_movement_decision.py",
            "approved_controlled_commercial_movement_execution.py",
            "approved_controlled_commercial_movement_execution_monitor.py",
            "next_controlled_commercial_movement_from_m92_decision.py",
            "approved_controlled_commercial_movement_from_m93_execution.py",
            "approved_controlled_commercial_movement_from_m93_execution_monitor.py",
            "next_controlled_commercial_movement_from_m95_decision.py",
            "approved_controlled_commercial_movement_from_m96_decision_execution.py",
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py",
            "private_commercial_split.py",
            "fulfillment_request.py",
            "fulfill_from_request.ps1",
            "relay_bundle.py",
            "dukas_mt5_ohlc_download.py",
            "mt5_ipc_diagnostic.py",
            "dukas_mt5_download.json",
            "dukas_mt5_download",
            "mt5_ipc_diagnostic",
            "real_mtf_pipeline_run",
            "analysis_output",
            "sqx-edge-relay",
            "customer_success_renewal",
            "customer_cockpit",
            "pro_buyer_pack",
            "buyer_onboarding_support_gate",
            "template_pack_1_delivery",
            "template_pack_1_offer",
            "template_pack_1_publication",
            "template_pack_1_purchase_drill",
            "template_pack_1_handoff",
            "template_pack_1_sales_register",
            "template_pack_1_feedback_cohort",
            "template_pack_1_action_plan",
            "template_pack_2_specs",
            "template_pack_2_assets",
            "template_pack_2_offer_pack",
            "template_pack_2_publication",
            "template_pack_2_purchase_drill",
            "template_pack_2_handoff",
            "template_pack_2_sales_register",
            "template_pack_2_feedback_cohort",
            "buyer_ready_checkout_closeout",
            "public_buyer_page_cadence",
            "first_controlled_buyer_log",
            "post_sale_improvement_loop",
            "post_sale_micro_updates",
            "next_controlled_buyer_readiness",
            "next_controlled_buyer_outcome",
            "controlled_distribution_step",
            "controlled_distribution_review",
            "next_buyer_facing_asset",
            "private_asset_review",
            "controlled_publication_gate",
            "limited_publication_draft",
            "operator_publication_review",
            "manual_limited_publication_record",
            "manual_publication_monitor",
            "controlled_traffic_expansion_review",
            "controlled_traffic_expansion_step",
            "controlled_traffic_expansion_monitor",
            "controlled_traffic_expansion_decision",
            "controlled_traffic_expansion_execution",
            "controlled_traffic_expansion_execution_monitor",
            "controlled_commercial_next_movement",
            "controlled_commercial_next_movement_execution",
            "controlled_commercial_next_movement_execution_monitor",
            "next_controlled_commercial_movement_decision",
            "approved_controlled_commercial_movement_execution",
            "approved_controlled_commercial_movement_execution_monitor",
            "next_controlled_commercial_movement_from_m92_decision",
            "approved_controlled_commercial_movement_from_m93_execution",
            "approved_controlled_commercial_movement_from_m93_execution_monitor",
            "next_controlled_commercial_movement_from_m95_decision",
            "approved_controlled_commercial_movement_from_m96_decision_execution",
            "approved_controlled_commercial_movement_from_m96_decision_execution_monitor",
            "private-commercial",
            "commercial-private",
            "pro-template-pack-1",
            "pro-template-pack-2",
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

    def test_gitignore_guards_local_license_file(self):
        text = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8-sig")
        self.assertIn("backend/sqx-edge-tool/config/license.json", text)
        self.assertIn("sqx-edge-tool/config/license.json", text)
        self.assertIn("backend/sqx-edge-tool/data/customer_success_renewal/", text)
        self.assertIn("backend/sqx-edge-tool/data/customer_cockpit/", text)
        self.assertIn("backend/sqx-edge-tool/data/pro_buyer_pack/", text)
        self.assertIn("backend/sqx-edge-tool/data/buyer_onboarding_support_gate/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_delivery/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_offer/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_publication/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_purchase_drill/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_handoff/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_sales_register/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_feedback_cohort/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_1_action_plan/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_specs/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_assets/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_offer_pack/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_publication/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_purchase_drill/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_handoff/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_sales_register/", text)
        self.assertIn("backend/sqx-edge-tool/data/template_pack_2_feedback_cohort/", text)
        self.assertIn("backend/sqx-edge-tool/data/buyer_ready_checkout_closeout/", text)
        self.assertIn("backend/sqx-edge-tool/data/public_buyer_page_cadence/", text)
        self.assertIn("backend/sqx-edge-tool/data/first_controlled_buyer_log/", text)
        self.assertIn("backend/sqx-edge-tool/data/post_sale_improvement_loop/", text)
        self.assertIn("backend/sqx-edge-tool/data/post_sale_micro_updates/", text)
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_readiness/", text)
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_buyer_outcome/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_step/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_distribution_review/", text)
        self.assertIn("backend/sqx-edge-tool/data/next_buyer_facing_asset/", text)
        self.assertIn("backend/sqx-edge-tool/data/private_asset_review/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_publication_gate/", text)
        self.assertIn("backend/sqx-edge-tool/data/limited_publication_draft/", text)
        self.assertIn("backend/sqx-edge-tool/data/operator_publication_review/", text)
        self.assertIn("backend/sqx-edge-tool/data/manual_limited_publication_record/", text)
        self.assertIn("backend/sqx-edge-tool/data/manual_publication_monitor/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_review/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_step/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_monitor/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_decision/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_execution/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_traffic_expansion_execution_monitor/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_commercial_next_movement/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution/", text)
        self.assertIn("backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution_monitor/", text)
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_decision/", text)
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution/", text)
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution_monitor/", text)
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m92_decision/", text)
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution/", text)
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution_monitor/", text)
        self.assertIn("backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m95_decision/", text)
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution/", text)
        self.assertIn("backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution_monitor/", text)
        self.assertIn("docs/private-commercial/", text)
        self.assertIn("commercial-private/", text)
        self.assertIn("private-commercial/", text)

    def test_ci_baseline_and_dev_requirements_are_present(self):
        requirements = (PROJECT_ROOT / "requirements-dev.txt").read_text(encoding="utf-8-sig")
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8-sig")

        self.assertIn("-r backend/sqx-edge-tool/requirements.txt", requirements)
        self.assertIn("-r backend/sqx-edge-relay/requirements.txt", requirements)
        self.assertIn("pytest", requirements)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn("actions/setup-node@v4", workflow)
        self.assertIn("python -m compileall backend", workflow)
        self.assertIn("python -m pytest", workflow)
        self.assertIn("tests/js/contracts", workflow)
        self.assertIn("git diff --check", workflow)

    def test_private_commercial_docs_boundary_is_documented(self):
        boundary = (PROJECT_ROOT / "docs" / "PRIVATE_COMMERCIAL_DOCS.md").read_text(encoding="utf-8-sig")
        manifest = (PROJECT_ROOT / "docs" / "private_commercial_manifest.json").read_text(encoding="utf-8-sig")

        self.assertIn("private GitHub repository", boundary)
        self.assertIn("Treat existing public Git history as already exposed", boundary)
        self.assertIn("docs/private-commercial/", boundary)
        self.assertIn("Prepared Export", boundary)
        self.assertIn("recommendedTarget", manifest)
        self.assertIn("private_github_repository", manifest)
        self.assertIn("private_commercial_split.py", manifest)
        self.assertIn("public_redacted_private_repo_published", manifest)
        self.assertIn("public_repository_keeps_only_traceability_pointers", manifest)
        self.assertIn("copy_sensitive_docs_to_private_repo_with_sha256_index", manifest)
        self.assertIn("docs/MONETIZATION_M*.md", manifest)
        self.assertIn("docs/sales/", manifest)
        self.assertIn("resources/pro-template-pack-2/", manifest)

    def test_private_commercial_split_tool_builds_traceable_index(self):
        tool_path = TOOL_ROOT / "tools" / "private_commercial_split.py"
        py_compile.compile(str(tool_path), doraise=True)

        result = subprocess.run(
            [sys.executable, str(tool_path), "--no-write"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        index = json.loads(result.stdout)
        sources = {item["source"] for item in index["sources"]}

        self.assertEqual(index["migrationStage"], "public_redacted_private_repo_published")
        self.assertGreater(index["sourceCount"], 80)
        self.assertIn("commercial-private", index["outputDir"])
        self.assertIn("docs/MONETIZATION_ROADMAP.md", sources)
        self.assertIn("docs/MONETIZATION_M70.md", sources)
        self.assertIn("docs/sales/NEXT_CONTROLLED_BUYER_READINESS.md", sources)
        self.assertTrue(any(source.startswith("resources/pro-template-pack-2/") for source in sources))

        split_plan = (PROJECT_ROOT / "docs" / "PRIVATE_COMMERCIAL_SPLIT_PLAN.md").read_text(encoding="utf-8-sig")
        self.assertIn("private_repo_published", split_plan)
        self.assertIn("ed79719 Initial private commercial export", split_plan)
        self.assertIn("https://github.com/CryptoLeon78/sqx-edge-commercial-private", split_plan)
        self.assertIn("Visibilidad verificada", split_plan)

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
