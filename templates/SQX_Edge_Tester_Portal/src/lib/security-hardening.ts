import { buildTesterWatermark, type TesterEntitlement } from "./access-contract";

export const HARDENING_ENV = {
  globalKillSwitch: "T8_GLOBAL_KILL_SWITCH_ENABLED",
  rateLimitEnabled: "T8_RATE_LIMIT_ENABLED",
  rateLimitMaxRequests: "T8_RATE_LIMIT_MAX_REQUESTS",
  rateLimitWindowSeconds: "T8_RATE_LIMIT_WINDOW_SECONDS"
} as const;

export type RateLimitResult =
  | { ok: true; limit: number; remaining: number; resetAt: string; reasonCode: null }
  | { ok: false; status: 429; limit: number; remaining: 0; resetAt: string; reasonCode: "rate_limit_exceeded" };

type RateLimitBucket = {
  count: number;
  resetAtMs: number;
};

const RATE_LIMIT_BUCKETS = new Map<string, RateLimitBucket>();

export function isGlobalKillSwitchEnabled(): boolean {
  return process.env[HARDENING_ENV.globalKillSwitch] === "true";
}

export function isRateLimitEnabled(): boolean {
  return process.env[HARDENING_ENV.rateLimitEnabled] === "true";
}

export function readRateLimitMaxRequests(): number {
  const value = Number.parseInt(process.env[HARDENING_ENV.rateLimitMaxRequests] ?? "30", 10);
  return Number.isFinite(value) && value > 0 ? value : 30;
}

export function readRateLimitWindowSeconds(): number {
  const value = Number.parseInt(process.env[HARDENING_ENV.rateLimitWindowSeconds] ?? "60", 10);
  return Number.isFinite(value) && value > 0 ? value : 60;
}

export function isKillSwitchExemptPath(pathname: string): boolean {
  return pathname === "/expired" || pathname === "/api/health" || pathname === "/favicon.ico";
}

export function buildRateLimitKey(headers: Headers, pathname: string): string {
  const forwardedFor = headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown-ip";
  const userAgent = headers.get("user-agent") || "unknown-agent";
  return `${pathname}:${forwardedFor}:${userAgent.slice(0, 80)}`;
}

export function evaluateRateLimit(key: string, now = new Date()): RateLimitResult {
  const limit = readRateLimitMaxRequests();
  const windowMs = readRateLimitWindowSeconds() * 1000;
  const currentMs = now.getTime();
  const existing = RATE_LIMIT_BUCKETS.get(key);

  if (!isRateLimitEnabled()) {
    return {
      ok: true,
      limit,
      remaining: limit,
      resetAt: new Date(currentMs + windowMs).toISOString(),
      reasonCode: null
    };
  }

  const bucket = !existing || existing.resetAtMs <= currentMs
    ? { count: 0, resetAtMs: currentMs + windowMs }
    : existing;

  bucket.count += 1;
  RATE_LIMIT_BUCKETS.set(key, bucket);

  const remaining = Math.max(0, limit - bucket.count);
  const resetAt = new Date(bucket.resetAtMs).toISOString();

  if (bucket.count > limit) {
    return {
      ok: false,
      status: 429,
      limit,
      remaining: 0,
      resetAt,
      reasonCode: "rate_limit_exceeded"
    };
  }

  return {
    ok: true,
    limit,
    remaining,
    resetAt,
    reasonCode: null
  };
}

export function buildVisibleWatermark(entitlement: Pick<TesterEntitlement, "testerId" | "email">): string {
  return buildTesterWatermark(entitlement);
}

export function buildDemoVisibleWatermark(): string {
  return buildVisibleWatermark({
    testerId: "demo-tester-local-only",
    email: "tester@example.invalid"
  });
}

