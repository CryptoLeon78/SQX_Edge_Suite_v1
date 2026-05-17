"""
xml_patcher.py — patches específicos sobre los XMLs internos de un .cfx.

Cada función toma un ElementTree (root) y aplica un cambio puntual.
Se aplican sobre TODOS los Setup nodes encontrados (Build + Retest + AutomaticRetest),
para que el .cfx sea coherente extremo a extremo.
"""
from __future__ import annotations

from typing import Optional
from xml.etree import ElementTree as ET

from .config_loader import load_manifest

_GENERATOR_PROFILE = load_manifest("generator_profiles.json")
RETEST_PERIODS = {
    key: tuple(value)
    for key, value in (_GENERATOR_PROFILE.get("retestPeriods") or {}).items()
}


# ── Helpers ───────────────────────────────────────────────────────
def _all_setups(root: ET.Element) -> list[ET.Element]:
    """Devuelve todos los nodos <Setup> encontrados en el XML."""
    return root.findall(".//Setup")


def _all_charts(root: ET.Element) -> list[ET.Element]:
    return root.findall(".//Setup/Chart")


def _all_swaps(root: ET.Element) -> list[ET.Element]:
    return root.findall(".//Setup/Swap")


def _all_market_sides(root: ET.Element) -> list[ET.Element]:
    return root.findall(".//MarketSides")


def _all_strategy_types(root: ET.Element) -> list[ET.Element]:
    return root.findall(".//StrategyType")


