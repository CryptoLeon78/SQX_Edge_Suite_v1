"""
Plan Quality Advisor for SQX Edge.

This tool adapts the useful idea from the compared Jose Livan repository:
rank the current mining plan against dashboard score data and propose a
diversified, data-informed candidate plan.
"""
from __future__ import annotations

import argparse
import importlib.util
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


def load_multi_timeframe_scoring():
    path = Path(__file__).with_name("multi_timeframe_scoring.py")
    spec = importlib.util.spec_from_file_location("multi_timeframe_scoring", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def mtf_entry(mtf_report: dict[str, Any] | None, asset: str, category: str | None) -> dict[str, Any] | None:
    if not mtf_report or not category:
        return None
    entry = ((mtf_report.get("consensus") or {}).get(asset) or {}).get(category)
    return entry if isinstance(entry, dict) else None


def mtf_pct(entry: dict[str, Any] | None) -> float | None:
    if not entry:
        return None
    weighted = entry.get("weighted_composite")
    if weighted is None:
        return None
    return round(float(weighted) * 100, 1)


def mtf_assessment(entry: dict[str, Any] | None) -> str:
    if not entry:
        return "missing"
    weighted = float(entry.get("weighted_composite") or 0)
    coverage = int(entry.get("coverage") or 0)
    consensus = entry.get("consensus")
    if coverage < 2:
        return "limited"
    if consensus == "divergent":
        return "divergent"
    if weighted >= 0.75:
        return "strong"
    if weighted >= 0.50:
        return "moderate"
    return "weak"


def enrich_with_mtf(items: list[dict[str, Any]], mtf_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not mtf_report:
        return items
    enriched: list[dict[str, Any]] = []
    for item in items:
        entry = mtf_entry(mtf_report, item.get("asset", ""), item.get("category"))
        if not entry:
            enriched.append({**item, "mtf_assessment": "missing"})
            continue
        enriched.append(
            {
                **item,
                "mtf_composite": mtf_pct(entry),
                "mtf_objective_rating": entry.get("objective"),
                "mtf_coverage": entry.get("coverage"),
                "mtf_consensus": entry.get("consensus"),
                "mtf_best_tf": entry.get("best_tf"),
                "mtf_assessment": mtf_assessment(entry),
            }
        )
    return enriched


def summarize_mtf_plan(items: list[dict[str, Any]]) -> dict[str, Any]:
    assessments = Counter(item.get("mtf_assessment", "missing") for item in items)
    covered = sum(1 for item in items if item.get("mtf_composite") is not None)
    strong = assessments.get("strong", 0)
    review = sum(assessments.get(key, 0) for key in ("divergent", "weak", "limited", "missing"))
    return {
        "covered": covered,
        "strong": strong,
        "needsReview": review,
        "assessments": dict(sorted(assessments.items())),
    }


def maybe_build_mtf_report(
    metrics_dir: Path | None,
    timeframes: list[str] | None,
    weights: dict[str, float] | None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if metrics_dir is None:
        return None, {"available": False, "reason": "not_requested"}
    try:
        mtf = load_multi_timeframe_scoring()
        report = mtf.build_report(metrics_dir=metrics_dir, timeframes=timeframes, weights=weights)
        meta = report["metadata"]
        return report, {
            "available": True,
            "source": str(metrics_dir),
            "timeframesLoaded": meta.get("timeframesLoaded", []),
            "weights": meta.get("weights", {}),
        }
    except Exception as exc:  # Keep H1 plan review usable if optional MTF data is absent.
        return None, {"available": False, "source": str(metrics_dir), "reason": str(exc)}


def build_report(
    *,
    limit: int = DEFAULT_LIMIT,
    min_composite: float = DEFAULT_MIN_COMPOSITE,
    max_per_asset: int = DEFAULT_MAX_PER_ASSET,
    max_per_category: int = DEFAULT_MAX_PER_CATEGORY,
    max_per_subtype: int = DEFAULT_MAX_PER_SUBTYPE,
    mtf_report: dict[str, Any] | None = None,
    mtf_metrics_dir: Path | None = None,
    mtf_timeframes: list[str] | None = None,
    mtf_weights: dict[str, float] | None = None,
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
    mtf_meta: dict[str, Any]
    if mtf_report is None:
        mtf_report, mtf_meta = maybe_build_mtf_report(mtf_metrics_dir, mtf_timeframes, mtf_weights)
    else:
        meta = mtf_report.get("metadata") or {}
        mtf_meta = {
            "available": True,
            "source": "provided_report",
            "timeframesLoaded": meta.get("timeframesLoaded", []),
            "weights": meta.get("weights", {}),
        }
    current = enrich_with_mtf(current, mtf_report)
    recommended = enrich_with_mtf(recommended, mtf_report)
    return {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "phase": "A50",
            "sourceImprovement": "Data-driven plan recommender pattern from compared Jose Livan repository",
            "scoreDataset": "app/js/scores-data.js H1 baseline",
            "multiTimeframe": mtf_meta,
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
            "caveat": "Recommendations still use the H1 baseline for ordering; optional multi-timeframe consensus is added as review evidence, not an automatic replacement.",
        },
        "currentPlanSummary": summarize_current_plan(current),
        "multiTimeframePlanSummary": summarize_mtf_plan(current) if mtf_meta.get("available") else None,
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
        f"- Multi-timeframe: `{', '.join(meta['multiTimeframe']['timeframesLoaded']) if meta['multiTimeframe']['available'] else meta['multiTimeframe']['reason']}`",
        f"- Candidates analyzed: `{meta['candidateCount']}`",
        f"- Current plan items: `{meta['currentPlanCount']}`",
        f"- Recommended items: `{meta['recommendedPlanCount']}`",
        f"- Current plan supported: `{report['currentPlanSummary']['supported']}`",
        f"- Current plan needs review: `{report['currentPlanSummary']['needsReview']}`",
        f"- Caveat: {meta['caveat']}",
        "",
        "## Current Plan Review",
        "",
        "| # | Asset | TF | BS | Dir | H1 Composite | Verdict | MTF Composite | MTF Evidence |",
        "| ---: | --- | --- | --- | --- | ---: | --- | ---: | --- |",
    ]
    for item in report["currentPlan"]:
        comp = "-" if item["composite"] is None else f"{item['composite']:.1f}"
        mtf_comp = "-" if item.get("mtf_composite") is None else f"{item['mtf_composite']:.1f}"
        mtf_evidence = item.get("mtf_assessment", "-")
        if item.get("mtf_consensus") and item.get("mtf_consensus") != item.get("mtf_assessment"):
            mtf_evidence += f" / {item['mtf_consensus']}"
        lines.append(
            f"| {item['num']} | {item['asset']} | {item['tf']} | {item['bs']} | "
            f"{item['direction']} | {comp} | {item['verdict']} | {mtf_comp} | {mtf_evidence} |"
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
    parser.add_argument("--mtf-metrics-dir", help="Optional directory with asset_metrics[_TF].json files.")
    parser.add_argument("--mtf-tf", default="H1,M30,M15,H4", help="Comma-separated TF list for optional MTF evidence.")
    parser.add_argument("--mtf-weights", help="Optional weights, e.g. H1=0.5,M30=0.3,M15=0.2")
    args = parser.parse_args()

    mtf_weights = load_multi_timeframe_scoring().parse_weights(args.mtf_weights) if args.mtf_weights else None
    report = build_report(
        limit=args.limit,
        min_composite=args.min_composite,
        mtf_metrics_dir=Path(args.mtf_metrics_dir) if args.mtf_metrics_dir else None,
        mtf_timeframes=[part.strip().upper() for part in args.mtf_tf.split(",") if part.strip()],
        mtf_weights=mtf_weights,
    )
    text = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_markdown(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
