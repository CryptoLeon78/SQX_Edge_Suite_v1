from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


VERSION = "sqx142-project-resource-repair-v1"
DAY_MS = 24 * 60 * 60 * 1000
TARGET_PROJECTS = (
    "Capa1_Long_SQX142_Base",
    "Capa2_Base_SQX142_Base",
    "IMOX XAU H1 2025(2)",
    "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2",
)
CONFIG_TEMPLATE_REFERENCE_RESTORE = {
    ("Capa1_Long_SQX142_Base", "Build-Task1.xml"): "",
    ("Capa2_Base_SQX142_Base", "Build-Task1.xml"): "",
    (
        "Capa2_Base_SQX142_Base",
        "AutomaticRetest-Task8.xml",
    ): "",
}
BASE_PROJECTS_NEUTRAL_IMPROVE_DATABANK = {
    "Capa1_Long_SQX142_Base",
    "Capa2_Base_SQX142_Base",
}
BASE_PROJECT_CLEAN_DONORS = {
    "Capa1_Long_SQX142_Base": "Capa1_Long_SQX142_Base(2)",
}
CLEAN_DONOR_REBUILDS = {
    "Capa1_Long_SQX142_Base": {
        "donor": "Capa1_Long_SQX142_Base(2)",
    },
    "Capa2_Base_SQX142_Base": {
        "donor": "Mining01_USDJPY_H1_BS_Volatilidad_v6_intraday_v6_LS_Capa2",
        "fromSymbol": "USDJPY_darwinex",
        "toSymbol": "AUDCAD_darwinex",
    },
}
CLEAN_LOAD_CONFIG_PROJECTS = {
    "Capa2_Base_SQX142_Base",
}
SQX142_CLEAN_PROJECT_VERSION = "142.2336"
NEUTRAL_IMPROVE_DATABANK = "Strategies to improve"
BASE_PROJECT_DATE_CAPS = {
    ("Capa1_Long_SQX142_Base", "Retest-Task1.xml"): {
        "dateFromMs": "1506902400000",
        "dateToMs": "1775606400000",
        "dateTo": "2026.04.08",
    },
    ("Capa2_Base_SQX142_Base", "AutomaticRetest-Task7.xml"): {
        "dateFromMs": "1506902400000",
        "dateToMs": "1777507200000",
        "dateTo": "2026.04.30",
    },
}
DEFAULT_SQX_ROOT = Path(os.environ.get("SQX142_ROOT", "<LOCAL_SQX142_ROOT>"))
BLOCKED_SURFACES = (
    "jars",
    "plugins",
    "license/activation",
    "data.db writes",
    "databank deletion",
    "run_project",
    "Migration Tool",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_zip_text(cfx: Path, entry: str) -> str:
    with zipfile.ZipFile(cfx) as archive:
        return archive.read(entry).decode("utf-8-sig")


def _java_double_text(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number != 0 and abs(number) < 0.001:
        text = f"{number:.1E}"
        text = text.replace("E-0", "E-").replace("E+0", "E")
        return text
    return str(number)


def _replace_file_with_retry(temp: Path, destination: Path) -> None:
    last_error: Exception | None = None
    for _ in range(5):
        try:
            os.replace(temp, destination)
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.5)
    try:
        shutil.copy2(temp, destination)
        temp.unlink()
        return
    except Exception as exc:
        raise RuntimeError(f"Failed to replace {destination}: {last_error or exc}") from exc


def _write_zip_texts(cfx: Path, replacements: dict[str, str]) -> None:
    temp = cfx.with_name(f"{cfx.name}.sqxedge_repair_tmp")
    with zipfile.ZipFile(cfx, "r") as source, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename in replacements:
                data = replacements[item.filename].encode("utf-8")
            target.writestr(item, data)
    _replace_file_with_retry(temp, cfx)


def _rewrite_project_name(config_text: str, target_project: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(config_text)
    previous = root.get("name") or ""
    if previous == target_project:
        return config_text, []
    root.set("name", target_project)
    return ET.tostring(root, encoding="unicode"), [
        {
            "code": "rewrite_clean_donor_project_name",
            "from": previous,
            "to": target_project,
        }
    ]


def _write_clean_donor_project(donor_cfx: Path, target_cfx: Path, target_project: str) -> list[dict[str, str]]:
    temp = target_cfx.with_name(f"{target_cfx.name}.sqxedge_rebuild_tmp")
    changes: list[dict[str, str]] = []
    with zipfile.ZipFile(donor_cfx, "r") as source, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "config.xml":
                text = data.decode("utf-8-sig")
                patched, name_changes = _rewrite_project_name(text, target_project)
                if name_changes:
                    data = patched.encode("utf-8")
                    changes.extend({"entry": "config.xml", **change} for change in name_changes)
            target.writestr(item, data)
    _replace_file_with_retry(temp, target_cfx)
    with zipfile.ZipFile(target_cfx) as archive:
        archive.testzip()
    return changes


def _replace_symbol_tokens(value: str | None, replacements: dict[str, str]) -> tuple[str | None, bool]:
    if value is None:
        return value, False
    updated = value
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    return updated, updated != value


def _patch_donor_symbol_family(
    text: str,
    from_symbol: str,
    resource: dict[str, str],
) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    from_asset = from_symbol.split("_", 1)[0]
    replacements = {
        from_symbol: resource["symbol"],
        from_asset: resource["uSymbol"],
    }
    changes: list[dict[str, str]] = []
    token_replacements = 0
    for node in root.iter():
        for attr, value in list(node.attrib.items()):
            updated, changed = _replace_symbol_tokens(value, replacements)
            if changed and updated is not None:
                node.set(attr, updated)
                token_replacements += 1
        updated_text, text_changed = _replace_symbol_tokens(node.text, replacements)
        if text_changed:
            node.text = updated_text
            token_replacements += 1
    if token_replacements:
        changes.append(
            {
                "code": "rewrite_clean_donor_symbol_tokens",
                "from": from_symbol,
                "to": resource["symbol"],
                "count": str(token_replacements),
            }
        )

    for chart in root.findall(".//Setup/Chart"):
        if chart.get("symbol") == resource["symbol"]:
            if chart.get("spread") != resource["defaultSpread"]:
                chart.set("spread", resource["defaultSpread"])
                changes.append({"code": "align_clean_donor_chart_spread", "symbol": resource["symbol"]})

    for resources in root.findall(".//Resources"):
        for symbol in resources.findall("./Symbols/Symbol"):
            if symbol.get("name") != resource["symbol"]:
                continue
            previous_period = f"{symbol.get('dateFrom') or ''}..{symbol.get('dateTo') or ''}"
            bounded_from, bounded_to, period_changed = _bounded_dates_for_local_data(
                symbol.get("dateFrom"),
                symbol.get("dateTo"),
                resource,
            )
            symbol.set("source", resource["source"])
            symbol.set("barType", symbol.get("barType") or "1")
            symbol.set("precision", resource["precision"])
            symbol.set("timezone", resource["timezone"])
            symbol.set("dateFrom", bounded_from)
            symbol.set("dateTo", bounded_to)
            symbol.set("uSymbol", resource["uSymbol"])
            symbol.set("uSymbolName", resource["uSymbolName"])
            symbol.set("removeWeekends", symbol.get("removeWeekends") or "false")
            symbol.set("broker", resource["broker"])
            info = symbol.find("InstrumentInfo")
            if info is None:
                info = ET.SubElement(symbol, "InstrumentInfo")
            _set_instrument_info_attrs(info, resource)
            _ensure_broker(resources, resource)
            _sync_standalone_instrument(resources, resource)
            changes.append({"code": "align_clean_donor_resource_metadata", "symbol": resource["symbol"]})
            if period_changed:
                changes.append(
                    {
                        "code": "bound_clean_donor_resource_dates_to_data_db",
                        "symbol": resource["symbol"],
                        "from": previous_period,
                        "to": f"{bounded_from}..{bounded_to}",
                    }
                )

    if not changes:
        return text, []
    patched = ET.tostring(root, encoding="unicode")
    patched, broker_changes = _prune_unused_resource_brokers(patched)
    return patched, changes + broker_changes


def _write_normalized_clean_donor_project(
    donor_cfx: Path,
    target_cfx: Path,
    target_project: str,
    from_symbol: str,
    resource: dict[str, str],
) -> list[dict[str, str]]:
    temp = target_cfx.with_name(f"{target_cfx.name}.sqxedge_rebuild_tmp")
    changes: list[dict[str, str]] = []
    with zipfile.ZipFile(donor_cfx, "r") as source, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8-sig")
                if item.filename == "config.xml":
                    text, name_changes = _rewrite_project_name(text, target_project)
                    changes.extend({"entry": item.filename, **change} for change in name_changes)
                text, symbol_changes = _patch_donor_symbol_family(text, from_symbol, resource)
                changes.extend({"entry": item.filename, **change} for change in symbol_changes)
                data = text.encode("utf-8")
            target.writestr(item, data)
    _replace_file_with_retry(temp, target_cfx)
    with zipfile.ZipFile(target_cfx) as archive:
        archive.testzip()
    return changes


def _resource_from_db(sqx_root: Path, symbol: str) -> dict[str, str]:
    db_path = sqx_root / "user" / "data" / "data.db"
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        data = con.execute(
            """
            select SYMBOL, INSTRUMENT, TIMEFRAME, TIMEZONE, DATEFROM, DATETO,
                   DATATYPE, ROWS, DECIMALS, SOURCE, USYMBOL, USYMBOLNAME, BROKER_ID
            from DATA
            where SYMBOL = ?
            """,
            (symbol,),
        ).fetchone()
        if data is None:
            raise RuntimeError(f"DATA row not found for {symbol}")
        info = con.execute(
            """
            select INSTRUMENT, DESCRIPTION, POINTVALUE, TICKSIZE, TICKSTEP,
                   DEFAULTSPREAD, COMMISSIONS, DATATYPE, EXCHANGE, COUNTRY,
                   SECTOR, DEFAULTSLIPPAGE, SWAP, ORDERSIZEMULTIPLIER,
                   ORDERSIZESTEP, BROKER_ID, MIN_DISTANCE
            from INSTRUMENTS
            where INSTRUMENT = ?
            """,
            (data["INSTRUMENT"],),
        ).fetchone()
        if info is None:
            raise RuntimeError(f"INSTRUMENTS row not found for {data['INSTRUMENT']}")
        broker = con.execute(
            "select ID, NAME, DESC, MT_TIMEZONE, POSTFIX from BROKER where ID = ?",
            (data["BROKER_ID"],),
        ).fetchone()
        if broker is None:
            raise RuntimeError(f"BROKER row not found for {data['BROKER_ID']}")
    finally:
        con.close()
    return {
        "symbol": data["SYMBOL"],
        "instrument": data["INSTRUMENT"],
        "timeframe": "H1",
        "precision": "TICK",
        "timezone": data["TIMEZONE"] or broker["MT_TIMEZONE"] or "EETUS",
        "source": str(data["SOURCE"]),
        "broker": str(data["BROKER_ID"]),
        "dateFrom": str(data["DATEFROM"]),
        "dateTo": str(data["DATETO"]),
        "dataDateFrom": int(data["DATEFROM"]),
        "dataDateTo": int(data["DATETO"]),
        "uSymbol": data["USYMBOL"] or data["SYMBOL"].split("_", 1)[0],
        "uSymbolName": data["USYMBOLNAME"] or data["USYMBOL"] or data["SYMBOL"].split("_", 1)[0],
        "description": info["DESCRIPTION"] or "",
        "tickSize": _java_double_text(info["TICKSIZE"]),
        "tickStep": _java_double_text(info["TICKSTEP"]),
        "minDistance": str(info["MIN_DISTANCE"] or 0.0),
        "defaultSpread": str(info["DEFAULTSPREAD"]),
        "defaultSlippage": str(info["DEFAULTSLIPPAGE"] or 0.0),
        "decimals": str(data["DECIMALS"]),
        "commissions": info["COMMISSIONS"] or "",
        "pointValue": str(info["POINTVALUE"]),
        "dataType": str(info["DATATYPE"]),
        "exchange": info["EXCHANGE"] or "",
        "country": info["COUNTRY"] or "",
        "sector": info["SECTOR"] or "",
        "swap": info["SWAP"] or "null",
        "orderSizeMultiplier": str(info["ORDERSIZEMULTIPLIER"] or 1.0),
        "orderSizeStep": str(info["ORDERSIZESTEP"] or 0.01),
        "brokerName": broker["NAME"] or "[[Darwinex]]",
        "brokerDescription": broker["DESC"] or "Darwinex CFDs",
        "brokerTimezone": broker["MT_TIMEZONE"] or "EETUS",
        "brokerPostfix": broker["POSTFIX"] or "_darwinex",
    }


def _maybe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _epoch_ms_to_sqx_date(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y.%m.%d")


def _data_row_exists(sqx_root: Path, symbol: str) -> bool:
    db_path = sqx_root / "user" / "data" / "data.db"
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return (
            con.execute("select 1 from DATA where SYMBOL = ? limit 1", (symbol,)).fetchone()
            is not None
        )
    finally:
        con.close()


def _local_darwinex_symbol(sqx_root: Path, symbol: str) -> str | None:
    if not symbol.endswith("_dukascopy"):
        return None
    candidate = f"{symbol[:-len('_dukascopy')]}_darwinex"
    return candidate if _data_row_exists(sqx_root, candidate) else None


def _bounded_dates_for_local_data(
    current_from: str | None,
    current_to: str | None,
    resource: dict[str, str],
) -> tuple[str, str, bool]:
    data_from = int(resource["dataDateFrom"])
    data_to = int(resource["dataDateTo"])
    requested_from = _maybe_int(current_from)
    requested_to = _maybe_int(current_to)
    if requested_from is None or requested_to is None or requested_from >= requested_to:
        return str(data_from), str(data_to), True

    # Keep tiny SQX rounding offsets intact; repair only real resolver gaps.
    if requested_to < data_from or requested_from > data_to:
        return str(data_from), str(data_to), True

    bounded_from = max(requested_from, data_from)
    bounded_to = min(requested_to, data_to)
    changed = requested_from < data_from - DAY_MS or requested_to > data_to + DAY_MS
    if changed:
        return str(bounded_from), str(bounded_to), True
    return str(requested_from), str(requested_to), False


def _setup_period_has_no_data(setup: ET.Element, resource: dict[str, str]) -> bool:
    date_to = setup.get("dateTo") or ""
    try:
        setup_to = datetime.strptime(date_to, "%Y.%m.%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    data_from = datetime.fromtimestamp(int(resource["dataDateFrom"]) / 1000, tz=timezone.utc)
    return setup_to <= data_from


def _patch_local_loadable_periods(root: ET.Element, symbol: str, resource: dict[str, str]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    data_from = _epoch_ms_to_sqx_date(int(resource["dataDateFrom"]))
    data_to = _epoch_ms_to_sqx_date(int(resource["dataDateTo"]))
    for setup in root.findall(".//Setup"):
        chart = setup.find("Chart")
        if chart is None or chart.get("symbol") != symbol:
            continue
        if not _setup_period_has_no_data(setup, resource):
            continue
        previous = f"{setup.get('dateFrom') or ''}..{setup.get('dateTo') or ''}"
        setup.set("dateFrom", data_from)
        setup.set("dateTo", data_to)
        changes.append(
            {
                "code": "bound_setup_dates_to_local_data",
                "symbol": symbol,
                "from": previous,
                "to": f"{data_from}..{data_to}",
            }
        )
    return changes


def _set_instrument_info_attrs(info: ET.Element, resource: dict[str, str]) -> None:
    attrs = {
        "instrument": resource["instrument"],
        "description": resource["description"],
        "tickSize": resource["tickSize"],
        "tickStep": resource["tickStep"],
        "minDistance": resource["minDistance"],
        "tickValueInMoney": "0.0",
        "dateFrom": "0",
        "dateTo": "0",
        "rows": "0",
        "totalDays": "0",
        "defaultSpread": resource["defaultSpread"],
        "defaultSlippage": resource["defaultSlippage"],
        "decimals": resource["decimals"],
        "commissions": resource["commissions"],
        "pointValue": resource["pointValue"],
        "dataType": resource["dataType"],
        "recognizedFromOrders": "false",
        "exchange": resource["exchange"],
        "country": resource["country"],
        "sector": resource["sector"],
        "swap": resource["swap"],
        "orderSizeMultiplier": resource["orderSizeMultiplier"],
        "orderSizeStep": resource["orderSizeStep"],
        "broker": resource["broker"],
    }
    for key, value in attrs.items():
        info.set(key, value)


def _ensure_broker(resources: ET.Element, resource: dict[str, str]) -> None:
    brokers = _ensure_child(resources, "Brokers")
    wanted_id = resource["broker"]
    existing = None
    for broker in brokers.findall("Broker"):
        if broker.get("id") == wanted_id:
            existing = broker
            break
    if existing is None:
        existing = ET.SubElement(brokers, "Broker")
    attrs = {
        "id": wanted_id,
        "name": resource["brokerName"],
        "description": resource["brokerDescription"],
        "timezone": resource["brokerTimezone"],
        "postfix": resource["brokerPostfix"],
        "mtUse": "true",
        "spUse": "false",
    }
    for key, value in attrs.items():
        existing.set(key, value)


def _sync_standalone_instrument(resources: ET.Element, resource: dict[str, str]) -> None:
    instruments = resources.find("Instruments")
    if instruments is None:
        return
    target = None
    for info in instruments.findall("InstrumentInfo"):
        if info.get("instrument") in {resource["instrument"], resource["symbol"]}:
            target = info
            break
    if target is None and list(instruments.findall("InstrumentInfo")):
        target = instruments.findall("InstrumentInfo")[0]
    if target is not None:
        _set_instrument_info_attrs(target, resource)


def _patch_resources_to_data_db(text: str, sqx_root: Path) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    resources_nodes = root.findall(".//Resources")
    for resources in resources_nodes:
        for symbol in resources.findall("./Symbols/Symbol"):
            symbol_name = symbol.get("name") or ""
            if not symbol_name or symbol_name.startswith("[["):
                continue
            try:
                resource = _resource_from_db(sqx_root, symbol_name)
            except RuntimeError:
                continue

            metadata_before = {
                "source": symbol.get("source") or "",
                "broker": symbol.get("broker") or "",
                "instrument": (symbol.find("InstrumentInfo").get("instrument") if symbol.find("InstrumentInfo") is not None else ""),
                "infoBroker": (symbol.find("InstrumentInfo").get("broker") if symbol.find("InstrumentInfo") is not None else ""),
            }
            metadata_after = {
                "source": resource["source"],
                "broker": resource["broker"],
                "instrument": resource["instrument"],
                "infoBroker": resource["broker"],
            }

            previous_period = f"{symbol.get('dateFrom') or ''}..{symbol.get('dateTo') or ''}"
            bounded_from, bounded_to, period_changed = _bounded_dates_for_local_data(
                symbol.get("dateFrom"),
                symbol.get("dateTo"),
                resource,
            )

            metadata_changed = metadata_before != metadata_after
            if not metadata_changed and not period_changed:
                continue

            symbol.set("source", resource["source"])
            symbol.set("barType", symbol.get("barType") or "1")
            symbol.set("precision", resource["precision"])
            symbol.set("timezone", resource["timezone"])
            symbol.set("dateFrom", bounded_from)
            symbol.set("dateTo", bounded_to)
            symbol.set("uSymbol", resource["uSymbol"])
            symbol.set("uSymbolName", resource["uSymbolName"])
            symbol.set("removeWeekends", symbol.get("removeWeekends") or "false")
            symbol.set("broker", resource["broker"])
            info = symbol.find("InstrumentInfo")
            if info is None:
                info = ET.SubElement(symbol, "InstrumentInfo")
            _set_instrument_info_attrs(info, resource)
            _ensure_broker(resources, resource)
            _sync_standalone_instrument(resources, resource)

            if metadata_changed:
                changes.append(
                    {
                        "code": "align_resource_metadata_to_data_db",
                        "symbol": symbol_name,
                        "previousHash": hashlib.sha256(json.dumps(metadata_before, sort_keys=True).encode("utf-8")).hexdigest()[:16],
                    }
                )
            if period_changed:
                changes.append(
                    {
                        "code": "bound_resource_dates_to_data_db",
                        "symbol": symbol_name,
                        "from": previous_period,
                        "to": f"{bounded_from}..{bounded_to}",
                    }
                )

            for chart in root.findall(".//Setup/Chart"):
                if chart.get("symbol") == symbol_name and chart.get("spread") != resource["defaultSpread"]:
                    chart.set("spread", resource["defaultSpread"])
                    changes.append({"code": "align_chart_spread_to_data_db", "symbol": symbol_name})
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_cross_broker_to_local_loadable(text: str, sqx_root: Path) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    conversions: dict[str, dict[str, str]] = {}

    for chart in root.findall(".//Setup/Chart"):
        symbol = chart.get("symbol") or ""
        local_symbol = _local_darwinex_symbol(sqx_root, symbol)
        if local_symbol is None:
            continue
        resource = _resource_from_db(sqx_root, local_symbol)
        chart.set("symbol", local_symbol)
        chart.set("spread", resource["defaultSpread"])
        conversions[symbol] = resource
        changes.append({"code": "convert_cross_broker_chart_to_local", "from": symbol, "to": local_symbol})

    for resources in root.findall(".//Resources"):
        for symbol in resources.findall("./Symbols/Symbol"):
            symbol_name = symbol.get("name") or ""
            local_symbol = _local_darwinex_symbol(sqx_root, symbol_name)
            if local_symbol is None:
                continue
            resource = _resource_from_db(sqx_root, local_symbol)
            previous_period = f"{symbol.get('dateFrom') or ''}..{symbol.get('dateTo') or ''}"
            symbol.set("name", local_symbol)
            symbol.set("source", resource["source"])
            symbol.set("barType", symbol.get("barType") or "1")
            symbol.set("precision", resource["precision"])
            symbol.set("timezone", resource["timezone"])
            symbol.set("dateFrom", str(resource["dataDateFrom"]))
            symbol.set("dateTo", str(resource["dataDateTo"]))
            symbol.set("uSymbol", resource["uSymbol"])
            symbol.set("uSymbolName", resource["uSymbolName"])
            symbol.set("removeWeekends", symbol.get("removeWeekends") or "false")
            symbol.set("broker", resource["broker"])
            info = symbol.find("InstrumentInfo")
            if info is None:
                info = ET.SubElement(symbol, "InstrumentInfo")
            _set_instrument_info_attrs(info, resource)
            _ensure_broker(resources, resource)
            _sync_standalone_instrument(resources, resource)
            conversions[symbol_name] = resource
            changes.append(
                {
                    "code": "convert_cross_broker_resource_to_local",
                    "from": symbol_name,
                    "to": local_symbol,
                    "periodFrom": previous_period,
                    "periodTo": f"{resource['dataDateFrom']}..{resource['dataDateTo']}",
                }
            )

    for old_symbol, resource in conversions.items():
        local_symbol = resource["symbol"]
        for node in root.findall(".//BackupStrategyTemplate//symbol"):
            if node.text == old_symbol:
                node.text = local_symbol
                changes.append({"code": "convert_backup_strategy_symbol_to_local", "from": old_symbol, "to": local_symbol})
        changes.extend(_patch_local_loadable_periods(root, local_symbol, resource))

    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_backup_strategy_symbols_to_chart(text: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    chart = root.find(".//Setup/Chart")
    if chart is None or not chart.get("symbol"):
        return text, []
    chart_symbol = chart.get("symbol")
    changes: list[dict[str, str]] = []
    for node in root.findall(".//BackupStrategyTemplate//symbol"):
        if node.text and node.text != chart_symbol:
            previous = node.text
            node.text = chart_symbol
            changes.append({"code": "align_backup_strategy_symbol_to_chart", "from": previous, "to": chart_symbol})
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_absolute_strategy_type_paths(text: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    for strategy_type in root.findall(".//StrategyType"):
        for attr in ("templateFile", "strategyFile"):
            value = strategy_type.get(attr) or ""
            if ":" in value or "\\" in value or "/" in value:
                strategy_type.set(attr, "")
                changes.append(
                    {
                        "code": f"blank_absolute_strategy_type_{attr}",
                        "previousHash": hashlib.sha256(value.encode("utf-8")).hexdigest()[:16],
                    }
                )
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _prune_unused_resource_brokers(text: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    for resources in root.findall(".//Resources"):
        used_brokers = {
            value
            for value in (
                [symbol.get("broker") for symbol in resources.findall("./Symbols/Symbol")]
                + [info.get("broker") for info in resources.findall("./Symbols/Symbol/InstrumentInfo")]
                + [info.get("broker") for info in resources.findall("./Instruments/InstrumentInfo")]
            )
            if value
        }
        brokers = resources.find("Brokers")
        if brokers is None or not used_brokers:
            continue
        removed = []
        for broker in list(brokers.findall("Broker")):
            broker_id = broker.get("id")
            if broker_id and broker_id not in used_brokers:
                brokers.remove(broker)
                removed.append(broker_id)
        if removed:
            changes.append(
                {
                    "code": "prune_unused_resource_brokers",
                    "removed": ",".join(sorted(removed)),
                    "used": ",".join(sorted(used_brokers)),
                }
            )
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_base_strategy_type_improve_databank(
    text: str, project_name: str
) -> tuple[str, list[dict[str, str]]]:
    if project_name not in BASE_PROJECTS_NEUTRAL_IMPROVE_DATABANK:
        return text, []
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    for strategy_type in root.findall(".//StrategyType"):
        current = strategy_type.get("improveDatabank") or ""
        if current and current != NEUTRAL_IMPROVE_DATABANK:
            strategy_type.set("improveDatabank", NEUTRAL_IMPROVE_DATABANK)
            changes.append(
                {
                    "code": "neutralize_base_improve_databank",
                    "from": current,
                    "to": NEUTRAL_IMPROVE_DATABANK,
                }
            )
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_base_project_date_caps(
    text: str, project_name: str, entry_name: str
) -> tuple[str, list[dict[str, str]]]:
    cap = BASE_PROJECT_DATE_CAPS.get((project_name, entry_name))
    if not cap:
        return text, []
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    for symbol in root.findall(".//Resources/Symbols/Symbol"):
        previous = (symbol.get("dateFrom") or "", symbol.get("dateTo") or "")
        wanted = (cap["dateFromMs"], cap["dateToMs"])
        if previous != wanted:
            symbol.set("dateFrom", cap["dateFromMs"])
            symbol.set("dateTo", cap["dateToMs"])
            changes.append(
                {
                    "code": "cap_base_resource_date_range",
                    "from": f"{previous[0]}..{previous[1]}",
                    "to": f"{wanted[0]}..{wanted[1]}",
                }
            )
    for setup in root.findall(".//Setup"):
        previous = setup.get("dateTo") or ""
        if previous != cap["dateTo"]:
            setup.set("dateTo", cap["dateTo"])
            changes.append(
                {
                    "code": "cap_base_setup_date_to",
                    "from": previous,
                    "to": cap["dateTo"],
                }
            )
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _ensure_child(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    return child


def _patch_config(config_text: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(config_text)
    changes: list[dict[str, str]] = []
    project_name = root.get("name") or ""
    for task in root.findall("./Tasks/Task"):
        template = task.get("templateFile")
        task_xml = task.get("taskXMLFile") or ""
        restore = CONFIG_TEMPLATE_REFERENCE_RESTORE.get((project_name, task_xml))
        if template == "" and restore:
            task.set("templateFile", restore)
            changes.append(
                {
                    "code": "restore_task_templateFile_reference",
                    "task": task.get("title") or task.get("name") or "",
                    "restoredHash": hashlib.sha256(restore.encode("utf-8")).hexdigest()[:16],
                }
            )
    if not changes:
        return config_text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_config_for_clean_load(config_text: str, project_name: str) -> tuple[str, list[dict[str, str]]]:
    if project_name not in CLEAN_LOAD_CONFIG_PROJECTS:
        return config_text, []
    root = ET.fromstring(config_text)
    changes: list[dict[str, str]] = []
    previous_version = root.get("version") or ""
    if previous_version != SQX142_CLEAN_PROJECT_VERSION:
        root.set("version", SQX142_CLEAN_PROJECT_VERSION)
        changes.append(
            {
                "code": "normalize_project_version_to_clean_sqx142",
                "from": previous_version,
                "to": SQX142_CLEAN_PROJECT_VERSION,
            }
        )
    for task in root.findall("./Tasks/Task"):
        template = task.get("templateFile")
        if not template:
            continue
        if (":" in template or "\\" in template or "/" in template) and not Path(template).exists():
            task.set("templateFile", "")
            changes.append(
                {
                    "code": "blank_missing_task_templateFile",
                    "taskXml": task.get("taskXMLFile") or "",
                    "previousHash": hashlib.sha256(template.encode("utf-8")).hexdigest()[:16],
                }
            )
    if not changes:
        return config_text, []
    return ET.tostring(root, encoding="unicode"), changes


def _patch_placeholder_to_resource(text: str, resource: dict[str, str]) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    placeholder_nodes = [
        node
        for node in root.findall(".//Resources/Symbols/Symbol")
        if (node.get("name") or "").startswith("[[")
    ]
    chart_nodes = [
        node
        for node in root.findall(".//Setup/Chart")
        if (node.get("symbol") or "").startswith("[[")
    ]
    if not placeholder_nodes and not chart_nodes:
        return text, []

    for chart in chart_nodes:
        chart.set("symbol", resource["symbol"])
        chart.set("timeframe", resource["timeframe"])
        chart.set("spread", resource["defaultSpread"])
        changes.append({"code": "patch_placeholder_chart", "symbol": resource["symbol"]})

    for setup in root.findall(".//Setup"):
        if setup.get("engine") == "MetaTrader4":
            setup.set("engine", "MetaTrader5 (hedged)")
            changes.append({"code": "patch_engine_mt5_hedged"})

    for resources in root.findall(".//Resources"):
        sessions = _ensure_child(resources, "Sessions")
        for session in list(sessions):
            sessions.remove(session)
        symbols = _ensure_child(resources, "Symbols")
        for symbol in list(symbols):
            symbols.remove(symbol)
        symbol = ET.SubElement(
            symbols,
            "Symbol",
            {
                "name": resource["symbol"],
                "source": resource["source"],
                "barType": "1",
                "precision": resource["precision"],
                "timezone": resource["timezone"],
                "dateFrom": resource["dateFrom"],
                "dateTo": resource["dateTo"],
                "uSymbol": resource["uSymbol"],
                "uSymbolName": resource["uSymbolName"],
                "removeWeekends": "false",
                "broker": resource["broker"],
            },
        )
        ET.SubElement(
            symbol,
            "InstrumentInfo",
            {
                "instrument": resource["instrument"],
                "description": resource["description"],
                "tickSize": resource["tickSize"],
                "tickStep": resource["tickStep"],
                "minDistance": resource["minDistance"],
                "tickValueInMoney": "0.0",
                "dateFrom": "0",
                "dateTo": "0",
                "rows": "0",
                "totalDays": "0",
                "defaultSpread": resource["defaultSpread"],
                "defaultSlippage": resource["defaultSlippage"],
                "decimals": resource["decimals"],
                "commissions": resource["commissions"],
                "pointValue": resource["pointValue"],
                "dataType": resource["dataType"],
                "recognizedFromOrders": "false",
                "exchange": resource["exchange"],
                "country": resource["country"],
                "sector": resource["sector"],
                "swap": resource["swap"],
                "orderSizeMultiplier": resource["orderSizeMultiplier"],
                "orderSizeStep": resource["orderSizeStep"],
                "broker": resource["broker"],
            },
        )
        brokers = _ensure_child(resources, "Brokers")
        for broker in list(brokers):
            brokers.remove(broker)
        ET.SubElement(
            brokers,
            "Broker",
            {
                "id": resource["broker"],
                "name": resource["brokerName"],
                "description": resource["brokerDescription"],
                "timezone": resource["brokerTimezone"],
                "postfix": resource["brokerPostfix"],
                "mtUse": "true",
                "spUse": "false",
            },
        )
        changes.append({"code": "rebuild_placeholder_resource", "symbol": resource["symbol"]})

    for node in root.findall(".//BackupStrategyTemplate//symbol"):
        if (node.text or "").startswith("[["):
            node.text = resource["symbol"]
            changes.append({"code": "patch_backup_strategy_symbol", "symbol": resource["symbol"]})
    return ET.tostring(root, encoding="unicode"), changes


def _patch_missing_strategy_type_paths(text: str) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(text)
    changes: list[dict[str, str]] = []
    for strategy_type in root.findall(".//StrategyType"):
        for attr in ("templateFile", "strategyFile"):
            value = strategy_type.get(attr) or ""
            if not value:
                continue
            if (":" in value or "\\" in value or "/" in value) and not Path(value).exists():
                strategy_type.set(attr, "")
                changes.append(
                    {
                        "code": f"blank_missing_strategy_type_{attr}",
                        "previousHash": hashlib.sha256(value.encode("utf-8")).hexdigest()[:16],
                    }
                )
    if not changes:
        return text, []
    return ET.tostring(root, encoding="unicode"), changes


def _project_plan(project_dir: Path, sqx_root: Path) -> dict:
    cfx = project_dir / "project.cfx"
    if not cfx.exists():
        return {"project": project_dir.name, "exists": False, "actions": []}
    actions: list[dict] = []
    with zipfile.ZipFile(cfx) as archive:
        config = archive.read("config.xml").decode("utf-8-sig")
        _, config_changes = _patch_config(config)
        actions.extend({"entry": "config.xml", **change} for change in config_changes)
        if config_changes:
            config, _ = _patch_config(config)
        _, clean_config_changes = _patch_config_for_clean_load(config, project_dir.name)
        actions.extend({"entry": "config.xml", **change} for change in clean_config_changes)
        for name in archive.namelist():
            if not name.endswith(".xml") or name == "config.xml":
                continue
            text = archive.read(name).decode("utf-8-sig")
            if "[[Dow Jones Industrial Average]]" in text and "IMOX XAU" in project_dir.name:
                actions.append(
                    {
                        "entry": name,
                        "code": "replace_sq_equity_placeholder_with_xauusd_darwinex",
                        "symbol": "XAUUSD_darwinex",
                    }
                )
            _, strategy_path_changes = _patch_missing_strategy_type_paths(text)
            actions.extend({"entry": name, **change} for change in strategy_path_changes)
            if strategy_path_changes:
                text, _ = _patch_missing_strategy_type_paths(text)
            _, absolute_path_changes = _patch_absolute_strategy_type_paths(text)
            actions.extend({"entry": name, **change} for change in absolute_path_changes)
            if absolute_path_changes:
                text, _ = _patch_absolute_strategy_type_paths(text)
            _, improve_databank_changes = _patch_base_strategy_type_improve_databank(
                text, project_dir.name
            )
            actions.extend({"entry": name, **change} for change in improve_databank_changes)
            if improve_databank_changes:
                text, _ = _patch_base_strategy_type_improve_databank(text, project_dir.name)
            _, local_loadable_changes = _patch_cross_broker_to_local_loadable(text, sqx_root)
            actions.extend({"entry": name, **change} for change in local_loadable_changes)
            if local_loadable_changes:
                text, _ = _patch_cross_broker_to_local_loadable(text, sqx_root)
            _, backup_symbol_changes = _patch_backup_strategy_symbols_to_chart(text)
            actions.extend({"entry": name, **change} for change in backup_symbol_changes)
            if backup_symbol_changes:
                text, _ = _patch_backup_strategy_symbols_to_chart(text)
            _, resource_changes = _patch_resources_to_data_db(text, sqx_root)
            actions.extend({"entry": name, **change} for change in resource_changes)
            if resource_changes:
                text, _ = _patch_resources_to_data_db(text, sqx_root)
            _, date_cap_changes = _patch_base_project_date_caps(text, project_dir.name, name)
            actions.extend({"entry": name, **change} for change in date_cap_changes)
            if date_cap_changes:
                text, _ = _patch_base_project_date_caps(text, project_dir.name, name)
            _, broker_changes = _prune_unused_resource_brokers(text)
            actions.extend({"entry": name, **change} for change in broker_changes)
    temp_files = sorted(path.name for path in project_dir.glob("zipfstmp*.tmp"))
    actions.extend({"entry": name, "code": "move_stale_zip_temp_file"} for name in temp_files)
    return {
        "project": project_dir.name,
        "exists": True,
        "projectCfxHash": _sha256(cfx),
        "actions": actions,
    }


def plan(sqx_root: Path) -> dict:
    projects_root = sqx_root / "user" / "projects"
    reports = [_project_plan(projects_root / name, sqx_root) for name in TARGET_PROJECTS]
    clean_donor_rebuilds = []
    for target, rebuild in CLEAN_DONOR_REBUILDS.items():
        donor = rebuild["donor"]
        clean_donor_rebuilds.append(
            {
                "target": target,
                "donor": donor,
                "fromSymbol": rebuild.get("fromSymbol"),
                "toSymbol": rebuild.get("toSymbol"),
                "targetExists": (projects_root / target / "project.cfx").exists(),
                "donorExists": (projects_root / donor / "project.cfx").exists(),
                "code": "available_clean_donor_rebuild",
            }
        )
    return {
        "ok": True,
        "version": VERSION,
        "action": "plan",
        "projects": reports,
        "cleanDonorRebuilds": clean_donor_rebuilds,
        "blockedSurfaces": BLOCKED_SURFACES,
    }


def repair(sqx_root: Path, repo_root: Path) -> dict:
    projects_root = sqx_root / "user" / "projects"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup_id = f"{VERSION}_{stamp}"
    backup_root = repo_root / ".local" / "sqx142_project_resource_repair" / "backups" / backup_id
    backup_root.mkdir(parents=True, exist_ok=True)
    resource = _resource_from_db(sqx_root, "XAUUSD_darwinex")
    project_results: list[dict] = []
    for name in TARGET_PROJECTS:
        project_dir = projects_root / name
        cfx = project_dir / "project.cfx"
        if not cfx.exists():
            project_results.append({"project": name, "exists": False, "changed": False})
            continue
        project_backup = backup_root / name
        project_backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cfx, project_backup / "project.cfx")
        replacements: dict[str, str] = {}
        changes: list[dict] = []
        with zipfile.ZipFile(cfx) as archive:
            config = archive.read("config.xml").decode("utf-8-sig")
            patched_config, config_changes = _patch_config(config)
            if config_changes:
                config = patched_config
            patched_config, clean_config_changes = _patch_config_for_clean_load(config, name)
            config_changes.extend(clean_config_changes)
            if config_changes:
                replacements["config.xml"] = patched_config
                changes.extend({"entry": "config.xml", **change} for change in config_changes)
            for entry in archive.namelist():
                if not entry.endswith(".xml") or entry == "config.xml":
                    continue
                original_text = archive.read(entry).decode("utf-8-sig")
                text = original_text
                if "[[Dow Jones Industrial Average]]" in text and "IMOX XAU" in name:
                    patched, xml_changes = _patch_placeholder_to_resource(text, resource)
                    if xml_changes:
                        text = patched
                        changes.extend({"entry": entry, **change} for change in xml_changes)
                patched, path_changes = _patch_missing_strategy_type_paths(text)
                if path_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in path_changes)
                patched, absolute_path_changes = _patch_absolute_strategy_type_paths(text)
                if absolute_path_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in absolute_path_changes)
                patched, improve_databank_changes = _patch_base_strategy_type_improve_databank(text, name)
                if improve_databank_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in improve_databank_changes)
                patched, local_loadable_changes = _patch_cross_broker_to_local_loadable(text, sqx_root)
                if local_loadable_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in local_loadable_changes)
                patched, backup_symbol_changes = _patch_backup_strategy_symbols_to_chart(text)
                if backup_symbol_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in backup_symbol_changes)
                patched, resource_changes = _patch_resources_to_data_db(text, sqx_root)
                if resource_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in resource_changes)
                patched, date_cap_changes = _patch_base_project_date_caps(text, name, entry)
                if date_cap_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in date_cap_changes)
                patched, broker_changes = _prune_unused_resource_brokers(text)
                if broker_changes:
                    text = patched
                    changes.extend({"entry": entry, **change} for change in broker_changes)
                if text != original_text:
                    replacements[entry] = text
        if replacements:
            _write_zip_texts(cfx, replacements)
        moved_temp_files = []
        for temp_file in sorted(project_dir.glob("zipfstmp*.tmp")):
            destination = project_backup / temp_file.name
            shutil.move(str(temp_file), str(destination))
            moved_temp_files.append({"from": str(temp_file), "to": str(destination)})
        project_results.append(
            {
                "project": name,
                "exists": True,
                "changed": bool(replacements or moved_temp_files),
                "beforeHash": _sha256(project_backup / "project.cfx"),
                "afterHash": _sha256(cfx),
                "changes": changes,
                "movedTempFiles": moved_temp_files,
            }
        )
    manifest = {
        "ok": True,
        "version": VERSION,
        "action": "repair",
        "backupId": backup_id,
        "backupRoot": str(backup_root),
        "projects": project_results,
        "blockedSurfaces": BLOCKED_SURFACES,
    }
    (backup_root / "rollback_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def rebuild_capa1_from_clean_donor(sqx_root: Path, repo_root: Path) -> dict:
    projects_root = sqx_root / "user" / "projects"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup_id = f"{VERSION}_clean-donor-rebuild_{stamp}"
    backup_root = repo_root / ".local" / "sqx142_project_resource_repair" / "backups" / backup_id
    backup_root.mkdir(parents=True, exist_ok=True)
    project_results: list[dict] = []
    for target_name, donor_name in BASE_PROJECT_CLEAN_DONORS.items():
        target_dir = projects_root / target_name
        donor_dir = projects_root / donor_name
        target_cfx = target_dir / "project.cfx"
        donor_cfx = donor_dir / "project.cfx"
        if not target_cfx.exists() or not donor_cfx.exists():
            project_results.append(
                {
                    "project": target_name,
                    "donor": donor_name,
                    "targetExists": target_cfx.exists(),
                    "donorExists": donor_cfx.exists(),
                    "changed": False,
                }
            )
            continue
        project_backup = backup_root / target_name
        project_backup.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target_cfx, project_backup / "project.cfx")
        before_hash = _sha256(project_backup / "project.cfx")
        donor_hash = _sha256(donor_cfx)
        changes = _write_clean_donor_project(donor_cfx, target_cfx, target_name)
        after_hash = _sha256(target_cfx)
        project_results.append(
            {
                "project": target_name,
                "donor": donor_name,
                "changed": before_hash != after_hash,
                "beforeHash": before_hash,
                "afterHash": after_hash,
                "donorHash": donor_hash,
                "changes": changes,
            }
        )
    manifest = {
        "ok": True,
        "version": VERSION,
        "action": "rebuild-capa1",
        "backupId": backup_id,
        "backupRoot": str(backup_root),
        "projects": project_results,
        "blockedSurfaces": BLOCKED_SURFACES,
    }
    (backup_root / "rollback_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def repair_capa2_clean_config(sqx_root: Path, repo_root: Path) -> dict:
    project_name = "Capa2_Base_SQX142_Base"
    cfx = sqx_root / "user" / "projects" / project_name / "project.cfx"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup_id = f"{VERSION}_capa2-clean-config_{stamp}"
    backup_root = repo_root / ".local" / "sqx142_project_resource_repair" / "backups" / backup_id
    backup_root.mkdir(parents=True, exist_ok=True)
    project_backup = backup_root / project_name
    project_backup.mkdir(parents=True, exist_ok=True)
    if not cfx.exists():
        manifest = {
            "ok": True,
            "version": VERSION,
            "action": "repair-capa2-config",
            "backupId": backup_id,
            "backupRoot": str(backup_root),
            "projects": [{"project": project_name, "exists": False, "changed": False}],
            "blockedSurfaces": BLOCKED_SURFACES,
        }
        (backup_root / "rollback_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest
    shutil.copy2(cfx, project_backup / "project.cfx")
    before_hash = _sha256(project_backup / "project.cfx")
    with zipfile.ZipFile(cfx) as archive:
        config = archive.read("config.xml").decode("utf-8-sig")
    patched_config, config_changes = _patch_config_for_clean_load(config, project_name)
    if config_changes:
        _write_zip_texts(cfx, {"config.xml": patched_config})
    with zipfile.ZipFile(cfx) as archive:
        archive.testzip()
    after_hash = _sha256(cfx)
    manifest = {
        "ok": True,
        "version": VERSION,
        "action": "repair-capa2-config",
        "backupId": backup_id,
        "backupRoot": str(backup_root),
        "projects": [
            {
                "project": project_name,
                "exists": True,
                "changed": before_hash != after_hash,
                "beforeHash": before_hash,
                "afterHash": after_hash,
                "changes": [{"entry": "config.xml", **change} for change in config_changes],
            }
        ],
        "blockedSurfaces": BLOCKED_SURFACES,
    }
    (backup_root / "rollback_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def rebuild_capa2_from_clean_donor(sqx_root: Path, repo_root: Path) -> dict:
    target_name = "Capa2_Base_SQX142_Base"
    rebuild = CLEAN_DONOR_REBUILDS[target_name]
    donor_name = rebuild["donor"]
    from_symbol = rebuild["fromSymbol"]
    to_symbol = rebuild["toSymbol"]
    projects_root = sqx_root / "user" / "projects"
    target_cfx = projects_root / target_name / "project.cfx"
    donor_cfx = projects_root / donor_name / "project.cfx"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup_id = f"{VERSION}_capa2-clean-donor-rebuild_{stamp}"
    backup_root = repo_root / ".local" / "sqx142_project_resource_repair" / "backups" / backup_id
    backup_root.mkdir(parents=True, exist_ok=True)
    project_backup = backup_root / target_name
    project_backup.mkdir(parents=True, exist_ok=True)
    if not target_cfx.exists() or not donor_cfx.exists():
        manifest = {
            "ok": True,
            "version": VERSION,
            "action": "rebuild-capa2",
            "backupId": backup_id,
            "backupRoot": str(backup_root),
            "projects": [
                {
                    "project": target_name,
                    "donor": donor_name,
                    "targetExists": target_cfx.exists(),
                    "donorExists": donor_cfx.exists(),
                    "changed": False,
                }
            ],
            "blockedSurfaces": BLOCKED_SURFACES,
        }
        (backup_root / "rollback_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest
    shutil.copy2(target_cfx, project_backup / "project.cfx")
    before_hash = _sha256(project_backup / "project.cfx")
    donor_hash = _sha256(donor_cfx)
    resource = _resource_from_db(sqx_root, to_symbol)
    changes = _write_normalized_clean_donor_project(
        donor_cfx,
        target_cfx,
        target_name,
        from_symbol,
        resource,
    )
    after_hash = _sha256(target_cfx)
    manifest = {
        "ok": True,
        "version": VERSION,
        "action": "rebuild-capa2",
        "backupId": backup_id,
        "backupRoot": str(backup_root),
        "projects": [
            {
                "project": target_name,
                "donor": donor_name,
                "changed": before_hash != after_hash,
                "beforeHash": before_hash,
                "afterHash": after_hash,
                "donorHash": donor_hash,
                "fromSymbol": from_symbol,
                "toSymbol": to_symbol,
                "changes": changes,
            }
        ],
        "blockedSurfaces": BLOCKED_SURFACES,
    }
    (backup_root / "rollback_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def rollback(sqx_root: Path, repo_root: Path, backup_id: str) -> dict:
    projects_root = sqx_root / "user" / "projects"
    backups_root = repo_root / ".local" / "sqx142_project_resource_repair" / "backups"
    backup_root = backups_root / backup_id
    if not backup_root.exists():
        raise RuntimeError(f"BackupId not found: {backup_id}")
    restored = []
    for project_backup in backup_root.iterdir():
        if not project_backup.is_dir():
            continue
        project_dir = projects_root / project_backup.name
        project_dir.mkdir(parents=True, exist_ok=True)
        source_cfx = project_backup / "project.cfx"
        if source_cfx.exists():
            shutil.copy2(source_cfx, project_dir / "project.cfx")
        for temp_file in project_backup.glob("zipfstmp*.tmp"):
            shutil.copy2(temp_file, project_dir / temp_file.name)
        restored.append({"project": project_backup.name, "projectCfxHash": _sha256(project_dir / "project.cfx")})
    return {
        "ok": True,
        "version": VERSION,
        "action": "rollback",
        "backupId": backup_id,
        "restored": restored,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=("plan", "repair", "rebuild-capa1", "repair-capa2-config", "rebuild-capa2", "rollback"),
        default="plan",
    )
    parser.add_argument("--sqx-root", default=str(DEFAULT_SQX_ROOT))
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[3]))
    parser.add_argument("--backup-id", default="")
    args = parser.parse_args()
    sqx_root = Path(args.sqx_root)
    repo_root = Path(args.repo_root)
    if args.action == "plan":
        payload = plan(sqx_root)
    elif args.action == "repair":
        payload = repair(sqx_root, repo_root)
    elif args.action == "rebuild-capa1":
        payload = rebuild_capa1_from_clean_donor(sqx_root, repo_root)
    elif args.action == "repair-capa2-config":
        payload = repair_capa2_clean_config(sqx_root, repo_root)
    elif args.action == "rebuild-capa2":
        payload = rebuild_capa2_from_clean_donor(sqx_root, repo_root)
    else:
        if not args.backup_id:
            raise RuntimeError("--backup-id is required for rollback")
        payload = rollback(sqx_root, repo_root, args.backup_id)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "version": VERSION, "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
