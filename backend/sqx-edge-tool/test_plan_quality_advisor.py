from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "backend" / "sqx-edge-tool" / "tools" / "plan_quality_advisor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plan_quality_advisor", TOOL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plan_quality_advisor_builds_report():
    advisor = load_module()

    report = advisor.build_report()

    assert report["metadata"]["phase"] == "A47"
    assert report["metadata"]["candidateCount"] >= 14
    assert report["metadata"]["currentPlanCount"] == 14
    assert report["metadata"]["recommendedPlanCount"] == 14
    assert report["currentPlanSummary"]["supported"] >= 1
    assert "verdicts" in report["currentPlanSummary"]
    assert report["currentPlan"][0]["asset"] == "XAUUSD"
    assert report["currentPlan"][0]["category"] == "tendencia"
    assert report["recommendedPlan"][0]["recommended_rank"] == 1
    assert report["diff"]["add"]
    assert report["diff"]["review_not_selected"]


def test_plan_quality_advisor_markdown_is_operator_readable():
    advisor = load_module()
    report = advisor.build_report(limit=5, min_composite=70)

    markdown = advisor.render_markdown(report)

    assert "# SQX Plan Quality Advisor" in markdown
    assert "## Current Plan Review" in markdown
    assert "## Recommended Plan" in markdown
    assert "H1 baseline" in markdown
    assert "Review, not automatically drop" in markdown
    assert "| Rank | Asset | TF | BS | Dir | Composite | Subtype |" in markdown
