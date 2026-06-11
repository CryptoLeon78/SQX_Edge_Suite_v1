(function () {
  "use strict";

  function strategy(overrides) {
    return Object.assign({
      id: "sqx-edge-gate-fixture",
      name: "SQX Edge Gate Fixture",
      projectName: "SQX Edge Lab Build",
      databankName: "Results",
      symbol: "AUDCAD_darwinex",
      timeframe: "H1",
      sampleType: "OOS",
      resultKey: "Portfolio",
      pipelineContext: "Build"
    }, overrides || {});
  }

  function stats(overrides) {
    return Object.assign({
      NetProfit: 12450.25,
      NumberOfTrades: 142,
      ProfitFactor: 1.42,
      RExpectancy: 0.086,
      ReturnDDRatio: 4.8,
      Drawdown: 2580.1,
      SampleType: "OOS"
    }, overrides || {});
  }

  function order(value, index, overrides) {
    return Object.assign({
      id: `fixture-order-${index}`,
      closeTime: `2024-03-${String((index % 25) + 1).padStart(2, "0")}T12:00:00Z`,
      profit: value
    }, overrides || {});
  }

  const passOrders = [240, -90, 180, 220, -70, 160, -40, 210, 190, -80, 130, 170].map(order);
  const largeOrders = Array.from({ length: 180 }, (_, index) => {
    const cycle = index % 13;
    const value = cycle < 8 ? 72 + cycle * 4 : -44 - cycle * 3;
    return order(value, index);
  });
  const lateDegradationOrders = [
    240, 210, 180, -60, 190, 170, 150, 130, 110,
    70, -40, 60, -55, 40, -70, 35, -60, 30,
    -120, -130, -110, -95, -140, 40, -125, -115, -150
  ].map(order);
  const concentrationOrders = [
    1200, 980, 870, 760, 690, -80, -70, -90, -60, 55, -75, 45, -65, 35, -50, 30, -45, 25, -40, 20
  ].map(order);
  const missingTimestampOrders = [120, -55, 90, -40, 80, -45, 70, -30, 60, -25].map((value, index) => (
    order(value, index, { closeTime: index % 2 === 0 ? "" : undefined })
  ));

  const fixtures = {
    buildPass: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Institutional BUILD PASS candidate", pipelineContext: "Build" }) },
        { type: "STATS_RESPONSE", data: stats() }
      ]
    },
    retestReview: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Retest 0 review candidate", databankName: "RETEST 0", pipelineContext: "Retest 0" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 76, ProfitFactor: 1.18, ReturnDDRatio: 2.3, RExpectancy: 0.022 }) }
      ]
    },
    tickRealRetentionBlock: {
      previousTrades: 140,
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Tick Real retention fail", databankName: "TICK", pipelineContext: "Tick Real" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 48, ProfitFactor: 1.19, ReturnDDRatio: 2.4, RExpectancy: 0.018 }) }
      ]
    },
    forwardMissingOos: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Forward holdout missing internal OOS", databankName: "Forward", sampleType: "main", pipelineContext: "Forward" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 68, ProfitFactor: 1.22, ReturnDDRatio: 2.6, RExpectancy: 0.027, SampleType: "main" }) }
      ]
    },
    portfolioCandidate: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Portfolio candidate", databankName: "Portfolio Candidate", symbol: "MULTI", timeframe: "MIXED", pipelineContext: "Portfolio Candidate" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 168, ProfitFactor: 1.24, ReturnDDRatio: 4.9, RExpectancy: 0.041 }) }
      ]
    },
    ordersLateDegradation: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Orders late degradation", pipelineContext: "Build" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: lateDegradationOrders } }
      ]
    },
    ordersConcentration: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Orders concentration", pipelineContext: "Build" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: concentrationOrders } }
      ]
    },
    missingTimestamps: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Missing timestamps", pipelineContext: "Build" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 122 }) },
        { type: "ORDERS_RESPONSE", data: { orders: missingTimestampOrders } }
      ]
    },
    noStrategy: {
      messages: []
    },
    missingStats: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Missing stats candidate" }) }
      ]
    },
    missingOOS: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Missing OOS marker", sampleType: "main", pipelineContext: "Build" }) },
        { type: "STATS_RESPONSE", data: stats({ SampleType: "main" }) }
      ]
    },
    ordersOptIn: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Orders opt-in fixture" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: passOrders } }
      ]
    },
    largeOrders: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Large order sample", symbol: "MULTI", timeframe: "MIXED" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 380, ProfitFactor: 1.34, ReturnDDRatio: 4.3 }) },
        { type: "ORDERS_RESPONSE", data: { orders: largeOrders } }
      ]
    }
  };

  fixtures.pass = fixtures.buildPass;
  fixtures.review = fixtures.retestReview;
  fixtures.block = {
    messages: [
      { type: "STRATEGY_DATA", data: strategy({ name: "Blocked candidate" }) },
      { type: "STATS_RESPONSE", data: stats({ NetProfit: -840, NumberOfTrades: 42, ProfitFactor: 0.94, ReturnDDRatio: 0.7, RExpectancy: -0.031 }) }
    ]
  };

  window.SQX_EDGE_GATE_FIXTURES = fixtures;
})();
