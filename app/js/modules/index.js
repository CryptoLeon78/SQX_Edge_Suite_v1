(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  SQX.moduleOrder = SQX.moduleOrder || ['core', 'config', 'storage', 'license', 'ui', 'formatters', 'domain', 'datasets', 'renderers', 'charts', 'strategies', 'home', 'support', 'fulfillment', 'customer-cockpit', 'workflow', 'project-generator'];

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
