# ADR-0002: TesterStore Abstraction and Storage Backend

**Status:** Accepted  
**Date:** 2026-06-23  
**Deciders:** Rafael Fernandez (SQX Edge)

---

## Context

The SQX Edge Tester Portal requires persistent, secure storage for:

- **Tester auth records** (`testers` table) — identity, status, password hash, expiry.
- **Sessions** (`tester_sessions`) — session ID hash, revocation state, expiry.
- **Renewal tokens** (`tester_renewal_tokens`) — one-use tokens with atomic consume semantics.
- **Audit events** (`tester_audit_events`) — append-only ordered log with range queries.

The portal's current MS1 "Demo" mode uses no persistent storage (cookie-trust, env-var credentials).  
MS2 introduces a **storage-agnostic `TesterStore` interface** so the demo driver, an in-memory test oracle, and the real Cloudflare D1 driver (MS3) all satisfy a common contract.

---

## Decision

### Storage backend: Cloudflare D1

D1 is the selected production storage for the `TesterStore`.

### Why not KV?

Cloudflare KV fails all three critical guarantees:

| Guarantee | Requirement | KV Behaviour | Result |
|-----------|-------------|--------------|--------|
| **G-atomic** | `consumeRenewalToken` — at most one caller gets non-null per token | No atomic read-modify-write; two concurrent Workers can both read `usedAt=null` before either writes the update | **FAILS** — double-use vulnerability |
| **G-strong** | `getSession` returns `null` *immediately* after `revokeSession` | KV has eventual consistency with up to ~60 s propagation lag between edge locations | **FAILS** — revoked session accepted for up to 60 s |
| **G-range** | `queryAudit` with `[from, to]` range, sorted by `occurredAt` | KV supports only key prefix scans; no secondary index, no range on values | **FAILS** — requires full-table scan + client-side filter |

### Why D1?

| Guarantee | D1 Mechanism |
|-----------|-------------|
| **G-atomic** | `UPDATE tester_renewal_tokens SET usedAt = ? WHERE tokenHash = ? AND usedAt IS NULL` — SQLite serialises writes; exactly one writer wins |
| **G-strong** | SQLite serialisable isolation within a D1 instance — a revoke write is immediately visible to the next read in the same or any subsequent request on the same DO shard |
| **G-range** | `SELECT … WHERE occurredAt BETWEEN ? AND ? ORDER BY occurredAt ASC` — native SQL range query with index support |

D1 also provides:
- Native SQLite in Cloudflare Workers (no external DB round-trip)
- Free tier sufficient for a private tester portal
- Type-safe schema via `cf:typegen` (wrangler)
- Transactional DDL for future migrations

---

## Drivers

| `TESTER_STORE_DRIVER` | Class | Use |
|------------------------|-------|-----|
| `"demo"` (default) | `DemoTesterStore` | Production deploy — cookie-trust, no DB |
| `"memory"` | `InMemoryTesterStore` | Local dev + vitest contract oracle |
| `"d1"` *(MS3)* | `D1TesterStore` | Production deploy with real persistence |

The factory (`getTesterStore()`) reads `TESTER_STORE_DRIVER` from the Cloudflare env (falls back to `process.env`). No module-level state; a new instance is created per request.

---

## Consequences

- **Positive:** The `TesterStore` interface decouples route handlers and middleware from storage details. D1 can be swapped in (MS3) without touching routes.
- **Positive:** `InMemoryTesterStore` is a specification-level oracle — any driver that passes `runTesterStoreContract` is correct by construction.
- **Negative:** `DemoTesterStore` is exempt from G-atomic / G-strong guarantees; this is acceptable because it is never used with real tokens or real sessions.
- **Negative:** D1 adds a synchronous SQLite write on every login and logout; acceptable at portal scale (< 100 concurrent testers).

---

## Tables (planned for MS3 D1 migration)

```sql
testers (testerId PK, emailNormalized UNIQUE, …)
tester_sessions (sessionIdHash PK, testerId, expiresAt, revokedAt, …)
tester_renewal_tokens (tokenHash PK, testerId, usedAt, revokedAt, …)
tester_audit_events (eventId PK, testerId, occurredAt INDEX, …)
```

See `auth-data-contract.ts → TESTER_AUTH_REQUIRED_TABLES` for the canonical table list.
