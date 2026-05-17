"""
project_generator.py — Orquestador. Toma un mining + plantilla seed y genera un .cfx
listo para SQX, con todos los XMLs internos parametrizados.

Si data.db de SQX está disponible, los costos (spread/swap/commission) se leen de ahí.
Si no, se usa ASSET_DEFAULTS (aproximaciones de Darwinex).
"""
from __future__ import annotations

import os
import shutil
from datetime import datetime
from typing import Optional

from .cfx_editor import CfxEditor
from .blocksettings import apply_blocksetting_to_xml, blocksetting_trace, resolve_blocksetting_entry
from .config_loader import load_manifest
from .plan import Mining
from .sqx_db import SqxDb
from .xml_patcher import RETEST_PERIODS, apply_mining_to_xml, patch_dates


_GENERATOR_PROFILE = load_manifest("generator_profiles.json")
_INSTRUMENTS_PROFILE = load_manifest("instruments.json")
CAPA_TASK_MAPS = {
    int(capa): task_map
    for capa, task_map in (_GENERATOR_PROFILE.get("taskPeriodMaps") or {}).items()
}
TRADING_TIME_RANGES = _GENERATOR_PROFILE.get("tradingTimeRanges") or {}
ASSET_DEFAULTS = _INSTRUMENTS_PROFILE.get("assetDefaults") or {}
DEFAULT_BROKER_POSTFIX = (
    _INSTRUMENTS_PROFILE.get("defaultBrokerPostfix")
    or _GENERATOR_PROFILE.get("defaultBrokerPostfix")
    or "_darwinex"
)


def _symbol_for_sqx(asset: str, postfix: str = DEFAULT_BROKER_POSTFIX) -> str:
    """Convierte 'XAUUSD' a 'XAUUSD_darwinex' (o el postfix del broker en uso)."""
    return f"{asset}{postfix}"


def _direction_label(direction: str) -> str:
    return {"long": "LONG", "short": "SHORT", "both": "L+S"}.get(direction, (direction or "").upper())


def _trading_window_for(capa: int, timeframe: str) -> Optional[tuple[str, str]]:
    layer = (TRADING_TIME_RANGES.get(f"capa{capa}") or {})
    value = layer.get((timeframe or "").upper())
    if not value or len(value) != 2:
        return None
    return str(value[0]), str(value[1])


def _build_task_title(blocksetting_id: str, capa: int, direction: str, timeframe: str) -> str:
    tf = (timeframe or "TF").upper()
    return f"Build {blocksetting_id} · Capa{capa} {_direction_label(direction)} {tf}"


def _fallback_market_shape(asset: str) -> dict:
    token = (asset or "").upper()
    if token.startswith("XAU"):
        return {"tick_size": 0.01, "tick_step": 0.01, "point_value": 100.0, "sector": "Commodities", "data_type": 4}
    if len(token) == 6 and token.isalpha():
        is_jpy = token.endswith("JPY")
        return {
            "tick_size": 0.01 if is_jpy else 0.0001,
            "tick_step": 0.001 if is_jpy else 0.00001,
            "point_value": 1000.0 if is_jpy else 100000.0,
            "sector": "Currency",
            "data_type": 3,
        }
    return {"tick_size": 0.01, "tick_step": 0.01, "point_value": 1.0, "sector": "", "data_type": 3}


