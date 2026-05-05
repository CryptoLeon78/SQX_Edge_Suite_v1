(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};
  var escapeHtml = PG.escapeHtml || function(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }[ch];
    });
  };

  function byId(doc, id) {
    return (doc || global.document).getElementById(id);
  }

  function inputValue(doc, id) {
    var input = byId(doc, id);
    return input && input.value || '';
  }

  function trimmedInputValue(doc, id) {
    return inputValue(doc, id).trim();
  }

  function setInputValue(doc, id, value) {
    var input = byId(doc, id);
    if (input) input.value = value || '';
  }

  function setText(doc, id, text) {
    var el = byId(doc, id);
    if (el) el.textContent = text;
  }

  function setHtml(doc, id, html) {
    var el = byId(doc, id);
    if (el) el.innerHTML = html;
    return el;
  }

  function readConfigInputs(doc, aliases) {
    return {
      sqxPath: trimmedInputValue(doc, 'pg-sqx-path'),
      sqxDataDb: trimmedInputValue(doc, 'pg-sqx-db'),
      sqxProjectsDir: trimmedInputValue(doc, 'pg-sqx-projects'),
      outputDir: trimmedInputValue(doc, 'pg-output-dir'),
      templateCapa1: trimmedInputValue(doc, 'pg-tpl-c1'),
      templateCapa2: trimmedInputValue(doc, 'pg-tpl-c2'),
      assetAliases: aliases || {}
    };
  }

  function writeConfigInputs(doc, config) {
    var c = config || {};
    setInputValue(doc, 'pg-sqx-path', c.sqx_path);
    setInputValue(doc, 'pg-sqx-db', c.sqx_data_db);
    setInputValue(doc, 'pg-sqx-projects', c.sqx_projects_dir);
    setInputValue(doc, 'pg-output-dir', c.output_dir);
    setInputValue(doc, 'pg-tpl-c1', c.template_capa1);
    setInputValue(doc, 'pg-tpl-c2', c.template_capa2);
  }

  function applySqxFields(doc, fields) {
    var data = fields || {};
    setInputValue(doc, 'pg-sqx-path', data.sqxPath);
    setInputValue(doc, 'pg-sqx-db', data.dataDb);
    setInputValue(doc, 'pg-sqx-projects', data.projectsDir);
  }

  function setSettingsOpen(doc, open) {
    var body = byId(doc, 'pg-settings-body');
    var arrow = byId(doc, 'pg-settings-arrow');
    if (!body || !arrow) return false;
    var shouldOpen = !!open;
    body.style.display = shouldOpen ? 'block' : 'none';
    arrow.classList.toggle('closed', !shouldOpen);
    return true;
  }

  function focusSettingsField(doc, id) {
    setSettingsOpen(doc, true);
    var target = byId(doc, id);
    if (!target) return false;
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    global.setTimeout(function() { target.focus(); }, 90);
    return true;
  }

  function setSettingsMessage(doc, status) {
    var msg = byId(doc, 'pg-settings-msg');
    var data = status || {};
    if (!msg) return false;
    msg.textContent = data.message || '';
    if (Object.prototype.hasOwnProperty.call(data, 'color')) msg.style.color = data.color;
    return true;
  }

  function appendLog(doc, message, level, dateFactory) {
    var log = byId(doc, 'pg-log');
    if (!log) return false;
    var date = dateFactory ? dateFactory() : new Date();
    var cls = level === 'ok' ? 'log-ok' : level === 'err' ? 'log-err' : 'log-info';
    if (log.textContent.trim() === '[esperando primera acción…]') log.textContent = '';
    log.append((doc || global.document).createTextNode('[' + date.toLocaleTimeString() + '] '));
    var span = (doc || global.document).createElement('span');
    span.className = cls;
    span.textContent = message;
    log.append(span, (doc || global.document).createTextNode('\n'));
    log.scrollTop = log.scrollHeight;
    return true;
  }

  function trace(targetGlobal, title, detail, level) {
    var host = targetGlobal || global;
    if (typeof host.addHomeTrace === 'function') {
      host.addHomeTrace(title, detail, level || 'info');
      return true;
    }
    return false;
  }

  Object.assign(PG, {
    dom: {
      appendLog: appendLog,
      applySqxFields: applySqxFields,
      byId: byId,
      escapeHtml: escapeHtml,
      focusSettingsField: focusSettingsField,
      inputValue: inputValue,
      readConfigInputs: readConfigInputs,
      setHtml: setHtml,
      setInputValue: setInputValue,
      setSettingsMessage: setSettingsMessage,
      setSettingsOpen: setSettingsOpen,
      setText: setText,
      trace: trace,
      trimmedInputValue: trimmedInputValue,
      writeConfigInputs: writeConfigInputs
    }
  });
})(window);
