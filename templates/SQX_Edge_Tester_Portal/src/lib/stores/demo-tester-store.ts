import type {
  TesterAuthRecord,
  TesterSessionRecord,
  RenewalTokenRecord,
  TesterAuditEvent,
} from "../auth-data-contract";
import { SESSION_COOKIE_CONTRACT } from "../auth-data-contract";
import type { TesterStore } from "../tester-store";

const DEMO_TESTER_EMAIL_ENV = "T4_DEMO_TESTER_EMAIL";
const DEMO_TESTER_ID = "demo-tester-001";

function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

function buildDemoRecord(emailNormalized: string): TesterAuthRecord {
  const now = new Date();
  return {
    testerId: DEMO_TESTER_ID,
    emailNormalized,
    displayName: "Demo Tester",
    status: "active",
    plan: "tester_pro",
    passwordHash: null,
    passwordHashAlgorithm: null,
    passwordUpdatedAt: null,
    expiresAt: new Date(now.getTime() + SESSION_COOKIE_CONTRACT.maxAgeMinutes * 60 * 1000).toISOString(),
    renewalCycleDays: 15,
    failedLoginCount: 0,
    lockedUntil: null,
    lastLoginAt: null,
    createdAt: now.toISOString(),
    updatedAt: now.toISOString(),
    privateNotesRef: null,
  };
}

function buildDemoSession(sessionIdHash: string): TesterSessionRecord {
  const now = new Date();
  return {
    sessionIdHash,
    testerId: DEMO_TESTER_ID,
    createdAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + SESSION_COOKIE_CONTRACT.maxAgeMinutes * 60 * 1000).toISOString(),
    revokedAt: null,
    lastSeenAt: null,
    ipHash: "",
    userAgentHash: "",
  };
}

/**
 * Cookie-trust store for the "demo" driver (default deploy mode).
 *
 * Session validity is determined solely by cookie presence — the cookie IS the storage.
 * createSession and revokeSession are no-ops; the route layer writes and clears the cookie.
 *
 * Exempt from G-atomic and G-strong guarantees per ADR-0002.
 */
export class DemoTesterStore implements TesterStore {
  private getDemoEmail(): string {
    return normalizeEmail(process.env[DEMO_TESTER_EMAIL_ENV] ?? "");
  }

  async getTesterByEmail(emailNormalized: string): Promise<TesterAuthRecord | null> {
    const demo = this.getDemoEmail();
    if (!demo || emailNormalized !== demo) return null;
    return buildDemoRecord(emailNormalized);
  }

  async getTesterById(testerId: string): Promise<TesterAuthRecord | null> {
    const demo = this.getDemoEmail();
    if (!demo || testerId !== DEMO_TESTER_ID) return null;
    return buildDemoRecord(demo);
  }

  async createTester(record: TesterAuthRecord): Promise<TesterAuthRecord> {
    return record;
  }

  async updateTester(
    _testerId: string,
    _updates: Partial<Omit<TesterAuthRecord, "testerId" | "emailNormalized" | "createdAt">>
  ): Promise<TesterAuthRecord | null> {
    return null;
  }

  async createSession(session: TesterSessionRecord): Promise<TesterSessionRecord> {
    return session;
  }

  /** Returns a synthetic session for any non-empty hash (cookie-trust model). */
  async getSession(sessionIdHash: string): Promise<TesterSessionRecord | null> {
    if (!sessionIdHash) return null;
    return buildDemoSession(sessionIdHash);
  }

  async revokeSession(_sessionIdHash: string): Promise<void> {
    // No-op: cookie cleared by the route layer
  }

  async createRenewalToken(token: RenewalTokenRecord): Promise<RenewalTokenRecord> {
    return token;
  }

  async consumeRenewalToken(_tokenHash: string): Promise<RenewalTokenRecord | null> {
    return null;
  }

  async appendAuditEvent(_event: TesterAuditEvent): Promise<void> {
    // No-op
  }

  async queryAudit(_opts: {
    testerId?: string | null;
    from: string;
    to: string;
  }): Promise<TesterAuditEvent[]> {
    return [];
  }
}
