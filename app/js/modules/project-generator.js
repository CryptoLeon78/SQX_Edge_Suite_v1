(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }[ch];
    });
  }

  function computeOnboardingState(input) {
    var data = input || {};
    var health = data.healthMeta || {};
    var minings = data.minings || [];
    var outputFiles = data.outputFiles || [];
    var outputDir = data.outputDir || '';
    var hasSqxInput = !!String(data.sqxPathInput || data.configState && data.configState.sqx_path || '').trim();
    var hasDbInput = !!String(data.dbInput || data.configState && data.configState.sqx_data_db || '').trim();
    var hasMinings = minings.length > 0;
    var outputReady = !!health.output_dir_exists;
    var templateReady = !!health.templates_capa1_exists && !!health.templates_capa2_exists && outputReady;
    var sqxReady = !!health.sqx_path_set && !!health.data_db_exists;
    var hasUnsavedSqxCandidate = hasSqxInput && (!health.sqx_path_set || !health.data_db_exists);
    var connected = !!data.connected;
    var apiBase = data.apiBase || '';
    var steps = [
      {
        id: 'api',
        label: 'API local',
        done: connected,
        detail: connected ? ('Backend listo en ' + apiBase) : 'Sin conexion con el backend local.'
      },
      {
        id: 'sqx',
        label: 'Ruta SQX',
        done: connected && sqxReady,
        detail: sqxReady
          ? ((health.sqx_path || 'Ruta SQX') + ' listo')
          : (hasSqxInput ? 'Hay una ruta configurada pendiente de validar.' : 'Detecta o pega la carpeta de StrategyQuant X.')
      },
      {
        id: 'templates',
        label: 'Templates y output',
        done: connected && templateReady,
        detail: templateReady
          ? ('C1, C2 y output listos en ' + (health.output_dir || outputDir || 'output'))
          : [
              health.templates_capa1_exists ? null : 'falta Capa 1',
              health.templates_capa2_exists ? null : 'falta Capa 2',
              outputReady ? null : 'revisa output'
            ].filter(Boolean).join(' · ')
      },
      {
        id: 'first',
        label: 'Primer .cfx',
        done: outputFiles.length > 0,
        detail: outputFiles.length
          ? (outputFiles.length + ' archivo(s) generado(s).')
          : (hasMinings ? ('Listo para generar desde ' + minings[0].asset + ' ' + minings[0].tf + '.') : 'No hay minings cargados en el plan.')
      }
    ];
    var completed = steps.filter(function(step) { return step.done; }).length;
    var current = steps.find(function(step) { return !step.done; }) || null;
    var state = {
      steps: steps,
      completed: completed,
      current: current,
      checks: [
        { label: 'API local responde', ok: connected },
        { label: hasDbInput ? 'data.db localizado' : 'data.db pendiente', ok: !!health.data_db_exists },
        { label: 'Templates C1 y C2 listos', ok: !!health.templates_capa1_exists && !!health.templates_capa2_exists },
        { label: hasMinings ? (minings.length + ' minings cargados') : 'Plan de minings pendiente', ok: hasMinings },
        { label: outputReady ? 'Output accesible' : 'Output pendiente', ok: outputReady },
        { label: outputFiles.length ? 'Primer .cfx generado' : 'Primer .cfx pendiente', ok: outputFiles.length > 0 }
      ],
      primaryLabel: 'Comprobar API',
      secondaryLabel: 'Abrir configuracion',
      tertiaryLabel: 'Guardar config',
      tertiaryAction: 'save',
      tertiaryVisible: true,
      primaryDisabled: false,
      title: 'Preparando flujo guiado',
      desc: 'Conecta la API y deja la configuracion lista para generar tu primer .cfx.',
      assistantNext: 'Comprobar API',
      assistantHint: 'Primero necesitamos confirmar que el backend local responde.'
    };

    if (!current) {
      state.title = 'Todo listo para producir';
      state.desc = 'Ya tienes la base configurada. Puedes abrir output o seguir afinando paths y templates.';
      state.primaryLabel = 'Abrir output';
      state.secondaryLabel = 'Abrir configuracion';
      state.tertiaryLabel = 'Actualizar estado';
      state.tertiaryAction = 'refresh';
      state.assistantNext = 'Produccion lista';
      state.assistantHint = 'La base esta preparada. Puedes generar mas proyectos o abrir la carpeta output.';
      return state;
    }

    if (current.id === 'api') {
      state.title = '1. Comprueba la API local';
      state.desc = 'El dashboard necesita el backend activo para leer config, minings, output y generar proyectos.';
      state.primaryLabel = 'Comprobar API';
      state.tertiaryVisible = false;
      state.assistantNext = 'Arrancar o comprobar backend';
      state.assistantHint = 'Si no conecta, usa START_SQX_EDGE.bat y vuelve a pulsar Comprobar API.';
      return state;
    }

    if (current.id === 'sqx') {
      state.title = hasSqxInput ? '2. Valida la ruta de SQX' : '2. Detecta tu instalacion de SQX';
      state.desc = hasSqxInput
        ? 'Valida la ruta actual para rellenar data.db y projects sin tener que tocar nada mas.'
        : 'Busca StrategyQuant X automaticamente o pega la ruta manualmente en configuracion.';
      state.primaryLabel = hasSqxInput ? 'Validar ruta SQX' : 'Auto-detectar SQX';
      state.tertiaryVisible = hasUnsavedSqxCandidate;
      state.assistantNext = hasSqxInput ? 'Validar y guardar ruta SQX' : 'Detectar instalacion SQX';
      state.assistantHint = hasSqxInput
        ? 'Si la validacion sale bien, guarda la configuracion para que el asistente avance.'
        : 'El asistente puede buscar instalaciones habituales de SQX y rellenar los campos por ti.';
      return state;
    }

    if (current.id === 'templates') {
      state.title = '3. Deja templates y output listos';
      state.desc = 'Revisa que existan las dos plantillas .cfx y que la carpeta output apunte al destino correcto.';
      state.primaryLabel = 'Revisar configuracion';
      state.secondaryLabel = 'Reintentar estado';
      state.tertiaryLabel = 'Guardar config';
      state.tertiaryAction = 'save';
      state.assistantNext = 'Completar templates y output';
      state.assistantHint = 'Cuando Capa 1, Capa 2 y output existan, el ultimo paso sera generar el primer .cfx.';
      return state;
    }

    state.title = hasMinings ? '4. Genera tu primer .cfx' : '4. Falta el plan de minings';
    state.desc = hasMinings
      ? ('Generaremos un ejemplo con el primer mining (' + minings[0].asset + ' ' + minings[0].tf + ') para dejar la rueda girando.')
      : 'No hay minings disponibles. Revisa el manifest del plan antes de continuar.';
    state.primaryLabel = hasMinings ? 'Generar primer .cfx' : 'Reintentar estado';
    state.primaryDisabled = !hasMinings;
    state.tertiaryLabel = 'Actualizar output';
    state.tertiaryAction = 'output';
    state.assistantNext = hasMinings ? 'Generar primer proyecto' : 'Recargar plan';
    state.assistantHint = hasMinings
      ? 'El asistente usara el primer mining del plan como prueba controlada.'
      : 'Sin minings no hay proyecto que generar; refresca el estado para volver a leer el plan.';
    return state;
  }

  function setText(doc, id, value) {
    var node = doc.getElementById(id);
    if (node) node.textContent = value == null ? '' : String(value);
    return node;
  }

  function prepareRequestOptions(options) {
    var opts = Object.assign({}, options || {});
    if (opts.body && typeof opts.body !== 'string') {
      opts.body = JSON.stringify(opts.body);
      opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    }
    return opts;
  }

  async function fetchJson(apiBase, apiPath, options, fetchImpl) {
    var request = fetchImpl || global.fetch;
    if (typeof request !== 'function') throw new Error('Fetch API no disponible');
    var response = await request((apiBase || '') + apiPath, prepareRequestOptions(options));
    var text = await response.text();
    var data = {};
    try {
      data = text ? JSON.parse(text) : {};
    } catch (_err) {
      data = { ok: false, error: text || ('HTTP ' + response.status) };
    }
    if (!response.ok || data.ok === false) throw new Error(data.error || ('HTTP ' + response.status));
    return data;
  }

  function applyStatusBanner(status, doc) {
    var target = doc || global.document;
    var banner = target.getElementById('pg-status-banner');
    var title = target.getElementById('pg-status-title');
    var desc = target.getElementById('pg-status-desc');
    if (!banner) return false;
    banner.classList.remove('pg-status-up', 'pg-status-down', 'pg-status-loading');
    banner.classList.add('pg-status-' + status.state);
    if (title) title.textContent = status.title || '';
    if (desc) desc.textContent = status.desc || '';
    return true;
  }

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

  function cleanerTableHtml(files, selectedPaths) {
    var selected = selectedPaths || {};
    if (!files || !files.length) return '';
    return ''
      + '<div class="matrix-wrap" style="max-height:380px;">'
      +   '<table class="cat-table" style="font-size:11px;">'
      +     '<thead><tr>'
      +       '<th style="width:30px;"><input type="checkbox" id="cln-th-check"></th>'
      +       '<th>Archivo</th><th>Asset</th><th>TF</th><th>Dir</th>'
      +       '<th>EAB</th><th>ID</th><th>KB</th>'
      +     '</tr></thead><tbody>'
      +     files.map(function(file) {
              var checked = selected[file.path] ? 'checked' : '';
              var eabClass = file.exit_after_bars_count > 0 ? 'cv-num warn' : 'cv-num pos';
              return ''
                + '<tr>'
                +   '<td><input type="checkbox" class="cln-row-check" data-path="' + escapeHtml(file.path) + '" ' + checked + '></td>'
                +   '<td style="font-family:Consolas,monospace;">' + escapeHtml(file.name) + '</td>'
                +   '<td><strong>' + escapeHtml(file.asset) + '</strong></td>'
                +   '<td>' + escapeHtml(file.timeframe) + '</td>'
                +   '<td>' + escapeHtml(file.direction) + '</td>'
                +   '<td class="' + eabClass + '">' + escapeHtml(file.exit_after_bars_count) + '</td>'
                +   '<td>' + escapeHtml(file.fitness_id) + '</td>'
                +   '<td style="color:var(--text2);">' + escapeHtml(file.size_kb) + '</td>'
                + '</tr>';
            }).join('')
      +     '</tbody></table>'
      + '</div>';
  }

  function cleanerSelectedMap(selectedPaths) {
    var selected = {};
    (selectedPaths || []).forEach(function(path) {
      selected[path] = true;
    });
    return selected;
  }

  function cleanerSelectedLabel(count) {
    return (count || 0) + ' seleccionadas';
  }

  function cleanerScanMessage(result) {
    var data = result || {};
    if (data.ok === false) {
      return {
        text: '✗ ' + (data.error || 'Error escaneando .sqx'),
        color: 'var(--red)',
        actionsDisplay: 'none'
      };
    }
    var count = data.count || 0;
    return {
      text: '✓ ' + count + ' archivos .sqx encontrados',
      color: 'var(--green)',
      actionsDisplay: count > 0 ? 'block' : 'none'
    };
  }

  function cleanerPreviewPattern(value) {
    var pattern = String(value || '').trim();
    return pattern || '{asset}_{tf}_{dir}_{id}';
  }

  function cleanerPreviewHeader(previews) {
    return 'Preview rename para ' + ((previews || []).length) + ' archivos:';
  }

  function cleanerPreviewLines(previews) {
    return (previews || []).map(function(preview) {
      if (preview.error) {
        return {
          text: '  ✗ ' + preview.path + ': ' + preview.error,
          level: 'err'
        };
      }
      return {
        text: '  ' + preview.current + ' → ' + preview.new_name,
        level: 'info'
      };
    });
  }

  function cleanerOptions(input) {
    var data = input || {};
    return {
      remove_exit_bars: !!data.removeExitBars,
      rename_institutional: !!data.renameInstitutional,
      rename_pattern: data.renamePattern || '{asset}_{tf}_{dir}_{id}'
    };
  }

  function cleanerHasAction(options) {
    return !!(options && (options.remove_exit_bars || options.rename_institutional));
  }

  function cleanerConfirmMessage(selectedCount, options) {
    var opts = options || {};
    return 'Procesar ' + selectedCount + ' archivos?\n\n'
      + (opts.remove_exit_bars ? '- Eliminar ExitAfterBars (set 0)\n' : '')
      + (opts.rename_institutional ? '- Renombrar a: ' + opts.rename_pattern + '\n' : '')
      + '\nSe crea backup automatico antes de modificar cada .sqx.';
  }

  function cleanerResultSummary(result) {
    var data = result || {};
    return 'Resultado: ' + (data.ok_count || 0) + ' OK · ' + (data.fail_count || 0) + ' FAIL';
  }

  function cleanerResultLevel(result) {
    return result && result.fail_count === 0 ? 'ok' : 'err';
  }

  function basename(filePath) {
    return String(filePath || '').split(/[\\/]/).pop();
  }

  function cleanerResultLines(results) {
    return (results || []).map(function(result) {
      var status = result.ok ? 'OK' : 'FAIL';
      return status + ' ' + basename(result.path) + ' - ' + (result.actions || []).join(', ');
    });
  }

  function applyOnboardingState(state, doc) {
    var target = doc || global.document;
    var progress = target.getElementById('pg-onboarding-progress');
    var title = target.getElementById('pg-onboarding-title');
    var desc = target.getElementById('pg-onboarding-desc');
    var bar = target.getElementById('pg-onboarding-bar');
    var stepsEl = target.getElementById('pg-onboarding-steps');
    var primary = target.getElementById('pg-onboarding-action');
    var secondary = target.getElementById('pg-onboarding-secondary');
    var tertiary = target.getElementById('pg-onboarding-tertiary');
    var next = target.getElementById('pg-assistant-next');
    var hint = target.getElementById('pg-assistant-hint');
    var checksEl = target.getElementById('pg-assistant-checks');
    if (!progress || !title || !desc || !bar || !stepsEl || !primary || !secondary || !tertiary || !next || !hint || !checksEl) return false;

    setText(target, 'pg-onboarding-progress', state.completed + '/' + state.steps.length);
    setText(target, 'pg-onboarding-title', state.title);
    setText(target, 'pg-onboarding-desc', state.desc);
    bar.style.width = Math.round((state.completed / state.steps.length) * 100) + '%';
    stepsEl.innerHTML = state.steps.map(function(step, index) {
      var isCurrent = state.current && state.current.id === step.id;
      var cls = step.done ? 'pg-step done' : (isCurrent ? 'pg-step current' : 'pg-step');
      var status = step.done ? 'Listo' : (isCurrent ? 'En curso' : 'Pendiente');
      return ''
        + '<div class="' + cls + '">'
        +   '<div class="pg-step-top">'
        +     '<span class="pg-step-num">' + (index + 1) + '</span>'
        +     '<span class="pg-step-state">' + status + '</span>'
        +   '</div>'
        +   '<div class="pg-step-title">' + escapeHtml(step.label) + '</div>'
        +   '<div class="pg-step-desc">' + escapeHtml(step.detail || '') + '</div>'
        + '</div>';
    }).join('');
    primary.textContent = state.primaryLabel;
    primary.disabled = !!state.primaryDisabled;
    secondary.textContent = state.secondaryLabel;
    tertiary.textContent = state.tertiaryLabel;
    tertiary.dataset.pgAssistantAction = state.tertiaryAction || 'save';
    tertiary.style.display = state.tertiaryVisible === false ? 'none' : '';
    next.textContent = state.assistantNext;
    hint.textContent = state.assistantHint;
    checksEl.innerHTML = state.checks.map(function(check) {
      return ''
        + '<div class="pg-assistant-check ' + (check.ok ? 'ok' : 'warn') + '">'
        +   '<span class="pg-check-dot">' + (check.ok ? '&#10003;' : '!') + '</span>'
        +   '<span>' + escapeHtml(check.label) + '</span>'
        + '</div>';
    }).join('');
    return true;
  }

  SQX.projectGenerator = SQX.projectGenerator || {
    aliasTableHtml: aliasTableHtml,
    applyOnboardingState: applyOnboardingState,
    applyStatusBanner: applyStatusBanner,
    autodetectCandidatesHtml: autodetectCandidatesHtml,
    basename: basename,
    cleanerConfirmMessage: cleanerConfirmMessage,
    cleanerHasAction: cleanerHasAction,
    cleanerOptions: cleanerOptions,
    cleanerPreviewHeader: cleanerPreviewHeader,
    cleanerPreviewLines: cleanerPreviewLines,
    cleanerPreviewPattern: cleanerPreviewPattern,
    cleanerResultLevel: cleanerResultLevel,
    cleanerResultLines: cleanerResultLines,
    cleanerResultSummary: cleanerResultSummary,
    cleanerScanMessage: cleanerScanMessage,
    cleanerSelectedLabel: cleanerSelectedLabel,
    cleanerSelectedMap: cleanerSelectedMap,
    cleanerTableHtml: cleanerTableHtml,
    computeOnboardingState: computeOnboardingState,
    directionClass: directionClass,
    directionLabel: directionLabel,
    escapeHtml: escapeHtml,
    fetchJson: fetchJson,
    messageHtml: messageHtml,
    miningRowsHtml: miningRowsHtml,
    outputListHtml: outputListHtml,
    prepareRequestOptions: prepareRequestOptions,
    sqxAppliedHtml: sqxAppliedHtml,
    sqxNotFoundHtml: sqxNotFoundHtml,
    validateSqxPathHtml: validateSqxPathHtml,
    uniqueAssets: uniqueAssets
  };

  if (SQX.registerModule) {
    SQX.registerModule('project-generator', SQX.projectGenerator);
  }
})(window);
