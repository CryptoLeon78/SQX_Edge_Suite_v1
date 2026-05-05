(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};
  var escapeHtml = PG.escapeHtml;

function directionClass(direction) {
    return direction === 'long' ? 'long' : direction === 'short' ? 'short' : 'both';
  }

function directionLabel(direction) {
    return direction === 'long' ? 'LONG' : direction === 'short' ? 'SHORT' : 'L+S';
  }

function symbolSourceBadge(info) {
    if (info && info.source === 'db') {
      return '<span class="pgm-src pgm-src-db" title="Costos leidos de data.db: '
        + escapeHtml(info.instrument) + ' spread=' + escapeHtml(info.spread)
        + ' swap=' + escapeHtml(info.swap_long) + '/' + escapeHtml(info.swap_short)
        + '">&#128202; DB</span>';
    }
    return '<span class="pgm-src pgm-src-fallback" title="Costos por defecto (data.db no disponible o asset no encontrado)">&#128203; Default</span>';
  }

function miningRowsHtml(minings) {
    return (minings || []).map(function(mining) {
      var info = mining._info;
      var alias = info && info.instrument && info.instrument !== mining.asset
        ? '<span class="pgm-alias" title="Alias: ' + escapeHtml(mining.asset) + ' -> ' + escapeHtml(info.instrument) + ' en SQX DB">&#8594; ' + escapeHtml(info.instrument) + '</span>'
        : '';
      return ''
        + '<div class="pg-mining-row">'
        +   '<div class="pgm-num">M' + String(mining.num).padStart(2, '0') + '</div>'
        +   '<div class="pgm-asset">' + escapeHtml(mining.asset) + alias + '</div>'
        +   '<div class="pgm-tf">' + escapeHtml(mining.tf) + '</div>'
        +   '<div class="pgm-bs">' + escapeHtml(mining.bs) + '</div>'
        +   '<div class="pgm-dir ' + directionClass(mining.dir) + '">' + directionLabel(mining.dir) + '</div>'
        +   symbolSourceBadge(info)
        +   '<div class="pgm-actions">'
        +     '<button class="pgm-btn c1" data-pg-gen="' + mining.num + '" data-pg-capa="1">&#128230; Capa 1</button>'
        +     '<button class="pgm-btn c2" data-pg-gen="' + mining.num + '" data-pg-capa="2">&#128230; Capa 2</button>'
        +   '</div>'
        + '</div>';
    }).join('');
  }

function outputListHtml(files) {
    if (!files || !files.length) {
      return '<div class="pg-output-empty">No hay .cfx generados todav&iacute;a. Pulsa un bot&oacute;n "&#128230; Capa 1/2" arriba.</div>';
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

function miningsCountLabel(count) {
    return (count || 0) + ' minings';
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

function outputState(result) {
    var data = result || {};
    var files = data.files || [];
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
    miningsCountLabel: miningsCountLabel,
    outputCountLabel: outputCountLabel,
    outputListHtml: outputListHtml,
    outputState: outputState
  });
})(window);
