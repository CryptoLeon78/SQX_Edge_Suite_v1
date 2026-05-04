"""
sqx_db.py — Lector de la DB de StrategyQuant X (data.db SQLite).

Extrae spread, swap, commission, slippage REALES por símbolo + broker postfix.
Sustituye los ASSET_DEFAULTS aproximados de project_generator.py cuando data.db
está disponible.

Tablas relevantes:
  INSTRUMENTS — datos por símbolo (DEFAULTSPREAD, COMMISSIONS, SWAP, ...)
  BROKER     — brokers disponibles (POSTFIX para sufijo de símbolo, ej. "_darwinex")
  DATA       — histórico cargado (DATEFROM/DATETO por símbolo+TF)
"""
from __future__ import annotations

import os
import sqlite3
from typing import Optional
from xml.etree import ElementTree as ET

from .config_loader import load_manifest

_INSTRUMENTS_PROFILE = load_manifest("instruments.json")
ASSET_TO_INSTRUMENT_DEFAULTS = _INSTRUMENTS_PROFILE.get("assetAliases") or {}

# Alias retro-compat (código viejo)
ASSET_TO_INSTRUMENT = ASSET_TO_INSTRUMENT_DEFAULTS


ASSET_SEARCH_HINTS = _INSTRUMENTS_PROFILE.get("searchHints") or {}
FALLBACK_VARIANTS = _INSTRUMENTS_PROFILE.get("fallbackVariants") or [
    "{asset}(2)",
    "{asset}_darwinex",
    "{assetLower}(2)",
]


def _row_get(row: sqlite3.Row, key: str, default=None):
    return row[key] if key in row.keys() else default


class SqxDb:
    """Lector read-only de data.db de SQX."""

    def __init__(self, db_path: str) -> None:
        if not os.path.isfile(db_path):
            raise FileNotFoundError(f"data.db not found: {db_path}")
        self.db_path = db_path
        # check_same_thread=False para Flask multi-thread
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        # Cache de brokers (ID → POSTFIX)
        self._broker_cache: Optional[dict] = None

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    # ── Brokers ───────────────────────────────────────────────────
    def brokers(self) -> list[dict]:
        try:
            rows = self._conn.execute("SELECT ID,NAME,POSTFIX,DESC FROM BROKER ORDER BY NAME").fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def broker_postfix(self, broker_id: int) -> Optional[str]:
        try:
            if self._broker_cache is None:
                brokers = self.brokers()
                self._broker_cache = {}
                for r in brokers:
                    bid = r.get("ID")
                    pfix = r.get("POSTFIX")
                    if bid is not None and pfix is not None:
                        self._broker_cache[bid] = pfix
            return self._broker_cache.get(broker_id)
        except Exception:
            return None

    def find_broker_by_postfix(self, postfix: str) -> Optional[dict]:
        for b in self.brokers():
            if b.get("POSTFIX") == postfix:
                return b
        return None

    # ── Instruments ───────────────────────────────────────────────
    def list_instruments(self) -> list[str]:
        rows = self._conn.execute("SELECT INSTRUMENT FROM INSTRUMENTS ORDER BY INSTRUMENT").fetchall()
        return [r["INSTRUMENT"] for r in rows]

    def get_instrument_raw(self, instrument: str) -> Optional[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM INSTRUMENTS WHERE INSTRUMENT = ?", (instrument,)
        ).fetchone()

    def get_symbol_info(self, asset: str, alias_override: Optional[dict] = None) -> dict:
        """
        Devuelve la mejor data disponible para `asset`.

        Args:
            asset: ticker del plan (ej. "USTEC")
            alias_override: dict opcional {asset: instrument} para sobreescribir
                            ASSET_TO_INSTRUMENT_DEFAULTS (típicamente del config.json)

        Returns dict con:
          source: 'db' si encontrado, 'fallback' si no
          instrument: ticker en la DB
          spread, slippage, point_value, tick_size
          commission_type, commission_value
          swap_long, swap_short, swap_type
          broker_id, broker_postfix
        """
        # Resolver alias: override del usuario > defaults > asset tal cual
        aliases = {**ASSET_TO_INSTRUMENT_DEFAULTS, **(alias_override or {})}
        instrument = aliases.get(asset, asset)
        row = self.get_instrument_raw(instrument)
        # Si no encuentra exacto, intentar variantes comunes (ej: XAUUSD -> XAUUSD(2))
        if row is None:
            variants = [
                pattern.format(asset=asset, assetLower=asset.lower(), instrument=instrument)
                for pattern in FALLBACK_VARIANTS
            ]
            for variant in variants:
                row = self.get_instrument_raw(variant)
                if row is not None:
                    instrument = variant
                    break
        if row is None:
            return {"source": "fallback", "asset": asset, "instrument": instrument, "error": "not_found"}

        info: dict = {
            "source": "db",
            "asset": asset,
            "instrument": instrument,
            "description": row["DESCRIPTION"],
            "point_value": row["POINTVALUE"],
            "tick_size": row["TICKSIZE"],
            "spread": row["DEFAULTSPREAD"],
            "slippage": row["DEFAULTSLIPPAGE"],
        }
        # SQX 142 tiene BROKER_ID; SQX 139 no
        if "BROKER_ID" in row.keys():
            info["broker_id"] = row["BROKER_ID"]
            info["broker_postfix"] = self.broker_postfix(row["BROKER_ID"])
        else:
            info["broker_id"] = None
            info["broker_postfix"] = None
        info.update(_parse_commission_xml(row["COMMISSIONS"]))
        info.update(_parse_swap_xml(row["SWAP"]))
        return info

    def suggest_instruments(self, asset: str, broker_id: Optional[int] = None) -> list[dict]:
        """
        Busca posibles instruments en la DB que correspondan a `asset`.
        Útil para crear aliases por broker (USTEC -> NDXm/NDX/USTEC100/etc).

        Returns lista de candidatos con score de relevancia (0-100).
        """
        # Buscar variantes en INSTRUMENT y DESCRIPTION
        hints = ASSET_SEARCH_HINTS.get(asset.upper(), [asset.lower()])
        # Asegurar que el asset original también está en los hints
        if asset.lower() not in hints:
            hints.append(asset.lower())

        results = []
        rows = self._conn.execute("SELECT INSTRUMENT, DESCRIPTION, DEFAULTSPREAD FROM INSTRUMENTS").fetchall()
        for r in rows:
            inst = (r["INSTRUMENT"] or "").lower()
            desc = (r["DESCRIPTION"] or "").lower()
            score = 0
            matched_via = []
            # Match directo en instrument
            if inst == asset.lower():
                score = 100
                matched_via.append("exact")
            elif asset.lower() in inst:
                score = 90
                matched_via.append("instrument_contains")
            # Match en hints
            for h in hints:
                if h in inst:
                    score = max(score, 80)
                    matched_via.append(f"hint_inst({h})")
                if h in desc:
                    score = max(score, 60)
                    matched_via.append(f"hint_desc({h})")
            if score == 0:
                continue
            # Bonus si coincide broker (solo SQX 142)
            if broker_id is not None and "BROKER_ID" in r.keys():
                if r["BROKER_ID"] == broker_id:
                    score += 5
            results.append({
                "instrument": r["INSTRUMENT"],
                "description": r["DESCRIPTION"],
                "broker_id": _row_get(r, "BROKER_ID"),
                "broker_postfix": self.broker_postfix(r["BROKER_ID"]) if "BROKER_ID" in r.keys() else None,
                "spread": r["DEFAULTSPREAD"],
                "score": min(score, 100),
                "matched_via": ", ".join(matched_via),
            })
        results.sort(key=lambda x: -x["score"])
        return results

    # ── Data history ──────────────────────────────────────────────
    def get_data_range(self, symbol: str, timeframe: Optional[str] = None) -> Optional[dict]:
        """Devuelve {date_from, date_to, rows} para un símbolo+TF (o el primero)."""
        sql = "SELECT SYMBOL,TIMEFRAME,DATEFROM,DATETO,ROWS FROM DATA WHERE SYMBOL = ?"
        params: tuple = (symbol,)
        if timeframe:
            sql += " AND TIMEFRAME = ?"
            params = (symbol, timeframe)
        sql += " ORDER BY DATEFROM ASC LIMIT 1"
        row = self._conn.execute(sql, params).fetchone()
        if row is None:
            return None
        return {
            "symbol": row["SYMBOL"],
            "timeframe": row["TIMEFRAME"],
            "date_from_ms": row["DATEFROM"],
            "date_to_ms": row["DATETO"],
            "rows": row["ROWS"],
        }


