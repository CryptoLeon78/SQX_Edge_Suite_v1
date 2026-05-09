import json
import shutil
import unittest
from pathlib import Path

from tools.next_controlled_commercial_movement_from_m98_decision import (
    collect_decision,
    markdown_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
CONFIG = TOOL_ROOT / "config" / "next_controlled_commercial_movement_from_m98_decision.json"
MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"


class NextControlledCommercialMovementFromM98DecisionTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = TOOL_ROOT / "data" / "_test_m99"
        self.tmp.mkdir(parents=True, exist_ok=True)
        self.monitor_file = self.tmp / "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_20260509_000000.json"
        self.monitor_file.write_text(
            json.dumps(
                {
                    "state": "approved_controlled_commercial_movement_from_m96_decision_execution_monitor_ready",
                    "monitor_status": "completed",
                    "monitor_decision": "prepare_next_decision",
                    "observation_hours": 24,
                    "positive_signals": 1,
                    "support_items_open": 0,
                    "refund_requests": 0,
                    "claims_issues": 0,
                    "incidents": 0,
                    "decision": {"go": True, "label": "GO", "blockers": [], "warnings": []},
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_go_for_clean_m98_next_micro_step_decision(self):
        report = collect_decision(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            monitor_file=self.monitor_file,
            source_decision="prepare_next_decision",
            next_movement="prepare_next_micro_step",
            owner="Ivan",
            rationale="M98 monitor is clean, so prepare one controlled micro-step.",
            next_gate="M100 execute the M99-approved controlled movement.",
            confirmations={
                "monitor_reviewed": True,
                "no_automation": True,
                "support_clear_or_paused": True,
                "claims_clear_or_paused": True,
                "redacted_evidence": True,
            },
        )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["decision_id"], "next_controlled_commercial_movement_from_m98_decision")
        self.assertEqual(report["next_movement"], "prepare_next_micro_step")
        self.assertEqual(report["observation_hours"], 24)
        self.assertIn("without_automatic_traffic_checkout_email_or_license_actions", report["decision_policy"])
        self.assertNotIn("buyer_email", json.dumps(report))

    def test_blocks_risky_next_micro_step(self):
        report = collect_decision(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            monitor_file=self.monitor_file,
            source_decision="prepare_next_decision",
            next_movement="prepare_next_micro_step",
            observation_hours=24,
            positive_signals=1,
            support_items_open=0,
            refund_requests=1,
            claims_issues=0,
            incidents=0,
            owner="Ivan",
            rationale="Refund risk present.",
            next_gate="Pause sales.",
            confirmations={
                "monitor_reviewed": True,
                "no_automation": True,
                "support_clear_or_paused": True,
                "claims_clear_or_paused": True,
                "redacted_evidence": True,
            },
        )
        blockers = report["decision"]["blockers"]
        self.assertFalse(report["decision"]["go"])
        self.assertIn("next_controlled_commercial_movement_from_m98_refund_requests_requires_hold_or_pause", blockers)
        self.assertIn("prepare_next_micro_step_blocked_by_risk", blockers)
        self.assertIn("risk_events_require_pause_sales", blockers)

    def test_markdown_report_stays_redacted(self):
        report = collect_decision(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            monitor_file=self.monitor_file,
            source_decision="prepare_next_decision",
            next_movement="prepare_private_review_packet",
            owner="Ivan",
            rationale="Prepare a private review packet with redacted signals.",
            next_gate="Private review packet gate.",
            confirmations={
                "monitor_reviewed": True,
                "no_automation": True,
                "support_clear_or_paused": True,
                "claims_clear_or_paused": True,
                "redacted_evidence": True,
            },
        )
        text = markdown_report(report)
        self.assertIn("Next Controlled Commercial Movement From M98 Decision Evidence", text)
        self.assertIn("positive_signals", text)
        self.assertNotIn("buyer_email", text)
        self.assertNotIn("license.json", text)


if __name__ == "__main__":
    unittest.main()
