"""
app_paths.py — canonical path helpers for SQX Edge Tool.

In dev (normal Python run), paths are derived from __file__ exactly as before.
In a Nuitka --standalone frozen build, the entrypoint sets SQX_APP_ROOT to the
executable's directory before importing any application module, so both helpers
re-base to that directory instead of the source tree.

    app_root()     → sqx-edge-tool/   (config/, fulfillment_requests/, …)
    project_root() → project root      (app/, templates/, …)

Behaviour when SQX_APP_ROOT is absent is bit-for-bit identical to the old
Path(__file__).resolve().parents[N] expressions in each caller.
"""
from __future__ import annotations

import os
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
