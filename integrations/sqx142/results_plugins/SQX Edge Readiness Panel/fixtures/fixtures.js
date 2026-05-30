window.SQX_EDGE_FIXTURES = {
  ready: {
    label: "Ready",
    messages: [
      {
        type: "STRATEGY_DATA",
        payload: {
          id: "mock-ready-001",
          name: "Redacted Strategy A",
          projectName: "Redacted Project",
          databankName: "Foward",
          symbol: "AUDCAD",
          timeframe: "H1"
        }
      },
      {
        type: "STATS_RESPONSE",
        payload: {
          NetProfit: 18450.25,
          NumberOfTrades: 142,
          ProfitFactor: 1.38,
          RExpectancy: 0.082,
          ReturnDDRatio: 3.4,
          Drawdown: 5420.1
        }
      },
      {
        type: "LAST_SETTINGS_XML_RESPONSE",
        payload: {
          available: true,
          redacted: true
        }
      },
      {
        type: "SYMBOL_INFO_RESPONSE",
        payload: {
          symbol: "AUDCAD",
          timeframe: "H1",
          precision: "TICK",
          timezone: "EETUS",
          brokerProfile: "redacted"
        }
      }
    ]
  },
  review: {
    label: "Review",
    messages: [
      {
        type: "STRATEGY_DATA",
        payload: {
          id: "mock-review-001",
          name: "Redacted Strategy B",
          projectName: "Redacted Project",
          databankName: "RETEST 0",
          symbol: "AUDCAD",
          timeframe: "M30"
        }
      },
      {
        type: "STATS_RESPONSE",
        payload: {
          NetProfit: 3620.5,
          NumberOfTrades: 44,
          ProfitFactor: 1.06,
          RExpectancy: 0.012,
          ReturnDDRatio: 0.92,
          Drawdown: 3910.4
        }
      },
      {
        type: "SYMBOL_INFO_RESPONSE",
        payload: {
          symbol: "AUDCAD",
          timeframe: "M30",
          precision: "TICK",
          timezone: "EETUS",
          brokerProfile: "redacted"
        }
      }
    ]
  },
  blocked: {
    label: "Blocked",
    messages: [
      {
        type: "STRATEGY_DATA",
        payload: {
          id: "mock-blocked-001",
          name: "Redacted Strategy C",
          projectName: "Redacted Project",
          databankName: "Results",
          symbol: "AUDCAD",
          timeframe: "M15"
        }
      },
      {
        type: "STATS_RESPONSE",
        payload: {
          NetProfit: -220.3,
          NumberOfTrades: 14,
          ProfitFactor: 0.94,
          RExpectancy: -0.015,
          ReturnDDRatio: 0.22,
          Drawdown: 980.2
        }
      },
      {
        type: "SYMBOL_INFO_RESPONSE",
        payload: {
          symbol: "AUDCAD",
          timeframe: "M15",
          precision: "TICK",
          timezone: "EETUS",
          brokerProfile: "redacted"
        }
      }
    ]
  }
};
