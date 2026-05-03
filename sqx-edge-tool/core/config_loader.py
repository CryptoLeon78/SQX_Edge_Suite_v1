"""
Shared JSON manifest loader for SQX Edge Tool.

The dashboard and backend now read the same canonical config files under
sqx-edge-tool/config/ instead of duplicating plan, periods, instruments, and UI
defaults in code.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def config_path(name: str) -> Path:
    return CONFIG_DIR / name


@lru_cache(maxsize=None)
def load_manifest(name: str) -> dict[str, Any]:
    path = config_path(name)
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clear_manifest_cache() -> None:
    load_manifest.cache_clear()
