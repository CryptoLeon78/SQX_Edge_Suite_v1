import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import sqx144_mt5_auto2_datamanager as auto2
from core import sqx144_mt5_auto9_health_watchdog as auto9
from core import sqx144_mt5_bridge as bridge


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def valid_response(request_id: str = "req_1", symbol: str = "USDJPY_Darwinex") -> dict:
    return {
        "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "requestId": request_id,
        "status": "ok",
        "symbol": symbol,
        "mt5Symbol": symbol.replace("_Darwinex", ""),
        "properties": {"pointValue": 624.30546, "tickSizeForSqx": 0.01, "tickStepForSqx": 0.001},
        "spreadStats": {"samples": 768790, "p50": 0.4, "p75": 0.6, "p90": 0.7, "p95": 1.2},
        "yearlySpreadStats": [{"year": 2024}, {"year": 2025}],
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "placesOrders": False,
        "usesMigrationTool": False,
    }


class Sqx144Mt5Auto9HealthWatchdogTests(unittest.TestCase):
    def test_bridge_health_reports_missing_mt5_response_without_launching_mt5(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp) / "files"
            experts_dir = Path(tmp) / "experts"
            files_dir.mkdir()
            experts_dir.mkdir()
            request_id = "sqx_auto2_AUDCAD_Darwinex_test"
            (files_dir / bridge.DEFAULT_REQUEST_FILE).write_text(
                bridge.request_ini(symbol="AUDCAD_Darwinex", request_id=request_id),
                encoding="ascii",
            )

            with (
                patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir),
                patch.object(bridge, "DEFAULT_MT5_EXPERTS_DIR", experts_dir),
            ):
                payload = bridge.health_payload(
                    project_root=PROJECT_ROOT,
                    expected_request_id=request_id,
                    expected_symbol="AUDCAD_Darwinex",
                    mt5_process_running=False,
                )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["panelStatus"], "mt5_bridge_no_responde_o_no_esta_activo")
        self.assertFalse(payload["launchesMt5"])
        self.assertFalse(payload["runsMt5Ea"])
        self.assertFalse(payload["writesDataDb"])
        self.assertTrue(payload["request"]["present"])
        self.assertFalse(payload["latestResponse"]["present"])

    def test_auto2_validate_keeps_waiting_status_but_adds_bridge_health(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp) / "files"
            experts_dir = Path(tmp) / "experts"
            files_dir.mkdir()
            experts_dir.mkdir()
            with (
                patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir),
                patch.object(bridge, "DEFAULT_MT5_EXPERTS_DIR", experts_dir),
                patch.object(bridge, "_detect_mt5_process_running", return_value=False),
            ):
                request_payload = auto2.request_payload(PROJECT_ROOT, symbol="audcad_darwinex", spread_policy="p90")
                payload = auto2.validate_payload(
                    project_root=PROJECT_ROOT,
                    spread_policy="p90",
                    expected_request_id=request_payload["requestId"],
                    expected_symbol="AUDCAD_Darwinex",
                )

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status"], "waiting_for_requested_response")
        self.assertIn("bridgeHealth", payload)
        self.assertEqual(payload["bridgeHealth"]["panelStatus"], "mt5_bridge_no_responde_o_no_esta_activo")
        self.assertIn("latest_response_missing", payload["warnings"])
        self.assertFalse(payload["bridgeHealth"]["launchesMt5"])
        self.assertFalse(payload["bridgeHealth"]["runsMt5Ea"])

    def test_auto2_validate_reports_stale_mismatch_health_for_old_latest(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp) / "files"
            experts_dir = Path(tmp) / "experts"
            files_dir.mkdir()
            experts_dir.mkdir()
            with (
                patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir),
                patch.object(bridge, "DEFAULT_MT5_EXPERTS_DIR", experts_dir),
                patch.object(bridge, "_detect_mt5_process_running", return_value=False),
            ):
                request_payload = auto2.request_payload(PROJECT_ROOT, symbol="eurgbp_darwinex", spread_policy="p90")
                (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(
                    json.dumps(valid_response("old_req", symbol="EURGBP_Darwinex")),
                    encoding="utf-8",
                )
                payload = auto2.validate_payload(
                    project_root=PROJECT_ROOT,
                    spread_policy="p90",
                    expected_request_id=request_payload["requestId"],
                    expected_symbol="EURGBP_Darwinex",
                )

        self.assertEqual(payload["status"], "waiting_for_requested_response")
        self.assertEqual(payload["bridgeHealth"]["panelStatus"], "mt5_bridge_no_responde_o_no_esta_activo")
        self.assertFalse(payload["bridgeHealth"]["requestIdMatches"])
        self.assertIn("latest_response_request_id_mismatch", payload["warnings"])

    def test_auto9_status_and_automation_plan_are_observe_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp) / "files"
            experts_dir = Path(tmp) / "experts"
            files_dir.mkdir()
            experts_dir.mkdir()
            with (
                patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir),
                patch.object(bridge, "DEFAULT_MT5_EXPERTS_DIR", experts_dir),
                patch.object(bridge, "_detect_mt5_process_running", return_value=False),
            ):
                status = auto9.status_payload(PROJECT_ROOT)
                plan = auto9.automation_plan_payload(PROJECT_ROOT)

        self.assertTrue(status["ok"])
        self.assertEqual(status["version"], auto9.SQX144_MT5_AUTO9_VERSION)
        self.assertTrue(status["healthWatchdogObserveOnly"])
        self.assertFalse(status["autoStartAllowed"])
        self.assertFalse(status["launchesMt5"])
        self.assertFalse(status["runsMt5Ea"])
        self.assertFalse(status["writesDataDb"])
        self.assertEqual(plan["status"], "auto10_internal_mt5_runner_design_only_no_execution")
        self.assertTrue(plan["blockedUntilFutureGate"]["launchMt5"])


if __name__ == "__main__":
    unittest.main()
