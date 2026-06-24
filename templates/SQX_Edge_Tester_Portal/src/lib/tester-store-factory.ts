import { DemoTesterStore } from "./stores/demo-tester-store";
import { InMemoryTesterStore } from "./stores/in-memory-tester-store";
import { D1TesterStore } from "./stores/d1-tester-store";
import type { TesterStore } from "./tester-store";

/**
 * Returns the active TesterStore for the current request.
 * Reads TESTER_STORE_DRIVER from the Cloudflare env binding (passed in by the caller).
 * No module-level state — a new instance is created on every call.
 *
 *   "demo"   → DemoTesterStore (default; cookie-trust; production deploy)
 *   "memory" → InMemoryTesterStore (dev / vitest oracle; state lost across requests)
 *   "d1"     → D1TesterStore (persistent; Cloudflare D1 backing)
 */
export function getTesterStore(env: CloudflareEnv): TesterStore {
  const driver = env.TESTER_STORE_DRIVER ?? "demo";
  switch (driver) {
    case "demo":
      return new DemoTesterStore();
    case "memory":
      return new InMemoryTesterStore();
    case "d1":
      return new D1TesterStore(env.TESTER_DB);
    default:
      throw new Error(`TesterStore driver "${driver}" not implemented yet`);
  }
}
