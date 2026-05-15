(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var TM_DB_NAME = 'SQXTemplateMakerDB';
  var TM_DB_VERSION = 1;
  var TM_STORE_STRATEGIES = 'tm_strategies';
  var TM_STORE_CONFIG = 'tm_config';
  var TM_CERT_VERSION = 'TMA2.2';
  var TM_RULESET = 'template-maker-cert-v2';
  var TM_SCHEMA_VERSION = 'template-maker-cert-v2';
  var TM_CERT_VIEW_NAME = 'Template Maker Cert';
  var REQUIRED_IDENTITY_COLUMNS = [
    'Strategy Name',
    'Symbol',
    'TimeFrame',
    'Fitness'
  ];
  var REQUIRED_METRICS_ALL = [
    'Net profit',
    '# of trades',
    'Profit factor',
    'Max DD %',
    'Sharpe Ratio',
    'Stability',
    'CAGR/Max DD %',
    'Winning Percent',
    'SQN',
    'Recovery Factor',
    'Calmar Ratio',
    'Sortino Ratio',
    '% Profitable Months'
  ];
  var DERIVED_METRICS = {
    'Ret/DD Ratio': 'CAGR/Max DD %'
  };
  var DIVERSITY_VERSION = 'template-maker-diversity-v1';
  var EXIT_POLICY_VERSION = 'sqx-exit-policy-v1';
  var DIVERSITY_METRICS = [
    'CAGR/Max DD %',
    'Profit factor',
    'Max DD %',
    '# of trades',
    'Winning Percent',
    'Stability'
  ];
  var DEFAULT_DIVERSITY_SETTINGS = {
    structuralThreshold: 0.70,
    metricThreshold: 0.88,
    hybridThreshold: 0.78,
    structuralWeight: 0.65,
    metricWeight: 0.35,
    bridgeStructuralThreshold: 0.45,
    metrics: DIVERSITY_METRICS.slice()
  };
  var C2_BLOCKSETTINGS = {
    tendencia: 'BS_Tendencia_v4',
    bs_tendencia: 'BS_Tendencia_v4',
    bs_tendencia_v4: 'BS_Tendencia_v4',
    BS_Tendencia_v4: 'BS_Tendencia_v4',
    momentum: 'BS_Momentum_v4',
    bs_momentum: 'BS_Momentum_v4',
    bs_momentum_v4: 'BS_Momentum_v4',
    BS_Momentum_v4: 'BS_Momentum_v4',
    volatilidad: 'BS_Volatilidad_v4',
    bs_volatilidad: 'BS_Volatilidad_v4',
    bs_volatilidad_v4: 'BS_Volatilidad_v4',
    BS_Volatilidad_v4: 'BS_Volatilidad_v4',
    regimen: 'BS_Regimen_v4',
    regime: 'BS_Regimen_v4',
    bs_regimen: 'BS_Regimen_v4',
    bs_regime: 'BS_Regimen_v4',
    bs_regimen_v4: 'BS_Regimen_v4',
    BS_Regimen_v4: 'BS_Regimen_v4',
    sr: 'BS_SoporteResistencia_v4',
    soporte_resistencia: 'BS_SoporteResistencia_v4',
    soporteresistencia: 'BS_SoporteResistencia_v4',
    bs_soporte_resistencia: 'BS_SoporteResistencia_v4',
    bs_soporteresistencia: 'BS_SoporteResistencia_v4',
    bs_soporteresistencia_v4: 'BS_SoporteResistencia_v4',
    BS_SoporteResistencia_v4: 'BS_SoporteResistencia_v4',
    volumen: 'BS_Volumen_v4',
    volume: 'BS_Volumen_v4',
    bs_volumen: 'BS_Volumen_v4',
    bs_volume: 'BS_Volumen_v4',
    bs_volumen_v4: 'BS_Volumen_v4',
    BS_Volumen_v4: 'BS_Volumen_v4',
    estadistico: 'BS_Estadistico_v4',
    estadistica: 'BS_Estadistico_v4',
    statistical: 'BS_Estadistico_v4',
    bs_estadistico: 'BS_Estadistico_v4',
    bs_estadistica: 'BS_Estadistico_v4',
    bs_estadistico_v4: 'BS_Estadistico_v4',
    BS_Estadistico_v4: 'BS_Estadistico_v4',
    filtros: 'BS_Filtros_v7_H1',
    bs_filtros: 'BS_Filtros_v7_H1',
    bs_filtros_v5: 'BS_Filtros_v5_D1',
    bs_filtros_v5_d1: 'BS_Filtros_v5_D1',
    bs_filtros_v7_h1: 'BS_Filtros_v7_H1',
    BS_Filtros_v7_H1: 'BS_Filtros_v7_H1',
    custom: 'BS_Custom',
    bs_custom: 'BS_Custom'
  };
  var METRIC_ALIASES = {
    'Strategy Name': ['Strategy Name', 'Name', 'Strategy'],
    Symbol: ['Symbol', 'Market', 'Instrument'],
    TimeFrame: ['TimeFrame', 'Timeframe', 'Time Frame', 'TF'],
    Fitness: ['Fitness', 'Fit'],
    RecoveryFactor: ['Recovery Factor', 'RecoveryFactor'],
    'Recovery Factor': ['Recovery Factor', 'RecoveryFactor'],
    CalmarRatio: ['Calmar Ratio', 'CalmarRatio'],
    'Calmar Ratio': ['Calmar Ratio', 'CalmarRatio'],
    SortinoRatio: ['Sortino Ratio', 'SortinoRatio'],
    'Sortino Ratio': ['Sortino Ratio', 'SortinoRatio'],
    'Profit Factor': ['Profit factor', 'Profit Factor'],
    'Profit factor': ['Profit factor', 'Profit Factor'],
    NumberOfTrades: ['# of trades', 'NumberOfTrades'],
    '# of trades': ['# of trades', 'NumberOfTrades'],
    DrawdownPct: ['Max DD %', 'DrawdownPct'],
    'Max DD %': ['Max DD %', 'DrawdownPct'],
    SharpeRatio: ['Sharpe Ratio', 'SharpeRatio'],
    'Sharpe Ratio': ['Sharpe Ratio', 'SharpeRatio'],
    WinningPct: ['Winning Percent', 'WinningPct', 'Win %'],
    'Win %': ['Winning Percent', 'WinningPct', 'Win %'],
    'Winning Percent': ['Winning Percent', 'WinningPct', 'Win %'],
    SQN: ['SQN'],
    Stability: ['Stability'],
    NetProfit: ['Net profit', 'NetProfit'],
    'Net profit': ['Net profit', 'NetProfit'],
    ProfitableMonthsPct: ['% Profitable Months', 'ProfitableMonthsPct'],
    '% Profitable Months': ['% Profitable Months', 'ProfitableMonthsPct'],
    'CAGR/Max DD %': ['CAGR/Max DD %', 'AnnualPctReturnDDRatio', 'Ret/DD Ratio'],
    AnnualPctReturnDDRatio: ['CAGR/Max DD %', 'AnnualPctReturnDDRatio', 'Ret/DD Ratio'],
    'Ret/DD Ratio': ['Ret/DD Ratio', 'CAGR/Max DD %', 'AnnualPctReturnDDRatio']
  };

  var PRESETS = {
    Generic: {
      1: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 200 },
        'Profit factor': { op: '>=', val: 1.2 },
        'Max DD %': { op: '<=', val: 30 },
        'Sharpe Ratio': { op: '>=', val: 0.5 },
        'Stability': { op: '>=', val: 0.5 },
        'CAGR/Max DD %': { op: '>=', val: 0.5 },
        'Winning Percent': { op: '>=', val: 40 },
        SQN: { op: '>=', val: 1 },
        'Recovery Factor': { op: '>=', val: 2 }
      },
      2: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 150 },
        'Profit factor': { op: '>=', val: 1.3 },
        'Max DD %': { op: '<=', val: 20 },
        'Sharpe Ratio': { op: '>=', val: 0.7 },
        'Recovery Factor': { op: '>=', val: 3 },
        SQN: { op: '>=', val: 1.5 },
        'Calmar Ratio': { op: '>=', val: 0.5 },
        'Sortino Ratio': { op: '>=', val: 0.8 },
        '% Profitable Months': { op: '>=', val: 55 },
        Stability: { op: '>=', val: 0.7 },
        'Winning Percent': { op: '>=', val: 45 }
      }
    },
    Indices: {
      1: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 300 },
        'Profit factor': { op: '>=', val: 1.3 },
        'Max DD %': { op: '<=', val: 20 },
        'Sharpe Ratio': { op: '>=', val: 0.8 },
        Stability: { op: '>=', val: 0.7 },
        'Winning Percent': { op: '>=', val: 45 },
        SQN: { op: '>=', val: 2 }
      },
      2: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 200 },
        'Profit factor': { op: '>=', val: 1.4 },
        'Max DD %': { op: '<=', val: 15 },
        'Sharpe Ratio': { op: '>=', val: 1 },
        SQN: { op: '>=', val: 2.5 },
        Stability: { op: '>=', val: 0.8 }
      }
    },
    Forex: {
      1: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 400 },
        'Profit factor': { op: '>=', val: 1.25 },
        'Max DD %': { op: '<=', val: 15 },
        'Sharpe Ratio': { op: '>=', val: 0.6 },
        'Winning Percent': { op: '>=', val: 50 }
      },
      2: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 300 },
        'Profit factor': { op: '>=', val: 1.35 },
        'Max DD %': { op: '<=', val: 10 },
        'Sharpe Ratio': { op: '>=', val: 0.9 }
      }
    },
    Crypto: {
      1: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 150 },
        'Profit factor': { op: '>=', val: 1.5 },
        'Max DD %': { op: '<=', val: 40 },
        'Sharpe Ratio': { op: '>=', val: 0.7 },
        'Recovery Factor': { op: '>=', val: 3 }
      },
      2: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 100 },
        'Profit factor': { op: '>=', val: 2 },
        'Max DD %': { op: '<=', val: 25 },
        'Sharpe Ratio': { op: '>=', val: 1.2 }
      }
    },
    Commodities: {
      1: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 180 },
        'Profit factor': { op: '>=', val: 1.25 },
        'Max DD %': { op: '<=', val: 28 },
        'Ret/DD Ratio': { op: '>=', val: 2 },
        'Winning Percent': { op: '>=', val: 40 }
      },
      2: {
        'Net profit': { op: '>', val: 0 },
        '# of trades': { op: '>=', val: 120 },
        'Profit factor': { op: '>=', val: 1.35 },
        'Max DD %': { op: '<=', val: 22 },
        'Ret/DD Ratio': { op: '>=', val: 3 },
        'Recovery Factor': { op: '>=', val: 3 }
      }
    }
  };

  var SYMBOL_PATTERNS = {
    Indices: /NAS100|US30|DE40|DAX|SP500|DOW|NQ|GER|HK50|US500|USTECH|GR40/i,
    Commodities: /XAU|GOLD|XAG|SILVER|OIL|WTI|BRENT/i,
    Forex: /^[A-Z]{6}$|^[A-Z]{3}[/.][A-Z]{3}$|EUR|USD|GBP|JPY|AUD|CAD|CHF|NZD/i,
    Crypto: /BTC|ETH|SOL|ADA|DOT|XRP|LTC|DOGE|USDT/i,
  };

  var _db = null;
  var _strategies = [];
  var _currentCapa = 1;
  var _currentPreset = 'Generic';
  var _thresholds = clone(PRESETS.Generic);
  var _diversitySettings = clone(DEFAULT_DIVERSITY_SETTINGS);
  var _nextId = 1;

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function resetRuntimeConfig() {
    _currentCapa = 1;
    _currentPreset = 'Generic';
    _thresholds = clone(PRESETS.Generic);
    _diversitySettings = clone(DEFAULT_DIVERSITY_SETTINGS);
  }

  function createBaseRecord(source) {
    var record = Object.assign({
      sources: {},
      metrics: {},
      logic: {},
      provenance: {
        schemaVersion: TM_SCHEMA_VERSION,
        certVersion: TM_CERT_VERSION,
        diversityVersion: DIVERSITY_VERSION,
        ruleset: TM_RULESET,
        exitPolicyVersion: EXIT_POLICY_VERSION,
        importedAt: new Date().toISOString(),
        events: []
      },
      certification: {}
    }, source || {});
    record.sources = Object.assign({}, record.sources || {});
    record.metrics = Object.assign({}, record.metrics || {});
    record.logic = Object.assign({}, record.logic || {});
    record.provenance = Object.assign({
      schemaVersion: TM_SCHEMA_VERSION,
      certVersion: TM_CERT_VERSION,
      diversityVersion: DIVERSITY_VERSION,
      ruleset: TM_RULESET,
      exitPolicyVersion: EXIT_POLICY_VERSION,
      importedAt: new Date().toISOString(),
      events: []
    }, record.provenance || {});
    record.provenance.events = Array.isArray(record.provenance.events) ? record.provenance.events.slice() : [];
    enforceCurrentProvenance(record.provenance);
    record.certification = Object.assign({}, record.certification || {});
    return record;
  }

  function enforceCurrentProvenance(provenance) {
    if (!provenance) return;
    provenance.schemaVersion = TM_SCHEMA_VERSION;
    provenance.certVersion = TM_CERT_VERSION;
    provenance.diversityVersion = DIVERSITY_VERSION;
    provenance.ruleset = TM_RULESET;
    provenance.exitPolicyVersion = EXIT_POLICY_VERSION;
  }

  function addEvent(strategy, type, source) {
    var target = strategy.provenance = strategy.provenance || { events: [] };
    target.events = Array.isArray(target.events) ? target.events : [];
    target.events.push({
      type: type,
      source: source || '',
      at: new Date().toISOString()
    });
  }

  function stableStringify(value) {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(stableStringify).join(',') + ']';
    return '{' + Object.keys(value).sort().map(function(key) {
      return JSON.stringify(key) + ':' + stableStringify(value[key]);
    }).join(',') + '}';
  }

  function bytesToHex(buffer) {
    return Array.prototype.map.call(new Uint8Array(buffer), function(byte) {
      return byte.toString(16).padStart(2, '0');
    }).join('');
  }

  function fallbackHash(value) {
    var text = typeof value === 'string' ? value : stableStringify(value);
    var h1 = 2166136261;
    var h2 = 16777619;
    for (var i = 0; i < text.length; i += 1) {
      h1 ^= text.charCodeAt(i);
      h1 = Math.imul(h1, 16777619);
      h2 ^= text.charCodeAt(i) << (i % 8);
      h2 = Math.imul(h2, 1099511627);
    }
    return ('00000000' + (h1 >>> 0).toString(16)).slice(-8) + ('00000000' + (h2 >>> 0).toString(16)).slice(-8);
  }

  function computeFileHash(fileOrValue) {
    if (fileOrValue && typeof fileOrValue.arrayBuffer === 'function') {
      return fileOrValue.arrayBuffer().then(function(buffer) {
        if (global.crypto && global.crypto.subtle && global.crypto.subtle.digest) {
          return global.crypto.subtle.digest('SHA-256', buffer).then(bytesToHex);
        }
        return fallbackHash(Array.prototype.join.call(new Uint8Array(buffer), ','));
      });
    }
    return Promise.resolve(fallbackHash(fileOrValue || ''));
  }

  function computeRowFingerprint(row) {
    return fallbackHash(stripRuntimeFields(row || {}));
  }

  function inferViewName(headers) {
    var names = headers || [];
    var required = getRequiredContractColumns();
    var missing = required.filter(function(column) {
      return !findMetricKeyFromList(column, names);
    });
    if (!missing.length) return TM_CERT_VIEW_NAME;
    if (missing.length <= 3) return 'Template Maker Cert compatible';
    return 'CSV compatible no identificado';
  }

  function getRequiredContractColumns() {
    return REQUIRED_IDENTITY_COLUMNS.concat(REQUIRED_METRICS_ALL);
  }

  function init() {
    return dbInit().then(ensureSchemaVersion).then(loadConfigFromDB).then(loadStrategiesFromDB).catch(function() {
      return _strategies.slice();
    });
  }

  function reset() {
    _strategies = [];
    _nextId = 1;
    resetRuntimeConfig();
    return clearDB().then(persistSchemaVersion);
  }

  function clearResultStrategies() {
    var removed = _strategies.length;
    _strategies = [];
    _nextId = 1;
    return saveStrategiesToDB().then(function() {
      return {
        removed: removed,
        total: _strategies.length
      };
    });
  }

  function deleteResultStrategies(strategyIds) {
    var ids = {};
    (strategyIds || []).forEach(function(id) {
      ids[String(id)] = true;
    });
    var before = _strategies.length;
    _strategies = _strategies.filter(function(strategy) {
      return !ids[String(strategy._id)];
    });
    syncNextId();
    return saveStrategiesToDB().then(function() {
      return {
        removed: before - _strategies.length,
        total: _strategies.length
      };
    });
  }

  function clearCSVStrategies() {
    return clearResultStrategies();
  }

  function parseCSV(text, options) {
    var opts = options || {};
    var csvText = String(text || '').replace(/^\uFEFF/, '');
    var lines = csvText.split(/\r?\n/).filter(function(line) {
      return line.trim();
    });
    if (lines.length < 2) return [];
    var separator = detectSeparator(lines[0]);
    var headers = parseCsvLine(lines[0], separator).map(cleanHeaderName);
    return lines.slice(1).map(function(line) {
      var values = parseCsvLine(line, separator);
      if (values.length < 2) return null;
      var row = createBaseRecord({ _id: _nextId++, _source: 'csv' });
      headers.forEach(function(header, index) {
        row[header] = values[index] || '';
      });
      row.sources.csv = {
        fileName: opts.fileName || '',
        fingerprint: computeRowFingerprint(row),
        importedAt: new Date().toISOString(),
        viewName: inferViewName(headers),
        columns: headers.slice()
      };
      row.provenance.csvFingerprint = row.sources.csv.fingerprint;
      row.provenance.viewName = row.sources.csv.viewName;
      addEvent(row, 'imported', 'csv');
      addEvent(row, 'parsed', 'csv');
      return normalizeStrategy(row);
    }).filter(Boolean);
  }

  function detectSeparator(line) {
    var candidates = [';', ',', '\t'];
    return candidates.map(function(separator) {
      return {
        separator: separator,
        count: parseCsvLine(line, separator).length
      };
    }).sort(function(a, b) {
      return b.count - a.count;
    })[0].separator;
  }

  function parseCsvLine(line, separator) {
    var out = [];
    var current = '';
    var inQuote = false;
    var csvSeparator = separator || (line.indexOf(';') >= 0 ? ';' : ',');
    for (var i = 0; i < line.length; i += 1) {
      var ch = line[i];
      if (ch === '"') {
        if (inQuote && line[i + 1] === '"') {
          current += '"';
          i += 1;
        } else {
          inQuote = !inQuote;
        }
        continue;
      }
      if (ch === csvSeparator && !inQuote) {
        out.push(current.trim());
        current = '';
        continue;
      }
      current += ch;
    }
    out.push(current.trim());
    return out;
  }

  function loadFromCSV(input, options) {
    var rows = Array.isArray(input) ? input.map(function(row) {
      var next = createBaseRecord(row || {});
      next.sources.csv = next.sources.csv || {
        fileName: options && options.fileName || '',
        fingerprint: computeRowFingerprint(row),
        importedAt: new Date().toISOString(),
        viewName: TM_CERT_VIEW_NAME,
        columns: Object.keys(row || {})
      };
      next.provenance.csvFingerprint = next.sources.csv.fingerprint;
      next.provenance.viewName = next.sources.csv.viewName;
      addEvent(next, 'imported', 'csv');
      return normalizeStrategy(next);
    }) : parseCSV(input, options);
    return addStrategies(rows);
  }

  function loadFromSQX(fileOrFiles) {
    var files = Array.isArray(fileOrFiles) ? fileOrFiles : Array.prototype.slice.call(fileOrFiles || []);
    if (!files.length && fileOrFiles) files = [fileOrFiles];
    return Promise.all(files.map(parseSQX)).then(addStrategies);
  }

  function parseSQX(file) {
    if (!global.JSZip) return Promise.reject(new Error('JSZip no esta cargado'));
    return computeFileHash(file).then(function(hash) {
      return global.JSZip.loadAsync(file).then(function(zip) {
        var result = createBaseRecord({
        _id: _nextId++,
        _source: 'sqx',
        'Strategy Name': String(file.name || 'strategy').replace(/\.sqx$/i, ''),
        _fileData: file
        });
        result.sources.sqx = {
          fileName: file.name || 'strategy.sqx',
          hash: hash,
          importedAt: new Date().toISOString()
        };
        result.provenance.sqxHash = hash;
        result.provenance.importedAt = result.sources.sqx.importedAt;
        addEvent(result, 'imported', 'sqx');
        var strategyFile = zip.file('strategy_Portfolio.xml');
        var settingsFile = zip.file('settings.xml');
        var strategyPromise = strategyFile ? strategyFile.async('string').then(function(xml) {
          result.logic.strategyXmlPresent = true;
          result.logic.features = extractLogicFeaturesFromXml(xml);
          mergeStrategyXml(result, xml);
        }) : Promise.resolve();
        var settingsPromise = settingsFile ? settingsFile.async('string').then(function(xml) {
          result.logic.settingsXmlPresent = true;
          mergeSettingsXml(result, xml);
        }) : Promise.resolve();
        return Promise.all([strategyPromise, settingsPromise]).then(function() {
          addEvent(result, 'parsed', 'sqx');
          return normalizeStrategy(result);
        });
      });
    });
  }

  function mergeStrategyXml(result, xml) {
    if (!global.DOMParser) return;
    result._strategyXml = xml;
    if (SQX.exitPolicy && SQX.exitPolicy.detectExitComponentsFromXml) {
      result.logic.exitComponents = SQX.exitPolicy.detectExitComponentsFromXml(xml);
    }
    var doc = new global.DOMParser().parseFromString(xml, 'text/xml');
    var opts = doc.querySelector('options');
    if (opts) {
      var name = opts.querySelector('StrategyName');
      if (name && name.textContent) result['Strategy Name'] = name.textContent;
    }
    var datas = doc.querySelectorAll('Datas data');
    if (datas.length) {
      var symbol = datas[0].querySelector('symbol');
      var tf = datas[0].querySelector('timeFrame');
      if (symbol && symbol.textContent && symbol.textContent !== 'NULL') result.Symbol = symbol.textContent;
      if (tf && tf.textContent && tf.textContent !== '0') result.TimeFrame = tf.textContent;
    }
  }

  function mergeSettingsXml(result, xml) {
    if (!global.DOMParser) return;
    var doc = new global.DOMParser().parseFromString(xml, 'text/xml');
    var resultsGroup = doc.querySelector('ResultsGroup');
    if (resultsGroup && resultsGroup.getAttribute('ResultName')) {
      result['Strategy Name'] = resultsGroup.getAttribute('ResultName');
    }
    var fitnesses = doc.querySelector('Fitnesses');
    if (fitnesses) {
      result.Fitness = getNumeric(fitnesses.getAttribute('FS')) || 0;
      result._IS = getNumeric(fitnesses.getAttribute('IS')) || 0;
      result._OOS = getNumeric(fitnesses.getAttribute('OOS')) || 0;
    }
    var res = doc.querySelector('Result');
    var key = res ? res.getAttribute('resultKey') || '' : '';
    var match = key.match(/Main:\s*(.+?)\/(.+)/);
    if (match) {
      result.Symbol = result.Symbol || match[1];
      result.TimeFrame = result.TimeFrame || match[2];
    }
  }

  function extractLogicFeatures(strategy) {
    if (!strategy) return finalizeLogicFeatures({});
    if (strategy.logic && strategy.logic.features) return clone(strategy.logic.features);
    if (strategy._strategyXml) return extractLogicFeaturesFromXml(strategy._strategyXml);
    return finalizeLogicFeatures({
      indicators: String(strategy['Entry indicators'] || strategy.entry_indicators || strategy.indicators || '').split(/[,|;/]+/),
      operators: String(strategy.operators || '').split(/[,|;/]+/),
      params: [],
      rules: []
    });
  }

  function extractLogicFeaturesFromXml(xml) {
    var source = String(xml || '');
    if (!source) return finalizeLogicFeatures({});
    if (global.DOMParser) {
      try {
        var doc = new global.DOMParser().parseFromString(source, 'text/xml');
        return extractLogicFeaturesFromDoc(doc);
      } catch (_err) {
        return extractLogicFeaturesFromText(source);
      }
    }
    return extractLogicFeaturesFromText(source);
  }

  function createFeatureBag() {
    return { indicators: [], indicatorLabelsByToken: {}, operators: [], params: [], rules: [] };
  }

  function addIndicatorFeature(features, rawValue) {
    var indicator = normalizeFeatureToken(rawValue);
    if (!indicator) return '';
    features.indicators.push(indicator);
    features.indicatorLabelsByToken = features.indicatorLabelsByToken || {};
    if (!features.indicatorLabelsByToken[indicator]) {
      features.indicatorLabelsByToken[indicator] = humanizeIndicatorName(rawValue || indicator);
    }
    return indicator;
  }

  function extractLogicFeaturesFromDoc(doc) {
    var features = createFeatureBag();
    Array.prototype.forEach.call(doc.querySelectorAll('Item'), function(item) {
      var category = item.getAttribute('categoryType') || '';
      var key = item.getAttribute('key') || item.getAttribute('name') || item.getAttribute('mI') || '';
      if (category === 'indicator') {
        var indicator = addIndicatorFeature(features, key || item.getAttribute('mI') || item.getAttribute('name'));
        if (indicator) {
          Array.prototype.forEach.call(item.querySelectorAll('Param'), function(param) {
            var paramKey = normalizeFeatureToken(param.getAttribute('key') || param.getAttribute('name'));
            if (paramKey) features.params.push(indicator + ':' + paramKey + '=' + normalizeParamValue(param.textContent || param.getAttribute('defaultValue') || ''));
          });
        }
      } else if (category === 'operators' || /cross|above|below|and|or|not|greater|less/i.test(key)) {
        var operator = normalizeFeatureToken(key);
        if (operator) features.operators.push(operator);
      }
    });
    Array.prototype.forEach.call(doc.querySelectorAll('Rule'), function(rule) {
      var name = normalizeFeatureToken(rule.getAttribute('name') || '');
      if (name) features.rules.push(name);
    });
    return finalizeLogicFeatures(features);
  }

  function extractLogicFeaturesFromText(xml) {
    var features = createFeatureBag();
    String(xml || '').replace(/<Item\b[^>]*>/gi, function(tag) {
      var attrs = parseXmlAttributes(tag);
      var category = attrs.categoryType || attrs.categorytype || '';
      var key = attrs.key || attrs.name || attrs.mI || attrs.mi || '';
      if (category === 'indicator') {
        addIndicatorFeature(features, key);
      } else if (category === 'operators' || /cross|above|below|and|or|not|greater|less/i.test(key)) {
        var operator = normalizeFeatureToken(key);
        if (operator) features.operators.push(operator);
      }
      return tag;
    });
    String(xml || '').replace(/<Rule\b[^>]*name="([^"]+)"/gi, function(_match, name) {
      features.rules.push(normalizeFeatureToken(name));
      return _match;
    });
    String(xml || '').replace(/<Item\b[^>]*categoryType="indicator"[^>]*>[\s\S]*?<\/Item>/gi, function(block) {
      var itemAttrs = parseXmlAttributes(block.split('>')[0] + '>');
      var indicator = addIndicatorFeature(features, itemAttrs.key || itemAttrs.name || itemAttrs.mI || itemAttrs.mi || '');
      if (!indicator) return block;
      block.replace(/<Param\b[^>]*>([\s\S]*?)<\/Param>/gi, function(tag, value) {
        var attrs = parseXmlAttributes(tag);
        var paramKey = normalizeFeatureToken(attrs.key || attrs.name || '');
        if (paramKey) features.params.push(indicator + ':' + paramKey + '=' + normalizeParamValue(value));
        return tag;
      });
      return block;
    });
    return finalizeLogicFeatures(features);
  }

  function parseXmlAttributes(tag) {
    var attrs = {};
    String(tag || '').replace(/([A-Za-z0-9_:#.-]+)="([^"]*)"/g, function(_match, key, value) {
      attrs[key] = value;
      return _match;
    });
    return attrs;
  }

  function normalizeFeatureToken(value) {
    return String(value || '')
      .toLowerCase()
      .replace(/&quot;|&amp;quot;/g, '')
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  }

  function humanizeIndicatorName(value) {
    var raw = String(value || '').replace(/&quot;|&amp;quot;/g, '').trim();
    if (!raw) return '';
    raw = raw
      .replace(/[_-]+/g, ' ')
      .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
      .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
      .replace(/\bAtr\b/g, 'ATR')
      .replace(/\bMacd\b/g, 'MACD')
      .replace(/\bEma\b/g, 'EMA')
      .replace(/\bSma\b/g, 'SMA')
      .replace(/\bRsi\b/g, 'RSI')
      .replace(/\bCci\b/g, 'CCI')
      .replace(/\bKer\b/g, 'KER')
      .replace(/\bVwap\b/g, 'VWAP')
      .replace(/\s+/g, ' ')
      .trim();
    return raw || String(value || '');
  }

  function normalizeParamValue(value) {
    var raw = String(value || '').trim();
    var numeric = getNumeric(raw);
    if (numeric !== null) {
      if (Math.abs(numeric) <= 5) return String(Math.round(numeric * 10) / 10);
      if (Math.abs(numeric) <= 50) return String(Math.round(numeric / 5) * 5);
      return String(Math.round(numeric / 10) * 10);
    }
    return normalizeFeatureToken(raw).slice(0, 40);
  }

  function finalizeLogicFeatures(features) {
    var out = {
      indicators: uniqueSorted(features.indicators),
      operators: uniqueSorted(features.operators),
      params: uniqueSorted(features.params),
      rules: uniqueSorted(features.rules)
    };
    var labelsByToken = features.indicatorLabelsByToken || {};
    out.indicatorLabels = out.indicators.map(function(token) {
      return labelsByToken[token] || humanizeIndicatorName(token);
    });
    out.signature = uniqueSorted([].concat(out.indicators, out.operators, out.params, out.rules)).join('|');
    return out;
  }

  function uniqueSorted(values) {
    var seen = {};
    return (values || []).map(function(value) {
      return normalizeFeatureToken(value);
    }).filter(function(value) {
      if (!value || seen[value]) return false;
      seen[value] = true;
      return true;
    }).sort();
  }

  function normalizeKey(key) {
    var canonical = stripSampleSuffix(key);
    var map = {
      RecoveryFactor: 'Recovery Factor',
      CalmarRatio: 'Calmar Ratio',
      SortinoRatio: 'Sortino Ratio',
      AnnualPctReturnDDRatio: 'CAGR/Max DD %',
      NumberOfTrades: '# of trades',
      NetProfit: 'Net profit',
      DrawdownPct: 'Max DD %',
      SharpeRatio: 'Sharpe Ratio',
      WinningPct: 'Winning Percent',
      ProfitableMonthsPct: '% Profitable Months',
      'Profit Factor': 'Profit factor',
      'Win %': 'Winning Percent',
      SQN: 'SQN'
    };
    return map[canonical] || canonical;
  }

  function cleanHeaderName(key) {
    return String(key || '').replace(/^\uFEFF/, '').trim();
  }

  function sampleSuffix(key) {
    var text = cleanHeaderName(key);
    var match = text.match(/\s*\(([^()]*)\)\s*$/);
    return match ? match[1].trim() : '';
  }

  function stripSampleSuffix(key) {
    var text = cleanHeaderName(key);
    var suffix = sampleSuffix(text);
    if (!suffix) return text;
    if (/^(is|oos|full sample|full|total|portfolio|main|backtest|training|validation|test|sample\s*\d+|is\s*\d+|oos\s*\d+|\d+)$/i.test(suffix)) {
      return text.replace(/\s*\([^()]*\)\s*$/, '').trim();
    }
    return text;
  }

  function sampleRank(key) {
    var suffix = sampleSuffix(key).toLowerCase();
    if (/^(full sample|full|total|main|portfolio|127)$/.test(suffix)) return 0;
    if (!suffix) return 1;
    if (/^oos/.test(suffix)) return 2;
    if (/^is/.test(suffix)) return 3;
    return 4;
  }

  function findMetricKeyFromList(metric, keys) {
    var aliases = METRIC_ALIASES[metric] || [metric];
    var normalizedAliases = aliases.map(normalizeKey);
    var matches = (keys || []).filter(function(key) {
      return normalizedAliases.indexOf(normalizeKey(key)) >= 0;
    });
    matches.sort(function(a, b) {
      return sampleRank(a) - sampleRank(b);
    });
    return matches[0] || '';
  }

  function metricValue(strategy, metric) {
    var containers = [strategy && strategy.metrics, strategy];
    for (var i = 0; i < containers.length; i += 1) {
      var source = containers[i] || {};
      var key = findMetricKeyFromList(metric, Object.keys(source));
      if (key && source[key] !== undefined && source[key] !== '') return source[key];
    }
    if (DERIVED_METRICS[metric]) {
      return metricValue(strategy, DERIVED_METRICS[metric]);
    }
    return undefined;
  }

  function pickMetrics(strategy) {
    var metrics = {};
    REQUIRED_METRICS_ALL.forEach(function(metric) {
      var value = metricValue(strategy, metric);
      if (value !== undefined && value !== '') metrics[metric] = value;
    });
    Object.keys(_thresholds[1] || {}).concat(Object.keys(_thresholds[2] || {})).forEach(function(metric) {
      var value = metricValue(strategy, metric);
      if (value !== undefined && value !== '') metrics[metric] = value;
    });
    return metrics;
  }

  function stripRuntimeFields(strategy) {
    var copy = {};
    Object.keys(strategy || {}).forEach(function(key) {
      if (key === '_fileData') return;
      if (key === '_strategyXml') return;
      copy[key] = strategy[key];
    });
    if (copy.sources && copy.sources.sqx) {
      copy.sources = Object.assign({}, copy.sources, {
        sqx: Object.assign({}, copy.sources.sqx)
      });
      delete copy.sources.sqx.fileData;
    }
    return copy;
  }

  function normalizeStrategy(strategy) {
    var base = createBaseRecord(strategy);
    var normalized = createBaseRecord({});
    var ranks = {};
    Object.keys(strategy || {}).forEach(function(key) {
      assignNormalizedValue(normalized, ranks, key, strategy[key]);
    });
    normalized.sources = Object.assign({}, base.sources || {}, normalized.sources || {});
    normalized.metrics = Object.assign({}, base.metrics || {}, normalized.metrics || {});
    normalized.logic = Object.assign({}, base.logic || {}, normalized.logic || {});
    normalized.provenance = Object.assign({}, base.provenance || {}, normalized.provenance || {});
    normalized.provenance.events = Array.isArray(base.provenance && base.provenance.events) ? base.provenance.events.slice() : [];
    enforceCurrentProvenance(normalized.provenance);
    normalized.certification = Object.assign({}, base.certification || {}, normalized.certification || {});
    if (!normalized._id) normalized._id = _nextId++;
    normalized.Asset = normalized.Asset || detectAssetClass(normalized.Symbol || normalized._symbol || '');
    normalized.metrics = Object.assign({}, normalized.metrics, pickMetrics(normalized));
    normalized.certification = validateMetricsContract(normalized);
    normalized.certification.status = getStrategyStatus(normalized, scoreStrategy(normalized));
    return normalized;
  }

  function assignNormalizedValue(target, ranks, key, value) {
    var canonical = normalizeKey(key);
    if (value === undefined || value === '') return;
    var rank = sampleRank(key);
    if (ranks[canonical] === undefined || rank < ranks[canonical] || target[canonical] === undefined || target[canonical] === '') {
      target[canonical] = value;
      ranks[canonical] = rank;
    }
  }

  function addStrategies(newStrategies) {
    (newStrategies || []).forEach(function(strategy) {
      var next = normalizeStrategy(strategy);
      var name = next['Strategy Name'];
      var existing = findExistingStrategy(next, name);
      if (existing) {
        addEvent(existing, 'matched', next._source || '');
        Object.keys(next).forEach(function(key) {
          if (key === '_id') return;
          if (key === 'sources' || key === 'metrics' || key === 'logic' || key === 'provenance' || key === 'certification') return;
          if (key === '_source' && existing._source !== next._source) {
            existing._source = 'csv+sqx';
            return;
          }
          if (next[key] !== undefined && next[key] !== '') existing[key] = next[key];
        });
        existing.sources = Object.assign({}, existing.sources || {}, next.sources || {});
        existing.metrics = Object.assign({}, existing.metrics || {}, pickMetrics(existing), next.metrics || {});
        existing.logic = Object.assign({}, existing.logic || {}, next.logic || {});
        existing.provenance = Object.assign({}, existing.provenance || {}, next.provenance || {});
        existing.provenance.events = [].concat(existing.provenance.events || [], next.provenance.events || []);
        enforceCurrentProvenance(existing.provenance);
        existing.certification = validateMetricsContract(existing);
        existing.certification.status = getStrategyStatus(existing, scoreStrategy(existing));
      } else {
        addEvent(next, 'certified', next.certification && next.certification.valid ? 'metrics' : 'pending');
        _strategies.push(next);
      }
    });
    syncNextId();
    return saveStrategiesToDB().then(function() {
      return _strategies.slice();
    });
  }

  function findExistingStrategy(next, name) {
    var sqxHash = next.sources && next.sources.sqx && next.sources.sqx.hash;
    if (sqxHash) {
      var byHash = _strategies.find(function(item) {
        return item.sources && item.sources.sqx && item.sources.sqx.hash === sqxHash;
      });
      if (byHash) return byHash;
    }
    var key = identityKey(next);
    return _strategies.find(function(item) {
      return identityKey(item) === key || (name && item['Strategy Name'] === name);
    }) || null;
  }

  function identityKey(strategy) {
    return [
      String(strategy && strategy['Strategy Name'] || '').toLowerCase().trim(),
      String(strategy && strategy.Symbol || '').toLowerCase().trim(),
      String(strategy && strategy.TimeFrame || '').toLowerCase().trim()
    ].join('|');
  }

  function syncNextId() {
    var numericIds = _strategies.map(function(strategy) {
      return Number(strategy._id) || 0;
    });
    _nextId = Math.max.apply(Math, [0].concat(numericIds)) + 1;
  }

  function detectAssetClass(symbol) {
    if (!symbol) return 'Generic';
    var names = Object.keys(SYMBOL_PATTERNS);
    for (var i = 0; i < names.length; i += 1) {
      if (SYMBOL_PATTERNS[names[i]].test(symbol)) return names[i];
    }
    return 'Generic';
  }

  function setCapa(capa) {
    _currentCapa = Number(capa) === 2 ? 2 : 1;
    return saveConfigToDB('currentCapa', _currentCapa);
  }

  function setPreset(name) {
    if (!PRESETS[name]) return Promise.resolve(_currentPreset);
    _currentPreset = name;
    _thresholds = clone(PRESETS[name]);
    return saveConfigToDB('currentPreset', _currentPreset).then(function() {
      return saveConfigToDB('thresholds', _thresholds);
    }).then(function() {
      return _currentPreset;
    });
  }

  function getPresets() {
    return Object.keys(PRESETS);
  }

  function autoDetectPreset() {
    if (!_strategies.length) return setPreset('Generic');
    var counts = {};
    _strategies.forEach(function(strategy) {
      var asset = detectAssetClass(strategy.Symbol || strategy._symbol || '');
      counts[asset] = (counts[asset] || 0) + 1;
    });
    var best = 'Generic';
    var count = 0;
    Object.keys(counts).forEach(function(asset) {
      if (counts[asset] > count) {
        best = asset;
        count = counts[asset];
      }
    });
    return setPreset(best);
  }

  function getThresholds(capa) {
    return clone(_thresholds[capa || _currentCapa] || {});
  }

  function getRequiredMetricNames(capa, preset) {
    var selectedPreset = preset || _currentPreset;
    var selectedCapa = Number(capa || _currentCapa) === 2 ? 2 : 1;
    var thresholds = PRESETS[selectedPreset] && PRESETS[selectedPreset][selectedCapa]
      ? PRESETS[selectedPreset][selectedCapa]
      : (_thresholds[selectedCapa] || {});
    var names = Object.keys(thresholds || {});
    REQUIRED_METRICS_ALL.forEach(function(metric) {
      if (names.indexOf(metric) < 0 && metric !== 'Ret/DD Ratio') names.push(metric);
    });
    return names;
  }

  function validateMetricsContract(strategy, capa, preset) {
    var required = getRequiredMetricNames(capa, preset);
    var requiredColumns = getRequiredContractColumns();
    var keys = getContractKeys(strategy);
    var hasCsv = !!(strategy && strategy.sources && strategy.sources.csv) || String(strategy && strategy._source || '').indexOf('csv') >= 0;
    var recognizedColumns = requiredColumns.filter(function(column) {
      var value = metricValue(strategy, column);
      return findMetricKeyFromList(column, keys) && value !== undefined && value !== '';
    });
    var missingRequired = requiredColumns.filter(function(column) {
      return recognizedColumns.indexOf(column) < 0;
    });
    var missing = required.filter(function(metric) {
      var value = metricValue(strategy, metric);
      return value === undefined || value === '';
    });
    var valid = hasCsv && missing.length === 0 && missingRequired.length === 0;
    return {
      valid: valid,
      required: required,
      missing: missing,
      present: required.filter(function(metric) { return missing.indexOf(metric) < 0; }),
      sourceView: strategy && strategy.provenance && strategy.provenance.viewName || strategy && strategy.sources && strategy.sources.csv && strategy.sources.csv.viewName || '',
      schemaVersion: TM_SCHEMA_VERSION,
      certVersion: TM_CERT_VERSION,
      ruleset: TM_RULESET,
      requiredColumns: requiredColumns,
      recognizedColumns: recognizedColumns,
      missingRequired: missingRequired,
      detectedCsvProfile: detectCsvProfile(hasCsv, missingRequired, missing),
      derivedMetrics: getDerivedMetricNotes(strategy),
      status: !hasCsv ? 'Faltan métricas' : missing.length || missingRequired.length ? 'Métricas no compatibles' : 'Completa'
    };
  }

  function getContractKeys(strategy) {
    var keys = Object.keys(strategy || {}).concat(Object.keys(strategy && strategy.metrics || {}));
    if (strategy && strategy.sources && strategy.sources.csv && Array.isArray(strategy.sources.csv.columns)) {
      keys = keys.concat(strategy.sources.csv.columns);
    }
    return keys;
  }

  function hasDirectMetric(strategy, metric) {
    return getContractKeys(strategy).some(function(key) {
      return normalizeKey(key) === normalizeKey(metric);
    });
  }

  function getDerivedMetricNotes(strategy) {
    return Object.keys(DERIVED_METRICS).filter(function(metric) {
      var value = metricValue(strategy, metric);
      return value !== undefined && value !== '' && !hasDirectMetric(strategy, metric);
    }).map(function(metric) {
      return metric + ' <- ' + DERIVED_METRICS[metric];
    });
  }

  function detectCsvProfile(hasCsv, missingRequired, missing) {
    if (!hasCsv) return 'Sin CSV';
    if (!missingRequired.length && !missing.length) return TM_CERT_VIEW_NAME + ' v2';
    if (missingRequired.length) return 'CSV incompleto o de otra view';
    return 'CSV compatible con metricas derivadas';
  }

  function unique(values) {
    var seen = {};
    return (values || []).filter(function(value) {
      if (!value || seen[value]) return false;
      seen[value] = true;
      return true;
    });
  }

  function getContractDiagnostics() {
    var requiredColumns = getRequiredContractColumns();
    if (!_strategies.length) {
      return {
        total: 0,
        schemaVersion: TM_SCHEMA_VERSION,
        certVersion: TM_CERT_VERSION,
        ruleset: TM_RULESET,
        requiredColumns: requiredColumns,
        recognizedColumns: [],
        missingRequired: [],
        detectedCsvProfile: 'Sin datos cargados',
        derivedMetrics: []
      };
    }
    var contracts = _strategies.map(function(strategy) {
      return validateMetricsContract(strategy);
    });
    return {
      total: _strategies.length,
      schemaVersion: TM_SCHEMA_VERSION,
      certVersion: TM_CERT_VERSION,
      ruleset: TM_RULESET,
      requiredColumns: requiredColumns,
      recognizedColumns: unique([].concat.apply([], contracts.map(function(contract) { return contract.recognizedColumns || []; }))),
      missingRequired: unique([].concat.apply([], contracts.map(function(contract) { return contract.missingRequired || []; }))),
      detectedCsvProfile: contracts.some(function(contract) { return contract.detectedCsvProfile === 'CSV incompleto o de otra view'; })
        ? 'CSV incompleto o de otra view'
        : contracts[0].detectedCsvProfile,
      derivedMetrics: unique([].concat.apply([], contracts.map(function(contract) { return contract.derivedMetrics || []; })))
    };
  }

  function getDiversitySettings() {
    return clone(_diversitySettings);
  }

  function setDiversitySetting(key, value) {
    if (!_diversitySettings || DEFAULT_DIVERSITY_SETTINGS[key] === undefined) return Promise.resolve(getDiversitySettings());
    var numeric = Number(value);
    if (Number.isNaN(numeric)) return Promise.resolve(getDiversitySettings());
    _diversitySettings[key] = Math.max(0, Math.min(1, numeric));
    return saveConfigToDB('diversitySettings', _diversitySettings).then(getDiversitySettings);
  }

  function comparableDiversityGroup(strategy) {
    return [
      String(strategy && strategy.Symbol || '').toLowerCase().trim(),
      String(strategy && strategy.TimeFrame || '').toLowerCase().trim()
    ].join('|');
  }

  function isDiversityCandidate(strategy) {
    if (!strategy) return { ok: false, reason: 'sin estrategia' };
    if (!validateMetricsContract(strategy).valid) return { ok: false, reason: 'contrato CSV pendiente' };
    if (!hasSQX(strategy)) return { ok: false, reason: 'falta .sqx' };
    if (scoreStrategy(strategy).classification !== 'PASSED') return { ok: false, reason: 'scoring no PASSED' };
    return { ok: true, reason: 'evaluable' };
  }

  function computeTemplateSimilarity(a, b) {
    var sameGroup = comparableDiversityGroup(a) === comparableDiversityGroup(b);
    if (!sameGroup) {
      return {
        comparable: false,
        structuralSimilarity: 0,
        metricSimilarity: 0,
        hybridSimilarity: 0,
        clusterMatch: false,
        reason: 'asset/timeframe distinto'
      };
    }
    var structural = computeStructuralSimilarity(extractLogicFeatures(a), extractLogicFeatures(b));
    var metric = computeMetricSimilarity(a, b);
    var weights = normalizedDiversityWeights();
    var hybrid = roundSimilarity((structural * weights.structural) + (metric * weights.metric));
    var settings = _diversitySettings || DEFAULT_DIVERSITY_SETTINGS;
    var clusterMatch = structural >= settings.structuralThreshold
      || (structural >= settings.bridgeStructuralThreshold && metric >= settings.metricThreshold)
      || hybrid >= settings.hybridThreshold;
    return {
      comparable: true,
      structuralSimilarity: structural,
      metricSimilarity: metric,
      hybridSimilarity: hybrid,
      clusterMatch: clusterMatch,
      reason: clusterMatch ? 'similitud hibrida' : 'diverso'
    };
  }

  function normalizedDiversityWeights() {
    var structural = Number(_diversitySettings.structuralWeight);
    var metric = Number(_diversitySettings.metricWeight);
    var total = (structural || 0) + (metric || 0);
    if (!total) return { structural: 0.65, metric: 0.35 };
    return { structural: structural / total, metric: metric / total };
  }

  function computeStructuralSimilarity(aFeatures, bFeatures) {
    var indicators = jaccard(aFeatures.indicators, bFeatures.indicators);
    var operators = jaccard(aFeatures.operators, bFeatures.operators);
    var params = jaccard(aFeatures.params, bFeatures.params);
    var rules = jaccard(aFeatures.rules, bFeatures.rules);
    return roundSimilarity((indicators * 0.55) + (operators * 0.20) + (params * 0.20) + (rules * 0.05));
  }

  function computeMetricSimilarity(a, b) {
    var sims = [];
    (_diversitySettings.metrics || DIVERSITY_METRICS).forEach(function(metric) {
      var av = getNumeric(metricValue(a, metric));
      var bv = getNumeric(metricValue(b, metric));
      if (av === null || bv === null) return;
      var denom = Math.max(Math.abs(av), Math.abs(bv), 1);
      sims.push(Math.max(0, 1 - (Math.abs(av - bv) / denom)));
    });
    if (!sims.length) return 0;
    return roundSimilarity(sims.reduce(function(sum, value) { return sum + value; }, 0) / sims.length);
  }

  function jaccard(a, b) {
    var left = uniqueSorted(a);
    var right = uniqueSorted(b);
    if (!left.length && !right.length) return 0;
    var rightMap = {};
    right.forEach(function(value) { rightMap[value] = true; });
    var intersection = left.filter(function(value) { return rightMap[value]; }).length;
    var unionMap = {};
    left.concat(right).forEach(function(value) { unionMap[value] = true; });
    return intersection / Object.keys(unionMap).length;
  }

  function roundSimilarity(value) {
    return Math.max(0, Math.min(1, Math.round((Number(value) || 0) * 1000) / 1000));
  }

  function buildDiversityClusters(strategies) {
    var list = (strategies || _strategies).slice();
    var report = {
      version: DIVERSITY_VERSION,
      settings: getDiversitySettings(),
      total: list.length,
      candidates: 0,
      clusters: [],
      winners: 0,
      discarded: 0,
      byId: {},
      statuses: []
    };
    var groups = {};
    list.forEach(function(strategy) {
      var candidate = isDiversityCandidate(strategy);
      var id = String(strategy && strategy._id);
      if (!candidate.ok) {
        report.byId[id] = diversityStatus(strategy, 'No evaluable', '-', 0, candidate.reason, false);
        report.statuses.push(report.byId[id]);
        return;
      }
      report.candidates += 1;
      var key = comparableDiversityGroup(strategy);
      groups[key] = groups[key] || [];
      groups[key].push(strategy);
    });
    Object.keys(groups).forEach(function(groupKey) {
      buildGroupClusters(groups[groupKey], groupKey, report);
    });
    return report;
  }

  function buildGroupClusters(group, groupKey, report) {
    var parent = group.map(function(_item, index) { return index; });
    var pairEvidence = {};
    function find(index) {
      while (parent[index] !== index) {
        parent[index] = parent[parent[index]];
        index = parent[index];
      }
      return index;
    }
    function union(a, b) {
      var rootA = find(a);
      var rootB = find(b);
      if (rootA !== rootB) parent[rootB] = rootA;
    }
    for (var i = 0; i < group.length; i += 1) {
      for (var j = i + 1; j < group.length; j += 1) {
        var similarity = computeTemplateSimilarity(group[i], group[j]);
        pairEvidence[i + ':' + j] = similarity;
        if (similarity.clusterMatch) union(i, j);
      }
    }
    var buckets = {};
    group.forEach(function(strategy, index) {
      var root = find(index);
      buckets[root] = buckets[root] || [];
      buckets[root].push({ strategy: strategy, index: index });
    });
    Object.keys(buckets).forEach(function(root) {
      var members = buckets[root];
      var winner = chooseDiversityWinner(members.map(function(item) { return item.strategy; }));
      var clusterId = 'CL' + String(report.clusters.length + 1).padStart(2, '0');
      var cluster = {
        id: clusterId,
        group: groupKey,
        size: members.length,
        winnerId: winner && winner._id,
        members: members.map(function(item) { return item.strategy._id; })
      };
      report.clusters.push(cluster);
      members.forEach(function(item) {
        var strategy = item.strategy;
        var relation = winner && String(strategy._id) !== String(winner._id)
          ? similarityBetweenIndexes(item.index, members.find(function(candidate) { return String(candidate.strategy._id) === String(winner._id); }).index, pairEvidence)
          : { hybridSimilarity: 0, structuralSimilarity: 0, metricSimilarity: 0 };
        var status = members.length === 1 ? 'Diverso' : String(strategy._id) === String(winner._id) ? 'Ganador cluster' : 'Similar descartada';
        var canGenerate = status === 'Diverso' || status === 'Ganador cluster';
        var reason = status === 'Similar descartada'
          ? 'similar a ' + (winner['Strategy Name'] || winner._id)
          : members.length === 1 ? 'sin similares detectados' : 'mejor score del cluster';
        var payload = diversityStatus(strategy, status, clusterId, relation.hybridSimilarity || 0, reason, canGenerate, relation);
        report.byId[String(strategy._id)] = payload;
        report.statuses.push(payload);
        if (canGenerate) report.winners += 1;
        else report.discarded += 1;
      });
    });
  }

  function similarityBetweenIndexes(a, b, evidence) {
    if (a === b) return { hybridSimilarity: 0, structuralSimilarity: 0, metricSimilarity: 0 };
    return evidence[Math.min(a, b) + ':' + Math.max(a, b)] || { hybridSimilarity: 0, structuralSimilarity: 0, metricSimilarity: 0 };
  }

  function chooseDiversityWinner(strategies) {
    return (strategies || []).slice().sort(function(a, b) {
      var scoreA = scoreStrategy(a);
      var scoreB = scoreStrategy(b);
      return scoreB.pct - scoreA.pct
        || (getNumeric(metricValue(b, 'Profit factor')) || 0) - (getNumeric(metricValue(a, 'Profit factor')) || 0)
        || (getNumeric(metricValue(b, 'CAGR/Max DD %')) || 0) - (getNumeric(metricValue(a, 'CAGR/Max DD %')) || 0)
        || (getNumeric(metricValue(a, 'Max DD %')) || 999999) - (getNumeric(metricValue(b, 'Max DD %')) || 999999)
        || (getNumeric(metricValue(b, '# of trades')) || 0) - (getNumeric(metricValue(a, '# of trades')) || 0)
        || (Number(a._id) || 0) - (Number(b._id) || 0);
    })[0] || null;
  }

  function diversityStatus(strategy, status, clusterId, similarity, reason, canGenerate, relation) {
    return {
      strategyId: strategy && strategy._id,
      strategyName: strategy && strategy['Strategy Name'] || '',
      status: status,
      clusterId: clusterId,
      similarity: roundSimilarity(similarity || 0),
      structuralSimilarity: roundSimilarity(relation && relation.structuralSimilarity || 0),
      metricSimilarity: roundSimilarity(relation && relation.metricSimilarity || 0),
      reason: reason || '',
      canGenerateC2: !!canGenerate,
      version: DIVERSITY_VERSION
    };
  }

  function getDiversityReport() {
    return buildDiversityClusters(_strategies);
  }

  function getDiversityStatus(strategy) {
    var resolved = typeof strategy === 'object' ? strategy : _strategies.find(function(item) {
      return String(item._id) === String(strategy);
    });
    if (!resolved) return diversityStatus(null, 'No evaluable', '-', 0, 'estrategia no encontrada', false);
    var report = getDiversityReport();
    return report.byId[String(resolved._id)] || diversityStatus(resolved, 'No evaluable', '-', 0, 'sin estado de diversidad', false);
  }

  function hasSQX(strategy) {
    return !!(strategy && (strategy._fileData || strategy.sources && strategy.sources.sqx));
  }

  function getStrategyStatus(strategy, score) {
    var contract = validateMetricsContract(strategy);
    if (!contract.valid) return contract.status;
    if (!hasSQX(strategy)) return 'Falta SQX';
    var resolvedScore = score || scoreStrategy(strategy);
    if (resolvedScore.classification === 'PASSED') {
      var diversity = getDiversityStatus(strategy);
      if (diversity.status === 'Similar descartada') return 'Similar descartada';
      return 'Lista para C2';
    }
    return 'Completa';
  }

  function canGenerateC2(strategy) {
    var diversity = getDiversityStatus(strategy);
    return hasSQX(strategy)
      && validateMetricsContract(strategy).valid
      && scoreStrategy(strategy).classification === 'PASSED'
      && (diversity.status === 'Diverso' || diversity.status === 'Ganador cluster');
  }

  function detectExitComponents(strategy) {
    if (strategy && strategy._strategyXml && SQX.exitPolicy && SQX.exitPolicy.detectExitComponentsFromXml) {
      return SQX.exitPolicy.detectExitComponentsFromXml(strategy._strategyXml);
    }
    if (strategy && strategy.logic && Array.isArray(strategy.logic.exitComponents)) {
      return clone(strategy.logic.exitComponents);
    }
    return [];
  }

  function getExitAuditReport(strategy) {
    var components = detectExitComponents(strategy);
    var plan = SQX.exitPolicy && SQX.exitPolicy.buildDefaultExitPlan
      ? SQX.exitPolicy.buildDefaultExitPlan(strategy || {}, {})
      : { version: EXIT_POLICY_VERSION, components: components };
    var summary = SQX.exitPolicy && SQX.exitPolicy.summarizeExitPlan
      ? SQX.exitPolicy.summarizeExitPlan(plan)
      : { version: EXIT_POLICY_VERSION, detected: components.map(function(item) { return item.label || item.key; }) };
    return {
      version: EXIT_POLICY_VERSION,
      components: components,
      plan: plan,
      summary: summary
    };
  }

  function readStrategyXml(strategy) {
    if (strategy && strategy._strategyXml) return Promise.resolve(strategy._strategyXml);
    if (!strategy || !strategy._fileData || !global.JSZip) return Promise.resolve('');
    return global.JSZip.loadAsync(strategy._fileData).then(function(zip) {
      var file = zip.file('strategy_Portfolio.xml');
      return file ? file.async('string') : '';
    });
  }

  function getC2GenerationPreview(strategy, options) {
    var opts = options || {};
    return readStrategyXml(strategy).then(function(xml) {
      var trace = resolveC2Trace(strategy, opts);
      var plan = SQX.exitPolicy && SQX.exitPolicy.buildDefaultExitPlan
        ? SQX.exitPolicy.buildDefaultExitPlan(xml || strategy || {}, opts.exitOverrides || {})
        : { version: EXIT_POLICY_VERSION, components: [] };
      var summary = SQX.exitPolicy && SQX.exitPolicy.summarizeExitPlan
        ? SQX.exitPolicy.summarizeExitPlan(plan)
        : { version: EXIT_POLICY_VERSION, detected: [] };
      return {
        trace: trace,
        exitPolicyVersion: EXIT_POLICY_VERSION,
        exitPlan: plan,
        exitSummary: summary,
        blocked: !!(summary.blocked && summary.blocked.length)
      };
    });
  }

  function formatLogicIndicators(strategy) {
    var features = extractLogicFeatures(strategy);
    var tokens = uniqueSorted(features.indicators || []);
    var labels = Array.isArray(features.indicatorLabels) && features.indicatorLabels.length
      ? features.indicatorLabels.slice()
      : tokens.map(humanizeIndicatorName);
    var labelMap = {};
    labels.forEach(function(label, index) {
      if (tokens[index]) labelMap[tokens[index]] = label;
    });
    labels = tokens.map(function(token) {
      return labelMap[token] || humanizeIndicatorName(token);
    }).filter(Boolean);
    var compact = tokens.length ? tokens.slice(0, 3).join('_') : 'SIN_INDICADOR';
    if (tokens.length > 3) compact += '_plus' + String(tokens.length - 3);
    return {
      tokens: tokens,
      labels: labels,
      display: labels.length ? labels.join(', ') : 'SIN_INDICADOR',
      compact: compact
    };
  }

  function normalizeBlockSetting(value) {
    var raw = String(value || '').trim();
    if (!raw) return '';
    var token = normalizeFeatureToken(raw);
    if (C2_BLOCKSETTINGS[token]) return C2_BLOCKSETTINGS[token];
    if (/^bs_/i.test(raw)) return traceNamePart(raw, 'BS_Custom');
    return '';
  }

  function normalizeClusterId(value) {
    var raw = String(value || '').trim();
    if (!raw || raw === '-') return 'CL00';
    var digits = raw.match(/\d+/);
    if (digits) return 'CL' + String(parseInt(digits[0], 10)).padStart(2, '0');
    var token = traceNamePart(raw, 'CL00').toUpperCase();
    return token.indexOf('CL') === 0 ? token : 'CL_' + token;
  }

  function normalizeC2Direction(value) {
    var raw = String(value || '').trim().toUpperCase();
    if (raw === 'L' || raw === 'LONG_ONLY' || raw === 'LONG') return 'LONG';
    if (raw === 'S' || raw === 'SHORT_ONLY' || raw === 'SHORT') return 'SHORT';
    if (raw === 'L+S' || raw === 'LS' || raw === 'LONG_SHORT' || raw === 'BOTH') return 'BOTH';
    return raw || 'BOTH';
  }

  function firstText(strategy, keys) {
    for (var i = 0; i < keys.length; i += 1) {
      var value = strategy && strategy[keys[i]];
      if (value !== undefined && value !== null && String(value).trim() !== '') return String(value).trim();
    }
    return '';
  }

  function traceNamePart(value, fallback) {
    var text = String(value === undefined || value === null || value === '' ? fallback : value);
    if (text.normalize) text = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    text = text
      .replace(/&quot;|&amp;quot;/g, '')
      .replace(/[^A-Za-z0-9_.-]+/g, '_')
      .replace(/^_+|_+$/g, '')
      .replace(/_{2,}/g, '_');
    return text || fallback || 'NA';
  }

  function resolveC2Trace(strategy, overrides) {
    var opts = overrides || {};
    var indicators = formatLogicIndicators(strategy);
    var diversity = getDiversityStatus(strategy);
    var blockSetting = normalizeBlockSetting(
      opts.blockSetting || opts.block || firstText(strategy, ['BlockSetting', 'blocksetting', 'BS', 'bs', 'Block', 'block'])
    ) || 'BS_Custom';
    var sourceName = opts.sourceStrategyName || firstText(strategy, ['Strategy Name', 'name']) || String(strategy && strategy._id || '0');
    var indicatorBase = String(opts.indicatorBase || opts.indicator || indicators.compact || '').trim() || 'SIN_INDICADOR';
    var clusterId = normalizeClusterId(opts.clusterId || opts.numCluster || diversity.clusterId || '');
    var trace = {
      asset: traceNamePart(opts.asset || firstText(strategy, ['Symbol', 'Asset']) || 'Asset', 'Asset'),
      blockSetting: blockSetting,
      indicatorBase: traceNamePart(indicatorBase, 'SIN_INDICADOR'),
      indicatorDisplay: indicators.display,
      indicatorTokens: indicators.tokens,
      clusterId: clusterId,
      direction: normalizeC2Direction(opts.direction || firstText(strategy, ['Direction', 'direction', 'Dir', 'dir']) || 'BOTH'),
      timeframe: traceNamePart(opts.timeframe || firstText(strategy, ['TimeFrame', 'Timeframe', 'TF', 'tf']) || 'TF', 'TF'),
      sourceStrategyName: traceNamePart(sourceName, 'Strategy_0'),
      sourceStrategyDisplay: sourceName,
      diversityStatus: diversity.status || 'No evaluable',
      missing: []
    };
    if (trace.indicatorBase === 'SIN_INDICADOR') trace.missing.push('Indicador base');
    if (trace.clusterId === 'CL00') trace.missing.push('NumCluster');
    if (trace.blockSetting === 'BS_Custom') trace.missing.push('BlockSetting');
    trace.name = buildC2TemplateName(strategy, trace);
    return trace;
  }

  function buildC2TemplateName(strategy, options) {
    var opts = options || {};
    var parts = [
      'template',
      opts.asset || firstText(strategy, ['Symbol', 'Asset']) || 'Asset',
      opts.blockSetting || opts.block || firstText(strategy, ['BlockSetting', 'blocksetting', 'BS', 'bs', 'Block', 'block']) || 'BS_Custom',
      opts.indicatorBase || opts.indicator || formatLogicIndicators(strategy).compact || 'SIN_INDICADOR',
      opts.clusterId || opts.numCluster || getDiversityStatus(strategy).clusterId || 'CL00',
      opts.direction || firstText(strategy, ['Direction', 'direction', 'Dir', 'dir']) || 'BOTH',
      opts.timeframe || firstText(strategy, ['TimeFrame', 'Timeframe', 'TF', 'tf']) || 'TF',
      opts.sourceStrategyName || firstText(strategy, ['Strategy Name', 'name']) || String(strategy && strategy._id || '0')
    ];
    return parts.map(function(part, index) {
      if (index === 2) return traceNamePart(normalizeBlockSetting(part) || part, 'BS_Custom');
      if (index === 4) return traceNamePart(normalizeClusterId(part), 'CL00');
      if (index === 5) return traceNamePart(normalizeC2Direction(part), 'BOTH');
      return traceNamePart(part, index === 3 ? 'SIN_INDICADOR' : 'NA');
    }).join('_');
  }

  function getIncompleteRecords() {
    return scoreAll().filter(function(item) {
      return getStrategyStatus(item.strategy, item.score) !== 'Lista para C2';
    }).map(function(item) {
      return Object.assign({}, item.strategy, {
        certification: Object.assign({}, item.strategy.certification || {}, {
          status: getStrategyStatus(item.strategy, item.score)
        })
      });
    });
  }

  function getProvenance(strategyId) {
    var strategy = typeof strategyId === 'object' ? strategyId : _strategies.find(function(item) {
      return String(item._id) === String(strategyId);
    });
    return clone(strategy && strategy.provenance || {});
  }

  function getStrategyRecords() {
    return _strategies.map(function(strategy) {
      var copy = clone(stripRuntimeFields(strategy));
      copy.certification = Object.assign({}, copy.certification || {}, {
        status: getStrategyStatus(strategy, scoreStrategy(strategy))
      });
      return copy;
    });
  }

  function reconcileStrategySources(records) {
    var merged = [];
    (records || []).forEach(function(record) {
      var next = normalizeStrategy(record);
      var hash = next.sources && next.sources.sqx && next.sources.sqx.hash;
      var target = hash ? merged.find(function(item) {
        return item.sources && item.sources.sqx && item.sources.sqx.hash === hash;
      }) : null;
      if (!target) {
        target = merged.find(function(item) { return identityKey(item) === identityKey(next); });
      }
      if (!target) {
        merged.push(next);
        return;
      }
      Object.keys(next).forEach(function(key) {
        if (key === '_id') return;
        if (key === 'sources' || key === 'metrics' || key === 'logic' || key === 'provenance' || key === 'certification') return;
        if (next[key] !== undefined && next[key] !== '') target[key] = next[key];
      });
      target._source = target._source === next._source ? target._source : 'csv+sqx';
      target.sources = Object.assign({}, target.sources || {}, next.sources || {});
      target.metrics = Object.assign({}, target.metrics || {}, next.metrics || {});
      target.logic = Object.assign({}, target.logic || {}, next.logic || {});
      target.provenance = Object.assign({}, target.provenance || {}, next.provenance || {});
      target.provenance.events = [].concat(target.provenance.events || [], next.provenance.events || []);
      enforceCurrentProvenance(target.provenance);
      target.certification = validateMetricsContract(target);
      target.certification.status = getStrategyStatus(target, scoreStrategy(target));
    });
    return merged;
  }

  function ingestFiles(files) {
    var list = Array.prototype.slice.call(files || []);
    if (!list.length) return Promise.resolve(_strategies.slice());
    var csvFiles = list.filter(function(file) { return /\.csv$/i.test(file.name || ''); });
    var sqxFiles = list.filter(function(file) { return /\.(sqx|zip)$/i.test(file.name || ''); });
    return csvFiles.reduce(function(chain, file) {
      return chain.then(function() {
        return file.text().then(function(text) {
          return loadFromCSV(text, { fileName: file.name || '' });
        });
      });
    }, Promise.resolve(_strategies.slice())).then(function() {
      return sqxFiles.length ? loadFromSQX(sqxFiles) : _strategies.slice();
    }).then(function() {
      _strategies = reconcileStrategySources(_strategies);
      syncNextId();
      return saveStrategiesToDB();
    }).then(function() {
      return _strategies.slice();
    });
  }

  function setThreshold(kpi, field, value, capa) {
    var selectedCapa = capa || _currentCapa;
    if (!_thresholds[selectedCapa] || !_thresholds[selectedCapa][kpi]) {
      return Promise.resolve(false);
    }
    _thresholds[selectedCapa][kpi][field] = field === 'val' ? Number(value) : value;
    return saveConfigToDB('thresholds', _thresholds).then(function() {
      return true;
    });
  }

  function getNumeric(value) {
    if (value === '' || value === 'N/A' || value === 'null' || value === undefined || value === null) return null;
    var normalized = String(value).replace(/%/g, '').replace(/\s/g, '').trim();
    if (normalized.indexOf(',') >= 0 && normalized.indexOf('.') >= 0) {
      normalized = normalized.lastIndexOf(',') > normalized.lastIndexOf('.')
        ? normalized.replace(/\./g, '').replace(',', '.')
        : normalized.replace(/,/g, '');
    } else if (normalized.indexOf(',') >= 0) {
      normalized = /,\d{1,4}$/.test(normalized)
        ? normalized.replace(',', '.')
        : normalized.replace(/,/g, '');
    }
    var parsed = parseFloat(normalized);
    return Number.isNaN(parsed) ? null : parsed;
  }

  function evaluateKPI(value, threshold) {
    var number = getNumeric(value);
    if (number === null) return 'na';
    if (threshold.op === '>') return number > threshold.val ? 'pass' : 'fail';
    if (threshold.op === '>=') return number >= threshold.val ? 'pass' : 'fail';
    if (threshold.op === '<') return number < threshold.val ? 'pass' : 'fail';
    if (threshold.op === '<=') return number <= threshold.val ? 'pass' : 'fail';
    return 'na';
  }

  function scoreStrategy(strategy, capa) {
    var selectedCapa = capa || _currentCapa;
    var thresholds = _thresholds[selectedCapa] || {};
    var pass = 0;
    var fail = 0;
    var total = 0;
    var details = {};
    Object.keys(thresholds).forEach(function(kpi) {
      var value = metricValue(strategy || {}, kpi);
      var result = evaluateKPI(value, thresholds[kpi]);
      details[kpi] = { value: value, result: result, threshold: clone(thresholds[kpi]) };
      if (result !== 'na') {
        total += 1;
        if (result === 'pass') pass += 1;
        else fail += 1;
      }
    });
    var pct = total ? Math.round((pass / total) * 100) : 0;
    var classification = pct >= 80 ? 'PASSED' : pct >= 60 ? 'REVIEW' : 'FAILED';
    return { pass: pass, fail: fail, total: total, pct: pct, classification: classification, details: details };
  }

  function scoreAll(capa) {
    return _strategies.map(function(strategy) {
      return { strategy: strategy, score: scoreStrategy(strategy, capa || _currentCapa) };
    });
  }

  function getPassingStrategies(options) {
    var minPct = options && options.minPct ? options.minPct : 80;
    return scoreAll(options && options.capa).filter(function(item) {
      return item.score.pct >= minPct;
    }).map(function(item) {
      return item.strategy;
    });
  }

  function getAuditReport() {
    var scored = scoreAll();
    var diversity = getDiversityReport();
    var total = scored.length;
    var passed = scored.filter(function(item) { return item.score.classification === 'PASSED'; }).length;
    var review = scored.filter(function(item) { return item.score.classification === 'REVIEW'; }).length;
    var failed = scored.filter(function(item) { return item.score.classification === 'FAILED'; }).length;
    var certified = _strategies.filter(function(strategy) {
      return strategy._checklist && Object.keys(strategy._checklist).filter(function(key) {
        return strategy._checklist[key];
      }).length >= 4;
    }).length;
    var assets = {};
    _strategies.forEach(function(strategy) {
      var asset = strategy.Asset || 'Generic';
      assets[asset] = (assets[asset] || 0) + 1;
    });
    return {
      total: total,
      passed: passed,
      review: review,
      failed: failed,
      certified: certified,
      passedPct: total ? Math.round((passed / total) * 100) : 0,
      certifiedPct: total ? Math.round((certified / total) * 100) : 0,
      assets: assets,
      diversity: {
        version: DIVERSITY_VERSION,
        candidates: diversity.candidates,
        clusters: diversity.clusters.length,
        winners: diversity.winners,
        discarded: diversity.discarded
      },
      exitPolicy: {
        version: EXIT_POLICY_VERSION,
        detected: _strategies.reduce(function(count, strategy) {
          return count + detectExitComponents(strategy).length;
        }, 0)
      },
      capa: _currentCapa,
      preset: _currentPreset
    };
  }

  function generateC2Template(strategy, options) {
    if (!strategy || !strategy._fileData) return Promise.reject(new Error('La estrategia no tiene .sqx de origen'));
    if (!canGenerateC2(strategy)) return Promise.reject(new Error('Requiere .sqx, CSV Template Maker Cert compatible, estado PASSED y diversidad aprobada.'));
    if (!global.JSZip) return Promise.reject(new Error('JSZip no esta cargado'));
    var trace = resolveC2Trace(strategy, options || {});
    return global.JSZip.loadAsync(strategy._fileData).then(function(zip) {
      var file = zip.file('strategy_Portfolio.xml');
      if (!file) throw new Error('strategy_Portfolio.xml no existe en el .sqx');
      return file.async('string').then(function(xml) {
        return patchStrategyXml(xml, strategy, Object.assign({}, options || {}, trace));
      }).then(function(xml) {
        zip.file('strategy_Portfolio.xml', xml);
        return zip.generateAsync({ type: 'blob' });
      });
    });
  }

  function patchStrategyXml(xml, strategy, options) {
    if (!global.DOMParser || !global.XMLSerializer) return xml;
    var doc = new global.DOMParser().parseFromString(xml, 'text/xml');
    injectRandomCondition(doc, '33333333-1111-1111-3333-333333333333', 1);
    injectRandomCondition(doc, '33333333-2222-1111-3333-333333333333', 2);
    var stratNode = doc.querySelector('Strategy');
    if (stratNode) stratNode.setAttribute('allowRandom', 'true');
    var opts = doc.querySelector('options StrategyName');
    if (opts) opts.textContent = buildC2TemplateName(strategy, options);
    var patchedXml = new global.XMLSerializer().serializeToString(doc);
    if (SQX.exitPolicy && SQX.exitPolicy.buildDefaultExitPlan && SQX.exitPolicy.applyExitPlanToStrategyXml) {
      var exitPlan = SQX.exitPolicy.buildDefaultExitPlan(patchedXml, options && options.exitOverrides || {});
      patchedXml = SQX.exitPolicy.applyExitPlanToStrategyXml(patchedXml, exitPlan);
    }
    return patchedXml;
  }

  function createRandomConditionBlock(doc, idNumber) {
    var xml = '<Block><Item key="RandomCondition" name="RandomCondition" returnType="boolean" ignoreInBuilder="true" display="RandomCondition(#Identification#)" generate="random" superType="condition" categoryType="randomBlock"><Param key="#Identification#" name="Identification" type="string" controlType="randomId">RandomCondition' + idNumber + '</Param><Param key="#Chart#" name="Chart" type="data" controlType="dataVar" defaultValue="Any">0</Param><Param key="#Group#" name="Random group" type="string" controlType="randomGroupId" randomGroupType="Conditions"/></Item></Block>';
    var parsed = new global.DOMParser().parseFromString(xml, 'text/xml');
    return doc.importNode(parsed.documentElement, true);
  }

  function injectRandomCondition(doc, signalVar, idNumber) {
    var signalNode = doc.querySelector('signal[variable="' + signalVar + '"]');
    if (!signalNode || !signalNode.firstElementChild) return;
    var existingItem = signalNode.firstElementChild;
    var randomBlock = createRandomConditionBlock(doc, idNumber);
    if (existingItem.getAttribute('key') === 'AND') {
      existingItem.appendChild(randomBlock);
      return;
    }
    var andItem = doc.createElement('Item');
    andItem.setAttribute('key', 'AND');
    var existingBlock = doc.createElement('Block');
    existingBlock.appendChild(existingItem.cloneNode(true));
    andItem.appendChild(existingBlock);
    andItem.appendChild(randomBlock);
    while (signalNode.firstChild) signalNode.removeChild(signalNode.firstChild);
    signalNode.appendChild(andItem);
  }

  function buildTemplateName(strategy, options) {
    return buildC2TemplateName(strategy, options || {});
  }

  function exportTemplateZip(strategies) {
    if (!global.JSZip) return Promise.reject(new Error('JSZip no esta cargado'));
    var zip = new global.JSZip();
    var list = strategies || getPassingStrategies();
    zip.file('template-maker-audit.json', JSON.stringify(getAuditReport(), null, 2));
    zip.file('passing-strategies.json', JSON.stringify(list, null, 2));
    return zip.generateAsync({ type: 'blob' });
  }

  function dbInit() {
    if (!global.indexedDB) return Promise.resolve(null);
    if (_db) return Promise.resolve(_db);
    return new Promise(function(resolve, reject) {
      var request = global.indexedDB.open(TM_DB_NAME, TM_DB_VERSION);
      request.onupgradeneeded = function(event) {
        var db = event.target.result;
        if (!db.objectStoreNames.contains(TM_STORE_STRATEGIES)) {
          db.createObjectStore(TM_STORE_STRATEGIES, { keyPath: '_id' });
        }
        if (!db.objectStoreNames.contains(TM_STORE_CONFIG)) {
          db.createObjectStore(TM_STORE_CONFIG);
        }
      };
      request.onsuccess = function(event) {
        _db = event.target.result;
        resolve(_db);
      };
      request.onerror = function(event) {
        reject(event.target.error);
      };
    });
  }

  function saveStrategiesToDB() {
    if (!global.indexedDB) return Promise.resolve();
    if (!_db) return dbInit().then(saveStrategiesToDB);
    if (!_db) return Promise.resolve();
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_STRATEGIES], 'readwrite');
      var store = tx.objectStore(TM_STORE_STRATEGIES);
      store.clear();
      _strategies.forEach(function(strategy) {
        var copy = stripRuntimeFields(strategy);
        store.put(copy);
      });
      tx.oncomplete = resolve;
      tx.onerror = function(event) { reject(event.target.error); };
    });
  }

  function loadStrategiesFromDB() {
    if (!global.indexedDB) return Promise.resolve(_strategies.slice());
    if (!_db) return dbInit().then(loadStrategiesFromDB);
    if (!_db) return Promise.resolve(_strategies.slice());
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_STRATEGIES], 'readonly');
      var request = tx.objectStore(TM_STORE_STRATEGIES).getAll();
      request.onsuccess = function() {
        _strategies = (request.result || []).map(normalizeStrategy);
        syncNextId();
        resolve(_strategies.slice());
      };
      request.onerror = function(event) { reject(event.target.error); };
    });
  }

  function saveConfigToDB(key, value) {
    if (!global.indexedDB) return Promise.resolve();
    if (!_db) return dbInit().then(function() { return saveConfigToDB(key, value); });
    if (!_db) return Promise.resolve();
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_CONFIG], 'readwrite');
      tx.objectStore(TM_STORE_CONFIG).put(value, key);
      tx.oncomplete = resolve;
      tx.onerror = function(event) { reject(event.target.error); };
    });
  }

  function readConfigFromDB(key) {
    if (!global.indexedDB || !_db) return Promise.resolve(undefined);
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_CONFIG], 'readonly');
      var request = tx.objectStore(TM_STORE_CONFIG).get(key);
      request.onsuccess = function() { resolve(request.result); };
      request.onerror = function(event) { reject(event.target.error); };
    });
  }

  function persistSchemaVersion() {
    return saveConfigToDB('schemaVersion', TM_SCHEMA_VERSION)
      .then(function() { return saveConfigToDB('certVersion', TM_CERT_VERSION); })
      .then(function() { return saveConfigToDB('ruleset', TM_RULESET); });
  }

  function ensureSchemaVersion() {
    if (!global.indexedDB || !_db) return Promise.resolve();
    return readConfigFromDB('schemaVersion').then(function(version) {
      if (version === TM_SCHEMA_VERSION) return persistSchemaVersion();
      _strategies = [];
      _nextId = 1;
      resetRuntimeConfig();
      return clearDB().then(persistSchemaVersion);
    });
  }

  function loadConfigFromDB() {
    if (!global.indexedDB || !_db) return Promise.resolve();
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_CONFIG], 'readonly');
      var store = tx.objectStore(TM_STORE_CONFIG);
    var keys = ['currentCapa', 'currentPreset', 'thresholds', 'diversitySettings'];
      var pending = keys.length;
      var config = {};
      keys.forEach(function(key) {
        var request = store.get(key);
        request.onsuccess = function() {
          config[key] = request.result;
          pending -= 1;
          if (!pending) {
            applyStoredConfig(config);
            resolve();
          }
        };
        request.onerror = function(event) { reject(event.target.error); };
      });
    });
  }

  function applyStoredConfig(payload) {
    if (!payload) return;
    if (payload.currentCapa) _currentCapa = Number(payload.currentCapa) === 2 ? 2 : 1;
    if (payload.currentPreset && PRESETS[payload.currentPreset]) _currentPreset = payload.currentPreset;
    if (payload.thresholds) _thresholds = payload.thresholds;
    if (payload.diversitySettings) {
      _diversitySettings = Object.assign({}, clone(DEFAULT_DIVERSITY_SETTINGS), payload.diversitySettings);
      _diversitySettings.metrics = DIVERSITY_METRICS.slice();
    }
  }

  function clearDB() {
    if (!global.indexedDB) return Promise.resolve();
    if (!_db) return dbInit().then(clearDB);
    if (!_db) return Promise.resolve();
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_STRATEGIES, TM_STORE_CONFIG], 'readwrite');
      tx.objectStore(TM_STORE_STRATEGIES).clear();
      tx.objectStore(TM_STORE_CONFIG).clear();
      tx.oncomplete = resolve;
      tx.onerror = function(event) { reject(event.target.error); };
    });
  }

  var api = {
    init: init,
    reset: reset,
    clearResultStrategies: clearResultStrategies,
    deleteResultStrategies: deleteResultStrategies,
    clearCSVStrategies: clearCSVStrategies,
    ingestFiles: ingestFiles,
    computeFileHash: computeFileHash,
    loadFromCSV: loadFromCSV,
    loadFromSQX: loadFromSQX,
    getStrategies: function() { return _strategies.slice(); },
    getStrategyRecords: getStrategyRecords,
    getIncompleteRecords: getIncompleteRecords,
    getProvenance: getProvenance,
    getPassingStrategies: getPassingStrategies,
    setCapa: setCapa,
    getCapa: function() { return _currentCapa; },
    setPreset: setPreset,
    getCurrentPreset: function() { return _currentPreset; },
    getPresets: getPresets,
    autoDetectPreset: autoDetectPreset,
    getThresholds: getThresholds,
    getRequiredMetricNames: getRequiredMetricNames,
    validateMetricsContract: validateMetricsContract,
    getContractDiagnostics: getContractDiagnostics,
    extractLogicFeatures: extractLogicFeatures,
    formatLogicIndicators: formatLogicIndicators,
    computeTemplateSimilarity: computeTemplateSimilarity,
    buildDiversityClusters: buildDiversityClusters,
    getDiversityReport: getDiversityReport,
    getDiversitySettings: getDiversitySettings,
    setDiversitySetting: setDiversitySetting,
    getDiversityStatus: getDiversityStatus,
    detectExitComponents: detectExitComponents,
    getC2GenerationPreview: getC2GenerationPreview,
    getExitAuditReport: getExitAuditReport,
    reconcileStrategySources: reconcileStrategySources,
    getStrategyStatus: getStrategyStatus,
    canGenerateC2: canGenerateC2,
    setThreshold: setThreshold,
    scoreStrategy: scoreStrategy,
    scoreAll: scoreAll,
    getAuditReport: getAuditReport,
    resolveC2Trace: resolveC2Trace,
    buildC2TemplateName: buildC2TemplateName,
    generateC2Template: generateC2Template,
    exportTemplateZip: exportTemplateZip,
    dbInit: dbInit,
    saveStrategies: saveStrategiesToDB,
    loadStrategies: loadStrategiesFromDB,
    clearDB: clearDB,
    parseCSV: parseCSV,
    parseSQX: parseSQX,
    detectAssetClass: detectAssetClass,
    getInfoColumns: function() { return ['Strategy Name', 'Asset', 'Symbol', 'TimeFrame', 'Fitness']; },
    getKPIColumns: function(capa) { return Object.keys(_thresholds[capa || _currentCapa] || {}); }
  };

  SQX.templateMaker = SQX.templateMaker || api;
  if (SQX.registerModule) SQX.registerModule('template-maker', SQX.templateMaker);
})(window);
