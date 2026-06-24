import type { D1Database, D1PreparedStatement } from "@cloudflare/workers-types";
import type {
  TesterAuthRecord,
  TesterSessionRecord,
  RenewalTokenRecord,
  TesterAuditEvent,
} from "../auth-data-contract";
import type { TesterStore } from "../tester-store";

// ---------------------------------------------------------------------------
// Date helpers — D1 stores all timestamps as Unix ms integers.
// ---------------------------------------------------------------------------

function toMs(iso: string | null | undefined): number | null {
  if (!iso) return null;
  return new Date(iso).getTime();
}

function toIso(ms: number | null | undefined): string | null {
  if (ms == null) return null;
  return new Date(ms).toISOString();
}

function toIsoRequired(ms: number): string {
  return new Date(ms).toISOString();
}

// ---------------------------------------------------------------------------
// Row types (columns as D1 returns them)
// ---------------------------------------------------------------------------

type AuthRow = {
  testerId: string;
  emailNormalized: string;
  displayName: string | null;
  status: string;
  plan: string | null;
  passwordHash: string | null;
  passwordHashAlgorithm: string | null;
  passwordUpdatedAt: number | null;
  expiresAt: number | null;
  renewalCycleDays: number | null;
  failedLoginCount: number;
  lockedUntil: number | null;
  lastLoginAt: number | null;
  createdAt: number;
  updatedAt: number | null;
  privateNotesRef: string | null;
};

type SessionRow = {
  sessionIdHash: string;
  testerId: string;
  createdAt: number;
  expiresAt: number;
  revokedAt: number | null;
  lastSeenAt: number | null;
  ipHash: string | null;
  userAgentHash: string | null;
};

type TokenRow = {
  tokenId: string;
  tokenHash: string;
  testerId: string;
  purpose: string | null;
  createdAt: number;
  expiresAt: number;
  usedAt: number | null;
  revokedAt: number | null;
};

type AuditRow = {
  eventId: string;
  type: string;
  testerId: string | null;
  actor: string | null;
  occurredAt: number;
  ipHash: string | null;
  userAgentHash: string | null;
  route: string | null;
  outcome: string | null;
  reasonCode: string | null;
  privateEvidenceRef: string | null;
};

// ---------------------------------------------------------------------------
// Row → domain record converters
// ---------------------------------------------------------------------------

function rowToAuthRecord(row: AuthRow): TesterAuthRecord {
  return {
    testerId: row.testerId,
    emailNormalized: row.emailNormalized,
    displayName: row.displayName ?? "",
    status: row.status as TesterAuthRecord["status"],
    plan: row.plan as TesterAuthRecord["plan"],
    passwordHash: row.passwordHash,
    passwordHashAlgorithm: row.passwordHashAlgorithm as TesterAuthRecord["passwordHashAlgorithm"],
    passwordUpdatedAt: toIso(row.passwordUpdatedAt),
    expiresAt: toIsoRequired(row.expiresAt ?? 0),
    renewalCycleDays: (row.renewalCycleDays ?? 15) as TesterAuthRecord["renewalCycleDays"],
    failedLoginCount: row.failedLoginCount,
    lockedUntil: toIso(row.lockedUntil),
    lastLoginAt: toIso(row.lastLoginAt),
    createdAt: toIsoRequired(row.createdAt),
    updatedAt: toIsoRequired(row.updatedAt ?? row.createdAt),
    privateNotesRef: row.privateNotesRef,
  };
}

function rowToSession(row: SessionRow): TesterSessionRecord {
  return {
    sessionIdHash: row.sessionIdHash,
    testerId: row.testerId,
    createdAt: toIsoRequired(row.createdAt),
    expiresAt: toIsoRequired(row.expiresAt),
    revokedAt: toIso(row.revokedAt),
    lastSeenAt: toIso(row.lastSeenAt),
    ipHash: row.ipHash ?? "",
    userAgentHash: row.userAgentHash ?? "",
  };
}

