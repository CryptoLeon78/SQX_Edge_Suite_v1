from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from uuid import uuid4

from .sqx_compatibility import SQX142_DEFAULT_ROOT


AI_WIZARD_VERSION = "sqx142-ai-wizard-v1"
AI_WIZARD_AI2_VERSION = "sqx142-ai-wizard-studio-v2"
AI_WIZARD_AI3_COMPILER_VERSION = "sqx142-aw-ai3-universal-prompt-compiler-v1"
AI_WIZARD_AI3_CATALOG_VERSION = "sqx142-aw-ai3-expanded-catalog-v1"
AI_WIZARD_AI4_RSI_COMPILER_VERSION = "sqx142-aw-ai4-rsi-mean-reversion-compiler-v1"
SPEC_TYPE = "sqx-edge.ai-wizard-strategy-spec"
CATALOG_TYPE = "sqx-edge.ai-wizard-capability-catalog-v1"
AST_TYPE = "sqx-edge.ai-wizard-strategy-ast-v1"
PACKAGE_TYPE = "sqx-edge.strategy-builder-package"
DEFAULT_OUTPUT_DIRNAME = "ai_wizard_drafts"
SESSION_DB_RELATIVE = Path(".local") / "sqx142_ai_wizard" / "ai_wizard.sqlite"
XML_ENTRY = "strategy_Portfolio.xml"


SUPPORTED_ARCHETYPES = {
    "ema_cross": {
        "label": "EMA cross trend-following",
        "ideaArchetype": "trend_following",
        "template": "EMACross.sqx",
        "keywords": ("ema", "moving average", "media movil", "media móvil", "cross", "cruce", "trend"),
        "rules": [
            "Fast EMA crosses above slow EMA for long signal.",
            "Fast EMA crosses below slow EMA for short signal.",
        ],
    },
    "breakout": {
        "label": "Breakout",
        "ideaArchetype": "breakout",
        "template": "breakout.sqx",
        "keywords": ("breakout", "break out", "rompimiento", "ruptura", "highest", "maximo", "máximo"),
        "rules": [
            "Enter when price breaks a prior range or high.",
            "Keep execution review manual before using the strategy in SQX.",
        ],
    },
    "range_breakout": {
        "label": "Range breakout",
        "ideaArchetype": "breakout",
        "template": "RangeBreakout.sqx",
        "keywords": ("range breakout", "rango", "inside range", "range break"),
        "rules": [
            "Define a recent range.",
            "Enter when price breaks the range boundary.",
        ],
    },
    "mean_reversion": {
        "label": "Mean reversion",
        "ideaArchetype": "mean_reversion",
        "template": "mean_reversion.sqx",
        "keywords": ("mean reversion", "reversion", "reversión", "reversion a la media", "buy dips", "dip"),
        "rules": [
            "Look for temporary extension away from mean.",
            "Return-to-mean logic remains a draft for manual AlgoWizard review.",
        ],
    },
}

SUPPORTED_ASSETS = {"EURUSD", "USDJPY", "AUDCAD", "GBPUSD", "US500", "XAUUSD"}
ASSET_ALIASES = {
    "SP500": "US500",
    "SP 500": "US500",
    "S&P500": "US500",
    "S&P 500": "US500",
    "US500": "US500",
}
SUPPORTED_TIMEFRAMES = {"M15", "M30", "H1", "H4", "D1"}


@dataclass(frozen=True)
class AiWizardProviderConfig:
    provider_id: str
    ollama_model: str
    openai_enabled: bool
    openai_model: str


def _privacy() -> dict[str, bool]:
    return {
        "local_paths_returned": False,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
        "external_api_called": False,
        "license_material_returned": False,
        "tokens_returned": False,
        "raw_xml_returned": False,
        "raw_template_names_returned": False,
        "raw_capability_labels_returned": False,
        "session_token_returned": False,
        "sqx_runtime_started": False,
        "sqx_data_db_written": False,
        "sqx_user_projects_written": False,
    }


AI_WIZARD_INTERPRETER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "asset": {"type": "string"},
        "timeframe": {"type": "string"},
        "direction": {"type": "string", "enum": ["long_only", "short_only", "both", ""]},
        "intent": {"type": "string"},
        "blocks": {"type": "array", "items": {"type": "string"}},
        "filters": {"type": "array", "items": {"type": "string"}},
        "risk": {
            "type": "object",
            "properties": {
                "stopLossPips": {"type": ["number", "integer", "null"]},
                "takeProfitPips": {"type": ["number", "integer", "null"]},
            },
        },
        "candlePattern": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "redCandles": {"type": ["integer", "null"]},
                "greenCandles": {"type": ["integer", "null"]},
                "requiresHammer": {"type": "boolean"},
                "entryTiming": {"type": "string"},
            },
        },
        "confidence": {"type": ["number", "integer", "null"]},
    },
    "required": [],
}


def _base_response(
    data: dict[str, Any] | None = None,
    *,
    ok: bool = True,
    error: str = "",
    blockers: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "version": AI_WIZARD_VERSION,
        "scope": "local_operator_only",
        "mode": "guided_strategy_draft",
        "data": data or {},
        "blockers": blockers or [],
        "warnings": warnings or [],
        "privacy": _privacy(),
    }
    if error:
        payload["error"] = error
    return payload


def _clean_text(value: Any, limit: int = 1200) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def _contains_private_or_path_text(prompt: str) -> bool:
    lowered = prompt.casefold()
    if re.search(r"[A-Za-z]:\\|/users/|\\users\\|token=|password=|apikey|api_key|secret", prompt, re.IGNORECASE):
        return True
    if any(word in lowered for word in ("license", "licencia", "bypass", "crack", "activation", "activacion", "activación")):
        return True
    return False


def _provider_config() -> AiWizardProviderConfig:
    openai_enabled = str(os.environ.get("SQX_AI_WIZARD_OPENAI_ENABLED", "")).strip().casefold() in {"1", "true", "yes", "on"}
    configured_provider = str(os.environ.get("SQX_AI_WIZARD_PROVIDER", "ollama")).strip().casefold()
    provider_id = "openai" if configured_provider == "openai" and openai_enabled else "ollama"
    return AiWizardProviderConfig(
        provider_id=provider_id,
        ollama_model=str(os.environ.get("SQX_AI_WIZARD_OLLAMA_MODEL", "qwen3.5:latest")).strip() or "qwen3.5:latest",
        openai_enabled=openai_enabled,
        openai_model=str(os.environ.get("SQX_AI_WIZARD_OPENAI_MODEL", "gpt-4.1-mini")).strip() or "gpt-4.1-mini",
    )


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _normalize_hint_list(value: Any, *, limit: int = 12) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value[:limit]:
        text = re.sub(r"[^A-Za-z0-9_&.+ -]+", "", str(item or "")).strip()
        if text:
            items.append(text[:80])
    return list(dict.fromkeys(items))


def _catalog_semantic_items(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    data = catalog.get("data", {}).get("catalog", catalog)
    semantic = data.get("semanticCatalog") if isinstance(data.get("semanticCatalog"), dict) else {}
    items = semantic.get("items") if isinstance(semantic.get("items"), list) else []
    return [item for item in items if isinstance(item, dict)]


def _catalog_prompt_summary(catalog: dict[str, Any]) -> dict[str, Any]:
    keys = _catalog_key_sets(catalog)
    data = catalog.get("data", {}).get("catalog", catalog)
    conditions = data.get("conditions") if isinstance(data.get("conditions"), dict) else {}
    condition_items = conditions.get("items") if isinstance(conditions.get("items"), list) else []
    safe_conditions = []
    for item in condition_items[:80]:
        if not isinstance(item, dict):
            continue
        safe_conditions.append({
            "id": str(item.get("id") or "")[:80],
            "category": str(item.get("category") or "")[:80],
            "returnType": str(item.get("returnType") or "")[:40],
        })
    return {
        "blocks": sorted(keys["blocks"])[:80],
        "comparisons": sorted(keys["comparisons"] | keys["conditions"])[:120],
        "conditions": safe_conditions,
        "semanticCatalog": [
            {
                "id": str(item.get("id") or "")[:100],
                "label": str(item.get("label") or "")[:120],
                "kind": str(item.get("kind") or "")[:40],
                "category": str(item.get("category") or "")[:80],
                "returnType": str(item.get("returnType") or "")[:40],
                "aliases": [str(alias)[:60] for alias in item.get("aliases", [])[:8] if alias],
                "compilerSupport": str(item.get("compilerSupport") or "")[:80],
            }
            for item in _catalog_semantic_items(catalog)[:120]
        ],
        "supports": {
            "ohlc": all(item in keys["blocks"] for item in ("Open", "Close", "High", "Low")),
            "atr": _catalog_has_atr_support(catalog),
        },
    }


def _try_local_model_interpretation(prompt: str, catalog: dict[str, Any], payload: dict[str, Any], llm_client: Any | None = None) -> dict[str, Any]:
    mode = str(payload.get("compilerMode") or payload.get("interpreterMode") or "auto").strip().casefold()
    if mode in {"heuristic", "off", "disabled"}:
        return {"source": "heuristic_requested", "available": False, "privacy": _privacy()}
    if llm_client is None:
        try:
            from .agent.llm_client import OllamaClient, OllamaConfig

            provider = _provider_config()
            timeout = _safe_float(os.environ.get("SQX_AI_WIZARD_INTERPRETER_TIMEOUT_SECONDS"), 2.0)
            client = OllamaClient(OllamaConfig(model=provider.ollama_model, timeout_seconds=timeout, auto_start=False))
        except Exception as exc:
            return {"source": "heuristic_model_client_unavailable", "available": False, "error": type(exc).__name__, "privacy": _privacy()}
    else:
        client = llm_client
    try:
        status = client.status(auto_start=False) if hasattr(client, "status") else {"available": True, "model": getattr(client, "model", "")}
        if not status.get("available") and mode == "ollama":
            return {"source": "heuristic_no_ollama", "available": False, "model": status.get("model", ""), "privacy": _privacy()}
        if not status.get("available"):
            return {"source": "heuristic_no_ollama", "available": False, "model": status.get("model", ""), "privacy": _privacy()}
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a local-only AlgoWizard AST interpreter. Return only JSON matching the schema. "
                    "Use only catalog ids provided. If unsure, leave fields empty or mark manual review. "
                    "Do not invent files, paths, providers, profitability claims, SQX runtime actions or private data."
                ),
            },
            {
                "role": "user",
                "content": _json_dump({
                    "prompt": prompt,
                    "catalog": _catalog_prompt_summary(catalog),
                    "target": "sqx-edge.ai-wizard-strategy-ast-v1",
                }),
            },
        ]
        raw = client.chat_json(messages=messages, schema=AI_WIZARD_INTERPRETER_SCHEMA, model=status.get("model"))
        if not isinstance(raw, dict):
            return {"source": "heuristic_after_model_error", "available": True, "model": status.get("model", ""), "error": "model_json_not_object", "privacy": _privacy()}
        return {
            "source": "ollama_ast",
            "available": True,
            "model": status.get("model", ""),
            "asset": str(raw.get("asset") or "")[:32],
            "timeframe": str(raw.get("timeframe") or "")[:16],
            "direction": str(raw.get("direction") or "")[:24],
            "intent": str(raw.get("intent") or "")[:120],
            "blocks": _normalize_hint_list(raw.get("blocks")),
            "filters": _normalize_hint_list(raw.get("filters")),
            "risk": raw.get("risk") if isinstance(raw.get("risk"), dict) else {},
            "candlePattern": raw.get("candlePattern") if isinstance(raw.get("candlePattern"), dict) else {},
            "confidence": max(0.0, min(_safe_float(raw.get("confidence"), 0.0), 1.0)),
            "privacy": _privacy(),
        }
    except Exception as exc:
        return {"source": "heuristic_after_model_error", "available": False, "error": type(exc).__name__, "privacy": _privacy()}


def _hash_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _resolve_sqx142_root(project_root: Path | None = None, sqx142_root: Path | None = None) -> Path:
    if sqx142_root:
        return Path(sqx142_root)
    env_root = os.environ.get("SQX142_ROOT")
    if env_root:
        return Path(env_root)
    if project_root:
        config_path = Path(project_root) / "backend" / "sqx-edge-tool" / "config.json"
        if config_path.is_file():
            try:
                import json

                config = json.loads(config_path.read_text(encoding="utf-8"))
                if config.get("sqx_path"):
                    return Path(str(config["sqx_path"]))
            except (OSError, ValueError, TypeError):
                pass
    return Path(SQX142_DEFAULT_ROOT)


