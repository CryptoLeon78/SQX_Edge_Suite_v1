import { DEFAULT_AFTER_LOGIN_ROUTE } from "@/lib/session-prototype";

export default async function LoginPage({ searchParams }: { searchParams?: Promise<{ next?: string }> }) {
  const params = await searchParams;
  const next = params?.next && params.next.startsWith("/") ? params.next : DEFAULT_AFTER_LOGIN_ROUTE;

  return (
    <main className="shell">
      <section className="panel hero auth-panel">
        <p className="eyebrow">Tester access</p>
        <h1>Sign in to SQX Edge</h1>
        <p>
          T4 provides a disabled-by-default local demo login. Real tester credentials, password hashing and persistence
          belong to later verified phases.
        </p>
        <form className="auth-form" action="/api/auth/login" method="post">
          <input type="hidden" name="next" value={next} />
          <label>
            Email
            <input name="email" type="email" autoComplete="email" required />
          </label>
          <label>
            Access code
            <input name="accessCode" type="password" autoComplete="one-time-code" required />
          </label>
          <button type="submit">Continue</button>
        </form>
      </section>
    </main>
  );
}
