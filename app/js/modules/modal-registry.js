(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var ACTIVE_MODALS = [
    {
      id: 'tm-modal-audit',
      tab: 'Template Maker',
      owner: 'template-maker-ui',
      action: 'auditar estrategias cargadas',
      reads: ['IndexedDB SQXTemplateMakerDB', 'CSV Template Maker Cert', '.sqx cargados'],
      writes: ['solo lectura'],
      trace: ['view detectada', 'contrato', 'estrategias', 'clusters', 'ganadoras C2'],
      failures: ['CSV incompleto', 'SQX faltante', 'contrato antiguo', 'cluster no calculado']
    },
    {
      id: 'tm-modal-c2',
      tab: 'Template Maker',
      owner: 'template-maker-ui',
      action: 'generar template C2 trazable',
      reads: ['estrategia certificada', 'logica SQX', 'cluster diversidad'],
      writes: ['descarga .sqx C2'],
      trace: ['asset', 'BlockSetting', 'indicador base', 'NumCluster', 'direccion', 'timeframe', 'origen'],
      failures: ['sin indicador', 'sin cluster', 'sin .sqx', 'no PASSED']
    },
    {
      id: 'strat-modal-backdrop',
      tab: 'Strategy Control',
      owner: 'dashboard',
      action: 'crear JSON manual de estrategia',
      reads: ['formulario manual'],
      writes: ['JSON copiable compatible con strategies.json'],
      trace: ['origen manual', 'asset', 'mining', 'template', 'blocksetting', 'status'],
      failures: ['campos minimos vacios', 'metricas incompletas', 'duplicado al consolidar']
    },
    {
      id: 'strat-import-backdrop',
      tab: 'Strategy Control',
      owner: 'dashboard',
      action: 'importar CSV Databank',
      reads: ['CSV Databank Export', 'meta comun del wizard'],
      writes: ['localStorage sqx_strategies_user_v1'],
      trace: ['batch import', 'columnas detectadas', 'seleccionadas', 'duplicadas', 'destino'],
      failures: ['CSV invalido', 'columnas no reconocidas', 'duplicados', 'localStorage no disponible']
    },
    {
      id: 'ps-add-mining-backdrop',
      tab: 'Mining Control',
      owner: 'dashboard',
      action: 'anadir mining al plan',
      reads: ['formulario + Mining', 'Plan Mining activo'],
      writes: ['localStorage sqx_plan_user_v1'],
      trace: ['origen manual', 'fase', 'asset', 'timeframe', 'blocksetting', 'direccion'],
      failures: ['duplicado real', 'fase inexistente', 'campos obligatorios vacios']
    },
    {
      id: 'ps-add-phase-backdrop',
      tab: 'Mining Control',
      owner: 'dashboard',
      action: 'crear fase del plan',
      reads: ['formulario + Fase', 'fases actuales'],
      writes: ['localStorage sqx_plan_user_v1'],
      trace: ['numero fase', 'nombre', 'descripcion', 'orden', 'estado vacio visible'],
      failures: ['fase duplicada', 'nombre vacio']
    },
    {
      id: 'state-restore-backdrop',
      tab: 'Control Panel',
      owner: 'state-backup',
      action: 'restaurar snapshot local',
      reads: ['backup local API /state/backups'],
      writes: ['localStorage permitido'],
      trace: ['snapshot', 'fecha', 'tamano', 'claves permitidas', 'backup previo automatico'],
      failures: ['API offline', 'snapshot corrupto', 'restore parcial']
    },
    {
      id: 'sqx-decision-backdrop',
      tab: 'Global',
      owner: 'modal-registry',
      action: 'confirmar decisiones criticas',
      reads: ['contexto de la accion solicitada'],
      writes: ['solo delega en la accion confirmada'],
      trace: ['origen', 'impacto', 'destino', 'recuperacion'],
      failures: ['cancelacion usuario', 'accion bloqueada por validacion']
    }
  ];

  var NATIVE_DECISIONS = [
    'reset plan mining',
    'reset fase',
    'eliminar mining',
    'eliminar fase',
    'editar fase',
    'eliminar estrategia',
    'limpiar importadas',
    'restore state',
    'consolidar JSON popup bloqueado'
  ];

  function esc(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function listItems(items) {
    return (items || []).filter(Boolean).map(function(item) {
      return '<span>' + esc(item) + '</span>';
    }).join('');
  }

  function tracePanelHtml(title, items, extraClass) {
    return '<div class="modal-trace-panel ' + esc(extraClass || '') + '">' +
      '<strong>' + esc(title || 'Trazabilidad') + '</strong>' +
      '<div class="modal-trace-items">' + listItems(items || []) + '</div>' +
    '</div>';
  }

  function getModal(id) {
    return ACTIVE_MODALS.find(function(modal) { return modal.id === id; }) || null;
  }

  function bindDecisionModal(doc) {
    var root = doc || global.document;
    var backdrop = root.getElementById('sqx-decision-backdrop');
    if (!backdrop || backdrop.dataset.bound === '1') return;
    backdrop.dataset.bound = '1';

    function resolve(value) {
      var pending = backdrop._sqxPending;
      backdrop.style.display = 'none';
      backdrop._sqxPending = null;
      if (pending) pending(value);
    }

    var cancel = root.getElementById('sqx-decision-cancel');
    var dismiss = root.getElementById('sqx-decision-dismiss');
    var confirm = root.getElementById('sqx-decision-confirm');
    if (cancel) cancel.addEventListener('click', function() { resolve({ ok: false, value: null }); });
    if (dismiss) dismiss.addEventListener('click', function() { resolve({ ok: false, value: null }); });
    if (confirm) confirm.addEventListener('click', function() {
      var input = root.getElementById('sqx-decision-input');
      resolve({ ok: true, value: input ? input.value : null });
    });
    backdrop.addEventListener('click', function(event) {
      if (event.target === backdrop) resolve({ ok: false, value: null });
    });
    root.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && backdrop.style.display !== 'none') resolve({ ok: false, value: null });
    });
  }

  function openDecision(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var backdrop = doc && doc.getElementById ? doc.getElementById('sqx-decision-backdrop') : null;
    if (!backdrop) {
      if (opts.mode === 'prompt' && global.prompt) {
        var answer = global.prompt(opts.message || opts.title || '', opts.value || '');
        return Promise.resolve({ ok: answer !== null, value: answer });
      }
      if (opts.mode === 'alert' && global.alert) {
        global.alert(opts.message || opts.title || '');
        return Promise.resolve({ ok: true, value: null });
      }
      var ok = !global.confirm || global.confirm(opts.message || opts.title || 'Confirmar accion');
      return Promise.resolve({ ok: !!ok, value: null });
    }
    bindDecisionModal(doc);
    var inputWrap = doc.getElementById('sqx-decision-input-wrap');
    var input = doc.getElementById('sqx-decision-input');
    var title = doc.getElementById('sqx-decision-title');
    var message = doc.getElementById('sqx-decision-message');
    var trace = doc.getElementById('sqx-decision-trace');
    var confirm = doc.getElementById('sqx-decision-confirm');
    var cancel = doc.getElementById('sqx-decision-dismiss');
    var inputLabel = doc.getElementById('sqx-decision-input-label');
    if (title) title.textContent = opts.title || 'Confirmar accion';
    if (message) message.textContent = opts.message || '';
    if (trace) trace.innerHTML = tracePanelHtml('Impacto de la decision', opts.trace || [], opts.risk || '');
    if (confirm) confirm.textContent = opts.confirmLabel || (opts.mode === 'alert' ? 'Entendido' : 'Confirmar');
    if (cancel) {
      cancel.textContent = opts.cancelLabel || 'Cancelar';
      cancel.style.display = opts.mode === 'alert' ? 'none' : 'inline-flex';
    }
    if (inputWrap && input) {
      var promptMode = opts.mode === 'prompt';
      inputWrap.hidden = !promptMode;
      input.value = opts.value || '';
      if (inputLabel) inputLabel.textContent = opts.inputLabel || 'Valor';
    }
    backdrop.style.display = 'flex';
    if (opts.mode === 'prompt' && input) input.focus();
    else if (confirm) confirm.focus();
    return new Promise(function(resolve) {
      backdrop._sqxPending = resolve;
    });
  }

  function confirmDecision(options) {
    return openDecision(Object.assign({ mode: 'confirm' }, options || {})).then(function(result) {
      return !!(result && result.ok);
    });
  }

  function promptDecision(options) {
    return openDecision(Object.assign({ mode: 'prompt' }, options || {})).then(function(result) {
      return result && result.ok ? result.value : null;
    });
  }

  function alertDecision(options) {
    return openDecision(Object.assign({ mode: 'alert' }, options || {}));
  }

  SQX.modalRegistry = SQX.modalRegistry || {
    bindDecisionModal: bindDecisionModal,
    confirm: confirmDecision,
    getModal: getModal,
    list: function() { return ACTIVE_MODALS.slice(); },
    nativeDecisions: function() { return NATIVE_DECISIONS.slice(); },
    prompt: promptDecision,
    alert: alertDecision,
    tracePanelHtml: tracePanelHtml
  };

  if (SQX.registerModule) {
    SQX.registerModule('modal-registry', SQX.modalRegistry);
  }
})(window);
