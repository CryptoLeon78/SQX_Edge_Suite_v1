import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document } = createLoadedSandbox([
  'app/js/modules/storage.js',
  'app/js/modules/ui.js',
]);

assert.equal(SQX.modules.storage, SQX.storage);
assert.equal(SQX.modules.ui, SQX.ui);

assert.equal(SQX.storage.key('missing', 'fallback-key'), 'fallback-key');
assert.equal(SQX.storage.setJson('k', { a: 1 }), true);
assert.deepEqual(SQX.storage.getJson('k', {}), { a: 1 });
assert.deepEqual(SQX.storage.getJson('missing', { fallback: true }), { fallback: true });
assert.equal(SQX.storage.remove('k'), true);
assert.deepEqual(SQX.storage.getJson('k', { gone: true }), { gone: true });

const node = document.add(new Element('node'));
SQX.ui.setText(node, 123);
assert.equal(node.textContent, '123');
SQX.ui.hide(node);
assert.equal(node.style.display, 'none');
SQX.ui.show(node, 'grid');
assert.equal(node.style.display, 'grid');
assert.equal(SQX.ui.byId('node'), node);
assert.equal(SQX.ui.all('.tab').length, 0);

let clickCount = 0;
let changeCount = 0;
let inputCount = 0;
assert.equal(SQX.ui.bindClick('node', () => { clickCount += 1; }), true);
assert.equal(SQX.ui.bindChange(node, () => { changeCount += 1; }), true);
assert.equal(SQX.ui.bindInput(node, () => { inputCount += 1; }), true);
node.click();
node.dispatch('change');
node.dispatch('input');
assert.equal(clickCount, 1);
assert.equal(changeCount, 1);
assert.equal(inputCount, 1);
assert.equal(SQX.ui.bindClick('missing', () => {}), false);

document.addTab('inicio', true);
document.addTab('workflow', false);
assert.equal(SQX.ui.activateTabById('workflow', document), true);
assert.equal(document.getElementById('tab-workflow').style.display, 'block');
assert.equal(document.getElementById('tab-inicio').style.display, 'none');
const hiddenToolPanel = document.add(new Element('tab-projectgen', ['tab-content']));
document.panels.push(hiddenToolPanel);
SQX.edgeFactory = { getState: () => ({ experienceMode: 'advanced' }) };
assert.equal(SQX.ui.activateTabById('projectgen', document), true);
assert.equal(hiddenToolPanel.style.display, 'block');
assert.equal(document.querySelector('.tab[data-tab="projectgen"]'), null);
assert.equal(SQX.ui.activateTabById('missing', document), false);

const homeBtn = document.add(new Element('home-shortcut', [], { homeTab: 'inicio' }));
let homeTarget = '';
SQX.ui.bindHomeTabButtons('[data-home-tab]', tab => { homeTarget = tab; }, document);
homeBtn.click();
assert.equal(homeTarget, 'inicio');

console.log('storage ui contracts ok');
