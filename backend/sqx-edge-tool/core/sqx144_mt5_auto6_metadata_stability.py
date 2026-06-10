from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import sqx144_mt5_auto3_broker_catalog as auto3
from . import sqx144_mt5_bridge as bridge


SQX144_MT5_AUTO6_VERSION = "sqx144-mt5-auto6-metadata-stability-policy-v1"
SQX144_MT5_AUTO6_PHASE = "SQX144-MT5-AUTO6"
SQX144_MT5_AUTO6_STATUS = "metadata_stability_observe_no_apply"
POLICY_ID = "mt5_metadata_stability_v1"
DEFAULT_BROKER = "darwinex"
DEFAULT_SPREAD_POLICY = "p90"
READ_MODE = "sqlite_uri_mode_ro_query_only"
ELIGIBLE_DECISION = "eligible_metadata_update"
OBSERVE_DECISION = "metadata_stability_observe_no_apply"

DEFAULT_POLICY = {
    "minSamples": 100000,
    "minYears": 2,
    "costReducingSpreadMinSamples": 250000,
    "costReducingSpreadMinYears": 3,
    "minObservationCount": 3,
    "minObservationWindowHours": 24,
    "cooldownDaysAfterApply": 7,
    "spreadHysteresisPips": 0.1,
    "spreadMaterialDeltaPips": 0.2,
    "pointValueObserveThresholdPct": 0.25,
    "pointValueBrokerReviewThresholdPct": 1.0,
}


