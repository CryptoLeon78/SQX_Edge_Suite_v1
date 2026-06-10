from __future__ import annotations

import hashlib
import json
import re
import secrets
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .agent.redaction import redact_text
from .blocksettings import (
    blocksetting_file,
    blocksetting_trace,
    entries_by_id,
    load_blocksettings_manifest,
    read_blocks_root,
    resolve_blocksetting_entry,
)
from .plan import Mining, normalize_direction
from .project_generator import DEFAULT_BROKER_POSTFIX, generate_project, resolve_costs


BS_AI_VERSION = "bs-ai-blocksettings-generator-v1"
BS_AI_RECIPE_TYPE = "sqx-edge.bs-ai-recipe-v1"
BS_AI_SESSION_TYPE = "sqx-edge.bs-ai-session-v1"
BS_AI_CANDIDATE_SCOPE = "local_candidate"
BS_AI_PROMOTION_STATE = "local_candidate"

TIMEFRAMES = {"M5", "M15", "M30", "H1", "H4", "D1"}
FAMILY_ALIASES = {
    "tendencia": "BS_Tendencia",
    "trend": "BS_Tendencia",
    "momentum": "BS_Momentum",
    "volatilidad": "BS_Volatilidad",
    "volatility": "BS_Volatilidad",
    "regimen": "BS_Regimen",
    "regime": "BS_Regimen",
    "volumen": "BS_Volumen",
    "volume": "BS_Volumen",
    "sr": "BS_SoporteResistencia",
    "soporte": "BS_SoporteResistencia",
    "resistencia": "BS_SoporteResistencia",
    "estadistico": "BS_Estadistico",
    "stat": "BS_Estadistico",
    "filtros": "BS_Filtros",
    "filters": "BS_Filtros",
}
CONCEPT_ALIASES = {
    "atr": ("atr", "average true range", "volatil"),
    "adx": ("adx", "trend strength"),
    "rsi": ("rsi", "relative strength"),
    "keltner": ("keltner",),
    "bollinger": ("bollinger",),
    "ema": ("ema", "exponential", "media exponencial"),
    "sma": ("sma", "simple moving"),
    "hull": ("hull",),
    "zscore": ("zscore", "z-score"),
    "percentrank": ("percentrank", "percent rank"),
    "volume": ("volume", "volumen"),
    "price": ("price", "prices.", "close", "high", "low", "open"),
}
PRIVATE_MARKERS = ("[REDACTED_EMAIL]", "[REDACTED_URL]", "[REDACTED_PATH]", "[REDACTED_SECRET]")
SAFE_TOKEN_RE = re.compile(r"[^A-Za-z0-9_]+")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _state_root(project_root: Path) -> Path:
    return Path(project_root) / ".local" / "blocksettings_ai"


def _sessions_dir(project_root: Path) -> Path:
    return _state_root(project_root) / "sessions"


def _candidates_dir(project_root: Path) -> Path:
    return _state_root(project_root) / "candidates"


def _ensure_state(project_root: Path) -> None:
    _sessions_dir(project_root).mkdir(parents=True, exist_ok=True)
    _candidates_dir(project_root).mkdir(parents=True, exist_ok=True)


def _safe_token(value: str | None, fallback: str) -> str:
    cleaned = SAFE_TOKEN_RE.sub("_", str(value or "").strip()).strip("_")
    return cleaned or fallback


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _is_public_safe_text(value: str) -> bool:
    redacted = redact_text(value)
    return not any(marker in redacted for marker in PRIVATE_MARKERS)


def _session_path(project_root: Path, session_id: str) -> Path:
    token = _safe_token(session_id, "")
    if not token.startswith("bsai_"):
        raise ValueError("invalid_bsai_session_id")
    return _sessions_dir(project_root) / f"{token}.json"


def _load_session(project_root: Path, session_id: str) -> dict[str, Any]:
    path = _session_path(project_root, session_id)
    if not path.is_file():
        raise FileNotFoundError("bsai_session_not_found")
    return json.loads(path.read_text(encoding="utf-8"))


