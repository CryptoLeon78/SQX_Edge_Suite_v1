/// <reference types="@cloudflare/vitest-pool-workers/types" />

import { beforeAll, describe, it, expect, inject } from "vitest";
import { env, applyD1Migrations } from "cloudflare:test";
import type { D1Migration } from "@cloudflare/vitest-pool-workers";
import { D1TesterStore } from "@/lib/stores/d1-tester-store";
import { runTesterStoreContract } from "../tester-store.contract";
import type { RenewalTokenRecord } from "@/lib/auth-data-contract";

// ---------------------------------------------------------------------------
// Apply migrations once — D1 is shared across all tests in this file.
// Migration data is provided by vitest.d1.global-setup.ts via inject().
// ---------------------------------------------------------------------------

beforeAll(async () => {
  const migrations = inject("d1Migrations") as D1Migration[];
  await applyD1Migrations(env.TESTER_DB, migrations);

  // Seed FK anchor — the contract suite's makeSession() and makeToken() helpers
  // hardcode testerId: "tester-1" without first calling createTester().
  // D1 enforces the FK constraint that InMemoryTesterStore does not.
  await env.TESTER_DB.prepare(
    `INSERT OR IGNORE INTO tester_auth_record
       (testerId, emailNormalized, status, failedLoginCount, createdAt)
     VALUES ('tester-1', 'tester-1@contract.invalid', 'active', 0, ?1)`
  )
    .bind(Date.now())
    .run();
});

// ---------------------------------------------------------------------------
// Full TesterStore contract suite against the D1 implementation
// ---------------------------------------------------------------------------

runTesterStoreContract(() => new D1TesterStore(env.TESTER_DB));

// ---------------------------------------------------------------------------
// D1-specific: G-atomic atomicity under concurrent consume calls
// ---------------------------------------------------------------------------

describe("D1-specific: consumeRenewalToken atomicity", () => {
  it("exactly one of two concurrent consume calls gets the token", async () => {
    const store = new D1TesterStore(env.TESTER_DB);
    const now = new Date();

    const token: RenewalTokenRecord = {
      tokenId: "atomicity-test-token-id",
      tokenHash: "atomicity-test-token-hash",
      testerId: "atomicity-test-tester",
      purpose: "renewal",
      createdAt: now.toISOString(),
      expiresAt: new Date(now.getTime() + 3_600_000).toISOString(),
      usedAt: null,
      revokedAt: null,
    };

    // createRenewalToken requires a tester_auth_record FK — insert a stub row first.
    await env.TESTER_DB.prepare(
      `INSERT OR IGNORE INTO tester_auth_record
         (testerId, emailNormalized, status, passwordHash, passwordHashAlgorithm,
          failedLoginCount, createdAt)
       VALUES (?1, ?2, 'active', '', '', 0, ?3)`
    )
      .bind("atomicity-test-tester", "atomicity@test.invalid", Date.now())
      .run();

    await store.createRenewalToken(token);

    const [r1, r2] = await Promise.all([
      store.consumeRenewalToken("atomicity-test-token-hash"),
      store.consumeRenewalToken("atomicity-test-token-hash"),
    ]);

    const nonNulls = [r1, r2].filter(Boolean);
    expect(nonNulls.length).toBe(1);
    expect(nonNulls[0]?.usedAt).not.toBeNull();
  });
});
