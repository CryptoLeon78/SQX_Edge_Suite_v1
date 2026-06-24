/// <reference types="@cloudflare/workers-types" />
// Project-specific Cloudflare bindings.
// The triple-slash reference brings D1Database (and other Workers types) into
// global scope without turning this file into a module (which would break the
// global interface merging below).

interface CloudflareEnv {
  TESTER_DB: D1Database;
  TESTER_STORE_DRIVER?: string;
}

// Extend Cloudflare.Env (used by cloudflare:test's `env` binding) so that
// env.TESTER_DB is typed correctly in vitest-pool-workers test files.
declare namespace Cloudflare {
  interface Env extends CloudflareEnv {}
}
