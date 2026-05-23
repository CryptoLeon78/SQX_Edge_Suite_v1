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
CROSS_BROKER_RETESTS = {
    int(capa): value
    for capa, value in (_GENERATOR_PROFILE.get("crossBrokerRetests") or {}).items()
}
ADAPTIVE_SPREAD_STRESS = {
    int(capa): value
    for capa, value in (_GENERATOR_PROFILE.get("adaptiveSpreadStress") or {}).items()
}
BROKER_PROFILES = _GENERATOR_PROFILE.get("brokerProfiles") or {}
TARGET_PROFILES = _GENERATOR_PROFILE.get("targetProfiles") or {}
ASSET_DEFAULTS = _INSTRUMENTS_PROFILE.get("assetDefaults") or {}
DEFAULT_BROKER_POSTFIX = (
    _INSTRUMENTS_PROFILE.get("defaultBrokerPostfix")
    or _GENERATOR_PROFILE.get("defaultBrokerPostfix")
    or "_darwinex"
)
DEFAULT_TARGET_PROFILE_ID = "sq_default_exact"


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


def _spread_stress_for(capa: int, filename: str) -> Optional[tuple[float, float]]:
    layer = ADAPTIVE_SPREAD_STRESS.get(capa) or {}
    value = layer.get(filename)
    if not isinstance(value, dict):
        return None
    try:
        min_multiplier = float(value.get("minMultiplier"))
        max_multiplier = float(value.get("maxMultiplier"))
    except (TypeError, ValueError):
        return None
    if min_multiplier <= 0 or max_multiplier <= 0 or min_multiplier > max_multiplier:
        return None
    return min_multiplier, max_multiplier


def _build_task_title(blocksetting_id: str, capa: int, direction: str, timeframe: str) -> str:
    tf = (timeframe or "TF").upper()
    return f"Build {blocksetting_id} · Capa{capa} {_direction_label(direction)} {tf}"


def _clean_profile_value(value, default=None):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _int_profile_value(value, default=None):
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _profile_from_broker(profile_id: str | None) -> dict:
    raw = BROKER_PROFILES.get(profile_id or "") or {}
    return {
        "brokerProfile": raw.get("id") or profile_id or "",
        "brokerPostfix": raw.get("brokerPostfix"),
        "brokerId": raw.get("brokerId"),
        "sourceId": raw.get("sourceId"),
        "brokerName": raw.get("brokerName"),
        "brokerDescription": raw.get("brokerDescription"),
        "timezone": raw.get("timezone"),
        "precision": raw.get("precision") or "TICK",
        "label": raw.get("label") or profile_id or "",
    }


def _format_symbol_template(template: str | None, asset: str) -> str | None:
    if not template:
        return None
    try:
        return str(template).format(asset=asset, assetUpper=(asset or "").upper(), assetLower=(asset or "").lower())
    except Exception:
        return str(template)


