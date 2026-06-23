import type {
  TesterAuthRecord,
  TesterSessionRecord,
  RenewalTokenRecord,
  TesterAuditEvent,
} from "../auth-data-contract";
import type { TesterStore } from "../tester-store";

/**
 * In-memory reference implementation of TesterStore.
 *
 * Satisfies G-atomic, G-strong, and G-range within a single process.
 * Use only for vitest contract suite and local dev (driver = "memory").
 * State is lost between requests under Cloudflare isolates.
 */
export class InMemoryTesterStore implements TesterStore {
  private readonly testers = new Map<string, TesterAuthRecord>();   // testerId → record
  private readonly emailIndex = new Map<string, string>();           // emailNormalized → testerId
  private readonly sessions = new Map<string, TesterSessionRecord>(); // sessionIdHash → record
  private readonly tokens = new Map<string, RenewalTokenRecord>();   // tokenHash → record
  private readonly auditLog: TesterAuditEvent[] = [];

  async getTesterByEmail(emailNormalized: string): Promise<TesterAuthRecord | null> {
    const id = this.emailIndex.get(emailNormalized);
    return id !== undefined ? (this.testers.get(id) ?? null) : null;
  }

  async getTesterById(testerId: string): Promise<TesterAuthRecord | null> {
    return this.testers.get(testerId) ?? null;
  }

  async createTester(record: TesterAuthRecord): Promise<TesterAuthRecord> {
    if (this.emailIndex.has(record.emailNormalized)) {
      throw new Error(`Duplicate emailNormalized: ${record.emailNormalized}`);
    }
    this.testers.set(record.testerId, record);
    this.emailIndex.set(record.emailNormalized, record.testerId);
    return record;
  }

  async updateTester(
    testerId: string,
    updates: Partial<Omit<TesterAuthRecord, "testerId" | "emailNormalized" | "createdAt">>
  ): Promise<TesterAuthRecord | null> {
    const existing = this.testers.get(testerId);
    if (!existing) return null;
    const updated: TesterAuthRecord = {
      ...existing,
      ...updates,
      testerId: existing.testerId,
      emailNormalized: existing.emailNormalized,
      createdAt: existing.createdAt,
    };
    this.testers.set(testerId, updated);
    return updated;
  }

  async createSession(session: TesterSessionRecord): Promise<TesterSessionRecord> {
    this.sessions.set(session.sessionIdHash, session);
    return session;
  }

  async getSession(sessionIdHash: string): Promise<TesterSessionRecord | null> {
    const s = this.sessions.get(sessionIdHash);
    if (!s) return null;
    if (s.revokedAt !== null) return null;
    if (new Date(s.expiresAt).getTime() <= Date.now()) return null;
    return s;
  }

  async revokeSession(sessionIdHash: string): Promise<void> {
    const s = this.sessions.get(sessionIdHash);
    if (s) {
      this.sessions.set(sessionIdHash, { ...s, revokedAt: new Date().toISOString() });
    }
  }

  async createRenewalToken(token: RenewalTokenRecord): Promise<RenewalTokenRecord> {
    this.tokens.set(token.tokenHash, token);
    return token;
  }

  async consumeRenewalToken(tokenHash: string): Promise<RenewalTokenRecord | null> {
    const token = this.tokens.get(tokenHash);
    if (!token || token.usedAt !== null) return null;
    const consumed: RenewalTokenRecord = { ...token, usedAt: new Date().toISOString() };
    this.tokens.set(tokenHash, consumed);
    return consumed;
  }

  async appendAuditEvent(event: TesterAuditEvent): Promise<void> {
    this.auditLog.push(event);
  }

  async queryAudit(opts: {
    testerId?: string | null;
    from: string;
    to: string;
  }): Promise<TesterAuditEvent[]> {
    const fromTs = new Date(opts.from).getTime();
    const toTs = new Date(opts.to).getTime();
    return this.auditLog
      .filter((e) => {
        const ts = new Date(e.occurredAt).getTime();
        if (ts < fromTs || ts > toTs) return false;
        if (opts.testerId != null && e.testerId !== opts.testerId) return false;
        return true;
      })
      .sort((a, b) => a.occurredAt.localeCompare(b.occurredAt));
  }
}
