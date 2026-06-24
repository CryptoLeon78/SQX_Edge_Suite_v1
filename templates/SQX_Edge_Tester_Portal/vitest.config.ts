import { defineConfig } from "vitest/config";
import { cloudflareTest } from "@cloudflare/vitest-pool-workers";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const alias = { "@": path.resolve(__dirname, "src") };

export default defineConfig({
  test: {
    projects: [
      // Node-environment suite: InMemoryTesterStore + DemoTesterStore smoke
      {
        test: {
          name: "node",
          environment: "node",
          include: ["tests/**/*.ts"],
          exclude: ["tests/d1/**"],
        },
        resolve: { alias },
      },
      // Workers-pool suite: D1TesterStore contract + atomicity test
      {
        plugins: [
          cloudflareTest({
            wrangler: { configPath: "./wrangler.test.jsonc" },
          }),
        ],
        test: {
          name: "d1",
          include: ["tests/d1/**/*.ts"],
          globalSetup: ["./vitest.d1.global-setup.ts"],
        },
        resolve: { alias },
      },
    ],
  },
});
