(function () {
  "use strict";

  function strategy(overrides) {
    return Object.assign({
      id: "sqx-edge-gate-fixture",
      name: "SQX Edge Gate Fixture",
      projectName: "SQX Edge Lab",
      databankName: "Results",
      symbol: "AUDCAD_darwinex",
      timeframe: "H1",
      sampleType: "OOS",
      resultKey: "Portfolio"
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

  function order(value, index) {
    return {
      id: `fixture-order-${index}`,
      closeTime: `2024-03-${String((index % 25) + 1).padStart(2, "0")}T12:00:00Z`,
      profit: value
    };
  }

  const passOrders = [240, -90, 180, 220, -70, 160, -40, 210, 190, -80, 130, 170].map(order);
  const largeOrders = Array.from({ length: 180 }, (_, index) => {
    const cycle = index % 13;
    const value = cycle < 8 ? 72 + cycle * 4 : -44 - cycle * 3;
    return order(value, index);
  });

  window.SQX_EDGE_GATE_FIXTURES = {
    pass: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Institutional PASS candidate" }) },
        { type: "STATS_RESPONSE", data: stats() }
      ]
    },
    review: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Review candidate" }) },
        { type: "STATS_RESPONSE", data: stats({ NumberOfTrades: 96, ProfitFactor: 1.22, ReturnDDRatio: 2.4, RExpectancy: 0.022 }) }
      ]
    },
    block: {
      messages: [
        { type: "STRATEGY_DATA", data: strategy({ name: "Blocked candidate" }) },
        { type: "STATS_RESPONSE", data: stats({ NetProfit: -840, NumberOfTrades: 42, ProfitFactor: 0.94, ReturnDDRatio: 0.7, RExpectancy: -0.031 }) }
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
        { type: "STRATEGY_DATA", data: strategy({ name: "Missing OOS marker", sampleType: "main" }) },
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
})();
