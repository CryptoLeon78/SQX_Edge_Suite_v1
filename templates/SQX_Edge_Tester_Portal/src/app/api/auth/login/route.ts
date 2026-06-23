import { NextResponse } from "next/server";
import {
  applySessionCookie,
  evaluatePrototypeLogin,
  hashSessionId,
  LOGIN_ROUTE,
} from "@/lib/session-prototype";
import { SESSION_COOKIE_CONTRACT } from "@/lib/auth-data-contract";
import { getTesterStore } from "@/lib/tester-store-factory";

export async function POST(request: Request) {
  const formData = await request.formData();
  const result = await evaluatePrototypeLogin(formData);

  if (!result.ok) {
    const loginUrl = new URL(LOGIN_ROUTE, request.url);
    loginUrl.searchParams.set("status", result.reasonCode);
    return NextResponse.redirect(loginUrl, { status: 303 });
  }

  const store = getTesterStore();
  const sessionIdHash = await hashSessionId(result.sessionId);
  const now = new Date();
  await store.createSession({
    sessionIdHash,
    testerId: "demo-tester",
    createdAt: now.toISOString(),
    expiresAt: new Date(
      now.getTime() + SESSION_COOKIE_CONTRACT.maxAgeMinutes * 60 * 1_000
    ).toISOString(),
    revokedAt: null,
    lastSeenAt: null,
    ipHash: "",
    userAgentHash: "",
  });

  const response = NextResponse.redirect(new URL(result.redirectTo, request.url), {
    status: 303,
  });
  return applySessionCookie(response, result.sessionId);
}
