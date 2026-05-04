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
ASSET_DEFAULTS = _INSTRUMENTS_PROFILE.get("assetDefaults") or {}
DEFAULT_BROKER_POSTFIX = (
    _INSTRUMENTS_PROFILE.get("defaultBrokerPostfix")
    or _GENERATOR_PROFILE.get("defaultBrokerPostfix")
    or "_darwinex"
)


def _symbol_for_sqx(asset: str, postfix: str = DEFAULT_BROKER_POSTFIX) -> str:
    """Convierte 'XAUUSD' a 'XAUUSD_darwinex' (o el postfix del broker en uso)."""
    return f"{asset}{postfix}"


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
                info = db.get_symbol_info(mining.asset, alias_override=alias_override)
                if info.get("source") == "db":
                    # Si broker_postfix es None (SQX 139), no usar postfix
                    pf = info.get("broker_postfix")
                    if pf is None:
                        pf = ""
                    return {
                        "source": "db",
                        "instrument": info["instrument"],
                        "symbol": _symbol_for_sqx(info["instrument"], pf) if pf else info["instrument"],
                        "spread": info.get("spread"),
                        "slippage": info.get("slippage"),
                        "swap_long": info.get("swap_long") if info.get("swap_long") is not None else 0.0,
                        "swap_short": info.get("swap_short") if info.get("swap_short") is not None else 0.0,
                        "swap_type": info.get("swap_type"),
                        "commission_type": info.get("commission_type"),
                        "commission_value": info.get("commission_value"),
                        "broker_postfix": pf,
                    }
            finally:
                db.close()
        except Exception:
            pass  # caer a fallback

    # 2) Fallback a ASSET_DEFAULTS
    d = ASSET_DEFAULTS.get(mining.asset, {"spread": 10, "swap_long": -1.0, "swap_short": -1.0})
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

    Returns:
        Path absoluto al .cfx generado.
    """
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    if capa not in CAPA_TASK_MAPS:
        raise ValueError(f"capa must be 1 or 2, got {capa}")

    editor = CfxEditor(template_path)
    task_map = CAPA_TASK_MAPS[capa]

    # Resolver costos: data.db → fallback. Override manual con sqx_data si pasa.
    costs = resolve_costs(mining, sqx_db_path, broker_postfix, alias_override=alias_override)
    if sqx_data:
        costs.update(sqx_data)

    # Aplicar patches a todos los XMLs internos del .cfx
    total_stats = {"files_patched": 0, "charts": 0, "swaps": 0, "sides": 0,
                   "dates": 0, "paths_cleaned": 0, "commissions": 0,
                   "costs_source": costs["source"], "symbol": costs["symbol"]}
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
            period=period,
            clean_paths=True,
        )
        editor.update_xml(filename, tree)
        total_stats["files_patched"] += 1
        for k in ("charts", "swaps", "sides", "dates", "paths_cleaned", "commissions"):
            total_stats[k] += stats[k]

    # Renombrar el proyecto en config.xml (incluye capa en el nombre)
    if editor.has("config.xml"):
        config_tree = editor.parse_xml("config.xml")
        config_tree.getroot().set("name", f"{mining.name}_Capa{capa}")
        editor.update_xml("config.xml", config_tree)

    # Guardar el .cfx
    out_name = f"{mining.name}_Capa{capa}{suffix}.cfx"
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
