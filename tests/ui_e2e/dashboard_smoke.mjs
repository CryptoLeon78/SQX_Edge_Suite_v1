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
    await desktop.waitForSelector('.tab[data-tab="workflow"].active');
    await desktop.waitForSelector('#workflow-command-center');
    const categoryTabCount = await desktop.locator('.tab[data-tab="categorias"]').count();
    if (categoryTabCount !== 0) throw new Error('Por Categoria should not be a primary tab');
    const priorityTabCount = await desktop.locator('.tab[data-tab="priority"]').count();
    if (priorityTabCount !== 0) throw new Error('Priority should not be a primary navigation section');
    const sidebarOrder = await desktop.locator('#main-tabs .tab').evaluateAll(nodes => nodes.map(node => node.dataset.tab));
    const expectedSidebarOrder = ['workflow', 'activos', 'pipeline', 'views', 'projectgen', 'estrategias', 'cvc', 'filtros', 'inicio'];
    if (sidebarOrder.join('|') !== expectedSidebarOrder.join('|')) {
      throw new Error(`Navigation should follow Workflow methodology order: ${sidebarOrder.join('|')}`);
    }
    const strategyBuilderTabCount = await desktop.locator('.tab[data-tab="strategybuilder"]').count();
    if (strategyBuilderTabCount !== 0) throw new Error('Strategy Builder should not be a primary navigation section');
    const commandCenterText = await desktop.locator('#workflow-command-center').innerText();
    if (commandCenterText.includes('Strategy Builder')) throw new Error('Workflow command center should not expose Strategy Builder');
    ['Estrategias', 'Champion vs Challenger'].forEach(expected => {
      if (!commandCenterText.includes(expected)) throw new Error(`Workflow command center should expose ${expected}`);
    });
    await desktop.locator('#workflow-command-center [data-home-tab="pipeline"]').click();
    await desktop.waitForSelector('.tab[data-tab="pipeline"].active');
    await desktop.waitForSelector('#ps-current-pipeline-status');
    const miningControlStatusText = await desktop.locator('#ps-current-pipeline-status').innerText();
    if (!miningControlStatusText.includes('TEMPLATE LINEAR cerrada') || !miningControlStatusText.includes('filter-by-correlation')) {
      throw new Error('Mining Control should own the current pipeline status section');
    }
    await saveShot(desktop, 'e2e-mining-control-status-desktop.png');
    await desktop.locator('.tab[data-tab="workflow"]').click();
    await desktop.waitForSelector('.tab[data-tab="workflow"].active');
    await desktop.locator('#wf-command-steps input[data-check="command-center-diagnostico"]').check();
    await desktop.waitForSelector('#wf-command-steps .workflow-command-step.is-done');
    await desktop.waitForFunction(() => document.getElementById('wf-command-progress-label')?.textContent.includes('1 de 7'));
    await desktop.locator('.tab[data-tab="inicio"]').click();
    await desktop.waitForSelector('.tab[data-tab="inicio"].active');
    await desktop.waitForSelector('#home-readiness-score');
    const panelTitle = await desktop.locator('#tab-inicio .home-hero h2').innerText();
    if (panelTitle.trim() !== 'Panel de estado') throw new Error(`Panel tab should be a status surface, got: ${panelTitle}`);
    const homeMethodSteps = await desktop.locator('#home-method-map .home-method-step').count();
    if (homeMethodSteps !== 6) throw new Error(`Panel methodology map should expose 6 ordered steps, got ${homeMethodSteps}`);
    const homeMethodText = await desktop.locator('#home-method-map').innerText();
    ['Workflow', 'SQX Views', 'Mining Control', 'Project Generator', 'Estrategias', 'Champion vs Challenger'].forEach(expected => {
      if (!homeMethodText.includes(expected)) throw new Error(`Panel methodology map should include ${expected}`);
    });
    const homeBuilderLinks = await desktop.locator('#tab-inicio [data-home-tab="strategybuilder"]').count();
    if (homeBuilderLinks !== 0) throw new Error('Panel should not expose retired Strategy Builder links');
    await saveShot(desktop, 'e2e-panel-desktop.png');
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
    const capa1Subtab = await desktop.locator('.subtab[data-subtab="wf-capa1"]').count();
    if (capa1Subtab !== 0) throw new Error('Capa 1 should live inside the pipeline step, not as a top workflow subtab');
    const setupGlobalKpi = await desktop.locator('#wf-setup-global-details').count();
    if (setupGlobalKpi !== 0) throw new Error('Setup Global KPI should be removed from Workflow overview');
    const planSummaryKpi = await desktop.locator('#wf-plan-v2-summary').count();
    if (planSummaryKpi !== 0) throw new Error('Plan operativo actual KPI should be removed from Workflow');
    const recommendedViewsText = await desktop.locator('#wf-overview', { hasText: 'Vista SQX recomendada' }).count();
    if (recommendedViewsText !== 0) throw new Error('SQX Views KPI should be mandatory, not recommended');
    const initialPipelineOpen = await desktop.locator('#wf-pipeline-flow-details[open]').count();
    if (initialPipelineOpen !== 1) throw new Error('Pipeline flow accordion should be open by default');
    const unifiedMethodTitle = await desktop.locator('#wf-pipeline-flow-details summary', { hasText: 'Filosofía y flujo completo del pipeline' }).count();
    if (unifiedMethodTitle !== 1) throw new Error('Workflow philosophy and pipeline flow should be unified in one accordion');
    const initiallyExpandedDetails = await desktop.locator('#wf-pipeline-flow-details .workflow-step-detail:not([hidden])').count();
    if (initiallyExpandedDetails !== 0) throw new Error('Open pipeline should show only main KPI cards by default');
    const viewsRequiredTrigger = await desktop.locator('[data-wf-detail-target="wf-sqx-views-required-detail"] .step-num', { hasText: '0' }).count();
    if (viewsRequiredTrigger !== 1) throw new Error('Mandatory SQX Views should be KPI 0 in the workflow pipeline');
    await desktop.locator('[data-wf-detail-target="wf-sqx-views-required-detail"]').click();
    await desktop.waitForSelector('#wf-sqx-views-required-detail:not([hidden])');
    const viewsCopy = await desktop.locator('#workflow-views-handoff .views-handoff-copy').innerText();
    if (!viewsCopy.includes('descarga el .vw') || !viewsCopy.includes('importalo en StrategyQuant X')) {
      throw new Error('Workflow SQX Views handoff should explain where and how to create views');
    }
    await saveShot(desktop, 'e2e-workflow-views-required-desktop.png');
    const removedOosKpi = await desktop.locator('#wf-pipeline-flow-details .step-title', { hasText: 'Validación OOS 2010-2017' }).count();
    if (removedOosKpi !== 0) throw new Error('OOS validation KPI should be removed from the full pipeline');
    const removedForwardKpi = await desktop.locator('#wf-pipeline-flow-details .step-title', { hasText: 'Validación Forward 2024-2026' }).count();
    if (removedForwardKpi !== 0) throw new Error('Forward validation KPI should be removed from the full pipeline');
    await desktop.locator('[data-wf-detail-target="wf-capa1-tree-detail"]').click();
    await desktop.waitForSelector('#wf-capa1-tree-detail:not([hidden])');
    const overviewStillActive = await desktop.locator('#wf-overview.active').count();
    if (overviewStillActive !== 1) throw new Error('Capa 1 detail should expand inline without leaving Vista General');
    const capa1PanelInactive = await desktop.locator('#wf-capa1.active').count();
    if (capa1PanelInactive !== 0) throw new Error('Capa 1 detail should not open the old standalone panel');
    const capa1TriggerExpanded = await desktop.locator('[data-wf-detail-target="wf-capa1-tree-detail"][aria-expanded="true"]').count();
    if (capa1TriggerExpanded !== 1) throw new Error('Capa 1 pipeline trigger should expand the inline tree detail');
    const capa1TreeNodes = await desktop.locator('#wf-capa1-tree-detail .pipeline-step.compact').count();
    if (capa1TreeNodes < 7) throw new Error('Capa 1 inline detail should render as a compact tree of KPI-style nodes');
    const capa1TreeText = await desktop.locator('#wf-capa1-tree-detail').innerText();
    [
      'Period: 2017.10 - 2026.04',
      'Re-optimize: NO (retest pasivo)',
      'Randomly skip trades 10%: OFF',
      'Apply optimized parameters to strategy: OFF',
      'Synthetic Bootstrap V2: ON',
      'Walk-Forward type: Simulated IS, Simulated OOS (fastest)',
      'Period: 2024.01 - 2026.04',
      'Ret/DD > 0.5',
    ].forEach(expected => {
      if (!capa1TreeText.includes(expected)) throw new Error(`Capa 1 tree should preserve retest config: ${expected}`);
    });
    await desktop.locator('#wf-capa1-tree-detail input[data-check="capa1-pre-mm"]').check();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_workflow_checklist_v1') || '{}')['capa1-pre-mm'] === true);
    await desktop.locator('#wf-capa1-tree-detail button[data-checklist-clear="capa1"]').click();
    await desktop.waitForFunction(() => !JSON.parse(localStorage.getItem('sqx_workflow_checklist_v1') || '{}')['capa1-pre-mm']);
    const workflowChecked = await desktop.locator('#wf-capa1-tree-detail input[data-check="capa1-pre-mm"]').isChecked();
    if (workflowChecked) throw new Error('Workflow checklist clear should uncheck capa1 items');
    await saveShot(desktop, 'e2e-workflow-desktop.png');
    await desktop.locator('.subtab[data-subtab="wf-overview"]').click();
    await desktop.waitForSelector('#wf-overview.active');
    const workflowOverviewText = await desktop.locator('#wf-overview').innerText();
    if (workflowOverviewText.includes('Estado actual del pipeline') || workflowOverviewText.includes('TEMPLATE LINEAR cerrada')) {
      throw new Error('Workflow overview should not render the current pipeline status section');
    }
    const removedWorkflowStats = await desktop.locator('#wf-overview .stats-row .stat-card').count();
    if (removedWorkflowStats !== 0) throw new Error('Workflow overview KPI cards should be removed');
    const setupSubtab = await desktop.locator('.subtab[data-subtab="wf-setup"]').count();
    if (setupSubtab !== 0) throw new Error('Setup Global should be integrated inside Vista General, not exposed as a subtab');
    await saveShot(desktop, 'e2e-workflow-handoff-desktop.png');
    await desktop.locator('[data-wf-detail-target="wf-pipeline-mining2-tree-detail"]').click();
    await desktop.waitForSelector('#wf-pipeline-mining2-tree-detail:not([hidden])');
    const capa2TriggerExpanded = await desktop.locator('[data-wf-detail-target="wf-pipeline-mining2-tree-detail"][aria-expanded="true"]').count();
    if (capa2TriggerExpanded !== 1) throw new Error('Mining 2 KPI should expand from the main workflow pipeline');
    const capa2TreeText = await desktop.locator('#wf-pipeline-mining2-tree-detail').innerText();
    [
      'Edge: NO RANDOM (template fijo)',
      'PF >= 1.20',
      'Randomly skip trades 10%: ON',
      'Randomize slippage: ON',
      'Entry levels: ON',
      'WF Ret/DD Ratio >= 5',
      'Ret/DD > 1.0',
      'Material operativo extendido',
    ].forEach(expected => {
      if (!capa2TreeText.includes(expected)) throw new Error(`Mining 2 tree should preserve Capa 2 config: ${expected}`);
    });
    await saveShot(desktop, 'e2e-workflow-mining2-desktop.png');
    await desktop.locator('[data-workflow-subtab-target="wf-capa2"]').click();
    await desktop.waitForSelector('#wf-capa2.active');
    const capa2TabText = await desktop.locator('#wf-capa2').innerText();
    if (!capa2TabText.includes('Checklist operativo Capa 2')) {
      throw new Error('Workflow Capa 2 tab should keep the extended operational content');
    }
    ['Checklist de aplicación Capa 2', 'Embudo esperado Capa 2', 'Configuraciones opcionales según objetivo'].forEach(expected => {
      if (!capa2TabText.includes(expected)) throw new Error(`Workflow Capa 2 tab should preserve: ${expected}`);
    });
    ['Orden de ejecución Capa 2', 'Reglas de oro Capa 2', 'wf-capa2-mining2-tree-detail', 'Capa 2 — Cheatsheet operativo', 'Config Base Builder Capa 2'].forEach(removedText => {
      if (capa2TabText.includes(removedText)) throw new Error(`Workflow Capa 2 tab should not include: ${removedText}`);
    });
    if (capa2TabText.indexOf('Checklist de aplicación Capa 2') > capa2TabText.indexOf('Embudo esperado Capa 2')) {
      throw new Error('Workflow Capa 2 checklist should appear before the expected funnel');
    }
    await saveShot(desktop, 'e2e-workflow-capa2-operational-desktop.png');
    await desktop.locator('.subtab[data-subtab="wf-rules"]').click();
    await desktop.waitForSelector('#wf-rules.active');
    const rulesTabText = await desktop.locator('#wf-rules').innerText();
    ['Reglas de Oro del Pipeline', 'Reglas de oro Capa 2', 'Apply optimized parameters: SIEMPRE OFF'].forEach(expected => {
      if (!rulesTabText.includes(expected)) throw new Error(`Workflow rules tab should preserve: ${expected}`);
    });
    await saveShot(desktop, 'e2e-workflow-rules-capa2-desktop.png');
    await desktop.locator('.subtab[data-subtab="wf-overview"]').click();
    await desktop.waitForSelector('#wf-overview.active');
    await desktop.locator('[data-wf-detail-target="wf-sqx-views-required-detail"]').click();
    await desktop.waitForSelector('#wf-sqx-views-required-detail:not([hidden])');
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
    const removedProjectGeneratorPanels = await desktop.locator('#pg-custom-starter-list, #pg-custom-family-list, #pg-buyer-handoff-card').count();
    if (removedProjectGeneratorPanels !== 0) throw new Error('Project Generator removed panels should not be visible in UX-NAV2');
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
    if (cvcHandoff.type !== 'sqx-edge.strategy-builder-handoff' || !cvcHandoff.recommended_candidate) throw new Error('Internal CVC handoff contract failed');
    const cvcHandoffButtonCount = await desktop.locator('#cvc-handoff-btn').count();
    if (cvcHandoffButtonCount !== 0) throw new Error('CVC should not expose the retired Strategy Builder handoff button');
    const strategyBuilderPanelCount = await desktop.locator('#tab-strategybuilder').count();
    if (strategyBuilderPanelCount !== 0) throw new Error('Strategy Builder tab panel should be removed from the dashboard shell');
    await saveShot(desktop, 'e2e-champion-challenger-desktop.png');
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
    await mobile.waitForSelector('.tab[data-tab="workflow"].active');
    await mobile.waitForSelector('#workflow-command-center');
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
    const mobileStrategyBuilderTabCount = await mobile.locator('.tab[data-tab="strategybuilder"]').count();
    if (mobileStrategyBuilderTabCount !== 0) throw new Error('Mobile navigation should not expose Strategy Builder');
    await saveShot(mobile, 'e2e-champion-challenger-mobile.png');
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
