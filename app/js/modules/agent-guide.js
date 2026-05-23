(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var VERSION = 'local-ai-agent-ui-v1';
  var state = {
    status: null,
    plan: null,
    busy: false,
    error: '',
    lastAction: null
  };

  function byId(id) {
    return global.document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function apiBase() {
    var raw = (SQX.config && SQX.config.raw) || global.SQX_CONFIG || {};
    var base = raw.apiBase ? raw.apiBase() : '/api';
    return String(base || '/api').replace(/\/$/, '');
  }

  function fetchJson(path, options) {
    if (!global.fetch) return Promise.resolve({ ok: false, error: 'fetch_unavailable' });
    return global.fetch(apiBase() + path, Object.assign({ credentials: 'include' }, options || {}))
      .then(function(response) {
        return response.json().catch(function() { return {}; }).then(function(json) {
          json._httpStatus = response.status;
          json._httpOk = response.ok;
          return json;
        });
      })
      .catch(function(err) {
        return { ok: false, error: err && err.message ? err.message : 'request_failed' };
      });
  }

  function edgeState() {
    return SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
  }

  function currentStage() {
    var current = edgeState().activeStep || 'session';
    return String(current || 'session');
  }

  function setBusy(value) {
    state.busy = !!value;
    render();
  }

  function statusLabel() {
    if (!state.status) return 'Comprobando';
    if (state.status.active && state.status.access && state.status.access.remote) return 'IA SQX activa';
    if (state.status.active) return 'Ollama local activo';
    if (state.status.provider && state.status.provider.available === false) return 'Ollama no disponible';
    if (state.status.error === 'remote_ai_session_required') return 'Inicia sesion';
    if (state.status.error === 'local_ai_agent_access_denied') return 'Agente bloqueado';
    if (state.status.error) return 'API pendiente';
    return 'Modo IA';
  }

  function statusDetail() {
    var provider = state.status && state.status.provider ? state.status.provider : {};
    var auto = provider.autoStart || {};
    if (state.status && state.status.active) {
      return auto.attempted ? 'autostart verificado' : 'conexion directa';
    }
    if (auto.attempted && auto.reason) return 'autostart: ' + auto.reason;
    if (provider.error) return provider.error;
    return provider.model || provider.configuredModel || 'modelo IA';
  }

  function renderStatus() {
    var status = byId('agent-guide-status');
    var model = byId('agent-guide-model');
    var summaryStatus = byId('home-agent-status');
    var summaryModel = byId('home-agent-model');
    if (status) {
      status.textContent = statusLabel();
      status.classList.toggle('is-ok', !!(state.status && state.status.active));
      status.classList.toggle('is-warn', !!(state.status && !state.status.active));
    }
    var modelText = state.status && state.status.provider
      ? (statusDetail() + ' · ' + (state.status.provider.model || state.status.provider.configuredModel || 'modelo IA'))
      : 'modelo IA';
    var compat = state.status && state.status.sqx142Compat;
    if (compat && compat.visible !== false && compat.status) {
      modelText += ' · SQX ' + compat.status;
    }
    var perf = state.status && state.status.sqx142Performance;
    if (perf && perf.visible !== false && perf.activeProfile) {
      modelText += ' · Perf ' + (perf.activeProfile.id || perf.status || 'perfil');
    }
    if (model) model.textContent = modelText;
    if (summaryStatus) summaryStatus.textContent = statusLabel();
    if (summaryModel) summaryModel.textContent = modelText;
  }

  function renderPlan() {
    var output = byId('agent-guide-output');
    if (!output) return;
    if (state.busy) {
      output.innerHTML = '<strong>Pensando con contexto seguro...</strong><span>Sin ejecutar nada todavía.</span>';
      return;
    }
    if (state.error) {
      output.innerHTML = '<strong>No he podido preparar la accion.</strong><span>' + escapeHtml(state.error) + '</span>';
      return;
    }
    if (!state.plan) {
      output.innerHTML = '<strong>Listo para guiar.</strong><span>Pregunta qué hacer ahora o pide revisar la etapa activa.</span>';
      return;
    }
    var action = state.plan.recommendedAction || {};
    output.innerHTML =
      '<strong>' + escapeHtml(state.plan.reply || 'Recomendacion preparada.') + '</strong>' +
      '<span>Accion: ' + escapeHtml(action.label || action.id || 'sin accion') + '</span>' +
      (state.plan.blockers && state.plan.blockers.length
        ? '<small>Bloqueos: ' + escapeHtml(state.plan.blockers.join(' · ')) + '</small>'
        : '<small>Requiere confirmacion antes de ejecutar cualquier cambio.</small>');
  }

  function renderActions() {
    var confirm = byId('agent-guide-confirm');
    var cancel = byId('agent-guide-cancel');
    var hasAction = !!(state.plan && state.plan.recommendedAction && state.plan.recommendedAction.id);
    if (confirm) {
      confirm.disabled = state.busy || !hasAction;
      confirm.textContent = !hasAction || (state.plan && state.plan.requiresConfirmation) ? 'Confirmar accion' : 'Ejecutar lectura';
    }
    if (cancel) cancel.disabled = state.busy || !hasAction;
  }

  function renderSummary() {
    var summary = byId('home-agent-last-action');
    if (!summary) return;
    if (!state.lastAction) {
      summary.textContent = 'Sin acciones confirmadas en esta sesion.';
      return;
    }
    summary.textContent = state.lastAction.label + ' · ' + state.lastAction.timeLabel;
  }

  function render() {
    renderStatus();
    renderPlan();
    renderActions();
    renderSummary();
  }

  function loadStatus() {
    return fetchJson('/agent/status').then(function(result) {
      state.status = result;
      render();
      return result;
    });
  }

  function buildPlanPayload() {
    var input = byId('agent-guide-input');
    return {
      version: VERSION,
      message: input ? input.value : '',
      activeStep: currentStage(),
      edgeFactoryState: edgeState()
    };
  }

  function requestPlan() {
    setBusy(true);
    state.error = '';
    return fetchJson('/agent/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPlanPayload())
    }).then(function(result) {
      state.busy = false;
      if (!result.ok) {
        state.error = result.error || 'agent_plan_failed';
        state.plan = null;
      } else {
        state.plan = result;
      }
      render();
      return result;
    });
  }

  function applyUiCommand(command) {
    var cmd = command || {};
    if (cmd.type === 'open_tool' && cmd.tool) {
      if (SQX.edgeFactoryUI && SQX.edgeFactoryUI.openTool) {
        SQX.edgeFactoryUI.openTool(cmd.tool);
      } else if (SQX.ui && SQX.ui.activateTabById) {
        SQX.ui.activateTabById(cmd.tool, global.document);
      }
      return true;
    }
    if (cmd.type === 'complete_step' && cmd.stage && SQX.edgeFactory && SQX.edgeFactory.completeStep) {
      SQX.edgeFactory.completeStep(cmd.stage, cmd.done !== false);
      if (SQX.edgeFactoryUI && SQX.edgeFactoryUI.renderState) SQX.edgeFactoryUI.renderState();
      return true;
    }
    if (cmd.type === 'refresh_agent_status') {
      loadStatus();
      return true;
    }
    return false;
  }

  function executeCurrentPlan() {
    if (!state.plan || !state.plan.recommendedAction) return Promise.resolve({ ok: false, error: 'no_agent_action' });
    var action = state.plan.recommendedAction;
    setBusy(true);
    state.error = '';
    return fetchJson('/agent/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ actionId: action.id, arguments: action.arguments || {} })
    }).then(function(confirmation) {
      if (!confirmation.ok) throw new Error(confirmation.error || 'agent_confirmation_failed');
      return fetchJson('/agent/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actionId: action.id,
          confirmationToken: confirmation.confirmation && confirmation.confirmation.token,
          arguments: action.arguments || {}
        })
      });
    }).then(function(result) {
      state.busy = false;
      if (!result.ok) {
        state.error = result.error || 'agent_execute_failed';
      } else {
        applyUiCommand(result.uiCommand);
        state.lastAction = {
          id: action.id,
          label: action.label || action.id,
          timeLabel: new Date().toLocaleTimeString()
        };
        state.plan = null;
      }
      render();
      return result;
    }).catch(function(err) {
      state.busy = false;
      state.error = err && err.message ? err.message : 'agent_execute_failed';
      render();
      return { ok: false, error: state.error };
    });
  }

  function cancelPlan() {
    state.plan = null;
    state.error = '';
    render();
  }

  function bind() {
    var ask = byId('agent-guide-ask');
    var confirm = byId('agent-guide-confirm');
    var cancel = byId('agent-guide-cancel');
    var refresh = byId('agent-guide-refresh');
    if (ask && !ask.__agentGuideBound) {
      ask.__agentGuideBound = true;
      ask.addEventListener('click', requestPlan);
    }
    if (confirm && !confirm.__agentGuideBound) {
      confirm.__agentGuideBound = true;
      confirm.addEventListener('click', executeCurrentPlan);
    }
    if (cancel && !cancel.__agentGuideBound) {
      cancel.__agentGuideBound = true;
      cancel.addEventListener('click', cancelPlan);
    }
    if (refresh && !refresh.__agentGuideBound) {
      refresh.__agentGuideBound = true;
      refresh.addEventListener('click', loadStatus);
    }
    global.addEventListener('sqx:edge-factory-state', function() {
      if (!state.plan) render();
    });
  }

  function init() {
    if (!byId('agent-guide-dock')) return false;
    bind();
    render();
    loadStatus();
    return true;
  }

  SQX.agentGuide = {
    version: VERSION,
    init: init,
    loadStatus: loadStatus,
    requestPlan: requestPlan,
    executeCurrentPlan: executeCurrentPlan,
    cancelPlan: cancelPlan,
    applyUiCommand: applyUiCommand,
    getState: function() { return Object.assign({}, state); }
  };

  if (SQX.registerModule) SQX.registerModule('agent-guide', SQX.agentGuide);
})(window);
