import type {
  TesterAuthRecord,
  TesterSessionRecord,
  RenewalTokenRecord,
  TesterAuditEvent,
} from "./auth-data-contract";

export interface TesterStore {
  // --- Tester records ---

  getTesterByEmail(emailNormalized: string): Promise<TesterAuthRecord | null>;
  getTesterById(testerId: string): Promise<TesterAuthRecord | null>;
  /** @throws if emailNormalized is already taken */
  createTester(record: TesterAuthRecord): Promise<TesterAuthRecord>;
  updateTester(
    testerId: string,
    updates: Partial<Omit<TesterAuthRecord, "testerId" | "emailNormalized" | "createdAt">>
  ): Promise<TesterAuthRecord | null>;

  // --- Sessions ---

  createSession(session: TesterSessionRecord): Promise<TesterSessionRecord>;
  /**
   * Returns the session if it exists, is not revoked, and has not expired; null otherwise.
   * @guarantee G-strong: after revokeSession(hash), returns null on the very next call
   */
  getSession(sessionIdHash: string): Promise<TesterSessionRecord | null>;
  /**
   * Marks the session as revoked.
   * @guarantee G-strong: subsequent getSession calls for the same hash return null
   */
  revokeSession(sessionIdHash: string): Promise<void>;

  // --- Renewal tokens ---

  createRenewalToken(token: RenewalTokenRecord): Promise<RenewalTokenRecord>;
  /**
   * Marks the token used and returns it if not yet consumed; returns null otherwise.
   * @guarantee G-atomic: at most one caller ever receives a non-null result for a given tokenHash.
   *   Within a single process this is guaranteed by JS single-threaded execution.
   *   Multi-replica deployments must use a database-level CAS
   *   (e.g. D1: UPDATE tester_renewal_tokens SET usedAt=? WHERE tokenHash=? AND usedAt IS NULL).
   */
  consumeRenewalToken(tokenHash: string): Promise<RenewalTokenRecord | null>;

  // --- Audit ---

  appendAuditEvent(event: TesterAuditEvent): Promise<void>;
  /**
   * Returns events where occurredAt >= opts.from AND occurredAt <= opts.to,
   * optionally filtered by testerId, sorted ascending by occurredAt.
   * @guarantee G-range
   */
  queryAudit(opts: {
    testerId?: string | null;
    from: string;
    to: string;
  }): Promise<TesterAuditEvent[]>;
}
