from __future__ import annotations

import copy
import json
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .config_loader import ROOT, config_path


RESOURCE_DIR = ROOT / "resources" / "blocksettings"
MANIFEST_NAME = "blocksettings_manifest.json"
INTRADAY_TIMEFRAMES = {"M5", "M15", "M30", "H1"}


def _normalize_token(value: str | None) -> str:
    token = str(value or "").strip()
    if token.lower().endswith(".sqb"):
        token = token[:-4]
    return token


@lru_cache(maxsize=1)
def load_blocksettings_manifest() -> dict[str, Any]:
    path = config_path(MANIFEST_NAME)
    if not path.is_file():
        raise FileNotFoundError(f"BlockSettings manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clear_blocksettings_cache() -> None:
    load_blocksettings_manifest.cache_clear()


def entries_by_id() -> dict[str, dict[str, Any]]:
    manifest = load_blocksettings_manifest()
    return {entry["canonicalId"]: entry for entry in manifest.get("entries", [])}


def resolve_alias(value: str | None) -> str:
    manifest = load_blocksettings_manifest()
    token = _normalize_token(value)
    aliases = manifest.get("aliases") or {}
    return aliases.get(token) or aliases.get(token + ".sqb") or token


def family_from_blocksetting(value: str | None) -> str:
    manifest = load_blocksettings_manifest()
    resolved = resolve_alias(value)
    entry = entries_by_id().get(resolved)
    if entry:
        return str(entry.get("family") or "")
    aliases = manifest.get("aliases") or {}
    legacy = aliases.get(_normalize_token(value), _normalize_token(value)).lower()
    if "soporteresistencia" in legacy:
        return "sr"
    for family in ("tendencia", "momentum", "volatilidad", "regimen", "volumen", "estadistico", "filtros"):
        if family in legacy:
            return family
    return ""


def resolve_capa1_id(blocksetting: str | None, timeframe: str | None) -> str:
    manifest = load_blocksettings_manifest()
    resolver = manifest.get("capa1Resolver") or {}
    family = family_from_blocksetting(blocksetting)
    family_rules = (resolver.get("families") or {}).get(family) or {}
    tf = str(timeframe or "").strip().upper()
    if tf in set(resolver.get("intradayTimeframes") or INTRADAY_TIMEFRAMES) and family_rules.get("intraday"):
        return str(family_rules["intraday"])
    return str(family_rules.get("default") or resolve_alias(blocksetting))


def recommend_capa2_id(timeframe: str | None) -> str:
    manifest = load_blocksettings_manifest()
    recommendations = ((manifest.get("capa2Recommendations") or {}).get("recommendations") or {})
    tf = str(timeframe or "").strip().upper()
    return str(recommendations.get(tf) or recommendations.get("fallback") or "BS_Filtros_v4")


def resolve_blocksetting_entry(
    blocksetting: str | None,
    timeframe: str | None = None,
    capa: int = 1,
    blocksetting_capa2: str | None = None,
) -> dict[str, Any]:
    entries = entries_by_id()
    if int(capa) == 2:
        candidate = resolve_alias(blocksetting_capa2) if blocksetting_capa2 else recommend_capa2_id(timeframe)
    else:
        candidate = resolve_capa1_id(blocksetting, timeframe)
    entry = entries.get(candidate)
    if not entry:
        raise KeyError(f"BlockSetting not found in manifest: {candidate}")
    return entry


def blocksetting_file(entry: dict[str, Any]) -> Path:
    filename = entry.get("filename")
    if not filename:
        raise ValueError("BlockSetting entry has no filename")
    path = RESOURCE_DIR / str(filename)
    if not path.is_file():
        raise FileNotFoundError(f"BlockSetting .sqb not found: {path}")
    return path


def read_blocks_root(entry: dict[str, Any]) -> ET.Element:
    path = blocksetting_file(entry)
    with zipfile.ZipFile(path) as zf:
        return ET.fromstring(zf.read("config.xml"))


def replace_blocks(root: ET.Element, blocks_root: ET.Element) -> bool:
    for parent in root.iter():
        children = list(parent)
        for index, child in enumerate(children):
            if child.tag == "Blocks":
                parent.remove(child)
                parent.insert(index, copy.deepcopy(blocks_root))
                return True
    return False


def apply_blocksetting_to_xml(root: ET.Element, entry: dict[str, Any]) -> bool:
    blocks_root = read_blocks_root(entry)
    return replace_blocks(root, blocks_root)


def blocksetting_trace(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonicalId": entry.get("canonicalId"),
        "filename": entry.get("filename"),
        "family": entry.get("family"),
        "familyLabel": entry.get("familyLabel"),
        "layer": entry.get("layer"),
        "variant": entry.get("variant"),
        "timeframes": entry.get("timeframes") or [],
        "sha256": entry.get("sha256"),
        "sha256Short": entry.get("sha256Short"),
        "sqxVersion": entry.get("sqxVersion"),
    }
