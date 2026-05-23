(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  SQX.moduleOrder = SQX.moduleOrder || ['core', 'config', 'storage', 'modal-registry', 'state-backup', 'license', 'ui', 'formatters', 'domain', 'datasets', 'champion-challenger-core', 'champion-challenger-regime', 'champion-challenger', 'strategy-builder-core', 'strategy-builder', 'renderers', 'charts', 'strategies', 'exit-policy', 'template-maker-worker-client', 'template-maker', 'template-maker-ui', 'home', 'support', 'fulfillment', 'customer-cockpit', 'workflow', 'edge-factory', 'edge-factory-ui', 'agent-guide', 'view-creator', 'project-generator'];

  SQX.boot = SQX.boot || function bootSQXModules() {
    SQX.booted = true;
    if (SQX.flushReady) SQX.flushReady();
  };

  if (SQX.registerModule) {
    SQX.registerModule('modules/index', {
      order: SQX.moduleOrder,
      boot: SQX.boot
    });
  }

  SQX.boot();
})(window);
