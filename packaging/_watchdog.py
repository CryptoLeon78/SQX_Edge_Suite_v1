"""
_watchdog.py -- Parent-PID watchdog for the SQX Edge sidecar.

Polls the Electron parent process and self-terminates when it disappears
(crash, SIGKILL, hard close).  No external dependencies; stdlib only.
"""
from __future__ import annotations

import logging
import os
import sys
import threading
import time

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Platform: liveness probe
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    # Open the handle once so PID reuse between polls cannot produce a false
    # "alive" reading.  SYNCHRONIZE is the minimum right needed for WFSO.
    _SYNCHRONIZE = 0x00100000
    _WAIT_TIMEOUT = 0x00000102  # still running

    _k32.OpenProcess.restype  = ctypes.wintypes.HANDLE
    _k32.OpenProcess.argtypes = [
        ctypes.wintypes.DWORD,
        ctypes.wintypes.BOOL,
        ctypes.wintypes.DWORD,
    ]
    _k32.WaitForSingleObject.restype  = ctypes.wintypes.DWORD
    _k32.WaitForSingleObject.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
    ]

    _handle_cache: dict[int, int] = {}

    def _parent_alive(pid: int) -> bool:
        handle = _handle_cache.get(pid)
        if handle is None:
            handle = _k32.OpenProcess(_SYNCHRONIZE, False, pid)
            if not handle:
                return False  # process gone or PID never existed
            _handle_cache[pid] = handle
        return _k32.WaitForSingleObject(handle, 0) == _WAIT_TIMEOUT

else:
    def _parent_alive(pid: int) -> bool:  # type: ignore[misc]
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True  # process exists; we just cannot signal it


# ---------------------------------------------------------------------------
# Watchdog
# ---------------------------------------------------------------------------

def _default_on_dead() -> None:
    _log.warning("parent gone -> sidecar self-terminating")
    os._exit(0)


def start_parent_watchdog(
    poll: float = 2.0,
    on_dead=None,
    _alive_fn=None,
) -> None:
    """
    Start a daemon thread that polls SQX_PARENT_PID and calls *on_dead* when
    that process disappears.

    Inert (no thread started) when SQX_PARENT_PID is absent, empty, "0",
    non-integer, or equal to this process's own PID.

    *_alive_fn* overrides the platform liveness probe (test injection only).
    """
    raw = os.environ.get("SQX_PARENT_PID", "").strip()
    if not raw or raw == "0":
        return
    try:
        parent_pid = int(raw)
    except ValueError:
        return
    if parent_pid == os.getpid():
        return

    callback = on_dead if on_dead is not None else _default_on_dead
    alive = _alive_fn if _alive_fn is not None else _parent_alive

    def _watch() -> None:
        while True:
            time.sleep(poll)
            if not alive(parent_pid):
                _log.warning("parent %d gone -> sidecar self-terminating", parent_pid)
                callback()
                return  # on_dead may not exit; return so thread ends cleanly

    t = threading.Thread(target=_watch, daemon=True, name="sqx-parent-watchdog")
    t.start()
    _log.debug("parent watchdog started for PID %d (poll=%.1f s)", parent_pid, poll)