def resolve_costs(mining: Mining, sqx_db_path: Optional[str], postfix: str = DEFAULT_BROKER_POSTFIX,
                  alias_override: Optional[dict] = None) -> dict:
    """
    Resuelve costos REALES por mining: lee data.db si está disponible, si no usa
    ASSET_DEFAULTS.

    Args:
        mining: Mining del plan
        sqx_db_path: ruta a data.db (None = usa fallback directo)
        postfix: sufijo de broker para construir el symbol final
        alias_override: dict {asset: instrument} para sobreescribir defaults

    Devuelve dict con: source, spread, swap_long, swap_short, swap_type,
    commission_type, commission_value, instrument, symbol.
    """
    # 1) Intentar data.db
    if sqx_db_path and os.path.isfile(sqx_db_path):
        try:
            db = SqxDb(sqx_db_path)
            try:
                info = db.get_symbol_info(
                    mining.asset,
                    alias_override=alias_override,
                    preferred_postfix=postfix,
                )
                if info.get("source") == "db":
                    pf = info.get("broker_postfix") or postfix or ""
                    return {
                        "source": "db",
                        "instrument": info["instrument"],
                        "symbol": info.get("data_symbol") or (_symbol_for_sqx(info["instrument"], pf) if pf else info["instrument"]),
                        "spread": info.get("spread"),
                        "slippage": info.get("slippage"),
                        "swap_long": info.get("swap_long") if info.get("swap_long") is not None else 0.0,
                        "swap_short": info.get("swap_short") if info.get("swap_short") is not None else 0.0,
                        "swap_type": info.get("swap_type"),
                        "commission_type": info.get("commission_type"),
                        "commission_value": info.get("commission_value"),
                        "broker_postfix": pf,
                        "broker_id": info.get("broker_id"),
                        "broker_name": info.get("broker_name"),
                        "broker_description": info.get("broker_description"),
                        "broker_timezone": info.get("broker_timezone"),
                        "data_type": info.get("data_type"),
                        "tick_size": info.get("tick_size"),
                        "tick_step": info.get("tick_step"),
                        "point_value": info.get("point_value"),
                        "description": info.get("description"),
                        "min_distance": info.get("min_distance"),
                        "commissions_xml": info.get("commissions_xml"),
                        "swap_xml": info.get("swap_xml"),
                        "date_from_ms": info.get("date_from_ms"),
                        "date_to_ms": info.get("date_to_ms"),
                        "rows": info.get("rows"),
                        "u_symbol": info.get("u_symbol"),
                        "u_symbol_name": info.get("u_symbol_name"),
                        "exchange": info.get("exchange"),
                        "country": info.get("country"),
                        "sector": info.get("sector"),
                        "ordersize_multiplier": info.get("ordersize_multiplier"),
                        "ordersize_step": info.get("ordersize_step"),
                        "data_available": bool(info.get("rows") and int(info.get("rows") or 0) > 0),
                        "data_rows": info.get("rows"),
                    }
            finally:
                db.close()
        except Exception:
            pass  # caer a fallback

    # 2) Fallback a ASSET_DEFAULTS
    d = ASSET_DEFAULTS.get(mining.asset, {"spread": 10, "swap_long": -1.0, "swap_short": -1.0})
    shape = _fallback_market_shape(mining.asset)
    return {
        "source": "fallback",
        "instrument": mining.asset,
        "symbol": _symbol_for_sqx(mining.asset, postfix),
        "spread": d["spread"],
        "slippage": 0,
        "swap_long": d["swap_long"],
        "swap_short": d["swap_short"],
        "swap_type": None,
        "commission_type": None,
        "commission_value": None,
        "broker_postfix": postfix,
        "broker_id": 4 if postfix == "_darwinex" else None,
        "broker_name": "Darwinex" if postfix == "_darwinex" else None,
        "broker_description": "Darwinex CFDs" if postfix == "_darwinex" else None,
        "broker_timezone": "EETUS" if postfix == "_darwinex" else None,
        "data_type": shape["data_type"],
        "tick_size": shape["tick_size"],
        "tick_step": shape["tick_step"],
        "point_value": shape["point_value"],
        "description": d.get("description") if isinstance(d, dict) and d.get("description") else mining.asset,
        "min_distance": 0,
        "commissions_xml": None,
        "swap_xml": None,
        "date_from_ms": None,
        "date_to_ms": None,
        "rows": None,
        "u_symbol": mining.asset,
        "u_symbol_name": mining.asset,
        "exchange": "",
        "country": "",
        "sector": shape["sector"],
        "ordersize_multiplier": 1.0,
        "ordersize_step": 0.01,
        "data_available": False,
        "data_rows": None,
    }


