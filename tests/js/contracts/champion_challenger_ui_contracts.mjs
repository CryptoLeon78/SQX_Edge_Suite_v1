import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document } = createLoadedSandbox([
  'app/js/modules/formatters.js',
  'app/js/modules/ui.js',
  'app/js/modules/champion-challenger-core.js',
  'app/js/modules/champion-challenger.js',
]);

[
  'cvc-champion-input',
  'cvc-challenger-input',
  'cvc-oos-input',
  'cvc-run-btn',
  'cvc-sample-btn',
  'cvc-clear-btn',
  'cvc-status',
  'cvc-summary',
  'cvc-ranking',
  'cvc-empty',
  'cvc-oos-summary',
  'cvc-candidate-count',
  'cvc-ready-count',
  'cvc-oos-ready-count',
].forEach(id => document.add(new Element(id)));

const cvc = SQX.championChallenger;
assert.ok(cvc, 'champion challenger UI module should register');
assert.equal(cvc.init({ document }), true);

document.getElementById('cvc-sample-btn').click();
assert.equal(document.getElementById('cvc-candidate-count').textContent, '3');
assert.equal(document.getElementById('cvc-ready-count').textContent, '1');
assert.equal(document.getElementById('cvc-oos-ready-count').textContent, '1');
assert.match(document.getElementById('cvc-status').textContent, /Comparacion lista/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Challenger A/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /OOS 100% positivo/);

document.getElementById('cvc-champion-input').value = [
  'Strategy Name,Symbol,Profit factor,Return/Drawdown,# trades',
  'Champion,EURUSD,1.50,4.00,200',
].join('\n');
document.getElementById('cvc-challenger-input').value = [
  'Strategy Name,Symbol,Profit factor,Return/Drawdown,# trades,Filters Result',
  '<script>alert(1)</script>,EURUSD,1.80,4.20,220,PASSED',
].join('\n');
document.getElementById('cvc-oos-input').value = '';

const model = cvc.evaluate({ document });
assert.equal(model.ok, true);
assert.equal(model.rankings.length, 1);
assert.match(document.getElementById('cvc-ranking').innerHTML, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
assert.doesNotMatch(document.getElementById('cvc-ranking').innerHTML, /<script>/);

document.getElementById('cvc-clear-btn').click();
assert.equal(document.getElementById('cvc-champion-input').value, '');
assert.equal(document.getElementById('cvc-ranking').innerHTML, '');
assert.equal(document.getElementById('cvc-candidate-count').textContent, '0');

document.getElementById('cvc-run-btn').click();
assert.match(document.getElementById('cvc-status').textContent, /Revisa los datos/);

console.log('champion challenger UI contracts ok');
