from __future__ import annotations

from core.bsai14_capa1_monitor_gate import (
    BS_AI14_CAPA1_MONITOR_GATE_VERSION,
    _recommendation,
)


def test_bsai14_version_marker():
    assert BS_AI14_CAPA1_MONITOR_GATE_VERSION == "bs-ai14-capa1-monitor-decision-v1"


def test_recommendation_blocks_capa2_if_capa2_has_strategies():
    remote = {
        "reachable": True,
        "matchCount": 2,
        "matches": [
            {"projectName": "capa1", "found": True, "strategies": 380, "hasUnresolvedResources": False},
            {"projectName": "capa2", "found": True, "strategies": 1, "hasUnresolvedResources": False},
        ],
    }
    snapshot = {"latestLog": {"ageSeconds": 1}, "projectSnapshots": [{}, {"databanksDir": {"fileCount": 0}}]}
    databanks = {"items": []}

    decision = _recommendation(remote, snapshot, databanks, ["capa1", "capa2"])

    assert decision["decision"] == "blocked_review_required_no_capa2"
    assert "capa2_not_intact_strategies_present" in decision["blockers"]
    assert decision["capa2StartAllowed"] is False


def test_recommendation_flags_stale_thin_retest0_as_stop_or_review_candidate():
    remote = {
        "reachable": True,
        "matchCount": 2,
        "matches": [
            {"projectName": "capa1", "found": True, "strategies": 380, "hasUnresolvedResources": False},
            {"projectName": "capa2", "found": True, "strategies": 0, "hasUnresolvedResources": False},
        ],
    }
    snapshot = {"latestLog": {"ageSeconds": 3600}, "projectSnapshots": [{}, {"databanksDir": {"fileCount": 0}}]}
    databanks = {"items": [{"databank": "RETEST 0", "sqxFiles": 3}]}

    decision = _recommendation(remote, snapshot, databanks, ["capa1", "capa2"])

    assert decision["decision"] == "stop_or_review_candidate_no_capa2"
    assert "latest_log_stale_over_10m" in decision["warnings"]
    assert "thin_retest0_survivor_count" in decision["warnings"]
    assert decision["stopAllowedByThisGate"] is False
