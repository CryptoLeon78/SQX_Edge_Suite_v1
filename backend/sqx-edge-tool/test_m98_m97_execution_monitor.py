import json
import shutil
import unittest
from pathlib import Path

from tools.approved_controlled_commercial_movement_from_m96_decision_execution_monitor import (
    collect_monitor,
    markdown_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
CONFIG = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_from_m96_decision_execution_monitor.json"
MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"


class ApprovedControlledCommercialMovementFromM96DecisionExecutionMonitorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = TOOL_ROOT / "data" / "_test_m98"
        self.tmp.mkdir(parents=True, exist_ok=True)
        self.execution_file = self.tmp / "approved_controlled_commercial_movement_from_m96_decision_execution_20260509_000000.json"
        self.execution_file.write_text(
            json.dumps(
                {
                    "state": "approved_controlled_commercial_movement_from_m96_decision_execution_ready",
                    "execution_result": "next_micro_step_prepared",
                    "decision": {"go": True, "label": "GO", "blockers": [], "warnings": []},
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_go_for_clean_m97_execution_monitor(self):
        report = collect_monitor(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            execution_file=self.execution_file,
            source_result="next_micro_step_prepared",
            monitor_status="completed",
            observation_hours=24,
            responses=3,
            positive_signals=1,
            support_items_open=0,
            refund_requests=0,
            claims_issues=0,
            incidents=0,
            decision="prepare_next_decision",
            owner="Ivan",
            monitor_notes="M97 execution observed with clean aggregate signals.",
            next_action="M99 decide the next controlled commercial movement.",
            confirmations={
                "execution_reviewed": True,
                "support_clear": True,
                "claims_clear": True,
                "refunds_clear": True,
                "no_automation": True,
                "redacted_metrics": True,
            },
        )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["monitor_id"], "approved_controlled_commercial_movement_from_m96_decision_execution_monitor")
        self.assertEqual(report["source_result"], "next_micro_step_prepared")
        self.assertEqual(report["monitor_decision"], "prepare_next_decision")
        self.assertIn("monitor_m97_execution_result", report["monitor_policy"])
        self.assertNotIn("buyer_email", json.dumps(report))

    def test_blocks_risk_and_short_observation(self):
        report = collect_monitor(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            execution_file=self.execution_file,
            source_result="next_micro_step_prepared",
            monitor_status="completed",
            observation_hours=4,
            responses=1,
            positive_signals=1,
            support_items_open=1,
            refund_requests=0,
            claims_issues=0,
            incidents=0,
            decision="prepare_next_decision",
            owner="Ivan",
            monitor_notes="Support item still open.",
            next_action="Hold until support is clear.",
            confirmations={
                "execution_reviewed": True,
                "support_clear": True,
                "claims_clear": True,
                "refunds_clear": True,
                "no_automation": True,
                "redacted_metrics": True,
            },
        )
        blockers = report["decision"]["blockers"]
        self.assertFalse(report["decision"]["go"])
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution_monitor_requires_observation_time", blockers)
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution_monitor_support_items_open_requires_hold_or_pause", blockers)
        self.assertIn("prepare_next_decision_blocked_by_risk", blockers)

    def test_markdown_report_stays_redacted(self):
        report = collect_monitor(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            execution_file=self.execution_file,
            source_result="next_micro_step_prepared",
            monitor_status="partial",
            observation_hours=24,
            responses=2,
            positive_signals=1,
            support_items_open=0,
            refund_requests=0,
            claims_issues=0,
            incidents=0,
            decision="prepare_private_review_packet",
            owner="Ivan",
            monitor_notes="Prepare private review without exposing buyer identities.",
            next_action="Build private review packet.",
            confirmations={
                "execution_reviewed": True,
                "support_clear": True,
                "claims_clear": True,
                "refunds_clear": True,
                "no_automation": True,
                "redacted_metrics": True,
            },
        )
        text = markdown_report(report)
        self.assertIn("Approved Controlled Commercial Movement From M96 Decision Execution Monitor Evidence", text)
        self.assertIn("positive_signals", text)
        self.assertNotIn("buyer_email", text)
        self.assertNotIn("license.json", text)


if __name__ == "__main__":
    unittest.main()
