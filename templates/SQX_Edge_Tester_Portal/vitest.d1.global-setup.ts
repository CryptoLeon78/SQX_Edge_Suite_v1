import { readD1Migrations } from "@cloudflare/vitest-pool-workers";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default async function setup({
  provide,
}: {
  provide: (key: string, value: unknown) => void;
}) {
  const migrations = await readD1Migrations(
    path.resolve(__dirname, "./migrations")
  );
  provide("d1Migrations", migrations);
}
