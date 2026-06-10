import json
import tempfile
import unittest
from pathlib import Path

from core import sqx144_mt5_bridge as bridge


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_TEST_ROOT = PROJECT_ROOT / ".local" / "mt5_bridge_auto1" / "tests"


def local_temp_dir():
    LOCAL_TEST_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=LOCAL_TEST_ROOT)


class Sqx144Mt5Auto1DataManagerBridgeTests(unittest.TestCase):
    def test_request_ini_contains_symbol_and_bridge_contract(self):
        text = bridge.request_ini(
            symbol="USDJPY_Darwinex",
            request_id="req_001",
            spread_timeframe="M1",
            from_year=2018,
            to_year=2026,
            max_bars=1000,
        )

        self.assertIn("version=sqx144-mt5-auto1-data-manager-bridge-v1", text)
        self.assertIn("requestId=req_001", text)
        self.assertIn("symbol=USDJPY_Darwinex", text)
        self.assertIn("spreadTimeframe=M1", text)
        self.assertIn("fromYear=2018", text)
        self.assertIn("toYear=2026", text)
        self.assertIn("maxBars=1000", text)

    def test_status_reports_source_and_never_sqx_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp) / "Files"
            experts_dir = Path(tmp) / "Experts"
            files_dir.mkdir()
            experts_dir.mkdir()

            payload = bridge.status_payload(PROJECT_ROOT, mt5_files_dir=files_dir, mt5_experts_dir=experts_dir)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["phase"], "SQX144-MT5-AUTO1")
        self.assertEqual(payload["host"], "sqx144_full")
        self.assertTrue(payload["sourcePresent"])
        self.assertEqual(payload["defaultSpreadPolicy"], "p90")
        self.assertFalse(payload["writesSqxHost"])
        self.assertFalse(payload["writesDataDb"])
        self.assertFalse(payload["writesUserProjects"])
        self.assertFalse(payload["mutatesDatabanks"])
        self.assertFalse(payload["runsSqxTasks"])
        self.assertTrue(payload["dataManagerButtonPlanned"])
        self.assertFalse(payload["dataManagerButtonInstalled"])

    def test_write_request_is_apply_gated(self):
        with local_temp_dir() as tmp:
            files_dir = Path(tmp)
            dry_run = bridge.write_request_payload(
                symbol="EURUSD_Darwinex",
                request_id="req_dry",
                mt5_files_dir=files_dir,
                project_root=PROJECT_ROOT,
                apply=False,
            )
            self.assertEqual(dry_run["status"], "request_ready_apply_required")
            self.assertFalse((files_dir / bridge.DEFAULT_REQUEST_FILE).exists())

            written = bridge.write_request_payload(
                symbol="EURUSD_Darwinex",
                request_id="req_write",
                mt5_files_dir=files_dir,
                project_root=PROJECT_ROOT,
                apply=True,
            )

            self.assertEqual(written["status"], "request_written_for_mt5_bridge")
            self.assertTrue((files_dir / bridge.DEFAULT_REQUEST_FILE).is_file())
            self.assertIn("symbol=EURUSD_Darwinex", (files_dir / bridge.DEFAULT_REQUEST_FILE).read_text(encoding="ascii"))

    def test_write_request_apply_blocks_unallowed_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(bridge.BridgeError) as ctx:
                bridge.write_request_payload(
                    symbol="EURUSD_Darwinex",
                    request_id="req_blocked",
                    mt5_files_dir=tmp,
                    project_root=PROJECT_ROOT,
                    apply=True,
                )
        self.assertEqual(ctx.exception.code, "mt5_files_dir_not_allowed")

    def test_install_source_is_apply_gated(self):
        with local_temp_dir() as tmp:
            experts_dir = Path(tmp)
            dry_run = bridge.install_source_payload(PROJECT_ROOT, mt5_experts_dir=experts_dir, apply=False)
            self.assertEqual(dry_run["status"], "install_source_ready_apply_required")
            self.assertFalse((experts_dir / "SQXInfoBridge.mq5").exists())

            installed = bridge.install_source_payload(PROJECT_ROOT, mt5_experts_dir=experts_dir, apply=True)

            self.assertEqual(installed["status"], "bridge_source_installed_to_mt5_experts")
            self.assertIn("SQXInfoBridge", (experts_dir / "SQXInfoBridge.mq5").read_text(encoding="utf-8"))

    def test_install_source_apply_requires_overwrite_for_existing_source(self):
        with local_temp_dir() as tmp:
            experts_dir = Path(tmp)
            (experts_dir / "SQXInfoBridge.mq5").write_text("// existing\n", encoding="utf-8")
            with self.assertRaises(bridge.BridgeError) as ctx:
                bridge.install_source_payload(PROJECT_ROOT, mt5_experts_dir=experts_dir, apply=True)
            self.assertEqual(ctx.exception.code, "mt5_bridge_source_exists_requires_overwrite")

            installed = bridge.install_source_payload(PROJECT_ROOT, mt5_experts_dir=experts_dir, apply=True, overwrite=True)
            self.assertTrue(installed["overwroteExistingSource"])

    def test_validate_bridge_response_proposes_selected_spread_percentile(self):
        response = {
            "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
            "requestId": "req_002",
            "status": "ok",
            "symbol": "USDJPY_Darwinex",
            "properties": {
                "pointValue": 624.93,
                "tickSizeForSqx": 0.01,
                "tickStepForSqx": 0.001,
            },
            "spreadStats": {
                "samples": 250000,
                "mean": 0.63,
                "p50": 0.5,
                "p75": 0.7,
                "p90": 1.1,
                "p95": 1.4,
                "p99": 2.2,
            },
            "yearlySpreadStats": [
                {"year": 2024, "samples": 120000, "p90": 1.0},
                {"year": 2025, "samples": 130000, "p90": 1.2},
            ],
            "writesSqxHost": False,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "runsSqxTasks": False,
            "placesOrders": False,
            "usesMigrationTool": False,
        }

        payload = bridge.validate_bridge_response(response, spread_policy="p90")

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "bridge_response_validated")
        self.assertEqual(payload["yearCount"], 2)
        self.assertEqual(payload["proposedSqxFields"]["DEFAULTSPREAD"], 1.1)
        self.assertEqual(payload["proposedSqxFields"]["spreadPolicy"], "p90")
        self.assertEqual(payload["proposedSqxFields"]["POINTVALUE"], 624.93)

    def test_validate_response_blocks_unsafe_flags_and_invalid_numbers(self):
        response = {
            "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
            "requestId": "req_bad",
            "status": "ok",
            "symbol": "USDJPY_Darwinex",
            "properties": {"pointValue": "nan"},
            "spreadStats": {"samples": 1, "p90": "nan"},
            "writesDataDb": True,
        }

        payload = bridge.validate_bridge_response(response, spread_policy="p90")

        self.assertFalse(payload["ok"])
        self.assertIn("unsafe_response_flag_writesDataDb", payload["blockers"])
        self.assertIn("spread_policy_value_missing", payload["blockers"])

    def test_validate_response_payload_reads_json_file(self):
        response = {
            "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
            "requestId": "req_file",
            "status": "ok",
            "symbol": "GBPJPY_Darwinex",
            "properties": {"pointValue": 650.0, "tickSizeForSqx": 0.01, "tickStepForSqx": 0.001},
            "spreadStats": {"samples": 2000, "p90": 1.6},
            "yearlySpreadStats": [],
            "writesSqxHost": False,
            "writesDataDb": False,
            "writesUserProjects": False,
            "mutatesDatabanks": False,
            "runsSqxTasks": False,
            "placesOrders": False,
            "usesMigrationTool": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / bridge.DEFAULT_RESPONSE_FILE
            path.write_text(json.dumps(response), encoding="utf-8")
            payload = bridge.validate_response_payload(response_path=path, spread_policy="p90")

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["symbol"], "GBPJPY_Darwinex")

    def test_invalid_spread_policy_is_blocked(self):
        with self.assertRaises(bridge.BridgeError):
            bridge.validate_bridge_response({"version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION}, spread_policy="p10")


if __name__ == "__main__":
    unittest.main()
