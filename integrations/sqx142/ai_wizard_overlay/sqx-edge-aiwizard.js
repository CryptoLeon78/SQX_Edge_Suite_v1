(function(global) {
  "use strict";

  var VERSION = "sqx142-ai-wizard-overlay-v2";

  function safeApiBase(value) {
    var fallback = "http://127.0.0.1:5050/api";
    var raw = String(value || fallback).replace(/\/$/, "");
    try {
      var parsed = new URL(raw, fallback);
      var host = parsed.hostname;
      if (host === "127.0.0.1" || host === "localhost" || host === "::1") {
        return parsed.origin + parsed.pathname.replace(/\/$/, "");
      }
    } catch (err) {
      return fallback;
    }
    return fallback;
  }

  var API_BASE = safeApiBase(global.SQX_EDGE_AI_WIZARD_API_BASE);
  var state = {
    status: null,
    catalog: null,
    sessions: [],
    currentSession: null,
    draft: null,
    busy: false,
    error: "",
    paramInvalid: false
  };

  function byId(id) {
    return global.document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function(ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function fetchJson(path, options) {
    return global.fetch(API_BASE + path, Object.assign({ credentials: "include" }, options || {}))
      .then(function(response) {
        return response.json().catch(function() { return {}; }).then(function(json) {
          json._httpStatus = response.status;
          json._httpOk = response.ok;
          return json;
        });
      })
      .catch(function(err) {
        return { ok: false, error: err && err.message ? err.message : "request_failed" };
      });
  }

  function setBusy(value) {
    state.busy = !!value;
    render();
  }

  function currentAst() {
    return state.currentSession && state.currentSession.ast ? state.currentSession.ast : null;
  }

  function currentValidation() {
    return state.currentSession && state.currentSession.validation ? state.currentSession.validation : null;
  }

  function hasValidSession() {
    var validation = currentValidation();
    return !!(state.currentSession && validation && validation.ok && !state.paramInvalid);
  }

  function renderStatus() {
    var node = byId("sqx-edge-aiwizard-status");
    if (!node) return;
    if (state.busy) {
      node.textContent = "Procesando con Flask local, sin ejecutar SQX...";
      return;
    }
    if (state.error) {
      node.textContent = state.error;
      return;
    }
    if (state.status && state.status.ok) {
      var provider = state.status.data && state.status.data.provider || {};
      node.textContent = "Listo · provider " + escapeHtml(provider.id || "ollama") + " · Revision manual requerida";
      return;
    }
    node.textContent = "Conecta con SQX Edge Flask local para planificar el draft.";
  }

  function renderSessions() {
    var list = byId("sqx-edge-aiwizard-session-list");
    if (!list) return;
    if (!state.sessions.length) {
      list.innerHTML = "<p class=\"sqx-edge-aiwizard-muted\">Sin sesiones guardadas todavia.</p>";
      return;
    }
    list.innerHTML = state.sessions.map(function(session) {
      var active = state.currentSession && state.currentSession.sessionId === session.sessionId ? " is-active" : "";
      return "<button type=\"button\" class=\"sqx-edge-aiwizard-session-item" + active + "\" data-sqx-aiwizard-session-id=\"" + escapeHtml(session.sessionId) + "\">" +
        "<b>" + escapeHtml(session.title || "Sesion") + "</b>" +
        "<small>" + escapeHtml(session.promptSummary || session.updatedAt || "Reanudar sesion") + "</small>" +
        "</button>";
    }).join("");
  }

  function renderPreview() {
    var node = byId("sqx-edge-aiwizard-preview");
    if (!node) return;
    var ast = currentAst();
    var validation = currentValidation();
    if (!ast) {
      node.innerHTML = "<strong>Sin especificacion.</strong><p class=\"sqx-edge-aiwizard-muted\">Crea una sesion con una idea AlgoWizard: EMA, RSI, Bollinger, Stochastic, MACD, CCI o ADX.</p>";
      return;
    }
    if (validation && !validation.ok) {
      node.innerHTML = "<strong>Bloqueado.</strong><p class=\"sqx-edge-aiwizard-muted\">" + escapeHtml((validation.blockers || []).join(" · ") || "param_invalid") + "</p>";
      return;
    }
    node.innerHTML =
      "<strong>" + escapeHtml(ast.strategyName || "AI Wizard strategy") + "</strong>" +
      "<div class=\"sqx-edge-aiwizard-grid\">" +
      "<div class=\"sqx-edge-aiwizard-chip\"><span>Asset</span>" + escapeHtml(ast.asset) + "</div>" +
      "<div class=\"sqx-edge-aiwizard-chip\"><span>Timeframe</span>" + escapeHtml(ast.timeframe) + "</div>" +
      "<div class=\"sqx-edge-aiwizard-chip\"><span>Direccion</span>" + escapeHtml(ast.direction) + "</div>" +
      "<div class=\"sqx-edge-aiwizard-chip\"><span>Bloques</span>" + escapeHtml(((ast.catalogRefs || {}).blockIds || []).join(", ")) + "</div>" +
      "</div>" +
      "<p class=\"sqx-edge-aiwizard-muted\">AST validado contra catalogo local. El draft se bloquea si el compilador aun no soporta la mezcla de bloques.</p>";
  }

  function renderDraft() {
    var node = byId("sqx-edge-aiwizard-draft");
    if (!node) return;
    if (state.draft && state.draft.ok && state.draft.data && state.draft.data.draft) {
      var draft = state.draft.data.draft;
      node.innerHTML =
        "<strong>Draft .sqx preparado.</strong><p class=\"sqx-edge-aiwizard-muted\">" + escapeHtml(draft.fileName) + "</p>" +
        "<a class=\"sqx-edge-aiwizard-download\" href=\"" + escapeHtml(API_BASE + draft.downloadUrl) + "\">Descargar .sqx</a>";
      return;
    }
    node.innerHTML = "<strong>Draft pendiente.</strong><p class=\"sqx-edge-aiwizard-muted\">Generar draft se activa solo con sesion valida y parametros correctos.</p>";
  }

  function renderCatalog() {
    var node = byId("sqx-edge-aiwizard-catalog");
    if (!node) return;
    var catalog = state.catalog && state.catalog.data ? state.catalog.data.catalog : null;
    if (!catalog) {
      node.innerHTML = "<strong>Catalogo de ideas</strong><p class=\"sqx-edge-aiwizard-muted\">Cargando catalogo AlgoWizard...</p>";
      return;
    }
    var counts = catalog.counts || {};
    var blocks = (((catalog.wizard || {}).blocks) || []).slice(0, 18);
    node.innerHTML =
      "<strong>Catalogo de ideas</strong>" +
      "<div class=\"sqx-edge-aiwizard-catalog-stats\">" +
      "<span>" + escapeHtml(counts.wizardBlocks || 0) + " bloques</span>" +
      "<span>" + escapeHtml(counts.conditionItems || 0) + " condiciones</span>" +
      "<span>" + escapeHtml(counts.parameterSets || 0) + " param sets</span>" +
      "</div>" +
      "<div class=\"sqx-edge-aiwizard-catalog-grid\">" +
      blocks.map(function(block) {
        return "<button type=\"button\" class=\"sqx-edge-aiwizard-catalog-item\" data-sqx-aiwizard-archetype=\"" + escapeHtml(block.id) + "\">" +
          "<b>" + escapeHtml(block.id) + "</b><small>" + escapeHtml(block.returnType || "value") + "</small></button>";
      }).join("") +
      "</div>";
  }

  function renderParams() {
    var node = byId("sqx-edge-aiwizard-params");
    if (!node) return;
    var ast = currentAst();
    if (!ast) {
      node.innerHTML = "<strong>Parametros estructurados</strong><p class=\"sqx-edge-aiwizard-muted\">Crea o reanuda una sesion para editar parametros.</p>";
      return;
    }
    var risk = ((ast.actions || {}).risk) || {};
    node.innerHTML =
      "<strong>Parametros estructurados</strong>" +
      "<div class=\"sqx-edge-aiwizard-param-grid\">" +
      "<label>Asset<input data-sqx-aiwizard-param=\"asset\" data-sqx-aiwizard-asset=\"true\" value=\"" + escapeHtml(ast.asset || "") + "\"></label>" +
      "<label>Timeframe<input data-sqx-aiwizard-param=\"timeframe\" data-sqx-aiwizard-timeframe=\"true\" value=\"" + escapeHtml(ast.timeframe || "") + "\"></label>" +
      "<label>SL pips<input type=\"number\" min=\"0\" max=\"100000\" data-sqx-aiwizard-param=\"stopLossPips\" value=\"" + escapeHtml(risk.stopLossPips || 0) + "\"></label>" +
      "<label>TP pips<input type=\"number\" min=\"0\" max=\"100000\" data-sqx-aiwizard-param=\"takeProfitPips\" value=\"" + escapeHtml(risk.takeProfitPips || 0) + "\"></label>" +
      "</div>" +
      "<p data-sqx-aiwizard-param-error=\"risk\" class=\"sqx-edge-aiwizard-param-error" + (state.paramInvalid ? " is-visible" : "") + "\">param_invalid: usa valores numericos entre 0 y 100000.</p>" +
      "<div class=\"sqx-edge-aiwizard-actions sqx-edge-aiwizard-actions-compact\"><button id=\"sqx-edge-aiwizard-validate-params\" type=\"button\">Validar parametros</button><button id=\"sqx-edge-aiwizard-reset-params\" type=\"button\">Reset parametros</button></div>";
  }

  function renderGuide() {
    var node = byId("sqx-edge-aiwizard-guide");
    if (!node) return;
    var draftReady = !!(state.draft && state.draft.ok && state.draft.data && state.draft.data.draft);
    var planReady = hasValidSession();
    var draftState = draftReady ? "done" : (planReady ? "active" : "");
    node.innerHTML =
      "<section class=\"sqx-edge-aiwizard-useful\">" +
      "<strong>Flujo de trabajo</strong>" +
      "<div class=\"sqx-edge-aiwizard-steps\">" +
      "<div class=\"sqx-edge-aiwizard-step is-" + (state.currentSession ? "done" : "active") + "\"><span>1</span><p><b>Sesion reutilizable</b><small>Crea, reanuda o fork para conservar contexto.</small></p></div>" +
      "<div class=\"sqx-edge-aiwizard-step is-" + (planReady ? "done" : "") + "\"><span>2</span><p><b>AST validado</b><small>El plan debe usar IDs del catalogo AlgoWizard.</small></p></div>" +
      "<div class=\"sqx-edge-aiwizard-step is-" + draftState + "\"><span>3</span><p><b>Draft controlado</b><small>Descarga .sqx solo si el compilador lo soporta.</small></p></div>" +
      "<div class=\"sqx-edge-aiwizard-step\"><span>4</span><p><b>Revision manual final</b><small>Ajusta en AlgoWizard antes de cualquier validacion.</small></p></div>" +
      "</div>" +
      "</section>" +
      "<section class=\"sqx-edge-aiwizard-useful\">" +
      "<strong>Ideas soportadas ahora</strong>" +
      "<div class=\"sqx-edge-aiwizard-patterns\">" +
      "<button type=\"button\" data-sqx-aiwizard-prompt=\"EMA cross trend-following EURUSD H1 with SL/TP\"><b>EMA cross</b><small>Draftable</small></button>" +
      "<button type=\"button\" data-sqx-aiwizard-prompt=\"RSI mean reversion EURUSD H1 with SL/TP\"><b>RSI</b><small>Plan + bloqueo si no compila</small></button>" +
      "<button type=\"button\" data-sqx-aiwizard-prompt=\"Bollinger mean reversion EURUSD H1 with SL/TP\"><b>Bollinger</b><small>Parametros editables</small></button>" +
      "<button type=\"button\" data-sqx-aiwizard-prompt=\"MACD trend EURUSD H1 with SL/TP\"><b>MACD</b><small>Catalog-aware</small></button>" +
      "</div>" +
      "</section>";
  }

  function renderBlockers() {
    var node = byId("sqx-edge-aiwizard-blockers");
    if (!node) return;
    var blockers = [];
    var validation = currentValidation();
    if (validation && validation.blockers) blockers = blockers.concat(validation.blockers);
    if (state.draft && state.draft.blockers) blockers = blockers.concat(state.draft.blockers);
    if (state.paramInvalid) blockers.push("param_invalid");
    node.innerHTML = blockers.length
      ? blockers.map(function(code) { return "<span class=\"sqx-edge-aiwizard-blocker is-blocked\" data-sqx-aiwizard-blocker-code=\"" + escapeHtml(code) + "\">" + escapeHtml(code) + "</span>"; }).join(" ")
      : "Sin bloqueos activos. Ninguna accion lanza SQX ni escribe data.db.";
  }

  function renderActions() {
    var planButton = byId("sqx-edge-aiwizard-plan");
    var draftButton = byId("sqx-edge-aiwizard-generate");
    var forkButton = byId("sqx-edge-aiwizard-fork");
    if (planButton) planButton.disabled = state.busy;
    if (draftButton) draftButton.disabled = state.busy || !hasValidSession();
    if (forkButton) forkButton.disabled = state.busy || !state.currentSession;
  }

  function renderLog() {
    var node = byId("sqx-edge-aiwizard-log");
    if (!node) return;
    var lines = [
      "Overlay: " + VERSION,
      "API: Flask local only",
      "API override: localhost-only",
      "Provider directo desde navegador: blocked",
      "Runtime SQX launch: blocked",
      "data.db/databanks write: blocked"
    ];
    if (state.catalog) lines.push("Catalog HTTP: " + state.catalog._httpStatus);
    if (state.currentSession) lines.push("Sesion: " + state.currentSession.sessionId);
    if (state.draft) lines.push("Draft HTTP: " + state.draft._httpStatus);
    node.textContent = lines.join("\n");
  }

  function render() {
    renderStatus();
    renderSessions();
    renderPreview();
    renderDraft();
    renderCatalog();
    renderParams();
    renderGuide();
    renderBlockers();
    renderActions();
    renderLog();
  }

  function loadStatus() {
    return fetchJson("/sqx142/ai-wizard/status").then(function(result) {
      state.status = result;
      render();
      return result;
    });
  }

  function loadCatalog() {
    return fetchJson("/sqx142/ai-wizard/catalog").then(function(result) {
      state.catalog = result;
      render();
      return result;
    });
  }

  function loadSessions() {
    return fetchJson("/sqx142/ai-wizard/sessions").then(function(result) {
      state.sessions = result && result.data && result.data.sessions ? result.data.sessions : [];
      if (!state.currentSession && state.sessions.length) state.currentSession = state.sessions[0];
      render();
      return result;
    });
  }

  function hydrateSession(result) {
    if (result && result.ok && result.data && result.data.session) {
      state.currentSession = result.data.session;
      state.error = "";
      state.paramInvalid = false;
      loadSessions();
    } else {
      state.error = (result && (result.error || (result.blockers || []).join(" · "))) || "session_store_unavailable";
    }
    state.busy = false;
    render();
    return result;
  }

  function saveSession() {
    var input = byId("sqx-edge-aiwizard-prompt");
    var prompt = input ? input.value : "";
    setBusy(true);
    state.draft = null;
    if (state.currentSession) {
      return fetchJson("/sqx142/ai-wizard/sessions/" + encodeURIComponent(state.currentSession.sessionId) + "/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt })
      }).then(hydrateSession);
    }
    return fetchJson("/sqx142/ai-wizard/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: prompt, title: prompt.slice(0, 72) || "Nueva sesion" })
    }).then(hydrateSession);
  }

  function newSession() {
    state.currentSession = null;
    state.draft = null;
    state.error = "";
    state.paramInvalid = false;
    var input = byId("sqx-edge-aiwizard-prompt");
    if (input) input.value = "";
    render();
  }

  function resumeSession(sessionId) {
    setBusy(true);
    return fetchJson("/sqx142/ai-wizard/sessions/" + encodeURIComponent(sessionId)).then(hydrateSession);
  }

  function forkSession() {
    if (!state.currentSession) return;
    var ast = currentAst() || {};
    var prompt = "Fork " + (ast.strategyName || state.currentSession.title || "AI Wizard session");
    var input = byId("sqx-edge-aiwizard-prompt");
    if (input && input.value) prompt = input.value;
    state.currentSession = null;
    setBusy(true);
    return fetchJson("/sqx142/ai-wizard/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: prompt, title: "Fork " + (ast.strategyName || "AI Wizard") })
    }).then(hydrateSession);
  }

  function generateDraft() {
    if (!state.currentSession) return;
    setBusy(true);
    state.error = "";
    return fetchJson("/sqx142/ai-wizard/sessions/" + encodeURIComponent(state.currentSession.sessionId) + "/drafts", {
      method: "POST"
    }).then(function(result) {
      state.draft = result;
      state.busy = false;
      state.error = result.ok ? "" : (result.error || "draft_failed");
      render();
      return result;
    });
  }

  function validateParams() {
    var ast = currentAst();
    if (!ast) return;
    var sl = Number((byId("sqx-edge-aiwizard-shell").querySelector("[data-sqx-aiwizard-param='stopLossPips']") || {}).value || 0);
    var tp = Number((byId("sqx-edge-aiwizard-shell").querySelector("[data-sqx-aiwizard-param='takeProfitPips']") || {}).value || 0);
    state.paramInvalid = !Number.isFinite(sl) || !Number.isFinite(tp) || sl < 0 || tp < 0 || sl > 100000 || tp > 100000;
    if (state.paramInvalid) {
      render();
      return;
    }
    ast.asset = ((byId("sqx-edge-aiwizard-shell").querySelector("[data-sqx-aiwizard-param='asset']") || {}).value || ast.asset || "EURUSD").toUpperCase();
    ast.timeframe = ((byId("sqx-edge-aiwizard-shell").querySelector("[data-sqx-aiwizard-param='timeframe']") || {}).value || ast.timeframe || "H1").toUpperCase();
    ast.actions = ast.actions || {};
    ast.actions.risk = ast.actions.risk || {};
    ast.actions.risk.stopLossPips = sl;
    ast.actions.risk.takeProfitPips = tp;
    setBusy(true);
    return fetchJson("/sqx142/ai-wizard/sessions/" + encodeURIComponent(state.currentSession.sessionId) + "/spec", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ast: ast })
    }).then(hydrateSession);
  }

  function resetParams() {
    state.paramInvalid = false;
    render();
  }

  function applyPrompt(value) {
    var input = byId("sqx-edge-aiwizard-prompt");
    if (!input) return;
    input.value = value;
    state.draft = null;
    state.error = "";
    render();
    input.focus();
  }

  function toggle(open) {
    var shell = byId("sqx-edge-aiwizard-shell");
    if (!shell) return;
    shell.classList.toggle("is-open", open == null ? !shell.classList.contains("is-open") : !!open);
  }

  function mount() {
    if (byId("sqx-edge-aiwizard-shell")) return;
    var launcher = global.document.createElement("button");
    launcher.id = "sqx-edge-aiwizard-launch";
    launcher.className = "sqx-edge-aiwizard-launch";
    launcher.type = "button";
    launcher.textContent = "AI Wizard";
    launcher.addEventListener("click", function() { toggle(true); });

    var shell = global.document.createElement("section");
    shell.id = "sqx-edge-aiwizard-shell";
    shell.className = "sqx-edge-aiwizard-shell";
    shell.setAttribute("aria-label", "SQX Edge AI Wizard");
    shell.innerHTML =
      "<aside class=\"sqx-edge-aiwizard-side\">" +
      "<div class=\"sqx-edge-aiwizard-head\"><div><strong>SQX Edge AI Studio</strong><small>Sesiones reutilizables · Draft AlgoWizard .sqx</small></div><button class=\"sqx-edge-aiwizard-close\" id=\"sqx-edge-aiwizard-close\" type=\"button\">x</button></div>" +
      "<section id=\"sqx-edge-aiwizard-sessions\" class=\"sqx-edge-aiwizard-sessions\"><div class=\"sqx-edge-aiwizard-section-head\"><strong>Sesiones reutilizables</strong><button id=\"sqx-edge-aiwizard-session-new\" type=\"button\">Nueva sesion</button></div><div id=\"sqx-edge-aiwizard-session-list\" class=\"sqx-edge-aiwizard-session-list\"></div></section>" +
      "<textarea id=\"sqx-edge-aiwizard-prompt\" class=\"sqx-edge-aiwizard-input\" placeholder=\"Ejemplo: EMA cross trend-following EURUSD H1 with SL/TP\"></textarea>" +
      "<div class=\"sqx-edge-aiwizard-actions\"><button id=\"sqx-edge-aiwizard-plan\" type=\"button\">Guardar sesion</button><button id=\"sqx-edge-aiwizard-generate\" type=\"button\" disabled>Generar draft</button><button id=\"sqx-edge-aiwizard-fork\" type=\"button\" disabled>Fork</button></div>" +
      "<button id=\"sqx-edge-aiwizard-session-save\" type=\"button\" hidden>Guardar sesion</button><button id=\"sqx-edge-aiwizard-session-resume\" type=\"button\" hidden>Reanudar sesion</button>" +
      "<p id=\"sqx-edge-aiwizard-status\" class=\"sqx-edge-aiwizard-muted\"></p>" +
      "</aside>" +
      "<main class=\"sqx-edge-aiwizard-main\">" +
      "<div id=\"sqx-edge-aiwizard-preview\" class=\"sqx-edge-aiwizard-preview\"></div>" +
      "<div id=\"sqx-edge-aiwizard-draft\" class=\"sqx-edge-aiwizard-preview\"></div>" +
      "<div id=\"sqx-edge-aiwizard-params\" class=\"sqx-edge-aiwizard-useful\"></div>" +
      "<div id=\"sqx-edge-aiwizard-catalog\" class=\"sqx-edge-aiwizard-catalog\"></div>" +
      "<div id=\"sqx-edge-aiwizard-guide\" class=\"sqx-edge-aiwizard-guide\"></div>" +
      "<div id=\"sqx-edge-aiwizard-lineage\" class=\"sqx-edge-aiwizard-lineage\" data-sqx-aiwizard-fork-from=\"\"></div>" +
      "<details class=\"sqx-edge-aiwizard-diagnostics\"><summary>Diagnostico local</summary><p id=\"sqx-edge-aiwizard-blockers\"></p><pre id=\"sqx-edge-aiwizard-log\" class=\"sqx-edge-aiwizard-log\"></pre></details>" +
      "</main>";

    global.document.body.appendChild(launcher);
    global.document.body.appendChild(shell);
    byId("sqx-edge-aiwizard-close").addEventListener("click", function() { toggle(false); });
    byId("sqx-edge-aiwizard-session-new").addEventListener("click", newSession);
    byId("sqx-edge-aiwizard-plan").addEventListener("click", saveSession);
    byId("sqx-edge-aiwizard-generate").addEventListener("click", generateDraft);
    byId("sqx-edge-aiwizard-fork").addEventListener("click", forkSession);
    shell.addEventListener("click", function(event) {
      var promptTarget = event.target && event.target.closest ? event.target.closest("[data-sqx-aiwizard-prompt]") : null;
      if (promptTarget) applyPrompt(promptTarget.getAttribute("data-sqx-aiwizard-prompt") || "");
      var sessionTarget = event.target && event.target.closest ? event.target.closest("[data-sqx-aiwizard-session-id]") : null;
      if (sessionTarget) resumeSession(sessionTarget.getAttribute("data-sqx-aiwizard-session-id") || "");
      var catalogTarget = event.target && event.target.closest ? event.target.closest("[data-sqx-aiwizard-archetype]") : null;
      if (catalogTarget) applyPrompt(catalogTarget.getAttribute("data-sqx-aiwizard-archetype") + " EURUSD H1 with SL/TP");
      if (event.target && event.target.id === "sqx-edge-aiwizard-validate-params") validateParams();
      if (event.target && event.target.id === "sqx-edge-aiwizard-reset-params") resetParams();
    });
    Promise.all([loadStatus(), loadCatalog(), loadSessions()]).then(render);
    render();
  }

  if (global.document.readyState === "loading") {
    global.document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})(window);
