-- Migration 0001: create_tester_store
-- Backing schema for D1TesterStore (driver = "d1").
-- Timestamps stored as Unix milliseconds (INTEGER) for efficient range queries.

CREATE TABLE IF NOT EXISTS tester_auth_record (
  testerId              TEXT    PRIMARY KEY,
  emailNormalized       TEXT    NOT NULL UNIQUE,
  displayName           TEXT,
  status                TEXT    NOT NULL,
  plan                  TEXT,
  passwordHash          TEXT,
  passwordHashAlgorithm TEXT,
  passwordUpdatedAt     INTEGER,
  expiresAt             INTEGER,
  renewalCycleDays      INTEGER,
  failedLoginCount      INTEGER NOT NULL DEFAULT 0,
  lockedUntil           INTEGER,
  lastLoginAt           INTEGER,
  createdAt             INTEGER NOT NULL,
  updatedAt             INTEGER,
  privateNotesRef       TEXT
);

CREATE TABLE IF NOT EXISTS tester_session (
  sessionIdHash TEXT    PRIMARY KEY,
  testerId      TEXT    NOT NULL REFERENCES tester_auth_record(testerId),
  createdAt     INTEGER NOT NULL,
  expiresAt     INTEGER NOT NULL,
  revokedAt     INTEGER,
  lastSeenAt    INTEGER,
  ipHash        TEXT,
  userAgentHash TEXT
);

CREATE INDEX IF NOT EXISTS idx_session_tester ON tester_session(testerId);

CREATE TABLE IF NOT EXISTS tester_renewal_token (
  tokenId   TEXT    PRIMARY KEY,
  tokenHash TEXT    NOT NULL UNIQUE,
  testerId  TEXT    NOT NULL REFERENCES tester_auth_record(testerId),
  purpose   TEXT,
  createdAt INTEGER NOT NULL,
  expiresAt INTEGER NOT NULL,
  usedAt    INTEGER,
  revokedAt INTEGER
);

CREATE TABLE IF NOT EXISTS tester_audit (
  eventId            TEXT    PRIMARY KEY,
  type               TEXT    NOT NULL,
  testerId           TEXT,
  actor              TEXT,
  occurredAt         INTEGER NOT NULL,
  ipHash             TEXT,
  userAgentHash      TEXT,
  route              TEXT,
  outcome            TEXT,
  reasonCode         TEXT,
  privateEvidenceRef TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_tester_at ON tester_audit(testerId, occurredAt);
