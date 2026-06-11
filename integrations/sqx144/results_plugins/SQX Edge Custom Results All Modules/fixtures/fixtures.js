(function () {
  "use strict";

  function strategy(overrides) {
    return Object.assign({
      id: "all-modules-fixture",
      name: "All Modules Fixture",
      projectName: "Fixture Project",
      databankName: "Results",
      symbol: "AUDCAD_darwinex",
      timeframe: "H1",
      sampleType: "Main+OOS"
    }, overrides || {});
  }

  function stats(overrides) {
    return Object.assign({
      NetProfit: 5250,
      OOSNetProfit: 1650,
      NumberOfTrades: 186,
      ProfitFactor: 1.34,
      OOSProfitFactor: 1.18,
      RExpectancy: 0.14,
      OOSRExpectancy: 0.08,
      ReturnDDRatio: 4.4,
      OOSReturnDDRatio: 2.6,
      Drawdown: 1190,
      Stability: 0.72,
      SQN: 2.1,
      WinningPct: 54.2,
      accountSize: 100000,
      propProfitTargetPct: 10,
      propMaxDailyLossPct: 5,
      propMaxLossPct: 10,
      randomBaselineWinRate: 50
    }, overrides || {});
  }

  function orders(profile) {
    var values = {
      steady: [120, -55, 95, 80, -40, 135, -75, 110, 65, -45, 140, 90, -85, 115, 70, 105],
      decay: [180, 135, 120, 90, -45, 85, 60, 40, -95, -120, 35, -160, 25, -190, 30, -210],
      prop: [720, 880, -420, 940, -380, 760, 520, -650, 980, 1120, -540, 850, 690, 770, -480, 920],
      weak: [45, -80, 30, -110, 25, -95, 50, -120, 35, -75, 20, -130, 40, -90, 15, -100]
    }[profile || "steady"];
    return values.map(function (profit, index) {
      var day = 1 + Math.floor(index / 2);
      return {
        id: "fixture-order-" + index,
        openTime: "2026-01-" + String(day).padStart(2, "0") + "T08:00:00Z",
        closeTime: "2026-01-" + String(day).padStart(2, "0") + "T16:00:00Z",
        profit: profit,
        mae: profit < 0 ? Math.abs(profit) * 1.2 : Math.abs(profit) * 0.45,
        mfe: profit > 0 ? profit * 1.4 : Math.abs(profit) * 0.35
      };
    });
  }

  window.SQX_EDGE_CUSTOM_RESULTS_ALL_MODULES_FIXTURES = {
    allReady: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy() },
        { type: "STATS_RESPONSE", payload: stats() },
        { type: "ORDERS_RESPONSE", payload: { orders: orders("steady") } }
      ]
    },
    edgeDecay: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Edge Decay" }) },
        { type: "STATS_RESPONSE", payload: stats({ ProfitFactor: 1.19, OOSProfitFactor: 0.96, ReturnDDRatio: 1.8 }) },
        { type: "ORDERS_RESPONSE", payload: { orders: orders("decay") } }
      ]
    },
    winRateResearch: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture WinRate Research" }) },
        { type: "STATS_RESPONSE", payload: stats({ WinningPct: 58.4, randomBaselineWinRate: 50, NumberOfTrades: 240 }) },
        { type: "ORDERS_RESPONSE", payload: { orders: orders("steady").concat(orders("steady")) } }
      ]
    },
    propFirm: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Prop Challenge" }) },
        { type: "STATS_RESPONSE", payload: stats({ NetProfit: 10580, ProfitFactor: 1.46, propProfitTargetPct: 10 }) },
        { type: "ORDERS_RESPONSE", payload: { orders: orders("prop") } }
      ]
    },
    blockedWeak: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Weak Candidate" }) },
        { type: "STATS_RESPONSE", payload: stats({ NetProfit: -640, OOSNetProfit: -280, ProfitFactor: 0.92, OOSProfitFactor: 0.84, NumberOfTrades: 28, WinningPct: 43, ReturnDDRatio: 0.6 }) },
        { type: "ORDERS_RESPONSE", payload: { orders: orders("weak") } }
      ]
    },
    missingOrders: {
      messages: [
        { type: "STRATEGY_DATA", payload: strategy({ name: "Fixture Missing Orders" }) },
        { type: "STATS_RESPONSE", payload: stats() }
      ]
    }
  };
})();
