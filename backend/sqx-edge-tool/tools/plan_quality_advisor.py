"""
Plan Quality Advisor for SQX Edge.

This tool adapts the useful idea from the compared Jose Livan repository:
rank the current mining plan against dashboard score data and propose a
diversified, data-informed candidate plan.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
CONFIG_DIR = TOOL_ROOT / "config"
APP_JS_DIR = PROJECT_ROOT / "app" / "js"

DEFAULT_LIMIT = 14
DEFAULT_MIN_COMPOSITE = 60.0
DEFAULT_MAX_PER_ASSET = 2
DEFAULT_MAX_PER_CATEGORY = 4
DEFAULT_MAX_PER_SUBTYPE = 5


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_js_assignment(path: Path, variable_name: str) -> Any:
    """Read a JSON object assigned as `window.NAME = {...};`."""
    text = path.read_text(encoding="utf-8").strip()
    prefix = f"window.{variable_name} = "
    if not text.startswith(prefix):
        raise ValueError(f"{path} does not start with {prefix!r}")
    payload = text[len(prefix) :]
    payload = re.sub(r";\s*$", "", payload, count=1, flags=re.DOTALL)
    return json.loads(payload)


def normalize_direction(direction: str) -> str:
    value = str(direction or "").strip().upper()
    if value in {"L/S", "L+S", "BOTH", "LONG/SHORT"}:
        return "L/S"
    if value in {"L", "LONG"}:
        return "L"
    if value in {"S", "SHORT"}:
        return "S"
    return value or "?"


def strip_strategy_version(bs_name: str) -> str:
    return re.sub(r"_v\d+$", "", str(bs_name or ""))


def build_bs_to_category(ui_manifest: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for category, bs_name in (ui_manifest.get("priorityCatToBs") or {}).items():
        out[strip_strategy_version(bs_name)] = category
    for bs_name, category in (ui_manifest.get("bsToPriorityCat") or {}).items():
        out[strip_strategy_version(bs_name)] = category
    for category, bs_name in (ui_manifest.get("catToBs") or {}).items():
        out[strip_strategy_version(bs_name)] = category
    return out


def split_timeframes(raw: str) -> list[str]:
    return [part.strip().upper() for part in str(raw or "").split(",") if part.strip()]


def score_entry(scores: dict[str, Any], asset: str, category: str) -> dict[str, Any] | None:
    asset_scores = scores.get(asset) or {}
    entry = asset_scores.get(category)
    if not isinstance(entry, dict):
        return None
    composite = entry.get("composite_score")
    if composite is None:
        return None
    return entry


def composite_pct(entry: dict[str, Any]) -> float:
    return round(float(entry["composite_score"]) * 100, 1)


def is_macro_excluded(candidate: dict[str, Any]) -> str | None:
    if (
        candidate["category"] == "tendencia"
        and candidate["direction"] == "S"
        and candidate["asset_type"] in {"index", "oro"}
    ):
        return "short tendencial en indice/oro contra bias estructural"
    return None


def build_candidates(
    assets_manifest: dict[str, Any],
    ui_manifest: dict[str, Any],
    scores: dict[str, Any],
    *,
    include_macro_excluded: bool = False,
) -> list[dict[str, Any]]:
    priority_bs = ui_manifest.get("priorityCatToBs") or {}
    candidates: list[dict[str, Any]] = []
    for asset in assets_manifest.get("assets") or []:
        asset_id = asset.get("id")
        if not asset_id:
            continue
        for category, definition in (asset.get("cats") or {}).items():
            base_category = re.sub(r"_S$", "", category)
            entry = score_entry(scores, asset_id, base_category)
            if not entry:
                continue
            for tf in split_timeframes(definition.get("tf")):
                candidate = {
                    "asset": asset_id,
                    "asset_type": asset.get("type", ""),
                    "subtype": asset.get("sub", ""),
                    "category": base_category,
                    "bs": priority_bs.get(base_category, base_category),
                    "tf": tf,
                    "direction": normalize_direction(definition.get("dir")),
                    "editorial_rating": definition.get("rating"),
                    "objective_rating": entry.get("objective"),
                    "composite": composite_pct(entry),
                    "score_source": "app/js/scores-data.js:H1-baseline",
                    "why": definition.get("why", ""),
                }
                macro_reason = is_macro_excluded(candidate)
                if macro_reason and not include_macro_excluded:
                    continue
                if macro_reason:
                    candidate["macro_warning"] = macro_reason
                candidates.append(candidate)
    candidates.sort(key=lambda item: (-item["composite"], item["asset"], item["category"], item["tf"]))
    return candidates


def recommend_plan(
    candidates: list[dict[str, Any]],
    *,
    limit: int = DEFAULT_LIMIT,
    min_composite: float = DEFAULT_MIN_COMPOSITE,
    max_per_asset: int = DEFAULT_MAX_PER_ASSET,
    max_per_category: int = DEFAULT_MAX_PER_CATEGORY,
    max_per_subtype: int = DEFAULT_MAX_PER_SUBTYPE,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    by_asset: Counter[str] = Counter()
    by_asset_category: Counter[tuple[str, str]] = Counter()
    by_category: Counter[str] = Counter()
    by_subtype: Counter[str] = Counter()
    seen: set[tuple[str, str, str, str]] = set()

    for candidate in candidates:
        if candidate["composite"] < min_composite:
            continue
        key = (candidate["asset"], candidate["category"], candidate["tf"], candidate["direction"])
        if key in seen:
            continue
        if by_asset[candidate["asset"]] >= max_per_asset:
            continue
        if by_asset_category[(candidate["asset"], candidate["category"])] >= 1:
            continue
        if by_category[candidate["category"]] >= max_per_category:
            continue
        if by_subtype[candidate["subtype"]] >= max_per_subtype:
            continue
        seen.add(key)
        by_asset[candidate["asset"]] += 1
        by_asset_category[(candidate["asset"], candidate["category"])] += 1
        by_category[candidate["category"]] += 1
        by_subtype[candidate["subtype"]] += 1
        selected.append({**candidate, "recommended_rank": len(selected) + 1})
        if len(selected) >= limit:
            break
    return selected


def annotate_current_plan(
    plan_manifest: dict[str, Any],
    scores: dict[str, Any],
    bs_to_category: dict[str, str],
) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for item in plan_manifest.get("minings") or []:
        bs = strip_strategy_version(item.get("bs", ""))
        category = bs_to_category.get(bs)
        entry = score_entry(scores, item.get("asset", ""), category or "")
        composite = composite_pct(entry) if entry else None
        if composite is None:
            verdict = "sin_score"
        elif composite >= 85:
            verdict = "maxima"
        elif composite >= 70:
            verdict = "alta"
        elif composite >= 60:
            verdict = "apta"
        elif composite >= 40:
            verdict = "secundaria"
        else:
            verdict = "revisar"
        annotated.append(
            {
                "num": item.get("num"),
                "phase": item.get("phase"),
                "asset": item.get("asset"),
                "tf": item.get("tf"),
                "bs": item.get("bs"),
                "category": category,
                "direction": normalize_direction(item.get("dir")),
                "composite": composite,
                "objective_rating": entry.get("objective") if entry else None,
                "verdict": verdict,
            }
        )
    return annotated


def diff_plan(current: list[dict[str, Any]], recommended: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    def cur_key(item: dict[str, Any]) -> tuple[str, str, str, str]:
        return (item["asset"], item.get("category") or "", item["tf"], item["direction"])

    current_by_key = {cur_key(item): item for item in current}
    recommended_by_key = {
        (item["asset"], item["category"], item["tf"], item["direction"]): item for item in recommended
    }
    keep_keys = sorted(set(current_by_key) & set(recommended_by_key))
    drop_keys = sorted(set(current_by_key) - set(recommended_by_key))
    add_keys = sorted(set(recommended_by_key) - set(current_by_key))
    return {
        "keep": [current_by_key[key] for key in keep_keys],
        "review_not_selected": [current_by_key[key] for key in drop_keys],
        "add": [recommended_by_key[key] for key in add_keys],
    }


def summarize_current_plan(current: list[dict[str, Any]]) -> dict[str, Any]:
    verdicts = Counter(item["verdict"] for item in current)
    supported = sum(1 for item in current if item["verdict"] in {"maxima", "alta", "apta"})
    needs_review = sum(1 for item in current if item["verdict"] in {"secundaria", "revisar", "sin_score"})
    return {
        "supported": supported,
        "needsReview": needs_review,
        "verdicts": dict(sorted(verdicts.items())),
    }


def build_report(
    *,
    limit: int = DEFAULT_LIMIT,
    min_composite: float = DEFAULT_MIN_COMPOSITE,
    max_per_asset: int = DEFAULT_MAX_PER_ASSET,
    max_per_category: int = DEFAULT_MAX_PER_CATEGORY,
    max_per_subtype: int = DEFAULT_MAX_PER_SUBTYPE,
) -> dict[str, Any]:
    assets_manifest = read_json(CONFIG_DIR / "assets.json")
    ui_manifest = read_json(CONFIG_DIR / "ui_manifest.json")
    plan_manifest = read_json(CONFIG_DIR / "plan.json")
    scores = read_js_assignment(APP_JS_DIR / "scores-data.js", "SQX_SCORES_DATA")

    candidates = build_candidates(assets_manifest, ui_manifest, scores)
    recommended = recommend_plan(
        candidates,
        limit=limit,
        min_composite=min_composite,
        max_per_asset=max_per_asset,
        max_per_category=max_per_category,
        max_per_subtype=max_per_subtype,
    )
    current = annotate_current_plan(plan_manifest, scores, build_bs_to_category(ui_manifest))
    return {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "phase": "A47",
            "sourceImprovement": "Data-driven plan recommender pattern from compared Jose Livan repository",
            "scoreDataset": "app/js/scores-data.js H1 baseline",
            "candidateCount": len(candidates),
            "currentPlanCount": len(current),
            "recommendedPlanCount": len(recommended),
            "constraints": {
                "limit": limit,
                "minComposite": min_composite,
                "maxPerAsset": max_per_asset,
                "maxPerCategory": max_per_category,
                "maxPerSubtype": max_per_subtype,
            },
            "caveat": "Current implementation uses the available H1 score baseline; multi-timeframe metrics remain a future upgrade.",
        },
        "currentPlanSummary": summarize_current_plan(current),
        "currentPlan": current,
        "recommendedPlan": recommended,
        "diff": diff_plan(current, recommended),
    }


def render_markdown(report: dict[str, Any]) -> str:
    meta = report["metadata"]
    lines = [
        "# SQX Plan Quality Advisor",
        "",
        f"- Phase: `{meta['phase']}`",
        f"- Score dataset: `{meta['scoreDataset']}`",
        f"- Candidates analyzed: `{meta['candidateCount']}`",
        f"- Current plan items: `{meta['currentPlanCount']}`",
        f"- Recommended items: `{meta['recommendedPlanCount']}`",
        f"- Current plan supported: `{report['currentPlanSummary']['supported']}`",
        f"- Current plan needs review: `{report['currentPlanSummary']['needsReview']}`",
        f"- Caveat: {meta['caveat']}",
        "",
        "## Current Plan Review",
        "",
        "| # | Asset | TF | BS | Dir | Composite | Verdict |",
        "| ---: | --- | --- | --- | --- | ---: | --- |",
    ]
    for item in report["currentPlan"]:
        comp = "-" if item["composite"] is None else f"{item['composite']:.1f}"
        lines.append(
            f"| {item['num']} | {item['asset']} | {item['tf']} | {item['bs']} | "
            f"{item['direction']} | {comp} | {item['verdict']} |"
        )
    lines += [
        "",
        "## Recommended Plan",
        "",
        "| Rank | Asset | TF | BS | Dir | Composite | Subtype |",
        "| ---: | --- | --- | --- | --- | ---: | --- |",
    ]
    for item in report["recommendedPlan"]:
        lines.append(
            f"| {item['recommended_rank']} | {item['asset']} | {item['tf']} | {item['bs']} | "
            f"{item['direction']} | {item['composite']:.1f} | {item['subtype']} |"
        )
    lines += [
        "",
        "## Delta",
        "",
        f"- Keep: {len(report['diff']['keep'])}",
        f"- Review, not automatically drop: {len(report['diff']['review_not_selected'])}",
        f"- Add: {len(report['diff']['add'])}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Review SQX plan quality against dashboard scores.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--out", help="Optional output path.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--min-composite", type=float, default=DEFAULT_MIN_COMPOSITE)
    args = parser.parse_args()

    report = build_report(limit=args.limit, min_composite=args.min_composite)
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
