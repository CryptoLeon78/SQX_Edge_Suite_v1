(function () {
  "use strict";

  function strategy(overrides) {
    return Object.assign({
      id: "regime-edge-fixture",
      name: "Regime Edge Fixture AUDCAD H1 L",
      strategyName: "Regime Edge Fixture AUDCAD H1 L",
      projectName: "SQX Edge Lab",
      databankName: "Results",
      symbol: "AUDCAD_darwinex",
      timeframe: "H1",
      sampleType: "OOS",
      resultKey: "Portfolio",
      direction: "long"
    }, overrides || {});
  }

  function stats(overrides) {
    return Object.assign({
      NetProfit: 6200,
      NumberOfTrades: 142,
      ProfitFactor: 1.36,
      ReturnDDRatio: 4.1,
      RExpectancy: 0.052,
      SampleType: "OOS"
    }, overrides || {});
  }

  function order(year, month, day, profit, side, index) {
    return {
      id: `regime-order-${year}-${index}`,
      closeTime: `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}T12:00:00Z`,
      profit,
      side: side || "long"
    };
  }

  function ordersForYear(year, values, side) {
    const expanded = [];
    for (let repeat = 0; repeat < 5; repeat += 1) {
      values.forEach((value) => expanded.push(value));
    }
    return expanded.map((value, index) => order(year, (index % 12) + 1, (index % 24) + 1, value, side, index));
  }

  function marketYear(year, first, last, label) {
    const bars = [];
    for (let month = 1; month <= 12; month += 1) {
      for (let slot = 1; slot <= 12; slot += 1) {
        const progress = ((month - 1) * 12 + (slot - 1)) / 143;
        const wave = Math.sin(progress * Math.PI * 4) * Math.abs(last - first) * 0.04;
        bars.push({
          time: `${year}-${String(month).padStart(2, "0")}-${String(Math.min(slot * 2, 28)).padStart(2, "0")}T00:00:00Z`,
          close: first + (last - first) * progress + wave,
          regime: label || ""
        });
      }
    }
    return bars;
  }

  const bullMarket = marketYear(2021, 1.0, 1.18, "BULL");
  const bearMarket = marketYear(2022, 1.18, 0.98, "BEAR");
  const sidewaysMarket = marketYear(2023, 0.99, 1.01, "SIDEWAYS");
  const mixedMarket = marketYear(2024, 1.0, 1.06, "MIXED");
  const standardMarket = bullMarket.concat(bearMarket, sidewaysMarket, mixedMarket);

  const longBullStrongOrders = []
    .concat(ordersForYear(2021, [150, 130, -45, 120, 110, -35, 95, 140, -50, 125, 100, -40], "long"))
    .concat(ordersForYear(2022, [45, -35, 40, -55, 35, -30, 55, -45, 25, -25], "long"))
    .concat(ordersForYear(2023, [60, -20, 55, -25, 50, -15, 45, -20], "long"));

  const longBullMismatchOrders = []
    .concat(ordersForYear(2021, [-120, 45, -110, -90, 35, -75, -60, 30, -95, -80], "long"))
    .concat(ordersForYear(2022, [150, -35, 130, 90, -45, 110, 75, -30], "long"))
    .concat(ordersForYear(2023, [40, -35, 30, -25, 25, -30], "long"));

  const longBearSurvivalOrders = []
    .concat(ordersForYear(2021, [120, 115, -35, 100, -40, 90, 85, -30], "long"))
    .concat(ordersForYear(2022, [15, -20, 25, -15, 20, -18, 10, -12], "long"))
    .concat(ordersForYear(2023, [50, -25, 45, -20, 35, -15], "long"));

  const shortBearStrongOrders = []
    .concat(ordersForYear(2021, [20, -35, 15, -40, 10, -30], "short"))
    .concat(ordersForYear(2022, [140, 120, -45, 130, 110, -35, 90, 150, -50, 100], "short"))
    .concat(ordersForYear(2023, [35, -20, 30, -15, 25, -20], "short"));

  const shortBearMismatchOrders = []
    .concat(ordersForYear(2021, [100, -40, 90, 70, -35, 80], "short"))
    .concat(ordersForYear(2022, [-130, 45, -110, -90, 30, -80, -70, 35], "short"));

  const sidewaysMeanRevertOrders = []
    .concat(ordersForYear(2021, [25, -30, 20, -35, 30, -25], "long"))
    .concat(ordersForYear(2023, [95, 90, -30, 80, -25, 70, 85, -20, 65, -25], "long"));

  const missingTimestampOrders = [
    { profit: 120, side: "long" },
    { profit: -45, side: "long" },
    { profit: 90, side: "long" },
    { profit: -35, side: "long" }
  ];

  const largeOrders = Array.from({ length: 180 }, (_, index) => {
    const year = 2021 + (index % 4);
    const value = index % 7 < 4 ? 70 + (index % 11) : -35 - (index % 13);
    return order(year, (index % 12) + 1, (index % 25) + 1, value, index % 2 ? "long" : "short", index);
  });

  const fixtures = {
    longBullStrong: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 L bull aligned", direction: "long" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: longBullStrongOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    longBullMismatch: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 L bull mismatch", direction: "long" }) },
        { type: "STATS_RESPONSE", data: stats({ ProfitFactor: 1.05, ReturnDDRatio: 1.8 }) },
        { type: "ORDERS_RESPONSE", data: { orders: longBullMismatchOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    longBearSurvival: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 L adverse survival", direction: "long" }) },
        { type: "STATS_RESPONSE", data: stats({ ProfitFactor: 1.27, ReturnDDRatio: 3.2 }) },
        { type: "ORDERS_RESPONSE", data: { orders: longBearSurvivalOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    shortBearStrong: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 S bear aligned", direction: "short" }) },
        { type: "STATS_RESPONSE", data: stats({ NetProfit: 5400, ProfitFactor: 1.31 }) },
        { type: "ORDERS_RESPONSE", data: { orders: shortBearStrongOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    shortBearMismatch: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 S bear mismatch", direction: "short" }) },
        { type: "STATS_RESPONSE", data: stats({ NetProfit: 600, ProfitFactor: 1.02 }) },
        { type: "ORDERS_RESPONSE", data: { orders: shortBearMismatchOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    sidewaysMeanRevert: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 mean reversion range", direction: "mean_reversion" }) },
        { type: "STATS_RESPONSE", data: stats({ ProfitFactor: 1.24 }) },
        { type: "ORDERS_RESPONSE", data: { orders: sidewaysMeanRevertOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    mixedUnknown: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "AUDCAD H1 mixed unknown" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: longBullStrongOrders.slice(0, 8) } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: marketYear(2024, 1.0, 1.05, "MIXED"), source: "embedded snapshot" } }
      ]
    },
    missingSeries: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Missing market series" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: longBullStrongOrders } }
      ]
    },
    missingTimestamps: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Missing timestamps" }) },
        { type: "STATS_RESPONSE", data: stats() },
        { type: "ORDERS_RESPONSE", data: { orders: missingTimestampOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    fewTrades: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Few trades" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 18 }) },
        { type: "ORDERS_RESPONSE", data: { orders: longBullStrongOrders.slice(0, 6) } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    largeOrders: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Large long short sample", direction: "long_short" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 180, ProfitFactor: 1.29 }) },
        { type: "ORDERS_RESPONSE", data: { orders: largeOrders } },
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    },
    noStrategy: {
      messages: [
        { type: "MARKET_SERIES_RESPONSE", data: { series: standardMarket, source: "embedded snapshot" } }
      ]
    }
  };

  window.SQX_REGIME_EDGE_FIXTURES = fixtures;
})();
