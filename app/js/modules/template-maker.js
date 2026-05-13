(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var TM_DB_NAME = 'SQXTemplateMakerDB';
  var TM_DB_VERSION = 1;
  var TM_STORE_STRATEGIES = 'tm_strategies';
  var TM_STORE_CONFIG = 'tm_config';

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

  function parseCSV(text) {
    var lines = String(text || '').split(/\r?\n/).filter(function(line) {
      return line.trim();
    });
    if (lines.length < 2) return [];
    var headers = parseCsvLine(lines[0]);
    return lines.slice(1).map(function(line) {
      var values = parseCsvLine(line);
      if (values.length < 2) return null;
      var row = { _id: _nextId++, _source: 'csv' };
      headers.forEach(function(header, index) {
        row[header] = values[index] || '';
      });
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

  function loadFromCSV(input) {
    var rows = Array.isArray(input) ? input.map(normalizeStrategy) : parseCSV(input);
    return addStrategies(rows);
  }

  function loadFromSQX(fileOrFiles) {
    var files = Array.isArray(fileOrFiles) ? fileOrFiles : Array.prototype.slice.call(fileOrFiles || []);
    if (!files.length && fileOrFiles) files = [fileOrFiles];
    return Promise.all(files.map(parseSQX)).then(addStrategies);
  }

  function parseSQX(file) {
    if (!global.JSZip) return Promise.reject(new Error('JSZip no esta cargado'));
    return global.JSZip.loadAsync(file).then(function(zip) {
      var result = {
        _id: _nextId++,
        _source: 'sqx',
        'Strategy Name': String(file.name || 'strategy').replace(/\.sqx$/i, ''),
        _fileData: file
      };
      var strategyFile = zip.file('strategy_Portfolio.xml');
      var settingsFile = zip.file('settings.xml');
      var strategyPromise = strategyFile ? strategyFile.async('string').then(function(xml) {
        mergeStrategyXml(result, xml);
      }) : Promise.resolve();
      var settingsPromise = settingsFile ? settingsFile.async('string').then(function(xml) {
        mergeSettingsXml(result, xml);
      }) : Promise.resolve();
      return Promise.all([strategyPromise, settingsPromise]).then(function() {
        return normalizeStrategy(result);
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
      'Profit Factor': 'Profit factor',
      'Win %': 'Winning Percent',
      SQN: 'SQN'
    };
    return map[key] || key;
  }

  function normalizeStrategy(strategy) {
    var normalized = {};
    Object.keys(strategy || {}).forEach(function(key) {
      normalized[normalizeKey(key)] = strategy[key];
    });
    if (!normalized._id) normalized._id = _nextId++;
    normalized.Asset = normalized.Asset || detectAssetClass(normalized.Symbol || normalized._symbol || '');
    return normalized;
  }

  function addStrategies(newStrategies) {
    (newStrategies || []).forEach(function(strategy) {
      var next = normalizeStrategy(strategy);
      var name = next['Strategy Name'];
      var existing = name ? _strategies.find(function(item) {
        return item['Strategy Name'] === name;
      }) : null;
      if (existing) {
        Object.keys(next).forEach(function(key) {
          if (key === '_id') return;
          if (key === '_source' && existing._source !== next._source) {
            existing._source = 'csv+sqx';
            return;
          }
          if (next[key] !== undefined && next[key] !== '') existing[key] = next[key];
        });
      } else {
        _strategies.push(next);
      }
    });
    syncNextId();
    return saveStrategiesToDB().then(function() {
      return _strategies.slice();
    });
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
      var result = evaluateKPI((strategy || {})[kpi], thresholds[kpi]);
      details[kpi] = { value: (strategy || {})[kpi], result: result, threshold: clone(thresholds[kpi]) };
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
        var copy = Object.assign({}, strategy);
        delete copy._fileData;
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
        _strategies = request.result || [];
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
    loadFromCSV: loadFromCSV,
    loadFromSQX: loadFromSQX,
    getStrategies: function() { return _strategies.slice(); },
    getPassingStrategies: getPassingStrategies,
    setCapa: setCapa,
    getCapa: function() { return _currentCapa; },
    setPreset: setPreset,
    getCurrentPreset: function() { return _currentPreset; },
    getPresets: getPresets,
    autoDetectPreset: autoDetectPreset,
    getThresholds: getThresholds,
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
