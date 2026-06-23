import { NextRequest, NextResponse } from "next/server";
import { SECURITY_HEADERS } from "@/lib/security-headers";
import {
  buildRateLimitKey,
  evaluateRateLimit,
  isGlobalKillSwitchEnabled,
  isKillSwitchExemptPath,
} from "@/lib/security-hardening";
import { buildLoginUrl, hashSessionId, isProtectedPath } from "@/lib/session-prototype";
import { SESSION_COOKIE_CONTRACT } from "@/lib/auth-data-contract";
import { getTesterStore } from "@/lib/tester-store-factory";

function applySecurityHeaders(response: NextResponse): NextResponse {
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    response.headers.set(key, value);
  }
  return response;
}

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  if (isGlobalKillSwitchEnabled() && !isKillSwitchExemptPath(pathname)) {
    if (pathname.startsWith("/api/")) {
      return applySecurityHeaders(
        NextResponse.json({ ok: false, reasonCode: "global_kill_switch_enabled" }, { status: 503 })
      );
    }
    return applySecurityHeaders(
      NextResponse.redirect(new URL("/expired?status=global_kill_switch_enabled", request.url))
    );
  }

  const rateLimit = evaluateRateLimit(buildRateLimitKey(request.headers, pathname));
  if (!rateLimit.ok) {
    const response = pathname.startsWith("/api/")
      ? NextResponse.json(
          { ok: false, reasonCode: rateLimit.reasonCode, resetAt: rateLimit.resetAt },
          { status: rateLimit.status }
        )
      : NextResponse.redirect(new URL("/expired?status=rate_limit_exceeded", request.url));
    response.headers.set(
      "Retry-After",
      String(Math.max(1, Math.ceil((Date.parse(rateLimit.resetAt) - Date.now()) / 1000)))
    );
    return applySecurityHeaders(response);
  }

  let hasValidSession = false;
  const cookieValue = request.cookies.get(SESSION_COOKIE_CONTRACT.name)?.value;
  if (cookieValue) {
    const sessionIdHash = await hashSessionId(cookieValue);
    const session = await getTesterStore().getSession(sessionIdHash);
    hasValidSession = session !== null;
  }

  const response =
    isProtectedPath(pathname) && !hasValidSession
      ? NextResponse.redirect(buildLoginUrl(request))
      : NextResponse.next();

  response.headers.set("X-RateLimit-Limit", String(rateLimit.limit));
  response.headers.set("X-RateLimit-Remaining", String(rateLimit.remaining));
  response.headers.set("X-RateLimit-Reset", rateLimit.resetAt);

  return applySecurityHeaders(response);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
