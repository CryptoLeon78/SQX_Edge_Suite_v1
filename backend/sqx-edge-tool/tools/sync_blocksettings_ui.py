from __future__ import annotations

import copy
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
UI_PATH = CONFIG_DIR / "ui_manifest.json"
BS_PATH = CONFIG_DIR / "blocksettings_manifest.json"

FAMILY_ORDER = ["tendencia", "momentum", "volatilidad", "regimen", "volumen", "sr", "estadistico"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def by_id(entries: list[dict]) -> dict[str, dict]:
    return {entry["canonicalId"]: entry for entry in entries}


def option_for(entry: dict) -> dict:
    return {
        "value": entry.get("canonicalId"),
        "label": entry.get("canonicalId"),
        "family": entry.get("family"),
        "variant": entry.get("variant"),
        "sha256Short": entry.get("sha256Short"),
        "timeframes": entry.get("timeframes") or [],
    }


def family_sort_key(entry: dict) -> tuple[int, str, str]:
    family = str(entry.get("family") or "")
    try:
        family_index = FAMILY_ORDER.index(family)
    except ValueError:
        family_index = 99
    return (family_index, str(entry.get("variant") or ""), str(entry.get("canonicalId") or ""))


def c1_option_sort_key(entry: dict, defaults: dict[str, str]) -> tuple[int, int, str, str]:
    base = family_sort_key(entry)
    current = 0 if defaults.get(str(entry.get("family") or "")) == entry.get("canonicalId") else 1
    return (base[0], current, base[1], base[2])


def short_indicators(entry: dict) -> list[str]:
    return list(entry.get("activeIndicators") or [])[:10]


def enrich_capa1_card(card: dict, entry: dict, intraday_entry: dict | None = None) -> dict:
    next_card = copy.deepcopy(card)
    cid = entry["canonicalId"]
    next_card["blockSetting"] = cid
    next_card["displayBlockSetting"] = cid
    next_card["filename"] = entry.get("filename")
    next_card["sha256Short"] = entry.get("sha256Short")
    next_card["activeBlocks"] = (entry.get("counts") or {}).get("activeBlocks")
    next_card["activeIndicators"] = short_indicators(entry)
    next_card["variant"] = entry.get("variant")
    next_card["timeframes"] = entry.get("timeframes") or []
    if intraday_entry:
        next_card["intradayBlockSetting"] = intraday_entry.get("canonicalId")
        next_card["intradayFilename"] = intraday_entry.get("filename")
        next_card["intradaySha256Short"] = intraday_entry.get("sha256Short")
        next_card["intradayVariant"] = intraday_entry.get("variant")
        next_card["displayBlockSetting"] = f"{cid} · intraday {intraday_entry.get('canonicalId')}"
        next_card["parameterStatus"] = (
            f"Fuente real: {entry.get('filename')} · hash {entry.get('sha256Short')}. "
            f"Intraday M5/M15/M30/H1: {intraday_entry.get('filename')} · hash {intraday_entry.get('sha256Short')}."
        )
    else:
        next_card["parameterStatus"] = f"Fuente real: {entry.get('filename')} · hash {entry.get('sha256Short')}."
    return next_card


def update_blocksettings_info(ui: dict, bs_manifest: dict) -> None:
    info = ui.setdefault("blockSettingsInfo", {})
    entries = by_id(bs_manifest.get("entries") or [])
    families = (bs_manifest.get("capa1Resolver") or {}).get("families") or {}
    existing_cards = {card.get("category"): card for card in info.get("capa1", []) if isinstance(card, dict)}
    cards = []
    for family in FAMILY_ORDER:
        rules = families.get(family) or {}
        default_entry = entries.get(rules.get("default"))
        if not default_entry:
            continue
        intraday_entry = entries.get(rules.get("intraday")) if rules.get("intraday") else None
        base_card = existing_cards.get(family, {"category": family})
        cards.append(enrich_capa1_card(base_card, default_entry, intraday_entry))
    info["capa1"] = cards
    info["subtitle"] = (
        "Escaparate metodologico de los BlockSettings reales v6 que usa SQX Edge para buscar Edge, "
        "resolver variantes por timeframe y endurecer Capa 2 con trazabilidad por hash."
    )
    info["capa1Intro"] = (
        "Cada tarjeta de Activos propone una hipotesis de edge por familia. En Capa 1 se resuelve "
        "automaticamente el BlockSetting oficial correcto; en familias con variante intraday, M5/M15/M30/H1 usan la variante intraday. "
        "Volatilidad queda cerrada con BS_Volatilidad_v6 como fuente general y BS_Volatilidad_v6_intraday_v6 para M5/M15/M30/H1."
    )
    capa2 = info.setdefault("capa2", {})
    recommendations = (bs_manifest.get("capa2Recommendations") or {}).get("recommendations") or {}
    capa2["blockSetting"] = "BS_Filtros_v6 / BS_Filtros_v6_D1"
    capa2["displayBlockSetting"] = "BS_Filtros v6 por timeframe"
    capa2["filename"] = "Selector manual con recomendacion automatica v6"
    capa2["sha256Short"] = "ver opcion elegida"
    capa2["recommendations"] = recommendations
    capa2["parameterStatus"] = (
        "Capa 2 usa BS_Filtros_v6 como recomendacion general y BS_Filtros_v6_D1 para D1. "
        "Los v4/v5/v7 quedan en catalogo como compatibilidad legacy, no como default metodologico."
    )


def update_core_mappings(ui: dict, bs_manifest: dict) -> None:
    entries = bs_manifest.get("entries") or []
    resolver = bs_manifest.get("capa1Resolver") or {}
    recommendations = bs_manifest.get("capa2Recommendations") or {}
    families = resolver.get("families") or {}
    ui["capa1Resolver"] = resolver
    ui["capa2Recommendations"] = recommendations
    ui["catToBs"] = {family: families.get(family, {}).get("default") for family in FAMILY_ORDER if families.get(family)}
    ui["priorityCatToBs"] = dict(ui["catToBs"])
    bs_to_priority = {
        "BS_Tendencia": "tendencia",
        "BS_Momentum": "momentum",
        "BS_Volatilidad": "volatilidad",
        "BS_Regimen": "regimen",
        "BS_Volumen": "volumen",
        "BS_SoporteResistencia": "sr",
        "BS_Estadistico": "estadistico",
    }
    for entry in entries:
        family = entry.get("family")
        if family in FAMILY_ORDER:
            bs_to_priority[entry["canonicalId"]] = family
            bs_to_priority[entry["filename"]] = family
    ui["bsToPriorityCat"] = bs_to_priority


def update_catalog(ui: dict, bs_manifest: dict) -> None:
    entries = bs_manifest.get("entries") or []
    families = ((bs_manifest.get("capa1Resolver") or {}).get("families") or {})
    defaults = {family: rules.get("default") for family, rules in families.items()}
    c1_entries = [entry for entry in entries if int(entry.get("layer") or 0) == 1]
    c2_entries = [entry for entry in entries if int(entry.get("layer") or 0) == 2]
    ui["blockSettingsCatalog"] = {
        "entries": entries,
        "aliases": bs_manifest.get("aliases") or {},
        "capa1Options": [option_for(entry) for entry in sorted(c1_entries, key=lambda e: c1_option_sort_key(e, defaults))],
        "capa2Options": [option_for(entry) for entry in sorted(c2_entries, key=family_sort_key)],
    }


def main() -> None:
    ui = read_json(UI_PATH)
    bs_manifest = read_json(BS_PATH)
    update_blocksettings_info(ui, bs_manifest)
    update_core_mappings(ui, bs_manifest)
    update_catalog(ui, bs_manifest)
    write_json(UI_PATH, ui)
    print(f"Synced BlockSettings v{bs_manifest.get('version')} into {UI_PATH}")


if __name__ == "__main__":
    main()
