import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');

class ClassList {
  constructor(initial = []) {
    this.values = new Set(initial);
  }
  add(...names) {
    names.forEach(name => this.values.add(name));
  }
  remove(...names) {
    names.forEach(name => this.values.delete(name));
  }
  contains(name) {
    return this.values.has(name);
  }
}

class Element {
  constructor(id, classes = [], dataset = {}) {
    this.id = id;
    this.classList = new ClassList(classes);
    this.dataset = dataset;
    this.listeners = {};
    this.style = { display: '', width: '' };
    this.textContent = '';
    this.innerHTML = '';
    this.checked = false;
    this.tagName = '';
    this.type = '';
  }
  addEventListener(type, handler) {
    this.listeners[type] = this.listeners[type] || [];
    this.listeners[type].push(handler);
  }
  click() {
    (this.listeners.click || []).forEach(handler => handler({ target: this }));
  }
  dispatch(type, event = { target: this }) {
    (this.listeners[type] || []).forEach(handler => handler(event));
  }
}

class FakeDocument {
  constructor() {
    this.elements = new Map();
    this.tabs = [];
    this.panels = [];
  }
  add(element) {
    this.elements.set(element.id, element);
    return element;
  }
  addTab(id, active = false) {
    const tab = this.add(new Element(`tab-btn-${id}`, ['tab'].concat(active ? ['active'] : []), { tab: id }));
    const panel = this.add(new Element(`tab-${id}`, ['tab-content']));
    panel.style.display = active ? 'block' : 'none';
    this.tabs.push(tab);
    this.panels.push(panel);
    return { tab, panel };
  }
  getElementById(id) {
    return this.elements.get(id) || null;
  }
  querySelector(selector) {
    if (selector.startsWith('.tab[data-tab="')) {
      const id = selector.match(/data-tab="([^"]+)"/)[1];
      return this.tabs.find(tab => tab.dataset.tab === id) || null;
    }
    if (selector.includes('.tab.active')) {
      return this.tabs.find(tab => tab.classList.contains('active')) || null;
    }
    if (selector.startsWith('input[data-pg-alias="')) {
      const id = selector.match(/data-pg-alias="([^"]+)"/)[1];
      return Array.from(this.elements.values()).find(el => el.dataset.pgAlias === id) || null;
    }
    return this.querySelectorAll(selector)[0] || null;
  }
  querySelectorAll(selector) {
    if (selector === '.tab') return this.tabs;
    if (selector === '.tab-content') return this.panels;
    if (selector === '.subtab') {
      return Array.from(this.elements.values()).filter(el => el.classList.contains('subtab'));
    }
    if (selector === '.subtab-content') {
      return Array.from(this.elements.values()).filter(el => el.classList.contains('subtab-content'));
    }
    if (selector === '[data-home-tab]') {
      return Array.from(this.elements.values()).filter(el => el.dataset.homeTab);
    }
    if (selector.startsWith('[data-filter-type]')) {
      return Array.from(this.elements.values()).filter(el => el.dataset.filterType);
    }
    if (selector === 'input[type="checkbox"][data-check]') {
      return Array.from(this.elements.values()).filter(el => el.tagName === 'input' && el.type === 'checkbox' && el.dataset.check);
    }
    if (selector === 'button[data-checklist-clear]') {
      return Array.from(this.elements.values()).filter(el => el.tagName === 'button' && el.dataset.checklistClear);
    }
    const checkPrefix = selector.match(/^input\[type="checkbox"\]\[data-check\^="([^"]+)"\]$/);
    if (checkPrefix) {
      return Array.from(this.elements.values()).filter(el => el.tagName === 'input' && el.type === 'checkbox' && (el.dataset.check || '').startsWith(checkPrefix[1]));
    }
    return [];
  }
}

function loadModule(context, relativePath) {
  const fullPath = path.join(repoRoot, relativePath);
  const code = fs.readFileSync(fullPath, 'utf8');
  vm.runInContext(code, context, { filename: fullPath });
}

function createSandbox() {
  const document = new FakeDocument();
  const store = new Map();
  const sandbox = {
    console,
    document,
    localStorage: {
      getItem: key => store.has(key) ? store.get(key) : null,
      setItem: (key, value) => store.set(key, String(value)),
      removeItem: key => store.delete(key),
    },
    SQX_CONFIG: { storageKeys: {} },
    SQX: {
      modules: {},
      registerModule(name, module) {
        this.modules[name] = module;
      },
      utils: {
        safeJsonParse(raw, fallback) {
          try { return JSON.parse(raw); } catch (_err) { return fallback; }
        }
      }
    }
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  return sandbox;
}

function createLoadedSandbox(modules = [
  'app/js/modules/formatters.js',
  'app/js/modules/domain.js',
  'app/js/modules/storage.js',
  'app/js/modules/ui.js',
  'app/js/modules/strategies.js',
  'app/js/modules/home.js',
  'app/js/modules/workflow.js',
  'app/js/modules/project-generator-core.js',
  'app/js/modules/project-generator-config.js',
  'app/js/modules/project-generator-renderers.js',
  'app/js/modules/project-generator-status.js',
  'app/js/modules/project-generator-cleaner.js',
  'app/js/modules/project-generator.js',
]) {
  const sandbox = createSandbox();
  const context = vm.createContext(sandbox);
  modules.forEach(file => loadModule(context, file));
  return { sandbox, context, SQX: sandbox.SQX, document: sandbox.document };
}

export { assert, Element, createLoadedSandbox, repoRoot };
