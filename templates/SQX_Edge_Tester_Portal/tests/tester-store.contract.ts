import { describe, it, expect, beforeEach } from "vitest";
import { InMemoryTesterStore } from "@/lib/stores/in-memory-tester-store";
import { DemoTesterStore } from "@/lib/stores/demo-tester-store";
import type { TesterStore } from "@/lib/tester-store";
import type {
  TesterAuthRecord,
  TesterSessionRecord,
  RenewalTokenRecord,
  TesterAuditEvent,
} from "@/lib/auth-data-contract";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

let _seq = 0;
function uid(): string {
  return `id-${++_seq}`;
}

function makeSession(overrides: Partial<TesterSessionRecord> = {}): TesterSessionRecord {
  const now = new Date();
  return {
    sessionIdHash: `hash-${uid()}`,
    testerId: "tester-1",
    createdAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + 3_600_000).toISOString(),
    revokedAt: null,
    lastSeenAt: null,
    ipHash: "ip",
    userAgentHash: "ua",
    ...overrides,
  };
}

function makeToken(overrides: Partial<RenewalTokenRecord> = {}): RenewalTokenRecord {
  const now = new Date();
  return {
    tokenId: uid(),
    tokenHash: `token-${uid()}`,
    testerId: "tester-1",
    purpose: "renewal",
    createdAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + 3_600_000).toISOString(),
    usedAt: null,
    revokedAt: null,
    ...overrides,
  };
}

function makeTester(overrides: Partial<TesterAuthRecord> = {}): TesterAuthRecord {
  const now = new Date();
  const id = uid();
  return {
    testerId: `tester-${id}`,
    emailNormalized: `tester-${id}@example.com`,
    displayName: "Test User",
    status: "active",
    plan: "tester_pro",
    passwordHash: null,
    passwordHashAlgorithm: null,
    passwordUpdatedAt: null,
    expiresAt: new Date(now.getTime() + 15 * 86_400_000).toISOString(),
    renewalCycleDays: 15,
    failedLoginCount: 0,
    lockedUntil: null,
    lastLoginAt: null,
    createdAt: now.toISOString(),
    updatedAt: now.toISOString(),
    privateNotesRef: null,
    ...overrides,
  };
}

