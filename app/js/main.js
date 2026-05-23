// ============================================================
// SQX Dashboard — main / INIT
// Initial render calls + app shell bindings
// ============================================================

renderSqxLegend();
renderAssetGrid();
renderCategoriesView();
renderFiltros();
renderPriority();
renderStrategies();
renderPipelineState();
renderHome();

if (window.SQX && window.SQX.license) {
  window.SQX.license.init();
}

if (window.SQX && window.SQX.support) {
  window.SQX.support.init();
}

if (window.SQX && window.SQX.mtfEvidence) {
  window.SQX.mtfEvidence.init();
}

if (window.SQX && window.SQX.championChallenger) {
  window.SQX.championChallenger.init();
}

if (window.SQX && window.SQX.strategyBuilder) {
  window.SQX.strategyBuilder.init();
}

if (window.SQX && window.SQX.templateMakerUI) {
  window.SQX.templateMakerUI.init();
}

if (window.SQX && window.SQX.fulfillment) {
  window.SQX.fulfillment.init();
}

if (window.SQX && window.SQX.customerCockpit) {
  window.SQX.customerCockpit.init();
}

if (window.SQX && window.SQX.stateBackup) {
  window.SQX.stateBackup.init();
}

if (window.SQX && window.SQX.workflow) {
  window.SQX.workflow.init();
}

if (window.SQX && window.SQX.edgeFactoryUI) {
  window.SQX.edgeFactoryUI.init();
}

if (window.SQX && window.SQX.agentGuide) {
  window.SQX.agentGuide.init();
}

if (window.SQX && window.SQX.viewCreator) {
  window.SQX.viewCreator.init();
}
