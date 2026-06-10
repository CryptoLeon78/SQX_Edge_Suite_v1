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
    getClientRects: () => [{}],
    querySelectorAll(selector) {
      if (selector === 'input') return controls.filter((control) => control.kind === 'input');
      if (selector === 'select') return controls.filter((control) => control.kind === 'select');
      return [];
    },
    contains: () => false,
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

const modal = visibleNode('Edit symbol Data symbol name Choose instrument', [
  input('EURGBP_darwinex'),
  select('EURGBP_darwinex'),
]);
const staleRow = visibleNode('DAX40_darwinex GDAXI_darwinex');

const document = {
  readyState: 'loading',
  body: visibleNode('body'),
  getElementById: () => null,
  addEventListener: () => {},
  createElement: () => visibleNode('created'),
  querySelectorAll(selector) {
    if (selector.includes("[role='dialog']") || selector.includes('.modal') || selector.endsWith(', div')) return [modal];
    if (selector.includes('rowselected') || selector.includes('selected')) return [staleRow];
    if (selector === 'input, select') return [input('WARRANTY')];
    return [];
  },
};

const window = {
  document,
  setInterval: () => 0,
  setTimeout: () => 0,
  getComputedStyle: () => ({ display: 'block', visibility: 'visible', opacity: '1' }),
};
window.window = window;
window.URL = URL;

vm.runInNewContext(source, window, { filename: 'sqx-edge-mt5-auto2.js' });

const api = window.SQXEdgeMt5Auto2;

assert.equal(api.isAllowedBareSymbol('WARRANTY'), false, 'WARRANTY must not be accepted as a bare symbol');
assert.equal(api.isAllowedBareSymbol('DAX40'), true, 'DAX40 must remain accepted as an explicit index token');
assert.equal(api.symbolFromSelectionItem({ name: 'WARRANTY' }), '', 'raw item.name WARRANTY must be rejected');
assert.equal(api.symbolFromSelectionItem({ name: 'EURGBP_darwinex' }), 'EURGBP_Darwinex', 'validated item.name can still supply a real symbol');
assert.equal(api.detectEditDialogSymbol(), 'EURGBP_Darwinex', 'edit modal symbol must be detected');
assert.equal(api.detectSymbol({ allowLast: false }), 'EURGBP_Darwinex', 'edit modal must beat stale selected grid rows');

console.log('sqx144 mt5 auto6 selection guard behavior ok');
