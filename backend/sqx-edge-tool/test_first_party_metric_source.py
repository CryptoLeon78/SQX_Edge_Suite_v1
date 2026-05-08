from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "first_party_metric_source.py"


def load_module():
    spec = importlib.util.spec_from_file_location("first_party_metric_source", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_assigned_json_from_scores_style_script():
    source = load_module()
    data = source.extract_assigned_json('window.SQX_SCORES_DATA = {"EURUSD":{"metrics":{}}};')

    assert data == {"EURUSD": {"metrics": {}}}


def test_first_party_metric_source_writes_h1_bundle_and_gate(tmp_path):
    source = load_module()
    report = source.build_metric_bundle(out_dir=tmp_path)
    metrics = json.loads((tmp_path / "asset_metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / "metric_source_manifest.json").read_text(encoding="utf-8"))

    assert report["metadata"]["phase"] == "A52"
    assert report["gate"]["status"] == "GO"
    assert report["gate"]["metadata"]["timeframesRequested"] == ["H1"]
    assert manifest["policy"]["noSyntheticTimeframes"] is True
    assert manifest["timeframesGenerated"] == ["H1"]
    assert len(manifest["source"]["scoresDataSha256"]) == 64
    assert metrics["EURUSD"]["source_timeframe"] == "H1"
    assert metrics["EURUSD"]["source"] == "app/js/scores-data.js"
    assert "hurst_dist" in metrics["EURUSD"]
    assert "asset_metrics.json" in source.render_markdown(report)
