(function () {
  "use strict";

  function strategy(overrides) {
    return Object.assign({
      id: "fixture-strategy",
      name: "Fixture Strategy",
      projectName: "Fixture Project",
      databankName: "Results",
      symbol: "AUDCAD_darwinex",
      timeframe: "H1",
      sampleType: "OOS"
    }, overrides || {});
  }

  function stats(overrides) {
    return Object.assign({
      NetProfit: 3450.25,
      NumberOfTrades: 132,
      ProfitFactor: 1.28,
      RExpectancy: 0.12,
      ReturnDDRatio: 4.2,
      Drawdown: 820.1
    }, overrides || {});
  }

  window.SQX_EDGE_CUSTOM_RESULTS_FIXTURES = {
    ready: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy() },
        { type: "STATS_RESPONSE", payload: stats() }
      ]
    },
    review: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Review Candidate" }) },
        { type: "STATS_RESPONSE", payload: stats({ NumberOfTrades: 54, ProfitFactor: 1.04, ReturnDDRatio: 1.2 }) }
      ]
    },
    blocked: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Blocked Candidate" }) },
        { type: "STATS_RESPONSE", payload: stats({ NumberOfTrades: 18, ProfitFactor: 0.92, RExpectancy: -0.04, ReturnDDRatio: 0.5 }) }
      ]
    },
    noStrategy: {
      messages: []
    },
    missingStats: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Missing Stats" }) }
      ]
    },
    largePortfolio: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Portfolio", databankName: "Portfolio", symbol: "MULTI", timeframe: "MIXED" }) },
        { type: "STATS_RESPONSE", payload: stats({ NetProfit: 84225.78, NumberOfTrades: 3480, ProfitFactor: 1.12, RExpectancy: 0.071, ReturnDDRatio: 2.35, Drawdown: 35880.4 }) }
      ]
    }
  };
})();
