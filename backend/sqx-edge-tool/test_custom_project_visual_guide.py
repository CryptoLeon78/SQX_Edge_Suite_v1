from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = TOOL_ROOT / "tools" / "render_custom_project_visual_guide.py"
REPO_ROOT = TOOL_ROOT.parents[1]


def _load_tool():
    spec = importlib.util.spec_from_file_location("render_custom_project_visual_guide", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_visual_guide_manifest_lists_required_sqx_capture_zones():
    tool = _load_tool()
    manifest = tool.load_json(REPO_ROOT / "resources" / "pdf" / "custom_project_visual_guide" / "manifest.json")
    ids = {item["id"] for item in manifest["screenshots"]}

    assert "task-flow" in ids
    assert "retest1-dukascopy" in ids
    assert "data-manager-main-symbol" in ids
    assert "resource-resolver" in ids
    assert all(item.get("required") is True for item in manifest["screenshots"])


def test_visual_guide_strict_failures_report_missing_screenshots(tmp_path):
    tool = _load_tool()
    manifest = {
        "screenshots": [
            {
                "id": "missing",
                "file": "missing.png",
                "title": "Missing",
                "required": True,
            }
        ]
    }

    statuses = tool.validate_screenshots(manifest, tmp_path)
    failures = tool.strict_failures(statuses)

    assert len(statuses) == 1
    assert statuses[0].problem == "captura pendiente"
    assert "missing" in failures[0]
