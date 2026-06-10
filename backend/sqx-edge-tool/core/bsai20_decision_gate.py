from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .bsai17_controlled_import_start_gate import DEFAULT_EXPERIMENT_ID
from .bsai_first_start_gate import _privacy_guard


BS_AI20_DECISION_GATE_VERSION = "bs-ai20-decision-gate-v1"
BS_AI20_STATUS = "decision_archive_branch_open_asset_broker_instrument_review_no_capa2"
EVIDENCE_DIR_PARTS = (".local", "blocksettings_ai", "decision_gate")
BS_AI19_EVIDENCE_PATTERN = "bsai19_post_run_readonly_review_review_*.json"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _latest_bsai19_review(project_root: Path) -> dict[str, Any]:
    evidence_dir = project_root / ".local" / "blocksettings_ai" / "post_run_review"
    files = sorted(
        (item for item in evidence_dir.glob(BS_AI19_EVIDENCE_PATTERN) if item.is_file()),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return {"found": False, "evidenceRef": None}

    latest = files[0]
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "found": True,
            "evidenceRef": latest.name,
            "readStatus": "failed",
            "errorCode": type(exc).__name__,
        }

    decision = payload.get("decision") if isinstance(payload.get("decision"), dict) else {}
    survivor_summary = {}
    survivor_audit = payload.get("survivorAudit")
    if isinstance(survivor_audit, dict) and isinstance(survivor_audit.get("summary"), dict):
        survivor_summary = survivor_audit["summary"]

    return {
        "found": True,
        "evidenceRef": latest.name,
        "readStatus": "ok",
        "version": payload.get("version"),
        "status": payload.get("status"),
        "hostProfile": payload.get("hostProfile"),
        "experimentId": payload.get("experimentId"),
        "decision": decision.get("decision"),
        "cleanTickForwardChainReady": decision.get("cleanTickForwardChainReady"),
        "databankCounts": payload.get("databankCounts") if isinstance(payload.get("databankCounts"), dict) else {},
        "survivorSummary": survivor_summary,
        "tradeRuleObserved": decision.get("tradeRuleObserved") if isinstance(decision.get("tradeRuleObserved"), dict) else {},
        "methodologyBlockers": decision.get("methodologyBlockers") if isinstance(decision.get("methodologyBlockers"), list) else [],
        "warnings": decision.get("warnings") if isinstance(decision.get("warnings"), list) else [],
    }


def _selected_decision(review: dict[str, Any]) -> dict[str, Any]:
    if not review.get("found") or review.get("readStatus") not in (None, "ok"):
        return {
            "decision": "bsai20_blocked_missing_or_unreadable_bsai19_review",
            "selectedNextGate": "repeat BS-AI19 review",
            "blockers": ["missing_or_unreadable_bsai19_review"],
            "warnings": [],
            "archiveCurrentBranch": False,
            "openAssetBrokerInstrumentReview": False,
            "designNewCapa1Now": False,
            "newCapa1DesignDeferred": True,
            "capa2StartAllowed": False,
            "projectStartAllowed": False,
            "projectImportAllowed": False,
        }

    counts = review.get("databankCounts") if isinstance(review.get("databankCounts"), dict) else {}
    tick = int(counts.get("TICK") or 0)
    forward = int(counts.get("Forward") or 0)
    retest1 = int(counts.get("retest 1") or 0)
    clean_chain = bool(review.get("cleanTickForwardChainReady")) and tick > 0 and forward > 0
    blockers: list[str] = []
    warnings: list[str] = []

    if not clean_chain:
        blockers.extend(["no_clean_tick_forward_chain", "current_branch_failed_for_capa2"])
    if retest1 > 0 and tick == 0:
        warnings.append("retest1_survivors_can_inform_hypotheses_only")
    warnings.extend(str(item) for item in review.get("warnings") or [])

    return {
        "decision": "archive_branch_and_open_asset_broker_instrument_review_no_capa2",
        "status": "selected",
        "selectedNextGate": "BS-AI21 asset/broker/instrument configuration review",
        "blockers": blockers,
        "warnings": sorted(set(warnings)),
        "archiveCurrentBranch": True,
        "archiveMeaning": "methodology_archive_only_no_host_project_move",
        "currentBranchState": "failed_candidate_for_capa2",
        "openAssetBrokerInstrumentReview": True,
        "designNewCapa1Now": False,
        "newCapa1DesignDeferred": True,
        "newCapa1Prereq": "complete BS-AI21 or explicitly waive it in a later operator-approved methodology gate",
        "capa2StartAllowed": False,
        "projectStartAllowed": False,
        "projectStopAllowed": False,
        "projectImportAllowed": False,
        "filterRelaxationAllowedForCurrentLot": False,
        "forcedPassAllowed": False,
        "currentLotMayBeReinterpreted": False,
        "reason": (
            "BS-AI19 has retest1 survivors but no real TICK/Forward survivors; the branch cannot seed Capa2. "
            "Because AUDCAD has recorded cost/config warnings and later metadata observations, the next run should first "
            "verify asset, broker, instrument, spread, point value, tick size/step and data-source alignment."
        ),
    }