def _save_session(project_root: Path, session: dict[str, Any]) -> None:
    _ensure_state(project_root)
    session["updatedAt"] = _utc_now()
    _session_path(project_root, str(session["sessionId"])).write_text(
        json.dumps(session, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _public_entry(entry: dict[str, Any]) -> dict[str, Any]:
    clean = dict(entry)
    clean.pop("localPath", None)
    clean.pop("candidateRoot", None)
    return clean


def _official_ids_and_files() -> tuple[set[str], set[str]]:
    entries = entries_by_id().values()
    return {str(entry.get("canonicalId")) for entry in entries}, {str(entry.get("filename")) for entry in entries}


def _extract_timeframe(text: str, payload: dict[str, Any]) -> str:
    raw = payload.get("timeframe") or payload.get("tf")
    if raw:
        tf = str(raw).strip().upper()
        if tf in TIMEFRAMES:
            return tf
    match = re.search(r"\b(M5|M15|M30|H1|H4|D1)\b", text.upper())
    return match.group(1) if match else "H1"


def _extract_asset(text: str, payload: dict[str, Any]) -> str:
    raw = payload.get("asset") or payload.get("symbol")
    if raw:
        return _safe_token(str(raw).upper(), "EURUSD")
    match = re.search(r"\b([A-Z]{6}|XAUUSD|USTEC|US500|SP500|GER40|NAS100)\b", text.upper())
    return _safe_token(match.group(1) if match else "EURUSD", "EURUSD")


def _extract_direction(text: str, payload: dict[str, Any]) -> str:
    raw = str(payload.get("direction") or payload.get("dir") or "").strip()
    if not raw:
        lowered = text.casefold()
        if any(token in lowered for token in ("short", "corto", "venta", "sell")):
            raw = "short"
        elif any(token in lowered for token in ("long", "largo", "compra", "buy")):
            raw = "long"
        else:
            raw = "both"
    try:
        return normalize_direction(raw)
    except ValueError:
        return "both"


def _extract_family(text: str, payload: dict[str, Any], layer: int) -> str:
    raw = str(payload.get("family") or payload.get("blocksettingFamily") or "").strip().casefold()
    if raw in FAMILY_ALIASES:
        return "filtros" if FAMILY_ALIASES[raw] == "BS_Filtros" else raw
    if layer == 2:
        return "filtros"
    lowered = text.casefold()
    for token in ("volatilidad", "volatility", "momentum", "tendencia", "trend", "regimen", "regime", "volumen", "volume", "soporte", "resistencia", "estadistico"):
        if token in lowered:
            return "sr" if token in {"soporte", "resistencia"} else token
    return "volatilidad"


def _extract_layer(text: str, payload: dict[str, Any]) -> int:
    raw = payload.get("layer") or payload.get("capa")
    try:
        value = int(raw)
        if value in (1, 2):
            return value
    except (TypeError, ValueError):
        pass
    lowered = text.casefold()
    if "capa2" in lowered or "capa 2" in lowered or "filtro" in lowered or "filter" in lowered:
        return 2
    return 1


def _extract_concepts(text: str, payload: dict[str, Any], family: str) -> list[str]:
    raw = payload.get("concepts")
    concepts: list[str] = []
    if isinstance(raw, list):
        concepts.extend(_safe_token(str(item).casefold(), "") for item in raw)
    lowered = text.casefold()
    for concept, aliases in CONCEPT_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            concepts.append(concept)
    if not concepts and family in {"volatilidad", "volumen", "momentum"}:
        concepts.append({"volatilidad": "atr", "volumen": "volume", "momentum": "rsi"}[family])
    return sorted({item for item in concepts if item})


def _extract_intent(payload: dict[str, Any], *, session: dict[str, Any] | None = None) -> dict[str, Any]:
    stored_intent = session.get("intent") if session and isinstance(session.get("intent"), dict) else {}
    text = str(payload.get("prompt") or payload.get("message") or "")
    if not text and session:
        text = str(session.get("intentTextForPlanning") or "")
    if not text.strip():
        raise ValueError("prompt_required")
    if not _is_public_safe_text(text):
        raise ValueError("prompt_not_public_safe")
    explicit_base = str(payload.get("explicitBaseCanonicalId") or stored_intent.get("explicitBaseCanonicalId") or "").strip()
    requested_base = str(payload.get("baseCanonicalId") or payload.get("blocksetting") or "").strip()
    if requested_base and "_v7" in requested_base.casefold() and not explicit_base:
        raise ValueError("filters_v7_requires_explicit_base_canonical_id")
    layer = int(stored_intent.get("layer") or _extract_layer(text, payload)) if not (payload.get("layer") or payload.get("capa")) else _extract_layer(text, payload)
    family = str(stored_intent.get("family") or _extract_family(text, payload, layer)) if not (payload.get("family") or payload.get("blocksettingFamily")) else _extract_family(text, payload, layer)
    concepts = _extract_concepts(text, payload, family) or list(stored_intent.get("concepts") or [])
    asset_value = str(payload.get("asset") or payload.get("symbol") or stored_intent.get("asset") or _extract_asset(text, payload)).upper()
    timeframe_value = str(payload.get("timeframe") or payload.get("tf") or stored_intent.get("timeframe") or _extract_timeframe(text, payload)).upper()
    return {
        "asset": _safe_token(asset_value, "EURUSD"),
        "timeframe": timeframe_value if timeframe_value in TIMEFRAMES else "H1",
        "direction": _extract_direction(text, payload) if (payload.get("direction") or payload.get("dir")) else str(stored_intent.get("direction") or _extract_direction(text, payload)),
        "layer": layer,
        "family": family,
        "concepts": sorted({str(item) for item in concepts}),
        "explicitBaseCanonicalId": explicit_base,
        "promptDigest": _digest_text(text),
        "promptWordCount": len(text.split()),
        # Stored only in ignored local state so a later plan call can work; never returned by public payloads.
        "intentTextForPlanning": redact_text(text)[:400],
    }


def _entry_for_intent(intent: dict[str, Any]) -> tuple[dict[str, Any], str]:
    explicit = str(intent.get("explicitBaseCanonicalId") or "")
    entries = entries_by_id()
    if explicit:
        entry = entries.get(explicit)
        if not entry:
            raise KeyError("explicit_base_not_found")
        if int(entry.get("layer") or 0) != int(intent.get("layer") or 1):
            raise ValueError("explicit_base_layer_mismatch")
        tf = str(intent.get("timeframe") or "").upper()
        timeframes = {str(item).upper() for item in (entry.get("timeframes") or [])}
        if timeframes and tf not in timeframes and "ALL" not in timeframes:
            raise ValueError("explicit_base_timeframe_mismatch")
        return entry, "explicit_base_preserve_official_v6_v7"
    if int(intent.get("layer") or 1) == 2:
        return resolve_blocksetting_entry("BS_Tendencia_v6", timeframe=intent.get("timeframe"), capa=2), "filters_default_v6_v6_d1_v7_explicit_only"
    family = str(intent.get("family") or "volatilidad").casefold()
    alias = FAMILY_ALIASES.get(family) or "BS_Volatilidad"
    return resolve_blocksetting_entry(alias, timeframe=intent.get("timeframe"), capa=1), "capa1_default_v6_intraday_policy"


def _matching_active_keys(entry: dict[str, Any], concepts: list[str]) -> list[str]:
    active = [str(item) for item in entry.get("activeBlocks") or []]
    if not concepts:
        return []
    matches: list[str] = []
    aliases = {concept: CONCEPT_ALIASES.get(concept, (concept,)) for concept in concepts}
    for key in active:
        lowered = key.casefold()
        if any(any(alias in lowered for alias in concept_aliases) for concept_aliases in aliases.values()):
            matches.append(key)
    return matches


def _active_from_root(root: ET.Element) -> tuple[list[str], list[str]]:
    active = [
        str(block.get("key"))
        for block in root.findall(".//BuildingBlocks/Block")
        if block.get("key") and str(block.get("use")).casefold() == "true" and block.get("key") not in ("#Left#", "#Right#")
    ]
    return active, [key for key in active if key.startswith("Indicators.")]


def _bias_root_weights(root: ET.Element, biased_keys: list[str]) -> int:
    wanted = set(biased_keys)
    changed = 0
    for block in root.findall(".//BuildingBlocks/Block"):
        key = str(block.get("key") or "")
        if key in wanted and str(block.get("use")).casefold() == "true":
            if block.get("weight") != "3":
                block.set("weight", "3")
                changed += 1
            generated = block.find("Generated")
            if generated is not None and generated.get("weight") != "3":
                generated.set("weight", "3")
                changed += 1
    return changed


def _serialize_xml(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def build_bsai_catalog(project_root: Path) -> dict[str, Any]:
    manifest = load_blocksettings_manifest()
    entries = []
    for entry in manifest.get("entries", []):
        entries.append({
            "canonicalId": entry.get("canonicalId"),
            "family": entry.get("family"),
            "familyLabel": entry.get("familyLabel"),
            "layer": entry.get("layer"),
            "variant": entry.get("variant"),
            "timeframes": entry.get("timeframes") or [],
            "sha256Short": entry.get("sha256Short"),
            "activeBlocks": len(entry.get("activeBlocks") or []),
            "activeIndicators": entry.get("activeIndicators") or [],
            "activeBlockPreview": entry.get("activeBlockPreview") or [],
        })
    candidate_count = len(list(_candidates_dir(project_root).glob("BSAI_*.sqb"))) if _candidates_dir(project_root).exists() else 0
    return {
        "ok": True,
        "version": BS_AI_VERSION,
        "catalog": {
            "type": "sqx-edge.bs-ai-catalog-v1",
            "officialManifestVersion": manifest.get("version"),
            "officialEntries": entries,
            "candidateCount": candidate_count,
            "versionPolicy": {
                "officialResourcesImmutable": True,
                "capa1Default": "v6",
                "capa2Default": "BS_Filtros_v6",
                "capa2D1Default": "BS_Filtros_v6_D1",
                "filtersV7": "explicitBaseCanonicalId_only",
                "candidateNamespace": "BSAI",
            },
        },
        "privacy": {"local_paths_returned": False, "raw_xml_returned": False, "prompt_persisted": False},
    }


def create_bsai_session(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    _ensure_state(project_root)
    if any(key in payload for key in ("path", "output", "dbPath", "sqxRoot", "fileName")):
        return {
            "ok": False,
            "version": BS_AI_VERSION,
            "error": "client_path_fields_blocked",
            "privacy": {"local_paths_returned": False, "tokens_returned": False},
        }
    try:
        intent = _extract_intent(payload)
    except ValueError as exc:
        return {"ok": False, "version": BS_AI_VERSION, "error": str(exc), "privacy": {"local_paths_returned": False, "prompt_persisted": False}}
    session_id = f"bsai_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
    session = {
        "type": BS_AI_SESSION_TYPE,
        "version": BS_AI_VERSION,
        "sessionId": session_id,
        "createdAt": _utc_now(),
        "updatedAt": _utc_now(),
        "status": "created",
        "intent": {key: value for key, value in intent.items() if key != "intentTextForPlanning"},
        "intentTextForPlanning": intent.get("intentTextForPlanning"),
    }
    _save_session(project_root, session)
    return {
        "ok": True,
        "version": BS_AI_VERSION,
        "session": {
            "sessionId": session_id,
            "status": "created",
            "intent": session["intent"],
        },
        "privacy": {"local_paths_returned": False, "prompt_persisted": False},
    }


def plan_bsai_session(project_root: Path, session_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        session = _load_session(project_root, session_id)
        intent = _extract_intent(payload or {}, session=session)
        base_entry, policy = _entry_for_intent(intent)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        return {"ok": False, "version": BS_AI_VERSION, "error": str(exc), "privacy": {"local_paths_returned": False, "prompt_persisted": False}}
    biased = _matching_active_keys(base_entry, intent.get("concepts") or [])
    recipe = {
        "type": BS_AI_RECIPE_TYPE,
        "status": "ready",
        "candidateLayer": intent["layer"],
        "asset": intent["asset"],
        "timeframe": intent["timeframe"],
        "direction": intent["direction"],
        "family": intent["family"],
        "baseCanonicalId": base_entry.get("canonicalId"),
        "baseVariant": base_entry.get("variant"),
        "baseSha256": base_entry.get("sha256"),
        "sourceVersionPolicy": policy,
        "candidateNamespace": "BSAI",
        "customizationMode": "weight_bias_only",
        "selectedConcepts": intent.get("concepts") or [],
        "weightBiasKeys": biased,
        "guardrails": [
            "official_v6_v7_resources_are_never_overwritten",
            "filters_v7_requires_explicitBaseCanonicalId",
            "candidate_stays_under_ignored_local_blocksettings_ai",
            "manual_sqx_review_required",
            "no_data_db_user_projects_or_databank_write",
        ],
    }
    session["status"] = "planned"
    session["intent"] = {key: value for key, value in intent.items() if key != "intentTextForPlanning"}
    session["intentTextForPlanning"] = intent.get("intentTextForPlanning")
    session["recipe"] = recipe
    _save_session(project_root, session)
    return {
        "ok": True,
        "version": BS_AI_VERSION,
        "sessionId": session_id,
        "recipe": recipe,
        "baseBlockSetting": blocksetting_trace(base_entry),
        "privacy": {"local_paths_returned": False, "raw_xml_returned": False, "prompt_persisted": False},
    }


def _next_candidate_revision(project_root: Path, prefix: str) -> int:
    existing = sorted(_candidates_dir(project_root).glob(f"{prefix}_r*.sqb"))
    revisions = []
    for path in existing:
        match = re.search(r"_r(\d{3})$", path.stem)
        if match:
            revisions.append(int(match.group(1)))
    return (max(revisions) + 1) if revisions else 1


def _candidate_prefix(recipe: dict[str, Any]) -> str:
    family = _safe_token(str(recipe.get("family") or "Custom").title(), "Custom")
    tf = _safe_token(str(recipe.get("timeframe") or "ALL").upper(), "ALL")
    base = _safe_token(str(recipe.get("baseCanonicalId") or "Base"), "Base")
    return f"BSAI_{family}_L{int(recipe.get('candidateLayer') or 1)}_{tf}_from_{base}"


def save_bsai_candidate(project_root: Path, session_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = plan_bsai_session(project_root, session_id, payload or {})
    if not plan.get("ok"):
        return plan
    recipe = plan["recipe"]
    try:
        base_entry = entries_by_id()[str(recipe["baseCanonicalId"])]
        base_path = blocksetting_file(base_entry)
    except Exception as exc:
        return {"ok": False, "version": BS_AI_VERSION, "error": str(exc), "privacy": {"local_paths_returned": False}}
    _ensure_state(project_root)
    prefix = _candidate_prefix(recipe)
    revision = _next_candidate_revision(project_root, prefix)
    canonical_id = f"{prefix}_r{revision:03d}"
    filename = f"{canonical_id}.sqb"
    official_ids, official_files = _official_ids_and_files()
    if canonical_id in official_ids or filename in official_files:
        return {"ok": False, "version": BS_AI_VERSION, "error": "candidate_conflicts_with_official_blocksetting", "privacy": {"local_paths_returned": False}}
    target = _candidates_dir(project_root) / filename
    root = read_blocks_root(base_entry)
    weight_changes = _bias_root_weights(root, list(recipe.get("weightBiasKeys") or []))
    with zipfile.ZipFile(base_path, "r") as source, zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as dest:
        for info in source.infolist():
            data = _serialize_xml(root) if info.filename == "config.xml" else source.read(info.filename)
            new_info = zipfile.ZipInfo(filename=info.filename, date_time=info.date_time)
            new_info.compress_type = zipfile.ZIP_DEFLATED
            new_info.external_attr = info.external_attr
            dest.writestr(new_info, data)
    candidate_sha = _sha256_file(target)
    active, active_indicators = _active_from_root(root)
    entry = {
        "canonicalId": canonical_id,
        "filename": filename,
        "family": base_entry.get("family"),
        "familyLabel": base_entry.get("familyLabel"),
        "layer": int(recipe.get("candidateLayer") or base_entry.get("layer") or 1),
        "variant": f"bsai_from_{base_entry.get('variant')}_r{revision:03d}",
        "timeframes": [recipe.get("timeframe")] if recipe.get("timeframe") else (base_entry.get("timeframes") or []),
        "sha256": candidate_sha,
        "sha256Short": candidate_sha[:12],
        "sqxVersion": base_entry.get("sqxVersion"),
        "counts": {"activeBlocks": len(active), "activeIndicators": len(active_indicators), "weightBiasChanges": weight_changes},
        "activeBlocks": active,
        "activeIndicators": active_indicators,
        "activeBlockPreview": active[:12],
        "origin": "bs-ai-generator",
        "sourceScope": BS_AI_CANDIDATE_SCOPE,
        "baseCanonicalId": base_entry.get("canonicalId"),
        "baseVariant": base_entry.get("variant"),
        "baseSha256": base_entry.get("sha256"),
        "candidateRevision": f"r{revision:03d}",
        "sourceVersionPolicy": recipe.get("sourceVersionPolicy"),
        "promotionState": BS_AI_PROMOTION_STATE,
        "localPath": str(target),
        "candidateRoot": str(_candidates_dir(project_root)),
    }
    metadata = {
        "version": BS_AI_VERSION,
        "artifactId": canonical_id,
        "createdAt": _utc_now(),
        "entry": entry,
        "recipe": recipe,
        "privacy": {"local_paths_returned": False, "official_resources_overwritten": False},
    }
    (target.with_suffix(".json")).write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    session = _load_session(project_root, session_id)
    session["status"] = "candidate_saved"
    session["candidate"] = metadata
    _save_session(project_root, session)
    return {
        "ok": True,
        "version": BS_AI_VERSION,
        "sessionId": session_id,
        "candidate": {
            "artifactId": canonical_id,
            "downloadUrl": f"/api/blocksettings/ai/download/{canonical_id}",
            "blocksetting": blocksetting_trace(entry),
            "entry": _public_entry(entry),
        },
        "privacy": {"local_paths_returned": False, "official_resources_overwritten": False, "prompt_persisted": False},
    }


def resolve_bsai_download(project_root: Path, artifact_id: str) -> Path | None:
    token = _safe_token(artifact_id, "")
    if not token.startswith("BSAI_"):
        return None
    path = (_candidates_dir(project_root) / f"{token}.sqb").resolve(strict=False)
    root = _candidates_dir(project_root).resolve(strict=False)
    try:
        path.relative_to(root)
    except ValueError:
        return None
    if path.is_file() and path.suffix.lower() == ".sqb":
        return path
    return None


def _candidate_entry_from_session(project_root: Path, session: dict[str, Any]) -> dict[str, Any]:
    candidate = session.get("candidate") if isinstance(session.get("candidate"), dict) else {}
    entry = candidate.get("entry") if isinstance(candidate.get("entry"), dict) else None
    if not entry:
        raise FileNotFoundError("bsai_candidate_not_saved")
    return dict(entry)


def _direction_tag(direction: str) -> str:
    return {"long": "L", "short": "S", "both": "LS"}[direction]


def _project_name(recipe: dict[str, Any], candidate_id: str) -> str:
    asset = _safe_token(str(recipe.get("asset") or "EURUSD").upper(), "EURUSD")
    tf = _safe_token(str(recipe.get("timeframe") or "H1").upper(), "H1")
    direction = _direction_tag(str(recipe.get("direction") or "both"))
    return _safe_token(f"BSAI_{asset}_{tf}_{candidate_id}_{direction}", f"BSAI_{asset}_{tf}_{direction}")


def _capa1_family_alias(recipe: dict[str, Any]) -> str:
    if int(recipe.get("candidateLayer") or 1) == 1:
        return str(recipe.get("baseCanonicalId") or "BS_Volatilidad")
    family = str(recipe.get("family") or "volatilidad").casefold()
    if family == "filtros":
        return "BS_Volatilidad"
    return FAMILY_ALIASES.get(family) or "BS_Volatilidad"


def generate_bsai_project_pair(
    project_root: Path,
    session_id: str,
    *,
    template_capa1: str,
    template_capa2: str,
    output_dir: str,
    sqx_db_path: str | None = None,
    broker_postfix: str = DEFAULT_BROKER_POSTFIX,
    alias_override: dict | None = None,
    target_profile: dict | None = None,
) -> dict[str, Any]:
    try:
        session = _load_session(project_root, session_id)
        if not session.get("candidate"):
            saved = save_bsai_candidate(project_root, session_id, {})
            if not saved.get("ok"):
                return saved
            session = _load_session(project_root, session_id)
        entry = _candidate_entry_from_session(project_root, session)
        recipe = session.get("recipe") if isinstance(session.get("recipe"), dict) else (session.get("candidate") or {}).get("recipe")
        if not isinstance(recipe, dict):
            raise ValueError("bsai_recipe_missing")
        layer = int(entry.get("layer") or recipe.get("candidateLayer") or 1)
        asset = _safe_token(str(recipe.get("asset") or "EURUSD").upper(), "EURUSD")
        tf = _safe_token(str(recipe.get("timeframe") or "H1").upper(), "H1")
        direction = normalize_direction(str(recipe.get("direction") or "both"))
        mining = Mining(num=0, phase=0, asset=asset, tf=tf, bs=_capa1_family_alias(recipe), dir=direction)
        project_name = _project_name(recipe, str(entry["canonicalId"]))
    except Exception as exc:
        return {"ok": False, "version": BS_AI_VERSION, "error": str(exc), "privacy": {"local_paths_returned": False}}

    results: dict[str, Any] = {}
    files: list[dict[str, Any]] = []
    for capa, template in ((1, template_capa1), (2, template_capa2)):
        try:
            override = entry if layer == capa else None
            out_path = Path(generate_project(
                mining,
                template_path=template,
                output_dir=output_dir,
                capa=capa,
                sqx_db_path=sqx_db_path,
                broker_postfix=broker_postfix,
                alias_override=alias_override,
                project_name=project_name,
                target_profile=target_profile,
                blocksetting_entry_override=override,
            ))
            costs = resolve_costs(mining, sqx_db_path, broker_postfix, alias_override=alias_override, target_profile=target_profile)
            used_entry = override or resolve_blocksetting_entry(mining.bs, timeframe=mining.tf, capa=capa)
            item = {
                "ok": True,
                "capa": capa,
                "filename": out_path.name,
                "downloadUrl": f"/api/output/download/{out_path.name}",
                "costsSource": costs.get("source"),
                "symbol": costs.get("symbol"),
                "blocksetting": blocksetting_trace(used_entry),
            }
            results[f"capa{capa}"] = item
            files.append({"capa": capa, "name": out_path.name, "downloadUrl": item["downloadUrl"]})
        except Exception as exc:
            results[f"capa{capa}"] = {"ok": False, "capa": capa, "error": redact_text(f"{type(exc).__name__}: {exc}")}
    ok_count = sum(1 for item in results.values() if item.get("ok"))
    session["status"] = "project_generated" if ok_count == 2 else "project_generation_partial"
    session["project"] = {"okCount": ok_count, "files": files, "generatedAt": _utc_now()}
    _save_session(project_root, session)
    return {
        "ok": ok_count == 2,
        "version": BS_AI_VERSION,
        "sessionId": session_id,
        "projectName": project_name,
        "candidate": {"artifactId": entry.get("canonicalId"), "blocksetting": blocksetting_trace(entry)},
        "results": results,
        "files": files,
        "privacy": {"local_paths_returned": False, "official_resources_overwritten": False, "prompt_persisted": False},
    }
