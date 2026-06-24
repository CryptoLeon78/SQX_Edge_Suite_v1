"""
app_main.py — Nuitka-frozen entry point for SQX Edge desktop build.

When running as a Nuitka --standalone compiled executable, __compiled__ is
defined as a compile-time constant.  We detect it and set SQX_APP_ROOT to the
executable's directory BEFORE any application module is imported, so that
core.app_roots picks up the frozen-build root rather than non-existent __file__
locations inside the compiled binary.

In dev (python packaging/app_main.py), __compiled__ raises NameError, the guard
is a no-op, and core.app_paths falls back to the standard __file__-based
resolution — identical behaviour to running the app normally.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _set_app_root_if_frozen() -> None:
    """Set SQX_APP_ROOT to the executable directory when running as a frozen build."""
    if os.environ.get("SQX_APP_ROOT"):
        return
    try:
        _ = __compiled__  # noqa: F821 — Nuitka defines this at build time
        exe_dir = Path(sys.executable).resolve().parent
        os.environ["SQX_APP_ROOT"] = str(exe_dir)
    except NameError:
        pass  # dev mode — core.app_paths will use __file__-based fallback


_set_app_root_if_frozen()

# Add sqx-edge-tool to sys.path for dev runs so core/ is importable
_TOOL_ROOT = Path(__file__).resolve().parents[1] / "backend" / "sqx-edge-tool"
if str(_TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(_TOOL_ROOT))

# Import AFTER setting SQX_APP_ROOT so core.app_paths sees the env var
from api.server import app, DEFAULT_HOST, DEFAULT_PORT  # noqa: E402


def main() -> None:
    host = os.environ.get("SQX_HOST", str(DEFAULT_HOST))
    port = int(os.environ.get("SQX_PORT", str(DEFAULT_PORT)))
    print(f"SQX Edge running at http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
