import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from core import sqx144_mt5_auto11_ea_attach_runner as auto11


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Sqx144Mt5Auto11EaAttachRunnerTests(unittest.TestCase):
    def test_status_is_source_ready_and_generic(self):
        payload = auto11.status_payload(PROJECT_ROOT)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["version"], "sqx144-mt5-auto11-ea-attach-runner-v1")
        self.assertTrue(payload["genericMt5SqxProfileAware"])
        self.assertFalse(payload["launchesMt5"])
        self.assertFalse(payload["runsMt5Ea"])
        self.assertFalse(payload["writesDataDb"])

    def test_plan_accepts_symbol_and_timeframe_as_profile_inputs(self):
        payload = auto11.plan_payload(
            PROJECT_ROOT,
            host="sqx144_full",
            mt5_profile="darwinex",
            symbol="EURUSD_Darwinex",
            timeframe="M5",
        )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["symbol"], "EURUSD_Darwinex")
        self.assertEqual(payload["timeframe"], "M5")
        self.assertEqual(payload["preferredAutomationPath"], "template_profile_autoload_then_auto10_heartbeat_verify")

    def test_attach_plan_dry_run_does_not_write_or_attach(self):
        payload = auto11.attach_plan_payload(PROJECT_ROOT, apply=False)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "auto11_attach_plan_ready_apply_required")
        self.assertEqual(payload["profileName"], "SQX_AUTO11_BRIDGE_darwinex_USDJPY_Darwinex_M1")
        self.assertEqual(payload["templateFileName"], "SQX_AUTO11_SQXInfoBridge.tpl")
        self.assertEqual(payload["chartSymbol"], "USDJPY")
        self.assertTrue(payload["wouldAttachSqxInfoBridge"])
        self.assertTrue(payload["wouldWriteMt5StartupConfig"])
        self.assertFalse(payload["writesMt5Template"])
        self.assertFalse(payload["writesMt5Profile"])
        self.assertFalse(payload["runsMt5Ea"])

    def test_attach_apply_requires_exact_approval(self):
        with self.assertRaises(auto11.Auto11Error) as raised:
            auto11.attach_plan_payload(PROJECT_ROOT, approval="APRUEBO AUTO11", apply=True)

        self.assertEqual(raised.exception.code, "auto11_attach_requires_exact_approval")

    def test_attach_apply_writes_profile_assets_under_local_auto11_terminal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / ".local" / "mt5_auto11" / "terminal"
            files_dir = data_dir / "MQL5" / "Files"
            experts_dir = data_dir / "MQL5" / "Experts"

            with patch.object(
                auto11.auto10,
                "preflight_payload",
                return_value={"discovery": {"process": {"targetTerminalProcessRunning": False}}},
            ):
                payload = auto11.attach_plan_payload(
                    root,
                    approval=auto11.AUTO11_ATTACH_APPROVAL_PHRASE,
                    apply=True,
                    mt5_files_dir=files_dir,
                    mt5_experts_dir=experts_dir,
                )

            profile_dir = data_dir / "MQL5" / "Profiles" / "Charts" / payload["profileName"]
            template_file = data_dir / "MQL5" / "Profiles" / "Templates" / "SQX_AUTO11_SQXInfoBridge.tpl"
            chart_file = profile_dir / "chart01.chr"
            order_file = profile_dir / "order.wnd"
            startup_file = root / ".local" / "mt5_auto11" / "startup" / payload["profileAssets"]["startupConfigFileName"]

            self.assertEqual(payload["status"], "auto11_attach_profile_writer_completed_ready_for_profile_launch")
            self.assertEqual(payload["statusMarker"], auto11.SQX144_MT5_AUTO11_PROFILE_WRITER_STATUS)
            self.assertTrue(payload["attachAllowedByGate"])
            self.assertTrue(payload["writesMt5Template"])
            self.assertTrue(payload["writesMt5Profile"])
            self.assertTrue(payload["writesMt5Chart"])
            self.assertTrue(payload["writesMt5StartupConfig"])
            self.assertFalse(payload["launchesMt5"])
            self.assertFalse(payload["runsMt5Ea"])
            self.assertFalse(payload["privacy"]["localPathsReturned"])
            self.assertTrue(template_file.is_file())
            self.assertTrue(chart_file.is_file())
            self.assertTrue(order_file.is_file())
            self.assertTrue(startup_file.is_file())

            chart_text = chart_file.read_text(encoding="utf-16")
            template_text = template_file.read_text(encoding="utf-16")
            startup_text = startup_file.read_text(encoding="utf-16")
            self.assertIn("<expert>", chart_text)
            self.assertIn("name=SQXInfoBridge", chart_text)
            self.assertIn("path=Experts\\SQXInfoBridge.ex5", chart_text)
            self.assertIn("InpDefaultSpreadTimeframe=PERIOD_M1", chart_text)
            self.assertEqual(template_text, chart_text)
            self.assertIn("Profile=SQX_AUTO11_BRIDGE_darwinex_USDJPY_Darwinex_M1", startup_text)

    def test_attach_apply_blocks_data_dir_outside_default_or_local_auto11(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            outside_data_dir = Path(outside_dir) / "terminal"
            with self.assertRaises(auto11.Auto11Error) as raised:
                auto11.attach_plan_payload(
                    Path(root_dir),
                    approval=auto11.AUTO11_ATTACH_APPROVAL_PHRASE,
                    apply=True,
                    mt5_files_dir=outside_data_dir / "MQL5" / "Files",
                    mt5_experts_dir=outside_data_dir / "MQL5" / "Experts",
                )

        self.assertEqual(raised.exception.code, "auto11_mt5_data_dir_not_allowed")

    def test_ui_fallback_plan_is_separately_gated(self):
        payload = auto11.ui_fallback_plan_payload(PROJECT_ROOT, apply=False)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "auto11_ui_fallback_plan_ready_separate_gate_required")
        self.assertTrue(payload["wouldUseVisibleOperatorControl"])
        self.assertFalse(payload["uiFallbackAllowedByGate"])

        with self.assertRaises(auto11.Auto11Error) as raised:
            auto11.ui_fallback_plan_payload(PROJECT_ROOT, approval="APRUEBO AUTO11 UI", apply=True)

        self.assertEqual(raised.exception.code, "auto11_ui_fallback_requires_exact_approval")

    def test_ui_fallback_apply_requires_existing_profile_assets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / ".local" / "mt5_auto11" / "terminal"

            with self.assertRaises(auto11.Auto11Error) as raised:
                auto11.ui_fallback_plan_payload(
                    root,
                    approval=auto11.AUTO11_UI_FALLBACK_APPROVAL_PHRASE,
                    apply=True,
                    mt5_files_dir=data_dir / "MQL5" / "Files",
                    mt5_experts_dir=data_dir / "MQL5" / "Experts",
                )

        self.assertEqual(raised.exception.code, "auto11_ui_fallback_profile_assets_missing_run_attach_writer_first")

    def test_ui_fallback_apply_handoffs_profile_and_verifies_heartbeat(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / ".local" / "mt5_auto11" / "terminal"
            files_dir = data_dir / "MQL5" / "Files"
            experts_dir = data_dir / "MQL5" / "Experts"
            auto11._write_profile_assets(root, mt5_files_dir=files_dir, mt5_experts_dir=experts_dir)

            with patch.object(auto11, "_target_process_state", return_value={"targetTerminalProcessRunning": True, "targetProcessCount": 1, "_targetPids": [123]}), \
                 patch.object(auto11, "_restore_visible_target_window", return_value={"windowFound": True, "windowRestored": True, "windowForegroundRequested": True, "windowTitleReturned": False}), \
                 patch.object(auto11, "_profile_handoff_to_mt5", return_value={"executed": True, "method": "visible_terminal_profile_config_handoff", "newTargetProcessObserved": False, "localPathsReturned": False}), \
                 patch.object(auto11, "_verify_ui_fallback_heartbeat", return_value={"ok": True, "status": "auto11_ui_fallback_bridge_ready", "requestWritten": True, "requestId": "sqx_auto11_ui_test"}):
                payload = auto11.ui_fallback_plan_payload(
                    root,
                    approval=auto11.AUTO11_UI_FALLBACK_APPROVAL_PHRASE,
                    apply=True,
                    mt5_files_dir=files_dir,
                    mt5_experts_dir=experts_dir,
                )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "auto11_ui_fallback_completed_bridge_ready")
        self.assertEqual(payload["statusMarker"], "auto11_ui_fallback_apply_visible_operator_control_completed")
        self.assertTrue(payload["uiFallbackAllowedByGate"])
        self.assertTrue(payload["visibleOperatorControl"])
        self.assertTrue(payload["writesMt5Files"])
        self.assertFalse(payload["launchesMt5"])
        self.assertTrue(payload["runsMt5Ea"])
        self.assertFalse(payload["placesOrders"])
        self.assertFalse(payload["privacy"]["localPathsReturned"])

    def test_invalid_timeframe_is_blocked(self):
        with self.assertRaises(auto11.Auto11Error) as raised:
            auto11.plan_payload(PROJECT_ROOT, timeframe="M2")

        self.assertEqual(raised.exception.code, "auto11_timeframe_not_supported")


if __name__ == "__main__":
    unittest.main()
