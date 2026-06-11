(function () {
  "use strict";

  const VERSION = "sqx144-custom-results5-edge-gate-v1";

  const THRESHOLDS = {
    tradesPass: 120,
    tradesReview: 80,
    tradesBlockBelow: 60,
    profitFactorPass: 1.3,
    profitFactorReview: 1.05,
    returnDdPass: 4,
    returnDdReview: 1.5,
    expectancyPass: 0,
    netProfitPass: 0
  };

  const LOCALES = {
    en: {
      title: "SQX Edge Gate",
      subtitle: "Trading Radar",
      verdict: "Verdict",
      context: "Context",
      radar: "Radar",
      reasons: "Reasons",
      nextAction: "Next action",
      orderRadar: "Order Radar",
      activateOrders: "Activate Order Radar",
      waiting: "Waiting for StrategyQuant data",
      noOrders: "Order Radar is opt-in. No order request has been sent yet.",
      ordersWaiting: "Order request sent. Waiting for ORDERS_RESPONSE.",
      disclaimer: "Diagnostic decision panel only. No pass-state promotion and no host mutation.",
      pass: "PASS",
      review: "REVIEW",
      block: "BLOCK"
    },
    es: {
      title: "SQX Edge Gate",
      subtitle: "Trading Radar",
      verdict: "Veredicto",
      context: "Contexto",
      radar: "Radar",
      reasons: "Razones",
      nextAction: "Siguiente accion",
      orderRadar: "Order Radar",
      activateOrders: "Activar Order Radar",
      waiting: "Esperando datos de StrategyQuant",
      noOrders: "Order Radar es opt-in. Aun no se ha enviado ninguna peticion de ordenes.",
      ordersWaiting: "Peticion de ordenes enviada. Esperando ORDERS_RESPONSE.",
      disclaimer: "Panel diagnostico de decision. No promociona estados ni muta el host.",
      pass: "PASS",
      review: "REVIEW",
      block: "BLOCK"
    }
  };

  function metric(stats, names) {
    const keys = Array.isArray(names) ? names : [names];
    for (const key of keys) {
      if (stats && Object.prototype.hasOwnProperty.call(stats, key)) {
        const value = Number(stats[key]);
        if (Number.isFinite(value)) return value;
      }
    }
    return NaN;
  }

  function fmt(value, digits) {
    return Number.isFinite(value) ? value.toFixed(digits) : "-";
  }

  function scale(value, low, high) {
    if (!Number.isFinite(value)) return 35;
    if (high <= low) return 0;
    const clamped = Math.max(low, Math.min(high, value));
    return Math.round(((clamped - low) / (high - low)) * 100);
  }

  function hasOosEvidence(strategy, stats) {
    const raw = [
      strategy && strategy.sampleType,
      strategy && strategy.sample,
      strategy && strategy.oosStart,
      strategy && strategy.oosCutoff,
      strategy && strategy.dateOOS,
      stats && stats.sampleType,
      stats && stats.SampleType,
      stats && stats.OOS,
      stats && stats.OutOfSample
    ].filter(Boolean).join(" ").toLowerCase();
    return raw.includes("oos") || raw.includes("out") || raw.includes("20");
  }

  function stateFor(value, pass, review, opts) {
    const options = opts || {};
    if (!Number.isFinite(value)) return options.missing || "review";
    if (value >= pass) return "pass";
    if (value >= review) return "review";
    return "block";
  }

  function buildChecks(strategy, stats) {
    const trades = metric(stats, ["NumberOfTrades", "Trades"]);
    const profitFactor = metric(stats, ["ProfitFactor", "PF"]);
    const returnDd = metric(stats, ["ReturnDDRatio", "RetDD", "ReturnToDrawdown"]);
    const expectancy = metric(stats, ["RExpectancy", "Expectancy", "AvgProfit"]);
    const netProfit = metric(stats, ["NetProfit", "Profit", "TotalProfit"]);
    const oos = hasOosEvidence(strategy, stats);

    return [
      {
        id: "evidence",
        label: "Evidence",
        state: stateFor(trades, THRESHOLDS.tradesPass, THRESHOLDS.tradesReview, { missing: "block" }),
        value: trades,
        target: `${THRESHOLDS.tradesPass}+ trades`,
        detail: `${fmt(trades, 0)} / ${THRESHOLDS.tradesPass}+`
      },
      {
        id: "profitability",
        label: "Profitability",
        state: stateFor(profitFactor, THRESHOLDS.profitFactorPass, THRESHOLDS.profitFactorReview),
        value: profitFactor,
        target: `PF ${THRESHOLDS.profitFactorPass}+`,
        detail: `${fmt(profitFactor, 2)} / ${THRESHOLDS.profitFactorPass.toFixed(2)}+`
      },
      {
        id: "risk",
        label: "Risk Efficiency",
        state: stateFor(returnDd, THRESHOLDS.returnDdPass, THRESHOLDS.returnDdReview),
        value: returnDd,
        target: `Ret/DD ${THRESHOLDS.returnDdPass}+`,
        detail: `${fmt(returnDd, 2)} / ${THRESHOLDS.returnDdPass.toFixed(2)}+`
      },
      {
        id: "expectancy",
        label: "Expectancy",
        state: Number.isFinite(expectancy) ? (expectancy > THRESHOLDS.expectancyPass ? "pass" : "block") : "review",
        value: expectancy,
        target: "RExpectancy > 0",
        detail: `${fmt(expectancy, 3)} / > 0`
      },
      {
        id: "netProfit",
        label: "Net Profit",
        state: Number.isFinite(netProfit) ? (netProfit > THRESHOLDS.netProfitPass ? "pass" : "block") : "review",
        value: netProfit,
        target: "NetProfit > 0",
        detail: `${fmt(netProfit, 2)} / > 0`
      },
      {
        id: "oos",
        label: "OOS Integrity",
        state: oos ? "pass" : "review",
        value: oos ? 1 : 0,
        target: "OOS evidence",
        detail: oos ? "detected" : "not detected"
      }
    ];
  }

  function reasonFor(check) {
    if (check.state === "pass") {
      return { severity: "pass", text: `${check.label}: ${check.detail}` };
    }
    if (check.state === "review") {
      return { severity: "review", text: `${check.label} review: ${check.detail}` };
    }
    return { severity: "block", text: `${check.label} blocked: ${check.detail}` };
  }

  function evaluateGate(strategy, stats) {
    if (!strategy) {
      return {
        verdict: "BLOCK",
        severity: "block",
        summary: "Select a strategy/backtest result before using SQX Edge Gate.",
        checks: [],
        reasons: [{ severity: "block", text: "strategy_required" }],
        nextAction: "Open a strategy result in the SQX Results tab."
      };
    }
    if (!stats) {
      return {
        verdict: "BLOCK",
        severity: "block",
        summary: "Statistics payload is missing.",
        checks: [],
        reasons: [{ severity: "block", text: "stats_required" }],
        nextAction: "Wait for STATS_RESPONSE or reload the Results tab."
      };
    }
    const checks = buildChecks(strategy, stats);
    const reasons = checks.map(reasonFor);
    const hasBlock = checks.some((item) => item.state === "block");
    const hasReview = checks.some((item) => item.state === "review");
    if (hasBlock) {
      return {
        verdict: "BLOCK",
        severity: "block",
        summary: "Hard SQX Edge gate failed.",
        checks,
        reasons,
        nextAction: "Do not promote. Repair the candidate, retest under the protected pipeline, or discard it."
      };
    }
    if (hasReview) {
      return {
        verdict: "REVIEW",
        severity: "review",
        summary: "Candidate needs operator review before promotion.",
        checks,
        reasons,
        nextAction: "Inspect weak axes, confirm OOS evidence, then continue only through the next governed validation gate."
      };
    }
    return {
      verdict: "PASS",
      severity: "pass",
      summary: "Candidate passes the institutional stats gate.",
      checks,
      reasons,
      nextAction: "Move to the next SQX Edge validation gate. Do not skip robustness, OOS or forward discipline."
    };
  }

  function radarAxes(strategy, stats) {
    const trades = metric(stats, ["NumberOfTrades", "Trades"]);
    const profitFactor = metric(stats, ["ProfitFactor", "PF"]);
    const returnDd = metric(stats, ["ReturnDDRatio", "RetDD", "ReturnToDrawdown"]);
    const expectancy = metric(stats, ["RExpectancy", "Expectancy", "AvgProfit"]);
    const hasOos = hasOosEvidence(strategy, stats);
    return [
      { label: "Evidence", score: scale(trades, 0, THRESHOLDS.tradesPass) },
      { label: "Profitability", score: scale(profitFactor, 0.8, THRESHOLDS.profitFactorPass) },
      { label: "Risk Efficiency", score: scale(returnDd, 0, THRESHOLDS.returnDdPass) },
      { label: "Expectancy", score: Number.isFinite(expectancy) ? scale(expectancy, -0.05, 0.12) : 40 },
      { label: "OOS Integrity", score: hasOos ? 100 : 55 }
    ];
  }

  function radarPoints(axes, cx, cy, radius) {
    const count = axes.length || 1;
    return axes.map((axis, index) => {
      const angle = -Math.PI / 2 + (index * 2 * Math.PI) / count;
      const r = radius * (Math.max(0, Math.min(100, axis.score)) / 100);
      return {
        x: Math.round((cx + Math.cos(angle) * r) * 100) / 100,
        y: Math.round((cy + Math.sin(angle) * r) * 100) / 100
      };
    });
  }

  function orderValue(order) {
    return metric(order, ["profit", "Profit", "pl", "PL", "netProfit", "NetProfit", "pnl", "Pnl"]);
  }

  function orderDate(order) {
    const raw = order && (order.closeTime || order.CloseTime || order.exitTime || order.ExitTime || order.time || order.Time || order.date || order.Date);
    const date = raw ? new Date(raw) : null;
    return date && !Number.isNaN(date.getTime()) ? date : null;
  }

  function normalizeOrders(payload) {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.orders)) return payload.orders;
    if (payload && Array.isArray(payload.data)) return payload.data;
    return [];
  }

  function analyzeOrders(payload) {
    const orders = normalizeOrders(payload);
    let maxLossStreak = 0;
    let maxWinStreak = 0;
    let currentLoss = 0;
    let currentWin = 0;
    let largestLoss = 0;
    let total = 0;
    let wins = 0;
    let losses = 0;
    const values = [];

    orders.forEach((order) => {
      const value = orderValue(order);
      if (!Number.isFinite(value)) return;
      values.push({ value, date: orderDate(order) });
      total += value;
      if (value < 0) {
        losses += 1;
        currentLoss += 1;
        currentWin = 0;
        largestLoss = Math.min(largestLoss, value);
      } else if (value > 0) {
        wins += 1;
        currentWin += 1;
        currentLoss = 0;
      } else {
        currentLoss = 0;
        currentWin = 0;
      }
      maxLossStreak = Math.max(maxLossStreak, currentLoss);
      maxWinStreak = Math.max(maxWinStreak, currentWin);
    });

    const thirds = values.length >= 9 ? Math.floor(values.length / 3) : 0;
    const firstNet = thirds ? values.slice(0, thirds).reduce((acc, item) => acc + item.value, 0) : NaN;
    const lastNet = thirds ? values.slice(-thirds).reduce((acc, item) => acc + item.value, 0) : NaN;
    const decay = Number.isFinite(firstNet) && firstNet > 0 ? (firstNet - lastNet) / Math.abs(firstNet) : NaN;
    const severity = maxLossStreak >= 8 || (Number.isFinite(decay) && decay > 1) ? "block" : (maxLossStreak >= 5 || (Number.isFinite(decay) && decay > 0.35) ? "review" : "pass");

    return {
      count: values.length,
      total,
      wins,
      losses,
      maxLossStreak,
      maxWinStreak,
      largestLoss,
      firstNet,
      lastNet,
      decay,
      severity
    };
  }

  const api = {
    VERSION,
    THRESHOLDS,
    LOCALES,
    metric,
    fmt,
    hasOosEvidence,
    buildChecks,
    evaluateGate,
    radarAxes,
    radarPoints,
    normalizeOrders,
    analyzeOrders
  };

  if (typeof window !== "undefined") {
    window.SQX_EDGE_GATE_VERSION = VERSION;
    window.SQX_EDGE_GATE_LOGIC = api;
  }
})();
