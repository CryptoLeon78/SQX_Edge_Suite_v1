from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPORT_PATH = PROJECT_ROOT / "analysis_output" / "real_mtf_pipeline_run" / "a56_real_mtf_pipeline_run.json"
MAX_ITEMS = 12


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _filename(value: Any) -> str:
    text = str(value or "").strip()
    return Path(text).name if text else ""


def _artifact_list(artifacts: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for key, value in sorted(artifacts.items()):
        if key == "planSummary":
            continue
        filename = _filename(value)
        if filename:
            items.append({"name": str(key), "file": filename})
    return items[:MAX_ITEMS]


def _output_list(builder: dict[str, Any]) -> list[dict[str, str]]:
    outputs = _safe_dict(builder.get("outputs"))
    items: list[dict[str, str]] = []
    for timeframe, path in sorted(outputs.items()):
        filename = _filename(path)
        if filename:
            items.append({"timeframe": str(timeframe), "file": filename})
    return items


def _processed_assets(builder: dict[str, Any]) -> list[str]:
    files = _safe_list(builder.get("files"))
    assets = {
        str(item.get("asset") or "").strip()
        for item in files
        if isinstance(item, dict) and item.get("status") == "processed" and item.get("asset")
    }
    return sorted(asset for asset in assets if asset)


def _failure_messages(*payloads: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for payload in payloads:
        for item in _safe_list(payload.get("failures")):
            if isinstance(item, str) and item.strip():
                failures.append(item.strip())
            elif isinstance(item, dict):
                message = item.get("message") or item.get("error") or item.get("reason")
                if message:
                    failures.append(str(message).strip())
    return failures[:MAX_ITEMS]


def _blocked_payload(state: str, message: str, report_path: Path, failures: list[str] | None = None) -> dict[str, Any]:
    return {
        "ok": True,
        "available": False,
        "status": "NO_GO",
        "state": state,
        "message": message,
        "generatedAt": _utc_now(),
        "policy": "read_only_after_a56_go",
        "report": {"file": report_path.name, "exists": report_path.is_file()},
        "summary": {
            "timeframeCount": 0,
            "assetCount": 0,
            "assets": [],
            "currentPlanMtfCovered": 0,
            "currentPlanMtfStrong": 0,
            "needsReview": 0,
        },
        "outputs": [],
        "artifacts": [],
        "failures": failures or [],
    }


def build_mtf_evidence(report_path: Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    if not report_path.is_file():
        return _blocked_payload(
            "missing",
            "No hay evidencia A56 GO disponible todavia.",
            report_path,
            ["Ejecuta real_mtf_pipeline_run.py con datos OHLC reales antes de exponer MTF."],
        )

    try:
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return _blocked_payload(
            "invalid",
            "La evidencia A56 existe, pero no se pudo leer como JSON valido.",
            report_path,
            [str(exc)],
        )

    metadata = _safe_dict(report.get("metadata"))
    builder = _safe_dict(report.get("builder"))
    artifacts = _safe_dict(report.get("artifacts"))
    plan_summary = _safe_dict(artifacts.get("planSummary"))
    outputs = _output_list(builder)
    assets = _processed_assets(builder)
    status = str(report.get("status") or "NO_GO").upper()
    available = status == "GO"
    failures = _failure_messages(report, artifacts)

    if not available:
        return {
            **_blocked_payload(
                "blocked",
                "La evidencia A56 aun no esta en GO; el dashboard la mantiene solo como lectura bloqueada.",
                report_path,
                failures or ["A56 devolvio NO_GO."],
            ),
            "status": status,
            "generatedAt": metadata.get("generatedAt") or metadata.get("createdAt") or _utc_now(),
            "outputs": outputs,
            "artifacts": _artifact_list(artifacts),
        }

    return {
        "ok": True,
        "available": True,
        "status": status,
        "state": "ready",
        "message": "Evidencia A56 GO disponible en modo lectura.",
        "generatedAt": metadata.get("generatedAt") or metadata.get("createdAt") or _utc_now(),
        "policy": "read_only_after_a56_go",
        "report": {"file": report_path.name, "exists": True},
        "summary": {
            "timeframeCount": len(outputs),
            "assetCount": len(assets),
            "assets": assets[:MAX_ITEMS],
            "currentPlanMtfCovered": int(plan_summary.get("covered") or 0),
            "currentPlanMtfStrong": int(plan_summary.get("strong") or 0),
            "needsReview": int(plan_summary.get("needsReview") or 0),
        },
        "outputs": outputs,
        "artifacts": _artifact_list(artifacts),
        "failures": failures,
    }
