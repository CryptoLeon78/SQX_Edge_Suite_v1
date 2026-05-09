(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var IDS = {
    sourceMode: 'sb-source-mode',
    asset: 'sb-asset',
    timeframe: 'sb-timeframe',
    archetype: 'sb-archetype',
    validationPack: 'sb-validation-pack',
    projectProfile: 'sb-project-profile',
    reviewed: 'sb-reviewed',
    build: 'sb-build-btn',
    sampleCvc: 'sb-sample-cvc-btn',
    importPackage: 'sb-import-btn',
    importFile: 'sb-import-file',
    sendProjectGenerator: 'sb-send-pg-btn',
    preparePreset: 'sb-prepare-preset-btn',
    sendViews: 'sb-send-views-btn',
    prepareCleaner: 'sb-prepare-cleaner-btn',
    prepareBuyerPack: 'sb-prepare-buyer-pack-btn',
    buyerSession: 'sb-buyer-session-btn',
    buyerSummary: 'sb-buyer-summary-btn',
    clear: 'sb-clear-btn',
    exportPackage: 'sb-export-btn',
    status: 'sb-status',
    preview: 'sb-package-preview',
    reviewList: 'sb-review-list',
    workflowSteps: 'sb-workflow-steps',
    auditList: 'sb-audit-list',
    state: 'sb-state',
    source: 'sb-source',
    assetOut: 'sb-asset-out',
    checks: 'sb-check-count'
  };

  var lastPackage = null;
  var lastBuyerHandoffPack = null;
  var lastBuyerPackReview = null;
  var lastBuyerSessionChecklist = null;
  var currentHandoff = null;
  var currentSourceSummary = null;
  var handoffAuditTrail = [];

  function core() {
    return SQX.strategyBuilderCore || null;
  }

  function byId(id, doc) {
    var target = doc || global.document;
    return target && target.getElementById ? target.getElementById(id) : null;
  }

  function value(id, doc) {
    var node = byId(id, doc);
    return node ? node.value || '' : '';
  }

  function checked(id, doc) {
    var node = byId(id, doc);
    return !!(node && node.checked);
  }

  function setValue(id, next, doc) {
    var node = byId(id, doc);
    if (node) node.value = next == null ? '' : String(next);
  }

  function setChecked(id, next, doc) {
    var node = byId(id, doc);
    if (node) node.checked = !!next;
  }

  function setText(id, next, doc) {
    var node = byId(id, doc);
    if (node) node.textContent = next == null ? '' : String(next);
  }

  function escapeHtml(value) {
    if (SQX.utils && SQX.utils.escapeHtml) return SQX.utils.escapeHtml(value);
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  function setStatus(message, tone, doc) {
    var node = byId(IDS.status, doc);
    if (!node) return;
    node.textContent = message || '';
    node.classList.remove('is-ok', 'is-warn', 'is-error');
    if (tone) node.classList.add('is-' + tone);
  }

  function optionHtml(value, label) {
    return '<option value="' + escapeHtml(value) + '">' + escapeHtml(label || value) + '</option>';
  }

  function fillOptions(doc) {
    var api = core();
    var source = byId(IDS.sourceMode, doc);
    var archetype = byId(IDS.archetype, doc);
    if (source && api) {
      source.innerHTML = [
        optionHtml('blank', 'Blank / manual'),
        optionHtml('cvc_handoff', 'CVC handoff'),
        optionHtml('project_generator_profile', 'Project Generator profile'),
        optionHtml('views_workflow', 'SQX Views workflow')
      ].join('');
    }
    if (archetype && api) {
      archetype.innerHTML = Object.keys(api.archetypes).map(function(id) {
        return optionHtml(id, api.archetypes[id].label);
      }).join('');
    }
  }

  function inputModel(doc) {
    return {
      source_mode: value(IDS.sourceMode, doc) || 'blank',
      source_handoff: currentHandoff,
      source_summary: currentSourceSummary,
      asset: value(IDS.asset, doc) || 'EURUSD',
      timeframe: value(IDS.timeframe, doc) || 'H1',
      idea_archetype: value(IDS.archetype, doc) || 'trend_following',
      validation_pack_id: value(IDS.validationPack, doc) || '',
      project_profile_id: value(IDS.projectProfile, doc) || '',
      operator_reviewed: checked(IDS.reviewed, doc),
      traceability: ['SB4 dashboard import/export hardening']
    };
  }

  function applyModel(model, doc) {
    if (!model) return;
    currentHandoff = model.source_handoff || model.sourceHandoff || null;
    currentSourceSummary = model.source_summary || model.sourceSummary || null;
    setValue(IDS.sourceMode, model.source_mode || model.sourceMode || 'blank', doc);
    setValue(IDS.asset, model.asset || 'EURUSD', doc);
    setValue(IDS.timeframe, model.timeframe || 'H1', doc);
    setValue(IDS.archetype, model.idea_archetype || model.ideaArchetype || 'trend_following', doc);
    setValue(IDS.validationPack, model.validation_pack_id || model.validationPackId || 'robustness', doc);
    setValue(IDS.projectProfile, model.project_profile_id || model.projectProfileId || 'starter-forex-h1-balanced', doc);
    setChecked(IDS.reviewed, !!(model.operator_reviewed || model.operatorReviewed), doc);
  }

  function renderPackage(payload, doc) {
    var preview = byId(IDS.preview, doc);
    var confirmed = (payload.operator_checklist || []).filter(function(item) { return item.confirmed; }).length;
    setText(IDS.state, payload.workflow_state, doc);
    setText(IDS.source, payload.source_mode, doc);
    setText(IDS.assetOut, payload.asset_profile.asset + ' ' + payload.asset_profile.timeframe, doc);
    setText(IDS.checks, confirmed + '/' + (payload.operator_checklist || []).length, doc);
    if (preview) preview.textContent = JSON.stringify(payload, null, 2);
    renderReviewList(payload, doc);
    renderBuyerWorkflow(payload, doc);
    setStatus(
      payload.workflow_state === 'package_exportable'
        ? 'Package ready for local export. Review remains mandatory before StrategyQuant use.'
        : 'Package preview blocked: ' + payload.workflow_state + '.',
      payload.workflow_state === 'package_exportable' ? 'ok' : 'warn',
      doc
    );
    return payload;
  }

  function reviewListHtml(payload) {
    var api = core();
    var summary = api && api.reviewChecklistSummary ? api.reviewChecklistSummary(payload) : {
      items: payload.operator_checklist || []
    };
    return (summary.items || []).map(function(item) {
      return ''
        + '<div class="sb-review-item ' + (item.confirmed ? 'is-ok' : 'is-warn') + '">'
        +   '<span>' + (item.confirmed ? 'OK' : '!') + '</span>'
        +   '<p>' + escapeHtml(item.label) + '</p>'
        + '</div>';
    }).join('');
  }

  function renderReviewList(payload, doc) {
    var list = byId(IDS.reviewList, doc);
    if (!list || !payload) return false;
    list.innerHTML = reviewListHtml(payload);
    return true;
  }

  function renderBuyerWorkflow(payload, doc) {
    var list = byId(IDS.workflowSteps, doc);
    var api = core();
    if (!list || !api || !api.buyerWorkflowSummary || !payload) return false;
    var summary = api.buyerWorkflowSummary(payload);
    list.innerHTML = summary.steps.map(function(step) {
      return ''
        + '<div class="sb-workflow-step is-' + escapeHtml(step.status) + '">'
        +   '<span>' + (step.status === 'done' ? 'OK' : '--') + '</span>'
        +   '<div><strong>' + escapeHtml(step.label) + '</strong><small>' + escapeHtml(step.note) + '</small></div>'
        + '</div>';
    }).join('');
    return true;
  }

  function renderAuditTrail(doc) {
    var list = byId(IDS.auditList, doc);
    if (!list) return false;
    if (!handoffAuditTrail.length) {
      list.innerHTML = '<div class="sb-audit-empty">Sin handoffs preparados en esta sesion.</div>';
      return true;
    }
    list.innerHTML = handoffAuditTrail.map(function(entry) {
      return ''
        + '<div class="sb-audit-row ' + (entry.ok ? 'is-ok' : 'is-warn') + '">'
        +   '<span>' + escapeHtml(entry.target) + '</span>'
        +   '<strong>' + escapeHtml(entry.asset + ' ' + entry.timeframe) + '</strong>'
        +   '<small>' + escapeHtml(entry.workflow_state + ' - accion final manual') + '</small>'
        + '</div>';
    }).join('');
    return true;
  }

  function addAuditEntry(target, payload, result, doc) {
    var api = core();
    if (!api || !api.handoffAuditEntry || !payload) return null;
    var entry = api.handoffAuditEntry(target, payload, result);
    handoffAuditTrail.unshift(entry);
    handoffAuditTrail = handoffAuditTrail.slice(0, 6);
    renderAuditTrail(doc);
    return entry;
  }

  function build(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    if (!api) {
      setStatus('Strategy Builder core missing.', 'error', doc);
      return null;
    }
    lastBuyerHandoffPack = null;
    lastBuyerPackReview = null;
    lastBuyerSessionChecklist = null;
    lastPackage = api.buildPackage(inputModel(doc));
    return renderPackage(lastPackage, doc);
  }

  function loadCvcSample(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    if (!api) return null;
    currentHandoff = api.sampleCvcHandoff();
    currentSourceSummary = null;
    setValue(IDS.sourceMode, 'cvc_handoff', doc);
    setValue(IDS.asset, 'EURUSD', doc);
    setValue(IDS.timeframe, 'H1', doc);
    setValue(IDS.archetype, 'trend_following', doc);
    setValue(IDS.validationPack, 'robustness', doc);
    setValue(IDS.projectProfile, 'starter-forex-h1-balanced', doc);
    setChecked(IDS.reviewed, true, doc);
    return build({ document: doc });
  }

  function clear(options) {
    var doc = options && options.document ? options.document : global.document;
    currentHandoff = null;
    currentSourceSummary = null;
    lastPackage = null;
    lastBuyerHandoffPack = null;
    lastBuyerPackReview = null;
    lastBuyerSessionChecklist = null;
    setValue(IDS.sourceMode, 'blank', doc);
    setValue(IDS.asset, 'EURUSD', doc);
    setValue(IDS.timeframe, 'H1', doc);
    setValue(IDS.archetype, 'trend_following', doc);
    setValue(IDS.validationPack, 'robustness', doc);
    setValue(IDS.projectProfile, 'starter-forex-h1-balanced', doc);
    setChecked(IDS.reviewed, false, doc);
    return build({ document: doc });
  }

  function safeFilename() {
    return 'sqx_strategy_builder_package_' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
  }

  function safeBuyerSessionSummaryFilename() {
    return 'sqx_buyer_session_summary_' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
  }

  function downloadJson(payload, filename, doc) {
    if (!global.Blob || !global.URL || !global.URL.createObjectURL || !doc || !doc.createElement) return false;
    var blob = new global.Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = global.URL.createObjectURL(blob);
    var link = doc.createElement('a');
    link.href = url;
    link.download = filename;
    if (link.click) link.click();
    global.setTimeout(function() { global.URL.revokeObjectURL(url); }, 0);
    return true;
  }

  function exportPackage(options) {
    var doc = options && options.document ? options.document : global.document;
    var payload = lastPackage || build({ document: doc });
    if (!payload || payload.workflow_state !== 'package_exportable') {
      setStatus('Export blocked until operator review is confirmed.', 'warn', doc);
      return null;
    }
    var downloaded = downloadJson(payload, safeFilename(), doc);
    addAuditEntry('Export JSON', payload, { ok: !!downloaded, guardrails: ['local_json_export'] }, doc);
    setStatus(downloaded ? 'Strategy Builder package exported locally.' : 'Strategy Builder package prepared in memory.', 'ok', doc);
    return payload;
  }

  function sendToProjectGenerator(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastPackage || build({ document: doc });
    if (!api || !api.projectGeneratorPrefillFromPackage) {
      setStatus('Project Generator prefill contract missing.', 'error', doc);
      return null;
    }
    var prefill = api.projectGeneratorPrefillFromPackage(payload);
    if (!prefill.ok) {
      setStatus('Project Generator prefill blocked: ' + prefill.errors.join(', ') + '.', 'warn', doc);
      return prefill;
    }
    var PG = SQX.projectGenerator || {};
    var dom = PG.dom || {};
    var config = PG.normalizeCustomProjectConfig ? PG.normalizeCustomProjectConfig(prefill.config) : prefill.config;
    if (!dom.writeCustomProjectInputs) {
      setStatus('Project Generator form is not available yet.', 'error', doc);
      return { ok: false, errors: ['project_generator_form_missing'], config: config };
    }
    dom.writeCustomProjectInputs(doc, config);
    if (dom.setCustomProjectStatus) {
      dom.setCustomProjectStatus(doc, {
        text: 'Prefill desde Strategy Builder. Revisa y pulsa Generar custom manualmente.',
        level: 'info'
      });
    }
    if (dom.appendLog) {
      dom.appendLog(doc, 'Strategy Builder prefill aplicado a Custom libre. Generacion manual pendiente.', 'info');
    }
    if (SQX.ui && SQX.ui.activateTabById) SQX.ui.activateTabById('projectgen', doc);
    addAuditEntry('Project Generator', payload, { ok: true, guardrails: prefill.guardrails }, doc);
    setStatus('Project Generator prefilled. No generation was triggered.', 'ok', doc);
    return { ok: true, errors: [], config: config, source: prefill.source, guardrails: prefill.guardrails };
  }

  function prepareProjectGeneratorPreset(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastPackage || build({ document: doc });
    if (!api || !api.projectGeneratorPresetDraftFromPackage) {
      setStatus('Project Generator preset draft contract missing.', 'error', doc);
      return null;
    }
    var draft = api.projectGeneratorPresetDraftFromPackage(payload);
    if (!draft.ok) {
      setStatus('Preset draft blocked: ' + draft.errors.join(', ') + '.', 'warn', doc);
      return draft;
    }
    var PG = SQX.projectGenerator || {};
    var dom = PG.dom || {};
    var config = PG.normalizeCustomProjectConfig ? PG.normalizeCustomProjectConfig(draft.config) : draft.config;
    if (!dom.writeCustomProjectInputs || !dom.setInputValue) {
      setStatus('Project Generator preset fields are not available yet.', 'error', doc);
      return { ok: false, errors: ['project_generator_preset_form_missing'], config: config };
    }
    dom.writeCustomProjectInputs(doc, config);
    dom.setInputValue(doc, 'pg-custom-preset-name', draft.preset_name);
    if (dom.setCustomProjectStatus) {
      dom.setCustomProjectStatus(doc, {
        text: 'Preset preparado desde Strategy Builder. Revisa y pulsa Guardar preset manualmente.',
        level: 'info'
      });
    }
    if (dom.appendLog) {
      dom.appendLog(doc, 'Strategy Builder preparo un borrador de preset. Guardado manual pendiente.', 'info');
    }
    if (SQX.ui && SQX.ui.activateTabById) SQX.ui.activateTabById('projectgen', doc);
    addAuditEntry('PG Preset Draft', payload, { ok: true, guardrails: draft.guardrails }, doc);
    setStatus('Project Generator preset draft prepared. No preset was saved.', 'ok', doc);
    return { ok: true, errors: [], config: config, preset_name: draft.preset_name, guardrails: draft.guardrails };
  }

  function sendToViews(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastPackage || build({ document: doc });
    if (!api || !api.sqxViewsHandoffFromPackage) {
      setStatus('SQX Views handoff contract missing.', 'error', doc);
      return null;
    }
    var result = api.sqxViewsHandoffFromPackage(payload);
    if (!result.ok) {
      setStatus('SQX Views handoff blocked: ' + result.errors.join(', ') + '.', 'warn', doc);
      return result;
    }
    if (!SQX.viewCreator || !SQX.viewCreator.openHandoff) {
      setStatus('SQX Views is not available yet.', 'error', doc);
      return { ok: false, errors: ['sqx_views_missing'], handoff: result.handoff };
    }
    SQX.viewCreator.openHandoff({
      preset: result.handoff.preset,
      viewName: result.handoff.viewName,
      yearCount: result.handoff.yearCount,
      sampleStart: result.handoff.sampleStart,
      groupMode: result.handoff.groupMode
    });
    addAuditEntry('SQX Views', payload, result, doc);
    setStatus('SQX Views prepared. No template was saved.', 'ok', doc);
    return result;
  }

  function setCleanerCheckbox(doc, id, checked) {
    var node = byId(id, doc);
    if (node) node.checked = !!checked;
  }

  function prepareStrategyCleaner(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastPackage || build({ document: doc });
    if (!api || !api.strategyCleanerDraftFromPackage) {
      setStatus('Strategy Cleaner draft contract missing.', 'error', doc);
      return null;
    }
    var result = api.strategyCleanerDraftFromPackage(payload);
    if (!result.ok) {
      setStatus('Strategy Cleaner draft blocked: ' + result.errors.join(', ') + '.', 'warn', doc);
      return result;
    }
    setCleanerCheckbox(doc, 'cln-recursive', result.draft.recursive);
    setCleanerCheckbox(doc, 'cln-opt-eab', result.draft.remove_exit_bars);
    setCleanerCheckbox(doc, 'cln-opt-rename', result.draft.rename_institutional);
    setValue('cln-pattern', result.draft.rename_pattern, doc);
    var patternWrap = byId('cln-pattern-wrap', doc);
    if (patternWrap) patternWrap.style.display = result.draft.rename_institutional ? 'inline-block' : 'none';
    var info = byId('cln-info', doc);
    if (info) {
      info.textContent = 'Draft desde Strategy Builder: elige carpeta .sqx, pulsa Escanear y procesa manualmente.';
      info.style.color = 'var(--accent)';
    }
    var PG = SQX.projectGenerator || {};
    var dom = PG.dom || {};
    if (dom.appendLog) {
      dom.appendLog(doc, 'Strategy Builder preparo opciones para Strategy Cleaner. Escaneo y limpieza manual pendientes.', 'info');
    }
    if (SQX.ui && SQX.ui.activateTabById) SQX.ui.activateTabById('projectgen', doc);
    addAuditEntry('Strategy Cleaner', payload, result, doc);
    setStatus('Strategy Cleaner draft prepared. No scan or cleanup was triggered.', 'ok', doc);
    return result;
  }

  function prepareBuyerHandoffPack(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastPackage || build({ document: doc });
    if (!api || !api.unifiedBuyerHandoffPackFromPackage) {
      setStatus('Buyer handoff pack contract missing.', 'error', doc);
      return null;
    }
    var result = api.unifiedBuyerHandoffPackFromPackage(payload);
    if (!result.ok) {
      setStatus('Buyer handoff pack blocked: ' + result.errors.join(', ') + '.', 'warn', doc);
      return result;
    }
    var preview = byId(IDS.preview, doc);
    if (preview) preview.textContent = JSON.stringify(result.pack, null, 2);
    lastBuyerHandoffPack = result.pack;
    lastBuyerPackReview = null;
    lastBuyerSessionChecklist = null;
    addAuditEntry('Buyer Handoff Pack', payload, result, doc);
    setStatus('Buyer handoff pack prepared in preview. No destination action was triggered.', 'ok', doc);
    return result;
  }

  function prepareBuyerSessionChecklist(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastBuyerPackReview || lastBuyerHandoffPack || lastPackage || build({ document: doc });
    if (!api || !api.guidedBuyerSessionChecklist) {
      setStatus('Buyer session checklist contract missing.', 'error', doc);
      return null;
    }
    var result = api.guidedBuyerSessionChecklist(payload);
    if (!result.ok) {
      setStatus('Buyer session checklist blocked: ' + result.errors.join(', ') + '.', 'warn', doc);
      return result;
    }
    var preview = byId(IDS.preview, doc);
    if (preview) preview.textContent = JSON.stringify(result.checklist, null, 2);
    lastBuyerSessionChecklist = result.checklist;
    addAuditEntry('Buyer Session Checklist', lastPackage, result, doc);
    setStatus('Buyer session checklist prepared in preview. No destination action was triggered.', 'ok', doc);
    return result;
  }

  function exportBuyerSessionSummary(options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    var payload = lastBuyerSessionChecklist || lastBuyerPackReview || lastBuyerHandoffPack || lastPackage || build({ document: doc });
    if (!api || !api.buyerSessionHandoffSummary) {
      setStatus('Buyer session summary contract missing.', 'error', doc);
      return null;
    }
    var result = api.buyerSessionHandoffSummary(payload);
    if (!result.ok) {
      setStatus('Buyer session summary blocked: ' + result.errors.join(', ') + '.', 'warn', doc);
      return result;
    }
    var preview = byId(IDS.preview, doc);
    if (preview) preview.textContent = JSON.stringify(result.summary, null, 2);
    var downloaded = downloadJson(result.summary, safeBuyerSessionSummaryFilename(), doc);
    addAuditEntry('Buyer Session Summary', lastPackage, result, doc);
    setStatus(
      downloaded
        ? 'Buyer session summary exported locally. No destination action was triggered.'
        : 'Buyer session summary prepared in preview. No destination action was triggered.',
      'ok',
      doc
    );
    return result;
  }

  function importText(raw, options) {
    var doc = options && options.document ? options.document : global.document;
    var api = core();
    if (!api || !api.importPayload) {
      setStatus('Strategy Builder import contract missing.', 'error', doc);
      return null;
    }
    var result = api.importPayload(raw);
    if (!result.ok) {
      setStatus('Import blocked: ' + result.errors.join(', ') + '.', 'error', doc);
      return result;
    }
    applyModel(result.model, doc);
    lastPackage = result.package;
    lastBuyerHandoffPack = null;
    lastBuyerPackReview = null;
    lastBuyerSessionChecklist = null;
    renderPackage(lastPackage, doc);
    if (result.buyer_pack_review) {
      var preview = byId(IDS.preview, doc);
      if (preview) preview.textContent = JSON.stringify(result.buyer_pack_review, null, 2);
      lastBuyerPackReview = result.buyer_pack_review;
      lastBuyerSessionChecklist = null;
      addAuditEntry('Buyer Pack Import Review', lastPackage, { ok: true, guardrails: result.buyer_pack_review.guardrails || [] }, doc);
      setStatus('Buyer pack imported for local review. Confirm manual review before export or handoffs.', 'warn', doc);
      return result;
    }
    addAuditEntry('Import JSON', lastPackage, { ok: true, guardrails: ['local_json_import', 'fresh_review_required'] }, doc);
    setStatus('Package imported locally. Confirm manual review before export.', 'warn', doc);
    return result;
  }

  function importFile(options) {
    var doc = options && options.document ? options.document : global.document;
    var input = byId(IDS.importFile, doc);
    if (!input || !input.files || !input.files[0]) {
      setStatus('Select a Strategy Builder JSON package first.', 'warn', doc);
      return null;
    }
    if (!global.FileReader) {
      setStatus('Local file reader is not available in this browser.', 'error', doc);
      return null;
    }
    var reader = new global.FileReader();
    reader.onload = function(evt) {
      importText(evt && evt.target ? evt.target.result : '', { document: doc });
    };
    reader.onerror = function() {
      setStatus('Import failed while reading the local JSON file.', 'error', doc);
    };
    reader.readAsText(input.files[0]);
    return true;
  }

  function bind(doc, id, handler) {
    var node = byId(id, doc);
    if (!node) return;
    if (SQX.ui && SQX.ui.bindClick) SQX.ui.bindClick(node, handler);
    else node.addEventListener('click', handler);
  }

  function bindChange(doc, id, handler) {
    var node = byId(id, doc);
    if (!node) return;
    node.addEventListener('change', handler);
    node.addEventListener('input', handler);
  }

  function init(options) {
    var doc = options && options.document ? options.document : global.document;
    if (!byId(IDS.build, doc)) return false;
    fillOptions(doc);
    bind(doc, IDS.build, function() { build({ document: doc }); });
    bind(doc, IDS.sampleCvc, function() { loadCvcSample({ document: doc }); });
    bind(doc, IDS.clear, function() { clear({ document: doc }); });
    bind(doc, IDS.exportPackage, function() { exportPackage({ document: doc }); });
    bind(doc, IDS.sendProjectGenerator, function() { sendToProjectGenerator({ document: doc }); });
    bind(doc, IDS.preparePreset, function() { prepareProjectGeneratorPreset({ document: doc }); });
    bind(doc, IDS.sendViews, function() { sendToViews({ document: doc }); });
    bind(doc, IDS.prepareCleaner, function() { prepareStrategyCleaner({ document: doc }); });
    bind(doc, IDS.prepareBuyerPack, function() { prepareBuyerHandoffPack({ document: doc }); });
    bind(doc, IDS.buyerSession, function() { prepareBuyerSessionChecklist({ document: doc }); });
    bind(doc, IDS.buyerSummary, function() { exportBuyerSessionSummary({ document: doc }); });
    bind(doc, IDS.importPackage, function() {
      var input = byId(IDS.importFile, doc);
      if (input && input.click) input.click();
    });
    bindChange(doc, IDS.importFile, function() { importFile({ document: doc }); });
    [IDS.sourceMode, IDS.asset, IDS.timeframe, IDS.archetype, IDS.validationPack, IDS.projectProfile, IDS.reviewed].forEach(function(id) {
      bindChange(doc, id, function() { build({ document: doc }); });
    });
    clear({ document: doc });
    renderAuditTrail(doc);
    return true;
  }

  SQX.strategyBuilder = SQX.strategyBuilder || {
    build: build,
    clear: clear,
    exportBuyerSessionSummary: exportBuyerSessionSummary,
    exportPackage: exportPackage,
    ids: IDS,
    importFile: importFile,
    importText: importText,
    init: init,
    loadCvcSample: loadCvcSample,
    prepareBuyerHandoffPack: prepareBuyerHandoffPack,
    prepareBuyerSessionChecklist: prepareBuyerSessionChecklist,
    prepareProjectGeneratorPreset: prepareProjectGeneratorPreset,
    prepareStrategyCleaner: prepareStrategyCleaner,
    renderAuditTrail: renderAuditTrail,
    sendToViews: sendToViews,
    sendToProjectGenerator: sendToProjectGenerator
  };

  if (SQX.registerModule) {
    SQX.registerModule('strategy-builder', SQX.strategyBuilder);
  }
})(window);
