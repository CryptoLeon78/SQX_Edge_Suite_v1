"""Descarga M15/M30/H1 desde 2010 de Dukascopy MT5 para todos los activos del dashboard.

Maneja el problema del caché frío de MT5 con retry + activación previa de símbolos.
Genera CSVs listos para SQX import en csv_for_sqx/<asset>_<TF>.csv.
"""
from __future__ import annotations

import time
import argparse
from datetime import datetime
from pathlib import Path

from sqx_analysis_common import all_asset_ids

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - optional local dependency
    pd = None
    PANDAS_IMPORT_ERROR = exc
else:
    PANDAS_IMPORT_ERROR = None

try:
    import MetaTrader5 as mt5
except ImportError:  # pragma: no cover - optional local dependency
    mt5 = None

DEFAULT_DUKAS_PATH = "C:/Program Files/Dukascopy MetaTrader 5/terminal64.exe"
START = datetime(2010, 1, 1)
END   = datetime(2026, 5, 1)
OUT_DIR = Path(__file__).parent / "csv_for_sqx"
OUT_DIR.mkdir(exist_ok=True)

# Dashboard ID -> Dukascopy symbol
SYMBOL_MAP: dict[str, str] = {
    "EURUSD":"EURUSD", "GBPUSD":"GBPUSD", "USDJPY":"USDJPY", "USDCHF":"USDCHF",
    "AUDUSD":"AUDUSD", "NZDUSD":"NZDUSD", "USDCAD":"USDCAD",
    "EURGBP":"EURGBP", "EURJPY":"EURJPY", "EURCAD":"EURCAD", "EURCHF":"EURCHF",
    "EURAUD":"EURAUD", "EURNZD":"EURNZD",
    "GBPJPY":"GBPJPY", "GBPNZD":"GBPNZD", "GBPAUD":"GBPAUD", "GBPCAD":"GBPCAD", "GBPCHF":"GBPCHF",
    "AUDJPY":"AUDJPY", "NZDJPY":"NZDJPY", "CADJPY":"CADJPY", "CHFJPY":"CHFJPY",
    "AUDNZD":"AUDNZD", "AUDCAD":"AUDCAD", "NZDCAD":"NZDCAD", "CADCHF":"CADCHF",
    "USDMXN":"USDMXN", "USDZAR":"USDZAR",
    "US500":"USA500.IDX", "USTEC":"USATECH.IDX", "GER40":"DEU.IDX", "US30":"USA30.IDX",
    "XAUUSD":"XAUUSD",
}

TFS: list[tuple[str, int]] = [
    ("M5",  5),
    ("M15", 15),
    ("M30", 30),
    ("H1",  60),
    ("H4",  240),
]


def mt5_timeframes() -> list[tuple[str, int]]:
    if mt5 is None:
        return []
    return [
        ("M5",  mt5.TIMEFRAME_M5),
        ("M15", mt5.TIMEFRAME_M15),
        ("M30", mt5.TIMEFRAME_M30),
        ("H1",  mt5.TIMEFRAME_H1),
        ("H4",  mt5.TIMEFRAME_H4),
    ]


def fetch_with_retry(symbol: str, tf_code: int, retries: int = 3, delay: float = 4.0):
    """Llama copy_rates_range con retry — el caché frío de MT5 a veces devuelve 0 barras la 1ª vez."""
    for attempt in range(retries):
        rates = mt5.copy_rates_range(symbol, tf_code, START, END)
        if rates is not None and len(rates) > 100:
            return rates
        if attempt < retries - 1:
            time.sleep(delay)
    return rates


