"""
Build SQX metric JSON files from reviewable OHLC CSV inputs.

A55 provides the missing real-data bridge: the operator supplies market CSVs
such as `EURUSD_M30.csv`, and this tool computes the metric fields consumed by
the A49/A51/A53/A54 multi-timeframe pipeline.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
DEFAULT_POLICY_PATH = CONFIG_DIR / "ohlc_metric_source_policy.json"
DEFAULT_ASSETS_PATH = CONFIG_DIR / "assets.json"
DEFAULT_OUT_DIR = PROJECT_ROOT / "analysis_output" / "ohlc_metrics"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_tf(tf: str) -> str:
    value = str(tf or "").strip().upper()
    if not value:
        raise ValueError("timeframe cannot be empty")
    return value


def safe_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if number != number or math.isinf(number):
        return None
    return number


def rounded(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def load_asset_index(path: Path = DEFAULT_ASSETS_PATH) -> dict[str, dict[str, Any]]:
    data = read_json(path)
    return {str(asset["id"]).upper(): asset for asset in data.get("assets", []) if asset.get("id")}


def find_column(fieldnames: list[str], aliases: list[str]) -> str | None:
    lowered = {name.strip().lower(): name for name in fieldnames}
    for alias in aliases:
        if alias.lower() in lowered:
            return lowered[alias.lower()]
    return None


def read_ohlc_csv(path: Path, policy: dict[str, Any]) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        reader = csv.DictReader(handle, dialect=dialect)
        if not reader.fieldnames:
            raise ValueError(f"{path} has no header")
        columns = {
            key: find_column(reader.fieldnames, aliases)
            for key, aliases in policy["acceptedColumns"].items()
        }
        missing = [key for key in ("open", "high", "low", "close") if not columns.get(key)]
        if missing:
            raise ValueError(f"{path} missing required columns: {', '.join(missing)}")

        bars: list[dict[str, float]] = []
        for row in reader:
            open_ = safe_float(row.get(columns["open"]))
            high = safe_float(row.get(columns["high"]))
            low = safe_float(row.get(columns["low"]))
            close = safe_float(row.get(columns["close"]))
            if open_ is None or high is None or low is None or close is None:
                continue
            volume = safe_float(row.get(columns["volume"])) if columns.get("volume") else None
            bars.append(
                {
                    "open": open_,
                    "high": max(high, open_, close),
                    "low": min(low, open_, close),
                    "close": close,
                    "volume": volume if volume is not None and volume > 0 else 1.0,
                }
            )
    return bars


def true_ranges(bars: list[dict[str, float]]) -> list[float]:
    ranges: list[float] = []
    prev_close = bars[0]["close"] if bars else 0.0
    for bar in bars:
        tr = max(
            bar["high"] - bar["low"],
            abs(bar["high"] - prev_close),
            abs(bar["low"] - prev_close),
        )
        ranges.append(tr)
        prev_close = bar["close"]
    return ranges


def simple_moving_average(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    running = 0.0
    for index, value in enumerate(values):
        running += value
        if index >= window:
            running -= values[index - window]
        if index + 1 < window:
            out.append(None)
        else:
            out.append(running / window)
    return out


def adx_mean(bars: list[dict[str, float]], period: int = 14) -> float | None:
    if len(bars) < period + 2:
        return None
    trs = true_ranges(bars)
    plus_dm = [0.0]
    minus_dm = [0.0]
    for prev, cur in zip(bars, bars[1:]):
        up_move = cur["high"] - prev["high"]
        down_move = prev["low"] - cur["low"]
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
    dx_values: list[float] = []
    for index in range(period, len(bars)):
        tr_sum = sum(trs[index - period + 1 : index + 1])
        if tr_sum <= 0:
            continue
        plus_di = 100 * sum(plus_dm[index - period + 1 : index + 1]) / tr_sum
        minus_di = 100 * sum(minus_dm[index - period + 1 : index + 1]) / tr_sum
        denom = plus_di + minus_di
        if denom > 0:
            dx_values.append(100 * abs(plus_di - minus_di) / denom)
    if not dx_values:
        return None
    return mean(dx_values[-min(len(dx_values), 100) :])


def rsi_values(closes: list[float], period: int = 14) -> list[float]:
    if len(closes) < period + 1:
        return []
    out: list[float] = []
    gains: list[float] = []
    losses: list[float] = []
    for prev, cur in zip(closes, closes[1:]):
        change = cur - prev
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
    for index in range(period - 1, len(gains)):
        avg_gain = mean(gains[index - period + 1 : index + 1])
        avg_loss = mean(losses[index - period + 1 : index + 1])
        if avg_loss == 0:
            out.append(100.0)
        else:
            rs = avg_gain / avg_loss
            out.append(100 - (100 / (1 + rs)))
    return out


def trend_efficiency(closes: list[float], window: int = 200) -> float | None:
    if len(closes) < 3:
        return None
    active_window = min(window, len(closes) - 1)
    segment = closes[-active_window - 1 :]
    direct = abs(segment[-1] - segment[0])
    path = sum(abs(cur - prev) for prev, cur in zip(segment, segment[1:]))
    return direct / path if path > 0 else 0.0


def sma_persistence(closes: list[float], window: int = 200) -> float | None:
    if len(closes) < 5:
        return None
    active_window = min(window, max(5, len(closes) // 2))
    smas = simple_moving_average(closes, active_window)
    streak = 0
    best = 0
    last_side: int | None = None
    for close, sma in zip(closes, smas):
        if sma is None:
            continue
        side = 1 if close >= sma else -1
        if side == last_side:
            streak += 1
        else:
            streak = 1
            last_side = side
        best = max(best, streak)
    return float(best)


def atr_pct_mean(bars: list[dict[str, float]], period: int = 14) -> float | None:
    if len(bars) < period:
        return None
    trs = true_ranges(bars)
    values = []
    for index in range(period - 1, len(bars)):
        atr = mean(trs[index - period + 1 : index + 1])
        close = bars[index]["close"]
        if close:
            values.append(100 * atr / abs(close))
    return mean(values[-min(len(values), 100) :]) if values else None


def vol_of_vol(bars: list[dict[str, float]], period: int = 14) -> float | None:
    if len(bars) < period * 2:
        return None
    trs = true_ranges(bars)
    atrs = [mean(trs[index - period + 1 : index + 1]) for index in range(period - 1, len(trs))]
    avg = mean(atrs)
    return pstdev(atrs) / avg if avg > 0 and len(atrs) > 1 else 0.0


def hurst_dist(closes: list[float]) -> float | None:
    if len(closes) < 40:
        return None
    returns = [math.log(cur / prev) for prev, cur in zip(closes, closes[1:]) if prev > 0 and cur > 0]
    if len(returns) < 30:
        return None
    mean_ret = mean(returns)
    cumulative: list[float] = []
    running = 0.0
    for value in returns:
        running += value - mean_ret
        cumulative.append(running)
    range_ = max(cumulative) - min(cumulative)
    std = pstdev(returns)
    if std <= 0:
        return 0.0
    rs = range_ / std
    hurst = math.log(max(rs, 1e-9)) / math.log(len(returns))
    return abs(max(0.0, min(1.0, hurst)) - 0.5)


def ou_half_life(closes: list[float]) -> float | None:
    if len(closes) < 30:
        return None
    x = closes[:-1]
    y = [cur - prev for prev, cur in zip(closes, closes[1:])]
    avg_x = mean(x)
    avg_y = mean(y)
    denom = sum((value - avg_x) ** 2 for value in x)
    if denom <= 0:
        return None
    beta = sum((xi - avg_x) * (yi - avg_y) for xi, yi in zip(x, y)) / denom
    if beta >= 0:
        return float(len(closes))
    return min(float(len(closes) * 10), -math.log(2) / beta)


def kurtosis(closes: list[float]) -> float | None:
    returns = [math.log(cur / prev) for prev, cur in zip(closes, closes[1:]) if prev > 0 and cur > 0]
    if len(returns) < 4:
        return None
    avg = mean(returns)
    std = pstdev(returns)
    if std <= 0:
        return 0.0
    return mean(((value - avg) / std) ** 4 for value in returns)


def rsi_edge_in_atrs(bars: list[dict[str, float]]) -> float | None:
    closes = [bar["close"] for bar in bars]
    rsis = rsi_values(closes)
    atr = atr_pct_mean(bars)
    if not rsis or atr is None:
        return None
    return mean(abs(value - 50) / 50 for value in rsis[-min(len(rsis), 100) :]) * max(1.0, atr)


def vwap_rejection_rate(bars: list[dict[str, float]]) -> float | None:
    if len(bars) < 20:
        return None
    cumulative_pv = 0.0
    cumulative_volume = 0.0
    touches = 0
    rejections = 0
    for bar in bars:
        typical = (bar["high"] + bar["low"] + bar["close"]) / 3
        volume = max(bar.get("volume", 1.0), 1.0)
        cumulative_pv += typical * volume
        cumulative_volume += volume
        vwap = cumulative_pv / cumulative_volume
        span = max(bar["high"] - bar["low"], abs(bar["close"]) * 0.0001)
        if bar["low"] <= vwap <= bar["high"]:
            touches += 1
            if abs(bar["close"] - vwap) >= span * 0.25:
                rejections += 1
    return rejections / touches if touches else 0.0


def round_bounce_rate(bars: list[dict[str, float]]) -> float | None:
    if len(bars) < 20:
        return None
    closes = [bar["close"] for bar in bars]
    price_scale = max(abs(mean(closes)), 1e-9)
    grid = 0.01 if price_scale > 50 else 0.001
    if price_scale > 1000:
        grid = 10.0
    touches = 0
    bounces = 0
    for bar in bars:
        nearest_low = round(bar["low"] / grid) * grid
        nearest_high = round(bar["high"] / grid) * grid
        threshold = grid * 0.08
        touched = abs(bar["low"] - nearest_low) <= threshold or abs(bar["high"] - nearest_high) <= threshold
        if not touched:
            continue
        touches += 1
        span = max(bar["high"] - bar["low"], grid)
        if abs(bar["close"] - nearest_low) >= span * 0.25 or abs(bar["close"] - nearest_high) >= span * 0.25:
            bounces += 1
    return bounces / touches if touches else 0.0


def infer_asset_tf(path: Path, supported_tfs: list[str]) -> tuple[str, str]:
    stem = path.stem.upper().replace("-", "_")
    for tf in sorted((normalize_tf(tf) for tf in supported_tfs), key=len, reverse=True):
        suffix = f"_{tf}"
        if stem.endswith(suffix):
            return stem[: -len(suffix)], tf
    raise ValueError(f"Could not infer asset/timeframe from {path.name}")


def output_file_for(tf: str, policy: dict[str, Any]) -> str:
    return policy.get("outputFiles", {}).get(normalize_tf(tf), f"asset_metrics_{normalize_tf(tf)}.json")


def build_metrics_for_bars(asset: str, tf: str, bars: list[dict[str, float]], asset_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    closes = [bar["close"] for bar in bars]
    asset_meta = asset_index.get(asset.upper(), {})
    return {
        "type": asset_meta.get("type", "unknown"),
        "subtype": asset_meta.get("sub", "unknown"),
        "source_timeframe": normalize_tf(tf),
        "source": "operator_supplied_ohlc_csv",
        "bar_count": len(bars),
        "adx_mean": rounded(adx_mean(bars), 4),
        "trend_efficiency_200": rounded(trend_efficiency(closes), 4),
        "sma200_persistence_bars": rounded(sma_persistence(closes), 2),
        "rsi_edge_in_atrs": rounded(rsi_edge_in_atrs(bars), 4),
        "atr_pct_mean": rounded(atr_pct_mean(bars), 4),
        "vol_of_vol": rounded(vol_of_vol(bars), 4),
        "hurst_dist": rounded(hurst_dist(closes), 4),
        f"ou_half_life_{normalize_tf(tf).lower()}": rounded(ou_half_life(closes), 2),
        "kurtosis": rounded(kurtosis(closes), 4),
        "vwap_rejection_rate": rounded(vwap_rejection_rate(bars), 4),
        "round_bounce_rate": rounded(round_bounce_rate(bars), 4),
    }


def build_metric_files(
    *,
    input_dir: Path,
    out_dir: Path = DEFAULT_OUT_DIR,
    policy_path: Path = DEFAULT_POLICY_PATH,
    assets_path: Path = DEFAULT_ASSETS_PATH,
) -> dict[str, Any]:
    policy = read_json(policy_path)
    supported_tfs = [normalize_tf(tf) for tf in policy["supportedTimeframes"]]
    min_bars = int(policy["minimumBars"])
    asset_index = load_asset_index(assets_path)
    by_tf: dict[str, dict[str, Any]] = {tf: {} for tf in supported_tfs}
    files: list[dict[str, Any]] = []
    failures: list[str] = []

    for path in sorted(input_dir.glob("*.csv")):
        try:
            asset, tf = infer_asset_tf(path, supported_tfs)
            bars = read_ohlc_csv(path, policy)
            if len(bars) < min_bars:
                failures.append(f"{path.name} has {len(bars)} bars below minimum {min_bars}")
                files.append({"file": str(path), "asset": asset, "tf": tf, "status": "too_few_bars", "bars": len(bars)})
                continue
            by_tf[tf][asset] = build_metrics_for_bars(asset, tf, bars, asset_index)
            files.append({"file": str(path), "asset": asset, "tf": tf, "status": "processed", "bars": len(bars)})
        except Exception as exc:
            failures.append(f"{path.name}: {exc}")
            files.append({"file": str(path), "status": "failed", "reason": str(exc)})

    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for tf, payload in by_tf.items():
        if not payload:
            continue
        target = out_dir / output_file_for(tf, policy)
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        outputs[tf] = str(target)

    report = {
        "metadata": {
            "phase": "A55",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "inputDir": str(input_dir),
            "outDir": str(out_dir),
            "policyState": policy["state"],
            "minimumBars": min_bars,
            "syntheticTimeframesAllowed": policy["syntheticTimeframesAllowed"],
            "caveat": "Metrics are computed only from operator-supplied OHLC CSV files; missing timeframes are not synthesized.",
        },
        "status": "GO" if outputs and not failures else "NO_GO",
        "outputs": outputs,
        "files": files,
        "failures": failures,
    }
    manifest_path = out_dir / "ohlc_metric_source_manifest.json"
    manifest_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report["manifestPath"] = str(manifest_path)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SQX OHLC Metric Builder",
        "",
        f"- Phase: `{report['metadata']['phase']}`",
        f"- Status: `{report['status']}`",
        f"- Input dir: `{report['metadata']['inputDir']}`",
        f"- Output dir: `{report['metadata']['outDir']}`",
        f"- Caveat: {report['metadata']['caveat']}",
        "",
        "## Outputs",
        "",
    ]
    if report["outputs"]:
        lines.extend(f"- {tf}: `{path}`" for tf, path in sorted(report["outputs"].items()))
    else:
        lines.append("- No metric files generated.")
    if report["failures"]:
        lines += ["", "## Failures", ""]
        lines.extend(f"- {failure}" for failure in report["failures"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SQX asset_metrics JSON files from OHLC CSV files.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("--assets", default=str(DEFAULT_ASSETS_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_metric_files(
        input_dir=Path(args.input_dir),
        out_dir=Path(args.out_dir),
        policy_path=Path(args.policy),
        assets_path=Path(args.assets),
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    print(text)
    return 0 if report["status"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