def _option_matrix(review: dict[str, Any], decision: dict[str, Any]) -> list[dict[str, Any]]:
    counts = review.get("databankCounts") if isinstance(review.get("databankCounts"), dict) else {}
    return [
        {
            "option": "archive_current_branch",
            "selected": True,
            "action": "mark BS-AI16 branch failed for Capa2 in methodology/docs only",
            "why": "TICK=0 and Forward=0 mean there is no clean real TICK/Forward chain.",
            "hostMutationAllowed": False,
            "capa2StartAllowed": False,
            "evidence": {
                "retest1": int(counts.get("retest 1") or 0),
                "tick": int(counts.get("TICK") or 0),
                "forward": int(counts.get("Forward") or 0),
            },
        },
        {
            "option": "design_new_preregistered_capa1",
            "selected": False,
            "decision": "deferred_until_asset_broker_instrument_review_or_explicit_waiver",
            "why": "A new experiment is valid only if thresholds, costs, asset config and data-source assumptions are fixed before seeing new results.",
            "requiredBeforeRun": [
                "pre-register hypothesis, asset/timeframe/direction/family",
                "pre-register TICK REAL filters and cost assumptions",
                "do not reuse retest1 survivors as Capa2 seed",
                "complete or explicitly waive BS-AI21",
            ],
            "capa2StartAllowed": False,
        },
        {
            "option": "open_asset_broker_instrument_review",
            "selected": bool(decision.get("openAssetBrokerInstrumentReview")),
            "decision": "selected_next_gate",
            "why": "The branch failed at real TICK/Forward and the project has recorded spread/cross-broker/AUDCAD metadata uncertainty.",
            "scope": [
                "AUDCAD_darwinex and AUDCAD_dukascopy",
                "spread/default spread policy",
                "point value, tick size, tick step, order size fields, commission and swap",
                "broker/source/data IDs and history coverage",
                "embedded project resources versus current host catalog",
                "timing of metadata observations versus BS-AI16 prepare/import/start",
            ],
            "applyAllowedInBsAi20": False,
        },
    ]


