(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var DEFAULT_REQUIRED_FIELDS = ['strategy_name', 'symbol', 'profit_factor', 'return_drawdown', 'trades'];
  var DEFAULT_RECOMMENDED_FIELDS = ['net_profit', 'drawdown_pct', 'r_expectancy', 'stagnation', 'entry_indicators', 'filters_result'];
  var DEFAULT_MAX_BYTES = 1024 * 1024;
  var DEFAULT_MAX_ROWS = 5000;
  var DEFAULT_MIN_OOS_BLOCKS = 3;
  var PRIMARY_OOS_METRICS = ['CAGR/Max DD', 'Profit Factor', 'Net Profit'];
  var TEMPORAL_HEALTH_METRICS = ['Net Profit', 'Net profit', 'NetProfit'];
  var TEMPORAL_HEALTH_DEFAULTS = {
    minBlocks: 4,
    recentPeakWindow: 3,
    maxDdAtClose: 0.15,
    minRecoveryIndex: 0.70
  };

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

  function normalizeMetricName(value) {
    return String(value == null ? '' : value)
      .replace(/^\uFEFF/, '')
      .trim()
      .replace(/\s+/g, ' ')
      .toLowerCase();
  }

  function displayMetricName(value) {
    return String(value == null ? '' : value).replace(/^\uFEFF/, '').trim().replace(/\s+/g, ' ');
  }

  function extractOosHeader(header) {
    var match = String(header == null ? '' : header).match(/^\s*(.*?)\s*\(\s*OOS\s*(\d+)\s*\)\s*$/i);
    if (!match) return null;
    var metric = displayMetricName(match[1]);
    var block = parseInt(match[2], 10);
    if (!metric || !block || block < 1) return null;
    return {
      metric: metric,
      normalizedMetric: normalizeMetricName(metric),
      block: block
    };
  }

  function resolveOosColumns(headers) {
    var metrics = {};
    var warnings = [];
    (headers || []).forEach(function(header, index) {
      var parsed = extractOosHeader(header);
      if (!parsed) return;
      metrics[parsed.normalizedMetric] = metrics[parsed.normalizedMetric] || {
        metric: parsed.metric,
        normalizedMetric: parsed.normalizedMetric,
        columns: {}
      };
      if (metrics[parsed.normalizedMetric].columns[parsed.block] != null) {
        warnings.push({ code: 'duplicate_oos_block_metric', metric: parsed.metric, block: parsed.block, index: index });
        return;
      }
      metrics[parsed.normalizedMetric].columns[parsed.block] = index;
    });
    return { metrics: metrics, warnings: warnings };
  }

  function choosePrimaryOosMetric(metricColumns, preferredMetrics) {
    var preferred = preferredMetrics || PRIMARY_OOS_METRICS;
    var names = Object.keys(metricColumns || {});
    for (var i = 0; i < preferred.length; i += 1) {
      var normalized = normalizeMetricName(preferred[i]);
      if (metricColumns[normalized]) return metricColumns[normalized].metric;
    }
    return names.length ? metricColumns[names[0]].metric : null;
  }

  function sortedBlockIds(metricInfo) {
    return Object.keys((metricInfo && metricInfo.columns) || {})
      .map(function(block) { return parseInt(block, 10); })
      .filter(function(block) { return isFinite(block); })
      .sort(function(a, b) { return a - b; });
  }

  function maxNegativeStreak(values) {
    var current = 0;
    var max = 0;
    values.forEach(function(value) {
      if (typeof value === 'number' && value < 0) {
        current += 1;
        if (current > max) max = current;
      } else {
        current = 0;
      }
    });
    return max;
  }

  function finiteNumber(value) {
    return typeof value === 'number' && isFinite(value);
  }

  function optionNumber(value, fallback, min) {
    var parsed = Number(value);
    if (!isFinite(parsed)) return fallback;
    return min == null ? parsed : Math.max(min, parsed);
  }

  function mergeTemporalHealthOptions(options) {
    var opts = options || {};
    return {
      minBlocks: opts.minBlocks == null ? TEMPORAL_HEALTH_DEFAULTS.minBlocks : optionNumber(opts.minBlocks, TEMPORAL_HEALTH_DEFAULTS.minBlocks, 1),
      recentPeakWindow: opts.recentPeakWindow == null ? TEMPORAL_HEALTH_DEFAULTS.recentPeakWindow : optionNumber(opts.recentPeakWindow, TEMPORAL_HEALTH_DEFAULTS.recentPeakWindow, 1),
      maxDdAtClose: opts.maxDdAtClose == null ? TEMPORAL_HEALTH_DEFAULTS.maxDdAtClose : optionNumber(opts.maxDdAtClose, TEMPORAL_HEALTH_DEFAULTS.maxDdAtClose),
      minRecoveryIndex: opts.minRecoveryIndex == null ? TEMPORAL_HEALTH_DEFAULTS.minRecoveryIndex : optionNumber(opts.minRecoveryIndex, TEMPORAL_HEALTH_DEFAULTS.minRecoveryIndex),
      recoveryOptional: !!opts.recoveryOptional
    };
  }

  function metricValueByNormalizedName(blockValues, metricName) {
    var normalized = normalizeMetricName(metricName);
    var keys = Object.keys(blockValues || {});
    for (var i = 0; i < keys.length; i += 1) {
      if (normalizeMetricName(keys[i]) === normalized) return blockValues[keys[i]];
    }
    return null;
  }

  function temporalMetricCandidates(oosRecord, options) {
    var opts = options || {};
    var preferred = (opts.preferredMetrics || TEMPORAL_HEALTH_METRICS).slice();
    if (oosRecord && oosRecord.primary_metric) preferred.push(oosRecord.primary_metric);
    return preferred.filter(function(metric, index, items) {
      return metric && items.map(normalizeMetricName).indexOf(normalizeMetricName(metric)) === index;
    });
  }

  function extractMetricSeries(oosRecord, metricName) {
    var metricsByBlock = oosRecord && oosRecord.metrics_by_block || {};
    var blocks = Object.keys(metricsByBlock)
      .map(function(block) { return parseInt(block, 10); })
      .filter(function(block) { return isFinite(block); })
      .sort(function(a, b) { return a - b; });
    var values = [];
    blocks.forEach(function(block) {
      var value = metricValueByNormalizedName(metricsByBlock[block], metricName);
      if (finiteNumber(value)) values.push({ block: block, value: value });
    });
    return values;
  }

  function emptyTemporalHealth(status, warnings, oosRecord, options) {
    var cfg = mergeTemporalHealthOptions(options);
    return {
      status: status || 'unknown',
      peak_block: null,
      block_count: oosRecord && oosRecord.block_count || 0,
      dd_at_close: null,
      recovery_index: null,
      pass_peak: false,
      pass_drawdown: false,
      pass_recovery: false,
      pass_all: false,
      source_metric: null,
      quality: 'insufficient',
      warnings: warnings || [],
      thresholds: cfg
    };
  }

  function computeTemporalHealth(oosRecord, options) {
    var cfg = mergeTemporalHealthOptions(options);
    var warnings = [];
    if (!oosRecord || !oosRecord.metrics_by_block) {
      return emptyTemporalHealth('unknown', [{ code: 'temporal_health_oos_missing' }], oosRecord, cfg);
    }

    var candidates = temporalMetricCandidates(oosRecord, options);
    var selected = null;
    var series = [];
    for (var i = 0; i < candidates.length; i += 1) {
      var values = extractMetricSeries(oosRecord, candidates[i]);
      if (values.length) {
        selected = candidates[i];
        series = values;
        break;
      }
    }

    if (!selected || !series.length) {
      return emptyTemporalHealth('unknown', [{ code: 'temporal_health_metric_missing' }], oosRecord, cfg);
    }

    var selectedNormalized = normalizeMetricName(selected);
    var preferredNormalized = TEMPORAL_HEALTH_METRICS.map(normalizeMetricName);
    var quality = preferredNormalized.indexOf(selectedNormalized) === -1 ? 'fallback' : 'full';
    if (quality === 'fallback') warnings.push({ code: 'temporal_health_metric_fallback', source_metric: selected });
    if (series.length < cfg.minBlocks) {
      warnings.push({ code: 'temporal_health_blocks_insufficient', min_blocks: cfg.minBlocks, actual_blocks: series.length });
      return {
        status: 'unknown',
        peak_block: null,
        block_count: series.length,
        dd_at_close: null,
        recovery_index: null,
        pass_peak: false,
        pass_drawdown: false,
        pass_recovery: false,
        pass_all: false,
        source_metric: selected,
        quality: 'insufficient',
        warnings: warnings,
        thresholds: cfg
      };
    }

    var equity = [];
    var cumulative = 0;
    series.forEach(function(item) {
      cumulative += item.value;
      equity.push({ block: item.block, value: cumulative });
    });

    var peak = equity[0];
    equity.forEach(function(item) {
      if (item.value > peak.value) peak = item;
    });
    var close = equity[equity.length - 1];
    var ddAtClose = null;
    var passDrawdown = false;
    if (peak.value > 0) {
      ddAtClose = Math.max(0, (peak.value - close.value) / peak.value);
      passDrawdown = ddAtClose < cfg.maxDdAtClose;
    } else {
      quality = 'fallback';
      warnings.push({ code: 'temporal_health_peak_non_positive', peak_value: peak.value });
    }

    var recentValues = series.slice(Math.max(0, series.length - cfg.recentPeakWindow)).map(function(item) { return item.value; });
    var sum = series.reduce(function(acc, item) { return acc + item.value; }, 0);
    var recentSum = recentValues.reduce(function(acc, value) { return acc + value; }, 0);
    var avgHistorical = sum / series.length;
    var avgRecent = recentSum / recentValues.length;
    var recoveryIndex = null;
    var passRecovery = false;
    if (avgHistorical !== 0 && isFinite(avgHistorical) && isFinite(avgRecent)) {
      recoveryIndex = avgRecent / avgHistorical;
      passRecovery = recoveryIndex >= cfg.minRecoveryIndex;
    } else {
      warnings.push({ code: 'temporal_health_recovery_unavailable', avg_historical: avgHistorical });
      passRecovery = cfg.recoveryOptional;
    }

    var peakPosition = equity.findIndex(function(item) { return item.block === peak.block; });
    var passPeak = peakPosition >= Math.floor(series.length / 2);
    var recentPeak = peakPosition >= Math.max(0, series.length - cfg.recentPeakWindow);
    var status = 'old_peak';
    if (!passDrawdown || !passRecovery) status = 'declining';
    else if (recentPeak) status = 'fresh';
    else if (passPeak) status = 'recovered';

    return {
      status: status,
      peak_block: peak.block,
      block_count: series.length,
      dd_at_close: ddAtClose,
      recovery_index: recoveryIndex,
      pass_peak: passPeak,
      pass_drawdown: passDrawdown,
      pass_recovery: passRecovery,
      pass_all: passPeak && passDrawdown && passRecovery,
      source_metric: selected,
      quality: quality,
      warnings: warnings,
      thresholds: cfg
    };
  }

  function parseOosRecord(row, headers, oosColumns, options) {
    var opts = options || {};
    var preferredMetrics = opts.primaryMetrics || PRIMARY_OOS_METRICS;
    var primaryMetric = choosePrimaryOosMetric(oosColumns.metrics, preferredMetrics);
    var warnings = [].concat(oosColumns.warnings || []);
    var metricsByBlock = {};
    var metricsAvailable = Object.keys(oosColumns.metrics || {}).map(function(key) {
      return oosColumns.metrics[key].metric;
    });

    Object.keys(oosColumns.metrics || {}).forEach(function(metricKey) {
      var info = oosColumns.metrics[metricKey];
      sortedBlockIds(info).forEach(function(block) {
        var parsed = parseNumber(row[info.columns[block]]);
        metricsByBlock[block] = metricsByBlock[block] || {};
        metricsByBlock[block][info.metric] = parsed.ok ? parsed.value : null;
        if (!parsed.ok) {
          warnings.push({ code: 'oos_non_numeric_metric', metric: info.metric, block: block, value: row[info.columns[block]] });
        }
      });
    });

    var primaryInfo = primaryMetric ? oosColumns.metrics[normalizeMetricName(primaryMetric)] : null;
    var blockIds = sortedBlockIds(primaryInfo);
    var expected = [];
    if (blockIds.length) {
      for (var block = blockIds[0]; block <= blockIds[blockIds.length - 1]; block += 1) expected.push(block);
      expected.forEach(function(blockId) {
        if (blockIds.indexOf(blockId) === -1) warnings.push({ code: 'oos_missing_block', block: blockId, metric: primaryMetric });
      });
    }

    var primaryValues = blockIds.map(function(blockId) {
      return metricsByBlock[blockId] ? metricsByBlock[blockId][primaryMetric] : null;
    }).filter(function(value) {
      return typeof value === 'number' && isFinite(value);
    });
    var positive = primaryValues.filter(function(value) { return value > 0; });
    var total = primaryValues.length;
    var sum = primaryValues.reduce(function(acc, value) { return acc + value; }, 0);
    var worstYearKey = Object.keys(oosColumns.metrics || {}).find(function(key) {
      return normalizeMetricName(oosColumns.metrics[key].metric) === normalizeMetricName('Worst Year Profit');
    });
    var worstYearValues = [];
    if (worstYearKey) {
      sortedBlockIds(oosColumns.metrics[worstYearKey]).forEach(function(blockId) {
        var value = metricsByBlock[blockId] ? metricsByBlock[blockId][oosColumns.metrics[worstYearKey].metric] : null;
        if (typeof value === 'number' && isFinite(value)) worstYearValues.push(value);
      });
    }

    return {
      headers: headers,
      primary_metric: primaryMetric,
      metrics_available: metricsAvailable,
      metrics_by_block: metricsByBlock,
      block_count: total,
      positive_block_count: positive.length,
      positive_block_ratio: total ? positive.length / total : null,
      primary_metric_min: total ? Math.min.apply(Math, primaryValues) : null,
      primary_metric_max: total ? Math.max.apply(Math, primaryValues) : null,
      primary_metric_avg: total ? sum / total : null,
      primary_metric_decay: total > 1 ? primaryValues[total - 1] - primaryValues[0] : null,
      max_negative_streak: maxNegativeStreak(primaryValues),
      has_negative_worst_year: worstYearValues.some(function(value) { return value < 0; }),
      stable_enough: total >= (opts.minBlocks || DEFAULT_MIN_OOS_BLOCKS),
      warnings: warnings
    };
  }

  function parseOosCsv(text, options) {
    var opts = options || {};
    var source = String(text == null ? '' : text);
    var parsed = parseCsv(source, opts);
    var errors = parsed.errors.map(function(error) { return { code: error }; });
    var warnings = [];
    if (!source.trim()) errors.push({ code: 'oos_csv_empty' });
    if (!parsed.rows.length) errors.push({ code: 'oos_header_missing' });

    var headers = parsed.rows[0] || [];
    var aliasResolution = resolveColumnAliases(headers, {
      requiredFields: [],
      aliases: opts.aliases || FIELD_ALIASES
    });
    var oosColumns = resolveOosColumns(headers);
    warnings = warnings.concat(aliasResolution.warnings).concat(oosColumns.warnings);
    if (!Object.keys(oosColumns.metrics).length) {
      errors.push({ code: 'oos_metric_columns_missing' });
    }

    var dataRows = parsed.rows.slice(1);
    if (!dataRows.length) errors.push({ code: 'oos_rows_missing' });

    var records = dataRows.map(function(row, index) {
      var strategyName = aliasResolution.columns.strategy_name != null ? String(row[aliasResolution.columns.strategy_name] || '').trim() : '';
      var symbol = aliasResolution.columns.symbol != null ? String(row[aliasResolution.columns.symbol] || '').trim() : '';
      var record = parseOosRecord(row, headers, oosColumns, opts);
      record.rowNumber = index + 2;
      record.strategy_name = strategyName;
      record.symbol = symbol;
      record.safe_strategy_name = escapeHtml(strategyName);
      record.safe_symbol = escapeHtml(symbol);
      return record;
    });

    return {
      ok: errors.length === 0,
      delimiter: parsed.delimiter,
      headers: headers,
      records: records,
      oos_columns: oosColumns.metrics,
      errors: errors,
      warnings: warnings
    };
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
    defaultMinOosBlocks: DEFAULT_MIN_OOS_BLOCKS,
    primaryOosMetrics: PRIMARY_OOS_METRICS,
    temporalHealthDefaults: TEMPORAL_HEALTH_DEFAULTS,
    temporalHealthMetrics: TEMPORAL_HEALTH_METRICS,
    compareCandidate: compareCandidate,
    computeTemporalHealth: computeTemporalHealth,
    detectDelimiter: detectDelimiter,
    escapeHtml: escapeHtml,
    choosePrimaryOosMetric: choosePrimaryOosMetric,
    extractOosHeader: extractOosHeader,
    normalizeHeader: normalizeHeader,
    normalizeMetricName: normalizeMetricName,
    parseCsv: parseCsv,
    parseNumber: parseNumber,
    parseOosCsv: parseOosCsv,
    parseOosRecord: parseOosRecord,
    parseStrategyCsv: parseStrategyCsv,
    rankCandidates: rankCandidates,
    resolveColumnAliases: resolveColumnAliases,
    resolveOosColumns: resolveOosColumns
  };

  if (SQX.registerModule) {
    SQX.registerModule('champion-challenger-core', SQX.championChallengerCore);
  }
})(window);
