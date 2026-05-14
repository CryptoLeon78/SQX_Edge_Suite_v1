import { chromium } from 'playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
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
    const expectedSidebarOrder = ['workflow', 'activos', 'pipeline', 'views', 'projectgen', 'templatemaker', 'estrategias', 'cvc', 'filtros', 'inicio'];
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
    await desktop.waitForFunction(() => document.getElementById('ps-current-pipeline-status')?.innerText.includes('Foco operativo'));
    await desktop.waitForSelector('#ps-command-strip');
    const miningControlCommandText = await desktop.locator('#ps-command-strip').innerText();
    ['Workflow', 'SQX Views', 'Plan mining', 'Project Generator', 'Estrategias', 'Champion vs Challenger'].forEach(expected => {
      if (!miningControlCommandText.includes(expected)) throw new Error(`Mining Control command strip should include ${expected}`);
    });
    if (miningControlCommandText.includes('Embudo')) throw new Error('Mining Control command strip should route to Project Generator instead of Embudo');
    const pipelinePriorityText = await desktop.locator('#tab-pipeline', { hasText: 'SQX Priority' }).count();
    if (pipelinePriorityText !== 0) throw new Error('Mining Control should not expose retired SQX Priority copy');
    await desktop.waitForSelector('#ps-plan-reset-plan');
    const planResetButtonText = await desktop.locator('#ps-plan-reset-plan').innerText();
    if (!planResetButtonText.includes('Reset plan mining')) throw new Error('Mining Control should expose a plan-level reset action');
    await desktop.evaluate(() => {
      window.setPhaseMetaUser(1, 'Fase editable E2E', 'Texto persistente E2E');
      window.renderPipelineState();
    });
    await desktop.waitForSelector('#ps-plan-table .ps-user-badge');
    const editedPlanText = await desktop.locator('#ps-plan-table').innerText();
    if (!editedPlanText.includes('Fase editable E2E') || !editedPlanText.includes('Texto persistente E2E')) {
      throw new Error('Mining Control phase edits should persist in the rendered plan');
    }
    await desktop.locator('#ps-plan-reset-plan').click();
    await desktop.waitForFunction(() => !document.getElementById('ps-plan-table')?.innerText.includes('Fase editable E2E'));
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('Plan mining vacío'));
    await desktop.evaluate(() => {
      const ok = window.addPlanMiningFromCandidate('EURUSD', 'tendencia', 'H1', 'L/S', 'asset-card');
      if (!ok) throw new Error('E2E addPlanMiningFromCandidate failed');
      window.renderPipelineState();
    });
    await desktop.waitForSelector('#ps-orphans-card', { state: 'visible' });
    const planPreloadText = await desktop.locator('#ps-orphans-card').innerText();
    if (!planPreloadText.includes('EURUSD') || !planPreloadText.includes('Mining #')) {
      throw new Error('Por Activo + Plan should appear as Plan mining preload, not as priority orphan');
    }
    const unifiedPlanText = await desktop.locator('#ps-plan-card').innerText();
    if (!unifiedPlanText.includes('EURUSD') || !unifiedPlanText.includes('Plan extendido')) {
      throw new Error('Added asset-card mining should join the unified Plan mining control center');
    }
    await desktop.locator('#ps-plan-table .ps-phase-reset-btn').first().click();
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('Fase sin minings todavia'));
    await desktop.evaluate(() => {
      window.resetProjectWorkingData();
      window.renderPipelineState();
    });
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('Plan mining vacío'));
    await desktop.waitForFunction(() => document.getElementById('ps-current-pipeline-status')?.innerText.includes('No hay mining activo que dirigir'));
    await desktop.locator('#ps-add-phase-btn').click();
    await desktop.locator('#psp-num').fill('7');
    await desktop.locator('#psp-name').fill('Fase vacia E2E');
    await desktop.locator('#psp-desc').fill('Debe verse aunque todavia no tenga minings');
    await desktop.locator('#psp-save').click();
    await desktop.waitForFunction(() => {
      const text = document.getElementById('ps-plan-table')?.innerText || '';
      return text.includes('FASE 7') && text.includes('Fase vacia E2E') && text.includes('Fase sin minings todavia');
    });
    const emptyPhasePlanText = await desktop.locator('#ps-plan-table').innerText();
    if (emptyPhasePlanText.includes('Plan mining vacío')) {
      throw new Error('+ Fase should render an empty phase card instead of the empty plan placeholder');
    }
    const cleanPlanState = await desktop.evaluate(() => JSON.parse(localStorage.getItem('sqx_plan_user_v1') || '{}'));
    if (!cleanPlanState.baseDisabled || !Array.isArray(cleanPlanState.hiddenBaseMinings) || cleanPlanState.hiddenBaseMinings.length === 0) {
      throw new Error('Clean project reset should disable and explicitly hide base plan minings');
    }
    const hiddenStrategyCount = await desktop.evaluate(() => JSON.parse(localStorage.getItem('sqx_strategies_deleted_v1') || '[]').length);
    if (hiddenStrategyCount === 0) throw new Error('Clean project reset should hide base strategies from the working view');
    await desktop.evaluate(() => {
      const ok = window.addMiningUser({
        num: 1,
        phase: 1,
        asset: 'XAUUSD',
        tf: 'H1',
        bs: 'BS_Tendencia',
        dir: 'L',
        source: 'manual'
      });
      if (!ok) throw new Error('Manual mining should be allowed after clean reset even when it matches a hidden base seed');
      window.renderPipelineState();
    });
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('XAUUSD'));
    await desktop.waitForFunction(() => {
      const text = document.getElementById('ps-current-pipeline-status')?.innerText || '';
      return text.includes('Foco operativo') && text.includes('XAUUSD H1') && text.includes('BS_Tendencia');
    });
    await desktop.evaluate(() => {
      window.clearPlanUser();
      localStorage.removeItem('sqx_strategies_deleted_v1');
    });
    await desktop.reload({ waitUntil: 'load' });
    await desktop.waitForSelector('.tab[data-tab="workflow"].active');
    await desktop.locator('.tab[data-tab="pipeline"]').click();
    await desktop.waitForSelector('.tab[data-tab="pipeline"].active');
    await desktop.waitForFunction(() => !document.getElementById('ps-plan-table')?.innerText.includes('Plan mining vacío'));
    const miningControlStatusText = await desktop.locator('#ps-current-pipeline-status').innerText();
    const miningControlStatusTextUpper = miningControlStatusText.toUpperCase();
    if (!miningControlStatusText.includes('Foco operativo') || !miningControlStatusTextUpper.includes('MINING 1') || !miningControlStatusTextUpper.includes('LINEAR') || !miningControlStatusTextUpper.includes('XAUUSD H1')) {
      throw new Error('Mining Control should render a dynamic operational focus section');
    }
    if (miningControlStatusText.includes('TEMPLATE LINEAR cerrada')) {
      throw new Error('Mining Control focus should not render the old hardcoded pipeline chronicle');
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
    const pgGuidedText = await desktop.locator('#tab-projectgen').innerText();
    const pgGuidedTextLower = pgGuidedText.toLowerCase();
    ['api local', 'configura sqx', 'elige generación', 'genera y revisa', 'resultado'].forEach(expected => {
      if (!pgGuidedTextLower.includes(expected)) throw new Error(`Project Generator should expose guided section: ${expected}`);
    });
    const pgGuideSteps = await desktop.locator('#tab-projectgen .pg-guide-flow li').count();
    if (pgGuideSteps !== 5) throw new Error(`Project Generator should render 5 guided steps, got ${pgGuideSteps}`);
    if (!pgGuidedText.includes('Plan Mining') || !pgGuidedText.includes('Custom libre')) throw new Error('Project Generator should clarify Plan Mining and Custom libre paths');
    await desktop.evaluate(() => {
      window.resetPlanMiningUserState();
      const ok = window.addMiningUser({ num: 1, phase: 1, asset: 'EURUSD', tf: 'H1', bs: 'BS_Tendencia', dir: 'L/S', source: 'e2e' });
      if (!ok) throw new Error('Project Generator E2E could not seed Plan Mining');
    });
    await desktop.locator('#pg-status-refresh').click();
    await desktop.waitForFunction(() => {
      const text = document.getElementById('pg-minings-table')?.innerText || '';
      return text.includes('EURUSD') && text.includes('USER');
    });
    const pgMiningPlanText = await desktop.locator('#pg-minings-table').innerText();
    if (!pgMiningPlanText.includes('EURUSD') || !pgMiningPlanText.includes('USER')) {
      throw new Error('Project Generator should render active local Plan Mining rows, including user minings');
    }
    await desktop.locator('#pg-select-all-minings').click();
    await desktop.waitForFunction(() => document.getElementById('pg-selected-count')?.textContent.includes('1 seleccionado'));
    await desktop.locator('#pg-clear-selected-minings').click();
    await desktop.waitForFunction(() => document.getElementById('pg-selected-count')?.textContent.includes('0 seleccionados'));
    if (await desktop.locator('#pg-generate-selected-c1').count() !== 1 || await desktop.locator('#pg-minings-table button[data-pg-gen="1"][data-pg-capa="1"]').count() !== 1) {
      throw new Error('Project Generator should expose selected and per-mining generation actions');
    }
    await desktop.waitForFunction(() => document.getElementById('pg-onboarding-steps')?.querySelectorAll('.pg-step').length === 4);
    await desktop.waitForFunction(() => {
      const progress = document.getElementById('pg-onboarding-progress')?.textContent.trim() || '';
      const match = progress.match(/^([0-4])\/4$/);
      return Boolean(match);
    });
    await desktop.waitForSelector('#pg-custom-generate');
    const removedProjectGeneratorPanels = await desktop.locator('#pg-custom-starter-list, #pg-custom-family-list, #pg-buyer-handoff-card').count();
    if (removedProjectGeneratorPanels !== 0) throw new Error('Project Generator removed panels should not be visible in UX-NAV2');
    const cleanerStillVisible = await desktop.locator('#cln-scan').count();
    if (cleanerStillVisible !== 1) throw new Error('Strategy Cleaner should remain available during Project Generator pass');
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
    const guidedHeadings = ['Elige la view que necesitas', 'Revisa la configuración', 'Comprueba la vista', 'Exporta e importa en SQX'];
    const guidedText = await desktop.locator('#tab-views').innerText();
    const guidedTextLower = guidedText.toLowerCase();
    guidedHeadings.forEach(expected => {
      if (!guidedTextLower.includes(expected.toLowerCase())) throw new Error(`SQX Views guided assistant should include step: ${expected}`);
    });
    const defaultClosedDetails = await desktop.evaluate(() => ({
      advanced: document.getElementById('vc-advanced-config')?.open === false,
      metrics: document.getElementById('vc-metrics-details')?.open === false,
    }));
    if (!defaultClosedDetails.advanced || !defaultClosedDetails.metrics) {
      throw new Error('SQX Views advanced settings and metrics editor should start collapsed');
    }
    await desktop.locator('#vc-metrics-details > summary').click();
    await desktop.waitForSelector('#vc-metric-list .views-metric-row');
    await desktop.locator('[data-vc-template-load="egt-first-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '104');
    await desktop.locator('#vc-advanced-config > summary').click();
    await desktop.locator('#vc-year-count').fill('5');
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '64');
    await desktop.locator('[data-vc-template-load="robustness-pack-screen"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Robustez');
    await desktop.waitForFunction(() => document.getElementById('vc-preview-title')?.textContent.trim() === 'Robustez');
    const previewHead = await desktop.locator('.views-preview-panel .views-panel-head').innerText();
    const previewHeadLower = previewHead.toLowerCase();
    if (!previewHeadLower.includes('paso 3') || !previewHead.includes('Comprueba la vista') || !previewHead.includes('Robustez')) {
      throw new Error('SQX Views preview step should show Paso 3, fixed title and selected view subtitle');
    }
    if (previewHead.includes('Paso 3 · Comprueba la vista')) {
      throw new Error('SQX Views preview step should not merge the step label and title');
    }
    await desktop.waitForFunction(() => document.getElementById('vc-active-guide')?.textContent.includes('Robustez'));
    const robustnessGuide = await desktop.locator('#vc-active-guide').innerText();
    ['HBP', 'WFM', 'Siguiente paso'].forEach(expected => {
      if (!robustnessGuide.includes(expected)) throw new Error(`SQX Views Robustez guide should include ${expected}`);
    });
    if (await desktop.locator('#vc-download-btn').count() !== 1) throw new Error('SQX Views should keep one primary .vw download button');
    await desktop.waitForSelector('#vc-template-list .views-template-card');
    const viewsTabText = await desktop.locator('#tab-views').innerText();
    const viewsTabTextUpper = viewsTabText.toUpperCase();
    const viewsTabTextLower = viewsTabText.toLowerCase();
    if (!viewsTabTextUpper.includes('ELIGE LA VIEW QUE NECESITAS')) throw new Error('SQX Views should expose guided view choice as the main entry');
    ['EGT Core', 'Robustez', 'Template Maker Cert', 'Risk', 'Full audit', 'obligatoria', 'recomendable'].forEach(expected => {
      if (!viewsTabText.includes(expected)) throw new Error(`SQX Views required/recommended block should include ${expected}`);
    });
    ['9oos', '7oos'].forEach(expected => {
      if (!viewsTabTextLower.includes(expected)) throw new Error(`SQX Views required/recommended block should include ${expected}`);
    });
    const templateListText = await desktop.locator('#vc-template-list').innerText();
    const templateListTextUpper = templateListText.toUpperCase();
    const templateListTextLower = templateListText.toLowerCase();
    ['PF', 'Trades', 'Ret/DD', 'HBP', 'MC', 'VaR', 'CVaR', 'CAGR/DD', 'CSV Cert'].forEach(expected => {
      if (!templateListTextUpper.includes(expected.toUpperCase())) throw new Error(`SQX Views template tags should include ${expected}`);
    });
    if (/\bfree\b|\bpro\b/i.test(templateListText)) {
      throw new Error('SQX Views template block should not include Free/Pro tags');
    }
    ['s21..', 's23..', '9 anos', '7 anos'].forEach(removed => {
      if (templateListTextLower.includes(removed)) throw new Error(`SQX Views template block should not include retired tag: ${removed}`);
    });
    ['Packs por perfil', 'Flujos por activo/validacion'].forEach(removed => {
      if (viewsTabText.includes(removed)) throw new Error(`SQX Views should not show retired KPI block: ${removed}`);
    });
    if (await desktop.locator('#vc-profile-list, #vc-workflow-pack-list').count() !== 0) {
      throw new Error('SQX Views profile/workflow pack KPI lists should be removed from the visible tab');
    }
    if (await desktop.locator('#vc-saved-details, #vc-advanced-actions, #vc-save-preset-btn, #vc-export-presets-btn, #vc-import-presets-btn').count() !== 0) {
      throw new Error('SQX Views should not expose custom preset or advanced action KPIs');
    }
    if (templateListText.includes('Guardar como preset')) {
      throw new Error('SQX Views guided cards should not expose save-as-preset actions');
    }
    if (viewsTabText.includes('sampleType=127') || viewsTabText.includes('127 total')) {
      throw new Error('SQX Views should explain the consolidated total without raw sampleType jargon');
    }
    const templateCount = await desktop.locator('#vc-template-list .views-template-card').count();
    if (templateCount < 5) throw new Error(`Expected buyer-ready SQX Views examples, got ${templateCount}`);
    await desktop.locator('[data-vc-template-load="template-maker-cert"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Template Maker Cert');
    await desktop.waitForFunction(() => document.getElementById('vc-active-guide')?.textContent.includes('Databank CSV'));
    const certMetrics = await desktop.evaluate(() => window.SQX.viewCreator.getTemplateMakerRequiredMetrics());
    if (!certMetrics.includes('Net profit') || !certMetrics.includes('Ret/DD Ratio')) {
      throw new Error('SQX Views should expose Template Maker Cert required metrics');
    }
    await desktop.locator('[data-vc-template-load="risk-capital-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Risk');
    const buyerPack = await desktop.evaluate(() => window.SQX.viewCreator.buildBuyerReadyTemplatePack());
    if (buyerPack.type !== 'sqx-edge.view-presets' || buyerPack.presets.length < 5) throw new Error('SQX Views buyer-ready pack contract failed');
    const retiredPackApis = await desktop.evaluate(() => ({
      buyerProfile: typeof window.SQX.viewCreator.buildBuyerProfilePack,
      validationWorkflow: typeof window.SQX.viewCreator.buildValidationWorkflowPack,
    }));
    if (retiredPackApis.buyerProfile !== 'undefined' || retiredPackApis.validationWorkflow !== 'undefined') {
      throw new Error('SQX Views retired profile/workflow pack APIs should not remain exposed');
    }
    await desktop.evaluate(() => localStorage.removeItem('sqx_view_creator_presets_v1'));
    await desktop.locator('[data-vc-template-load="risk-capital-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Risk');
    await desktop.locator('#vc-year-count').fill('5');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await saveShot(desktop, 'e2e-view-creator-desktop.png');

    await desktop.locator('.tab[data-tab="templatemaker"]').click();
    await desktop.waitForSelector('.tab[data-tab="templatemaker"].active');
    await desktop.waitForSelector('#tm-csv-input', { state: 'attached' });
    const templateMakerText = await desktop.locator('#tab-templatemaker').innerText();
    ['Template Maker', 'Template Maker Cert', 'Genera la view obligatoria', 'Carga tus fuentes', 'Resuelve el contrato', 'Evalua Perfil Capa 1', 'Resultados y C2', 'Cargar archivos', 'Reset resultados', 'Umbrales KPI editables'].forEach(expected => {
      if (!templateMakerText.includes(expected)) throw new Error(`Template Maker tab should include ${expected}`);
    });
    if (await desktop.locator('#tab-templatemaker [data-tm-capa="2"]').count() !== 0) {
      throw new Error('Template Maker should not expose a Capa 2 analysis control');
    }
    if (templateMakerText.includes('Validacion operable')) {
      throw new Error('Template Maker should keep Capa 2 validation language out of this tab');
    }
    const templateMakerTextLower = templateMakerText.toLowerCase();
    if (!templateMakerTextLower.includes('paso 1') || !templateMakerTextLower.includes('paso 5')) {
      throw new Error('Template Maker should render a five-step guided flow');
    }
    const advancedDefaults = await desktop.evaluate(() => ({
      loads: document.querySelector('.tm-secondary-loads')?.open === false,
      thresholds: document.querySelector('.tm-thresholds-details')?.open === false,
    }));
    if (!advancedDefaults.loads || !advancedDefaults.thresholds) {
      throw new Error('Template Maker advanced loads and thresholds should start collapsed');
    }
    await desktop.locator('.tm-secondary-loads > summary').click();
    const templateMakerSecondaryText = await desktop.locator('#tab-templatemaker').innerText();
    ['Importar CSV', 'Importar .sqx'].forEach(expected => {
      if (!templateMakerSecondaryText.includes(expected)) throw new Error(`Template Maker secondary loads should include ${expected}`);
    });
    await desktop.locator('.tm-secondary-loads > summary').click();
    await desktop.locator('#tm-open-cert-view').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Template Maker Cert');
    await desktop.locator('.tab[data-tab="templatemaker"]').click();
    await desktop.waitForSelector('.tab[data-tab="templatemaker"].active');
    const csvSamplePath = path.join(repoRoot, 'resources', 'template-maker-tool', 'test_capa1.csv');
    await desktop.locator('#tm-files-input').setInputFiles(csvSamplePath);
    await desktop.waitForFunction(() => window.SQX?.templateMaker?.getStrategies().length > 0);
    await desktop.waitForSelector('#tm-results-table:not([hidden])');
    await desktop.waitForFunction(() => document.getElementById('tm-problem-panel')?.textContent.includes('Falta SQX'));
    await desktop.waitForFunction(() => document.getElementById('tm-problem-panel')?.textContent.includes('añade el .sqx original'));
    await desktop.waitForFunction(() => (document.getElementById('tm-contract-summary')?.innerText || '').toLowerCase().includes('falta sqx'));
    const tmAuditAfterCsv = await desktop.evaluate(() => window.SQX.templateMaker.getAuditReport());
    if (tmAuditAfterCsv.total < 1 || tmAuditAfterCsv.passed < 1) {
      throw new Error('Template Maker should show loaded CSV scoring results');
    }
    const csvOnlyStatus = await desktop.evaluate(() => window.SQX.templateMaker.getStrategyStatus(window.SQX.templateMaker.getStrategies()[0]));
    if (csvOnlyStatus !== 'Falta SQX') throw new Error(`CSV-only strategy should show Falta SQX, got ${csvOnlyStatus}`);
    const tmCsvText = await readFile(csvSamplePath, 'utf8');
    await desktop.evaluate(async csvText => {
      const zip = new window.JSZip();
      zip.file('strategy_Portfolio.xml', '<Strategy><options><StrategyName>Strategy 1.15.34(3)</StrategyName></options><Datas><data><symbol>NASDAQ_darwinex</symbol><timeFrame>H1</timeFrame></data></Datas></Strategy>');
      zip.file('settings.xml', '<Settings><ResultsGroup ResultName="Strategy 1.15.34(3)"><Fitnesses FS="1" IS="1" OOS="1"/><Result resultKey="Main: NASDAQ_darwinex/H1"/></ResultsGroup></Settings>');
      const sqxBlob = await zip.generateAsync({ type: 'blob' });
      const csvFile = new File([csvText], 'test_capa1.csv', { type: 'text/csv' });
      const sqxFile = new File([sqxBlob], 'Strategy 1.15.34(3).sqx', { type: 'application/zip' });
      await window.SQX.templateMaker.reset();
      await window.SQX.templateMaker.ingestFiles([csvFile, sqxFile]);
      window.SQX.templateMakerUI.renderAll();
    }, tmCsvText);
    await desktop.waitForFunction(() => window.SQX.templateMaker.getStrategies().some(strategy => window.SQX.templateMaker.getStrategyStatus(strategy) === 'Lista para C2'));
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.innerText.includes('Lista para C2'));
    await desktop.waitForFunction(() => (document.getElementById('tm-contract-summary')?.innerText || '').toLowerCase().includes('lista para c2'));
    await desktop.waitForFunction(() => {
      const wrap = document.querySelector('#tab-templatemaker .tm-results-wrap');
      return wrap && wrap.scrollWidth <= wrap.clientWidth + 2;
    });
    await saveShot(desktop, 'e2e-template-maker-results-desktop.png');
    const enabledC2 = await desktop.locator('#tm-results-table [data-tm-export]:not([disabled])').count();
    if (enabledC2 < 1) throw new Error('Template Maker should enable C2 only for valid PASSED candidates');
    const beforeSelectedDelete = await desktop.evaluate(() => window.SQX.templateMaker.getStrategies().length);
    await desktop.locator('#tm-results-table [data-tm-select]').first().check();
    await desktop.waitForFunction(() => !document.getElementById('tm-delete-selected-btn')?.disabled);
    await desktop.evaluate(() => { window.confirm = () => true; });
    await desktop.locator('#tm-delete-selected-btn').click();
    await desktop.waitForFunction(previous => window.SQX.templateMaker.getStrategies().length === previous - 1, beforeSelectedDelete);
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.hidden === false);
    const afterSelectedDelete = await desktop.evaluate(() => window.SQX.templateMaker.getStrategies().length);
    if (afterSelectedDelete !== beforeSelectedDelete - 1) {
      throw new Error('Template Maker selected delete should remove only checked strategies');
    }
    await saveShot(desktop, 'e2e-template-maker-selected-delete-desktop.png');
    await desktop.waitForFunction(() => window.SQX.templateMaker.getCapa() === 1);
    await desktop.locator('#tm-reset-results-btn').click();
    await desktop.waitForFunction(() => window.SQX.templateMaker.getStrategies().length === 0);
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.hidden === true);
    await desktop.waitForFunction(() => document.getElementById('tm-empty-state')?.hidden === false);
    const enabledC2AfterResultsReset = await desktop.locator('#tm-results-table [data-tm-export]:not([disabled])').count();
    if (enabledC2AfterResultsReset !== 0) throw new Error('Template Maker should remove every C2 action after resetting results');
    await saveShot(desktop, 'e2e-template-maker-results-reset-desktop.png');
    await desktop.locator('#tm-audit-btn').click();
    await desktop.waitForSelector('#tm-modal-audit:not([hidden])');
    await desktop.locator('#tm-audit-close').click();
    await desktop.locator('#tm-reset-btn').click();
    await desktop.waitForFunction(() => window.SQX.templateMaker.getStrategies().length === 0);
    await saveShot(desktop, 'e2e-template-maker-desktop.png');

    await desktop.locator('.tab[data-tab="cvc"]').click();
    await desktop.waitForSelector('.tab[data-tab="cvc"].active');
    await desktop.waitForSelector('#cvc-run-btn');
    const cvcGuidedText = await desktop.locator('#tab-cvc').innerText();
    ['contexto de decisión', 'carga de datos', 'validación rápida', 'ranking operativo', 'entrega y siguiente acción'].forEach(expected => {
      if (!cvcGuidedText.toLowerCase().includes(expected)) throw new Error(`Champion vs Challenger should expose guided section: ${expected}`);
    });
    const cvcGuideSteps = await desktop.locator('#tab-cvc .cvc-guide-flow li').count();
    if (cvcGuideSteps !== 5) throw new Error(`Champion vs Challenger should render 5 guided steps, got ${cvcGuideSteps}`);
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
    await desktop.locator('#cvc-clear-btn').click();
    await desktop.waitForFunction(() => document.getElementById('cvc-empty')?.textContent.includes('Carga CSV') && document.getElementById('cvc-candidate-count')?.textContent.trim() === '0');
    await desktop.locator('#cvc-sample-btn').click();
    await desktop.waitForSelector('#cvc-ranking .cvc-result-row');
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
    const estrategiasText = await desktop.locator('#tab-estrategias').innerText();
    const estrategiasTextLower = estrategiasText.toLowerCase();
    ['repositorio operativo', 'resumen operativo', 'filtra y prioriza', 'repositorio', 'acciones', 'handoff', 'champion vs challenger'].forEach(expected => {
      if (!estrategiasTextLower.includes(expected)) throw new Error(`Strategies tab should include guided repository section: ${expected}`);
    });
    const summaryText = await desktop.locator('#strat-summary').innerText();
    const summaryTextLower = summaryText.toLowerCase();
    ['tier 1', 'candidatas', 'deployed', 'rejected', 'base visible', 'importadas', 'ocultas'].forEach(expected => {
      if (!summaryTextLower.includes(expected)) throw new Error(`Strategies summary should expose ${expected}`);
    });
    const cards = await desktop.locator('#tab-estrategias .strat-card').count();
    const deleteButtons = await desktop.locator('#tab-estrategias .strat-remove-btn').count();
    const sourceBadges = await desktop.locator('#tab-estrategias .strat-source-badge').count();
    if (cards < 1) throw new Error('Strategies tab rendered without strategy cards');
    if (cards !== deleteButtons) throw new Error(`Expected one delete button per card, got ${cards} cards and ${deleteButtons} buttons`);
    if (sourceBadges !== cards) throw new Error(`Expected one source badge per card, got ${sourceBadges} badges and ${cards} cards`);

    const firstStrategyId = await desktop.locator('#tab-estrategias .strat-card .sc-id').first().innerText();
    await desktop.locator('#strat-search').fill(firstStrategyId.trim());
    await desktop.waitForFunction(() => document.querySelectorAll('#tab-estrategias .strat-card').length >= 1);
    await desktop.waitForFunction(() => document.getElementById('strat-filter-count')?.textContent.includes('visibles de'));
    await desktop.locator('#strat-search').fill('');
    await desktop.locator('#tab-estrategias [data-strat-tier="1"]').click();
    await desktop.waitForFunction(() => document.getElementById('strat-filter-count')?.textContent.includes('visibles de'));
    await desktop.locator('#strat-filter-status').selectOption('PASSED');
    await desktop.waitForFunction(() => document.getElementById('strat-filter-count')?.textContent.includes('visibles de'));
    const firstTemplateOption = await desktop.evaluate(() => {
      const select = document.getElementById('strat-filter-template');
      return Array.from(select.options).find(option => option.value !== 'all')?.value || 'all';
    });
    await desktop.locator('#strat-filter-template').selectOption(firstTemplateOption);
    await desktop.waitForFunction(() => document.getElementById('strat-filter-count')?.textContent.includes('visibles de'));
    await desktop.locator('#tab-estrategias [data-strat-tier="all"]').click();
    await desktop.locator('#strat-filter-status').selectOption('all');
    await desktop.locator('#strat-filter-template').selectOption('all');
    await desktop.waitForSelector('#tab-estrategias .strat-card');

    await desktop.locator('#tab-estrategias .strat-remove-btn').first().click();
    await desktop.waitForFunction(() => localStorage.getItem('sqx_strategies_deleted_v1') !== null);
    const afterDelete = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterDelete !== cards - 1) throw new Error(`Deleting a base strategy should hide exactly one card, got ${afterDelete} from ${cards}`);
    await desktop.locator('#strat-restore-hidden-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_deleted_v1') || '[]').length === 0);
    const afterRestore = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterRestore !== cards) throw new Error(`Restoring hidden strategies should recover cards, got ${afterRestore} from ${cards}`);

    await desktop.locator('#strat-import-btn').click();
    await desktop.locator('#strat-import-file').setInputFiles(csvSamplePath);
    await desktop.waitForSelector('#csv-file-info');
    await desktop.locator('#csv-next-btn').click();
    await desktop.waitForSelector('#csv-pane-2.active');
    await desktop.locator('#csv-next-btn').click();
    await desktop.waitForSelector('#csv-pane-3.active');
    await desktop.locator('#csv-select-top10').click();
    await desktop.locator('#csv-next-btn').click();
    await desktop.waitForSelector('#csv-pane-4.active');
    await desktop.locator('#csv-finish-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_user_v1') || '[]').length > 0);
    await desktop.waitForFunction(() => document.getElementById('strat-summary')?.textContent.includes('Importadas'));
    await desktop.locator('#strat-clear-user-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_user_v1') || '[]').length === 0);

    await saveShot(desktop, 'e2e-strategies-desktop.png');
    await desktop.locator('#strat-open-cvc-btn').click();
    await desktop.waitForSelector('.tab[data-tab="cvc"].active');
    await desktop.locator('.tab[data-tab="estrategias"]').click();
    await desktop.waitForSelector('.tab[data-tab="estrategias"].active');
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
    await mobile.locator('.tab[data-tab="projectgen"]').click();
    await mobile.waitForSelector('.tab[data-tab="projectgen"].active');
    await mobile.waitForSelector('#pg-custom-generate');
    const mobilePgGuideSteps = await mobile.locator('#tab-projectgen .pg-guide-flow li').count();
    if (mobilePgGuideSteps !== 5) throw new Error('Mobile Project Generator guided flow should render 5 steps');
    await assertNoMobileOverflow(mobile);
    await saveShot(mobile, 'e2e-projectgen-mobile.png');
    await mobile.locator('.tab[data-tab="views"]').click();
    await mobile.waitForSelector('#vc-preview');
    await assertNoMobileOverflow(mobile);
    await saveShot(mobile, 'e2e-view-creator-mobile.png');
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
