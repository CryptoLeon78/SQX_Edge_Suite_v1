(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};
  var escapeHtml = PG.escapeHtml;

function uniqueAssets(minings) {
    var seen = {};
    return (minings || [])
      .map(function(mining) { return mining.asset; })
      .filter(function(asset) {
        if (!asset || seen[asset]) return false;
        seen[asset] = true;
        return true;
      })
      .sort();
  }

function aliasTableHtml(minings, aliases) {
    var assets = uniqueAssets(minings);
    if (!assets.length) return '<div style="color:var(--text2);font-size:12px;">(esperando minings...)</div>';
    return ''
      + '<table class="cat-table" style="font-size:12px;">'
      +   '<thead><tr><th>Asset (plan)</th><th>Instrument SQX (alias)</th><th></th></tr></thead>'
      +   '<tbody>'
      +   assets.map(function(asset) {
            var current = (aliases || {})[asset] || '';
            return ''
              + '<tr>'
              +   '<td style="font-weight:700;">' + escapeHtml(asset) + '</td>'
              +   '<td><input type="text" class="search-input" style="width:200px;font-size:12px;padding:4px 8px;" data-pg-alias="' + escapeHtml(asset) + '" value="' + escapeHtml(current) + '" placeholder="(default)"></td>'
              +   '<td><button class="export-btn" style="padding:3px 10px;font-size:11px;" data-pg-suggest-asset="' + escapeHtml(asset) + '">&#128269;</button></td>'
              + '</tr>';
          }).join('')
      +   '</tbody>'
      + '</table>';
  }

function aliasTopSuggestions(suggestions, limit) {
    return (suggestions || []).slice(0, limit || 5);
  }

function aliasSuggestionPrompt(asset, suggestions) {
    var top = aliasTopSuggestions(suggestions, 5);
    var options = top.map(function(suggestion, index) {
      return (index + 1) + '. ' + suggestion.instrument + ' [' + suggestion.score + '%] — '
        + (suggestion.description || '') + ' (broker_id=' + suggestion.broker_id + ')';
    }).join('\n');
    return 'Sugerencias para "' + asset + '":\n\n'
      + options
      + '\n\nElige número (1-' + top.length + ') o escribe el ticker manualmente:';
  }

function aliasChoiceValue(choice, suggestions) {
    var raw = String(choice || '').trim();
    if (!raw) return '';
    var top = aliasTopSuggestions(suggestions, 5);
    var index = parseInt(raw, 10);
    if (index >= 1 && index <= top.length) return top[index - 1].instrument;
    return raw;
  }

function aliasProposedMessage(asset, instrument) {
    return 'Alias propuesto: ' + asset + ' → ' + instrument + ' (pulsa Guardar config)';
  }

function aliasSuggestionEmptyMessage(asset) {
    return 'Sin sugerencias para ' + asset + ' en data.db';
  }

function aliasAutoSuggestStartMessage(count) {
    return 'Auto-sugiriendo para ' + (count || 0) + ' assets…';
  }

function aliasAutoSuggestResult(found) {
    var count = found || 0;
    return {
      text: 'Auto-suggest: ' + count + ' aliases nuevos propuestos (pulsa Guardar config)',
      level: count > 0 ? 'ok' : 'info'
    };
  }

function configSaveBody(input) {
    var data = input || {};
    return {
      sqx_path: data.sqxPath || '',
      sqx_data_db: data.sqxDataDb || '',
      sqx_projects_dir: data.sqxProjectsDir || '',
      output_dir: data.outputDir || '',
      template_capa1: data.templateCapa1 || '',
      template_capa2: data.templateCapa2 || '',
      asset_aliases: data.assetAliases || {}
    };
  }

function configSaveStatus(result) {
    var keys = result && result.updated_keys || [];
    return {
      message: '✓ Guardado: ' + keys.join(', '),
      color: 'var(--green)',
      logText: 'Config actualizada (' + keys.length + ' keys)',
      logLevel: 'ok',
      traceTitle: 'Configuracion guardada',
      traceDetail: keys.join(', '),
      traceLevel: 'ok'
    };
  }

function configSaveError(message) {
    return {
      message: '✗ Error: ' + message,
      color: 'var(--red)',
      traceTitle: 'Error guardando configuracion',
      traceDetail: message,
      traceLevel: 'err'
    };
  }

function sqxCandidateFields(candidate) {
    var data = candidate || {};
    return {
      sqxPath: data.sqx_path || '',
      dataDb: data.data_db || '',
      projectsDir: data.projects_dir || ''
    };
  }

function sqxCandidateSelectedStatus(candidate) {
    var fields = sqxCandidateFields(candidate);
    return {
      logText: 'Path SQX seleccionado: ' + fields.sqxPath + ' (pulsa Guardar config)',
      logLevel: 'info',
      traceTitle: 'Ruta SQX detectada',
      traceDetail: fields.sqxPath,
      traceLevel: 'info'
    };
  }