def generate_project(
    mining: Mining,
    template_path: str,
    output_dir: str,
    capa: int = 1,
    suffix: str = "",
    sqx_data: Optional[dict] = None,
    sqx_db_path: Optional[str] = None,
    broker_postfix: str = DEFAULT_BROKER_POSTFIX,
    alias_override: Optional[dict] = None,
    overwrite: bool = True,
    project_name: Optional[str] = None,
    blocksetting_capa2: Optional[str] = None,
) -> str:
    """
    Genera un .cfx para el mining especificado.

    Args:
        mining: instancia Mining del plan
        template_path: path al .cfx seed (Capa1_Long.cfx o Capa2_Base.cfx)
        output_dir: carpeta donde se guarda el .cfx generado
        capa: 1 o 2 — determina el mapping de tasks → períodos
        suffix: sufijo opcional para el nombre (ej. "_v1")
        sqx_data: dict con datos extraídos de data.db (si None, usa ASSET_DEFAULTS)
        overwrite: sobreescribir si existe
        project_name: nombre base opcional para proyectos custom fuera del plan

    Returns:
        Path absoluto al .cfx generado.
    """
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    if capa not in CAPA_TASK_MAPS:
        raise ValueError(f"capa must be 1 or 2, got {capa}")
    editor = CfxEditor(template_path)
    task_map = CAPA_TASK_MAPS[capa]
    blocksetting_entry = resolve_blocksetting_entry(
        mining.bs,
        timeframe=mining.tf,
        capa=capa,
        blocksetting_capa2=blocksetting_capa2,
    )
    resolved_bs = str(blocksetting_entry.get("canonicalId") or mining.bs)
    base_project_name = project_name or f"Mining{mining.num:02d}_{mining.asset}_{mining.tf}_{resolved_bs}"
    trading_window = _trading_window_for(capa, mining.tf)

    # Resolver costos: data.db → fallback. Override manual con sqx_data si pasa.
    costs = resolve_costs(mining, sqx_db_path, broker_postfix, alias_override=alias_override)
    if sqx_data:
        costs.update(sqx_data)

    # Aplicar patches a todos los XMLs internos del .cfx
    total_stats = {"files_patched": 0, "charts": 0, "swaps": 0, "sides": 0,
                   "dates": 0, "resources": 0, "paths_cleaned": 0, "commissions": 0,
                   "trading_window": 0, "blocksettings": 0, "costs_source": costs["source"], "symbol": costs["symbol"],
                   "blocksetting": blocksetting_trace(blocksetting_entry)}
    for filename, tree in editor.iter_xml_files():
        if filename == "config.xml":
            continue  # config.xml no contiene Setup nodes
        root = tree.getroot()
        # Determinar el período correcto para este task XML según capa
        period_key = task_map.get(filename, "BUILD")
        period = RETEST_PERIODS[period_key]

        stats = apply_mining_to_xml(
            root,
            symbol=costs["symbol"],
            timeframe=mining.tf,
            direction=mining.dir,
            swap_long=costs["swap_long"],
            swap_short=costs["swap_short"],
            spread=costs["spread"],
            swap_type=costs.get("swap_type"),
            commission_type=costs.get("commission_type"),
            commission_value=costs.get("commission_value"),
            resource={**costs, "asset": mining.asset},
            period=period,
            trading_window=trading_window,
            clean_paths=True,
        )
        if apply_blocksetting_to_xml(root, blocksetting_entry):
            total_stats["blocksettings"] += 1
        editor.update_xml(filename, tree)
        total_stats["files_patched"] += 1
        for k in ("charts", "swaps", "sides", "dates", "resources", "paths_cleaned", "commissions", "trading_window"):
            total_stats[k] += stats[k]

    # Renombrar el proyecto en config.xml (incluye capa en el nombre)
    if editor.has("config.xml"):
        config_tree = editor.parse_xml("config.xml")
        config_root = config_tree.getroot()
        config_root.set("name", f"{base_project_name}_Capa{capa}")
        build_title = _build_task_title(resolved_bs, capa, mining.dir, mining.tf)
        for task in config_root.findall(".//Task"):
            if task.get("type") == "Build":
                task.set("title", build_title)
        editor.update_xml("config.xml", config_tree)

    # Guardar el .cfx
    out_name = f"{base_project_name}_Capa{capa}{suffix}.cfx"
    out_path = os.path.abspath(os.path.join(output_dir, out_name))
    if overwrite and os.path.isfile(out_path):
        backup_dir = os.path.join(output_dir, "__cfx_backups")
        os.makedirs(backup_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = os.path.splitext(out_name)[0]
        backup_path = os.path.join(backup_dir, f"{stem}.{stamp}.cfx")
        counter = 2
        while os.path.exists(backup_path):
            backup_path = os.path.join(backup_dir, f"{stem}.{stamp}.{counter}.cfx")
            counter += 1
        shutil.copy2(out_path, backup_path)
    editor.save(out_path, overwrite=overwrite)
    return out_path
