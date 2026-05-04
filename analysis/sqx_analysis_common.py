"""Shared helpers for SQX analytical scripts.

The dashboard source of truth in this repo is ``app/js/manifest-data.js`` plus
``backend/sqx-edge-tool/config/*.json``. These helpers keep standalone analysis scripts
decoupled from the dashboard's rendering modules.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ANALYSIS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ANALYSIS_ROOT.parent


def load_manifest(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Load ``window.SQX_MANIFEST = {...};`` from app/js/manifest-data.js."""
    path = root / "app" / "js" / "manifest-data.js"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"window\.SQX_MANIFEST\s*=\s*(\{.*\})\s*;\s*$", text, re.DOTALL)
    if not match:
        return {}
    return json.loads(match.group(1))


def load_assets(root: Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    return list(((load_manifest(root).get("assets") or {}).get("assets") or []))


def load_plan(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    path = root / "backend" / "sqx-edge-tool" / "config" / "plan.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return load_manifest(root).get("plan") or {}


def load_ui(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    return load_manifest(root).get("ui") or {}


def editorial_asset_map(root: Path = PROJECT_ROOT) -> dict[str, dict[str, Any]]:
    """Return asset metadata indexed by asset id for scoring scripts."""
    out: dict[str, dict[str, Any]] = {}
    for asset in load_assets(root):
        asset_id = asset.get("id")
        if not asset_id:
            continue
        cats = asset.get("cats") or {}
        ratings = {
            key: value.get("rating")
            for key, value in cats.items()
            if isinstance(value, dict) and value.get("rating") is not None
        }
        out[asset_id] = {
            "type": asset.get("type", ""),
            "subtype": asset.get("sub") or asset.get("subtype") or "",
            "ratings": ratings,
            "cats": cats,
        }
    return out


def all_asset_ids(root: Path = PROJECT_ROOT) -> list[str]:
    return sorted(editorial_asset_map(root).keys())

