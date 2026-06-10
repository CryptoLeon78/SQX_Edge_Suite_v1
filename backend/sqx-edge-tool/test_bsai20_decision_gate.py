from __future__ import annotations

import json
from pathlib import Path

from core.bsai20_decision_gate import (
    BS_AI20_DECISION_GATE_VERSION,
    BS_AI20_STATUS,
    decide_payload,
)


EXPERIMENT_ID = "BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_bsai19(root: Path, *, tick: int = 0, forward: int = 0, retest1: int = 14) -> None:
    _write_json(
        root / ".local" / "blocksettings_ai" / "post_run_review" / "bsai19_post_run_readonly_review_review_20260610_194339.json",
        {
            "version": "bs-ai19-post-run-readonly-review-v1",
            "status": "post_run_readonly_review_completed_no_capa2",
            "hostProfile": "sqx144_full",
            "experimentId": EXPERIMENT_ID,
            "databankCounts": {
                "Results": 1321,
                "RETEST 0": 112,
                "retest 1": retest1,
                "TICK": tick,
                "Forward": forward,
            },
            "survivorAudit": {
                "summary": {
                    "survivorCount": retest1,
                    "tradeCountMin": 265,
                    "tradeCountMedian": 295,
                    "tradeCountMax": 360,
                    "netProfitIsMin": 3440.5601,
                    "netProfitIsMax": 6314.8599,
                }
            },
            "decision": {
                "decision": "post_run_review_no_capa2_tick_forward_empty",
                "cleanTickForwardChainReady": tick > 0 and forward > 0,
                "methodologyBlockers": [
                    "tick_databank_empty_no_real_tick_survivors",
                    "forward_databank_empty_no_forward_survivors",
                ],
                "warnings": ["retest1_survivors_exist_but_none_reached_tick_output"],
                "tradeRuleObserved": {
                    "preRegisteredShape": "realTickTrades >= max(absoluteFloor, floor(priorValidationTrades * retentionRatio))",
                    "absoluteMainFilter": {"column": "NumberOfTrades", "value": "120"},
                    "retentionFilter": {"column": "NumberOfTrades", "rightPctRatio": "65"},
                },
            },
        },
    )


def test_bsai20_version_marker():
    assert BS_AI20_DECISION_GATE_VERSION == "bs-ai20-decision-gate-v1"
    assert BS_AI20_STATUS == "decision_archive_branch_open_asset_broker_instrument_review_no_capa2"


def test_decide_archives_branch_and_selects_asset_review(tmp_path):
    _write_bsai19(tmp_path)
    payload = decide_payload(tmp_path, write_evidence=True)
    blob = json.dumps(payload, ensure_ascii=False)

    assert payload["version"] == BS_AI20_DECISION_GATE_VERSION
    assert payload["status"] == BS_AI20_STATUS
    assert payload["decision"]["decision"] == "archive_branch_and_open_asset_broker_instrument_review_no_capa2"
    assert payload["decision"]["archiveCurrentBranch"] is True
    assert payload["decision"]["archiveMeaning"] == "methodology_archive_only_no_host_project_move"
    assert payload["decision"]["openAssetBrokerInstrumentReview"] is True
    assert payload["decision"]["selectedNextGate"] == "BS-AI21 asset/broker/instrument configuration review"
    assert payload["decision"]["designNewCapa1Now"] is False
    assert payload["decision"]["newCapa1DesignDeferred"] is True
    assert payload["decision"]["capa2StartAllowed"] is False
    assert payload["guards"]["hostProjectArchiveMutationAllowed"] is False
    assert payload["guards"]["directDataDbPatch"] is False
    assert payload["guards"]["directUserProjectsPatch"] is False
    assert payload["guards"]["directDatabankMutation"] is False
    assert payload["evidenceRef"].startswith("bsai20_decision_gate_decide_")
    assert str(tmp_path) not in blob
    assert "<Task" not in blob
    assert "<Project" not in blob


def test_option_matrix_keeps_new_capa1_deferred_and_capa2_blocked(tmp_path):
    _write_bsai19(tmp_path)
    payload = decide_payload(tmp_path)
    options = {item["option"]: item for item in payload["options"]}

    assert options["archive_current_branch"]["selected"] is True
    assert options["archive_current_branch"]["hostMutationAllowed"] is False
    assert options["design_new_preregistered_capa1"]["selected"] is False
    assert options["design_new_preregistered_capa1"]["decision"] == "deferred_until_asset_broker_instrument_review_or_explicit_waiver"
    assert options["open_asset_broker_instrument_review"]["selected"] is True
    assert payload["methodology"]["currentBranchCanBeRescued"] is False
    assert payload["methodology"]["retest1SurvivorsCanSeedCapa2"] is False


def test_missing_bsai19_review_blocks_decision_without_actions(tmp_path):
    payload = decide_payload(tmp_path)

    assert payload["ok"] is False
    assert payload["status"] == "decision_blocked_missing_bsai19_review_no_capa2"
    assert payload["decision"]["decision"] == "bsai20_blocked_missing_or_unreadable_bsai19_review"
    assert payload["decision"]["capa2StartAllowed"] is False
    assert payload["guards"]["projectStartRequested"] is False
    assert payload["guards"]["projectImportRequested"] is False