def _format_attr(value, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _decimal_count(tick_size) -> str:
    text = str(tick_size or "")
    if "E-" in text.upper():
        try:
            return str(abs(int(text.upper().split("E-")[-1])))
        except Exception:
            return "0"
    if "." in text:
        return str(len(text.rstrip("0").split(".")[-1]))
    return "0"


def _ensure_resource_broker(resources: ET.Element, resource: dict, broker_id) -> None:
    broker_id_text = _format_attr(broker_id, "")
    if not broker_id_text or broker_id_text in ("-1", "None"):
        return
    brokers = resources.find("Brokers")
    if brokers is None:
        brokers = ET.SubElement(resources, "Brokers")
    broker = None
    for candidate in brokers.findall("Broker"):
        if candidate.get("id") == broker_id_text:
            broker = candidate
            break
    if broker is None:
        broker = ET.SubElement(brokers, "Broker")
    postfix = resource.get("broker_postfix") or "_darwinex"
    broker.set("id", broker_id_text)
    broker.set("name", _format_attr(resource.get("broker_name"), "Darwinex"))
    broker.set("description", _format_attr(resource.get("broker_description"), "Darwinex CFDs" if postfix == "_darwinex" else ""))
    broker.set("timezone", _format_attr(resource.get("broker_timezone"), "EETUS"))
    broker.set("postfix", _format_attr(postfix, ""))
    broker.set("mtUse", "true")
    broker.set("spUse", "false")


def _clear_resource_sessions(resources: ET.Element) -> None:
    """Drop stale session resources inherited from seed projects.

    Generated SQX Edge projects explicitly use "No Session" in every Setup.
    Leaving old Resources/Sessions entries in the .cfx makes SQX 142 prompt for
    missing sessions such as Futures_Commodities1 even though no setup uses them.
    """
    sessions = resources.find("Sessions")
    if sessions is None:
        ET.SubElement(resources, "Sessions")
        return
    for node in list(sessions.findall("Session")):
        sessions.remove(node)


def patch_no_session(root: ET.Element) -> int:
    """Force SQX projects to use No Session consistently.

    SQX stores session intent in multiple places. Some seed projects keep a
    stale BuildTradingOptions/MarketOpenSession even when Setup already says
    "No Session", which triggers the SQX 142 resource resolver. Keep the
    generated project explicit and internally consistent.
    """
    patched = 0
    for setup in _all_setups(root):
        if setup.get("session") != "No Session":
            setup.set("session", "No Session")
            patched += 1
    for param in root.findall(".//BuildTradingOptions/Params/Param[@key='MarketOpenSession']"):
        if (param.text or "") != "No Session":
            param.text = "No Session"
            patched += 1
    for resources in root.findall(".//Resources"):
        before = len(resources.findall("./Sessions/Session"))
        _clear_resource_sessions(resources)
        patched += before
    return patched


# ── Patches por concepto ──────────────────────────────────────────
def patch_symbol_tf_spread(
    root: ET.Element,
    symbol: str,
    timeframe: str,
    spread: Optional[float] = None,
) -> int:
    """Cambia el símbolo + TF (+ spread opcional) en todos los Charts."""
    n = 0
    for chart in _all_charts(root):
        chart.set("symbol", symbol)
        chart.set("timeframe", timeframe)
        if spread is not None:
            chart.set("spread", str(spread))
        n += 1
    return n


def _asset_from_symbol(symbol: str) -> str:
    return (symbol or "").split("_", 1)[0] or "ASSET"


def patch_embedded_strategy_metadata(root: ET.Element, symbol: str, timeframe: str) -> int:
    """Patch symbols stored inside embedded StrategyFile templates.

    Capa 2 seeds can carry a BackupStrategyTemplate with its own Strategy XML.
    SQX may inspect that embedded strategy during project load, so it must not
    keep an old symbol while the visible charts/resources point elsewhere.
    """
    patched = 0
    asset = _asset_from_symbol(symbol)
    safe_tf = (timeframe or "TF").upper()
    strategy_name = f"SQXEDGE_TEMPLATE_{asset}_{safe_tf}"
    strategy_class = "".join(ch if ch.isalnum() else "_" for ch in strategy_name)
    for node in root.findall(".//BackupStrategyTemplate//symbol"):
        if (node.text or "") != symbol:
            node.text = symbol
            patched += 1
    for node in root.findall(".//BackupStrategyTemplate//StrategyName"):
        if (node.text or "") != strategy_name:
            node.text = strategy_name
            patched += 1
    for node in root.findall(".//BackupStrategyTemplate//StrategyClassName"):
        if (node.text or "") != strategy_class:
            node.text = strategy_class
            patched += 1
    return patched


def patch_symbol_resources(root: ET.Element, resource: Optional[dict]) -> int:
    """Rebuilds <Resources><Symbols> so SQX can resolve the generated chart symbol."""
    if not resource or not resource.get("symbol"):
        return 0
    patched = 0
    for resources in root.findall(".//Resources"):
        _clear_resource_sessions(resources)
        symbols = resources.find("Symbols")
        if symbols is None:
            symbols = ET.SubElement(resources, "Symbols")
        existing = list(symbols.findall("Symbol"))
        template_symbol = existing[0] if existing else None
        template_info = template_symbol.find("InstrumentInfo") if template_symbol is not None else None
        base_attrs = dict(template_symbol.attrib) if template_symbol is not None else {}
        info_attrs = dict(template_info.attrib) if template_info is not None else {}
        for node in existing:
            symbols.remove(node)

        broker_id = resource.get("broker_id")
        if broker_id is None or str(broker_id) in ("", "-1"):
            broker_id = base_attrs.get("broker") or 4
        source = broker_id if str(broker_id) not in ("", "-1", "None") else base_attrs.get("source", "4")
        _ensure_resource_broker(resources, resource, broker_id)
        date_from = resource.get("date_from_ms")
        date_to = resource.get("date_to_ms")
        if date_from is None:
            date_from = "0"
        if date_to is None:
            date_to = "0"
        timezone = resource.get("broker_timezone") or base_attrs.get("timezone") or "EETUS"
        u_symbol = resource.get("u_symbol") or resource.get("asset") or resource.get("instrument") or resource.get("symbol")
        u_symbol_name = resource.get("u_symbol_name") or u_symbol

        symbol_node = ET.SubElement(symbols, "Symbol")
        symbol_node.attrib.update({
            "name": _format_attr(resource.get("symbol")),
            "source": _format_attr(source, "4"),
            "barType": base_attrs.get("barType", "1"),
            "precision": base_attrs.get("precision", "TICK"),
            "timezone": _format_attr(timezone, "EETUS"),
            "dateFrom": _format_attr(date_from, "0"),
            "dateTo": _format_attr(date_to, "0"),
            "uSymbol": _format_attr(u_symbol),
            "uSymbolName": _format_attr(u_symbol_name),
            "removeWeekends": base_attrs.get("removeWeekends", "false"),
            "broker": _format_attr(broker_id, "4"),
        })

        instrument_info = ET.SubElement(symbol_node, "InstrumentInfo")
        tick_size = resource.get("tick_size") or info_attrs.get("tickSize")
        tick_step = resource.get("tick_step") or info_attrs.get("tickStep")
        instrument_info.attrib.update(info_attrs)
        instrument_info.attrib.update({
            "instrument": _format_attr(resource.get("instrument") or resource.get("symbol")),
            "description": _format_attr(resource.get("description"), info_attrs.get("description", "")),
            "tickSize": _format_attr(tick_size, info_attrs.get("tickSize", "")),
            "tickStep": _format_attr(tick_step, info_attrs.get("tickStep", "")),
            "minDistance": _format_attr(resource.get("min_distance"), info_attrs.get("minDistance", "0.0")),
            "tickValueInMoney": info_attrs.get("tickValueInMoney", "0.0"),
            "dateFrom": _format_attr(date_from, info_attrs.get("dateFrom", "0")),
            "dateTo": _format_attr(date_to, info_attrs.get("dateTo", "0")),
            "rows": _format_attr(resource.get("rows"), info_attrs.get("rows", "0")),
            "defaultSpread": _format_attr(resource.get("spread"), info_attrs.get("defaultSpread", "")),
            "defaultSlippage": _format_attr(resource.get("slippage"), info_attrs.get("defaultSlippage", "0.0")),
            "decimals": info_attrs.get("decimals") or _decimal_count(tick_size),
            "pointValue": _format_attr(resource.get("point_value"), info_attrs.get("pointValue", "")),
            "dataType": _format_attr(resource.get("data_type"), info_attrs.get("dataType", "3")),
            "recognizedFromOrders": info_attrs.get("recognizedFromOrders", "false"),
            "exchange": _format_attr(resource.get("exchange"), info_attrs.get("exchange", "")),
            "country": _format_attr(resource.get("country"), info_attrs.get("country", "")),
            "sector": _format_attr(resource.get("sector"), info_attrs.get("sector", "")),
            "orderSizeMultiplier": _format_attr(resource.get("ordersize_multiplier"), info_attrs.get("orderSizeMultiplier", "1.0")),
            "orderSizeStep": _format_attr(resource.get("ordersize_step"), info_attrs.get("orderSizeStep", "0.01")),
            "broker": _format_attr(resource.get("broker_id"), info_attrs.get("broker", "-1")),
        })
        if resource.get("commissions_xml"):
            instrument_info.set("commissions", resource["commissions_xml"])
        if resource.get("swap_xml"):
            instrument_info.set("swap", resource["swap_xml"])
        patched += 1
    return patched


def patch_swap(root: ET.Element, swap_long: float, swap_short: float,
               swap_type: Optional[str] = None) -> int:
    """Cambia los swap long/short (+ type opcional 'money'|'points') en todos los Setup."""
    n = 0
    for swap in _all_swaps(root):
        swap.set("long", str(swap_long))
        swap.set("short", str(swap_short))
        if swap_type:
            swap.set("type", swap_type)
        n += 1
    return n


def patch_commission(root: ET.Element, ctype: str, value: float) -> int:
    """
    Cambia la comisión en todos los Setup.
    SQX representa comisiones con varios <Method> (PercentageBased, SizeBased, ...)
    y solo uno tiene use="true". Ajustamos el activo o lo cambiamos.
    """
    n = 0
    for setup in _all_setups(root):
        comm = setup.find("Commissions")
        if comm is None:
            continue
        # Desactivar todos los Methods
        for m in comm.findall("Method"):
            m.set("use", "false")
        # Buscar el del tipo deseado, o crear si no existe
        target = comm.find(f"Method[@type='{ctype}']")
        if target is None:
            # Crear nuevo
            target = ET.SubElement(comm, "Method")
            target.set("type", ctype)
            params_node = ET.SubElement(target, "Params")
            param = ET.SubElement(params_node, "Param")
            param.set("key", "Commission")
            param.set("className", ctype)
            param.text = str(value)
        else:
            # Actualizar valor del Param key="Commission"
            param = target.find("Params/Param[@key='Commission']")
            if param is not None:
                param.text = str(value)
        target.set("use", "true")
        n += 1
    return n


def patch_direction(root: ET.Element, direction: str) -> int:
    """direction ∈ {'long', 'short', 'both'}."""
    if direction not in ("long", "short", "both"):
        raise ValueError(f"direction must be long|short|both, got {direction!r}")
    n = 0
    for ms in _all_market_sides(root):
        ms.set("type", direction)
    n += len(_all_market_sides(root))
    return n


def patch_dates(
    root: ET.Element,
    date_from: str,
    date_to: str,
) -> int:
    """Setea dateFrom/dateTo en TODOS los Setup del XML."""
    n = 0
    for setup in _all_setups(root):
        setup.set("dateFrom", date_from)
        setup.set("dateTo", date_to)
        n += 1
    return n


def clean_external_paths(root: ET.Element) -> int:
    """
    Quita los paths absolutos del PC original en <StrategyType>.
    El usuario tendrá que re-seleccionarlos manualmente en SQX Builder
    (templateFile y strategyFile), pero al menos no apuntan a un PC ajeno.
    """
    n = 0
    for st in _all_strategy_types(root):
        for attr in ("templateFile", "strategyFile"):
            if st.get(attr):
                st.set(attr, "")
                n += 1
    return n


# ── Aplicar tal y como el cheatsheet pide por mining ──────────────
def apply_mining_to_xml(
    root: ET.Element,
    symbol: str,
    timeframe: str,
    direction: str,
    swap_long: float,
    swap_short: float,
    spread: Optional[float] = None,
    swap_type: Optional[str] = None,
    commission_type: Optional[str] = None,
    commission_value: Optional[float] = None,
    resource: Optional[dict] = None,
    period: tuple[str, str] = RETEST_PERIODS["BUILD"],
    clean_paths: bool = True,
) -> dict:
    """Aplica el set completo de patches por mining a un XML root."""
    stats = {
        "sessions": patch_no_session(root),
        "charts": patch_symbol_tf_spread(root, symbol, timeframe, spread),
        "embedded_strategy": patch_embedded_strategy_metadata(root, symbol, timeframe),
        "swaps": patch_swap(root, swap_long, swap_short, swap_type),
        "sides": patch_direction(root, direction),
        "dates": patch_dates(root, period[0], period[1]),
        "resources": patch_symbol_resources(root, resource),
        "paths_cleaned": clean_external_paths(root) if clean_paths else 0,
        "commissions": 0,
    }
    if commission_type and commission_value is not None:
        stats["commissions"] = patch_commission(root, commission_type, commission_value)
    return stats