function rowToToken(row: TokenRow): RenewalTokenRecord {
  return {
    tokenId: row.tokenId,
    tokenHash: row.tokenHash,
    testerId: row.testerId,
    purpose: (row.purpose ?? "renewal") as RenewalTokenRecord["purpose"],
    createdAt: toIsoRequired(row.createdAt),
    expiresAt: toIsoRequired(row.expiresAt),
    usedAt: toIso(row.usedAt),
    revokedAt: toIso(row.revokedAt),
  };
}

function rowToAudit(row: AuditRow): TesterAuditEvent {
  return {
    eventId: row.eventId,
    type: row.type as TesterAuditEvent["type"],
    testerId: row.testerId,
    actor: (row.actor ?? "system") as TesterAuditEvent["actor"],
    occurredAt: toIsoRequired(row.occurredAt),
    ipHash: row.ipHash,
    userAgentHash: row.userAgentHash,
    route: row.route,
    outcome: (row.outcome ?? "completed") as TesterAuditEvent["outcome"],
    reasonCode: row.reasonCode,
    privateEvidenceRef: row.privateEvidenceRef,
  };
}

// ---------------------------------------------------------------------------
// D1TesterStore
// ---------------------------------------------------------------------------

export class D1TesterStore implements TesterStore {
  constructor(private readonly db: D1Database) {}

  // --- Tester records -------------------------------------------------------

