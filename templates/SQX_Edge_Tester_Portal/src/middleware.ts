import { NextRequest, NextResponse } from "next/server";
import { SECURITY_HEADERS } from "@/lib/security-headers";
import { buildLoginUrl, hasPrototypeSession, isProtectedPath } from "@/lib/session-prototype";

export function middleware(request: NextRequest) {
  const response = isProtectedPath(request.nextUrl.pathname) && !hasPrototypeSession(request)
    ? NextResponse.redirect(buildLoginUrl(request))
    : NextResponse.next();

  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    response.headers.set(key, value);
  }

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
