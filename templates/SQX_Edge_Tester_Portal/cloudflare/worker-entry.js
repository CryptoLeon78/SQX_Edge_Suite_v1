import openNextWorker from "../.open-next/worker.js";

const SESSION_COOKIE = "__Host-sqx_tester_session";
const SESSION_MAX_AGE_SECONDS = 60 * 60;
const TOOL_DOWNLOAD_PATH = "/download/sqx-edge-tool.zip";
const FEATURES = [
  {
    id: "sqx_dashboard_full",
    label: "SQX Dashboard full",
    description: "Premium dashboard access for the protected tester cohort.",
    status: "ready"
  },
  {
    id: "strategy_builder",
    label: "Strategy Builder",
    description: "Commercial hook reserved for the next product iteration.",
    status: "planned"
  },
  {
    id: "project_generator",
    label: "Project Generator",
    description: "Generate buyer-ready project packs from approved profiles.",
    status: "ready"
  },
  {
    id: "views_creator",
    label: "Views Creator",
    description: "Prepare focused tester views without exposing internals.",
    status: "ready"
  },
  {
    id: "buyer_handoff_exports",
    label: "Buyer handoff exports",
    description: "Package delivery material for Pro buyer onboarding.",
    status: "ready"
  },
  {
    id: "support_case_bundle",
    label: "Support case bundle",
    description: "Collect reproducible support context for operator review.",
    status: "ready"
  }
];