# ── Parsers para XML embebido en INSTRUMENTS ──────────────────────
def _parse_commission_xml(xml_str: Optional[str]) -> dict:
    """Parsea el XML COMMISSIONS de SQX y extrae type+value."""
    if not xml_str:
        return {"commission_type": None, "commission_value": None}
    try:
        root = ET.fromstring(xml_str)
        # <Method type="..."><Params><Param key="Commission" ...>VALUE</Param></Params></Method>
        ctype = root.get("type")
        param = root.find(".//Param[@key='Commission']")
        cval = float(param.text) if param is not None and param.text else None
        return {"commission_type": ctype, "commission_value": cval}
    except Exception:
        return {"commission_type": None, "commission_value": None}


def _parse_swap_xml(xml_str: Optional[str]) -> dict:
    """Parsea el XML SWAP de SQX. Devuelve long/short/type/triple/rollout."""
    if not xml_str:
        return {"swap_long": None, "swap_short": None, "swap_type": None,
                "swap_triple_on": None, "swap_rollout_hour": None}
    try:
        root = ET.fromstring(xml_str)
        # <Swap use="true" type="money|points" long="..." short="..." tripleSwapOn="..." rolloutHour="..."/>
        return {
            "swap_long":         _to_float(root.get("long")),
            "swap_short":        _to_float(root.get("short")),
            "swap_type":         root.get("type"),
            "swap_triple_on":    root.get("tripleSwapOn"),
            "swap_rollout_hour": root.get("rolloutHour"),
        }
    except Exception:
        return {"swap_long": None, "swap_short": None, "swap_type": None,
                "swap_triple_on": None, "swap_rollout_hour": None}


def _to_float(v) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
