(function(global) {
  "use strict";

  var VERSION = "sqx144-blocksettings-ai-overlay-v1";

  function safeApiBase(value) {
    var fallback = "http://127.0.0.1:5050/api";
    var raw = String(value || fallback).replace(/\/$/, "");
    try {
      var parsed = new URL(raw, fallback);
      if (parsed.hostname === "127.0.0.1" || parsed.hostname === "localhost" || parsed.hostname === "::1") {
        return parsed.origin + parsed.pathname.replace(/\/$/, "");
      }
    } catch (err) {
      return fallback;
    }
    return fallback;
  }

  function localOperatorApiBase(value) {
    return safeApiBase(value);
  }

  var API_BASE = localOperatorApiBase(global.SQX_EDGE_BSAI_API_BASE);
  var API_ORIGIN = (function() {
    try { return new URL(API_BASE).origin; } catch (err) { return "http://127.0.0.1:5050"; }
  })();
  var state = {
    visible: false,
    busy: false,
    sessionId: "",
    catalog: null,
    candidate: null,
    project: null,
    error: "",
    formDirty: false,
    currentSignature: "",
    lastPlannedSignature: "",
    lastCandidateSignature: "",
    lastProjectSignature: ""
  };

  function byId(id) {
    return global.document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function(ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function apiUrl(path) {
    var raw = String(path || "");
    if (/^https?:\/\//i.test(raw)) return safeApiBase(raw);
    if (raw.indexOf("/api/") === 0) return API_ORIGIN + raw;
    return API_BASE + (raw.charAt(0) === "/" ? raw : "/" + raw);
  }

  function fetchJson(path, options) {
    return global.fetch(apiUrl(path), Object.assign({ credentials: "include" }, options || {}))
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

  function normalizedPayload() {
    var prompt = byId("sqx-edge-bsai-prompt") ? byId("sqx-edge-bsai-prompt").value : "";
    var asset = byId("sqx-edge-bsai-asset") ? byId("sqx-edge-bsai-asset").value : "";
    var timeframe = byId("sqx-edge-bsai-timeframe") ? byId("sqx-edge-bsai-timeframe").value : "";
    var direction = byId("sqx-edge-bsai-direction") ? byId("sqx-edge-bsai-direction").value : "";
    var explicitBaseCanonicalId = byId("sqx-edge-bsai-base") ? byId("sqx-edge-bsai-base").value : "";
    return {
      prompt: String(prompt || "").trim(),
      asset: String(asset || "").trim().toUpperCase(),
      timeframe: String(timeframe || "").trim().toUpperCase(),
      direction: String(direction || "").trim(),
      explicitBaseCanonicalId: String(explicitBaseCanonicalId || "").trim()
    };
  }

  function formPayload() {
    return normalizedPayload();
  }

  function formSignature(payload) {
    var data = payload || normalizedPayload();
    return [
      data.prompt,
      data.asset,
      data.timeframe,
      data.direction,
      data.explicitBaseCanonicalId
    ].join("||");
  }

  function responseStillCurrent(signature) {
    return formSignature() === signature;
  }

  function candidateIsCurrent() {
    return !!(state.candidate && !state.formDirty && state.lastCandidateSignature === formSignature());
  }

  function projectIsCurrent() {
    return !!(state.project && !state.formDirty && state.lastProjectSignature === formSignature());
  }

  function planIsCurrent() {
    return !!(!state.formDirty && state.lastPlannedSignature === formSignature());
  }

  function markFormDirty() {
    var signature = formSignature();
    if (state.formDirty && state.currentSignature === signature) return;
    state.sessionId = "";
    state.candidate = null;
    state.project = null;
    state.error = "";
    state.formDirty = true;
    state.currentSignature = signature;
    state.lastPlannedSignature = "";
    state.lastCandidateSignature = "";
    state.lastProjectSignature = "";
    render();
  }

  function resetSession() {
    if (byId("sqx-edge-bsai-prompt")) byId("sqx-edge-bsai-prompt").value = "";
    if (byId("sqx-edge-bsai-asset")) byId("sqx-edge-bsai-asset").value = "AUDCAD";
    if (byId("sqx-edge-bsai-timeframe")) byId("sqx-edge-bsai-timeframe").value = "H1";
    if (byId("sqx-edge-bsai-direction")) byId("sqx-edge-bsai-direction").value = "long";
    if (byId("sqx-edge-bsai-base")) byId("sqx-edge-bsai-base").value = "";
    state.sessionId = "";
    state.candidate = null;
    state.project = null;
    state.error = "";
    state.busy = false;
    state.formDirty = false;
    state.currentSignature = formSignature();
    state.lastPlannedSignature = "";
    state.lastCandidateSignature = "";
    state.lastProjectSignature = "";
    render();
  }

  function blocksettingFromCandidate() {
    var candidate = state.candidate || (state.project && state.project.candidate) || null;
    if (!candidate) return null;
    if (candidate.blocksetting) return candidate.blocksetting;
    if (candidate.entry) return candidate.entry;
    return candidate;
  }

  function policyLabel(blocksetting) {
    var payload = normalizedPayload();
    var base = String((blocksetting && blocksetting.baseCanonicalId) || payload.explicitBaseCanonicalId || "");
    var policy = String((blocksetting && blocksetting.sourceVersionPolicy) || "");
    var requestedBase = String(payload.explicitBaseCanonicalId || "");
    var v7Selected = base.indexOf("_v7") >= 0 || requestedBase.indexOf("_v7") >= 0;
    if (v7Selected) {
      return "v7 explicito";
    }
    if (payload.timeframe === "D1" || base === "BS_Filtros_v6_D1" || policy.indexOf("v6_d1") >= 0) {
      return "D1 default v6_D1";
    }
    return "default v6/v6_D1";
  }

  function baseLabel(blocksetting) {
    if (blocksetting && blocksetting.baseCanonicalId) return blocksetting.baseCanonicalId;
    var payload = normalizedPayload();
    if (payload.explicitBaseCanonicalId) return payload.explicitBaseCanonicalId;
    if (payload.timeframe === "D1") return "BS_Filtros_v6_D1";
    return "BS_Filtros_v6";
  }

  function renderTrace(blocksetting) {
    if (!blocksetting) return "";
    var candidateId = blocksetting.canonicalId || (state.candidate && state.candidate.artifactId) || "";
    return "<div class=\"sqx-edge-bsai-trace\">" +
      "<div><span>Candidato activo</span><code>" + escapeHtml(candidateId || "pendiente") + "</code></div>" +
      "<div><span>Base usada</span><code>" + escapeHtml(baseLabel(blocksetting)) + "</code></div>" +
      "<div><span>Politica</span><code>" + escapeHtml(policyLabel(blocksetting)) + "</code></div>" +
      "</div>";
  }

  function downloadLabel(item) {
    var name = String((item && (item.name || item.filename)) || "");
    if (item && item.capa) return "Capa" + item.capa;
    if (/Capa1/i.test(name)) return "Capa1";
    if (/Capa2/i.test(name)) return "Capa2";
    return "Descarga";
  }

  function renderDownloads(files) {
    return "<div class=\"sqx-edge-bsai-downloads\">" + (files || []).map(function(item) {
      var href = apiUrl(item.downloadUrl);
      var name = item.name || item.filename || href;
      return "<a class=\"sqx-edge-bsai-download\" href=\"" + escapeHtml(href) + "\">" +
        "<span>" + escapeHtml(downloadLabel(item)) + "</span><code>" + escapeHtml(name) + "</code></a>";
    }).join("") + "</div>";
  }

  function renderCandidateDownload() {
    if (!state.candidate || !state.candidate.downloadUrl) return "";
    return "<div class=\"sqx-edge-bsai-downloads\"><a class=\"sqx-edge-bsai-download\" href=\"" +
      escapeHtml(apiUrl(state.candidate.downloadUrl)) +
      "\"><span>Candidato .sqb</span><code>Descargar .sqb candidato</code></a></div>";
  }

  function setBusy(value) {
    state.busy = !!value;
    render();
  }

  function setError(message) {
    state.error = message || "";
    state.busy = false;
    render();
  }

  function renderOutput() {
    var output = byId("sqx-edge-bsai-output");
    if (!output) return;
    if (state.busy) {
      output.innerHTML = "<strong>Preparando BSAI...</strong><small>Flask valida catalogo, versionado y trazabilidad.</small>";
      return;
    }
    if (state.error) {
      output.innerHTML = "<strong>Bloqueado</strong><small>" + escapeHtml(state.error) + "</small>";
      return;
    }
    if (state.formDirty) {
      output.innerHTML = "<strong>Cambios pendientes</strong><small>Pulsa Plan para validar esta demanda antes de guardar/generar.</small>";
      return;
    }
    if (projectIsCurrent() && state.project && state.project.files) {
      output.innerHTML = "<strong>Proyecto BSAI listo</strong><small>Descarga manual Capa1/Capa2. No se importa nada en SQX.</small>" +
        renderTrace(blocksettingFromCandidate()) + renderDownloads(state.project.files);
      return;
    }
    if (candidateIsCurrent()) {
      output.innerHTML = "<strong>Candidato guardado</strong>" +
        renderTrace(blocksettingFromCandidate()) + renderCandidateDownload();
      return;
    }
    if (planIsCurrent()) {
      output.innerHTML = "<strong>Plan validado</strong><small>Guarda el candidato .sqb para activar la generacion .cfx de esta demanda.</small>";
      return;
    }
    output.innerHTML = "<strong>Listo</strong><small>Describe el BlockSetting. No se sobrescriben v6/v7 oficiales.</small>";
  }

  function render() {
    var panel = byId("sqx-edge-bsai-panel");
    var signature = formSignature();
    if (panel) panel.hidden = !state.visible;
    var planButton = byId("sqx-edge-bsai-plan");
    var saveButton = byId("sqx-edge-bsai-save");
    var generateButton = byId("sqx-edge-bsai-generate");
    var resetButton = byId("sqx-edge-bsai-reset");
    if (planButton) planButton.disabled = state.busy;
    if (saveButton) saveButton.disabled = state.busy || state.formDirty || state.lastPlannedSignature !== signature;
    if (generateButton) generateButton.disabled = state.busy || !candidateIsCurrent();
    if (resetButton) resetButton.disabled = state.busy;
    renderOutput();
  }

  function ensureSession() {
    if (state.sessionId) return Promise.resolve({ ok: true, session: { sessionId: state.sessionId } });
    return fetchJson("/blocksettings/ai/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formPayload())
    }).then(function(result) {
      if (result.ok && result.session) state.sessionId = result.session.sessionId;
      return result;
    });
  }

  function plan() {
    var signature = formSignature();
    state.candidate = null;
    state.project = null;
    state.error = "";
    setBusy(true);
    return ensureSession().then(function(session) {
      if (!session.ok) throw new Error(session.error || "bsai_session_failed");
      return fetchJson("/blocksettings/ai/sessions/" + encodeURIComponent(state.sessionId) + "/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formPayload())
      });
    }).then(function(result) {
      if (!result.ok) throw new Error(result.error || "bsai_plan_failed");
      state.busy = false;
      if (!responseStillCurrent(signature)) {
        state.formDirty = true;
        render();
        return result;
      }
      state.currentSignature = signature;
      state.formDirty = false;
      state.lastPlannedSignature = signature;
      state.lastCandidateSignature = "";
      state.lastProjectSignature = "";
      state.project = null;
      state.candidate = null;
      state.error = "";
      render();
      return result;
    }).catch(function(err) {
      setError(err && err.message ? err.message : "bsai_plan_failed");
    });
  }

  function saveCandidate() {
    var signature = formSignature();
    if (state.lastPlannedSignature !== signature || state.formDirty) {
      setError("plan_required_for_current_form");
      return Promise.resolve({ ok: false, error: "plan_required_for_current_form" });
    }
    setBusy(true);
    return ensureSession().then(function(session) {
      if (!session.ok) throw new Error(session.error || "bsai_session_failed");
      return fetchJson("/blocksettings/ai/sessions/" + encodeURIComponent(state.sessionId) + "/save-candidate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formPayload())
      });
    }).then(function(result) {
      if (!result.ok) throw new Error(result.error || "bsai_save_candidate_failed");
      state.busy = false;
      if (!responseStillCurrent(signature)) {
        state.formDirty = true;
        render();
        return result;
      }
      state.candidate = result.candidate;
      state.project = null;
      state.error = "";
      state.formDirty = false;
      state.currentSignature = signature;
      state.lastPlannedSignature = signature;
      state.lastCandidateSignature = signature;
      state.lastProjectSignature = "";
      render();
      return result;
    }).catch(function(err) {
      setError(err && err.message ? err.message : "bsai_save_candidate_failed");
    });
  }

  function generateProject() {
    var signature = formSignature();
    if (!candidateIsCurrent()) {
      setError("candidate_required_for_current_form");
      return Promise.resolve({ ok: false, error: "candidate_required_for_current_form" });
    }
    setBusy(true);
    return ensureSession().then(function(session) {
      if (!session.ok) throw new Error(session.error || "bsai_session_failed");
      return fetchJson("/blocksettings/ai/sessions/" + encodeURIComponent(state.sessionId) + "/generate-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formPayload())
      });
    }).then(function(result) {
      if (!result.ok) throw new Error(result.error || "bsai_generate_project_failed");
      state.busy = false;
      if (!responseStillCurrent(signature)) {
        state.formDirty = true;
        render();
        return result;
      }
      state.project = result;
      state.candidate = Object.assign({}, state.candidate || {}, result.candidate || {});
      state.error = "";
      state.formDirty = false;
      state.currentSignature = signature;
      state.lastPlannedSignature = signature;
      state.lastCandidateSignature = signature;
      state.lastProjectSignature = signature;
      render();
      return result;
    }).catch(function(err) {
      setError(err && err.message ? err.message : "bsai_generate_project_failed");
    });
  }

  function bindFormInvalidation() {
    [
      "sqx-edge-bsai-prompt",
      "sqx-edge-bsai-asset",
      "sqx-edge-bsai-timeframe",
      "sqx-edge-bsai-direction",
      "sqx-edge-bsai-base"
    ].forEach(function(id) {
      var node = byId(id);
      if (!node) return;
      node.addEventListener("input", markFormDirty);
      node.addEventListener("change", markFormDirty);
    });
  }

  function mount() {
    if (byId("sqx-edge-bsai-panel")) return;
    var launcher = global.document.createElement("button");
    launcher.id = "sqx-edge-bsai-launcher";
    launcher.className = "sqx-edge-bsai-launcher";
    launcher.type = "button";
    launcher.textContent = "BS-AI";
    launcher.addEventListener("click", function() {
      state.visible = !state.visible;
      render();
    });
    var panel = global.document.createElement("section");
    panel.id = "sqx-edge-bsai-panel";
    panel.className = "sqx-edge-bsai-panel";
    panel.hidden = true;
    panel.innerHTML =
      "<div class=\"sqx-edge-bsai-head\"><div><strong>BlockSettings AI</strong><small>" + VERSION + " - v6/v7 protegidos</small></div><button class=\"sqx-edge-bsai-close\" id=\"sqx-edge-bsai-close\" type=\"button\">x</button></div>" +
      "<div class=\"sqx-edge-bsai-body\">" +
      "<label>Demanda<textarea id=\"sqx-edge-bsai-prompt\" placeholder=\"Ej: filtros H1 con ADX para AUDCAD largo\"></textarea></label>" +
      "<div class=\"sqx-edge-bsai-grid\"><label>Asset<input id=\"sqx-edge-bsai-asset\" value=\"AUDCAD\"></label><label>Timeframe<select id=\"sqx-edge-bsai-timeframe\"><option>H1</option><option>M5</option><option>M15</option><option>M30</option><option>H4</option><option>D1</option></select></label></div>" +
      "<div class=\"sqx-edge-bsai-grid\"><label>Direccion<select id=\"sqx-edge-bsai-direction\"><option value=\"long\">Long</option><option value=\"short\">Short</option><option value=\"both\">L+S</option></select></label><label>Base explicita<input id=\"sqx-edge-bsai-base\" placeholder=\"solo para v7/manual\"></label></div>" +
      "</div><div class=\"sqx-edge-bsai-actions\"><button id=\"sqx-edge-bsai-reset\" type=\"button\">Nueva sesion / Limpiar</button><button id=\"sqx-edge-bsai-plan\" type=\"button\">Plan</button><button id=\"sqx-edge-bsai-save\" type=\"button\">Guardar .sqb</button><button id=\"sqx-edge-bsai-generate\" type=\"button\">Generar .cfx</button></div><div class=\"sqx-edge-bsai-output\" id=\"sqx-edge-bsai-output\"></div>";
    global.document.body.appendChild(launcher);
    global.document.body.appendChild(panel);
    byId("sqx-edge-bsai-close").addEventListener("click", function() {
      state.visible = false;
      render();
    });
    byId("sqx-edge-bsai-reset").addEventListener("click", resetSession);
    byId("sqx-edge-bsai-plan").addEventListener("click", plan);
    byId("sqx-edge-bsai-save").addEventListener("click", saveCandidate);
    byId("sqx-edge-bsai-generate").addEventListener("click", generateProject);
    bindFormInvalidation();
    state.currentSignature = formSignature();
    render();
    fetchJson("/blocksettings/ai/catalog").then(function(result) {
      if (result && result.ok) state.catalog = result.catalog || null;
    });
  }

  if (global.document.readyState === "loading") {
    global.document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }

  global.SQX_EDGE_BSAI_OVERLAY = {
    version: VERSION,
    apiBase: API_BASE,
    apiUrl: apiUrl,
    fetchJson: fetchJson,
    state: state,
    formPayload: formPayload,
    formSignature: formSignature,
    markFormDirty: markFormDirty,
    resetSession: resetSession,
    candidateIsCurrent: candidateIsCurrent,
    projectIsCurrent: projectIsCurrent
  };
})(window);