const PORTAL_ACTIONS = [
  {
    href: "/tool",
    title: "Download SQX Edge tool",
    text: "Get the protected portable package for real end-user testing.",
    badge: "Real tool"
  },
  {
    href: "/handoff",
    title: "Start tester handoff",
    text: "Open the controlled launch checklist and confirm what to test first.",
    badge: "Today"
  },
  {
    href: "/feedback",
    title: "Send structured feedback",
    text: "Report friction, missing value or buying objections without exposing secrets.",
    badge: "Important"
  },
  {
    href: "/renewal",
    title: "Review access window",
    text: "Check the 15-day tester cycle and the renewal decision flow.",
    badge: "Cycle"
  }
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

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function statusMessage(status) {
  const messages = {
    demo_login_disabled: "Demo login is not enabled for this Worker yet.",
    invalid_demo_credential: "The email or access code does not match the active tester gate.",
    feedback_ready: "Feedback packet prepared. Send the private notes through the agreed operator channel."
  };
  return messages[status] || status;
}

function normalizeField(value, fallback, maxLength) {
  const normalized = String(value || "")
    .replace(/\s+/g, " ")
    .trim();
  return (normalized || fallback).slice(0, maxLength);
}

function packetReference() {
  const random = crypto.randomUUID().slice(0, 8).toUpperCase();
  return `SQX-FB-${random}`;
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
    .hero, .section { display: grid; gap: 22px; padding: 32px; }
    .topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; color: var(--muted); }
    .brand { color: var(--text); font-weight: 900; }
    .eyebrow { margin: 0; color: var(--blue); text-transform: uppercase; font-size: 0.78rem; font-weight: 800; letter-spacing: 0; }
    h1 { margin: 0; font-size: clamp(2rem, 4vw, 4rem); letter-spacing: 0; }
    h2 { margin: 0; font-size: clamp(1.25rem, 2vw, 1.8rem); letter-spacing: 0; }
    p { margin: 0; color: var(--muted); line-height: 1.6; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .action-card { display: grid; gap: 12px; padding: 18px; border: 1px solid var(--border); border-radius: 8px; background: rgba(21, 34, 56, 0.72); text-decoration: none; color: var(--text); }
    .action-card:hover { border-color: rgba(101, 165, 255, 0.72); background: rgba(24, 43, 74, 0.78); }
    .badge { width: fit-content; padding: 6px 9px; border: 1px solid rgba(35, 209, 139, 0.38); border-radius: 999px; color: var(--green); background: rgba(35, 209, 139, 0.08); font-size: 0.76rem; font-weight: 800; }
    .metric { padding: 18px; border: 1px solid var(--border); border-radius: 8px; background: rgba(21, 34, 56, 0.72); }
    .metric strong { display: block; margin-bottom: 8px; }
    .stack { display: grid; gap: 14px; }
    .checklist { display: grid; gap: 10px; margin: 0; padding: 0; list-style: none; }
    .checklist li { padding: 12px 14px; border: 1px solid var(--border); border-radius: 8px; background: rgba(8, 17, 31, 0.56); color: var(--muted); }
    .checklist strong { color: var(--text); }
    .auth-form { display: grid; gap: 16px; max-width: 460px; }
    label { display: grid; gap: 8px; color: var(--text); font-weight: 700; }
    input, select, textarea { min-height: 44px; border-radius: 8px; border: 1px solid var(--border); background: #08111f; color: var(--text); padding: 0 12px; }
    textarea { min-height: 120px; padding: 12px; resize: vertical; }
    .packet { display: grid; gap: 12px; padding: 18px; border: 1px solid rgba(35, 209, 139, 0.34); border-radius: 8px; background: rgba(8, 17, 31, 0.72); }
    .packet pre { white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; color: #d9fbe9; font: 0.92rem/1.55 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    button, .button { min-height: 44px; width: fit-content; padding: 0 18px; border: 0; border-radius: 8px; background: #1d4ed8; color: white; font-weight: 800; cursor: pointer; text-decoration: none; display: inline-grid; place-items: center; }
    .button.secondary { background: rgba(101, 165, 255, 0.14); border: 1px solid rgba(101, 165, 255, 0.38); }
    .inline-actions { display: flex; flex-wrap: wrap; gap: 10px; }
    .feature-list { display: flex; flex-wrap: wrap; gap: 8px; }
    .feature-list span { padding: 8px 10px; border: 1px solid var(--border); border-radius: 8px; background: rgba(35, 209, 139, 0.1); color: var(--green); }
    .notice { padding: 14px; border: 1px solid rgba(101, 165, 255, 0.38); border-radius: 8px; background: rgba(101, 165, 255, 0.1); }
    .watermark { position: fixed; right: 18px; bottom: 16px; font-size: 0.72rem; color: rgba(247, 251, 255, 0.58); }
    @media (max-width: 860px) { .grid, .actions { grid-template-columns: 1fr; } .hero, .section { padding: 22px; } .topbar { align-items: flex-start; flex-direction: column; } }
  </style>
</head>
<body>${content}</body>
</html>`;
}

function renderTopbar() {
  return `<div class="topbar">
    <div><span class="brand">SQX Edge</span> Tester Portal</div>
    <form action="/api/auth/logout" method="post"><button type="submit">Sign out</button></form>
  </div>`;
}

function requireSessionPage(request, renderer, next = "/portal") {
  return hasSession(request) ? htmlResponse(renderer()) : redirect(`/login?next=${encodeURIComponent(next)}`);
}

function loginPage(url) {
  const next = url.searchParams.get("next")?.startsWith("/") ? url.searchParams.get("next") : "/portal";
  const status = url.searchParams.get("status");
  const message = status
    ? `<div class="metric"><strong>Access status</strong><p>${escapeHtml(statusMessage(status))}</p></div>`
    : "";
  return buildShell(
    "SQX Edge Tester Portal",
    `<main class="shell">
      <section class="panel hero">
        <p class="eyebrow">Tester access</p>
        <h1>Sign in to SQX Edge</h1>
        <p>Protected tester bootstrap for the SQX Edge Pro experience.</p>
        ${message}
        <form class="auth-form" action="/api/auth/login" method="post">
          <input type="hidden" name="next" value="${escapeHtml(next)}" />
          <label>Email<input name="email" type="email" autocomplete="email" required /></label>
          <label>Access code<input name="accessCode" type="password" autocomplete="one-time-code" required /></label>
          <button type="submit">Continue</button>
        </form>
      </section>
    </main>`
  );
}

function portalPage() {
  const actionCards = PORTAL_ACTIONS.map(
    (action) => `<a class="action-card" href="${action.href}">
      <span class="badge">${action.badge}</span>
      <strong>${action.title}</strong>
      <p>${action.text}</p>
    </a>`
  ).join("");
  const features = FEATURES.map(
    (feature) => `<span title="${feature.description}">${feature.label} - ${feature.status}</span>`
  ).join("");
  return buildShell(
    "SQX Edge Tester Portal",
    `<main class="shell">
      ${renderTopbar()}
      <section class="panel hero">
        <p class="eyebrow">Tester Pro</p>
        <h1>Tester launch room</h1>
        <p>SQX Edge Pro tester access is active. This protected room gives testers a practical first path: what to validate, where to report friction and how the 15-day review cycle works.</p>
        <div class="grid">
          <div class="metric"><strong>Access</strong><p>Cloudflare Access plus SQX tester session is active.</p></div>
          <div class="metric"><strong>Cycle</strong><p>15-day tester review window with manual continuation decision.</p></div>
          <div class="metric"><strong>Scope</strong><p>Pro pilot features only. No payment data is collected here.</p></div>
        </div>
        <div class="actions">${actionCards}</div>
        <div class="stack">
          <h2>Available Pro surface</h2>
          <div class="feature-list">${features}</div>
        </div>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

function handoffPage() {
  return buildShell(
    "SQX Edge Tester Handoff",
    `<main class="shell">
      ${renderTopbar()}
      <section class="panel section">
        <p class="eyebrow">Tester handoff</p>
        <h1>What to test first</h1>
        <p>This is the controlled first-run checklist for invited testers. Keep feedback practical: what confused you, what created value, what would block a paid subscription.</p>
        <ul class="checklist">
          <li><strong>1. Access</strong><br />Confirm Cloudflare Access, SQX login and sign-out work cleanly in an incognito window.</li>
          <li><strong>2. Product value</strong><br />Review the Pro feature surface and mark what feels commercially useful versus decorative.</li>
          <li><strong>3. Trading workflow</strong><br />Validate whether dashboard, project generation and view creation match a real buyer workflow.</li>
          <li><strong>4. Objections</strong><br />Record anything that would stop you from recommending or paying for SQX Edge Pro.</li>
        </ul>
        <div class="inline-actions">
          <a class="button" href="/feedback">Prepare feedback</a>
          <a class="button secondary" href="/portal">Back to portal</a>
        </div>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

function toolPage() {
  return buildShell(
    "SQX Edge Tool Delivery",
    `<main class="shell">
      ${renderTopbar()}
      <section class="panel section">
        <p class="eyebrow">Real tool</p>
        <h1>Download SQX Edge Pro</h1>
        <p>This protected delivery path is for invited testers only. The package is portable: download, extract and run the launcher. No Python installation is required on the tester machine.</p>
        <div class="grid">
          <div class="metric"><strong>1. Download</strong><p>Use the protected download button from this portal session.</p></div>
          <div class="metric"><strong>2. Extract</strong><p>Unzip the package into a normal folder, not inside the ZIP viewer.</p></div>
          <div class="metric"><strong>3. Launch</strong><p>Run START_SQX_EDGE.bat and keep feedback in the protected flow.</p></div>
        </div>
        <div class="notice"><strong>Tester boundary</strong><p>Do not redistribute the package, publish links, share access codes or upload screenshots containing private account data.</p></div>
        <div class="inline-actions">
          <a class="button" href="${TOOL_DOWNLOAD_PATH}">Download portable ZIP</a>
          <a class="button secondary" href="/handoff">Open handoff checklist</a>
          <a class="button secondary" href="/portal">Back to portal</a>
        </div>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

function feedbackPage(url) {
  const status = url.searchParams.get("status");
  const category = url.searchParams.get("category");
  const message = status
    ? `<div class="notice"><strong>${escapeHtml(statusMessage(status))}</strong>${category ? `<p>Category: ${escapeHtml(category)}</p>` : ""}</div>`
    : "";
  return buildShell(
    "SQX Edge Tester Feedback",
    `<main class="shell">
      ${renderTopbar()}
      <section class="panel section">
        <p class="eyebrow">Feedback</p>
        <h1>Structured tester signal</h1>
        <p>This form prepares a private feedback packet. The Worker does not persist raw notes; send detailed private notes through the agreed operator channel after submitting.</p>
        ${message}
        <form class="auth-form" action="/api/tester/feedback" method="post">
          <label>Category
            <select name="category" required>
              <option value="onboarding">Onboarding</option>
              <option value="product_value">Product value</option>
              <option value="workflow">Workflow</option>
              <option value="commercial_objection">Commercial objection</option>
              <option value="bug_or_blocker">Bug or blocker</option>
            </select>
          </label>
          <label>Severity
            <select name="severity" required>
              <option value="signal">Signal</option>
              <option value="friction">Friction</option>
              <option value="blocker">Blocker</option>
              <option value="commercial">Commercial</option>
            </select>
          </label>
          <label>Signal summary<textarea name="summary" maxlength="800" placeholder="Short private summary. Do not include passwords, URLs, screenshots or account secrets." required></textarea></label>
          <button type="submit">Prepare feedback packet</button>
        </form>
        <div class="inline-actions"><a class="button secondary" href="/portal">Back to portal</a></div>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

function feedbackPacketPage(packet) {
  const packetText = [
    `Reference: ${packet.reference}`,
    `Category: ${packet.category}`,
    `Severity: ${packet.severity}`,
    `Summary: ${packet.summary}`,
    "Private evidence: attach only through the agreed operator channel"
  ].join("\n");
  return buildShell(
    "SQX Edge Feedback Packet",
    `<main class="shell">
      ${renderTopbar()}
      <section class="panel section">
        <p class="eyebrow">Feedback packet</p>
        <h1>Ready to send</h1>
        <p>The Worker generated this handoff packet and did not store it. Copy the text below into the private operator channel, then return to the portal.</p>
        <div class="packet">
          <strong>${escapeHtml(packet.reference)}</strong>
          <pre>${escapeHtml(packetText)}</pre>
        </div>
        <div class="notice"><strong>Privacy guard</strong><p>Do not add passwords, access codes, private URLs, screenshots or account secrets to public channels.</p></div>
        <div class="inline-actions">
          <a class="button" href="/feedback">Prepare another packet</a>
          <a class="button secondary" href="/portal">Back to portal</a>
        </div>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

function renewalPage() {
  return buildShell(
    "SQX Edge Tester Renewal",
    `<main class="shell">
      ${renderTopbar()}
      <section class="panel section">
        <p class="eyebrow">Review cycle</p>
        <h1>15-day access window</h1>
        <p>Tester access is intentionally temporary. At the end of the cycle, the operator reviews activity, feedback quality and product fit before continuing, pausing or closing access.</p>
        <div class="grid">
          <div class="metric"><strong>Continue</strong><p>Useful feedback and clear fit for the Pro pilot.</p></div>
          <div class="metric"><strong>Pause</strong><p>No current availability or feedback still pending.</p></div>
          <div class="metric"><strong>Close</strong><p>Access no longer needed or distribution risk detected.</p></div>
        </div>
        <div class="inline-actions">
          <a class="button" href="/feedback">Prepare renewal feedback</a>
          <a class="button secondary" href="/portal">Back to portal</a>
        </div>
      </section>
      <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
    </main>`
  );
}

async function feedback(request) {
  if (!hasSession(request)) {
    return jsonResponse({ ok: false, reasonCode: "missing_session" }, { status: 401 });
  }
  const form = await request.formData();
  const packet = {
    reference: packetReference(),
    category: normalizeField(form.get("category"), "uncategorized", 80),
    severity: normalizeField(form.get("severity"), "signal", 40),
    summary: normalizeField(form.get("summary"), "No summary provided.", 800)
  };
  return htmlResponse(feedbackPacketPage(packet));
}

async function downloadTool(request, env) {
  if (!hasSession(request)) {
    return redirect("/login?next=/tool");
  }

  if (!env?.ASSETS?.fetch) {
    return htmlResponse(toolPage(), { status: 503 });
  }

  const url = new URL(request.url);
  url.pathname = "/downloads/SQX_Edge_Tool_Portable_Tester.zip";
  url.search = "";
  const assetResponse = await env.ASSETS.fetch(new Request(url.toString(), request));

  if (assetResponse.status === 404) {
    return htmlResponse(
      buildShell(
        "SQX Edge Tool Delivery Pending",
        `<main class="shell">
          ${renderTopbar()}
          <section class="panel section">
            <p class="eyebrow">Real tool</p>
            <h1>Package pending</h1>
            <p>The protected delivery route is ready, but the portable ZIP has not been attached to this Worker asset bundle yet.</p>
            <div class="inline-actions">
              <a class="button secondary" href="/tool">Back to delivery</a>
              <a class="button secondary" href="/portal">Back to portal</a>
            </div>
          </section>
          <p class="watermark">SQX-DEMO-TESTER-LOCAL-ONLY</p>
        </main>`,
      ),
      { status: 404 },
    );
  }

  const headers = new Headers(assetResponse.headers);
  headers.set("Content-Type", "application/zip");
  headers.set("Content-Disposition", 'attachment; filename="SQX_Edge_Tool_Portable_Tester.zip"');
  headers.set("X-Robots-Tag", "noindex, nofollow");
  return new Response(assetResponse.body, {
    status: assetResponse.status,
    headers,
  });
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

    if (request.method === "GET" && url.pathname === "/handoff") {
      return requireSessionPage(request, handoffPage, "/handoff");
    }

    if (request.method === "GET" && url.pathname === "/tool") {
      return requireSessionPage(request, toolPage, "/tool");
    }

    if (request.method === "GET" && url.pathname === TOOL_DOWNLOAD_PATH) {
      return downloadTool(request, env);
    }

    if (request.method === "GET" && url.pathname === "/feedback") {
      return requireSessionPage(request, () => feedbackPage(url), "/feedback");
    }

    if (request.method === "POST" && url.pathname === "/api/tester/feedback") {
      return feedback(request);
    }

    if (request.method === "GET" && url.pathname === "/renewal") {
      return requireSessionPage(request, renewalPage, "/renewal");
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
