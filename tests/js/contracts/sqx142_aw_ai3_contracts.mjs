import { assert } from './harness.mjs';
import fs from 'fs';
import path from 'path';

const repoRoot = process.cwd();
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx142_ai_wizard.py'), 'utf8');
const studioTest = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_sqx142_ai_wizard_studio.py'), 'utf8');
const overlayJs = fs.readFileSync(path.join(repoRoot, 'integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js'), 'utf8');
const doc = fs.existsSync(path.join(repoRoot, 'docs/SQX142_AW_AI3_UNIVERSAL_PROMPT_COMPILER.md'))
  ? fs.readFileSync(path.join(repoRoot, 'docs/SQX142_AW_AI3_UNIVERSAL_PROMPT_COMPILER.md'), 'utf8')
  : '';

assert.match(core, /AI_WIZARD_AI3_COMPILER_VERSION = "sqx142-aw-ai3-universal-prompt-compiler-v1"/);
assert.match(core, /AI_WIZARD_AI3_CATALOG_VERSION = "sqx142-aw-ai3-expanded-catalog-v1"/);
assert.match(core, /AI_WIZARD_AI4_RSI_COMPILER_VERSION = "sqx142-aw-ai4-rsi-mean-reversion-compiler-v1"/);
assert.match(core, /AI_WIZARD_INTERPRETER_SCHEMA/);
assert.match(core, /_try_local_model_interpretation/);
assert.match(core, /_build_semantic_catalog/);
assert.match(core, /_collect_xml_item_keys/);
assert.match(core, /OllamaClient\(OllamaConfig/);
assert.match(core, /auto_start=False/);
assert.match(core, /rawPromptPersisted": False/);
assert.match(core, /rawResponsePersisted": False/);
assert.match(core, /externalApiCalled": False/);
assert.match(core, /universalPromptIntake": True/);
assert.match(core, /universalSqxGeneration": False/);

assert.match(core, /"candle_atr_sequence"/);
assert.match(core, /"rsi_mean_reversion"/);
assert.match(core, /_patch_rsi_mean_reversion_strategy_xml/);
assert.match(core, /blocked_multi_family_compiler_not_ready/);
assert.match(core, /semanticFamilies/);
assert.match(core, /"expanded_planning_catalog_not_universal_sqx_generation"/);
assert.match(core, /"semanticCatalog": semantic_catalog/);
assert.match(core, /"semanticIds"/);
assert.match(core, /unknown_semantic_item/);
assert.match(core, /mentioned_categories/);
assert.match(core, /file_size <= 2_000_000/);
assert.match(core, /generate_ai_wizard_draft_from_ast/);
assert.match(core, /_patch_candle_atr_strategy_xml/);
assert.match(core, /_copy_sqx_with_patched_xml/);
assert.match(core, /"zip_entries_preserved"/);
assert.match(core, /"no_sqx_user_projects_write"/);
assert.match(core, /"no_data_db_write"/);
assert.match(core, /"no_runtime_launch"/);
assert.match(core, /"manual_algowizard_review_required"/);
assert.match(core, /"key": "talib_ATR"/);
assert.match(core, /_xml_price_value\("Close", shift\)/);
assert.match(core, /_xml_price_value\("Open", shift\)/);

assert.match(studioTest, /test_ai3_spanish_candle_prompt_compiles_traceable_draft/);
assert.match(studioTest, /test_ai4_rsi_mean_reversion_compiles_long_short_and_both/);
assert.match(studioTest, /test_ai3_expanded_catalog_understands_condition_items_without_draft/);
assert.match(studioTest, /test_ai3_local_model_interpreter_feeds_ast_without_persisting_raw/);
assert.match(studioTest, /create_ai_wizard_session_draft/);
assert.match(studioTest, /blocked_not_draftable_yet/);
assert.match(studioTest, /SQX Edge AI3 Universal Prompt Compiler draft/);
assert.match(studioTest, /fake-local-model/);

assert.match(overlayJs, /Catalogo AlgoWizard ampliado/);
assert.match(overlayJs, /semanticCatalog/);
assert.match(overlayJs, /draftableFamilies/);
assert.match(overlayJs, /Generable ahora/);
assert.match(overlayJs, /RSI mean reversion/);
assert.match(overlayJs, /items semanticos/);
assert.match(overlayJs, /features de ejemplos/);
assert.match(overlayJs, /familias probadas/);
assert.match(overlayJs, /promptSeed/);
assert.match(overlayJs, /data-sqx-aiwizard-prompt/);
assert.doesNotMatch(overlayJs, /127\.0\.0\.1:11434|localhost:11434|ollama\/api/i);
assert.doesNotMatch(overlayJs, /OPENAI_API_KEY|Authorization|Bearer|token=/i);

if (doc) {
  assert.match(doc, /SQX142-AW-AI3 Universal Prompt Compiler/);
  assert.match(doc, /sqx142-aw-ai3-universal-prompt-compiler-v1/);
  assert.match(doc, /universal_prompt_intake_not_universal_sqx_generation/);
  assert.match(doc, /allowlisted_catalog_only/);
  assert.match(doc, /sqx142-aw-ai3-expanded-catalog-v1/);
  assert.match(doc, /candle_atr_sequence/);
  assert.match(doc, /raw_prompt_persisted=false/);
  assert.match(doc, /raw_provider_response_persisted=false/);
  assert.match(doc, /no provider calls from browser/);
}

console.log('sqx142 aw ai3 contracts ok');
