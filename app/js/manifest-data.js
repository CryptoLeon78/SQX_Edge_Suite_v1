window.SQX_MANIFEST = {
  "version": 1,
  "ui": {
    "version": 1,
    "header": {
      "titleHtml": "SQX <span>Edge</span>",
      "subtitle": ""
    },
    "tabs": [
      {
        "id": "inicio",
        "label": "Inicio",
        "active": true
      },
      {
        "id": "activos",
        "label": "Por Activo"
      },
      {
        "id": "categorias",
        "label": "Por Categoria"
      },
      {
        "id": "filtros",
        "label": "Filtros Fase 2"
      },
      {
        "id": "priority",
        "label": "SQX Priority"
      },
      {
        "id": "pipeline",
        "label": "Pipeline State"
      },
      {
        "id": "projectgen",
        "label": "Project Generator"
      },
      {
        "id": "estrategias",
        "label": "Estrategias"
      },
      {
        "id": "workflow",
        "label": "Workflow"
      }
    ],
    "filters": {
      "assetTypes": [
        {
          "value": "all",
          "label": "Todos",
          "active": true
        },
        {
          "value": "forex",
          "label": "Forex"
        },
        {
          "value": "index",
          "label": "Indices"
        },
        {
          "value": "oro",
          "label": "Oro"
        }
      ],
      "sqxConfigs": [
        {
          "value": "all",
          "label": "Todas",
          "active": true
        },
        {
          "value": "A",
          "label": "A · Both+Sym",
          "title": "Forex simétrico (Both + Entry Symmetry)"
        },
        {
          "value": "B",
          "label": "B · Both",
          "title": "Long ≠ Short — índices/oro (Both sin Symmetry)"
        },
        {
          "value": "C",
          "label": "C · Long puro",
          "title": "Activos con categorías sólo-Long puras"
        },
        {
          "value": "D",
          "label": "D · Short puro",
          "title": "Activos con categorías sólo-Short puras"
        }
      ],
      "directions": [
        {
          "value": "all",
          "label": "Todos",
          "active": true
        },
        {
          "value": "L",
          "label": "Long"
        },
        {
          "value": "S",
          "label": "Short"
        }
      ],
      "assetSort": [
        {
          "value": "name",
          "label": "Nombre A-Z"
        },
        {
          "value": "score-desc",
          "label": "Score desc"
        },
        {
          "value": "score-asc",
          "label": "Score asc"
        },
        {
          "value": "cats-desc",
          "label": "Categorias desc"
        }
      ],
      "ratings": [
        {
          "value": "all",
          "label": "Todos"
        },
        {
          "value": "++",
          "label": "Estrella"
        },
        {
          "value": "+",
          "label": "Bueno"
        },
        {
          "value": "~",
          "label": "Precaucion"
        },
        {
          "value": "-",
          "label": "No recom."
        }
      ],
      "subtypes": [
        {
          "value": "all",
          "label": "Todos"
        },
        {
          "value": "Major",
          "label": "Major"
        },
        {
          "value": "Minor",
          "label": "Minor"
        },
        {
          "value": "Exotic",
          "label": "Exotic"
        },
        {
          "value": "SP500",
          "label": "SP500"
        },
        {
          "value": "Nasdaq",
          "label": "Nasdaq"
        },
        {
          "value": "DAX",
          "label": "DAX"
        },
        {
          "value": "Dow Jones",
          "label": "Dow Jones"
        },
        {
          "value": "Oro",
          "label": "Oro"
        }
      ],
      "timeframes": [
        {
          "value": "all",
          "label": "Todos"
        },
        {
          "value": "M5",
          "label": "M5"
        },
        {
          "value": "M15",
          "label": "M15"
        },
        {
          "value": "M30",
          "label": "M30"
        },
        {
          "value": "H1",
          "label": "H1"
        },
        {
          "value": "H4",
          "label": "H4"
        },
        {
          "value": "D1",
          "label": "D1"
        }
      ],
      "priorityMin": [
        {
          "value": "0",
          "label": "Todos",
          "active": true
        },
        {
          "value": "55",
          "label": ">=55%"
        },
        {
          "value": "70",
          "label": ">=70%"
        },
        {
          "value": "85",
          "label": ">=85%"
        }
      ],
      "categories": [
        {
          "value": "all",
          "label": "Todas"
        },
        {
          "value": "tendencia",
          "label": "Tendencia"
        },
        {
          "value": "momentum",
          "label": "Momentum"
        },
        {
          "value": "volatilidad",
          "label": "Volatilidad"
        },
        {
          "value": "regimen",
          "label": "Regimen"
        },
        {
          "value": "volumen",
          "label": "Volumen"
        },
        {
          "value": "sr",
          "label": "Soporte/Resistencia"
        },
        {
          "value": "estadistico",
          "label": "Estadistico"
        }
      ],
      "strategyTiers": [
        {
          "value": "all",
          "label": "Todas",
          "active": true
        },
        {
          "value": "1",
          "label": "TIER 1"
        },
        {
          "value": "1.5",
          "label": "TIER 1.5"
        },
        {
          "value": "2",
          "label": "TIER 2"
        },
        {
          "value": "tentativa",
          "label": "Tentativas"
        }
      ],
      "strategyStatus": [
        {
          "value": "all",
          "label": "Todos"
        },
        {
          "value": "CANDIDATA",
          "label": "CANDIDATA"
        },
        {
          "value": "PASSED",
          "label": "PASSED"
        },
        {
          "value": "PASSED_ASTERISK",
          "label": "PASSED*"
        },
        {
          "value": "DEPLOYED",
          "label": "DEPLOYED"
        },
        {
          "value": "REJECTED",
          "label": "REJECTED"
        }
      ],
      "directionsFull": [
        {
          "value": "L",
          "label": "Long"
        },
        {
          "value": "S",
          "label": "Short"
        },
        {
          "value": "L/S",
          "label": "Long+Short"
        }
      ]
    },
    "categories": {
      "tendencia": {
        "name": "Tendencia",
        "icon": "T",
        "color": "#3b82f6",
        "desc": "EMA, MACD, Ichimoku, SuperTrend"
      },
      "momentum": {
        "name": "Momentum",
        "icon": "M",
        "color": "#22c55e",
        "desc": "RSI, Stochastic, CCI, ROC"
      },
      "volatilidad": {
        "name": "Volatilidad",
        "icon": "V",
        "color": "#f97316",
        "desc": "Bollinger, Keltner, Donchian, StdDev"
      },
      "regimen": {
        "name": "Regimen",
        "icon": "R",
        "color": "#a855f7",
        "desc": "CSSAMarketRegime, Entropy, Hilbert"
      },
      "volumen": {
        "name": "Volumen",
        "icon": "W",
        "color": "#06b6d4",
        "desc": "VWAP, AvgVolume"
      },
      "sr": {
        "name": "Soporte/Resistencia",
        "icon": "S",
        "color": "#ec4899",
        "desc": "Pivots, Fibo, Fractals, H/L"
      },
      "estadistico": {
        "name": "Estadistico",
        "icon": "E",
        "color": "#eab308",
        "desc": "ZScore, PercentRank"
      }
    },
    "filtros": [
      {
        "id": "ADX",
        "name": "ADX",
        "desc": "Fuerza de tendencia (Average Directional Index)",
        "long": "> 25 (confirmar tendencia real)",
        "short": "> 30 en indices (necesita tendencia bajista fuerte)"
      },
      {
        "id": "ATR",
        "name": "ATR",
        "desc": "Rango verdadero promedio — filtrar volatilidad",
        "long": "ATR min (evitar mercados planos)",
        "short": "ATR min MAS ALTO que Long (necesita volatilidad para Short rentable)"
      },
      {
        "id": "Choppiness",
        "name": "Choppiness Index",
        "desc": "Trending vs Ranging (bajo = trending)",
        "long": "< 45 (trending)",
        "short": "< 38 en indices (Short solo en tendencia bajista clara)"
      },
      {
        "id": "Hurst",
        "name": "Hurst Exponent",
        "desc": "Persistencia del movimiento (>0.5 = trending)",
        "long": "> 0.5 (persistencia)",
        "short": "> 0.55 en indices (mayor umbral para confirmar persistencia bajista)"
      },
      {
        "id": "KER",
        "name": "Kaufman Eff. Ratio",
        "desc": "Eficiencia del movimiento (0-1)",
        "long": "> 0.3 (eficiencia)",
        "short": "> 0.4 en indices (movimiento bajista debe ser mas eficiente)"
      },
      {
        "id": "AvgVolume",
        "name": "Average Volume",
        "desc": "Filtro de liquidez",
        "long": "> media (liquidez)",
        "short": "> 1.2x media en indices (volumen alto confirma sell-off real)"
      }
    ],
    "ratingOrder": {
      "++": 3,
      "+": 2,
      "~": 1,
      "-": 0
    },
    "sqxConfigDesc": {
      "A": {
        "label": "Both + Entry Sym",
        "desc": "<strong>Forex simétrico</strong>Reglas L/S espejadas en la entrada. SQX optimiza un lado y replica al otro."
      },
      "B": {
        "label": "Both sin Symmetry",
        "desc": "<strong>Long ≠ Short</strong>Índices y oro — SQX optimiza Long y Short por separado (reglas distintas)."
      },
      "C": {
        "label": "Only Long",
        "desc": "<strong>Ideas Long puras</strong>Filtra activos con ≥1 categoría sólo-Long (índices/oro). Para correr SQX en modo Only Long."
      },
      "D": {
        "label": "Only Short",
        "desc": "<strong>Ideas Short puras</strong>Filtra activos con ≥1 categoría sólo-Short (índices/oro). Para correr SQX en modo Only Short."
      }
    },
    "macroEvents": [
      {
        "date": "2008-09",
        "label": "Lehman / Crisis",
        "color": "#ef4444"
      },
      {
        "date": "2012-07",
        "label": "Draghi QE",
        "color": "#f97316"
      },
      {
        "date": "2016-06",
        "label": "Brexit",
        "color": "#06b6d4"
      },
      {
        "date": "2020-03",
        "label": "COVID",
        "color": "#a855f7"
      },
      {
        "date": "2022-02",
        "label": "Ucrania / Inflación",
        "color": "#eab308"
      },
      {
        "date": "2025-01",
        "label": "Trump II",
        "color": "#3b82f6"
      }
    ],
    "approachHints": {
      "tendencia": "Trend follow · EMA cross · MACD · SuperTrend",
      "momentum": "RSI / Stoch reversal · ROC reversal",
      "volatilidad": "Bollinger / Donchian breakout · Keltner",
      "regimen": "ADX / Hurst / SMA200 filter",
      "volumen": "VWAP rejection · AvgVolume filter",
      "sr": "Pivot / Fibo / Round number bounce",
      "estadistico": "ZScore / OU mean-reversion · PercentRank"
    },
    "catToBs": {
      "tendencia": "BS_Tendencia_v4",
      "momentum": "BS_Momentum_v4",
      "volatilidad": "BS_Volatilidad_v4",
      "regimen": "BS_Regimen_v4",
      "volumen": "BS_Volumen_v4",
      "sr": "BS_SoporteResistencia_v4",
      "estadistico": "BS_Estadistico_v4"
    },
    "bsToPriorityCat": {
      "BS_Tendencia": "tendencia",
      "BS_Momentum": "momentum",
      "BS_Volatilidad": "volatilidad",
      "BS_Regimen": "regimen",
      "BS_Volumen": "volumen",
      "BS_SoporteResistencia": "sr",
      "BS_Estadistico": "estadistico"
    },
    "priorityCatToBs": {
      "tendencia": "BS_Tendencia",
      "momentum": "BS_Momentum",
      "volatilidad": "BS_Volatilidad",
      "regimen": "BS_Regimen",
      "volumen": "BS_Volumen",
      "sr": "BS_SoporteResistencia",
      "estadistico": "BS_Estadistico"
    },
    "priorityTiers": [
      {
        "min": 85,
        "label": "MAXIMA",
        "cls": "tier-max",
        "color": "var(--green)"
      },
      {
        "min": 70,
        "label": "ALTA",
        "cls": "tier-high",
        "color": "var(--accent)"
      },
      {
        "min": 55,
        "label": "SECUNDARIA",
        "cls": "tier-mid",
        "color": "var(--yellow)"
      },
      {
        "min": 40,
        "label": "BAJA",
        "cls": "tier-low",
        "color": "var(--orange)"
      },
      {
        "min": 0,
        "label": "SKIP",
        "cls": "tier-skip",
        "color": "var(--text2)"
      }
    ],
    "statuses": [
      {
        "id": "pending",
        "label": "○ Pendiente"
      },
      {
        "id": "current",
        "label": "▶ En curso"
      },
      {
        "id": "completed",
        "label": "✓ Completado"
      }
    ],
    "storageKeys": {
      "priorityProgress": "sqx_priority_progress_v1",
      "planUser": "sqx_plan_user_v1",
      "pipelineState": "sqx_pipeline_state_v1",
      "strategiesUser": "sqx_strategies_user_v1",
      "strategiesDeleted": "sqx_strategies_deleted_v1",
      "workflowChecklist": "sqx_workflow_checklist_v1",
      "apiBase": "sqx_pg_api_base_v1"
    },
    "chart": {
      "width": 720,
      "height": 220,
      "padL": 44,
      "padR": 14,
      "padT": 18,
      "padB": 32,
      "smaPeriod": 24,
      "minBandMonths": 6
    },
    "pipeline": {
      "funnelStagesDefault": [
        {
          "id": "mining",
          "name": "Mining inicial",
          "terminal": false
        },
        {
          "id": "retest0",
          "name": "Retest 0 (período completo)",
          "terminal": false
        },
        {
          "id": "retest_oos",
          "name": "Retest 1 (OOS 2010-2017)",
          "terminal": false
        },
        {
          "id": "retest_fwd",
          "name": "Retest 2 (Forward 2024-26)",
          "terminal": false
        },
        {
          "id": "hbp",
          "name": "HBP",
          "terminal": false
        },
        {
          "id": "mc",
          "name": "MC Trades",
          "terminal": false
        },
        {
          "id": "mc2",
          "name": "MC2 Historical",
          "terminal": false
        },
        {
          "id": "sequential",
          "name": "Sequential",
          "terminal": false
        },
        {
          "id": "synthetic",
          "name": "Synthetic",
          "terminal": false
        },
        {
          "id": "spp",
          "name": "SPP",
          "terminal": false
        },
        {
          "id": "wfm",
          "name": "WFM ⭐ Final",
          "terminal": true
        }
      ],
      "funnelPreload": {
        "1|LINEAR": {
          "mining": 1000,
          "retest0": 388,
          "retest_oos": 21,
          "retest_fwd": null,
          "hbp": 17,
          "mc": 17,
          "mc2": 8,
          "sequential": 6,
          "synthetic": 4,
          "spp": 4,
          "wfm": 3
        }
      },
      "defaultNextAction": "Filter-by-correlation entre las 3 PASSED del WFM (threshold 0.7) → confirmar diversidad estructural → cerrar TEMPLATE LINEAR. Después: Capa 2 sobre TEMPLATES ICHIMOKU x2, MACD y SUPER (mismo flujo)."
    },
    "csvImport": {
      "columnMap": {
        "Strategy Name": "_strategy_name",
        "TimeFrame": "tf",
        "Symbol": "_symbol",
        "Net profit": "m.net_profit",
        "Fitness": "m.fitness",
        "Net profit in %": "m.net_profit_pct",
        "Drawdown": "m.dd",
        "Max DD %": "m.dd_pct",
        "Open Drawdown %": "m.open_dd_pct",
        "Max Intraday Drawdown": "m.max_intraday_dd",
        "Ret/DD Ratio": "m.ret_dd",
        "Annual % Return": "m.annual_pct_return",
        "Sharpe Ratio": "m.sharpe",
        "Profit factor": "m.pf",
        "# of trades": "m.trades",
        "# of profits": "m.wins",
        "# of losses": "m.losses",
        "Max Consec. Wins": "m.max_consec_wins",
        "Max Consec. Losses": "m.max_consec_losses",
        "Winning Percent": "m.win_pct",
        "Avg. Trades Per Month": "m.trades_per_month",
        "Longest trade (days)": "m.longest_trade_days",
        "Entry indicators": "indicators",
        "Exit quality": "m.exit_quality",
        "Complexity": "m.complexity",
        "EquityAngle": "m.equity_angle",
        "Stagnation": "m.stagnation_days",
        "Exposure Position": "m.exposure",
        "RecoveryFactor": "m.recovery_factor",
        "ZScore": "m.z_score",
        "SQN Score": "m.sqn",
        "R Expectancy": "m.r_exp",
        "StandardDev": "m.std_dev",
        "Payout ratio": "m.payout_ratio",
        "Avg. Bars in Trade": "m.avg_bars_in_trade"
      },
      "templateKeywords": [
        {
          "template": "LINEAR",
          "keywords": [
            "LINEARREGRESSION"
          ]
        },
        {
          "template": "ICHIMOKU",
          "keywords": [
            "ICHIMOKU"
          ]
        },
        {
          "template": "SUPER",
          "keywords": [
            "SUPERTREND"
          ]
        },
        {
          "template": "MACD",
          "keywords": [
            "MACD"
          ]
        },
        {
          "template": "SAR",
          "keywords": [
            "PARABOLICSAR"
          ]
        },
        {
          "template": "EMA",
          "keywords": [
            "EMA",
            "SMA"
          ]
        },
        {
          "template": "STOCH",
          "keywords": [
            "STOCHASTIC",
            "STOCH"
          ]
        },
        {
          "template": "RSI",
          "keywords": [
            "RSI"
          ]
        },
        {
          "template": "CCI",
          "keywords": [
            "CCI"
          ]
        },
        {
          "template": "BOLLINGER",
          "keywords": [
            "BOLLINGER"
          ]
        },
        {
          "template": "KELTNER",
          "keywords": [
            "KELTNER"
          ]
        },
        {
          "template": "DONCHIAN",
          "keywords": [
            "DONCHIAN"
          ]
        },
        {
          "template": "ADX",
          "keywords": [
            "ADX"
          ]
        },
        {
          "template": "ATR",
          "keywords": [
            "ATR"
          ]
        }
      ]
    },
    "projectGenerator": {
      "aliasSuggestMinScore": 80
    },
    "api": {
      "defaultHost": "127.0.0.1",
      "defaultPort": 5050,
      "basePath": "/api"
    }
  },
  "product": {
    "version": 1,
    "product": {
      "name": "SQX Edge",
      "publicName": "SQX Edge Suite",
      "edition": "Pro",
      "licenseVersion": 1
    },
    "build": {
      "channel": "internal",
      "label": "Internal Build",
      "defaultPlan": "internal",
      "activationMode": "manual_signed_file",
      "allowOfflineUse": true
    },
    "licensing": {
      "storageKey": "sqx_license_state_v1",
      "licenseFile": "config/license.json",
      "graceDays": 7,
      "signatureMode": "rsa_sha256_pkcs1_v1_5",
      "signatureAlgorithm": "RS256",
      "manualBetaDelivery": true,
      "keyManagement": {
        "productionKeyRequired": true,
        "publicKeyReplacementRequiredBeforePublicSale": true,
        "privateKeyPolicy": "never_commit_never_ship",
        "keypairTool": "backend/sqx-edge-tool/tools/license_keypair.ps1",
        "signerTool": "backend/sqx-edge-tool/tools/license_signer.py",
        "issuerTool": "backend/sqx-edge-tool/tools/license_issue.py",
        "localPrivateKeyFolders": [
          "license_keys",
          "licenses_private",
          "private_keys"
        ]
      },
      "publicKey": {
        "kty": "RSA",
        "kid": "sqx-prod-2026-05-placeholder",
        "alg": "RS256",
        "n": "rn0HogKI_r59abwzTUhgZAQsCKCq4qsMD8pW3nGsSoV_1iwOFotw4YEXm-rRaYNjgMydgYAMiBgblGMKv8SI8aYcIYEzMpIe7jw7LZSdwqiqhbTU7wTUh-rLhUDCkw2es5syqK1-IH_XWavaIJoVHKPk3wmBVkqtjOjdfFqXOq3EoG0-kRQiEDSk6vG9ow2zzThMFMpR01nRMvbWmOeR20NpEY_WQnse0Db-z2QvA9p5J81jqCk28VGz9EzqgbWMVycX21_QNGUD6hcWshSE7jItWJUbSbOUcme-GMnmMcSlDiQ_rugZxqD7-oV2vmhUsVQR768QjsTHuByNiXqphQ",
        "e": "AQAB"
      }
    },
    "security": {
      "apiBoundary": "local_only",
      "allowedHosts": [
        "localhost",
        "127.0.0.1",
        "::1"
      ],
      "sensitiveFilesExcludedFromPortable": [
        "config.json",
        "config/license.json",
        ".env",
        "backups",
        "dist",
        "output",
        "node_modules",
        "venv",
        ".git",
        "license_keys",
        "licenses_private",
        "private_keys",
        "*_private_key.json",
        "*.private_key.json",
        "license_signed_*.json",
        "signed_license_*.json",
        "license_payload_*.json",
        "unsigned_license_*.json",
        "fulfillment_request_*.json",
        "webhook_event_*.json",
        "relay_event_*.json",
        "fulfillment_requests",
        "backend/sqx-edge-tool/tools/license_signer.py",
        "backend/sqx-edge-tool/tools/license_keypair.ps1",
        "backend/sqx-edge-tool/tools/license_issue.py",
        "backend/sqx-edge-tool/tools/prepare_customer_delivery.ps1",
        "backend/sqx-edge-tool/tools/checkout_live_readiness.py",
        "backend/sqx-edge-tool/tools/commercial_release_candidate.py",
        "backend/sqx-edge-tool/tools/pilot_purchase_kit.py",
        "backend/sqx-edge-tool/tools/limited_public_launch.py",
        "backend/sqx-edge-tool/tools/post_launch_control.py",
        "backend/sqx-edge-tool/tools/commercial_feedback_loop.py",
        "backend/sqx-edge-tool/tools/public_offer_pack.py",
        "backend/sqx-edge-tool/tools/launch_assets_kit.py",
        "backend/sqx-edge-tool/tools/public_release_gate.py",
        "backend/sqx-edge-tool/tools/release_publication_record.py",
        "backend/sqx-edge-tool/tools/post_release_monitor.py",
        "backend/sqx-edge-tool/tools/hotfix_rollback_release.py",
        "backend/sqx-edge-tool/tools/customer_success_renewal.py",
        "backend/sqx-edge-tool/tools/fulfillment_request.py",
        "backend/sqx-edge-tool/tools/fulfill_from_request.ps1",
        "backend/sqx-edge-tool/tools/relay_bundle.py"
      ],
      "releaseAudit": "backend/sqx-edge-tool/tools/audit_distribution.ps1"
    },
    "support": {
      "diagnosticsEndpoint": "/api/support/diagnostics",
      "diagnosticsFilenamePrefix": "SQX_support_diagnostic",
      "privacyMode": "redacted_local_json",
      "safeToSend": true,
      "excludedFromDiagnostics": [
        "personal paths",
        "license payload",
        "strategy files",
        "localStorage data",
        "raw config values"
      ]
    },
    "features": {
      "dashboard.view": {
        "label": "Dashboard",
        "tier": "free"
      },
      "strategies.basic": {
        "label": "Estrategias basicas",
        "tier": "free"
      },
      "strategies.import_full": {
        "label": "Import CSV completo",
        "tier": "pro"
      },
      "strategies.export_advanced": {
        "label": "Export avanzado",
        "tier": "pro"
      },
      "project_generator.demo": {
        "label": "Project Generator demo",
        "tier": "free"
      },
      "project_generator.generate": {
        "label": "Project Generator completo",
        "tier": "pro"
      },
      "strategy_cleaner.preview": {
        "label": "Strategy Cleaner preview",
        "tier": "free"
      },
      "strategy_cleaner.apply": {
        "label": "Strategy Cleaner aplicar cambios",
        "tier": "pro"
      },
      "backups.advanced": {
        "label": "Backups avanzados",
        "tier": "pro"
      },
      "workflows.premium": {
        "label": "Workflows premium",
        "tier": "pro"
      },
      "templates.premium": {
        "label": "Packs de templates premium",
        "tier": "pack"
      },
      "support.priority": {
        "label": "Soporte prioritario",
        "tier": "add_on"
      }
    },
    "accessLevels": {
      "free": {
        "label": "SQX Edge Free",
        "state": "free",
        "features": [
          "dashboard.view",
          "strategies.basic",
          "project_generator.demo",
          "strategy_cleaner.preview"
        ]
      },
      "pro": {
        "label": "SQX Edge Pro",
        "state": "pro_active",
        "features": [
          "dashboard.view",
          "strategies.basic",
          "strategies.import_full",
          "strategies.export_advanced",
          "project_generator.demo",
          "project_generator.generate",
          "strategy_cleaner.preview",
          "strategy_cleaner.apply",
          "backups.advanced",
          "workflows.premium"
        ]
      },
      "internal": {
        "label": "SQX Edge Internal",
        "state": "internal",
        "features": [
          "*"
        ]
      }
    },
    "lockedResponses": {
      "proRequired": {
        "ok": false,
        "error": "pro_required",
        "message": "Esta funcion requiere SQX Edge Pro."
      }
    },
    "upgrade": {
      "headline": "SQX Edge Pro",
      "primaryMessage": "Convierte tu flujo SQX en un pipeline guiado, repetible y listo para trabajar.",
      "secondaryMessage": "Activa Pro para usar Project Generator, Strategy Cleaner, workflows premium y export avanzado.",
      "bullets": [
        "Genera Custom Projects .cfx desde tu plan de minings.",
        "Limpia y normaliza estrategias .sqx con preview seguro.",
        "Mantiene trazabilidad local de activos, pipeline y estrategias.",
        "Pensado para usuarios no tecnicos: portable, local y de un click."
      ],
      "plans": [
        {
          "id": "pro_monthly",
          "label": "Pro Mensual",
          "price": "24 EUR/mes",
          "checkoutUrl": ""
        },
        {
          "id": "pro_annual",
          "label": "Pro Anual",
          "price": "199 EUR/ano",
          "checkoutUrl": ""
        },
        {
          "id": "setup_assist",
          "label": "Setup Assist",
          "price": "149 EUR",
          "checkoutUrl": ""
        }
      ],
      "disclaimer": "No promete rentabilidad ni resultados financieros. La propuesta es productividad, orden y reduccion de errores operativos.",
      "checkoutProvider": "Lemon Squeezy",
      "checkoutLabel": "Comprar Pro",
      "checkoutUrl": "",
      "checkout": {
        "status": "customer_success_renewal_ready",
        "primaryProvider": "Lemon Squeezy",
        "fallbackProvider": "Gumroad",
        "mode": "hosted_checkout",
        "primaryUrl": "",
        "fallbackUrl": "",
        "supportEmail": "",
        "fulfillmentMode": "manual_signed_license",
        "deliveryArtifact": "SQX_Edge_Tool_Portable_*.zip",
        "licenseIssuerTool": "backend/sqx-edge-tool/tools/license_issue.py",
        "deliveryTool": "backend/sqx-edge-tool/tools/prepare_customer_delivery.ps1",
        "liveReadinessTool": "backend/sqx-edge-tool/tools/checkout_live_readiness.py",
        "liveReadinessEvidenceDir": "backend/sqx-edge-tool/data/checkout_live_readiness",
        "commercialReleaseCandidateTool": "backend/sqx-edge-tool/tools/commercial_release_candidate.py",
        "commercialReleaseCandidateEvidenceDir": "backend/sqx-edge-tool/data/commercial_release_candidate",
        "pilotPurchaseKitTool": "backend/sqx-edge-tool/tools/pilot_purchase_kit.py",
        "pilotPurchaseKitEvidenceDir": "backend/sqx-edge-tool/data/pilot_purchase_kit",
        "limitedPublicLaunchTool": "backend/sqx-edge-tool/tools/limited_public_launch.py",
        "limitedPublicLaunchEvidenceDir": "backend/sqx-edge-tool/data/limited_public_launch",
        "limitedPublicLaunchPolicy": "soft_launch_first_5_sales_then_review",
        "postLaunchControlTool": "backend/sqx-edge-tool/tools/post_launch_control.py",
        "postLaunchControlEvidenceDir": "backend/sqx-edge-tool/data/post_launch_control",
        "postLaunchControlPolicy": "review_first_sales_before_scaling",
        "commercialFeedbackLoopTool": "backend/sqx-edge-tool/tools/commercial_feedback_loop.py",
        "commercialFeedbackLoopEvidenceDir": "backend/sqx-edge-tool/data/commercial_feedback_loop",
        "commercialFeedbackLoopPolicy": "classify_feedback_before_offer_changes",
        "publicOfferPackTool": "backend/sqx-edge-tool/tools/public_offer_pack.py",
        "publicOfferPackEvidenceDir": "backend/sqx-edge-tool/data/public_offer_pack",
        "publicOfferPackPolicy": "review_copy_faq_release_notes_before_public_page",
        "launchAssetsKitTool": "backend/sqx-edge-tool/tools/launch_assets_kit.py",
        "launchAssetsKitEvidenceDir": "backend/sqx-edge-tool/data/launch_assets_kit",
        "launchAssetsKitPolicy": "prepare_assets_release_draft_and_publication_checklist",
        "publicReleaseGateTool": "backend/sqx-edge-tool/tools/public_release_gate.py",
        "publicReleaseGateEvidenceDir": "backend/sqx-edge-tool/data/public_release_gate",
        "publicReleaseGatePolicy": "confirm_tag_release_zip_checksum_support_and_rollback",
        "releasePublicationRecordTool": "backend/sqx-edge-tool/tools/release_publication_record.py",
        "releasePublicationRecordEvidenceDir": "backend/sqx-edge-tool/data/release_publication_record",
        "releasePublicationRecordPolicy": "record_tag_release_asset_checksum_support_and_rollback_publication",
        "postReleaseMonitorTool": "backend/sqx-edge-tool/tools/post_release_monitor.py",
        "postReleaseMonitorEvidenceDir": "backend/sqx-edge-tool/data/post_release_monitor",
        "postReleaseMonitorPolicy": "monitor_incidents_activation_support_refunds_and_scale_decision",
        "hotfixRollbackReleaseTool": "backend/sqx-edge-tool/tools/hotfix_rollback_release.py",
        "hotfixRollbackReleaseEvidenceDir": "backend/sqx-edge-tool/data/hotfix_rollback_release",
        "hotfixRollbackReleasePolicy": "prepare_hotfix_or_rollback_release_notes_comms_and_closure_evidence",
        "customerSuccessRenewalTool": "backend/sqx-edge-tool/tools/customer_success_renewal.py",
        "customerSuccessRenewalEvidenceDir": "backend/sqx-edge-tool/data/customer_success_renewal",
        "customerSuccessRenewalPolicy": "track_onboarding_activation_support_renewal_and_safe_expansion",
        "rollbackPolicy": "disable_checkout_pause_webhook_pause_worker_manual_fulfillment",
        "automation": {
          "status": "customer_success_renewal_ready",
          "webhookProvider": "Lemon Squeezy",
          "webhookSignatureHeader": "X-Signature",
          "webhookSigningAlgorithm": "hmac_sha256_hex",
          "webhookSecretEnv": "SQX_LEMON_WEBHOOK_SECRET",
          "receiverEndpoint": "/api/fulfillment/webhook/lemon",
          "relayIngestEndpoint": "/api/fulfillment/relay-ingest",
          "relaySignatureHeader": "X-SQX-Relay-Signature",
          "relaySecretEnv": "SQX_FULFILLMENT_RELAY_SECRET",
          "relayServiceProject": "backend/sqx-edge-relay",
          "relayHealthEndpoint": "/relay/health",
          "relayConfigCheckEndpoint": "/relay/config-check",
          "relayObservabilityEndpoint": "/relay/observability",
          "relaySnapshotEndpoint": "/relay/observability/snapshot",
          "relayWebhookEndpoint": "/relay/webhook/lemon",
          "relayQueueEndpoint": "/relay/queue",
          "relayDispatchEndpoint": "/relay/dispatch",
          "relayRequeueEndpoint": "/relay/requeue",
          "relayOperatorTokenEnv": "SQX_RELAY_OPERATOR_TOKEN",
          "relayWorkerScript": "backend/sqx-edge-relay/worker/dispatch_worker.py",
          "relayWorkerMode": "supervised_dispatch_loop",
          "relaySimulationTool": "backend/sqx-edge-relay/tools/simulate_purchase_flow.py",
          "relayObservabilityMode": "jsonl_events_and_queue_snapshots",
          "relayDeploymentCheckTool": "backend/sqx-edge-relay/tools/deployment_check.py",
          "relayStagingSmokeTool": "backend/sqx-edge-relay/tools/staging_smoke.py",
          "relayStagingEvidenceTool": "backend/sqx-edge-relay/tools/staging_evidence.py",
          "relayRenderApiPreflightTool": "backend/sqx-edge-relay/tools/render_api_preflight.py",
          "relayRenderCredentialsHandshakeTool": "backend/sqx-edge-relay/tools/render_credentials_handshake.py",
          "relayRenderStagingGateTool": "backend/sqx-edge-relay/tools/render_staging_gate.py",
          "relayRenderStagingApplyGateTool": "backend/sqx-edge-relay/tools/render_staging_apply_gate.py",
          "relayRenderStagingPurchaseDrillTool": "backend/sqx-edge-relay/tools/render_staging_purchase_drill.py",
          "relayRenderStagingLaunchPackTool": "backend/sqx-edge-relay/tools/render_staging_launch_pack.py",
          "relayRenderStagingSecretsKitTool": "backend/sqx-edge-relay/tools/render_staging_secrets_kit.py",
          "relayLocalIngestTunnelCheckTool": "backend/sqx-edge-relay/tools/local_ingest_tunnel_check.py",
          "relayLocalIngestTunnelLauncherTool": "backend/sqx-edge-relay/tools/local_ingest_tunnel_launcher.py",
          "relayLocalIngestStagingSessionTool": "backend/sqx-edge-relay/tools/local_ingest_staging_session.py",
          "relayLocalIngestRenderHandoffTool": "backend/sqx-edge-relay/tools/local_ingest_render_handoff.py",
          "relayRenderCredentialPolicy": "api_key_only_no_account_password",
          "relayRenderPreflightEvidenceDir": "backend/sqx-edge-relay/data/render_preflight_evidence",
          "relayRenderStagingGateEvidenceDir": "backend/sqx-edge-relay/data/render_staging_gate",
          "relayRenderStagingApplyGateEvidenceDir": "backend/sqx-edge-relay/data/render_staging_apply_gate",
          "relayRenderStagingPurchaseDrillEvidenceDir": "backend/sqx-edge-relay/data/render_staging_purchase_drill",
          "relayRenderStagingLaunchPackEvidenceDir": "backend/sqx-edge-relay/data/render_staging_launch_pack",
          "relayRenderStagingSecretsKitEvidenceDir": "backend/sqx-edge-relay/data/render_staging_secrets_kit",
          "relayLocalIngestTunnelCheckEvidenceDir": "backend/sqx-edge-relay/data/local_ingest_tunnel_check",
          "relayLocalIngestTunnelLaunchEvidenceDir": "backend/sqx-edge-relay/data/local_ingest_tunnel_launch",
          "relayLocalIngestStagingSessionEvidenceDir": "backend/sqx-edge-relay/data/local_ingest_staging_session",
          "relayLocalIngestRenderHandoffEvidenceDir": "backend/sqx-edge-relay/data/local_ingest_render_handoff",
          "relayStagingEnvExample": "backend/sqx-edge-relay/.env.staging.example",
          "relayRecommendedStagingProvider": "render",
          "relayDockerfile": "backend/sqx-edge-relay/Dockerfile",
          "relayDockerCompose": "backend/sqx-edge-relay/deploy/docker-compose.yml",
          "relayRenderBlueprint": "backend/sqx-edge-relay/deploy/render.yaml.example",
          "relayRenderStagingBlueprint": "backend/sqx-edge-relay/deploy/render.staging.yaml.example",
          "relayRailwayConfig": "backend/sqx-edge-relay/deploy/railway.json",
          "relayFlyConfig": "backend/sqx-edge-relay/deploy/fly.toml.example",
          "relaySystemdWebService": "backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay.service",
          "relaySystemdWorkerService": "backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay-worker.service",
          "relayDeploymentTargets": [
            "docker",
            "render",
            "railway",
            "fly_io",
            "vps_systemd"
          ],
          "relayStagingChecks": [
            "render_api_key",
            "render_owner_id",
            "render_blueprint_validation",
            "/relay/health",
            "/relay/config-check",
            "/relay/observability",
            "/relay/observability/snapshot",
            "/relay/webhook/lemon"
          ],
          "relayRequiredProductionSecrets": [
            "SQX_LEMON_WEBHOOK_SECRET",
            "SQX_FULFILLMENT_RELAY_SECRET",
            "SQX_RELAY_OPERATOR_TOKEN"
          ],
          "queueListEndpoint": "/api/fulfillment/requests",
          "processEndpoint": "/api/fulfillment/process",
          "requestStatusEndpoint": "/api/fulfillment/request-status",
          "normalizerTool": "backend/sqx-edge-tool/tools/fulfillment_request.py",
          "fulfillmentTool": "backend/sqx-edge-tool/tools/fulfill_from_request.ps1",
          "relayBundleTool": "backend/sqx-edge-tool/tools/relay_bundle.py",
          "queueRoot": "backend/sqx-edge-tool/fulfillment_requests",
          "deduplicationKey": "provider_event_id",
          "operatorPanelEnabled": true,
          "retryMode": "manual_retry_with_attempt_log",
          "relayMode": "trusted_remote_relay_signed_bundle",
          "relayRetryPolicy": "exponential_backoff_remote_queue",
          "requestStatuses": [
            "queued",
            "processing",
            "needs_review",
            "failed",
            "completed",
            "ignored"
          ],
          "handledEvents": [
            "order_created",
            "subscription_created",
            "subscription_updated",
            "subscription_payment_success",
            "subscription_cancelled",
            "subscription_expired"
          ],
          "eventStorePolicy": "store_raw_event_then_process_offline",
          "publicEndpointStatus": "not_enabled",
          "receiverScope": "local_private_operator_only"
        },
        "variants": [
          {
            "plan": "pro_monthly",
            "label": "SQX Edge Pro Mensual",
            "providerVariantId": "",
            "price": "24 EUR/mes",
            "billing": "monthly_subscription",
            "licenseDurationDays": 31,
            "activationLimit": 1
          },
          {
            "plan": "pro_annual",
            "label": "SQX Edge Pro Anual",
            "providerVariantId": "",
            "price": "199 EUR/ano",
            "billing": "annual_subscription",
            "licenseDurationDays": 366,
            "activationLimit": 1
          },
          {
            "plan": "setup_assist",
            "label": "Setup Assist",
            "providerVariantId": "",
            "price": "149 EUR",
            "billing": "one_time_service",
            "licenseDurationDays": 31,
            "activationLimit": 1
          }
        ],
        "postPurchaseSteps": [
          "Confirmar pago en Lemon Squeezy o Gumroad.",
          "Generar licencia firmada con license_issue.py.",
          "Preparar entrega con prepare_customer_delivery.ps1.",
          "Enviar ZIP portable, licencia JSON e instrucciones al cliente."
        ]
      }
    },
    "marketing": {
      "tagline": "De idea a pipeline operativo SQX con menos friccion.",
      "audience": "Usuarios de StrategyQuant X que quieren ordenar generacion, limpieza y validacion sin depender de scripts manuales.",
      "promise": "Menos trabajo repetitivo, mas trazabilidad y una entrega portable facil de usar.",
      "safeClaims": [
        "Ahorra tiempo preparando proyectos SQX.",
        "Reduce errores de rutas, plantillas y exports.",
        "Mantiene tu pipeline documentado y repetible.",
        "Funciona localmente y no requiere instalar Python."
      ],
      "avoidClaims": [
        "beneficios garantizados",
        "estrategias ganadoras",
        "rentabilidad asegurada",
        "resultados financieros garantizados"
      ]
    },
    "releaseProfiles": {
      "free": {
        "label": "Free public ZIP",
        "includeInternalTools": false,
        "defaultPlan": "free"
      },
      "pro": {
        "label": "Pro licensed ZIP",
        "includeInternalTools": false,
        "defaultPlan": "free"
      },
      "internal": {
        "label": "Internal development build",
        "includeInternalTools": true,
        "defaultPlan": "internal"
      }
    }
  },
  "plan": {
    "version": 1,
    "minings": [
      {
        "num": 1,
        "phase": 1,
        "asset": "XAUUSD",
        "tf": "H1",
        "bs": "BS_Tendencia",
        "dir": "L"
      },
      {
        "num": 2,
        "phase": 1,
        "asset": "XAUUSD",
        "tf": "H4",
        "bs": "BS_Tendencia",
        "dir": "L"
      },
      {
        "num": 3,
        "phase": 1,
        "asset": "XAUUSD",
        "tf": "M30",
        "bs": "BS_Tendencia",
        "dir": "L"
      },
      {
        "num": 4,
        "phase": 2,
        "asset": "EURUSD",
        "tf": "H1",
        "bs": "BS_Tendencia",
        "dir": "L/S"
      },
      {
        "num": 5,
        "phase": 2,
        "asset": "EURUSD",
        "tf": "H4",
        "bs": "BS_Tendencia",
        "dir": "L/S"
      },
      {
        "num": 6,
        "phase": 2,
        "asset": "EURUSD",
        "tf": "M30",
        "bs": "BS_Momentum",
        "dir": "L/S"
      },
      {
        "num": 7,
        "phase": 3,
        "asset": "USTEC",
        "tf": "H1",
        "bs": "BS_Tendencia",
        "dir": "L"
      },
      {
        "num": 8,
        "phase": 3,
        "asset": "USTEC",
        "tf": "H1",
        "bs": "BS_Momentum",
        "dir": "L"
      },
      {
        "num": 9,
        "phase": 3,
        "asset": "USTEC",
        "tf": "M30",
        "bs": "BS_Momentum",
        "dir": "L"
      },
      {
        "num": 10,
        "phase": 4,
        "asset": "GBPUSD",
        "tf": "H1",
        "bs": "BS_Volatilidad",
        "dir": "L/S"
      },
      {
        "num": 11,
        "phase": 4,
        "asset": "GBPJPY",
        "tf": "H1",
        "bs": "BS_Volatilidad",
        "dir": "L/S"
      },
      {
        "num": 12,
        "phase": 5,
        "asset": "EURGBP",
        "tf": "H4",
        "bs": "BS_Regimen",
        "dir": "L/S"
      },
      {
        "num": 13,
        "phase": 5,
        "asset": "AUDNZD",
        "tf": "H4",
        "bs": "BS_Regimen",
        "dir": "L/S"
      },
      {
        "num": 14,
        "phase": 5,
        "asset": "EURGBP",
        "tf": "H1",
        "bs": "BS_Estadistico",
        "dir": "L/S"
      }
    ],
    "phases": {
      "1": {
        "name": "Completar Oro",
        "desc": "XAUUSD en distintos TF, edge tendencial"
      },
      "2": {
        "name": "Major versátil",
        "desc": "EURUSD multi-TF + momentum"
      },
      "3": {
        "name": "Índice direccional",
        "desc": "USTEC con bias alcista"
      },
      "4": {
        "name": "Volatilidad",
        "desc": "GBPUSD / GBPJPY breakout y bandas"
      },
      "5": {
        "name": "Mean reversion / Cruces",
        "desc": "EURGBP + AUDNZD régimen y estadístico"
      }
    }
  },
  "assets": {
    "version": 1,
    "assets": [
      {
        "id": "EURUSD",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Tendencias macro por divergencia de politica monetaria",
            "rating": "++"
          },
          "momentum": {
            "dir": "L/S",
            "tf": "M15, M30, H1",
            "why": "Buenas reversiones en extremos RSI/Stoch",
            "rating": "+"
          },
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Ciclos claros trending/consolidacion por macro",
            "rating": "+"
          },
          "volumen": {
            "dir": "L/S",
            "tf": "M5, M15, M30",
            "why": "Mayor tick volume = VWAP representativo",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Pivots y Fibos muy respetados por institucionales",
            "rating": "++"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "M30, H1, H4",
            "why": "Baja kurtosis, distribucion mas normal. ZScore funciona bien",
            "rating": "+"
          }
        }
      },
      {
        "id": "GBPUSD",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Tendencias macro por divergencia de politica monetaria",
            "rating": "+"
          },
          "momentum": {
            "dir": "L/S",
            "tf": "M15, M30, H1",
            "why": "Buenas reversiones en extremos RSI/Stoch",
            "rating": "+"
          },
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1, H4",
            "why": "GBP alta volatilidad intrinseca",
            "rating": "++"
          },
          "volumen": {
            "dir": "L/S",
            "tf": "M5, M15, M30",
            "why": "Mayor tick volume = VWAP representativo",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Pivots y Fibos muy respetados por institucionales",
            "rating": "+"
          }
        }
      },
      {
        "id": "USDJPY",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Tendencias macro por divergencia de politica monetaria",
            "rating": "+"
          },
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1, H4",
            "why": "Volatilidad en sesion asiatica",
            "rating": "+"
          },
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Ciclos claros trending/consolidacion por macro",
            "rating": "+"
          },
          "volumen": {
            "dir": "L/S",
            "tf": "M5, M15, M30",
            "why": "Mayor tick volume = VWAP representativo",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Pivots y Fibos muy respetados por institucionales",
            "rating": "+"
          }
        }
      },
      {
        "id": "USDCHF",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Tendencias macro por divergencia de politica monetaria",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4, D1",
            "why": "Pivots y Fibos respetados",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "M30, H1, H4",
            "why": "Baja kurtosis, distribucion mas normal",
            "rating": "+"
          }
        }
      },
      {
        "id": "AUDUSD",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M15, M30, H1",
            "why": "Buenas reversiones en extremos RSI/Stoch",
            "rating": "+"
          },
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Ciclos claros trending/consolidacion por macro",
            "rating": "+"
          }
        }
      },
      {
        "id": "NZDUSD",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M15, M30, H1",
            "why": "Buenas reversiones en extremos RSI/Stoch",
            "rating": "+"
          }
        }
      },
      {
        "id": "USDCAD",
        "type": "forex",
        "sub": "Major",
        "cats": {
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1, H4",
            "why": "Correlacion con petroleo genera expansion de volatilidad",
            "rating": "+"
          }
        }
      },
      {
        "id": "EURGBP",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Tendencias lentas pero limpias",
            "rating": "+"
          },
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Alterna semanas en rango y breakout",
            "rating": "++"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "S/R claros en rango",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Par ideal para mean-reversion. ZScore extremo = reversion",
            "rating": "++"
          }
        }
      },
      {
        "id": "EURJPY",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "JPY-crosses trendan fuerte en ambas direcciones",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "JPY-crosses respetan pivots",
            "rating": "+"
          }
        }
      },
      {
        "id": "EURCAD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "CAD-crosses trendan bien por correlacion con petroleo",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Respeta bien pivots diarios y niveles Fibo",
            "rating": "+"
          }
        }
      },
      {
        "id": "EURCHF",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Baja volatilidad, momentum ciclico predecible",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "M30, H1, H4",
            "why": "Baja kurtosis, buena para ZScore",
            "rating": "+"
          }
        }
      },
      {
        "id": "EURAUD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1",
            "why": "High-vol cross, expansion de bandas predecible",
            "rating": "+"
          }
        }
      },
      {
        "id": "EURNZD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M30, H1",
            "why": "Momentum amplio por diferencial de tipos EUR vs NZD",
            "rating": "+"
          },
          "volatilidad": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Spread amplio de volatilidad, buenas expansiones",
            "rating": "+"
          }
        }
      },
      {
        "id": "GBPJPY",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "JPY-crosses trendan fuerte en ambas direcciones",
            "rating": "+"
          },
          "momentum": {
            "dir": "L/S",
            "tf": "M30, H1",
            "why": "Carry trades generan impulsos de momentum claros",
            "rating": "+"
          },
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1",
            "why": "High-vol cross, expansion de bandas predecible",
            "rating": "++"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "JPY-crosses respetan pivots",
            "rating": "+"
          }
        }
      },
      {
        "id": "GBPNZD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1",
            "why": "High-vol cross, expansion de bandas predecible",
            "rating": "+"
          }
        }
      },
      {
        "id": "GBPAUD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Tendencias amplias, alta direccionalidad",
            "rating": "+"
          },
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1",
            "why": "GBP-cross de alta volatilidad, bandas anchas",
            "rating": "+"
          }
        }
      },
      {
        "id": "GBPCAD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "CAD-crosses trendan bien por correlacion con petroleo",
            "rating": "+"
          },
          "volatilidad": {
            "dir": "L/S",
            "tf": "M15, H1",
            "why": "GBP-cross de alta volatilidad, bandas anchas",
            "rating": "+"
          }
        }
      },
      {
        "id": "GBPCHF",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "tendencia": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Tendencias claras, GBP volatil vs CHF estable",
            "rating": "+"
          },
          "sr": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Respeta bien pivots diarios y niveles Fibo",
            "rating": "+"
          }
        }
      },
      {
        "id": "AUDJPY",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M30, H1",
            "why": "Carry trades generan impulsos de momentum claros",
            "rating": "+"
          }
        }
      },
      {
        "id": "NZDJPY",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M30, H1",
            "why": "Carry trades generan impulsos de momentum claros",
            "rating": "+"
          }
        }
      },
      {
        "id": "CADJPY",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M30, H1",
            "why": "Carry trades generan impulsos de momentum claros",
            "rating": "+"
          }
        }
      },
      {
        "id": "CHFJPY",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Safe-haven vs safe-haven, regimenes marcados por risk-on/risk-off",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Par de rango con distribucion estadistica predecible",
            "rating": "+"
          }
        }
      },
      {
        "id": "AUDNZD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Baja volatilidad, momentum ciclico predecible",
            "rating": "+"
          },
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Alterna semanas en rango y breakout",
            "rating": "++"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Par ideal para mean-reversion. ZScore extremo = reversion",
            "rating": "++"
          }
        }
      },
      {
        "id": "AUDCAD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "momentum": {
            "dir": "L/S",
            "tf": "M30, H1",
            "why": "Impulsos por divergencia commodities (oro AU vs petroleo CA)",
            "rating": "+"
          },
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Cambios de regimen claros por fundamentales commodity",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Par de rango con distribucion estadistica predecible",
            "rating": "+"
          }
        }
      },
      {
        "id": "NZDCAD",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Alterna semanas en rango y breakout",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Par ideal para mean-reversion",
            "rating": "+"
          }
        }
      },
      {
        "id": "CADCHF",
        "type": "forex",
        "sub": "Minor",
        "cats": {
          "regimen": {
            "dir": "L/S",
            "tf": "H4, D1",
            "why": "Cambios de regimen claros por fundamentales commodity/safe-haven",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Par de rango con distribucion estadistica predecible",
            "rating": "+"
          }
        }
      },
      {
        "id": "USDMXN",
        "type": "forex",
        "sub": "Exotic",
        "cats": {
          "volatilidad": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Volatilidad extrema, breakout de bandas",
            "rating": "+"
          }
        }
      },
      {
        "id": "USDZAR",
        "type": "forex",
        "sub": "Exotic",
        "cats": {
          "volatilidad": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "Volatilidad extrema, breakout de bandas",
            "rating": "+"
          }
        }
      },
      {
        "id": "US500",
        "type": "index",
        "sub": "SP500",
        "cats": {
          "tendencia": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Bias alcista estructural, tendencias multi-mes",
            "rating": "++"
          },
          "tendencia_S": {
            "dir": "S",
            "tf": "M30, H1",
            "why": "Solo correcciones profundas. No recomendado Short tendencial puro",
            "rating": "-"
          },
          "momentum": {
            "dir": "L",
            "tf": "M30, H1",
            "why": "Momentum alcista en rallies",
            "rating": "+"
          },
          "momentum_S": {
            "dir": "S",
            "tf": "M5, M15, M30",
            "why": "ESTRELLA SHORT: caidas rapidas con momentum extremo",
            "rating": "++"
          },
          "volatilidad": {
            "dir": "L",
            "tf": "H1, H4",
            "why": "Breakout alcista de Bollinger/Keltner",
            "rating": "+"
          },
          "volatilidad_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "VIX sube en caidas = expansion masiva. Donchian breakout Short",
            "rating": "++"
          },
          "regimen": {
            "dir": "L",
            "tf": "H4, D1",
            "why": "Regimen trending alcista = comprar",
            "rating": "+"
          },
          "regimen_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Solo Short cuando regimen confirma bearish",
            "rating": "+"
          },
          "volumen": {
            "dir": "L",
            "tf": "M5, M15, M30",
            "why": "Volumen real. Reclaim VWAP = Long intraday",
            "rating": "+"
          },
          "volumen_S": {
            "dir": "S",
            "tf": "M5, M15",
            "why": "Rechazo en VWAP desde abajo = Short intraday",
            "rating": "+"
          },
          "sr": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Rebote en soporte (Pivots S1/S2, Fibos 61.8%)",
            "rating": "+"
          },
          "sr_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Rechazo en resistencia. Funciona bien en techo de rango",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L",
            "tf": "H1, H4",
            "why": "ZScore muy negativo (>-2) = Long por reversion",
            "rating": "+"
          },
          "estadistico_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "ZScore >+2 menos fiable Short por bias alcista. Con confirmacion",
            "rating": "~"
          }
        }
      },
      {
        "id": "USTEC",
        "type": "index",
        "sub": "Nasdaq",
        "cats": {
          "tendencia": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Bias alcista estructural, tech rallies",
            "rating": "++"
          },
          "tendencia_S": {
            "dir": "S",
            "tf": "M30, H1",
            "why": "No recomendado Short tendencial puro",
            "rating": "-"
          },
          "momentum": {
            "dir": "L",
            "tf": "M30, H1",
            "why": "Momentum alcista explosivo en tech rallies",
            "rating": "++"
          },
          "momentum_S": {
            "dir": "S",
            "tf": "M5, M15, M30",
            "why": "ESTRELLA SHORT: caidas rapidas con momentum extremo",
            "rating": "++"
          },
          "volatilidad": {
            "dir": "L",
            "tf": "H1, H4",
            "why": "Breakout alcista de Bollinger/Keltner",
            "rating": "+"
          },
          "volatilidad_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "VIX sube en caidas = expansion masiva",
            "rating": "++"
          },
          "regimen": {
            "dir": "L",
            "tf": "H4, D1",
            "why": "Regimen trending alcista",
            "rating": "+"
          },
          "regimen_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Solo Short cuando regimen bearish confirmado",
            "rating": "+"
          },
          "volumen": {
            "dir": "L",
            "tf": "M5, M15, M30",
            "why": "Volumen real. Reclaim VWAP = Long",
            "rating": "+"
          },
          "volumen_S": {
            "dir": "S",
            "tf": "M5, M15",
            "why": "Rechazo VWAP = Short intraday",
            "rating": "+"
          },
          "sr": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Rebote en soporte",
            "rating": "+"
          },
          "sr_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Rechazo en resistencia",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L",
            "tf": "H1, H4",
            "why": "ZScore negativo extremo = Long",
            "rating": "+"
          },
          "estadistico_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "ZScore positivo menos fiable Short",
            "rating": "~"
          }
        }
      },
      {
        "id": "GER40",
        "type": "index",
        "sub": "DAX",
        "cats": {
          "tendencia": {
            "dir": "L",
            "tf": "H1, H4",
            "why": "Tendencia alcista europea",
            "rating": "+"
          },
          "tendencia_S": {
            "dir": "S",
            "tf": "M30, H1",
            "why": "No recomendado Short tendencial",
            "rating": "-"
          },
          "momentum": {
            "dir": "L",
            "tf": "M15, M30",
            "why": "Ciclos intraday marcados, European open",
            "rating": "+"
          },
          "momentum_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "Caidas intraday bruscas",
            "rating": "+"
          },
          "volatilidad_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "Expansion vol en gap-downs y crisis europeas",
            "rating": "+"
          },
          "regimen": {
            "dir": "L",
            "tf": "H4, D1",
            "why": "Regimen trending alcista",
            "rating": "+"
          },
          "regimen_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Regimen bearish confirmado",
            "rating": "+"
          },
          "volumen": {
            "dir": "L",
            "tf": "M5, M15, M30",
            "why": "Volumen real",
            "rating": "+"
          },
          "sr": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Niveles psicologicos (18000, 20000)",
            "rating": "+"
          },
          "sr_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Rechazo en resistencia",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L",
            "tf": "M30, H1",
            "why": "Reversion intraday sesion europea",
            "rating": "+"
          }
        }
      },
      {
        "id": "US30",
        "type": "index",
        "sub": "Dow Jones",
        "cats": {
          "tendencia": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Bias alcista estructural",
            "rating": "++"
          },
          "tendencia_S": {
            "dir": "S",
            "tf": "M30, H1",
            "why": "No recomendado",
            "rating": "-"
          },
          "momentum": {
            "dir": "L",
            "tf": "M30, H1",
            "why": "Momentum en rallies",
            "rating": "+"
          },
          "momentum_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "Momentum Short en caidas",
            "rating": "+"
          },
          "volumen": {
            "dir": "L",
            "tf": "M5, M15, M30",
            "why": "Volumen real",
            "rating": "+"
          },
          "volumen_S": {
            "dir": "S",
            "tf": "M5, M15",
            "why": "Short intraday VWAP",
            "rating": "+"
          },
          "sr": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Niveles redondos + pivots",
            "rating": "+"
          },
          "sr_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Rechazo en resistencia",
            "rating": "+"
          }
        }
      },
      {
        "id": "XAUUSD",
        "type": "oro",
        "sub": "Oro",
        "cats": {
          "tendencia": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Tendencias fuertes en risk-off/inflacion. Muy bueno Long",
            "rating": "++"
          },
          "tendencia_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Solo en fases USD fuerte. Tendencias Short cortas y erraticas",
            "rating": "~"
          },
          "momentum": {
            "dir": "L",
            "tf": "M30, H1",
            "why": "Impulsos Long en datos macro (CPI, NFP, FOMC)",
            "rating": "+"
          },
          "momentum_S": {
            "dir": "S",
            "tf": "M15, M30",
            "why": "Caidas por USD fuerte son rapidas. Momentum Short en TF cortos",
            "rating": "++"
          },
          "volatilidad": {
            "dir": "L",
            "tf": "H1, H4",
            "why": "Expansion vol en crisis = Oro sube rompiendo bandas superiores",
            "rating": "+"
          },
          "volatilidad_S": {
            "dir": "S",
            "tf": "M30, H1",
            "why": "Expansion vol en USD fuerte, bandas inferiores se rompen rapido",
            "rating": "+"
          },
          "regimen": {
            "dir": "L",
            "tf": "H4, D1",
            "why": "Fases acumulacion a expansion muy marcadas",
            "rating": "+"
          },
          "regimen_S": {
            "dir": "S",
            "tf": "H4",
            "why": "Detectar regimen bearish (USD rally) antes de operar Short",
            "rating": "+"
          },
          "volumen": {
            "dir": "L/S",
            "tf": "M15, M30",
            "why": "VWAP como pivot intraday, ambas direcciones",
            "rating": "+"
          },
          "sr": {
            "dir": "L",
            "tf": "H1, H4, D1",
            "why": "Niveles redondos (2000, 2500, 3000) + Fibo historicos",
            "rating": "++"
          },
          "sr_S": {
            "dir": "S",
            "tf": "H1, H4",
            "why": "Rechazo en resistencia / Highest. Short en techo de rango",
            "rating": "+"
          },
          "estadistico": {
            "dir": "L/S",
            "tf": "H1, H4",
            "why": "ZScore sobre ATR detecta movimientos anomalos",
            "rating": "+"
          }
        }
      }
    ]
  },
  "strategies": {
    "version": 1,
    "strategies": [
      {
        "id": "0.621529",
        "name": "ATR + LinearRegression",
        "mining": 1,
        "asset": "XAUUSD",
        "tf": "H1",
        "blocksetting": "BS_Tendencia",
        "template": "LINEAR",
        "direction": "L",
        "indicators": "ATR + LinearRegression",
        "exits": "ATR-based PT/SL/TS",
        "metrics": {
          "net_profit": 9412,
          "wfm_profit": 6304,
          "pf": 1.94,
          "sharpe": 1.42,
          "ret_dd": 12.32,
          "dd_pct": 0.76,
          "trades": 315,
          "win_pct": 49.84,
          "r_exp": 0.47
        },
        "tier": "1",
        "status": "PASSED",
        "tests_passed": [
          "OOS",
          "Forward",
          "HBP",
          "MC",
          "MC2",
          "Sequential",
          "Synthetic",
          "SPP",
          "WFM"
        ],
        "tests_failed": [],
        "notes": "Pasa TODOS los tests sin excepciones. Candidata #1 absoluta del template LINEAR.",
        "added": "2026-05-01"
      },
      {
        "id": "0.920817",
        "name": "KER + LinearRegression",
        "mining": 1,
        "asset": "XAUUSD",
        "tf": "H1",
        "blocksetting": "BS_Tendencia",
        "template": "LINEAR",
        "direction": "L",
        "indicators": "KaufmanEfficiencyRatio + LinearRegression",
        "exits": "ATR-based PT/SL/TS",
        "metrics": {
          "net_profit": 8303,
          "wfm_profit": 6458,
          "pf": 2.13,
          "sharpe": 1.33,
          "ret_dd": 15.56,
          "dd_pct": 0.5,
          "trades": 225,
          "win_pct": 53.54,
          "r_exp": 0.42
        },
        "tier": "1.5",
        "status": "PASSED_ASTERISK",
        "tests_passed": [
          "OOS",
          "Forward",
          "HBP",
          "MC",
          "MC2",
          "Sequential",
          "SPP",
          "WFM"
        ],
        "tests_failed": [
          "Synthetic (4.2%)"
        ],
        "notes": "Excepcional — PF y Ret/DD mejores del grupo. Falló Synthetic por 4.2% (margen estrecho), por eso TIER 1.5.",
        "added": "2026-05-01"
      },
      {
        "id": "0.553059",
        "name": "LinearRegression solo",
        "mining": 1,
        "asset": "XAUUSD",
        "tf": "H1",
        "blocksetting": "BS_Tendencia",
        "template": "LINEAR",
        "direction": "L",
        "indicators": "LinearRegression (sin filtro adicional)",
        "exits": "ATR-based PT/SL/TS",
        "metrics": {
          "net_profit": 11841,
          "wfm_profit": 7894,
          "pf": 1.86,
          "sharpe": 1.06,
          "ret_dd": 8.56,
          "dd_pct": 1.34,
          "trades": 228,
          "win_pct": 42.98,
          "r_exp": 0.3
        },
        "tier": "2",
        "status": "PASSED",
        "tests_passed": [
          "OOS",
          "Forward",
          "HBP",
          "MC",
          "MC2",
          "Sequential",
          "Synthetic",
          "SPP",
          "WFM"
        ],
        "tests_failed": [],
        "notes": "Edge LinReg puro sin filtro adicional. NetProfit más alto del grupo pero números más optimistas vs mediana.",
        "added": "2026-05-01"
      },
      {
        "id": "0.1497964",
        "name": "MACD + ADX dual",
        "mining": 1,
        "asset": "XAUUSD",
        "tf": "H1",
        "blocksetting": "BS_Tendencia",
        "template": "MACD",
        "direction": "L",
        "indicators": "MACD(8,17,9) Signal[1] crosses above 2.7 + ADX(40,+DI)[1] >= ADX(30,Main)[1]",
        "exits": "PT 10*ATR / SL 45*ATR / TS 60*ATR",
        "metrics": {
          "net_profit": 14822.64,
          "pf": 1.62,
          "sharpe": 1.12,
          "ret_dd": 9.11,
          "dd_pct": 1.58,
          "dd": 1626.58,
          "trades": 273,
          "win_pct": 44.69,
          "r_exp": 0.34,
          "r_exp_score": 10.99,
          "sqn": 0.58,
          "cagr": 1.74,
          "stagnation_days": 451,
          "stagnation_pct": 14.58,
          "z_probability": 1.16,
          "exposure": 9.69
        },
        "tier": "tentativa",
        "status": "CANDIDATA",
        "tests_passed": [],
        "tests_failed": [],
        "notes": "Candidata tentativa template MACD. Pendiente WFM, MC, correlación con LINEAR ganadoras. Threshold MACD '2.7' y ADX dual (40/30) huelen a overfitting — verificar en Sequential. Stagnation 451d alta.",
        "added": "2026-05-02"
      }
    ]
  }
};
