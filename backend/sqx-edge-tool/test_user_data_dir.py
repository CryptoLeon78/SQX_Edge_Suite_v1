"""
test_user_data_dir.py — Tests for user_data_dir() resolution and config.json round-trip.

Covers:
  - Override mode  : SQX_USER_DATA_DIR set                 -> uses that dir
  - Packaged-sim   : SQX_APP_ROOT set, APPDATA controlled  -> %APPDATA%\\SQX Edge\\ (win32)
  - Dev mode       : neither env var set                    -> app_root() unchanged
  - Round-trip     : config.json write + read under resolved dir
  - Regression     : dev mode resolves to the repo-relative path (not APPDATA)
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_app_paths(monkeypatch, env: dict):
    """
    Reload core.app_paths with a clean environment and return the fresh module.
    We patch os.environ at the module level and reimport so that module-level
    constants (_HERE) are stable while the functions re-read os.environ at call time.
    """
    import os
    for key in ("SQX_USER_DATA_DIR", "SQX_APP_ROOT", "APPDATA", "XDG_DATA_HOME"):
        monkeypatch.delenv(key, raising=False)
    for key, val in env.items():
        monkeypatch.setenv(key, val)
    import core.app_paths as ap
    importlib.reload(ap)
    return ap


# ---------------------------------------------------------------------------
# Resolution tests
# ---------------------------------------------------------------------------

class TestUserDataDirResolution:

    def test_override_mode(self, monkeypatch, tmp_path):
        """SQX_USER_DATA_DIR set -> use exactly that path."""
        override = tmp_path / "override_data"
        ap = _reload_app_paths(monkeypatch, {"SQX_USER_DATA_DIR": str(override)})
        result = ap.user_data_dir()
        assert result == override
        assert result.is_dir(), "user_data_dir() must mkdir the override path"

    def test_override_takes_priority_over_packaged(self, monkeypatch, tmp_path):
        """SQX_USER_DATA_DIR wins even when SQX_APP_ROOT is also set."""
        override = tmp_path / "override_wins"
        fake_appdata = tmp_path / "appdata"
        ap = _reload_app_paths(monkeypatch, {
            "SQX_USER_DATA_DIR": str(override),
            "SQX_APP_ROOT": str(tmp_path / "fake_app_root"),
            "APPDATA": str(fake_appdata),
        })
        result = ap.user_data_dir()
        assert result == override

    def test_packaged_windows(self, monkeypatch, tmp_path):
        """Packaged on win32 -> %APPDATA%\\SQX Edge\\."""
        fake_appdata = tmp_path / "AppData" / "Roaming"
        fake_appdata.mkdir(parents=True)
        ap = _reload_app_paths(monkeypatch, {
            "SQX_APP_ROOT": str(tmp_path / "fake_app"),
            "APPDATA": str(fake_appdata),
        })
        monkeypatch.setattr(ap.sys, "platform", "win32")
        result = ap.user_data_dir()
        assert result == fake_appdata / "SQX Edge"
        assert result.is_dir()

    def test_packaged_linux(self, monkeypatch, tmp_path):
        """Packaged on linux -> $XDG_DATA_HOME/SQX Edge."""
        fake_xdg = tmp_path / "xdg_data"
        fake_xdg.mkdir()
        ap = _reload_app_paths(monkeypatch, {
            "SQX_APP_ROOT": str(tmp_path / "fake_app"),
            "XDG_DATA_HOME": str(fake_xdg),
        })
        monkeypatch.setattr(ap.sys, "platform", "linux")
        result = ap.user_data_dir()
        assert result == fake_xdg / "SQX Edge"
        assert result.is_dir()

    def test_packaged_darwin(self, monkeypatch, tmp_path):
        """Packaged on darwin -> ~/Library/Application Support/SQX Edge."""
        fake_home = tmp_path / "home"
        (fake_home / "Library" / "Application Support").mkdir(parents=True)
        ap = _reload_app_paths(monkeypatch, {
            "SQX_APP_ROOT": str(tmp_path / "fake_app"),
        })
        monkeypatch.setattr(ap.sys, "platform", "darwin")
        monkeypatch.setattr(ap.Path, "home", staticmethod(lambda: fake_home))
        result = ap.user_data_dir()
        assert result == fake_home / "Library" / "Application Support" / "SQX Edge"
        assert result.is_dir()

    def test_dev_mode_equals_app_root(self, monkeypatch):
        """Dev mode (no overrides) -> user_data_dir() == app_root()."""
        ap = _reload_app_paths(monkeypatch, {})
        assert ap.user_data_dir() == ap.app_root()

    def test_dev_mode_regression_not_appdata(self, monkeypatch, tmp_path):
        """Regression: in dev mode the result must NOT be inside a fake APPDATA tree."""
        fake_appdata = tmp_path / "AppData" / "Roaming"
        fake_appdata.mkdir(parents=True)
        # Set APPDATA but NOT SQX_APP_ROOT — simulates dev with APPDATA in env
        ap = _reload_app_paths(monkeypatch, {"APPDATA": str(fake_appdata)})
        result = ap.user_data_dir()
        # Must resolve to the repo's sqx-edge-tool directory, not APPDATA
        assert fake_appdata not in [result, *result.parents]
        # Must be the same as app_root()
        assert result == ap.app_root()


# ---------------------------------------------------------------------------
# Round-trip tests
# ---------------------------------------------------------------------------

class TestConfigRoundTrip:

    def test_config_json_round_trip_override(self, monkeypatch, tmp_path):
        """Write config.json under override dir, read it back via user_data_dir()."""
        override = tmp_path / "user_data"
        ap = _reload_app_paths(monkeypatch, {"SQX_USER_DATA_DIR": str(override)})

        data = {"sqx_path": "C:/SQX", "output_dir": "output", "test": True}
        cfg_path = ap.user_data_dir() / "config.json"
        cfg_path.write_text(json.dumps(data), encoding="utf-8")

        read_back = json.loads((ap.user_data_dir() / "config.json").read_text(encoding="utf-8"))
        assert read_back == data

    def test_config_json_round_trip_packaged(self, monkeypatch, tmp_path):
        """Write config.json in packaged mode, read back from %APPDATA%\\SQX Edge\\."""
        fake_appdata = tmp_path / "AppData" / "Roaming"
        fake_appdata.mkdir(parents=True)
        ap = _reload_app_paths(monkeypatch, {
            "SQX_APP_ROOT": str(tmp_path / "app"),
            "APPDATA": str(fake_appdata),
        })
        monkeypatch.setattr(ap.sys, "platform", "win32")

        data = {"sqx_path": "D:/SQX", "packaged": True}
        udd = ap.user_data_dir()
        cfg_path = udd / "config.json"
        cfg_path.write_text(json.dumps(data), encoding="utf-8")

        read_back = json.loads((ap.user_data_dir() / "config.json").read_text(encoding="utf-8"))
        assert read_back == data
        assert udd == fake_appdata / "SQX Edge"

    def test_config_json_round_trip_dev(self, monkeypatch, tmp_path):
        """Round-trip config.json in dev mode under a temp app_root."""
        # Simulate dev: no SQX_APP_ROOT, no SQX_USER_DATA_DIR
        # We monkeypatch _HERE so app_root() points to tmp_path
        ap = _reload_app_paths(monkeypatch, {})
        # Override _HERE so app_root() returns tmp_path/core/../ = tmp_path
        fake_core = tmp_path / "core" / "app_paths.py"
        monkeypatch.setattr(ap, "_HERE", fake_core)

        udd = ap.user_data_dir()
        assert udd == ap.app_root()

        cfg_path = udd / "config.json"
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"dev": True, "output_dir": "output"}
        cfg_path.write_text(json.dumps(data), encoding="utf-8")

        read_back = json.loads((ap.user_data_dir() / "config.json").read_text(encoding="utf-8"))
        assert read_back == data