function validateSqxMissingPathHtml() {
    return messageHtml('Pon primero un SQX install path.', 'warning');
  }

function validateSqxResolvedFields(result) {
    var resolved = result && result.resolved || {};
    return {
      dataDb: resolved.data_db || '',
      projectsDir: resolved.projects_dir || ''
    };
  }

function validateSqxShouldApply(result) {
    return !!(result && result.valid && result.resolved && result.resolved.data_db);
  }

function validateSqxTrace(path) {
    return {
      title: 'Validacion SQX correcta',
      detail: path,
      level: 'ok'
    };
  }

function messageHtml(message, tone) {
    var color = tone === 'error' ? 'var(--red)' : tone === 'warning' ? 'var(--yellow)' : 'var(--text2)';
    return '<div style="color:' + color + ';font-size:12px;">' + escapeHtml(message) + '</div>';
  }

function sqxNotFoundHtml() {
    return '<div class="alert warning"><div class="alert-icon">!</div><div class="alert-content"><strong>No se encontro ninguna instalacion de SQX.</strong>Edita los campos manualmente con la ruta donde este StrategyQuantX.exe.</div></div>';
  }

function sqxAppliedHtml() {
    return '<div class="alert success"><div class="alert-icon">&#10003;</div><div class="alert-content"><strong>Aplicado.</strong> Pulsa "Guardar config" para persistir.</div></div>';
  }

function autodetectCandidatesHtml(result) {
    var candidates = (result && result.candidates) || [];
    if (!result || !result.found) return sqxNotFoundHtml();
    return '<div style="font-size:12px;color:var(--text2);margin-bottom:6px;">' + result.found + ' instalacion(es) detectada(s):</div>'
      + candidates.map(function(candidate, index) {
        return ''
          + '<div class="pg-autodetect-row">'
          +   '<div style="flex:1;">'
          +     '<div style="font-weight:700;font-size:13px;">SQX v' + escapeHtml(candidate.version) + (candidate.has_exe ? ' &#10003;' : ' ! sin .exe') + '</div>'
          +     '<div style="font-family:Consolas,monospace;font-size:11px;color:var(--text2);">' + escapeHtml(candidate.sqx_path) + '</div>'
          +     '<div style="font-family:Consolas,monospace;font-size:10px;color:var(--text2);">-&gt; data.db: ' + escapeHtml(candidate.data_db) + '</div>'
          +   '</div>'
          +   '<button class="export-btn pg-use-btn" data-idx="' + index + '" style="border-color:var(--green);color:var(--green);">Usar esta</button>'
          + '</div>';
      }).join('');
  }

function validationItemHtml(label, ok) {
    return '<li style="color:' + (ok ? 'var(--green)' : 'var(--red)') + ';">' + (ok ? 'OK' : 'X') + ' ' + escapeHtml(label) + '</li>';
  }

function validateSqxPathHtml(result) {
    var checks = result.checks || {};
    return '<div class="alert ' + (result.valid ? 'success' : 'warning') + '"><div class="alert-icon">' + (result.valid ? 'OK' : '!') + '</div><div class="alert-content"><strong>' + (result.valid ? 'Path valido' : 'Path con problemas') + '</strong>'
      + '<ul style="margin-top:6px;padding-left:20px;font-size:12px;">'
      + validationItemHtml('Directorio base existe', checks.base_exists)
      + validationItemHtml('user/data/data.db existe', checks.data_db_exists)
      + validationItemHtml('user/projects existe', checks.projects_exists)
      + validationItemHtml('StrategyQuantX.exe existe', checks.exe_exists)
      + '</ul></div></div>';
  }

  Object.assign(PG, {
    aliasTableHtml: aliasTableHtml,
    aliasAutoSuggestResult: aliasAutoSuggestResult,
    aliasAutoSuggestStartMessage: aliasAutoSuggestStartMessage,
    aliasChoiceValue: aliasChoiceValue,
    aliasProposedMessage: aliasProposedMessage,
    aliasSuggestionEmptyMessage: aliasSuggestionEmptyMessage,
    aliasSuggestionPrompt: aliasSuggestionPrompt,
    aliasTopSuggestions: aliasTopSuggestions,
    autodetectCandidatesHtml: autodetectCandidatesHtml,
    configSaveBody: configSaveBody,
    configSaveError: configSaveError,
    configSaveStatus: configSaveStatus,
    messageHtml: messageHtml,
    sqxAppliedHtml: sqxAppliedHtml,
    sqxCandidateFields: sqxCandidateFields,
    sqxCandidateSelectedStatus: sqxCandidateSelectedStatus,
    sqxNotFoundHtml: sqxNotFoundHtml,
    uniqueAssets: uniqueAssets,
    validateSqxMissingPathHtml: validateSqxMissingPathHtml,
    validateSqxPathHtml: validateSqxPathHtml,
    validateSqxResolvedFields: validateSqxResolvedFields,
    validateSqxShouldApply: validateSqxShouldApply,
    validateSqxTrace: validateSqxTrace
  });
})(window);