def _base_payload(action: str, project_root: Path, experiment_id: str) -> dict[str, Any]:
    review = _latest_bsai19_review(project_root)
    decision = _selected_decision(review)
    payload: dict[str, Any] = {
        "ok": decision["decision"] != "bsai20_blocked_missing_or_unreadable_bsai19_review",
        "version": BS_AI20_DECISION_GATE_VERSION,
        "action": action,
        "status": BS_AI20_STATUS if decision["decision"] != "bsai20_blocked_missing_or_unreadable_bsai19_review" else "decision_blocked_missing_bsai19_review_no_capa2",
        "hostProfile": "sqx144_full",
        "experimentId": experiment_id,
        "targetProject": experiment_id,
        "latestBsai19Review": review,
        "decision": decision,
        "options": _option_matrix(review, decision),
        "methodology": {
            "antiOverfitRule": "do not use post-run evidence to relax filters or reinterpret a failed branch",
            "selectionBiasControl": "new thresholds or new hypotheses must be pre-registered before the next run",
            "retest1SurvivorsCanInformNextHypothesis": True,
            "retest1SurvivorsCanSeedCapa2": False,
            "currentBranchCanBeRescued": False,
            "academicSources": [
                {
                    "label": "Bailey, Borwein, Lopez de Prado and Zhu - Probability of Backtest Overfitting",
                    "sourceRef": "ssrn_pbo_abstract_2326253",
                    "externalUrlStored": False,
                },
                {
                    "label": "Bailey and Lopez de Prado - Deflated Sharpe Ratio",
                    "sourceRef": "ssrn_dsr_abstract_2460551",
                    "externalUrlStored": False,
                },
            ],
        },
        "guards": {
            "readOnly": True,
            "methodologyDecisionOnly": True,
            "hostProjectArchiveMutationAllowed": False,
            "projectStartRequested": False,
            "projectStopRequested": False,
            "projectImportRequested": False,
            "capa2StartAllowed": False,
            "taskmanagerOpenProjectAllowed": False,
            "loadAsIsAllowed": False,
            "addMissingSymbolsAllowed": False,
            "directDataDbPatch": False,
            "directUserProjectsPatch": False,
            "directDatabankMutation": False,
            "migrationToolAllowed": False,
            "officialBlocksettingsPromotion": False,
            "sqx144UpdatePromotion": False,
        },
        "privacy": {
            "localPathsReturned": False,
            "rawXmlReturned": False,
            "rawLogReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
        },
    }
    _privacy_guard(payload)
    return payload


def write_evidence_file(project_root: Path, action: str, payload: dict[str, Any]) -> str:
    _privacy_guard(payload)
    evidence_dir = project_root.joinpath(*EVIDENCE_DIR_PARTS)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"bsai20_decision_gate_{action}_{_utc_stamp()}.json"
    (evidence_dir / filename).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return filename


def status_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
) -> dict[str, Any]:
    return _base_payload("status", _project_root(project_root), experiment_id)


def decide_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
    write_evidence: bool = False,
) -> dict[str, Any]:
    root = _project_root(project_root)
    payload = _base_payload("decide", root, experiment_id)
    if write_evidence:
        payload["evidenceWritten"] = True
        payload["evidenceRef"] = write_evidence_file(root, "decide", payload)
    else:
        payload["evidenceWritten"] = False
    _privacy_guard(payload)
    return payload


def decision_template_payload(
    project_root: str | Path,
    *,
    experiment_id: str = DEFAULT_EXPERIMENT_ID,
) -> dict[str, Any]:
    payload = _base_payload("decision-template", _project_root(project_root), experiment_id)
    payload["selectedDecision"] = "ARCHIVAR RAMA Y ABRIR BS-AI21 REVISION ACTIVO/BROKER/INSTRUMENTO"
    payload["blockedDecisions"] = [
        "ARRANCAR CAPA2 DESDE ESTE LOTE",
        "DISENAR NUEVO CAPA1 SIN REVISAR O EXPLICITAMENTE DISPENSAR CONFIGURACION",
        "RELAJAR FILTROS O FORZAR PASS STATES",
    ]
    _privacy_guard(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "decide", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--experiment-id", default=DEFAULT_EXPERIMENT_ID)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "decide":
        payload = decide_payload(args.project_root, experiment_id=args.experiment_id, write_evidence=args.write_evidence)
    elif args.action == "decision-template":
        payload = decision_template_payload(args.project_root, experiment_id=args.experiment_id)
    else:
        payload = status_payload(args.project_root, experiment_id=args.experiment_id)

    _privacy_guard(payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
