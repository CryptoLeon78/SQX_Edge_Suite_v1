import { NextRequest, NextResponse } from "next/server";
import { SECURITY_HEADERS } from "@/lib/security-headers";

const PROTECTED_PREFIXES = ["/portal", "/admin", "/api/tester"];

export function middleware(request: NextRequest) {
  const isProtected = PROTECTED_PREFIXES.some((prefix) => request.nextUrl.pathname.startsWith(prefix));
  const hasSession = Boolean(request.cookies.get("sqx_tester_session")?.value);
  const response =
    isProtected && !hasSession
      ? NextResponse.redirect(new URL("/expired", request.url))
      : NextResponse.next();

  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    response.headers.set(key, value);
  }

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};

