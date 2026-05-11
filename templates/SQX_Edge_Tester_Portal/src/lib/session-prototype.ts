import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE_CONTRACT, type TesterAuditEvent } from "./auth-data-contract";
import { isRuntimeEnvEnabled, readRuntimeEnv } from "./runtime-env";

export const LOGIN_ROUTE = "/login";
export const DEFAULT_AFTER_LOGIN_ROUTE = "/portal";
export const PROTECTED_PREFIXES = ["/portal", "/admin", "/api/tester", "/api/admin"] as const;
export const DEMO_LOGIN_FLAG = "T4_DEMO_LOGIN_ENABLED";
export const DEMO_TESTER_EMAIL_ENV = "T4_DEMO_TESTER_EMAIL";
export const DEMO_ACCESS_CODE_ENV = "T4_DEMO_ACCESS_CODE";

export type LoginAttemptResult =
  | { ok: true; sessionId: string; redirectTo: string; audit: TesterAuditEvent }
  | { ok: false; status: number; reasonCode: string; audit: TesterAuditEvent };

export function isDemoLoginEnabled(): boolean {
  return isRuntimeEnvEnabled(DEMO_LOGIN_FLAG);
}

export function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

export function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

export function hasPrototypeSession(request: NextRequest): boolean {
  return Boolean(request.cookies.get(SESSION_COOKIE_CONTRACT.name)?.value);
}

export function applySessionCookie(response: NextResponse, sessionId: string): NextResponse {
  response.cookies.set({
    name: SESSION_COOKIE_CONTRACT.name,
    value: sessionId,
    httpOnly: SESSION_COOKIE_CONTRACT.httpOnly,
    secure: SESSION_COOKIE_CONTRACT.secure,
    sameSite: SESSION_COOKIE_CONTRACT.sameSite,
    path: SESSION_COOKIE_CONTRACT.path,
    maxAge: SESSION_COOKIE_CONTRACT.maxAgeMinutes * 60
  });
  return response;
}

export function clearSessionCookie(response: NextResponse): NextResponse {
  response.cookies.set({
    name: SESSION_COOKIE_CONTRACT.name,
    value: "",
    httpOnly: SESSION_COOKIE_CONTRACT.httpOnly,
    secure: SESSION_COOKIE_CONTRACT.secure,
    sameSite: SESSION_COOKIE_CONTRACT.sameSite,
    path: SESSION_COOKIE_CONTRACT.path,
    maxAge: 0
  });
  return response;
}

export function buildLoginUrl(request: NextRequest): URL {
  const loginUrl = new URL(LOGIN_ROUTE, request.url);
  loginUrl.searchParams.set("next", request.nextUrl.pathname);
  return loginUrl;
}

export function sanitizeRedirectTarget(value: FormDataEntryValue | null): string {
  const candidate = typeof value === "string" ? value : DEFAULT_AFTER_LOGIN_ROUTE;
  if (!candidate.startsWith("/") || candidate.startsWith("//")) {
    return DEFAULT_AFTER_LOGIN_ROUTE;
  }
  if (candidate.startsWith("/api/")) {
    return DEFAULT_AFTER_LOGIN_ROUTE;
  }
  return candidate;
}

export function verifyDemoCredential(email: string, accessCode: string): boolean {
  const expectedEmail = normalizeEmail(readRuntimeEnv(DEMO_TESTER_EMAIL_ENV));
  const expectedAccessCode = readRuntimeEnv(DEMO_ACCESS_CODE_ENV);
  return isDemoLoginEnabled() && Boolean(expectedEmail) && Boolean(expectedAccessCode) && normalizeEmail(email) === expectedEmail && accessCode === expectedAccessCode;
}

export function createPrototypeSessionId(): string {
  return crypto.randomUUID();
}

export function buildAuditEvent(type: TesterAuditEvent["type"], outcome: TesterAuditEvent["outcome"], reasonCode: string | null): TesterAuditEvent {
  return {
    eventId: crypto.randomUUID(),
    type,
    testerId: null,
    actor: "tester",
    occurredAt: new Date().toISOString(),
    ipHash: null,
    userAgentHash: null,
    route: null,
    outcome,
    reasonCode,
    privateEvidenceRef: null
  };
}

export async function evaluatePrototypeLogin(formData: FormData): Promise<LoginAttemptResult> {
  const email = String(formData.get("email") ?? "");
  const accessCode = String(formData.get("accessCode") ?? "");
  const redirectTo = sanitizeRedirectTarget(formData.get("next"));

  if (!isDemoLoginEnabled()) {
    return {
      ok: false,
      status: 403,
      reasonCode: "demo_login_disabled",
      audit: buildAuditEvent("login_failed", "blocked", "demo_login_disabled")
    };
  }

  if (!verifyDemoCredential(email, accessCode)) {
    return {
      ok: false,
      status: 401,
      reasonCode: "invalid_demo_credential",
      audit: buildAuditEvent("login_failed", "failed", "invalid_demo_credential")
    };
  }

  return {
    ok: true,
    sessionId: createPrototypeSessionId(),
    redirectTo,
    audit: buildAuditEvent("session_created", "allowed", null)
  };
}
