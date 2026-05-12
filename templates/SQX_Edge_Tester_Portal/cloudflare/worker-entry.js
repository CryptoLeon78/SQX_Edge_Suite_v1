import openNextWorker from "../.open-next/worker.js";

const SESSION_COOKIE = "__Host-sqx_tester_session";
const SESSION_MAX_AGE_SECONDS = 60 * 60;
const FEATURES = [
  "sqx_dashboard_full",
  "strategy_builder",
  "project_generator",
  "views_creator",
  "buyer_handoff_exports",
  "support_case_bundle"
];

const SECURITY_HEADERS = {
  "Content-Type": "text/html; charset=utf-8",
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "X-Robots-Tag": "noindex, nofollow",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Resource-Policy": "same-origin",
  "Content-Security-Policy":
    "default-src 'self'; script-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'"
};

function htmlResponse(body, init = {}) {
  return new Response(body, {
    ...init,
    headers: {
      ...SECURITY_HEADERS,
      ...(init.headers || {})
    }
  });
}

function jsonResponse(payload, init = {}) {
  return new Response(JSON.stringify(payload, null, 2), {
    ...init,
    headers: {
      ...SECURITY_HEADERS,
      "Content-Type": "application/json; charset=utf-8",
      ...(init.headers || {})
    }
  });
}

function redirect(location, init = {}) {
  return new Response(null, {
    status: init.status || 303,
    headers: {
      Location: location,
      ...(init.headers || {})
    }
  });
}

function readCookie(request, name) {
  const cookie = request.headers.get("Cookie") || "";
  return cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`))
    ?.slice(name.length + 1);
}

function hasSession(request) {
  return Boolean(readCookie(request, SESSION_COOKIE));
}

function readEnv(env, name, fallback = "") {
  return typeof env?.[name] === "string" ? env[name] : fallback;
}

function buildShell(title, content) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${title}</title>
  <style>
    :root { color-scheme: dark; --bg: #08111f; --panel: #101a2b; --panel2: #152238; --text: #f7fbff; --muted: #9cb3cf; --blue: #65a5ff; --green: #23d18b; --border: rgba(148, 163, 184, 0.26); }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: radial-gradient(circle at 15% 12%, rgba(101, 165, 255, 0.18), transparent 30%), linear-gradient(135deg, #07101d 0%, #0f172a 52%, #07111f 100%); color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .shell { width: min(1120px, calc(100% - 40px)); margin: 0 auto; padding: 56px 0; }
    .panel { border: 1px solid var(--border); border-radius: 8px; background: rgba(16, 26, 43, 0.84); box-shadow: 0 24px 80px rgba(0, 0, 0, 0.28); }
    .hero { display: grid; gap: 22px; padding: 32px; }
    .eyebrow { margin: 0; color: var(--blue); text-transform: uppercase; font-size: 0.78rem; font-weight: 800; letter-spacing: 0; }
    h1 { margin: 0; font-size: clamp(2rem, 4vw, 4rem); letter-spacing: 0; }
    p { margin: 0; color: var(--muted); line-height: 1.6; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .metric { padding: 18px; border: 1px solid var(--border); border-radius: 8px; background: rgba(21, 34, 56, 0.72); }
    .metric strong { display: block; margin-bottom: 8px; }
    .auth-form { display: grid; gap: 16px; max-width: 460px; }
    label { display: grid; gap: 8px; color: var(--text); font-weight: 700; }
    input { min-height: 44px; border-radius: 8px; border: 1px solid var(--border); background: #08111f; color: var(--text); padding: 0 12px; }
    button, .button { min-height: 44px; width: fit-content; padding: 0 18px; border: 0; border-radius: 8px; background: #1d4ed8; color: white; font-weight: 800; cursor: pointer; text-decoration: none; display: inline-grid; place-items: center; }
    .feature-list { display: flex; flex-wrap: wrap; gap: 8px; }
    .feature-list span { padding: 8px 10px; border: 1px solid var(--border); border-radius: 8px; background: rgba(35, 209, 139, 0.1); color: var(--green); }
    .watermark { position: fixed; right: 18px; bottom: 16px; font-size: 0.72rem; color: rgba(247, 251, 255, 0.58); }
    @media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .hero { padding: 22px; } }
  </style>
</head>
<body>${content}</body>
</html>`;
}

