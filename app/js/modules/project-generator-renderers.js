(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};
  var escapeHtml = PG.escapeHtml;
  var OUTPUT_RESET_STORAGE_KEY = 'sqx_pg_generated_cfx_reset_v1';
  var OUTPUT_RESET_SCHEMA = 'pg-generated-cfx-reset-v1';

function normalizeDirection(direction) {
    var value = String(direction || '').trim().toLowerCase();
    if (value === 'l' || value === 'long') return 'long';
    if (value === 's' || value === 'short') return 'short';
    return 'both';
  }

function directionClass(direction) {
    return normalizeDirection(direction);
  }

function directionLabel(direction) {
    var normalized = normalizeDirection(direction);
    return normalized === 'long' ? 'LONG' : normalized === 'short' ? 'SHORT' : 'L+S';
  }

function symbolSourceBadge(info) {
    if (info && info.source === 'db') {
      return '<span class="pgm-src pgm-src-db" title="Costos leidos de data.db: '
        + escapeHtml(info.instrument) + ' spread=' + escapeHtml(info.spread)
        + ' swap=' + escapeHtml(info.swap_long) + '/' + escapeHtml(info.swap_short)
        + '">DB</span>';
    }
    return '<span class="pgm-src pgm-src-fallback" title="Costos por defecto (data.db no disponible o asset no encontrado)">Default</span>';
  }

function blocksettingEntry(value) {
    var manifest = (global.SQX_MANIFEST && global.SQX_MANIFEST.blocksettings) || {};
    var aliases = manifest.aliases || {};
    var entries = manifest.entries || [];
    var token = String(value || '').replace(/\.sqb$/i, '');
    var canonical = aliases[token] || aliases[token + '.sqb'] || token;
    for (var i = 0; i < entries.length; i += 1) {
      if (entries[i].canonicalId === canonical) return entries[i];
    }
    return null;
  }

function blocksettingTraceHtml(value) {
    var entry = blocksettingEntry(value);
    if (!entry) return '<div class="pgm-bs">' + escapeHtml(value || 'BS_Custom') + '<small>sin manifiesto</small></div>';
    return '<div class="pgm-bs" title="Archivo real: ' + escapeHtml(entry.filename) + ' · SHA ' + escapeHtml(entry.sha256Short) + '">'
      + '<span>' + escapeHtml(entry.canonicalId) + '</span>'
      + '<small>' + escapeHtml(entry.variant || '-') + ' · ' + escapeHtml(entry.sha256Short || '-') + '</small>'
      + '</div>';
  }

function miningSourceBadge(mining) {
    if (mining && mining._user) {
      var source = mining.source ? ' · ' + escapeHtml(mining.source) : '';
      return '<span class="pgm-plan-source user" title="Añadido al Plan Mining desde la UI">USER' + source + '</span>';
    }
    return '<span class="pgm-plan-source base" title="Mining del plan base activo">BASE</span>';
  }

function miningRowsHtml(minings, selectedMap) {
    var selected = selectedMap || {};
    var rows = minings || [];
    if (!rows.length) {
      return '<div class="pg-minings-empty">'
        + '<strong>Plan Mining vacío.</strong>'
        + '<span>Añade minings desde Mining Control con + Mining o desde las tarjetas de activos. Después vuelve aquí para generar los .cfx.</span>'
        + '</div>';
    }
    return rows.map(function(mining) {
      var info = mining._info;
      var checked = selected[mining.num] ? ' checked' : '';
      var alias = info && info.instrument && info.instrument !== mining.asset
        ? '<span class="pgm-alias" title="Alias: ' + escapeHtml(mining.asset) + ' -> ' + escapeHtml(info.instrument) + ' en SQX DB">&#8594; ' + escapeHtml(info.instrument) + '</span>'
        : '';
      return ''
        + '<div class="pg-mining-row" data-pg-mining-row="' + mining.num + '">'
        +   '<label class="pgm-check" title="Seleccionar este mining"><input type="checkbox" data-pg-mining-check="' + mining.num + '"' + checked + '><span></span></label>'
        +   '<div class="pgm-num">M' + String(mining.num).padStart(2, '0') + '</div>'
        +   '<div class="pgm-asset">' + escapeHtml(mining.asset) + alias + '</div>'
        +   '<div class="pgm-tf">' + escapeHtml(mining.tf) + '</div>'
        +   blocksettingTraceHtml(mining.bs)
        +   '<div class="pgm-dir ' + directionClass(mining.dir) + '">' + directionLabel(mining.dir) + '</div>'
        +   miningSourceBadge(mining)
        +   symbolSourceBadge(info)
        + '</div>';
    }).join('');
  }

