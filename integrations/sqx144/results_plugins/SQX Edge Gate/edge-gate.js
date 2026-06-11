(function () {
  "use strict";

  const VERSION = "sqx144-custom-results6-edge-gate-v2";
  const LEGACY_INSTALLED_VERSION = "sqx144-custom-results5-edge-gate-v1";

  const PIPELINE_CONTEXTS = {
    build: {
      id: "build",
      label: "Build",
      tradesPass: 120,
      tradesReview: 80,
      tradesBlockBelow: 60,
      profitFactorPass: 1.3,
      profitFactorReview: 1.05,
      returnDdPass: 4,
      returnDdReview: 1.5,
      missingOosState: "review"
    },
    retest0: {
      id: "retest0",
      label: "Retest 0",
      tradesPass: 100,
      tradesReview: 70,
      tradesBlockBelow: 50,
      profitFactorPass: 1.25,
      profitFactorReview: 1.05,
      returnDdPass: 3.5,
      returnDdReview: 1.5,
      missingOosState: "review"
    },
    retest1: {
      id: "retest1",
      label: "Retest 1",
      tradesPass: 100,
      tradesReview: 70,
      tradesBlockBelow: 50,
      profitFactorPass: 1.2,
      profitFactorReview: 1.03,
      returnDdPass: 3,
      returnDdReview: 1.3,
      missingOosState: "review"
    },
    tickReal: {
      id: "tickReal",
      label: "Tick Real",
      tradesPass: 80,
      tradesReview: 50,
      tradesBlockBelow: 30,
      profitFactorPass: 1.15,
      profitFactorReview: 1,
      returnDdPass: 2,
      returnDdReview: 1,
      retentionPass: 0.7,
      retentionReview: 0.4,
      missingRetentionState: "review",
      missingOosState: "review"
    },
    forward: {
      id: "forward",
      label: "Forward",
      tradesPass: 50,
      tradesReview: 30,
      tradesBlockBelow: 20,
      profitFactorPass: 1.15,
      profitFactorReview: 1,
      returnDdPass: 2,
      returnDdReview: 1,
      missingOosState: "pass",
      oosInferredByStage: true
    },
    portfolioCandidate: {
      id: "portfolioCandidate",
      label: "Portfolio Candidate",
      tradesPass: 150,
      tradesReview: 100,
      tradesBlockBelow: 70,
      profitFactorPass: 1.2,
      profitFactorReview: 1.05,
      returnDdPass: 4.5,
      returnDdReview: 2,
      missingOosState: "review"
    }
  };

  const GATE_SCORE_WEIGHTS = {
    evidence: 0.25,
    profitability: 0.2,
    risk: 0.25,
    expectancy: 0.15,
    oos: 0.15
  };

  const THRESHOLDS = {
    tradesPass: PIPELINE_CONTEXTS.build.tradesPass,
    tradesReview: PIPELINE_CONTEXTS.build.tradesReview,
    tradesBlockBelow: PIPELINE_CONTEXTS.build.tradesBlockBelow,
    profitFactorPass: PIPELINE_CONTEXTS.build.profitFactorPass,
    profitFactorReview: PIPELINE_CONTEXTS.build.profitFactorReview,
    returnDdPass: PIPELINE_CONTEXTS.build.returnDdPass,
    returnDdReview: PIPELINE_CONTEXTS.build.returnDdReview,
    expectancyPass: 0,
    netProfitPass: 0
  };

  const REPAIR_ACTIONS = {
    evidence: {
      review: "No promote; revisar universo/TF o ampliar evidencia antes de avanzar.",
      block: "No promote; revisar universo/TF o descartar."
    },
    profitability: {
      review: "No tocar filtro para rescatar; volver a robustez y confirmar costes.",
      block: "No tocar filtro para rescatar; volver a robustez o descartar."
    },
    risk: {
      review: "Riesgo poco eficiente; revisar DD clusters antes de promover.",
      block: "Riesgo no eficiente; revisar DD clusters o descartar."
    },
    expectancy: {
      review: "Confirmar expectancy con muestra protegida antes de avanzar.",
      block: "Expectancy no positiva; bloquear promocion."
    },
    netProfit: {
      review: "Confirmar NetProfit en muestra correcta antes de avanzar.",
      block: "NetProfit no positivo; bloquear promocion."
    },
    oos: {
      review: "Confirmar sampleType/OOS antes de decision.",
      block: "Sin integridad OOS suficiente; bloquear promocion."
    },
    orders: {
      review: "Revisar Order Radar; no promover sin resolver senales de degradacion.",
      block: "Order Radar degrada el candidato; devolver a revision metodologica."
    }
  };

  const LOCALES = {
    en: {
      title: "SQX Edge Gate",
      subtitle: "Trading Radar",
      verdict: "Verdict",
      context: "Context",
      pipeline: "Pipeline Context",
      gateScore: "Gate Score",
      radar: "Radar",
      reasons: "Reasons",
      nextAction: "Next action",
      decisionMatrix: "Decision Matrix",
      orderRadar: "Order Radar V2",
      activateOrders: "Activate Order Radar",
      copySummary: "Copy Summary",
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
      pipeline: "Pipeline Context",
      gateScore: "Gate Score",
      radar: "Radar",
      reasons: "Razones",
      nextAction: "Siguiente accion",
      decisionMatrix: "Matriz de decision",
      orderRadar: "Order Radar V2",
      activateOrders: "Activar Order Radar",
      copySummary: "Copy Summary",
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

  function clamp(value, low, high) {
    return Math.max(low, Math.min(high, value));
  }

  function scale(value, low, high) {
    if (!Number.isFinite(value)) return 35;
    if (high <= low) return 0;
    return Math.round(((clamp(value, low, high) - low) / (high - low)) * 100);
  }

  function normalizePipelineContext(value) {
    const raw = String(value || "").trim().toLowerCase().replace(/[\s_-]+/g, "");
    if (!raw) return "build";
    if (raw.includes("portfolio")) return "portfolioCandidate";
    if (raw.includes("forward") || raw.includes("walkforward")) return "forward";
    if (raw.includes("tick") || raw.includes("real")) return "tickReal";
    if (raw.includes("retest1") || raw.includes("retestone")) return "retest1";
    if (raw.includes("retest0") || raw.includes("retestzero")) return "retest0";
    if (raw.includes("build") || raw.includes("mining") || raw.includes("generate")) return "build";
    return Object.prototype.hasOwnProperty.call(PIPELINE_CONTEXTS, value) ? value : "build";
  }

  function pipelinePolicy(contextId) {
    return PIPELINE_CONTEXTS[normalizePipelineContext(contextId)] || PIPELINE_CONTEXTS.build;
  }

  function detectPipelineContext(strategy, stats) {
    const raw = [
      strategy && strategy.pipelineContext,
      strategy && strategy.pipelineStage,
      strategy && strategy.stage,
      strategy && strategy.databankName,
      strategy && strategy.resultGroup,
      strategy && strategy.projectName,
      stats && stats.pipelineContext,
      stats && stats.pipelineStage,
      stats && stats.stage,
      stats && stats.Databank,
      stats && stats.SampleType
    ].filter(Boolean).join(" ");
    return normalizePipelineContext(raw);
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

  function worstState(states) {
    if (states.includes("block")) return "block";
    if (states.includes("review")) return "review";
    return "pass";
  }

  function optionsWithDefaults(strategy, stats, options) {
    const opts = options || {};
    const detected = detectPipelineContext(strategy, stats);
    const context = normalizePipelineContext(opts.pipelineContext || detected);
    const previousTrades = Number(opts.previousTrades);
    return {
      pipelineContext: context,
      pipelineContextDetected: detected,
      pipelineContextSource: opts.pipelineContext ? "manual" : "auto",
      previousTrades: Number.isFinite(previousTrades) && previousTrades > 0 ? previousTrades : NaN,
      ordersAnalysis: opts.ordersAnalysis || null
    };
  }

  function buildChecks(strategy, stats, options) {
    const opts = optionsWithDefaults(strategy, stats, options);
    const policy = pipelinePolicy(opts.pipelineContext);
    const trades = metric(stats, ["NumberOfTrades", "Trades"]);
    const profitFactor = metric(stats, ["ProfitFactor", "PF"]);
    const returnDd = metric(stats, ["ReturnDDRatio", "RetDD", "ReturnToDrawdown"]);
    const expectancy = metric(stats, ["RExpectancy", "Expectancy", "AvgProfit"]);
    const netProfit = metric(stats, ["NetProfit", "Profit", "TotalProfit"]);
    const oos = hasOosEvidence(strategy, stats);
    const tradeState = stateFor(trades, policy.tradesPass, policy.tradesReview, { missing: "block" });
    let evidenceState = tradeState;
    let evidenceTarget = `${policy.tradesPass}+ trades`;
    let evidenceDetail = `${fmt(trades, 0)} / ${policy.tradesPass}+`;
    let retention = NaN;

    if (policy.id === "tickReal") {
      retention = Number.isFinite(opts.previousTrades) && Number.isFinite(trades) ? trades / opts.previousTrades : NaN;
      const retentionState = Number.isFinite(retention)
        ? stateFor(retention, policy.retentionPass, policy.retentionReview)
        : policy.missingRetentionState;
      evidenceState = worstState([tradeState, retentionState]);
      evidenceTarget = `${policy.tradesPass}+ trades and ${(policy.retentionPass * 100).toFixed(0)}% retention`;
      evidenceDetail = `${fmt(trades, 0)} trades; retention ${Number.isFinite(retention) ? fmt(retention * 100, 0) + "%" : "not available"}`;
    }

    const oosState = oos ? "pass" : policy.missingOosState;
    const oosDetail = oos ? "reported" : (policy.oosInferredByStage ? "inferred by Forward stage" : "missing");

    return [
      {
        id: "evidence",
        label: "Evidence",
        state: evidenceState,
        value: trades,
        retention,
        target: evidenceTarget,
        detail: evidenceDetail,
        score: evidenceScore(trades, policy, retention)
      },
      {
        id: "profitability",
        label: "Profitability",
        state: stateFor(profitFactor, policy.profitFactorPass, policy.profitFactorReview),
        value: profitFactor,
        target: `PF ${policy.profitFactorPass}+`,
        detail: `${fmt(profitFactor, 2)} / ${policy.profitFactorPass.toFixed(2)}+`,
        score: scale(profitFactor, Math.max(0, policy.profitFactorReview - 0.25), policy.profitFactorPass)
      },
      {
        id: "risk",
        label: "Risk Efficiency",
        state: stateFor(returnDd, policy.returnDdPass, policy.returnDdReview),
        value: returnDd,
        target: `Ret/DD ${policy.returnDdPass}+`,
        detail: `${fmt(returnDd, 2)} / ${policy.returnDdPass.toFixed(2)}+`,
        score: scale(returnDd, 0, policy.returnDdPass)
      },
      {
        id: "expectancy",
        label: "Expectancy",
        state: Number.isFinite(expectancy) ? (expectancy > THRESHOLDS.expectancyPass ? "pass" : "block") : "review",
        value: expectancy,
        target: "RExpectancy > 0",
        detail: `${fmt(expectancy, 3)} / > 0`,
        score: Number.isFinite(expectancy) ? scale(expectancy, -0.05, 0.12) : 40
      },
      {
        id: "netProfit",
        label: "Net Profit",
        state: Number.isFinite(netProfit) ? (netProfit > THRESHOLDS.netProfitPass ? "pass" : "block") : "review",
        value: netProfit,
        target: "NetProfit > 0",
        detail: `${fmt(netProfit, 2)} / > 0`,
        score: Number.isFinite(netProfit) && netProfit > 0 ? 100 : 0
      },
      {
        id: "oos",
        label: "OOS Integrity",
        state: oosState,
        value: oos ? 1 : 0,
        target: policy.oosInferredByStage ? "Forward holdout context" : "OOS evidence",
        detail: oosDetail,
        inferredByStage: Boolean(!oos && policy.oosInferredByStage),
        score: oos ? 100 : (policy.oosInferredByStage ? 80 : 55)
      }
    ];
  }

  function evidenceScore(trades, policy, retention) {
    const tradeScore = scale(trades, 0, policy.tradesPass);
    if (policy.id !== "tickReal") return tradeScore;
    const retentionScore = Number.isFinite(retention) ? scale(retention, 0, policy.retentionPass) : 45;
    return Math.round((tradeScore * 0.55) + (retentionScore * 0.45));
  }

  function reasonFor(check) {
    const repair = (REPAIR_ACTIONS[check.id] && REPAIR_ACTIONS[check.id][check.state]) || "";
    const prefix = check.state === "pass" ? `${check.label}:` : `${check.label} ${check.state}:`;
    return {
      severity: check.state,
      id: check.id,
      text: `${prefix} ${check.detail}`,
      repairAction: repair
    };
  }

  function gateScoreFromChecks(checks) {
    const byId = {};
    checks.forEach((check) => { byId[check.id] = check; });
    const score = (
      ((byId.evidence && byId.evidence.score) || 0) * GATE_SCORE_WEIGHTS.evidence +
      ((byId.profitability && byId.profitability.score) || 0) * GATE_SCORE_WEIGHTS.profitability +
      ((byId.risk && byId.risk.score) || 0) * GATE_SCORE_WEIGHTS.risk +
      ((byId.expectancy && byId.expectancy.score) || 0) * GATE_SCORE_WEIGHTS.expectancy +
      ((byId.oos && byId.oos.score) || 0) * GATE_SCORE_WEIGHTS.oos
    );
    return Math.round(score);
  }

  function applyOrderRadarToDecision(decision, ordersAnalysis) {
    if (!ordersAnalysis || !ordersAnalysis.count || ordersAnalysis.severity === "pass") return decision;
    const orderReason = {
      severity: ordersAnalysis.severity,
      id: "orders",
      text: `Order Radar ${ordersAnalysis.severity}: ${ordersAnalysis.summary}`,
      repairAction: REPAIR_ACTIONS.orders[ordersAnalysis.severity] || REPAIR_ACTIONS.orders.review
    };
    const next = {
      ...decision,
      reasons: [...decision.reasons, orderReason],
      orderRadarApplied: true
    };
    if (decision.verdict === "PASS") {
      next.verdict = "REVIEW";
      next.severity = "review";
      next.summary = "Stats pass, but Order Radar requires operator review.";
      next.nextAction = "Do not promote yet. Resolve Order Radar degradation before continuing.";
    }
    return next;
  }

  function evaluateGate(strategy, stats, options) {
    const opts = optionsWithDefaults(strategy, stats, options);
    if (!strategy) {
      return {
        verdict: "BLOCK",
        severity: "block",
        score: 0,
        pipelineContext: opts.pipelineContext,
        pipelineLabel: pipelinePolicy(opts.pipelineContext).label,
        summary: "Select a strategy/backtest result before using SQX Edge Gate.",
        checks: [],
        reasons: [{ severity: "block", id: "strategy", text: "strategy_required", repairAction: "Open a strategy result in the SQX Results tab." }],
        nextAction: "Open a strategy result in the SQX Results tab."
      };
    }
    if (!stats) {
      return {
        verdict: "BLOCK",
        severity: "block",
        score: 0,
        pipelineContext: opts.pipelineContext,
        pipelineLabel: pipelinePolicy(opts.pipelineContext).label,
        summary: "Statistics payload is missing.",
        checks: [],
        reasons: [{ severity: "block", id: "stats", text: "stats_required", repairAction: "Wait for STATS_RESPONSE or reload the Results tab." }],
        nextAction: "Wait for STATS_RESPONSE or reload the Results tab."
      };
    }
    const checks = buildChecks(strategy, stats, opts);
    const reasons = checks.map(reasonFor);
    const hasBlock = checks.some((item) => item.state === "block");
    const hasReview = checks.some((item) => item.state === "review");
    const base = {
      pipelineContext: opts.pipelineContext,
      pipelineLabel: pipelinePolicy(opts.pipelineContext).label,
      pipelineContextDetected: opts.pipelineContextDetected,
      pipelineContextSource: opts.pipelineContextSource,
      score: gateScoreFromChecks(checks),
      checks,
      reasons,
      contractStatus: contractStatus(strategy, stats, opts)
    };
    if (hasBlock) {
      return applyOrderRadarToDecision({
        ...base,
        verdict: "BLOCK",
        severity: "block",
        summary: "Hard SQX Edge gate failed.",
        nextAction: "Do not promote. Repair the candidate, retest under the protected pipeline, or discard it."
      }, opts.ordersAnalysis);
    }
    if (hasReview) {
      return applyOrderRadarToDecision({
        ...base,
        verdict: "REVIEW",
        severity: "review",
        summary: "Candidate needs operator review before promotion.",
        nextAction: "Inspect weak axes, confirm stage/OOS evidence, then continue only through the next governed validation gate."
      }, opts.ordersAnalysis);
    }
    return applyOrderRadarToDecision({
      ...base,
      verdict: "PASS",
      severity: "pass",
      summary: "Candidate passes the institutional stage-aware stats gate.",
      nextAction: "Move to the next SQX Edge validation gate. Do not skip robustness, OOS or forward discipline."
    }, opts.ordersAnalysis);
  }

  function radarAxes(strategy, stats, options) {
    const checks = buildChecks(strategy, stats || {}, options);
    const byId = {};
    checks.forEach((check) => { byId[check.id] = check; });
    return [
      { id: "evidence", label: "Evidence", score: (byId.evidence && byId.evidence.score) || 0 },
      { id: "profitability", label: "Profitability", score: (byId.profitability && byId.profitability.score) || 0 },
      { id: "risk", label: "Risk Efficiency", score: (byId.risk && byId.risk.score) || 0 },
      { id: "expectancy", label: "Expectancy", score: (byId.expectancy && byId.expectancy.score) || 0 },
      { id: "oos", label: "OOS Integrity", score: (byId.oos && byId.oos.score) || 0 }
    ];
  }

  function radarPoints(axes, cx, cy, radius) {
    const count = axes.length || 1;
    return axes.map((axis, index) => {
      const angle = -Math.PI / 2 + (index * 2 * Math.PI) / count;
      const r = radius * (clamp(axis.score, 0, 100) / 100);
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

  function sumValues(items) {
    return items.reduce((acc, item) => acc + item.value, 0);
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
    let grossProfit = 0;
    let grossLoss = 0;
    const values = [];

    orders.forEach((order, index) => {
      const value = orderValue(order);
      if (!Number.isFinite(value)) return;
      const date = orderDate(order);
      values.push({ value, date, index });
      total += value;
      if (value < 0) {
        losses += 1;
        grossLoss += Math.abs(value);
        currentLoss += 1;
        currentWin = 0;
        largestLoss = Math.min(largestLoss, value);
      } else if (value > 0) {
        wins += 1;
        grossProfit += value;
        currentWin += 1;
        currentLoss = 0;
      } else {
        currentLoss = 0;
        currentWin = 0;
      }
      maxLossStreak = Math.max(maxLossStreak, currentLoss);
      maxWinStreak = Math.max(maxWinStreak, currentWin);
    });

    const incompleteTimestampCount = values.filter((item) => !item.date).length;
    const ordered = incompleteTimestampCount ? values : values.slice().sort((a, b) => a.date - b.date);
    const thirdsSize = ordered.length >= 9 ? Math.floor(ordered.length / 3) : 0;
    const firstNet = thirdsSize ? sumValues(ordered.slice(0, thirdsSize)) : NaN;
    const middleNet = thirdsSize ? sumValues(ordered.slice(thirdsSize, thirdsSize * 2)) : NaN;
    const lastNet = thirdsSize ? sumValues(ordered.slice(-thirdsSize)) : NaN;
    const decay = Number.isFinite(firstNet) && firstNet > 0 ? (firstNet - lastNet) / Math.abs(firstNet) : NaN;
    const lossValues = values.filter((item) => item.value < 0).map((item) => item.value);
    const averageLoss = lossValues.length ? lossValues.reduce((acc, value) => acc + value, 0) / lossValues.length : NaN;
    const worstToAverageLossRatio = Number.isFinite(averageLoss) && averageLoss !== 0 ? Math.abs(largestLoss / averageLoss) : NaN;
    const topFiveProfit = values
      .filter((item) => item.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, 5)
      .reduce((acc, item) => acc + item.value, 0);
    const topFiveContribution = grossProfit > 0 ? topFiveProfit / grossProfit : NaN;
    const lateDegradation = Number.isFinite(firstNet) && Number.isFinite(lastNet) && firstNet > 0 && lastNet < 0;
    const warnings = [];
    if (values.length < 30) warnings.push("few_orders");
    if (incompleteTimestampCount > 0) warnings.push("timestamps_incomplete");
    if (maxLossStreak >= 5) warnings.push("loss_streak");
    if (Number.isFinite(topFiveContribution) && topFiveContribution > 0.5) warnings.push("pnl_concentration_top5");
    if (lateDegradation) warnings.push("late_degradation");
    if (Number.isFinite(decay) && decay > 0.35) warnings.push("profit_decay_by_thirds");
    if (Number.isFinite(worstToAverageLossRatio) && worstToAverageLossRatio > 3) warnings.push("worst_loss_outlier");

    const severity = (
      maxLossStreak >= 8 ||
      lateDegradation ||
      (Number.isFinite(topFiveContribution) && topFiveContribution >= 0.7) ||
      (Number.isFinite(decay) && decay > 1)
    ) ? "block" : (warnings.length ? "review" : "pass");

    const summary = warnings.length ? warnings.join(", ") : "orders_clean";

    return {
      count: values.length,
      total,
      wins,
      losses,
      grossProfit,
      grossLoss,
      maxLossStreak,
      maxWinStreak,
      largestLoss,
      averageLoss,
      worstToAverageLossRatio,
      firstNet,
      middleNet,
      lastNet,
      decay,
      topFiveContribution,
      lateDegradation,
      incompleteTimestampCount,
      warnings,
      summary,
      severity
    };
  }

  function contractStatus(strategy, stats, options) {
    const opts = optionsWithDefaults(strategy, stats, options);
    const policy = pipelinePolicy(opts.pipelineContext);
    const oos = hasOosEvidence(strategy, stats);
    return [
      { label: "No promote state", state: "pass", detail: "diagnostic only" },
      { label: "No source code", state: "pass", detail: "blocked" },
      { label: "No databank mutation", state: "pass", detail: "blocked" },
      { label: "Orders opt-in", state: "pass", detail: "manual button only" },
      { label: "OOS", state: oos ? "pass" : policy.missingOosState, detail: oos ? "reported" : (policy.oosInferredByStage ? "inferred" : "missing") }
    ];
  }

  function buildSummary(decision, strategy, stats, options) {
    const opts = optionsWithDefaults(strategy, stats, options);
    const policy = pipelinePolicy(opts.pipelineContext);
    const lines = [
      `SQX Edge Gate ${VERSION}`,
      `Verdict: ${decision.verdict}`,
      `Gate Score: ${decision.score}/100`,
      `Pipeline Context: ${policy.label}`,
      `Strategy: ${(strategy && strategy.name) || "-"}`,
      `Trades: ${fmt(metric(stats, ["NumberOfTrades", "Trades"]), 0)}`,
      `ProfitFactor: ${fmt(metric(stats, ["ProfitFactor", "PF"]), 2)}`,
      `ReturnDDRatio: ${fmt(metric(stats, ["ReturnDDRatio", "RetDD", "ReturnToDrawdown"]), 2)}`,
      `RExpectancy: ${fmt(metric(stats, ["RExpectancy", "Expectancy", "AvgProfit"]), 3)}`,
      `NetProfit: ${fmt(metric(stats, ["NetProfit", "Profit", "TotalProfit"]), 2)}`,
      "Reasons:"
    ];
    (decision.reasons || []).forEach((reason) => {
      lines.push(`- ${reason.text}${reason.repairAction ? " | Action: " + reason.repairAction : ""}`);
    });
    lines.push(`Next Action: ${decision.nextAction || "-"}`);
    return lines.join("\n");
  }

  const api = {
    VERSION,
    LEGACY_INSTALLED_VERSION,
    THRESHOLDS,
    PIPELINE_CONTEXTS,
    GATE_SCORE_WEIGHTS,
    REPAIR_ACTIONS,
    LOCALES,
    metric,
    fmt,
    scale,
    normalizePipelineContext,
    pipelinePolicy,
    detectPipelineContext,
    hasOosEvidence,
    buildChecks,
    evaluateGate,
    gateScoreFromChecks,
    radarAxes,
    radarPoints,
    normalizeOrders,
    analyzeOrders,
    contractStatus,
    buildSummary
  };

  if (typeof window !== "undefined") {
    window.SQX_EDGE_GATE_VERSION = VERSION;
    window.SQX_EDGE_GATE_LOGIC = api;
  }
})();
