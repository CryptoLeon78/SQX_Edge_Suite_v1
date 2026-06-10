(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var POLICY_VERSION = 'sqx-exit-policy-v1';
  var STORAGE_KEY = 'sqx_exit_policy_user_v1';

  var ACTIONS = {
    KEEP: 'keep',
    DISABLE: 'disable',
    RANDOMIZE: 'randomize',
    BLOCK: 'block'
  };

  var KNOWN_EXIT_LABELS = {
    exit_after_bars: 'Exit After Bars',
    exit_after_days: 'Exit After Days LaCity',
    exit_after_trading_days: 'Exit After TDays LaCity',
    profit_target: 'Profit Target',
    stop_loss: 'Stop Loss',
    trailing_stop: 'Trailing Stop',
    break_even: 'Move SL to BE',
    ts_activation: 'TS Activation Level',
    unknown: 'Salida desconocida'
  };

  var DEFAULT_KIND_ACTIONS = {
    exit_after_bars: ACTIONS.DISABLE,
    exit_after_days: ACTIONS.DISABLE,
    exit_after_trading_days: ACTIONS.DISABLE,
    profit_target: ACTIONS.RANDOMIZE,
    stop_loss: ACTIONS.RANDOMIZE,
    trailing_stop: ACTIONS.RANDOMIZE,
    break_even: ACTIONS.DISABLE,
    ts_activation: ACTIONS.DISABLE,
    unknown: ACTIONS.BLOCK
  };

  var FORMULA_BY_KIND = {
    profit_target: 'SQ.Formulas.SLPT.FixedValue',
    stop_loss: 'SQ.Formulas.SLPT.FixedValue',
    trailing_stop: 'SQ.Formulas.RangeLevel.FixedValue'
  };

  var _policy = loadPolicy();

  function loadPolicy() {
    var fallback = { version: POLICY_VERSION, overrides: {} };
    try {
      if (!global.localStorage) return fallback;
      var parsed = JSON.parse(global.localStorage.getItem(STORAGE_KEY) || 'null');
      if (!parsed || parsed.version !== POLICY_VERSION) return fallback;
      parsed.overrides = parsed.overrides || {};
      return parsed;
    } catch (_err) {
      return fallback;
    }
  }

  function savePolicy() {
    try {
      if (global.localStorage) {
        global.localStorage.setItem(STORAGE_KEY, JSON.stringify(_policy));
      }
    } catch (_err) {}
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function cleanText(value) {
    return String(value === undefined || value === null ? '' : value).trim();
  }

  function normalizeToken(value) {
    return cleanText(value)
      .toLowerCase()
      .replace(/&quot;|&amp;quot;/g, '')
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  }

  function parseAttributes(tag) {
    var attrs = {};
    String(tag || '').replace(/([A-Za-z0-9_:#.-]+)="([^"]*)"/g, function(_match, key, value) {
      attrs[key] = value;
      return _match;
    });
    return attrs;
  }

  function textValueFromParamTag(paramTag) {
    var inner = String(paramTag || '').replace(/^<Param\b[^>]*>/i, '').replace(/<\/Param>\s*$/i, '');
    if (/<Formula\b/i.test(inner)) return '[Formula]';
    return cleanText(inner.replace(/<[^>]+>/g, ''));
  }

  function numericValue(value) {
    var raw = cleanText(value).replace(',', '.');
    if (!raw || raw === '[Formula]') return null;
    var parsed = parseFloat(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }

  function isActiveValue(component) {
    if (!component) return false;
    if (component.hasFormula) return true;
    if (component.generated) return true;
    var number = numericValue(component.value);
    if (number !== null) return number !== 0;
    return cleanText(component.value) !== '';
  }

  function classifyExit(attrs) {
    var raw = [
      attrs.key,
      attrs.name,
      attrs.display,
      attrs.controlType,
      attrs.exitMethodType,
      attrs.identification
    ].join(' ');
    var token = normalizeToken(raw);
    if (/exit_after_bars|exitafterbars|exitafterxbars/.test(token)) return 'exit_after_bars';
    if (/exit_after_trading_days|exitaftertradingdays|exit_after_tdays|exitaftertdays|exit_aft_trd_dys|exitafttrddys|tdays_lacity/.test(token)) return 'exit_after_trading_days';
    if (/exit_after_days|exitafterdays|exit_aft_dys|exitaftdys|after_days_lacity/.test(token)) return 'exit_after_days';
    if (/profit_target|profittarget/.test(token) || attrs.exitMethodType === 'PT') return 'profit_target';
    if (/trailing_stop|trailingstop/.test(token)) return 'trailing_stop';
    if (/move_sl.*be|sl.*be|break_even|breakeven/.test(token)) return 'break_even';
    if (/ts_activation|activation_level/.test(token)) return 'ts_activation';
    if (/stop_loss|stoploss/.test(token) || attrs.exitMethodType === 'SL') return 'stop_loss';
    return 'unknown';
  }

  function labelFor(attrs, kind) {
    return cleanText(attrs.name || attrs.display) || KNOWN_EXIT_LABELS[kind] || KNOWN_EXIT_LABELS.unknown;
  }

  function componentId(kind, key, index, entryIndex) {
    return [kind, normalizeToken(key || 'no_key'), entryIndex || 0, index].join('__');
  }

  function detectExitComponentsFromDoc(doc) {
    var params = doc ? doc.querySelectorAll('Param[exitMethod="true"]') : [];
    var entryIndexes = new Map();
    var nextEntryIndex = 1;
    return Array.prototype.map.call(params, function(param, index) {
      var attrs = {};
      Array.prototype.forEach.call(param.attributes || [], function(attr) {
        attrs[attr.name] = attr.value;
      });
      var enterItem = closestElement(param, function(node) {
        return node.tagName === 'Item' && node.getAttribute('key') === 'EnterAtMarket';
      });
      if (enterItem && !entryIndexes.has(enterItem)) {
        entryIndexes.set(enterItem, nextEntryIndex);
        nextEntryIndex += 1;
      }
      var entryIndex = enterItem ? entryIndexes.get(enterItem) : 0;
      var kind = classifyExit(attrs);
      var value = cleanText(param.textContent || attrs.defaultValue || '');
      var generated = param.getAttribute('generate') === 'random' || param.getAttribute('randomValue') === 'default';
      var hasFormula = !!param.querySelector('Formula');
      var component = {
        id: componentId(kind, attrs.key, index, entryIndex),
        index: index,
        entryIndex: entryIndex,
        key: attrs.key || '',
        name: attrs.name || '',
        label: labelFor(attrs, kind),
        kind: kind,
        value: value,
        generated: generated,
        hasFormula: hasFormula,
        active: false
      };
      component.active = isActiveValue(component);
      return component;
    });
  }

  function closestElement(node, predicate) {
    var current = node;
    while (current) {
      if (current.nodeType === 1 && predicate(current)) return current;
      current = current.parentNode;
    }
    return null;
  }

  function detectExitComponentsFromText(xml) {
    var components = [];
    var entryIndex = 0;
    String(xml || '').replace(/<Item\b[^>]*key="EnterAtMarket"[\s\S]*?<\/Item>/gi, function(block) {
      entryIndex += 1;
      block.replace(/<Param\b[^>]*exitMethod="true"[^>]*>[\s\S]*?<\/Param>/gi, function(paramTag) {
        var attrs = parseAttributes(paramTag.split('>')[0] + '>');
        var kind = classifyExit(attrs);
        var component = {
          id: componentId(kind, attrs.key, components.length, entryIndex),
          index: components.length,
          entryIndex: entryIndex,
          key: attrs.key || '',
          name: attrs.name || '',
          label: labelFor(attrs, kind),
          kind: kind,
          value: textValueFromParamTag(paramTag),
          generated: /generate="random"|randomValue="default"/i.test(paramTag),
          hasFormula: /<Formula\b/i.test(paramTag),
          active: false
        };
        component.active = isActiveValue(component);
        components.push(component);
        return paramTag;
      });
      return block;
    });
    return components;
  }

  function detectExitComponentsFromXml(xml) {
    var source = String(xml || '');
    if (!source) return [];
    if (global.DOMParser) {
      try {
        var doc = new global.DOMParser().parseFromString(source, 'text/xml');
        return detectExitComponentsFromDoc(doc);
      } catch (_err) {
        return detectExitComponentsFromText(source);
      }
    }
    return detectExitComponentsFromText(source);
  }

  function resolveXml(strategyOrXml) {
    if (typeof strategyOrXml === 'string') return strategyOrXml;
    if (strategyOrXml && strategyOrXml._strategyXml) return strategyOrXml._strategyXml;
    return '';
  }

  function resolveOverrides(overrides) {
    var merged = Object.assign({}, _policy.overrides || {});
    Object.keys(overrides || {}).forEach(function(key) {
      merged[key] = overrides[key];
    });
    return merged;
  }

  function defaultReason(kind, action) {
    if (action === ACTIONS.RANDOMIZE) return 'salida operativa permitida por metodologia C2';
    if (kind === 'exit_after_bars') return 'desactivado para no fijar cierre temporal del template C2';
    if (kind === 'exit_after_days' || kind === 'exit_after_trading_days') return 'salida LaCity temporal no metodologica para C2';
    if (kind === 'break_even' || kind === 'ts_activation') return 'salida auxiliar no incluida en el template base C2';
    if (kind === 'unknown') return 'salida activa desconocida requiere decision explicita';
    return 'perfil metodologico por defecto';
  }

  function buildDefaultExitPlan(strategyOrXml, overrides) {
    var components = detectExitComponentsFromXml(resolveXml(strategyOrXml));
    var mergedOverrides = resolveOverrides(overrides);
    var planned = components.map(function(component) {
      var override = mergedOverrides[component.id] || mergedOverrides[component.kind] || {};
      if (typeof override === 'string') override = { action: override };
      var defaultAction = DEFAULT_KIND_ACTIONS[component.kind] || ACTIONS.BLOCK;
      var action = override.action || defaultAction;
      var plannedComponent = Object.assign({}, component, {
        defaultAction: defaultAction,
        action: action,
        overridden: !!override.action,
        randomize: action === ACTIONS.RANDOMIZE,
        blocked: action === ACTIONS.BLOCK && component.active,
        reason: override.reason || defaultReason(component.kind, action)
      });
      return plannedComponent;
    });
    return {
      version: POLICY_VERSION,
      profile: 'metodologica-c2',
      components: planned,
      generatedAt: new Date().toISOString()
    };
  }

  function createFixedValueFormula(doc, formulaKey) {
    var formula = doc.createElement('Formula');
    formula.setAttribute('key', formulaKey);
    var param = doc.createElement('Param');
    param.setAttribute('key', '#Value#');
    param.setAttribute('name', 'Value');
    param.setAttribute('type', 'double');
    param.setAttribute('defaultValue', '50');
    param.setAttribute('controlType', 'jspinnerVar');
    param.setAttribute('minValue', '1');
    param.setAttribute('maxValue', '9999999');
    param.setAttribute('step', '1');
    param.setAttribute('postfix', 'pips');
    param.setAttribute('builderMinValue', '5');
    param.setAttribute('builderMaxValue', '500');
    param.setAttribute('builderStep', '1');
    param.textContent = '50';
    formula.appendChild(param);
    return formula;
  }

  function entryIdentification(param, fallbackIndex) {
    var enterItem = closestElement(param, function(node) {
      return node.tagName === 'Item' && node.getAttribute('key') === 'EnterAtMarket';
    });
    if (enterItem) {
      var idParam = enterItem.querySelector('Param[key="#Identification#"]');
      if (idParam && cleanText(idParam.textContent)) return cleanText(idParam.textContent);
    }
    return 'EnterAtMarket' + String(fallbackIndex || 1);
  }

  function mutateParam(param, component, action) {
    if (action === ACTIONS.KEEP) return;
    if (action === ACTIONS.DISABLE) {
      param.removeAttribute('generate');
      param.removeAttribute('randomValue');
      while (param.firstChild) param.removeChild(param.firstChild);
      param.textContent = '0';
      return;
    }
    if (action === ACTIONS.RANDOMIZE) {
      var formulaKey = FORMULA_BY_KIND[component.kind];
      if (!formulaKey) return;
      param.setAttribute('generate', 'random');
      param.setAttribute('randomValue', 'default');
      param.setAttribute('identification', entryIdentification(param, component.entryIndex));
      while (param.firstChild) param.removeChild(param.firstChild);
      param.appendChild(createFixedValueFormula(param.ownerDocument, formulaKey));
    }
  }

  function applyExitPlanWithDom(xml, plan) {
    var summary = summarizeExitPlan(plan);
    if (summary.blocked.length) {
      throw new Error('Salida desconocida activa sin decision: ' + summary.blocked.join(', '));
    }
    var doc = new global.DOMParser().parseFromString(String(xml || ''), 'text/xml');
    var params = doc.querySelectorAll('Param[exitMethod="true"]');
    var byId = {};
    (plan.components || []).forEach(function(component) {
      byId[component.id] = component;
    });
    var detected = detectExitComponentsFromDoc(doc);
    Array.prototype.forEach.call(params, function(param, index) {
      var component = byId[detected[index] && detected[index].id] || detected[index];
      if (!component) return;
      mutateParam(param, component, component.action);
    });
    return new global.XMLSerializer().serializeToString(doc);
  }

  function replaceParamContent(paramTag, content, stripRandom) {
    var open = paramTag.match(/^<Param\b[^>]*>/i);
    var close = paramTag.match(/<\/Param>\s*$/i);
    if (!open || !close) return paramTag;
    var openTag = open[0];
    if (stripRandom) {
      openTag = openTag.replace(/\s+generate="[^"]*"/ig, '').replace(/\s+randomValue="[^"]*"/ig, '');
    }
    return openTag + content + close[0];
  }

  function applyExitPlanWithText(xml, plan) {
    var summary = summarizeExitPlan(plan);
    if (summary.blocked.length) {
      throw new Error('Salida desconocida activa sin decision: ' + summary.blocked.join(', '));
    }
    var componentIndex = 0;
    return String(xml || '').replace(/<Param\b[^>]*exitMethod="true"[^>]*>[\s\S]*?<\/Param>/gi, function(paramTag) {
      var component = (plan.components || [])[componentIndex];
      componentIndex += 1;
      if (!component || component.action === ACTIONS.KEEP) return paramTag;
      if (component.action === ACTIONS.DISABLE) return replaceParamContent(paramTag, '0', true);
      if (component.action === ACTIONS.RANDOMIZE) {
        var formulaKey = FORMULA_BY_KIND[component.kind];
        if (!formulaKey) return paramTag;
        var formula = '<Formula key="' + formulaKey + '"><Param key="#Value#" name="Value" type="double" defaultValue="50" controlType="jspinnerVar" minValue="1" maxValue="9999999" step="1" postfix="pips" builderMinValue="5" builderMaxValue="500" builderStep="1">50</Param></Formula>';
        var openTag = paramTag.match(/^<Param\b[^>]*>/i)[0];
        openTag = openTag.replace(/\s+generate="[^"]*"/ig, '').replace(/\s+randomValue="[^"]*"/ig, '');
        if (!/\sgenerate="/i.test(openTag)) openTag = openTag.replace(/>$/, ' generate="random" randomValue="default">');
        return openTag + formula + '</Param>';
      }
      return paramTag;
    });
  }

  function applyExitPlanToStrategyXml(xml, plan) {
    var exitPlan = plan || buildDefaultExitPlan(xml);
    if (global.DOMParser && global.XMLSerializer) return applyExitPlanWithDom(xml, exitPlan);
    return applyExitPlanWithText(xml, exitPlan);
  }

  function summarizeExitPlan(plan) {
    var summary = {
      version: POLICY_VERSION,
      detected: [],
      disabled: [],
      randomized: [],
      kept: [],
      blocked: [],
      unknown: [],
      overrides: []
    };
    (plan && plan.components || []).forEach(function(component) {
      var label = component.label || component.key || component.kind;
      summary.detected.push(label);
      if (component.kind === 'unknown') summary.unknown.push(label);
      if (component.overridden) summary.overrides.push(label);
      if (component.action === ACTIONS.DISABLE) summary.disabled.push(label);
      if (component.action === ACTIONS.RANDOMIZE) summary.randomized.push(label);
      if (component.action === ACTIONS.KEEP) summary.kept.push(label);
      if (component.blocked) summary.blocked.push(label);
    });
    return summary;
  }

  function getPolicy() {
    return clone(_policy);
  }

  function setUserOverride(key, value) {
    if (!key) return getPolicy();
    _policy.version = POLICY_VERSION;
    _policy.overrides = _policy.overrides || {};
    if (value === undefined || value === null || value === '') delete _policy.overrides[key];
    else _policy.overrides[key] = value;
    savePolicy();
    return getPolicy();
  }

  SQX.exitPolicy = {
    version: POLICY_VERSION,
    actions: ACTIONS,
    detectExitComponentsFromXml: detectExitComponentsFromXml,
    buildDefaultExitPlan: buildDefaultExitPlan,
    applyExitPlanToStrategyXml: applyExitPlanToStrategyXml,
    summarizeExitPlan: summarizeExitPlan,
    getPolicy: getPolicy,
    setUserOverride: setUserOverride
  };

  if (SQX.registerModule) SQX.registerModule('exit-policy', SQX.exitPolicy);
})(window);
