import fs from 'node:fs';
import path from 'node:path';
import { assert, Element, createLoadedSandbox, repoRoot } from './harness.mjs';

const { SQX, sandbox, document } = createLoadedSandbox([
  'app/js/modules/ui.js',
  'app/js/modules/edge-factory.js',
  'app/js/modules/edge-factory-ui.js',
  'app/js/modules/agent-guide.js',
]);

sandbox.addEventListener = () => {};
sandbox.dispatchEvent = () => {};
sandbox.CustomEvent = function CustomEvent(name, options) {
  return { name, detail: options && options.detail };
};

document.add(new Element('agent-guide-dock'));
document.add(new Element('agent-guide-status'));
document.add(new Element('agent-guide-model'));
document.add(new Element('agent-guide-output'));
document.add(new Element('agent-guide-input'));
document.add(new Element('agent-guide-ask'));
document.add(new Element('agent-guide-confirm'));
document.add(new Element('agent-guide-cancel'));
document.add(new Element('agent-guide-refresh'));
document.add(new Element('home-agent-status'));
document.add(new Element('home-agent-model'));
document.add(new Element('home-agent-last-action'));
document.addTab('workflow', true);
document.addTab('projectgen', false);

const calls = [];
sandbox.fetch = (url, options = {}) => {
  calls.push({ url, options });
  if (url.endsWith('/agent/status')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        ok: true,
        active: true,
        provider: { available: true, model: 'qwen3.5:latest' },
        sqx142Performance: {
          visible: true,
          status: 'warn',
          activeProfile: { id: 'baseline_143_safe' },
        },
        privacy: { prompt_persisted: false },
      }),
    });
  }
  if (url.endsWith('/agent/plan')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        ok: true,
        reply: 'Abre Project Generator con confirmacion.',
        profile: 'capa1-generate',
        recommendedAction: {
          id: 'open_stage_tool:capa1-generate',
          label: 'Abrir herramienta de Generar Capa 1',
          arguments: { type: 'open_tool', tool: 'projectgen', stage: 'capa1-generate' },
        },
        requiresConfirmation: true,
        blockers: [],
      }),
    });
  }
  if (url.endsWith('/agent/confirm')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        ok: true,
        confirmation: { token: 'confirm-1', actionId: 'open_stage_tool:capa1-generate' },
      }),
    });
  }
  if (url.endsWith('/agent/execute')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        ok: true,
        uiCommand: { type: 'open_tool', tool: 'projectgen' },
        action: { id: 'open_stage_tool:capa1-generate', risk: 'navigate' },
      }),
    });
  }
  throw new Error(`unexpected fetch ${url}`);
};

sandbox.SQX_CONFIG.apiBase = () => 'https://sqx.example.invalid/api';
sandbox.SQX_CONFIG.storageKeys = { edgeFactoryState: 'sqx_edge_factory_state_v1' };

assert.equal(SQX.agentGuide.version, 'local-ai-agent-ui-v1');
assert.equal(typeof SQX.agentGuide.init, 'function');
assert.equal(SQX.agentGuide.init(), true);

await SQX.agentGuide.loadStatus();
assert.equal(document.getElementById('agent-guide-status').textContent, 'Ollama local activo');
assert.equal(document.getElementById('home-agent-model').textContent.includes('qwen3.5:latest'), true);
assert.equal(document.getElementById('home-agent-model').textContent.includes('Perf baseline_143_safe'), true);

SQX.edgeFactory.setActiveStep('capa1-generate');
document.getElementById('agent-guide-input').value = 'abre el siguiente paso';
await SQX.agentGuide.requestPlan();
assert.equal(document.getElementById('agent-guide-confirm').disabled, false);
assert.equal(document.getElementById('agent-guide-output').innerHTML.includes('Project Generator'), true);

await SQX.agentGuide.executeCurrentPlan();
assert.equal(document.getElementById('tab-projectgen').style.display, 'block');
assert.equal(document.getElementById('home-agent-last-action').textContent.includes('Abrir herramienta'), true);
assert.equal(sandbox.localStorage.getItem('sqx_agent_history_v1'), null);
assert.equal(calls.some(call => call.url === 'https://sqx.example.invalid/api/agent/confirm'), true);

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const indexJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/index.js'), 'utf8');
assert.equal(html.includes('id="agent-guide-dock"'), true);
assert.equal(html.includes('js/modules/agent-guide.js'), true);
assert.equal(html.includes('data-tab="agent"'), false);
assert.equal(indexJs.includes('agent-guide'), true);

console.log('agent guide contracts ok');
