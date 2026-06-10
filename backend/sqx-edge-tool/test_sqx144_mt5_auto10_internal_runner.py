import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import sqx144_mt5_auto10_internal_runner as auto10


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Sqx144Mt5Auto10InternalRunnerTests(unittest.TestCase):
    def test_default_mt5_root_uses_standard_darwinex_not_bepb(self):
        self.assertEqual(auto10.DEFAULT_MT5_ROOT.name, "Darwinex MetaTrader 5")
        self.assertNotIn("BEPB", str(auto10.DEFAULT_MT5_ROOT))

    def _fake_mt5_layout(self, tmp: str, *, terminal: bool = True, metaeditor: bool = True):
        root = Path(tmp) / "mt5"
        files = Path(tmp) / "files"
        experts = Path(tmp) / "experts"
        root.mkdir()
        files.mkdir()
        experts.mkdir()
        if terminal:
            (root / auto10.DEFAULT_TERMINAL_EXE_NAME).write_text("fake terminal", encoding="utf-8")
        if metaeditor:
            (root / auto10.DEFAULT_METAEDITOR_EXE_NAME).write_text("fake metaeditor", encoding="utf-8")
        return root, files, experts

    def test_discover_reports_fake_paths_without_returning_local_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            mt5_root, files_dir, experts_dir = self._fake_mt5_layout(tmp)
            with patch.object(auto10, "_detect_process_state", return_value={"known": True, "terminalProcessRunning": False, "processCount": 0}):
                payload = auto10.discover_payload(
                    PROJECT_ROOT,
                    mt5_root=mt5_root,
                    mt5_files_dir=files_dir,
                    mt5_experts_dir=experts_dir,
                )

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["terminal"]["present"])
        self.assertTrue(payload["metaeditor"]["present"])
        self.assertTrue(payload["filesDir"]["present"])
        self.assertTrue(payload["expertsDir"]["present"])
        self.assertTrue(payload["bridgeSource"]["present"])
        self.assertFalse(payload["privacy"]["localPathsReturned"])
        self.assertNotIn(str(mt5_root), json.dumps(payload))

    def test_preflight_blocks_missing_terminal_without_launching(self):
        with tempfile.TemporaryDirectory() as tmp:
            mt5_root, files_dir, experts_dir = self._fake_mt5_layout(tmp, terminal=False)
            with patch.object(auto10, "_detect_process_state", return_value={"known": True, "terminalProcessRunning": False, "processCount": 0}):
                payload = auto10.preflight_payload(
                    PROJECT_ROOT,
                    mt5_root=mt5_root,
                    mt5_files_dir=files_dir,
                    mt5_experts_dir=experts_dir,
                )

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status"], "auto10_preflight_blocked_no_launch")
        self.assertIn("mt5_terminal_exe_missing", payload["blockers"])
        self.assertFalse(payload["launchesMt5"])
        self.assertFalse(payload["runsMt5Ea"])
        self.assertFalse(payload["writesDataDb"])

    def test_preflight_warns_when_installed_source_hash_differs(self):
        with tempfile.TemporaryDirectory() as tmp:
            mt5_root, files_dir, experts_dir = self._fake_mt5_layout(tmp)
            (experts_dir / auto10.DEFAULT_BRIDGE_SOURCE_NAME).write_text("different source", encoding="utf-8")
            with patch.object(auto10, "_detect_process_state", return_value={"known": True, "terminalProcessRunning": False, "processCount": 0}):
                payload = auto10.preflight_payload(
                    PROJECT_ROOT,
                    mt5_root=mt5_root,
                    mt5_files_dir=files_dir,
                    mt5_experts_dir=experts_dir,
                )

        self.assertTrue(payload["ok"])
        self.assertIn("bridge_source_hash_differs_from_installed", payload["warnings"])

    def test_install_source_dry_run_does_not_copy_or_compile(self):
        with tempfile.TemporaryDirectory() as tmp:
            mt5_root, _files_dir, experts_dir = self._fake_mt5_layout(tmp)
            target = experts_dir / auto10.DEFAULT_BRIDGE_SOURCE_NAME
            payload = auto10.install_source_payload(
                PROJECT_ROOT,
                mt5_root=mt5_root,
                mt5_experts_dir=experts_dir,
                apply=False,
            )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "auto10_install_source_ready_apply_required")
        self.assertFalse(target.exists())
        self.assertFalse(payload["writesMt5Source"])
        self.assertFalse(payload["launchesMt5"])

    def test_launch_plan_does_not_spawn_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            mt5_root, _files_dir, _experts_dir = self._fake_mt5_layout(tmp)
            with patch.object(auto10.subprocess, "Popen") as popen:
                payload = auto10.launch_payload(PROJECT_ROOT, mt5_root=mt5_root, apply=False)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "auto10_launch_ready_apply_required")
        self.assertFalse(payload["launchesMt5"])
        popen.assert_not_called()

    def test_launch_apply_requires_exact_approval(self):
        with self.assertRaises(auto10.Auto10Error) as raised:
            auto10.launch_payload(PROJECT_ROOT, approval="APRUEBO AUTO10", apply=True)

        self.assertEqual(raised.exception.code, "auto10_launch_requires_exact_approval")

    def test_verify_dry_run_does_not_write_request(self):
        payload = auto10.verify_payload(PROJECT_ROOT, symbol="AUDCAD_Darwinex", apply=False)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "auto10_verify_smoke_ready_apply_required")
        self.assertTrue(payload["wouldWriteBridgeRequest"])
        self.assertFalse(payload["writesMt5Files"])
        self.assertFalse(payload["launchesMt5"])

    def test_stop_dry_run_is_limited_to_managed_pid(self):
        payload = auto10.stop_payload(PROJECT_ROOT, apply=False)

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["stopsOnlyManagedAuto10Pid"])
        self.assertEqual(payload["status"], "auto10_stop_ready_apply_required")


if __name__ == "__main__":
    unittest.main()
