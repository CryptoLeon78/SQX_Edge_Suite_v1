import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

const source = fs.readFileSync(
  path.join(repoRoot, 'integrations/sqx144/datamanager_mt5_auto2_overlay/sqx-edge-mt5-auto2.js'),
  'utf8',
);

function visibleNode(text, controls = []) {
  return {
    textContent: text,
    offsetWidth: 100,
    offsetHeight: 20,
    className: '',
    innerHTML: '',
    value: '',
    selectedOptions: [],
    parentNode: null,
    parentElement: null,
    getClientRects: () => [{}],
    querySelectorAll(selector) {
      if (selector === 'input') return controls.filter((control) => control.kind === 'input');
      if (selector === 'select') return controls.filter((control) => control.kind === 'select');
      return [];
    },
    contains: () => false,
    addEventListener: () => {},
    appendChild: () => {},
  };
}

function input(value) {
  return { kind: 'input', value, selectedOptions: [] };
}

function select(value) {
  return {
    kind: 'select',
    value,
    selectedOptions: [{ textContent: value, value }],
  };
}

const checkedRow = visibleNode('DAX40_dukascopy GDAXI_darwinex');
const checkedInput = {
  kind: 'input',
  type: 'checkbox',
  checked: true,
  value: '',
  selectedOptions: [],
  parentNode: checkedRow,
  parentElement: checkedRow,
  closest: () => checkedRow,
  getBoundingClientRect: () => ({ top: 10, height: 20 }),
};

const modal = visibleNode('Edit symbol Data symbol name Choose instrument', [
  input('DAX40_dukascopy'),
  select('GDAXI_darwinex'),
]);
const panel = visibleNode('');
const body = visibleNode('');
const close = visibleNode('');
const refresh = visibleNode('');
const ids = new Map([
  ['sqx-edge-mt5-auto2-panel', panel],
  ['sqx-edge-mt5-auto2-body', body],
  ['sqx-edge-mt5-auto2-close', close],
  ['sqx-edge-mt5-auto2-refresh', refresh],
]);

const document = {
  readyState: 'loading',
  body: visibleNode('body'),
  getElementById: (id) => ids.get(id) || null,
  addEventListener: () => {},
  createElement: () => visibleNode('created'),
  querySelectorAll(selector) {
    if (selector === "input[type='checkbox']:checked") return [checkedInput];
    if (selector.includes("[role='dialog']") || selector.includes('.modal') || selector.endsWith(', div')) return [modal];
    if (selector.includes('rowselected') || selector.includes('selected')) return [visibleNode('AUDCAD_darwinex stale row')];
    if (selector === 'input, select') return [input('WARRANTY')];
    return [];
  },
};

const calls = [];
const window = {
  document,
  setInterval: () => 0,
  setTimeout: () => 0,
  getComputedStyle: () => ({ display: 'block', visibility: 'visible', opacity: '1' }),
  fetch: async (url, options = {}) => {
    calls.push({ url: String(url), options });
    return {
      ok: true,
      status: 200,
      json: async () => ({
        ok: true,
        status: 'plan_ready_noop_data_symbol_uses_darwinex_instrument',
        dataSymbol: 'DAX40_dukascopy',
        linkedInstrument: 'GDAXI_darwinex',
        changes: {},
        noops: { DEFAULTSPREAD: 14, POINTVALUE: 11.66292, TICKSIZE: 0.1, TICKSTEP: 0.1 },
      }),
    };
  },
};
window.window = window;
window.URL = URL;

vm.runInNewContext(source, window, { filename: 'sqx-edge-mt5-auto2.js' });

const api = window.SQXEdgeMt5Auto2;
assert.equal(api.detectDukascopyDataSymbol(), 'DAX40_dukascopy', 'data symbol input must beat linked instrument dropdown');
assert.equal(api.detectEditDialogSymbol(), 'DAX40_dukascopy', 'edit dialog must route the actual data symbol');
assert.equal(api.detectLinkedInstrument(), 'GDAXI_Darwinex', 'linked instrument should be passed separately');

api.requestBridge(api.detectEditDialogSymbol());
for (let i = 0; i < 6; i += 1) await Promise.resolve();

assert.equal(calls.length, 1, 'dukascopy data symbols must make a single AUTO7 call');
assert.ok(calls[0].url.endsWith('/api/sqx144/mt5-auto7/plan'), 'DAX40_dukascopy must route to AUTO7 plan');
assert.ok(!calls[0].url.includes('/mt5-auto2/request'), 'DAX40_dukascopy must not write an MT5 request');
assert.ok(!calls[0].url.includes('/mt5-auto3/bridge-validate'), 'DAX40_dukascopy must not poll bridge validate');
assert.ok(!calls[0].url.includes('/mt5-auto6/evaluate'), 'DAX40_dukascopy must not evaluate live MT5 stability');

let bodyJson = JSON.parse(calls[0].options.body);
assert.equal(bodyJson.symbol, 'DAX40_dukascopy');
assert.equal(bodyJson.linkedInstrument, 'GDAXI_Darwinex');

checkedRow.textContent = 'AUDCAD_dukascopy AUDCAD_darwinex';
api.requestBridge('AUDCAD_dukascopy');
for (let i = 0; i < 6; i += 1) await Promise.resolve();

bodyJson = JSON.parse(calls.at(-1).options.body);
assert.equal(bodyJson.symbol, 'AUDCAD_dukascopy', 'checked row must drive the first follow-up request');

checkedRow.textContent = 'EURCAD_dukascopy EURCAD_darwinex';
api.requestBridge('EURCAD_dukascopy');
for (let i = 0; i < 6; i += 1) await Promise.resolve();

bodyJson = JSON.parse(calls.at(-1).options.body);
assert.equal(bodyJson.symbol, 'EURCAD_dukascopy', 'second dukascopy request must not reuse stale AUDCAD state');

console.log('sqx144 mt5 auto7 datamanager routing behavior ok');
