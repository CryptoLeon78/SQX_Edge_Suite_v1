"""
browser_finder.py -- Locate a Chromium-based browser on Windows.

Used by app_main.py to open the dashboard in Edge/Chrome --app mode.
Extracted as a standalone module so it can be unit-tested without importing
the Flask app or triggering any route registration.
"""
from __future__ import annotations

import os
from pathlib import Path


def find_chromium(candidates: list[str] | None = None) -> str | None:
    """Return the path to an Edge or Chrome executable, or None if not found.

    Parameters
    ----------
    candidates:
        Override the default search list.  Pass an explicit list to make the
        function deterministic in tests (no filesystem side-effects needed).
    """
    if candidates is None:
        home = Path.home()
        candidates = [
            # Edge -- present on every Windows 10/11 machine
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            # Chrome -- common dev/user install
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            str(home / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"),
        ]
        # Prefer the registry App Path for Edge (handles non-standard installs)
        try:
            import winreg  # Windows only
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    key = winreg.OpenKey(
                        hive,
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
                    )
                    path, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)
                    if path:
                        candidates.insert(0, path)
                except OSError:
                    pass
        except ImportError:
            pass  # Linux / macOS (tests or build machines)

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None
