import json
import shutil
import unittest
from pathlib import Path

from tools.approved_controlled_commercial_movement_from_m96_decision_execution import (
    collect_execution,
    markdown_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "backend" / "sqx-edge-tool"
CONFIG = TOOL_ROOT / "config" / "approved_controlled_commercial_movement_from_m96_decision_execution.json"
MANIFEST = TOOL_ROOT / "config" / "product_manifest.json"


class ApprovedControlledCommercialMovementFromM96DecisionExecutionTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = TOOL_ROOT / "data" / "_test_m97"
        self.tmp.mkdir(parents=True, exist_ok=True)
        self.decision_file = self.tmp / "next_controlled_commercial_movement_from_m95_decision_20260509_000000.json"
        self.decision_file.write_text(
            json.dumps(
                {
                    "state": "next_controlled_commercial_movement_from_m95_decision_ready",
                    "next_movement": "prepare_next_micro_step",
                    "decision": {"go": True, "label": "GO", "blockers": [], "warnings": []},
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_go_for_exact_m96_micro_step_execution(self):
        report = collect_execution(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            decision_file=self.decision_file,
            source_movement="prepare_next_micro_step",
            execution_result="next_micro_step_prepared",
            new_private_links=1,
            new_invites=3,
            owner="Ivan",
            execution_summary="Prepared one private link and three invite slots for manual operator use.",
            next_monitor="M98 monitor the M97 execution result before any additional movement.",
            confirmations={
                "decision_reviewed": True,
                "exact_movement": True,
                "no_automation": True,
                "safe_claims_reviewed": True,
                "redacted_evidence": True,
            },
        )
        self.assertTrue(report["decision"]["go"])
        self.assertEqual(report["execution_id"], "approved_controlled_commercial_movement_from_m96_decision_execution")
        self.assertEqual(report["execution_result"], "next_micro_step_prepared")
        self.assertEqual(report["new_private_links"], 1)
        self.assertEqual(report["new_invites"], 3)
        self.assertIn("without_automatic_traffic_checkout_email_or_license_execution", report["execution_policy"])
        self.assertNotIn("buyer_email", json.dumps(report))

    def test_blocks_movement_mismatch_and_traffic_overflow(self):
        report = collect_execution(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            decision_file=self.decision_file,
            source_movement="prepare_next_micro_step",
            execution_result="observation_continued",
            new_private_links=2,
            new_invites=4,
            owner="Ivan",
            execution_summary="Tried to deviate from M96.",
            next_monitor="M98",
            confirmations={
                "decision_reviewed": True,
                "exact_movement": True,
                "no_automation": True,
                "safe_claims_reviewed": True,
                "redacted_evidence": True,
            },
        )
        blockers = report["decision"]["blockers"]
        self.assertFalse(report["decision"]["go"])
        self.assertIn("approved_controlled_commercial_movement_from_m96_decision_execution_result_not_allowed_for_m96_movement", blockers)
        self.assertIn("non_micro_step_execution_must_not_create_new_traffic", blockers)

    def test_markdown_report_stays_redacted(self):
        report = collect_execution(
            config_path=CONFIG,
            manifest_path=MANIFEST,
            decision_file=self.decision_file,
            source_movement="prepare_next_micro_step",
            execution_result="next_micro_step_prepared",
            new_private_links=0,
            new_invites=0,
            owner="Ivan",
            execution_summary="Prepared the exact M96 movement without external execution.",
            next_monitor="M98",
            confirmations={
                "decision_reviewed": True,
                "exact_movement": True,
                "no_automation": True,
                "safe_claims_reviewed": True,
                "redacted_evidence": True,
            },
        )
        text = markdown_report(report)
        self.assertIn("Approved Controlled Commercial Movement From M96 Decision Execution Evidence", text)
        self.assertIn("new_private_links", text)
        self.assertNotIn("buyer_email", text)
        self.assertNotIn("license.json", text)


if __name__ == "__main__":
    unittest.main()
