(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var DEFAULT_REQUIRED_FIELDS = ['strategy_name', 'symbol', 'profit_factor', 'return_drawdown', 'trades'];
  var DEFAULT_RECOMMENDED_FIELDS = ['net_profit', 'drawdown_pct', 'r_expectancy', 'stagnation', 'entry_indicators', 'filters_result'];
  var DEFAULT_MAX_BYTES = 1024 * 1024;
  var DEFAULT_MAX_ROWS = 5000;

  var FIELD_ALIASES = {
    strategy_name: ['Strategy Name', 'Strategy', 'Name'],
    symbol: ['Symbol', 'Market', 'Asset'],
    net_profit: ['Net profit', 'Net Profit', 'NetProfit'],
    profit_factor: ['Profit factor', 'Profit Factor', 'PF'],
    return_drawdown: ['Return/Drawdown', 'Return / Drawdown', 'Ret/DD', 'CAGR/Max DD'],
    drawdown_pct: ['Drawdown %', 'Max Drawdown %', 'DD %'],
    trades: ['# trades', 'Trades', 'Number of trades'],
    r_expectancy: ['R Expectancy', 'Expectancy', 'R-Expectancy'],
    stagnation: ['Stagnation', 'Stagnation %', 'Max Stagnation'],
    entry_indicators: ['Entry indicators', 'Entry Indicators', 'Indicators'],
    filters_result: ['Filters Result', 'Forward', 'OOS Result']
  };

  var NUMERIC_FIELDS = {
    net_profit: true,
    profit_factor: true,
    return_drawdown: true,
    drawdown_pct: true,
    trades: true,
    r_expectancy: true,
    stagnation: true
  };

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function escapeHtml(value) {
    var formatters = SQX.formatters || {};
    if (formatters.escapeHtml) return formatters.escapeHtml(value);
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function normalizeHeader(value) {
    return String(value == null ? '' : value)
      .replace(/^\uFEFF/, '')
      .trim()
      .replace(/\s+/g, ' ')
      .toLowerCase();
  }

  function aliasIndex(aliasMap) {
    var aliases = aliasMap || FIELD_ALIASES;
    var index = {};
    Object.keys(aliases).forEach(function(field) {
      aliases[field].forEach(function(alias) {
        index[normalizeHeader(alias)] = field;
      });
    });
    return index;
  }

  function detectDelimiter(text) {
    var sample = String(text || '').split(/\r?\n/).find(function(line) {
      return line.trim();
    }) || '';
    var inQuotes = false;
    var comma = 0;
    var semicolon = 0;
    for (var i = 0; i < sample.length; i += 1) {
      var ch = sample.charAt(i);
      if (ch === '"') {
        if (inQuotes && sample.charAt(i + 1) === '"') i += 1;
        else inQuotes = !inQuotes;
      } else if (!inQuotes && ch === ',') comma += 1;
      else if (!inQuotes && ch === ';') semicolon += 1;
    }
    return semicolon > comma ? ';' : ',';
  }

  function parseCsv(text, options) {
    var opts = options || {};
    var delimiter = opts.delimiter || detectDelimiter(text);
    var rows = [];
    var row = [];
    var cell = '';
    var inQuotes = false;
    var source = String(text == null ? '' : text).replace(/\r\n/g, '\n').replace(/\r/g, '\n');

    for (var i = 0; i < source.length; i += 1) {
      var ch = source.charAt(i);
      if (ch === '"') {
        if (inQuotes && source.charAt(i + 1) === '"') {
          cell += '"';
          i += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (!inQuotes && ch === delimiter) {
        row.push(cell);
        cell = '';
      } else if (!inQuotes && ch === '\n') {
        row.push(cell);
        rows.push(row);
        row = [];
        cell = '';
      } else {
        cell += ch;
      }
    }

    if (inQuotes) {
      return { delimiter: delimiter, rows: rows, errors: ['csv_unclosed_quote'] };
    }
    if (cell.length || row.length || source.length) {
      row.push(cell);
      rows.push(row);
    }

    rows = rows.filter(function(items) {
      return items.some(function(item) { return String(item || '').trim() !== ''; });
    });
    return { delimiter: delimiter, rows: rows, errors: [] };
  }

  function parseNumber(value) {
    if (value == null || value === '') return { value: null, ok: false, reason: 'blank' };
    if (typeof value === 'number') {
      return isFinite(value) ? { value: value, ok: true } : { value: null, ok: false, reason: 'not_finite' };
    }

    var raw = String(value).trim();
    if (!raw) return { value: null, ok: false, reason: 'blank' };
    var hadPercent = raw.indexOf('%') !== -1;
    raw = raw
      .replace(/[%]/g, '')
      .replace(/\s/g, '')
      .replace(/[$€£]/g, '');

    var comma = raw.lastIndexOf(',');
    var dot = raw.lastIndexOf('.');
    if (comma !== -1 && dot !== -1) {
      if (comma > dot) raw = raw.replace(/\./g, '').replace(',', '.');
      else raw = raw.replace(/,/g, '');
    } else if (comma !== -1) {
      var decimals = raw.length - comma - 1;
      if (decimals > 0 && decimals <= 4) raw = raw.replace(',', '.');
      else raw = raw.replace(/,/g, '');
    }

    raw = raw.replace(/[^0-9.+-]/g, '');
    var parsed = parseFloat(raw);
    if (!isFinite(parsed)) return { value: null, ok: false, reason: 'nan' };
    return { value: parsed, ok: true, percent: hadPercent };
  }

  function resolveColumnAliases(headers, options) {
    var opts = options || {};
    var index = aliasIndex(opts.aliases);
    var columns = {};
    var warnings = [];
    var unknown = [];

    (headers || []).forEach(function(header, position) {
      var normalized = normalizeHeader(header);
      if (!normalized) return;
      var field = index[normalized];
      if (!field) {
        unknown.push({ header: header, index: position });
        return;
      }
      if (columns[field] != null) {
        warnings.push({
          code: 'duplicate_alias',
          field: field,
          header: header,
          existingIndex: columns[field],
          duplicateIndex: position
        });
        return;
      }
      columns[field] = position;
    });

    return { columns: columns, warnings: warnings, unknown: unknown };
  }

  function normalizeRecord(row, headers, columns, rowNumber) {
    var raw = {};
    var metrics = {};
    var warnings = [];

    headers.forEach(function(header, index) {
      raw[header] = row[index] == null ? '' : String(row[index]).trim();
    });

    Object.keys(columns).forEach(function(field) {
      var value = row[columns[field]];
      if (NUMERIC_FIELDS[field]) {
        var parsed = parseNumber(value);
        metrics[field] = parsed.ok ? parsed.value : null;
        if (!parsed.ok) {
          warnings.push({ code: 'non_numeric_metric', field: field, rowNumber: rowNumber, value: value });
        }
      } else {
        metrics[field] = value == null ? '' : String(value).trim();
      }
    });

    return {
      rowNumber: rowNumber,
      raw: raw,
      metrics: metrics,
      safe: {
        strategy_name: escapeHtml(metrics.strategy_name || ''),
        symbol: escapeHtml(metrics.symbol || '')
      },
      warnings: warnings
    };
  }

  function validateRecords(records, options) {
    var opts = options || {};
    var role = opts.role || 'challenger';
    var required = opts.requiredFields || DEFAULT_REQUIRED_FIELDS;
    var recommended = opts.recommendedFields || DEFAULT_RECOMMENDED_FIELDS;
    var errors = [];
    var warnings = [];

    if (role === 'champion' && records.length !== 1) {
      errors.push({ code: 'champion_row_count_invalid', expected: 1, actual: records.length });
    }
    if (role === 'challenger' && records.length < 1) {
      errors.push({ code: 'challenger_rows_missing' });
    }

    records.forEach(function(record) {
      required.forEach(function(field) {
        var value = record.metrics[field];
        if (value == null || value === '') {
          errors.push({ code: 'required_field_missing', field: field, rowNumber: record.rowNumber });
        }
      });
      recommended.forEach(function(field) {
        if (!(field in record.metrics) || record.metrics[field] == null || record.metrics[field] === '') {
          warnings.push({ code: 'recommended_field_missing', field: field, rowNumber: record.rowNumber });
        }
      });
      record.warnings.forEach(function(warning) {
        warnings.push(warning);
      });
    });

    return { errors: errors, warnings: warnings };
  }

  function parseStrategyCsv(text, options) {
    var opts = options || {};
    var errors = [];
    var warnings = [];
    var source = String(text == null ? '' : text);
    var maxBytes = opts.maxBytes || DEFAULT_MAX_BYTES;
    var maxRows = opts.maxRows || DEFAULT_MAX_ROWS;

    if (!source.trim()) {
      return { ok: false, records: [], headers: [], delimiter: opts.delimiter || ',', errors: ['csv_empty'], warnings: [] };
    }
    if (source.length > maxBytes) errors.push({ code: 'csv_too_large', maxBytes: maxBytes, actualBytes: source.length });

    var parsed = parseCsv(source, opts);
    parsed.errors.forEach(function(error) { errors.push({ code: error }); });
    if (!parsed.rows.length) errors.push({ code: 'csv_header_missing' });

    var headers = parsed.rows[0] || [];
    if (!headers.length || !headers.some(function(header) { return String(header || '').trim(); })) {
      errors.push({ code: 'csv_header_missing' });
    }

    var aliasResolution = resolveColumnAliases(headers, opts);
    warnings = warnings.concat(aliasResolution.warnings);
    aliasResolution.unknown.forEach(function(item) {
      warnings.push({ code: 'unknown_column', header: item.header, index: item.index });
    });

    var required = opts.requiredFields || DEFAULT_REQUIRED_FIELDS;
    required.forEach(function(field) {
      if (aliasResolution.columns[field] == null) {
        errors.push({ code: 'required_column_missing', field: field });
      }
    });

    var dataRows = parsed.rows.slice(1);
    if (dataRows.length > maxRows) {
      errors.push({ code: 'csv_too_many_rows', maxRows: maxRows, actualRows: dataRows.length });
      dataRows = dataRows.slice(0, maxRows);
    }

    var records = dataRows.map(function(row, index) {
      return normalizeRecord(row, headers, aliasResolution.columns, index + 2);
    });
    var validation = validateRecords(records, {
      role: opts.role,
      requiredFields: required,
      recommendedFields: opts.recommendedFields || DEFAULT_RECOMMENDED_FIELDS
    });
    errors = errors.concat(validation.errors);
    warnings = warnings.concat(validation.warnings);

    return {
      ok: errors.length === 0,
      delimiter: parsed.delimiter,
      headers: headers,
      columns: aliasResolution.columns,
      records: records,
      errors: errors,
      warnings: warnings
    };
  }

  function checkMetric(code, passed, actual, required, severity, label) {
    return {
      code: code,
      label: label,
      passed: !!passed,
      severity: severity || 'hard',
      actual: actual,
      required: required
    };
  }

  function compareCandidate(champion, challenger, options) {
    var opts = options || {};
    var thresholds = {
      profitFactorMultiplier: opts.profitFactorMultiplier == null ? 1.05 : opts.profitFactorMultiplier,
      returnDrawdownMultiplier: opts.returnDrawdownMultiplier == null ? 0.95 : opts.returnDrawdownMultiplier,
      tradesMultiplier: opts.tradesMultiplier == null ? 0.70 : opts.tradesMultiplier,
      drawdownMultiplier: opts.drawdownMultiplier == null ? 1.20 : opts.drawdownMultiplier,
      enableDrawdownCheck: !!opts.enableDrawdownCheck,
      enableForwardCheck: !!opts.enableForwardCheck
    };
    var champ = champion.metrics || champion;
    var cand = challenger.metrics || challenger;
    var checks = [];
    var failureReasons = [];
    var warnings = [];

    checks.push(checkMetric(
      'profit_factor',
      cand.profit_factor >= champ.profit_factor * thresholds.profitFactorMultiplier,
      cand.profit_factor,
      champ.profit_factor * thresholds.profitFactorMultiplier,
      'hard',
      'Profit factor'
    ));
    checks.push(checkMetric(
      'return_drawdown',
      cand.return_drawdown >= champ.return_drawdown * thresholds.returnDrawdownMultiplier,
      cand.return_drawdown,
      champ.return_drawdown * thresholds.returnDrawdownMultiplier,
      'hard',
      'Return/drawdown'
    ));
    checks.push(checkMetric(
      'trades',
      cand.trades >= champ.trades * thresholds.tradesMultiplier,
      cand.trades,
      champ.trades * thresholds.tradesMultiplier,
      'hard',
      'Trades'
    ));

    if (thresholds.enableDrawdownCheck && champ.drawdown_pct != null && cand.drawdown_pct != null) {
      checks.push(checkMetric(
        'drawdown_pct',
        cand.drawdown_pct <= champ.drawdown_pct * thresholds.drawdownMultiplier,
        cand.drawdown_pct,
        champ.drawdown_pct * thresholds.drawdownMultiplier,
        'advisory',
        'Drawdown percent'
      ));
    } else {
      warnings.push({ code: 'drawdown_check_disabled' });
    }

    if (thresholds.enableForwardCheck) {
      var forwardText = String(cand.filters_result || '').toLowerCase();
      checks.push(checkMetric(
        'forward_oos_flag',
        forwardText.indexOf('passed') !== -1 || forwardText.indexOf('pass') !== -1,
        cand.filters_result || '',
        'PASSED',
        'advisory',
        'Forward/OOS flag'
      ));
    }

    checks.forEach(function(check) {
      if (!check.passed) failureReasons.push(check.code);
    });

    return {
      strategy_name: cand.strategy_name || '',
      symbol: cand.symbol || '',
      safe_strategy_name: escapeHtml(cand.strategy_name || ''),
      formal_pass_count: checks.filter(function(check) { return check.severity === 'hard' && check.passed; }).length,
      formal_fail_count: checks.filter(function(check) { return check.severity === 'hard' && !check.passed; }).length,
      advisory_pass_count: checks.filter(function(check) { return check.severity === 'advisory' && check.passed; }).length,
      advisory_fail_count: checks.filter(function(check) { return check.severity === 'advisory' && !check.passed; }).length,
      checks: checks,
      failure_reasons: failureReasons,
      warnings: warnings,
      normalized_metrics: clone(cand),
      source_trace: {
        champion_row: champion.rowNumber || null,
        challenger_row: challenger.rowNumber || null
      }
    };
  }

  function rankCandidates(champion, challengers, options) {
    return (challengers || [])
      .map(function(challenger) {
        return compareCandidate(champion, challenger, options);
      })
      .sort(function(a, b) {
        if (a.formal_fail_count !== b.formal_fail_count) return a.formal_fail_count - b.formal_fail_count;
        if (a.formal_pass_count !== b.formal_pass_count) return b.formal_pass_count - a.formal_pass_count;
        return (b.normalized_metrics.profit_factor || 0) - (a.normalized_metrics.profit_factor || 0);
      });
  }

  SQX.championChallengerCore = SQX.championChallengerCore || {
    fieldAliases: FIELD_ALIASES,
    numericFields: NUMERIC_FIELDS,
    defaultRequiredFields: DEFAULT_REQUIRED_FIELDS,
    defaultRecommendedFields: DEFAULT_RECOMMENDED_FIELDS,
    compareCandidate: compareCandidate,
    detectDelimiter: detectDelimiter,
    escapeHtml: escapeHtml,
    normalizeHeader: normalizeHeader,
    parseCsv: parseCsv,
    parseNumber: parseNumber,
    parseStrategyCsv: parseStrategyCsv,
    rankCandidates: rankCandidates,
    resolveColumnAliases: resolveColumnAliases
  };

  if (SQX.registerModule) {
    SQX.registerModule('champion-challenger-core', SQX.championChallengerCore);
  }
})(window);