def normalize_target_profile(target_profile=None, broker_postfix: str = DEFAULT_BROKER_POSTFIX) -> dict:
    """Resolve a generation target profile into the fields used by XML patching.

    The public UI can send either a profile id or `{id, custom}`. Custom mode is
    intentionally conservative: it remaps symbols only with explicit broker
    fields supplied by the operator/user; otherwise it falls back to the SQX Edge
    Darwinex server profile.
    """
    raw = target_profile or DEFAULT_TARGET_PROFILE_ID
    if isinstance(raw, str):
        profile_id = raw or DEFAULT_TARGET_PROFILE_ID
        custom = {}
    elif isinstance(raw, dict):
        profile_id = str(raw.get("id") or raw.get("profile") or DEFAULT_TARGET_PROFILE_ID)
        custom = raw.get("custom") if isinstance(raw.get("custom"), dict) else raw
        if profile_id not in TARGET_PROFILES and (
            raw.get("brokerProfile") or raw.get("brokerPostfix") or raw.get("brokerId") or raw.get("sourceId")
        ):
            broker_profile_id = str(raw.get("brokerProfile") or raw.get("id") or "")
            direct = _profile_from_broker(broker_profile_id)
            direct.update({
                "id": profile_id,
                "label": raw.get("label") or direct.get("label") or profile_id,
                "mode": raw.get("mode") or "direct_profile",
                "warning": raw.get("warning") or "",
            })
            for key in ("brokerPostfix", "brokerId", "sourceId", "brokerName", "brokerDescription", "timezone", "precision", "symbol", "dataType"):
                if raw.get(key) is not None:
                    direct[key] = raw.get(key)
            if raw.get("brokerName") and not raw.get("brokerDescription"):
                direct["brokerDescription"] = _clean_profile_value(raw.get("brokerName"), "User broker")
            if not direct.get("timezone"):
                direct["timezone"] = "EETUS"
            if not direct.get("precision"):
                direct["precision"] = "TICK"
            return direct
    else:
        profile_id = DEFAULT_TARGET_PROFILE_ID
        custom = {}

    profile = dict(TARGET_PROFILES.get(profile_id) or TARGET_PROFILES.get(DEFAULT_TARGET_PROFILE_ID) or {})
    broker_profile_id = str(profile.get("brokerProfile") or "darwinex")
    resolved = _profile_from_broker(broker_profile_id)
    resolved.update({
        "id": profile.get("id") or profile_id,
        "label": profile.get("label") or resolved.get("label") or profile_id,
        "mode": profile.get("mode") or "server_default",
        "warning": profile.get("warning") or "",
    })
    for key in (
        "brokerPostfix",
        "brokerId",
        "sourceId",
        "brokerName",
        "brokerDescription",
        "timezone",
        "precision",
        "dataType",
        "symbol",
        "symbolTemplate",
        "forceExactSymbol",
    ):
        if profile.get(key) is not None:
            resolved[key] = profile.get(key)

    if resolved["id"] == "custom_user_broker":
        custom_postfix = _clean_profile_value(custom.get("brokerPostfix") or custom.get("postfix"))
        custom_symbol = _clean_profile_value(custom.get("symbol"))
        if custom_postfix is not None:
            resolved["brokerPostfix"] = custom_postfix
        if custom_symbol is not None:
            resolved["symbol"] = custom_symbol
        for key, source_key in (("brokerId", "brokerId"), ("sourceId", "sourceId")):
            value = _int_profile_value(custom.get(source_key))
            if value is not None:
                resolved[key] = value
        for key, source_key in (
            ("brokerName", "brokerName"),
            ("brokerDescription", "brokerDescription"),
            ("timezone", "timezone"),
            ("precision", "precision"),
        ):
            value = _clean_profile_value(custom.get(source_key))
            if value is not None:
                resolved[key] = value
        if custom.get("brokerName") and not custom.get("brokerDescription"):
            resolved["brokerDescription"] = _clean_profile_value(custom.get("brokerName"), "User broker")

    if resolved.get("brokerPostfix") is None:
        resolved["brokerPostfix"] = broker_postfix
    if not resolved.get("brokerPostfix") and not resolved.get("symbol"):
        resolved["brokerPostfix"] = broker_postfix
    if not resolved.get("timezone"):
        resolved["timezone"] = "EETUS"
    if not resolved.get("precision"):
        resolved["precision"] = "TICK"
    return resolved


def public_target_profile(profile: dict) -> dict:
    data = profile or {}
    return {
        "id": data.get("id"),
        "label": data.get("label"),
        "mode": data.get("mode"),
        "brokerPostfix": data.get("brokerPostfix"),
        "brokerId": data.get("brokerId"),
        "sourceId": data.get("sourceId"),
        "symbol": data.get("symbol"),
        "symbolTemplate": data.get("symbolTemplate"),
        "forceExactSymbol": bool(data.get("forceExactSymbol")),
        "dataType": data.get("dataType"),
        "warning": data.get("warning"),
    }


def _cross_broker_retest(capa: int, filename: str) -> Optional[dict]:
    layer = CROSS_BROKER_RETESTS.get(capa) or {}
    value = layer.get(filename)
    return value if isinstance(value, dict) else None


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


