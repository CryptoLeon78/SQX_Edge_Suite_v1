(function () {
  "use strict";

  const VERSION = "sqx144-custom-results8-regime-edge-analyzer-v1";
  const DEFAULT_REGIME_SOURCE = "embedded snapshot or manual fixture";

  const LABELS = {
    strong: "REGIME_STRONG",
    compatible: "REGIME_COMPATIBLE",
    defensive: "REGIME_DEFENSIVE",
    meanRevert: "REGIME_MEAN_REVERT",
    mismatch: "REGIME_MISMATCH_REVIEW",
    adverse: "REGIME_ADVERSE_RISK",
    insufficient: "REGIME_INSUFFICIENT",
    unknown: "REGIME_UNKNOWN"
  };

  const REGIME_COLORS = {
    BULL: "#25a66a",
    BEAR: "#d84d43",
    SIDEWAYS: "#d79a2b",
    MIXED: "#7f8b98",
    UNKNOWN: "#8b8f85"
  };

  const REPAIR_ACTIONS = {
    orders: "Activar Regime Orders antes de concluir comportamiento anual.",
    series: "Confirmar serie de mercado Data Manager o fallback embebido antes de decidir.",
    timestamps: "No usar lectura anual hasta corregir timestamps de ordenes.",
    trades: "No promover; ampliar evidencia o descartar si no alcanza muestra minima.",
    aligned: "No rescatar con filtros; volver a robustez si falla en su regimen favorable.",
    adverse: "Revisar clusters de DD en regimen adverso antes de portfolio.",
    direction: "Confirmar direccion long/short y aplicar override si SQX no la expone.",
    quality: "Tratar como diagnostico parcial; faltan datos suficientes para decision fuerte."
  };

  function number(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : NaN;
  }

  function clamp(value, low, high) {
    return Math.max(low, Math.min(high, value));
  }

  function pct(value) {
    return Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "-";
  }

  function fmt(value, digits) {
    return Number.isFinite(value) ? value.toFixed(digits || 2) : "-";
  }

  function sum(values) {
    return values.reduce((acc, value) => acc + (Number.isFinite(value) ? value : 0), 0);
  }

  function mean(values) {
    const finite = values.filter(Number.isFinite);
    return finite.length ? sum(finite) / finite.length : NaN;
  }

  function sd(values) {
    const avg = mean(values);
    const finite = values.filter(Number.isFinite);
    if (!finite.length || !Number.isFinite(avg)) return NaN;
    return Math.sqrt(mean(finite.map((value) => Math.pow(value - avg, 2)))) || 0;
  }

  function parseDate(value) {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    return date;
  }

  function metric(stats, names) {
    const keys = Array.isArray(names) ? names : [names];
    for (const key of keys) {
      if (stats && Object.prototype.hasOwnProperty.call(stats, key)) {
        const value = number(stats[key]);
        if (Number.isFinite(value)) return value;
      }
    }
    return NaN;
  }

  function normalizeStatsPayload(payload) {
    if (!payload) return null;
    if (payload.stats) return payload.stats;
    if (payload.data && payload.data.stats) return payload.data.stats;
    return payload;
  }

  function normalizeOrders(payload) {
    const raw = Array.isArray(payload) ? payload : (payload && (payload.orders || payload.data || payload.Orders)) || [];
    if (!Array.isArray(raw)) return [];
    return raw.map((item, index) => {
      const profit = metric(item, ["profit", "Profit", "pl", "PL", "pnl", "Pnl", "netProfit", "NetProfit"]);
      const closeDate = parseDate(item.closeTime || item.CloseTime || item.exitTime || item.ExitTime || item.time || item.Time || item.date || item.Date);
      const openDate = parseDate(item.openTime || item.OpenTime || item.entryTime || item.EntryTime);
      return {
        index,
        profit,
        date: closeDate || openDate,
        hasTimestamp: !!(closeDate || openDate),
        side: normalizeSide(item.side || item.Side || item.direction || item.Direction || item.type || item.Type)
      };
    });
  }

  function normalizeSide(value) {
    const raw = String(value || "").trim().toLowerCase();
    if (!raw) return "unknown";
    if (raw.includes("short") || raw === "sell" || raw === "-1" || raw === "s") return "short";
    if (raw.includes("long") || raw === "buy" || raw === "1" || raw === "l") return "long";
    return "unknown";
  }

  function normalizeMarketSeries(payload) {
    const source = Array.isArray(payload) ? payload : (payload && (payload.bars || payload.series || payload.data)) || [];
    if (!Array.isArray(source)) return [];
    return source.map((item) => {
      const date = parseDate(item.time || item.date || item.Date || item.Time);
      const close = number(item.close || item.Close || item.price || item.Price);
      const label = normalizeRegime(item.regime || item.label || item.Regime);
      return { date, close, label };
    }).filter((item) => item.date && (Number.isFinite(item.close) || item.label !== "UNKNOWN"));
  }

  function normalizeRegime(value) {
    const raw = String(value || "").trim().toUpperCase();
    if (raw.includes("BULL") || raw.includes("UP")) return "BULL";
    if (raw.includes("BEAR") || raw.includes("DOWN")) return "BEAR";
    if (raw.includes("SIDE") || raw.includes("RANGE") || raw.includes("FLAT")) return "SIDEWAYS";
    if (raw.includes("MIX")) return "MIXED";
    return "UNKNOWN";
  }

  function groupByYear(items) {
    const map = new Map();
    items.forEach((item) => {
      if (!item.date) return;
      const year = item.date.getUTCFullYear();
      if (!map.has(year)) map.set(year, []);
      map.get(year).push(item);
    });
    return map;
  }

  function classifyAnnualRegimes(series) {
    const byYear = groupByYear(normalizeMarketSeries(series));
    const rows = Array.from(byYear.entries()).map(([year, bars]) => {
      const sorted = bars.slice().sort((a, b) => a.date - b.date);
      const labels = sorted.map((item) => item.label).filter((item) => item !== "UNKNOWN");
      const labelCounts = labels.reduce((acc, label) => {
        acc[label] = (acc[label] || 0) + 1;
        return acc;
      }, {});
      const labelWinner = Object.entries(labelCounts).sort((a, b) => b[1] - a[1])[0];
      const first = sorted.find((item) => Number.isFinite(item.close));
      const last = sorted.slice().reverse().find((item) => Number.isFinite(item.close));
      const closes = sorted.map((item) => item.close).filter(Number.isFinite);
      const totalMove = first && last && first.close !== 0 ? (last.close - first.close) / Math.abs(first.close) : NaN;
      let stepMove = 0;
      for (let i = 1; i < closes.length; i += 1) stepMove += Math.abs(closes[i] - closes[i - 1]);
      const efficiency = first && last && stepMove > 0 ? Math.abs(last.close - first.close) / stepMove : NaN;
      const monthCount = new Set(sorted.map((item) => `${item.date.getUTCFullYear()}-${item.date.getUTCMonth()}`)).size;
      return {
        year,
        bars: sorted.length,
        months: monthCount,
        returnPct: totalMove,
        efficiency,
        labelWinner: labelWinner ? labelWinner[0] : "UNKNOWN",
        regime: "UNKNOWN",
        quality: sorted.length >= 120 || monthCount >= 9 ? "ok" : "thin"
      };
    }).sort((a, b) => a.year - b.year);
    const returns = rows.map((row) => row.returnPct).filter(Number.isFinite);
    const avg = mean(returns);
    const sigma = sd(returns);
    rows.forEach((row) => {
      if (row.quality !== "ok") {
        row.regime = "UNKNOWN";
        return;
      }
      if (row.labelWinner !== "UNKNOWN") {
        row.regime = row.labelWinner;
        return;
      }
      const z = sigma > 0 ? (row.returnPct - avg) / sigma : 0;
      row.zScore = z;
      if (Number.isFinite(row.returnPct) && row.returnPct > 0 && z >= 0.35 && row.efficiency >= 0.10) row.regime = "BULL";
      else if (Number.isFinite(row.returnPct) && row.returnPct < 0 && z <= -0.35 && row.efficiency >= 0.10) row.regime = "BEAR";
      else if (Math.abs(z) <= 0.20 || row.efficiency < 0.08 || Math.abs(row.returnPct) < 0.03) row.regime = "SIDEWAYS";
      else row.regime = "MIXED";
    });
    return rows;
  }

  function maxLossStreak(items) {
    let current = 0;
    let max = 0;
    items.forEach((item) => {
      if (item.profit < 0) {
        current += 1;
        max = Math.max(max, current);
      } else {
        current = 0;
      }
    });
    return max;
  }

  function equityDrawdown(items) {
    let equity = 0;
    let peak = 0;
    let maxDd = 0;
    items.forEach((item) => {
      equity += Number.isFinite(item.profit) ? item.profit : 0;
      peak = Math.max(peak, equity);
      maxDd = Math.max(maxDd, peak - equity);
    });
    return maxDd;
  }

  function aggregateOrders(items) {
    const valid = items.filter((item) => Number.isFinite(item.profit));
    const wins = valid.filter((item) => item.profit > 0);
    const losses = valid.filter((item) => item.profit < 0);
    const grossWin = sum(wins.map((item) => item.profit));
    const grossLoss = Math.abs(sum(losses.map((item) => item.profit)));
    const sideCounts = valid.reduce((acc, item) => {
      acc[item.side] = (acc[item.side] || 0) + 1;
      return acc;
    }, {});
    return {
      trades: valid.length,
      net: sum(valid.map((item) => item.profit)),
      profitFactor: grossLoss > 0 ? grossWin / grossLoss : (grossWin > 0 ? 99 : NaN),
      expectancy: valid.length ? sum(valid.map((item) => item.profit)) / valid.length : NaN,
      winRate: valid.length ? wins.length / valid.length : NaN,
      maxLossStreak: maxLossStreak(valid),
      maxDrawdown: equityDrawdown(valid),
      worstTrade: valid.length ? Math.min(...valid.map((item) => item.profit)) : NaN,
      sideCounts
    };
  }

  function yearlyOrderStats(orders) {
    const normalized = normalizeOrders(orders);
    const timestamped = normalized.filter((item) => item.hasTimestamp);
    const byYear = groupByYear(timestamped);
    const rows = Array.from(byYear.entries()).map(([year, items]) => Object.assign({ year }, aggregateOrders(items)));
    rows.sort((a, b) => a.year - b.year);
    return {
      rows,
      normalized,
      timestampCoverage: normalized.length ? timestamped.length / normalized.length : 0,
      missingTimestampCount: normalized.length - timestamped.length
    };
  }

  function detectDirection(strategy, stats, orders, override) {
    const explicit = String(override || "").trim();
    if (["long_only", "short_only", "long_short", "mean_reversion"].includes(explicit)) {
      return { direction: explicit, confidence: "manual" };
    }
    const raw = [
      strategy && strategy.direction,
      strategy && strategy.Direction,
      strategy && strategy.name,
      strategy && strategy.strategyName,
      stats && stats.Direction
    ].filter(Boolean).join(" ").toLowerCase();
    if (raw.includes("mean") || raw.includes("revert") || raw.includes("sideways") || raw.includes("range")) return { direction: "mean_reversion", confidence: "name" };
    if (raw.includes("long_short") || raw.includes("long/short") || raw.includes("both")) return { direction: "long_short", confidence: "metadata" };
    if (raw.includes("short") || raw.includes("_s_") || raw.endsWith("_s")) return { direction: "short_only", confidence: "metadata" };
    if (raw.includes("long") || raw.includes("_l_") || raw.endsWith("_l")) return { direction: "long_only", confidence: "metadata" };
    const sideCounts = aggregateOrders(normalizeOrders(orders)).sideCounts || {};
    if ((sideCounts.long || 0) > 0 && (sideCounts.short || 0) > 0) return { direction: "long_short", confidence: "orders" };
    if ((sideCounts.short || 0) > (sideCounts.long || 0)) return { direction: "short_only", confidence: "orders" };
    if ((sideCounts.long || 0) > 0) return { direction: "long_only", confidence: "orders" };
    return { direction: "long_only", confidence: "fallback" };
  }

  function alignedRegimesFor(direction) {
    if (direction === "short_only") return ["BEAR"];
    if (direction === "long_short") return ["BULL", "BEAR"];
    if (direction === "mean_reversion") return ["SIDEWAYS"];
    return ["BULL"];
  }

  function adverseRegimesFor(direction) {
    if (direction === "short_only") return ["BULL"];
    if (direction === "mean_reversion") return ["BULL", "BEAR"];
    return ["BEAR"];
  }

  function combineYearRows(orderRows, regimeRows) {
    const regimes = new Map(regimeRows.map((row) => [row.year, row]));
    return orderRows.map((row) => {
      const regime = regimes.get(row.year) || { regime: "UNKNOWN", quality: "thin" };
      return Object.assign({}, row, {
        regime: regime.regime,
        marketReturnPct: regime.returnPct,
        marketEfficiency: regime.efficiency,
        marketQuality: regime.quality
      });
    });
  }

  function aggregateRows(rows, regimes) {
    const selected = rows.filter((row) => regimes.includes(row.regime));
    const trades = sum(selected.map((row) => row.trades));
    const net = sum(selected.map((row) => row.net));
    const grossWinEstimate = sum(selected.filter((row) => row.net > 0).map((row) => row.net));
    const grossLossEstimate = Math.abs(sum(selected.filter((row) => row.net < 0).map((row) => row.net)));
    return {
      trades,
      net,
      profitFactor: grossLossEstimate > 0 ? grossWinEstimate / grossLossEstimate : (grossWinEstimate > 0 ? 99 : NaN),
      expectancy: trades ? net / trades : NaN,
      winRate: trades ? sum(selected.map((row) => row.winRate * row.trades)) / trades : NaN,
      maxLossStreak: selected.length ? Math.max(...selected.map((row) => row.maxLossStreak || 0)) : 0,
      maxDrawdown: selected.length ? Math.max(...selected.map((row) => row.maxDrawdown || 0)) : 0,
      worstTrade: selected.length ? Math.min(...selected.map((row) => Number.isFinite(row.worstTrade) ? row.worstTrade : 0)) : NaN,
      yearCount: selected.length,
      rows: selected
    };
  }

  function scoreFromAggregate(agg, targetTrades) {
    if (!agg || agg.trades === 0) return 0;
    const tradeScore = clamp(agg.trades / targetTrades, 0, 1);
    const pfScore = Number.isFinite(agg.profitFactor) ? clamp((agg.profitFactor - 1) / 0.6, 0, 1) : 0;
    const netScore = agg.net > 0 ? 1 : 0;
    return Math.round((tradeScore * 0.3 + pfScore * 0.4 + netScore * 0.3) * 100);
  }

  function evaluateRegime(strategy, statsPayload, ordersPayload, marketPayload, options) {
    const opts = options || {};
    const stats = normalizeStatsPayload(statsPayload) || {};
    const orders = normalizeOrders(ordersPayload);
    const marketSeries = normalizeMarketSeries(marketPayload);
    const directionInfo = detectDirection(strategy || {}, stats, orders, opts.directionOverride);
    const reasons = [];
    if (!strategy) {
      return baseDecision(LABELS.unknown, 0, directionInfo, [{ code: "NO_STRATEGY", text: "No strategy selected.", repairAction: REPAIR_ACTIONS.quality }]);
    }
    if (!orders.length) {
      reasons.push({ code: "ORDERS_REQUIRED", text: "Orders are required for annual regime behavior.", repairAction: REPAIR_ACTIONS.orders });
    }
    if (!marketSeries.length) {
      reasons.push({ code: "MARKET_SERIES_MISSING", text: "Market series is missing or unavailable.", repairAction: REPAIR_ACTIONS.series });
    }
    if (orders.length && marketSeries.length) {
      const annualOrders = yearlyOrderStats(orders);
      const annualRegimes = classifyAnnualRegimes(marketSeries);
      const rows = combineYearRows(annualOrders.rows, annualRegimes);
      const aligned = aggregateRows(rows, alignedRegimesFor(directionInfo.direction));
      const adverse = aggregateRows(rows, adverseRegimesFor(directionInfo.direction));
      const positiveYears = rows.filter((row) => row.net > 0).length;
      const timestampScore = annualOrders.timestampCoverage;
      const alignedScore = scoreFromAggregate(aligned, 30);
      const adverseScore = adverse.trades === 0 ? 50 : (adverse.net >= 0 ? 100 : clamp(100 + adverse.net / Math.max(1, Math.abs(aligned.net || 1)) * 100, 0, 85));
      const consistencyScore = rows.length ? Math.round((positiveYears / rows.length) * 100) : 0;
      const qualityScore = Math.round((timestampScore * 0.55 + clamp(orders.length / 120, 0, 1) * 0.25 + clamp(annualRegimes.filter((row) => row.regime !== "UNKNOWN").length / Math.max(1, annualRegimes.length), 0, 1) * 0.20) * 100);
      const score = Math.round(alignedScore * 0.35 + adverseScore * 0.25 + consistencyScore * 0.20 + qualityScore * 0.20);
      const enoughOrders = orders.length >= 60;
      const enoughAligned = aligned.trades >= 15 && aligned.yearCount >= 1;
      const unknownRegimeShare = annualRegimes.length ? annualRegimes.filter((row) => row.regime === "UNKNOWN").length / annualRegimes.length : 1;
      let label = LABELS.compatible;
      if (annualOrders.timestampCoverage < 0.8 || unknownRegimeShare > 0.35) {
        label = LABELS.unknown;
        reasons.push({ code: "LOW_DATA_QUALITY", text: "Timestamps or market regime coverage are incomplete.", repairAction: REPAIR_ACTIONS.timestamps });
      } else if (!enoughOrders || !enoughAligned) {
        label = LABELS.insufficient;
        reasons.push({ code: "INSUFFICIENT_REGIME_EVIDENCE", text: "Not enough orders or aligned regime years.", repairAction: REPAIR_ACTIONS.trades });
      } else if (aligned.net <= 0) {
        label = LABELS.mismatch;
        reasons.push({ code: "ALIGNED_REGIME_MISMATCH", text: "Strategy loses in its favorable regime.", repairAction: REPAIR_ACTIONS.aligned });
      } else if (adverse.net < 0 && Math.abs(adverse.net) > Math.max(1, aligned.net) * 0.75) {
        label = LABELS.adverse;
        reasons.push({ code: "ADVERSE_REGIME_RISK", text: "Adverse regime losses are too large versus aligned edge.", repairAction: REPAIR_ACTIONS.adverse });
      } else if (directionInfo.direction === "mean_reversion" && aligned.net > 0) {
        label = LABELS.meanRevert;
      } else if (score >= 85 && aligned.profitFactor >= 1.3) {
        label = LABELS.strong;
      } else if (score >= 70) {
        label = LABELS.compatible;
      } else if (score >= 55) {
        label = LABELS.defensive;
      } else {
        label = LABELS.mismatch;
        reasons.push({ code: "REGIME_SCORE_WEAK", text: "Regime score is weak for the detected direction.", repairAction: REPAIR_ACTIONS.direction });
      }
      if (directionInfo.confidence === "fallback") {
        reasons.push({ code: "DIRECTION_FALLBACK", text: "Direction was inferred as long-only fallback.", repairAction: REPAIR_ACTIONS.direction });
      }
      if (!reasons.length) {
        reasons.push({ code: "REGIME_EVIDENCE_OK", text: "Aligned regime edge and data quality are acceptable.", repairAction: "Mantener como evidencia complementaria, no como promocion automatica." });
      }
      return {
        label,
        score,
        direction: directionInfo.direction,
        directionConfidence: directionInfo.confidence,
        reasons,
        rows,
        annualRegimes,
        aligned,
        adverse,
        components: {
          alignedEdge: alignedScore,
          adverseSurvival: Math.round(adverseScore),
          yearlyConsistency: consistencyScore,
          dataQuality: qualityScore
        },
        stats: {
          netProfit: metric(stats, ["NetProfit", "Net profit", "NetProfitIS"]),
          trades: metric(stats, ["NumberOfTrades", "Trades"]),
          profitFactor: metric(stats, ["ProfitFactor", "PF"]),
          returnDd: metric(stats, ["ReturnDDRatio", "Return/DD"])
        },
        methodology: {
          selectedStrategyOnly: true,
          ordersOptIn: true,
          marketSource: opts.marketSource || DEFAULT_REGIME_SOURCE,
          noPromotionState: true
        }
      };
    }
    return baseDecision(
      reasons.some((reason) => reason.code === "ORDERS_REQUIRED" || reason.code === "MARKET_SERIES_MISSING") ? LABELS.unknown : LABELS.insufficient,
      0,
      directionInfo,
      reasons
    );
  }

  function baseDecision(label, score, directionInfo, reasons) {
    return {
      label,
      score,
      direction: directionInfo.direction,
      directionConfidence: directionInfo.confidence,
      reasons,
      rows: [],
      annualRegimes: [],
      aligned: aggregateOrders([]),
      adverse: aggregateOrders([]),
      components: { alignedEdge: 0, adverseSurvival: 0, yearlyConsistency: 0, dataQuality: 0 },
      stats: {},
      methodology: {
        selectedStrategyOnly: true,
        ordersOptIn: true,
        marketSource: DEFAULT_REGIME_SOURCE,
        noPromotionState: true
      }
    };
  }

  function buildSummary(decision, strategy) {
    const name = (strategy && (strategy.name || strategy.strategyName || strategy.id)) || "selected strategy";
    const firstReason = decision.reasons && decision.reasons[0] ? decision.reasons[0] : null;
    return [
      `Regime Edge Analyzer`,
      `Strategy: ${name}`,
      `Label: ${decision.label}`,
      `Regime Score: ${decision.score}/100`,
      `Direction: ${decision.direction} (${decision.directionConfidence})`,
      `Aligned Edge: ${decision.components.alignedEdge}/100`,
      `Adverse Survival: ${decision.components.adverseSurvival}/100`,
      `Yearly Consistency: ${decision.components.yearlyConsistency}/100`,
      `Data Quality: ${decision.components.dataQuality}/100`,
      firstReason ? `Primary reason: ${firstReason.code} - ${firstReason.text}` : "Primary reason: none",
      firstReason ? `Repair action: ${firstReason.repairAction}` : "Repair action: keep as complementary evidence"
    ].join("\n");
  }

  window.SQX_REGIME_EDGE_LOGIC = {
    VERSION,
    LABELS,
    REGIME_COLORS,
    REPAIR_ACTIONS,
    normalizeStatsPayload,
    normalizeOrders,
    normalizeMarketSeries,
    classifyAnnualRegimes,
    yearlyOrderStats,
    detectDirection,
    evaluateRegime,
    buildSummary,
    fmt,
    pct
  };
})();