function makeAuditEvent(
  overrides: Partial<TesterAuditEvent> & { occurredAt: string }
): TesterAuditEvent {
  return {
    eventId: uid(),
    type: "login_succeeded",
    testerId: "t1",
    actor: "tester",
    ipHash: null,
    userAgentHash: null,
    route: null,
    outcome: "allowed",
    reasonCode: null,
    privateEvidenceRef: null,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Contract suite — run against any compliant TesterStore
// ---------------------------------------------------------------------------

export function runTesterStoreContract(makeStore: () => TesterStore): void {
  describe("TesterStore contract", () => {
    let store: TesterStore;

    beforeEach(() => {
      store = makeStore();
    });

    // --- G-atomic -----------------------------------------------------------

    describe("G-atomic: consumeRenewalToken", () => {
      it("returns the token on first call and null on second call", async () => {
        const token = makeToken();
        await store.createRenewalToken(token);

        const first = await store.consumeRenewalToken(token.tokenHash);
        expect(first).not.toBeNull();
        expect(first?.tokenId).toBe(token.tokenId);
        expect(first?.usedAt).not.toBeNull();

        const second = await store.consumeRenewalToken(token.tokenHash);
        expect(second).toBeNull();
      });

      it("returns null for an unknown tokenHash", async () => {
        const result = await store.consumeRenewalToken("does-not-exist");
        expect(result).toBeNull();
      });
    });

    // --- G-strong -----------------------------------------------------------

    describe("G-strong: revokeSession", () => {
      it("getSession returns null immediately after revokeSession", async () => {
        const session = makeSession();
        await store.createSession(session);

        const before = await store.getSession(session.sessionIdHash);
        expect(before).not.toBeNull();

        await store.revokeSession(session.sessionIdHash);

        const after = await store.getSession(session.sessionIdHash);
        expect(after).toBeNull();
      });

      it("revoking an unknown hash is a no-op", async () => {
        await expect(store.revokeSession("unknown")).resolves.toBeUndefined();
      });
    });

    // --- Lookup auth --------------------------------------------------------

    describe("lookup auth: tester email uniqueness", () => {
      it("createTester rejects a duplicate emailNormalized", async () => {
        const email = "dup@example.com";
        const t1 = makeTester({ emailNormalized: email });
        const t2 = makeTester({ emailNormalized: email });

        await store.createTester(t1);
        await expect(store.createTester(t2)).rejects.toThrow();
      });

      it("getTesterByEmail returns the correct record", async () => {
        const tester = makeTester();
        await store.createTester(tester);

        const found = await store.getTesterByEmail(tester.emailNormalized);
        expect(found?.testerId).toBe(tester.testerId);
      });

      it("getTesterByEmail returns null for unknown email", async () => {
        const result = await store.getTesterByEmail("nobody@example.com");
        expect(result).toBeNull();
      });
    });

    // --- G-range ------------------------------------------------------------

    describe("G-range: queryAudit", () => {
      it("returns events in [from, to] sorted ascending by occurredAt", async () => {
        const base = new Date("2025-01-01T00:00:00.000Z").getTime();
        const events = [
          makeAuditEvent({ eventId: "e1", occurredAt: new Date(base + 1_000).toISOString() }),
          makeAuditEvent({ eventId: "e2", occurredAt: new Date(base + 2_000).toISOString() }),
          makeAuditEvent({ eventId: "e3", occurredAt: new Date(base + 3_000).toISOString() }),
          makeAuditEvent({ eventId: "e4", occurredAt: new Date(base + 4_000).toISOString() }),
        ];
        for (const e of events) await store.appendAuditEvent(e);

        const from = new Date(base + 1_500).toISOString(); // after e1
        const to = new Date(base + 3_500).toISOString();   // before e4
        const result = await store.queryAudit({ testerId: "t1", from, to });

        expect(result.map((e) => e.eventId)).toEqual(["e2", "e3"]);
      });

      it("filters by testerId when provided", async () => {
        const base = new Date("2025-02-01T00:00:00.000Z").getTime();
        await store.appendAuditEvent(
          makeAuditEvent({ eventId: "ea", testerId: "ta", occurredAt: new Date(base + 500).toISOString() })
        );
        await store.appendAuditEvent(
          makeAuditEvent({ eventId: "eb", testerId: "tb", occurredAt: new Date(base + 1_000).toISOString() })
        );

        const result = await store.queryAudit({
          testerId: "ta",
          from: new Date(base).toISOString(),
          to: new Date(base + 2_000).toISOString(),
        });
        expect(result.map((e) => e.eventId)).toEqual(["ea"]);
      });
    });

    // --- Expiry -------------------------------------------------------------

    describe("expiry", () => {
      it("getSession returns null for an already-expired session", async () => {
        const session = makeSession({
          expiresAt: new Date(Date.now() - 1_000).toISOString(),
        });
        await store.createSession(session);

        const result = await store.getSession(session.sessionIdHash);
        expect(result).toBeNull();
      });
    });
  });
}

// ---------------------------------------------------------------------------
// Run the full contract suite against InMemoryTesterStore
// ---------------------------------------------------------------------------

runTesterStoreContract(() => new InMemoryTesterStore());

// ---------------------------------------------------------------------------
// DemoTesterStore — smoke tests + login regression
// ---------------------------------------------------------------------------

describe("DemoTesterStore smoke", () => {
  const DEMO_EMAIL = "demo@sqx-test.invalid";
  let store: DemoTesterStore;

  beforeEach(() => {
    process.env["T4_DEMO_TESTER_EMAIL"] = DEMO_EMAIL;
    store = new DemoTesterStore();
  });

  it("getSession returns a synthetic session for any non-empty hash", async () => {
    const result = await store.getSession("any-non-empty-hash");
    expect(result).not.toBeNull();
    expect(result?.sessionIdHash).toBe("any-non-empty-hash");
  });

  it("getSession returns null for an empty hash", async () => {
    const result = await store.getSession("");
    expect(result).toBeNull();
  });

  it("createSession is a no-op and echoes the record back", async () => {
    const session = makeSession({ sessionIdHash: "test-hash" });
    const result = await store.createSession(session);
    expect(result.sessionIdHash).toBe("test-hash");
  });

  it("revokeSession is a no-op (still returns session after revoke)", async () => {
    await store.revokeSession("any-hash");
    const result = await store.getSession("any-hash");
    expect(result).not.toBeNull();
  });

  it("login regression: getTesterByEmail returns record for the demo email", async () => {
    const result = await store.getTesterByEmail(DEMO_EMAIL);
    expect(result).not.toBeNull();
    expect(result?.emailNormalized).toBe(DEMO_EMAIL);
    expect(result?.status).toBe("active");
    expect(result?.plan).toBe("tester_pro");
  });

  it("login regression: getTesterByEmail returns null for unknown email", async () => {
    const result = await store.getTesterByEmail("unknown@example.com");
    expect(result).toBeNull();
  });

  it("consumeRenewalToken always returns null in demo mode", async () => {
    const result = await store.consumeRenewalToken("any-token-hash");
    expect(result).toBeNull();
  });

  it("queryAudit always returns an empty array in demo mode", async () => {
    await store.appendAuditEvent(makeAuditEvent({ occurredAt: new Date().toISOString() }));
    const result = await store.queryAudit({
      from: new Date(0).toISOString(),
      to: new Date().toISOString(),
    });
    expect(result).toEqual([]);
  });
});
