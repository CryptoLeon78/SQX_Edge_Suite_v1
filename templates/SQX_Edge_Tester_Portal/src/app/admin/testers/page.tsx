import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ADMIN_TESTER_ACTIONS, buildDemoAdminTesterRows } from "@/lib/admin-console";
import { SESSION_COOKIE_CONTRACT } from "@/lib/auth-data-contract";
import { LOGIN_ROUTE } from "@/lib/session-prototype";

const rows = buildDemoAdminTesterRows();

export default async function AdminTestersPage() {
  const session = (await cookies()).get(SESSION_COOKIE_CONTRACT.name)?.value;
  if (!session) {
    redirect(`${LOGIN_ROUTE}?next=/admin/testers`);
  }

  return (
    <main className="shell">
      <section className="panel hero">
        <p className="eyebrow">Admin tester console</p>
        <h1>Operator review before tester access changes</h1>
        <p>
          T7 provides a protected admin surface for create, renew, deny, block and audit review. The public-safe
          template only previews decisions; it never persists tester data.
        </p>
        <div className="admin-toolbar" aria-label="Admin tester actions">
          {ADMIN_TESTER_ACTIONS.map((action) => (
            <form key={action} action="/api/admin/testers" method="post">
              <input type="hidden" name="action" value={action} />
              <input type="hidden" name="testerId" value="demo-new-tester" />
              <button type="submit">{action}</button>
            </form>
          ))}
        </div>
        <div className="admin-table" role="table" aria-label="Demo tester lifecycle review">
          <div className="admin-row admin-head" role="row">
            <span>Tester</span>
            <span>Status</span>
            <span>Expires</span>
            <span>Audit</span>
            <span>Risk</span>
          </div>
          {rows.map((row) => (
            <div className="admin-row" role="row" key={row.testerId}>
              <span>
                <strong>{row.displayName}</strong>
                <small>{row.email}</small>
              </span>
              <span className={`status-pill status-${row.status}`}>{row.status}</span>
              <span>{row.expiresAt.slice(0, 10)}</span>
              <span>{row.lastAuditEvent}</span>
              <span>{row.riskNote}</span>
            </div>
          ))}
        </div>
        <p>
          Real T7 production use must add private persistence, role-based operator identity, immutable audit records and
          explicit approval before deployment.
        </p>
      </section>
    </main>
  );
}
