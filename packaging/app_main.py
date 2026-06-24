"""
app_main.py -- Nuitka-frozen entry point for SQX Edge desktop build.

When running as a Nuitka --standalone compiled executable, __compiled__ is
defined as a compile-time constant.  We detect it and set SQX_APP_ROOT to the
executable directory BEFORE any application module is imported, so that
core.app_paths picks up the frozen-build root rather than non-existent __file__
locations inside the compiled binary.

In dev (python packaging/app_main.py), __compiled__ raises NameError, the guard
is a no-op, and core.app_paths falls back to the standard __file__-based
resolution -- identical behaviour to running the app normally.

Environment variables:
  SQX_HOST         Override Flask listen host (default: 127.0.0.1)
  SQX_PORT         Override Flask listen port (default: random free port)
  SQX_NO_WINDOW=1  Headless mode: start Flask only, no native window.
                   Use for tests, API spikes, or CI.
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


def _set_app_root_if_frozen() -> None:
    """Set SQX_APP_ROOT to the executable directory when running as a frozen build."""
    if os.environ.get("SQX_APP_ROOT"):
        return
    try:
        _ = __compiled__  # noqa: F821 -- Nuitka defines this at build time
        exe_dir = Path(sys.executable).resolve().parent
        os.environ["SQX_APP_ROOT"] = str(exe_dir)
    except NameError:
        pass  # dev mode -- core.app_paths will use __file__-based fallback


_set_app_root_if_frozen()

# Add sqx-edge-tool to sys.path for dev runs so core/ and api/ are importable.
_TOOL_ROOT = Path(__file__).resolve().parents[1] / "backend" / "sqx-edge-tool"
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

# Import AFTER setting SQX_APP_ROOT so core.app_paths sees the env var.
from api.server import app, DEFAULT_HOST, DEFAULT_PORT, DASHBOARD_ROOT  # noqa: E402

# Register the dashboard-serving routes on the same Flask app so the browser
# sees a single origin for both UI and API.  Must happen before app.run().
from dashboard_routes import register_dashboard_routes  # noqa: E402
register_dashboard_routes(app, DASHBOARD_ROOT)

# Headless guard -- read once at import so tests can inspect the flag.
_NO_WINDOW = os.environ.get("SQX_NO_WINDOW", "").strip() not in ("", "0")


# ---- helpers ----------------------------------------------------------------

def _free_port() -> int:
    """Return an OS-assigned free port on 127.0.0.1."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_health(host: str, port: int, timeout: float = 15.0) -> bool:
    """Poll /api/health until Flask responds or timeout expires."""
    url = f"http://{host}:{port}/api/health"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.1)
    return False


# ---- entry point ------------------------------------------------------------

def main() -> None:
    host = os.environ.get("SQX_HOST", str(DEFAULT_HOST))
    raw_port = os.environ.get("SQX_PORT", "").strip()
    port = int(raw_port) if raw_port else _free_port()

    if _NO_WINDOW:
        # Headless: block in the main thread (test / API spike mode).
        print(f"SQX Edge (headless) at http://{host}:{port}")
        app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)
        return

    # Window mode: run Flask in a daemon thread, wait for it, then open webview.
    flask_thread = threading.Thread(
        target=lambda: app.run(
            host=host, port=port, debug=False, use_reloader=False, threaded=True
        ),
        daemon=True,
    )
    flask_thread.start()

    if not _wait_for_health(host, port, timeout=15.0):
        print(f"[SQX] Flask did not become ready on port {port} within 15 s", flush=True)
        sys.exit(1)

    import webview  # only import when we actually need the native window
    webview.create_window("SQX Edge", f"http://{host}:{port}/")
    webview.start()


if __name__ == "__main__":
    main()
