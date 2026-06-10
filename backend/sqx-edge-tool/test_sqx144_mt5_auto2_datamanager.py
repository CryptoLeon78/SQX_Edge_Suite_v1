import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from api import server
from core import local_memory_outbox
from core import sqx144_mt5_auto2_datamanager as auto2
from core import sqx144_mt5_bridge as bridge


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def valid_response(request_id: str = "req_1", symbol: str = "USDJPY_Darwinex") -> dict:
    return {
        "version": bridge.SQX144_MT5_AUTO1_BRIDGE_VERSION,
        "requestId": request_id,
        "status": "ok",
        "symbol": symbol,
        "mt5Symbol": "USDJPY",
        "properties": {"pointValue": 624.30546, "tickSizeForSqx": 0.01, "tickStepForSqx": 0.001},
        "spreadStats": {"samples": 768790, "p50": 0.4, "p75": 0.6, "p90": 0.7, "p95": 1.2, "p99": 6.5},
        "yearlySpreadStats": [{"year": 2024}, {"year": 2025}, {"year": 2026}],
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "placesOrders": False,
        "usesMigrationTool": False,
    }


class Sqx144Mt5Auto2DataManagerTests(unittest.TestCase):
    def test_normalize_datamanager_symbol_preserves_darwinex_bridge_shape(self):
        self.assertEqual(auto2.normalize_datamanager_symbol("usdjpy_darwinex"), "USDJPY_Darwinex")
        self.assertEqual(auto2.normalize_datamanager_symbol("EURUSD"), "EURUSD")

    def test_request_payload_writes_only_mt5_request_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp)
            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
                payload = auto2.request_payload(PROJECT_ROOT, symbol="usdjpy_darwinex", spread_policy="p90")

            request_file = files_dir / bridge.DEFAULT_REQUEST_FILE
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "mt5_bridge_request_written")
            self.assertEqual(payload["symbol"], "USDJPY_Darwinex")
            self.assertTrue(request_file.is_file())
            text = request_file.read_text(encoding="ascii")
            self.assertIn("symbol=USDJPY_Darwinex", text)
            self.assertFalse(payload["writesDataDb"])
            self.assertFalse(payload["writesUserProjects"])
        self.assertFalse(payload["mutatesDatabanks"])
        self.assertTrue(payload["doesNotApplyToSqx"])
        self.assertTrue(payload["doesNotApplyInstrumentConfig"])

    def test_validate_payload_waits_for_matching_request_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp)
            (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(json.dumps(valid_response("old_req")), encoding="utf-8")
            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
                payload = auto2.validate_payload(spread_policy="p90", expected_request_id="new_req")

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status"], "waiting_for_requested_response")
        self.assertIn("latest_response_request_id_mismatch", payload["warnings"])
        self.assertIn("mt5_bridge_no_request_pending", payload["warnings"])
        self.assertEqual(payload["blockers"], [])

    def test_audcad_request_then_old_usdjpy_response_waits_without_symbol_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp)
            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
                request_payload = auto2.request_payload(PROJECT_ROOT, symbol="audcad_darwinex", spread_policy="p90")
                (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(
                    json.dumps(valid_response("old_usdjpy_req", symbol="USDJPY_Darwinex")),
                    encoding="utf-8",
                )
                validate_payload = auto2.validate_payload(
                    spread_policy="p90",
                    expected_request_id=request_payload["requestId"],
                    expected_symbol="AUDCAD_Darwinex",
                )
                request_text = (files_dir / bridge.DEFAULT_REQUEST_FILE).read_text(encoding="ascii")

        self.assertTrue(request_payload["ok"])
        self.assertEqual(request_payload["symbol"], "AUDCAD_Darwinex")
        self.assertIn("symbol=AUDCAD_Darwinex", request_text)
        self.assertFalse(validate_payload["ok"])
        self.assertEqual(validate_payload["status"], "waiting_for_requested_response")
        self.assertIn("latest_response_request_id_mismatch", validate_payload["warnings"])
        self.assertNotIn("latest_response_symbol_mismatch", validate_payload["blockers"])

    def test_validate_payload_blocks_symbol_mismatch_after_request_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp)
            (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(
                json.dumps(valid_response("req_ok", symbol="EURUSD_Darwinex")),
                encoding="utf-8",
            )
            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
                payload = auto2.validate_payload(
                    spread_policy="p90",
                    expected_request_id="req_ok",
                    expected_symbol="USDJPY_darwinex",
                )

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status"], "bridge_response_blocked")
        self.assertIn("latest_response_symbol_mismatch", payload["blockers"])

    def test_validate_payload_proposes_p90_fields_without_sqx_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp)
            (files_dir / bridge.DEFAULT_RESPONSE_FILE).write_text(json.dumps(valid_response("req_ok")), encoding="utf-8")
            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
                payload = auto2.validate_payload(spread_policy="p90", expected_request_id="req_ok")

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "bridge_response_validated")
        self.assertEqual(payload["proposedSqxFields"]["DEFAULTSPREAD"], 0.7)
        self.assertFalse(payload["writesDataDb"])
        self.assertFalse(payload["runsSqxTasks"])
        self.assertTrue(payload["doesNotApplyToSqx"])

    def test_status_payload_reports_installed_overlay_from_host_assets_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            tool_root = root / "backend" / "sqx-edge-tool"
            source_root = root / "integrations" / "sqx144" / "datamanager_mt5_auto2_overlay"
            host_root = Path(tmp) / "SQX_144_Full"
            common_root = host_root / "internal" / "web" / "common"
            index_root = host_root / "internal" / "web" / "SQMANAGER"
            bridge_source_root = root / "integrations" / "sqx144" / "mt5_bridge"
            files_dir = Path(tmp) / "mt5-files"
            experts_dir = Path(tmp) / "mt5-experts"
            for path in (tool_root, source_root, common_root, index_root, bridge_source_root, files_dir, experts_dir):
                path.mkdir(parents=True)
            (tool_root / "config.json").write_text(json.dumps({"sqx_path": str(host_root)}), encoding="utf-8")
            (source_root / auto2.OVERLAY_JS_NAME).write_text(auto2.AUTO4_MARKER, encoding="utf-8")
            (source_root / auto2.OVERLAY_CSS_NAME).write_text("/* source */", encoding="utf-8")
            (common_root / auto2.OVERLAY_JS_NAME).write_text(auto2.AUTO4_MARKER, encoding="utf-8")
            (common_root / auto2.OVERLAY_CSS_NAME).write_text("/* installed */", encoding="utf-8")
            (index_root / "index.html").write_text(
                '<link rel="stylesheet" href="../common/sqx-edge-mt5-auto2.css">'
                '<script src="../common/sqx-edge-mt5-auto2.js"></script>',
                encoding="utf-8",
            )
            (bridge_source_root / "SQXInfoBridge.mq5").write_text("// bridge", encoding="utf-8")

            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir), patch.object(bridge, "DEFAULT_MT5_EXPERTS_DIR", experts_dir):
                payload = auto2.status_payload(root)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], auto2.AUTO4_STATUS_INSTALLED)
        self.assertTrue(payload["dataManagerButtonInstalled"])
        self.assertTrue(payload["installed"])
        self.assertTrue(payload["assetsPresent"])
        self.assertTrue(payload["sourcesPresent"])
        self.assertTrue(payload["sourceHasAuto4"])
        self.assertTrue(payload["targetHasAuto4"])
        self.assertEqual(payload["includeCount"], 2)
        self.assertTrue(payload["hostRootAccepted"])
        self.assertFalse(payload["writesDataDb"])
        self.assertTrue(payload["doesNotApplyInstrumentConfig"])

    def test_flask_auto2_request_endpoint_is_local_operator_only_and_safe(self):
        client = server.app.test_client()
        with tempfile.TemporaryDirectory() as tmp:
            files_dir = Path(tmp)
            with patch.object(bridge, "DEFAULT_MT5_FILES_DIR", files_dir):
                response = client.post(
                    "/api/sqx144/mt5-auto2/request",
                    json={"symbol": "USDJPY_darwinex", "spreadPolicy": "p90"},
                )

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode("utf-8"))
            self.assertTrue(data["ok"])
            self.assertEqual(data["version"], auto2.SQX144_MT5_AUTO2_VERSION)
            self.assertEqual(data["symbol"], "USDJPY_Darwinex")
            self.assertFalse(data["writesDataDb"])
            self.assertTrue((files_dir / bridge.DEFAULT_REQUEST_FILE).is_file())

    def test_local_memory_outbox_enqueue_list_and_mark_synced(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "memory_outbox.sqlite"
            enqueued = local_memory_outbox.enqueue_note(
                db_path,
                title="SQX memory note",
                content="durable content",
                tags=["sqx", "auto2"],
            )
            listed = local_memory_outbox.list_notes(db_path)
            synced = local_memory_outbox.mark_synced(db_path, outbox_id=enqueued["outboxId"], mem_note_id="mem-1")

        self.assertTrue(enqueued["ok"])
        self.assertEqual(enqueued["pendingCount"], 1)
        self.assertEqual(listed["notes"][0]["title"], "SQX memory note")
        self.assertTrue(synced["ok"])
        self.assertEqual(synced["pendingCount"], 0)


if __name__ == "__main__":
    unittest.main()