def _template_root(sqx142_root: Path | None = None, project_root: Path | None = None) -> Path:
    return _resolve_sqx142_root(project_root, sqx142_root) / "internal" / "web" / "AlgoWizard" / "examples"


def _template_path(archetype: str, sqx142_root: Path | None = None, project_root: Path | None = None) -> Path:
    template = SUPPORTED_ARCHETYPES[archetype]["template"]
    return _template_root(sqx142_root, project_root) / template


def _output_root(project_root: Path, output_dir: Path | None = None) -> Path:
    return Path(output_dir or (Path(project_root) / "output" / DEFAULT_OUTPUT_DIRNAME))


def _safe_file_stem(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())[:80].strip("._-")
    return cleaned or "SQX_Edge_AI_Draft"


def _detect_asset(prompt: str) -> str:
    upper = prompt.upper()
    compact = re.sub(r"[^A-Z0-9]+", "", upper)
    for alias, asset in sorted(ASSET_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in upper or re.sub(r"[^A-Z0-9]+", "", alias) in compact:
            return asset
    for asset in SUPPORTED_ASSETS:
        if asset in upper:
            return asset
    return "EURUSD"


def _detect_timeframe(prompt: str) -> str:
    upper = prompt.upper()
    for timeframe in sorted(SUPPORTED_TIMEFRAMES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(timeframe)}\b", upper):
            return timeframe
    return "H1"


def _detect_direction(prompt: str) -> str:
    lowered = prompt.casefold()
    long_tokens = ("long only", "solo long", "only long", "compras only", "en largo", "largo", "comprar", "compra", "buy", "alcista")
    short_tokens = ("short only", "solo short", "only short", "ventas only", "en corto", "corto", "vender", "venta", "sell", "bajista")
    has_long = any(token in lowered for token in long_tokens) or bool(re.search(r"\blong\b", lowered))
    has_short = any(token in lowered for token in short_tokens) or bool(re.search(r"\bshort\b", lowered))
    if has_long and not has_short:
        return "long_only"
    if has_short and not has_long:
        return "short_only"
    return "both"


def _detect_archetype(prompt: str) -> str:
    lowered = prompt.casefold()
    if "range breakout" in lowered or "rango" in lowered:
        return "range_breakout"
    scores: dict[str, int] = {}
    for archetype, meta in SUPPORTED_ARCHETYPES.items():
        scores[archetype] = sum(1 for keyword in meta["keywords"] if keyword in lowered)
    best = max(scores, key=lambda key: scores[key])
    return best if scores[best] > 0 else ""


def _strategy_name(asset: str, timeframe: str, archetype: str) -> str:
    label = SUPPORTED_ARCHETYPES[archetype]["label"].replace(" ", "_").replace("-", "_")
    return _safe_file_stem(f"SQXEdgeAI_{asset}_{timeframe}_{label}")


def _strategy_builder_package(spec: dict[str, Any]) -> dict[str, Any]:
    archetype = spec["archetype"]
    return {
        "type": PACKAGE_TYPE,
        "version": AI_WIZARD_VERSION,
        "workflow_state": "package_exportable",
        "source_mode": "ai_wizard_prompt",
        "asset_profile": {
            "asset": spec["asset"],
            "timeframe": spec["timeframe"],
            "direction": spec["direction"],
        },
        "idea_archetype": {
            "id": SUPPORTED_ARCHETYPES[archetype]["ideaArchetype"],
            "source": "ai_wizard",
        },
        "project_generator_handoff": {
            "auto_run_bulk_generation": False,
            "manual_review_required": True,
        },
        "algo_wizard_draft": {
            "supported": True,
            "templateClass": archetype,
            "templateFileRef": _hash_id("aw_template", SUPPORTED_ARCHETYPES[archetype]["template"]),
        },
        "guardrails": [
            "no_generation_triggered",
            "no_sqx_runtime_launch",
            "no_data_db_write",
            "manual_algowizard_review_required",
        ],
    }


def build_ai_wizard_spec(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    prompt = _clean_text(payload.get("prompt") or payload.get("message") or payload.get("idea"))
    if not prompt:
        blocked = ["prompt_required"]
        return _base_response(
            {
                "status": "blocked",
                "spec": {"type": SPEC_TYPE, "status": "blocked", "blockers": blocked},
                "nextStep": "Describe a simple supported strategy idea.",
            },
            ok=False,
            error="prompt_required",
            blockers=blocked,
        )
    if _contains_private_or_path_text(prompt):
        blocked = ["private_or_forbidden_text_detected"]
        return _base_response(
            {
                "status": "blocked",
                "spec": {"type": SPEC_TYPE, "status": "blocked", "blockers": blocked},
                "nextStep": "Remove paths, sensitive values, license terms or bypass language from the request.",
            },
            ok=False,
            error="prompt_not_public_safe",
            blockers=blocked,
        )
    archetype = _detect_archetype(prompt)
    if not archetype:
        blocked = ["blocked_unsupported_rule"]
        return _base_response(
            {
                "status": "blocked",
                "spec": {
                    "type": SPEC_TYPE,
                    "status": "blocked",
                    "blockers": blocked,
                    "supportedArchetypes": list(SUPPORTED_ARCHETYPES),
                },
                "nextStep": "Use EMA cross, breakout, range breakout or mean reversion for v1.",
            },
            ok=False,
            error="blocked_unsupported_rule",
            blockers=blocked,
        )
    asset = _detect_asset(prompt)
    timeframe = _detect_timeframe(prompt)
    direction = _detect_direction(prompt)
    name = _strategy_name(asset, timeframe, archetype)
    spec = {
        "type": SPEC_TYPE,
        "version": AI_WIZARD_VERSION,
        "status": "ready",
        "ideaFingerprint": _hash_id("idea", prompt),
        "asset": asset,
        "timeframe": timeframe,
        "direction": direction,
        "archetype": archetype,
        "label": SUPPORTED_ARCHETYPES[archetype]["label"],
        "strategyName": name,
        "rules": SUPPORTED_ARCHETYPES[archetype]["rules"],
        "risk": {
            "slTpMentioned": bool(re.search(r"\b(sl|stop loss|tp|take profit)\b", prompt, re.IGNORECASE)),
            "manualReviewRequired": True,
        },
    }
    package = _strategy_builder_package(spec)
    return _base_response({
        "status": "ready",
        "spec": spec,
        "strategyBuilderPackage": package,
        "nextStep": "Generate draft .sqx and review it manually inside AlgoWizard.",
    })


def probe_algowizard_templates(sqx142_root: Path | None = None, project_root: Path | None = None) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    blockers: list[str] = []
    for archetype, meta in SUPPORTED_ARCHETYPES.items():
        path = _template_path(archetype, sqx142_root, project_root)
        exists = path.is_file()
        is_zip = exists and zipfile.is_zipfile(path)
        has_xml = False
        entry_count = 0
        if is_zip:
            try:
                with zipfile.ZipFile(path, "r") as archive:
                    names = set(archive.namelist())
                    has_xml = XML_ENTRY in names
                    entry_count = len(names)
            except (OSError, zipfile.BadZipFile):
                is_zip = False
        if not (exists and is_zip and has_xml):
            blockers.append(f"{archetype}_template_unavailable")
        items.append({
            "archetype": archetype,
            "templateRef": _hash_id("aw_template", str(meta["template"])),
            "exists": exists,
            "isZip": bool(is_zip),
            "hasStrategyPortfolioXml": bool(has_xml),
            "entryCount": entry_count,
        })
    return _base_response({
        "templates": items,
        "allReady": not blockers,
        "xmlEntry": XML_ENTRY,
    }, ok=not blockers, blockers=blockers, error="template_probe_failed" if blockers else "")


def _patch_strategy_xml(xml_bytes: bytes, spec: dict[str, Any]) -> bytes:
    root = ET.fromstring(xml_bytes)
    name = str(spec.get("strategyName") or "SQXEdgeAI_Draft")
    options = root.find("options")
    if options is not None:
        strategy_name = options.find("StrategyName")
        if strategy_name is not None:
            strategy_name.text = name
        date = options.find("Date")
        if date is not None:
            date.text = datetime.now().strftime("%m/%d/%Y %H:%M")
    strategy = root.find("Strategy")
    if strategy is not None:
        strategy.set("name", f"{name}.sqx")
        description = strategy.find("Description")
        if description is not None:
            description.text = (
                "SQX Edge AI Wizard draft. "
                f"Asset={spec.get('asset')}; timeframe={spec.get('timeframe')}; "
                f"direction={spec.get('direction')}; archetype={spec.get('archetype')}. "
                "Review manually in AlgoWizard before any SQX validation."
            )
    ET.indent(root, space="  ")
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8")


def _set_strategy_metadata(root: ET.Element, name: str, description_text: str) -> None:
    options = root.find("options")
    if options is not None:
        strategy_name = options.find("StrategyName")
        if strategy_name is not None:
            strategy_name.text = name
        date = options.find("Date")
        if date is not None:
            date.text = datetime.now().strftime("%m/%d/%Y %H:%M")
    strategy = root.find("Strategy")
    if strategy is not None:
        strategy.set("name", f"{name}.sqx")
        description = strategy.find("Description")
        if description is None:
            description = ET.SubElement(strategy, "Description")
        description.text = description_text


def _set_nested_slpt_values(root: ET.Element, *, stop_loss: int | float, take_profit: int | float) -> None:
    targets = {
        "#StopLoss.StopLoss#": stop_loss,
        "#ProfitTarget.ProfitTarget#": take_profit,
    }
    for param in root.iter("Param"):
        target = targets.get(param.get("key") or "")
        if target is None:
            continue
        for child in param.iter("Param"):
            if child is not param and child.get("key") == "#Value#":
                child.text = str(target)
                child.set("variable", "false")
                break


def _replace_element_children(parent: ET.Element, child: ET.Element) -> None:
    for existing in list(parent):
        parent.remove(existing)
    parent.append(child)


def _candle_atr_conditions(ast: dict[str, Any]) -> list[ET.Element]:
    pattern = ast.get("recognized", {}).get("pattern", {}) if isinstance(ast.get("recognized"), dict) else {}
    red_count = max(1, min(_safe_int(pattern.get("redCandles"), 3) or 3, 5))
    conditions: list[ET.Element] = []
    # On bar close: shift 1 is the second green confirmation, shift 2 is the hammer/first green.
    for shift in range(red_count + 2, 2, -1):
        conditions.append(_xml_red_candle(shift))
    conditions.append(_xml_green_candle(2))
    if pattern.get("requiresHammer"):
        # Conservative hammer proxy expressible with allowlisted OHLC: green body and lower wick below both body endpoints.
        conditions.append(_xml_comparison("IsLower", _xml_price_value("Low", 2), _xml_price_value("Open", 2)))
        conditions.append(_xml_comparison("IsLower", _xml_price_value("Low", 2), _xml_price_value("Close", 2)))
    conditions.append(_xml_green_candle(1))
    filters = ast.get("recognized", {}).get("filters", []) if isinstance(ast.get("recognized"), dict) else []
    if any(isinstance(item, dict) and item.get("blockId") == "ATR" and item.get("availableInCatalog") for item in filters):
        conditions.append(_xml_comparison("IsGreater", _xml_atr_value(14, 1), _xml_atr_value(14, 2)))
    return conditions


def _patch_candle_atr_strategy_xml(xml_bytes: bytes, ast: dict[str, Any]) -> bytes:
    root = ET.fromstring(xml_bytes)
    name = str(ast.get("strategyName") or "SQXEdgeAI3_Candle_ATR")
    risk = ast.get("actions", {}).get("risk", {}) if isinstance(ast.get("actions"), dict) else {}
    _set_strategy_metadata(
        root,
        name,
        (
            "SQX Edge AI3 Universal Prompt Compiler draft. "
            f"Asset={ast.get('asset')}; timeframe={ast.get('timeframe')}; direction={ast.get('direction')}; "
            "family=candle_atr_sequence. Manual AlgoWizard review required before any SQX validation."
        ),
    )
    signals = root.findall(".//signal")
    if len(signals) < 2:
        raise ValueError("candle_atr_template_missing_signals")
    _replace_element_children(signals[0], _xml_and(_candle_atr_conditions(ast)))
    _replace_element_children(signals[1], _xml_false_condition())
    _set_nested_slpt_values(
        root,
        stop_loss=risk.get("stopLossPips", 0),
        take_profit=risk.get("takeProfitPips", 0),
    )
    ET.indent(root, space="  ")
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8")


def _rsi_mean_reversion_conditions(direction: str) -> tuple[ET.Element, ET.Element]:
    long_condition = _xml_comparison("IsLower", _xml_rsi_value(14, 1), _xml_number_value(30))
    short_condition = _xml_comparison("IsGreater", _xml_rsi_value(14, 1), _xml_number_value(70))
    if direction == "long_only":
        return long_condition, _xml_false_condition()
    if direction == "short_only":
        return _xml_false_condition(), short_condition
    return long_condition, short_condition


def _patch_rsi_mean_reversion_strategy_xml(xml_bytes: bytes, ast: dict[str, Any]) -> bytes:
    root = ET.fromstring(xml_bytes)
    name = str(ast.get("strategyName") or "SQXEdgeAI4_RSI_MeanReversion")
    risk = ast.get("actions", {}).get("risk", {}) if isinstance(ast.get("actions"), dict) else {}
    direction = str(ast.get("direction") or "both")
    _set_strategy_metadata(
        root,
        name,
        (
            "SQX Edge AI4 RSI Mean-Reversion Compiler draft. "
            f"Asset={ast.get('asset')}; timeframe={ast.get('timeframe')}; direction={direction}; "
            "family=rsi_mean_reversion. Manual AlgoWizard review required before any SQX validation."
        ),
    )
    signals = root.findall(".//signal")
    if len(signals) < 2:
        raise ValueError("rsi_mean_reversion_template_missing_signals")
    long_condition, short_condition = _rsi_mean_reversion_conditions(direction)
    _replace_element_children(signals[0], long_condition)
    _replace_element_children(signals[1], short_condition)
    _set_nested_slpt_values(
        root,
        stop_loss=risk.get("stopLossPips", 0),
        take_profit=risk.get("takeProfitPips", 0),
    )
    ET.indent(root, space="  ")
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8")


def _copy_sqx_with_patched_xml(template: Path, target: Path, patched_xml: bytes) -> None:
    with zipfile.ZipFile(template, "r") as source:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in source.infolist():
                if item.filename == XML_ENTRY:
                    archive.writestr(item, patched_xml)
                else:
                    archive.writestr(item, source.read(item.filename))


def generate_draft_sqx(
    payload: dict[str, Any] | None,
    *,
    project_root: Path,
    sqx142_root: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    plan = build_ai_wizard_spec(payload)
    if not plan.get("ok"):
        return plan
    spec = plan["data"]["spec"]
    probe = probe_algowizard_templates(sqx142_root, project_root)
    if not probe.get("ok"):
        return _base_response(
            {
                "status": "blocked",
                "spec": spec,
                "probe": probe["data"],
                "nextStep": "Repair or verify AlgoWizard example templates before generating drafts.",
            },
            ok=False,
            error="template_probe_failed",
            blockers=probe.get("blockers", []),
        )
    template = _template_path(spec["archetype"], sqx142_root, project_root)
    output_root = _output_root(project_root, output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"{_safe_file_stem(spec['strategyName'])}_{timestamp}.sqx"
    target = (output_root / file_name).resolve()
    try:
        target.relative_to(output_root.resolve())
    except ValueError:
        return _base_response(ok=False, error="output_path_invalid", blockers=["output_path_invalid"])
    try:
        with zipfile.ZipFile(template, "r") as source:
            xml_bytes = source.read(XML_ENTRY)
            patched_xml = _patch_strategy_xml(xml_bytes, spec)
            with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("META-INF/MANIFEST.MF", source.read("META-INF/MANIFEST.MF") if "META-INF/MANIFEST.MF" in source.namelist() else b"Manifest-Version: 1.0\n")
                archive.writestr(XML_ENTRY, patched_xml)
        valid = zipfile.is_zipfile(target)
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        return _base_response(ok=False, error=type(exc).__name__, blockers=["draft_generation_failed"])
    return _base_response({
        "status": "draft_ready" if valid else "blocked",
        "spec": spec,
        "strategyBuilderPackage": plan["data"]["strategyBuilderPackage"],
        "draft": {
            "fileName": file_name,
            "fileId": _hash_id("draft", file_name),
            "downloadUrl": f"/api/sqx142/ai-wizard/draft-sqx/download/{file_name}",
            "isZip": bool(valid),
            "xmlEntry": XML_ENTRY,
            "manualReviewRequired": True,
        },
        "guardrails": [
            "written_to_sqx_edge_output_only",
            "no_sqx_user_projects_write",
            "no_data_db_write",
            "no_runtime_launch",
        ],
    }, ok=bool(valid), error="" if valid else "draft_zip_invalid")


def generate_ai_wizard_draft_from_ast(
    ast: dict[str, Any],
    *,
    project_root: Path,
    sqx142_root: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    compiler = ast.get("compiler", {}) if isinstance(ast.get("compiler"), dict) else {}
    if not compiler.get("draftable"):
        return _base_response_v2(ok=False, error="blocked_not_draftable_yet", blockers=compiler.get("blockers", ["blocked_not_draftable_yet"]))
    template_class = str(compiler.get("templateClass") or "")
    if template_class == "ema_cross":
        prompt = f"EMA cross trend-following {ast.get('asset', 'EURUSD')} {ast.get('timeframe', 'H1')} with SL/TP"
        return generate_draft_sqx({"prompt": prompt}, project_root=project_root, sqx142_root=sqx142_root, output_dir=output_dir)
    if template_class not in {"candle_atr_sequence", "rsi_mean_reversion"}:
        return _base_response_v2(ok=False, error="blocked_unsupported_compiler_family", blockers=["blocked_unsupported_compiler_family"])
    template = _template_path("ema_cross", sqx142_root, project_root)
    if not template.is_file() or not zipfile.is_zipfile(template):
        return _base_response_v2(ok=False, error=f"{template_class}_template_unavailable", blockers=[f"{template_class}_template_unavailable"])
    output_root = _output_root(project_root, output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    fallback_name = "SQXEdgeAI4_RSI_MeanReversion" if template_class == "rsi_mean_reversion" else "SQXEdgeAI3_Candle_ATR"
    file_name = f"{_safe_file_stem(str(ast.get('strategyName') or fallback_name))}_{timestamp}.sqx"
    target = (output_root / file_name).resolve()
    try:
        target.relative_to(output_root.resolve())
    except ValueError:
        return _base_response_v2(ok=False, error="output_path_invalid", blockers=["output_path_invalid"])
    try:
        with zipfile.ZipFile(template, "r") as source:
            xml_bytes = source.read(XML_ENTRY)
            source_entries = sorted(source.namelist())
        if template_class == "rsi_mean_reversion":
            patched_xml = _patch_rsi_mean_reversion_strategy_xml(xml_bytes, ast)
        else:
            patched_xml = _patch_candle_atr_strategy_xml(xml_bytes, ast)
        _copy_sqx_with_patched_xml(template, target, patched_xml)
        valid = zipfile.is_zipfile(target)
        with zipfile.ZipFile(target, "r") as generated:
            generated_entries = sorted(generated.namelist())
        if source_entries != generated_entries:
            return _base_response_v2(ok=False, error="draft_zip_entries_changed", blockers=["draft_zip_entries_changed"])
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError, ValueError) as exc:
        return _base_response_v2(ok=False, error=type(exc).__name__, blockers=["draft_generation_failed"])
    return _base_response_v2({
        "status": "draft_ready" if valid else "blocked",
        "draft": {
            "fileName": file_name,
            "fileId": _hash_id("draft", file_name),
            "downloadUrl": f"/api/sqx142/ai-wizard/draft-sqx/download/{file_name}",
            "isZip": bool(valid),
            "xmlEntry": XML_ENTRY,
            "manualReviewRequired": True,
            "compilerFamily": template_class,
            "compilerVersion": AI_WIZARD_AI4_RSI_COMPILER_VERSION if template_class == "rsi_mean_reversion" else AI_WIZARD_AI3_COMPILER_VERSION,
        },
        "ast": ast,
        "guardrails": [
            "written_to_sqx_edge_output_only",
            "zip_entries_preserved",
            "no_sqx_user_projects_write",
            "no_data_db_write",
            "no_runtime_launch",
            "manual_algowizard_review_required",
        ],
    }, ok=bool(valid), error="" if valid else "draft_zip_invalid")


def build_ai_wizard_status(project_root: Path, sqx142_root: Path | None = None) -> dict[str, Any]:
    provider = _provider_config()
    probe = probe_algowizard_templates(sqx142_root, project_root)
    output_root = _output_root(project_root)
    draft_count = 0
    if output_root.is_dir():
        draft_count = len([path for path in output_root.glob("*.sqx") if path.is_file()])
    return _base_response({
        "provider": {
            "id": provider.provider_id,
            "ollama": {"default": provider.provider_id == "ollama", "model": provider.ollama_model},
            "openai": {
                "enabled": provider.openai_enabled,
                "configured": bool(os.environ.get("OPENAI_API_KEY")),
                "model": provider.openai_model if provider.openai_enabled else "",
            },
        },
        "readiness": {
            "templatesReady": bool(probe.get("ok")),
            "draftOutputReady": True,
            "supportedArchetypes": list(SUPPORTED_ARCHETYPES),
            "draftCount": draft_count,
        },
        "probe": probe["data"],
        "limits": [
            "local_operator_only",
            "manual_algowizard_review_required",
            "no_sqx_runtime_launch",
            "no_data_db_write",
            "no_144_internals",
        ],
    }, ok=bool(probe.get("ok")), blockers=probe.get("blockers", []), error=probe.get("error", ""))


def resolve_draft_download(project_root: Path, file_name: str, output_dir: Path | None = None) -> Path | None:
    raw = str(file_name or "")
    safe = Path(raw).name
    if raw != safe:
        return None
    if not safe.endswith(".sqx"):
        return None
    output_root = _output_root(project_root, output_dir).resolve()
    candidate = (output_root / safe).resolve()
    try:
        candidate.relative_to(output_root)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _base_response_v2(
    data: dict[str, Any] | None = None,
    *,
    ok: bool = True,
    error: str = "",
    blockers: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    payload = _base_response(data, ok=ok, error=error, blockers=blockers, warnings=warnings)
    payload["version"] = AI_WIZARD_AI2_VERSION
    payload["mode"] = "algo_wizard_ai_studio"
    return payload


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


def _ai2_db_path(project_root: Path, db_path: Path | None = None) -> Path:
    path = Path(db_path or (Path(project_root) / SESSION_DB_RELATIVE))
    if not path.is_absolute():
        path = Path(project_root) / path
    path = path.resolve()
    local_root = (Path(project_root) / ".local").resolve()
    try:
        path.relative_to(local_root)
    except ValueError as exc:
        raise ValueError("ai_wizard_db_outside_local_root") from exc
    return path


def _connect_ai2_db(project_root: Path, db_path: Path | None = None) -> sqlite3.Connection:
    path = _ai2_db_path(project_root, db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            prompt_hash TEXT NOT NULL DEFAULT '',
            prompt_summary TEXT NOT NULL DEFAULT '',
            ast_json TEXT NOT NULL DEFAULT '{}',
            validation_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            prompt_hash TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        );
        CREATE TABLE IF NOT EXISTS spec_revisions (
            revision_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            ast_json TEXT NOT NULL,
            validation_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        );
        CREATE TABLE IF NOT EXISTS drafts (
            draft_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            ast_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            audit_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL DEFAULT '',
            event_type TEXT NOT NULL,
            details_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS catalog_snapshots (
            catalog_id TEXT PRIMARY KEY,
            source_hash TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    return con


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_load(value: str | None, fallback: Any) -> Any:
    try:
        return json.loads(value or "")
    except (TypeError, ValueError):
        return fallback


def _redacted_prompt_summary(prompt: str) -> str:
    text = _clean_text(prompt, limit=220)
    asset = _detect_asset(text)
    timeframe = _detect_timeframe(text)
    blocks = _detect_ai2_blocks(text)[:5]
    if _detect_candle_pattern(text):
        blocks = ["CandlePattern"] + blocks
    if re.search(r"\batr\b", text, re.IGNORECASE) and "ATR" not in blocks:
        blocks.append("ATR")
    archetype = _detect_archetype(text) or "custom_aw"
    parts = [" + ".join(blocks), archetype, asset, timeframe]
    return " | ".join(part for part in parts if part)[:180]


def _source_ref(value: str) -> str:
    return _hash_id("src", value)


def _parse_xml_safely(text: str, wrapper: str | None = None) -> ET.Element | None:
    try:
        return ET.fromstring(text)
    except ET.ParseError:
        if not wrapper:
            return None
    try:
        return ET.fromstring(f"<{wrapper}>{text}</{wrapper}>")
    except ET.ParseError:
        return None


def _read_text_if_safe(path: Path, max_chars: int = 2_000_000) -> tuple[str, str]:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", ""
    if len(data) > max_chars:
        data = data[:max_chars]
    return data, hashlib.sha256(data.encode("utf-8", errors="replace")).hexdigest()[:16]


def _parse_values(values: str | None) -> list[dict[str, str]]:
    parsed: list[dict[str, str]] = []
    for raw in str(values or "").split(","):
        part = raw.strip()
        if not part:
            continue
        if "=" in part:
            label, value = part.split("=", 1)
            parsed.append({"label": label.strip()[:80], "value": value.strip()[:80]})
        else:
            parsed.append({"label": part[:80], "value": part[:80]})
    return parsed[:80]


def _param_payload(node: ET.Element) -> dict[str, Any]:
    return {
        "key": str(node.get("key") or "")[:80],
        "name": str(node.get("name") or "")[:120],
        "type": str(node.get("type") or "")[:40],
        "controlType": str(node.get("controlType") or "")[:60],
        "defaultValue": str(node.get("defaultValue") or "")[:120],
        "minValue": str(node.get("minValue") or "")[:40],
        "maxValue": str(node.get("maxValue") or "")[:40],
        "step": str(node.get("step") or "")[:40],
        "values": _parse_values(node.get("values")),
    }


def _split_catalog_words(value: Any) -> list[str]:
    text = str(value or "")
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"[_#@()[\]{}.,:;\\/+-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return [part for part in text.split(" ") if part]


def _catalog_aliases(*values: Any, limit: int = 10) -> list[str]:
    aliases: list[str] = []
    stopwords = {
        "a", "an", "and", "at", "by", "de", "del", "el", "en", "is", "la", "of", "or", "the",
        "to", "y", "con", "sin", "than", "level", "bar",
    }
    for value in values:
        raw = str(value or "").strip()
        if not raw:
            continue
        compact = re.sub(r"\s+", " ", raw)[:100]
        words = _split_catalog_words(raw)
        phrase = " ".join(words)[:100]
        for alias in (compact, phrase):
            cleaned = re.sub(r"[^A-Za-z0-9 ._+-]+", "", alias).strip()
            if len(cleaned) >= 2 and cleaned.casefold() not in stopwords:
                aliases.append(cleaned)
        for word in words:
            normalized = re.sub(r"[^A-Za-z0-9+-]+", "", word).strip()
            if len(normalized) >= 3 and normalized.casefold() not in stopwords:
                aliases.append(normalized)
    deduped: list[str] = []
    seen: set[str] = set()
    for alias in aliases:
        key = alias.casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(alias[:80])
        if len(deduped) >= limit:
            break
    return deduped


def _semantic_prompt_seed(item: dict[str, Any]) -> str:
    label = str(item.get("label") or item.get("id") or "AlgoWizard condition")
    category = str(item.get("category") or "").strip()
    if category and category.casefold() not in label.casefold():
        return f"{category} {label}".strip()[:140]
    return label[:140]


def _collect_xml_item_keys(xml_bytes: bytes) -> set[str]:
    keys: set[str] = set()
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return keys
    for node in root.findall(".//Item"):
        key = str(node.get("key") or "").strip()
        if key:
            keys.add(key[:100])
    return keys


def _collect_parameter_sets(sqx142_root: Path, warnings: list[str]) -> dict[str, Any]:
    rel = Path("internal") / "ctemplate" / "parameterSets.xml"
    path = sqx142_root / rel
    text, digest = _read_text_if_safe(path)
    root = _parse_xml_safely(text, "parameterSets") if text else None
    sets: list[dict[str, Any]] = []
    if root is None:
        warnings.append("parameter_sets_unavailable")
    else:
        for set_node in root.findall("set"):
            params: list[dict[str, Any]] = []
            for param in set_node.findall(".//param"):
                params.append(_param_payload(param))
            sets.append({
                "id": str(set_node.get("name") or "")[:100],
                "paramCount": len(params),
                "params": params[:40],
            })
    return {
        "sourceRef": _source_ref(str(rel).replace("\\", "/")),
        "sourceHash": digest,
        "count": len(sets),
        "paramCount": sum(int(item.get("paramCount") or 0) for item in sets),
        "items": sets[:160],
    }


def _collect_conditions(sqx142_root: Path, warnings: list[str]) -> dict[str, Any]:
    rel = Path("internal") / "ctemplate" / "conditions.xml"
    path = sqx142_root / rel
    text, digest = _read_text_if_safe(path)
    root = _parse_xml_safely(text) if text else None
    categories: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    if root is None:
        warnings.append("conditions_unavailable")
    else:
        for cat in root.findall("category"):
            cat_name = str(cat.get("name") or "")[:120]
            cat_items = [node for node in cat.findall("item") if node.get("key")]
            categories.append({
                "name": cat_name,
                "key": str(cat.get("key") or "")[:80],
                "customIndicatorCategory": str(cat.get("ci") or "").lower() == "true",
                "itemCount": len(cat_items),
            })
            for node in cat_items:
                items.append({
                    "id": str(node.get("key") or "")[:100],
                    "name": str(node.get("name") or "")[:140],
                    "category": cat_name,
                    "returnType": str(node.get("returnType") or "")[:40],
                    "parameterSet": str(node.get("parameterSet") or "")[:100],
                    "displayTemplate": str(node.get("display") or "")[:220],
                    "engine": str(node.get("inEngine") or "")[:80],
                    "source": "conditions.xml",
                })
    return {
        "sourceRef": _source_ref(str(rel).replace("\\", "/")),
        "sourceHash": digest,
        "categories": categories,
        "items": items,
        "count": len(items),
    }


def _collect_wizard(sqx142_root: Path, warnings: list[str]) -> dict[str, Any]:
    rel = Path("internal") / "ctemplate" / "wizard.xml"
    path = sqx142_root / rel
    text, digest = _read_text_if_safe(path)
    root = _parse_xml_safely(text) if text else None
    steps: list[dict[str, Any]] = []
    blocks: dict[str, dict[str, Any]] = {}
    comparisons: dict[str, dict[str, Any]] = {}
    if root is None:
        warnings.append("wizard_xml_unavailable")
    else:
        for step in root.findall("./Steps/Step"):
            step_id = str(step.get("type") or step.get("caption") or "")[:80]
            block_items = []
            comparison_items = []
            for node in step.findall("./Blocks/Item"):
                key = str(node.get("key") or "")[:100]
                if not key:
                    continue
                payload = {
                    "id": key,
                    "displayTemplate": str(node.get("display") or "")[:220],
                    "returnType": str(node.get("returnType") or "price")[:40],
                    "source": "wizard.xml",
                }
                blocks[key] = payload
                block_items.append(key)
            for node in step.findall("./Comparisons/Item"):
                key = str(node.get("key") or "")[:100]
                if not key:
                    continue
                payload = {
                    "id": key,
                    "displayTemplate": str(node.get("display") or "")[:220],
                    "returnType": str(node.get("returnType") or "boolean")[:40],
                    "source": "wizard.xml",
                }
                comparisons[key] = payload
                comparison_items.append(key)
            steps.append({
                "caption": str(step.get("caption") or "")[:120],
                "type": step_id,
                "blockCount": len(block_items),
                "comparisonCount": len(comparison_items),
                "blocks": block_items[:60],
                "comparisons": comparison_items[:40],
            })
    return {
        "sourceRef": _source_ref(str(rel).replace("\\", "/")),
        "sourceHash": digest,
        "steps": steps,
        "blocks": sorted(blocks.values(), key=lambda item: item["id"]),
        "comparisons": sorted(comparisons.values(), key=lambda item: item["id"]),
        "blockCount": len(blocks),
        "comparisonCount": len(comparisons),
    }


def _collect_examples(sqx142_root: Path, warnings: list[str]) -> dict[str, Any]:
    root = sqx142_root / "internal" / "web" / "AlgoWizard" / "examples"
    items: list[dict[str, Any]] = []
    feature_ids: set[str] = set()
    if not root.is_dir():
        warnings.append("algowizard_examples_unavailable")
    else:
        for path in sorted(root.glob("*.sqx")):
            entry_count = 0
            has_xml = False
            example_features: set[str] = set()
            is_zip = zipfile.is_zipfile(path)
            if is_zip:
                try:
                    with zipfile.ZipFile(path, "r") as archive:
                        names = archive.namelist()
                        entry_count = len(names)
                        has_xml = XML_ENTRY in names
                        if has_xml:
                            info = archive.getinfo(XML_ENTRY)
                            if info.file_size <= 2_000_000:
                                example_features = _collect_xml_item_keys(archive.read(XML_ENTRY))
                                feature_ids.update(example_features)
                            elif "algowizard_example_xml_too_large" not in warnings:
                                warnings.append("algowizard_example_xml_too_large")
                except (OSError, zipfile.BadZipFile):
                    is_zip = False
            items.append({
                "exampleRef": _hash_id("aw_example", path.name),
                "isZip": bool(is_zip),
                "hasStrategyPortfolioXml": bool(has_xml),
                "entryCount": entry_count,
                "featureRefs": sorted(example_features)[:60],
                "sizeClass": "large" if path.stat().st_size > 1_000_000 else "small",
            })
    feature_hash = hashlib.sha256(",".join(sorted(feature_ids)).encode("utf-8", errors="replace")).hexdigest()[:16]
    return {
        "count": len(items),
        "featureCount": len(feature_ids),
        "featureHash": feature_hash,
        "featureIds": sorted(feature_ids)[:220],
        "items": items[:80],
    }


def _collect_snippet_families(sqx142_root: Path) -> dict[str, Any]:
    code_root = sqx142_root / "internal" / "extend" / "Code"
    families: list[dict[str, Any]] = []
    if code_root.is_dir():
        for family in sorted([item for item in code_root.iterdir() if item.is_dir()]):
            blocks_dir = family / "blocks"
            files = list(blocks_dir.glob("*")) if blocks_dir.is_dir() else []
            ids = sorted({path.stem for path in files if path.is_file()})[:120]
            families.append({
                "family": family.name[:80],
                "blockCount": len([path for path in files if path.is_file()]),
                "sampleIds": ids[:20],
                "sampleHash": hashlib.sha256(",".join(ids).encode("utf-8", errors="replace")).hexdigest()[:16],
            })
    return {"familyCount": len(families), "families": families[:40]}


def _collect_custom_indicators(sqx142_root: Path) -> dict[str, Any]:
    root = sqx142_root / "custom_indicators"
    by_platform: dict[str, int] = {}
    sample_ids: list[str] = []
    if root.is_dir():
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".mq4", ".mq5", ".java", ".jfx", ".txt"}:
                continue
            rel_parts = path.relative_to(root).parts
            platform = rel_parts[0] if rel_parts else "unknown"
            by_platform[platform] = by_platform.get(platform, 0) + 1
            if len(sample_ids) < 40:
                sample_ids.append(path.stem[:80])
    return {
        "count": sum(by_platform.values()),
        "platforms": [{"platform": key, "count": by_platform[key]} for key in sorted(by_platform)],
        "sampleIds": sorted(set(sample_ids))[:40],
    }


def _collect_blocksettings(project_root: Path) -> dict[str, Any]:
    manifest = Path(project_root) / "backend" / "sqx-edge-tool" / "config" / "blocksettings_manifest.json"
    resources = Path(project_root) / "backend" / "sqx-edge-tool" / "resources" / "blocksettings"
    items: list[dict[str, Any]] = []
    if manifest.is_file():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            raw_items = payload.get("entries") or payload.get("items") or payload.get("blocksettings") or []
            if isinstance(raw_items, list):
                for item in raw_items[:120]:
                    if isinstance(item, dict):
                        name = str(item.get("id") or item.get("name") or item.get("file") or "")[:120]
                        if name:
                            items.append({"id": _hash_id("bs", name), "name": name})
        except (OSError, ValueError, TypeError):
            items = []
    if not items and resources.is_dir():
        for path in sorted(resources.glob("*.sqb")):
            items.append({"id": _hash_id("bs", path.name), "name": path.name[:120]})
    return {"count": len(items), "items": items[:120]}


def _build_semantic_catalog(
    wizard: dict[str, Any],
    conditions: dict[str, Any],
    examples: dict[str, Any],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    by_category: dict[str, int] = {}

    for block in wizard.get("blocks", []) if isinstance(wizard.get("blocks"), list) else []:
        if not isinstance(block, dict) or not block.get("id"):
            continue
        item = {
            "id": str(block.get("id") or "")[:100],
            "label": str(block.get("id") or "")[:120],
            "kind": "wizard_block",
            "category": "Wizard block",
            "returnType": str(block.get("returnType") or "")[:40],
            "aliases": _catalog_aliases(block.get("id"), block.get("displayTemplate")),
            "compilerSupport": "draftable_rsi_mean_reversion" if str(block.get("id") or "") == "RSI" else "catalog_ref_only",
            "promptSeed": str(block.get("id") or "")[:120],
        }
        items.append(item)
        by_category[item["category"]] = by_category.get(item["category"], 0) + 1

    for condition in conditions.get("items", []) if isinstance(conditions.get("items"), list) else []:
        if not isinstance(condition, dict) or not condition.get("id"):
            continue
        label = str(condition.get("name") or condition.get("id") or "")[:120]
        category = str(condition.get("category") or "Condition")[:80]
        item = {
            "id": str(condition.get("id") or "")[:100],
            "label": label,
            "kind": "condition_item",
            "category": category,
            "returnType": str(condition.get("returnType") or "")[:40],
            "aliases": _catalog_aliases(condition.get("id"), label, category, condition.get("displayTemplate")),
            "compilerSupport": "planning_only_not_draftable",
        }
        item["promptSeed"] = _semantic_prompt_seed(item)
        items.append(item)
        by_category[category] = by_category.get(category, 0) + 1

    for feature_id in examples.get("featureIds", []) if isinstance(examples.get("featureIds"), list) else []:
        feature = str(feature_id or "")[:100]
        if not feature or any(item.get("id") == feature for item in items):
            continue
        item = {
            "id": feature,
            "label": feature,
            "kind": "example_feature",
            "category": "Example feature",
            "returnType": "",
            "aliases": _catalog_aliases(feature),
            "compilerSupport": "observed_in_examples_planning_only",
            "promptSeed": feature,
        }
        items.append(item)
        by_category[item["category"]] = by_category.get(item["category"], 0) + 1

    items = sorted(items, key=lambda item: (str(item.get("category") or ""), str(item.get("id") or "")))
    alias_count = sum(len(item.get("aliases", [])) for item in items)
    return {
        "type": "sqx-edge.ai-wizard-semantic-catalog-v1",
        "version": AI_WIZARD_AI3_CATALOG_VERSION,
        "policy": "expanded_planning_catalog_not_universal_sqx_generation",
        "compilerBoundary": "semantic_items_do_not_make_draftable_without_compiler_family",
        "itemCount": len(items),
        "aliasCount": alias_count,
        "familyCount": len(by_category),
        "draftableFamilies": [
            {
                "id": "rsi_mean_reversion",
                "label": "RSI mean reversion",
                "version": AI_WIZARD_AI4_RSI_COMPILER_VERSION,
            }
        ],
        "families": [
            {"category": category, "itemCount": by_category[category]}
            for category in sorted(by_category)
        ],
        "items": items[:260],
    }


def build_ai_wizard_capability_catalog(
    project_root: Path,
    sqx142_root: Path | None = None,
    *,
    persist: bool = False,
    db_path: Path | None = None,
) -> dict[str, Any]:
    warnings: list[str] = []
    root = _resolve_sqx142_root(project_root, sqx142_root)
    hot_safe = {
        "sqxProcessState": "may_be_open",
        "userDataPolicy": "pending_stable_snapshot",
        "userProjectsPolicy": "pending_stable_snapshot",
        "writesToSqxRoot": False,
    }
    parameter_sets = _collect_parameter_sets(root, warnings)
    conditions = _collect_conditions(root, warnings)
    wizard = _collect_wizard(root, warnings)
    examples = _collect_examples(root, warnings)
    snippets = _collect_snippet_families(root)
    custom_indicators = _collect_custom_indicators(root)
    blocksettings = _collect_blocksettings(project_root)
    semantic_catalog = _build_semantic_catalog(wizard, conditions, examples)
    source_hash = hashlib.sha256(_json_dump({
        "parameterSets": parameter_sets.get("sourceHash"),
        "conditions": conditions.get("sourceHash"),
        "wizard": wizard.get("sourceHash"),
        "examples": examples.get("count"),
        "exampleFeatures": examples.get("featureHash"),
        "snippets": snippets.get("familyCount"),
        "customIndicators": custom_indicators.get("count"),
        "blockSettings": blocksettings.get("count"),
        "semanticCatalog": semantic_catalog.get("itemCount"),
    }).encode("utf-8", errors="replace")).hexdigest()[:16]
    catalog = {
        "type": CATALOG_TYPE,
        "version": AI_WIZARD_AI2_VERSION,
        "catalogId": _hash_id("catalog", source_hash),
        "sourceHash": source_hash,
        "generatedAt": _now_iso(),
        "scope": "algowizard_only",
        "accessPolicy": "read_only_allowlist_sanitized",
        "hotSafe": hot_safe,
        "counts": {
            "conditionItems": conditions.get("count", 0),
            "wizardBlocks": wizard.get("blockCount", 0),
            "wizardComparisons": wizard.get("comparisonCount", 0),
            "parameterSets": parameter_sets.get("count", 0),
            "parameterCount": parameter_sets.get("paramCount", 0),
            "examples": examples.get("count", 0),
            "exampleFeatureIds": examples.get("featureCount", 0),
            "snippetFamilies": snippets.get("familyCount", 0),
            "customIndicators": custom_indicators.get("count", 0),
            "blockSettings": blocksettings.get("count", 0),
            "semanticItems": semantic_catalog.get("itemCount", 0),
            "semanticFamilies": semantic_catalog.get("familyCount", 0),
            "semanticAliases": semantic_catalog.get("aliasCount", 0),
        },
        "conditions": conditions,
        "wizard": wizard,
        "parameterSets": parameter_sets,
        "examples": examples,
        "semanticCatalog": semantic_catalog,
        "snippetFamilies": snippets,
        "customIndicators": custom_indicators,
        "blockSettings": blocksettings,
        "compilerSupport": {
            "draftablePatterns": ["ema_cross", "candle_atr_sequence", "rsi_mean_reversion"],
            "blockedFallback": "blocked_not_draftable_yet",
            "manualReviewRequired": True,
            "phase": AI_WIZARD_AI4_RSI_COMPILER_VERSION,
            "universalPromptIntake": True,
            "universalSqxGeneration": False,
        },
    }
    if persist:
        with _connect_ai2_db(project_root, db_path) as con:
            con.execute(
                "INSERT OR REPLACE INTO catalog_snapshots(catalog_id, source_hash, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (catalog["catalogId"], source_hash, _json_dump(catalog), catalog["generatedAt"]),
            )
            con.execute(
                "INSERT INTO audit_events(audit_id, event_type, details_json, created_at) VALUES (?, ?, ?, ?)",
                (_safe_id("audit"), "catalog_refresh", _json_dump({"catalogId": catalog["catalogId"], "sourceHash": source_hash}), _now_iso()),
            )
    return _base_response_v2({"catalog": catalog}, warnings=warnings)


def _catalog_key_sets(catalog: dict[str, Any]) -> dict[str, set[str]]:
    data = catalog.get("data", {}).get("catalog", catalog)
    wizard = data.get("wizard") if isinstance(data.get("wizard"), dict) else {}
    conditions = data.get("conditions") if isinstance(data.get("conditions"), dict) else {}
    semantic = data.get("semanticCatalog") if isinstance(data.get("semanticCatalog"), dict) else {}
    examples = data.get("examples") if isinstance(data.get("examples"), dict) else {}
    return {
        "blocks": {str(item.get("id")) for item in wizard.get("blocks", []) if isinstance(item, dict) and item.get("id")},
        "comparisons": {str(item.get("id")) for item in wizard.get("comparisons", []) if isinstance(item, dict) and item.get("id")},
        "conditions": {str(item.get("id")) for item in conditions.get("items", []) if isinstance(item, dict) and item.get("id")},
        "semantic": {str(item.get("id")) for item in semantic.get("items", []) if isinstance(item, dict) and item.get("id")},
        "exampleFeatures": {str(item) for item in examples.get("featureIds", []) if item},
    }


def _value_node(kind: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"kind": "value", "blockId": kind, "params": params or {}}


def _condition_node(comparison: str, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "comparison", "operatorId": comparison, "left": left, "right": right}


def _catalog_has_atr_support(catalog: dict[str, Any]) -> bool:
    keys = _catalog_key_sets(catalog)
    if "ATR" in keys["blocks"] or "talib_ATR" in keys["blocks"] or "talib_ATR" in keys["exampleFeatures"]:
        return True
    if "ATR" in keys["conditions"] or "talib_ATR" in keys["conditions"] or "ATR" in keys["semantic"]:
        return True
    return False


def _xml_param(key: str, name: str, value: Any, **attrs: Any) -> ET.Element:
    param = ET.Element("Param", {"key": key, "name": name, **{k: str(v) for k, v in attrs.items() if v is not None}})
    param.text = str(value)
    return param


def _xml_block(child: ET.Element, key: str | None = None) -> ET.Element:
    attrs = {"key": key} if key else {}
    block = ET.Element("Block", attrs)
    block.append(child)
    return block


def _xml_price_value(block_id: str, shift: int) -> ET.Element:
    item = ET.Element(
        "Item",
        {
            "key": block_id,
            "name": f"({block_id[0]}) {block_id}",
            "display": f"{block_id}[#Shift#]",
            "mI": "Price",
            "returnType": "price",
            "categoryType": "priceValue",
        },
    )
    item.append(_xml_param("#Chart#", "Chart", 0, type="data", controlType="dataVar", defaultValue="0"))
    item.append(_xml_param("#Shift#", "Shift", shift, type="int", defaultValue="1", controlType="jspinnerVar", minValue="0", maxValue="1000", step="1", builderStep="1"))
    return item


def _xml_number_value(value: int | float) -> ET.Element:
    item = ET.Element("Item", {"key": "Number", "name": "(NUM) Number", "display": "#Number#", "mI": "Other", "returnType": "number", "categoryType": "other", "notFirstValue": "true"})
    item.append(_xml_param("#Number#", "Number", value, type="double", defaultValue="0", controlType="jspinner", minValue="-999999999", maxValue="999999999", step="1", builderStep="1", variable="false"))
    return item


def _xml_atr_value(period: int = 14, shift: int = 1) -> ET.Element:
    item = ET.Element(
        "Item",
        {
            "key": "talib_ATR",
            "name": "(ATR) Average True Range",
            "display": "ATR(@Chart@#TimePeriod#)[#Shift#]",
            "returnType": "pricerange",
            "categoryType": "indicator",
        },
    )
    item.append(_xml_param("#Chart#", "Chart", 0, type="data", controlType="dataVar", defaultValue="0"))
    item.append(_xml_param("#TimePeriod#", "Time Period", period, type="int", controlType="jspinnerVar", defaultValue="14", step="1", builderStep="1", minValue="2", maxValue="10000", builderMinValue="1", builderMaxValue="200", builderStepValue="1", paramType="period"))
    item.append(_xml_param("#Shift#", "Shift", shift, type="int", defaultValue="1", controlType="jspinnerVar", minValue="0", maxValue="1000", step="1", builderStep="1"))
    return item


def _xml_rsi_value(period: int = 14, shift: int = 1) -> ET.Element:
    item = ET.Element(
        "Item",
        {
            "key": "RSI",
            "name": "(RSI) RSI",
            "display": "RSI(#Period#)[#Shift#]",
            "returnType": "number",
            "categoryType": "indicator",
        },
    )
    item.append(_xml_param("#Chart#", "Chart", 0, type="data", controlType="dataVar", defaultValue="0"))
    item.append(_xml_param("#Period#", "Period", period, type="int", controlType="jspinnerVar", defaultValue="14", step="1", builderStep="1", minValue="1", maxValue="10000", paramType="period"))
    item.append(_xml_param("#Shift#", "Shift", shift, type="int", defaultValue="1", controlType="jspinnerVar", minValue="0", maxValue="1000", step="1", builderStep="1"))
    return item


def _xml_comparison(operator_id: str, left: ET.Element, right: ET.Element) -> ET.Element:
    labels = {
        "IsGreater": ("(>) Is greater", "#Left# > #Right#"),
        "IsLower": ("(<) Is lower", "#Left# < #Right#"),
        "Equals": ("(=) Equals", "#Left# = #Right#"),
    }
    name, display = labels.get(operator_id, (operator_id, operator_id))
    item = ET.Element("Item", {"key": operator_id, "name": name, "display": display, "mI": "Comparisons", "returnType": "boolean", "categoryType": "operators"})
    item.append(_xml_block(left, "#Left#"))
    item.append(_xml_block(right, "#Right#"))
    return item


def _xml_and(conditions: list[ET.Element]) -> ET.Element:
    filtered = [condition for condition in conditions if condition is not None]
    if not filtered:
        return _xml_comparison("Equals", _xml_number_value(1), _xml_number_value(1))
    if len(filtered) == 1:
        return filtered[0]
    item = ET.Element("Item", {"key": "AND"})
    item.append(_xml_block(filtered[0]))
    item.append(_xml_block(_xml_and(filtered[1:])))
    return item


def _xml_red_candle(shift: int) -> ET.Element:
    return _xml_comparison("IsLower", _xml_price_value("Close", shift), _xml_price_value("Open", shift))


def _xml_green_candle(shift: int) -> ET.Element:
    return _xml_comparison("IsGreater", _xml_price_value("Close", shift), _xml_price_value("Open", shift))


def _xml_false_condition() -> ET.Element:
    return _xml_comparison("IsGreater", _xml_number_value(0), _xml_number_value(1))


def _parse_number_token(value: str) -> int | float:
    number = float(str(value).replace(",", "."))
    return int(number) if number.is_integer() else number


def _detect_named_count(text: str, fallback: int = 0) -> int:
    lowered = text.casefold()
    named = {
        "una": 1,
        "un": 1,
        "one": 1,
        "dos": 2,
        "two": 2,
        "tres": 3,
        "three": 3,
        "cuatro": 4,
        "four": 4,
        "cinco": 5,
        "five": 5,
    }
    if lowered.isdigit():
        return int(lowered)
    return named.get(lowered, fallback)


def _detect_pip_value(prompt: str, labels: tuple[str, ...]) -> int | float | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    patterns = [
        rf"\b(?:{label_pattern})\b\s*(?:de|=|:)?\s*(\d+(?:[\.,]\d+)?)\s*(?:pips?)?",
        rf"\b(\d+(?:[\.,]\d+)?)\s*(?:pips?)?\s*(?:de\s*)?(?:{label_pattern})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return _parse_number_token(match.group(1))
    return None


def _default_risk(prompt: str) -> dict[str, Any]:
    lowered = prompt.casefold()
    sl = _detect_pip_value(prompt, ("sl", "stop loss", "stop"))
    tp = _detect_pip_value(prompt, ("tp", "take profit", "profit target", "objetivo"))
    if sl is None:
        sl = 50 if any(token in lowered for token in ("sl", "stop", "stop loss")) else 0
    if tp is None:
        tp = 70 if any(token in lowered for token in ("tp", "take profit", "profit target", "objetivo")) else 0
    return {
        "stopLossPips": sl,
        "takeProfitPips": tp,
        "trailing": "none",
        "moneyManagement": {"type": "FixedSize", "size": 0.1},
        "manualReviewRequired": True,
    }


def _detect_candle_pattern(prompt: str) -> dict[str, Any] | None:
    lowered = prompt.casefold()
    if not any(token in lowered for token in ("vela", "velas", "candle", "candles", "martillo", "hammer")):
        return None
    red_count = 0
    red_match = re.search(r"\b(\d+|una|un|one|dos|two|tres|three|cuatro|four|cinco|five)\s+(?:velas?|candles?)\s+(?:rojas?|red)\b", lowered)
    if red_match:
        red_count = _detect_named_count(red_match.group(1), 0)
    green_count = 0
    green_match = re.search(r"\b(\d+|una|un|one|dos|two|tres|three|cuatro|four|cinco|five)\s+(?:velas?|candles?)\s+(?:verdes?|green)\b", lowered)
    if green_match:
        green_count = _detect_named_count(green_match.group(1), 0)
    has_hammer = "martillo" in lowered or "hammer" in lowered
    entry_timing = "manual_review"
    if "segunda vela verde" in lowered or "second green" in lowered:
        entry_timing = "market_on_second_green_after_confirmation"
    elif "siguiente verde" in lowered or "next green" in lowered:
        entry_timing = "market_after_next_green_confirmation"
    return {
        "type": "candlestick_sequence",
        "label": "Secuencia de velas con confirmacion martillo",
        "redCandles": red_count,
        "greenCandlesMentioned": green_count,
        "requiresHammer": has_hammer,
        "entryTiming": entry_timing,
        "compilerSupport": "blocked_unsupported_candle_pattern",
        "manualReviewRequired": True,
    }


def _detect_ai2_filters(prompt: str, catalog: dict[str, Any]) -> list[dict[str, Any]]:
    lowered = prompt.casefold()
    keys = _catalog_key_sets(catalog)
    atr_supported = "ATR" in keys["blocks"] or _catalog_has_atr_support(catalog)
    filters: list[dict[str, Any]] = []
    if re.search(r"\batr\b", lowered):
        filters.append({
            "type": "volatility_filter",
            "blockId": "ATR",
            "availableInCatalog": atr_supported,
            "compilerSupport": "compiled_as_atr_rising" if atr_supported else "manual_review_only",
            "manualReviewRequired": True,
        })
    return filters


def _keyword_matches_prompt(prompt_lower: str, token: str) -> bool:
    token_lower = str(token or "").strip().casefold()
    if not token_lower:
        return False
    if re.fullmatch(r"[a-z0-9]+", token_lower):
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(token_lower)}(?![a-z0-9])", prompt_lower))
    return token_lower in prompt_lower


def _detect_ai2_blocks(prompt: str, model_interpretation: dict[str, Any] | None = None) -> list[str]:
    lowered = prompt.casefold()
    ordered = [
        ("EMA", ("ema", "exponential moving average", "media exponencial")),
        ("SMA", ("sma", "moving average", "media movil", "media móvil")),
        ("RSI", ("rsi", "relative strength")),
        ("BollingerBands", ("bollinger", "bbands", "bb ")),
        ("Stochastic", ("stochastic", "estocastico", "estocástico")),
        ("MACD", ("macd",)),
        ("CCI", ("cci", "commodity channel")),
        ("ADX", ("adx",)),
    ]
    blocks: list[str] = []
    for block_id, tokens in ordered:
        if any(_keyword_matches_prompt(lowered, token) for token in tokens):
            blocks.append(block_id)
    if model_interpretation and model_interpretation.get("source") == "ollama_ast":
        model_blocks = _normalize_hint_list(model_interpretation.get("blocks"))
        known_aliases = {"ATR": "ATR", "TALIB_ATR": "ATR", "CANDLE": "Close", "PRICE": "Close"}
        for item in model_blocks:
            candidate = known_aliases.get(item.upper(), item)
            if candidate in {"EMA", "SMA", "RSI", "BollingerBands", "Stochastic", "MACD", "CCI", "ADX", "High", "Low", "Close", "Open", "Number", "ATR"} and candidate not in blocks:
                blocks.append(candidate)
    if not blocks and _detect_archetype(prompt) == "breakout":
        blocks.extend(["High", "Low"])
    if _detect_candle_pattern(prompt) and "Close" not in blocks:
        blocks.append("Close")
    return blocks


def _semantic_alias_score(prompt_lower: str, alias: str, *, weight: int = 1) -> int:
    text = str(alias or "").strip().casefold()
    if len(text) < 3:
        return 0
    words = [
        word
        for word in _split_catalog_words(text)
        if len(word) >= 3 and word.casefold() not in {"and", "bar", "con", "del", "is", "level", "the", "with"}
    ]
    if re.fullmatch(r"[a-z0-9+-]{2,}", text):
        generic = {
            "above", "band", "below", "change", "changes", "closes", "cross", "crosses", "direction",
            "falling", "higher", "level", "lower", "opens", "rising", "upper", "value",
        }
        if text in generic:
            return 0
        return weight if re.search(rf"(?<![a-z0-9]){re.escape(text)}(?![a-z0-9])", prompt_lower) else 0
    if len(words) >= 2 and all(re.search(rf"(?<![a-z0-9]){re.escape(word.casefold())}(?![a-z0-9])", prompt_lower) for word in words):
        return weight
    return weight if text in prompt_lower else 0


def _semantic_alias_matches(prompt_lower: str, alias: str) -> bool:
    return _semantic_alias_score(prompt_lower, alias) > 0


def _detect_semantic_family_mentions(prompt: str, catalog: dict[str, Any]) -> list[str]:
    prompt_lower = prompt.casefold()
    families: list[str] = []
    for item in _catalog_semantic_items(catalog):
        category = str(item.get("category") or "")
        if category and _semantic_alias_score(prompt_lower, category, weight=1) > 0:
            families.append(category)
    return list(dict.fromkeys(families))


def _detect_semantic_refs(
    prompt: str,
    catalog: dict[str, Any],
    model_interpretation: dict[str, Any] | None = None,
) -> list[str]:
    prompt_lower = prompt.casefold()
    model_terms = {
        item.casefold()
        for item in (
            _normalize_hint_list(model_interpretation.get("blocks")) + _normalize_hint_list(model_interpretation.get("filters"))
            if isinstance(model_interpretation, dict)
            else []
        )
    }
    refs: list[str] = []
    scored_refs: list[tuple[int, str]] = []
    semantic_items = _catalog_semantic_items(catalog)
    mentioned_categories = set(_detect_semantic_family_mentions(prompt, catalog))
    for item in semantic_items:
        item_id = str(item.get("id") or "")
        if not item_id:
            continue
        category = str(item.get("category") or "")
        if (
            mentioned_categories
            and category
            and category not in mentioned_categories
            and str(item.get("kind") or "") == "condition_item"
        ):
            continue
        category_aliases = {alias.casefold() for alias in _catalog_aliases(category, limit=8)}
        score = 0
        item_score = 0
        aliases = [str(alias) for alias in item.get("aliases", []) if alias and str(alias).casefold() not in category_aliases]
        category_score = _semantic_alias_score(prompt_lower, category, weight=4)
        score += _semantic_alias_score(prompt_lower, item_id, weight=5)
        score += _semantic_alias_score(prompt_lower, str(item.get("label") or ""), weight=3)
        for alias in aliases:
            score += _semantic_alias_score(prompt_lower, alias, weight=1)
        item_score = score
        score += category_score if item_score else 0
        matched_model = any(term and any(term == alias.casefold() for alias in aliases) for term in model_terms)
        if matched_model:
            score += 5
        if item_score >= 3 or (matched_model and score >= 5):
            scored_refs.append((score, item_id))
    for _, item_id in sorted(scored_refs, key=lambda pair: (-pair[0], pair[1])):
        refs.append(item_id)
        if len(refs) >= 24:
            break
    return list(dict.fromkeys(refs))


def _risk_from_prompt_and_model(prompt: str, model_interpretation: dict[str, Any] | None = None) -> dict[str, Any]:
    risk = _default_risk(prompt)
    model_risk = model_interpretation.get("risk") if isinstance(model_interpretation, dict) and isinstance(model_interpretation.get("risk"), dict) else {}
    for key in ("stopLossPips", "takeProfitPips"):
        if risk.get(key) in {0, None} and model_risk.get(key) is not None:
            risk[key] = _parse_number_token(str(model_risk.get(key)))
    return risk


def _candle_pattern_from_prompt_and_model(prompt: str, model_interpretation: dict[str, Any] | None = None) -> dict[str, Any] | None:
    pattern = _detect_candle_pattern(prompt)
    model_pattern = model_interpretation.get("candlePattern") if isinstance(model_interpretation, dict) and isinstance(model_interpretation.get("candlePattern"), dict) else {}
    if not pattern and str(model_pattern.get("type") or "").casefold() in {"candlestick_sequence", "candle_sequence"}:
        pattern = {
            "type": "candlestick_sequence",
            "label": "Secuencia de velas con confirmacion martillo",
            "redCandles": _safe_int(model_pattern.get("redCandles"), 0),
            "greenCandlesMentioned": _safe_int(model_pattern.get("greenCandles"), 0),
            "requiresHammer": bool(model_pattern.get("requiresHammer")),
            "entryTiming": str(model_pattern.get("entryTiming") or "manual_review")[:80],
            "compilerSupport": "blocked_unsupported_candle_pattern",
            "manualReviewRequired": True,
        }
    elif pattern and model_pattern:
        if not pattern.get("redCandles") and model_pattern.get("redCandles") is not None:
            pattern["redCandles"] = _safe_int(model_pattern.get("redCandles"), 0)
        if not pattern.get("greenCandlesMentioned") and model_pattern.get("greenCandles") is not None:
            pattern["greenCandlesMentioned"] = _safe_int(model_pattern.get("greenCandles"), 0)
        if model_pattern.get("requiresHammer"):
            pattern["requiresHammer"] = True
    return pattern


def _ast_from_prompt(prompt: str, catalog: dict[str, Any], model_interpretation: dict[str, Any] | None = None) -> dict[str, Any]:
    model_interpretation = model_interpretation or {"source": "heuristic"}
    model_asset = str(model_interpretation.get("asset") or "").upper()
    model_timeframe = str(model_interpretation.get("timeframe") or "").upper()
    model_direction = str(model_interpretation.get("direction") or "")
    asset = ASSET_ALIASES.get(model_asset, model_asset) if model_asset in SUPPORTED_ASSETS or model_asset in ASSET_ALIASES else _detect_asset(prompt)
    timeframe = model_timeframe if model_timeframe in SUPPORTED_TIMEFRAMES else _detect_timeframe(prompt)
    direction = model_direction if model_direction in {"long_only", "short_only", "both"} else _detect_direction(prompt)
    blocks = _detect_ai2_blocks(prompt, model_interpretation)
    candle_pattern = _candle_pattern_from_prompt_and_model(prompt, model_interpretation)
    filters = _detect_ai2_filters(prompt, catalog)
    semantic_refs = _detect_semantic_refs(prompt, catalog, model_interpretation)
    semantic_families = _detect_semantic_family_mentions(prompt, catalog)
    if model_interpretation.get("source") == "ollama_ast":
        model_filters = {item.casefold() for item in _normalize_hint_list(model_interpretation.get("filters"))}
        if "atr" in model_filters and not any(item.get("blockId") == "ATR" for item in filters):
            filters.extend(_detect_ai2_filters("ATR", catalog))
    for item in filters:
        block_id = str(item.get("blockId") or "")
        if item.get("availableInCatalog") and block_id and block_id not in blocks:
            blocks.append(block_id)
    conditions_long: list[dict[str, Any]] = []
    conditions_short: list[dict[str, Any]] = []
    if "EMA" in blocks and ("cross" in prompt.casefold() or "cruce" in prompt.casefold() or len(blocks) == 1):
        fast = _value_node("EMA", {"Period": 14, "Shift": 1, "ComputedFrom": "Close"})
        slow = _value_node("EMA", {"Period": 50, "Shift": 1, "ComputedFrom": "Close"})
        conditions_long.append(_condition_node("CrossesAbove", fast, slow))
        conditions_short.append(_condition_node("CrossesBelow", fast, slow))
    if "RSI" in blocks:
        rsi = _value_node("RSI", {"Period": 14, "Shift": 1})
        conditions_long.append(_condition_node("IsLower", rsi, _value_node("Number", {"Number": 30})))
        conditions_short.append(_condition_node("IsGreater", rsi, _value_node("Number", {"Number": 70})))
    if "BollingerBands" in blocks:
        close = _value_node("Close", {"Shift": 1})
        lower = _value_node("BollingerBands", {"Period": 20, "Deviation": 2, "Line": "Lower", "Shift": 1})
        upper = _value_node("BollingerBands", {"Period": 20, "Deviation": 2, "Line": "Upper", "Shift": 1})
        conditions_long.append(_condition_node("IsLower", close, lower))
        conditions_short.append(_condition_node("IsGreater", close, upper))
    if "Stochastic" in blocks:
        stoch = _value_node("Stochastic", {"KPeriod": 9, "DPeriod": 3, "Slowing": 3, "Mode": "SlowD", "Shift": 1})
        conditions_long.append(_condition_node("IsLower", stoch, _value_node("Number", {"Number": 20})))
        conditions_short.append(_condition_node("IsGreater", stoch, _value_node("Number", {"Number": 80})))
    if "MACD" in blocks:
        macd = _value_node("MACD", {"Fast": 12, "Slow": 26, "Smooth": 9, "Output": "Main", "Shift": 1})
        zero = _value_node("Number", {"Number": 0})
        conditions_long.append(_condition_node("CrossesAbove", macd, zero))
        conditions_short.append(_condition_node("CrossesBelow", macd, zero))
    if "CCI" in blocks:
        cci = _value_node("CCI", {"Period": 14, "Shift": 1})
        conditions_long.append(_condition_node("IsLower", cci, _value_node("Number", {"Number": -100})))
        conditions_short.append(_condition_node("IsGreater", cci, _value_node("Number", {"Number": 100})))
    if "ADX" in blocks:
        adx = _value_node("ADX", {"Period": 14, "Shift": 1})
        conditions_long.append(_condition_node("IsGreater", adx, _value_node("Number", {"Number": 20})))
        conditions_short.append(_condition_node("IsGreater", adx, _value_node("Number", {"Number": 20})))
    if "High" in blocks or "Low" in blocks:
        close = _value_node("Close", {"Shift": 1})
        conditions_long.append(_condition_node("IsGreater", close, _value_node("High", {"Shift": 2})))
        conditions_short.append(_condition_node("IsLower", close, _value_node("Low", {"Shift": 2})))
    block_set = set(blocks)
    compiler_known_blocks = {"EMA", "RSI", "BollingerBands", "Stochastic", "MACD", "CCI", "ADX", "ATR", "High", "Low", "Close", "Open", "Number"}
    semantic_family_refs = {
        item_id
        for item_id in semantic_refs
        if item_id and item_id not in block_set and not item_id.startswith("RSI")
    }
    non_rsi_semantic_families = {
        family for family in semantic_families if family.casefold() not in {"relative strength index", "rsi"}
    }
    rsi_multi_family = bool("RSI" in block_set and ((block_set & (compiler_known_blocks - {"RSI"})) or semantic_family_refs or non_rsi_semantic_families))
    candle_compilable = bool(
        candle_pattern
        and candle_pattern.get("type") == "candlestick_sequence"
        and direction in {"long_only", "both"}
        and all(item in _catalog_key_sets(catalog)["blocks"] for item in ("Open", "Close", "High", "Low", "Number"))
        and all(item.get("availableInCatalog", True) for item in filters)
    )
    ema_draftable = len(set(blocks)) == 1 and blocks[0] == "EMA" and bool(conditions_long)
    rsi_draftable = "RSI" in block_set and not rsi_multi_family and not candle_pattern and not filters and bool(conditions_long or conditions_short)
    draftable = bool(ema_draftable or candle_compilable or rsi_draftable)
    compiler_blockers: list[str] = []
    if candle_pattern and not candle_compilable:
        compiler_blockers.append("blocked_unsupported_candle_pattern")
    if rsi_multi_family:
        compiler_blockers.append("blocked_multi_family_compiler_not_ready")
    if filters and not candle_compilable and not ema_draftable and not rsi_draftable:
        compiler_blockers.append("blocked_unsupported_filter")
    if not draftable:
        compiler_blockers.append("blocked_not_draftable_yet")
    understood = bool(blocks or candle_pattern or filters or semantic_refs or semantic_families or conditions_long or conditions_short)
    name_tokens: list[str] = []
    if candle_pattern:
        name_tokens.append("CandlePattern")
    name_tokens.extend(str(item.get("blockId")) for item in filters if item.get("blockId"))
    name_tokens.extend(blocks[:4])
    name_suffix = "_".join(dict.fromkeys(token for token in name_tokens if token)) or "custom_aw"
    return {
        "type": AST_TYPE,
        "version": AI_WIZARD_AI2_VERSION,
        "status": "draftable_candidate" if draftable else ("plan_only" if understood else "blocked"),
        "asset": asset,
        "timeframe": timeframe,
        "direction": direction,
        "strategyName": _safe_file_stem(f"SQXEdgeAI2_{asset}_{timeframe}_{name_suffix}"),
        "scope": "algowizard_only",
        "promptUnderstanding": {
            "recognized": understood,
            "unsupportedNaturalLanguageFallback": False,
            "manualReviewRequired": True,
        },
        "interpreter": {
            "phase": AI_WIZARD_AI3_COMPILER_VERSION,
            "source": str(model_interpretation.get("source") or "heuristic")[:80],
            "model": str(model_interpretation.get("model") or "")[:80],
            "confidence": max(0.0, min(_safe_float(model_interpretation.get("confidence"), 0.0), 1.0)),
            "rawPromptPersisted": False,
            "rawResponsePersisted": False,
            "externalApiCalled": False,
        },
        "recognized": {
            "pattern": candle_pattern,
            "filters": filters,
        },
        "rules": {
            "longEntry": {"logic": "AND", "conditions": conditions_long},
            "shortEntry": {"logic": "AND", "conditions": conditions_short if direction != "long_only" else []},
            "longExit": {"logic": "manual_review", "conditions": []},
            "shortExit": {"logic": "manual_review", "conditions": []},
        },
        "actions": {
            "entry": {"orderType": "EnterAtMarket", "allowDuplicateTrades": False},
            "risk": _risk_from_prompt_and_model(prompt, model_interpretation),
        },
        "catalogRefs": {
            "blockIds": [block_id for block_id in blocks if block_id in _catalog_key_sets(catalog)["blocks"]],
            "semanticIds": [item_id for item_id in semantic_refs if item_id in _catalog_key_sets(catalog)["semantic"]],
            "semanticFamilies": semantic_families[:12],
            "comparisonIds": sorted({cond["operatorId"] for cond in conditions_long + conditions_short}),
        },
        "compiler": {
            "draftable": draftable,
            "templateClass": "candle_atr_sequence" if candle_compilable else ("rsi_mean_reversion" if rsi_draftable else ("ema_cross" if ema_draftable else "")),
            "version": AI_WIZARD_AI4_RSI_COMPILER_VERSION if rsi_draftable else AI_WIZARD_AI3_COMPILER_VERSION,
            "universalPromptIntake": True,
            "universalSqxGeneration": False,
            "blockers": list(dict.fromkeys(compiler_blockers)),
        },
    }


def validate_ai_wizard_ast(ast: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    keys = _catalog_key_sets(catalog)
    if not isinstance(ast, dict) or ast.get("type") != AST_TYPE:
        blockers.append("ast_type_invalid")
    if ast.get("scope") != "algowizard_only":
        blockers.append("scope_not_algowizard")
    prompt_understanding = ast.get("promptUnderstanding") if isinstance(ast.get("promptUnderstanding"), dict) else {}
    if prompt_understanding.get("recognized") is False:
        blockers.append("prompt_not_understood")
    catalog_refs = ast.get("catalogRefs") if isinstance(ast.get("catalogRefs"), dict) else {}
    for block_id in catalog_refs.get("blockIds", []):
        if block_id not in keys["blocks"]:
            blockers.append(f"unknown_block:{block_id}")
    for semantic_id in catalog_refs.get("semanticIds", []):
        if semantic_id not in keys["semantic"]:
            blockers.append(f"unknown_semantic_item:{semantic_id}")
    for comparison_id in catalog_refs.get("comparisonIds", []):
        if comparison_id not in keys["comparisons"] and comparison_id not in keys["conditions"]:
            blockers.append(f"unknown_comparison:{comparison_id}")
    risk = ast.get("actions", {}).get("risk", {}) if isinstance(ast.get("actions"), dict) else {}
    for key in ("stopLossPips", "takeProfitPips"):
        value = risk.get(key, 0)
        if not isinstance(value, (int, float)) or value < 0 or value > 100000:
            blockers.append(f"risk_param_out_of_range:{key}")
    compiler = ast.get("compiler", {}) if isinstance(ast.get("compiler"), dict) else {}
    if not compiler.get("draftable"):
        warnings.extend(str(item) for item in compiler.get("blockers", []) if item)
        warnings.append("blocked_not_draftable_yet")
    warnings = list(dict.fromkeys(warnings))
    return {
        "ok": not blockers,
        "status": "valid" if not blockers else "blocked",
        "blockers": blockers,
        "warnings": warnings,
        "manualReviewRequired": True,
        "privacy": _privacy(),
    }


def build_ai_wizard_ast_from_prompt(
    payload: dict[str, Any] | None,
    *,
    project_root: Path,
    sqx142_root: Path | None = None,
    llm_client: Any | None = None,
) -> dict[str, Any]:
    payload = payload or {}
    prompt = _clean_text(payload.get("prompt") or payload.get("message") or payload.get("idea"))
    if not prompt:
        return _base_response_v2(ok=False, error="prompt_required", blockers=["prompt_required"])
    if _contains_private_or_path_text(prompt):
        return _base_response_v2(ok=False, error="prompt_not_public_safe", blockers=["private_or_forbidden_text_detected"])
    if any(term in prompt.casefold() for term in ("full editor", "custom java", "java snippet", "engine plugin")):
        return _base_response_v2(ok=False, error="blocked_full_editor_scope", blockers=["blocked_full_editor_scope"])
    catalog_report = build_ai_wizard_capability_catalog(project_root, sqx142_root)
    catalog = catalog_report["data"]["catalog"]
    model_interpretation = _try_local_model_interpretation(prompt, catalog, payload, llm_client)
    ast = _ast_from_prompt(prompt, catalog, model_interpretation)
    validation = validate_ai_wizard_ast(ast, catalog)
    return _base_response_v2({
        "status": "ready" if validation["ok"] else "blocked",
        "ast": ast,
        "validation": validation,
        "catalogSummary": catalog.get("counts", {}),
        "compiler": {
            "phase": AI_WIZARD_AI3_COMPILER_VERSION,
            "interpreterSource": ast.get("interpreter", {}).get("source"),
            "model": ast.get("interpreter", {}).get("model"),
            "universalPromptIntake": True,
            "universalSqxGeneration": False,
        },
        "nextStep": "Edit structured parameters or generate a draft if compiler support is available.",
    }, ok=validation["ok"], blockers=validation["blockers"], warnings=validation["warnings"])


def _session_public(row: sqlite3.Row) -> dict[str, Any]:
    ast = _json_load(row["ast_json"], {})
    validation = _json_load(row["validation_json"], {})
    return {
        "sessionId": row["session_id"],
        "title": row["title"],
        "status": row["status"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "promptHash": row["prompt_hash"],
        "promptSummary": row["prompt_summary"],
        "ast": ast,
        "validation": validation,
    }


def list_ai_wizard_sessions(project_root: Path, *, db_path: Path | None = None, limit: int = 20) -> dict[str, Any]:
    with _connect_ai2_db(project_root, db_path) as con:
        rows = con.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (max(1, min(int(limit or 20), 100)),),
        ).fetchall()
    return _base_response_v2({"sessions": [_session_public(row) for row in rows], "storage": "local_sqlite_redacted"})


def create_ai_wizard_session(project_root: Path, payload: dict[str, Any] | None = None, *, db_path: Path | None = None) -> dict[str, Any]:
    payload = payload or {}
    prompt = _clean_text(payload.get("prompt") or payload.get("message") or payload.get("idea"))
    title_idea = _clean_text(payload.get("title") or "")
    idea_text = prompt or title_idea
    ast_report = build_ai_wizard_ast_from_prompt({"prompt": idea_text}, project_root=project_root)
    if not ast_report.get("ok") and ast_report.get("error") in {"prompt_not_public_safe", "blocked_full_editor_scope"}:
        return ast_report
    ast = ast_report.get("data", {}).get("ast", {})
    validation = ast_report.get("data", {}).get("validation", {"ok": False, "blockers": ["prompt_required"]})
    session_id = _safe_id("aws")
    now = _now_iso()
    prompt_hash = _hash_id("prompt", prompt) if prompt else ""
    summary = _redacted_prompt_summary(idea_text) if idea_text else ""
    title = summary or "AI Wizard session"
    with _connect_ai2_db(project_root, db_path) as con:
        con.execute(
            "INSERT INTO sessions(session_id, title, status, created_at, updated_at, prompt_hash, prompt_summary, ast_json, validation_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, title, "active", now, now, prompt_hash, summary, _json_dump(ast), _json_dump(validation)),
        )
        if prompt:
            con.execute(
                "INSERT INTO interactions(interaction_id, session_id, role, prompt_hash, summary, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (_safe_id("msg"), session_id, "operator", prompt_hash, summary, now),
            )
        con.execute(
            "INSERT INTO spec_revisions(revision_id, session_id, ast_json, validation_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (_safe_id("rev"), session_id, _json_dump(ast), _json_dump(validation), now),
        )
        row = con.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    return _base_response_v2({"session": _session_public(row), "created": True}, ok=bool(ast_report.get("ok")), blockers=ast_report.get("blockers", []), warnings=ast_report.get("warnings", []), error=ast_report.get("error", ""))


def get_ai_wizard_session(project_root: Path, session_id: str, *, db_path: Path | None = None) -> dict[str, Any]:
    with _connect_ai2_db(project_root, db_path) as con:
        row = con.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return _base_response_v2(ok=False, error="session_not_found", blockers=["session_not_found"])
        interactions = con.execute(
            "SELECT role, prompt_hash, summary, created_at FROM interactions WHERE session_id = ? ORDER BY created_at ASC LIMIT 80",
            (session_id,),
        ).fetchall()
        revisions = con.execute(
            "SELECT revision_id, created_at, validation_json FROM spec_revisions WHERE session_id = ? ORDER BY created_at DESC LIMIT 20",
            (session_id,),
        ).fetchall()
        drafts = con.execute(
            "SELECT draft_id, file_name, file_hash, created_at FROM drafts WHERE session_id = ? ORDER BY created_at DESC LIMIT 20",
            (session_id,),
        ).fetchall()
    return _base_response_v2({
        "session": _session_public(row),
        "interactions": [dict(item) for item in interactions],
        "revisions": [{"revisionId": item["revision_id"], "createdAt": item["created_at"], "validation": _json_load(item["validation_json"], {})} for item in revisions],
        "drafts": [{"draftId": item["draft_id"], "fileName": item["file_name"], "fileHash": item["file_hash"], "createdAt": item["created_at"]} for item in drafts],
    })


def add_ai_wizard_message(project_root: Path, session_id: str, payload: dict[str, Any] | None = None, *, db_path: Path | None = None) -> dict[str, Any]:
    payload = payload or {}
    prompt = _clean_text(payload.get("prompt") or payload.get("message") or payload.get("idea"))
    if not prompt:
        return _base_response_v2(ok=False, error="prompt_required", blockers=["prompt_required"])
    ast_report = build_ai_wizard_ast_from_prompt({"prompt": prompt}, project_root=project_root)
    if not ast_report.get("ok") and ast_report.get("error") in {"prompt_not_public_safe", "blocked_full_editor_scope"}:
        return ast_report
    ast = ast_report.get("data", {}).get("ast", {})
    validation = ast_report.get("data", {}).get("validation", {})
    now = _now_iso()
    prompt_hash = _hash_id("prompt", prompt)
    summary = _redacted_prompt_summary(prompt)
    with _connect_ai2_db(project_root, db_path) as con:
        row = con.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return _base_response_v2(ok=False, error="session_not_found", blockers=["session_not_found"])
        con.execute(
            "INSERT INTO interactions(interaction_id, session_id, role, prompt_hash, summary, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (_safe_id("msg"), session_id, "operator", prompt_hash, summary, now),
        )
        con.execute(
            "INSERT INTO spec_revisions(revision_id, session_id, ast_json, validation_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (_safe_id("rev"), session_id, _json_dump(ast), _json_dump(validation), now),
        )
        con.execute(
            "UPDATE sessions SET updated_at = ?, prompt_hash = ?, prompt_summary = ?, ast_json = ?, validation_json = ? WHERE session_id = ?",
            (now, prompt_hash, summary, _json_dump(ast), _json_dump(validation), session_id),
        )
    return get_ai_wizard_session(project_root, session_id, db_path=db_path)


def patch_ai_wizard_session_spec(project_root: Path, session_id: str, payload: dict[str, Any] | None = None, *, db_path: Path | None = None) -> dict[str, Any]:
    payload = payload or {}
    ast = payload.get("ast") if isinstance(payload.get("ast"), dict) else payload.get("spec")
    if not isinstance(ast, dict):
        return _base_response_v2(ok=False, error="ast_required", blockers=["ast_required"])
    catalog = build_ai_wizard_capability_catalog(project_root)["data"]["catalog"]
    validation = validate_ai_wizard_ast(ast, catalog)
    now = _now_iso()
    with _connect_ai2_db(project_root, db_path) as con:
        row = con.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return _base_response_v2(ok=False, error="session_not_found", blockers=["session_not_found"])
        con.execute(
            "INSERT INTO spec_revisions(revision_id, session_id, ast_json, validation_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (_safe_id("rev"), session_id, _json_dump(ast), _json_dump(validation), now),
        )
        con.execute(
            "UPDATE sessions SET updated_at = ?, ast_json = ?, validation_json = ? WHERE session_id = ?",
            (now, _json_dump(ast), _json_dump(validation), session_id),
        )
    return get_ai_wizard_session(project_root, session_id, db_path=db_path)


def create_ai_wizard_session_draft(project_root: Path, session_id: str, *, db_path: Path | None = None) -> dict[str, Any]:
    with _connect_ai2_db(project_root, db_path) as con:
        row = con.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return _base_response_v2(ok=False, error="session_not_found", blockers=["session_not_found"])
        ast = _json_load(row["ast_json"], {})
        validation = _json_load(row["validation_json"], {})
    if not validation.get("ok"):
        return _base_response_v2({"validation": validation, "ast": ast}, ok=False, error="ast_invalid", blockers=validation.get("blockers", ["ast_invalid"]))
    compiler = ast.get("compiler", {}) if isinstance(ast.get("compiler"), dict) else {}
    if not compiler.get("draftable"):
        compiler_blockers = list(dict.fromkeys(str(item) for item in compiler.get("blockers", []) if item)) or ["blocked_not_draftable_yet"]
        return _base_response_v2(
            {"validation": validation, "ast": ast, "nextStep": "Use the structured plan now; draft compiler support for this block mix is not proven yet."},
            ok=False,
            error="blocked_not_draftable_yet",
            blockers=compiler_blockers,
            warnings=validation.get("warnings", []),
        )
    draft_report = generate_ai_wizard_draft_from_ast(ast, project_root=project_root)
    if not draft_report.get("ok"):
        return draft_report
    draft = draft_report["data"]["draft"]
    path = resolve_draft_download(project_root, draft["fileName"])
    file_hash = ""
    if path and path.is_file():
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    draft_id = _safe_id("awd")
    now = _now_iso()
    with _connect_ai2_db(project_root, db_path) as con:
        con.execute(
            "INSERT INTO drafts(draft_id, session_id, file_name, file_hash, ast_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (draft_id, session_id, draft["fileName"], file_hash, _json_dump(ast), now),
        )
    draft["draftId"] = draft_id
    draft["downloadUrl"] = f"/api/sqx142/ai-wizard/drafts/{draft_id}/download"
    draft["fileHash"] = file_hash
    return _base_response_v2({"draft": draft, "ast": ast, "validation": validation, "guardrails": draft_report["data"].get("guardrails", [])})


def resolve_ai_wizard_draft_download(project_root: Path, draft_id: str, *, db_path: Path | None = None) -> Path | None:
    with _connect_ai2_db(project_root, db_path) as con:
        row = con.execute("SELECT file_name FROM drafts WHERE draft_id = ?", (draft_id,)).fetchone()
    if not row:
        return None
    return resolve_draft_download(project_root, str(row["file_name"]))
