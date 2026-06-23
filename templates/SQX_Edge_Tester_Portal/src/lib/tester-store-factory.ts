import { DemoTesterStore } from "./stores/demo-tester-store";
import { InMemoryTesterStore } from "./stores/in-memory-tester-store";
import type { TesterStore } from "./tester-store";

/**
 * Returns the active TesterStore for the current request.
 * Reads TESTER_STORE_DRIVER from process.env (Cloudflare bindings are visible via process.env
 * under OpenNext; consistent with the rest of this codebase).
 * No module-level state — a new instance is created on every call.
 *
 *   "demo"   → DemoTesterStore (default; cookie-trust; production deploy)
 *   "memory" → InMemoryTesterStore (dev / vitest oracle; state lost across requests)
 */
export function getTesterStore(): TesterStore {
  const driver = process.env.TESTER_STORE_DRIVER ?? "demo";
  switch (driver) {
    case "demo":
      return new DemoTesterStore();
    case "memory":
      return new InMemoryTesterStore();
    default:
      throw new Error(`TesterStore driver "${driver}" not implemented yet`);
  }
}
