from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
RESOURCE_DIR = TOOL_ROOT / "resources" / "blocksettings"
OUT_PATH = TOOL_ROOT / "config" / "blocksettings_manifest.json"
INTRADAY_TIMEFRAMES = ["M5", "M15", "M30", "H1"]
ALL_CAPA1_TIMEFRAMES = ["M5", "M15", "M30", "H1", "H4", "D1"]


FAMILY_LABELS = {
    "tendencia": "Tendencia",
    "momentum": "Momentum",
    "volatilidad": "Volatilidad",
    "regimen": "Regimen",
    "volumen": "Volumen",
    "sr": "Soporte/Resistencia",
    "estadistico": "Estadistico",
    "filtros": "Filtros operativos",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def canonical_id(path: Path) -> str:
    return path.stem


def family_from_id(cid: str) -> str:
    base = cid.lower()
    if base.startswith("bs_soporteresistencia"):
        return "sr"
    for family in ("tendencia", "momentum", "volatilidad", "regimen", "volumen", "estadistico"):
        if base.startswith("bs_" + family):
            return family
    if base.startswith("bs_filtros"):
        return "filtros"
    return "custom"


def variant_from_id(cid: str) -> str:
    lower = cid.lower()
    if "intraday_v5" in lower:
        return "intraday_v5"
    match = re.search(r"_v\d+(?:_[a-z0-9]+)?", lower)
    return match.group(0).lstrip("_") if match else "base"


def timeframes_from_id(cid: str, layer: int, variant: str) -> list[str]:
    upper = cid.upper()
    if layer == 1:
        return INTRADAY_TIMEFRAMES if variant == "intraday_v5" else ALL_CAPA1_TIMEFRAMES
    for tf in ("M5", "M15", "M30", "H1", "H4", "D1"):
        if upper.endswith("_" + tf):
            return [tf]
    return ["M5", "M15", "M30", "H1", "H4", "D1"]


def read_sqb_root(path: Path) -> ET.Element:
    with zipfile.ZipFile(path) as zf:
        return ET.fromstring(zf.read("config.xml"))


def param_signature(block: ET.Element) -> dict:
    params = []
    for param in block.findall("./Generated/Param"):
        params.append({
            "key": param.get("key"),
            "name": param.get("name"),
            "type": param.get("type"),
            "generation": param.get("generation"),
            "min": param.get("minValue"),
            "max": param.get("maxValue"),
            "step": param.get("step"),
        })
    return {"generated": params}


def parse_sqb(path: Path) -> dict:
    cid = canonical_id(path)
    layer = 2 if cid.lower().startswith("bs_filtros") else 1
    family = family_from_id(cid)
    variant = variant_from_id(cid)
    digest = sha256(path)
    root = read_sqb_root(path)
    blocks = [
        block for block in root.findall(".//BuildingBlocks/Block")
        if block.get("key") and block.get("key") not in ("#Left#", "#Right#")
    ]
    active = [block for block in blocks if (block.get("use") or "").lower() == "true"]
    changed = [
        block for block in blocks
        if (block.find("Predefined") is not None and (block.find("Predefined").get("changed") or "").lower() == "true")
    ]
    categories = Counter(block.get("category") or "none" for block in blocks)
    used_categories = Counter(block.get("category") or "none" for block in active)
    active_keys = [block.get("key") for block in active if block.get("key")]
    active_indicators = [key for key in active_keys if key.startswith("Indicators.")]
    return {
        "canonicalId": cid,
        "filename": path.name,
        "family": family,
        "familyLabel": FAMILY_LABELS.get(family, family),
        "layer": layer,
        "variant": variant,
        "timeframes": timeframes_from_id(cid, layer, variant),
        "sha256": digest,
        "sha256Short": digest[:12],
        "sqxVersion": root.get("version"),
        "counts": {
            "blocks": len(blocks),
            "activeBlocks": len(active),
            "changedBlocks": len(changed),
            "categories": dict(sorted(categories.items())),
            "activeCategories": dict(sorted(used_categories.items())),
        },
        "activeBlocks": active_keys,
        "activeIndicators": active_indicators,
        "activeBlockPreview": active_keys[:12],
        "parameterPreview": {
            block.get("key"): param_signature(block)
            for block in active[:8]
            if block.get("key")
        },
    }


def build_manifest() -> dict:
    entries = [parse_sqb(path) for path in sorted(RESOURCE_DIR.glob("*.sqb"))]
    aliases = {
        "BS_Tendencia": "BS_Tendencia_v4",
        "BS_Momentum": "BS_Momentum_v4",
        "BS_Volatilidad": "BS_Volatilidad_v4",
        "BS_Regimen": "BS_Regimen_v4",
        "BS_Volumen": "BS_Volumen_v4",
        "BS_SoporteResistencia": "BS_SoporteResistencia_v4",
        "BS_Estadistico": "BS_Estadistico_v4",
        "BS_Filtros": "BS_Filtros_v4",
        "BS_Filtros_v5": "BS_Filtros_v5_D1",
        "BS_Filtros_v7": "BS_Filtros_v7_H1",
    }
    aliases.update({entry["canonicalId"]: entry["canonicalId"] for entry in entries})
    aliases.update({entry["filename"]: entry["canonicalId"] for entry in entries})
    capa1 = {
        "intradayTimeframes": INTRADAY_TIMEFRAMES,
        "families": {
            "tendencia": {"default": "BS_Tendencia_v4"},
            "momentum": {"default": "BS_Momentum_v4"},
            "volatilidad": {"default": "BS_Volatilidad_v4", "intraday": "BS_Volatilidad_v4_intraday_v5"},
            "regimen": {"default": "BS_Regimen_v4"},
            "volumen": {"default": "BS_Volumen_v4", "intraday": "BS_Volumen_v4_intraday_v5"},
            "sr": {"default": "BS_SoporteResistencia_v4", "intraday": "BS_SoporteResistencia_v4_intraday_v5"},
            "estadistico": {"default": "BS_Estadistico_v4"},
        },
    }
    capa2 = {
        "manual": True,
        "recommendations": {
            "M5": "BS_Filtros_v7_M5",
            "M15": "BS_Filtros_v7_M15",
            "M30": "BS_Filtros_v7_M30",
            "H1": "BS_Filtros_v7_H1",
            "H4": "BS_Filtros_v7_H4",
            "D1": "BS_Filtros_v5_D1",
            "fallback": "BS_Filtros_v4",
        },
    }
    return {
        "version": 1,
        "source": {
            "resourceDir": "backend/sqx-edge-tool/resources/blocksettings",
            "generatedFrom": "versioned .sqb resources",
        },
        "entries": entries,
        "aliases": aliases,
        "capa1Resolver": capa1,
        "capa2Recommendations": capa2,
    }


def main() -> None:
    manifest = build_manifest()
    OUT_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} with {len(manifest['entries'])} BlockSettings")


if __name__ == "__main__":
    main()
