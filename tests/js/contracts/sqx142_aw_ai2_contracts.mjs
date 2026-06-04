import { assert } from './harness.mjs';
import fs from 'fs';
import path from 'path';

const repoRoot = process.cwd();
const overlayJs = fs.readFileSync(path.join(repoRoot, 'integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js'), 'utf8');
const overlayCss = fs.readFileSync(path.join(repoRoot, 'integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.css'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx142_ai_wizard.py'), 'utf8');
const doc = fs.existsSync(path.join(repoRoot, 'docs/SQX142_AW_AI2_AI_STUDIO.md'))
  ? fs.readFileSync(path.join(repoRoot, 'docs/SQX142_AW_AI2_AI_STUDIO.md'), 'utf8')
  : '';

assert.match(core, /AI_WIZARD_AI2_VERSION = "sqx142-ai-wizard-studio-v2"/);
assert.match(core, /CATALOG_TYPE = "sqx-edge\.ai-wizard-capability-catalog-v1"/);
assert.match(core, /AST_TYPE = "sqx-edge\.ai-wizard-strategy-ast-v1"/);
assert.match(core, /SESSION_DB_RELATIVE = Path\("\.local"\) \/ "sqx142_ai_wizard" \/ "ai_wizard\.sqlite"/);
assert.match(core, /blocked_not_draftable_yet/);
assert.match(core, /raw_xml_returned/);
assert.match(core, /raw_prompt_persisted/);
assert.match(core, /resolve_ai_wizard_draft_download/);

[
  '/api/sqx142/ai-wizard/catalog',
  '/api/sqx142/ai-wizard/catalog/refresh',
  '/api/sqx142/ai-wizard/sessions',
  '/api/sqx142/ai-wizard/sessions/<session_id>',
  '/api/sqx142/ai-wizard/sessions/<session_id>/messages',
  '/api/sqx142/ai-wizard/sessions/<session_id>/spec',
  '/api/sqx142/ai-wizard/sessions/<session_id>/drafts',
  '/api/sqx142/ai-wizard/drafts/<draft_id>/download',
].forEach((route) => assert.match(server, new RegExp(route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace('<session_id>', '<session_id>').replace('<draft_id>', '<draft_id>'))));
assert.match(server, /_require_sqx142_local_operator\(AI_WIZARD_AI2_VERSION\)/);
assert.match(server, /client_path_fields_blocked/);
assert.match(server, /raw_catalog_request_blocked/);

assert.match(overlayJs, /sqx142-ai-wizard-overlay-v2/);
assert.match(overlayJs, /sqx-edge-aiwizard-sessions/);
assert.match(overlayJs, /sqx-edge-aiwizard-catalog/);
assert.match(overlayJs, /sqx-edge-aiwizard-params/);
assert.match(overlayJs, /sqx-edge-aiwizard-fork/);
assert.match(overlayJs, /function apiUrl\(path\)/);
assert.match(overlayJs, /function blockerLabel\(code\)/);
assert.match(overlayJs, /raw\.indexOf\("\/api\/"\) === 0/);
assert.match(overlayJs, /data-sqx-aiwizard-download/);
assert.match(overlayJs, /Crear bot SQX/);
assert.match(overlayJs, /Idea del bot/);
assert.match(overlayJs, /Crear plan/);
assert.match(overlayJs, /Generar \.sqx/);
assert.match(overlayJs, /Duplicar/);
assert.match(overlayJs, /Modo guiado/);
assert.match(overlayJs, /data-sqx-aiwizard-session-id/);
assert.match(overlayJs, /data-sqx-aiwizard-archetype/);
assert.match(overlayJs, /data-sqx-aiwizard-param/);
assert.match(overlayJs, /session_store_unavailable|session_not_found/);
assert.match(overlayJs, /param_invalid/);
assert.match(overlayJs, /Provider directo desde navegador: blocked/);
assert.match(overlayJs, /Runtime SQX launch: blocked/);
assert.doesNotMatch(overlayJs, /localStorage|sessionStorage|indexedDB|document\.cookie/i);
assert.doesNotMatch(overlayJs, /api\.openai\.com|OPENAI_API_KEY|Authorization|Bearer|token=/i);
assert.doesNotMatch(overlayJs, /127\.0\.0\.1:11434|localhost:11434|ollama\/api/i);
assert.doesNotMatch(overlayJs, /API_BASE \+ draft\.downloadUrl/);

assert.match(overlayCss, /\.sqx-edge-aiwizard-session-list/);
assert.match(overlayCss, /\.sqx-edge-aiwizard-catalog/);
assert.match(overlayCss, /\.sqx-edge-aiwizard-param-grid/);
assert.match(overlayCss, /\.sqx-edge-aiwizard-prompt-label/);
assert.match(overlayCss, /\.sqx-edge-aiwizard-primary/);

if (doc) {
  assert.match(doc, /SQX142-AW-AI2/);
  assert.match(doc, /sqx-edge\.ai-wizard-capability-catalog-v1/);
  assert.match(doc, /sqx-edge\.ai-wizard-strategy-ast-v1/);
  assert.match(doc, /blocked_not_draftable_yet/);
}

console.log('sqx142 aw ai2 contracts ok');
