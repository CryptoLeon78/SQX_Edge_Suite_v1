"""
Tests for packaging/_watchdog.py

Run as part of the normal pytest suite (testpaths includes backend/sqx-edge-tool).
"""
import os
import sys
import threading
import time
import unittest
from pathlib import Path

# Make packaging/_watchdog importable without modifying pytest.ini.
_PACKAGING = Path(__file__).resolve().parents[2] / "packaging"
if str(_PACKAGING) not in sys.path:
    sys.path.insert(0, str(_PACKAGING))

from _watchdog import _parent_alive, _wfso_alive, start_parent_watchdog  # noqa: E402


class TestWfsoAlive(unittest.TestCase):
    """Cross-platform: _wfso_alive is module-level and runs on any OS."""

    def test_wait_object_0_is_dead(self):
        self.assertFalse(_wfso_alive(0x00000000))  # WAIT_OBJECT_0 -> terminated

    def test_wait_timeout_is_alive(self):
        self.assertTrue(_wfso_alive(0x00000102))   # WAIT_TIMEOUT -> still running

    def test_wait_failed_is_alive(self):
        self.assertTrue(_wfso_alive(0xFFFFFFFF))   # WAIT_FAILED -> assume alive (fail-safe)


class TestParentAlive(unittest.TestCase):
    def test_own_pid_is_alive(self):
        self.assertTrue(_parent_alive(os.getpid()))

    def test_unused_high_pid_is_not_alive(self):
        # 99999 is not a multiple of 4, so it can never be a valid Windows PID;
        # on Linux it is almost certainly free in a test environment.
        self.assertFalse(_parent_alive(99999))


class TestWatchdogInert(unittest.TestCase):
    """Regression guard: no thread must start when the guard conditions apply."""

    def _assert_no_new_thread(self, env_setup, env_cleanup):
        """Helper: set up env, call start_parent_watchdog, assert thread count unchanged."""
        env_setup()
        called = []
        count_before = threading.active_count()
        try:
            start_parent_watchdog(on_dead=lambda: called.append(1))
            self.assertEqual(threading.active_count(), count_before,
                             "watchdog must not start a thread when inert")
            self.assertEqual(called, [], "on_dead must not be called when inert")
        finally:
            env_cleanup()

    def test_no_env_var(self):
        backup = os.environ.pop("SQX_PARENT_PID", None)
        self._assert_no_new_thread(lambda: None, lambda: (
            os.environ.__setitem__("SQX_PARENT_PID", backup) if backup is not None else None
        ))

    def test_empty_string(self):
        self._assert_no_new_thread(
            lambda: os.environ.__setitem__("SQX_PARENT_PID", ""),
            lambda: os.environ.__delitem__("SQX_PARENT_PID"),
        )

    def test_zero(self):
        self._assert_no_new_thread(
            lambda: os.environ.__setitem__("SQX_PARENT_PID", "0"),
            lambda: os.environ.__delitem__("SQX_PARENT_PID"),
        )

    def test_non_integer(self):
        self._assert_no_new_thread(
            lambda: os.environ.__setitem__("SQX_PARENT_PID", "notanint"),
            lambda: os.environ.__delitem__("SQX_PARENT_PID"),
        )

    def test_own_pid(self):
        self._assert_no_new_thread(
            lambda: os.environ.__setitem__("SQX_PARENT_PID", str(os.getpid())),
            lambda: os.environ.__delitem__("SQX_PARENT_PID"),
        )


class TestWatchdogLoop(unittest.TestCase):
    """Drive the poll loop with injected probes -- no real sleeps beyond poll=0.01."""

    def setUp(self):
        os.environ["SQX_PARENT_PID"] = "99999"

    def tearDown(self):
        os.environ.pop("SQX_PARENT_PID", None)

    def test_dead_parent_calls_on_dead_exactly_once(self):
        called = []
        done = threading.Event()

        def on_dead():
            called.append(1)
            done.set()

        start_parent_watchdog(poll=0.01, on_dead=on_dead, _alive_fn=lambda pid: False)
        self.assertTrue(done.wait(timeout=2.0), "on_dead must be called within 2 s")
        self.assertEqual(called, [1], "on_dead must be called exactly once")

    def test_alive_parent_does_not_call_on_dead(self):
        called = []

        start_parent_watchdog(
            poll=0.01,
            on_dead=lambda: called.append(1),
            _alive_fn=lambda pid: True,
        )
        time.sleep(0.05)
        self.assertEqual(called, [], "on_dead must not be called while parent is alive")


if __name__ == "__main__":
    unittest.main()
