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
        "id": "workflow",
        "label": "Workflow",
        "icon": "W",
        "active": true
      },
      {
        "id": "activos",
        "label": "Activos",
        "icon": "A"
      },
      {
        "id": "pipeline",
        "label": "Mining Control",
        "icon": "M"
      },
      {
        "id": "views",
        "label": "SQX Views",
        "icon": "V"
      },
      {
        "id": "projectgen",
        "label": "Project Generator",
        "icon": "P"
      },
      {
        "id": "templatemaker",
        "label": "Template Maker",
        "icon": "T"
      },
      {
        "id": "estrategias",
        "label": "Strategy Control",
        "icon": "S"
      },
      {
        "id": "cvc",
        "label": "Champion vs Challenger",
        "icon": "CvC"
      },
      {
        "id": "filtros",
        "label": "BlockSettings Info",
        "icon": "B"
      },
      {
        "id": "inicio",
        "label": "Control Panel",
        "icon": "C"
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
    "blockSettingsInfo": {
      "title": "BlockSettings Info",
      "subtitle": "Escaparate metodologico de los BlockSettings reales v6 que usa SQX Edge para buscar Edge, resolver variantes por timeframe y endurecer Capa 2 con trazabilidad por hash.",
      "mode": "hibrido",
      "capa1Title": "Capa 1 · Buscar Edge",
      "capa1Intro": "Cada tarjeta de Activos propone una hipotesis de edge por familia. En Capa 1 se resuelve automaticamente el BlockSetting oficial correcto; en familias con variante intraday, M5/M15/M30/H1 usan la variante intraday. Volatilidad mantiene fallback general v4 en H4/D1 porque el paquete v6 recibido no incluye un .sqb general de esa familia.",
      "capa2Title": "Capa 2 · Filtros operativos",
      "capa2Intro": "Capa 2 conserva el edge ganador de Capa 1 y anade filtros random controlados, SL, TP y Trailing basados en ATR para convertirlo en una estrategia operable.",
      "capa1": [
        {
          "category": "tendencia",
          "blockSetting": "BS_Tendencia_v6",
          "displayBlockSetting": "BS_Tendencia_v6",
          "objective": "Detectar persistencia direccional limpia.",
          "marketLogic": "Busca mercados con continuidad, pendiente y ruptura ordenada. Encaja con EMA, MACD, Ichimoku y SuperTrend.",
          "whenToUse": "Activos con sesgo tendencial, rupturas con seguimiento y ratings altos en tarjetas de Tendencia.",
          "capaUse": "Capa 1: edge direccional base sin gestion operativa avanzada.",
          "assetCardLink": "Tarjetas de Activos etiquetadas como Tendencia.",
          "tags": [
            "Trend follow",
            "EMA",
            "MACD",
            "Ichimoku",
            "SuperTrend"
          ],
          "parameterStatus": "Fuente real: BS_Tendencia_v6.sqb · hash D51F88B9B2D5.",
          "filename": "BS_Tendencia_v6.sqb",
          "sha256Short": "D51F88B9B2D5",
          "activeBlocks": 38,
          "activeIndicators": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku"
          ],
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "category": "momentum",
          "blockSetting": "BS_Momentum_v6",
          "displayBlockSetting": "BS_Momentum_v6",
          "objective": "Capturar impulso, agotamiento y reversion de corto plazo.",
          "marketLogic": "Normaliza osciladores para detectar aceleracion, sobrecompra/sobreventa y cambios de ritmo.",
          "whenToUse": "Activos donde la tarjeta muestra momentum recurrente o rebotes estadisticos con volumen suficiente.",
          "capaUse": "Capa 1: edge de impulso/reversion antes de optimizar salidas.",
          "assetCardLink": "Tarjetas de Activos etiquetadas como Momentum.",
          "tags": [
            "RSI",
            "Stochastic",
            "CCI",
            "ROC",
            "Reversal"
          ],
          "parameterStatus": "Fuente real: BS_Momentum_v6.sqb · hash 774E79AB6273.",
          "filename": "BS_Momentum_v6.sqb",
          "sha256Short": "774E79AB6273",
          "activeBlocks": 26,
          "activeIndicators": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR"
          ],
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "category": "volatilidad",
          "blockSetting": "BS_Volatilidad_v4",
          "displayBlockSetting": "BS_Volatilidad_v4 · intraday BS_Volatilidad_v6_intraday_v6",
          "filename": "BS_Volatilidad_v4.sqb",
          "sha256Short": "112975F33993",
          "activeBlocks": 39,
          "activeIndicators": [
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange"
          ],
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "intradayBlockSetting": "BS_Volatilidad_v6_intraday_v6",
          "intradayFilename": "BS_Volatilidad_v6_intraday_v6.sqb",
          "intradaySha256Short": "63EEAE27584F",
          "intradayVariant": "v6_intraday_v6",
          "parameterStatus": "Fuente real: BS_Volatilidad_v4.sqb · hash 112975F33993. Intraday M5/M15/M30/H1: BS_Volatilidad_v6_intraday_v6.sqb · hash 63EEAE27584F."
        },
        {
          "category": "regimen",
          "blockSetting": "BS_Regimen_v6",
          "displayBlockSetting": "BS_Regimen_v6",
          "objective": "Separar contextos de tendencia, rango y ruido.",
          "marketLogic": "Usa indicadores de regimen para evitar mezclar edges que solo funcionan bajo una estructura concreta.",
          "whenToUse": "Activos donde el problema principal es elegir contexto de mercado antes de disparar entradas.",
          "capaUse": "Capa 1: edge condicionado por regimen sin sobrecargar la salida.",
          "assetCardLink": "Tarjetas de Activos etiquetadas como Regimen.",
          "tags": [
            "ADX",
            "Hurst",
            "Entropy",
            "Hilbert",
            "SMA200"
          ],
          "parameterStatus": "Fuente real: BS_Regimen_v6.sqb · hash 0589FD1B4FC8.",
          "filename": "BS_Regimen_v6.sqb",
          "sha256Short": "0589FD1B4FC8",
          "activeBlocks": 22,
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ChoppinessIndex",
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath",
            "Indicators.HurstExponent"
          ],
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "category": "volumen",
          "blockSetting": "BS_Volumen_v6",
          "displayBlockSetting": "BS_Volumen_v6 · intraday BS_Volumen_v6_intraday_v6",
          "objective": "Confirmar participacion, liquidez y zonas con rechazo real.",
          "marketLogic": "Filtra senales que necesitan volumen relativo o precio respecto a VWAP para no operar movimientos debiles.",
          "whenToUse": "Activos con patrones de liquidez, rechazo a VWAP o necesidad de confirmar participacion.",
          "capaUse": "Capa 1: edge apoyado en contexto de volumen.",
          "assetCardLink": "Tarjetas de Activos etiquetadas como Volumen.",
          "tags": [
            "VWAP",
            "AvgVolume",
            "Liquidity",
            "Rejection"
          ],
          "parameterStatus": "Fuente real: BS_Volumen_v6.sqb · hash CA74EB900440. Intraday M5/M15/M30/H1: BS_Volumen_v6_intraday_v6.sqb · hash 9CC8A6D14E8A.",
          "filename": "BS_Volumen_v6.sqb",
          "sha256Short": "CA74EB900440",
          "activeBlocks": 28,
          "activeIndicators": [
            "Indicators.AvgVolume",
            "Indicators.VWAP"
          ],
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "intradayBlockSetting": "BS_Volumen_v6_intraday_v6",
          "intradayFilename": "BS_Volumen_v6_intraday_v6.sqb",
          "intradaySha256Short": "9CC8A6D14E8A",
          "intradayVariant": "v6_intraday_v6"
        },
        {
          "category": "sr",
          "blockSetting": "BS_SoporteResistencia_v6",
          "displayBlockSetting": "BS_SoporteResistencia_v6 · intraday BS_SoporteResistencia_v6_intraday_v6",
          "objective": "Buscar respuesta del precio en zonas tecnicas repetibles.",
          "marketLogic": "Estructura entradas alrededor de pivots, fractales, fibonacci y extremos de rango.",
          "whenToUse": "Activos que respetan niveles, rechazos o zonas de soporte/resistencia con suficiente recurrencia.",
          "capaUse": "Capa 1: edge de nivel tecnico antes de gestion operativa.",
          "assetCardLink": "Tarjetas de Activos etiquetadas como Soporte/Resistencia.",
          "tags": [
            "Pivots",
            "Fibo",
            "Fractals",
            "H/L",
            "Bounce"
          ],
          "parameterStatus": "Fuente real: BS_SoporteResistencia_v6.sqb · hash 9CCC2B2876E3. Intraday M5/M15/M30/H1: BS_SoporteResistencia_v6_intraday_v6.sqb · hash 059314501E43.",
          "filename": "BS_SoporteResistencia_v6.sqb",
          "sha256Short": "9CCC2B2876E3",
          "activeBlocks": 32,
          "activeIndicators": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange"
          ],
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "intradayBlockSetting": "BS_SoporteResistencia_v6_intraday_v6",
          "intradayFilename": "BS_SoporteResistencia_v6_intraday_v6.sqb",
          "intradaySha256Short": "059314501E43",
          "intradayVariant": "v6_intraday_v6"
        },
        {
          "category": "estadistico",
          "blockSetting": "BS_Estadistico_v6",
          "displayBlockSetting": "BS_Estadistico_v6",
          "objective": "Detectar desviaciones estadisticas con probabilidad de normalizacion.",
          "marketLogic": "Agrupa senales de distancia, percentiles y mean reversion para edges no puramente tendenciales.",
          "whenToUse": "Activos con ratings estadisticos altos, desviaciones repetibles y comportamiento de retorno a media.",
          "capaUse": "Capa 1: edge estadistico base con control posterior en Capa 2.",
          "assetCardLink": "Tarjetas de Activos etiquetadas como Estadistico.",
          "tags": [
            "ZScore",
            "PercentRank",
            "OU",
            "Mean reversion"
          ],
          "parameterStatus": "Fuente real: BS_Estadistico_v6.sqb · hash 12218A93C737.",
          "filename": "BS_Estadistico_v6.sqb",
          "sha256Short": "12218A93C737",
          "activeBlocks": 22,
          "activeIndicators": [
            "Indicators.HurstExponent",
            "Indicators.KaufmanEfficiencyRatio",
            "Indicators.SRPercentRank",
            "Indicators.ZScore"
          ],
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        }
      ],
      "capa2": {
        "blockSetting": "BS_Filtros_v6 / BS_Filtros_v6_D1",
        "objective": "Endurecer una plantilla ganadora con filtros operativos sin cambiar el edge base.",
        "marketLogic": "Los filtros se anaden como condiciones random controladas y se combinan con salidas ATR-based para mejorar operabilidad.",
        "capaUse": "Capa 2: TEMPLATE ganador fijo, 1-2 filtros adicionales, SL/TP/Trailing y retests completos.",
        "parameterStatus": "Capa 2 usa BS_Filtros_v6 como recomendacion general y BS_Filtros_v6_D1 para D1. Los v4/v5/v7 quedan en catalogo como compatibilidad legacy, no como default metodologico.",
        "filterIds": [
          "ADX",
          "ATR",
          "Choppiness",
          "Hurst",
          "KER",
          "AvgVolume"
        ],
        "displayBlockSetting": "BS_Filtros v6 por timeframe",
        "filename": "Selector manual con recomendacion automatica v6",
        "sha256Short": "ver opcion elegida",
        "recommendations": {
          "M5": "BS_Filtros_v6",
          "M15": "BS_Filtros_v6",
          "M30": "BS_Filtros_v6",
          "H1": "BS_Filtros_v6",
          "H4": "BS_Filtros_v6",
          "D1": "BS_Filtros_v6_D1",
          "fallback": "BS_Filtros_v6"
        }
      },
      "principles": [
        {
          "title": "Familias de comportamiento",
          "text": "El BlockSetting se elige por comportamiento de mercado, no por capricho ni por nombre del activo."
        },
        {
          "title": "Capa 1 no contamina salidas",
          "text": "Primero se busca edge estructural; la gestion operativa se deja para Capa 2."
        },
        {
          "title": "Capa 2 conserva el template",
          "text": "El edge ganador queda fijo y solo se anaden filtros/SL/TP/Trailing para hacerlo operable."
        },
        {
          "title": "No relajar sin diagnostico",
          "text": "Si no aparecen candidatos, revisa activo, categoria o timeframe antes de romper la calibracion."
        }
      ],
      "flow": [
        {
          "step": "Activos",
          "text": "La tarjeta marca la hipotesis: activo, categoria, direccion y timeframe."
        },
        {
          "step": "Plan Mining",
          "text": "El mining conserva el origen y el BlockSetting metodologico que toca usar."
        },
        {
          "step": "Project Generator",
          "text": "Genera el .cfx con el BlockSetting correcto para Capa 1 o Capa 2."
        },
        {
          "step": "SQX",
          "text": "Se ejecuta el mining/retest con la configuracion calibrada."
        },
        {
          "step": "Template Maker / CVC",
          "text": "Se certifican metricas, C2 y decision final sin perder trazabilidad."
        }
      ],
      "modeLabel": "FUENTE SQB REAL",
      "modeText": "Cada tarjeta enlaza con un .sqb versionado, hash SHA-256 y parametros extraidos del config.xml real."
    },
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
      "tendencia": "BS_Tendencia_v6",
      "momentum": "BS_Momentum_v6",
      "volatilidad": "BS_Volatilidad_v4",
      "regimen": "BS_Regimen_v6",
      "volumen": "BS_Volumen_v6",
      "sr": "BS_SoporteResistencia_v6",
      "estadistico": "BS_Estadistico_v6"
    },
    "bsToPriorityCat": {
      "BS_Tendencia": "tendencia",
      "BS_Momentum": "momentum",
      "BS_Volatilidad": "volatilidad",
      "BS_Regimen": "regimen",
      "BS_Volumen": "volumen",
      "BS_SoporteResistencia": "sr",
      "BS_Estadistico": "estadistico",
      "BS_Estadistico_v4": "estadistico",
      "BS_Estadistico_v4.sqb": "estadistico",
      "BS_Estadistico_v6": "estadistico",
      "BS_Estadistico_v6.sqb": "estadistico",
      "BS_Momentum_v4": "momentum",
      "BS_Momentum_v4.sqb": "momentum",
      "BS_Momentum_v6": "momentum",
      "BS_Momentum_v6.sqb": "momentum",
      "BS_Regimen_v4": "regimen",
      "BS_Regimen_v4.sqb": "regimen",
      "BS_Regimen_v6": "regimen",
      "BS_Regimen_v6.sqb": "regimen",
      "BS_SoporteResistencia_v4": "sr",
      "BS_SoporteResistencia_v4.sqb": "sr",
      "BS_SoporteResistencia_v4_intraday_v5": "sr",
      "BS_SoporteResistencia_v4_intraday_v5.sqb": "sr",
      "BS_SoporteResistencia_v6": "sr",
      "BS_SoporteResistencia_v6.sqb": "sr",
      "BS_SoporteResistencia_v6_intraday_v6": "sr",
      "BS_SoporteResistencia_v6_intraday_v6.sqb": "sr",
      "BS_Tendencia_v4": "tendencia",
      "BS_Tendencia_v4.sqb": "tendencia",
      "BS_Tendencia_v6": "tendencia",
      "BS_Tendencia_v6.sqb": "tendencia",
      "BS_Volatilidad_v4": "volatilidad",
      "BS_Volatilidad_v4.sqb": "volatilidad",
      "BS_Volatilidad_v4_intraday_v5": "volatilidad",
      "BS_Volatilidad_v4_intraday_v5.sqb": "volatilidad",
      "BS_Volatilidad_v6_intraday_v6": "volatilidad",
      "BS_Volatilidad_v6_intraday_v6.sqb": "volatilidad",
      "BS_Volumen_v4": "volumen",
      "BS_Volumen_v4.sqb": "volumen",
      "BS_Volumen_v4_intraday_v5": "volumen",
      "BS_Volumen_v4_intraday_v5.sqb": "volumen",
      "BS_Volumen_v6": "volumen",
      "BS_Volumen_v6.sqb": "volumen",
      "BS_Volumen_v6_intraday_v6": "volumen",
      "BS_Volumen_v6_intraday_v6.sqb": "volumen"
    },
    "priorityCatToBs": {
      "tendencia": "BS_Tendencia_v6",
      "momentum": "BS_Momentum_v6",
      "volatilidad": "BS_Volatilidad_v4",
      "regimen": "BS_Regimen_v6",
      "volumen": "BS_Volumen_v6",
      "sr": "BS_SoporteResistencia_v6",
      "estadistico": "BS_Estadistico_v6"
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
      "viewCreatorPresets": "sqx_view_creator_presets_v1",
      "navCollapsed": "sqx_nav_collapsed_v1",
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
    },
    "blockSettingsCatalog": {
      "entries": [
        {
          "canonicalId": "BS_Estadistico_v4",
          "filename": "BS_Estadistico_v4.sqb",
          "family": "estadistico",
          "familyLabel": "Estadistico",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "812A906949CA2555B8FC4E2C6142A030F89863EBC2D1FE21A91550E9F6D69010",
          "sha256Short": "812A906949CA",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 20,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 20
            }
          },
          "activeBlocks": [
            "Indicators.SRPercentRank",
            "Indicators.ZScore",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLowerCount",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreaterCount",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.SRPercentRank",
            "Indicators.ZScore"
          ],
          "activeBlockPreview": [
            "Indicators.SRPercentRank",
            "Indicators.ZScore",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLowerCount",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals"
          ],
          "parameterPreview": {
            "Indicators.SRPercentRank": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Mode#",
                  "name": "Mode",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Length#",
                  "name": "Length",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#ATRPeriod#",
                  "name": "ATR Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.ZScore": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Open": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "IsLowerPercentil": {
              "generated": [
                {
                  "key": "#Indicator#",
                  "name": "Indicator",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Bars#",
                  "name": "Bars",
                  "type": "int",
                  "generation": "random",
                  "min": "100",
                  "max": "1000",
                  "step": "100"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Percentile#",
                  "name": "Percentile",
                  "type": "double",
                  "generation": "random",
                  "min": "5",
                  "max": "95",
                  "step": "5"
                }
              ]
            },
            "IsLowerCount": {
              "generated": [
                {
                  "key": "#Bars#",
                  "name": "Bars",
                  "type": "int",
                  "generation": "random",
                  "min": "2",
                  "max": "10",
                  "step": "1"
                },
                {
                  "key": "#NotStrict#",
                  "name": "Allow same values",
                  "type": "boolean",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#IndicatorLeft#",
                  "name": "Indicator Left",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#IndicatorRight#",
                  "name": "Indicator Right",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Estadistico_v6",
          "filename": "BS_Estadistico_v6.sqb",
          "family": "estadistico",
          "familyLabel": "Estadistico",
          "layer": 1,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "12218A93C737FAD0A0D3F0F5F55374C7162D0717007A7ECF3DEA80E9DD56112B",
          "sha256Short": "12218A93C737",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 22,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 22
            }
          },
          "activeBlocks": [
            "Indicators.HurstExponent",
            "Indicators.KaufmanEfficiencyRatio",
            "Indicators.SRPercentRank",
            "Indicators.ZScore",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLowerCount",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreaterCount",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.HurstExponent",
            "Indicators.KaufmanEfficiencyRatio",
            "Indicators.SRPercentRank",
            "Indicators.ZScore"
          ],
          "activeBlockPreview": [
            "Indicators.HurstExponent",
            "Indicators.KaufmanEfficiencyRatio",
            "Indicators.SRPercentRank",
            "Indicators.ZScore",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLowerCount",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "Indicators.HurstExponent": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.SRPercentRank": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Mode#",
                  "name": "Mode",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Length#",
                  "name": "Length",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#ATRPeriod#",
                  "name": "ATR Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.ZScore": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Open": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v4",
          "filename": "BS_Filtros_v4.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "EAED2430BB0ACC4E6477704BDFB8F807D5555DD5B1EA8733B5C952255B02669E",
          "sha256Short": "EAED2430BB0A",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v5_D1",
          "filename": "BS_Filtros_v5_D1.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v5_d1",
          "timeframes": [
            "D1"
          ],
          "sha256": "B5AB92C6390A994C0550788FBB257CFA0158DA8376BEE5ADD80D9C575DC1E3A9",
          "sha256Short": "B5AB92C6390A",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 31,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 28,
              "signals": 3
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "CBlock_DCloseMayorSMA20",
            "CBlock_DCloseMinorSMA20",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "CBlock_DCloseMayorSMA20",
            "CBlock_DCloseMinorSMA20",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "CBlock_DCloseMayorSMA20": {
              "generated": [
                {
                  "key": "#Chart1#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            },
            "CBlock_DCloseMinorSMA20": {
              "generated": [
                {
                  "key": "#Chart1#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v6",
          "filename": "BS_Filtros_v6.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "306EDDFF6F857167D494C74530019C1FA2EABF0144A333B6CDEE06EF50291D52",
          "sha256Short": "306EDDFF6F85",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v6_D1",
          "filename": "BS_Filtros_v6_D1.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v6_d1",
          "timeframes": [
            "D1"
          ],
          "sha256": "B5AB92C6390A994C0550788FBB257CFA0158DA8376BEE5ADD80D9C575DC1E3A9",
          "sha256Short": "B5AB92C6390A",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 31,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 28,
              "signals": 3
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "CBlock_DCloseMayorSMA20",
            "CBlock_DCloseMinorSMA20",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "CBlock_DCloseMayorSMA20",
            "CBlock_DCloseMinorSMA20",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "CBlock_DCloseMayorSMA20": {
              "generated": [
                {
                  "key": "#Chart1#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            },
            "CBlock_DCloseMinorSMA20": {
              "generated": [
                {
                  "key": "#Chart1#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v7_H1",
          "filename": "BS_Filtros_v7_H1.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v7_h1",
          "timeframes": [
            "H1"
          ],
          "sha256": "BBB9FAC0B8174DE15F62B1F0CE89D806B73F64EFFCF4423D85779A3C16D5D360",
          "sha256Short": "BBB9FAC0B817",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v7_H4",
          "filename": "BS_Filtros_v7_H4.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v7_h4",
          "timeframes": [
            "H4"
          ],
          "sha256": "B11EE14CED4B5B006262376CDB738BC2DE2F09F836C6A775A6B9873C7972A9FE",
          "sha256Short": "B11EE14CED4B",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v7_M15",
          "filename": "BS_Filtros_v7_M15.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v7_m15",
          "timeframes": [
            "M15"
          ],
          "sha256": "A5FF1A9E80075F6845DCDE2655B9FAC64E9C2FD8EC768F0ECC8D7E8C80942FC2",
          "sha256Short": "A5FF1A9E8007",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v7_M30",
          "filename": "BS_Filtros_v7_M30.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v7_m30",
          "timeframes": [
            "M30"
          ],
          "sha256": "301882B9E55AD54E5427735898313361771C122BFEE9777C256C9B3D476E3B5A",
          "sha256Short": "301882B9E55A",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Filtros_v7_M5",
          "filename": "BS_Filtros_v7_M5.sqb",
          "family": "filtros",
          "familyLabel": "Filtros operativos",
          "layer": 2,
          "variant": "v7_m5",
          "timeframes": [
            "M5"
          ],
          "sha256": "4834062C9D1541FF8CABB996AA8B2871DD6DDA9087FCF5106D2FEC583A99FAD6",
          "sha256Short": "4834062C9D15",
          "sqxVersion": "141.2225",
          "counts": {
            "blocks": 540,
            "activeBlocks": 21,
            "changedBlocks": 62,
            "categories": {
              "indicators": 100,
              "signals": 383,
              "stopLimitBlocks": 57
            },
            "activeCategories": {
              "indicators": 20,
              "signals": 1
            }
          },
          "activeBlocks": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio"
          ],
          "activeBlockPreview": [
            "AlwaysTrue",
            "Indicators.ADX",
            "Indicators.ATR",
            "Indicators.AvgVolume",
            "Indicators.KaufmanEfficiencyRatio",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "AlwaysTrue": {
              "generated": []
            },
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.KaufmanEfficiencyRatio": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Momentum_v4",
          "filename": "BS_Momentum_v4.sqb",
          "family": "momentum",
          "familyLabel": "Momentum",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "394C66C00CA610EC36C40FF5A1C78C34352AC77A15A1DBA8E397C79307199854",
          "sha256Short": "394C66C00CA6",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 26,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 26
            }
          },
          "activeBlocks": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLowerCount",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreaterCount",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR"
          ],
          "activeBlockPreview": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open"
          ],
          "parameterPreview": {
            "Indicators.AwesomeOscillator": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.CCI": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Momentum": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.OSMA": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#FastEMA#",
                  "name": "Fast EMA",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#SlowEMA#",
                  "name": "Slow EMA",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#SignalPeriod#",
                  "name": "Signal Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.ROC": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.RSI": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Stochastic": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#KPeriod#",
                  "name": "%K Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#DPeriod#",
                  "name": "%D Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Slowing#",
                  "name": "Slowing",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#MAMethod#",
                  "name": "MA Method",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#PriceField#",
                  "name": "Price Field",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.WilliamsPR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Momentum_v6",
          "filename": "BS_Momentum_v6.sqb",
          "family": "momentum",
          "familyLabel": "Momentum",
          "layer": 1,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "774E79AB6273F018FBD1F7DD6FB6CEBD0082983DA2AE2FC223C28DF95FC96ADB",
          "sha256Short": "774E79AB6273",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 26,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 26
            }
          },
          "activeBlocks": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLowerCount",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreaterCount",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR"
          ],
          "activeBlockPreview": [
            "Indicators.AwesomeOscillator",
            "Indicators.CCI",
            "Indicators.Momentum",
            "Indicators.OSMA",
            "Indicators.ROC",
            "Indicators.RSI",
            "Indicators.Stochastic",
            "Indicators.WilliamsPR",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open"
          ],
          "parameterPreview": {
            "Indicators.AwesomeOscillator": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.CCI": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Momentum": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.OSMA": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#FastEMA#",
                  "name": "Fast EMA",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#SlowEMA#",
                  "name": "Slow EMA",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#SignalPeriod#",
                  "name": "Signal Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.ROC": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.RSI": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Stochastic": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#KPeriod#",
                  "name": "%K Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#DPeriod#",
                  "name": "%D Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Slowing#",
                  "name": "Slowing",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#MAMethod#",
                  "name": "MA Method",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#PriceField#",
                  "name": "Price Field",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.WilliamsPR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Regimen_v4",
          "filename": "BS_Regimen_v4.sqb",
          "family": "regimen",
          "familyLabel": "Regimen",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "7D655C44656C2FF7FA6A756E9951318AA06203F6E52B6EDC0E5B718F3676FF41",
          "sha256Short": "7D655C44656C",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 19,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 19
            }
          },
          "activeBlocks": [
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath"
          ],
          "activeBlockPreview": [
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals"
          ],
          "parameterPreview": {
            "Indicators.CSSAMarketRegime": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#HLSumPeriod#",
                  "name": "HL Sum Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#HLPeriod#",
                  "name": "HL Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#AvgPeriod#",
                  "name": "Avg Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#PercRankPeriod#",
                  "name": "Perc Rank Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.EhlersHilbertTransform": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.EntropyMath": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#EMPeriod#",
                  "name": "EM Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Open": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "IsLowerPercentil": {
              "generated": [
                {
                  "key": "#Indicator#",
                  "name": "Indicator",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Bars#",
                  "name": "Bars",
                  "type": "int",
                  "generation": "random",
                  "min": "100",
                  "max": "1000",
                  "step": "100"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Percentile#",
                  "name": "Percentile",
                  "type": "double",
                  "generation": "random",
                  "min": "5",
                  "max": "95",
                  "step": "5"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Regimen_v6",
          "filename": "BS_Regimen_v6.sqb",
          "family": "regimen",
          "familyLabel": "Regimen",
          "layer": 1,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "0589FD1B4FC8CE3D23752BFED77BDF8CA3DADB0E33E3DB62EBCE8820BD6FEA8C",
          "sha256Short": "0589FD1B4FC8",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 22,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 22
            }
          },
          "activeBlocks": [
            "Indicators.ADX",
            "Indicators.ChoppinessIndex",
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath",
            "Indicators.HurstExponent",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "NotEquals",
            "Equals",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ADX",
            "Indicators.ChoppinessIndex",
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath",
            "Indicators.HurstExponent"
          ],
          "activeBlockPreview": [
            "Indicators.ADX",
            "Indicators.ChoppinessIndex",
            "Indicators.CSSAMarketRegime",
            "Indicators.EhlersHilbertTransform",
            "Indicators.EntropyMath",
            "Indicators.HurstExponent",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower"
          ],
          "parameterPreview": {
            "Indicators.ADX": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Input",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ChoppinessIndex": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.CSSAMarketRegime": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#HLSumPeriod#",
                  "name": "HL Sum Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#HLPeriod#",
                  "name": "HL Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#AvgPeriod#",
                  "name": "Avg Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#PercRankPeriod#",
                  "name": "Perc Rank Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.EhlersHilbertTransform": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.EntropyMath": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#EMPeriod#",
                  "name": "EM Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.HurstExponent": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_SoporteResistencia_v4",
          "filename": "BS_SoporteResistencia_v4.sqb",
          "family": "sr",
          "familyLabel": "Soporte/Resistencia",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "D55DFCC3E2CB6F74A56663C0DB4FAD8F4BE6F866DB634E640AC9A7FFAD89FEFA",
          "sha256Short": "D55DFCC3E2CB",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 30,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 30
            }
          },
          "activeBlocks": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising",
            "Not"
          ],
          "activeIndicators": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange"
          ],
          "activeBlockPreview": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low"
          ],
          "parameterPreview": {
            "Indicators.Fractal": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Fractal#",
                  "name": "Fractal",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.Highest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.HighestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Lowest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.LowestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.CloseD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.HighD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_SoporteResistencia_v4_intraday_v5",
          "filename": "BS_SoporteResistencia_v4_intraday_v5.sqb",
          "family": "sr",
          "familyLabel": "Soporte/Resistencia",
          "layer": 1,
          "variant": "v4_intraday_v5",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ],
          "sha256": "4325F5C4D16A9BE0007E64908A34A603372BAD8BCF2AB2C16C40CEFF3EA52B2C",
          "sha256Short": "4325F5C4D16A",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 18,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 18
            }
          },
          "activeBlocks": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising",
            "Not"
          ],
          "activeIndicators": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange"
          ],
          "activeBlockPreview": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater"
          ],
          "parameterPreview": {
            "Indicators.Fractal": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Fractal#",
                  "name": "Fractal",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.Highest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.HighestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Lowest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.LowestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_SoporteResistencia_v6",
          "filename": "BS_SoporteResistencia_v6.sqb",
          "family": "sr",
          "familyLabel": "Soporte/Resistencia",
          "layer": 1,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "9CCC2B2876E3538591A4A16B430F50D1299D5F628DD4D62C450C7DB11F7F79A4",
          "sha256Short": "9CCC2B2876E3",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 32,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 32
            }
          },
          "activeBlocks": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising",
            "Not"
          ],
          "activeIndicators": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange"
          ],
          "activeBlockPreview": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low"
          ],
          "parameterPreview": {
            "Indicators.Fractal": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Fractal#",
                  "name": "Fractal",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.Highest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.HighestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Lowest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.LowestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.CloseD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.HighD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_SoporteResistencia_v6_intraday_v6",
          "filename": "BS_SoporteResistencia_v6_intraday_v6.sqb",
          "family": "sr",
          "familyLabel": "Soporte/Resistencia",
          "layer": 1,
          "variant": "v6_intraday_v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ],
          "sha256": "059314501E430EAF0EB743A8D63D180692D7FA28FB4B017F0AD46179059D32CA",
          "sha256Short": "059314501E43",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 20,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 20
            }
          },
          "activeBlocks": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising",
            "Not"
          ],
          "activeIndicators": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange"
          ],
          "activeBlockPreview": [
            "Indicators.Fractal",
            "Indicators.Highest",
            "Indicators.HighestInRange",
            "Indicators.Lowest",
            "Indicators.LowestInRange",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual"
          ],
          "parameterPreview": {
            "Indicators.Fractal": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Fractal#",
                  "name": "Fractal",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.Highest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.HighestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Lowest": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.LowestInRange": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TimeFrom#",
                  "name": "Time From",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#TimeTo#",
                  "name": "Time To",
                  "type": "int",
                  "generation": "random",
                  "min": "0",
                  "max": "2359",
                  "step": "30"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Tendencia_v4",
          "filename": "BS_Tendencia_v4.sqb",
          "family": "tendencia",
          "familyLabel": "Tendencia",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "9838AC0CB5753CAA5AFB7D584E5D51B0657AD4EAD8485DCAF4FE6530A6E1A4E0",
          "sha256Short": "9838AC0CB575",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 36,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 36
            }
          },
          "activeBlocks": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater",
            "IsGreaterOrEqual",
            "IndicatorCrossesAboveMA",
            "IndicatorCrossesBelowMA",
            "IndicatorBelowMA",
            "IndicatorAboveMA",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku"
          ],
          "activeBlockPreview": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD"
          ],
          "parameterPreview": {
            "Indicators.ATRTrailingStops": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ATRPeriod#",
                  "name": "ATR Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#ATRSmoothigPeriod#",
                  "name": "ATR Smoothig Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#ATRMultiplier#",
                  "name": "ATR Multiplier",
                  "type": "double",
                  "generation": "random",
                  "min": "0.5",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#ATRSmoothingMode#",
                  "name": "ATRSmoothingMode",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Method#",
                  "name": "Method",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.EMA": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.LinearRegression": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.MACD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Fast#",
                  "name": "Fast",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Slow#",
                  "name": "Slow",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Smooth#",
                  "name": "Smooth",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ParabolicSAR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Step#",
                  "name": "Step",
                  "type": "double",
                  "generation": "random",
                  "min": "0.01",
                  "max": "0.04",
                  "step": "0.01"
                },
                {
                  "key": "#Maximum#",
                  "name": "Maximum",
                  "type": "double",
                  "generation": "random",
                  "min": "0.1",
                  "max": "0.4",
                  "step": "0.1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.SMA": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.SuperTrend": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Mode#",
                  "name": "Mode",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#ATRPeriod#",
                  "name": "ATR Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#ATRMult#",
                  "name": "ATR Mult",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Ichimoku": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TenkanPeriod#",
                  "name": "Tenkan",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#KijunPeriod#",
                  "name": "Kijun",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#SenkouPeriod#",
                  "name": "Senkou",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Tendencia_v6",
          "filename": "BS_Tendencia_v6.sqb",
          "family": "tendencia",
          "familyLabel": "Tendencia",
          "layer": 1,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "D51F88B9B2D51194EB5FEA1C39227E7078951F290761E4ABCCB56D6FDC02C387",
          "sha256Short": "D51F88B9B2D5",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 38,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 38
            }
          },
          "activeBlocks": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "IndicatorCrossesAboveMA",
            "IndicatorCrossesBelowMA",
            "IndicatorBelowMA",
            "IndicatorAboveMA",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku"
          ],
          "activeBlockPreview": [
            "Indicators.ATRTrailingStops",
            "Indicators.EMA",
            "Indicators.LinearRegression",
            "Indicators.MACD",
            "Indicators.ParabolicSAR",
            "Indicators.SMA",
            "Indicators.SuperTrend",
            "Indicators.Ichimoku",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD"
          ],
          "parameterPreview": {
            "Indicators.ATRTrailingStops": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ATRPeriod#",
                  "name": "ATR Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#ATRSmoothigPeriod#",
                  "name": "ATR Smoothig Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#ATRMultiplier#",
                  "name": "ATR Multiplier",
                  "type": "double",
                  "generation": "random",
                  "min": "0.5",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#ATRSmoothingMode#",
                  "name": "ATRSmoothingMode",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Method#",
                  "name": "Method",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.EMA": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.LinearRegression": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.MACD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Fast#",
                  "name": "Fast",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Slow#",
                  "name": "Slow",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Smooth#",
                  "name": "Smooth",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.ParabolicSAR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Step#",
                  "name": "Step",
                  "type": "double",
                  "generation": "random",
                  "min": "0.01",
                  "max": "0.04",
                  "step": "0.01"
                },
                {
                  "key": "#Maximum#",
                  "name": "Maximum",
                  "type": "double",
                  "generation": "random",
                  "min": "0.1",
                  "max": "0.4",
                  "step": "0.1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.SMA": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.SuperTrend": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Mode#",
                  "name": "Mode",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#ATRPeriod#",
                  "name": "ATR Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#ATRMult#",
                  "name": "ATR Mult",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.Ichimoku": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#TenkanPeriod#",
                  "name": "Tenkan",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#KijunPeriod#",
                  "name": "Kijun",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#SenkouPeriod#",
                  "name": "Senkou",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volatilidad_v4",
          "filename": "BS_Volatilidad_v4.sqb",
          "family": "volatilidad",
          "familyLabel": "Volatilidad",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "112975F339939FB00BE56420D053A3A8CD840B4824E328A78D8F8E7E407D8815",
          "sha256Short": "112975F33993",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 39,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 39
            }
          },
          "activeBlocks": [
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands",
            "Indicators.VWAPBollingerBands",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands",
            "Indicators.VWAPBollingerBands"
          ],
          "activeBlockPreview": [
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands"
          ],
          "parameterPreview": {
            "Indicators.BollingerBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.DonchianChannels": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.HullMovingAverageATRBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Multiplication#",
                  "name": "Multiplication",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.HullMovingAverageBollingerBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.KeltnerChannel": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.LogATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.MTATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.MTKeltnerChannel": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volatilidad_v4_intraday_v5",
          "filename": "BS_Volatilidad_v4_intraday_v5.sqb",
          "family": "volatilidad",
          "familyLabel": "Volatilidad",
          "layer": 1,
          "variant": "v4_intraday_v5",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ],
          "sha256": "4D52651F0868BA88A6DD53A09043B566024D52FF64B3CB64E77F82E045737AD7",
          "sha256Short": "4D52651F0868",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 28,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 28
            }
          },
          "activeBlocks": [
            "Indicators.ATR",
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands",
            "Indicators.VWAPBollingerBands",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ATR",
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands",
            "Indicators.VWAPBollingerBands"
          ],
          "activeBlockPreview": [
            "Indicators.ATR",
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex"
          ],
          "parameterPreview": {
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.BollingerBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.DonchianChannels": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.HullMovingAverageATRBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Multiplication#",
                  "name": "Multiplication",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.HullMovingAverageBollingerBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.KeltnerChannel": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.LogATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.MTATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volatilidad_v6_intraday_v6",
          "filename": "BS_Volatilidad_v6_intraday_v6.sqb",
          "family": "volatilidad",
          "familyLabel": "Volatilidad",
          "layer": 1,
          "variant": "v6_intraday_v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ],
          "sha256": "63EEAE27584F67CADCB59F4548648F5048CE43EBA2B220B8F60B7BDF2B08AE61",
          "sha256Short": "63EEAE27584F",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 28,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 28
            }
          },
          "activeBlocks": [
            "Indicators.ATR",
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands",
            "Indicators.VWAPBollingerBands",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.ATR",
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex",
            "Indicators.VWAPATRBands",
            "Indicators.VWAPBollingerBands"
          ],
          "activeBlockPreview": [
            "Indicators.ATR",
            "Indicators.BollingerBands",
            "Indicators.DonchianChannels",
            "Indicators.HullMovingAverageATRBands",
            "Indicators.HullMovingAverageBollingerBands",
            "Indicators.KeltnerChannel",
            "Indicators.LogATR",
            "Indicators.MTATR",
            "Indicators.MTKeltnerChannel",
            "Indicators.StdDev",
            "Indicators.TrueRange",
            "Indicators.UlcerIndex"
          ],
          "parameterPreview": {
            "Indicators.ATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.BollingerBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.DonchianChannels": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.HullMovingAverageATRBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Multiplication#",
                  "name": "Multiplication",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "5.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.HullMovingAverageBollingerBands": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#ComputedFrom#",
                  "name": "Computed From",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.KeltnerChannel": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Deviation#",
                  "name": "Deviation",
                  "type": "double",
                  "generation": "random",
                  "min": "1.0",
                  "max": "3.0",
                  "step": "0.5"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Line#",
                  "name": "Line",
                  "type": "int",
                  "generation": "random",
                  "min": null,
                  "max": null,
                  "step": null
                }
              ]
            },
            "Indicators.LogATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.MTATR": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volumen_v4",
          "filename": "BS_Volumen_v4.sqb",
          "family": "volumen",
          "familyLabel": "Volumen",
          "layer": 1,
          "variant": "v4",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "8425FE9589BCF2E67E63C9710E886BB0223D5A698E85B238B53C190384210C78",
          "sha256Short": "8425FE9589BC",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 25,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 25
            }
          },
          "activeBlocks": [
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.VWAP"
          ],
          "activeBlockPreview": [
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM"
          ],
          "parameterPreview": {
            "Indicators.VWAP": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#VWAPPeriod#",
                  "name": "VWAP Period",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000003",
                  "max": "-1000004",
                  "step": "1"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.CloseD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.HighD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.LowD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.OpenD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volumen_v4_intraday_v5",
          "filename": "BS_Volumen_v4_intraday_v5.sqb",
          "family": "volumen",
          "familyLabel": "Volumen",
          "layer": 1,
          "variant": "v4_intraday_v5",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ],
          "sha256": "6F432A092DD0509EA75D668FF8DEEA1F159A0CADC5DEF1E77C45FD5493068CFA",
          "sha256Short": "6F432A092DD0",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 14,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 14
            }
          },
          "activeBlocks": [
            "Indicators.AvgVolume",
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.AvgVolume",
            "Indicators.VWAP"
          ],
          "activeBlockPreview": [
            "Indicators.AvgVolume",
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow"
          ],
          "parameterPreview": {
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.VWAP": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#VWAPPeriod#",
                  "name": "VWAP Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Open": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "IsLower": {
              "generated": [
                {
                  "key": "#Left#",
                  "name": "Left",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Right#",
                  "name": "Right",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            },
            "IsLowerOrEqual": {
              "generated": [
                {
                  "key": "#Left#",
                  "name": "Left",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Right#",
                  "name": "Right",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volumen_v6",
          "filename": "BS_Volumen_v6.sqb",
          "family": "volumen",
          "familyLabel": "Volumen",
          "layer": 1,
          "variant": "v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ],
          "sha256": "CA74EB9004408F4AA2533D33DD7F557A28BB6C9C387C45EABC7D1E76ADD553C5",
          "sha256Short": "CA74EB900440",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 28,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 28
            }
          },
          "activeBlocks": [
            "Indicators.AvgVolume",
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM",
            "Prices.OpenM",
            "Prices.Open",
            "Prices.CloseW",
            "Prices.HighW",
            "Prices.LowW",
            "Prices.OpenW",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.AvgVolume",
            "Indicators.VWAP"
          ],
          "activeBlockPreview": [
            "Indicators.AvgVolume",
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.CloseD",
            "Prices.HighD",
            "Prices.LowD",
            "Prices.OpenD",
            "Prices.High",
            "Prices.Low",
            "Prices.CloseM",
            "Prices.HighM",
            "Prices.LowM"
          ],
          "parameterPreview": {
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.VWAP": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#VWAPPeriod#",
                  "name": "VWAP Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.CloseD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.HighD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.LowD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.OpenD": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            }
          }
        },
        {
          "canonicalId": "BS_Volumen_v6_intraday_v6",
          "filename": "BS_Volumen_v6_intraday_v6.sqb",
          "family": "volumen",
          "familyLabel": "Volumen",
          "layer": 1,
          "variant": "v6_intraday_v6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ],
          "sha256": "9CC8A6D14E8A1DD0FEFFA99F358732D269907281B5C9CA18AF77A3806042DB92",
          "sha256Short": "9CC8A6D14E8A",
          "sqxVersion": "142.2336",
          "counts": {
            "blocks": 749,
            "activeBlocks": 16,
            "changedBlocks": 76,
            "categories": {
              "indicators": 124,
              "signals": 553,
              "stopLimitBlocks": 72
            },
            "activeCategories": {
              "indicators": 16
            }
          },
          "activeBlocks": [
            "Indicators.AvgVolume",
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual",
            "CrossesAbove",
            "CrossesBelow",
            "IsFalling",
            "IsRising"
          ],
          "activeIndicators": [
            "Indicators.AvgVolume",
            "Indicators.VWAP"
          ],
          "activeBlockPreview": [
            "Indicators.AvgVolume",
            "Indicators.VWAP",
            "Prices.Close",
            "Prices.High",
            "Prices.Low",
            "Prices.Open",
            "IsLowerPercentil",
            "IsLower",
            "IsLowerOrEqual",
            "IsGreaterPercentil",
            "IsGreater",
            "IsGreaterOrEqual"
          ],
          "parameterPreview": {
            "Indicators.AvgVolume": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Period#",
                  "name": "Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Indicators.VWAP": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#VWAPPeriod#",
                  "name": "VWAP Period",
                  "type": "int",
                  "generation": "random",
                  "min": "10",
                  "max": "200",
                  "step": "10"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Close": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.High": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Low": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "Prices.Open": {
              "generated": [
                {
                  "key": "#Chart#",
                  "name": "Chart",
                  "type": "data",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                }
              ]
            },
            "IsLowerPercentil": {
              "generated": [
                {
                  "key": "#Indicator#",
                  "name": "Indicator",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Bars#",
                  "name": "Bars",
                  "type": "int",
                  "generation": "random",
                  "min": "100",
                  "max": "1000",
                  "step": "100"
                },
                {
                  "key": "#Shift#",
                  "name": "Shift",
                  "type": "int",
                  "generation": "random",
                  "min": "-1000001",
                  "max": "-1000002",
                  "step": "1"
                },
                {
                  "key": "#Percentile#",
                  "name": "Percentile",
                  "type": "double",
                  "generation": "random",
                  "min": "5",
                  "max": "95",
                  "step": "5"
                }
              ]
            },
            "IsLower": {
              "generated": [
                {
                  "key": "#Left#",
                  "name": "Left",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                },
                {
                  "key": "#Right#",
                  "name": "Right",
                  "type": "value",
                  "generation": "random",
                  "min": "null",
                  "max": "null",
                  "step": "null"
                }
              ]
            }
          }
        }
      ],
      "aliases": {
        "BS_Tendencia": "BS_Tendencia_v6",
        "BS_Momentum": "BS_Momentum_v6",
        "BS_Volatilidad": "BS_Volatilidad_v4",
        "BS_Regimen": "BS_Regimen_v6",
        "BS_Volumen": "BS_Volumen_v6",
        "BS_SoporteResistencia": "BS_SoporteResistencia_v6",
        "BS_Estadistico": "BS_Estadistico_v6",
        "BS_Filtros": "BS_Filtros_v6",
        "BS_Filtros_v5": "BS_Filtros_v5_D1",
        "BS_Filtros_v6_D1": "BS_Filtros_v6_D1",
        "BS_Filtros_v6": "BS_Filtros_v6",
        "BS_Filtros_v7": "BS_Filtros_v7_H1",
        "BS_Estadistico_v4": "BS_Estadistico_v4",
        "BS_Estadistico_v6": "BS_Estadistico_v6",
        "BS_Filtros_v4": "BS_Filtros_v4",
        "BS_Filtros_v5_D1": "BS_Filtros_v5_D1",
        "BS_Filtros_v7_H1": "BS_Filtros_v7_H1",
        "BS_Filtros_v7_H4": "BS_Filtros_v7_H4",
        "BS_Filtros_v7_M15": "BS_Filtros_v7_M15",
        "BS_Filtros_v7_M30": "BS_Filtros_v7_M30",
        "BS_Filtros_v7_M5": "BS_Filtros_v7_M5",
        "BS_Momentum_v4": "BS_Momentum_v4",
        "BS_Momentum_v6": "BS_Momentum_v6",
        "BS_Regimen_v4": "BS_Regimen_v4",
        "BS_Regimen_v6": "BS_Regimen_v6",
        "BS_SoporteResistencia_v4": "BS_SoporteResistencia_v4",
        "BS_SoporteResistencia_v4_intraday_v5": "BS_SoporteResistencia_v4_intraday_v5",
        "BS_SoporteResistencia_v6": "BS_SoporteResistencia_v6",
        "BS_SoporteResistencia_v6_intraday_v6": "BS_SoporteResistencia_v6_intraday_v6",
        "BS_Tendencia_v4": "BS_Tendencia_v4",
        "BS_Tendencia_v6": "BS_Tendencia_v6",
        "BS_Volatilidad_v4": "BS_Volatilidad_v4",
        "BS_Volatilidad_v4_intraday_v5": "BS_Volatilidad_v4_intraday_v5",
        "BS_Volatilidad_v6_intraday_v6": "BS_Volatilidad_v6_intraday_v6",
        "BS_Volumen_v4": "BS_Volumen_v4",
        "BS_Volumen_v4_intraday_v5": "BS_Volumen_v4_intraday_v5",
        "BS_Volumen_v6": "BS_Volumen_v6",
        "BS_Volumen_v6_intraday_v6": "BS_Volumen_v6_intraday_v6",
        "BS_Estadistico_v4.sqb": "BS_Estadistico_v4",
        "BS_Estadistico_v6.sqb": "BS_Estadistico_v6",
        "BS_Filtros_v4.sqb": "BS_Filtros_v4",
        "BS_Filtros_v5_D1.sqb": "BS_Filtros_v5_D1",
        "BS_Filtros_v6.sqb": "BS_Filtros_v6",
        "BS_Filtros_v6_D1.sqb": "BS_Filtros_v6_D1",
        "BS_Filtros_v7_H1.sqb": "BS_Filtros_v7_H1",
        "BS_Filtros_v7_H4.sqb": "BS_Filtros_v7_H4",
        "BS_Filtros_v7_M15.sqb": "BS_Filtros_v7_M15",
        "BS_Filtros_v7_M30.sqb": "BS_Filtros_v7_M30",
        "BS_Filtros_v7_M5.sqb": "BS_Filtros_v7_M5",
        "BS_Momentum_v4.sqb": "BS_Momentum_v4",
        "BS_Momentum_v6.sqb": "BS_Momentum_v6",
        "BS_Regimen_v4.sqb": "BS_Regimen_v4",
        "BS_Regimen_v6.sqb": "BS_Regimen_v6",
        "BS_SoporteResistencia_v4.sqb": "BS_SoporteResistencia_v4",
        "BS_SoporteResistencia_v4_intraday_v5.sqb": "BS_SoporteResistencia_v4_intraday_v5",
        "BS_SoporteResistencia_v6.sqb": "BS_SoporteResistencia_v6",
        "BS_SoporteResistencia_v6_intraday_v6.sqb": "BS_SoporteResistencia_v6_intraday_v6",
        "BS_Tendencia_v4.sqb": "BS_Tendencia_v4",
        "BS_Tendencia_v6.sqb": "BS_Tendencia_v6",
        "BS_Volatilidad_v4.sqb": "BS_Volatilidad_v4",
        "BS_Volatilidad_v4_intraday_v5.sqb": "BS_Volatilidad_v4_intraday_v5",
        "BS_Volatilidad_v6_intraday_v6.sqb": "BS_Volatilidad_v6_intraday_v6",
        "BS_Volumen_v4.sqb": "BS_Volumen_v4",
        "BS_Volumen_v4_intraday_v5.sqb": "BS_Volumen_v4_intraday_v5",
        "BS_Volumen_v6.sqb": "BS_Volumen_v6",
        "BS_Volumen_v6_intraday_v6.sqb": "BS_Volumen_v6_intraday_v6"
      },
      "capa1Options": [
        {
          "value": "BS_Tendencia_v6",
          "label": "BS_Tendencia_v6",
          "family": "tendencia",
          "variant": "v6",
          "sha256Short": "D51F88B9B2D5",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Tendencia_v4",
          "label": "BS_Tendencia_v4",
          "family": "tendencia",
          "variant": "v4",
          "sha256Short": "9838AC0CB575",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Momentum_v6",
          "label": "BS_Momentum_v6",
          "family": "momentum",
          "variant": "v6",
          "sha256Short": "774E79AB6273",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Momentum_v4",
          "label": "BS_Momentum_v4",
          "family": "momentum",
          "variant": "v4",
          "sha256Short": "394C66C00CA6",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Volatilidad_v4",
          "label": "BS_Volatilidad_v4",
          "family": "volatilidad",
          "variant": "v4",
          "sha256Short": "112975F33993",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Volatilidad_v4_intraday_v5",
          "label": "BS_Volatilidad_v4_intraday_v5",
          "family": "volatilidad",
          "variant": "v4_intraday_v5",
          "sha256Short": "4D52651F0868",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ]
        },
        {
          "value": "BS_Volatilidad_v6_intraday_v6",
          "label": "BS_Volatilidad_v6_intraday_v6",
          "family": "volatilidad",
          "variant": "v6_intraday_v6",
          "sha256Short": "63EEAE27584F",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ]
        },
        {
          "value": "BS_Regimen_v6",
          "label": "BS_Regimen_v6",
          "family": "regimen",
          "variant": "v6",
          "sha256Short": "0589FD1B4FC8",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Regimen_v4",
          "label": "BS_Regimen_v4",
          "family": "regimen",
          "variant": "v4",
          "sha256Short": "7D655C44656C",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Volumen_v6",
          "label": "BS_Volumen_v6",
          "family": "volumen",
          "variant": "v6",
          "sha256Short": "CA74EB900440",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Volumen_v4",
          "label": "BS_Volumen_v4",
          "family": "volumen",
          "variant": "v4",
          "sha256Short": "8425FE9589BC",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Volumen_v4_intraday_v5",
          "label": "BS_Volumen_v4_intraday_v5",
          "family": "volumen",
          "variant": "v4_intraday_v5",
          "sha256Short": "6F432A092DD0",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ]
        },
        {
          "value": "BS_Volumen_v6_intraday_v6",
          "label": "BS_Volumen_v6_intraday_v6",
          "family": "volumen",
          "variant": "v6_intraday_v6",
          "sha256Short": "9CC8A6D14E8A",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ]
        },
        {
          "value": "BS_SoporteResistencia_v6",
          "label": "BS_SoporteResistencia_v6",
          "family": "sr",
          "variant": "v6",
          "sha256Short": "9CCC2B2876E3",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_SoporteResistencia_v4",
          "label": "BS_SoporteResistencia_v4",
          "family": "sr",
          "variant": "v4",
          "sha256Short": "D55DFCC3E2CB",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_SoporteResistencia_v4_intraday_v5",
          "label": "BS_SoporteResistencia_v4_intraday_v5",
          "family": "sr",
          "variant": "v4_intraday_v5",
          "sha256Short": "4325F5C4D16A",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ]
        },
        {
          "value": "BS_SoporteResistencia_v6_intraday_v6",
          "label": "BS_SoporteResistencia_v6_intraday_v6",
          "family": "sr",
          "variant": "v6_intraday_v6",
          "sha256Short": "059314501E43",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1"
          ]
        },
        {
          "value": "BS_Estadistico_v6",
          "label": "BS_Estadistico_v6",
          "family": "estadistico",
          "variant": "v6",
          "sha256Short": "12218A93C737",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Estadistico_v4",
          "label": "BS_Estadistico_v4",
          "family": "estadistico",
          "variant": "v4",
          "sha256Short": "812A906949CA",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        }
      ],
      "capa2Options": [
        {
          "value": "BS_Filtros_v4",
          "label": "BS_Filtros_v4",
          "family": "filtros",
          "variant": "v4",
          "sha256Short": "EAED2430BB0A",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Filtros_v5_D1",
          "label": "BS_Filtros_v5_D1",
          "family": "filtros",
          "variant": "v5_d1",
          "sha256Short": "B5AB92C6390A",
          "timeframes": [
            "D1"
          ]
        },
        {
          "value": "BS_Filtros_v6",
          "label": "BS_Filtros_v6",
          "family": "filtros",
          "variant": "v6",
          "sha256Short": "306EDDFF6F85",
          "timeframes": [
            "M5",
            "M15",
            "M30",
            "H1",
            "H4",
            "D1"
          ]
        },
        {
          "value": "BS_Filtros_v6_D1",
          "label": "BS_Filtros_v6_D1",
          "family": "filtros",
          "variant": "v6_d1",
          "sha256Short": "B5AB92C6390A",
          "timeframes": [
            "D1"
          ]
        },
        {
          "value": "BS_Filtros_v7_H1",
          "label": "BS_Filtros_v7_H1",
          "family": "filtros",
          "variant": "v7_h1",
          "sha256Short": "BBB9FAC0B817",
          "timeframes": [
            "H1"
          ]
        },
        {
          "value": "BS_Filtros_v7_H4",
          "label": "BS_Filtros_v7_H4",
          "family": "filtros",
          "variant": "v7_h4",
          "sha256Short": "B11EE14CED4B",
          "timeframes": [
            "H4"
          ]
        },
        {
          "value": "BS_Filtros_v7_M15",
          "label": "BS_Filtros_v7_M15",
          "family": "filtros",
          "variant": "v7_m15",
          "sha256Short": "A5FF1A9E8007",
          "timeframes": [
            "M15"
          ]
        },
        {
          "value": "BS_Filtros_v7_M30",
          "label": "BS_Filtros_v7_M30",
          "family": "filtros",
          "variant": "v7_m30",
          "sha256Short": "301882B9E55A",
          "timeframes": [
            "M30"
          ]
        },
        {
          "value": "BS_Filtros_v7_M5",
          "label": "BS_Filtros_v7_M5",
          "family": "filtros",
          "variant": "v7_m5",
          "sha256Short": "4834062C9D15",
          "timeframes": [
            "M5"
          ]
        }
      ]
    },
    "capa1Resolver": {
      "intradayTimeframes": [
        "M5",
        "M15",
        "M30",
        "H1"
      ],
      "families": {
        "tendencia": {
          "default": "BS_Tendencia_v6"
        },
        "momentum": {
          "default": "BS_Momentum_v6"
        },
        "volatilidad": {
          "default": "BS_Volatilidad_v4",
          "intraday": "BS_Volatilidad_v6_intraday_v6"
        },
        "regimen": {
          "default": "BS_Regimen_v6"
        },
        "volumen": {
          "default": "BS_Volumen_v6",
          "intraday": "BS_Volumen_v6_intraday_v6"
        },
        "sr": {
          "default": "BS_SoporteResistencia_v6",
          "intraday": "BS_SoporteResistencia_v6_intraday_v6"
        },
        "estadistico": {
          "default": "BS_Estadistico_v6"
        }
      }
    },
    "capa2Recommendations": {
      "manual": true,
      "recommendations": {
        "M5": "BS_Filtros_v6",
        "M15": "BS_Filtros_v6",
        "M30": "BS_Filtros_v6",
        "H1": "BS_Filtros_v6",
        "H4": "BS_Filtros_v6",
        "D1": "BS_Filtros_v6_D1",
        "fallback": "BS_Filtros_v6"
      }
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
        "kid": "sqx-tester-2026-05-v1",
        "alg": "RS256",
        "n": "6VcVwszmZim-p_tumiPvN-M1qoqLPgj8dT8eroA5m8p04e2DjWeAaALdvj_M6BQnWZtIZi5OKo4hWj2CBpAHjySDdZChApeF3vz54UPkhOghIH8JlhiTzrthlLC2sN8NyfUuLLVZT5JYCwrxcLcnRt4_012iATlEHbusuxLuHDEPGTsXzlCE9yjD9csMV3tDv6tOWA5Kr9C9rII6NhKY-s4esRm9QN8W1oY00X9Q-XSO9R_AZGgypp812gAuj27zAV_ro824Du2ir7CzN6tVlZS4SD1ClmOKBUtj16n102UJl4c6nd6APh08e6yugIPJbnoiTxegme91yYjv2oOBjQ",
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
        "analysis_output",
        "node_modules",
        "venv",
        ".git",
        ".next",
        ".open-next",
        ".vercel",
        ".wrangler",
        ".local",
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
        "backend/sqx-edge-tool/data/customer_success_renewal",
        "backend/sqx-edge-tool/data/customer_cockpit",
        "backend/sqx-edge-tool/data/pro_buyer_pack",
        "backend/sqx-edge-tool/data/buyer_onboarding_support_gate",
        "backend/sqx-edge-tool/data/template_pack_1_delivery",
        "backend/sqx-edge-tool/data/template_pack_1_offer",
        "backend/sqx-edge-tool/data/template_pack_1_publication",
        "backend/sqx-edge-tool/data/template_pack_1_purchase_drill",
        "backend/sqx-edge-tool/data/template_pack_1_handoff",
        "backend/sqx-edge-tool/data/template_pack_1_sales_register",
        "backend/sqx-edge-tool/data/template_pack_1_feedback_cohort",
        "backend/sqx-edge-tool/data/template_pack_1_action_plan",
        "backend/sqx-edge-tool/data/template_pack_2_specs",
        "backend/sqx-edge-tool/data/template_pack_2_assets",
        "backend/sqx-edge-tool/data/template_pack_2_offer_pack",
        "backend/sqx-edge-tool/data/template_pack_2_publication",
        "backend/sqx-edge-tool/data/template_pack_2_purchase_drill",
        "backend/sqx-edge-tool/data/template_pack_2_handoff",
        "backend/sqx-edge-tool/data/template_pack_2_sales_register",
        "backend/sqx-edge-tool/data/template_pack_2_feedback_cohort",
        "backend/sqx-edge-tool/data/buyer_ready_checkout_closeout",
        "backend/sqx-edge-tool/data/public_buyer_page_cadence",
        "backend/sqx-edge-tool/data/first_controlled_buyer_log",
        "backend/sqx-edge-tool/data/post_sale_improvement_loop",
        "backend/sqx-edge-tool/data/post_sale_micro_updates",
        "backend/sqx-edge-tool/data/next_controlled_buyer_readiness",
        "backend/sqx-edge-tool/data/next_controlled_buyer_outcome",
        "backend/sqx-edge-tool/data/controlled_distribution_step",
        "backend/sqx-edge-tool/data/controlled_distribution_review",
        "backend/sqx-edge-tool/data/next_buyer_facing_asset",
        "backend/sqx-edge-tool/data/private_asset_review",
        "resources/pro-template-pack-1",
        "resources/pro-template-pack-2",
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
        "backend/sqx-edge-tool/tools/pro_buyer_pack.py",
        "backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py",
        "backend/sqx-edge-tool/tools/template_pack_1_delivery.py",
        "backend/sqx-edge-tool/tools/template_pack_1_offer.py",
        "backend/sqx-edge-tool/tools/template_pack_1_publication.py",
        "backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py",
        "backend/sqx-edge-tool/tools/template_pack_1_handoff.py",
        "backend/sqx-edge-tool/tools/template_pack_1_sales_register.py",
        "backend/sqx-edge-tool/tools/template_pack_1_feedback_cohort.py",
        "backend/sqx-edge-tool/tools/template_pack_1_action_plan.py",
        "backend/sqx-edge-tool/tools/template_pack_2_specs.py",
        "backend/sqx-edge-tool/tools/template_pack_2_assets.py",
        "backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py",
        "backend/sqx-edge-tool/tools/template_pack_2_publication.py",
        "backend/sqx-edge-tool/tools/template_pack_2_purchase_drill.py",
        "backend/sqx-edge-tool/tools/template_pack_2_handoff.py",
        "backend/sqx-edge-tool/tools/template_pack_2_sales_register.py",
        "backend/sqx-edge-tool/tools/template_pack_2_feedback_cohort.py",
        "backend/sqx-edge-tool/tools/buyer_ready_checkout_closeout.py",
        "backend/sqx-edge-tool/tools/public_buyer_page_cadence.py",
        "backend/sqx-edge-tool/tools/first_controlled_buyer_log.py",
        "backend/sqx-edge-tool/tools/post_sale_improvement_loop.py",
        "backend/sqx-edge-tool/tools/post_sale_micro_updates.py",
        "backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py",
        "backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py",
        "backend/sqx-edge-tool/tools/controlled_distribution_step.py",
        "backend/sqx-edge-tool/tools/controlled_distribution_review.py",
        "backend/sqx-edge-tool/tools/next_buyer_facing_asset.py",
        "backend/sqx-edge-tool/tools/private_asset_review.py",
        "backend/sqx-edge-tool/tools/private_commercial_split.py",
        "backend/sqx-edge-tool/tools/fulfillment_request.py",
        "backend/sqx-edge-tool/tools/fulfill_from_request.ps1",
        "backend/sqx-edge-tool/tools/relay_bundle.py",
        "backend/sqx-edge-tool/tools/dukas_mt5_ohlc_download.py",
        "backend/sqx-edge-tool/tools/mt5_ipc_diagnostic.py",
        "backend/sqx-edge-tool/config/dukas_mt5_download.json",
        "data/ohlc",
        "analysis_output/dukas_mt5_download",
        "analysis_output/mt5_ipc_diagnostic",
        "analysis_output/real_mtf_pipeline_run",
        "backend/sqx-edge-tool/data/controlled_publication_gate",
        "backend/sqx-edge-tool/tools/controlled_publication_gate.py",
        "backend/sqx-edge-tool/data/limited_publication_draft",
        "backend/sqx-edge-tool/tools/limited_publication_draft.py",
        "backend/sqx-edge-tool/data/operator_publication_review",
        "backend/sqx-edge-tool/tools/operator_publication_review.py",
        "backend/sqx-edge-tool/data/manual_limited_publication_record",
        "backend/sqx-edge-tool/tools/manual_limited_publication_record.py",
        "backend/sqx-edge-tool/data/manual_publication_monitor",
        "backend/sqx-edge-tool/tools/manual_publication_monitor.py",
        "backend/sqx-edge-tool/data/controlled_traffic_expansion_review",
        "backend/sqx-edge-tool/tools/controlled_traffic_expansion_review.py",
        "backend/sqx-edge-tool/data/controlled_traffic_expansion_step",
        "backend/sqx-edge-tool/tools/controlled_traffic_expansion_step.py",
        "backend/sqx-edge-tool/data/controlled_traffic_expansion_monitor",
        "backend/sqx-edge-tool/tools/controlled_traffic_expansion_monitor.py",
        "backend/sqx-edge-tool/data/controlled_traffic_expansion_decision",
        "backend/sqx-edge-tool/tools/controlled_traffic_expansion_decision.py",
        "backend/sqx-edge-tool/data/controlled_traffic_expansion_execution",
        "backend/sqx-edge-tool/tools/controlled_traffic_expansion_execution.py",
        "backend/sqx-edge-tool/data/controlled_traffic_expansion_execution_monitor",
        "backend/sqx-edge-tool/tools/controlled_traffic_expansion_execution_monitor.py",
        "backend/sqx-edge-tool/data/controlled_commercial_next_movement",
        "backend/sqx-edge-tool/tools/controlled_commercial_next_movement.py",
        "backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution",
        "backend/sqx-edge-tool/tools/controlled_commercial_next_movement_execution.py",
        "backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution_monitor",
        "backend/sqx-edge-tool/tools/controlled_commercial_next_movement_execution_monitor.py",
        "backend/sqx-edge-tool/data/next_controlled_commercial_movement_decision",
        "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_decision.py",
        "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution",
        "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_execution.py",
        "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution_monitor",
        "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_execution_monitor.py",
        "backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m92_decision",
        "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m92_decision.py",
        "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution",
        "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m93_execution.py",
        "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution_monitor",
        "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m93_execution_monitor.py",
        "backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m95_decision",
        "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m95_decision.py",
        "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution",
        "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution.py",
        "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution_monitor",
        "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py",
        "backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m98_decision",
        "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m98_decision.py"
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
      "view_creator.core": {
        "label": "SQX View Creator EGT Core",
        "tier": "free"
      },
      "view_creator.full": {
        "label": "SQX View Creator completo",
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
          "strategy_cleaner.preview",
          "view_creator.core"
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
          "view_creator.core",
          "view_creator.full",
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
        },
        {
          "id": "template_pack_1",
          "label": "Template Pack 1",
          "price": "49 EUR",
          "checkoutUrl": ""
        },
        {
          "id": "template_pack_2",
          "label": "Template Pack 2",
          "price": "79 EUR",
          "checkoutUrl": ""
        }
      ],
      "disclaimer": "No promete rentabilidad ni resultados financieros. La propuesta es productividad, orden y reduccion de errores operativos.",
      "checkoutProvider": "Lemon Squeezy",
      "checkoutLabel": "Comprar Pro",
      "checkoutUrl": "",
      "checkout": {
        "status": "next_controlled_commercial_movement_from_m98_decision_ready",
        "primaryProvider": "Lemon Squeezy",
        "fallbackProvider": "Gumroad",
        "mode": "hosted_checkout",
        "primaryUrl": "",
        "fallbackUrl": "",
        "supportEmail": "",
        "fulfillmentMode": "manual_signed_license",
        "deliveryArtifact": "SQX_Edge_Tool_Portable_*.zip",
        "verifiedReleaseCandidate": {
          "phase": "R47",
          "status": "controlled_commercial_candidate_ready",
          "portableZip": "dist/SQX_Edge_Tool_Portable_20260509_102131.zip",
          "sha256": "18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D",
          "tagDraft": "v0.2.0-r47",
          "publicationPlan": "docs/R47_CONTROLLED_COMMERCIAL_RELEASE.md",
          "publishPolicy": "manual_github_release_only_after_public_release_gate_go"
        },
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
        "customerCockpitEndpoint": "/api/customer-cockpit",
        "customerCockpitConfig": "backend/sqx-edge-tool/config/customer_cockpit.json",
        "customerCockpitPolicy": "render_redacted_operator_summary_without_license_payloads_or_raw_events",
        "proBuyerPackConfig": "backend/sqx-edge-tool/config/pro_buyer_pack.json",
        "proBuyerPackResourceDir": "resources/pro-buyer-pack",
        "proBuyerPackValidationTool": "backend/sqx-edge-tool/tools/pro_buyer_pack.py",
        "proBuyerPackPolicy": "ship_safe_buyer_material_without_license_payloads_private_keys_or_financial_promises",
        "buyerOnboardingSupportGateConfig": "backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json",
        "buyerOnboardingResourceDir": "resources/pro-buyer-pack/onboarding",
        "buyerOnboardingSupportGateTool": "backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py",
        "buyerOnboardingSupportGateEvidenceDir": "backend/sqx-edge-tool/data/buyer_onboarding_support_gate",
        "buyerOnboardingSupportGatePolicy": "confirm_purchase_zip_license_start_here_faq_support_and_safe_claims_before_handoff",
        "templatePack1Config": "backend/sqx-edge-tool/config/template_pack_1.json",
        "templatePack1ResourceDir": "resources/pro-template-pack-1",
        "templatePack1DeliveryTool": "backend/sqx-edge-tool/tools/template_pack_1_delivery.py",
        "templatePack1EvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_delivery",
        "templatePack1Policy": "deliver_as_separate_addon_zip_after_buyer_onboarding_gate_and_safe_claims_review",
        "templatePack1OfferConfig": "backend/sqx-edge-tool/config/template_pack_1_offer.json",
        "templatePack1OfferResourceDir": "resources/pro-template-pack-1/offer",
        "templatePack1OfferTool": "backend/sqx-edge-tool/tools/template_pack_1_offer.py",
        "templatePack1OfferEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_offer",
        "templatePack1OfferPolicy": "prepare_public_addon_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout",
        "templatePack1PublicationConfig": "backend/sqx-edge-tool/config/template_pack_1_publication.json",
        "templatePack1PublicationTool": "backend/sqx-edge-tool/tools/template_pack_1_publication.py",
        "templatePack1PublicationEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_publication",
        "templatePack1PublicationPolicy": "require_real_checkout_url_variant_support_email_and_rollback_before_controlled_publication",
        "templatePack1PurchaseDrillConfig": "backend/sqx-edge-tool/config/template_pack_1_purchase_drill.json",
        "templatePack1PurchaseDrillTool": "backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py",
        "templatePack1PurchaseDrillEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_purchase_drill",
        "templatePack1PurchaseDrillPolicy": "record_controlled_addon_order_payment_delivery_support_and_refund_pause_before_scaling",
        "templatePack1HandoffConfig": "backend/sqx-edge-tool/config/template_pack_1_handoff.json",
        "templatePack1HandoffTool": "backend/sqx-edge-tool/tools/template_pack_1_handoff.py",
        "templatePack1HandoffEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_handoff",
        "templatePack1HandoffPolicy": "confirm_delivery_support_first_value_and_scale_or_pause_decision_after_controlled_purchase",
        "templatePack1SalesRegisterConfig": "backend/sqx-edge-tool/config/template_pack_1_sales_register.json",
        "templatePack1SalesRegisterTool": "backend/sqx-edge-tool/tools/template_pack_1_sales_register.py",
        "templatePack1SalesRegisterEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_sales_register",
        "templatePack1SalesRegisterPolicy": "track_redacted_addon_sales_delivery_support_refunds_and_scale_decision_before_more_traffic",
        "templatePack1FeedbackCohortConfig": "backend/sqx-edge-tool/config/template_pack_1_feedback_cohort.json",
        "templatePack1FeedbackCohortTool": "backend/sqx-edge-tool/tools/template_pack_1_feedback_cohort.py",
        "templatePack1FeedbackCohortEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_feedback_cohort",
        "templatePack1FeedbackCohortPolicy": "review_redacted_buyer_feedback_support_refunds_and_positive_signals_before_scaling_or_template_pack_2",
        "templatePack1ActionPlanConfig": "backend/sqx-edge-tool/config/template_pack_1_action_plan.json",
        "templatePack1ActionPlanTool": "backend/sqx-edge-tool/tools/template_pack_1_action_plan.py",
        "templatePack1ActionPlanEvidenceDir": "backend/sqx-edge-tool/data/template_pack_1_action_plan",
        "templatePack1ActionPlanPolicy": "convert_feedback_cohort_into_owner_priority_support_claims_distribution_and_next_phase_actions",
        "templatePack2SpecsConfig": "backend/sqx-edge-tool/config/template_pack_2_specs.json",
        "templatePack2SpecsTool": "backend/sqx-edge-tool/tools/template_pack_2_specs.py",
        "templatePack2SpecsEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_specs",
        "templatePack2SpecsPolicy": "define_pack_2_scope_assets_presets_support_delivery_and_next_phase_before_building_resources",
        "templatePack2AssetsConfig": "backend/sqx-edge-tool/config/template_pack_2_assets.json",
        "templatePack2ResourceDir": "resources/pro-template-pack-2",
        "templatePack2AssetsTool": "backend/sqx-edge-tool/tools/template_pack_2_assets.py",
        "templatePack2AssetsEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_assets",
        "templatePack2AssetsPolicy": "deliver_initial_pack_2_assets_as_separate_addon_zip_after_specs_gate_and_safe_claims_review",
        "templatePack2OfferPackConfig": "backend/sqx-edge-tool/config/template_pack_2_offer_pack.json",
        "templatePack2OfferPackResourceDir": "resources/pro-template-pack-2/offer",
        "templatePack2OfferPackTool": "backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py",
        "templatePack2OfferPackEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_offer_pack",
        "templatePack2OfferPackPolicy": "prepare_pack_2_offer_copy_faq_checkout_draft_delivery_macro_and_support_macro_before_live_checkout",
        "templatePack2PublicationConfig": "backend/sqx-edge-tool/config/template_pack_2_publication.json",
        "templatePack2PublicationTool": "backend/sqx-edge-tool/tools/template_pack_2_publication.py",
        "templatePack2PublicationEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_publication",
        "templatePack2PublicationPolicy": "require_real_checkout_url_variant_support_rollback_and_purchase_drill_before_controlled_publication",
        "templatePack2PurchaseDrillConfig": "backend/sqx-edge-tool/config/template_pack_2_purchase_drill.json",
        "templatePack2PurchaseDrillTool": "backend/sqx-edge-tool/tools/template_pack_2_purchase_drill.py",
        "templatePack2PurchaseDrillEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_purchase_drill",
        "templatePack2PurchaseDrillPolicy": "record_controlled_pack_2_order_payment_delivery_support_and_refund_pause_before_scaling",
        "templatePack2HandoffConfig": "backend/sqx-edge-tool/config/template_pack_2_handoff.json",
        "templatePack2HandoffTool": "backend/sqx-edge-tool/tools/template_pack_2_handoff.py",
        "templatePack2HandoffEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_handoff",
        "templatePack2HandoffPolicy": "confirm_delivery_support_first_value_and_scale_or_pause_decision_after_controlled_pack_2_purchase",
        "templatePack2SalesRegisterConfig": "backend/sqx-edge-tool/config/template_pack_2_sales_register.json",
        "templatePack2SalesRegisterTool": "backend/sqx-edge-tool/tools/template_pack_2_sales_register.py",
        "templatePack2SalesRegisterEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_sales_register",
        "templatePack2SalesRegisterPolicy": "track_redacted_pack_2_sales_delivery_support_refunds_and_scale_decision_before_more_traffic",
        "templatePack2FeedbackCohortConfig": "backend/sqx-edge-tool/config/template_pack_2_feedback_cohort.json",
        "templatePack2FeedbackCohortTool": "backend/sqx-edge-tool/tools/template_pack_2_feedback_cohort.py",
        "templatePack2FeedbackCohortEvidenceDir": "backend/sqx-edge-tool/data/template_pack_2_feedback_cohort",
        "templatePack2FeedbackCohortPolicy": "review_redacted_pack_2_buyer_feedback_support_refunds_and_positive_signals_before_expanding_traffic",
        "buyerReadyCheckoutCloseoutConfig": "backend/sqx-edge-tool/config/buyer_ready_checkout_closeout.json",
        "buyerReadyCheckoutCloseoutTool": "backend/sqx-edge-tool/tools/buyer_ready_checkout_closeout.py",
        "buyerReadyCheckoutCloseoutEvidenceDir": "backend/sqx-edge-tool/data/buyer_ready_checkout_closeout",
        "buyerReadyCheckoutCloseoutPolicy": "confirm_basic_user_checkout_release_license_support_and_rollback_before_controlled_sales",
        "publicBuyerPageCadenceConfig": "backend/sqx-edge-tool/config/public_buyer_page_cadence.json",
        "publicBuyerPageCadenceTool": "backend/sqx-edge-tool/tools/public_buyer_page_cadence.py",
        "publicBuyerPageCadenceEvidenceDir": "backend/sqx-edge-tool/data/public_buyer_page_cadence",
        "publicBuyerPageCadencePolicy": "prepare_public_buyer_page_checklist_support_cadence_and_first_sale_operations_before_wider_distribution",
        "firstControlledBuyerLogConfig": "backend/sqx-edge-tool/config/first_controlled_buyer_log.json",
        "firstControlledBuyerLogTool": "backend/sqx-edge-tool/tools/first_controlled_buyer_log.py",
        "firstControlledBuyerLogEvidenceDir": "backend/sqx-edge-tool/data/first_controlled_buyer_log",
        "firstControlledBuyerLogPolicy": "record_first_controlled_buyer_activation_support_feedback_and_post_sale_decision_without_personal_data",
        "postSaleImprovementLoopConfig": "backend/sqx-edge-tool/config/post_sale_improvement_loop.json",
        "postSaleImprovementLoopTool": "backend/sqx-edge-tool/tools/post_sale_improvement_loop.py",
        "postSaleImprovementLoopEvidenceDir": "backend/sqx-edge-tool/data/post_sale_improvement_loop",
        "postSaleImprovementLoopPolicy": "convert_first_controlled_buyer_feedback_into_onboarding_support_macro_public_copy_and_safe_claim_micro_updates",
        "postSaleMicroUpdatesConfig": "backend/sqx-edge-tool/config/post_sale_micro_updates.json",
        "postSaleMicroUpdatesTool": "backend/sqx-edge-tool/tools/post_sale_micro_updates.py",
        "postSaleMicroUpdatesEvidenceDir": "backend/sqx-edge-tool/data/post_sale_micro_updates",
        "postSaleMicroUpdatesPolicy": "verify_applied_buyer_facing_micro_updates_and_next_controlled_buyer_readiness",
        "nextControlledBuyerReadinessConfig": "backend/sqx-edge-tool/config/next_controlled_buyer_readiness.json",
        "nextControlledBuyerReadinessTool": "backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py",
        "nextControlledBuyerReadinessEvidenceDir": "backend/sqx-edge-tool/data/next_controlled_buyer_readiness",
        "nextControlledBuyerReadinessPolicy": "confirm_single_private_buyer_slot_checkout_license_delivery_support_followup_safe_claims_and_pause_rule",
        "nextControlledBuyerOutcomeConfig": "backend/sqx-edge-tool/config/next_controlled_buyer_outcome.json",
        "nextControlledBuyerOutcomeTool": "backend/sqx-edge-tool/tools/next_controlled_buyer_outcome.py",
        "nextControlledBuyerOutcomeEvidenceDir": "backend/sqx-edge-tool/data/next_controlled_buyer_outcome",
        "nextControlledBuyerOutcomePolicy": "record_redacted_controlled_buyer_result_activation_first_value_support_refund_claims_and_next_distribution_decision",
        "controlledDistributionStepConfig": "backend/sqx-edge-tool/config/controlled_distribution_step.json",
        "controlledDistributionStepTool": "backend/sqx-edge-tool/tools/controlled_distribution_step.py",
        "controlledDistributionStepEvidenceDir": "backend/sqx-edge-tool/data/controlled_distribution_step",
        "controlledDistributionStepPolicy": "execute_selected_m71_decision_as_tiny_reversible_distribution_step",
        "controlledDistributionReviewConfig": "backend/sqx-edge-tool/config/controlled_distribution_review.json",
        "controlledDistributionReviewTool": "backend/sqx-edge-tool/tools/controlled_distribution_review.py",
        "controlledDistributionReviewEvidenceDir": "backend/sqx-edge-tool/data/controlled_distribution_review",
        "controlledDistributionReviewPolicy": "review_m72_evidence_before_repeating_holding_pausing_or_preparing_next_buyer_facing_asset",
        "nextBuyerFacingAssetConfig": "backend/sqx-edge-tool/config/next_buyer_facing_asset.json",
        "nextBuyerFacingAssetTool": "backend/sqx-edge-tool/tools/next_buyer_facing_asset.py",
        "nextBuyerFacingAssetEvidenceDir": "backend/sqx-edge-tool/data/next_buyer_facing_asset",
        "nextBuyerFacingAssetPolicy": "prepare_one_small_buyer_facing_asset_for_private_review_only_after_m73",
        "privateAssetReviewConfig": "backend/sqx-edge-tool/config/private_asset_review.json",
        "privateAssetReviewTool": "backend/sqx-edge-tool/tools/private_asset_review.py",
        "privateAssetReviewEvidenceDir": "backend/sqx-edge-tool/data/private_asset_review",
        "privateAssetReviewPolicy": "approve_asset_for_controlled_publication_only_after_private_review_safe_claims_support_release_notes_and_rollback",
        "rollbackPolicy": "disable_checkout_pause_webhook_pause_worker_manual_fulfillment",
        "automation": {
          "status": "next_controlled_commercial_movement_from_m98_decision_ready",
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
          },
          {
            "plan": "template_pack_1",
            "label": "Template Pack 1",
            "providerVariantId": "",
            "price": "49 EUR",
            "billing": "one_time_addon",
            "licenseDurationDays": 0,
            "activationLimit": 0
          },
          {
            "plan": "template_pack_2",
            "label": "Template Pack 2",
            "providerVariantId": "",
            "price": "79 EUR",
            "billing": "one_time_addon",
            "licenseDurationDays": 0,
            "activationLimit": 0
          }
        ],
        "postPurchaseSteps": [
          "Confirmar pago en Lemon Squeezy o Gumroad.",
          "Generar licencia firmada con license_issue.py.",
          "Preparar entrega con prepare_customer_delivery.ps1.",
          "Validar buyer onboarding support gate antes de entregar.",
          "Enviar ZIP portable, licencia JSON, START_HERE.md, FAQ y plantilla de soporte al cliente.",
          "Si compra Template Pack 1 o Template Pack 2, generar y entregar el ZIP add-on separado."
        ],
        "controlledPublicationGateConfig": "backend/sqx-edge-tool/config/controlled_publication_gate.json",
        "controlledPublicationGateTool": "backend/sqx-edge-tool/tools/controlled_publication_gate.py",
        "controlledPublicationGateEvidenceDir": "backend/sqx-edge-tool/data/controlled_publication_gate",
        "controlledPublicationGatePolicy": "prepare_controlled_publication_only_after_private_asset_review_support_safe_claims_release_notes_rollback_and_pause_rule_are_ready",
        "limitedPublicationDraftConfig": "backend/sqx-edge-tool/config/limited_publication_draft.json",
        "limitedPublicationDraftTool": "backend/sqx-edge-tool/tools/limited_publication_draft.py",
        "limitedPublicationDraftEvidenceDir": "backend/sqx-edge-tool/data/limited_publication_draft",
        "limitedPublicationDraftPolicy": "prepare_limited_publication_copy_for_operator_review_only_after_m76_support_safe_claims_rollback_pause_rule_and_channel_limits_are_ready",
        "operatorPublicationReviewConfig": "backend/sqx-edge-tool/config/operator_publication_review.json",
        "operatorPublicationReviewTool": "backend/sqx-edge-tool/tools/operator_publication_review.py",
        "operatorPublicationReviewEvidenceDir": "backend/sqx-edge-tool/data/operator_publication_review",
        "operatorPublicationReviewPolicy": "approve_manual_limited_publication_only_after_human_review_safe_copy_support_rollback_pause_rule_channel_limit_and_basic_user_flow_are_ready",
        "manualLimitedPublicationRecordConfig": "backend/sqx-edge-tool/config/manual_limited_publication_record.json",
        "manualLimitedPublicationRecordTool": "backend/sqx-edge-tool/tools/manual_limited_publication_record.py",
        "manualLimitedPublicationRecordEvidenceDir": "backend/sqx-edge-tool/data/manual_limited_publication_record",
        "manualLimitedPublicationRecordPolicy": "record_manual_limited_publication_only_after_m78_approval_support_rollback_pause_rule_monitoring_and_redacted_channel_evidence_are_ready",
        "manualPublicationMonitorConfig": "backend/sqx-edge-tool/config/manual_publication_monitor.json",
        "manualPublicationMonitorTool": "backend/sqx-edge-tool/tools/manual_publication_monitor.py",
        "manualPublicationMonitorEvidenceDir": "backend/sqx-edge-tool/data/manual_publication_monitor",
        "manualPublicationMonitorPolicy": "monitor_manual_limited_publication_before_any_traffic_expansion_and_block_scaling_when_support_claims_refunds_or_incidents_are_unresolved",
        "controlledTrafficExpansionReviewConfig": "backend/sqx-edge-tool/config/controlled_traffic_expansion_review.json",
        "controlledTrafficExpansionReviewTool": "backend/sqx-edge-tool/tools/controlled_traffic_expansion_review.py",
        "controlledTrafficExpansionReviewEvidenceDir": "backend/sqx-edge-tool/data/controlled_traffic_expansion_review",
        "controlledTrafficExpansionReviewPolicy": "approve_only_tiny_controlled_traffic_expansion_after_m80_monitoring_support_claims_refunds_incidents_rollback_and_pause_rule_are_clean",
        "controlledTrafficExpansionStepConfig": "backend/sqx-edge-tool/config/controlled_traffic_expansion_step.json",
        "controlledTrafficExpansionStepTool": "backend/sqx-edge-tool/tools/controlled_traffic_expansion_step.py",
        "controlledTrafficExpansionStepEvidenceDir": "backend/sqx-edge-tool/data/controlled_traffic_expansion_step",
        "controlledTrafficExpansionStepPolicy": "execute_only_one_tiny_reversible_traffic_step_after_m81_go_with_support_rollback_pause_rule_and_safe_claims_confirmed",
        "controlledTrafficExpansionMonitorConfig": "backend/sqx-edge-tool/config/controlled_traffic_expansion_monitor.json",
        "controlledTrafficExpansionMonitorTool": "backend/sqx-edge-tool/tools/controlled_traffic_expansion_monitor.py",
        "controlledTrafficExpansionMonitorEvidenceDir": "backend/sqx-edge-tool/data/controlled_traffic_expansion_monitor",
        "controlledTrafficExpansionMonitorPolicy": "monitor_m82_tiny_step_before_repeating_pausing_or_widening_again",
        "controlledTrafficExpansionDecisionConfig": "backend/sqx-edge-tool/config/controlled_traffic_expansion_decision.json",
        "controlledTrafficExpansionDecisionTool": "backend/sqx-edge-tool/tools/controlled_traffic_expansion_decision.py",
        "controlledTrafficExpansionDecisionEvidenceDir": "backend/sqx-edge-tool/data/controlled_traffic_expansion_decision",
        "controlledTrafficExpansionDecisionPolicy": "convert_m83_monitor_evidence_into_one_small_operator_decision_without_automatic_traffic_checkout_or_license_actions",
        "controlledTrafficExpansionExecutionConfig": "backend/sqx-edge-tool/config/controlled_traffic_expansion_execution.json",
        "controlledTrafficExpansionExecutionTool": "backend/sqx-edge-tool/tools/controlled_traffic_expansion_execution.py",
        "controlledTrafficExpansionExecutionEvidenceDir": "backend/sqx-edge-tool/data/controlled_traffic_expansion_execution",
        "controlledTrafficExpansionExecutionPolicy": "record_only_the_manual_m84_approved_action_without_automatic_traffic_checkout_email_or_license_execution",
        "controlledTrafficExpansionExecutionMonitorConfig": "backend/sqx-edge-tool/config/controlled_traffic_expansion_execution_monitor.json",
        "controlledTrafficExpansionExecutionMonitorTool": "backend/sqx-edge-tool/tools/controlled_traffic_expansion_execution_monitor.py",
        "controlledTrafficExpansionExecutionMonitorEvidenceDir": "backend/sqx-edge-tool/data/controlled_traffic_expansion_execution_monitor",
        "controlledTrafficExpansionExecutionMonitorPolicy": "monitor_m85_execution_result_before_any_further_traffic_or_commercial_movement",
        "controlledCommercialNextMovementConfig": "backend/sqx-edge-tool/config/controlled_commercial_next_movement.json",
        "controlledCommercialNextMovementTool": "backend/sqx-edge-tool/tools/controlled_commercial_next_movement.py",
        "controlledCommercialNextMovementEvidenceDir": "backend/sqx-edge-tool/data/controlled_commercial_next_movement",
        "controlledCommercialNextMovementPolicy": "decide_next_controlled_commercial_movement_from_m86_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        "controlledCommercialNextMovementExecutionConfig": "backend/sqx-edge-tool/config/controlled_commercial_next_movement_execution.json",
        "controlledCommercialNextMovementExecutionTool": "backend/sqx-edge-tool/tools/controlled_commercial_next_movement_execution.py",
        "controlledCommercialNextMovementExecutionEvidenceDir": "backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution",
        "controlledCommercialNextMovementExecutionPolicy": "record_only_the_manual_m87_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        "controlledCommercialNextMovementExecutionMonitorConfig": "backend/sqx-edge-tool/config/controlled_commercial_next_movement_execution_monitor.json",
        "controlledCommercialNextMovementExecutionMonitorTool": "backend/sqx-edge-tool/tools/controlled_commercial_next_movement_execution_monitor.py",
        "controlledCommercialNextMovementExecutionMonitorEvidenceDir": "backend/sqx-edge-tool/data/controlled_commercial_next_movement_execution_monitor",
        "controlledCommercialNextMovementExecutionMonitorPolicy": "monitor_m88_execution_result_before_any_broader_commercial_movement",
        "nextControlledCommercialMovementDecisionConfig": "backend/sqx-edge-tool/config/next_controlled_commercial_movement_decision.json",
        "nextControlledCommercialMovementDecisionTool": "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_decision.py",
        "nextControlledCommercialMovementDecisionEvidenceDir": "backend/sqx-edge-tool/data/next_controlled_commercial_movement_decision",
        "nextControlledCommercialMovementDecisionPolicy": "decide_next_controlled_commercial_movement_from_m89_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        "approvedControlledCommercialMovementExecutionConfig": "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_execution.json",
        "approvedControlledCommercialMovementExecutionTool": "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_execution.py",
        "approvedControlledCommercialMovementExecutionEvidenceDir": "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution",
        "approvedControlledCommercialMovementExecutionPolicy": "record_only_the_manual_m90_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        "approvedControlledCommercialMovementExecutionMonitorConfig": "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_execution_monitor.json",
        "approvedControlledCommercialMovementExecutionMonitorTool": "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_execution_monitor.py",
        "approvedControlledCommercialMovementExecutionMonitorEvidenceDir": "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_execution_monitor",
        "approvedControlledCommercialMovementExecutionMonitorPolicy": "monitor_m91_execution_result_before_any_additional_commercial_movement",
        "nextControlledCommercialMovementFromM92DecisionConfig": "backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m92_decision.json",
        "nextControlledCommercialMovementFromM92DecisionTool": "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m92_decision.py",
        "nextControlledCommercialMovementFromM92DecisionEvidenceDir": "backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m92_decision",
        "nextControlledCommercialMovementFromM92DecisionPolicy": "decide_next_controlled_commercial_movement_from_m92_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        "approvedControlledCommercialMovementFromM93ExecutionConfig": "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m93_execution.json",
        "approvedControlledCommercialMovementFromM93ExecutionTool": "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m93_execution.py",
        "approvedControlledCommercialMovementFromM93ExecutionEvidenceDir": "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution",
        "approvedControlledCommercialMovementFromM93ExecutionPolicy": "record_only_the_manual_m93_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        "approvedControlledCommercialMovementFromM93ExecutionMonitorConfig": "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m93_execution_monitor.json",
        "approvedControlledCommercialMovementFromM93ExecutionMonitorTool": "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m93_execution_monitor.py",
        "approvedControlledCommercialMovementFromM93ExecutionMonitorEvidenceDir": "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m93_execution_monitor",
        "approvedControlledCommercialMovementFromM93ExecutionMonitorPolicy": "monitor_m94_execution_result_before_any_additional_commercial_movement",
        "nextControlledCommercialMovementFromM95DecisionConfig": "backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m95_decision.json",
        "nextControlledCommercialMovementFromM95DecisionTool": "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m95_decision.py",
        "nextControlledCommercialMovementFromM95DecisionEvidenceDir": "backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m95_decision",
        "nextControlledCommercialMovementFromM95DecisionPolicy": "decide_next_controlled_commercial_movement_from_m95_evidence_without_automatic_traffic_checkout_email_or_license_actions",
        "approvedControlledCommercialMovementFromM96DecisionExecutionConfig": "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution.json",
        "approvedControlledCommercialMovementFromM96DecisionExecutionTool": "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution.py",
        "approvedControlledCommercialMovementFromM96DecisionExecutionEvidenceDir": "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution",
        "approvedControlledCommercialMovementFromM96DecisionExecutionPolicy": "record_only_the_manual_m96_approved_movement_without_automatic_traffic_checkout_email_or_license_execution",
        "approvedControlledCommercialMovementFromM96DecisionExecutionMonitorConfig": "backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.json",
        "approvedControlledCommercialMovementFromM96DecisionExecutionMonitorTool": "backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py",
        "approvedControlledCommercialMovementFromM96DecisionExecutionMonitorEvidenceDir": "backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution_monitor",
        "approvedControlledCommercialMovementFromM96DecisionExecutionMonitorPolicy": "monitor_m97_execution_result_before_any_additional_commercial_movement",
        "nextControlledCommercialMovementFromM98DecisionConfig": "backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m98_decision.json",
        "nextControlledCommercialMovementFromM98DecisionTool": "backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m98_decision.py",
        "nextControlledCommercialMovementFromM98DecisionEvidenceDir": "backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m98_decision",
        "nextControlledCommercialMovementFromM98DecisionPolicy": "decide_next_controlled_commercial_movement_from_m98_evidence_without_automatic_traffic_checkout_email_or_license_actions"
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
      "tester": {
        "label": "Tester licensed ZIP",
        "includeInternalTools": false,
        "defaultPlan": "free",
        "activationMode": "signed_tester_file",
        "redistributionAllowed": false
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
        "bs": "BS_Tendencia_v6",
        "dir": "L"
      },
      {
        "num": 2,
        "phase": 1,
        "asset": "XAUUSD",
        "tf": "H4",
        "bs": "BS_Tendencia_v6",
        "dir": "L"
      },
      {
        "num": 3,
        "phase": 1,
        "asset": "XAUUSD",
        "tf": "M30",
        "bs": "BS_Tendencia_v6",
        "dir": "L"
      },
      {
        "num": 4,
        "phase": 2,
        "asset": "EURUSD",
        "tf": "H1",
        "bs": "BS_Tendencia_v6",
        "dir": "L/S"
      },
      {
        "num": 5,
        "phase": 2,
        "asset": "EURUSD",
        "tf": "H4",
        "bs": "BS_Tendencia_v6",
        "dir": "L/S"
      },
      {
        "num": 6,
        "phase": 2,
        "asset": "EURUSD",
        "tf": "M30",
        "bs": "BS_Momentum_v6",
        "dir": "L/S"
      },
      {
        "num": 7,
        "phase": 3,
        "asset": "USTEC",
        "tf": "H1",
        "bs": "BS_Tendencia_v6",
        "dir": "L"
      },
      {
        "num": 8,
        "phase": 3,
        "asset": "USTEC",
        "tf": "H1",
        "bs": "BS_Momentum_v6",
        "dir": "L"
      },
      {
        "num": 9,
        "phase": 3,
        "asset": "USTEC",
        "tf": "M30",
        "bs": "BS_Momentum_v6",
        "dir": "L"
      },
      {
        "num": 10,
        "phase": 4,
        "asset": "GBPUSD",
        "tf": "H1",
        "bs": "BS_Volatilidad_v6_intraday_v6",
        "dir": "L/S"
      },
      {
        "num": 11,
        "phase": 4,
        "asset": "GBPJPY",
        "tf": "H1",
        "bs": "BS_Volatilidad_v6_intraday_v6",
        "dir": "L/S"
      },
      {
        "num": 12,
        "phase": 5,
        "asset": "EURGBP",
        "tf": "H4",
        "bs": "BS_Regimen_v6",
        "dir": "L/S"
      },
      {
        "num": 13,
        "phase": 5,
        "asset": "AUDNZD",
        "tf": "H4",
        "bs": "BS_Regimen_v6",
        "dir": "L/S"
      },
      {
        "num": 14,
        "phase": 5,
        "asset": "EURGBP",
        "tf": "H1",
        "bs": "BS_Estadistico_v6",
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
        "blocksetting": "BS_Tendencia_v6",
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
        "blocksetting": "BS_Tendencia_v6",
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
        "blocksetting": "BS_Tendencia_v6",
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
        "blocksetting": "BS_Tendencia_v6",
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
  },
  "blocksettings": {
    "version": 2,
    "source": {
      "resourceDir": "backend/sqx-edge-tool/resources/blocksettings",
      "generatedFrom": "versioned .sqb resources",
      "defaultGeneration": "v6",
      "legacyGeneration": "v4/v5/v7 resources retained for backwards compatibility"
    },
    "entries": [
      {
        "canonicalId": "BS_Estadistico_v4",
        "filename": "BS_Estadistico_v4.sqb",
        "family": "estadistico",
        "familyLabel": "Estadistico",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "812A906949CA2555B8FC4E2C6142A030F89863EBC2D1FE21A91550E9F6D69010",
        "sha256Short": "812A906949CA",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 20,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 20
          }
        },
        "activeBlocks": [
          "Indicators.SRPercentRank",
          "Indicators.ZScore",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLowerCount",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreaterCount",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.SRPercentRank",
          "Indicators.ZScore"
        ],
        "activeBlockPreview": [
          "Indicators.SRPercentRank",
          "Indicators.ZScore",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLowerCount",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals"
        ],
        "parameterPreview": {
          "Indicators.SRPercentRank": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Mode#",
                "name": "Mode",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Length#",
                "name": "Length",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#ATRPeriod#",
                "name": "ATR Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.ZScore": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Open": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "IsLowerPercentil": {
            "generated": [
              {
                "key": "#Indicator#",
                "name": "Indicator",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Bars#",
                "name": "Bars",
                "type": "int",
                "generation": "random",
                "min": "100",
                "max": "1000",
                "step": "100"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Percentile#",
                "name": "Percentile",
                "type": "double",
                "generation": "random",
                "min": "5",
                "max": "95",
                "step": "5"
              }
            ]
          },
          "IsLowerCount": {
            "generated": [
              {
                "key": "#Bars#",
                "name": "Bars",
                "type": "int",
                "generation": "random",
                "min": "2",
                "max": "10",
                "step": "1"
              },
              {
                "key": "#NotStrict#",
                "name": "Allow same values",
                "type": "boolean",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#IndicatorLeft#",
                "name": "Indicator Left",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#IndicatorRight#",
                "name": "Indicator Right",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Estadistico_v6",
        "filename": "BS_Estadistico_v6.sqb",
        "family": "estadistico",
        "familyLabel": "Estadistico",
        "layer": 1,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "12218A93C737FAD0A0D3F0F5F55374C7162D0717007A7ECF3DEA80E9DD56112B",
        "sha256Short": "12218A93C737",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 22,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 22
          }
        },
        "activeBlocks": [
          "Indicators.HurstExponent",
          "Indicators.KaufmanEfficiencyRatio",
          "Indicators.SRPercentRank",
          "Indicators.ZScore",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLowerCount",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreaterCount",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.HurstExponent",
          "Indicators.KaufmanEfficiencyRatio",
          "Indicators.SRPercentRank",
          "Indicators.ZScore"
        ],
        "activeBlockPreview": [
          "Indicators.HurstExponent",
          "Indicators.KaufmanEfficiencyRatio",
          "Indicators.SRPercentRank",
          "Indicators.ZScore",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLowerCount",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "Indicators.HurstExponent": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.SRPercentRank": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Mode#",
                "name": "Mode",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Length#",
                "name": "Length",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#ATRPeriod#",
                "name": "ATR Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.ZScore": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Open": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v4",
        "filename": "BS_Filtros_v4.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "EAED2430BB0ACC4E6477704BDFB8F807D5555DD5B1EA8733B5C952255B02669E",
        "sha256Short": "EAED2430BB0A",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v5_D1",
        "filename": "BS_Filtros_v5_D1.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v5_d1",
        "timeframes": [
          "D1"
        ],
        "sha256": "B5AB92C6390A994C0550788FBB257CFA0158DA8376BEE5ADD80D9C575DC1E3A9",
        "sha256Short": "B5AB92C6390A",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 31,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 28,
            "signals": 3
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "CBlock_DCloseMayorSMA20",
          "CBlock_DCloseMinorSMA20",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "CBlock_DCloseMayorSMA20",
          "CBlock_DCloseMinorSMA20",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "CBlock_DCloseMayorSMA20": {
            "generated": [
              {
                "key": "#Chart1#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          },
          "CBlock_DCloseMinorSMA20": {
            "generated": [
              {
                "key": "#Chart1#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v6",
        "filename": "BS_Filtros_v6.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "306EDDFF6F857167D494C74530019C1FA2EABF0144A333B6CDEE06EF50291D52",
        "sha256Short": "306EDDFF6F85",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v6_D1",
        "filename": "BS_Filtros_v6_D1.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v6_d1",
        "timeframes": [
          "D1"
        ],
        "sha256": "B5AB92C6390A994C0550788FBB257CFA0158DA8376BEE5ADD80D9C575DC1E3A9",
        "sha256Short": "B5AB92C6390A",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 31,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 28,
            "signals": 3
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "CBlock_DCloseMayorSMA20",
          "CBlock_DCloseMinorSMA20",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "CBlock_DCloseMayorSMA20",
          "CBlock_DCloseMinorSMA20",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "CBlock_DCloseMayorSMA20": {
            "generated": [
              {
                "key": "#Chart1#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          },
          "CBlock_DCloseMinorSMA20": {
            "generated": [
              {
                "key": "#Chart1#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v7_H1",
        "filename": "BS_Filtros_v7_H1.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v7_h1",
        "timeframes": [
          "H1"
        ],
        "sha256": "BBB9FAC0B8174DE15F62B1F0CE89D806B73F64EFFCF4423D85779A3C16D5D360",
        "sha256Short": "BBB9FAC0B817",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v7_H4",
        "filename": "BS_Filtros_v7_H4.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v7_h4",
        "timeframes": [
          "H4"
        ],
        "sha256": "B11EE14CED4B5B006262376CDB738BC2DE2F09F836C6A775A6B9873C7972A9FE",
        "sha256Short": "B11EE14CED4B",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v7_M15",
        "filename": "BS_Filtros_v7_M15.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v7_m15",
        "timeframes": [
          "M15"
        ],
        "sha256": "A5FF1A9E80075F6845DCDE2655B9FAC64E9C2FD8EC768F0ECC8D7E8C80942FC2",
        "sha256Short": "A5FF1A9E8007",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v7_M30",
        "filename": "BS_Filtros_v7_M30.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v7_m30",
        "timeframes": [
          "M30"
        ],
        "sha256": "301882B9E55AD54E5427735898313361771C122BFEE9777C256C9B3D476E3B5A",
        "sha256Short": "301882B9E55A",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Filtros_v7_M5",
        "filename": "BS_Filtros_v7_M5.sqb",
        "family": "filtros",
        "familyLabel": "Filtros operativos",
        "layer": 2,
        "variant": "v7_m5",
        "timeframes": [
          "M5"
        ],
        "sha256": "4834062C9D1541FF8CABB996AA8B2871DD6DDA9087FCF5106D2FEC583A99FAD6",
        "sha256Short": "4834062C9D15",
        "sqxVersion": "141.2225",
        "counts": {
          "blocks": 540,
          "activeBlocks": 21,
          "changedBlocks": 62,
          "categories": {
            "indicators": 100,
            "signals": 383,
            "stopLimitBlocks": 57
          },
          "activeCategories": {
            "indicators": 20,
            "signals": 1
          }
        },
        "activeBlocks": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio"
        ],
        "activeBlockPreview": [
          "AlwaysTrue",
          "Indicators.ADX",
          "Indicators.ATR",
          "Indicators.AvgVolume",
          "Indicators.KaufmanEfficiencyRatio",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "AlwaysTrue": {
            "generated": []
          },
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.KaufmanEfficiencyRatio": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Momentum_v4",
        "filename": "BS_Momentum_v4.sqb",
        "family": "momentum",
        "familyLabel": "Momentum",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "394C66C00CA610EC36C40FF5A1C78C34352AC77A15A1DBA8E397C79307199854",
        "sha256Short": "394C66C00CA6",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 26,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 26
          }
        },
        "activeBlocks": [
          "Indicators.AwesomeOscillator",
          "Indicators.CCI",
          "Indicators.Momentum",
          "Indicators.OSMA",
          "Indicators.ROC",
          "Indicators.RSI",
          "Indicators.Stochastic",
          "Indicators.WilliamsPR",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLowerCount",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreaterCount",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.AwesomeOscillator",
          "Indicators.CCI",
          "Indicators.Momentum",
          "Indicators.OSMA",
          "Indicators.ROC",
          "Indicators.RSI",
          "Indicators.Stochastic",
          "Indicators.WilliamsPR"
        ],
        "activeBlockPreview": [
          "Indicators.AwesomeOscillator",
          "Indicators.CCI",
          "Indicators.Momentum",
          "Indicators.OSMA",
          "Indicators.ROC",
          "Indicators.RSI",
          "Indicators.Stochastic",
          "Indicators.WilliamsPR",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open"
        ],
        "parameterPreview": {
          "Indicators.AwesomeOscillator": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.CCI": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Momentum": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.OSMA": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#FastEMA#",
                "name": "Fast EMA",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#SlowEMA#",
                "name": "Slow EMA",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#SignalPeriod#",
                "name": "Signal Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.ROC": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.RSI": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Stochastic": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#KPeriod#",
                "name": "%K Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#DPeriod#",
                "name": "%D Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Slowing#",
                "name": "Slowing",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#MAMethod#",
                "name": "MA Method",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#PriceField#",
                "name": "Price Field",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.WilliamsPR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Momentum_v6",
        "filename": "BS_Momentum_v6.sqb",
        "family": "momentum",
        "familyLabel": "Momentum",
        "layer": 1,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "774E79AB6273F018FBD1F7DD6FB6CEBD0082983DA2AE2FC223C28DF95FC96ADB",
        "sha256Short": "774E79AB6273",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 26,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 26
          }
        },
        "activeBlocks": [
          "Indicators.AwesomeOscillator",
          "Indicators.CCI",
          "Indicators.Momentum",
          "Indicators.OSMA",
          "Indicators.ROC",
          "Indicators.RSI",
          "Indicators.Stochastic",
          "Indicators.WilliamsPR",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLowerCount",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreaterCount",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.AwesomeOscillator",
          "Indicators.CCI",
          "Indicators.Momentum",
          "Indicators.OSMA",
          "Indicators.ROC",
          "Indicators.RSI",
          "Indicators.Stochastic",
          "Indicators.WilliamsPR"
        ],
        "activeBlockPreview": [
          "Indicators.AwesomeOscillator",
          "Indicators.CCI",
          "Indicators.Momentum",
          "Indicators.OSMA",
          "Indicators.ROC",
          "Indicators.RSI",
          "Indicators.Stochastic",
          "Indicators.WilliamsPR",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open"
        ],
        "parameterPreview": {
          "Indicators.AwesomeOscillator": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.CCI": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Momentum": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.OSMA": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#FastEMA#",
                "name": "Fast EMA",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#SlowEMA#",
                "name": "Slow EMA",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#SignalPeriod#",
                "name": "Signal Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.ROC": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.RSI": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Stochastic": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#KPeriod#",
                "name": "%K Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#DPeriod#",
                "name": "%D Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Slowing#",
                "name": "Slowing",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#MAMethod#",
                "name": "MA Method",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#PriceField#",
                "name": "Price Field",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.WilliamsPR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Regimen_v4",
        "filename": "BS_Regimen_v4.sqb",
        "family": "regimen",
        "familyLabel": "Regimen",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "7D655C44656C2FF7FA6A756E9951318AA06203F6E52B6EDC0E5B718F3676FF41",
        "sha256Short": "7D655C44656C",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 19,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 19
          }
        },
        "activeBlocks": [
          "Indicators.CSSAMarketRegime",
          "Indicators.EhlersHilbertTransform",
          "Indicators.EntropyMath",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.CSSAMarketRegime",
          "Indicators.EhlersHilbertTransform",
          "Indicators.EntropyMath"
        ],
        "activeBlockPreview": [
          "Indicators.CSSAMarketRegime",
          "Indicators.EhlersHilbertTransform",
          "Indicators.EntropyMath",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals"
        ],
        "parameterPreview": {
          "Indicators.CSSAMarketRegime": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#HLSumPeriod#",
                "name": "HL Sum Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#HLPeriod#",
                "name": "HL Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#AvgPeriod#",
                "name": "Avg Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#PercRankPeriod#",
                "name": "Perc Rank Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.EhlersHilbertTransform": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.EntropyMath": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#EMPeriod#",
                "name": "EM Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Open": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "IsLowerPercentil": {
            "generated": [
              {
                "key": "#Indicator#",
                "name": "Indicator",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Bars#",
                "name": "Bars",
                "type": "int",
                "generation": "random",
                "min": "100",
                "max": "1000",
                "step": "100"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Percentile#",
                "name": "Percentile",
                "type": "double",
                "generation": "random",
                "min": "5",
                "max": "95",
                "step": "5"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Regimen_v6",
        "filename": "BS_Regimen_v6.sqb",
        "family": "regimen",
        "familyLabel": "Regimen",
        "layer": 1,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "0589FD1B4FC8CE3D23752BFED77BDF8CA3DADB0E33E3DB62EBCE8820BD6FEA8C",
        "sha256Short": "0589FD1B4FC8",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 22,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 22
          }
        },
        "activeBlocks": [
          "Indicators.ADX",
          "Indicators.ChoppinessIndex",
          "Indicators.CSSAMarketRegime",
          "Indicators.EhlersHilbertTransform",
          "Indicators.EntropyMath",
          "Indicators.HurstExponent",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "NotEquals",
          "Equals",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ADX",
          "Indicators.ChoppinessIndex",
          "Indicators.CSSAMarketRegime",
          "Indicators.EhlersHilbertTransform",
          "Indicators.EntropyMath",
          "Indicators.HurstExponent"
        ],
        "activeBlockPreview": [
          "Indicators.ADX",
          "Indicators.ChoppinessIndex",
          "Indicators.CSSAMarketRegime",
          "Indicators.EhlersHilbertTransform",
          "Indicators.EntropyMath",
          "Indicators.HurstExponent",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower"
        ],
        "parameterPreview": {
          "Indicators.ADX": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Input",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ChoppinessIndex": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.CSSAMarketRegime": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#HLSumPeriod#",
                "name": "HL Sum Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#HLPeriod#",
                "name": "HL Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#AvgPeriod#",
                "name": "Avg Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#PercRankPeriod#",
                "name": "Perc Rank Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.EhlersHilbertTransform": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.EntropyMath": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#EMPeriod#",
                "name": "EM Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.HurstExponent": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_SoporteResistencia_v4",
        "filename": "BS_SoporteResistencia_v4.sqb",
        "family": "sr",
        "familyLabel": "Soporte/Resistencia",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "D55DFCC3E2CB6F74A56663C0DB4FAD8F4BE6F866DB634E640AC9A7FFAD89FEFA",
        "sha256Short": "D55DFCC3E2CB",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 30,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 30
          }
        },
        "activeBlocks": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising",
          "Not"
        ],
        "activeIndicators": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange"
        ],
        "activeBlockPreview": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low"
        ],
        "parameterPreview": {
          "Indicators.Fractal": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Fractal#",
                "name": "Fractal",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.Highest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.HighestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Lowest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.LowestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.CloseD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.HighD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_SoporteResistencia_v4_intraday_v5",
        "filename": "BS_SoporteResistencia_v4_intraday_v5.sqb",
        "family": "sr",
        "familyLabel": "Soporte/Resistencia",
        "layer": 1,
        "variant": "v4_intraday_v5",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1"
        ],
        "sha256": "4325F5C4D16A9BE0007E64908A34A603372BAD8BCF2AB2C16C40CEFF3EA52B2C",
        "sha256Short": "4325F5C4D16A",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 18,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 18
          }
        },
        "activeBlocks": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising",
          "Not"
        ],
        "activeIndicators": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange"
        ],
        "activeBlockPreview": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater"
        ],
        "parameterPreview": {
          "Indicators.Fractal": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Fractal#",
                "name": "Fractal",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.Highest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.HighestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Lowest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.LowestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_SoporteResistencia_v6",
        "filename": "BS_SoporteResistencia_v6.sqb",
        "family": "sr",
        "familyLabel": "Soporte/Resistencia",
        "layer": 1,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "9CCC2B2876E3538591A4A16B430F50D1299D5F628DD4D62C450C7DB11F7F79A4",
        "sha256Short": "9CCC2B2876E3",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 32,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 32
          }
        },
        "activeBlocks": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising",
          "Not"
        ],
        "activeIndicators": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange"
        ],
        "activeBlockPreview": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low"
        ],
        "parameterPreview": {
          "Indicators.Fractal": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Fractal#",
                "name": "Fractal",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.Highest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.HighestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Lowest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.LowestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.CloseD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.HighD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_SoporteResistencia_v6_intraday_v6",
        "filename": "BS_SoporteResistencia_v6_intraday_v6.sqb",
        "family": "sr",
        "familyLabel": "Soporte/Resistencia",
        "layer": 1,
        "variant": "v6_intraday_v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1"
        ],
        "sha256": "059314501E430EAF0EB743A8D63D180692D7FA28FB4B017F0AD46179059D32CA",
        "sha256Short": "059314501E43",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 20,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 20
          }
        },
        "activeBlocks": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising",
          "Not"
        ],
        "activeIndicators": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange"
        ],
        "activeBlockPreview": [
          "Indicators.Fractal",
          "Indicators.Highest",
          "Indicators.HighestInRange",
          "Indicators.Lowest",
          "Indicators.LowestInRange",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual"
        ],
        "parameterPreview": {
          "Indicators.Fractal": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Fractal#",
                "name": "Fractal",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.Highest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.HighestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Lowest": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.LowestInRange": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TimeFrom#",
                "name": "Time From",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#TimeTo#",
                "name": "Time To",
                "type": "int",
                "generation": "random",
                "min": "0",
                "max": "2359",
                "step": "30"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Tendencia_v4",
        "filename": "BS_Tendencia_v4.sqb",
        "family": "tendencia",
        "familyLabel": "Tendencia",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "9838AC0CB5753CAA5AFB7D584E5D51B0657AD4EAD8485DCAF4FE6530A6E1A4E0",
        "sha256Short": "9838AC0CB575",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 36,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 36
          }
        },
        "activeBlocks": [
          "Indicators.ATRTrailingStops",
          "Indicators.EMA",
          "Indicators.LinearRegression",
          "Indicators.MACD",
          "Indicators.ParabolicSAR",
          "Indicators.SMA",
          "Indicators.SuperTrend",
          "Indicators.Ichimoku",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater",
          "IsGreaterOrEqual",
          "IndicatorCrossesAboveMA",
          "IndicatorCrossesBelowMA",
          "IndicatorBelowMA",
          "IndicatorAboveMA",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ATRTrailingStops",
          "Indicators.EMA",
          "Indicators.LinearRegression",
          "Indicators.MACD",
          "Indicators.ParabolicSAR",
          "Indicators.SMA",
          "Indicators.SuperTrend",
          "Indicators.Ichimoku"
        ],
        "activeBlockPreview": [
          "Indicators.ATRTrailingStops",
          "Indicators.EMA",
          "Indicators.LinearRegression",
          "Indicators.MACD",
          "Indicators.ParabolicSAR",
          "Indicators.SMA",
          "Indicators.SuperTrend",
          "Indicators.Ichimoku",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD"
        ],
        "parameterPreview": {
          "Indicators.ATRTrailingStops": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ATRPeriod#",
                "name": "ATR Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#ATRSmoothigPeriod#",
                "name": "ATR Smoothig Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#ATRMultiplier#",
                "name": "ATR Multiplier",
                "type": "double",
                "generation": "random",
                "min": "0.5",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#ATRSmoothingMode#",
                "name": "ATRSmoothingMode",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Method#",
                "name": "Method",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.EMA": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.LinearRegression": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.MACD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Fast#",
                "name": "Fast",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Slow#",
                "name": "Slow",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Smooth#",
                "name": "Smooth",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ParabolicSAR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Step#",
                "name": "Step",
                "type": "double",
                "generation": "random",
                "min": "0.01",
                "max": "0.04",
                "step": "0.01"
              },
              {
                "key": "#Maximum#",
                "name": "Maximum",
                "type": "double",
                "generation": "random",
                "min": "0.1",
                "max": "0.4",
                "step": "0.1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.SMA": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.SuperTrend": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Mode#",
                "name": "Mode",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#ATRPeriod#",
                "name": "ATR Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#ATRMult#",
                "name": "ATR Mult",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Ichimoku": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TenkanPeriod#",
                "name": "Tenkan",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#KijunPeriod#",
                "name": "Kijun",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#SenkouPeriod#",
                "name": "Senkou",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Tendencia_v6",
        "filename": "BS_Tendencia_v6.sqb",
        "family": "tendencia",
        "familyLabel": "Tendencia",
        "layer": 1,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "D51F88B9B2D51194EB5FEA1C39227E7078951F290761E4ABCCB56D6FDC02C387",
        "sha256Short": "D51F88B9B2D5",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 38,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 38
          }
        },
        "activeBlocks": [
          "Indicators.ATRTrailingStops",
          "Indicators.EMA",
          "Indicators.LinearRegression",
          "Indicators.MACD",
          "Indicators.ParabolicSAR",
          "Indicators.SMA",
          "Indicators.SuperTrend",
          "Indicators.Ichimoku",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "IndicatorCrossesAboveMA",
          "IndicatorCrossesBelowMA",
          "IndicatorBelowMA",
          "IndicatorAboveMA",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ATRTrailingStops",
          "Indicators.EMA",
          "Indicators.LinearRegression",
          "Indicators.MACD",
          "Indicators.ParabolicSAR",
          "Indicators.SMA",
          "Indicators.SuperTrend",
          "Indicators.Ichimoku"
        ],
        "activeBlockPreview": [
          "Indicators.ATRTrailingStops",
          "Indicators.EMA",
          "Indicators.LinearRegression",
          "Indicators.MACD",
          "Indicators.ParabolicSAR",
          "Indicators.SMA",
          "Indicators.SuperTrend",
          "Indicators.Ichimoku",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD"
        ],
        "parameterPreview": {
          "Indicators.ATRTrailingStops": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ATRPeriod#",
                "name": "ATR Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#ATRSmoothigPeriod#",
                "name": "ATR Smoothig Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#ATRMultiplier#",
                "name": "ATR Multiplier",
                "type": "double",
                "generation": "random",
                "min": "0.5",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#ATRSmoothingMode#",
                "name": "ATRSmoothingMode",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Method#",
                "name": "Method",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.EMA": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.LinearRegression": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.MACD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Fast#",
                "name": "Fast",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Slow#",
                "name": "Slow",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Smooth#",
                "name": "Smooth",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.ParabolicSAR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Step#",
                "name": "Step",
                "type": "double",
                "generation": "random",
                "min": "0.01",
                "max": "0.04",
                "step": "0.01"
              },
              {
                "key": "#Maximum#",
                "name": "Maximum",
                "type": "double",
                "generation": "random",
                "min": "0.1",
                "max": "0.4",
                "step": "0.1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.SMA": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.SuperTrend": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Mode#",
                "name": "Mode",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#ATRPeriod#",
                "name": "ATR Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#ATRMult#",
                "name": "ATR Mult",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.Ichimoku": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#TenkanPeriod#",
                "name": "Tenkan",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#KijunPeriod#",
                "name": "Kijun",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#SenkouPeriod#",
                "name": "Senkou",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volatilidad_v4",
        "filename": "BS_Volatilidad_v4.sqb",
        "family": "volatilidad",
        "familyLabel": "Volatilidad",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "112975F339939FB00BE56420D053A3A8CD840B4824E328A78D8F8E7E407D8815",
        "sha256Short": "112975F33993",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 39,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 39
          }
        },
        "activeBlocks": [
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands",
          "Indicators.VWAPBollingerBands",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands",
          "Indicators.VWAPBollingerBands"
        ],
        "activeBlockPreview": [
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands"
        ],
        "parameterPreview": {
          "Indicators.BollingerBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.DonchianChannels": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.HullMovingAverageATRBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Multiplication#",
                "name": "Multiplication",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.HullMovingAverageBollingerBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.KeltnerChannel": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.LogATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.MTATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.MTKeltnerChannel": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volatilidad_v4_intraday_v5",
        "filename": "BS_Volatilidad_v4_intraday_v5.sqb",
        "family": "volatilidad",
        "familyLabel": "Volatilidad",
        "layer": 1,
        "variant": "v4_intraday_v5",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1"
        ],
        "sha256": "4D52651F0868BA88A6DD53A09043B566024D52FF64B3CB64E77F82E045737AD7",
        "sha256Short": "4D52651F0868",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 28,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 28
          }
        },
        "activeBlocks": [
          "Indicators.ATR",
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands",
          "Indicators.VWAPBollingerBands",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ATR",
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands",
          "Indicators.VWAPBollingerBands"
        ],
        "activeBlockPreview": [
          "Indicators.ATR",
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex"
        ],
        "parameterPreview": {
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.BollingerBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.DonchianChannels": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.HullMovingAverageATRBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Multiplication#",
                "name": "Multiplication",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.HullMovingAverageBollingerBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.KeltnerChannel": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.LogATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.MTATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volatilidad_v6_intraday_v6",
        "filename": "BS_Volatilidad_v6_intraday_v6.sqb",
        "family": "volatilidad",
        "familyLabel": "Volatilidad",
        "layer": 1,
        "variant": "v6_intraday_v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1"
        ],
        "sha256": "63EEAE27584F67CADCB59F4548648F5048CE43EBA2B220B8F60B7BDF2B08AE61",
        "sha256Short": "63EEAE27584F",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 28,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 28
          }
        },
        "activeBlocks": [
          "Indicators.ATR",
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands",
          "Indicators.VWAPBollingerBands",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.ATR",
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex",
          "Indicators.VWAPATRBands",
          "Indicators.VWAPBollingerBands"
        ],
        "activeBlockPreview": [
          "Indicators.ATR",
          "Indicators.BollingerBands",
          "Indicators.DonchianChannels",
          "Indicators.HullMovingAverageATRBands",
          "Indicators.HullMovingAverageBollingerBands",
          "Indicators.KeltnerChannel",
          "Indicators.LogATR",
          "Indicators.MTATR",
          "Indicators.MTKeltnerChannel",
          "Indicators.StdDev",
          "Indicators.TrueRange",
          "Indicators.UlcerIndex"
        ],
        "parameterPreview": {
          "Indicators.ATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.BollingerBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.DonchianChannels": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.HullMovingAverageATRBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Multiplication#",
                "name": "Multiplication",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "5.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.HullMovingAverageBollingerBands": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#ComputedFrom#",
                "name": "Computed From",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.KeltnerChannel": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Deviation#",
                "name": "Deviation",
                "type": "double",
                "generation": "random",
                "min": "1.0",
                "max": "3.0",
                "step": "0.5"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Line#",
                "name": "Line",
                "type": "int",
                "generation": "random",
                "min": null,
                "max": null,
                "step": null
              }
            ]
          },
          "Indicators.LogATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.MTATR": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volumen_v4",
        "filename": "BS_Volumen_v4.sqb",
        "family": "volumen",
        "familyLabel": "Volumen",
        "layer": 1,
        "variant": "v4",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "8425FE9589BCF2E67E63C9710E886BB0223D5A698E85B238B53C190384210C78",
        "sha256Short": "8425FE9589BC",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 25,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 25
          }
        },
        "activeBlocks": [
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.VWAP"
        ],
        "activeBlockPreview": [
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM"
        ],
        "parameterPreview": {
          "Indicators.VWAP": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#VWAPPeriod#",
                "name": "VWAP Period",
                "type": "int",
                "generation": "random",
                "min": "-1000003",
                "max": "-1000004",
                "step": "1"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.CloseD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.HighD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.LowD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.OpenD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volumen_v4_intraday_v5",
        "filename": "BS_Volumen_v4_intraday_v5.sqb",
        "family": "volumen",
        "familyLabel": "Volumen",
        "layer": 1,
        "variant": "v4_intraday_v5",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1"
        ],
        "sha256": "6F432A092DD0509EA75D668FF8DEEA1F159A0CADC5DEF1E77C45FD5493068CFA",
        "sha256Short": "6F432A092DD0",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 14,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 14
          }
        },
        "activeBlocks": [
          "Indicators.AvgVolume",
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.AvgVolume",
          "Indicators.VWAP"
        ],
        "activeBlockPreview": [
          "Indicators.AvgVolume",
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow"
        ],
        "parameterPreview": {
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.VWAP": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#VWAPPeriod#",
                "name": "VWAP Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Open": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "IsLower": {
            "generated": [
              {
                "key": "#Left#",
                "name": "Left",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Right#",
                "name": "Right",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          },
          "IsLowerOrEqual": {
            "generated": [
              {
                "key": "#Left#",
                "name": "Left",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Right#",
                "name": "Right",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volumen_v6",
        "filename": "BS_Volumen_v6.sqb",
        "family": "volumen",
        "familyLabel": "Volumen",
        "layer": 1,
        "variant": "v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1",
          "H4",
          "D1"
        ],
        "sha256": "CA74EB9004408F4AA2533D33DD7F557A28BB6C9C387C45EABC7D1E76ADD553C5",
        "sha256Short": "CA74EB900440",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 28,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 28
          }
        },
        "activeBlocks": [
          "Indicators.AvgVolume",
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM",
          "Prices.OpenM",
          "Prices.Open",
          "Prices.CloseW",
          "Prices.HighW",
          "Prices.LowW",
          "Prices.OpenW",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.AvgVolume",
          "Indicators.VWAP"
        ],
        "activeBlockPreview": [
          "Indicators.AvgVolume",
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.CloseD",
          "Prices.HighD",
          "Prices.LowD",
          "Prices.OpenD",
          "Prices.High",
          "Prices.Low",
          "Prices.CloseM",
          "Prices.HighM",
          "Prices.LowM"
        ],
        "parameterPreview": {
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.VWAP": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#VWAPPeriod#",
                "name": "VWAP Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.CloseD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.HighD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.LowD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.OpenD": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          }
        }
      },
      {
        "canonicalId": "BS_Volumen_v6_intraday_v6",
        "filename": "BS_Volumen_v6_intraday_v6.sqb",
        "family": "volumen",
        "familyLabel": "Volumen",
        "layer": 1,
        "variant": "v6_intraday_v6",
        "timeframes": [
          "M5",
          "M15",
          "M30",
          "H1"
        ],
        "sha256": "9CC8A6D14E8A1DD0FEFFA99F358732D269907281B5C9CA18AF77A3806042DB92",
        "sha256Short": "9CC8A6D14E8A",
        "sqxVersion": "142.2336",
        "counts": {
          "blocks": 749,
          "activeBlocks": 16,
          "changedBlocks": 76,
          "categories": {
            "indicators": 124,
            "signals": 553,
            "stopLimitBlocks": 72
          },
          "activeCategories": {
            "indicators": 16
          }
        },
        "activeBlocks": [
          "Indicators.AvgVolume",
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual",
          "CrossesAbove",
          "CrossesBelow",
          "IsFalling",
          "IsRising"
        ],
        "activeIndicators": [
          "Indicators.AvgVolume",
          "Indicators.VWAP"
        ],
        "activeBlockPreview": [
          "Indicators.AvgVolume",
          "Indicators.VWAP",
          "Prices.Close",
          "Prices.High",
          "Prices.Low",
          "Prices.Open",
          "IsLowerPercentil",
          "IsLower",
          "IsLowerOrEqual",
          "IsGreaterPercentil",
          "IsGreater",
          "IsGreaterOrEqual"
        ],
        "parameterPreview": {
          "Indicators.AvgVolume": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Period#",
                "name": "Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Indicators.VWAP": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#VWAPPeriod#",
                "name": "VWAP Period",
                "type": "int",
                "generation": "random",
                "min": "10",
                "max": "200",
                "step": "10"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Close": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.High": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Low": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "Prices.Open": {
            "generated": [
              {
                "key": "#Chart#",
                "name": "Chart",
                "type": "data",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              }
            ]
          },
          "IsLowerPercentil": {
            "generated": [
              {
                "key": "#Indicator#",
                "name": "Indicator",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Bars#",
                "name": "Bars",
                "type": "int",
                "generation": "random",
                "min": "100",
                "max": "1000",
                "step": "100"
              },
              {
                "key": "#Shift#",
                "name": "Shift",
                "type": "int",
                "generation": "random",
                "min": "-1000001",
                "max": "-1000002",
                "step": "1"
              },
              {
                "key": "#Percentile#",
                "name": "Percentile",
                "type": "double",
                "generation": "random",
                "min": "5",
                "max": "95",
                "step": "5"
              }
            ]
          },
          "IsLower": {
            "generated": [
              {
                "key": "#Left#",
                "name": "Left",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              },
              {
                "key": "#Right#",
                "name": "Right",
                "type": "value",
                "generation": "random",
                "min": "null",
                "max": "null",
                "step": "null"
              }
            ]
          }
        }
      }
    ],
    "aliases": {
      "BS_Tendencia": "BS_Tendencia_v6",
      "BS_Momentum": "BS_Momentum_v6",
      "BS_Volatilidad": "BS_Volatilidad_v4",
      "BS_Regimen": "BS_Regimen_v6",
      "BS_Volumen": "BS_Volumen_v6",
      "BS_SoporteResistencia": "BS_SoporteResistencia_v6",
      "BS_Estadistico": "BS_Estadistico_v6",
      "BS_Filtros": "BS_Filtros_v6",
      "BS_Filtros_v5": "BS_Filtros_v5_D1",
      "BS_Filtros_v6_D1": "BS_Filtros_v6_D1",
      "BS_Filtros_v6": "BS_Filtros_v6",
      "BS_Filtros_v7": "BS_Filtros_v7_H1",
      "BS_Estadistico_v4": "BS_Estadistico_v4",
      "BS_Estadistico_v6": "BS_Estadistico_v6",
      "BS_Filtros_v4": "BS_Filtros_v4",
      "BS_Filtros_v5_D1": "BS_Filtros_v5_D1",
      "BS_Filtros_v7_H1": "BS_Filtros_v7_H1",
      "BS_Filtros_v7_H4": "BS_Filtros_v7_H4",
      "BS_Filtros_v7_M15": "BS_Filtros_v7_M15",
      "BS_Filtros_v7_M30": "BS_Filtros_v7_M30",
      "BS_Filtros_v7_M5": "BS_Filtros_v7_M5",
      "BS_Momentum_v4": "BS_Momentum_v4",
      "BS_Momentum_v6": "BS_Momentum_v6",
      "BS_Regimen_v4": "BS_Regimen_v4",
      "BS_Regimen_v6": "BS_Regimen_v6",
      "BS_SoporteResistencia_v4": "BS_SoporteResistencia_v4",
      "BS_SoporteResistencia_v4_intraday_v5": "BS_SoporteResistencia_v4_intraday_v5",
      "BS_SoporteResistencia_v6": "BS_SoporteResistencia_v6",
      "BS_SoporteResistencia_v6_intraday_v6": "BS_SoporteResistencia_v6_intraday_v6",
      "BS_Tendencia_v4": "BS_Tendencia_v4",
      "BS_Tendencia_v6": "BS_Tendencia_v6",
      "BS_Volatilidad_v4": "BS_Volatilidad_v4",
      "BS_Volatilidad_v4_intraday_v5": "BS_Volatilidad_v4_intraday_v5",
      "BS_Volatilidad_v6_intraday_v6": "BS_Volatilidad_v6_intraday_v6",
      "BS_Volumen_v4": "BS_Volumen_v4",
      "BS_Volumen_v4_intraday_v5": "BS_Volumen_v4_intraday_v5",
      "BS_Volumen_v6": "BS_Volumen_v6",
      "BS_Volumen_v6_intraday_v6": "BS_Volumen_v6_intraday_v6",
      "BS_Estadistico_v4.sqb": "BS_Estadistico_v4",
      "BS_Estadistico_v6.sqb": "BS_Estadistico_v6",
      "BS_Filtros_v4.sqb": "BS_Filtros_v4",
      "BS_Filtros_v5_D1.sqb": "BS_Filtros_v5_D1",
      "BS_Filtros_v6.sqb": "BS_Filtros_v6",
      "BS_Filtros_v6_D1.sqb": "BS_Filtros_v6_D1",
      "BS_Filtros_v7_H1.sqb": "BS_Filtros_v7_H1",
      "BS_Filtros_v7_H4.sqb": "BS_Filtros_v7_H4",
      "BS_Filtros_v7_M15.sqb": "BS_Filtros_v7_M15",
      "BS_Filtros_v7_M30.sqb": "BS_Filtros_v7_M30",
      "BS_Filtros_v7_M5.sqb": "BS_Filtros_v7_M5",
      "BS_Momentum_v4.sqb": "BS_Momentum_v4",
      "BS_Momentum_v6.sqb": "BS_Momentum_v6",
      "BS_Regimen_v4.sqb": "BS_Regimen_v4",
      "BS_Regimen_v6.sqb": "BS_Regimen_v6",
      "BS_SoporteResistencia_v4.sqb": "BS_SoporteResistencia_v4",
      "BS_SoporteResistencia_v4_intraday_v5.sqb": "BS_SoporteResistencia_v4_intraday_v5",
      "BS_SoporteResistencia_v6.sqb": "BS_SoporteResistencia_v6",
      "BS_SoporteResistencia_v6_intraday_v6.sqb": "BS_SoporteResistencia_v6_intraday_v6",
      "BS_Tendencia_v4.sqb": "BS_Tendencia_v4",
      "BS_Tendencia_v6.sqb": "BS_Tendencia_v6",
      "BS_Volatilidad_v4.sqb": "BS_Volatilidad_v4",
      "BS_Volatilidad_v4_intraday_v5.sqb": "BS_Volatilidad_v4_intraday_v5",
      "BS_Volatilidad_v6_intraday_v6.sqb": "BS_Volatilidad_v6_intraday_v6",
      "BS_Volumen_v4.sqb": "BS_Volumen_v4",
      "BS_Volumen_v4_intraday_v5.sqb": "BS_Volumen_v4_intraday_v5",
      "BS_Volumen_v6.sqb": "BS_Volumen_v6",
      "BS_Volumen_v6_intraday_v6.sqb": "BS_Volumen_v6_intraday_v6"
    },
    "capa1Resolver": {
      "intradayTimeframes": [
        "M5",
        "M15",
        "M30",
        "H1"
      ],
      "families": {
        "tendencia": {
          "default": "BS_Tendencia_v6"
        },
        "momentum": {
          "default": "BS_Momentum_v6"
        },
        "volatilidad": {
          "default": "BS_Volatilidad_v4",
          "intraday": "BS_Volatilidad_v6_intraday_v6"
        },
        "regimen": {
          "default": "BS_Regimen_v6"
        },
        "volumen": {
          "default": "BS_Volumen_v6",
          "intraday": "BS_Volumen_v6_intraday_v6"
        },
        "sr": {
          "default": "BS_SoporteResistencia_v6",
          "intraday": "BS_SoporteResistencia_v6_intraday_v6"
        },
        "estadistico": {
          "default": "BS_Estadistico_v6"
        }
      }
    },
    "capa2Recommendations": {
      "manual": true,
      "recommendations": {
        "M5": "BS_Filtros_v6",
        "M15": "BS_Filtros_v6",
        "M30": "BS_Filtros_v6",
        "H1": "BS_Filtros_v6",
        "H4": "BS_Filtros_v6",
        "D1": "BS_Filtros_v6_D1",
        "fallback": "BS_Filtros_v6"
      }
    }
  }
};
