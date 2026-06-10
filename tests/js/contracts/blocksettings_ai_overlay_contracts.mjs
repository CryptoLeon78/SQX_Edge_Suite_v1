import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const overlayRoot = path.join(repoRoot, 'integrations/sqx144/blocksettings_ai_overlay');
const js = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-bsai.js'), 'utf8');
const css = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-bsai.css'), 'utf8');
const wrapper = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_blocksettings_ai_overlay.ps1'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');

assert.ok(js.includes('sqx144-blocksettings-ai-overlay-v1'), 'overlay should expose SQX144 BSAI version');
assert.ok(js.includes('/blocksettings/ai/sessions'), 'overlay should create BSAI sessions through Flask');
assert.ok(js.includes('/save-candidate'), 'overlay should save candidate through Flask');
assert.ok(js.includes('/generate-project'), 'overlay should generate projects through Flask');
assert.ok(js.includes('safeApiBase'), 'overlay should restrict API base handling');
assert.ok(js.includes('127.0.0.1') && js.includes('localhost'), 'overlay should stay local API oriented');
assert.ok(!js.includes('11434'), 'overlay must not call Ollama directly');
assert.ok(!js.includes('data.db'), 'overlay must not reference data.db');
assert.ok(!js.includes('user/projects'), 'overlay must not write user/projects');
assert.ok(css.includes('.sqx-edge-bsai-panel'), 'overlay CSS should style the panel');

assert.ok(wrapper.includes("[ValidateSet('status', 'plan', 'install', 'rollback')]"), 'wrapper should expose guarded actions');
assert.ok(wrapper.includes('$Apply'), 'wrapper should be dry-run-first');
assert.ok(wrapper.includes('sqx_process_running'), 'wrapper should block install while SQX is running');
assert.ok(wrapper.includes('New-Backup'), 'wrapper should create a backup before install');
assert.ok(wrapper.includes('writesDataDb = $false'), 'wrapper plan should state no data.db writes');
assert.ok(wrapper.includes('writesUserProjects = $false'), 'wrapper plan should state no user/projects writes');
assert.ok(wrapper.includes('runsSqxTasks = $false'), 'wrapper plan should state no SQX tasks');

assert.ok(server.includes('/api/blocksettings/ai/catalog'), 'server should expose BSAI catalog endpoint');
assert.ok(server.includes('/api/blocksettings/ai/sessions/<session_id>/generate-project'), 'server should expose BSAI project generation endpoint');
assert.ok(server.includes('BS_AI_VERSION'), 'server should tag BSAI responses with version');

console.log('blocksettings ai overlay contracts ok');
