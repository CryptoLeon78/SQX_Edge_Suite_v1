import { NextResponse } from "next/server";
import { clearSessionCookie, LOGIN_ROUTE } from "@/lib/session-prototype";

export function POST(request: Request) {
  const response = NextResponse.redirect(new URL(LOGIN_ROUTE, request.url), { status: 303 });
  return clearSessionCookie(response);
}