  async getTesterByEmail(emailNormalized: string): Promise<TesterAuthRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM tester_auth_record WHERE emailNormalized = ?1")
      .bind(emailNormalized)
      .first<AuthRow>();
    return row ? rowToAuthRecord(row) : null;
  }

  async getTesterById(testerId: string): Promise<TesterAuthRecord | null> {
    const row = await this.db
      .prepare("SELECT * FROM tester_auth_record WHERE testerId = ?1")
      .bind(testerId)
      .first<AuthRow>();
    return row ? rowToAuthRecord(row) : null;
  }

  async createTester(record: TesterAuthRecord): Promise<TesterAuthRecord> {
    await this.db
      .prepare(
        `INSERT INTO tester_auth_record
          (testerId, emailNormalized, displayName, status, plan,
           passwordHash, passwordHashAlgorithm, passwordUpdatedAt,
           expiresAt, renewalCycleDays, failedLoginCount, lockedUntil,
           lastLoginAt, createdAt, updatedAt, privateNotesRef)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14, ?15, ?16)`
      )
      .bind(
        record.testerId,
        record.emailNormalized,
        record.displayName,
        record.status,
        record.plan,
        record.passwordHash,
        record.passwordHashAlgorithm,
        toMs(record.passwordUpdatedAt),
        toMs(record.expiresAt),
        record.renewalCycleDays,
        record.failedLoginCount,
        toMs(record.lockedUntil),
        toMs(record.lastLoginAt),
        new Date(record.createdAt).getTime(),
        toMs(record.updatedAt),
        record.privateNotesRef
      )
      .run();
    return record;
  }

  async updateTester(
    testerId: string,
    updates: Partial<Omit<TesterAuthRecord, "testerId" | "emailNormalized" | "createdAt">>
  ): Promise<TesterAuthRecord | null> {
    const existing = await this.getTesterById(testerId);
    if (!existing) return null;
    const merged = { ...existing, ...updates };
    await this.db
      .prepare(
        `UPDATE tester_auth_record SET
           displayName = ?2, status = ?3, plan = ?4,
           passwordHash = ?5, passwordHashAlgorithm = ?6, passwordUpdatedAt = ?7,
           expiresAt = ?8, renewalCycleDays = ?9, failedLoginCount = ?10,
           lockedUntil = ?11, lastLoginAt = ?12, updatedAt = ?13, privateNotesRef = ?14
         WHERE testerId = ?1`
      )
      .bind(
        testerId,
        merged.displayName,
        merged.status,
        merged.plan,
        merged.passwordHash,
        merged.passwordHashAlgorithm,
        toMs(merged.passwordUpdatedAt),
        toMs(merged.expiresAt),
        merged.renewalCycleDays,
        merged.failedLoginCount,
        toMs(merged.lockedUntil),
        toMs(merged.lastLoginAt),
        toMs(merged.updatedAt),
        merged.privateNotesRef
      )
      .run();
    return merged;
  }

  // --- Sessions -------------------------------------------------------------

  async createSession(session: TesterSessionRecord): Promise<TesterSessionRecord> {
    await this.db
      .prepare(
        `INSERT INTO tester_session
          (sessionIdHash, testerId, createdAt, expiresAt, revokedAt, lastSeenAt, ipHash, userAgentHash)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)`
      )
      .bind(
        session.sessionIdHash,
        session.testerId,
        new Date(session.createdAt).getTime(),
        new Date(session.expiresAt).getTime(),
        toMs(session.revokedAt),
        toMs(session.lastSeenAt),
        session.ipHash,
        session.userAgentHash
      )
      .run();
    return session;
  }

  async getSession(sessionIdHash: string): Promise<TesterSessionRecord | null> {
    const now = Date.now();
    const row = await this.db
      .prepare(
        `SELECT * FROM tester_session
         WHERE sessionIdHash = ?1 AND revokedAt IS NULL AND expiresAt > ?2`
      )
      .bind(sessionIdHash, now)
      .first<SessionRow>();
    return row ? rowToSession(row) : null;
  }

  async revokeSession(sessionIdHash: string): Promise<void> {
    await this.db
      .prepare("UPDATE tester_session SET revokedAt = ?2 WHERE sessionIdHash = ?1")
      .bind(sessionIdHash, Date.now())
      .run();
  }

  // --- Renewal tokens -------------------------------------------------------

  async createRenewalToken(token: RenewalTokenRecord): Promise<RenewalTokenRecord> {
    await this.db
      .prepare(
        `INSERT INTO tester_renewal_token
          (tokenId, tokenHash, testerId, purpose, createdAt, expiresAt, usedAt, revokedAt)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)`
      )
      .bind(
        token.tokenId,
        token.tokenHash,
        token.testerId,
        token.purpose,
        new Date(token.createdAt).getTime(),
        new Date(token.expiresAt).getTime(),
        toMs(token.usedAt),
        toMs(token.revokedAt)
      )
      .run();
    return token;
  }

  async consumeRenewalToken(tokenHash: string): Promise<RenewalTokenRecord | null> {
    const now = Date.now();
    // G-atomic: single UPDATE...RETURNING so only one concurrent caller can win.
    const row = await this.db
      .prepare(
        `UPDATE tester_renewal_token SET usedAt = ?2
         WHERE tokenHash = ?1 AND usedAt IS NULL AND revokedAt IS NULL AND expiresAt > ?2
         RETURNING *`
      )
      .bind(tokenHash, now)
      .first<TokenRow>();
    return row ? rowToToken(row) : null;
  }

  // --- Audit ----------------------------------------------------------------

  async appendAuditEvent(event: TesterAuditEvent): Promise<void> {
    await this.db
      .prepare(
        `INSERT INTO tester_audit
          (eventId, type, testerId, actor, occurredAt, ipHash, userAgentHash,
           route, outcome, reasonCode, privateEvidenceRef)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)`
      )
      .bind(
        event.eventId,
        event.type,
        event.testerId,
        event.actor,
        new Date(event.occurredAt).getTime(),
        event.ipHash,
        event.userAgentHash,
        event.route,
        event.outcome,
        event.reasonCode,
        event.privateEvidenceRef
      )
      .run();
  }

  async queryAudit(opts: {
    testerId?: string | null;
    from: string;
    to: string;
  }): Promise<TesterAuditEvent[]> {
    const fromMs = new Date(opts.from).getTime();
    const toMs2 = new Date(opts.to).getTime();

    let sql: string;
    let stmt: D1PreparedStatement;

    if (opts.testerId != null) {
      sql = `SELECT * FROM tester_audit
             WHERE occurredAt >= ?1 AND occurredAt <= ?2 AND testerId = ?3
             ORDER BY occurredAt ASC`;
      stmt = this.db.prepare(sql).bind(fromMs, toMs2, opts.testerId);
    } else {
      sql = `SELECT * FROM tester_audit
             WHERE occurredAt >= ?1 AND occurredAt <= ?2
             ORDER BY occurredAt ASC`;
      stmt = this.db.prepare(sql).bind(fromMs, toMs2);
    }

    const result = await stmt.all<AuditRow>();
    return (result.results ?? []).map(rowToAudit);
  }
}
