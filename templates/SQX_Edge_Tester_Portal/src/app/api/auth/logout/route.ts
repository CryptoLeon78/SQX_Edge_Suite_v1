import { NextResponse } from "next/server";
import { getCloudflareContext } from "@opennextjs/cloudflare";
import { clearSessionCookie, hashSessionId, LOGIN_ROUTE } from "@/lib/session-prototype";
import { SESSION_COOKIE_CONTRACT } from "@/lib/auth-data-contract";
import { getTesterStore } from "@/lib/tester-store-factory";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const cookieStore = await cookies();
  const cookieValue = cookieStore.get(SESSION_COOKIE_CONTRACT.name)?.value;

  if (cookieValue) {
    const { env } = await getCloudflareContext({ async: true });
    const store = getTesterStore(env);
    const sessionIdHash = await hashSessionId(cookieValue);
    await store.revokeSession(sessionIdHash);
  }

  const response = NextResponse.redirect(new URL(LOGIN_ROUTE, request.url), { status: 303 });
  return clearSessionCookie(response);
}