def resolve_costs(
    mining: Mining,
    sqx_db_path: Optional[str],
    postfix: str = DEFAULT_BROKER_POSTFIX,
    alias_override: Optional[dict] = None,
    target_profile: Optional[dict] = None,
) -> dict:
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
    profile = normalize_target_profile(target_profile, postfix) if target_profile else normalize_target_profile(
        DEFAULT_TARGET_PROFILE_ID,
        postfix,
    )
    force_exact_symbol = bool(profile.get("forceExactSymbol"))
    profile_postfix = profile.get("brokerPostfix")
    postfix = "" if force_exact_symbol and profile_postfix == "" else (profile_postfix if profile_postfix is not None else (postfix or ""))
    explicit_symbol = profile.get("symbol") or _format_symbol_template(profile.get("symbolTemplate"), mining.asset)

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
                    pf = postfix if force_exact_symbol else (info.get("broker_postfix") or postfix or "")
                    broker_id = profile.get("brokerId") if (force_exact_symbol or (profile.get("id") == "custom_user_broker" and profile.get("brokerId") is not None)) else info.get("broker_id")
                    source_id = profile.get("sourceId")
                    broker_name = profile.get("brokerName") or info.get("broker_name")
                    broker_description = profile.get("brokerDescription") or info.get("broker_description")
                    broker_timezone = profile.get("timezone") or info.get("broker_timezone") or "EETUS"
                    resolved_symbol = explicit_symbol or info.get("data_symbol") or (_symbol_for_sqx(info["instrument"], pf) if pf else info["instrument"])
                    resolved_instrument = resolved_symbol if force_exact_symbol else info["instrument"]
                    profile_data_type = profile.get("dataType")
                    return {
                        "source": "db",
                        "instrument": resolved_instrument,
                        "symbol": resolved_symbol,
                        "spread": info.get("spread"),
                        "slippage": info.get("slippage"),
                        "swap_long": info.get("swap_long") if info.get("swap_long") is not None else 0.0,
                        "swap_short": info.get("swap_short") if info.get("swap_short") is not None else 0.0,
                        "swap_type": info.get("swap_type"),
                        "commission_type": info.get("commission_type"),
                        "commission_value": info.get("commission_value"),
                        "broker_postfix": pf,
                        "broker_id": broker_id,
                        "source_id": source_id,
                        "broker_name": broker_name,
                        "broker_description": broker_description,
                        "broker_timezone": broker_timezone,
                        "target_profile": public_target_profile(profile),
                        "data_type": profile_data_type if profile_data_type is not None else info.get("data_type"),
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
    fallback_symbol = explicit_symbol or (_symbol_for_sqx(mining.asset, postfix) if postfix else mining.asset)
    return {
        "source": "fallback",
        "instrument": fallback_symbol if force_exact_symbol else mining.asset,
        "symbol": fallback_symbol,
        "spread": d["spread"],
        "slippage": 0,
        "swap_long": d["swap_long"],
        "swap_short": d["swap_short"],
        "swap_type": None,
        "commission_type": d.get("commission_type", "SizeBased") if isinstance(d, dict) else "SizeBased",
        "commission_value": d.get("commission_value", 0.0) if isinstance(d, dict) else 0.0,
        "broker_postfix": postfix,
        "broker_id": profile.get("brokerId"),
        "source_id": profile.get("sourceId"),
        "broker_name": profile.get("brokerName"),
        "broker_description": profile.get("brokerDescription"),
        "broker_timezone": profile.get("timezone"),
        "target_profile": public_target_profile(profile),
        "data_type": profile.get("dataType") if profile.get("dataType") is not None else shape["data_type"],
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
    target_profile: Optional[dict] = None,
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
    resolved_target_profile = normalize_target_profile(target_profile, broker_postfix)

    # Resolver costos: data.db → fallback. Override manual con sqx_data si pasa.
    costs = resolve_costs(
        mining,
        sqx_db_path,
        broker_postfix,
        alias_override=alias_override,
        target_profile=resolved_target_profile,
    )
    if sqx_data:
        costs.update(sqx_data)

    # Aplicar patches a todos los XMLs internos del .cfx
    total_stats = {"files_patched": 0, "charts": 0, "swaps": 0, "sides": 0,
                   "dates": 0, "resources": 0, "paths_cleaned": 0, "commissions": 0, "spread_stress": 0,
                   "trading_window": 0, "blocksettings": 0, "costs_source": costs["source"], "symbol": costs["symbol"],
                   "blocksetting": blocksetting_trace(blocksetting_entry)}
    for filename, tree in editor.iter_xml_files():
        if filename == "config.xml":
            continue  # config.xml no contiene Setup nodes
        root = tree.getroot()
        # Determinar el período correcto para este task XML según capa
        period_key = task_map.get(filename, "BUILD")
        period = RETEST_PERIODS[period_key]
        active_costs = costs
        cross_retest = _cross_broker_retest(capa, filename)
        if cross_retest:
            broker_profile_id = str(cross_retest.get("brokerProfile") or "")
            cross_profile = _profile_from_broker(broker_profile_id)
            cross_profile.update({
                "id": broker_profile_id,
                "mode": "methodology_cross_broker",
                "warning": cross_retest.get("label") or "",
            })
            active_costs = resolve_costs(
                mining,
                sqx_db_path,
                str(cross_profile.get("brokerPostfix") or broker_postfix),
                alias_override=alias_override,
                target_profile=cross_profile,
            )
            cross_period_key = str(cross_retest.get("period") or period_key)
            period = RETEST_PERIODS.get(cross_period_key, period)

        stats = apply_mining_to_xml(
            root,
            symbol=active_costs["symbol"],
            timeframe=mining.tf,
            direction=mining.dir,
            swap_long=active_costs["swap_long"],
            swap_short=active_costs["swap_short"],
            spread=active_costs["spread"],
            swap_type=active_costs.get("swap_type"),
            commission_type=active_costs.get("commission_type"),
            commission_value=active_costs.get("commission_value"),
            resource={**active_costs, "asset": mining.asset},
            period=period,
            trading_window=trading_window,
            spread_stress_multipliers=_spread_stress_for(capa, filename),
            clean_paths=True,
        )
        if apply_blocksetting_to_xml(root, blocksetting_entry):
            total_stats["blocksettings"] += 1
        editor.update_xml(filename, tree)
        total_stats["files_patched"] += 1
        for k in ("charts", "swaps", "sides", "dates", "resources", "paths_cleaned", "commissions", "trading_window", "spread_stress"):
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
