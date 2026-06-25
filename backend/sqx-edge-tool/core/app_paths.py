"""
app_paths.py — canonical path helpers for SQX Edge Tool.

In dev (normal Python run), paths are derived from __file__ exactly as before.
In a Nuitka --standalone frozen build, the entrypoint sets SQX_APP_ROOT to the
executable's directory before importing any application module, so both helpers
re-base to that directory instead of the source tree.

    app_root()      → sqx-edge-tool/   (config/, fulfillment_requests/, …)
    project_root()  → project root      (app/, templates/, …)
    user_data_dir() → writable user-data dir for config.json, license.json, output/, backups/
                      Resolution order:
                        1. SQX_USER_DATA_DIR env var   (tests/CI override)
                        2. Packaged build (SQX_APP_ROOT set)  → %APPDATA%\\SQX Edge\\ on Windows
                        3. Dev from source              → app_root() (unchanged, no migration)

Behaviour when SQX_APP_ROOT is absent is bit-for-bit identical to the old
Path(__file__).resolve().parents[N] expressions in each caller.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Anchor for the __file__-based fallback (this file lives in core/)
_HERE = Path(__file__).resolve()


def app_root() -> Path:
    """Return the tool root directory (sqx-edge-tool/ in dev, SQX_APP_ROOT when frozen)."""
    env = os.environ.get("SQX_APP_ROOT")
    if env:
        return Path(env)
    return _HERE.parents[1]   # core/ → sqx-edge-tool/


def project_root() -> Path:
    """Return the project root directory (SQX_Edge_Suite_v1/ in dev, SQX_APP_ROOT when frozen)."""
    env = os.environ.get("SQX_APP_ROOT")
    if env:
        return Path(env)
    return _HERE.parents[3]   # core/ → sqx-edge-tool/ → backend/ → project root


def _is_packaged() -> bool:
    """True when running as a frozen Nuitka/installed binary (SQX_APP_ROOT is set)."""
    return bool(os.environ.get("SQX_APP_ROOT"))


def user_data_dir() -> Path:
    """Return the user-writable data directory (config.json, license.json, output/, backups/).

    Resolution order (strict):
      1. SQX_USER_DATA_DIR — explicit override for tests and CI
      2. Packaged build    — %APPDATA%\\SQX Edge\\ (Windows) / platform equivalent
      3. Dev from source   — app_root() unchanged; START_SQX_EDGE.bat keeps working
    """
    override = os.environ.get("SQX_USER_DATA_DIR")
    if override:
        p = Path(override)
        p.mkdir(parents=True, exist_ok=True)
        return p

    if _is_packaged():
        if sys.platform == "win32":
            base = Path(os.environ["APPDATA"])
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
        p = base / "SQX Edge"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # Dev: same directory as before — no change in behaviour
    return app_root()
