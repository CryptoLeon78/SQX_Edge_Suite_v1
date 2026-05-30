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

async function acceptDecision(page) {
  const visible = await page.locator('#sqx-decision-backdrop').evaluate(node => node && getComputedStyle(node).display !== 'none').catch(() => false);
  if (visible) await page.locator('#sqx-decision-confirm').click();
}

async function openTab(page, tabId) {
  const visibleTab = page.locator(`.tab[data-tab="${tabId}"]`);
  if (await visibleTab.count()) {
    await visibleTab.click();
  } else {
    const ok = await page.evaluate(id => window.SQX?.ui?.activateTabById(id), tabId);
    if (!ok) throw new Error(`Could not activate tab ${tabId}`);
  }
  await page.waitForFunction(id => {
    const panel = document.getElementById(`tab-${id}`);
    return panel && getComputedStyle(panel).display !== 'none';
  }, tabId);
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
    await desktop.waitForSelector('#edge-factory-shell');
    await desktop.evaluate(() => {
      const localModel = window.SQX.home.computeRemoteServiceModel({});
      window.SQX.home.applyRemoteServiceModel(localModel, document);
    });
    const welcomeInitiallyHidden = await desktop.locator('#remote-welcome-gate').evaluate(node => node.hidden);
    if (!welcomeInitiallyHidden) throw new Error('Remote welcome gate should stay hidden in local file mode');
    const trustCenterCopy = await desktop.locator('#remote-trust-center').textContent();
    ['SQX Edge Suite Security Self-Assessment', 'Privacy & Data Handling Statement', 'Remote Service Safety Checklist'].forEach(expected => {
      if (!trustCenterCopy.includes(expected)) throw new Error(`Trust Center should include ${expected}`);
    });
    await desktop.evaluate(() => {
      sessionStorage.removeItem('sqx_remote_welcome_dismissed_v1');
      const pendingModel = window.SQX.home.computeRemoteServiceModel({
        access: {
          mode: 'remote_tunnel_only',
          authenticated: true,
          access: { allowed: true, reason: 'access_allowed', feature_scope: 'full' },
          entitlement: { kind: 'tester_free', status: 'active', feature_scope: 'full', grant_key_configured: true, grant_key_required: false },
        },
        session: { session: { active: false }, access: { allowed: false, reason: 'session_missing' } },
        workspace: { ok: false, workspace: {} },
        security: {
          ok: true,
          killSwitch: { active: false },
          revocation: { currentSessionRevoked: false },
          blocking: { currentIdentityBlocked: false },
          watermark: { enabled: true, label: 'SQX REMOTE PRO', marker: 'demo' },
        },
        health: {
          ok: true,
          sqx_path_set: true,
          data_db_exists: true,
          templates_capa1_exists: true,
          templates_capa2_exists: true,
        },
      });
      window.SQX.home.applyRemoteServiceModel(pendingModel, document);
      window.SQX.home.bindRemoteWelcomeGate(document);
    });
    await desktop.waitForSelector('#remote-welcome-gate:not([hidden])');
    const pendingWelcomeText = await desktop.locator('#remote-welcome-gate').innerText();
    ['Acceso DASHBOARD', 'OK identidad validada', 'workspace privado', 'Listo al entrar', 'Trust Center', 'Sin instalacion local', 'productividad', 'QXPro'].forEach(expected => {
      if (!pendingWelcomeText.includes(expected)) throw new Error(`Remote welcome gate should explain ${expected}`);
    });
    if (pendingWelcomeText.includes('falta crear la sesion de app')) {
      throw new Error('Remote welcome should not expose internal app-session wording to testers');
    }
    if (pendingWelcomeText.includes('OK identidad validada. Pulsa Acceso DASHBOARD')) {
      throw new Error('Remote welcome should not repeat OK identidad validada in the body copy');
    }
    const pendingWelcomeAction = await desktop.locator('#remote-welcome-primary').evaluate(node => node.dataset.remoteWelcomeAction);
    if (pendingWelcomeAction !== 'login') throw new Error(`Remote welcome primary action should login, got ${pendingWelcomeAction}`);
    const welcomeKeyCount = await desktop.locator('#remote-welcome-grant-key').count();
    if (welcomeKeyCount !== 0) throw new Error('Remote welcome should not ask approved testers for a second key');
    await desktop.locator('#remote-welcome-trust-toggle').click();
    await desktop.waitForSelector('#remote-trust-center:not([hidden])');
    await desktop.evaluate(() => {
      const activeModel = window.SQX.home.computeRemoteServiceModel({
        access: {
          mode: 'remote_tunnel_only',
          authenticated: true,
          access: { allowed: true, reason: 'access_allowed', feature_scope: 'full' },
          entitlement: { kind: 'tester_free', status: 'active', feature_scope: 'full' },
        },
        session: {
          session: { active: true, entitlement_kind: 'tester_free' },
          access: { allowed: true, reason: 'session_active', feature_scope: 'full' },
        },
        workspace: { ok: true, workspace: { id: 'ws_demo_remote_123456' } },
        security: {
          ok: true,
          killSwitch: { active: false },
          revocation: { currentSessionRevoked: false },
          blocking: { currentIdentityBlocked: false },
          watermark: { enabled: true, label: 'SQX REMOTE PRO', marker: 'demo' },
        },
        health: {
          ok: true,
          sqx_path_set: true,
          data_db_exists: true,
          templates_capa1_exists: true,
          templates_capa2_exists: true,
        },
      });
      window.SQX.home.applyRemoteServiceModel(activeModel, document);
    });
    await desktop.waitForFunction(() => document.getElementById('remote-welcome-primary')?.dataset.remoteWelcomeAction === 'enter');
    const activeWelcomeText = await desktop.locator('#remote-welcome-gate').innerText();
    if (!activeWelcomeText.includes('OK todo validado')) throw new Error('Remote welcome should confirm OK todo validado before dashboard access');
    await desktop.locator('#remote-welcome-primary').click();
    await desktop.waitForFunction(() => document.getElementById('remote-welcome-gate')?.hidden === true);
    await desktop.waitForFunction(() => {
      const mark = document.querySelector('.brand-mark');
      return mark && mark.complete && mark.naturalWidth >= 64;
    });
    const sidebarBrandImage = await desktop.locator('#main-tabs').evaluate(node => getComputedStyle(node, '::before').backgroundImage);
    if (!sidebarBrandImage.includes('sqx-favicon.png')) throw new Error('Sidebar brand should use the SQX favicon asset');
    const workflowWatermark = await desktop.locator('#tab-workflow').evaluate(node => getComputedStyle(node, '::before').backgroundImage);
    if (!workflowWatermark.includes('sqx-tab-watermark.png')) throw new Error('Tabs should render the SQX watermark asset');
    const workflowMethodIcon = await desktop.locator('#edge-factory-shell .workflow-command-eyebrow').evaluate(node => getComputedStyle(node, '::before').backgroundImage);
    if (!workflowMethodIcon.includes('sqx-internal-pipeline-icon.png')) throw new Error('Workflow should render the internal SQX pipeline icon');
    const categoryTabCount = await desktop.locator('.tab[data-tab="categorias"]').count();
    if (categoryTabCount !== 0) throw new Error('Por Categoria should not be a primary tab');
    const priorityTabCount = await desktop.locator('.tab[data-tab="priority"]').count();
    if (priorityTabCount !== 0) throw new Error('Priority should not be a primary navigation section');
    const sidebarOrder = await desktop.locator('#main-tabs .tab').evaluateAll(nodes => nodes.map(node => node.dataset.tab));
    const expectedSidebarOrder = ['workflow', 'inicio'];
    if (sidebarOrder.join('|') !== expectedSidebarOrder.join('|')) {
      throw new Error(`Primary navigation should show only Edge Factory and Control Panel: ${sidebarOrder.join('|')}`);
    }
    const sidebarModel = await desktop.locator('#main-tabs .tab').evaluateAll(nodes => nodes.map(node => ({
      id: node.dataset.tab,
      label: node.querySelector('.tab-label')?.textContent.trim(),
      icon: node.querySelector('.tab-icon')?.textContent.trim(),
    })));
    const expectedSidebarModel = {
      workflow: ['Edge Factory', 'EF'],
      inicio: ['Control Panel', 'C'],
    };
    sidebarModel.forEach(item => {
      const expected = expectedSidebarModel[item.id];
      if (!expected || item.label !== expected[0] || item.icon !== expected[1]) {
        throw new Error(`Navigation item ${item.id} should render ${expected?.join('/')} but got ${item.label}/${item.icon}`);
      }
    });
    await desktop.locator('#tabs-collapse-toggle').click();
    await desktop.waitForSelector('body.nav-collapsed');
    const collapsedNavWidth = await desktop.locator('#main-tabs').evaluate(node => Math.round(node.getBoundingClientRect().width));
    if (collapsedNavWidth > 90) throw new Error(`Collapsed navigation should leave only icons, got ${collapsedNavWidth}px`);
    await saveShot(desktop, 'e2e-navigation-collapsed-desktop.png');
    await desktop.locator('#tabs-collapse-toggle').click();
    await desktop.waitForFunction(() => !document.body.classList.contains('nav-collapsed'));
    await openTab(desktop, 'filtros');
    await desktop.waitForSelector('#filtros-view .bs-card');
    const blockSettingsText = await desktop.locator('#tab-filtros').innerText();
    [
      'Biblioteca metodológica de BlockSettings SQX',
      'Capa 1 · Buscar Edge',
      'Capa 2 · Filtros operativos',
      'BS_Filtros_v6',
      'BS_Filtros_v6_D1',
      'Calibración normalizada',
      'Cómo se conecta con el flujo',
    ].forEach(expected => {
      if (!blockSettingsText.includes(expected)) throw new Error(`BlockSettings Info should include ${expected}`);
    });
    const capa1Blocks = await desktop.locator('#filtros-view .bs-card').count();
    if (capa1Blocks !== 7) throw new Error(`BlockSettings Info should render 7 Capa 1 cards, got ${capa1Blocks}`);
    const capa2Filters = await desktop.locator('#filtros-view .bs-filter-card').count();
    if (capa2Filters !== 6) throw new Error(`BlockSettings Info should render 6 Capa 2 filter cards, got ${capa2Filters}`);
    if (blockSettingsText.includes('Umbrales recomendados para la segunda fase de filtrado')) {
      throw new Error('BlockSettings Info should not render the old generic Help copy');
    }
    await saveShot(desktop, 'e2e-blocksettings-info-desktop.png');
    await openTab(desktop, 'workflow');
    const strategyBuilderTabCount = await desktop.locator('.tab[data-tab="strategybuilder"]').count();
    if (strategyBuilderTabCount !== 0) throw new Error('Strategy Builder should not be a primary navigation section');
    const edgeFactoryPrimaryText = await desktop.locator('#edge-factory-shell').evaluate(node => node.textContent || '');
    if (edgeFactoryPrimaryText.includes('Strategy Builder')) throw new Error('Edge Factory should not expose Strategy Builder');
    ['Strategy Control', 'Champion vs Challenger'].forEach(expected => {
      if (!edgeFactoryPrimaryText.includes(expected)) throw new Error(`Edge Factory should expose ${expected} as guided/advanced access`);
    });
    await openTab(desktop, 'pipeline');
    const retiredMiningInfoCards = await desktop.locator('#ps-current-pipeline-status, #ps-orphans-card, #ps-plan-user-info').count();
    if (retiredMiningInfoCards !== 0) throw new Error('Mining Control should not render retired focus/preload info cards');
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
    await acceptDecision(desktop);
    await desktop.waitForFunction(() => !document.getElementById('ps-plan-table')?.innerText.includes('Fase editable E2E'));
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('Plan mining vacío'));
    await desktop.evaluate(() => window.quickAddToPlan('EURUSD', 'momentum', 'M15, M30, H1', 'L/S'));
    await desktop.waitForSelector('#tf-select-backdrop[style*="flex"]');
    await desktop.locator('#tf-select-options [data-tf="M30"]').click();
    await desktop.locator('#tf-select-confirm').click();
    await desktop.waitForFunction(() => {
      const text = document.getElementById('ps-plan-table')?.innerText || '';
      return text.includes('EURUSD') && text.includes('M30');
    });
    const unifiedPlanText = await desktop.locator('#ps-plan-card').innerText();
    if (!unifiedPlanText.includes('EURUSD') || !unifiedPlanText.includes('TARJETA') || !unifiedPlanText.includes('M30')) {
      throw new Error('Added asset-card mining should join the unified Plan mining table with selected timeframe and TARJETA source tag');
    }
    const tfTraceState = await desktop.evaluate(() => {
      const state = JSON.parse(localStorage.getItem('sqx_plan_user_v1') || '{}');
      const mining = (state.minings || []).find(item => item.asset === 'EURUSD' && item.tf === 'M30');
      return mining ? {
        selectedTimeframe: mining.selectedTimeframe,
        timeframeSource: mining.timeframeSource,
        availableTimeframes: mining.availableTimeframes,
        blocksetting: mining.blocksettingTrace && mining.blocksettingTrace.canonicalId
      } : null;
    });
    if (!tfTraceState || tfTraceState.selectedTimeframe !== 'M30' || tfTraceState.timeframeSource !== 'card-selection' || !tfTraceState.blocksetting) {
      throw new Error('Asset-card mining should persist selected timeframe trace and real BlockSetting trace');
    }
    const edgeFactoryCardState = await desktop.evaluate(() => {
      const state = JSON.parse(localStorage.getItem('sqx_edge_factory_state_v1') || '{}');
      return {
        card: state.selectedCard,
        mining: state.selectedMining,
        activeStep: state.activeStep,
        completedSteps: state.completedSteps || []
      };
    });
    if (!edgeFactoryCardState.card || edgeFactoryCardState.card.asset !== 'EURUSD' || edgeFactoryCardState.card.timeframe !== 'M30') {
      throw new Error('Edge Factory should inherit selected card context from Activos -> Plan Mining');
    }
    if (!edgeFactoryCardState.mining || edgeFactoryCardState.mining.asset !== 'EURUSD' || edgeFactoryCardState.mining.timeframe !== 'M30') {
      throw new Error('Edge Factory should persist the selected mining handoff');
    }
    if (!edgeFactoryCardState.completedSteps.includes('asset') || edgeFactoryCardState.activeStep !== 'capa1-generate') {
      throw new Error('Edge Factory should advance from card selection to Capa 1 generation');
    }
    if (unifiedPlanText.includes('Plan extendido') || unifiedPlanText.includes('Precarga desde Por Activo')) {
      throw new Error('Mining Control should not keep retired plan preload showcase copy');
    }
    await desktop.locator('#ps-plan-table .ps-phase-reset-btn').first().click();
    await acceptDecision(desktop);
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('Fase sin minings todavia'));
    await desktop.evaluate(() => {
      window.resetProjectWorkingData();
      window.renderPipelineState();
    });
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('Plan mining vacío'));
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
        bs: 'BS_Tendencia_v6',
        dir: 'L',
        source: 'manual'
      });
      if (!ok) throw new Error('Manual mining should be allowed after clean reset even when it matches a hidden base seed');
      window.renderPipelineState();
    });
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('XAUUSD'));
    await desktop.waitForFunction(() => document.getElementById('ps-plan-table')?.innerText.includes('MANUAL'));
    await desktop.evaluate(() => {
      window.clearPlanUser();
      localStorage.removeItem('sqx_strategies_deleted_v1');
    });
    await desktop.reload({ waitUntil: 'load' });
    await desktop.waitForSelector('.tab[data-tab="workflow"].active');
    await openTab(desktop, 'pipeline');
    await desktop.waitForFunction(() => !document.getElementById('ps-plan-table')?.innerText.includes('Plan mining vacío'));
    const miningControlText = await desktop.locator('#tab-pipeline').innerText();
    const miningControlTextUpper = miningControlText.toUpperCase();
    if (!miningControlTextUpper.includes('MINING 1') || !miningControlTextUpper.includes('XAUUSD') || !miningControlTextUpper.includes('BS_TENDENCIA')) {
      throw new Error('Mining Control plan should render the restored base plan as the operational source of truth');
    }
    if (miningControlText.includes('Foco operativo') || miningControlText.includes('Precarga desde Por Activo') || miningControlText.includes('Plan extendido')) {
      throw new Error('Mining Control should not render retired focus/preload sections');
    }
    if (miningControlText.includes('TEMPLATE LINEAR cerrada')) {
      throw new Error('Mining Control should not render the old hardcoded pipeline chronicle');
    }
    await saveShot(desktop, 'e2e-mining-control-status-desktop.png');
    await openTab(desktop, 'workflow');
    await desktop.waitForSelector('[data-edge-mode="basic"].active');
    if (await desktop.locator('#edge-tools-toggle:visible').count() !== 0) {
      throw new Error('Edge Factory basic mode should hide the advanced tools toggle');
    }
    await desktop.locator('[data-edge-mode="advanced"]').click();
    await desktop.waitForSelector('[data-edge-mode="advanced"].active');
    await desktop.locator('input[data-edge-complete="session"]').check();
    await desktop.waitForFunction(() => {
      const state = JSON.parse(localStorage.getItem('sqx_edge_factory_state_v1') || '{}');
      return (state.completedSteps || []).includes('session') && document.getElementById('edge-factory-progress-label')?.textContent.includes('de 8');
    });
    await openTab(desktop, 'inicio');
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
    await openTab(desktop, 'pipeline');
    await openTab(desktop, 'activos');
    await desktop.locator('[data-filter-type="forex"]').click();
    await desktop.waitForSelector('[data-filter-type="forex"].active');
    await desktop.fill('#search-asset', 'EUR');
    await desktop.waitForSelector('#asset-grid .asset-card');
    await desktop.evaluate(() => navToAsset('EURUSD'));
    await desktop.waitForSelector('#detail-panel.visible');
    await openTab(desktop, 'workflow');
    await desktop.waitForSelector('#edge-factory-shell');
    const edgeFactoryText = await desktop.locator('#edge-factory-shell').evaluate(node => node.textContent || '');
    [
      'Punto de partida',
      'Elegir edge',
      'Generar Capa 1',
      'Certificar Capa 1',
      'Crear Template C2',
      'Generar Capa 2',
      'Revisar Capa 2',
      'Portfolio',
      'Custom libre avanzado',
    ].forEach(expected => {
      if (!edgeFactoryText.includes(expected)) throw new Error(`Edge Factory should expose stage: ${expected}`);
    });
    const hiddenLegacyWorkflow = await desktop.locator('#workflow-command-center').evaluate(node => getComputedStyle(node).display === 'none');
    if (!hiddenLegacyWorkflow) throw new Error('Legacy Workflow command center should be hidden behind Edge Factory');
    const edgeStageCount = await desktop.locator('#edge-factory-stages .edge-stage-card').count();
    if (edgeStageCount !== 8) throw new Error(`Edge Factory should render 8 stages, got ${edgeStageCount}`);
    const edgeContextCount = await desktop.locator('#edge-factory-stages [data-edge-context]').count();
    if (edgeContextCount !== 8) throw new Error(`Edge Factory should render 8 handoff context strips, got ${edgeContextCount}`);
    await desktop.locator('[data-edge-mode="advanced"]').click();
    await desktop.locator('input[data-edge-complete="asset"]').check();
    await desktop.waitForFunction(() => (JSON.parse(localStorage.getItem('sqx_edge_factory_state_v1') || '{}').completedSteps || []).includes('asset'));
    await desktop.locator('#edge-tools-toggle').click();
    await desktop.waitForSelector('#edge-tool-drawer:not([hidden])');
    const drawerToolCount = await desktop.locator('#edge-tool-drawer .edge-tool-card').count();
    if (drawerToolCount !== 8) throw new Error(`Edge Factory advanced drawer should expose 8 tools, got ${drawerToolCount}`);
    await desktop.locator('#edge-portfolio-sample').click();
    await desktop.locator('#edge-portfolio-run').click();
    await desktop.waitForFunction(() => document.getElementById('edge-portfolio-results')?.innerText.toUpperCase().includes('PORTFOLIO'));
    await desktop.waitForFunction(() => document.getElementById('edge-portfolio-results')?.innerText.toUpperCase().includes('SIMILAR'));
    await desktop.waitForFunction(() => {
      const state = JSON.parse(localStorage.getItem('sqx_edge_factory_state_v1') || '{}');
      return state.portfolioLab &&
        state.portfolioLab.winners > 0 &&
        state.portfolioMasterContract &&
        state.portfolioMasterContract.status === 'blocked_pending_operator_inputs' &&
        !(state.completedSteps || []).includes('portfolio');
    });
    await desktop.locator('#edge-portfolio-export-csv').click();
    await saveShot(desktop, 'e2e-edge-factory-desktop.png');
    await openTab(desktop, 'views');
    await desktop.evaluate(() => window.SQX.viewCreator.loadBuyerReadyTemplate('robustness-pack-screen'));
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Robustez');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 104);
    await openTab(desktop, 'projectgen');
    await desktop.waitForSelector('#pg-step-api');
    const pgGuidedText = await desktop.locator('#tab-projectgen').innerText();
    const pgGuidedTextLower = pgGuidedText.toLowerCase();
    ['conexión', 'entorno sqx', 'elige generación', 'genera y revisa', 'resultado'].forEach(expected => {
      if (!pgGuidedTextLower.includes(expected)) throw new Error(`Project Generator should expose guided section: ${expected}`);
    });
    ['paths sqx', 'sqx path:', 'http://127.0.0.1', 'localhost', 'ruta de instalacion'].forEach(forbidden => {
      if (pgGuidedTextLower.includes(forbidden)) throw new Error(`Project Generator should not expose internal service detail: ${forbidden}`);
    });
    if (await desktop.locator('#tab-projectgen .pg-service-readiness-grid').count() !== 1) {
      throw new Error('Project Generator should show a route-free service readiness grid');
    }
    const pgGuideSteps = await desktop.locator('#tab-projectgen .pg-guide-flow li').count();
    if (pgGuideSteps !== 5) throw new Error(`Project Generator should render 5 guided steps, got ${pgGuideSteps}`);
    if (!pgGuidedTextLower.includes('plan mining') || !pgGuidedTextLower.includes('custom libre')) throw new Error('Project Generator should clarify Plan Mining and Custom libre paths');
    const pgClosedSteps = await desktop.locator('#tab-projectgen details.pg-step-panel:not([open])').count();
    if (pgClosedSteps !== 5) throw new Error(`Project Generator steps should start closed, got ${pgClosedSteps} closed`);
    await desktop.locator('#pg-step-choice > summary').click();
    await desktop.locator('#pg-mode-methodological').click();
    await desktop.waitForSelector('#pg-step-generate[open]');
    await desktop.waitForSelector('#pg-mode-methodological-panel:not([hidden])');
    if (await desktop.locator('#pg-mode-manual-panel:not([hidden])').count() !== 0) {
      throw new Error('Project Generator should hide manual workspace when methodological generation is active');
    }
    if (await desktop.locator('#pg-gen-all-c1, #pg-gen-all-c2').count() !== 0) {
      throw new Error('Project Generator should remove bulk-all generation buttons');
    }
    await desktop.evaluate(() => {
      window.resetPlanMiningUserState();
      const key = window.SQX?.projectGenerator?.outputResetStorageKey;
      const resetState = key ? JSON.parse(localStorage.getItem(key) || '{}') : {};
      if (resetState.reason !== 'plan-mining-reset') throw new Error('Plan Mining reset should reset the generated CFX session');
      const outputText = document.getElementById('pg-output-list')?.innerText || '';
      const logText = document.getElementById('pg-log')?.textContent || '';
      if (!outputText.includes('No hay .cfx') || !logText.includes('nueva sesión')) {
        throw new Error('Plan Mining reset should clear Project Generator CFX list and log context');
      }
      const ok = window.addMiningUser({ num: 1, phase: 1, asset: 'EURUSD', tf: 'H1', bs: 'BS_Tendencia_v6', dir: 'L/S', source: 'e2e' });
      if (!ok) throw new Error('Project Generator E2E could not seed Plan Mining');
    });
    await desktop.locator('#pg-step-api > summary').click();
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
    if (await desktop.locator('#pg-generate-selected-c1').count() !== 1 || await desktop.locator('#pg-minings-table button[data-pg-gen]').count() !== 0) {
      throw new Error('Project Generator should expose selected generation and remove per-row generation buttons');
    }
    await desktop.waitForFunction(() => document.getElementById('pg-onboarding-steps')?.querySelectorAll('.pg-step').length === 4);
    await desktop.waitForFunction(() => {
      const progress = document.getElementById('pg-onboarding-progress')?.textContent.trim() || '';
      const match = progress.match(/^([0-4])\/4$/);
      return Boolean(match);
    });
    const removedProjectGeneratorPanels = await desktop.locator('#pg-custom-starter-list, #pg-custom-family-list, #pg-buyer-handoff-card').count();
    if (removedProjectGeneratorPanels !== 0) throw new Error('Project Generator removed panels should not be visible in UX-NAV2');
    const cleanerStillVisible = await desktop.locator('#cln-scan').count();
    if (cleanerStillVisible !== 1) throw new Error('Strategy Cleaner should remain available during Project Generator pass');
    await desktop.locator('#pg-mode-manual').click();
    await desktop.waitForSelector('#pg-mode-manual-panel:not([hidden]) #pg-custom-generate');
    if (await desktop.locator('#pg-mode-methodological-panel:not([hidden])').count() !== 0) {
      throw new Error('Project Generator should hide Plan Mining workspace when manual generation is active');
    }
    await desktop.evaluate(() => window.quickToProjectGen('AUDCAD', 'momentum', 'M15, M30, H1', 'L/S'));
    await desktop.waitForSelector('#tf-select-backdrop[style*="flex"]');
    await desktop.locator('#tf-select-options [data-tf="M30"]').click();
    await desktop.locator('#tf-select-confirm').click();
    await desktop.waitForFunction(() => document.getElementById('pg-custom-tf')?.value === 'M30');
    await desktop.waitForFunction(() => document.getElementById('pg-custom-bs')?.value === 'BS_Momentum_v6');
    const pgTfTraceStatus = await desktop.locator('#pg-custom-status').innerText();
    if (!pgTfTraceStatus.includes('timeframe M30 confirmado')) {
      throw new Error('Project Generator card prefill should announce selected timeframe trace');
    }
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
    await openTab(desktop, 'views');
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
    ['TICK REAL', 'WFM', 'Siguiente paso'].forEach(expected => {
      if (!robustnessGuide.includes(expected)) throw new Error(`SQX Views Robustez guide should include ${expected}`);
    });
    if (await desktop.locator('#vc-download-btn').count() !== 1) throw new Error('SQX Views should keep one primary .vw download button');
    await desktop.waitForSelector('#vc-template-list .views-template-card');
    const viewsTabText = await desktop.locator('#tab-views').innerText();
    const viewsTabTextUpper = viewsTabText.toUpperCase();
    const viewsTabTextLower = viewsTabText.toLowerCase();
    if (!viewsTabTextUpper.includes('ELIGE LA VIEW QUE NECESITAS')) throw new Error('SQX Views should expose guided view choice as the main entry');
    ['EGT Core', 'Robustez', 'SQX EDGE CORRELATION REVIEW', 'CVC Decision Cert', 'Risk', 'Full audit', 'obligatoria', 'recomendable'].forEach(expected => {
      if (!viewsTabText.includes(expected)) throw new Error(`SQX Views required/recommended block should include ${expected}`);
    });
    ['9oos', '7oos'].forEach(expected => {
      if (!viewsTabTextLower.includes(expected)) throw new Error(`SQX Views required/recommended block should include ${expected}`);
    });
    const templateListText = await desktop.locator('#vc-template-list').innerText();
    const templateListTextUpper = templateListText.toUpperCase();
    const templateListTextLower = templateListText.toLowerCase();
    ['PF', 'Trades', 'Ret/DD', 'TICK REAL', 'MC', 'VaR', 'CVaR', 'CAGR/DD', 'CORR1', 'Decision', 'Arquetipo', 'Volatilidad'].forEach(expected => {
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
    await desktop.locator('[data-vc-template-load="sqx-edge-correlation-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX EDGE CORRELATION REVIEW');
    await desktop.waitForFunction(() => document.getElementById('vc-active-guide')?.textContent.includes('Databank CSV'));
    const certMetrics = await desktop.evaluate(() => window.SQX.viewCreator.getTemplateMakerRequiredMetrics());
    if (!certMetrics.includes('Profit factor') || !certMetrics.includes('Ret/DD Ratio') || !certMetrics.includes('SQX Edge Corr Decision')) {
      throw new Error('SQX Views should expose SQX Edge Correlation Review metrics for Template Maker C2');
    }
    await desktop.locator('[data-vc-template-load="cvc-decision-cert"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'CVC Decision Cert');
    const cvcCertMetrics = await desktop.evaluate(() => window.SQX.viewCreator.getCvcDecisionRequiredMetrics());
    if (!cvcCertMetrics.includes('Avg. Bars in Trade') || !cvcCertMetrics.includes('Avg. Trades Per Month')) {
      throw new Error('SQX Views should expose CVC Decision Cert required metrics');
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

    await openTab(desktop, 'templatemaker');
    await desktop.waitForSelector('#tm-csv-input', { state: 'attached' });
    const templateMakerText = await desktop.locator('#tab-templatemaker').innerText();
    ['Template Maker', 'SQX EDGE CORRELATION REVIEW', 'Genera la view obligatoria', 'Carga tus fuentes', 'Resuelve el contrato', 'Evalua Perfil Capa 1', 'Resultados y C2', 'Cargar archivos', 'Reset resultados', 'Umbrales KPI editables'].forEach(expected => {
      if (!templateMakerText.includes(expected)) throw new Error(`Template Maker tab should include ${expected}`);
    });
    if (!templateMakerText.includes('Descorrelación de templates')) {
      throw new Error('Template Maker should include diversity controls before C2');
    }
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
      diversity: document.querySelector('.tm-diversity-details')?.open === false,
    }));
    if (!advancedDefaults.loads || !advancedDefaults.thresholds || !advancedDefaults.diversity) {
      throw new Error('Template Maker advanced loads and thresholds should start collapsed');
    }
    await desktop.locator('.tm-secondary-loads > summary').click();
    const templateMakerSecondaryText = await desktop.locator('#tab-templatemaker').innerText();
    ['Importar CSV', 'Importar .sqx'].forEach(expected => {
      if (!templateMakerSecondaryText.includes(expected)) throw new Error(`Template Maker secondary loads should include ${expected}`);
    });
    await desktop.locator('.tm-secondary-loads > summary').click();
    await desktop.locator('#tm-open-cert-view').click();
    await desktop.waitForFunction(() => getComputedStyle(document.getElementById('tab-views')).display !== 'none');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX EDGE CORRELATION REVIEW');
    await openTab(desktop, 'templatemaker');
    const csvSamplePath = path.join(repoRoot, 'resources', 'template-maker-tool', 'template_maker_cert_v2_sample.csv');
    const sqxSamplePaths = [
      path.join(repoRoot, 'resources', 'template-maker-tool', 'Strategy TM.01.sqx'),
      path.join(repoRoot, 'resources', 'template-maker-tool', 'Strategy TM ExitPolicy.sqx'),
      path.join(repoRoot, 'resources', 'template-maker-tool', 'Strategy TM.03.sqx'),
    ];
    await desktop.locator('#tm-files-input').setInputFiles(csvSamplePath);
    await desktop.waitForFunction(() => window.SQX?.templateMaker?.getStrategies().length > 0);
    await desktop.waitForSelector('#tm-results-table:not([hidden])');
    await desktop.waitForFunction(() => document.getElementById('tm-problem-panel')?.textContent.includes('Falta SQX'));
    await desktop.waitForFunction(() => document.getElementById('tm-problem-panel')?.textContent.includes('añade el .sqx original'));
    await desktop.waitForFunction(() => (document.getElementById('tm-contract-summary')?.innerText || '').toLowerCase().includes('falta sqx'));
    await desktop.waitForFunction(() => (document.getElementById('tm-contract-diagnostics')?.innerText || '').includes('template-maker-cert-v2'));
    await desktop.waitForFunction(() => (document.getElementById('tm-contract-diagnostics')?.innerText || '').toLowerCase().includes('faltantes reales: ninguna'));
    const tmAuditAfterCsv = await desktop.evaluate(() => window.SQX.templateMaker.getAuditReport());
    if (tmAuditAfterCsv.total < 1 || tmAuditAfterCsv.passed < 1) {
      throw new Error('Template Maker should show loaded CSV scoring results');
    }
    const csvOnlyStatus = await desktop.evaluate(() => window.SQX.templateMaker.getStrategyStatus(window.SQX.templateMaker.getStrategies()[0]));
    if (csvOnlyStatus !== 'Falta SQX') throw new Error(`CSV-only strategy should show Falta SQX, got ${csvOnlyStatus}`);
    await desktop.evaluate(async () => {
      await window.SQX.templateMaker.reset();
      window.SQX.templateMakerUI.renderAll();
    });
    await desktop.locator('#tm-files-input').setInputFiles([csvSamplePath].concat(sqxSamplePaths));
    await desktop.waitForFunction(() => window.SQX.templateMaker.getStrategies().some(strategy => window.SQX.templateMaker.getStrategyStatus(strategy) === 'Lista para C2'));
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.innerText.includes('Lista para C2'));
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.innerText.includes('Similar descartada'));
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.innerText.includes('Ganador cluster'));
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.innerText.includes('Diverso'));
    await desktop.waitForFunction(() => (document.getElementById('tm-contract-summary')?.innerText || '').toLowerCase().includes('lista para c2'));
    await desktop.waitForFunction(() => {
      const wrap = document.querySelector('#tab-templatemaker .tm-results-wrap');
      return wrap && wrap.scrollWidth <= wrap.clientWidth + 2;
    });
    await saveShot(desktop, 'e2e-template-maker-results-desktop.png');
    if (await desktop.locator('#tm-results-table [data-tm-export]').count() !== 0) {
      throw new Error('Template Maker should keep C2 actions outside the result table');
    }
    await desktop.locator('#tm-results-table [data-tm-select]').nth(1).check();
    await desktop.waitForFunction(() => !document.getElementById('tm-c2-selected-btn')?.disabled);
    await desktop.locator('#tm-c2-selected-btn').click();
    await desktop.waitForSelector('#tm-modal-c2:not([hidden])');
    await desktop.waitForFunction(() => (document.getElementById('tm-c2-indicator')?.value || '').length > 0);
    await desktop.waitForFunction(() => /^CL\d+/.test(document.getElementById('tm-c2-cluster')?.value || ''));
    await desktop.waitForFunction(() => (document.getElementById('tm-c2-exit-list')?.innerText || '').length > 0);
    const c2TraceInitial = await desktop.evaluate(() => ({
      indicator: document.getElementById('tm-c2-indicator')?.value || '',
      cluster: document.getElementById('tm-c2-cluster')?.value || '',
      block: document.getElementById('tm-c2-block')?.value || '',
      detected: document.getElementById('tm-c2-indicators-detected')?.textContent || '',
      preview: document.getElementById('tm-c2-name-preview')?.textContent || '',
      exits: document.getElementById('tm-c2-exit-list')?.innerText || '',
      exitVersion: document.getElementById('tm-c2-exit-version')?.textContent || '',
    }));
    if (!c2TraceInitial.indicator || c2TraceInitial.indicator === 'SIN_INDICADOR') {
      throw new Error('Template Maker C2 modal should prefill the base indicator from SQX logic');
    }
    if (!c2TraceInitial.cluster.startsWith('CL')) throw new Error('Template Maker C2 modal should prefill NumCluster');
    if (!c2TraceInitial.block.startsWith('BS_')) throw new Error('Template Maker C2 modal should use BS_* blocksettings');
    ['template_', c2TraceInitial.indicator, c2TraceInitial.cluster, c2TraceInitial.block].forEach(expected => {
      if (!c2TraceInitial.preview.includes(expected)) throw new Error(`C2 filename preview should include ${expected}`);
    });
    if (!c2TraceInitial.detected || c2TraceInitial.detected === '-') {
      throw new Error('Template Maker C2 modal should show detected indicators');
    }
    if (!c2TraceInitial.exitVersion.includes('sqx-exit-policy-v1')) {
      throw new Error('Template Maker C2 modal should expose the exit policy version');
    }
    ['Profit Target', 'Stop Loss', 'Trailing Stop'].forEach(expected => {
      if (!c2TraceInitial.exits.includes(expected)) throw new Error(`C2 exit policy should list ${expected}`);
    });
    await desktop.locator('#tm-c2-indicator').fill(`${c2TraceInitial.indicator}_custom`);
    await desktop.locator('#tm-c2-cluster').fill('CL09');
    await desktop.waitForFunction(() => {
      const preview = document.getElementById('tm-c2-name-preview')?.textContent || '';
      return preview.includes('_custom') && preview.includes('CL09');
    });
    const generatedC2Trace = await desktop.evaluate(async () => {
      const strategyId = document.getElementById('tm-modal-c2')?.dataset.strategyId;
      const strategy = window.SQX.templateMaker.getStrategies().find(item => String(item._id) === String(strategyId));
      const options = {
        asset: document.getElementById('tm-c2-asset')?.value,
        direction: document.getElementById('tm-c2-direction')?.value,
        timeframe: document.getElementById('tm-c2-tf')?.value,
        indicatorBase: document.getElementById('tm-c2-indicator')?.value,
        clusterId: document.getElementById('tm-c2-cluster')?.value,
        blockSetting: document.getElementById('tm-c2-block')?.value,
      };
      const trace = window.SQX.templateMaker.resolveC2Trace(strategy, options);
      const blob = await window.SQX.templateMaker.generateC2Template(strategy, options);
      const zip = await window.JSZip.loadAsync(blob);
      const xml = await zip.file('strategy_Portfolio.xml').async('string');
      return {
        name: trace.name,
        xmlHasName: xml.includes(`<StrategyName>${trace.name}</StrategyName>`),
        exitAfterBarsDisabled: /#ExitAfterBars\.ExitAfterBars#"[^>]*>0<\/Param>/.test(xml),
        ptRandom: /#ProfitTarget\.ProfitTarget#"[^>]*generate="random"[^>]*randomValue="default"/.test(xml),
        slRandom: /#StopLoss\.StopLoss#"[^>]*generate="random"[^>]*randomValue="default"/.test(xml),
        tsRandom: /#TrailingStop\.TrailingStop#"[^>]*generate="random"[^>]*randomValue="default"/.test(xml),
      };
    });
    if (!generatedC2Trace.name.includes('CL09') || !generatedC2Trace.name.includes('_custom')) {
      throw new Error('Generated C2 trace name should include edited indicator and cluster');
    }
    if (!generatedC2Trace.xmlHasName) {
      throw new Error('Generated C2 SQX should write the traceable name into StrategyName');
    }
    if (!generatedC2Trace.exitAfterBarsDisabled) {
      throw new Error('Generated C2 SQX should disable ExitAfterBars through exit policy');
    }
    if (!generatedC2Trace.ptRandom || !generatedC2Trace.slRandom || !generatedC2Trace.tsRandom) {
      throw new Error('Generated C2 SQX should randomize PT/SL/TS through exit policy');
    }
    await desktop.locator('#tm-c2-cancel').click();
    await desktop.locator('#tm-results-table [data-tm-select]').nth(1).uncheck();
    await desktop.locator('#tm-results-table [data-tm-select]').first().check();
    await desktop.waitForFunction(() => document.getElementById('tm-c2-selected-btn')?.disabled === true);
    await desktop.locator('#tm-results-table [data-tm-select]').first().uncheck();
    const beforeSelectedDelete = await desktop.evaluate(() => window.SQX.templateMaker.getStrategies().length);
    await desktop.locator('#tm-results-table [data-tm-select]').first().check();
    await desktop.waitForFunction(() => !document.getElementById('tm-delete-selected-btn')?.disabled);
    await desktop.evaluate(() => { window.confirm = () => true; });
    await desktop.locator('#tm-delete-selected-btn').click();
    await acceptDecision(desktop);
    await desktop.waitForFunction(previous => window.SQX.templateMaker.getStrategies().length === previous - 1, beforeSelectedDelete);
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.hidden === false);
    const afterSelectedDelete = await desktop.evaluate(() => window.SQX.templateMaker.getStrategies().length);
    if (afterSelectedDelete !== beforeSelectedDelete - 1) {
      throw new Error('Template Maker selected delete should remove only checked strategies');
    }
    await saveShot(desktop, 'e2e-template-maker-selected-delete-desktop.png');
    await desktop.waitForFunction(() => window.SQX.templateMaker.getCapa() === 1);
    await desktop.locator('#tm-reset-results-btn').click();
    await acceptDecision(desktop);
    await desktop.waitForFunction(() => window.SQX.templateMaker.getStrategies().length === 0);
    await desktop.waitForFunction(() => document.getElementById('tm-results-table')?.hidden === true);
    await desktop.waitForFunction(() => document.getElementById('tm-empty-state')?.hidden === false);
    await desktop.waitForFunction(() => document.getElementById('tm-c2-selected-btn')?.disabled === true);
    await saveShot(desktop, 'e2e-template-maker-results-reset-desktop.png');
    await desktop.locator('#tm-audit-btn').click();
    await desktop.waitForSelector('#tm-modal-audit:not([hidden])');
    await desktop.locator('#tm-audit-close').click();
    await desktop.locator('#tm-reset-btn').click();
    await acceptDecision(desktop);
    await desktop.waitForFunction(() => window.SQX.templateMaker.getStrategies().length === 0);
    await saveShot(desktop, 'e2e-template-maker-desktop.png');

    await openTab(desktop, 'cvc');
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
    await desktop.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('Dir short_only'));
    await desktop.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('Coherencia'));
    await desktop.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('Arquetipo MEAN_REVERT'));
    await desktop.waitForFunction(() => document.getElementById('cvc-ranking')?.textContent.includes('Vol VOL_'));
    await desktop.waitForFunction(() => document.getElementById('cvc-ready-count')?.textContent.trim() === '1');
    await desktop.waitForFunction(() => document.getElementById('cvc-regime-ready-count')?.textContent.trim() === '3');
    await desktop.locator('#cvc-filter-health-ok').check();
    await desktop.waitForFunction(() => document.getElementById('cvc-status')?.textContent.includes('Filtro activo: 2/3 visibles'));
    await desktop.locator('#cvc-filter-egt-v2-ok').check();
    await desktop.waitForFunction(() => document.getElementById('cvc-status')?.textContent.includes('Filtro activo: 2/3 visibles'));
    await desktop.locator('#cvc-filter-health-ok').uncheck();
    await desktop.locator('#cvc-filter-egt-v2-ok').uncheck();
    await desktop.waitForFunction(() => document.querySelectorAll('#cvc-ranking .cvc-result-row').length === 3);
    await desktop.locator('#cvc-clear-btn').click();
    await desktop.waitForFunction(() => document.getElementById('cvc-empty')?.textContent.includes('Carga CSV') && document.getElementById('cvc-candidate-count')?.textContent.trim() === '0');
    await desktop.locator('#cvc-sample-btn').click();
    await desktop.waitForSelector('#cvc-ranking .cvc-result-row');
    const cvcModel = await desktop.evaluate(() => window.SQX.championChallenger.evaluate());
    if (!cvcModel.ok || cvcModel.rankings.length !== 3) throw new Error('Champion vs Challenger sample contract failed');
    if (!cvcModel.rankings.every(row => row.regime_evidence && row.regime_evidence.symbol === 'AUDCAD')) throw new Error('Champion vs Challenger regime evidence missing');
    if (!cvcModel.rankings.some(row => row.egt_v2?.direction === 'short_only' && row.archetype?.archetype === 'MEAN_REVERT')) throw new Error('Champion vs Challenger should expose short-only mean-revert evidence');
    if (!cvcModel.rankings.every(row => row.oos_timeline && row.volatility_coherence?.verdict)) throw new Error('Champion vs Challenger should expose OOS timeline and volatility evidence');
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
    await openTab(desktop, 'estrategias');
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
    await acceptDecision(desktop);
    await desktop.waitForFunction(() => localStorage.getItem('sqx_strategies_deleted_v1') !== null);
    const afterDelete = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterDelete !== cards - 1) throw new Error(`Deleting a base strategy should hide exactly one card, got ${afterDelete} from ${cards}`);
    await desktop.locator('#strat-restore-hidden-btn').click();
    await acceptDecision(desktop);
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
    await acceptDecision(desktop);
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_user_v1') || '[]').length === 0);

    await saveShot(desktop, 'e2e-strategies-desktop.png');
    await desktop.locator('#strat-open-cvc-btn').click();
    await desktop.waitForFunction(() => getComputedStyle(document.getElementById('tab-cvc')).display !== 'none');
    await openTab(desktop, 'estrategias');
    await desktop.locator('#strat-views-handoff [data-vc-handoff="risk"]').click();
    await desktop.waitForFunction(() => getComputedStyle(document.getElementById('tab-views')).display !== 'none');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX Risk Review');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    assertNoBrowserErrors(desktopErrors, 'desktop');
    await desktop.close();

    const compact = await browser.newPage({ viewport: { width: 1280, height: 820 } });
    const compactErrors = [];
    collectBrowserErrors(compact, compactErrors);
    await compact.goto(dashboardUrl, { waitUntil: 'load' });
    await compact.waitForSelector('.tab[data-tab="workflow"].active');
    await compact.waitForSelector('#edge-factory-shell');
    await compact.evaluate(() => {
      sessionStorage.setItem('sqx_remote_welcome_dismissed_v1', '1');
      const localModel = window.SQX.home.computeRemoteServiceModel({});
      window.SQX.home.applyRemoteServiceModel(localModel, document);
    });
    await compact.waitForFunction(() => document.getElementById('remote-welcome-gate')?.hidden === true);
    await compact.locator('[data-edge-mode="advanced"]').click();
    await compact.waitForSelector('[data-edge-mode="advanced"].active');
    await compact.locator('#edge-tools-toggle').click();
    await compact.waitForSelector('#edge-tool-drawer:not([hidden])');
    await openTab(compact, 'projectgen');
    await compact.waitForSelector('#tab-projectgen details.pg-step-panel:not([open])');
    await compact.locator('#pg-step-choice > summary').click();
    await compact.locator('#pg-mode-manual').click();
    await compact.waitForSelector('#pg-mode-manual-panel:not([hidden]) #pg-custom-generate');
    await saveShot(compact, 'e2e-projectgen-compact-pc.png');
    await openTab(compact, 'views');
    await compact.waitForSelector('#vc-preview');
    await openTab(compact, 'cvc');
    await compact.waitForSelector('#cvc-run-btn');
    await compact.locator('#cvc-sample-btn').click();
    await compact.waitForSelector('#cvc-ranking .cvc-result-row');
    await openTab(compact, 'estrategias');
    await compact.waitForSelector('#tab-estrategias .strat-card');
    await openTab(compact, 'filtros');
    await compact.waitForSelector('#filtros-view .bs-card');
    const compactBlockSettingsCards = await compact.locator('#filtros-view .bs-card').count();
    if (compactBlockSettingsCards !== 7) throw new Error('Compact PC BlockSettings Info should render 7 Capa 1 cards');
    await saveShot(compact, 'e2e-blocksettings-info-compact-pc.png');
    assertNoBrowserErrors(compactErrors, 'compact pc');
    await compact.close();
  } finally {
    await browser.close();
  }
}

run().catch(error => {
  console.error(error);
  process.exit(1);
});