class Auto6Error(RuntimeError):
    def __init__(self, code: str, *, details: dict[str, Any] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


def _project_root(value: str | Path | None = None) -> Path:
    return Path(value or Path.cwd()).resolve(strict=False)


def _config_path(project_root: Path) -> Path:
    return project_root / "backend" / "sqx-edge-tool" / "config.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _load_config(project_root: Path) -> dict[str, Any]:
    path = _config_path(project_root)
    if not path.is_file():
        raise Auto6Error("sqx_edge_config_missing")
    return _read_json(path)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _base_payload(action: str, host_profile: str = "sqx144_full") -> dict[str, Any]:
    return {
        "ok": False,
        "version": SQX144_MT5_AUTO6_VERSION,
        "phase": SQX144_MT5_AUTO6_PHASE,
        "statusMarker": SQX144_MT5_AUTO6_STATUS,
        "policyId": POLICY_ID,
        "action": action,
        "host": "sqx144_full",
        "hostProfile": host_profile,
        "readMode": READ_MODE,
        "readOnlyPolicyGate": True,
        "applyAllowed": False,
        "futureApplyGateAllowed": False,
        "writesSqxHost": False,
        "writesDataDb": False,
        "writesUserProjects": False,
        "mutatesDatabanks": False,
        "runsSqxTasks": False,
        "launchesMt5": False,
        "runsMt5Ea": False,
        "usesMigrationTool": False,
        "doesNotApplyToSqx": True,
        "doesNotApplyInstrumentConfig": True,
        "importExecutionAllowed": False,
        "directDbHistoryInsertAllowed": False,
        "privacy": {
            "localPathsReturned": False,
            "accountReturned": False,
            "secretsReturned": False,
            "licenseMaterialReturned": False,
            "sqlReturned": False,
            "rawBridgeResponseReturned": False,
            "applyApprovalReturned": False,
        },
    }


def _response_paths() -> list[Path]:
    directory = bridge.DEFAULT_MT5_FILES_DIR
    if not directory.is_dir():
        return []
    paths = list(directory.glob("SQXInfoBridge.response.*.json"))
    latest = directory / bridge.DEFAULT_RESPONSE_FILE
    if latest.is_file():
        paths.append(latest)
    return sorted({path.resolve(strict=False) for path in paths}, key=lambda item: item.name.lower())


def _response_summary() -> dict[str, Any]:
    latest = bridge.DEFAULT_MT5_FILES_DIR / bridge.DEFAULT_RESPONSE_FILE
    if not latest.is_file():
        return {"exists": False, "fileName": bridge.DEFAULT_RESPONSE_FILE}
    try:
        payload = _read_json(latest)
    except Exception:
        return {"exists": True, "jsonValid": False, "fileName": latest.name}
    return {
        "exists": True,
        "jsonValid": True,
        "fileName": latest.name,
        "sha256": _sha256_file(latest),
        "requestId": payload.get("requestId"),
        "symbol": payload.get("symbol"),
        "status": payload.get("status"),
    }


def _safe_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except Exception:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _symbol_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _parse_request_time(value: Any) -> datetime | None:
    match = re.search(r"(\d{8})_(\d{6})", str(value or ""))
    if not match:
        return None
    try:
        return datetime.strptime("".join(match.groups()), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _hours_between(values: list[datetime]) -> float:
    if len(values) < 2:
        return 0.0
    return round((max(values) - min(values)).total_seconds() / 3600.0, 3)


def _round_value(field: str, value: Any) -> float | str | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None if value is None else str(value)
    if field == "POINTVALUE":
        return round(parsed, 6)
    if field in {"TICKSIZE", "TICKSTEP"}:
        return round(parsed, 8)
    return round(parsed, 4)


def _candidate_signature(changes: dict[str, dict[str, Any]], proposed: dict[str, Any]) -> str:
    items = []
    for field in sorted(changes):
        items.append([field, _round_value(field, proposed.get(field))])
    raw = json.dumps(items, ensure_ascii=True, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _public_change_assessment(field: str, old_value: Any, new_value: Any) -> dict[str, Any]:
    old = _safe_float(old_value)
    new = _safe_float(new_value)
    result: dict[str, Any] = {
        "field": field,
        "old": old_value,
        "new": new_value,
        "material": False,
        "requiresRepeat": True,
        "requiresBrokerContractReview": False,
        "reasons": [],
    }
    if old is None or new is None:
        result["requiresBrokerContractReview"] = True
        result["reasons"].append("non_numeric_metadata_change")
        return result
    if field == "DEFAULTSPREAD":
        delta = round(new - old, 6)
        abs_delta = abs(delta)
        result["deltaPips"] = delta
        result["absoluteDeltaPips"] = abs_delta
        result["direction"] = "decrease" if delta < 0 else "increase"
        if abs_delta <= DEFAULT_POLICY["spreadHysteresisPips"] + 1e-9:
            result["reasons"].append("spread_delta_inside_hysteresis")
        elif abs_delta < DEFAULT_POLICY["spreadMaterialDeltaPips"]:
            result["reasons"].append("spread_delta_below_material_threshold")
        else:
            result["material"] = True
        return result
    if field == "POINTVALUE":
        delta = new - old
        rel_pct = abs(delta) / abs(old) * 100.0 if old else 100.0
        result["relativeDeltaPct"] = round(rel_pct, 6)
        result["direction"] = "decrease" if delta < 0 else "increase"
        if rel_pct >= DEFAULT_POLICY["pointValueBrokerReviewThresholdPct"]:
            result["requiresBrokerContractReview"] = True
            result["reasons"].append("pointvalue_delta_requires_broker_contract_review")
        elif rel_pct >= DEFAULT_POLICY["pointValueObserveThresholdPct"]:
            result["material"] = True
        else:
            result["reasons"].append("pointvalue_delta_below_threshold")
        return result
    result["material"] = True
    result["requiresBrokerContractReview"] = True
    result["reasons"].append("tick_contract_change_requires_review")
    return result


def _collect_observations(
    *,
    expected_symbol: str,
    spread_policy: str,
    changes: dict[str, dict[str, Any]],
    candidate_signature: str,
) -> dict[str, Any]:
    expected_key = _symbol_key(expected_symbol)
    observations: list[dict[str, Any]] = []
    matching_times: list[datetime] = []
    for path in _response_paths():
        try:
            response = _read_json(path)
            validation = bridge.validate_bridge_response(response, spread_policy=spread_policy)
        except Exception:
            continue
        if not validation.get("ok"):
            continue
        symbol = str(validation.get("symbol") or response.get("symbol") or "")
        if _symbol_key(symbol) != expected_key:
            continue
        proposed = validation.get("proposedSqxFields") if isinstance(validation.get("proposedSqxFields"), dict) else {}
        signature = _candidate_signature(changes, proposed)
        if signature != candidate_signature:
            continue
        request_id = str(validation.get("requestId") or response.get("requestId") or "")
        timestamp = _parse_request_time(request_id)
        if timestamp:
            matching_times.append(timestamp)
        observations.append({
            "fileName": path.name,
            "sha256": _sha256_file(path),
            "requestId": request_id,
            "symbol": symbol,
            "samples": proposed.get("spreadSamples"),
            "yearCount": validation.get("yearCount"),
        })
    return {
        "candidateSignature": candidate_signature,
        "matchingObservationCount": len(observations),
        "matchingObservationWindowHours": _hours_between(matching_times),
        "observations": observations[:12],
    }


def status_payload(project_root: str | Path) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    blockers: list[str] = []
    if host_profile != "sqx144_full":
        blockers.append("host_profile_not_sqx144_full")
    try:
        profiles = auto3.load_broker_profiles(root)
    except auto3.Auto3Error as exc:
        profiles = {}
        blockers.append(exc.code)
    response = _response_summary()
    payload = _base_payload("status", host_profile)
    payload.update({
        "ok": not blockers,
        "status": "status_ready" if not blockers else "status_blocked",
        "brokerProfiles": sorted(profiles),
        "policy": DEFAULT_POLICY,
        "response": response,
        "blockers": sorted(set(blockers)),
    })
    return payload


def evaluate_payload(
    project_root: str | Path,
    *,
    broker_key: str = DEFAULT_BROKER,
    symbol: str,
    spread_policy: str = DEFAULT_SPREAD_POLICY,
    expected_request_id: str | None = None,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("evaluate", host_profile)
    validation = auto3.bridge_validate_payload(
        root,
        broker_key=broker_key,
        symbol=symbol,
        spread_policy=spread_policy,
        expected_request_id=expected_request_id or None,
        db_path=db_path,
    )
    blockers = list(validation.get("blockers") or [])
    catalog_decision = str(validation.get("catalogDecision") or "")
    if catalog_decision and catalog_decision != "ready_existing":
        status = "blocked_catalog_not_ready"
        blockers.append(f"catalog_not_ready_existing_{catalog_decision}")
    elif not validation.get("ok"):
        status = "blocked_bridge_not_ready"
        blockers.append("bridge_validation_not_ready")
    else:
        status = ""
    proposed = validation.get("proposedSqxFields") if isinstance(validation.get("proposedSqxFields"), dict) else {}
    changes = validation.get("metadataDiff") if isinstance(validation.get("metadataDiff"), dict) else {}
    if blockers:
        payload.update({
            "ok": False,
            "status": status or "blocked",
            "decision": status or "blocked",
            "brokerKey": str(broker_key).lower(),
            "targetInstrument": (validation.get("symbolResolution") or {}).get("targetInstrument") if isinstance(validation.get("symbolResolution"), dict) else symbol,
            "catalogDecision": catalog_decision,
            "bridgeStatus": validation.get("status"),
            "blockers": sorted(set(blockers)),
            "warnings": sorted(set(validation.get("warnings") or [])),
        })
        return payload
    if not changes:
        payload.update({
            "ok": True,
            "status": "stable_no_change",
            "decision": "stable_no_change",
            "brokerKey": str(broker_key).lower(),
            "targetInstrument": (validation.get("symbolResolution") or {}).get("targetInstrument"),
            "requestId": validation.get("requestId"),
            "spreadPolicy": str(spread_policy).lower(),
            "coverage": {
                "samples": proposed.get("spreadSamples"),
                "yearCount": validation.get("yearCount"),
                "minSamples": DEFAULT_POLICY["minSamples"],
                "minYears": DEFAULT_POLICY["minYears"],
            },
            "changes": {},
            "warnings": sorted(set(validation.get("warnings") or [])),
            "blockers": [],
        })
        return payload

    samples = _safe_int(proposed.get("spreadSamples"))
    years = _safe_int(validation.get("yearCount"))
    warnings = sorted(set(validation.get("warnings") or []))
    policy_reasons: list[str] = []
    if samples < DEFAULT_POLICY["minSamples"]:
        policy_reasons.append("stability_insufficient_samples")
    if years < DEFAULT_POLICY["minYears"]:
        policy_reasons.append("stability_insufficient_years")
    if any(str(item) == "max_bars_limit_reached" for item in warnings):
        policy_reasons.append("stability_max_bars_limit_reached")
    assessments = {
        field: _public_change_assessment(field, change.get("old"), change.get("new"))
        for field, change in sorted(changes.items())
    }
    if any(item.get("requiresBrokerContractReview") for item in assessments.values()):
        payload.update({
            "ok": True,
            "status": "stability_broker_contract_review_required",
            "decision": "blocked_broker_contract_review",
            "brokerKey": str(broker_key).lower(),
            "targetInstrument": (validation.get("symbolResolution") or {}).get("targetInstrument"),
            "requestId": validation.get("requestId"),
            "spreadPolicy": str(spread_policy).lower(),
            "changes": changes,
            "fieldAssessment": assessments,
            "coverage": {"samples": samples, "yearCount": years},
            "policyReasons": sorted(set(policy_reasons + ["broker_contract_review_required"])),
            "blockers": [],
            "warnings": warnings,
        })
        return payload

    spread_assessment = assessments.get("DEFAULTSPREAD")
    cost_reducing_spread = bool(spread_assessment and spread_assessment.get("direction") == "decrease")
    if cost_reducing_spread:
        if samples < DEFAULT_POLICY["costReducingSpreadMinSamples"]:
            policy_reasons.append("cost_reducing_spread_needs_more_samples")
        if years < DEFAULT_POLICY["costReducingSpreadMinYears"]:
            policy_reasons.append("cost_reducing_spread_needs_more_years")
    material_fields = sorted(field for field, item in assessments.items() if item.get("material"))
    for item in assessments.values():
        policy_reasons.extend(str(reason) for reason in item.get("reasons") or [])
    signature = _candidate_signature(changes, proposed)
    resolved = validation.get("symbolResolution") if isinstance(validation.get("symbolResolution"), dict) else {}
    expected_symbol = str(resolved.get("mt5BridgeSymbol") or validation.get("symbol") or symbol)
    observations = _collect_observations(
        expected_symbol=expected_symbol,
        spread_policy=str(spread_policy).lower(),
        changes=changes,
        candidate_signature=signature,
    )
    repeat_ok = (
        observations["matchingObservationCount"] >= DEFAULT_POLICY["minObservationCount"]
        and observations["matchingObservationWindowHours"] >= DEFAULT_POLICY["minObservationWindowHours"]
    )
    if material_fields and not repeat_ok:
        policy_reasons.append("repeat_observation_window_not_satisfied")
    eligible = bool(material_fields and not policy_reasons and repeat_ok)
    status = "stable_drift_candidate_for_future_auto5" if eligible else "stability_policy_not_satisfied"
    decision = ELIGIBLE_DECISION if eligible else OBSERVE_DECISION
    payload.update({
        "ok": True,
        "status": status,
        "decision": decision,
        "brokerKey": str(broker_key).lower(),
        "targetInstrument": resolved.get("targetInstrument"),
        "sourceSymbol": validation.get("symbol"),
        "requestId": validation.get("requestId"),
        "spreadPolicy": str(spread_policy).lower(),
        "futureApplyGateAllowed": eligible,
        "futureApplyGate": {
            "requiresSeparateBackup": True,
            "requiresExactApproval": True,
            "requiresPolicyId": POLICY_ID,
            "requiresDecision": ELIGIBLE_DECISION,
            "stillPreserves": "no_source_broker_data_history no_projects_no_databanks_no_tasks no_migration_tool",
        },
        "coverage": {
            "samples": samples,
            "yearCount": years,
            "minSamples": DEFAULT_POLICY["minSamples"],
            "minYears": DEFAULT_POLICY["minYears"],
            "costReducingSpreadMinSamples": DEFAULT_POLICY["costReducingSpreadMinSamples"],
            "costReducingSpreadMinYears": DEFAULT_POLICY["costReducingSpreadMinYears"],
        },
        "changes": changes,
        "fieldAssessment": assessments,
        "materialFields": material_fields,
        "observationSet": observations,
        "policyReasons": sorted(set(policy_reasons)),
        "blockers": [],
        "warnings": warnings,
    })
    return payload


def decision_template_payload(project_root: str | Path) -> dict[str, Any]:
    root = _project_root(project_root)
    config = _load_config(root)
    host_profile = str(config.get("sqx_host_profile") or "")
    payload = _base_payload("decision-template", host_profile)
    payload.update({
        "ok": True,
        "status": "decision_template_ready_no_apply_phrase",
        "decisionTemplate": (
            "Future metadata apply may be considered only when "
            "stabilityPolicy=mt5_metadata_stability_v1, "
            "stabilityDecision=eligible_metadata_update, broker, instrument, "
            "spreadPolicy, observation count/window, response hashes, plan id, backup id "
            "and no_source_broker_data_history are all named in a separate gate."
        ),
        "policy": DEFAULT_POLICY,
    })
    return payload


def _handle_error(action: str, project_root: str | Path, error: Exception) -> dict[str, Any]:
    try:
        host_profile = str(_load_config(_project_root(project_root)).get("sqx_host_profile") or "")
    except Exception:
        host_profile = ""
    code = getattr(error, "code", str(error))
    payload = _base_payload(action, host_profile)
    payload.update({
        "status": "blocked",
        "error": code,
        "details": getattr(error, "details", {}),
        "blockers": [code],
    })
    return payload


def error_payload(action: str, error: Exception, *, project_root: str | Path = ".") -> dict[str, Any]:
    return _handle_error(action, project_root, error)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SQX144 MT5 AUTO6 metadata stability policy")
    parser.add_argument("action", choices=("status", "evaluate", "decision-template"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--broker", default=DEFAULT_BROKER)
    parser.add_argument("--symbol", default="")
    parser.add_argument("--spread-policy", default=DEFAULT_SPREAD_POLICY)
    parser.add_argument("--expected-request-id", default=None)
    args = parser.parse_args(argv)
    try:
        if args.action == "status":
            payload = status_payload(args.project_root)
        elif args.action == "evaluate":
            payload = evaluate_payload(
                args.project_root,
                broker_key=args.broker,
                symbol=args.symbol,
                spread_policy=args.spread_policy,
                expected_request_id=args.expected_request_id,
                db_path=args.db_path,
            )
        else:
            payload = decision_template_payload(args.project_root)
    except (Auto6Error, auto3.Auto3Error, bridge.BridgeError) as exc:
        payload = _handle_error(args.action, args.project_root, exc)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
