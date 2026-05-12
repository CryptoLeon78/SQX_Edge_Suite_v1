import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const dashboardUrl = 'file:///' + path.join(repoRoot, 'app', 'SQX_Dashboard_v6.html').replace(/\\/g, '/');
const screenshotsEnabled = process.env.SQX_E2E_SCREENSHOTS === '1';
const screenshotDir = path.join(repoRoot, 'output', 'playwright');

async function assertNoMobileOverflow(page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 8);
  if (overflow) throw new Error('Mobile viewport has horizontal overflow');
}

function collectBrowserErrors(page, bucket) {
  page.on('pageerror', error => bucket.push(`pageerror: ${error.message}`));
  page.on('console', message => {
    if (message.type() !== 'error') return;
    const text = message.text();
    if (text.includes('net::ERR_CONNECTION_REFUSED')) return;
    if (text.includes('Failed to load resource: the server responded with a status of 404')) return;
    bucket.push(`console error: ${text}`);
  });
}

function assertNoBrowserErrors(bucket, label) {
  if (bucket.length) throw new Error(`${label} browser errors:\n${bucket.join('\n')}`);
}

async function saveShot(page, name) {
  if (!screenshotsEnabled) return;
  await mkdir(screenshotDir, { recursive: true });
  await page.screenshot({ path: path.join(screenshotDir, name), fullPage: true });
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const desktopErrors = [];
    collectBrowserErrors(desktop, desktopErrors);
    desktop.on('dialog', dialog => dialog.accept());
    await desktop.goto(dashboardUrl, { waitUntil: 'load' });
    await desktop.waitForSelector('.tab[data-tab="inicio"].active');
    await desktop.waitForSelector('#home-readiness-score');
    await desktop.locator('[data-home-tab="pipeline"]').first().click();
    await desktop.waitForSelector('.tab[data-tab="pipeline"].active');
    await desktop.locator('.tab[data-tab="activos"]').click();
    await desktop.waitForSelector('.tab[data-tab="activos"].active');
    await desktop.locator('[data-filter-type="forex"]').click();
    await desktop.waitForSelector('[data-filter-type="forex"].active');
    await desktop.fill('#search-asset', 'EUR');
    await desktop.waitForSelector('#asset-grid .asset-card');
    await desktop.evaluate(() => navToAsset('EURUSD'));
    await desktop.waitForSelector('#detail-panel.visible');
    await desktop.locator('.tab[data-tab="workflow"]').click();
    await desktop.waitForSelector('.tab[data-tab="workflow"].active');
    await desktop.evaluate(() => localStorage.removeItem('sqx_workflow_checklist_v1'));
    await desktop.locator('.subtab[data-subtab="wf-capa1"]').click();
    await desktop.waitForSelector('#wf-capa1.active');
    await desktop.locator('input[data-check="capa1-pre-mm"]').check();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_workflow_checklist_v1') || '{}')['capa1-pre-mm'] === true);
    await desktop.locator('button[data-checklist-clear="capa1"]').click();
    await desktop.waitForFunction(() => !JSON.parse(localStorage.getItem('sqx_workflow_checklist_v1') || '{}')['capa1-pre-mm']);
    const workflowChecked = await desktop.locator('input[data-check="capa1-pre-mm"]').isChecked();
    if (workflowChecked) throw new Error('Workflow checklist clear should uncheck capa1 items');
    await saveShot(desktop, 'e2e-workflow-desktop.png');
    await desktop.locator('.subtab[data-subtab="wf-overview"]').click();
    await desktop.waitForSelector('#wf-overview.active');
    await saveShot(desktop, 'e2e-workflow-handoff-desktop.png');
    await desktop.locator('#workflow-views-handoff [data-vc-handoff="robustness"]').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX Robustez');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 104);
    await desktop.locator('.tab[data-tab="projectgen"]').click();
    await desktop.waitForSelector('.tab[data-tab="projectgen"].active');
    await desktop.waitForSelector('#pg-onboarding-title');
    await desktop.waitForFunction(() => document.getElementById('pg-onboarding-steps')?.querySelectorAll('.pg-step').length === 4);
    await desktop.waitForFunction(() => {
      const progress = document.getElementById('pg-onboarding-progress')?.textContent.trim() || '';
      const match = progress.match(/^([0-4])\/4$/);
      return Boolean(match);
    });
    await desktop.waitForSelector('#pg-custom-generate');
    await desktop.waitForSelector('#pg-custom-starter-list .pg-custom-starter-card');
    const customStarterCount = await desktop.locator('#pg-custom-starter-list .pg-custom-starter-card').count();
    if (customStarterCount < 8) throw new Error(`Expected richer Project Generator starter profiles, got ${customStarterCount}`);
    await desktop.waitForSelector('#pg-custom-family-list .pg-custom-family-card');
    const customFamilyCount = await desktop.locator('#pg-custom-family-list .pg-custom-family-card').count();
    if (customFamilyCount < 4) throw new Error(`Expected Project Generator profile families, got ${customFamilyCount}`);
    await desktop.locator('[data-pg-starter-load="forex-h1-balanced"]').click();
    await desktop.waitForFunction(() => document.getElementById('pg-custom-asset')?.value === 'EURUSD');
    await desktop.waitForFunction(() => document.getElementById('pg-custom-tf')?.value === 'H1');
    await desktop.locator('[data-pg-family-load="buyer-first-setup"]').click();
    await desktop.waitForFunction(() => document.getElementById('pg-custom-status')?.textContent.includes('Familia cargada'));
    await desktop.locator('[data-pg-family-save="buyer-first-setup"]').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').some(preset => preset.id === 'family-buyer-first-setup-forex-h1-balanced'));
    const familyPack = await desktop.evaluate(() => window.SQX.projectGenerator.buildCustomProfileFamilyPack('buyer-first-setup'));
    if (familyPack.type !== 'sqx-edge.project-generator-custom-presets' || familyPack.presets.length !== 3) throw new Error('Project Generator profile family pack contract failed');
    await desktop.evaluate(() => localStorage.removeItem('sqx_pg_custom_presets_v1'));
    await desktop.locator('[data-pg-starter-save="forex-h1-balanced"]').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').some(preset => preset.id === 'starter-forex-h1-balanced'));
    const starterPack = await desktop.evaluate(() => window.SQX.projectGenerator.buildCustomStarterProfilePack());
    if (starterPack.type !== 'sqx-edge.project-generator-custom-presets' || starterPack.presets.length < 8) throw new Error('Project Generator starter pack contract failed');
    await desktop.evaluate(() => localStorage.removeItem('sqx_pg_custom_presets_v1'));
    await desktop.locator('#pg-custom-asset').fill('EURUSD');
    await desktop.locator('#pg-custom-tf').fill('H1');
    await desktop.locator('#pg-custom-name').fill('Custom_EURUSD_H1');
    await desktop.locator('#pg-custom-capa').selectOption('1');
    await desktop.locator('#pg-custom-preset-name').fill('EURUSD H1 Smoke');
    await desktop.locator('#pg-custom-save-preset').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').length === 1);
    await desktop.locator('#pg-custom-asset').fill('GBPUSD');
    await desktop.locator('#pg-custom-load-preset').click();
    await desktop.waitForFunction(() => document.getElementById('pg-custom-asset')?.value === 'EURUSD');
    const customPresetPack = await desktop.evaluate(() => window.SQX.projectGenerator.buildCustomProjectPresetPackage());
    if (customPresetPack.type !== 'sqx-edge.project-generator-custom-presets' || customPresetPack.presets.length !== 1) throw new Error('Project Generator custom preset pack contract failed');
    await desktop.locator('#pg-custom-delete-preset').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').length === 0);
    await desktop.waitForFunction(() => document.getElementById('pg-custom-status')?.textContent.includes('Preset eliminado'));
    const customPackPath = path.join(screenshotDir, 'pg-custom-preset-pack-smoke.json');
    await mkdir(screenshotDir, { recursive: true });
    await writeFile(customPackPath, JSON.stringify(customPresetPack, null, 2), 'utf8');
    await desktop.locator('#pg-custom-import-presets-file').setInputFiles(customPackPath);
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').length === 1);
    await desktop.waitForFunction(() => document.getElementById('pg-custom-import-preview')?.classList.contains('has-items'));
    await desktop.waitForFunction(() => document.getElementById('pg-custom-import-preview')?.textContent.includes('Preview: 1 preset'));
    await desktop.locator('#pg-custom-load-preset').click();
    await desktop.waitForFunction(() => document.getElementById('pg-custom-asset')?.value === 'EURUSD');
    await saveShot(desktop, 'e2e-projectgen-desktop.png');
    await desktop.locator('.tab[data-tab="views"]').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForSelector('#vc-metric-list .views-metric-row');
    await desktop.locator('[data-vc-preset="egt-core"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '104');
    await desktop.locator('#vc-year-count').fill('5');
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '64');
    await desktop.locator('[data-vc-preset="risk"]').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await desktop.waitForSelector('#vc-template-list .views-template-card');
    const templateCount = await desktop.locator('#vc-template-list .views-template-card').count();
    if (templateCount < 4) throw new Error(`Expected buyer-ready SQX Views examples, got ${templateCount}`);
    await desktop.locator('[data-vc-template-load="risk-capital-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Risk Capital Review');
    await desktop.locator('[data-vc-template-save="risk-capital-review"]').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').some(preset => preset.id === 'buyer-risk-capital-review'));
    const buyerPack = await desktop.evaluate(() => window.SQX.viewCreator.buildBuyerReadyTemplatePack());
    if (buyerPack.type !== 'sqx-edge.view-presets' || buyerPack.presets.length < 4) throw new Error('SQX Views buyer-ready pack contract failed');
    await desktop.evaluate(() => localStorage.removeItem('sqx_view_creator_presets_v1'));
    await desktop.waitForSelector('#vc-profile-list .views-profile-card');
    const profilePackCount = await desktop.locator('#vc-profile-list .views-profile-card').count();
    if (profilePackCount < 4) throw new Error(`Expected SQX Views buyer profile packs, got ${profilePackCount}`);
    await desktop.locator('[data-vc-profile-load="pro-setup-assist"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'EGT First Review');
    await desktop.locator('[data-vc-profile-save="pro-setup-assist"]').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').some(preset => preset.id === 'profile-pro-setup-assist-risk-capital-review'));
    const profilePack = await desktop.evaluate(() => window.SQX.viewCreator.buildBuyerProfilePack('pro-setup-assist'));
    if (profilePack.type !== 'sqx-edge.view-presets' || profilePack.presets.length !== 3) throw new Error('SQX Views buyer profile pack contract failed');
    await desktop.waitForSelector('#vc-workflow-pack-list .views-workflow-card');
    const workflowPackCount = await desktop.locator('#vc-workflow-pack-list .views-workflow-card').count();
    if (workflowPackCount < 4) throw new Error(`Expected SQX Views workflow packs, got ${workflowPackCount}`);
    await desktop.locator('[data-vc-workflow-load="asset-family-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Forex First Review');
    await desktop.locator('[data-vc-workflow-save="asset-family-review"]').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').some(preset => preset.id === 'workflow-asset-family-review-gold-risk-review'));
    const workflowPack = await desktop.evaluate(() => window.SQX.viewCreator.buildValidationWorkflowPack('asset-family-review'));
    if (workflowPack.type !== 'sqx-edge.view-presets' || workflowPack.presets.length !== 3) throw new Error('SQX Views workflow pack contract failed');
    await desktop.evaluate(() => localStorage.removeItem('sqx_view_creator_presets_v1'));
    await desktop.locator('#vc-year-count').fill('5');
    await desktop.locator('[data-vc-preset="risk"]').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await desktop.locator('#vc-preset-name').fill('Risk V2 Smoke');
    await desktop.locator('#vc-save-preset-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').length === 1);
    const exportedPack = await desktop.evaluate(() => window.SQX.viewCreator.buildPresetPackage());
    if (exportedPack.type !== 'sqx-edge.view-presets' || exportedPack.presets.length !== 1) throw new Error('SQX Views export pack contract failed');
    await desktop.locator('[data-vc-preset="egt-core"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '64');
    await desktop.locator('#vc-load-preset-btn').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await desktop.locator('#vc-delete-preset-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').length === 0);
    await mkdir(screenshotDir, { recursive: true });
    const importPackPath = path.join(screenshotDir, 'view-preset-pack-smoke.json');
    await writeFile(importPackPath, JSON.stringify(exportedPack, null, 2), 'utf8');
    await desktop.locator('#vc-import-presets-file').setInputFiles(importPackPath);
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').length === 1);
    await desktop.waitForFunction(() => document.getElementById('vc-import-preview')?.classList.contains('has-items'));
    await desktop.waitForFunction(() => document.getElementById('vc-import-preview')?.textContent.includes('Preview: 1 preset'));
    await desktop.locator('#vc-load-preset-btn').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await saveShot(desktop, 'e2e-view-creator-desktop.png');
    await desktop.locator('.tab[data-tab="cvc"]').click();
    await desktop.waitForSelector('.tab[data-tab="cvc"].active');
    await desktop.waitForSelector('#cvc-run-btn');
    await desktop.locator('#cvc-sample-btn').click();
    await desktop.waitForSelector('#cvc-ranking .cvc-result-row');
    await desktop.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('Health fresh'));
    await desktop.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('EGT v2 STRONG'));
    await desktop.waitForFunction(() => document.getElementById('cvc-ready-count')?.textContent.trim() === '1');
    await desktop.waitForFunction(() => Number(document.getElementById('cvc-regime-ready-count')?.textContent.trim() || 0) > 0);
    await desktop.locator('#cvc-filter-health-ok').check();
    await desktop.waitForFunction(() => document.getElementById('cvc-status')?.textContent.includes('Filtro activo: 2/3 visibles'));
    await desktop.locator('#cvc-filter-egt-v2-ok').check();
    await desktop.waitForFunction(() => document.getElementById('cvc-status')?.textContent.includes('Filtro activo: 1/3 visibles'));
    await desktop.locator('#cvc-filter-health-ok').uncheck();
    await desktop.locator('#cvc-filter-egt-v2-ok').uncheck();
    await desktop.waitForFunction(() => document.querySelectorAll('#cvc-ranking .cvc-result-row').length === 3);
    const cvcModel = await desktop.evaluate(() => window.SQX.championChallenger.evaluate());
    if (!cvcModel.ok || cvcModel.rankings.length !== 3) throw new Error('Champion vs Challenger sample contract failed');
    if (!cvcModel.rankings.every(row => row.regime_evidence && row.regime_evidence.symbol === 'EURUSD')) throw new Error('Champion vs Challenger regime evidence missing');
    const cvcReview = await desktop.evaluate(() => window.SQX.championChallenger.buildReviewExport(window.SQX.championChallenger.evaluate()));
    if (cvcReview.type !== 'sqx-edge.champion-challenger-review' || cvcReview.summary.candidate_count !== 3) throw new Error('Champion vs Challenger export contract failed');
    if (JSON.stringify(cvcReview).includes('Champion CSV')) throw new Error('Champion vs Challenger export should not include raw CSV payloads');
    const cvcHandoff = await desktop.evaluate(review => window.SQX.championChallenger.buildStrategyBuilderHandoff(review), cvcReview);
    if (cvcHandoff.type !== 'sqx-edge.strategy-builder-handoff' || !cvcHandoff.recommended_candidate) throw new Error('Strategy Builder handoff contract failed');
    await desktop.locator('#cvc-handoff-btn').click();
    await desktop.waitForFunction(() => document.getElementById('cvc-handoff-preview')?.textContent.includes('Strategy Builder handoff'));
    await saveShot(desktop, 'e2e-champion-challenger-desktop.png');
    await desktop.locator('.tab[data-tab="strategybuilder"]').click();
    await desktop.waitForSelector('.tab[data-tab="strategybuilder"].active');
    await desktop.waitForSelector('#sb-build-btn');
    await desktop.locator('#sb-sample-cvc-btn').click();
    await desktop.waitForFunction(() => document.getElementById('sb-state')?.textContent.trim() === 'package_exportable');
    await desktop.waitForFunction(() => document.getElementById('sb-workflow-steps')?.querySelectorAll('.sb-workflow-step.is-done').length >= 5);
    const builderPackage = await desktop.evaluate(() => window.SQX.strategyBuilderCore.buildPackage({
      source_mode: 'cvc_handoff',
      source_handoff: window.SQX.strategyBuilderCore.sampleCvcHandoff(),
      timeframe: 'H1',
      idea_archetype: 'trend_following',
      validation_pack_id: 'robustness',
      project_profile_id: 'starter-forex-h1-balanced',
      operator_reviewed: true,
    }));
    if (builderPackage.type !== 'sqx-edge.strategy-builder-package' || builderPackage.workflow_state !== 'package_exportable') throw new Error('Strategy Builder package contract failed');
    if (JSON.stringify(builderPackage).includes('Guaranteed profitable')) throw new Error('Strategy Builder package should not include blocked marketing claims');
    await desktop.locator('#sb-send-pg-btn').click();
    await desktop.waitForSelector('.tab[data-tab="projectgen"].active');
    const pgPrefill = await desktop.evaluate(() => ({
      name: document.getElementById('pg-custom-name')?.value,
      asset: document.getElementById('pg-custom-asset')?.value,
      tf: document.getElementById('pg-custom-tf')?.value,
      bs: document.getElementById('pg-custom-bs')?.value,
      status: document.getElementById('pg-custom-status')?.textContent,
      outputText: document.getElementById('pg-output-list')?.textContent || '',
    }));
    if (pgPrefill.name !== 'SB_EURUSD_H1_trend_following' || pgPrefill.asset !== 'EURUSD' || pgPrefill.tf !== 'H1' || pgPrefill.bs !== 'BS_Tendencia') throw new Error(`Strategy Builder Project Generator prefill failed: ${JSON.stringify(pgPrefill)}`);
    if (!pgPrefill.status.includes('Prefill desde Strategy Builder')) throw new Error('Strategy Builder prefill status missing');
    if (/Custom_EURUSD_H1_Capa/.test(pgPrefill.outputText)) throw new Error('Strategy Builder prefill should not generate custom output');
    await saveShot(desktop, 'e2e-strategy-builder-pg-prefill-desktop.png');
    await desktop.locator('.tab[data-tab="strategybuilder"]').click();
    await desktop.waitForSelector('.tab[data-tab="strategybuilder"].active');
    const presetCountBeforeDraft = await desktop.evaluate(() => window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length);
    await desktop.locator('#sb-prepare-preset-btn').click();
    await desktop.waitForSelector('.tab[data-tab="projectgen"].active');
    const pgPresetDraft = await desktop.evaluate(() => ({
      presetName: document.getElementById('pg-custom-preset-name')?.value,
      status: document.getElementById('pg-custom-status')?.textContent,
      savedCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (pgPresetDraft.presetName !== 'SB EURUSD H1 trend following') throw new Error(`Strategy Builder preset draft failed: ${JSON.stringify(pgPresetDraft)}`);
    if (!pgPresetDraft.status.includes('Guardar preset manualmente')) throw new Error('Strategy Builder preset draft status missing manual save boundary');
    if (pgPresetDraft.savedCount !== presetCountBeforeDraft) throw new Error('Strategy Builder preset draft should not auto-save a preset');
    await saveShot(desktop, 'e2e-strategy-builder-pg-preset-draft-desktop.png');
    await desktop.locator('.tab[data-tab="strategybuilder"]').click();
    await desktop.waitForSelector('.tab[data-tab="strategybuilder"].active');
    const viewPresetCountBeforeHandoff = await desktop.evaluate(() => window.SQX.viewCreator.getSavedPresets(localStorage).length);
    await desktop.locator('#sb-send-views-btn').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    const viewsHandoff = await desktop.evaluate(() => ({
      viewName: document.getElementById('vc-view-name')?.value,
      status: document.getElementById('vc-status')?.textContent,
      columnCount: Number(document.getElementById('vc-column-count')?.textContent.trim() || 0),
      savedCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
    }));
    if (viewsHandoff.viewName !== 'SB EURUSD H1 Robustness') throw new Error(`Strategy Builder SQX Views handoff name failed: ${JSON.stringify(viewsHandoff)}`);
    if (!viewsHandoff.status.includes('Handoff cargado')) throw new Error('Strategy Builder SQX Views handoff status missing');
    if (viewsHandoff.columnCount <= 104) throw new Error(`Strategy Builder SQX Views handoff columns too low: ${JSON.stringify(viewsHandoff)}`);
    if (viewsHandoff.savedCount !== viewPresetCountBeforeHandoff) throw new Error('Strategy Builder SQX Views handoff should not auto-save a template');
    await saveShot(desktop, 'e2e-strategy-builder-views-handoff-desktop.png');
    await desktop.locator('.tab[data-tab="strategybuilder"]').click();
    await desktop.waitForSelector('.tab[data-tab="strategybuilder"].active');
    await desktop.locator('#sb-prepare-cleaner-btn').click();
    await desktop.waitForSelector('.tab[data-tab="projectgen"].active');
    const cleanerDraft = await desktop.evaluate(() => ({
      recursive: document.getElementById('cln-recursive')?.checked,
      removeExitBars: document.getElementById('cln-opt-eab')?.checked,
      rename: document.getElementById('cln-opt-rename')?.checked,
      pattern: document.getElementById('cln-pattern')?.value,
      info: document.getElementById('cln-info')?.textContent,
      tableText: document.getElementById('cln-table')?.textContent || '',
      log: document.getElementById('pg-log')?.textContent || '',
    }));
    if (!cleanerDraft.recursive || !cleanerDraft.removeExitBars || !cleanerDraft.rename || cleanerDraft.pattern !== '{asset}_{tf}_{dir}_{id}') throw new Error(`Strategy Cleaner draft options failed: ${JSON.stringify(cleanerDraft)}`);
    if (!cleanerDraft.info.includes('procesa manualmente')) throw new Error(`Strategy Cleaner draft info missing manual boundary: ${JSON.stringify(cleanerDraft)}`);
    if (cleanerDraft.tableText.trim() !== '') throw new Error('Strategy Cleaner draft should not scan .sqx files');
    if (!cleanerDraft.log.includes('limpieza manual pendientes')) throw new Error('Strategy Cleaner draft should log manual cleanup boundary');
    await saveShot(desktop, 'e2e-strategy-builder-cleaner-draft-desktop.png');
    await desktop.locator('.tab[data-tab="strategybuilder"]').click();
    await desktop.waitForSelector('.tab[data-tab="strategybuilder"].active');
    await desktop.locator('#sb-prepare-buyer-pack-btn').click();
    const buyerHandoffPack = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      pack: JSON.parse(document.getElementById('sb-package-preview')?.textContent || '{}'),
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_buyer_pack_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!buyerHandoffPack.preview.includes('sqx-edge.strategy-builder-buyer-handoff-pack')) throw new Error('Strategy Builder buyer pack preview missing type');
    if (!buyerHandoffPack.preview.includes('project_generator_prefill') || !buyerHandoffPack.preview.includes('sqx_views') || !buyerHandoffPack.preview.includes('strategy_cleaner')) throw new Error(`Strategy Builder buyer pack missing destination handoffs: ${buyerHandoffPack.preview}`);
    if (!buyerHandoffPack.status.includes('No destination action')) throw new Error(`Strategy Builder buyer pack status missing manual boundary: ${JSON.stringify(buyerHandoffPack)}`);
    if (!buyerHandoffPack.auditRows.some(text => text.includes('Buyer Handoff Pack'))) throw new Error(`Strategy Builder buyer pack audit row missing: ${JSON.stringify(buyerHandoffPack)}`);
    if (buyerHandoffPack.storageText !== null) throw new Error('Strategy Builder buyer pack should stay preview-only, not localStorage');
    if (buyerHandoffPack.viewPresetCount !== viewPresetCountBeforeHandoff) throw new Error('Strategy Builder buyer pack should not auto-save SQX Views presets');
    if (buyerHandoffPack.pgPresetCount !== presetCountBeforeDraft) throw new Error('Strategy Builder buyer pack should not auto-save Project Generator presets');
    await saveShot(desktop, 'e2e-strategy-builder-buyer-pack-desktop.png');
    const auditTrail = await desktop.evaluate(() => ({
      rows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      workflowDone: document.querySelectorAll('#sb-workflow-steps .sb-workflow-step.is-done').length,
      storageText: localStorage.getItem('sqx_strategy_builder_audit_v1'),
    }));
    if (auditTrail.workflowDone < 5) throw new Error(`Strategy Builder workflow polish missing ready steps: ${JSON.stringify(auditTrail)}`);
    if (!auditTrail.rows.some(text => text.includes('SQX Views')) || !auditTrail.rows.some(text => text.includes('Project Generator')) || !auditTrail.rows.some(text => text.includes('PG Preset Draft')) || !auditTrail.rows.some(text => text.includes('Strategy Cleaner')) || !auditTrail.rows.some(text => text.includes('Buyer Handoff Pack'))) throw new Error(`Strategy Builder audit trail missing handoffs: ${JSON.stringify(auditTrail)}`);
    if (auditTrail.storageText !== null) throw new Error('Strategy Builder audit trail should stay session-only, not localStorage');
    await saveShot(desktop, 'e2e-strategy-builder-audit-desktop.png');
    const buyerPackImport = await desktop.evaluate(pack => {
      const beforeViewPresets = window.SQX.viewCreator.getSavedPresets(localStorage).length;
      const beforePgPresets = window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length;
      const result = window.SQX.strategyBuilder.importText(JSON.stringify(pack));
      return {
        ok: result.ok,
        workflowState: result.package && result.package.workflow_state,
        reviewType: result.buyer_pack_review && result.buyer_pack_review.type,
        preview: document.getElementById('sb-package-preview')?.textContent || '',
        status: document.getElementById('sb-status')?.textContent || '',
        auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
        storageText: localStorage.getItem('sqx_strategy_builder_buyer_pack_v1'),
        viewPresetDelta: window.SQX.viewCreator.getSavedPresets(localStorage).length - beforeViewPresets,
        pgPresetDelta: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length - beforePgPresets,
      };
    }, buyerHandoffPack.pack);
    if (!buyerPackImport.ok || buyerPackImport.workflowState !== 'blocked_operator_review') throw new Error(`Strategy Builder buyer pack import should require fresh review: ${JSON.stringify(buyerPackImport)}`);
    if (buyerPackImport.reviewType !== 'sqx-edge.strategy-builder-buyer-handoff-pack-review') throw new Error(`Strategy Builder buyer pack import review missing: ${JSON.stringify(buyerPackImport)}`);
    if (!buyerPackImport.preview.includes('included_handoffs')) throw new Error('Strategy Builder buyer pack import preview should show review handoffs');
    if (!buyerPackImport.status.includes('Buyer pack imported for local review')) throw new Error(`Strategy Builder buyer pack import status missing: ${JSON.stringify(buyerPackImport)}`);
    if (!buyerPackImport.auditRows.some(text => text.includes('Buyer Pack Import Review'))) throw new Error(`Strategy Builder buyer pack import audit missing: ${JSON.stringify(buyerPackImport)}`);
    if (buyerPackImport.storageText !== null || buyerPackImport.viewPresetDelta !== 0 || buyerPackImport.pgPresetDelta !== 0) throw new Error(`Strategy Builder buyer pack import should not persist destination state: ${JSON.stringify(buyerPackImport)}`);
    await saveShot(desktop, 'e2e-strategy-builder-buyer-pack-import-desktop.png');
    await desktop.locator('#sb-buyer-session-btn').click();
    const buyerSessionChecklist = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_buyer_session_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!buyerSessionChecklist.preview.includes('sqx-edge.strategy-builder-buyer-session-checklist')) throw new Error('Strategy Builder buyer session checklist preview missing type');
    if (!buyerSessionChecklist.preview.includes('Confirm manual review first') || !buyerSessionChecklist.preview.includes('operator_executes_every_step_manually')) throw new Error(`Strategy Builder buyer session checklist missing manual guidance: ${buyerSessionChecklist.preview}`);
    if (!buyerSessionChecklist.status.includes('Buyer session checklist prepared')) throw new Error(`Strategy Builder buyer session checklist status missing: ${JSON.stringify(buyerSessionChecklist)}`);
    if (!buyerSessionChecklist.auditRows.some(text => text.includes('Buyer Session Checklist'))) throw new Error(`Strategy Builder buyer session checklist audit missing: ${JSON.stringify(buyerSessionChecklist)}`);
    if (buyerSessionChecklist.storageText !== null || buyerSessionChecklist.viewPresetCount !== viewPresetCountBeforeHandoff || buyerSessionChecklist.pgPresetCount !== presetCountBeforeDraft) throw new Error(`Strategy Builder buyer session checklist should not persist destination state: ${JSON.stringify(buyerSessionChecklist)}`);
    await saveShot(desktop, 'e2e-strategy-builder-buyer-session-desktop.png');
    await desktop.locator('#sb-buyer-summary-btn').click();
    const buyerSessionSummary = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_buyer_session_summary_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!buyerSessionSummary.preview.includes('sqx-edge.strategy-builder-buyer-session-summary')) throw new Error('Strategy Builder buyer session summary preview missing type');
    if (!buyerSessionSummary.preview.includes('no_buyer_identity') || !buyerSessionSummary.preview.includes('no_destination_action_triggered')) throw new Error(`Strategy Builder buyer session summary missing redaction/manual guardrails: ${buyerSessionSummary.preview}`);
    if (!buyerSessionSummary.status.includes('Buyer session summary')) throw new Error(`Strategy Builder buyer session summary status missing: ${JSON.stringify(buyerSessionSummary)}`);
    if (!buyerSessionSummary.auditRows.some(text => text.includes('Buyer Session Summary'))) throw new Error(`Strategy Builder buyer session summary audit missing: ${JSON.stringify(buyerSessionSummary)}`);
    if (buyerSessionSummary.storageText !== null || buyerSessionSummary.viewPresetCount !== viewPresetCountBeforeHandoff || buyerSessionSummary.pgPresetCount !== presetCountBeforeDraft) throw new Error(`Strategy Builder buyer session summary should not persist destination state: ${JSON.stringify(buyerSessionSummary)}`);
    await saveShot(desktop, 'e2e-strategy-builder-buyer-summary-desktop.png');
    await desktop.locator('#sb-buyer-notes-btn').click();
    const buyerSessionNotes = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_buyer_session_notes_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!buyerSessionNotes.preview.includes('SQX Edge buyer session notes - EURUSD H1')) throw new Error('Strategy Builder buyer session notes preview missing title');
    if (!buyerSessionNotes.preview.includes('Handoff targets') || !buyerSessionNotes.preview.includes('Operator guardrails')) throw new Error(`Strategy Builder buyer session notes missing printable sections: ${buyerSessionNotes.preview}`);
    if (!buyerSessionNotes.status.includes('Buyer session printable notes')) throw new Error(`Strategy Builder buyer session notes status missing: ${JSON.stringify(buyerSessionNotes)}`);
    if (!buyerSessionNotes.auditRows.some(text => text.includes('Buyer Session Notes'))) throw new Error(`Strategy Builder buyer session notes audit missing: ${JSON.stringify(buyerSessionNotes)}`);
    if (buyerSessionNotes.storageText !== null || buyerSessionNotes.viewPresetCount !== viewPresetCountBeforeHandoff || buyerSessionNotes.pgPresetCount !== presetCountBeforeDraft) throw new Error(`Strategy Builder buyer session notes should not persist destination state: ${JSON.stringify(buyerSessionNotes)}`);
    await saveShot(desktop, 'e2e-strategy-builder-buyer-notes-desktop.png');
    await desktop.locator('#sb-buyer-support-case-btn').click();
    const buyerSupportCase = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_buyer_support_case_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!buyerSupportCase.preview.includes('sqx-edge.strategy-builder-buyer-session-support-case-bundle')) throw new Error('Strategy Builder buyer support case preview missing type');
    if (!buyerSupportCase.preview.includes('no_remote_ticket_created') || !buyerSupportCase.preview.includes('full_strategy_builder_package')) throw new Error(`Strategy Builder buyer support case missing safety manifest: ${buyerSupportCase.preview}`);
    if (!buyerSupportCase.status.includes('Buyer support case bundle')) throw new Error(`Strategy Builder buyer support case status missing: ${JSON.stringify(buyerSupportCase)}`);
    if (!buyerSupportCase.auditRows.some(text => text.includes('Buyer Support Case'))) throw new Error(`Strategy Builder buyer support case audit missing: ${JSON.stringify(buyerSupportCase)}`);
    if (buyerSupportCase.storageText !== null || buyerSupportCase.viewPresetCount !== viewPresetCountBeforeHandoff || buyerSupportCase.pgPresetCount !== presetCountBeforeDraft) throw new Error(`Strategy Builder buyer support case should not persist destination state: ${JSON.stringify(buyerSupportCase)}`);
    await saveShot(desktop, 'e2e-strategy-builder-buyer-support-case-desktop.png');
    await desktop.locator('#sb-buyer-resolution-btn').click();
    const buyerResolution = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_buyer_resolution_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!buyerResolution.preview.includes('sqx-edge.strategy-builder-buyer-session-support-resolution-checklist')) throw new Error('Strategy Builder buyer resolution preview missing type');
    if (!buyerResolution.preview.includes('case_close_or_escalate') || !buyerResolution.preview.includes('strategyquant_validation_boundary_confirmed')) throw new Error(`Strategy Builder buyer resolution missing close/escalation conditions: ${buyerResolution.preview}`);
    if (!buyerResolution.status.includes('Buyer support resolution checklist')) throw new Error(`Strategy Builder buyer resolution status missing: ${JSON.stringify(buyerResolution)}`);
    if (!buyerResolution.auditRows.some(text => text.includes('Buyer Resolution Checklist'))) throw new Error(`Strategy Builder buyer resolution audit missing: ${JSON.stringify(buyerResolution)}`);
    if (buyerResolution.storageText !== null || buyerResolution.viewPresetCount !== viewPresetCountBeforeHandoff || buyerResolution.pgPresetCount !== presetCountBeforeDraft) throw new Error(`Strategy Builder buyer resolution should not persist destination state: ${JSON.stringify(buyerResolution)}`);
    await saveShot(desktop, 'e2e-strategy-builder-buyer-resolution-desktop.png');
    await desktop.locator('#sb-evidence-index-btn').click();
    const evidenceIndex = await desktop.evaluate(() => ({
      preview: document.getElementById('sb-package-preview')?.textContent || '',
      status: document.getElementById('sb-status')?.textContent || '',
      auditRows: Array.from(document.querySelectorAll('#sb-audit-list .sb-audit-row')).map(row => row.textContent),
      storageText: localStorage.getItem('sqx_strategy_builder_evidence_index_v1'),
      viewPresetCount: window.SQX.viewCreator.getSavedPresets(localStorage).length,
      pgPresetCount: window.SQX.projectGenerator.getCustomProjectPresets(localStorage).length,
    }));
    if (!evidenceIndex.preview.includes('sqx-edge.strategy-builder-evidence-handoff-index')) throw new Error('Strategy Builder evidence index preview missing type');
    if (!evidenceIndex.preview.includes('buyer_resolution_checklist') || !evidenceIndex.preview.includes('ready_for_buyer_handoff')) throw new Error(`Strategy Builder evidence index missing handoff readiness: ${evidenceIndex.preview}`);
    if (!evidenceIndex.status.includes('Evidence handoff index prepared')) throw new Error(`Strategy Builder evidence index status missing: ${JSON.stringify(evidenceIndex)}`);
    if (!evidenceIndex.auditRows.some(text => text.includes('Evidence Index'))) throw new Error(`Strategy Builder evidence index audit missing: ${JSON.stringify(evidenceIndex)}`);
    if (evidenceIndex.storageText !== null || evidenceIndex.viewPresetCount !== viewPresetCountBeforeHandoff || evidenceIndex.pgPresetCount !== presetCountBeforeDraft) throw new Error(`Strategy Builder evidence index should not persist destination state: ${JSON.stringify(evidenceIndex)}`);
    await saveShot(desktop, 'e2e-strategy-builder-evidence-index-desktop.png');
    const importResult = await desktop.evaluate(pkg => window.SQX.strategyBuilder.importText(JSON.stringify(pkg)), builderPackage);
    if (!importResult.ok || importResult.package.workflow_state !== 'blocked_operator_review') throw new Error('Strategy Builder import should require fresh operator review');
    await desktop.waitForFunction(() => document.getElementById('sb-status')?.textContent.includes('Confirm manual review'));
    await saveShot(desktop, 'e2e-strategy-builder-desktop.png');
    await desktop.locator('.tab[data-tab="estrategias"]').click();
    await desktop.waitForSelector('#tab-estrategias .strat-card');
    const cards = await desktop.locator('#tab-estrategias .strat-card').count();
    const deleteButtons = await desktop.locator('#tab-estrategias .strat-remove-btn').count();
    if (cards < 1) throw new Error('Strategies tab rendered without strategy cards');
    if (cards !== deleteButtons) throw new Error(`Expected one delete button per card, got ${cards} cards and ${deleteButtons} buttons`);

    await desktop.locator('#tab-estrategias .strat-remove-btn').first().click();
    await desktop.waitForFunction(() => localStorage.getItem('sqx_strategies_deleted_v1') !== null);
    const afterDelete = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterDelete !== cards - 1) throw new Error(`Deleting a base strategy should hide exactly one card, got ${afterDelete} from ${cards}`);
    await desktop.locator('#strat-restore-hidden-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_deleted_v1') || '[]').length === 0);
    const afterRestore = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterRestore !== cards) throw new Error(`Restoring hidden strategies should recover cards, got ${afterRestore} from ${cards}`);
    await saveShot(desktop, 'e2e-strategies-desktop.png');
    await desktop.locator('#strat-views-handoff [data-vc-handoff="risk"]').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX Risk Review');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    assertNoBrowserErrors(desktopErrors, 'desktop');
    await desktop.close();

    const mobile = await browser.newPage({ viewport: { width: 390, height: 920 } });
    const mobileErrors = [];
    collectBrowserErrors(mobile, mobileErrors);
    await mobile.goto(dashboardUrl, { waitUntil: 'load' });
    await mobile.waitForSelector('.tab[data-tab="inicio"].active');
    await mobile.locator('.tab[data-tab="views"]').click();
    await mobile.waitForSelector('#vc-preview');
    await assertNoMobileOverflow(mobile);
    await mobile.locator('.tab[data-tab="cvc"]').click();
    await mobile.waitForSelector('#cvc-run-btn');
    await mobile.locator('#cvc-sample-btn').click();
    await mobile.waitForSelector('#cvc-ranking .cvc-result-row');
    await mobile.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('Health fresh'));
    await mobile.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('EGT v2 STRONG'));
    await mobile.waitForFunction(() => Number(document.getElementById('cvc-regime-ready-count')?.textContent.trim() || 0) > 0);
    const mobileHandoff = await mobile.evaluate(() => window.SQX.championChallenger.buildStrategyBuilderHandoff(window.SQX.championChallenger.buildReviewExport(window.SQX.championChallenger.evaluate())));
    if (mobileHandoff.type !== 'sqx-edge.strategy-builder-handoff') throw new Error('Mobile CVC handoff contract failed');
    await assertNoMobileOverflow(mobile);
    await saveShot(mobile, 'e2e-champion-challenger-mobile.png');
    await mobile.locator('.tab[data-tab="strategybuilder"]').click();
    await mobile.waitForSelector('#sb-build-btn');
    await mobile.locator('#sb-sample-cvc-btn').click();
    await mobile.waitForFunction(() => document.getElementById('sb-state')?.textContent.trim() === 'package_exportable');
    await assertNoMobileOverflow(mobile);
    await saveShot(mobile, 'e2e-strategy-builder-mobile.png');
    await mobile.locator('.tab[data-tab="estrategias"]').click();
    await mobile.waitForSelector('#tab-estrategias .strat-card');
    const activeTabBox = await mobile.locator('.tab.active').boundingBox();
    const tabsBox = await mobile.locator('.tabs').boundingBox();
    if (activeTabBox && activeTabBox.height > 80) throw new Error('Mobile active tab is too tall');
    if (tabsBox && tabsBox.height > 90) throw new Error('Mobile tabs bar is too tall');
    await assertNoMobileOverflow(mobile);
    await saveShot(mobile, 'e2e-strategies-mobile.png');
    assertNoBrowserErrors(mobileErrors, 'mobile');
    await mobile.close();
  } finally {
    await browser.close();
  }
}

run().catch(error => {
  console.error(error);
  process.exit(1);
});
