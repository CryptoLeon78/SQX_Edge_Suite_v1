import json
from pathlib import Path

from core.mtf_evidence import build_mtf_evidence


def test_missing_mtf_evidence_is_blocked_and_read_only(tmp_path: Path):
    payload = build_mtf_evidence(tmp_path / "missing_a56.json")

    assert payload["ok"] is True
    assert payload["available"] is False
    assert payload["status"] == "NO_GO"
    assert payload["state"] == "missing"
    assert payload["policy"] == "read_only_after_a56_go"
    assert payload["summary"]["timeframeCount"] == 0
    assert payload["outputs"] == []


def test_go_mtf_evidence_is_summarized_without_full_paths(tmp_path: Path):
    report = tmp_path / "a56_real_mtf_pipeline_run.json"
    report.write_text(
        json.dumps(
            {
                "status": "GO",
                "metadata": {"generatedAt": "2026-05-08T18:00:00Z"},
                "builder": {
                    "outputs": {
                        "H1": "C:/secret/run/asset_metrics_H1.json",
                        "M30": "C:/secret/run/asset_metrics_M30.json",
                    },
                    "files": [
                        {"asset": "EURUSD", "status": "processed"},
                        {"asset": "GBPUSD", "status": "processed"},
                        {"asset": "XAUUSD", "status": "skipped"},
                    ],
                },
                "artifacts": {
                    "planSummary": {"covered": 9, "strong": 4, "needsReview": 2},
                    "advisor": "C:/secret/run/plan_quality_advisor.json",
                },
            }
        ),
        encoding="utf-8",
    )

    payload = build_mtf_evidence(report)

    assert payload["available"] is True
    assert payload["status"] == "GO"
    assert payload["state"] == "ready"
    assert payload["summary"]["timeframeCount"] == 2
    assert payload["summary"]["assetCount"] == 2
    assert payload["summary"]["assets"] == ["EURUSD", "GBPUSD"]
    assert payload["summary"]["currentPlanMtfCovered"] == 9
    assert payload["summary"]["currentPlanMtfStrong"] == 4
    assert payload["summary"]["needsReview"] == 2
    assert payload["outputs"] == [
        {"timeframe": "H1", "file": "asset_metrics_H1.json"},
        {"timeframe": "M30", "file": "asset_metrics_M30.json"},
    ]
    assert payload["artifacts"] == [{"name": "advisor", "file": "plan_quality_advisor.json"}]
    assert "C:/secret" not in json.dumps(payload)
