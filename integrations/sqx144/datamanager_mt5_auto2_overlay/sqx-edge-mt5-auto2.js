(function(global) {
  "use strict";

  var VERSION = "sqx144-mt5-auto2-data-manager-button-bridge-v1";
  var CATALOG_TRIAGE_VERSION = "sqx144-mt5-auto4-datamanager-catalog-triage-v1";
  var AUTO6_STABILITY_VERSION = "sqx144-mt5-auto6-metadata-stability-policy-v1";
  var AUTO7_DUKASCOPY_MIRROR_VERSION = "sqx144-mt5-auto7-dukascopy-metadata-mirror-v1";
  var AUTO7_DATA_SYMBOL_GUARD_VERSION = "sqx144-mt5-auto7-datamanager-data-symbol-selection-guard-v1";
  var AUTO8_NATIVE_SAVE_VERSION = "sqx144-mt5-auto8-datamanager-native-save-apply-v1";
  var AUTO8_UX_STATUS_VERSION = "sqx144-mt5-auto8-datamanager-native-save-ux-status-v1";
  var AUTO9_HEALTH_WATCHDOG_VERSION = "sqx144-mt5-auto9-datamanager-health-watchdog-v1";
  var AUTO9_HEALTH_POLL_STOP_VERSION = "sqx144-mt5-auto9-datamanager-health-watchdog-poll-stop-v1";
  var AUTO9_SINGLE_CLICK_UX_VERSION = "sqx144-mt5-auto9-datamanager-single-click-ux-v1";
  var AUTO9_SINGLE_CLICK_FALLBACK_VERSION = AUTO9_SINGLE_CLICK_UX_VERSION;
  var AUTO9_CHECKED_ROW_SELECTION_VERSION = "sqx144-mt5-auto9c-datamanager-checked-row-selection-v1";
  var AUTO9_VISUAL_ES_SELECTION_VERSION = "sqx144-mt5-auto9c-visual-es-selection-v1";
  var AUTO9_DATA_SYMBOL_PRIORITY_VERSION = "sqx144-mt5-auto9d-datamanager-data-symbol-priority-v1";
  var SELECTION_GUARD_VERSION = "sqx144-mt5-auto6-datamanager-selection-guard-v1";
  var BROKER_SUFFIXES = ["darwinex", "dukascopy", "oanda", "ftmo", "icmarkets", "roboforex", "pepperstone", "monevis", "monexis", "the5ers", "thesers", "axi"];
  var BROKER_SUFFIX_PATTERN = "(?:" + BROKER_SUFFIXES.join("|") + ")";
  var DEFAULT_POLICY = "p90";
  var DEFAULT_BROKER = "darwinex";
  var LEGACY_VALIDATE_ENDPOINT = "/sqx144/mt5-auto2/validate";
  var CROSSED_SYMBOL_BLOCKER = "latest_response_symbol_mismatch";
  var SELECTED_SYMBOL_NOT_FOUND_STATUS = "selected_symbol_not_found";
  var CHECKED_ROW_REQUIRED_STATUS = "checked_row_required_for_mt5_bridge";
  var MULTIPLE_CHECKED_ROWS_STATUS = "multiple_checked_rows_blocked_for_mt5_bridge";
  var AUTO8_NATIVE_SAVE_CONTRACT = {
    nativeDataManagerSaveAllowed: true,
    sqxOpenNativeSaveAllowed: true,
    directDbWriteAllowed: false,
    directDbHistoryInsertAllowed: false,
    historyImportAllowed: false,
    usesDataSourceHistoryImport: false
  };
  var AUTO9_HEALTH_WATCHDOG_CONTRACT = {
    healthWatchdogObserveOnly: true,
    autoStartAllowed: false,
    directDbWriteAllowed: false,
    historyImportAllowed: false,
    launchesMt5: false,
    runsMt5Ea: false,
    usesMigrationTool: false
  };
  var AUTO9_HEALTH_STATUS_LABELS = {
    noResponseOrInactive: "mt5_bridge_no_responde_o_no_esta_activo",
    eaNotResponding: "mt5_bridge_ea_no_responde",
    staleLatest: "mt5_bridge_latest_desfasado",
    latestMatchesRequest: "mt5_bridge_ready_latest_matches_request"
  };
  var LIVE_APPLY_FIELD_MAP = {
    DEFAULTSPREAD: "defaultSpread",
    POINTVALUE: "pointValue",
    TICKSIZE: "tickSize",
    TICKSTEP: "tickStep",
    DEFAULTSLIPPAGE: "defaultSlippage",
    ORDERSIZEMULTIPLIER: "orderSizeMultiplier",
    ORDERSIZESTEP: "orderSizeStep",
    COMMISSIONS: "commissions",
    SWAP: "swap"
  };

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

  var API_BASE = safeApiBase(global.SQX_EDGE_MT5_AUTO2_API_BASE);
  var API_ORIGIN = (function() {
    try { return new URL(API_BASE).origin; } catch (err) { return "http://127.0.0.1:5050"; }
  })();
  var state = {
    open: false,
    busy: false,
    lastSymbol: "",
    lastRequestId: "",
    catalogResult: null,
    resolvePlan: null,
    stabilityResult: null,
    mirrorResult: null,
    applyResult: null,
    lastResult: null,
    linkedInstrument: "",
    requestSeq: 0,
    selectionSeq: 0,
    checkedSelection: null,
    selectionWarning: "",
    error: ""
  };
  var angularRegistered = false;

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
          if (!response.ok) {
            json.ok = false;
            if (!json.error && !json.status) {
              json.error = response.status === 404
                ? endpointMissingError(path)
                : "api_http_" + response.status;
            }
            if (!Array.isArray(json.blockers)) json.blockers = [json.error || json.status || "api_http_error"];
          }
          return json;
        });
      })
      .catch(function(err) {
        return { ok: false, error: err && err.message ? err.message : "request_failed" };
      });
  }

  function endpointMissingError(path) {
    var raw = String(path || "");
    if (raw.indexOf("mt5-auto6") >= 0) return "auto6_backend_endpoint_missing_restart_required";
    if (raw.indexOf("mt5-auto3") >= 0) return "auto3_backend_endpoint_missing_restart_required";
    return "auto2_backend_endpoint_missing_restart_required";
  }

  function candidateFromText(text) {
    var raw = String(text || "").replace(/\s+/g, " ");
    var matches = suffixedSymbolCandidatesFromText(raw);
    if (matches.length) return normalizeSymbol(matches[0]);
    var bare = raw.toUpperCase().match(/\b[A-Z0-9]{3,18}\b/g) || [];
    for (var i = 0; i < bare.length; i += 1) {
      if (isAllowedBareSymbol(bare[i])) return normalizeSymbol(bare[i]);
    }
    return "";
  }

  function suffixedSymbolCandidatesFromText(text) {
    var raw = String(text || "").replace(/\s+/g, " ");
    var re = new RegExp("\\b[A-Z0-9]{3,18}_" + BROKER_SUFFIX_PATTERN + "\\b", "gi");
    var matches = raw.match(re) || [];
    var result = [];
    for (var i = 0; i < matches.length; i += 1) {
      var normalized = normalizeSymbol(matches[i]);
      if (normalized && normalized.indexOf("_") !== -1 && result.indexOf(normalized) === -1) {
        result.push(normalized);
      }
    }
    return result;
  }

  function preferredDataSymbolCandidate(candidates) {
    for (var i = 0; i < candidates.length; i += 1) {
      if (candidates[i] && !/_darwinex$/i.test(candidates[i])) return candidates[i];
    }
    return candidates.length ? candidates[0] : "";
  }

  function candidateFromDataRowText(text, requireSuffixed) {
    var raw = String(text || "").replace(/\s+/g, " ");
    var suffixed = suffixedSymbolCandidatesFromText(raw);
    var preferred = preferredDataSymbolCandidate(suffixed);
    if (preferred) return preferred;
    return requireSuffixed ? "" : candidateFromText(raw);
  }

  function isAllowedBareSymbol(value) {
    var token = String(value || "").toUpperCase();
    if (!token || token === "WARRANTY" || token === "CURRENCY" || token === "FUTURES" || token === "FOREX" || token === "INDEX") return false;
    var currencies = ["AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "USD"];
    if (token.length === 6 && currencies.indexOf(token.slice(0, 3)) >= 0 && currencies.indexOf(token.slice(3)) >= 0) return true;
    var known = [
      "DAX40", "GDAXI", "NASDAQ", "NDX", "SP500", "US500", "USA30IDXUSD", "US30",
      "XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD"
    ];
    return known.indexOf(token) >= 0;
  }

  function normalizeSymbol(symbol) {
    var raw = String(symbol || "").trim().replace(/\s+/g, "");
    if (!raw) return "";
    if (raw.indexOf("_") === -1) return raw.toUpperCase();
    var parts = raw.split("_");
    if (parts.length < 2) return raw.toUpperCase();
    var suffix = parts.slice(1).join("_");
    if (suffix.toLowerCase() === "darwinex") return parts[0].toUpperCase() + "_Darwinex";
    return parts[0].toUpperCase() + "_" + suffix;
  }

  function isDukascopyMirrorSymbol(symbol) {
    var raw = String(symbol || "");
    return /_dukascopy$/i.test(raw);
  }

  function selectedSymbol(options) {
    var allowLast = !(options && options.allowLast === false);
    var modalHit = selectedSymbolFromEditDialog();
    if (modalHit) return modalHit;
    var checkedHit = selectedSymbolFromCheckedRows();
    if (checkedHit) return checkedHit;
    var selectors = [
      "tr.rowselected",
      "tr.dhx_selected",
      "tr.selected",
      "tr[class*='selected']",
      "div[class*='rowselected']",
      "div[class*='dhx_selected']",
      "div[class*='selected']"
    ];
    for (var i = 0; i < selectors.length; i += 1) {
      var nodes = global.document.querySelectorAll(selectors[i]);
      for (var n = 0; n < nodes.length; n += 1) {
        var hit = candidateFromText(nodes[n].textContent || "");
        if (hit) return hit;
      }
    }
    var inputs = global.document.querySelectorAll("input, select");
    for (var j = 0; j < inputs.length; j += 1) {
      var value = inputs[j].value || "";
      var inputHit = candidateFromText(value);
      if (inputHit) return inputHit;
    }
    return allowLast ? (state.lastSymbol || "") : "";
  }

  function selectedSymbolFromCheckedRows() {
    var selection = checkedRowSelectionState();
    return selection.ok ? selection.symbol : "";
  }

  function checkedRowSelectionState() {
    var checks = global.document.querySelectorAll("input[type='checkbox']:checked");
    var matches = [];
    for (var i = 0; i < checks.length; i += 1) {
      var input = checks[i];
      if (isInsideMt5Panel(input) || isMt5BridgeActionNode(input) || isInsideEditDialog(input)) continue;
      var container = rowContainerForCheckedInput(input);
      var rowText = checkedRowText(input, container);
      var hit = candidateFromDataRowText(rowText, false);
      matches.push({
        symbol: hit,
        linkedInstrument: linkedInstrumentFromCheckedRow(container, hit, rowText),
        text: rowText
      });
    }
    if (matches.length === 0) {
      return {
        ok: false,
        count: 0,
        status: CHECKED_ROW_REQUIRED_STATUS,
        blockers: [CHECKED_ROW_REQUIRED_STATUS]
      };
    }
    if (matches.length > 1) {
      return {
        ok: false,
        count: matches.length,
        status: MULTIPLE_CHECKED_ROWS_STATUS,
        blockers: [MULTIPLE_CHECKED_ROWS_STATUS],
        symbols: matches.map(function(item) { return item.symbol || ""; }).filter(Boolean)
      };
    }
    if (!matches[0].symbol) {
      return {
        ok: false,
        count: 1,
        status: "checked_row_symbol_not_found",
        blockers: ["checked_row_symbol_not_found"]
      };
    }
    return {
      ok: true,
      count: 1,
      status: "checked_row_selection_ready",
      symbol: matches[0].symbol,
      linkedInstrument: matches[0].linkedInstrument || ""
    };
  }

  function rowContainerForCheckedInput(input) {
    if (!input) return null;
    if (typeof input.closest === "function") {
      var closest = input.closest("tr, [role='row'], .x-grid-row, .dhx_row, .dhx_grid-row, .datagrid-row");
      if (closest) return closest;
    }
    var node = input;
    while (node && node !== global.document.body) {
      var tagName = String(node.tagName || "").toUpperCase();
      var className = String(node.className || "");
      var role = String(node.getAttribute ? (node.getAttribute("role") || "") : "");
      if (
        tagName === "TR" ||
        role === "row" ||
        className.indexOf("x-grid-row") >= 0 ||
        className.indexOf("dhx_row") >= 0 ||
        className.indexOf("dhx_grid-row") >= 0 ||
        className.indexOf("datagrid-row") >= 0
      ) {
        return node;
      }
      node = node.parentElement;
    }
    return input.parentElement || input;
  }

  function checkedRowText(input, container) {
    return uniqueMessages([
      (container && container.textContent) || "",
      (input && input.value) || "",
      checkedRowTextFromAncestors(input),
      checkedRowTextFromGeometry(input)
    ]).join(" ");
  }

  function checkedRowTextFromAncestors(input) {
    var node = input ? input.parentElement : null;
    var depth = 0;
    while (node && node !== global.document.body && depth < 8) {
      if (!isInsideMt5Panel(node) && !isMt5BridgeActionNode(node) && !isInsideEditDialog(node)) {
        var text = String(node.textContent || "");
        if (text.length <= 800 && candidateFromDataRowText(text, false)) return text;
      }
      node = node.parentElement;
      depth += 1;
    }
    return "";
  }

  function checkedRowTextFromGeometry(input) {
    if (!input || typeof input.getBoundingClientRect !== "function") return "";
    var inputRect = input.getBoundingClientRect();
    if (!inputRect) return "";
    var inputCenter = inputRect.top + (inputRect.height || 0) / 2;
    var selectors = [
      "tr",
      "[role='row']",
      ".x-grid-row",
      ".dhx_row",
      ".dhx_grid-row",
      ".datagrid-row",
      "td",
      "[role='gridcell']",
      ".x-grid-cell",
      ".dhx_cell",
      "[class*='cell']"
    ];
    var candidates = [];
    for (var s = 0; s < selectors.length; s += 1) {
      var nodes = global.document.querySelectorAll(selectors[s]);
      for (var i = 0; i < nodes.length; i += 1) {
        var node = nodes[i];
        if (!node || node === input || isInsideMt5Panel(node) || isMt5BridgeActionNode(node) || isInsideEditDialog(node) || !isVisibleElement(node)) continue;
        if (typeof node.getBoundingClientRect !== "function") continue;
        var rect = node.getBoundingClientRect();
        if (!rect || rect.height <= 0) continue;
        var text = String(node.textContent || "");
        if (!candidateFromDataRowText(text, false)) continue;
        var nodeCenter = rect.top + rect.height / 2;
        var distance = Math.abs(nodeCenter - inputCenter);
        var tolerance = Math.max(8, Math.min(22, Math.max(rect.height, inputRect.height || 0) / 2 + 6));
        if (distance > tolerance) continue;
        var score = distance + Math.min(text.length, 1000) / 1000;
        candidates.push({ score: score, text: text });
      }
    }
    if (!candidates.length) return "";
    candidates.sort(function(a, b) { return a.score - b.score; });
    var combined = uniqueMessages(candidates.map(function(item) { return item.text; })).join(" ");
    return candidateFromDataRowText(combined, true) ? combined : candidates[0].text;
  }

  function linkedInstrumentFromCheckedRow(container, selectedSymbolName, fallbackText) {
    var text = ((container && container.textContent) || "") + " " + (fallbackText || "");
    var candidates = [];
    var match = String(text).match(/[A-Z0-9]{3,12}_(?:darwinex|dukascopy|oanda|ftmo|icmarkets|monevis|pepperstone|roboforex|thesers|axi)\b/ig);
    if (match) {
      for (var m = 0; m < match.length; m += 1) {
        var normalized = candidateFromText(match[m]);
        if (normalized && candidates.indexOf(normalized) === -1) candidates.push(normalized);
      }
    }
    for (var i = 0; i < candidates.length; i += 1) {
      if (candidates[i] && candidates[i] !== selectedSymbolName && !isDukascopyMirrorSymbol(candidates[i])) return candidates[i];
    }
    for (var j = 0; j < candidates.length; j += 1) {
      if (candidates[j] && !isDukascopyMirrorSymbol(candidates[j])) return candidates[j];
    }
    return "";
  }

  function isInsideEditDialog(node) {
    while (node && node !== global.document.body) {
      var id = String(node.id || "").toLowerCase();
      var className = String(node.className || "").toLowerCase();
      var role = String(node.getAttribute ? (node.getAttribute("role") || "") : "").toLowerCase();
      var dialogClass = /(^|\s)(modal|dialog|x-window|dhx_window|dhx-window|ui-dialog)(\s|$)/.test(className);
      if (
        role === "dialog" ||
        id.indexOf("dialog") !== -1 ||
        dialogClass
      ) {
        return true;
      }
      node = node.parentElement;
    }
    return false;
  }

  function selectedSymbolFromEditDialog() {
    var dukascopyDataSymbol = selectedDukascopyDataSymbolFromEditDialog();
    if (dukascopyDataSymbol) return dukascopyDataSymbol;
    var scopes = editDialogScopes();
    for (var s = 0; s < scopes.length; s += 1) {
      var selectHit = firstControlCandidate(scopes[s], "select");
      if (selectHit) return selectHit;
      var inputHit = firstControlCandidate(scopes[s], "input");
      if (inputHit) return inputHit;
    }
    return "";
  }

  function selectedDukascopyDataSymbolFromEditDialog() {
    var scopes = editDialogScopes();
    for (var s = 0; s < scopes.length; s += 1) {
      var inputHit = firstControlCandidateWhere(scopes[s], "input", isDukascopyMirrorSymbol);
      if (inputHit) return inputHit;
    }
    return "";
  }

  function linkedInstrumentFromEditDialog() {
    var scopes = editDialogScopes();
    for (var s = 0; s < scopes.length; s += 1) {
      var selectHit = firstControlCandidate(scopes[s], "select");
      if (selectHit) return selectHit;
    }
    return "";
  }

  function editDialogScopes() {
    var scopes = [];
    var nodes = global.document.querySelectorAll("[role='dialog'], .modal, .modal-dialog, .ui-dialog, .dhxwin_active, .dhx_window_active, .x-window, div");
    for (var i = 0; i < nodes.length; i += 1) {
      var node = nodes[i];
      if (!isVisibleElement(node) || isInsideMt5Panel(node)) continue;
      var text = String(node.textContent || "");
      if (text.indexOf("Edit symbol") < 0 && text.indexOf("Data symbol name") < 0 && text.indexOf("Choose instrument") < 0) continue;
      scopes.push(node);
    }
    scopes.sort(function(a, b) {
      return String(a.textContent || "").length - String(b.textContent || "").length;
    });
    return scopes;
  }

  function firstControlCandidate(scope, selector) {
    return firstControlCandidateWhere(scope, selector, function() { return true; });
  }

  function firstControlCandidateWhere(scope, selector, predicate) {
    var controls = scope.querySelectorAll(selector);
    for (var i = 0; i < controls.length; i += 1) {
      var control = controls[i];
      var values = [];
      if (selector === "select") {
        var selected = control.selectedOptions || [];
        for (var j = 0; j < selected.length; j += 1) {
          values.push(selected[j].textContent || "");
          values.push(selected[j].value || "");
        }
      }
      values.push(control.value || "");
      for (var v = 0; v < values.length; v += 1) {
        var hit = candidateFromText(values[v]);
        if (hit && predicate(hit)) return hit;
      }
    }
    return "";
  }

  function isInsideMt5Panel(node) {
    var panel = byId("sqx-edge-mt5-auto2-panel");
    return !!(panel && (node === panel || panel.contains(node)));
  }

  function isVisibleElement(node) {
    if (!node) return false;
    if (node.offsetWidth || node.offsetHeight || node.getClientRects().length) return true;
    if (!global.getComputedStyle) return false;
    var style = global.getComputedStyle(node);
    return !!style && style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0";
  }

  function rememberClickedSymbol(event) {
    if (state.busy) return;
    var node = event.target;
    if (isInsideMt5Panel(node) || isMt5BridgeActionNode(node)) return;
    while (node && node !== global.document.body) {
      var hit = candidateFromText(node.textContent || "");
      if (hit) {
        if (hit !== state.lastSymbol) clearTransientResults();
        state.lastSymbol = hit;
        render();
        return;
      }
      node = node.parentElement;
    }
  }

  function ensurePanel() {
    if (byId("sqx-edge-mt5-auto2-panel")) return;
    var panel = global.document.createElement("div");
    panel.id = "sqx-edge-mt5-auto2-panel";
    panel.className = "sqx-edge-mt5-auto2-panel";
    panel.innerHTML = [
      '<div class="sqx-edge-mt5-auto2-head">',
      '<span>MT5 Bridge</span>',
      '<button type="button" id="sqx-edge-mt5-auto2-close" title="Close">x</button>',
      '</div>',
      '<div class="sqx-edge-mt5-auto2-body" id="sqx-edge-mt5-auto2-body"></div>'
    ].join("");
    global.document.body.appendChild(panel);
    byId("sqx-edge-mt5-auto2-close").addEventListener("click", function() {
      state.open = false;
      render();
    });
  }

  function ensureLauncher() {
    var button = byId("sqx-edge-mt5-auto2-launcher");
    if (hasVisibleAngularAction()) {
      if (button && button.parentNode) button.parentNode.removeChild(button);
      return;
    }
    if (!button) {
      button = global.document.createElement("button");
      button.type = "button";
      button.id = "sqx-edge-mt5-auto2-launcher";
      button.textContent = "MT5";
      button.title = "MT5 Bridge";
      button.addEventListener("click", function() {
        requestFromSelection([]);
      });
    }

    var host = findActiveRibbonHost() || findDataSourceRibbonHost() || findInstrumentRibbonHost();
    if (host) {
      button.className = "menu-button sqx-edge-mt5-auto2-launcher";
      host.appendChild(button);
    } else {
      button.className = "sqx-edge-mt5-auto2-floating";
      global.document.body.appendChild(button);
    }
  }

  function label(text) {
    return typeof global.Ltsq === "function" ? global.Ltsq(text) : text;
  }

  function registerAngularAction() {
    if (!global.angular || angularRegistered) return false;
    try {
      var dataModule = global.angular.module("app.data");
      var instrumentsModule = global.angular.module("app.instruments");
      dataModule.config(["sqPluginProvider", function(sqPluginProvider) {
        sqPluginProvider.plugin("DataManagerActionTools", 45, {
          key: "mt5Bridge",
          title: label("MT5 bridge"),
          source: "data,instruments",
          class: "sqx-edge-mt5-bridge-action",
          id: "sqx-edge-mt5-bridge-data-action",
          group: "data-source",
          group1: "instruments-sessions",
          controller: "SQXEdgeMt5BridgeActionCtrl",
          onSelect: function(rows) {
            requestFromSelection(rows);
          }
        });
      }]);
      instrumentsModule.config(["sqPluginProvider", function(sqPluginProvider) {
        sqPluginProvider.plugin("DataManagerActionInstrument", 85, {
          title: label("MT5 bridge"),
          source: "instruments",
          class: "sqx-edge-mt5-bridge-action",
          id: "sqx-edge-mt5-bridge-action",
          controller: "SQXEdgeMt5BridgeActionCtrl",
          onSelect: function(instruments) {
            requestFromSelection(instruments);
          }
        });
      }]);
      dataModule.controller("SQXEdgeMt5BridgeActionCtrl", ["$scope", function($scope) {
        if ($scope && $scope.action) {
          $scope.action.onSelect = function(instruments) {
            requestFromSelection(instruments);
          };
        }
      }]);
      angularRegistered = true;
      return true;
    } catch (err) {
      return false;
    }
  }

  function requestFromSelection(instruments) {
    var settleSeq = 0;
    clearTransientResults();
    state.selectionSeq += 1;
    settleSeq = state.selectionSeq;
    state.open = true;
    state.selectionWarning = "resolviendo_seleccion_data_manager";
    render();
    requestFromSelectionSettled(instruments || [], settleSeq, 0);
  }

  function requestFromSelectionSettled(instruments, settleSeq, attempt) {
    var delays = [0, 75, 200];
    global.setTimeout(function() {
      if (settleSeq !== state.selectionSeq) return;
      var resolved = resolveSelectionPayload(instruments);
      if (resolved.symbol) {
        clearTransientResults();
        state.lastSymbol = resolved.symbol;
        state.linkedInstrument = resolved.linkedInstrument;
        state.checkedSelection = resolved;
        state.open = true;
        render();
        requestBridge(resolved.symbol, { linkedInstrument: resolved.linkedInstrument });
        return;
      }
      if (attempt + 1 < delays.length) {
        requestFromSelectionSettled(instruments, settleSeq, attempt + 1);
        return;
      }
      clearTransientResults();
      state.open = true;
      state.lastSymbol = "";
      state.linkedInstrument = "";
      state.checkedSelection = resolved;
      state.lastResult = { ok: false, status: resolved.status || CHECKED_ROW_REQUIRED_STATUS, blockers: resolved.blockers || [] };
      state.error = resolved.status || CHECKED_ROW_REQUIRED_STATUS;
      state.selectionWarning = resolved.status || CHECKED_ROW_REQUIRED_STATUS;
      render();
    }, delays[attempt] || 0);
  }

  function resolveSelectionPayload(instruments) {
    return checkedRowSelectionState();
  }

  function symbolFromSelectionItem(item) {
    var fields = [
      "dataSymbol", "DataSymbol", "DATA_SYMBOL", "dataSymbolName", "Data symbol name",
      "symbolName", "Symbol Name", "symbol", "SYMBOL", "uSymbol", "USYMBOL",
      "mt5Symbol", "name", "NAME", "instrument", "INSTRUMENT"
    ];
    var firstHit = "";
    for (var i = 0; i < fields.length; i += 1) {
      var hit = candidateFromText(item && item[fields[i]]);
      if (!hit) continue;
      if (isDukascopyMirrorSymbol(hit)) return hit;
      if (!firstHit) firstHit = hit;
    }
    return firstHit;
  }

  function linkedInstrumentFromSelectionItem(item) {
    var fields = ["linkedInstrument", "sqxInstrument", "instrument", "INSTRUMENT", "Instrument"];
    for (var i = 0; i < fields.length; i += 1) {
      var hit = candidateFromText(item && item[fields[i]]);
      if (hit) return hit;
    }
    return "";
  }

  function hasVisibleAngularAction() {
    var ids = ["sqx-edge-mt5-bridge-data-action", "sqx-edge-mt5-bridge-action"];
    for (var i = 0; i < ids.length; i += 1) {
      var node = byId(ids[i]);
      if (node && (node.offsetWidth || node.offsetHeight || node.getClientRects().length)) return true;
    }
    return false;
  }

  function isMt5BridgeActionNode(node) {
    var current = node;
    while (current && current !== global.document.body) {
      var id = String(current.id || "");
      var className = String(current.className || "");
      if (id === "sqx-edge-mt5-bridge-data-action" || id === "sqx-edge-mt5-bridge-action") return true;
      if (className.indexOf("sqx-edge-mt5-bridge-action") >= 0) return true;
      current = current.parentElement;
    }
    return false;
  }

  function handleAngularActionClickFallback(event) {
    if (!event || !isMt5BridgeActionNode(event.target)) return;
    var beforeSeq = state.requestSeq;
    global.setTimeout(function() {
      if (state.requestSeq !== beforeSeq || state.busy) return;
      requestFromSelection([]);
    }, 150);
  }

  function findActiveRibbonHost() {
    var candidates = global.document.querySelectorAll(".datamanager-menu > div");
    var active = null;
    for (var i = 0; i < candidates.length; i += 1) {
      var className = String(candidates[i].className || "");
      if (className.indexOf("active") < 0) continue;
      if (className.indexOf("right-separator") >= 0) continue;
      active = candidates[i];
    }
    return active;
  }

  function findDataSourceRibbonHost() {
    var candidates = global.document.querySelectorAll(".datamanager-menu > div");
    var dataSource = null;
    for (var i = 0; i < candidates.length; i += 1) {
      var ngClass = candidates[i].getAttribute("ng-class") || "";
      var className = String(candidates[i].className || "");
      if (ngClass.indexOf("data-sources") >= 0 && className.indexOf("right-separator") < 0) {
        dataSource = candidates[i];
      }
    }
    return dataSource;
  }

  function findInstrumentRibbonHost() {
    var candidates = global.document.querySelectorAll(".datamanager-menu > div");
    for (var i = 0; i < candidates.length; i += 1) {
      var ngClass = candidates[i].getAttribute("ng-class") || "";
      if (ngClass.indexOf("instruments-sessions") >= 0) return candidates[i];
    }
    return null;
  }

  function render() {
    ensurePanel();
    var panel = byId("sqx-edge-mt5-auto2-panel");
    var body = byId("sqx-edge-mt5-auto2-body");
    if (!panel || !body) return;
    panel.className = "sqx-edge-mt5-auto2-panel" + (state.open ? " open" : "");
    var result = state.lastResult || {};
    var catalog = state.catalogResult || {};
    var stability = state.stabilityResult || {};
    var mirror = state.mirrorResult || {};
    var health = result.bridgeHealth || {};
    var uiState = nativeSaveUiState(result, stability, mirror);
    var fields = result.proposedSqxFields || {};
    var lines = [];
    lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Instrument</b><span>' + escapeHtml(state.lastSymbol || (state.checkedSelection && state.checkedSelection.symbol) || "-") + '</span></div>');
    lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Policy</b><span>' + DEFAULT_POLICY + '</span></div>');
    if (catalog.decision) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Catalog</b><span>' + escapeHtml(catalog.decision) + '</span></div>');
    }
    if (catalog.brokerKey) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Broker</b><span>' + escapeHtml(catalog.brokerKey) + '</span></div>');
    }
    if (catalog.planId) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Plan</b><span>' + escapeHtml(catalog.planId) + '</span></div>');
    }
    if (catalog.nextAction) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Next</b><span>' + escapeHtml(catalog.nextAction) + '</span></div>');
    }
    if (state.lastRequestId) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Request</b><span>' + escapeHtml(state.lastRequestId) + '</span></div>');
    }
    if (health.panelStatus || health.status) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Health</b><span>' + escapeHtml(visualMessage(health.panelStatus || health.status)) + '</span></div>');
    }
    if (health.terminalProcessRunning != null) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>MT5</b><span>' + escapeHtml(health.terminalProcessRunning ? "proceso_detectado" : "proceso_no_detectado") + '</span></div>');
    }
    if (health.request && health.request.present) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Request age</b><span>' + escapeHtml(formatAge(health.request.ageSeconds)) + '</span></div>');
    }
    if (health.latestResponse && health.latestResponse.present) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Latest age</b><span>' + escapeHtml(formatAge(health.latestResponse.ageSeconds)) + '</span></div>');
    }
    if (stability.policyId) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Stability policy</b><span>' + escapeHtml(stability.policyId) + '</span></div>');
    }
    if (mirror.mirrorPolicy) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Mirror</b><span>' + escapeHtml(mirror.mirrorPolicy) + '</span></div>');
    }
    if (mirror.dataSymbol) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Data symbol</b><span>' + escapeHtml(mirror.dataSymbol) + '</span></div>');
    }
    if (mirror.linkedInstrument) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Linked</b><span>' + escapeHtml(mirror.linkedInstrument) + '</span></div>');
    }
    if (mirror.sourceInstrument) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Source</b><span>' + escapeHtml(mirror.sourceInstrument) + '</span></div>');
    }
    if (mirror.targetInstrument) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Target</b><span>' + escapeHtml(mirror.targetInstrument) + '</span></div>');
    }
    if (stability.decision) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Stability</b><span>' + escapeHtml(stability.decision) + '</span></div>');
    }
    if (stability.futureApplyGateAllowed != null) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Future gate</b><span>' + escapeHtml(stability.futureApplyGateAllowed ? "eligible_metadata_update" : "blocked_by_policy") + '</span></div>');
    }
    if (stability.coverage) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Coverage</b><span>' + escapeHtml("samples=" + (stability.coverage.samples == null ? "-" : stability.coverage.samples) + ", years=" + (stability.coverage.yearCount == null ? "-" : stability.coverage.yearCount)) + '</span></div>');
    }
    lines.push('<div class="sqx-edge-mt5-auto2-status ' + uiState.className + '">' + escapeHtml(visualMessage(uiState.status)) + '</div>');
    if (fields.DEFAULTSPREAD != null) {
      lines.push('<div class="sqx-edge-mt5-auto2-grid">');
      lines.push(fieldLine("DEFAULTSPREAD", fields.DEFAULTSPREAD));
      lines.push(fieldLine("POINTVALUE", fields.POINTVALUE));
      lines.push(fieldLine("TICKSIZE", fields.TICKSIZE));
      lines.push(fieldLine("TICKSTEP", fields.TICKSTEP));
      lines.push(fieldLine("samples", fields.spreadSamples));
      lines.push('</div>');
    }
    if (mirror.changes || mirror.noops) {
      lines.push('<div class="sqx-edge-mt5-auto2-grid">');
      var mirrorValues = mirror.changes || {};
      var mirrorNoops = mirror.noops || {};
      ["DEFAULTSPREAD", "POINTVALUE", "TICKSIZE", "TICKSTEP"].forEach(function(key) {
        if (mirrorValues[key]) {
          lines.push(fieldLine(key, mirrorValues[key].new));
        } else if (mirrorNoops[key] != null) {
          lines.push(fieldLine(key, mirrorNoops[key]));
        }
      });
      lines.push('</div>');
    }
    var blockers = uniqueMessages((catalog.blockers || []).concat(result.blockers || []).concat(mirror.blockers || []).concat(health.blockers || []));
    var warnings = visibleWarnings(catalog, result, stability, mirror, uiState);
    if (state.selectionWarning) warnings.push(state.selectionWarning);
    if (stability.error) warnings.push(stability.error);
    warnings = uniqueMessages(warnings);
    if (blockers.length || warnings.length) {
      lines.push('<div class="sqx-edge-mt5-auto2-flags">' + escapeHtml(blockers.concat(warnings).map(visualMessage).join(", ")) + '</div>');
    }
    if (state.applyResult && state.applyResult.status) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Apply</b><span>' + escapeHtml(visualMessage(state.applyResult.status)) + '</span></div>');
      if (state.applyResult.planId) {
        lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Apply plan</b><span>' + escapeHtml(state.applyResult.planId) + '</span></div>');
      }
    }
    if (state.applyResult && state.applyResult.appliedFields && state.applyResult.appliedFields.length) {
      lines.push('<div class="sqx-edge-mt5-auto2-row"><b>Fields</b><span>' + escapeHtml(state.applyResult.appliedFields.join(", ")) + '</span></div>');
    }
    lines.push('<div class="sqx-edge-mt5-auto2-actions"><button type="button" id="sqx-edge-mt5-auto2-refresh">Refrescar</button><button type="button" id="sqx-edge-mt5-auto8-apply" title="' + escapeHtml(uiState.buttonTitle) + '" ' + (!uiState.canApply ? 'disabled="disabled"' : '') + '>Aplicar cambios</button></div>');
    body.innerHTML = lines.join("");
    var refresh = byId("sqx-edge-mt5-auto2-refresh");
    if (refresh) refresh.addEventListener("click", function() {
      requestFromSelection([]);
    });
    var apply = byId("sqx-edge-mt5-auto8-apply");
    if (apply) apply.addEventListener("click", applyChanges);
  }

  function fieldLine(label, value) {
    return '<div><b>' + escapeHtml(label) + '</b><span>' + escapeHtml(value == null ? "-" : value) + '</span></div>';
  }

  function formatAge(seconds) {
    var value = Number(seconds);
    if (!isFinite(value) || value < 0) return "-";
    if (value < 90) return Math.round(value) + "s";
    return Math.round(value / 60) + "m";
  }

  function uniqueMessages(values) {
    var seen = {};
    var output = [];
    (values || []).forEach(function(value) {
      var key = String(value || "");
      if (!key || seen[key]) return;
      seen[key] = true;
      output.push(key);
    });
    return output;
  }

  function visualMessage(value) {
    var key = String(value == null ? "" : value);
    var labels = {
      checked_row_required_for_mt5_bridge: "Marca una unica fila con el check antes de usar MT5 Bridge.",
      multiple_checked_rows_blocked_for_mt5_bridge: "Hay mas de una fila marcada. Deja solo un check para continuar.",
      checked_row_symbol_not_found: "No encuentro el simbolo de la fila marcada. Cambia el check o pulsa Refrescar.",
      checked_row_target_mismatch_for_mt5_bridge: "La fila marcada no coincide con el simbolo solicitado. Deja marcado solo el instrumento que quieres usar.",
      checked_row_selection_ready: "Fila marcada lista.",
      selected_symbol_not_found: "No encuentro un instrumento valido. Marca una fila con el check.",
      listo_para_aplicar_en_data_manager: "Listo para aplicar en Data Manager.",
      sin_cambios_en_data_manager: "Sin cambios en Data Manager.",
      waiting_for_mt5_bridge: "Esperando respuesta del bridge MT5.",
      waiting_for_dukascopy_mirror_plan: "Comprobando mirror Dukascopy.",
      waiting_for_requested_response: "Esperando la respuesta solicitada.",
      waiting_for_requested_response_but_bridge_inactive: "MT5 Bridge no responde o no esta activo.",
      mt5_bridge_no_responde_o_no_esta_activo: "MT5 Bridge no responde o no esta activo.",
      mt5_bridge_ea_no_responde: "El EA de MT5 no responde.",
      mt5_bridge_latest_desfasado: "La ultima respuesta del bridge esta desfasada.",
      mt5_bridge_error_symbol_select_failed: "MT5 no pudo seleccionar el simbolo solicitado.",
      latest_response_request_id_mismatch: "La ultima respuesta pertenece a otra peticion.",
      latest_response_stale: "La ultima respuesta esta desfasada.",
      bridge_error_symbol_select_failed: "MT5 no pudo seleccionar el simbolo solicitado.",
      bridge_response_not_ok: "La respuesta del bridge no es valida.",
      spread_samples_missing: "Faltan muestras de spread en la respuesta.",
      spread_policy_value_missing: "Falta el valor de spread para la politica seleccionada.",
      latest_response_symbol_mismatch: "La ultima respuesta pertenece a otro simbolo.",
      request_newer_than_latest_response: "La peticion actual es mas nueva que la ultima respuesta.",
      resolviendo_seleccion_data_manager: "Resolviendo seleccion de Data Manager.",
      native_save_running: "Aplicando cambios en Data Manager.",
      applying_in_data_manager: "Aplicando cambios en Data Manager.",
      apply_completed_live_native_datamanager_save: "Cambios aplicados en Data Manager.",
      apply_noop_no_changes: "Sin cambios que aplicar.",
      nothing_to_apply: "Sin cambios que aplicar.",
      native_save_unavailable: "El Save nativo de Data Manager no esta disponible.",
      native_save_failed: "No se pudieron aplicar los cambios en Data Manager.",
      native_save_target_missing: "No encuentro el instrumento destino en Data Manager.",
      instrument_not_found_in_sqx_constants: "No encuentro el instrumento en Data Manager.",
      apply_refresh_required: "Pulsa Refrescar antes de aplicar.",
      bridge_validation_required: "Hace falta validar el bridge antes de aplicar.",
      apply_blocked_plan_not_ready: "El plan aun no esta listo para aplicar.",
      mirror_plan_not_ready: "El plan mirror aun no esta listo.",
      apply_blocked_by_policy: "La politica de estabilidad aun no permite aplicar.",
      current_check_running: "Hay una comprobacion en curso.",
      apply_wait_for_current_check: "Espera a que termine la comprobacion actual.",
      ready: "Listo.",
      catalog_ready_existing: "Catalogo listo: instrumento existente.",
      catalog_metadata_diff_only: "Catalogo listo: solo hay diferencias de metadatos.",
      catalog_history_missing: "Falta historia para este instrumento.",
      catalog_instrument_missing: "Falta crear el instrumento.",
      catalog_broker_missing: "Falta resolver el broker.",
      catalog_ambiguous_collision: "Hay una colision ambigua de simbolos.",
      plan_ready_apply_gated_offline: "Listo para aplicar en Data Manager.",
      plan_ready_apply_native_save: "Listo para aplicar en Data Manager.",
      plan_ready_noop_data_symbol_uses_darwinex_instrument: "Sin cambios en Data Manager.",
      dukascopy_metadata_mirror_requires_separate_exact_gate: "El mirror Dukascopy requiere confirmacion separada para aplicar.",
      dukascopy_data_symbol_already_uses_darwinex_instrument: "Este simbolo Dukascopy ya usa el instrumento Darwinex.",
      blocked_by_policy: "Bloqueado por politica.",
      stable_no_change: "Sin cambios estables que aplicar.",
      stability_policy_not_satisfied: "La politica de estabilidad aun no se cumple.",
      stability_insufficient_coverage: "Cobertura insuficiente para aplicar cambios.",
      stability_broker_contract_review_required: "Requiere revision del contrato del broker.",
      blocked_broker_contract_review: "Bloqueado: requiere revision del contrato del broker.",
      broker_contract_review_required: "Requiere revision del contrato del broker.",
      endpoint_missing_restart_required: "Falta reiniciar el backend local.",
      auto2_backend_endpoint_missing_restart_required: "Falta reiniciar el backend local.",
      auto3_backend_endpoint_missing_restart_required: "Falta reiniciar el backend local.",
      auto6_backend_endpoint_missing_restart_required: "Falta reiniciar el backend local."
    };
    return labels[key] || key;
  }

  function applyStatusLabel(status) {
    if (status === "native_save_running") return "aplicando_en_data_manager";
    if (status === "apply_completed_live_native_datamanager_save") return "aplicado_en_data_manager";
    if (status === "apply_noop_no_changes") return "sin_cambios_en_data_manager";
    return status || "";
  }

  function mirrorHasReadyNativeSaveStatus(mirror) {
    var status = mirror && mirror.status;
    return status === "plan_ready_apply_gated_offline" || status === "plan_ready_apply_native_save";
  }

  function mirrorHasNoopStatus(mirror) {
    return !!(mirror && mirror.ok && mirror.status === "plan_ready_noop_data_symbol_uses_darwinex_instrument");
  }

  function mirrorCanUseNativeSave(mirror) {
    return !!(
      mirror &&
      mirror.ok &&
      mirrorHasReadyNativeSaveStatus(mirror) &&
      !(mirror.blockers || []).length &&
      hasChanges(extractMirrorApplyFields(mirror))
    );
  }

  function bridgeCanUseNativeSave(result, stability) {
    return !!(
      result &&
      result.ok &&
      stability &&
      stability.futureApplyGateAllowed === true &&
      hasChanges(extractBridgeApplyFields(result))
    );
  }

  function mirrorHasNoNativeSaveChanges(mirror) {
    return !!(
      mirror &&
      mirror.ok &&
      !(mirror.blockers || []).length &&
      (mirrorHasNoopStatus(mirror) || (mirror.status && !hasChanges(extractMirrorApplyFields(mirror))))
    );
  }

  function nativeSaveUiState(result, stability, mirror) {
    var catalog = state.catalogResult || {};
    var plan = state.resolvePlan || {};
    var apply = state.applyResult || {};
    var healthState = bridgeHealthUiState(result);
    if (state.error) {
      return { status: state.error, className: "bad", canApply: false, buttonTitle: "Corrige el bloqueo antes de aplicar cambios" };
    }
    if (healthState) return healthState;
    if (state.selectionWarning === "resolviendo_seleccion_data_manager") {
      return { status: state.selectionWarning, className: "hold", canApply: false, buttonTitle: "Espera a que Data Manager confirme la seleccion" };
    }
    if (state.busy && isDukascopyMirrorSymbol(state.lastSymbol)) {
      return { status: "waiting_for_dukascopy_mirror_plan", className: "hold", canApply: false, buttonTitle: "Espera a que termine la comprobacion" };
    }
    if (state.busy) {
      return { status: "waiting_for_mt5_bridge", className: "hold", canApply: false, buttonTitle: "Espera a que termine la comprobacion" };
    }
    if (apply.status) {
      return {
        status: applyStatusLabel(apply.status),
        className: apply.ok ? "ok" : "hold",
        canApply: false,
        buttonTitle: apply.ok ? "Operacion ya resuelta; refresca para recalcular" : "No se puede aplicar hasta resolver el bloqueo"
      };
    }
    if (mirrorCanUseNativeSave(mirror)) {
      return {
        status: "listo_para_aplicar_en_data_manager",
        className: "ok",
        canApply: true,
        buttonTitle: "Aplicar con Save nativo de Data Manager"
      };
    }
    if (mirrorHasNoNativeSaveChanges(mirror)) {
      return {
        status: "sin_cambios_en_data_manager",
        className: "ok",
        canApply: false,
        buttonTitle: "No hay cambios de metadatos que aplicar"
      };
    }
    if (bridgeCanUseNativeSave(result, stability)) {
      return {
        status: "listo_para_aplicar_en_data_manager",
        className: "ok",
        canApply: true,
        buttonTitle: "Aplicar con Save nativo de Data Manager"
      };
    }
    if (stability && (stability.decision === "stable_no_change" || stability.status === "stable_no_change")) {
      return {
        status: "sin_cambios_en_data_manager",
        className: "ok",
        canApply: false,
        buttonTitle: "No hay cambios de metadatos que aplicar"
      };
    }
    if (mirror && mirror.status) {
      return {
        status: mirror.status,
        className: mirror.ok ? "hold" : "bad",
        canApply: false,
        buttonTitle: "El plan mirror aun no es aplicable"
      };
    }
    if (stability && stability.status) {
      return {
        status: stability.status,
        className: stability.futureApplyGateAllowed === true ? "ok" : "hold",
        canApply: false,
        buttonTitle: "La politica de estabilidad aun no permite aplicar"
      };
    }
    if (result && result.status) {
      return {
        status: result.status,
        className: result.ok ? "ok" : "bad",
        canApply: false,
        buttonTitle: "Refresca o resuelve el bloqueo antes de aplicar"
      };
    }
    if (plan.decision) {
      return { status: "catalog_" + plan.decision, className: "hold", canApply: false, buttonTitle: "Falta un plan aplicable" };
    }
    if (catalog.decision) {
      return { status: "catalog_" + catalog.decision, className: "hold", canApply: false, buttonTitle: "Falta un plan aplicable" };
    }
    return { status: "ready", className: "", canApply: false, buttonTitle: "Refresca para calcular cambios" };
  }

  function bridgeHealthUiState(result) {
    var health = result && result.bridgeHealth ? result.bridgeHealth : null;
    if (!health) return null;
    var status = health.panelStatus || health.status || "";
    if (!status || status === "mt5_bridge_health_ok" || status === "mt5_bridge_ready_latest_matches_request") return null;
    if (status === "mt5_bridge_no_request_pending" && !result.status) return null;
    if (result.status === "waiting_for_requested_response" || health.severity === "bad" || health.latestResponseStale) {
      return {
        status: status,
        className: health.severity === "bad" ? "bad" : "hold",
        canApply: false,
        buttonTitle: "El bridge MT5 no ha producido una respuesta fresca"
      };
    }
    return null;
  }

  function shouldStopPollingForBridgeHealth(result) {
    var health = result && result.bridgeHealth ? result.bridgeHealth : null;
    var status = health ? (health.panelStatus || health.status || "") : "";
    if (!health) return false;
    if (status === "mt5_bridge_ready_latest_matches_request" || status === "mt5_bridge_health_ok") return false;
    if (health.severity === "bad") return true;
    if (health.latestResponseStale || health.requestNewerThanLatestResponse) return true;
    return status === "mt5_bridge_no_responde_o_no_esta_activo" ||
      status === "mt5_bridge_ea_no_responde" ||
      status === "mt5_bridge_latest_desfasado" ||
      status === "mt5_bridge_error_symbol_select_failed";
  }

  function visibleWarnings(catalog, result, stability, mirror, uiState) {
    var health = result.bridgeHealth || {};
    var warnings = (catalog.warnings || [])
      .concat(result.warnings || [])
      .concat(health.blockers || [])
      .concat(health.warnings || [])
      .concat(stability.blockers || [])
      .concat(stability.warnings || [])
      .concat(stability.policyReasons || [])
      .concat(mirror.warnings || []);
    var hideLegacyMirrorGate = uiState.status === "listo_para_aplicar_en_data_manager" || uiState.status === "sin_cambios_en_data_manager";
    if (!hideLegacyMirrorGate) return uniqueMessages(warnings);
    return uniqueMessages(warnings.filter(function(warning) {
      return warning !== "dukascopy_metadata_mirror_requires_separate_exact_gate" &&
        warning !== "dukascopy_data_symbol_already_uses_darwinex_instrument";
    }));
  }

  function statusText(result) {
    var stability = state.stabilityResult || {};
    var mirror = state.mirrorResult || {};
    return nativeSaveUiState(result || {}, stability, mirror).status;
  }

  function statusClass(result, stability) {
    return nativeSaveUiState(result || {}, stability || {}, state.mirrorResult || {}).className;
  }

  function requestBridge(symbolOverride, options) {
    var requestedSymbol = candidateFromText(symbolOverride);
    var selection = checkedRowSelectionState();
    var symbol = "";
    var linkedInstrument = (options && options.linkedInstrument) || state.linkedInstrument || "";
    var seq = 0;
    clearTransientResults();
    if (!selection.ok) {
      state.error = selection.status || CHECKED_ROW_REQUIRED_STATUS;
      state.lastSymbol = "";
      state.linkedInstrument = "";
      state.checkedSelection = selection;
      state.lastResult = { ok: false, status: state.error, blockers: selection.blockers || [state.error] };
      state.open = true;
      render();
      return;
    }
    if (requestedSymbol && requestedSymbol !== selection.symbol) {
      state.error = "checked_row_target_mismatch_for_mt5_bridge";
      state.lastSymbol = "";
      state.linkedInstrument = "";
      state.checkedSelection = selection;
      state.lastResult = { ok: false, status: state.error, blockers: [state.error] };
      state.open = true;
      render();
      return;
    }
    symbol = selection.symbol;
    linkedInstrument = selection.linkedInstrument || linkedInstrument;
    seq = beginRequest(symbol, linkedInstrument);
    state.lastSymbol = symbol;
    state.linkedInstrument = linkedInstrument;
    state.checkedSelection = { ok: true, count: 1, status: "checked_row_selection_ready", symbol: symbol, linkedInstrument: linkedInstrument };
    state.busy = true;
    render();
    if (isDukascopyMirrorSymbol(symbol)) {
      state.busy = true;
      mirrorDukascopy(symbol, linkedInstrument).then(function(mirror) {
        if (!isCurrentRequest(seq, symbol)) return;
        state.busy = false;
        state.mirrorResult = mirror;
        state.lastResult = mirror;
        if (!mirror.ok) {
          state.error = mirror.error || mirror.status || (mirror.blockers || []).join(", ") || "dukascopy_mirror_plan_blocked";
        }
        render();
      });
      return;
    }
    auditCatalog(symbol).then(function(catalog) {
      if (!isCurrentRequest(seq, symbol)) return null;
      state.catalogResult = catalog;
      return resolveCatalogPlan(symbol).then(function(plan) {
        if (!isCurrentRequest(seq, symbol)) return null;
        state.resolvePlan = plan;
        if (plan && plan.ok) {
          state.catalogResult = Object.assign({}, catalog, {
            planId: plan.planId || "",
            nextAction: plan.nextAction || ""
          });
        }
        return catalog;
      });
    }).then(function(catalog) {
      if (!isCurrentRequest(seq, symbol) || !catalog) return null;
      if (!catalog.ok) {
        state.busy = false;
        state.error = catalog.error || catalog.status || catalog.decision || "catalog_audit_failed";
        state.lastResult = catalog;
        render();
        return null;
      }
      if (catalog.decision === "broker_missing" || catalog.decision === "ambiguous_collision") {
        state.busy = false;
        state.error = catalog.decision;
        state.lastResult = catalog;
        render();
        return null;
      }
      return fetchJson("/sqx144/mt5-auto2/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: symbol, spreadPolicy: DEFAULT_POLICY, spreadTimeframe: "M1" })
      });
    }).then(function(json) {
      if (!isCurrentRequest(seq, symbol)) return;
      if (!json) return;
      state.busy = false;
      if (!json.ok) {
        state.error = json.error || json.status || "request_failed";
        state.lastResult = json;
        render();
        return;
      }
      state.lastRequestId = json.requestId || "";
      state.lastResult = json;
      render();
      validateBridge(0, { symbol: symbol, requestId: state.lastRequestId, seq: seq });
    });
  }

  function auditCatalog(symbol) {
    return fetchJson("/sqx144/mt5-auto3/catalog-audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ broker: DEFAULT_BROKER, symbol: symbol })
    });
  }

  function resolveCatalogPlan(symbol) {
    return fetchJson("/sqx144/mt5-auto3/resolve-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ broker: DEFAULT_BROKER, symbol: symbol, spreadPolicy: DEFAULT_POLICY })
    });
  }

  function validateBridge(attempt, context) {
    var bridgeContext = context || { symbol: state.lastSymbol || "", requestId: state.lastRequestId || "" };
    var seq = bridgeContext.seq || state.requestSeq;
    if (!isCurrentRequest(seq, bridgeContext.symbol)) return;
    state.busy = true;
    render();
    fetchJson("/sqx144/mt5-auto3/bridge-validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        broker: DEFAULT_BROKER,
        symbol: bridgeContext.symbol || "",
        spreadPolicy: DEFAULT_POLICY,
        expectedRequestId: bridgeContext.requestId || "",
        expectedSymbol: bridgeContext.symbol || ""
      })
    }).then(function(json) {
      if (!isCurrentRequest(seq, bridgeContext.symbol)) return;
      state.lastResult = json;
      if (json.status === "waiting_for_requested_response" && !shouldStopPollingForBridgeHealth(json) && attempt < 20) {
        global.setTimeout(function() { validateBridge(attempt + 1, bridgeContext); }, 1500);
        return;
      }
      if (!json.ok) {
        state.busy = false;
        state.error = json.bridgeHealth ? "" : (json.error || json.status || (json.blockers || []).join(", ") || CROSSED_SYMBOL_BLOCKER || "validation_failed");
        render();
        return;
      }
      evaluateStability(bridgeContext).then(function(stability) {
        if (!isCurrentRequest(seq, bridgeContext.symbol)) return;
        state.stabilityResult = stability;
        state.busy = false;
        state.error = "";
        render();
      });
    });
  }

  function evaluateStability(context) {
    var bridgeContext = context || { symbol: state.lastSymbol || "", requestId: state.lastRequestId || "" };
    return fetchJson("/sqx144/mt5-auto6/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        broker: DEFAULT_BROKER,
        symbol: bridgeContext.symbol || "",
        spreadPolicy: DEFAULT_POLICY,
        expectedRequestId: bridgeContext.requestId || ""
      })
    });
  }

  function mirrorDukascopy(symbol, linkedInstrument) {
    return fetchJson("/sqx144/mt5-auto7/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol: symbol, linkedInstrument: linkedInstrument || linkedInstrumentFromEditDialog() })
    });
  }

  function clearTransientResults() {
    state.lastRequestId = "";
    state.catalogResult = null;
    state.resolvePlan = null;
    state.stabilityResult = null;
    state.mirrorResult = null;
    state.applyResult = null;
    state.lastResult = null;
    state.checkedSelection = null;
    state.selectionWarning = "";
    state.error = "";
  }

  function beginRequest(symbol, linkedInstrument) {
    state.requestSeq += 1;
    state.lastSymbol = symbol;
    state.linkedInstrument = linkedInstrument || "";
    return state.requestSeq;
  }

  function isCurrentRequest(seq, symbol) {
    return seq === state.requestSeq && (!symbol || state.lastSymbol === symbol);
  }

  function hasChanges(changes) {
    return !!(changes && Object.keys(changes).length);
  }

  function angularInjector() {
    if (!global.angular || !global.document || !global.document.body) return null;
    try {
      var wrapped = global.angular.element(global.document.body);
      return wrapped && wrapped.injector ? wrapped.injector() : null;
    } catch (err) {
      return null;
    }
  }

  function angularService(name) {
    var injector = angularInjector();
    if (!injector || !injector.get) return null;
    try {
      return injector.get(name);
    } catch (err) {
      return null;
    }
  }

  function cloneValue(value) {
    if (global.angular && global.angular.copy) {
      try { return global.angular.copy(value); } catch (err) {}
    }
    return JSON.parse(JSON.stringify(value || {}));
  }

  function sameInstrumentName(left, right) {
    return String(left || "").toLowerCase() === String(right || "").toLowerCase();
  }

  function sameFieldValue(left, right) {
    if (left == null && right == null) return true;
    var leftNumber = Number(left);
    var rightNumber = Number(right);
    if (!isNaN(leftNumber) && !isNaN(rightNumber)) {
      return Math.abs(leftNumber - rightNumber) < 0.000000001;
    }
    return String(left == null ? "" : left) === String(right == null ? "" : right);
  }

  function sqxInstrumentFromConstants(instrumentName) {
    var SQConstants = angularService("SQConstants");
    var constants = SQConstants && SQConstants.getConstants ? SQConstants.getConstants() : null;
    var instruments = constants && constants.instruments ? constants.instruments : [];
    for (var i = 0; i < instruments.length; i += 1) {
      if (sameInstrumentName(instruments[i].instrument, instrumentName)) return cloneValue(instruments[i]);
    }
    return null;
  }

  function newValueFromChange(change) {
    if (change && typeof change === "object" && Object.prototype.hasOwnProperty.call(change, "new")) {
      return change.new;
    }
    return change;
  }

  function extractMirrorApplyFields(mirror) {
    var fields = {};
    var changes = (mirror && mirror.changes) || {};
    Object.keys(LIVE_APPLY_FIELD_MAP).forEach(function(key) {
      if (Object.prototype.hasOwnProperty.call(changes, key)) {
        fields[key] = newValueFromChange(changes[key]);
      }
    });
    return fields;
  }

  function extractBridgeApplyFields(result) {
    var fields = {};
    var proposed = (result && result.proposedSqxFields) || {};
    ["DEFAULTSPREAD", "POINTVALUE", "TICKSIZE", "TICKSTEP"].forEach(function(key) {
      if (proposed[key] != null) fields[key] = proposed[key];
    });
    return fields;
  }

  function buildNativeInstrumentPayload(targetInstrument, fields) {
    var current = sqxInstrumentFromConstants(targetInstrument);
    var applied = [];
    var noops = [];
    var payload;
    if (!current) {
      return { ok: false, status: "native_save_target_missing", blockers: ["instrument_not_found_in_sqx_constants"] };
    }
    payload = cloneValue(current);
    Object.keys(fields || {}).forEach(function(key) {
      var property = LIVE_APPLY_FIELD_MAP[key];
      var next = fields[key];
      if (!property || next == null) return;
      if (sameFieldValue(payload[property], next)) {
        noops.push(key);
      } else {
        payload[property] = next;
        applied.push(key);
      }
    });
    if (!applied.length) {
      return { ok: true, status: "apply_noop_no_changes", noops: noops };
    }
    payload.description = payload.description || "not set";
    return { ok: true, payload: payload, appliedFields: applied, noops: noops };
  }

  function applyViaNativeDataManagerSave(payload) {
    var BackendService = angularService("BackendService");
    var rootScope = angularService("$rootScope");
    if (!BackendService || !BackendService.getPromise) {
      return Promise.resolve({ ok: false, status: "native_save_unavailable", blockers: ["backend_service_unavailable"] });
    }
    return Promise.resolve(BackendService.getPromise("/instruments/editInstrument", payload)).then(function(result) {
      var data = (result && result.data) || {};
      if (data.success || (result && result.success)) {
        if (rootScope && rootScope.showSuccess) rootScope.showSuccess("Instrument modified");
        return { ok: true, status: "apply_completed_live_native_datamanager_save", success: data.success || result.success };
      }
      return {
        ok: false,
        status: "native_save_failed",
        blockers: [data.error || (result && result.error) || "native_save_failed"]
      };
    }).catch(function(err) {
      return { ok: false, status: "native_save_failed", blockers: [err && err.message ? err.message : "native_save_failed"] };
    });
  }

  function liveApplyPlan() {
    var selection = checkedRowSelectionState();
    if (!selection.ok) {
      return { ok: false, status: selection.status, blockers: selection.blockers || [selection.status] };
    }
    if (state.lastSymbol && selection.symbol !== state.lastSymbol) {
      return {
        ok: false,
        status: "checked_row_target_mismatch_for_mt5_bridge",
        blockers: ["checked_row_target_mismatch_for_mt5_bridge"]
      };
    }
    var mirror = state.mirrorResult || {};
    var stability = state.stabilityResult || {};
    var result = state.lastResult || {};
    if (isDukascopyMirrorSymbol(state.lastSymbol)) {
      if (!mirror.status) return { ok: false, status: "apply_refresh_required", blockers: ["refresh_required"] };
      if (!mirror.ok || (mirror.blockers || []).length) {
        return { ok: false, status: "apply_blocked_plan_not_ready", blockers: mirror.blockers || ["mirror_plan_not_ready"] };
      }
      return {
        ok: true,
        targetInstrument: mirror.targetInstrument || state.linkedInstrument || state.lastSymbol,
        source: "dukascopy_mirror",
        planId: mirror.planId || "",
        fields: extractMirrorApplyFields(mirror)
      };
    }
    if (!result.ok) return { ok: false, status: "apply_refresh_required", blockers: ["bridge_validation_required"] };
    if (stability.futureApplyGateAllowed !== true) {
      return {
        ok: false,
        status: "apply_blocked_by_policy",
        blockers: stability.blockers || stability.policyReasons || ["stability_policy_not_satisfied"]
      };
    }
    return {
      ok: true,
      targetInstrument: state.lastSymbol,
      source: "mt5_bridge_stability_eligible",
      planId: (state.catalogResult && state.catalogResult.planId) || "",
      fields: extractBridgeApplyFields(result)
    };
  }

  function applyChanges() {
    if (state.busy) {
      state.applyResult = { ok: false, status: "apply_wait_for_current_check", blockers: ["current_check_running"] };
      render();
      return Promise.resolve(state.applyResult);
    }
    var plan = liveApplyPlan();
    if (!plan.ok) {
      state.applyResult = plan;
      render();
      return Promise.resolve(plan);
    }
    if (!hasChanges(plan.fields)) {
      state.applyResult = { ok: true, status: "apply_noop_no_changes", planId: plan.planId || "", warnings: ["nothing_to_apply"] };
      render();
      return Promise.resolve(state.applyResult);
    }
    var built = buildNativeInstrumentPayload(plan.targetInstrument, plan.fields);
    if (!built.ok || !built.payload) {
      state.applyResult = Object.assign({ planId: plan.planId || "" }, built);
      render();
      return Promise.resolve(state.applyResult);
    }
    if (!built.appliedFields || !built.appliedFields.length) {
      state.applyResult = { ok: true, status: "apply_noop_no_changes", planId: plan.planId || "", noops: built.noops || [] };
      render();
      return Promise.resolve(state.applyResult);
    }
    state.busy = true;
    state.applyResult = {
      ok: true,
      status: "native_save_running",
      planId: plan.planId || "",
      targetInstrument: plan.targetInstrument,
      appliedFields: built.appliedFields,
      source: plan.source
    };
    render();
    return applyViaNativeDataManagerSave(built.payload).then(function(saved) {
      state.busy = false;
      state.applyResult = Object.assign({}, saved, {
        planId: plan.planId || "",
        targetInstrument: plan.targetInstrument,
        appliedFields: built.appliedFields,
        source: plan.source,
        nativeSqxInstrumentEndpoint: "/instruments/editInstrument",
        nativeDataManagerSaveAllowed: AUTO8_NATIVE_SAVE_CONTRACT.nativeDataManagerSaveAllowed,
        sqxOpenNativeSaveAllowed: AUTO8_NATIVE_SAVE_CONTRACT.sqxOpenNativeSaveAllowed,
        directDbWriteAllowed: AUTO8_NATIVE_SAVE_CONTRACT.directDbWriteAllowed,
        directDbHistoryInsertAllowed: AUTO8_NATIVE_SAVE_CONTRACT.directDbHistoryInsertAllowed,
        historyImportAllowed: AUTO8_NATIVE_SAVE_CONTRACT.historyImportAllowed,
        usesDataSourceHistoryImport: AUTO8_NATIVE_SAVE_CONTRACT.usesDataSourceHistoryImport
      });
      render();
      return state.applyResult;
    }).catch(function(err) {
      state.busy = false;
      state.applyResult = {
        ok: false,
        status: "native_save_failed",
        blockers: [err && err.message ? err.message : "native_save_failed"],
        planId: plan.planId || "",
        targetInstrument: plan.targetInstrument,
        appliedFields: built.appliedFields,
        directDbWriteAllowed: false
      };
      render();
      return state.applyResult;
    });
  }

  function init() {
    ensurePanel();
    registerAngularAction();
    ensureLauncher();
    global.document.addEventListener("pointerdown", handleAngularActionClickFallback, true);
    global.document.addEventListener("click", handleAngularActionClickFallback, true);
    global.setInterval(function() {
      registerAngularAction();
      ensureLauncher();
    }, 2000);
  }

  registerAngularAction();

  if (global.document.readyState === "loading") {
    global.document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.SQXEdgeMt5Auto2 = {
    version: VERSION,
    catalogTriageVersion: CATALOG_TRIAGE_VERSION,
    stabilityVersion: AUTO6_STABILITY_VERSION,
    dukascopyMirrorVersion: AUTO7_DUKASCOPY_MIRROR_VERSION,
    dukascopyDataSymbolGuardVersion: AUTO7_DATA_SYMBOL_GUARD_VERSION,
    auto8NativeSaveVersion: AUTO8_NATIVE_SAVE_VERSION,
    auto8UxStatusVersion: AUTO8_UX_STATUS_VERSION,
    auto9HealthWatchdogVersion: AUTO9_HEALTH_WATCHDOG_VERSION,
    auto9HealthPollStopVersion: AUTO9_HEALTH_POLL_STOP_VERSION,
    auto9SingleClickUxVersion: AUTO9_SINGLE_CLICK_UX_VERSION,
    auto9SingleClickFallbackVersion: AUTO9_SINGLE_CLICK_FALLBACK_VERSION,
    auto9CheckedRowSelectionVersion: AUTO9_CHECKED_ROW_SELECTION_VERSION,
    auto9VisualEsSelectionVersion: AUTO9_VISUAL_ES_SELECTION_VERSION,
    auto9DataSymbolPriorityVersion: AUTO9_DATA_SYMBOL_PRIORITY_VERSION,
    nativeSaveContract: AUTO8_NATIVE_SAVE_CONTRACT,
    healthWatchdogContract: AUTO9_HEALTH_WATCHDOG_CONTRACT,
    healthStatusLabels: AUTO9_HEALTH_STATUS_LABELS,
    selectionGuardVersion: SELECTION_GUARD_VERSION,
    detectSymbol: selectedSymbol,
    detectEditDialogSymbol: selectedSymbolFromEditDialog,
    detectCheckedRowSymbol: selectedSymbolFromCheckedRows,
    checkedRowSelectionState: checkedRowSelectionState,
    detectDukascopyDataSymbol: selectedDukascopyDataSymbolFromEditDialog,
    detectLinkedInstrument: linkedInstrumentFromEditDialog,
    isAllowedBareSymbol: isAllowedBareSymbol,
    candidateFromDataRowText: candidateFromDataRowText,
    symbolFromSelectionItem: symbolFromSelectionItem,
    linkedInstrumentFromSelectionItem: linkedInstrumentFromSelectionItem,
    requestFromSelection: requestFromSelection,
    auditCatalog: auditCatalog,
    resolveCatalogPlan: resolveCatalogPlan,
    evaluateStability: evaluateStability,
    mirrorDukascopy: mirrorDukascopy,
    applyChanges: applyChanges,
    applyViaNativeDataManagerSave: applyViaNativeDataManagerSave,
    liveApplyPlan: liveApplyPlan,
    nativeSaveUiState: nativeSaveUiState,
    visualMessage: visualMessage,
    shouldStopPollingForBridgeHealth: shouldStopPollingForBridgeHealth,
    isMt5BridgeActionNode: isMt5BridgeActionNode,
    isDukascopyMirrorSymbol: isDukascopyMirrorSymbol,
    requestBridge: requestBridge
  };
})(window);
