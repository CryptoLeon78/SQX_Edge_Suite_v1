(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};

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
        label: 'API SQX Edge',
        done: connected,
        detail: connected ? ('Backend listo en ' + apiBase) : 'Sin conexion con el servicio.'
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
          ? 'C1, C2 y workspace de descargas listos'
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
        { label: 'API SQX Edge responde', ok: connected },
        { label: hasDbInput ? 'data.db localizado' : 'data.db pendiente', ok: !!health.data_db_exists },
        { label: 'Templates C1 y C2 listos', ok: !!health.templates_capa1_exists && !!health.templates_capa2_exists },
        { label: hasMinings ? (minings.length + ' minings cargados') : 'Plan de minings pendiente', ok: hasMinings },
        { label: outputReady ? 'Descargas preparadas' : 'Descargas pendientes', ok: outputReady },
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
      assistantHint: 'Primero necesitamos confirmar que el servicio responde.'
    };

    if (!current) {
      state.title = 'Todo listo para producir';
      state.desc = 'Ya tienes la base configurada. Puedes descargar output o seguir afinando paths y templates.';
      state.primaryLabel = 'Descargar output';
      state.secondaryLabel = 'Abrir configuracion';
      state.tertiaryLabel = 'Actualizar estado';
      state.tertiaryAction = 'refresh';
      state.assistantNext = 'Produccion lista';
      state.assistantHint = 'La base esta preparada. Puedes generar mas proyectos o descargar los .cfx del output.';
      return state;
    }

    if (current.id === 'api') {
      state.title = '1. Comprueba la API SQX Edge';
      state.desc = 'El dashboard necesita el servicio activo para leer config, minings, output y generar proyectos.';
      state.primaryLabel = 'Comprobar API';
      state.tertiaryVisible = false;
      state.assistantNext = 'Comprobar servicio';
      state.assistantHint = 'Si no conecta, pulsa Reintentar o registra incidencia desde Control Panel.';
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
      state.desc = 'Revisa que existan las dos plantillas .cfx y que el output apunte al workspace correcto.';
      state.primaryLabel = 'Revisar configuracion';
      state.secondaryLabel = 'Reintentar estado';
      state.tertiaryLabel = 'Guardar config';
      state.tertiaryAction = 'save';
      state.assistantNext = 'Completar templates y output';
      state.assistantHint = 'Cuando Capa 1, Capa 2 y output existan, el ultimo paso sera generar el primer .cfx y descargarlo desde el navegador.';
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

  Object.assign(PG, {
    applyOnboardingState: applyOnboardingState,
    applyStatusBanner: applyStatusBanner,
    computeOnboardingState: computeOnboardingState,
    escapeHtml: escapeHtml,
    fetchJson: fetchJson,
    prepareRequestOptions: prepareRequestOptions
  });
})(window);