def main(path: str = DEFAULT_DUKAS_PATH, out_dir: Path = OUT_DIR) -> None:
    if PANDAS_IMPORT_ERROR is not None:
        print("pandas no está instalado. Ejecuta: pip install -r requirements-analysis.txt")
        return
    if mt5 is None:
        print("MetaTrader5 no está instalado. Ejecuta: pip install -r requirements-analysis.txt")
        return
    out_dir.mkdir(exist_ok=True)
    tfs = mt5_timeframes()
    known_assets = set(all_asset_ids())
    symbol_map = {k: v for k, v in SYMBOL_MAP.items() if not known_assets or k in known_assets}

    if not mt5.initialize(path=path):
        print("MT5 init failed:", mt5.last_error())
        return

    # Activar todos los símbolos a la vez para que el terminal precargue
    print("Activando símbolos...")
    activated = []
    missing = []
    for did, sym in symbol_map.items():
        if mt5.symbol_info(sym) is None:
            missing.append((did, sym))
            continue
        mt5.symbol_select(sym, True)
        activated.append((did, sym))

    print(f"  Activados: {len(activated)} | No encontrados: {len(missing)}")
    for did, sym in missing:
        print(f"    [skip] {did} -> {sym}")

    print("Esperando 8s para que el terminal inicialice cachés...")
    time.sleep(8)

    # Descarga
    summary = []
    t_start = time.time()
    total = len(activated) * len(tfs)
    done = 0

    for did, sym in activated:
        for tf_name, tf_code in tfs:
            done += 1
            out_path = out_dir / f"{did}_{tf_name}.csv"
            # Skip si ya existe (idempotente — borra el CSV manual si quieres re-descargar)
            if out_path.exists():
                size_kb = out_path.stat().st_size / 1024
                # Solo skip si tiene más de 50KB (evita CSVs vacíos/corruptos)
                if size_kb > 50:
                    print(f"[{done:3d}/{total}] {did:8s} {tf_name:4s} - SKIP (ya existe, {size_kb:.1f} KB)")
                    summary.append((did, tf_name, -1, "", "", 0))
                    continue
            t0 = time.time()
            rates = fetch_with_retry(sym, tf_code)
            elapsed = time.time() - t0

            if rates is None or len(rates) == 0:
                print(f"[{done:3d}/{total}] {did:8s} {tf_name:4s} - NO DATA tras retries")
                summary.append((did, tf_name, 0, "", "", elapsed))
                continue

            df = pd.DataFrame(rates)
            df["Date"] = pd.to_datetime(df["time"], unit="s")
            df = df.rename(columns={
                "open":"Open", "high":"High", "low":"Low", "close":"Close", "tick_volume":"Volume",
            })
            df = df[["Date","Open","High","Low","Close","Volume"]]

            out_path = out_dir / f"{did}_{tf_name}.csv"
            df.to_csv(out_path, index=False)

            first = df["Date"].iloc[0].strftime("%Y-%m-%d")
            last  = df["Date"].iloc[-1].strftime("%Y-%m-%d")
            mb = out_path.stat().st_size / 1024 / 1024
            print(f"[{done:3d}/{total}] {did:8s} {tf_name:4s} {len(df):>8,} bars  {first}->{last}  {mb:5.1f} MB  ({elapsed:.1f}s)")
            summary.append((did, tf_name, len(df), first, last, elapsed))

    mt5.shutdown()

    total_elapsed = time.time() - t_start
    print(f"\n=== RESUMEN ({total_elapsed/60:.1f} min total) ===")
    failed = [s for s in summary if s[2] == 0]
    ok = [s for s in summary if s[2] > 0]
    total_bars = sum(s[2] for s in ok)
    total_mb = sum((out_dir / f"{s[0]}_{s[1]}.csv").stat().st_size for s in ok) / 1024 / 1024
    print(f"OK:       {len(ok)}/{len(summary)}")
    print(f"Failed:   {len(failed)}")
    print(f"Bars:     {total_bars:,}")
    print(f"Total MB: {total_mb:.0f}")

    if failed:
        print("\nFallos (re-ejecuta el script — el segundo intento suele resolverlos):")
        for did, tf, _, _, _, _ in failed:
            print(f"  {did} {tf}")

    # Generar coverage report CSV
    cov_path = out_dir / "_coverage_report.csv"
    pd.DataFrame(summary, columns=["asset","tf","bars","first","last","seconds"]).to_csv(cov_path, index=False)
    print(f"\nCoverage report: {cov_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=DEFAULT_DUKAS_PATH, help="Ruta a terminal64.exe de Dukascopy MT5")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Carpeta destino de CSVs")
    args = parser.parse_args()
    main(path=args.path, out_dir=Path(args.out_dir))
