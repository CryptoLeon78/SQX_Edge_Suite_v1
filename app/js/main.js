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

if (window.SQX && window.SQX.workflow) {
  window.SQX.workflow.init();
}
