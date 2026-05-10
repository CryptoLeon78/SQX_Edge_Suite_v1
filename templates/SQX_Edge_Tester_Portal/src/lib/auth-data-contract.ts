import { TESTER_RENEWAL_CYCLE_DAYS, TESTER_STATUSES, type TesterPlan, type TesterStatus } from "./access-contract";

export const PASSWORD_HASH_POLICY = {
  algorithm: "argon2id",
  minimumMemoryKiB: 19456,
  minimumIterations: 2,
  parallelism: 1,
  pepperEnvName: "PASSWORD_PEPPER",
  plaintextPasswordStorageAllowed: false,
  fastHashAlgorithmsAllowed: false
} as const;

export const SESSION_COOKIE_CONTRACT = {
  name: "__Host-sqx_tester_session",
  httpOnly: true,
  secure: true,
  sameSite: "strict",
  path: "/",
  domain: null,
  storage: "server-side-session-id",
  localStorageAllowed: false,
  maxAgeMinutes: 60
} as const;

export const RENEWAL_TOKEN_CONTRACT = {
  tokenKind: "renewal",
  oneUseOnly: true,
  storeOnlyHash: true,
  maxAgeHours: 24,
  bindToTesterId: true,
  invalidateExistingSessionsOnDenyOrBlock: true
} as const;

export const AUDIT_EVENT_TYPES = [
  "tester_invited",
  "password_set_requested",
  "password_set_completed",
  "login_succeeded",
  "login_failed",
  "session_created",
  "session_revoked",
  "tester_expired",
  "renewal_requested",
  "renewal_approved",
  "renewal_denied",
  "tester_blocked",
  "tester_unblocked",
  "watermark_rendered",
  "cron_expiry_dry_run",
  "cron_expiry_completed"
] as const;

export type AuditEventType = (typeof AUDIT_EVENT_TYPES)[number];

export type TesterAuthRecord = {
  testerId: string;
  emailNormalized: string;
  displayName: string;
  status: TesterStatus;
  plan: TesterPlan;
  passwordHash: string | null;
  passwordHashAlgorithm: typeof PASSWORD_HASH_POLICY.algorithm | null;
  passwordUpdatedAt: string | null;
  expiresAt: string;
  renewalCycleDays: typeof TESTER_RENEWAL_CYCLE_DAYS;
  failedLoginCount: number;
  lockedUntil: string | null;
  lastLoginAt: string | null;
  createdAt: string;
  updatedAt: string;
  privateNotesRef: string | null;
};

export type TesterSessionRecord = {
  sessionIdHash: string;
  testerId: string;
  createdAt: string;
  expiresAt: string;
  revokedAt: string | null;
  lastSeenAt: string | null;
  ipHash: string;
  userAgentHash: string;
};

export type RenewalTokenRecord = {
  tokenId: string;
  tokenHash: string;
  testerId: string;
  purpose: typeof RENEWAL_TOKEN_CONTRACT.tokenKind;
  createdAt: string;
  expiresAt: string;
  usedAt: string | null;
  revokedAt: string | null;
};

export type TesterAuditEvent = {
  eventId: string;
  type: AuditEventType;
  testerId: string | null;
  actor: "tester" | "operator" | "system";
  occurredAt: string;
  ipHash: string | null;
  userAgentHash: string | null;
  route: string | null;
  outcome: "allowed" | "blocked" | "denied" | "failed" | "dry_run" | "completed";
  reasonCode: string | null;
  privateEvidenceRef: string | null;
};

export const TESTER_AUTH_REQUIRED_TABLES = [
  "testers",
  "tester_sessions",
  "tester_renewal_tokens",
  "tester_audit_events"
] as const;

export function isValidTesterStatus(status: string): status is TesterStatus {
  return (TESTER_STATUSES as readonly string[]).includes(status);
}

export function isActiveTesterRecord(record: Pick<TesterAuthRecord, "status" | "plan" | "expiresAt">, now = new Date()): boolean {
  return record.status === "active" && record.plan === "tester_pro" && new Date(record.expiresAt).getTime() > now.getTime();
}

