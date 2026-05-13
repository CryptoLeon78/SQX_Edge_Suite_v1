(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var TM_DB_NAME = 'SQXTemplateMakerDB';
  var TM_DB_VERSION = 1;
  var TM_STORE_STRATEGIES = 'tm_strategies';
  var TM_STORE_CONFIG = 'tm_config';
  var TM_CERT_VERSION = 'TMA2.1';
  var TM_RULESET = 'template-maker-cert-v1';
  var TM_CERT_VIEW_NAME = 'Template Maker Cert';
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
    '% Profitable Months',
    'Ret/DD Ratio'
  ];
  var METRIC_ALIASES = {
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
  var _nextId = 1;

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function createBaseRecord(source) {
    var record = Object.assign({
      sources: {},
      metrics: {},
      logic: {},
      provenance: {
        certVersion: TM_CERT_VERSION,
        ruleset: TM_RULESET,
        importedAt: new Date().toISOString(),
        events: []
      },
      certification: {}
    }, source || {});
    record.sources = Object.assign({}, record.sources || {});
    record.metrics = Object.assign({}, record.metrics || {});
    record.logic = Object.assign({}, record.logic || {});
    record.provenance = Object.assign({
      certVersion: TM_CERT_VERSION,
      ruleset: TM_RULESET,
      importedAt: new Date().toISOString(),
      events: []
    }, record.provenance || {});
    record.provenance.events = Array.isArray(record.provenance.events) ? record.provenance.events.slice() : [];
    record.certification = Object.assign({}, record.certification || {});
    return record;
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
    var required = REQUIRED_METRICS_ALL.filter(function(metric) {
      return metric !== 'Ret/DD Ratio';
    });
    var compatible = required.every(function(metric) {
      return findMetricKeyFromList(metric, names);
    });
    return compatible ? TM_CERT_VIEW_NAME : 'CSV compatible no identificado';
  }

  function init() {
    return dbInit().then(loadConfigFromDB).then(loadStrategiesFromDB).catch(function() {
      return _strategies.slice();
    });
  }

  function reset() {
    _strategies = [];
    _nextId = 1;
    return clearDB();
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
    var lines = String(text || '').split(/\r?\n/).filter(function(line) {
      return line.trim();
    });
    if (lines.length < 2) return [];
    var headers = parseCsvLine(lines[0]);
    return lines.slice(1).map(function(line) {
      var values = parseCsvLine(line);
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

  function parseCsvLine(line) {
    var out = [];
    var current = '';
    var inQuote = false;
    var separator = line.indexOf(';') >= 0 ? ';' : ',';
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
      if (ch === separator && !inQuote) {
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

  function normalizeKey(key) {
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
    return map[key] || key;
  }

  function findMetricKeyFromList(metric, keys) {
    var aliases = METRIC_ALIASES[metric] || [metric];
    for (var i = 0; i < aliases.length; i += 1) {
      if ((keys || []).indexOf(aliases[i]) >= 0) return aliases[i];
    }
    return '';
  }

  function metricValue(strategy, metric) {
    var aliases = METRIC_ALIASES[metric] || [metric];
    for (var i = 0; i < aliases.length; i += 1) {
      var key = aliases[i];
      if (strategy && strategy[key] !== undefined && strategy[key] !== '') return strategy[key];
      if (strategy && strategy.metrics && strategy.metrics[key] !== undefined && strategy.metrics[key] !== '') return strategy.metrics[key];
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
    Object.keys(strategy || {}).forEach(function(key) {
      normalized[normalizeKey(key)] = strategy[key];
    });
    normalized.sources = Object.assign({}, base.sources || {}, normalized.sources || {});
    normalized.metrics = Object.assign({}, base.metrics || {}, normalized.metrics || {});
    normalized.logic = Object.assign({}, base.logic || {}, normalized.logic || {});
    normalized.provenance = Object.assign({}, base.provenance || {}, normalized.provenance || {});
    normalized.provenance.events = Array.isArray(base.provenance && base.provenance.events) ? base.provenance.events.slice() : [];
    normalized.certification = Object.assign({}, base.certification || {}, normalized.certification || {});
    if (!normalized._id) normalized._id = _nextId++;
    normalized.Asset = normalized.Asset || detectAssetClass(normalized.Symbol || normalized._symbol || '');
    normalized.metrics = Object.assign({}, normalized.metrics, pickMetrics(normalized));
    normalized.certification = validateMetricsContract(normalized);
    normalized.certification.status = getStrategyStatus(normalized, scoreStrategy(normalized));
    return normalized;
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
    var keys = Object.keys(strategy || {}).concat(Object.keys(strategy && strategy.metrics || {}));
    var hasCsv = !!(strategy && strategy.sources && strategy.sources.csv) || String(strategy && strategy._source || '').indexOf('csv') >= 0;
    var missing = required.filter(function(metric) {
      if (metric === 'Ret/DD Ratio') return false;
      return !findMetricKeyFromList(metric, keys) || metricValue(strategy, metric) === undefined || metricValue(strategy, metric) === '';
    });
    var valid = hasCsv && missing.length === 0;
    return {
      valid: valid,
      required: required,
      missing: missing,
      present: required.filter(function(metric) { return missing.indexOf(metric) < 0; }),
      sourceView: strategy && strategy.provenance && strategy.provenance.viewName || strategy && strategy.sources && strategy.sources.csv && strategy.sources.csv.viewName || '',
      certVersion: TM_CERT_VERSION,
      ruleset: TM_RULESET,
      status: !hasCsv ? 'Faltan métricas' : missing.length ? 'Métricas no compatibles' : 'Completa'
    };
  }

  function hasSQX(strategy) {
    return !!(strategy && (strategy._fileData || strategy.sources && strategy.sources.sqx));
  }

  function getStrategyStatus(strategy, score) {
    var contract = validateMetricsContract(strategy);
    if (!contract.valid) return contract.status;
    if (!hasSQX(strategy)) return 'Falta SQX';
    var resolvedScore = score || scoreStrategy(strategy);
    if (resolvedScore.classification === 'PASSED') return 'Lista para C2';
    return 'Completa';
  }

  function canGenerateC2(strategy) {
    return hasSQX(strategy) && validateMetricsContract(strategy).valid && scoreStrategy(strategy).classification === 'PASSED';
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
    var csvPromise = Promise.all(csvFiles.map(function(file) {
      return file.text().then(function(text) {
        return loadFromCSV(text, { fileName: file.name || '' });
      });
    }));
    var sqxPromise = sqxFiles.length ? loadFromSQX(sqxFiles) : Promise.resolve(_strategies.slice());
    return csvPromise.then(function() {
      return sqxPromise;
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
    var normalized = String(value).replace(/%/g, '').replace(/,/g, '').trim();
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
      capa: _currentCapa,
      preset: _currentPreset
    };
  }

  function generateC2Template(strategy, options) {
    if (!strategy || !strategy._fileData) return Promise.reject(new Error('La estrategia no tiene .sqx de origen'));
    if (!canGenerateC2(strategy)) return Promise.reject(new Error('Requiere .sqx, CSV Template Maker Cert compatible y estado PASSED.'));
    if (!global.JSZip) return Promise.reject(new Error('JSZip no esta cargado'));
    return global.JSZip.loadAsync(strategy._fileData).then(function(zip) {
      var file = zip.file('strategy_Portfolio.xml');
      if (!file) throw new Error('strategy_Portfolio.xml no existe en el .sqx');
      return file.async('string').then(function(xml) {
        return patchStrategyXml(xml, strategy, options || {});
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
    updateExits(doc, 'Long entry', 1);
    updateExits(doc, 'Short entry', 2);
    var stratNode = doc.querySelector('Strategy');
    if (stratNode) stratNode.setAttribute('allowRandom', 'true');
    var opts = doc.querySelector('options StrategyName');
    if (opts) opts.textContent = buildTemplateName(strategy, options);
    return new global.XMLSerializer().serializeToString(doc);
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

  function findRule(doc, ruleName) {
    var rules = doc.querySelectorAll('Rule');
    for (var i = 0; i < rules.length; i += 1) {
      if (rules[i].getAttribute('name') === ruleName) return rules[i];
    }
    return null;
  }

  function updateExits(doc, ruleName, idNumber) {
    var ruleNode = findRule(doc, ruleName);
    if (!ruleNode) return;
    var enterItem = ruleNode.querySelector('Then Item[key="EnterAtMarket"]');
    if (!enterItem) return;
    var exitBars = enterItem.querySelector('Param[key="#ExitAfterBars.ExitAfterBars#"]');
    if (exitBars) exitBars.textContent = '0';
    randomizeExitParam(doc, enterItem, '#ProfitTarget.ProfitTarget#', 'SQ.Formulas.SLPT.FixedValue', idNumber);
    randomizeExitParam(doc, enterItem, '#StopLoss.StopLoss#', 'SQ.Formulas.SLPT.FixedValue', idNumber);
    randomizeExitParam(doc, enterItem, '#TrailingStop.TrailingStop#', 'SQ.Formulas.RangeLevel.FixedValue', idNumber);
  }

  function randomizeExitParam(doc, enterItem, key, formulaKey, idNumber) {
    var param = enterItem.querySelector('Param[key="' + key + '"]');
    if (!param) return;
    param.setAttribute('generate', 'random');
    param.setAttribute('randomValue', 'default');
    param.setAttribute('identification', 'EnterAtMarket' + idNumber);
    while (param.firstChild) param.removeChild(param.firstChild);
    param.appendChild(createFixedValueFormula(doc, formulaKey));
  }

  function createFixedValueFormula(doc, formulaKey) {
    var formula = doc.createElement('Formula');
    formula.setAttribute('key', formulaKey);
    var param = doc.createElement('Param');
    param.setAttribute('key', '#Value#');
    param.setAttribute('name', 'Value');
    param.setAttribute('type', 'double');
    param.setAttribute('defaultValue', '50');
    param.setAttribute('controlType', 'jspinnerVar');
    param.setAttribute('minValue', '1');
    param.setAttribute('maxValue', '9999999');
    param.setAttribute('step', '1');
    param.setAttribute('postfix', 'pips');
    param.setAttribute('builderMinValue', '5');
    param.setAttribute('builderMaxValue', '500');
    param.setAttribute('builderStep', '1');
    param.textContent = '50';
    formula.appendChild(param);
    return formula;
  }

  function buildTemplateName(strategy, options) {
    var parts = [
      'template',
      options.asset || strategy.Symbol || 'Asset',
      options.direction || 'BOTH',
      options.timeframe || strategy.TimeFrame || 'TF',
      options.indicator || 'IND',
      options.block || 'EDGE',
      String(strategy['Strategy Name'] || strategy._id || '0').replace(/\s+/g, '_')
    ];
    return parts.join('_').replace(/[^A-Za-z0-9_.-]+/g, '_');
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

  function loadConfigFromDB() {
    if (!global.indexedDB || !_db) return Promise.resolve();
    return new Promise(function(resolve, reject) {
      var tx = _db.transaction([TM_STORE_CONFIG], 'readonly');
      var store = tx.objectStore(TM_STORE_CONFIG);
      var keys = ['currentCapa', 'currentPreset', 'thresholds'];
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
    reconcileStrategySources: reconcileStrategySources,
    getStrategyStatus: getStrategyStatus,
    canGenerateC2: canGenerateC2,
    setThreshold: setThreshold,
    scoreStrategy: scoreStrategy,
    scoreAll: scoreAll,
    getAuditReport: getAuditReport,
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