function outputListHtml(files) {
    if (!files || !files.length) {
      return '<div class="pg-output-empty">No hay .cfx generados todav&iacute;a. Elige un modo, selecciona minings o completa Custom libre y genera Capa 1 o Capa 2.</div>';
    }
    return files.map(function(file) {
      return ''
        + '<div class="pg-output-row">'
        +   '<div class="pgo-name">' + escapeHtml(file.name) + '</div>'
        +   '<div class="pgo-size">' + escapeHtml(file.size_kb) + ' KB</div>'
        +   '<div class="pgo-time">' + new Date(file.mtime * 1000).toLocaleString() + '</div>'
        + '</div>';
    }).join('');
  }

function outputFileTimestampMs(file) {
    var data = file || {};
    if (Number.isFinite(Number(data.mtime_ms))) return Number(data.mtime_ms);
    if (Number.isFinite(Number(data.mtime))) return Number(data.mtime) * 1000;
    if (data.modified_at) {
      var parsed = Date.parse(data.modified_at);
      if (Number.isFinite(parsed)) return parsed;
    }
    return 0;
  }

function outputFileSignature(file) {
    var data = file || {};
    return [
      String(data.name || ''),
      String(data.size_kb == null ? '' : data.size_kb),
      String(data.mtime == null ? '' : data.mtime)
    ].join('|');
  }

function readGeneratedOutputReset(storage) {
    var store = storage || global.localStorage;
    if (!store || typeof store.getItem !== 'function') return {};
    try {
      var raw = store.getItem(OUTPUT_RESET_STORAGE_KEY);
      if (!raw) return {};
      var parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (_err) {
      return {};
    }
  }

function writeGeneratedOutputReset(state, storage) {
    var store = storage || global.localStorage;
    if (!store || typeof store.setItem !== 'function') return false;
    try {
      store.setItem(OUTPUT_RESET_STORAGE_KEY, JSON.stringify(state || {}));
      return true;
    } catch (_err) {
      return false;
    }
  }

function markGeneratedOutputReset(files, options) {
    var opts = options || {};
    var now = Number.isFinite(Number(opts.now)) ? Number(opts.now) : Date.now();
    var state = {
      schema: OUTPUT_RESET_SCHEMA,
      resetAt: now,
      reason: opts.reason || 'plan-mining-reset',
      hiddenSignatures: (files || []).map(outputFileSignature).filter(Boolean)
    };
    writeGeneratedOutputReset(state, opts.storage);
    return state;
  }

function filterOutputFilesSinceReset(files, resetState) {
    var rows = files || [];
    var state = resetState || readGeneratedOutputReset();
    var resetAt = Number(state && state.resetAt) || 0;
    var hidden = new Set((state && state.hiddenSignatures) || []);
    if (!resetAt && !hidden.size) return rows.slice();
    return rows.filter(function(file) {
      if (hidden.has(outputFileSignature(file))) return false;
      var timestamp = outputFileTimestampMs(file);
      return !resetAt || !timestamp || timestamp > resetAt;
    });
  }

function miningsCountLabel(count) {
    return (count || 0) + ' minings';
  }

function selectedMiningCountLabel(count) {
    var value = count || 0;
    return value + ' seleccionado' + (value === 1 ? '' : 's');
  }

function bulkGenerateLabel(count) {
    return miningsCountLabel(count) + ' · Capa 1 + Capa 2';
  }

async function enrichMiningsWithSymbolInfo(minings, getSymbolInfo) {
    var list = minings || [];
    var resolver = getSymbolInfo || function() { return Promise.resolve(null); };
    return Promise.all(list.map(async function(mining) {
      try {
        return Object.assign({}, mining, { _info: await resolver(mining.asset) });
      } catch (_err) {
        return Object.assign({}, mining, { _info: null });
      }
    }));
  }

function outputCountLabel(files) {
    return ((files || []).length) + ' archivos';
  }

function outputState(result, resetState) {
    var data = result || {};
    var files = filterOutputFilesSinceReset(data.files || [], resetState);
    return {
      outputDir: data.output_dir || '',
      files: files,
      countLabel: outputCountLabel(files),
      html: outputListHtml(files)
    };
  }

  Object.assign(PG, {
    bulkGenerateLabel: bulkGenerateLabel,
    directionClass: directionClass,
    directionLabel: directionLabel,
    enrichMiningsWithSymbolInfo: enrichMiningsWithSymbolInfo,
    miningRowsHtml: miningRowsHtml,
    miningSourceBadge: miningSourceBadge,
    normalizeDirection: normalizeDirection,
    miningsCountLabel: miningsCountLabel,
    outputCountLabel: outputCountLabel,
    outputFileSignature: outputFileSignature,
    outputFileTimestampMs: outputFileTimestampMs,
    filterOutputFilesSinceReset: filterOutputFilesSinceReset,
    markGeneratedOutputReset: markGeneratedOutputReset,
    outputListHtml: outputListHtml,
    outputResetStorageKey: OUTPUT_RESET_STORAGE_KEY,
    outputState: outputState,
    readGeneratedOutputReset: readGeneratedOutputReset,
    selectedMiningCountLabel: selectedMiningCountLabel
  });
})(window);