function loginPage(url) {
  const next = url.searchParams.get("next")?.startsWith("/") ? url.searchParams.get("next") : "/portal";
  const status = url.searchParams.get("status");
  const message = status ? `<div class="metric"><strong>Access status</strong><p>${status}</p></div>` : "";
  return buildShell(
    "SQX Edge Tester Portal",
    `<main class="shell">
      <section class="panel hero">
        <p class="eyebrow">Tester access</p>
        <h1>Sign in to SQX Edge</h1>
        <p>Protected tester bootstrap for the SQX Edge Pro experience.</p>
        ${message}
        <form class="auth-form" action="/api/auth/login" method="post">
          <input type="hidden" name="next" value="${next}" />
          <label>Email<input name="email" type="email" autocomplete="email" required /></label>
          <label>Access code<input name="accessCode" type="password" autocomplete="one-time-code" required /></label>
          <button type="submit">Continue</button>
        </form>
      </section>
    </main>`
  );
}

function portalPage() {
  return buildShell(
    "SQX Edge Tester Portal",
    `<main class="shell">
      <section class="panel hero">
        <p class="eyebrow">Tester Pro</p>
        <h1>Protected portal</h1>
        <p>SQX Edge Pro tester access is active for this protected preview. This rescue shell avoids the unstable Next/OpenNext runtime path while the tester pilot is validated.</p>
        <div class="grid">
          <div class="metric"><strong>Access</strong><p>Cloudflare Access plus SQX tester session.</p></div>
          <div class="metric"><strong>Cycle</strong><p>15-day tester review window.</p></div>
          <div class="metric"><strong>Watermark</strong><p>Demo tester identity marker enabled.</p></div>
        </div>
        <div class="feature-list">${FEATURES.map((feature) => `<span>${feature}</span>`).join("")}</div>
        <form action="/api/auth/logout" method="post"><button type="submit">Sign out</button></form>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

async function login(request, env) {
  const form = await request.formData();
  const email = String(form.get("email") || "").trim().toLowerCase();
  const accessCode = String(form.get("accessCode") || "");
  const next = String(form.get("next") || "/portal");
  const expectedEmail = readEnv(env, "T4_DEMO_TESTER_EMAIL").trim().toLowerCase();
  const expectedCode = readEnv(env, "T4_DEMO_ACCESS_CODE");
  const enabled = readEnv(env, "T4_DEMO_LOGIN_ENABLED") === "true";

  if (!enabled) {
    return redirect("/login?status=demo_login_disabled");
  }

  if (!expectedEmail || !expectedCode || email !== expectedEmail || accessCode !== expectedCode) {
    return redirect("/login?status=invalid_demo_credential");
  }

  const safeNext = next.startsWith("/") && !next.startsWith("//") && !next.startsWith("/api/") ? next : "/portal";
  return redirect(safeNext, {
    headers: {
      "Set-Cookie": `${SESSION_COOKIE}=${crypto.randomUUID()}; Max-Age=${SESSION_MAX_AGE_SECONDS}; Path=/; HttpOnly; Secure; SameSite=Strict`
    }
  });
}

function logout() {
  return redirect("/login", {
    headers: {
      "Set-Cookie": `${SESSION_COOKIE}=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict`
    }
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/login")) {
      return htmlResponse(loginPage(url));
    }

    if (request.method === "POST" && url.pathname === "/api/auth/login") {
      return login(request, env);
    }

    if (request.method === "POST" && url.pathname === "/api/auth/logout") {
      return logout();
    }

    if (request.method === "GET" && url.pathname === "/portal") {
      return hasSession(request) ? htmlResponse(portalPage()) : redirect("/login?next=/portal");
    }

    if (request.method === "GET" && url.pathname === "/api/health") {
      return jsonResponse({ ok: true, service: "sqx-edge-tester-portal", mode: "cloudflare-rescue-entry" });
    }

    if (request.method === "GET" && url.pathname === "/api/tester/features") {
      if (!hasSession(request)) {
        return jsonResponse({ ok: false, reasonCode: "missing_session" }, { status: 401 });
      }
      if (readEnv(env, "T5_DEMO_TESTER_PRO_ENABLED") !== "true") {
        return jsonResponse({ ok: false, reasonCode: "demo_entitlement_disabled" }, { status: 403 });
      }
      return jsonResponse({ ok: true, plan: "tester_pro", features: FEATURES });
    }

    return openNextWorker.fetch(request, env, ctx);
  }
};
