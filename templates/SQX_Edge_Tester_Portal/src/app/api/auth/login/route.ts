import { NextResponse } from "next/server";
import { applySessionCookie, evaluatePrototypeLogin, LOGIN_ROUTE } from "@/lib/session-prototype";

export async function POST(request: Request) {
  const formData = await request.formData();
  const result = await evaluatePrototypeLogin(formData);

  if (!result.ok) {
    const loginUrl = new URL(LOGIN_ROUTE, request.url);
    loginUrl.searchParams.set("status", result.reasonCode);
    return NextResponse.redirect(loginUrl, { status: 303 });
  }

  const response = NextResponse.redirect(new URL(result.redirectTo, request.url), { status: 303 });
  return applySessionCookie(response, result.sessionId);
}

